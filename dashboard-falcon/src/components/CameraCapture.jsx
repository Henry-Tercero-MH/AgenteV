import React, { useRef, useState, useEffect } from 'react';
import axios from 'axios';

/**
 * Componente de cámara integrado en el dashboard
 * Permite capturar frames de la webcam y enviarlos al backend para procesamiento
 * MODO AUTO-DETECCIÓN: Escanea continuamente como un lector QR
 */
function CameraCapture({ apiUrl, onDetection }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const detectionCanvasRef = useRef(null); // Canvas para overlay de detecciones
  const [cameraActive, setCameraActive] = useState(false);
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

  // Iniciar cámara
  const startCamera = async () => {
    try {
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
        console.log('✅ Cámara iniciada');
      }
    } catch (error) {
      console.error('❌ Error al acceder a la cámara:', error);
      alert('No se pudo acceder a la cámara. Verifica los permisos.');
    }
  };

  // Detener cámara
  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject;
      const tracks = stream.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
      setCameraActive(false);
      console.log('🛑 Cámara detenida');
    }
  };

  // Escaneo automático continuo - detecta placas en tiempo real
  const autoScan = async () => {
    if (!videoRef.current || !canvasRef.current || !autoScanEnabled) {
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    // Configurar tamaño del canvas
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Dibujar frame actual
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Actualizar estadísticas
    setDetectionStats(prev => ({
      ...prev,
      scans: prev.scans + 1,
      lastScan: new Date().toLocaleTimeString()
    }));

    // Enviar a procesar en segundo plano (sin esperar respuesta)
    processFrameBackground(canvas);
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

  // Captura manual (botón)
  const captureFrame = async () => {
    if (!videoRef.current || !canvasRef.current) {
      return;
    }

    setProcessing(true);

    try {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, 'image/jpeg', 0.9);
      });

      const formData = new FormData();
      formData.append('file', blob, 'captura_manual.jpg');

      console.log('📸 Captura manual...');

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

      alert('✅ Imagen capturada y procesada correctamente');

    } catch (error) {
      console.error('❌ Error al procesar frame:', error);

      if (error.response?.status === 404) {
        alert('El endpoint de procesamiento no está disponible. Verifica que el API esté corriendo en ' + apiUrl);
      } else {
        alert('Error al procesar la imagen: ' + error.message);
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

  // Auto-escaneo continuo
  useEffect(() => {
    if (autoScanEnabled && cameraActive) {
      console.log('🚀 Iniciando auto-escaneo continuo...');

      scanIntervalRef.current = setInterval(() => {
        autoScan();
      }, scanInterval);

      return () => {
        if (scanIntervalRef.current) {
          clearInterval(scanIntervalRef.current);
          console.log('⏹️ Auto-escaneo detenido');
        }
      };
    }
  }, [autoScanEnabled, cameraActive, scanInterval]);

  // Cleanup al desmontar
  useEffect(() => {
    return () => {
      stopCamera();
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
      {/* Header */}
      <div className="border-b pb-4 mb-4">
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
      </div>

      {/* Video Feed */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-4">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-auto"
          style={{ maxHeight: '400px', display: cameraActive ? 'block' : 'none' }}
        />

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
              <p className="text-lg">Cámara apagada</p>
              <p className="text-sm mt-2">Presiona "Iniciar Cámara" para comenzar</p>
            </div>
          </div>
        )}

        {/* Overlay de estado */}
        {cameraActive && autoScanEnabled && (
          <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-2 text-center">
            <div className="flex items-center justify-center gap-4">
              <span className="animate-pulse">🔍 Escaneando automáticamente...</span>
              <div className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded">
                {detectionStats.scans} escaneos | {detectionStats.detections} detecciones
              </div>
            </div>
          </div>
        )}
        {cameraActive && processing && !autoScanEnabled && (
          <div className="absolute top-0 left-0 right-0 bg-blue-600 text-white px-4 py-2 text-center">
            <span className="animate-pulse">📸 Procesando imagen...</span>
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
              onClick={startCamera}
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
              Iniciar Cámara
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
                {processing ? 'Procesando...' : 'Capturar Frame'}
              </button>

              <button
                onClick={stopCamera}
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
                  <span className="font-bold text-gray-800">🔍 Escaneo Automático</span>
                  <p className="text-xs text-gray-600">Modo escáner QR: detecta placas instantáneamente</p>
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
                    <p className="text-2xl font-bold text-green-600">{detectionStats.scans}</p>
                    <p className="text-xs text-gray-600">Escaneos</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-blue-600">{detectionStats.detections}</p>
                    <p className="text-xs text-gray-600">Detectadas</p>
                  </div>
                  <div>
                    <p className="text-sm font-mono text-gray-700">{detectionStats.lastScan || '--:--:--'}</p>
                    <p className="text-xs text-gray-600">Último escaneo</p>
                  </div>
                </div>
                <p className="text-xs text-green-700 mt-2 text-center font-semibold">
                  ✅ Sistema escaneando continuamente - Muestra una placa al cuadro
                </p>
              </div>
            )}

            {!autoScanEnabled && (
              <p className="text-xs text-gray-600 text-center">
                💡 Activa el escaneo automático para detectar placas en tiempo real sin presionar botones
              </p>
            )}
          </div>
        )}

        {/* Última captura */}
        {lastCapture && (
          <div className="border-t pt-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Última Captura:</p>
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
