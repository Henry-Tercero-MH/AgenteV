import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5001';

function PlateDisplay({ resultados }) {
  const [currentPlateIndex, setCurrentPlateIndex] = useState(0);
  const [allPlates, setAllPlates] = useState([]);
  const [plateValidation, setPlateValidation] = useState(null);

  // Extraer todas las placas con texto de los resultados
  useEffect(() => {
    if (!resultados || resultados.length === 0) return;

    const plates = [];
    resultados.forEach((resultado) => {
      if (resultado.detecciones && resultado.detecciones.length > 0) {
        resultado.detecciones.forEach((deteccion) => {
          if (deteccion.texto) {
            plates.push({
              texto: deteccion.texto,
              imagen: deteccion.imagen_placa,
              confianza_deteccion: deteccion.confianza_deteccion,
              confianza_ocr: deteccion.confianza_ocr,
              imagen_original: resultado.nombre_imagen,
              timestamp: resultado.timestamp
            });
          }
        });
      }
    });

    setAllPlates(plates);
  }, [resultados]);

  const currentPlate = allPlates[currentPlateIndex];

  // Validar la placa actual cuando cambie
  useEffect(() => {
    if (!currentPlate) return;

    const validatePlate = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/placas/validar/${currentPlate.texto}`);
        setPlateValidation(response.data);
      } catch (error) {
        console.error('Error al validar placa:', error);
        setPlateValidation(null);
      }
    };

    validatePlate();
  }, [currentPlateIndex, allPlates]);

  // Cambiar de placa cada 3 segundos
  useEffect(() => {
    if (allPlates.length === 0) return;

    const interval = setInterval(() => {
      setCurrentPlateIndex((prevIndex) => (prevIndex + 1) % allPlates.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [allPlates]);

  if (allPlates.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <p className="text-gray-500">No hay placas detectadas para mostrar</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="text-center mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Placa Detectada</h2>
        <p className="text-sm text-gray-500 mt-1">
          {currentPlateIndex + 1} de {allPlates.length} placas
        </p>
      </div>

      {/* Placa de Guatemala - Diseño realista */}
      <div className="relative mx-auto max-w-md">
        {/* Contenedor de la placa con animación */}
        <div className="plate-container transform transition-all duration-500 hover:scale-105">
          {/* Placa de Guatemala */}
          <div className="relative bg-gradient-to-b from-white to-gray-100 rounded-lg shadow-2xl border-4 border-gray-800 p-6 overflow-hidden">
            {/* Fondo con patrón de Guatemala */}
            <div className="absolute inset-0 opacity-5">
              <div className="w-full h-full" style={{
                backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,.1) 10px, rgba(0,0,0,.1) 20px)'
              }}></div>
            </div>

            {/* Cabecera de la placa */}
            <div className="relative text-center mb-3">
              <div className="flex items-center justify-center gap-2 mb-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-xs">GT</span>
                </div>
                <h3 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                  República de Guatemala
                </h3>
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-xs">GT</span>
                </div>
              </div>
            </div>

            {/* Número de placa - Texto grande y centrado */}
            <div className="relative bg-white rounded-md shadow-inner border-2 border-gray-300 p-4 mb-3">
              <div className="text-center">
                <span className="text-5xl font-black tracking-widest text-gray-900 font-mono plate-text">
                  {currentPlate.texto}
                </span>
              </div>
            </div>

            {/* Imagen de la placa detectada */}
            {currentPlate.imagen && (
              <div className="mt-3 rounded-md overflow-hidden border-2 border-gray-300">
                <img
                  src={`${API_URL}/outputs/${currentPlate.imagen}`}
                  alt={`Placa ${currentPlate.texto}`}
                  className="w-full h-auto"
                />
              </div>
            )}

            {/* Validación de Placa */}
            {plateValidation && (
              <div className={`mt-3 rounded-lg p-3 ${
                plateValidation.registrada
                  ? plateValidation.estado === 'AUTORIZADO' ? 'bg-green-50 border-2 border-green-500'
                  : plateValidation.estado === 'SUSPENDIDO' ? 'bg-red-50 border-2 border-red-500'
                  : plateValidation.estado === 'RESTRINGIDO' ? 'bg-yellow-50 border-2 border-yellow-500'
                  : 'bg-blue-50 border-2 border-blue-500'
                  : 'bg-gray-50 border-2 border-gray-400'
              }`}>
                <div className="text-center">
                  {plateValidation.registrada ? (
                    <>
                      <div className="flex items-center justify-center gap-2 mb-2">
                        <svg className={`h-6 w-6 ${
                          plateValidation.estado === 'AUTORIZADO' ? 'text-green-600'
                          : plateValidation.estado === 'SUSPENDIDO' ? 'text-red-600'
                          : plateValidation.estado === 'RESTRINGIDO' ? 'text-yellow-600'
                          : 'text-blue-600'
                        }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className={`font-bold text-sm ${
                          plateValidation.estado === 'AUTORIZADO' ? 'text-green-700'
                          : plateValidation.estado === 'SUSPENDIDO' ? 'text-red-700'
                          : plateValidation.estado === 'RESTRINGIDO' ? 'text-yellow-700'
                          : 'text-blue-700'
                        }`}>
                          {plateValidation.estado}
                        </span>
                      </div>
                      <div className="text-xs space-y-1">
                        <p><span className="font-semibold">Tipo:</span> {plateValidation.tipo_vehiculo}</p>
                        <p><span className="font-semibold">Propietario:</span> {plateValidation.propietario}</p>
                        <p><span className="font-semibold">Departamento:</span> {plateValidation.departamento}</p>
                        <p><span className="font-semibold">Vigencia:</span> {plateValidation.vigencia}</p>
                        <p className="text-gray-600 italic">{plateValidation.observaciones}</p>
                      </div>
                    </>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      <svg className="h-6 w-6 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <span className="font-bold text-sm text-gray-700">NO REGISTRADA</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Información adicional */}
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
              <div className="bg-gray-50 rounded p-2">
                <span className="text-gray-600">Detección:</span>
                <span className="ml-1 font-bold text-green-600">
                  {(currentPlate.confianza_deteccion * 100).toFixed(1)}%
                </span>
              </div>
              <div className="bg-gray-50 rounded p-2">
                <span className="text-gray-600">OCR:</span>
                <span className="ml-1 font-bold text-blue-600">
                  {(currentPlate.confianza_ocr * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Pie de la placa */}
            <div className="mt-3 text-center">
              <p className="text-xs text-gray-500">
                Origen: {currentPlate.imagen_original}
              </p>
            </div>
          </div>
        </div>

        {/* Indicadores de navegación */}
        <div className="flex justify-center mt-4 gap-1">
          {allPlates.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentPlateIndex(index)}
              className={`w-2 h-2 rounded-full transition-all duration-300 ${
                index === currentPlateIndex
                  ? 'bg-blue-600 w-8'
                  : 'bg-gray-300 hover:bg-gray-400'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Controles */}
      <div className="flex justify-center gap-4 mt-6">
        <button
          onClick={() => setCurrentPlateIndex((prev) => (prev - 1 + allPlates.length) % allPlates.length)}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition flex items-center gap-2"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Anterior
        </button>
        <button
          onClick={() => setCurrentPlateIndex((prev) => (prev + 1) % allPlates.length)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition flex items-center gap-2"
        >
          Siguiente
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}

export default PlateDisplay;
