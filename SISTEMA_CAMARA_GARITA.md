# 🎥 Sistema de Cámara para Control de Garita

Sistema completo de detección automática de placas en tiempo real con cámara integrada.

## 🚀 Características del Sistema

- ✅ **Cámara en tiempo real** (webcam o IP camera)
- ✅ **Detección automática** de placas con YOLO
- ✅ **Procesamiento en segundo plano** (multithreading)
- ✅ **Envío automático al API** cuando detecta una placa
- ✅ **Sistema de cooldown** para evitar duplicados
- ✅ **Dashboard actualizado en vivo** vía WebSocket
- ✅ **Estadísticas en tiempo real**
- ✅ **Guardado automático** de capturas

## 🏗️ Arquitectura Completa

```
┌─────────────────┐
│     CÁMARA      │ (OpenCV)
│   (Siempre ON)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Detector YOLO  │ (En segundo plano)
│  + OCR Engine   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validación    │
│   + Cooldown    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐         ┌──────────────┐
│   API REST      │ ◄────── │  Dashboard   │
│   (FastAPI)     │ ──────► │  (React)     │
└────────┬────────┘ WebSocket└──────────────┘
         │
         ▼
┌─────────────────┐
│  Base de Datos  │
│  (JSON Logs)    │
└─────────────────┘
```

## ⚡ Inicio Rápido

### Método 1: Todo Automático (Recomendado)

```bash
# Windows
start_sistema_completo.bat
```

Esto iniciará en orden:
1. API Backend (puerto 8001)
2. Dashboard React (puerto 5173)
3. Sistema de Cámara (ventana OpenCV)

### Método 2: Manual (Paso a Paso)

**Terminal 1 - API Backend:**
```bash
python api_dashboard.py
```

**Terminal 2 - Dashboard React:**
```bash
cd dashboard-falcon
npm run dev
```

**Terminal 3 - Sistema de Cámara:**
```bash
python camera_garita.py
```

## 📹 Uso del Sistema de Cámara

### Parámetros de Inicio

```bash
python camera_garita.py --camera 0 --api http://localhost:8001 --cooldown 30
```

**Parámetros:**
- `--camera` : Fuente de cámara
  - `0` = Webcam por defecto
  - `1` = Segunda cámara
  - `http://192.168.1.100/stream` = IP Camera
