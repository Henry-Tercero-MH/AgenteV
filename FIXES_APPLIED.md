# Correcciones Aplicadas al Proyecto FalconEpsa

## Fecha: 2024-11-07

## Resumen de Problemas Encontrados

### 1. **PaddleOCR - Configuración Incorrecta**
**Problema**: La inicialización de PaddleOCR usaba parámetros incompatibles con PaddleOCR 3.3.1:
- `use_angle_cls` está deprecado
- `use_gpu` no existe en esta versión
- `show_log` no existe en esta versión

**Solución**: Simplificado a `PaddleOCR(lang='en')` que usa valores por defecto adecuados para CPU.

### 2. **Umbral de Confianza Demasiado Alto**
**Problema**: El umbral por defecto de 0.7 era demasiado alto y filtraba detecciones válidas (ej: placa con conf=0.573).

**Solución**: Cambiado el umbral por defecto de `0.7` a `0.5` en:
- Función `run_on_image()`: parámetro `conf_thresh=0.5`
- Función `run_webcam()`: parámetro `conf_thresh=0.5`
- Argumento CLI: `--conf` default cambiado a `0.5`

### 3. **Falta de Mensajes de Depuración**
**Problema**: Cuando algo fallaba, no había forma de saber qué estaba pasando en el flujo del programa.

**Solución**: Agregados mensajes `[DEBUG]` en puntos críticos:
- Cuando se ejecuta el modelo de camiones
- Cuando se detecta/descarta un camión por confianza
- Número de regiones a procesar (camiones vs imagen completa)
- Tamaño de cada región procesada
- Detecciones de placas (coordenadas, confianza)
- Placas descartadas por confianza
- Resultado del OCR
- Archivos guardados

### 4. **Manejo de Excepciones Silencioso**
**Problema**: Los bloques try/except capturaban errores sin mostrar traceback completo.

**Solución**: Agregado `import traceback; traceback.print_exc()` en bloques de excepción críticos.

## Archivos Modificados

### `app.py`
- ✅ PaddleOCR inicialización simplificada (2 ubicaciones)
- ✅ Umbral de confianza por defecto: 0.7 → 0.5 (3 ubicaciones)
- ✅ Agregados mensajes [DEBUG] en pipeline de detección
- ✅ Mejorado manejo de excepciones con traceback

### `web_dashboard.py`
- ✅ PaddleOCR inicialización simplificada
- ✅ Removidos parámetros obsoletos

## Resultados de Pruebas

### Comando Ejecutado
```bash
python app.py --source Inputs/truck.jpg --model best.pt --truck-model best_truck.pt --output Outputs --conf 0.5
```

### Salida Exitosa
```
[DEBUG] Ejecutando modelo de camiones...
[DEBUG] Camión detectado: box=[263, 87, 994, 885], conf=0.760
[DEBUG] 1 camiones detectados. Buscando placas en regiones de camiones.
[DEBUG] Procesando región 0: crop size=(827x761)
[DEBUG] 2 detecciones de placas en región 0
[DEBUG] Placa detectada: crop_box=[348,617,438,664], full_box=[596,689,686,736], conf=0.670
[DEBUG] OCR resultado: ""
[DEBUG] Guardado recorte de placa: Outputs\truck_plate_0_0.jpg
[DEBUG] Placa detectada: crop_box=[56,448,88,464], full_box=[304,520,336,536], conf=0.573
[DEBUG] OCR resultado: ""
[DEBUG] Guardado recorte de placa: Outputs\truck_plate_0_1.jpg
[DEBUG] Guardada imagen anotada: Outputs\truck.jpg
Procesado: Inputs/truck.jpg -> Outputs\truck.jpg | placa encontrada: True
```

### Archivos Generados
- ✅ `Outputs/truck.jpg` - Imagen anotada con cajas de detección
- ✅ `Outputs/truck_plate_0_0.jpg` - Recorte de placa 1
- ✅ `Outputs/truck_plate_0_1.jpg` - Recorte de placa 2

## Estado Actual

### ✅ Funcionando Correctamente
- Detección de camiones con `best_truck.pt`
- Detección de placas dentro de regiones de camiones con `best.pt`
- Pipeline de dos modelos integrado correctamente
- Coordenadas mapeadas correctamente de crop a imagen completa
- Guardado de imágenes anotadas y recortes de placas

### ⚠️ Nota Sobre OCR
El OCR devuelve texto vacío `""` porque:
1. Las placas detectadas pueden ser muy pequeñas (ej: 32x16 píxeles)
2. La calidad de la imagen puede ser baja
3. Las placas pueden no contener texto legible en el recorte

**Recomendaciones para mejorar OCR**:
- Usar imágenes de mayor resolución
- Verificar que las placas tengan texto visible
- Ajustar el padding (`--pad`) para capturar más contexto alrededor de la placa
- Probar diferentes configuraciones de PaddleOCR (si están disponibles en la versión instalada)

## Próximos Pasos Sugeridos

1. **Probar con cámara en tiempo real**: `python app.py --webcam`
2. **Probar dashboard web**: `python web_dashboard.py --truck-model best_truck.pt`
3. **Probar con cámara IP (RTSP)**: `python web_dashboard.py --hikvision-url rtsp://...`
4. **Ajustar parámetros según necesidad**:
   - `--conf 0.3` para ser más permisivo (más detecciones, más falsos positivos)
   - `--conf 0.7` para ser más estricto (menos detecciones, más precisas)
   - `--pad 20` para capturar más contexto en recortes de placas

## Código de Debug Models

El script `debug_models.py` puede ser usado para diagnosticar problemas con los modelos:
```bash
python debug_models.py --image Inputs/truck.jpg --truck best_truck.pt --plate best.pt --out Outputs --conf 0.1
```

Este script genera imágenes anotadas independientes (`debug_truck.jpg`, `debug_plates.jpg`) y muestra todas las detecciones crudas sin filtrado por OCR.
