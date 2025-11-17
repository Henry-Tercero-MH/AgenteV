# 🚗 FalconEPSA - Sistema 100% OCR Real

## ¿Qué es FalconEPSA?

**FalconEPSA es un sistema de detección de vehículos en TIEMPO REAL que lee placas REALES desde tu cámara web usando OCR Tesseract.**

- ✅ **100% Producción** - Sin código de demostración
- ✅ **OCR Real** - Lee placas genuinas desde video en vivo
- ✅ **YOLO Detection** - Detección de vehículos con modelo best.pt
- ✅ **Guardado Automático** - Todas las detecciones en `Outputs/detecciones.txt`
- ✅ **Interfaz Tkinter** - GUI simple y responsiva

---

## 📋 Requisitos

### Software requerido:
- **Python 3.8+** (recomendado 3.10+)
- **Tesseract OCR** instalado en `C:\Program Files\Tesseract-OCR\`
- **Cámara web** conectada

### Dependencias Python:
```
opencv-python        # Captura de video
ultralytics          # YOLO (detección de vehículos)
pytesseract          # Wrapper OCR
pillow               # Procesamiento de imágenes
tkinter              # GUI (incluido en Python)
```

---

## 🚀 Instalación Rápida

### 1. Crear entorno virtual
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows
# o
source .venv/bin/activate      # Linux/Mac
```

### 2. Instalar dependencias
```bash
pip install opencv-python ultralytics pytesseract pillow
```

### 3. Instalar Tesseract OCR
**Windows:**
1. Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Ejecutar: `tesseract-ocr-w64-setup-v5.x.exe`
3. Instalar en: `C:\Program Files\Tesseract-OCR\`

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

---

## ▶️ Ejecutar la Aplicación

```bash
# Activar entorno virtual
source .venv/Scripts/activate  # Windows

# Ejecutar
python run_app.py
```

La ventana aparecerá con:
- 📹 **Video en vivo** de tu cámara
- 🟩 **Recuadros verdes** = Vehículos detectados
- 🔤 **Placas leídas** = Texto OCR real (ejemplo: ABC1234)
- 📊 **Estadísticas** = Contador de vehículos y placas
- 📁 **Archivo** = `Outputs/detecciones.txt`

---

## 📁 Estructura del Proyecto

```
falconEpsa/
├── app_gui.py              # Aplicación principal (100% producción)
├── run_app.py              # Script launcher
├── best.pt                 # Modelo YOLO para detección
├── Outputs/
│   └── detecciones.txt     # Archivo de detecciones (se crea automáticamente)
└── README_PRODUCCION.md    # Este archivo
```

---

## 🔧 Configuración Avanzada

### Cambiar ruta de Tesseract (Windows)
Si instalaste Tesseract en otra ruta, edita `app_gui.py` línea ~319:

```python
pytesseract.pytesseract.pytesseract_cmd = r'TU_RUTA_AQUI\tesseract.exe'
```

### Ajustar sensibilidad YOLO
En `app_gui.py` línea ~105, cambia `conf=0.5`:
- Más bajo (0.3) = Detecta más, más falsos positivos
- Más alto (0.7) = Detecta menos, más preciso

```python
results = model(frame, conf=0.5, verbose=False)  # Ajustar aquí
```

### Intervalo de deduplicación
En `app_gui.py` línea ~55, cambia `3.0` (segundos):
```python
if now - state['plate_history'][plate] >= 3.0:  # 3 segundos entre detecciones
```

---

## 📊 Archivo de Detecciones

Formato: `Outputs/detecciones.txt`

```
=== 2024-11-11 14:30:45 ===

2024-11-11 14:30:47.234 | ABC1234 | 92% | PLACA
2024-11-11 14:30:52.567 | XYZ5678 | 88% | PLACA
2024-11-11 14:31:03.891 | ABC1234 | 91% | PLACA
```

Campos:
- **Timestamp** = Hora exacta (YYYY-MM-DD HH:MM:SS.mmm)
- **Placa** = Texto leído por OCR
- **Confianza** = Porcentaje de confianza del OCR
- **Tipo** = Siempre "PLACA" (para vehículos reales)

---

## 🐛 Troubleshooting

### Error: `ModuleNotFoundError: No module named 'cv2'`
```bash
pip install opencv-python
```

### Error: `pytesseract: "tesseract-ocr is not installed"`
- Tesseract EXE no está en la ruta esperada
- Instala desde: https://github.com/UB-Mannheim/tesseract/wiki
- O edita la ruta en `app_gui.py`

### La cámara no funciona
- Verifica que tu cámara esté conectada
- Prueba con: `python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"`

### No detecta placas
- Acerca los vehículos a la cámara
- Asegúrate que las placas sean legibles
- La iluminación es importante para OCR

---

## 📝 Notas Técnicas

### OCR Configuration (Tesseract)
```
--psm 7       = Asumir una línea de texto
--oem 3       = Usar ambos motores OCR clásico y neural
-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-
```

### Pre-procesamiento de imagen
```python
# Aumentar contraste (facilita lectura)
ImageEnhance.Contrast(image).enhance(2.0)

# Aumentar nitidez
ImageEnhance.Sharpness(image).enhance(2.0)

# Aumentar brillo
ImageEnhance.Brightness(image).enhance(1.1)
```

### Thread Safety
- Usa `state['lock']` para acceso a variables compartidas
- Captura en thread separado, UI en thread principal
- Evita race conditions en `vehicle_count` y `plate_count`

---

## 🎯 Casos de Uso

✅ Sistemas de estacionamiento inteligente
✅ Control de acceso vehicular
✅ Monitoreo de tráfico en tiempo real
✅ Estadísticas de movimiento de vehículos
✅ Detección de violaciones de tránsito

---

## 📄 Licencia

Sistema FalconEPSA - Uso libre para proyectos comerciales y educativos.

---

## 📞 Soporte

Si encuentras problemas:
1. Verifica que Tesseract esté instalado: `tesseract --version`
2. Verifica la cámara: `python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"`
3. Verifica imports: `python -c "import app_gui; print('[OK]')"`

---

**Versión:** 2.0 (100% Producción - Sin Demo)
**Última actualización:** Noviembre 2024
**Estado:** ✅ Listo para producción
