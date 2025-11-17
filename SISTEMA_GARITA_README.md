# 🦅 Sistema de Control de Garita - Falcon EPSA

Sistema de detección y registro automático de placas vehiculares para control de garita de seguridad.

## 📋 Características

- ✅ **Detección automática** de placas con YOLO
- ✅ **Registro automático** de entradas/salidas
- ✅ **Validación en tiempo real** contra base de datos
- ✅ **WebSocket** para actualizaciones instantáneas
- ✅ **Dashboard interactivo** con React
- ✅ **Historial completo** de registros
- ✅ **Información detallada** del vehículo si está registrado

## 🏗️ Arquitectura

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────┐
│  Detector YOLO  │ ──────> │   API REST   │ <────── │  Dashboard  │
│  (Python)       │         │  (FastAPI)   │         │  (React)    │
└─────────────────┘         └──────────────┘         └─────────────┘
                                   │                         ▲
                                   │                         │
                                   ▼                         │
                            ┌──────────────┐                 │
                            │  Base de     │                 │
                            │  Datos JSON  │                 │
                            └──────────────┘                 │
                                   │                         │
                                   └─── WebSocket ───────────┘
                                   (Tiempo Real)
```

## 🚀 Inicio Rápido

### 1. Iniciar el Backend (API)

```bash
# Terminal 1 - Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Iniciar API
python api_dashboard.py
```

El API estará corriendo en: `http://localhost:8001`
- Documentación: http://localhost:8001/docs
- WebSocket: ws://localhost:8001/ws

### 2. Iniciar el Dashboard React

```bash
# Terminal 2 - Ir a la carpeta del dashboard
cd dashboard-falcon

# Instalar dependencias (solo la primera vez)
npm install

# Iniciar dashboard
npm run dev
```

El dashboard estará en: `http://localhost:5173`

### 3. Probar el Sistema

```bash
# Terminal 3 - Script de prueba
python test_garita.py
```

Opciones disponibles:
1. Simular detección de placa registrada
2. Simular detección de placa NO registrada
3. Simular múltiples detecciones automáticas
4. Ver historial de registros

## 📱 Uso del Dashboard

### Layout Principal

El dashboard se divide en dos secciones principales:

#### **Lado Izquierdo: Placa Detectada**
- Estado de registro (REGISTRADA / NO REGISTRADA)
- Número de placa en formato visual
- Imagen de la placa detectada
- Confianza de detección
- Fecha y hora de la detección
- Tipo de evento (ENTRADA/SALIDA)

#### **Lado Derecho: Datos del Vehículo**

**Si está registrada:**
- Información del propietario
- Tipo de vehículo
- Departamento
- Estado (AUTORIZADO, RESTRINGIDO, SUSPENDIDO, NORMAL)
- Fechas de registro y vigencia
- Observaciones
- Historial de visitas

**Si NO está registrada:**
- Alerta de placa no registrada
- Opción para registrar

### Historial Completo

Tabla con todos los registros:
- ID del registro
- Placa detectada
- Tipo de evento (ENTRADA/SALIDA)
- Fecha y hora
- Estado (registrada o no)

## 🔌 API Endpoints

### WebSocket
```
ws://localhost:8001/ws
```
Recibe notificaciones en tiempo real cuando se detecta una placa.

### POST /api/registros/entrada
Registra una nueva detección de placa.

**Request:**
```json
{
  "placa": "ABC123",
  "confianza": 0.95,
  "imagen_path": "Outputs/placa.jpg"
}
```

**Response (placa registrada):**
```json
{
  "registro": {
    "id": 1,
    "placa": "ABC123",
    "timestamp": "2025-11-16T10:30:00",
    "tipo_evento": "ENTRADA",
    "registrada": true
  },
  "placa_info": {
    "placa": "ABC123",
    "propietario": "Juan Pérez",
    "tipo_vehiculo": "PARTICULAR",
    "estado": "AUTORIZADO",
    "departamento": "Guatemala",
    "vigencia": "2025-12-31"
  },
  "registrada": true,
  "mensaje": "Vehículo registrado"
}
```

### GET /api/registros/historial?limit=50
Obtiene el historial de registros.

### GET /api/registros/placa/{placa}
Obtiene el historial de una placa específica.

### GET /api/placas/validar/{placa}
Valida si una placa existe en la base de datos.

## 📁 Estructura de Archivos