- `--api` : URL del API backend (default: http://localhost:8001)
- `--cooldown` : Segundos entre detecciones de la misma placa (default: 30)

### Controles de Teclado

Durante la ejecución de la cámara:

- **ESPACIO** : Forzar captura y procesamiento del frame actual
- **'q' o ESC** : Salir del sistema
- **'s'** : Mostrar estadísticas detalladas

## 🔄 Flujo de Trabajo Automático

### 1. Detección Continua
```
Cámara ON → Frame cada 1/3 segundos → Cola de procesamiento
```

### 2. Procesamiento en Segundo Plano
```
Thread 1: Captura frames
Thread 2: Procesa frames de la cola
  ├─ Detecta placas con YOLO
  ├─ Extrae texto con OCR
  ├─ Valida formato
  └─ Verifica cooldown
```

### 3. Envío Automático al API
```
Si placa válida + NO en cooldown:
  ├─ Guarda captura en Outputs/capturas_garita/
  ├─ POST a /api/registros/entrada
  ├─ Actualiza cooldown (30s por defecto)
  └─ WebSocket notifica al Dashboard
```

### 4. Actualización del Dashboard
```
Dashboard recibe notificación WebSocket:
  ├─ Actualiza placa detectada (izquierda)
  ├─ Muestra datos del vehículo (derecha)
  └─ Añade al historial
```

## 📊 Interfaz de la Cámara

La ventana de OpenCV muestra:

```
╔════════════════════════════════════════╗
║  FALCON EPSA - Control de Garita      ║
║  FPS: 28.5                API: ✓       ║
║  Detecciones: 15                       ║
║  Enviadas: 12                          ║
║  Cola: 0                               ║
╠════════════════════════════════════════╣
║                                        ║
║      [VIDEO EN VIVO DE LA CÁMARA]     ║
║                                        ║
╚════════════════════════════════════════╝
```

## 🛡️ Sistema de Cooldown

**¿Por qué cooldown?**
Para evitar registrar el mismo vehículo múltiples veces mientras está en el campo de visión.

**¿Cómo funciona?**
- Cuando se detecta una placa, se guarda con timestamp
- Durante los próximos 30 segundos (configurable), esa placa se ignora
- Después de 30s, puede ser detectada nuevamente

**Ejemplo:**
```
10:00:00 - Detecta "ABC123" → Envía al API ✓
10:00:05 - Detecta "ABC123" → Ignora (cooldown)
10:00:10 - Detecta "ABC123" → Ignora (cooldown)
10:00:31 - Detecta "ABC123" → Envía al API ✓ (cooldown expiró)
```

## 📁 Estructura de Archivos Generados

```
Outputs/
└── capturas_garita/
    ├── 20251116_103045_123456_ABC123_0.jpg
    ├── 20251116_103125_789012_XYZ789_0.jpg
    └── ...
```

**Formato del nombre:**
```
{timestamp}_{placa}_{indice}.jpg
```

## 🔧 Configuración Avanzada

### Cambiar Resolución de Cámara

En `camera_garita.py`, línea ~69:
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)   # 1080p
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
```

### Ajustar Frecuencia de Procesamiento

En `camera_garita.py`, línea ~254:
```python
skip_frames = 5  # Procesar 1 de cada 5 frames (más rápido)
skip_frames = 10 # Procesar 1 de cada 10 frames (más eficiente)
```

### Cambiar Cooldown

```bash
python camera_garita.py --cooldown 60  # 1 minuto
python camera_garita.py --cooldown 10  # 10 segundos
```

## 📈 Estadísticas del Sistema

Presiona **'s'** durante la ejecución para ver:

```
======================================================================
📊 ESTADÍSTICAS DEL SISTEMA
======================================================================
Total de detecciones: 45
Total enviadas al API: 38
Total de errores: 2
Placas en cooldown: 5
Items en cola: 0
======================================================================
```

**Métricas:**
- **Total de detecciones**: Placas detectadas por YOLO
- **Total enviadas**: Placas enviadas exitosamente al API
- **Total de errores**: Errores de conexión o procesamiento
- **Placas en cooldown**: Placas que están en período de espera
- **Items en cola**: Frames esperando ser procesados

## 🎯 Casos de Uso Real

### Escenario 1: Entrada de Vehículo Registrado

```
1. Vehículo entra al campo de visión
2. Cámara detecta placa "PO28GHQ"
3. Sistema extrae texto y valida
4. Consulta API → Vehículo REGISTRADO
5. Dashboard muestra:
   - Izquierda: Placa "PO28GHQ" ✓ REGISTRADA
   - Derecha: Datos del propietario, tipo, estado AUTORIZADO
6. Guarda en historial con timestamp
7. Sistema espera 30s antes de poder detectar nuevamente
```

### Escenario 2: Entrada de Vehículo NO Registrado

```
1. Vehículo entra al campo de visión
2. Cámara detecta placa "XXX999"
3. Sistema extrae texto y valida
4. Consulta API → Vehículo NO REGISTRADO
5. Dashboard muestra:
   - Izquierda: Placa "XXX999" ✗ NO REGISTRADA
   - Derecha: Alerta roja "Placa no registrada"
6. Personal de seguridad puede tomar acción
7. Guarda en historial como "no registrada"
```

### Escenario 3: Tráfico Continuo

```
10:00:00 - Detecta ABC123 → Procesa → Envía → Cooldown 30s
10:00:15 - Detecta XYZ789 → Procesa → Envía → Cooldown 30s
10:00:20 - Detecta ABC123 → IGNORA (en cooldown)
10:00:35 - Detecta DEF456 → Procesa → Envía → Cooldown 30s
10:00:45 - Detecta ABC123 → Procesa → Envía (cooldown expiró)
```

## 🐛 Troubleshooting

### La cámara no se abre
```bash
# Verificar cámaras disponibles
python -c "import cv2; print([cv2.VideoCapture(i).isOpened() for i in range(4)])"

