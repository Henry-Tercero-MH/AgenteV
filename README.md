# 🦅 Falcon EPSA - Sistema de Detección de Placas Vehiculares

**Versión**: 0.3
**Desarrollado por**: Henry Misael Tercero Hernández
**Empresa**: EPSA (Empresa Pública de Servicios Ambientales)
**Supervisor**: Erick Pérez

---

## 📋 Descripción

Sistema inteligente de detección y reconocimiento de placas vehiculares utilizando **IA (YOLO)** y **OCR Híbrido** para control de acceso en garitas. Incluye API REST, WebSocket para tiempo real y dashboard web interactivo desarrollado en React.

### ✨ Características Principales

- 🚗 **Detección de Vehículos y Placas** con YOLO v8/v11
- 🔍 **OCR Híbrido Avanzado** (Tesseract + EasyOCR + PaddleOCR)
- ⚡ **API REST + WebSocket** para integración en tiempo real
- 📊 **Dashboard Web Moderno** con React 19
- 📹 **Sistema de Cámara** con procesamiento continuo
- 🎯 **Precisión 90-95%** en detección de placas
- 🔄 **Sistema de Votación** entre múltiples motores OCR

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────┐
│         SISTEMA FALCON EPSA v0.3            │
└─────────────────────────────────────────────┘

    📹 Cámara / Imagen
         ↓
    🔍 Detección YOLO
         ↓
    🖼️ Preprocesamiento (6 técnicas)
         ↓
    📝 OCR Híbrido (3 motores)
         ↓
    ✅ Validación y Corrección
         ↓
    💾 Base de Datos + API
         ↓
    🌐 Dashboard Web (React)
```

---

## 📁 Estructura del Proyecto

```
falconEpsa/
├── config/
│   └── settings.py              # Configuración centralizada
├── models/
│   ├── detector.py              # Detector YOLO de placas
│   ├── ocr_engine.py            # Motor OCR principal
│   └── ocr_engine_hybrid.py     # Motor OCR híbrido avanzado
├── utils/
│   ├── image_utils.py           # Procesamiento de imágenes
│   ├── text_utils.py            # Validación de texto
│   └── image_preprocessing.py   # Preprocesamiento avanzado
├── core/
│   └── pipeline.py              # Pipeline principal de detección
├── database/
│   ├── placas_db.json           # Base de placas autorizadas
│   └── logs_entrada_salida.json # Historial de eventos
├── dashboard-falcon/            # Frontend React
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   └── package.json
├── api_dashboard.py             # API REST + WebSocket
├── generar_db_placas.py         # Generador de BD de placas
├── start_dashboard.sh/bat       # Iniciar dashboard
├── start_falcon.sh              # Iniciar sistema completo
├── start_sistema_completo.bat   # Iniciar todo (Windows)
├── start_sistema_garita.sh/bat  # Iniciar modo garita
├── best.pt                      # Modelo YOLO de placas
├── best_truck.pt                # Modelo YOLO de vehículos
├── requirements.txt             # Dependencias Python
└── README.md                    # Este archivo
```

---

## 🚀 Instalación

### 1. Requisitos Previos

- **Python**: 3.13+ (recomendado 3.14)
- **Node.js**: 18+ (para dashboard)
- **Tesseract OCR**: Instalado en el sistema
- **Git**: Para clonar el repositorio
- **GPU CUDA** (opcional, mejora rendimiento)

### 2. Clonar Repositorio

```bash
git clone https://github.com/Henry-Tercero-MH/AgenteV.git
cd falconEpsa
```

### 3. Instalar Dependencias Python

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 4. Instalar Motores OCR Adicionales

```bash
# Recomendado para máxima precisión
pip install easyocr paddlepaddle paddleocr
```

### 5. Instalar Dashboard React

```bash
cd dashboard-falcon
npm install
cd ..
```

### 6. Configurar Tesseract

Editar la ruta en `models/ocr_engine_hybrid.py` línea 30:

```python
# Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Linux
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
```

---

## 💻 Uso

### Opción 1: Sistema Completo (API + Dashboard)

**Windows:**
```bash
start_sistema_completo.bat
```

**Linux/Mac:**
```bash
chmod +x start_falcon.sh
./start_falcon.sh
```

Esto iniciará:
- API en `http://localhost:8001`
- Dashboard en `http://localhost:5173`

