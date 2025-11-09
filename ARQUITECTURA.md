# Sistema de Detección de Placas - Arquitectura Modular v2.0

## 📁 Estructura del Proyecto

```
falconEpsa/
├── app.py                      # Script principal CLI (100 líneas) ✨
├── web_dashboard.py            # Dashboard web (versión anterior)
├── ocr_wrapper.py              # Wrapper OCR Python 3.13
├── best.pt                     # Modelo YOLO placas
├── best_truck.pt               # Modelo YOLO camiones
│
├── config/                     # ⚙️ Configuración
│   ├── __init__.py
│   └── settings.py            # Parámetros centralizados
│
├── models/                     # 🤖 Modelos de IA
│   ├── __init__.py
│   ├── detector.py            # Detector YOLO (placas + camiones)
│   └── ocr_engine.py          # Motor OCR con PaddleOCR
│
├── utils/                      # 🛠️ Utilidades
│   ├── __init__.py
│   ├── text_utils.py          # Validación y limpieza de texto
│   └── image_utils.py         # Procesamiento de imágenes
│
├── core/                       # 🎯 Lógica principal
│   ├── __init__.py
│   └── pipeline.py            # Pipeline de detección completo
│
├── Inputs/                     # 📥 Imágenes de entrada
└── Outputs/                    # 📤 Resultados
```

## 🚀 Uso

### Instalación

```bash
# Python 3.14 (entorno principal)
python -m venv venv
source venv/Scripts/activate  # Windows Git Bash
pip install -r requirements.txt

# Python 3.13 (entorno para OCR)
python3.13 -m venv venv_old_3.13
source venv_old_3.13/Scripts/activate
pip install paddlepaddle paddleocr
```

### Comandos

```bash
# Procesar una imagen
python app.py --source Inputs/camion.jpg --model best.pt --truck-model best_truck.pt

# Procesar un directorio completo
python app.py --source Inputs/ --model best.pt --conf 0.3

# Ajustar umbral de confianza
python app.py --source Inputs/test.jpg --model best.pt --conf 0.4

# Especificar carpeta de salida
python app.py --source Inputs/test.jpg --model best.pt --output Resultados
```

## 📦 Módulos

### 1. `config/settings.py`
Configuración centralizada del sistema:
- Rutas de modelos
- Parámetros de detección
- Configuración OCR
- Reglas de validación de placas

### 2. `models/detector.py`
Clase `DetectorPlacas`:
- `detectar_camiones()` - Detecta vehículos en la imagen
- `detectar_placas_en_region()` - Encuentra placas en regiones específicas
- `generar_regiones_busqueda()` - Crea zonas de búsqueda optimizadas

### 3. `models/ocr_engine.py`
Clase `MotorOCR`:
- `extraer_texto()` - Reconoce texto de placas con PaddleOCR
- Validación inteligente de formato de placas
- Deduplicación automática de textos

### 4. `utils/text_utils.py`
Utilidades de texto:
- `limpiar_texto()` - Normaliza texto (solo alfanuméricos)
- `es_placa_valida()` - Valida formato usando patrones regex
- `deduplicar_textos()` - Elimina duplicados y subcadenas

### 5. `utils/image_utils.py`
Utilidades de imagen:
- `convertir_a_numpy()` - Conversión segura de tensores
- `redimensionar_placa()` - Mejora resolución para OCR
- `recortar_region()` - Extrae regiones con validación
- `dibujar_deteccion()` - Anota imágenes con resultados

### 6. `core/pipeline.py`
Clase `PipelineDeteccion`:
- `procesar_imagen()` - Pipeline completo para una imagen
- `procesar_directorio()` - Procesamiento por lotes

## 🎯 Ventajas de la Arquitectura Modular

### ✅ Mantenibilidad
- Cada módulo tiene una responsabilidad única (SRP)
- Código organizado y fácil de navegar
- Cambios localizados no afectan otros módulos

### ✅ Testabilidad
- Cada clase puede probarse independientemente
- Mock fácil de dependencias
- Tests unitarios por módulo

### ✅ Reutilización
- `DetectorPlacas` puede usarse en otros proyectos
- `MotorOCR` es independiente del detector
- Utilidades son funciones puras

### ✅ Escalabilidad
- Agregar nuevos detectores sin modificar existentes
- Cambiar motor OCR sin tocar pipeline
- Extensible con nuevas utilidades

### ✅ Configuración Centralizada
- Un solo lugar para cambiar parámetros
- Fácil ajuste de umbrales y rutas
- Consistencia en todo el proyecto

## 📊 Comparación: Antes vs Después

| Aspecto | Versión Anterior | Versión Modular |
|---------|------------------|-----------------|
| **Líneas totales** | 732 en 1 archivo | ~500 en 8 módulos |
| **Funciones por archivo** | 15+ | 3-5 promedio |
| **Acoplamiento** | Alto | Bajo |
| **Testeable** | Difícil | Fácil |
| **Navegación** | Scroll infinito | Estructura clara |
| **Reutilización** | No | Sí |
| **Mantenimiento** | Complejo | Simple |

## 🔧 Configuración

Edita `config/settings.py` para ajustar:

```python
# Modelos
MODELO_PLACAS_DEFAULT = 'best.pt'
MODELO_CAMIONES_DEFAULT = 'best_truck.pt'

# Detección
UMBRAL_CONFIANZA_DEFAULT = 0.5
PADDING_RECORTE = 15

# Validación de placas
LONGITUD_MIN_PLACA = 4
LONGITUD_MAX_PLACA = 10
DIGITOS_MIN_PLACA_ANTIGUA = 5

# Filtros de país
PALABRAS_CLAVE_PAIS = ['GUATEMALA', 'MEXICO', 'CENTRO', 'AMÉRICA', 'AMERICA']
```

## 🐛 Debugging

Todos los módulos imprimen mensajes `[DEBUG]` para seguir el flujo:

```
[INFO] Modelo de placas cargado: best.pt
[INFO] Modelo de camiones cargado: best_truck.pt
[INFO] Motor OCR inicializado correctamente
[INFO] Procesando: Inputs/test3.png
[DEBUG] Ejecutando modelo de camiones...
[DEBUG] No se detectaron camiones. Buscando placas en la imagen completa.
[DEBUG] Procesando región 0: crop size=(247x500)
[DEBUG] 1 detecciones de placas en región 0
[DEBUG] Placa detectada: full_box=[4,14,460,238], conf=0.848
[DEBUG] Textos OCR: ['GUATEMALA', 'P123SAT', 'CENTRO AMÉRICA'] -> resultado: [P123SAT]
[DEBUG] Resultado OCR: "P123SAT" conf=0.949
```

## 📝 TODOs

- [ ] Implementar `utils/camera_utils.py` para webcam
- [ ] Agregar tests unitarios en `tests/`
- [ ] Crear `requirements-dev.txt` para desarrollo
- [ ] Documentación API con Sphinx
- [ ] Modo batch con multiprocessing
- [ ] Cache inteligente de resultados OCR

## 📄 Licencia

Proyecto interno - FalconEPSA

---

**Nota**: El archivo `app_old.py` contiene la versión monolítica anterior como respaldo.