# Probar con índice diferente
python camera_garita.py --camera 1
```

### No detecta placas
- Verificar iluminación de la zona
- Asegurar que las placas estén en foco
- Verificar que el modelo YOLO esté cargado correctamente
- Revisar resolución de la cámara

### Muchos falsos positivos
- Ajustar threshold de confianza en `core/pipeline.py`
- Aumentar filtros de validación de texto
- Mejorar iluminación del área

### Sistema lento
```bash
# Procesar menos frames
# En camera_garita.py, cambiar skip_frames a un valor mayor
skip_frames = 10  # Procesar 1 de cada 10 frames
```

## 🔗 Integración con IP Cameras

### Hikvision
```bash
python camera_garita.py --camera "rtsp://admin:password@192.168.1.64:554/Streaming/Channels/101"
```

### Otras cámaras IP
```bash
# RTSP
python camera_garita.py --camera "rtsp://usuario:pass@IP:puerto/stream"

# HTTP
python camera_garita.py --camera "http://192.168.1.100/video.mjpg"
```

## 📊 Rendimiento Esperado

**Hardware Mínimo:**
- CPU: Intel i5 o equivalente
- RAM: 8GB
- Cámara: 720p @ 30fps

**Hardware Recomendado:**
- CPU: Intel i7 o equivalente
- RAM: 16GB
- GPU: NVIDIA GTX 1050 o superior (para YOLO)
- Cámara: 1080p @ 30fps

**Rendimiento típico:**
- FPS: 25-30 (visualización)
- Latencia detección → API: 1-3 segundos
- Latencia API → Dashboard: < 100ms (WebSocket)

## 🎓 Flujo Completo Paso a Paso

```mermaid
┌─────────────┐
│   CÁMARA    │ Frame @ 30 FPS
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Skip Frames │ Procesa 1/3 frames
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    COLA     │ Queue (max 10)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   THREAD    │ Procesamiento Background
│ YOLO + OCR  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  COOLDOWN   │ ¿Ya detectada?
│   CHECK     │
└──────┬──────┘
       │ No → Continuar
       ▼
┌─────────────┐
│ POST al API │ /api/registros/entrada
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  WEBSOCKET  │ Broadcast a clientes
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  DASHBOARD  │ Actualización en vivo
└─────────────┘
```

## 📝 Logs del Sistema

La consola muestra en tiempo real:

```
📤 Enviando detección al API:
   Placa: ABC123
   Confianza: 92.5%
✅ Registro exitoso (ID: 15)
   🚗 VEHÍCULO REGISTRADO
   Propietario: Juan Pérez
   Tipo: PARTICULAR
   Estado: AUTORIZADO
   Dashboard actualizado vía WebSocket ✓
```

## 🔐 Consideraciones de Seguridad

1. **Privacidad**: Las imágenes se guardan localmente
2. **Acceso**: Solo personal autorizado debe tener acceso al sistema
3. **Logs**: Se mantiene registro de todas las detecciones
4. **API**: Usar HTTPS en producción
5. **Cámaras IP**: Cambiar contraseñas por defecto

## 🚀 Próximas Mejoras

- [ ] Detección de dirección (entrada vs salida)
- [ ] Reconocimiento de país por color/formato de placa
- [ ] Alertas sonoras para placas RESTRINGIDAS
- [ ] Base de datos SQL en lugar de JSON
- [ ] Múltiples cámaras simultáneas
- [ ] Análisis de velocidad de vehículos
- [ ] Exportar reportes PDF

---

**Sistema desarrollado para Falcon EPSA - Control de Garita Automatizado**
