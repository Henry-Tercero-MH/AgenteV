function Header({ metadata, onRefresh }) {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">
              Falcon EPSA - Dashboard de Detección de Placas
            </h1>
            <p className="mt-1 text-blue-100">
              {metadata?.fecha_procesamiento ?
                `Última actualización: ${new Date(metadata.fecha_procesamiento).toLocaleString('es-ES')}`
                : 'Sistema de detección con YOLO + PaddleOCR'}
            </p>
          </div>
          <button
            onClick={onRefresh}
            className="bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Actualizar
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
