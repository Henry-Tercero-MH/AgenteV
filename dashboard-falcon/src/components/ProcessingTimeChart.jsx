import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function ProcessingTimeChart({ resultados }) {
  if (!resultados || resultados.length === 0) return null;

  // Preparar datos para el gráfico
  const chartData = resultados.map(r => ({
    nombre: r.nombre_imagen.length > 15 ? r.nombre_imagen.substring(0, 12) + '...' : r.nombre_imagen,
    tiempo: r.tiempo_procesamiento,
    placas: r.cantidad_placas
  }));

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Tiempos de Procesamiento</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="nombre"
            angle={-45}
            textAnchor="end"
            height={100}
            interval={0}
          />
          <YAxis label={{ value: 'Tiempo (segundos)', angle: -90, position: 'insideLeft' }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
            formatter={(value, name) => [
              name === 'tiempo' ? `${value}s` : value,
              name === 'tiempo' ? 'Tiempo' : 'Placas'
            ]}
          />
          <Legend />
          <Bar dataKey="tiempo" fill="#3b82f6" name="Tiempo (s)" />
          <Bar dataKey="placas" fill="#10b981" name="Placas detectadas" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ProcessingTimeChart;
