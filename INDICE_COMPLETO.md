# 📚 ÍNDICE COMPLETO - FalconEPSA 

## 🎯 ARCHIVOS PRINCIPALES (Aquí está lo importante)

### ✅ Aplicación
```
run_app.py                  ← EJECUTAR ESTO para GUI gráfica
app_gui.py                  ← Código principal (GUI Tkinter + OCR)
```

### ✅ Modos Alternativos
```
camera_live_cli.py          ← Versión CLI (línea de comandos)
webcam_web.py               ← Versión Web (Flask en navegador)
```

### ✅ Herramientas
```
demo_visualizacion.py       ← Demo sin cámara
generate_example.py         ← Genera imagen de ejemplo
INSTALAR_OCR.py             ← Verifica Tesseract OCR
```

---

## 📖 DOCUMENTACIÓN IMPORTANTE

### 🟢 LEER PRIMERO (Guías para usuario final)
```
GUIA_RAPIDA_OCR.md          ← 3 pasos para instalar Tesseract
EXPLICACION_OCR.md          ← Por qué necesitas OCR + cómo funciona
```

### 🟡 LEER SEGUNDO (Resúmenes técnicos)
```
CAMBIOS_OCR_REAL.md         ← Cambios exactos implementados
CAMBIOS_REALIZADOS.md       ← Mejoras de visualización
RESUMEN_FINAL.md            ← Estado actual del proyecto
```

### 🔵 REFERENCIA (Documentación técnica)
```
README_MEJORAS.md           ← Detalles de mejoras
ARQUITECTURA.md             ← Estructura del sistema
```

---

## 🔧 CONFIGURACIÓN

```
requirements.txt            ← Dependencias Python
best.pt                     ← Modelo YOLO (detección)
best_truck.pt               ← Modelo YOLO (camiones)
```

---

## 📁 DIRECTORIO Outputs

```
Outputs/
├── detecciones.txt         ← Placas detectadas (generado en runtime)
└── ejemplo_visualizacion.png ← Imagen de ejemplo visual
```

---

## 🔴 ARCHIVOS LEGACY (No usar, ya modificados)

```
app.py                      ← Versión vieja modular
camera_detection.py         ← Antiguo
camera_live.py              ← Antiguo
camera_yolo_real.py         ← Antiguo
falcon_auto.py              ← Antiguo
run_falcon.py               ← Antiguo
run_server.py               ← Antiguo
web_dashboard.py            ← Versión vieja Flask
```

---

## 📝 ORDEN RECOMENDADO PARA LEER

### Si quieres USAR el sistema (No desarrollar):

1. **GUIA_RAPIDA_OCR.md** ← Empieza aquí
2. **EXPLICACION_OCR.md** ← Entiende el sistema
3. **run_app.py** ← Ejecuta esto

### Si quieres ENTENDER el código:

1. **CAMBIOS_OCR_REAL.md** ← Qué cambió
2. **app_gui.py** ← Lee el código
3. **RESUMEN_FINAL.md** ← Entende estado final

### Si quieres DESARROLLAR:

1. **ARQUITECTURA.md** ← Estructura
2. **app_gui.py** ← Código principal
3. **CAMBIOS_OCR_REAL.md** ← Cómo modificar

---

## 🚀 CÓMO EJECUTAR

### Opción 1: GUI Gráfica (RECOMENDADO)
```bash
cd c:\Users\henry\Desktop\Codigos-Proyectos\falconEpsa
source venv/Scripts/activate
python run_app.py
```
- ✅ Interfaz gráfica bonita
- ✅ Controles visuales
- ✅ Estadísticas en vivo
- ✅ Con OCR (si Tesseract está instalado)

### Opción 2: Línea de Comandos
```bash
python camera_live_cli.py
```
- ✅ Solo texto
- ✅ Perfecto para servidores
- ✅ Sin dependencia de GUI

### Opción 3: Navegador Web
```bash
python webcam_web.py
# Abre: http://localhost:5000
```
- ✅ Visualización en navegador
- ✅ Accesible desde otra PC
- ✅ Responsivo

### Opción 4: Demo (Sin cámara)
```bash
python demo_visualizacion.py
```
- ✅ Prueba sin hardware
- ✅ Genera archivo de ejemplo
- ✅ Demuestra las características

---

## 🎯 ESTADO ACTUAL

```
✅ YOLO             → Detecta vehículos en la cámara
✅ OpenCV           → Procesa imágenes
✅ Tkinter GUI      → Interfaz gráfica
✅ Contadores       → Thread-safe
✅ Deduplicación    → 3 segundos cooldown
✅ Guardado a TXT   → Timestamps precisos
✅ pytesseract      → Interface OCR (instalado)
❌ Tesseract EXE    → OCR real (FALTA INSTALAR)
```

