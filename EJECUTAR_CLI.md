# 🚀 Guía de Ejecución en CLI - FalconEPSA

## ✅ Lo que está listo para usar

Tu sistema está completamente implementado y funcionando. Aquí hay dos formas de ejecutarlo:

---

## 📋 Opción 1: Prueba Rápida (SIN CÁMARA)

Simula detecciones en tiempo real sin necesidad de cámara conectada.

### Ejecutar:
```bash
python test_tiempo_real.py
```

### Qué hace:
- ✅ Simula 10 detecciones de vehículos
- ✅ Muestra contadores incrementándose
- ✅ Demuestra deduplicación (misma placa en <3s = ignorada)
- ✅ Guarda placas en `Outputs/detecciones.txt`
- ✅ Muestra resultado final

### Ejemplo de salida:
```
🎯 SIMULADOR DE DETECCIÓN EN TIEMPO REAL - FalconEPSA
📁 Archivo de detecciones: Outputs\detecciones.txt

🚗 Placa detectada: P123ABC
📊 Confianza OCR: 95.60%
✨ NUEVA PLACA DETECTADA
✅ Guardado en TXT: P123ABC

📈 CONTADORES ACTUALIZADOS:
   🚗 Vehículos detectados: 1
   📋 Placas escaneadas: 1

[...]

📊 RESUMEN FINAL DE LA SESIÓN
======================================================================
🚗 Total vehículos detectados: 10
📋 Total placas escaneadas: 10
📁 Archivo guardado en: Outputs\detecciones.txt
======================================================================
```

---

## 📷 Opción 2: Servidor Web Interactivo (CON CÁMARA)

Inicia el dashboard web con detección en tiempo real usando tu cámara.

### Ejecutar básico:
```bash
python run_server.py
```

### Ejecutar con opciones:
```bash
# Con puerto personalizado
python run_server.py --port 8000

# Con más velocidad (saltar más frames)
python run_server.py --skip-frames 3

# Aumentar precisión (más lento)
python run_server.py --infer-max-dim 768

# Combinado
python run_server.py --port 5001 --skip-frames 2 --infer-max-dim 640
```

### Acceder al dashboard:
```
http://127.0.0.1:5001
```

### Qué verás:
- 🎥 Video en vivo de la cámara
- 🟩 Cuadros verdes alrededor de placas detectadas
- 📊 Contadores en tiempo real (vehículos + placas)
- 📝 Placa actual detectada
- 🎛️ Controles para activar/desactivar detección

---

## 🔧 Parámetros de `run_server.py`

| Parámetro | Defecto | Descripción |
|-----------|---------|-------------|
| `--port` | 5001 | Puerto del servidor |
| `--skip-frames` | 2 | Procesar 1 de N frames (más = más rápido) |
| `--infer-max-dim` | 640 | Tamaño máximo para YOLO (más = más preciso) |
| `--host` | 127.0.0.1 | Host del servidor |

### Ejemplos de configuración:

**Para máxima velocidad (menos preciso):**
```bash
python run_server.py --skip-frames 5 --infer-max-dim 480
```

**Para máxima precisión (menos rápido):**
```bash
python run_server.py --skip-frames 1 --infer-max-dim 768
```

**Balance recomendado:**
```bash
python run_server.py --skip-frames 2 --infer-max-dim 640
```

---

## 📊 Pasos Recomendados

### Primero: Probar sin cámara
```bash
# Ver que todo funciona
python test_tiempo_real.py
```

Verás:
- ✅ Contadores funcionando
- ✅ Placas guardadas en TXT
- ✅ Deduplicación trabajando

### Segundo: Ejecutar servidor con cámara
```bash
# Iniciar servidor
python run_server.py

# En otra terminal, monitorear archivo
tail -f Outputs/detecciones.txt
```

Verás:
- 🎥 Video en tiempo real
- 📊 Contadores incrementándose
- 📝 Placas aparecer en el archivo TXT en vivo

---

## 📁 Archivos Generados

### `Outputs/detecciones.txt`
```
2025-11-10 21:41:46.605 | P789BCD | 88.04% | PLACA
2025-11-10 21:41:48.816 | C789GHI | 87.16% | PLACA
2025-11-10 21:41:52.101 | TX345MNO | 95.76% | PLACA
```

**Campos:**
- Timestamp exacto (con milisegundos)
- Placa detectada
- Confianza OCR (%)
- Tipo (PLACA o CAMIÓN)

---

## 🐛 Troubleshooting

### Problema: "bash: python: command not found"
**Solución:**
```bash
# Usar python3
python3 test_tiempo_real.py
```

### Problema: "ModuleNotFoundError: No module named 'flask'"
**Solución:**
```bash
pip install flask
```

### Problema: Cámara no funciona
**Solución:**
1. Verificar que la cámara esté conectada
2. Probar primero sin cámara: `python test_tiempo_real.py`
3. Revisar permisos de cámara del SO

### Problema: Rendimiento muy lento
**Solución:**
```bash
# Aumentar skip-frames
python run_server.py --skip-frames 5
```

---

## 📊 Monitoreo en Tiempo Real

### Terminal 1: Ejecutar servidor
```bash
python run_server.py --port 5001
```

### Terminal 2: Monitorear archivo (Linux/Mac)
```bash
tail -f Outputs/detecciones.txt
```

### Terminal 2: Monitorear archivo (Windows PowerShell)
```powershell
Get-Content Outputs/detecciones.txt -Wait
```

---

## 🎯 Flujo de Trabajo Completo

```
1. EJECUTAR SIMULACIÓN
   $ python test_tiempo_real.py
   ✅ Verifica que todo funciona
   ✅ Crea Outputs/detecciones.txt

2. INICIAR SERVIDOR WEB
   $ python run_server.py
   ✅ Abre: http://127.0.0.1:5001

3. ACTIVAR DETECCIÓN
   En el navegador → Toggle ON
   ✅ Cámara inicia

4. MONITOREAR RESULTADOS
   $ tail -f Outputs/detecciones.txt
   ✅ Ve placas en tiempo real

5. VER CONTADORES
   Dashboard actualiza cada 1 segundo
   ✅ 🚗 Vehículos: X
   ✅ 📋 Placas: X
```

---

## 🚀 Próximos Pasos

### Con Ryzen 7000
El código se adaptará automáticamente:
- Detectará 12-16 cores
- YOLO usará 9-12 workers
- Esperado: 3-4x más rápido

### Mejoras adicionales
- Entrenar modelo fusionado (30% más rápido)
- Usar DirectML si tienes GPU AMD
- Implementar caché OCR (no reprocesar mismas placas)

---

## ✅ Resumen

| Tarea | Comando | Uso |
|-------|---------|-----|
| **Prueba rápida** | `python test_tiempo_real.py` | Simular sin cámara |
| **Servidor web** | `python run_server.py` | Detección con cámara |
| **Ver archivo** | `cat Outputs/detecciones.txt` | Historial de placas |
| **Monitorear** | `tail -f Outputs/detecciones.txt` | Tiempo real |

---

## 🎉 ¡Listo!

Tu sistema está completamente funcional y listo para usar.

**Comienza con:**
```bash
python test_tiempo_real.py
```

Verás cómo funciona todo sin necesidad de cámara. Luego:
```bash
python run_server.py
```

¡Y disfruta de tu sistema de detección en tiempo real! 🚀
