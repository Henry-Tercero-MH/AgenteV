# 📹 Configuración de Cámara IP Hikvision

## Estado Actual

❌ **La cámara Hikvision (10.10.7.224) no es accesible desde la red**

**Error:** `401 Unauthorized` + `Connection refused`

---

## 🔧 Cómo Configurar la Cámara Hikvision

### Paso 1: Verificar la IP de la Cámara

1. Accede a la interfaz web de la cámara:
   ```
   http://10.10.7.224
   ```

2. Si no carga, la IP es incorrecta. Consulta:
   - El manual de la cámara
   - La interfaz web del router
   - El software de descubrimiento Hikvision

### Paso 2: Actualizar Credenciales

Si la cámara tiene contraseña diferente a `admin`:

**Edita `config.py`:**
```python
CAMERA_USER = "admin"
CAMERA_PASSWORD = "tu_contraseña_real"
```

### Paso 3: Actualizar la Dirección IP

Si la IP no es `10.10.7.224`:

**Edita `config.py`:**
```python
CAMERA_IP = "192.168.1.100"  # O tu IP correcta
```

Las URLs se generarán automáticamente:
```python
RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:554/Streaming/Channels/101"
```

### Paso 4: Identificar el Canal RTSP Correcto

Diferentes modelos Hikvision usan canales diferentes:

**Opción A - Estándar (más común):**
```
rtsp://admin:admin@10.10.7.224:554/Streaming/Channels/101
```

**Opción B - Canal 1:**
```
rtsp://admin:admin@10.10.7.224:554/Streaming/Channels/1
```

**Opción C - Stream simplificado:**
```
rtsp://admin:admin@10.10.7.224:554/stream1
```

**Para probar cual funciona**, edita `config.py` y cambia `RTSP_URL`.

---

## 🧪 Verificar Conexión

### Usar el Diagnóstico Automático
```bash
python diagnostico_hikvision.py
```

Este script probará automáticamente:
- Conectividad a la IP
- Todos los canales RTSP comunes
- HTTP streaming

### Verificación Manual con Python
```python
import cv2

# Reemplaza con tu URL correcta
url = "rtsp://admin:admin@10.10.7.224:554/Streaming/Channels/101"
cap = cv2.VideoCapture(url)

if cap.isOpened():
    print("[OK] Conexion exitosa!")
    ret, frame = cap.read()
    if ret:
        print(f"[OK] Frame recibido: {frame.shape}")
else:
    print("[ERROR] No se pudo conectar")

cap.release()
```

### Verificación con Ping
```bash
ping 10.10.7.224
```

Si no responde, la cámara no está en la red.

---

## 📋 Configuración Completa de `config.py`

```python
# =====================================================
# CONFIGURACIÓN DE CÁMARA IP HIKVISION
# =====================================================

# IP de la cámara (ACTUALIZAR)
CAMERA_IP = "10.10.7.224"

# Credenciales (ACTUALIZAR si es diferente)
CAMERA_USER = "admin"
CAMERA_PASSWORD = "admin"

# Puerto RTSP (típicamente 554)
RTSP_PORT = 554

# Canal RTSP (probar: 101, 1, o stream1)
RTSP_CHANNEL = "101"

# URLs generadas automáticamente
RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:{RTSP_PORT}/Streaming/Channels/{RTSP_CHANNEL}"
HTTP_URL = f"http://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:8080/video"
```

---

## ❌ Errores Comunes

### Error: `401 Unauthorized`
**Causa:** Credenciales incorrectas
**Solución:**
1. Verifica usuario/contraseña
2. Accede a http://10.10.7.224 para confirmar
3. Actualiza `config.py`

### Error: `Connection refused` / `Connection timeout`
**Causa:** La cámara no responde
**Solución:**
1. Verifica que la IP es correcta (ping)
2. Verifica que la cámara está encendida
3. Verifica que estás en la misma red (o VPN)
4. Verifica que el firewall permite puerto 554

### Error: `404 Not Found` (en HTTP)
**Causa:** El canal RTSP es incorrecto
**Solución:**
1. Prueba otros canales (1, 101, stream1, etc.)
2. Consulta manual de la cámara
3. Usa el script de diagnóstico

### Error: `Method DESCRIBE failed`
**Causa:** La URL o canal es incorrecto
**Solución:**
1. Verifica formato de URL
2. Prueba diferentes canales
3. Consulta la documentación Hikvision

---

## 🚀 Una Vez Configurada

### Ejecutar la Aplicación
```bash
python run_app.py
```

### Cambiar entre Cámara Web y Hikvision

En `app_gui.py`, cambia esta línea:

**Para usar cámara web local:**
```python
cap = cv2.VideoCapture(0)
```

**Para usar Hikvision:**
```python
cap = cv2.VideoCapture(RTSP_URL)  # Desde config.py
```

---

## 📊 Parámetros de Configuración

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `CAMERA_IP` | 10.10.7.224 | IP de la cámara |
| `CAMERA_USER` | admin | Usuario RTSP |
| `CAMERA_PASSWORD` | admin | Contraseña RTSP |
| `RTSP_PORT` | 554 | Puerto RTSP (estándar) |
| `RTSP_CHANNEL` | 101 | Canal (varía por modelo) |
| `YOLO_CONFIDENCE` | 0.5 | Sensibilidad YOLO |
| `FRAME_WIDTH` | 1280 | Ancho de frame |
| `FRAME_HEIGHT` | 720 | Alto de frame |
| `TARGET_FPS` | 30 | FPS objetivo |

---

## 📖 Referencias

- **Documentación Hikvision:** https://www.hikvision.com/
- **RTSP Streaming:** https://en.wikipedia.org/wiki/Real_Time_Streaming_Protocol
- **OpenCV VideoCapture:** https://docs.opencv.org/master/d8/dfe/classcv_1_1VideoCapture.html

---

## 🆘 Próximos Pasos

1. **Verifica la IP:** `ping 10.10.7.224`
2. **Accede a web:** http://10.10.7.224
3. **Actualiza config.py** con datos correctos
4. **Ejecuta diagnóstico:** `python diagnostico_hikvision.py`
5. **Ejecuta app:** `python run_app.py`

---

**Última actualización:** Noviembre 2024
**Estado:** ⏳ Esperando configuración de cámara
