# Dashboard Falcon EPSA - Detección de Placas

Dashboard profesional en React.js 18 + TailwindCSS + FastAPI para visualizar resultados de detección de placas con YOLO + PaddleOCR.

## Características

- **Estadísticas en tiempo real**: Total de imágenes, placas detectadas, tasa de éxito OCR
- **Gráficos interactivos**: Visualización de tiempos de procesamiento con Recharts
- **Tabla de resultados**: Vista detallada de cada imagen procesada
- **Visualización de imágenes**: Modal para ampliar imágenes anotadas
- **Detalles de placas**: Visualización individual de cada placa detectada con su confianza
- **Diseño responsive**: Compatible con dispositivos móviles, tablets y escritorio

## Tecnologías Utilizadas

### Backend
- **FastAPI**: API REST moderna y rápida
- **Python 3.14**: Procesamiento con YOLO + PaddleOCR
- **Uvicorn**: Servidor ASGI de alto rendimiento

### Frontend
- **React.js 18**: Librería de UI moderna
- **Vite**: Build tool ultra-rápido
- **TailwindCSS**: Framework CSS utility-first
- **Recharts**: Librería de gráficos para React
- **Axios**: Cliente HTTP para consumir la API

## Instalación

### Requisitos Previos
- Python 3.14+
- Node.js 16+ y npm
- Modelos YOLO (`best.pt`, `best_truck.pt`)

### Instalación de Dependencias Python

```bash
pip install fastapi uvicorn python-multipart
```

### Instalación de Dependencias React

```bash
cd dashboard-falcon
npm install
```

## Uso del Sistema

### Paso 1: Procesar Imágenes

Ejecuta el script de procesamiento batch para generar los datos:

```bash
python process_batch.py --input Inputs --output Outputs --model best.pt --truck-model best_truck.pt
```

Esto generará el archivo `Outputs/resultados_dashboard.json` con todas las métricas.

### Paso 2: Iniciar la API Backend

En una terminal:

```bash
python api_dashboard.py
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

### Paso 3: Iniciar el Dashboard React

En otra terminal:

```bash
cd dashboard-falcon
npm run dev
```

El dashboard estará disponible en: **http://localhost:5173**

## Estructura del Proyecto

```
falconEpsa/
├── Inputs/                    # Imágenes de entrada
├── Outputs/                   # Resultados procesados
│   └── resultados_dashboard.json  # Datos para el dashboard
├── dashboard-falcon/          # Proyecto React
│   ├── src/
│   │   ├── components/       # Componentes React
│   │   │   ├── Header.jsx
│   │   │   ├── StatisticsCards.jsx
│   │   │   ├── ProcessingTimeChart.jsx
│   │   │   ├── ResultsTable.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── App.jsx           # Componente principal
│   │   └── index.css         # Estilos con Tailwind
│   └── package.json
├── process_batch.py           # Script de procesamiento batch
├── api_dashboard.py           # API FastAPI
├── app.py                     # Script CLI original
└── README.md                  # Este archivo
```

## API Endpoints

### GET /api/resultados
Obtiene todos los resultados del procesamiento batch.

**Respuesta:**
```json
{
  "metadatos": {
    "fecha_procesamiento": "2025-11-16T...",
    "total_imagenes": 13,
    "tiempo_total": 45.2,
    "tiempo_promedio": 3.48,
    "total_placas_detectadas": 34,
    "total_placas_con_texto": 25,
    "tasa_exito_ocr": 73.5
  },
  "resultados": [...]
}
```

### GET /api/estadisticas
Obtiene solo las estadísticas generales.

### GET /api/resultados/{imagen_id}
Obtiene el resultado de una imagen específica por ID.

### GET /outputs/{nombre}
Sirve imágenes procesadas.

### GET /inputs/{nombre}
Sirve imágenes originales.

## Componentes del Dashboard

### Header
- Título del dashboard
- Fecha de última actualización
- Botón de actualización

### StatisticsCards
- Total de imágenes procesadas
- Total de placas detectadas
- Tasa de éxito OCR
- Tiempo promedio de procesamiento

### ProcessingTimeChart
- Gráfico de barras con tiempos de procesamiento
- Comparativa de placas detectadas por imagen

### ResultsTable
- Tabla interactiva con todos los resultados
- Filas expandibles para ver detalles de cada placa
- Botón para ampliar imágenes
- Vista previa de placas recortadas

## Scripts de Uso Rápido

### Procesar una sola imagen
```bash
python app.py --source Inputs/test.jpg --model best.pt --truck-model best_truck.pt --output Outputs --conf 0.3
```

### Procesar todas las imágenes
```bash
python process_batch.py
```

### Iniciar todo el sistema (Windows)
Crea un archivo `start_dashboard.bat`:

```batch
@echo off
echo Iniciando Falcon EPSA Dashboard...

echo [1/3] Procesando imágenes...
python process_batch.py

echo [2/3] Iniciando API...
start cmd /k python api_dashboard.py

echo [3/3] Iniciando Dashboard...
cd dashboard-falcon
start cmd /k npm run dev

echo Dashboard iniciado! Abre http://localhost:5173
```

## Personalización

### Cambiar Puerto del API
Edita `api_dashboard.py` línea final:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Cambia 8000 por tu puerto
```

### Cambiar URL del API en React
Edita `dashboard-falcon/src/App.jsx`:
```javascript
const API_URL = 'http://localhost:8000';  // Cambia por tu URL
```

### Modificar Estilos
Los estilos están en:
- `dashboard-falcon/src/index.css` - Estilos globales
- `dashboard-falcon/tailwind.config.js` - Configuración de Tailwind

## Solución de Problemas

### Error: "No se encontraron resultados"
Ejecuta primero `python process_batch.py` para generar los datos.

### Error: "Error al conectar con el servidor"
Asegúrate de que la API esté corriendo en `http://localhost:8000`.

### Imágenes no se cargan
Verifica que las rutas en `Outputs/` y `Inputs/` sean correctas.

### Error en npm install
Borra `node_modules` y `package-lock.json`, luego ejecuta `npm install` nuevamente.

## Licencia

MIT - Falcon EPSA 2025

## Autor

Sistema desarrollado para detección automática de placas vehiculares con YOLO v8 + PaddleOCR.