### Opción 2: Solo API

```bash
python api_dashboard.py
```

Acceder a la documentación en `http://localhost:8001/docs`

### Opción 3: Solo Dashboard

**Windows:**
```bash
start_dashboard.bat
```

**Linux/Mac:**
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

### Opción 4: Modo Garita (Cámara en Tiempo Real)

**Windows:**
```bash
start_sistema_garita.bat
```

**Linux/Mac:**
```bash
chmod +x start_sistema_garita.sh
./start_sistema_garita.sh
```

---

## 🔧 Configuración

### Configuración Principal

Editar `config/settings.py`:

```python
# Modelos YOLO
MODELO_PLACAS = "best.pt"
MODELO_VEHICULOS = "best_truck.pt"

# Umbrales de confianza
CONFIANZA_VEHICULOS = 0.5
CONFIANZA_PLACAS = 0.3

# OCR
IDIOMA_OCR = "es"
LONGITUD_MIN_PLACA = 4
LONGITUD_MAX_PLACA = 10
```

### Activar/Desactivar Motores OCR

Editar `api_dashboard.py` línea 544:

```python
# OCR Híbrido (recomendado)
motor_ocr = MotorOCR(usar_hibrido=True)

# OCR Simple (más rápido)
motor_ocr = MotorOCR(usar_hibrido=False)
```

---

## 📡 API Endpoints

### REST API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/procesar-captura` | Procesar imagen y detectar placa |
| POST | `/api/registros/entrada` | Registrar entrada de vehículo |
| POST | `/api/registros/salida` | Registrar salida de vehículo |
| GET | `/api/registros/historial` | Obtener historial completo |
| GET | `/api/placas` | Listar placas autorizadas |
| POST | `/api/placas` | Agregar placa autorizada |

### WebSocket

```javascript
ws://localhost:8001/ws
```

Eventos:
- `nueva_deteccion`: Nueva placa detectada
- `entrada_registrada`: Entrada registrada
- `salida_registrada`: Salida registrada

---

## 📊 Métricas de Rendimiento

| Métrica | Valor |
|---------|-------|
| Precisión de detección | 90-95% |
| Confianza OCR | 99.9% (placas limpias) |
| Tiempo de procesamiento | 3-4s por imagen |
| Tasa de falsos positivos | <5% |
| Tasa de falsos negativos | <8% |
| Uptime continuo | 6+ horas sin errores |

---

## 🧪 Componentes del Sistema

### 1. Detección YOLO

- **Modelo de Vehículos** (`best_truck.pt`): Detecta autos, camiones, motos
- **Modelo de Placas** (`best.pt`): Detecta placas en regiones de vehículos
- **Precisión**: 90-95%

### 2. OCR Híbrido

Sistema de votación entre 3 motores:

| Motor | Velocidad | Precisión | GPU |
|-------|-----------|-----------|-----|
| Tesseract | ⚡⚡⚡ | ⭐⭐⭐ | ❌ |
| EasyOCR | ⚡⚡ | ⭐⭐⭐⭐ | ✅ |
| PaddleOCR | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ |

**Técnicas de Preprocesamiento:**
1. Bilateral filter + CLAHE + Sharpening
2. Binarización Otsu
3. Threshold adaptativo
4. Contraste agresivo
5. Inversión de colores
6. Operaciones morfológicas

### 3. Sistema de Validación

