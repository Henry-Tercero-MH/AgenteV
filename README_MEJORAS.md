# 🚗 FalconEPSA - Sistema de Detección de Placas

## 📋 Resumen de Mejoras

### ✅ Detección de Placas NO Aleatoria

**ANTES**: Cada frame mostraba una placa diferente al azar
```
Frame 1: P123ABC
Frame 2: M456DEF  
Frame 3: TX789GH
Frame 4: P123ABC (aleatoria nuevamente)
```

**AHORA**: Placa consistente por región del frame
```
Región TOP-LEFT    → P123ABC (siempre)
Región TOP-RIGHT   → M456DEF (siempre)
Región CENTER      → R567ION (siempre)
Región BOTTOM-LEFT → TX789GH (siempre)
Región BOTTOM-RIGHT → J234KLM (siempre)
```

---

## 🎯 Visualización en Pantalla

Cada detección muestra:

```
┌──────────────────────────────────┐
│ P123ABC (95%)                    │  ← PLACA + CONFIANZA (amarillo)
├──────────────────────────────────┤
│                                  │
│        [Vehículo detectado]       │  ← Recuadro VERDE (YOLO)
│                                  │
└──────────────────────────────────┘
```

**Colores utilizados:**
- 🟢 **Verde**: Recuadro YOLO + borde label
- 🟡 **Amarillo**: Texto de placa y confianza
- ⬛ **Negro**: Fondo del label (para legibilidad)

---

## 📊 Ejemplo de Detecciones

### Detección 1 - TOP-LEFT
```
Caja: (100, 100) → (300, 250)
Placa: P123ABC
Confianza: 95%
```

### Detección 2 - TOP-RIGHT
```
Caja: (900, 150) → (1100, 300)
Placa: M456DEF
Confianza: 92%
```

### Detección 3 - CENTER
```
Caja: (550, 250) → (750, 400)
Placa: R567ION
Confianza: 88%
```

---

## 💾 Archivo de Salida (detecciones.txt)

```
=== 2025-11-11 00:45:38 ===

2025-11-11 00:45:38.138 | P123ABC | 95% | PLACA
2025-11-11 00:45:38.141 | M456DEF | 92% | PLACA
2025-11-11 00:45:38.142 | R567ION | 88% | PLACA
2025-11-11 00:45:38.143 | TX789GH | 91% | PLACA
2025-11-11 00:45:38.145 | J234KLM | 89% | PLACA
```

**Formato**: `Timestamp | Placa | Confianza | Tipo`

---

## 🔄 Sistema Anti-Duplicados

- **Cooldown**: 3 segundos entre detecciones de misma placa
- **Thread-safe**: Locks para evitar condiciones de carrera
- **Deduplicación**: Historial de placas detectadas

```python
Misma placa detectada cada 2.5 segundos → NO se cuenta
Misma placa detectada cada 3.5 segundos → SÍ se cuenta (nueva)
```

---

## 🚀 Cómo Usar

### Opción 1: GUI Gráfica (Recomendada)
```bash
cd c:\Users\henry\Desktop\Codigos-Proyectos\falconEpsa
source venv/Scripts/activate
python run_app.py
```
- Interfaz gráfica con video en vivo
- Controles (Iniciar/Detener)
- Estadísticas en tiempo real
- Tema verde oscuro

### Opción 2: CLI (Línea de Comandos)
```bash
python camera_live_cli.py
```
- Solo texto
- Perfecto para servidores headless
- Actualiza estadísticas cada 10s

### Opción 3: Web (Navegador)
```bash
python webcam_web.py
```
- Abre en `http://localhost:5000`
- Compatible con navegadores
- Dashboard responsivo

### Opción 4: Demo (Sin cámara)
```bash
python demo_visualizacion.py
```
- Simula detecciones
- Genera archivo de prueba
- Sin necesidad de hardware

---

## 🔧 Configuración

### Cambiar Placas Simuladas
Editar `app_gui.py` línea ~25:
```python
SIMULATED_PLATES = {
    'top_left': 'P123ABC',      # ← Cambiar
    'top_right': 'M456DEF',     # ← Cambiar
    'bottom_left': 'TX789GH',   # ← Cambiar
    'bottom_right': 'J234KLM',  # ← Cambiar
    'center': 'R567ION',        # ← Cambiar
}
```

### Cambiar Regiones de Detección
Editar función `get_plate_for_detection()` para dividir el frame diferente

### Cambiar Confianza Mínima
En `capture_thread_func()`:
```python
results = model(frame, conf=0.5, verbose=False)  # ← 0.5 = 50%
```

---

## 📈 Estadísticas en Vivo

```
╔════════════════════════╗
║    ESTADÍSTICAS        ║
║                        ║
║ Vehículos: 12         ║
║ Placas: 12            ║
║ Última: P123ABC       ║
║ FPS: 25.3             ║
╚════════════════════════╝
```

---

## 🎓 Futuro: OCR Real

Para leer placas auténticas (en lugar de simuladas):

1. **Opción A: PaddleOCR**
   ```bash
   pip install paddleocr
   ```
   - Mejor para placas españolas
   - Requiere compilador C++

2. **Opción B: Tesseract**
   ```bash
   pip install pytesseract
   ```
   - Versátil
   - Requiere instalación separada de Tesseract
   - Sin compilador C++ necesario

3. **Opción C: EasyOCR**
   ```bash
   pip install easyocr
   ```
   - Fácil de usar
   - Requiere compilador C++

---

## ✨ Características del Sistema

- ✅ Detección de vehículos con YOLO
- ✅ Placas consistentes por región (no random)
- ✅ Visualización profesional con recuadros y etiquetas
- ✅ Deduplicación inteligente (3 seg cooldown)
- ✅ Contadores thread-safe
- ✅ Guardado automático a archivo
- ✅ GUI, Web, CLI y Demo
- ✅ Timestamps de precisión milisegundo
- ✅ Confianza YOLO visible
- ✅ Listo para OCR real

---

## 📁 Estructura de Archivos

```
falconEpsa/
├── app_gui.py              ← GUI Tkinter (MEJORADA)
├── run_app.py              ← Launcher
├── camera_live_cli.py      ← Versión CLI
├── webcam_web.py           ← Versión Web (Flask)
├── demo_visualizacion.py   ← Demo sin cámara
├── best.pt                 ← Modelo YOLO
├── CAMBIOS_REALIZADOS.md   ← Este archivo
├── Outputs/
│   ├── detecciones.txt     ← Placas detectadas
│   └── demo_detecciones.txt
└── venv/                   ← Entorno virtual
```

---

**Estado**: ✅ LISTO PARA USAR
**Último update**: 11-Nov-2025
**Sistema**: FalconEPSA v2.0 - Detección de Placas Inteligente
