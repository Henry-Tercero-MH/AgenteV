# 📹 Guía: Dashboard React con Cámara Integrada

## 🎯 Sistema Completamente Integrado en React

El sistema de control de garita ahora está **100% integrado en el dashboard React**. La cámara web funciona directamente desde el navegador.

---

## 🚀 Inicio Rápido

### 1. Iniciar el Backend
```bash
# Terminal 1
python api_dashboard.py
```

### 2. Iniciar el Dashboard React
```bash
# Terminal 2
cd dashboard-falcon
npm run dev
```

### 3. Abrir en el Navegador
```
http://localhost:5173
```

---

## 📱 Interfaz del Dashboard

### Layout Completo

```
┌─────────────────────────────────────────────────────────────┐
│  🦅 Falcon EPSA - Control de Garita    🟢 Conectado        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  📹 CÁMARA DE DETECCIÓN                               │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │                                                  │  │ │
│  │  │         [VIDEO EN VIVO DE LA CÁMARA]            │  │ │
│  │  │                                                  │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  │                                                        │ │
│  │  [Iniciar Cámara]  [Capturar Frame]  [Detener]       │ │
│  │  ☑ Auto-Captura (Intervalo: 5s)                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────┐ │
│  │ PLACA DETECTADA     │  │ DATOS DEL VEHÍCULO          │ │
│  │  ✓ REGISTRADA       │  │  Propietario: Juan Pérez    │ │
│  │  ABC123             │  │  Tipo: PARTICULAR           │ │
│  │  [Imagen]           │  │  Estado: AUTORIZADO         │ │
│  │  Confianza: 95%     │  │  Historial: [...]           │ │
│  └─────────────────────┘  └─────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  📋 HISTORIAL COMPLETO DE REGISTROS                   │ │
│  │  [Tabla con todos los registros...]                   │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎥 Uso de la Cámara

### Paso 1: Permisos de Cámara

Al hacer clic en **"Iniciar Cámara"**, el navegador pedirá permisos:

```
┌──────────────────────────────────────┐
│ localhost:5173 desea usar tu cámara │
│                                      │
│  [ Bloquear ]      [ Permitir ]     │
└──────────────────────────────────────┘
```

✅ Selecciona **"Permitir"**

### Paso 2: Modos de Captura

#### Modo Manual
1. Presiona **"Capturar Frame"** cuando veas un vehículo
2. El sistema automáticamente:
   - 📸 Captura la imagen
   - ⬆️  Envía al backend
   - 🤖 Detecta placas con YOLO + OCR
   - ✓ Valida contra base de datos
   - 📡 Actualiza el dashboard vía WebSocket

#### Modo Auto-Captura
1. Activa el checkbox **"Auto-Captura"**
2. Selecciona intervalo (3s, 5s, 10s, 15s, 30s)
3. El sistema captura automáticamente cada X segundos

```
☑ Auto-Captura (Intervalo: 5s)
🔄 La cámara capturará automáticamente cada 5 segundos
```

---

## 🔄 Flujo Completo

```
1. USUARIO → Presiona "Capturar Frame" (o auto-captura)
              ↓
2. REACT → Captura frame del video con canvas
              ↓
3. REACT → Envía imagen al backend (POST /api/procesar-captura)
              ↓
4. BACKEND → Recibe imagen y la guarda temporalmente
              ↓
5. BACKEND → Procesa con YOLO + OCR
              ↓
6. BACKEND → Detecta placas y extrae texto
              ↓
7. BACKEND → Valida en base de datos
              ↓
8. BACKEND → Guarda en logs_entrada_salida.json
              ↓
9. BACKEND → Envía notificación por WebSocket
              ↓
10. REACT → Recibe notificación y actualiza dashboard
              ↓