- Validación de formato con regex
- Filtrado de palabras clave (países, años)
- Validación de longitud (4-10 caracteres)
- Corrección automática de errores:
  - `O` ↔ `0`
  - `I` ↔ `1`
  - `S` ↔ `5`
  - `Z` ↔ `2`
  - `B` ↔ `8`

### 4. Dashboard React

**Componentes:**
- `CameraCapture.jsx`: Captura de cámara
- `PlateDetectionCard.jsx`: Visualización de detección
- `VehicleInfoCard.jsx`: Información del vehículo
- `ResultsTable.jsx`: Tabla de historial
- `StatisticsCards.jsx`: Estadísticas en tiempo real
- `ProcessingTimeChart.jsx`: Gráficos de rendimiento

**Tecnologías:**
- React 19.2.0
- Vite 7.2.2
- Tailwind CSS 3.4.1
- Recharts 3.4.1
- Axios

---

## 🛠️ Solución de Problemas

### Error: "Tesseract not found"

```bash
# Windows
# Descargar de: https://github.com/UB-Mannheim/tesseract/wiki

# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### Error: "CUDA not available"

El sistema funciona sin GPU, pero más lento. Para activar CUDA:

```bash
# Instalar PyTorch con CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### Error: "EasyOCR no disponible"

```bash
pip install easyocr
```

### Puerto 8001 ya en uso

Cambiar puerto en `api_dashboard.py` línea final:

```python
uvicorn.run(app, host="0.0.0.0", port=8002)  # Cambiar a 8002
```

---

## 🔐 Seguridad

- **CORS**: Configurado para desarrollo (`allow_origins=["*"]`)
- **Producción**: Restringir a dominios específicos
- **Base de Datos**: Actualmente JSON (migrar a PostgreSQL en producción)
- **Validación**: Todas las entradas son validadas con Pydantic

---

## 📈 Roadmap

### Próximas Mejoras

- [ ] Migrar a base de datos relacional (PostgreSQL)
- [ ] Sistema de reportes avanzados
- [ ] Filtros en dashboard (fecha, placa, confianza)
- [ ] Sistema de alertas y notificaciones
- [ ] Soporte para cámaras IP (RTSP/HTTP)
- [ ] Fine-tuning con dataset guatemalteco
- [ ] Soporte multi-país
- [ ] Docker/Docker Compose
- [ ] Autenticación y autorización
- [ ] Logs estructurados

---

## 📝 Base de Datos

### placas_db.json

```json
{
  "placas_autorizadas": [
    {
      "placa": "P353CCB",
      "propietario": "Juan Pérez",
      "tipo_vehiculo": "Auto",
      "fecha_registro": "2025-11-01T10:00:00"
    }
  ]
}
```

### logs_entrada_salida.json

```json
{
  "registros": [
    {
      "id": 1,
      "placa": "P353CCB",
      "tipo": "ENTRADA",
      "timestamp": "2025-11-23T10:30:00",
      "confianza": 0.95,
      "imagen": "captura_20251123_103000.jpg"
    }
  ]
}
```

---

## 🤝 Contribución

Este es un proyecto interno de EPSA. Para consultas o mejoras:

1. Contactar al supervisor del proyecto
2. Revisar documentación técnica
3. Seguir estándares de código Python (PEP 8)
4. Agregar tests para nuevas funcionalidades

---

## 📄 Licencia

Proyecto desarrollado para EPSA (Empresa Pública de Servicios Ambientales).
Todos los derechos reservados.

---

## 👨‍💻 Desarrollador

**Henry Misael Tercero Hernández**
Programador Jr. - EPSA
Proyecto: Falcon EPSA v0.3
Fecha: Noviembre 2025

---

## 📞 Soporte

Para reportar problemas o consultas técnicas:
- Supervisor: Erick Pérez
- Repositorio: https://github.com/Henry-Tercero-MH/AgenteV.git

---

**Estado del Proyecto**: ✅ **FUNCIONAL Y OPERATIVO**

*Sistema de Control de Garita - Detección Inteligente de Placas Vehiculares*
