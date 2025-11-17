# Inicio Rápido - Dashboard Falcon EPSA

## Opción 1: Inicio Automático (Recomendado)

### Windows
```bash
start_dashboard.bat
```

### Linux/Mac
```bash
chmod +x start_dashboard.sh
./start_dashboard.sh
```

Esto ejecutará automáticamente:
1. Procesamiento de todas las imágenes
2. Inicio de la API en http://localhost:8000
3. Inicio del Dashboard en http://localhost:5173

---

## Opción 2: Inicio Manual (Paso a Paso)

### Paso 1: Procesar Imágenes

```bash
python process_batch.py
```

Esto generará `Outputs/resultados_dashboard.json` con todos los datos.

### Paso 2: Iniciar API Backend

En una terminal:

```bash
python api_dashboard.py
```

La API correrá en http://localhost:8000

### Paso 3: Iniciar Dashboard React

En otra terminal:

```bash
cd dashboard-falcon
npm run dev
```

El dashboard correrá en http://localhost:5173

---

## URLs Importantes

- **Dashboard**: http://localhost:5173
- **API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Redoc API**: http://localhost:8000/redoc

---

## Procesar una Sola Imagen (CLI)

```bash
python app.py --source Inputs/test.jpg --model best.pt --truck-model best_truck.pt --output Outputs --conf 0.3
```

---

## Solución de Problemas

### Error: "No se encontraron resultados"
**Solución**: Ejecuta `python process_batch.py` primero.

### Error: "Error al conectar con el servidor"
**Solución**: Asegúrate que la API esté corriendo en puerto 8000.

### Puerto en uso
**Solución**: Cambia el puerto en `api_dashboard.py` (línea final) y en `dashboard-falcon/src/App.jsx` (línea 9).

---

## Características del Dashboard

✅ Estadísticas en tiempo real
✅ Gráficos de tiempos de procesamiento
✅ Tabla interactiva de resultados
✅ Visualización de imágenes anotadas
✅ Detalles de cada placa detectada
✅ Diseño responsive (móvil, tablet, escritorio)

---

## Arquitectura del Sistema

```
Frontend (React + TailwindCSS)
         ↓ HTTP Requests
API REST (FastAPI)
         ↓ Lee datos de
JSON (resultados_dashboard.json)
         ↑ Generado por
Procesamiento Batch (YOLO + OCR)
```

---

## Próximos Pasos

1. ✅ Ejecuta el sistema
2. 🌐 Abre http://localhost:5173
3. 📊 Explora las estadísticas
4. 🖼️ Visualiza las detecciones
5. 🔍 Revisa los detalles de cada placa

---

**Desarrollado por Falcon EPSA - 2025**
