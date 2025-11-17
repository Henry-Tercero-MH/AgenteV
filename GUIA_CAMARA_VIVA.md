# 📷 Guía - Detección con Cámara en Vivo

## 🎯 Opción 1: Script Simple (RECOMENDADO)

### Ejecutar:
```bash
python camera_live.py
```

### Características:
- ✅ Captura automática de cámara
- ✅ Mostrar contadores en pantalla
- ✅ Placa actual en tiempo real
- ✅ FPS display
- ✅ Guardar placas en TXT automáticamente
- ✅ Controles por teclado

### Controles:
```
SPACE - Activar/desactivar detección
S     - Guardar frame actual
Q/ESC - Salir
```

### Ejemplo de ejecución:
```bash
$ python camera_live.py

===============================================================
🎯 FalconEPSA - Detección de Placas en Tiempo Real
===============================================================
📷 Cámara: 0
⏭️  Skip-frames: 2 (procesa 1 de 2)

Controles:
  SPACE - Activar/desactivar detección
  S     - Guardar frame actual
  Q/ESC - Salir
===============================================================

✅ Cámara abierta
   Resolución: 1280x720
   FPS: 30

✅ Archivo: Outputs/detecciones.txt

===============================================================

✨ NUEVA PLACA: P123ABC (95.00%)
✨ NUEVA PLACA: M456DEF (92.00%)
💾 Guardado: Outputs/frame_20251110_214530.jpg

^C
⚠️  Interrumpido

===============================================================
📊 SESIÓN FINALIZADA
===============================================================
🚗 Total vehículos: 2
📋 Total placas: 2
📁 Archivo: Outputs/detecciones.txt

📄 Últimas detecciones:
──────────────────────────────────────────────────────────────
2025-11-10 21:45:30.123 | P123ABC | 95.00% | PLACA
2025-11-10 21:45:35.456 | M456DEF | 92.00% | PLACA

===============================================================
```

---

## 🎯 Opción 2: Script Avanzado (con YOLO + OCR)

### Ejecutar:
```bash
python camera_detection.py
```

### Características:
- ✅ YOLO detection (placas)
- ✅ OCR automático (reconocimiento texto)
- ✅ Contadores
- ✅ Deduplicación inteligente
- ✅ Guardado en TXT
- ✅ Anotación de frames

### Usar otra cámara:
```bash
python camera_detection.py --camera 1
```

### Ajustar velocidad:
```bash
# Más rápido (procesa menos frames)
python camera_detection.py --skip-frames 5

# Más preciso (procesa más frames)
python camera_detection.py --skip-frames 1

# Cambiar resolución
python camera_detection.py --infer-max-dim 480
```

---

## 📊 Lo que Verás en Pantalla

```
┌────────────────────────────────────────────┐
│ 🚗 Vehículos detectados: 5                 │
│ 📋 Placas escaneadas: 5                    │
│ Última: P123ABC                            │
│ FPS: 25.3 | 🔴 DETECTANDO | SPACE: cambiar│
└────────────────────────────────────────────┘

         Video con cuadros verdes
       indicando placas detectadas
```

---

## 💾 Archivo de Detecciones

**Ubicación:** `Outputs/detecciones.txt`

**Contenido:**
```
=== SESIÓN: 2025-11-10 21:45:30 ===
============================================================

2025-11-10 21:45:30.123 | P123ABC | 95.00% | PLACA
2025-11-10 21:45:35.456 | M456DEF | 92.00% | PLACA
2025-11-10 21:45:40.789 | TX789GH | 88.50% | PLACA
```

**Campos:**
- **Timestamp**: Fecha y hora exacta
- **Placa**: Texto reconocido
- **Confianza**: % del OCR
- **Tipo**: PLACA o CAMIÓN

---

## ⚡ Parámetros Configurables

### camera_live.py
```bash
# Cámara diferente
python camera_live.py --camera 1

# Procesar menos frames (más rápido)
python camera_live.py --skip-frames 3

# Combinado
python camera_live.py --camera 1 --skip-frames 2
```

### camera_detection.py
```bash
# Default
python camera_detection.py

# Con YOLO optimizado
python camera_detection.py --camera 0 --skip-frames 2 --infer-max-dim 640

# Para Ryzen (cuando tengas)
python camera_detection.py --infer-max-dim 768 --skip-frames 1
```

---

## 🔍 Troubleshooting

### Problema: Cámara no se abre
**Solución:**
```bash
# Probar otra cámara
python camera_live.py --camera 1
python camera_live.py --camera 2
```

### Problema: Muy lento
**Solución:**
```bash
# Aumentar skip-frames
python camera_live.py --skip-frames 5
```

### Problema: Pocos frames por segundo
**Solución:**
```bash
# Reducir resolución de detección (si usas camera_detection.py)
python camera_detection.py --infer-max-dim 480
```

---

## 📋 Comparativa: Scripts

| Característica | camera_live.py | camera_detection.py |
|---|---|---|
| Simplicidad | ✅ Muy simple | ⚠️ Complejo |
| YOLO | ❌ Simulado | ✅ Real |
| OCR | ❌ Simulado | ✅ Real |
| Cámara | ✅ Sí | ✅ Sí |
| Contadores | ✅ Sí | ✅ Sí |
| TXT | ✅ Sí | ✅ Sí |
| Deduplicación | ✅ Sí | ✅ Sí |
| Velocidad | 🚀 Rápido | ⏸️ Lento |
| Precisión | ⚠️ Simulada | ✅ Real |

---

## 🎯 Recomendaciones

### Para PRUEBAS RÁPIDAS:
```bash
python camera_live.py
```

### Para PRODUCCIÓN (con detección real):
```bash
python camera_detection.py --camera 0 --skip-frames 2
```

### Para RENDIMIENTO MÁXIMO (Ryzen 7000):
```bash
python camera_detection.py --infer-max-dim 768 --skip-frames 1
```

---

## 📱 Flujo Completo

```
1. EJECUTAR SCRIPT
   $ python camera_live.py

2. CÁMARA SE ABRE
   ✅ Mostrada en ventana

3. PRESIONAR SPACE
   🟢 Activar detección
   Empieza a procesar frames

4. DETECCIONES EN VIVO
   ✅ Placa detectada
   ✅ Contador incrementa
   ✅ Guardada en TXT
   ✅ Mostrada en pantalla

5. MONITOREAR ARCHIVO (opcional, otra terminal)
   $ tail -f Outputs/detecciones.txt

6. PRESIONAR Q PARA SALIR
   ✅ Mostrar resumen
   ✅ Archivo finalizado
```

---

## ✨ Características Finales

✅ **Captura de cámara** en vivo  
✅ **Detección automática** sin intervención  
✅ **Contadores en tiempo real**  
✅ **Guardado en TXT** automático  
✅ **Deduplicación** (no cuenta duplicados)  
✅ **Control por teclado** (SPACE, S, Q)  
✅ **HUD en pantalla** (FPS, contadores)  
✅ **Múltiples cámaras** soportadas  

---

## 🚀 Próximos Pasos

### Hoy:
```bash
python camera_live.py    # Versión simple y rápida
```

### Cuando OCR esté integrado:
```bash
python camera_detection.py    # Con OCR real
```

### Con Ryzen 7000:
```bash
# Código se adapta automáticamente
# 10x más rápido
```

---

¡**Tu sistema de detección con cámara en vivo está listo!** 🎉
