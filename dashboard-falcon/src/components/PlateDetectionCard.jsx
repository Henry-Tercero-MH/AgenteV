import React from 'react';

/**
 * Componente para mostrar la placa detectada en tiempo real
 * Lado izquierdo del dashboard
 */
function PlateDetectionCard({ detectionData, apiUrl }) {
  if (!detectionData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 h-full">
        <div className="flex flex-col items-center justify-center h-full text-gray-400">
          <svg
            className="w-32 h-32 mb-4 animate-pulse"
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
          <p className="text-2xl font-bold">Esperando detección...</p>
          <p className="text-sm mt-2">El sistema está listo para detectar placas</p>
        </div>
      </div>
    );
  }

  const { registro, registrada } = detectionData;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full flex flex-col">
      {/* Header */}
      <div className="border-b pb-4 mb-4">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <svg
            className="w-8 h-8 text-green-600"
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
          Placa Detectada
        </h2>
      </div>

      {/* Placa Display */}
      <div className="flex-1 flex flex-col justify-center items-center mb-6">
        {/* Status Badge */}
        <div className="mb-4">
          {registrada ? (
            <div className="flex items-center gap-2 bg-green-100 text-green-800 px-6 py-3 rounded-full border-2 border-green-300">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="font-bold text-lg">REGISTRADA</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 bg-red-100 text-red-800 px-6 py-3 rounded-full border-2 border-red-300">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
              <span className="font-bold text-lg">NO REGISTRADA</span>
            </div>
          )}
        </div>

        {/* Placa número - Estilo matrícula */}
        <div className="bg-gradient-to-b from-white to-gray-100 border-4 border-gray-800 rounded-lg px-8 py-6 mb-6 shadow-xl">
          <div className="text-center">
            <p className="text-xs text-gray-600 mb-1 font-semibold">GUATEMALA</p>
            <p className="text-6xl font-black text-gray-900 tracking-wider font-mono">
              {registro?.placa}
            </p>
          </div>
        </div>

        {/* Imagen de la placa (si está disponible) */}
        {registro?.imagen_path && (
          <div className="w-full max-w-md">
            <img
              src={`${apiUrl}/${registro.imagen_path}`}
              alt="Placa detectada"
              className="w-full h-auto rounded-lg shadow-lg border-2 border-gray-200"
              onError={(e) => {
                e.target.style.display = 'none';
              }}
            />
          </div>
        )}

        {/* Confianza de detección */}
        {registro?.confianza && (
          <div className="mt-4">
            <div className="bg-blue-50 rounded-lg px-6 py-3 border border-blue-200">
              <p className="text-sm text-blue-700 font-semibold mb-1">
                Confianza de Detección
              </p>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-blue-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-blue-600 h-full transition-all duration-500"
                    style={{ width: `${registro.confianza * 100}%` }}
                  />
                </div>
                <span className="text-xl font-bold text-blue-900">
                  {(registro.confianza * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Información de timestamp */}
      <div className="border-t pt-4">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-gray-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-medium">Fecha y Hora</span>
            </div>
            <span className="font-mono text-gray-900 font-semibold">
              {new Date(registro?.timestamp).toLocaleString('es-GT', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
              })}
            </span>
          </div>
        </div>

        {/* Tipo de evento */}
        <div className="mt-3 flex items-center justify-center gap-2">
          <svg
            className="w-5 h-5 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
            />
          </svg>
          <span className="text-lg font-bold text-green-700">
            {registro?.tipo_evento || 'ENTRADA'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default PlateDetectionCard;
