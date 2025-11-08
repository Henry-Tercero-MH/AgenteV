# 🚗 Sistema de Detección de Placas con YOLO + OCR# Detección de placas (YOLO + PaddleOCR)



Sistema completo de detección de placas vehiculares usando modelos YOLO para detección y PaddleOCR para reconocimiento de texto. Compatible con imágenes, webcam y cámaras RTSP (Hikvision).Este proyecto contiene un script (`app.py`) para detectar placas usando un modelo YOLO (`best.pt`) y reconocer texto con PaddleOCR.



## 📋 RequisitosRequisitos

- Python 3.8+

- **Python 3.14.0** (principal)- `best.pt` (ya pegado en la raíz del proyecto)

- **Python 3.13.7** (para OCR - en `venv_old_3.13`)

- Windows con Git BashInstalación rápida (bash en Windows):

- Modelos YOLO:

  - `best.pt` - Detección de placas```bash

  - `best_truck.pt` - Detección de vehículospython -m venv venv

source venv/Scripts/activate   # en Git Bash / bash.exe en Windows

## 🚀 Instalaciónpip install -r requirements.txt

# IMPORTANTE: paddleocr requiere paddlepaddle; si falla la instalación, sigue las instrucciones en https://www.paddlepaddle.org.cn/

### Primera vez (Setup completo)```



```bashUso

# 1. Crear entorno Python 3.14 (principal)

py -3.14 -m venv venv- Procesar una imagen:

source venv/Scripts/activate

pip install -r requirements.txt```bash

python app.py --source Inputs/image_001.jpg --model best.pt --output Outputs

# 2. Crear entorno Python 3.13 (solo para OCR)```

py -3.13 -m venv venv_old_3.13

venv_old_3.13/Scripts/activate- Procesar todas las imágenes en una carpeta:

pip install paddlepaddle==3.2.1 paddleocr==3.3.1

deactivate```bash

python app.py --source Inputs/ --model best.pt --output Outputs

# 3. Volver al entorno principal```

source venv/Scripts/activate

```- Usar la cámara en tiempo real (modo interactivo):



## 💻 Comandos para Ejecutar```bash

python app.py --webcam --model best.pt --output Outputs

### 📸 Detección en Imágenes (CLI)```



```bashOpciones útiles para cámara:

# Activar entorno- `--cam-index` índice de la cámara (por defecto 0)

cd /c/Users/henry/Desktop/Codigos-Proyectos/falconEpsa- `--skip-frames` cantidad de frames a saltar entre inferencias para reducir carga (por ejemplo 3)

source venv/Scripts/activate- Durante la ventana de la cámara: presiona `c` o `SPACE` para capturar y guardar el frame anotado, `q` para salir.



# Procesar una imagenOpciones principales:

python app.py \- `--conf` umbral de confianza (default 0.7)

  --source Inputs/truck.jpg \- `--pad` padding en píxeles al recortar la placa (default 15)

  --model best.pt \- `--show` mostrar la imagen final en una ventana (si el entorno permite GUI)

  --truck-model best_truck.pt \

  --output Outputs \Salida

  --conf 0.3- Las imágenes anotadas se guardan en `Outputs/` con el mismo nombre que la entrada.

- Además se guardan recortes de las placas como `<imagen>_plate_<i>.jpg`.

# Procesar múltiples imágenes

python app.py \Notas y recomendaciones

  --source Inputs/ \- Si estás en Windows y tienes GPU NVIDIA, instala la variante GPU de paddlepaddle; si no, instala la variante CPU.

  --model best.pt \- Si no puedes usar `cv2.imshow` (ambiente sin GUI), el script solo guardará las imágenes en `Outputs/`.

  --truck-model best_truck.pt \- Si tu clase de placa no es `0`, ajusta la comprobación en `app.py` (la lógica asume clase 0 para placas).

  --output Outputs

Si quieres, puedo:

# Solo detección de placas (sin modelo de vehículos)- adaptar el script para usar una clase diferente (no 0),

python app.py \- añadir guardado en CSV con los textos reconocidos,

  --source Inputs/image.png \- o preparar una pequeña GUI/Flask para procesar varias imágenes desde un navegador.

  --model best.pt \
  --output Outputs
```

