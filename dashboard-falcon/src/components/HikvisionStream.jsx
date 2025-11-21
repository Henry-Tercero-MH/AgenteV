import React from 'react';

// Componente para mostrar el stream MJPEG de Hikvision
function HikvisionStream({ streamUrl }) {
  return (
    <div className="rounded-lg shadow-lg bg-black p-2 flex flex-col items-center">
      <h3 className="text-lg font-bold text-white mb-2">Vista en Vivo - Cámara Hikvision</h3>
      {/* Si el stream es MJPEG, usar <img> */}
      <img
        src={streamUrl}
        alt="Stream Hikvision"
        style={{ width: '100%', maxWidth: 640, borderRadius: 8 }}
      />
    </div>
  );
}

export default HikvisionStream;
