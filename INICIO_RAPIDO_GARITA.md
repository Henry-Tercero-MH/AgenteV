# 🚀 Inicio Rápido - Sistema de Control de Garita

## ⚡ Método Rápido (Recomendado)

### Windows
```bash
start_sistema_garita.bat
```

### Linux/Mac
```bash
./start_sistema_garita.sh
```

Esto iniciará:
1. ✅ API Backend en http://localhost:8001
2. ✅ Dashboard React en http://localhost:5173
3. ✅ WebSocket en ws://localhost:8001/ws

---

## 📝 Método Manual

### 1. Instalar dependencias (solo primera vez)

**Backend:**
```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

**Frontend:**
```bash
cd dashboard-falcon
npm install
```

### 2. Iniciar el sistema

**Terminal 1 - API Backend:**
```bash
python api_dashboard.py
```

**Terminal 2 - Dashboard React:**
```bash
cd dashboard-falcon
npm run dev
```

---

## 🧪 Probar el Sistema

### Opción 1: Script de prueba interactivo
```bash
python test_garita.py
```

Menú interactivo con opciones:
- Simular detección de placa registrada
- Simular detección de placa NO registrada
- Simular múltiples detecciones automáticas
- Ver historial

### Opción 2: Prueba manual con curl

**Registrar una placa:**
```bash
curl -X POST "http://localhost:8001/api/registros/entrada" \
  -H "Content-Type: application/json" \
  -d '{"placa": "PO28GHQ", "confianza": 0.95}'
```

**Ver historial:**
```bash
curl "http://localhost:8001/api/registros/historial?limit=10"
```

**Validar placa:**
```bash
curl "http://localhost:8001/api/placas/validar/PO28GHQ"
```

### Opción 3: Usar la interfaz web (Swagger)
Abrir: http://localhost:8001/docs

---

## 🎯 Flujo de Prueba Completo

1. **Iniciar el sistema** (API + Dashboard)

2. **Abrir el dashboard** en el navegador:
   - http://localhost:5173

3. **Ejecutar el script de prueba:**
   ```bash
   python test_garita.py
   ```

4. **Seleccionar opción 3** (múltiples detecciones automáticas)
   - Cantidad: 5
   - Intervalo: 3 segundos

5. **Observar el dashboard:**
   - ✅ WebSocket se conecta (indicador verde)
   - ✅ Aparecen placas detectadas en tiempo real
   - ✅ Se muestran datos del vehículo (si está registrado)
   - ✅ Se actualiza el historial automáticamente

---

## 📊 Estructura Visual del Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  🦅 Falcon EPSA - Control de Garita      🟢 Conectado  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │ PLACA DETECTADA  │    │ DATOS DEL VEHÍCULO       │  │
│  │                  │    │                          │  │
│  │  ✓ REGISTRADA    │    │ Propietario: Juan Pérez  │  │
│  │                  │    │ Tipo: PARTICULAR         │  │
│  │  ┌──────────┐    │    │ Estado: AUTORIZADO       │  │
│  │  │ PO28GHQ  │    │    │ Departamento: Guatemala  │  │
│  │  └──────────┘    │    │                          │  │
│  │                  │    │ Historial:               │  │
│  │  [Imagen placa]  │    │  • Entrada: 10:30 AM     │  │
│  │                  │    │  • Entrada: 08:15 AM     │  │
│  │  Confianza: 95%  │    │  • Salida:  05:30 PM     │  │
│  │                  │    │                          │  │
│  │  📅 16/11/2025   │    │                          │  │
│  │  🕐 10:30:00     │    │                          │  │
│  │  ➡️  ENTRADA      │    │                          │  │
│  └──────────────────┘    └──────────────────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  📋 HISTORIAL COMPLETO DE REGISTROS                    │
├─────────────────────────────────────────────────────────┤
│  #  │ Placa    │ Evento  │ Fecha/Hora      │ Estado  │
│  1  │ PO28GHQ  │ ENTRADA │ 16/11/25 10:30  │ ✓ Reg.  │
│  2  │ GC987D   │ ENTRADA │ 16/11/25 10:27  │ ✓ Reg.  │
│  3  │ ABC123   │ ENTRADA │ 16/11/25 10:24  │ ✗ No    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Placas de Prueba

### Placas Registradas (aparecerán con datos)
- `PO28GHQ` - Estado: NORMAL
- `GC987D` - Estado: RESTRINGIDO
- `NCV896` - Estado: SUSPENDIDO

### Placas NO Registradas (aparecerán con alerta)
- `ABC123`
- `XYZ789`

---

## ⚠️ Troubleshooting

### El API no inicia
```bash
# Verificar que el puerto 8001 esté libre
netstat -ano | findstr :8001  # Windows
lsof -i :8001  # Linux/Mac

# Instalar dependencias faltantes
pip install fastapi uvicorn websockets pydantic
```

### El Dashboard no conecta
```bash
# Verificar que el API esté corriendo
curl http://localhost:8001/health

# Verificar configuración en dashboard-falcon/src/App.jsx
# Debe ser: const API_URL = 'http://localhost:8001';
```

### WebSocket no conecta
- Abre la consola del navegador (F12)
- Busca errores de WebSocket
- Verifica que uses `ws://` y no `wss://`

---

## 🎨 Personalizar

### Cambiar puerto del API
En `api_dashboard.py`:
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Cambiar aquí
```

Y en `dashboard-falcon/src/App.jsx`:
```javascript
const API_URL = 'http://localhost:8001';  // Cambiar aquí
```

### Agregar más placas a la DB
```bash
# Editar database/placas_db.json
# O regenerar:
python generar_db_placas.py
```

---

## 📚 Documentación Completa

Para más información, consulta:
- **README completo:** `SISTEMA_GARITA_README.md`
- **API Docs:** http://localhost:8001/docs
- **Código fuente:** Revisa los comentarios en cada archivo

---

## ✅ Checklist de Inicio

- [ ] Entorno virtual activado
- [ ] Dependencias instaladas (pip install -r requirements.txt)
- [ ] Dashboard instalado (npm install en dashboard-falcon)
- [ ] API corriendo en puerto 8001
- [ ] Dashboard corriendo en puerto 5173
- [ ] WebSocket conectado (indicador verde en dashboard)
- [ ] Prueba realizada con test_garita.py

---

**¡Listo! El sistema está funcionando correctamente. 🎉**
