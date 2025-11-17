"""
Configuración de Cámara IP - FalconEPSA
Edita este archivo para cambiar la cámara IP o credenciales
"""

# =====================================================
# CONFIGURACIÓN DE CÁMARA IP HIKVISION
# =====================================================

# IP de la cámara
CAMERA_IP = "10.10.7.224"

# Credenciales por defecto (CAMBIAR EN PRODUCCIÓN)
CAMERA_USER = "admin"
CAMERA_PASSWORD = "Ccamar4."

# Puerto RTSP (típicamente 554)
RTSP_PORT = 554

# Canal RTSP (típicamente 101 o 102 para Hikvision)
RTSP_CHANNEL = "102"

# URLs generadas automáticamente
RTSP_URL = f"rtsp://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}:{RTSP_PORT}/Streaming/Channels/{RTSP_CHANNEL}"
HTTP_URL = f"http://{CAMERA_USER}:{CAMERA_PASSWORD}@{CAMERA_IP}/video"

# =====================================================
# CONFIGURACIÓN DE DETECCIÓN YOLO
# =====================================================

# Confianza mínima para detectar (0.0 a 1.0)
YOLO_CONFIDENCE = 0.5

# Intervalo de procesamiento (1 = todos los frames, 2 = cada 2 frames, etc)
PROCESS_INTERVAL = 2

# =====================================================
# CONFIGURACIÓN DE OCR TESSERACT
# =====================================================

# Ruta de Tesseract (Windows)
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Modo de segmentación (PSM)
# 7 = asumir una línea de texto (ideal para placas)
TESSERACT_PSM = 7

# Motor OCR (OEM)
# 3 = usar ambos (clásico + neural)
TESSERACT_OEM = 3

# Longitud mínima de placa detectada
MIN_PLATE_LENGTH = 4

# =====================================================
# CONFIGURACIÓN DE VIDEO
# =====================================================

# Ancho de frame
FRAME_WIDTH = 1280

# Alto de frame
FRAME_HEIGHT = 720

# FPS objetivo
TARGET_FPS = 30

# Buffer size (reducir para menos latencia)
BUFFER_SIZE = 1

# =====================================================
# CONFIGURACIÓN DE DEDUPLICACIÓN
# =====================================================

# Tiempo mínimo entre detecciones de la misma placa (segundos)
DEDUP_TIME = 3.0

# =====================================================
# CONFIGURACIÓN DE SALIDA
# =====================================================

# Carpeta de salida
OUTPUT_FOLDER = "Outputs"

# Archivo de detecciones
DETECCIONES_FILE = "Outputs/detecciones.txt"

# =====================================================
# EJEMPLOS DE CONFIGURACIÓN
# =====================================================

"""
# Para usar cámara LOCAL:
CAMERA_IP = "local"

# Para usar IP diferente:
CAMERA_IP = "192.168.1.100"

# Para cambiar credenciales:
CAMERA_USER = "usuario_personalizado"
CAMERA_PASSWORD = "contraseña_segura"

# Para aumentar sensibilidad:
YOLO_CONFIDENCE = 0.3  # Detecta más

# Para aumentar precisión:
YOLO_CONFIDENCE = 0.7  # Detecta menos pero más preciso
"""
