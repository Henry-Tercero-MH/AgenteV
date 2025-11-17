import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';
import * as cocoSsd from '@tensorflow-models/coco-ssd';
import '@tensorflow/tfjs';
import HlsStream from './HlsStream';

/**
 * Componente de cámara integrado en el dashboard
 * Permite capturar frames de la webcam o RTSP y enviarlos al backend para procesamiento
 * MODO AUTO-DETECCIÓN: Escanea continuamente como un lector QR
 */
function CameraCapture({ apiUrl, onDetection }) {
    const [cameraActive, setCameraActive] = useState(false);
  const [vehicleBoxes, setVehicleBoxes] = useState([]);
  // Estado para error visual
  const [errorMsg, setErrorMsg] = useState(null);
  const [cocoModel, setCocoModel] = useState(null);
  // Estado para fuente de video
  const [videoSource, setVideoSource] = useState('webcam'); // 'webcam' o 'rtsp'

  // URLs de streams RTSP
  const RTSP_URL = 'rtsp://admin:Ccamar4.@10.10.7.224:554/Streaming/Channels/2';
  const HLS_URL = `${apiUrl}/hls/stream.m3u8`;
  // Validar carga del modelo
  useEffect(() => {
    setErrorMsg(
      !cocoModel
        ? 'El modelo de detección no está cargado. Espera unos segundos o recarga la página.'
        : null
    );
  }, [cocoModel]);
  // Dibuja los recuadros de vehículos detectados sobre el video
  useEffect(() => {
    if (!cameraActive) return;
    const canvas = detectionCanvasRef.current;
    const video = videoRef.current;
    // Validar referencias y dimensiones
    if (!canvas || !video || !video.videoWidth || !video.videoHeight) return;
    // Evitar dimensiones inválidas
    if (video.videoWidth < 10 || video.videoHeight < 10) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    vehicleBoxes.forEach(([x, y, w, h]) => {
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);
      ctx.font = '16px Arial';
      ctx.fillStyle = '#00ff00';
      ctx.fillText('Vehículo', x, y - 8);
    });
  }, [vehicleBoxes, cameraActive]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const detectionCanvasRef = useRef(null); // Canvas para overlay de detecciones
  const hlsStreamRef = useRef(null); // Ref para el componente HlsStream
  const [processing, setProcessing] = useState(false);
  const [lastCapture, setLastCapture] = useState(null);
  const [autoScanEnabled, setAutoScanEnabled] = useState(false);
  const [scanInterval, setScanInterval] = useState(500); // milisegundos entre escaneos
  const scanIntervalRef = useRef(null);
  const processingQueueRef = useRef(new Set()); // Control de duplicados
  const lastProcessedRef = useRef({}); // timestamp de última procesada por placa
  const animationFrameRef = useRef(null);
  const [detectionStats, setDetectionStats] = useState({
    scans: 0,
    detections: 0,
    lastScan: null
  });

  // Estado para animación de línea escaneo
  const [scanLinePos, setScanLinePos] = useState(0);
  const scanLineDirection = useRef(1);
  // Animación de línea de escaneo QR
  useEffect(() => {
    if (autoScanEnabled && cameraActive) {
      let rafId;
      const animateLine = () => {
        setScanLinePos(prev => {
          const video = videoRef.current;
          if (!video) return 0;
          const max = video.videoHeight || 400;
          let next = prev + scanLineDirection.current * 6;
          if (next >= max - 10) {
            scanLineDirection.current = -1;
            next = max - 10;
          } else if (next <= 10) {
            scanLineDirection.current = 1;
            next = 10;
          }
          return next;
        });
        rafId = requestAnimationFrame(animateLine);
      };
      animateLine();
      return () => {
        cancelAnimationFrame(rafId);
      };
    } else {
      setScanLinePos(0);
    }
  }, [autoScanEnabled, cameraActive]);

  // Cargar el modelo COCO-SSD al montar
  useEffect(() => {
    cocoSsd.load().then(setCocoModel);
  }, []);

  // Detección de vehículos en el frame
  const detectVehicleInFrame = async (canvas) => {
    if (!cocoModel || !canvas) return false;
    const predictions = await cocoModel.detect(canvas);
    const vehicles = predictions.filter(pred =>
      ['car', 'truck', 'bus', 'motorcycle'].includes(pred.class) && pred.score > 0.5
    );
    setVehicleBoxes(vehicles.map(v => v.bbox)); // Para overlay
    return vehicles.length > 0;
  };

  // Iniciar fuente de video (webcam o RTSP)
  const startVideoSource = async () => {
    try {
      if (videoSource === 'webcam') {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment' // Cámara trasera en móviles
          }
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCameraActive(true);
          console.log('✅ Cámara web iniciada');
        }
      } else if (videoSource === 'rtsp') {
        // Para RTSP, usamos HLS stream que debería estar corriendo en el backend
        setCameraActive(true);
        console.log('✅ Stream RTSP/HLS iniciado');
      }
    } catch (error) {
      console.error('❌ Error al acceder a la fuente de video:', error);
      alert(`No se pudo acceder a la ${videoSource === 'webcam' ? 'cámara' : 'fuente RTSP'}. Verifica los permisos y conexiones.`);
    }
  };

  // Detener fuente de video
  const stopVideoSource = () => {
    if (videoSource === 'webcam' && videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    console.log('🛑 Fuente de video detenida');
  };

  // Cambiar fuente de video
  const changeVideoSource = (newSource) => {
    if (cameraActive) {
      stopVideoSource();
    }
    setVideoSource(newSource);
    // Reiniciar con la nueva fuente después de un breve delay
    setTimeout(() => {
      if (newSource !== videoSource) {
        startVideoSource();
      }
    }, 500);
  };

  // Procesar frame en segundo plano sin bloquear el escaneo
  const processFrameBackground = async (canvas) => {
    try {
      // Convertir a blob
      const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/jpeg', 0.85);
      });

      // Crear un ID único para este frame
      const frameId = Date.now();

      // Evitar procesar múltiples veces el mismo frame
      if (processingQueueRef.current.size > 2) {
        console.log('⏭️ Cola de procesamiento llena, saltando frame');
        return;
      }

      processingQueueRef.current.add(frameId);

      // Crear FormData para enviar la imagen
      const formData = new FormData();
      formData.append('file', blob, `scan_${frameId}.jpg`);

      console.log('🔍 Escaneando frame...');

      // Enviar al backend sin bloquear
      const response = await axios.post(
        `${apiUrl}/api/procesar-captura`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          timeout: 10000 // timeout de 10s
        }
      );

      // Remover de la cola
      processingQueueRef.current.delete(frameId);

      if (response.data?.success && response.data?.detecciones?.length > 0) {
        console.log('✅ Placa(s) detectada(s):', response.data);

        // Actualizar estadísticas
        setDetectionStats(prev => ({
          ...prev,
          detections: prev.detections + response.data.detecciones.length
        }));

        // Guardar imagen con detección
        const imageUrl = canvas.toDataURL('image/jpeg');
        setLastCapture(imageUrl);

        // Marcar como procesada para evitar duplicados
        response.data.detecciones.forEach(det => {
          lastProcessedRef.current[det.placa] = Date.now();
        });

        // Callback con la detección
        if (onDetection) {
          onDetection(response.data);
        }

        // Reproducir sonido de éxito (opcional)
        playSuccessSound();
      }

    } catch (error) {
      // Silenciar errores para no interrumpir el escaneo continuo
      if (error.response?.status === 404) {
        console.warn('⚠️ API no disponible');
      } else if (!error.response) {
        console.warn('⚠️ Timeout o error de red');
      } else {
        console.warn('⚠️ Error al procesar:', error.message);
      }

      // Remover de la cola en caso de error
      processingQueueRef.current.clear();
    }
  };

  // Captura manual (botón) - funciona con ambas fuentes
  const captureFrame = async () => {
    if (!canvasRef.current) {
      return;
    }

    setProcessing(true);

    try {
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      if (videoSource === 'webcam' && videoRef.current) {
        // Captura desde webcam
        const video = videoRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
      } else if (videoSource === 'rtsp') {
        // Para RTSP, necesitamos capturar del video HLS usando la ref
        const hlsVideo = hlsStreamRef.current?.getVideoElement();
        if (hlsVideo && hlsVideo.videoWidth > 0) {
          canvas.width = hlsVideo.videoWidth;
          canvas.height = hlsVideo.videoHeight;
          context.drawImage(hlsVideo, 0, 0, canvas.width, canvas.height);
        } else {
          throw new Error('Stream RTSP no disponible o no cargado');
        }
      }

      const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/jpeg', 0.9);
      });

      const formData = new FormData();
      formData.append('file', blob, `captura_${videoSource}_${Date.now()}.jpg`);

      console.log(`📸 Captura manual desde ${videoSource}...`);

      const response = await axios.post(
        `${apiUrl}/api/procesar-captura`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      console.log('✅ Frame procesado:', response.data);

      const imageUrl = canvas.toDataURL('image/jpeg');
      setLastCapture(imageUrl);

      if (onDetection && response.data) {
        onDetection(response.data);
      }

      alert(`✅ Imagen capturada desde ${videoSource === 'webcam' ? 'cámara web' : 'stream RTSP'} y procesada correctamente`);

    } catch (error) {
      console.error('❌ Error al procesar frame:', error);

      if (error.response?.status === 404) {
        alert('El endpoint de procesamiento no está disponible. Verifica que el API esté corriendo en ' + apiUrl);
      } else {
        alert(`Error al procesar la imagen desde ${videoSource === 'webcam' ? 'cámara web' : 'stream RTSP'}: ` + error.message);
      }
    } finally {
      setProcessing(false);
    }
  };

  // Sonido de éxito (opcional)
  const playSuccessSound = () => {
    try {
      const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZSA0PVKno66xZFglGmN/yvmwgBzGG0fPUgTMHHm/A7+CYRw0NVKjo661aFgo=');
      audio.volume = 0.3;
      audio.play().catch(() => {});
    } catch (e) {
      // Ignorar si no se puede reproducir
    }
  };

  // Auto-escaneo continuo con detección de vehículos en DOS PASOS
  useEffect(() => {
    if (autoScanEnabled && cameraActive) {
      console.log(`🚀 Iniciando auto-escaneo de 2 pasos desde ${videoSource}...`);
      scanIntervalRef.current = setInterval(async () => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const context = canvas.getContext('2d');

        // PASO 1: Capturar frame del video
        if (videoSource === 'webcam' && videoRef.current) {
          const video = videoRef.current;
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
        } else if (videoSource === 'rtsp') {
          const hlsVideo = hlsStreamRef.current?.getVideoElement();
          if (hlsVideo && hlsVideo.videoWidth > 0) {
            canvas.width = hlsVideo.videoWidth;
            canvas.height = hlsVideo.videoHeight;
            context.drawImage(hlsVideo, 0, 0, canvas.width, canvas.height);
          } else {
            return; // Skip si no hay video RTSP disponible
          }
        }

        // PASO 2: Pre-escaneo - Detectar si hay vehículo/camión
        console.log('🔍 PASO 1: Buscando vehículos en el frame...');
        const hasVehicle = await detectVehicleInFrame(canvas);

        // Actualizar estadísticas de escaneos
        setDetectionStats(prev => ({
          ...prev,
          scans: prev.scans + 1,
          lastScan: new Date().toLocaleTimeString()
        }));

        if (hasVehicle) {
          console.log('🚗 PASO 2: ¡Vehículo detectado! Enviando al OCR para extracción de placa...');
          // Solo procesar OCR si hay vehículo detectado
          processFrameBackground(canvas);
        } else {
          console.log('➖ No hay vehículos en el frame - saltando procesamiento OCR');
        }
      }, scanInterval);
      return () => {
        if (scanIntervalRef.current) {
          clearInterval(scanIntervalRef.current);
          console.log('⏹️ Auto-escaneo de 2 pasos detenido');
        }
      };
    }
  }, [autoScanEnabled, cameraActive, scanInterval, cocoModel, videoSource]);

  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      stopVideoSource();
      if (scanIntervalRef.current) {
        clearInterval(scanIntervalRef.current);
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {errorMsg && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error:</strong> {errorMsg}
        </div>
      )}
      {/* Header */}
      <div className="border-b pb-4 mb-4">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <svg
              className="w-8 h-8 text-blue-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            Cámara de Detección
          </h2>
          {/* Selector de fuente de video */}
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">Fuente:</label>
            <select
              value={videoSource}
              onChange={(e) => changeVideoSource(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg bg-white text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={cameraActive && autoScanEnabled}
            >
              <option value="webcam">📷 Webcam</option>
              <option value="rtsp">🎥 RTSP Canal 2</option>
            </select>
          </div>
        </div>
      </div>

      {/* Video Feed */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-4">
        {/* Video de webcam */}
        {videoSource === 'webcam' && (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full h-auto"
            style={{ maxHeight: '400px', display: cameraActive ? 'block' : 'none' }}
          />
        )}

        {/* Stream RTSP/HLS */}
        {videoSource === 'rtsp' && cameraActive && (
          <div style={{ maxHeight: '400px' }}>
            <HlsStream
              ref={hlsStreamRef}
              src={HLS_URL}
              style={{ width: '100%', height: 'auto', maxHeight: '400px' }}
            />
          </div>
        )}

        {/* Canvas overlay para recuadros de vehículos (solo para webcam) */}
        {videoSource === 'webcam' && (
          <canvas
            ref={detectionCanvasRef}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              pointerEvents: 'none',
              width: '100%',
              height: '100%',
              zIndex: 20,
              display: cameraActive ? 'block' : 'none'
            }}
          />
        )}

        {/* Efecto línea escaneo tipo QR (solo para webcam) */}
        {videoSource === 'webcam' && cameraActive && autoScanEnabled && (
          <div style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: scanLinePos,
            height: '4px',
            background: 'linear-gradient(90deg, #00ff00 0%, #00eaff 100%)',
            boxShadow: '0 0 12px 2px #00ff00',
            opacity: 0.85,
            zIndex: 10,
            transition: 'top 0.1s linear'
          }} />
        )}

        {!cameraActive && (
          <div className="flex items-center justify-center h-64 bg-gray-800">
            <div className="text-center text-gray-400">
              <svg
                className="w-16 h-16 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              <p className="text-lg">
                {videoSource === 'webcam' ? 'Cámara apagada' : 'Stream RTSP no activo'}
              </p>
              <p className="text-sm mt-2">
                Presiona "Iniciar {videoSource === 'webcam' ? 'Cámara' : 'Stream'}" para comenzar
              </p>
            </div>
          </div>
        )}

        {/* Overlay de estado */}
        {cameraActive && autoScanEnabled && (
          <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-2 text-center">
            <div className="flex items-center justify-center gap-4">
              <span className="animate-pulse">
                🔍 Escaneo Inteligente 2 Pasos: {videoSource === 'webcam' ? 'Webcam' : 'RTSP'}
              </span>
              <div className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">
                {detectionStats.scans} frames | {detectionStats.detections} placas
              </div>
            </div>
            <div className="text-xs mt-1 opacity-90">
              PASO 1: Buscar vehículo → PASO 2: Extraer placa OCR
            </div>
          </div>
        )}
        {cameraActive && processing && !autoScanEnabled && (
          <div className="absolute top-0 left-0 right-0 bg-blue-600 text-white px-4 py-2 text-center">
            <span className="animate-pulse">
              📸 Procesando imagen desde {videoSource === 'webcam' ? 'webcam' : 'RTSP'}...
            </span>
          </div>
        )}
      </div>

      {/* Canvas oculto para captura */}
      <canvas ref={canvasRef} style={{ display: 'none' }} />

      {/* Controles */}
      <div className="space-y-4">
        {/* Botones principales */}
        <div className="flex gap-2">
          {!cameraActive ? (
            <button
              onClick={startVideoSource}
              className="flex-1 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              Iniciar {videoSource === 'webcam' ? 'Cámara' : 'Stream RTSP'}
            </button>
          ) : (
            <>
              <button
                onClick={captureFrame}
                disabled={processing}
                className={`flex-1 px-4 py-3 rounded-lg transition font-semibold flex items-center justify-center gap-2 ${
                  processing
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
                {processing ? 'Procesando...' : `Capturar desde ${videoSource === 'webcam' ? 'Webcam' : 'RTSP'}`}
              </button>

              <button
                onClick={stopVideoSource}
                className="px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-semibold flex items-center justify-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
                  />
                </svg>
                Detener
              </button>
            </>
          )}
        </div>

        {/* Auto-escaneo continuo */}
        {cameraActive && (
          <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-4 border-2 border-green-200">
            <div className="flex items-center justify-between mb-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoScanEnabled}
                  onChange={(e) => {
                    setAutoScanEnabled(e.target.checked);
                    if (e.target.checked) {
                      setDetectionStats({ scans: 0, detections: 0, lastScan: null });
                    }
                  }}
                  className="w-5 h-5 text-green-600"
                />
                <div>
                  <span className="font-bold text-gray-800">🔍 Escaneo Inteligente 2 Pasos</span>
                  <p className="text-xs text-gray-600">
                    PASO 1: Detecta vehículo/camión → PASO 2: Extrae placa con OCR
                  </p>
                </div>
              </label>

              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600 font-medium">Velocidad:</label>
                <select
                  value={scanInterval}
                  onChange={(e) => setScanInterval(Number(e.target.value))}
                  className="px-3 py-1 border-2 border-green-300 rounded-lg text-sm font-semibold bg-white"
                  disabled={!autoScanEnabled}
                >
                  <option value={300}>⚡ Rápido (300ms)</option>
                  <option value={500}>🚀 Medio (500ms)</option>
                  <option value={1000}>🐢 Lento (1s)</option>
                  <option value={2000}>🐌 Muy lento (2s)</option>
                </select>
              </div>
            </div>

            {autoScanEnabled && (
              <div className="mt-3 p-3 bg-white rounded border border-green-200">
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-blue-600">{detectionStats.scans}</p>
                    <p className="text-xs text-gray-600">Frames Analizados</p>
                    <p className="text-xs text-blue-500">PASO 1</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-green-600">{detectionStats.detections}</p>
                    <p className="text-xs text-gray-600">Placas Detectadas</p>
                    <p className="text-xs text-green-500">PASO 2</p>
                  </div>
                  <div>
                    <p className="text-sm font-mono text-gray-700">{detectionStats.lastScan || '--:--:--'}</p>
                    <p className="text-xs text-gray-600">Último escaneo</p>
                    <p className="text-xs text-gray-500">Continuo</p>
                  </div>
                </div>
                <p className="text-xs text-green-700 mt-2 text-center font-semibold">
                  ✅ Sistema de 2 pasos activo: Solo procesa OCR cuando detecta vehículo
                </p>
              </div>
            )}

            {!autoScanEnabled && (
              <p className="text-xs text-gray-600 text-center">
                💡 Activa el escaneo automático para detectar placas desde {videoSource === 'webcam' ? 'la webcam' : 'el stream RTSP'} en tiempo real sin presionar botones
              </p>
            )}
          </div>
        )}

        {/* Información sobre RTSP */}
        {videoSource === 'rtsp' && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-semibold text-blue-800">Stream RTSP Canal 2</p>
                <p className="text-xs text-blue-700">
                  Conectado a: <code className="bg-blue-100 px-1 rounded">rtsp://admin:Ccamar4.@10.10.7.224:554/Streaming/Channels/2</code>
                </p>
                <p className="text-xs text-blue-600 mt-1">
                  El stream se convierte a HLS para reproducción web. Asegúrate de que el backend esté ejecutándose.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Última captura */}
        {lastCapture && (
          <div className="border-t pt-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">
              Última Captura ({videoSource === 'webcam' ? 'Webcam' : 'RTSP Canal 2'}):
            </p>
            <img
              src={lastCapture}
              alt="Última captura"
              className="w-full rounded border"
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default CameraCapture;