```
falconEpsa/
├── api_dashboard.py          # API FastAPI con WebSocket
├── test_garita.py            # Script de prueba
├── database/
│   ├── placas_db.json        # Base de datos de placas
│   └── logs_entrada_salida.json  # Logs de registros
├── dashboard-falcon/         # Dashboard React
│   ├── src/
│   │   ├── App.jsx           # Componente principal
│   │   └── components/
│   │       ├── PlateDetectionCard.jsx    # Muestra placa detectada
│   │       └── VehicleInfoCard.jsx       # Muestra info del vehículo
│   └── package.json
└── models/
    └── detector.py           # Detector YOLO
```

## 🔄 Flujo de Trabajo

1. **Detección**
   - El detector YOLO identifica una placa en una imagen
   - Extrae el texto de la placa

2. **Registro**
   - Se envía al endpoint POST /api/registros/entrada
   - Se valida si la placa existe en la DB
   - Se guarda en logs_entrada_salida.json

3. **Notificación**
   - El API envía notificación por WebSocket
   - Todos los dashboards conectados se actualizan en tiempo real

4. **Visualización**
   - Dashboard muestra la placa detectada (izquierda)
   - Dashboard muestra los datos del vehículo (derecha)
   - Se actualiza el historial completo

## 🎯 Casos de Uso

### Caso 1: Vehículo Autorizado
1. Detector identifica placa "PO28GHQ"
2. Sistema consulta DB y encuentra que es AUTORIZADO
3. Dashboard muestra datos completos del vehículo
4. Guarda registro de entrada con timestamp

### Caso 2: Vehículo Restringido
1. Detector identifica placa "GC987D"
2. Sistema consulta DB y encuentra que es RESTRINGIDO
3. Dashboard muestra alerta visual (amarillo)
4. Guarda registro y muestra observaciones

### Caso 3: Placa No Registrada
1. Detector identifica placa "XYZ999"
2. Sistema no encuentra la placa en DB
3. Dashboard muestra alerta de NO REGISTRADA (rojo)
4. Guarda registro como "no registrada"

## 🛠️ Integración con el Detector

Para integrar el detector YOLO real:

```python
from models.detector import PlateDetector
import requests

detector = PlateDetector(model_path="best.pt")

# Detectar placa
imagen = "path/to/image.jpg"
resultados = detector.detectar(imagen)

for deteccion in resultados:
    # Enviar al API
    payload = {
        "placa": deteccion['texto'],
        "confianza": deteccion['confianza'],
        "imagen_path": deteccion['imagen_path']
    }

    response = requests.post(
        "http://localhost:8001/api/registros/entrada",
        json=payload
    )

    print(f"Placa registrada: {response.json()}")
```

## 📊 Base de Datos

### placas_db.json
```json
{
  "metadata": {
    "fecha_generacion": "2025-11-16T14:42:18",
    "total_placas": 74,
    "version": "1.0"
  },
  "placas": [
    {
      "id": 1,
      "placa": "PO28GHQ",
      "estado": "AUTORIZADO",
      "tipo_vehiculo": "COMERCIAL",
      "propietario": "Empresa XYZ",
      "departamento": "Guatemala",
      "vigencia": "2025-12-31"
    }
  ]
}
```

### logs_entrada_salida.json
```json
{
  "registros": [
    {
      "id": 1,
      "placa": "PO28GHQ",
      "timestamp": "2025-11-16T10:30:00",
      "tipo_evento": "ENTRADA",
      "registrada": true
    }
  ]
}
```

## 🔧 Configuración

### Puertos
- API Backend: `8001`
- Dashboard React: `5173` (Vite default)
- WebSocket: `8001/ws`

### CORS
El API permite todas las origins por defecto (desarrollo).
Para producción, edita en `api_dashboard.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Solo tu dashboard
    ...
)
```

## 🐛 Troubleshooting

### Dashboard no se conecta al API
- Verifica que el API esté corriendo en puerto 8001
- Revisa `API_URL` en `dashboard-falcon/src/App.jsx`

### WebSocket no conecta
- Verifica que usas `ws://` y no `wss://`
- Revisa la consola del navegador para errores

### No se guardan registros
- Verifica que exista la carpeta `database/`
- Revisa permisos de escritura

## 📝 Notas

- El sistema usa una DB JSON simulada para desarrollo
- Para producción, considera migrar a PostgreSQL o MongoDB
- El WebSocket se reconecta automáticamente si se pierde la conexión
- Los registros se guardan inmediatamente en el archivo JSON

## 🤝 Contribuir

Para agregar nuevas funcionalidades:
1. Modifica el backend en `api_dashboard.py`
2. Actualiza los componentes React en `dashboard-falcon/src/components/`
3. Prueba con `test_garita.py`

---

**Desarrollado para Falcon EPSA - Sistema de Control de Garita**
