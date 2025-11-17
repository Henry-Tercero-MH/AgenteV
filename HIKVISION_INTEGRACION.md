# 📹 Integración Cámara IP Hikvision

## ✅ Sistema Implementado

El sistema FalconEPSA ahora soporta **cámara IP Hikvision** en la dirección `10.10.7.224`.

---

## 🎯 Características

✅ **Conexión automática** a Hikvision 10.10.7.224
✅ **Fallback RTSP → HTTP → Cámara Local**
✅ **Configuración centralizada** en `config.py`
✅ **Detección OCR en tiempo real**
✅ **Reducción de latencia** (BUFFERSIZE=1)

---

## ⚙️ Configuración

### Archivo: `config.py`

```python
# IP de la cámara
CAMERA_IP = "10.10.7.224"

# Credenciales
CAMERA_USER = "admin"
CAMERA_PASSWORD = "12345"

# URLs generadas automáticamente
RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/Streaming/Channels/101"
HTTP_URL = f"http://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:8080/video"
```

---

## 🚀 Cómo Usar

### 1. **Iniciar la aplicación:**
```bash
python run_app.py
```

### 2. **La aplicación intentará conectar en este orden:**

1. **RTSP** (rtsp://10.10.7.224:554/Streaming/Channels/101)
   - Protocolo recomendado
   - Baja latencia
   - Mayor compatibilidad

2. **HTTP/MJPEG** (http://10.10.7.224:8080/video)
   - Si RTSP falla
   - Más lento pero más compatible

3. **Cámara Local** (VideoCapture(0))
   - Si ambas fallan
   - Fallback a webcam

---

## 🔧 Cambiar Configuración

### Cambiar IP de cámara:
```python
# config.py
CAMERA_IP = "192.168.1.100"  # Nueva IP
```

### Cambiar credenciales:
```python
# config.py
CAMERA_USER = "usuario_personalizado"
CAMERA_PASSWORD = "contraseña_segura"
```

### Cambiar canal RTSP:
```python
# config.py
RTSP_CHANNEL = "102"  # Canal 102 en lugar de 101
```

### Cambiar puerto RTSP:
```python
# config.py
RTSP_PORT = 554  # Puerto estándar
```

---

## 📊 Códigos de Canal RTSP (Hikvision)

| Canal | Descripción | URL |
|-------|-------------|-----|
| 101 | Canal 1 | /Streaming/Channels/101 |
| 102 | Canal 2 | /Streaming/Channels/102 |
| 103 | Canal 3 | /Streaming/Channels/103 |
| 104 | Canal 4 | /Streaming/Channels/104 |

---

## 🔐 Cambiar Credenciales de Hikvision

### En la cámara IP:

1. Accede a: http://10.10.7.224
2. Login con admin/12345
3. Configuración → Seguridad → Cuenta
4. Edita contraseña
5. Guarda cambios

### Luego actualiza `config.py`:
```python
CAMERA_PASSWORD = "nueva_contraseña"
```

---

## 🧪 Test de Conexión

### Verificar conectividad:
```bash
# Test RTSP
ffprobe rtsp://admin:12345@10.10.7.224:554/Streaming/Channels/101

# Test HTTP
curl http://admin:12345@10.10.7.224:8080/video

# Test con OpenCV
python -c "
import cv2
cap = cv2.VideoCapture('rtsp://admin:12345@10.10.7.224:554/Streaming/Channels/101')
print('Conectado' if cap.isOpened() else 'Error de conexión')
cap.release()
"
```

---

## 📊 Parámetros de Captura

### En `config.py`:

```python
# Resolución
FRAME_WIDTH = 1280      # Ancho
FRAME_HEIGHT = 720      # Alto

# Velocidad
TARGET_FPS = 30         # Fotogramas por segundo

# Latencia
BUFFER_SIZE = 1         # Bajo = menor latencia
```

### Para mayor calidad (más lento):
```python
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
TARGET_FPS = 30
```

### Para mejor rendimiento (más rápido):
```python
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
TARGET_FPS = 15
```

---

## 🎯 Detección en Tiempo Real

Una vez conectada la cámara Hikvision:

1. ✅ YOLO detecta vehículos
2. ✅ OCR lee placas reales
3. ✅ Se guardan en `Outputs/detecciones.txt`
4. ✅ FPS mostrado en pantalla

---

## ⚠️ Troubleshooting

### Error: "No se puede conectar a Hikvision"

**Solución 1: Verificar IP**
```bash
ping 10.10.7.224
```

**Solución 2: Verificar credenciales**
```python
# config.py - Intenta credenciales por defecto
CAMERA_USER = "admin"
CAMERA_PASSWORD = "12345"
```

**Solución 3: Verificar puerto RTSP**
```bash
# Hikvision típicamente usa puerto 554
RTSP_PORT = 554
```

### Error: "RTSP no disponible"

La aplicación automáticamente fallará a HTTP/MJPEG:
```python
# app_gui.py automáticamente intenta:
# 1. RTSP (rtsp://...)
# 2. HTTP (http://...)
# 3. Cámara local (0)
```

### Latencia alta

```python
# config.py - Reducir buffer
BUFFER_SIZE = 1  # Mínimo buffer
```

---

## 📈 Monitoreo

### Ver estadísticas en tiempo real:

La interfaz Tkinter muestra:
- 📊 Vehículos detectados
- 📋 Placas leídas
- 🔤 Última placa
- ⚡ FPS actual

### Archivo de detecciones:

```
Outputs/detecciones.txt

=== 2024-11-11 14:35:22 ===

2024-11-11 14:35:24.123 | ABC1234 | 92% | PLACA
2024-11-11 14:35:28.456 | XYZ5678 | 89% | PLACA
```

---

## 🔄 Integración Completa

### Flujo de funcionamiento:

```
Hikvision 10.10.7.224
        ↓
    RTSP → HTTP → Cámara Local
        ↓
    OpenCV (cv2.VideoCapture)
        ↓
    YOLO (Detección de vehículos)
        ↓
    OCR Tesseract (Lectura de placas)
        ↓
    Tkinter GUI (Visualización)
        ↓
    Outputs/detecciones.txt (Guardado)
```

---

## ✨ Ventajas

✅ **Configuración centralizada** - Todo en `config.py`
✅ **Fallback automático** - RTSP → HTTP → Cámara Local
✅ **Bajo mantenimiento** - Solo cambiar parámetros en config
✅ **Compatible** - Soporta todos los protocolos
✅ **Producción** - Sistema robusto y confiable

---

## 📝 Ejemplo Completo

```bash
# 1. Editar config.py si es necesario
nano config.py

# 2. Ejecutar aplicación
python run_app.py

# 3. Hacer clic en "▶ Iniciar"

# 4. Ver detecciones en tiempo real

# 5. Revisar resultados
cat Outputs/detecciones.txt
```

---

**Versión:** 2.2 (Con soporte Hikvision)
**Cámara:** Hikvision 10.10.7.224
**Estado:** ✅ Operativo
