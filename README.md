# Detección de placas (YOLO + PaddleOCR)

Este proyecto contiene un script (`app.py`) para detectar placas usando un modelo YOLO (`best.pt`) y reconocer texto con PaddleOCR.

Requisitos
- Python 3.8+
- `best.pt` (ya pegado en la raíz del proyecto)

Instalación rápida (bash en Windows):

```bash
python -m venv venv
source venv/Scripts/activate   # en Git Bash / bash.exe en Windows
pip install -r requirements.txt
# IMPORTANTE: paddleocr requiere paddlepaddle; si falla la instalación, sigue las instrucciones en https://www.paddlepaddle.org.cn/
```

Uso

- Procesar una imagen:

```bash
python app.py --source Inputs/image_001.jpg --model best.pt --output Outputs
```

- Procesar todas las imágenes en una carpeta:

```bash
python app.py --source Inputs/ --model best.pt --output Outputs
```

- Usar la cámara en tiempo real (modo interactivo):

```bash
python app.py --webcam --model best.pt --output Outputs
```

Opciones útiles para cámara:
- `--cam-index` índice de la cámara (por defecto 0)
- `--skip-frames` cantidad de frames a saltar entre inferencias para reducir carga (por ejemplo 3)
- Durante la ventana de la cámara: presiona `c` o `SPACE` para capturar y guardar el frame anotado, `q` para salir.

Opciones principales:
- `--conf` umbral de confianza (default 0.7)
- `--pad` padding en píxeles al recortar la placa (default 15)
- `--show` mostrar la imagen final en una ventana (si el entorno permite GUI)

Salida
- Las imágenes anotadas se guardan en `Outputs/` con el mismo nombre que la entrada.
- Además se guardan recortes de las placas como `<imagen>_plate_<i>.jpg`.

Notas y recomendaciones
- Si estás en Windows y tienes GPU NVIDIA, instala la variante GPU de paddlepaddle; si no, instala la variante CPU.
- Si no puedes usar `cv2.imshow` (ambiente sin GUI), el script solo guardará las imágenes en `Outputs/`.
- Si tu clase de placa no es `0`, ajusta la comprobación en `app.py` (la lógica asume clase 0 para placas).

Si quieres, puedo:
- adaptar el script para usar una clase diferente (no 0),
- añadir guardado en CSV con los textos reconocidos,
- o preparar una pequeña GUI/Flask para procesar varias imágenes desde un navegador.