11. DASHBOARD → Muestra placa + datos en tiempo real
```

---

## ⚙️ Características

### Componente de Cámara

✅ **Feed de video en vivo** directo en el navegador
✅ **Captura manual** con botón
✅ **Auto-captura** con intervalo configurable
✅ **Vista previa** de última captura
✅ **Controles intuitivos** (Iniciar/Detener/Capturar)
✅ **Indicador de procesamiento** mientras analiza

### Procesamiento Backend

✅ **Endpoint dedicado** (`POST /api/procesar-captura`)
✅ **Detección automática** con YOLO
✅ **OCR** para extraer texto de placas
✅ **Validación** contra base de datos
✅ **Registro automático** con timestamp
✅ **Broadcast WebSocket** a todos los clientes

### Dashboard en Tiempo Real

✅ **Actualización instantánea** (< 100ms)
✅ **Sin recargar página**
✅ **Indicador de conexión** WebSocket
✅ **Historial completo** de detecciones
✅ **Información detallada** del vehículo

---

## 🎯 Casos de Uso

### Caso 1: Captura Manual en Garita

**Escenario:** Guardia de seguridad ve llegar un vehículo

1. Vehículo se detiene frente a la garita
2. Guardia presiona **"Capturar Frame"**
3. Sistema detecta placa "ABC123"
4. Dashboard muestra:
   - ✅ PLACA REGISTRADA
   - Propietario: Juan Pérez
   - Estado: AUTORIZADO
5. Guardia autoriza el paso

### Caso 2: Auto-Captura Continua

**Escenario:** Monitoreo 24/7 de entrada/salida

1. Guardia activa **Auto-Captura** con intervalo de 5s
2. Sistema captura automáticamente cada 5 segundos
3. Cuando detecta una placa:
   - Registra automáticamente
   - Muestra en dashboard
   - Guarda en historial
4. Guardia solo supervisa el dashboard

### Caso 3: Placa No Registrada

**Escenario:** Vehículo desconocido intenta entrar

1. Sistema captura frame
2. Detecta placa "XXX999"
3. Dashboard muestra:
   - ❌ PLACA NO REGISTRADA
   - Alerta roja
   - "Placa no está en el sistema"
4. Guardia detiene el vehículo para verificación manual

---

## 🔧 Configuración

### Cambiar Intervalo de Auto-Captura

En el dashboard, selecciona del dropdown:
- **3s** - Muy frecuente (alto consumo de recursos)
- **5s** - Recomendado para tráfico moderado
- **10s** - Recomendado para tráfico bajo
- **15s** - Monitoreo espaciado
- **30s** - Monitoreo ocasional

### Calidad de Imagen

La cámara captura en:
- **Resolución:** 1280x720 (720p)
- **Formato:** JPEG
- **Calidad:** 90%

Para cambiar, edita `CameraCapture.jsx`:
```javascript
video: {
  width: { ideal: 1920 },  // Full HD
  height: { ideal: 1080 },
  facingMode: 'environment'
}
```

---

## 🐛 Solución de Problemas

### La cámara no se activa

**Problema:** Al presionar "Iniciar Cámara" no pasa nada

**Soluciones:**
1. Verifica que estés en HTTPS o localhost
2. Revisa permisos del navegador (Configuración → Privacidad)
3. Asegúrate de tener una cámara web conectada
4. Prueba en otro navegador (Chrome recomendado)

### "No se detectaron placas"

**Problema:** La captura se envía pero no detecta placas

**Soluciones:**
1. Verifica que el vehículo esté bien enfocado
2. Asegura buena iluminación
3. La placa debe estar visible y legible
4. Intenta acercar más la cámara
5. Verifica que el modelo YOLO esté cargado

### El dashboard no se actualiza

**Problema:** La detección funciona pero el dashboard no actualiza

**Soluciones:**
1. Verifica el indicador WebSocket (debe estar verde)
2. Revisa la consola del navegador (F12)
3. Recarga la página
4. Verifica que el API esté corriendo

### Error de conexión con API

**Problema:** "Error al conectar con el servidor"

**Soluciones:**
1. Verifica que el API esté corriendo: `http://localhost:8001/health`
2. Revisa que el puerto 8001 esté libre
3. Comprueba que `API_URL` en App.jsx sea correcto
4. Revisa CORS en api_dashboard.py

---

## 📊 Rendimiento

### Tiempos Típicos

- **Captura de frame:** < 100ms
- **Envío al backend:** ~200-500ms
- **Procesamiento YOLO + OCR:** 1-3 segundos
- **WebSocket a dashboard:** < 100ms
- **Total:** ~2-4 segundos desde captura hasta visualización

### Consumo de Recursos

**Frontend (React):**
- RAM: ~100-200MB
- CPU: 5-10% (con cámara activa)

**Backend (Python):**
- RAM: ~500MB-1GB (con modelos YOLO cargados)
- CPU: 20-50% (durante procesamiento)

---

## 🔐 Seguridad

### Permisos de Cámara

- El navegador siempre pide permiso explícito
- Los permisos se pueden revocar en cualquier momento
- Solo funciona en localhost o HTTPS

### Privacidad

- Las imágenes se procesan en el backend local
- No se envían a servicios externos
- Las capturas se guardan localmente en `Outputs/`

### Datos

- Los logs se guardan en JSON local
- No hay conexión a internet requerida
- Todo el procesamiento es on-premise

---

## 📱 Compatibilidad

### Navegadores Soportados

✅ **Chrome/Chromium** - Recomendado
✅ **Edge** - Compatible
✅ **Firefox** - Compatible
⚠️ **Safari** - Compatible pero con restricciones
❌ **IE** - No soportado

### Dispositivos

✅ **Desktop** (Windows/Mac/Linux)
✅ **Laptop** con webcam
✅ **Tablet** (Chrome/Safari)
✅ **Móvil** (experimental)

---

## 🚀 Mejoras Futuras

- [ ] Soporte para múltiples cámaras
- [ ] Zoom digital
- [ ] Filtros de imagen (contraste, brillo)
- [ ] Captura automática al detectar movimiento
- [ ] Grabación de video
- [ ] Exportar capturas como PDF
- [ ] Modo nocturno/infrarojo
- [ ] Notificaciones de escritorio

---

## ✅ Checklist de Uso

Antes de usar el sistema:

- [ ] Backend API corriendo en puerto 8001
- [ ] Dashboard React corriendo en puerto 5173
- [ ] Cámara web conectada y funcionando
- [ ] Permisos de cámara otorgados en el navegador
- [ ] Base de datos de placas generada
- [ ] WebSocket conectado (indicador verde)
- [ ] Buena iluminación en el área de detección

---

**🦅 Sistema Falcon EPSA - Control de Garita con Cámara Integrada**

*Todo en un solo dashboard. Todo en tiempo real.*
