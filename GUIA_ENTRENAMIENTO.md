# 🚀 Guía Rápida: Entrenar Modelo Fusionado en Google Colab

## 📋 Proceso Completo

### 1️⃣ Preparación Local (En tu PC)

```bash
# 1. Fusionar datasets
python fusionar_datasets.py \
  --camiones ruta/dataset_camiones \
  --placas ruta/dataset_placas \
  --salida dataset_fusionado

# 2. Comprimir para subir
zip -r dataset_fusionado.zip dataset_fusionado/
```

**Resultado:** `dataset_fusionado.zip` listo para subir

---

### 2️⃣ Subir a Google Drive

1. Ve a [Google Drive](https://drive.google.com)
2. Sube `dataset_fusionado.zip`
3. Anota la ruta (ej: `/MyDrive/dataset_fusionado.zip`)

---

### 3️⃣ Entrenar en Google Colab

1. Ve a [Google Colab](https://colab.research.google.com)
2. Crea un nuevo notebook
3. Copia el contenido de `colab_entrenamiento.py`
4. Ejecuta celda por celda
5. Espera ~2-4 horas (depende del tamaño del dataset)

---

### 4️⃣ Descargar Modelo

Al finalizar, descarga de Google Drive:
- ✅ `best_fusionado.pt` → Tu nuevo modelo
- 📊 `resultados_entrenamiento.zip` → Métricas

---

### 5️⃣ Usar Modelo en tu Proyecto

```bash
# Renombrar y reemplazar
mv best_fusionado.pt best.pt

# Probar nuevo modelo (SIN --truck-model)
python app.py --source Inputs/test.jpg --model best.pt --conf 0.3

# ¡30% más rápido! ⚡
```

---

## 📊 Estructura del Dataset Fusionado

```
dataset_fusionado/
├── images/
│   ├── train/
│   │   ├── truck_img1.jpg      # Prefijo truck_
│   │   ├── truck_img2.jpg
│   │   ├── plate_img1.jpg      # Prefijo plate_
│   │   └── plate_img2.jpg
│   └── val/
│       └── ...
├── labels/
│   ├── train/
│   │   ├── truck_img1.txt      # class 0 = camion
│   │   ├── truck_img2.txt
│   │   ├── plate_img1.txt      # class 1 = placa
│   │   └── plate_img2.txt
│   └── val/
│       └── ...
└── dataset.yaml                 # Configuración YOLO
```

---

## ⚙️ Configuración Recomendada

### Para dataset pequeño (<1000 imágenes):
```python
epochs=100
batch=16
imgsz=640
modelo='yolov8n.pt'  # Nano (más rápido)
```

### Para dataset mediano (1000-5000 imágenes):
```python
epochs=150
batch=16
imgsz=640
modelo='yolov8s.pt'  # Small (balanceado)
```

### Para dataset grande (>5000 imágenes):
```python
epochs=200
batch=16
imgsz=640
modelo='yolov8m.pt'  # Medium (más preciso)
```

---

## 🎯 Clases en el Modelo Fusionado

```
0: camion   (o trailer, según tu dataset)
1: placa    (o License_Plate)
```

El script ajusta automáticamente los IDs:
- Dataset camiones: mantiene `class_id=0`
- Dataset placas: cambia de `0` a `1`

---

## ✅ Validación

Después del entrenamiento, verifica:

```python
from ultralytics import YOLO

# Cargar modelo
modelo = YOLO('best.pt')

# Ver clases
print(modelo.names)  # {0: 'camion', 1: 'placa'}

# Probar detección
resultados = modelo('test_image.jpg')

# Ver detecciones
for r in resultados:
    for box in r.boxes:
        clase = int(box.cls)
        conf = float(box.conf)
        print(f"Clase {clase} ({modelo.names[clase]}): {conf:.3f}")
```

---

## 🐛 Solución de Problemas

### ❌ Error: "No labels found"
- Verifica que los archivos .txt tengan el mismo nombre que las imágenes
- Ejemplo: `imagen1.jpg` → `imagen1.txt`

### ❌ Error: "Index out of range"
- Verifica que los `class_id` en los .txt sean 0 o 1 (no mayores)
- Usa el script de fusión para ajustar automáticamente

### ❌ GPU out of memory
- Reduce `batch` de 16 → 8 o 4
- Reduce `imgsz` de 640 → 416

---

## 📈 Métricas Esperadas

Para un modelo bien entrenado:

| Métrica | Valor Objetivo |
|---------|----------------|
| mAP50 | >0.90 |
| mAP50-95 | >0.70 |
| Precisión | >0.85 |
| Recall | >0.80 |

Si tus métricas son bajas:
- ✅ Aumenta epochs (100 → 150 → 200)
- ✅ Verifica calidad de labels (revisar manualmente)
- ✅ Balancea el dataset (cantidad similar de cada clase)

---

## 🚀 Próximos Pasos

Una vez tengas el modelo fusionado:

1. **Reemplazar** `best.pt` en tu proyecto
2. **Eliminar** parámetro `--truck-model`
3. **Actualizar** `web_dashboard.py` para usar un solo modelo
4. **Medir** mejora de velocidad (~30% más rápido)

---

## 💡 Tips Adicionales

- 🔄 Usa **data augmentation** (ya incluido en el notebook)
- 📊 Revisa **confusion matrix** para ver errores comunes
- 🎯 Ajusta **conf_threshold** según tu caso de uso
- 💾 Guarda **checkpoints cada 10 epochs** por si falla

---

**¿Necesitas ayuda?** Revisa el archivo `colab_entrenamiento.py` con comentarios detallados.