---

## 🔧 INSTALACIÓN RÁPIDA

```bash
# 1. Activar venv
source venv/Scripts/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Descargar Tesseract OCR
# URL: https://github.com/UB-Mannheim/tesseract/wiki
# Instalar en: C:\Program Files\Tesseract-OCR

# 4. Verificar
python INSTALAR_OCR.py

# 5. Ejecutar
python run_app.py
```

---

## 💾 CARPETA VIRTUAL (venv)

```
venv/
├── Scripts/
│   ├── activate          ← Activar entorno
│   ├── python.exe        ← Python en el venv
│   └── pip.exe           ← Gestor de paquetes
├── Lib/
│   └── site-packages/    ← Paquetes instalados
│       ├── cv2/          ← OpenCV
│       ├── ultralytics/  ← YOLO
│       ├── torch/        ← PyTorch
│       └── ... (más)
└── Include/
    └── python.h          ← Headers de desarrollo
```

---

## 🔄 ESTRUCTURA DEL CÓDIGO PRINCIPAL (app_gui.py)

```python
# Imports y configuración (líneas 1-50)
# - YOLO, OpenCV, Tkinter, PIL, pytesseract
# - Variables de estado global

# Placas simuladas (líneas 30-36)
# SIMULATED_PLATES = {...}

# Funciones de utilidad (líneas 38-125)
# - save_plate()
# - is_new()
# - get_plate_for_detection()
# - read_plate_with_ocr() ← NUEVA FUNCIÓN OCR
# - capture_thread_func()

# Clase principal (líneas 265-430)
class FalconEPSAApp:
    - __init__()
    - setup_ui()
    - load_model()
    - load_ocr() ← NUEVA FUNCIÓN
    - start_capture()
    - stop_capture()
    - update_display()

# Main (líneas 432-438)
if __name__ == '__main__':
    # Crear ventana Tkinter
    # Iniciar app
```

---

## 📊 FLUJO DE DATOS

```
Cámara
  ↓
OpenCV (cv2.VideoCapture)
  ↓
YOLO (model.predict)
  ↓
Tesseract OCR (pytesseract) ← OCR REAL
  ↓
Fallback a placas simuladas ← Si OCR falla
  ↓
Deduplicación (3 seg cooldown)
  ↓
Incrementar contadores (thread-safe)
  ↓
Guardar en TXT
  ↓
Mostrar en GUI (Tkinter)
  ↓
Actualizar estadísticas en vivo
```

---

## 🎓 APUNTES TÉCNICOS

### OCR Real vs Demo

**DEMO (Actual sin Tesseract):**
- Placa = Región del frame
- P123ABC siempre en TOP-LEFT
- M456DEF siempre en TOP-RIGHT
- ❌ NO es placa real

**REAL (Con Tesseract):**
- Placa = OCR lee imagen
- ABC1234 (lo que hay realmente)
- XYZ5678 (específico de cada vehículo)
- ✅ ES placa real de la imagen

### Thread-Safe

Todos los accesos a estado global usan locks:
```python
with state['lock']:
    state['vehicle_count'] += 1
    state['plate_count'] += 1
```

### Deduplicación

Cooldown de 3 segundos:
```python
def is_new(plate):
    now = time.time()
    if plate not in history:
        history[plate] = now
        return True
    if now - history[plate] >= 3.0:
        history[plate] = now
        return True
    return False
```

---

## 🚨 TROUBLESHOOTING

**Error: cv2 not found**
- Solución: `pip install opencv-python-headless`

**Error: YOLO model not found (best.pt)**
- Solución: Coloca `best.pt` en la carpeta raíz

**Error: Tesseract not found**
- Solución: Instala desde https://github.com/UB-Mannheim/tesseract/wiki

**Error: Tkinter not working**
- Solución: En Linux: `apt-get install python3-tk`
- En Windows: Viene incluido

**Bajo FPS**
- Aumenta `frame_count % N` (saltea más frames)
- Reduce resolución
- Usa GPU si disponible

---

## ✨ CARACTERÍSTICAS FINALES

✅ Detección de vehículos YOLO
✅ OCR Real con Tesseract (si está instalado)
✅ Fallback a placas simuladas por región
✅ GUI bonita con Tkinter
✅ Web dashboard con Flask
✅ CLI para línea de comandos
✅ Thread-safe
✅ Deduplicación inteligente
✅ Timestamps de precisión milisegundo
✅ Múltiples modos de ejecución

---

**Para empezar: Lee GUIA_RAPIDA_OCR.md y ejecuta `python run_app.py`**
