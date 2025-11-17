import { useState } from 'react';

const API_URL = 'http://localhost:5001';

function ResultsTable({ resultados, onSelectImage }) {
  const [expandedRows, setExpandedRows] = useState(new Set());

  // Filtrar solo resultados con placas detectadas (cantidad_placas > 0)
  const resultadosConPlacas = resultados ? resultados.filter(r => r.cantidad_placas > 0) : [];

  if (!resultadosConPlacas || resultadosConPlacas.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center">
        <p className="text-gray-500">No hay placas detectadas para mostrar</p>
      </div>
    );
  }

  const toggleRow = (id) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedRows(newExpanded);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900">
          Placas Detectadas ({resultadosConPlacas.length} imágenes)
        </h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                #
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Imagen
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Placas
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Con Texto
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tiempo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Vista Previa
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Detalles
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {resultadosConPlacas.map((resultado) => (
              <>
                <tr key={resultado.id} className="hover:bg-gray-50 transition">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {resultado.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {resultado.nombre_imagen}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                      {resultado.cantidad_placas}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      resultado.placas_con_texto > 0 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {resultado.placas_con_texto}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {resultado.tiempo_procesamiento}s
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <button
                      onClick={() => onSelectImage(resultado)}
                      className="text-blue-600 hover:text-blue-800 font-medium"
                    >
                      Ver imagen
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <button
                      onClick={() => toggleRow(resultado.id)}
                      className="text-gray-600 hover:text-gray-900 font-medium flex items-center gap-1"
                    >
                      {expandedRows.has(resultado.id) ? (
                        <>
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                          </svg>
                          Ocultar
                        </>
                      ) : (
                        <>
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                          Ver detalle
                        </>
                      )}
                    </button>
                  </td>
                </tr>
                {expandedRows.has(resultado.id) && (
                  <tr>
                    <td colSpan="7" className="px-6 py-4 bg-gray-50">
                      <div className="space-y-3">
                        <h4 className="font-semibold text-gray-900">Detecciones:</h4>
                        {resultado.detecciones && resultado.detecciones.length > 0 ? (
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {resultado.detecciones.map((det, idx) => (
                              <div key={idx} className="bg-white border border-gray-200 rounded-lg p-3">
                                <div className="text-sm">
                                  <p className="font-semibold text-gray-900">
                                    Placa #{idx + 1}: {det.texto || '(sin texto)'}
                                  </p>
                                  <p className="text-gray-600">
                                    Confianza detección: {(det.confianza_deteccion * 100).toFixed(1)}%
                                  </p>
                                  <p className="text-gray-600">
                                    Confianza OCR: {(det.confianza_ocr * 100).toFixed(1)}%
                                  </p>
                                  {det.imagen_placa && (
                                    <img
                                      src={`${API_URL}/outputs/${det.imagen_placa}`}
                                      alt={`Placa ${idx + 1}`}
                                      className="mt-2 w-full h-auto rounded border border-gray-300"
                                    />
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-500">No se detectaron placas en esta imagen</p>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ResultsTable;