### 🎥 Detección en Webcam

```bash
python app.py \
  --source 0 \
  --model best.pt \
  --truck-model best_truck.pt \
  --output Outputs
```

### 🌐 Dashboard Web con RTSP

```bash
# Cámara Hikvision
python web_dashboard.py \
  --hikvision-url "rtsp://admin:Ccamar4.@10.10.7.64:554/Streaming/Channels/101" \
  --model best.pt \
  --truck-model best_truck.pt \
  --device cpu \
  --infer-max-dim 640 \
  --host 127.0.0.1 \
  --port 8080

# Abrir en navegador: http://127.0.0.1:8080
```

### 📹 Dashboard con Webcam

```bash
python web_dashboard.py \
  --camera-index 0 \
  --model best.pt \
  --truck-model best_truck.pt \
  --device cpu \
  --port 8080
```

## ⚙️ Parámetros Principales

### `app.py` (CLI)

| Parámetro | Descripción | Ejemplo | Default |
|-----------|-------------|---------|---------|
| `--source` | Imagen, carpeta, webcam (0) | `Inputs/truck.jpg` | Requerido |
| `--model` | Modelo YOLO para placas | `best.pt` | Requerido |
| `--truck-model` | Modelo YOLO para vehículos | `best_truck.pt` | Opcional |
| `--output` | Carpeta de salida | `Outputs` | `Outputs` |
| `--conf` | Umbral de confianza | `0.3` | `0.5` |
| `--show` | Mostrar imagen con detecciones | - | No |

### `web_dashboard.py` (Dashboard Web)

| Parámetro | Descripción | Ejemplo | Default |
|-----------|-------------|---------|---------|
| `--hikvision-url` | URL RTSP de cámara Hikvision | `rtsp://user:pass@ip:port/...` | - |
| `--camera-index` | Índice de webcam | `0` | - |
| `--model` | Modelo YOLO para placas | `best.pt` | Requerido |
| `--truck-model` | Modelo YOLO para vehículos | `best_truck.pt` | Opcional |
| `--device` | Dispositivo (cpu/cuda) | `cpu` | `cpu` |
| `--infer-max-dim` | Dimensión máxima para inferencia | `640` | `640` |
| `--host` | Host del servidor | `127.0.0.1` | `127.0.0.1` |
| `--port` | Puerto del servidor | `8080` | `5000` |
| `--skip-frames` | Frames a saltar (CPU) | `15` | `15` |

## 📁 Estructura del Proyecto

```
falconEpsa/
├── venv/                      # Python 3.14.0 (principal)
├── venv_old_3.13/            # Python 3.13.7 (OCR)
├── app.py                     # CLI - Detección en imágenes/webcam
├── web_dashboard.py           # Dashboard web con streaming
├── ocr_wrapper.py             # Wrapper OCR (Python 3.13 subprocess)
├── debug_models.py            # Script de diagnóstico
├── analyze_plate.py           # Análisis avanzado de placas
├── best.pt                    # Modelo YOLO - Placas
├── best_truck.pt              # Modelo YOLO - Vehículos
├── templates/
│   └── index.html            # UI del dashboard
├── Inputs/                    # Imágenes de entrada
├── Outputs/                   # Resultados (imágenes anotadas y crops)
├── requirements.txt           # Dependencias Python 3.14
├── MIGRATION_NOTES.md         # Notas de migración a Python 3.14
└── README.md                  # Este archivo
```

## 🎯 Características

- ✅ **Detección en dos etapas**: Vehículos → Placas
- ✅ **OCR con PaddleOCR**: Reconocimiento de texto en placas
- ✅ **Filtrado inteligente**: Elimina nombres de países (GUATEMALA, MEXICO, etc.)
- ✅ **Confianza y timestamps**: Muestra porcentaje de confianza y hora
- ✅ **Dashboard web**: Streaming en tiempo real con MJPEG
- ✅ **Modo manual y automático**: Captura bajo demanda o continua
- ✅ **Optimizado para CPU**: Skip frames y downscaling configurables
- ✅ **Soporte RTSP**: Compatible con cámaras IP Hikvision

