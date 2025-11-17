# 🔍 Sistema de Escaneo Automático de Placas

## ✨ Nueva Funcionalidad: Modo Escáner QR

El dashboard ahora incluye un sistema de detección automática continua que funciona como un lector QR:

### 🚀 Características Principales

1. **Escaneo Continuo**: El sistema escanea constantemente el video en busca de placas
2. **Procesamiento en Segundo Plano**: Las detecciones se procesan sin bloquear el escaneo
3. **Detección Instantánea**: Cuando detecta una placa, la captura y procesa automáticamente
4. **Control de Duplicados**: Evita procesar la misma placa múltiples veces
5. **Feedback Visual**: Muestra estadísticas en tiempo real de escaneos y detecciones
6. **Sonido de Confirmación**: Reproduce un beep cuando detecta una placa (opcional)

### 📋 Cómo Usar

#### 1. Iniciar el Sistema

```bash
# Terminal 1: Iniciar API Backend
cd C:/Users/henry/Desktop/Codigos-Proyectos/falconEpsa
python api_dashboard.py

# Terminal 2: Iniciar Dashboard React
cd C:/Users/henry/Desktop/Codigos-Proyectos/falconEpsa/dashboard-falcon
npm run dev
```

#### 2. Usar el Dashboard

1. **Abrir el Dashboard**: http://localhost:5173
2. **Activar la Cámara**: Click en "Iniciar Cámara"
3. **Activar Escaneo Automático**:
   - Marcar el checkbox "🔍 Escaneo Automático"
   - Seleccionar velocidad de escaneo:
     - ⚡ Rápido (300ms) - Para detecciones muy rápidas
     - 🚀 Medio (500ms) - **Recomendado**
     - 🐢 Lento (1s) - Para equipos más lentos
     - 🐌 Muy lento (2s) - Para procesamiento pesado

4. **Mostrar Placa a la Cámara**:
   - El sistema escanea continuamente
   - Cuando detecta una placa, la procesa automáticamente
   - Verás un contador de escaneos y detecciones en tiempo real

### 📊 Estadísticas en Tiempo Real

El panel muestra:
- **Escaneos**: Número total de frames escaneados
- **Detectadas**: Número de placas detectadas exitosamente
- **Último escaneo**: Hora del último escaneo realizado

### 🎯 Ventajas vs Modo Manual

**Modo Manual (Antiguo)**:
- ❌ Requiere hacer click en "Capturar" cada vez
- ❌ Puede perder placas si no se captura a tiempo
- ❌ Proceso lento y manual

**Modo Escaneo Automático (Nuevo)**:
- ✅ Detección continua sin intervención
- ✅ Captura automática al detectar placas
- ✅ Procesa múltiples vehículos sin intervención
- ✅ Ideal para garita con flujo continuo

### ⚙️ Configuración del Backend

El endpoint `/api/procesar-captura` ya está configurado para:
- ✅ Recibir imágenes desde el dashboard
- ✅ Detectar placas con YOLO
- ✅ Extraer texto con PaddleOCR
- ✅ Validar contra base de datos
- ✅ Registrar automáticamente en logs
- ✅ Enviar notificaciones via WebSocket

### 🔧 Ajustes de Rendimiento

**Si el sistema va lento**:
1. Reducir velocidad de escaneo (usar modo "Lento" o "Muy lento")
2. Verificar que el API esté usando GPU si está disponible
3. Cerrar otras aplicaciones pesadas

**Si se pierden detecciones**:
1. Aumentar velocidad de escaneo (usar modo "Rápido")
2. Mejorar iluminación de la cámara
3. Acercar más la placa a la cámara

### 📝 Logs y Debugging

En la consola del navegador verás:
- `🔍 Escaneando frame...` - Cada vez que escanea
- `✅ Placa(s) detectada(s)` - Cuando encuentra placas
- `⚠️ API no disponible` - Si el backend no responde
- `⏭️ Cola de procesamiento llena` - Si hay muchas detecciones pendientes

### 🐛 Solución de Problemas

**Error 404 al procesar captura**:
- Verificar que `api_dashboard.py` esté corriendo
- Verificar que el puerto sea 8001: `netstat -ano | grep 8001`
- Verificar URL del API en el dashboard (http://localhost:8001)

**No detecta placas**:
- Verificar iluminación
- Acercar más la placa
- Verificar que los modelos YOLO estén cargados
- Revisar logs del API en la terminal

**Sistema muy lento**:
- Reducir velocidad de escaneo a 1-2 segundos
- Verificar uso de CPU/GPU
- Cerrar otras aplicaciones

### 🎬 Flujo de Trabajo Completo

```
1. Usuario muestra placa a cámara
   ↓
2. Sistema escanea frame cada X ms
   ↓
3. Envía frame al backend en segundo plano
   ↓
4. YOLO detecta placa en frame
   ↓
5. PaddleOCR extrae texto de placa
   ↓
6. Backend valida contra DB
   ↓
7. Registra entrada/salida automáticamente
   ↓
8. Envía notificación al dashboard via WebSocket
   ↓
9. Dashboard muestra detección + sonido
   ↓
10. Sistema continúa escaneando siguiente vehículo
```

### 🔐 Seguridad

- Control de duplicados: No procesa la misma placa varias veces seguidas
- Timeout: Requests al backend tienen timeout de 10 segundos
- Cola limitada: Máximo 2 frames en procesamiento simultáneo
- Validación: Backend valida imágenes antes de procesar

## 📚 Archivos Modificados

- `dashboard-falcon/src/components/CameraCapture.jsx` - Componente principal mejorado
- `api_dashboard.py` - Endpoint `/api/procesar-captura` ya existente

## 🎉 ¡Listo para Producción!

El sistema ahora funciona como una **garita automática**:
- Vehículo se acerca
- Cámara detecta placa automáticamente
- Sistema registra entrada/salida
- Vehículo puede pasar
- Todo sin intervención manual

---

**Desarrollado para**: Falcon EPSA
**Versión**: 2.0 - Escaneo Automático
**Fecha**: 2025-01-16
