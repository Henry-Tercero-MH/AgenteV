# 🦅 Falcon EPSA - Sistema Completo de Control de Garita

## 🎯 Descripción General

Sistema automatizado de control de garita con detección de placas vehiculares en tiempo real usando cámara, procesamiento con IA (YOLO + OCR), validación contra base de datos y dashboard interactivo con actualizaciones en vivo.

## ⚡ Inicio Rápido - 1 Click

```bash
# Windows
start_sistema_completo.bat
```

Esto iniciará automáticamente:
1. ✅ API Backend (FastAPI + WebSocket)
2. ✅ Dashboard React (Interfaz web)
3. ✅ Sistema de Cámara (Detección en tiempo real)

**Accesos:**
- 🌐 Dashboard: http://localhost:5173
- 📡 API: http://localhost:8001
- 📚 Docs API: http://localhost:8001/docs
- 🎥 Cámara: Ventana OpenCV

---

## 📋 Tabla de Contenidos

1. [Características](#-características)
2. [Arquitectura del Sistema](#-arquitectura-del-sistema)
3. [Instalación](#-instalación)
4. [Uso](#-uso)
5. [Componentes](#-componentes)
6. [Flujo de Trabajo](#-flujo-de-trabajo)
7. [API Endpoints](#-api-endpoints)
8. [Dashboard](#-dashboard)
9. [Documentación Adicional](#-documentación-adicional)
10. [Troubleshooting](#-troubleshooting)

---

## 🌟 Características

### Sistema de Cámara
- ✅ Detección automática 24/7
- ✅ Procesamiento en segundo plano (multithreading)
- ✅ Sistema de cooldown inteligente
- ✅ Soporte para webcam e IP cameras
- ✅ Guardado automático de capturas
- ✅ Estadísticas en tiempo real

### Backend (API)
- ✅ FastAPI con documentación automática
- ✅ WebSocket para tiempo real
- ✅ Sistema de logs completo
- ✅ Validación automática contra DB
- ✅ Endpoints RESTful

### Dashboard (React)
- ✅ Actualización en tiempo real (WebSocket)
- ✅ Layout dividido: Placa + Datos
- ✅ Historial completo de registros
- ✅ Estadísticas visuales
- ✅ Responsive design

### Detección IA
- ✅ YOLO v8 para detección de placas
- ✅ OCR para extracción de texto
- ✅ Validación de formato
- ✅ Alta precisión (>90%)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA FALCON EPSA                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   CÁMARA     │       │     API      │       │  DASHBOARD   │
│   OpenCV     │ ────► │   FastAPI    │ ◄───► │    React     │
│              │       │  + WebSocket │       │              │
└──────┬───────┘       └──────┬───────┘       └──────────────┘
       │                      │
       │                      │
       ▼                      ▼
┌──────────────┐       ┌──────────────┐
│ YOLO + OCR   │       │  Database    │
│  Detection   │       │  JSON Logs   │
└──────────────┘       └──────────────┘

Flujo:
Cámara → Detección → Validación → API → WebSocket → Dashboard
                                  ↓
                              Base de Datos
```

---

## 💻 Instalación

### Requisitos
- Python 3.12+
- Node.js 18+
- Cámara (webcam o IP camera)
- 8GB RAM mínimo
- GPU recomendada (para mejor rendimiento)

### Paso 1: Clonar el Repositorio
```bash
git clone <repo>
cd falconEpsa
```

### Paso 2: Instalar Dependencias Python
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 3: Instalar Dependencias Node.js
```bash
cd dashboard-falcon
npm install
cd ..
```

### Paso 4: Generar Base de Datos
```bash
# Asegúrate de tener resultados procesados primero
python process_batch.py --input Inputs --output Outputs

# Generar base de datos de placas
python generar_db_placas.py
```

---

## 🚀 Uso

### Método 1: Automático (Recomendado)
```bash
start_sistema_completo.bat
```

### Método 2: Manual (Paso a Paso)

**Terminal 1 - API:**
```bash
python api_dashboard.py
```

**Terminal 2 - Dashboard:**
```bash
cd dashboard-falcon
npm run dev
```

**Terminal 3 - Cámara:**
```bash
python camera_garita.py
```

### Método 3: Solo Pruebas (Sin Cámara)
```bash
# Terminal 1
python api_dashboard.py

# Terminal 2
cd dashboard-falcon
npm run dev

# Terminal 3
python test_garita.py
```

---

## 🧩 Componentes

### 1. Sistema de Cámara (`camera_garita.py`)

**Función:** Captura video en tiempo real y detecta placas automáticamente

**Características:**
- Procesamiento en segundo plano (threading)
- Sistema de cooldown (evita duplicados)
- Guardado automático de capturas
- Estadísticas en vivo

**Uso:**
```bash
python camera_garita.py \
  --camera 0 \
  --api http://localhost:8001 \
  --cooldown 30
```

**Controles:**
- `ESPACIO`: Captura manual
- `q` o `ESC`: Salir
- `s`: Ver estadísticas

### 2. API Backend (`api_dashboard.py`)

**Función:** Servidor REST + WebSocket para gestión de detecciones

**Endpoints principales:**
- `POST /api/registros/entrada` - Registrar detección
- `GET /api/registros/historial` - Ver historial
- `GET /api/placas/validar/{placa}` - Validar placa
- `ws://localhost:8001/ws` - WebSocket

**Documentación:** http://localhost:8001/docs

### 3. Dashboard React (`dashboard-falcon/`)

**Función:** Interfaz web para visualización en tiempo real

**Características:**
- WebSocket para actualizaciones instantáneas
- Layout dividido: Placa (izq.) + Datos (der.)
- Historial completo de registros
- Indicador de conexión

**URL:** http://localhost:5173

### 4. Script de Pruebas (`test_garita.py`)

**Función:** Simula detecciones sin necesidad de cámara

**Uso:**
```bash
python test_garita.py
```

Opciones:
1. Simular placa registrada
2. Simular placa NO registrada
3. Simular múltiples detecciones automáticas
4. Ver historial

---

## 🔄 Flujo de Trabajo

### Flujo Completo (Con Cámara)

```
1. CÁMARA DETECTA VEHÍCULO
   ↓
2. YOLO DETECTA PLACA
   ↓
3. OCR EXTRAE TEXTO
   │
   ├─ Valida formato
   ├─ Verifica cooldown
   └─ Si OK → Continúa
   ↓
4. POST AL API
   /api/registros/entrada
   {
     "placa": "ABC123",
     "confianza": 0.95
   }
   ↓
5. API VALIDA EN DB
   │
   ├─ ✓ Registrada → Obtiene datos
   └─ ✗ No registrada → Alerta
   ↓
6. GUARDA EN LOGS
   database/logs_entrada_salida.json
   ↓
7. BROADCAST WEBSOCKET
   Notifica a todos los clientes
   ↓
8. DASHBOARD ACTUALIZA
   - Placa (izquierda)
   - Datos (derecha)
   - Historial
```

### Detección de Placa Registrada

```
Vehículo "ABC123" entra
  ↓
Cámara detecta placa
  ↓
Sistema valida en DB → ENCONTRADA
  ↓
Dashboard muestra:
  ┌─────────────────┬─────────────────┐
  │ PLACA: ABC123   │ REGISTRADA ✓    │
  │ [Imagen]        │ Propietario:... │
  │ Confianza: 95%  │ Tipo: Comercial │
  │ Entrada 10:30   │ Estado: Normal  │
  └─────────────────┴─────────────────┘
```

### Detección de Placa NO Registrada

```
Vehículo "XYZ999" entra
  ↓
Cámara detecta placa
  ↓
Sistema valida en DB → NO ENCONTRADA
  ↓
Dashboard muestra:
  ┌─────────────────┬─────────────────┐
  │ PLACA: XYZ999   │ NO REGISTRADA ✗ │
  │ [Imagen]        │ ⚠️  ALERTA      │
  │ Confianza: 88%  │ Placa no está   │
  │ Entrada 10:35   │ en el sistema   │
  └─────────────────┴─────────────────┘
```

---

## 📡 API Endpoints

### Registros

**POST /api/registros/entrada**
```json
// Request
{
  "placa": "ABC123",
  "confianza": 0.95,
  "imagen_path": "Outputs/captura.jpg"
}

// Response (Registrada)
{
  "registro": {
    "id": 1,
    "placa": "ABC123",
    "timestamp": "2025-11-16T10:30:00",
    "tipo_evento": "ENTRADA",
    "registrada": true
  },
  "placa_info": {
    "propietario": "Juan Pérez",
    "tipo_vehiculo": "PARTICULAR",
    "estado": "AUTORIZADO"
  }
}
```

**GET /api/registros/historial?limit=50**
```json
{
  "registros": [
    {
      "id": 1,
      "placa": "ABC123",
      "timestamp": "2025-11-16T10:30:00",
      "tipo_evento": "ENTRADA",
      "registrada": true
    }
  ],
  "total": 45
}
```

**GET /api/registros/placa/{placa}**
```json
{
  "placa": "ABC123",
  "registros": [...],
  "total": 5
}
```

### Placas

**GET /api/placas/validar/{placa}**
**GET /api/placas/todas**

### WebSocket

**ws://localhost:8001/ws**

Mensaje recibido:
```json
{
  "tipo": "nueva_deteccion",
  "data": {
    "registro": {...},
    "placa_info": {...},
    "registrada": true
  }
}
```

---

## 🎨 Dashboard

### Layout Principal

```
┌────────────────────────────────────────────────────────────┐
│  🦅 Falcon EPSA - Control de Garita    🟢 Conectado       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌─────────────────────┐  ┌─────────────────────────┐    │
│  │ PLACA DETECTADA     │  │ DATOS DEL VEHÍCULO      │    │
│  │                     │  │                         │    │
│  │  ✓ REGISTRADA       │  │ Propietario: Juan P.    │    │
│  │                     │  │ Tipo: PARTICULAR        │    │
│  │  ┌──────────┐       │  │ Estado: AUTORIZADO      │    │
│  │  │ ABC123   │       │  │ Depto: Guatemala        │    │
│  │  └──────────┘       │  │                         │    │
│  │                     │  │ Historial:              │    │
│  │  [Imagen]           │  │  • Entrada: 10:30 AM    │    │
│  │                     │  │  • Entrada: 08:15 AM    │    │
│  │  Confianza: 95%     │  │  • Salida:  05:30 PM    │    │
│  │  10:30:00           │  │                         │    │
│  │  ➡️  ENTRADA         │  │                         │    │
│  └─────────────────────┘  └─────────────────────────┘    │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  📋 HISTORIAL COMPLETO                                    │
│  ┌────────────────────────────────────────────────────┐   │
│  │ #  │ Placa   │ Evento  │ Fecha      │ Estado     │   │
│  │ 1  │ ABC123  │ ENTRADA │ 16/11 10:30│ ✓ Reg.     │   │
│  │ 2  │ XYZ789  │ ENTRADA │ 16/11 10:35│ ✗ No Reg.  │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## 📚 Documentación Adicional

- **[Sistema de Garita](SISTEMA_GARITA_README.md)** - API y Backend
- **[Sistema de Cámara](SISTEMA_CAMARA_GARITA.md)** - Detección en tiempo real
- **[Inicio Rápido](INICIO_RAPIDO_GARITA.md)** - Guía de inicio rápido

---

## 🐛 Troubleshooting

### El sistema no inicia

**Verificar API:**
```bash
curl http://localhost:8001/health
# Debe retornar: {"status":"ok"}
```

**Verificar Dashboard:**
```bash
cd dashboard-falcon
npm run dev
# Debe abrir en http://localhost:5173
```

### La cámara no funciona

```bash
# Listar cámaras disponibles
python -c "import cv2; [print(f'Cámara {i}: {cv2.VideoCapture(i).isOpened()}') for i in range(4)]"

# Probar con otra cámara
python camera_garita.py --camera 1
```

### WebSocket no conecta

- Verificar que el API esté corriendo
- Revisar consola del navegador (F12)
- Verificar que el puerto 8001 esté libre

### No detecta placas

- Verificar iluminación
- Asegurar que las placas estén en foco
- Verificar que el modelo YOLO esté cargado
- Revisar logs del sistema

---

## 📊 Especificaciones Técnicas

### Hardware Recomendado
- CPU: Intel i7 o superior
- RAM: 16GB
- GPU: NVIDIA GTX 1050+ (opcional pero recomendado)
- Cámara: 1080p @ 30fps

### Software
- Python: 3.12+
- Node.js: 18+
- OpenCV: 4.x
- YOLO: v8
- React: 19.x
- FastAPI: 0.115+

### Rendimiento
- FPS Cámara: 25-30
- Latencia Detección: 1-3 segundos
- Latencia WebSocket: <100ms
- Precisión OCR: >90%

---

## 🔐 Seguridad

- ✅ Logs completos de todos los accesos
- ✅ Imágenes guardadas con timestamp
- ✅ Validación de formato de placas
- ✅ Sistema de cooldown anti-duplicados
- ⚠️  Usar HTTPS en producción
- ⚠️  Cambiar contraseñas de cámaras IP

---

## 🎯 Casos de Uso

1. **Control de Acceso Vehicular** - Garita de seguridad
2. **Estacionamientos** - Registro de entrada/salida
3. **Peajes** - Cobro automático
4. **Zonas Restringidas** - Validación de autorizaciones
5. **Edificios Corporativos** - Control de visitantes

---

## 🚀 Roadmap Futuro

- [ ] Detección de dirección (entrada/salida)
- [ ] Múltiples cámaras simultáneas
- [ ] Base de datos SQL (PostgreSQL)
- [ ] Reconocimiento facial del conductor
- [ ] Alertas por email/SMS
- [ ] Exportar reportes PDF/Excel
- [ ] App móvil para guardias
- [ ] Integración con barreras automáticas

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar la documentación
2. Verificar logs del sistema
3. Consultar sección de Troubleshooting

---

## 📄 Licencia

Este proyecto fue desarrollado para Falcon EPSA.

---

**🦅 Falcon EPSA - Sistema de Control de Garita Automatizado**

*Detectando vehículos, protegiendo accesos.*