## 🔍 Ejemplos de Uso

### Procesar imagen con alta confianza
```bash
python app.py --source Inputs/truck.jpg --model best.pt --truck-model best_truck.pt --conf 0.7
```

### Dashboard con detección continua
```bash
python web_dashboard.py \
  --hikvision-url "rtsp://admin:password@10.10.7.64:554/Streaming/Channels/101" \
  --model best.pt \
  --truck-model best_truck.pt \
  --skip-frames 10 \
  --port 8080
```

### Procesar todas las imágenes en carpeta
```bash
python app.py --source Inputs/ --model best.pt --truck-model best_truck.pt --output Results/
```

## 🐛 Solución de Problemas

### Error: "Python 3.13 no encontrado"
```bash
# Verificar que existe venv_old_3.13
ls venv_old_3.13/Scripts/python.exe

# Si no existe, crear:
py -3.13 -m venv venv_old_3.13
venv_old_3.13/Scripts/activate
pip install paddlepaddle==3.2.1 paddleocr==3.3.1
deactivate
```

### Error: "No module named 'ultralytics'"
```bash
# Activar entorno y reinstalar
source venv/Scripts/activate
pip install -r requirements.txt
```

### Dashboard no carga en navegador
```bash
# Verificar que el puerto no esté ocupado
# Cambiar puerto:
python web_dashboard.py --port 8081 ...
```

### OCR muy lento (primera ejecución)
⚠️ **Normal**: La primera llamada OCR tarda ~30 segundos cargando PaddleOCR en Python 3.13. Las siguientes son más rápidas.

## 📊 Rendimiento

| Operación | Tiempo Promedio |
|-----------|----------------|
| YOLO Vehículos | ~900ms |
| YOLO Placas | ~850ms |
| OCR (primera vez) | ~30s |
| OCR (siguientes) | ~2s |
| **Total por frame** | ~3.5s |

**Optimización CPU**: Usar `--skip-frames 15` para procesar cada 15 frames (mejor fluidez)

## 🔄 Actualización

```bash
# Actualizar código
git pull

# Actualizar dependencias
source venv/Scripts/activate
pip install -r requirements.txt --upgrade
```

## 📝 Notas Importantes

1. **No eliminar `venv_old_3.13/`**: Necesario para OCR
2. **Primer OCR lento**: Carga inicial de PaddleOCR tarda ~30s
3. **Puerto 5000 ocupado**: En Windows, a veces está ocupado. Usar `--port 8080`
4. **RTSP timeout**: Si la cámara no responde, verificar red y credenciales

## 🛠️ Comandos de Diagnóstico

```bash
# Verificar versiones
python --version
python -c "from ultralytics import YOLO; print('YOLO OK')"
python -c "from ocr_wrapper import PaddleOCR; print('OCR OK')"

# Probar modelos independientemente
python debug_models.py --image Inputs/truck.jpg --truck best_truck.pt --plate best.pt

# Analizar placa específica
python analyze_plate.py --plate-crop Outputs/truck_plate_0_0.jpg

# Ver logs en tiempo real (dashboard)
python web_dashboard.py ... 2>&1 | tee dashboard.log
```

## 📞 Cámara Hikvision Configurada

```
IP: 10.10.7.64
Usuario: admin
Password: Ccamar4.
Puerto RTSP: 554
Stream: /Streaming/Channels/101

URL Completa:
rtsp://admin:Ccamar4.@10.10.7.64:554/Streaming/Channels/101
```

## ✅ Verificación Rápida

```bash
# 1. Activar entorno
source venv/Scripts/activate

# 2. Verificar Python 3.14
python --version  # Debe decir: Python 3.14.0

# 3. Probar detección simple
python app.py --source Inputs/truck.jpg --model best.pt --output Test/

# 4. Ver resultado
ls -lh Test/truck.jpg
```

## 🎉 ¡Listo!

El sistema está completamente funcional. Para cualquier duda, revisa `MIGRATION_NOTES.md` para detalles técnicos de la arquitectura.

---

**Versión**: 2.0 (Python 3.14)  
**Última actualización**: Noviembre 7, 2025  
**Python**: 3.14.0 + OCR wrapper (Python 3.13)
