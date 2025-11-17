import React from 'react';

/**
 * Componente para mostrar información completa del vehículo
 * Estilo "libro de registro" con todos los datos
 */
function VehicleInfoCard({ vehicleData, historial }) {
  if (!vehicleData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 h-full">
        <div className="flex flex-col items-center justify-center h-full text-gray-400">
          <svg
            className="w-24 h-24 mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p className="text-lg font-medium">Esperando detección...</p>
          <p className="text-sm mt-2">Los datos del vehículo aparecerán aquí</p>
        </div>
      </div>
    );
  }

  const { placa_info, registrada, mensaje, registro } = vehicleData;

  // Determinar color según el estado
  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'AUTORIZADO':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'NORMAL':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'RESTRINGIDO':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'SUSPENDIDO':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 h-full overflow-y-auto">
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Registro de Vehículo
        </h2>
      </div>

      {registrada ? (
        <>
          {/* Información Principal */}
          <div className="space-y-4">
            {/* Placa y Estado */}
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Placa</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {placa_info.placa}
                  </p>
                </div>
                <span
                  className={`px-4 py-2 rounded-full font-semibold text-sm border-2 ${getEstadoColor(
                    placa_info.estado
                  )}`}
                >
                  {placa_info.estado}
                </span>
              </div>
            </div>

            {/* Datos Básicos */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-xs text-blue-600 font-semibold mb-1">
                  Tipo de Vehículo
                </p>
                <p className="text-lg font-medium text-gray-900">
                  {placa_info.tipo_vehiculo}
                </p>
              </div>

              <div className="bg-blue-50 rounded-lg p-3">
                <p className="text-xs text-blue-600 font-semibold mb-1">
                  Departamento
                </p>
                <p className="text-lg font-medium text-gray-900">
                  {placa_info.departamento}
                </p>
              </div>
            </div>

            {/* Propietario */}
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-600 mb-1">Propietario</p>
              <p className="text-xl font-semibold text-gray-900">
                {placa_info.propietario}
              </p>
            </div>

            {/* Fechas */}
            <div className="grid grid-cols-2 gap-4">
              <div className="border rounded-lg p-3">
                <p className="text-xs text-gray-600 mb-1">Fecha Registro</p>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(placa_info.fecha_registro).toLocaleDateString(
                    'es-GT'
                  )}
                </p>
              </div>

              <div className="border rounded-lg p-3">
                <p className="text-xs text-gray-600 mb-1">Vigencia</p>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(placa_info.vigencia).toLocaleDateString('es-GT')}
                </p>
              </div>
            </div>

            {/* Observaciones */}
            {placa_info.observaciones && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800 font-semibold mb-1">
                  Observaciones
                </p>
                <p className="text-sm text-yellow-900">
                  {placa_info.observaciones}
                </p>
              </div>
            )}

            {/* Historial de Entradas */}
            {historial && historial.length > 0 && (
              <div className="mt-6 border-t pt-4">
                <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
                  <svg
                    className="w-5 h-5 text-gray-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  Historial de Visitas
                </h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {historial.slice(0, 10).map((reg, idx) => (
                    <div
                      key={idx}
                      className="flex justify-between items-center bg-gray-50 rounded p-3 text-sm"
                    >
                      <div>
                        <p className="font-medium text-gray-900">
                          {reg.tipo_evento}
                        </p>
                        <p className="text-xs text-gray-600">
                          {new Date(reg.timestamp).toLocaleString('es-GT')}
                        </p>
                      </div>
                      {reg.confianza && (
                        <span className="text-xs text-gray-500">
                          {(reg.confianza * 100).toFixed(1)}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        // Placa NO registrada
        <div className="text-center py-8">
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-6">
            <svg
              className="w-16 h-16 text-red-500 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h3 className="text-xl font-bold text-red-800 mb-2">
              Placa No Registrada
            </h3>
            <p className="text-lg font-mono font-bold text-red-900 mb-3">
              {registro?.placa}
            </p>
            <p className="text-sm text-red-700">{mensaje}</p>
            <div className="mt-4 text-xs text-red-600">
              <p>Detectado: {new Date(registro?.timestamp).toLocaleString('es-GT')}</p>
            </div>
          </div>
        </div>
      )}

      {/* Info de detección actual */}
      <div className="mt-6 pt-4 border-t">
        <p className="text-xs text-gray-500 text-center">
          Última actualización:{' '}
          {new Date(registro?.timestamp).toLocaleString('es-GT')}
        </p>
      </div>
    </div>
  );
}

export default VehicleInfoCard;
