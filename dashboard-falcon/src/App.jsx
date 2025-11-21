import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import StatisticsCards from './components/StatisticsCards';
import ProcessingTimeChart from './components/ProcessingTimeChart';
import ResultsTable from './components/ResultsTable';
import Header from './components/Header';
import LoadingSpinner from './components/LoadingSpinner';
import PlateDisplay from './components/PlateDisplay';
import PlateDetectionCard from './components/PlateDetectionCard';
import VehicleInfoCard from './components/VehicleInfoCard';
import CameraCapture from './components/CameraCapture';
import HlsStream from './components/HlsStream';

const API_URL = 'http://localhost:8001';
const WS_URL = 'ws://localhost:8001/ws';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedImage, setSelectedImage] = useState(null);

  // Estados para el control de garita
  const [currentDetection, setCurrentDetection] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [backendConnected, setBackendConnected] = useState(false);
  const wsRef = useRef(null);

  // URL del stream HLS (canal 102)

  // Conectar WebSocket
  useEffect(() => {
    connectWebSocket();
    fetchHistorial();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    fetchData();
  }, []);

  // Verificar conexión del backend cada 30 segundos
  useEffect(() => {
    checkBackendConnection();
    const interval = setInterval(checkBackendConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  const connectWebSocket = () => {
    try {
      // Evitar múltiples intentos simultáneos
      if (wsRef.current &&
          (wsRef.current.readyState === WebSocket.CONNECTING ||
           wsRef.current.readyState === WebSocket.OPEN)) {
        return;
      }

      console.log('🔌 Intentando conectar WebSocket...');
      const ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        setWsConnected(true);
        // Enviar ping cada 30 segundos para mantener conexión
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000);
        ws.pingInterval = pingInterval;
      };

      ws.onmessage = (event) => {
        try {
          // Ignorar mensajes "pong" del servidor
          if (event.data === 'pong') {
            return;
          }
          const message = JSON.parse(event.data);
          if (message.tipo === 'nueva_deteccion') {
            console.log('🚗 Nueva detección recibida:', message.data);
            setCurrentDetection(message.data);
            // Actualizar historial
            fetchHistorial();
            // Obtener historial específico de esta placa
            if (message.data.registrada) {
              fetchHistorialPlaca(message.data.registro.placa);
            }
          }
        } catch (error) {
          // Silenciar errores de parseo en desarrollo (React StrictMode)
          if (!event.data.includes('pong')) {
            console.warn('⚠️ Error procesando mensaje WebSocket:', error.message);
          }
        }
      };

      ws.onerror = (error) => {
        console.warn('⚠️ Error de WebSocket (posiblemente backend no está corriendo):', error);
        setWsConnected(false);
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket desconectado');
        setWsConnected(false);
        if (ws.pingInterval) {
          clearInterval(ws.pingInterval);
        }

        // Solo reconectar si no fue cierre limpio
        if (event.code !== 1000) {
          setTimeout(() => {
            console.log('🔄 Intentando reconectar WebSocket...');
            connectWebSocket();
          }, 3000);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error al crear conexión WebSocket:', error);
      setWsConnected(false);
    }
  };

  const handleScanImages = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_URL}/api/procesar-batch`);
      console.log('Procesamiento iniciado:', response.data);

      // Esperar 5 segundos antes de refrescar
      setTimeout(() => {
        fetchData();
      }, 5000);

      alert('Procesamiento batch iniciado. Los resultados se actualizarán automáticamente.');
    } catch (err) {
      console.error('Error al iniciar procesamiento:', err);
      alert('Error al iniciar el procesamiento batch');
      setLoading(false);
    }
  };

  const fetchHistorial = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/registros/historial`);
      setHistorial(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error al cargar historial:', error);
      setHistorial([]);
    }
  };

  const fetchHistorialPlaca = async (placa) => {
    try {
      const response = await axios.get(`${API_URL}/api/registros/placa/${placa}`);
      console.log('Historial de placa:', response.data);
    } catch (error) {
      console.error('Error al cargar historial de placa:', error);
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/resultados`);
      setData(response.data);
      setError(null);
      setBackendConnected(true);
    } catch (err) {
      console.error('Error al cargar datos:', err);
      setError(
        err.response?.status === 404
          ? 'No se encontraron resultados. Ejecuta primero: python process_batch.py'
          : 'Error al conectar con el servidor. Asegúrate de que la API esté corriendo en el puerto 8001.'
      );
      setBackendConnected(false);
    } finally {
      setLoading(false);
    }
  };

  const checkBackendConnection = async () => {
    try {
      await axios.get(`${API_URL}/health`, { timeout: 5000 });
      setBackendConnected(true);
    } catch (error) {
      setBackendConnected(false);
    }
  };

  const handleCameraDetection = (detectionData) => {
    console.log('🎥 Detección desde cámara:', detectionData);

    // Si hay detecciones exitosas, el WebSocket ya actualizará el dashboard
    // Opcionalmente podemos actualizar el historial manualmente
    if (detectionData.success && detectionData.detecciones?.length > 0) {
      fetchHistorial();
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
          <div className="text-center">
            <svg className="mx-auto h-16 w-16 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="mt-4 text-xl font-bold text-gray-900">Error</h2>
            <p className="mt-2 text-gray-600">{error}</p>
            <button
              onClick={fetchData}
              className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header con indicador WebSocket */}
      <header className="bg-white shadow-md">
        <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <h1 className="text-3xl font-bold text-gray-900">
                🦅 Falcon EPSA - Control de Garita
              </h1>
              {/* Indicadores de conexión */}
              <div className="flex items-center gap-4">
                {/* WebSocket */}
                <div className="flex items-center gap-2">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      wsConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                    }`}
                    title={wsConnected ? 'WebSocket conectado' : 'WebSocket desconectado'}
                  />
                  <span className={`text-sm font-bold ${wsConnected ? 'text-green-700' : 'text-red-700'}`}>
                    WS: {wsConnected ? 'Conectado' : 'Desconectado'}
                  </span>
                </div>
                {/* Backend API */}
                <div className="flex items-center gap-2">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      backendConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
                    }`}
                    title={backendConnected ? 'Backend conectado' : 'Backend desconectado'}
                  />
                  <span className={`text-sm font-bold ${backendConnected ? 'text-green-700' : 'text-yellow-700'}`}>
                    API: {backendConnected ? 'OK' : 'Verificando...'}
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={fetchHistorial}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              🔄 Actualizar
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Componente de Cámara */}
        <div className="mb-8">
          <CameraCapture
            apiUrl={API_URL}
            onDetection={handleCameraDetection}
          />
        </div>

        {/* Layout principal: Placa (izquierda) + Datos (derecha) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Lado Izquierdo: Placa Detectada */}
          <div className="h-[600px]">
            <PlateDetectionCard
              detectionData={currentDetection}
              apiUrl={API_URL}
            />
          </div>

          {/* Lado Derecho: Datos del Vehículo */}
          <div className="h-[600px]">
            <VehicleInfoCard
              vehicleData={currentDetection}
              historial={historial}
            />
          </div>
        </div>

        {/* Sección de historial completo */}
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center gap-2">
              <svg
                className="w-7 h-7 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              Historial Completo de Registros
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Placa
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Evento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha y Hora
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estado
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {!Array.isArray(historial) || historial.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                        No hay registros todavía
                      </td>
                    </tr>
                  ) : (
                    historial.map((reg, idx) => (
                      <tr key={reg.id || idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {reg.id || idx + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-bold text-gray-900">
                          {reg.placa || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                            {reg.tipo_evento || 'ENTRADA'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                          {reg.timestamp ? new Date(reg.timestamp).toLocaleString('es-GT') : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {reg.registrada ? (
                            <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                              ✓ Registrada
                            </span>
                          ) : (
                            <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                              ✗ No registrada
                            </span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Sección adicional: Estadísticas y gráficos (colapsable) */}
        {data && (
          <details className="mb-8">
            <summary className="cursor-pointer bg-white rounded-lg shadow-lg p-4 hover:bg-gray-50 transition">
              <span className="text-lg font-bold text-gray-800">
                📊 Ver Estadísticas y Análisis Detallado
              </span>
            </summary>
            <div className="mt-4 space-y-6">
              <StatisticsCards metadata={data?.metadatos} />
              <ProcessingTimeChart resultados={data?.resultados} />
              <ResultsTable
                resultados={data?.resultados}
                onSelectImage={setSelectedImage}
              />
            </div>
          </details>
        )}
      </main>

      {/* Modal de imagen ampliada (si está seleccionada) */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-4xl w-full bg-white rounded-lg p-4" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold text-gray-900">{selectedImage.nombre_imagen}</h3>
              <button
                onClick={() => setSelectedImage(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <img
              src={`${API_URL}/${selectedImage.ruta_imagen_anotada}`}
              alt={selectedImage.nombre_imagen}
              className="w-full h-auto rounded"
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
