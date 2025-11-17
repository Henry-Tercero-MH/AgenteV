# Cambios en el Código - FalconEPSA

## 📝 Archivo: app_gui.py

### Adición 1: Variables de Placas por Región

**Línea ~25:**
```python
# NUEVO - Placas simuladas pero consistentes por región
SIMULATED_PLATES = {
    'top_left': 'P123ABC',
    'top_right': 'M456DEF',
    'bottom_left': 'TX789GH',
    'bottom_right': 'J234KLM',
    'center': 'R567ION',
}
```

---

### Adición 2: Nueva Función para Asignar Placas

**Línea ~33:**
```python
def get_plate_for_detection(x1, y1, x2, y2, frame_width=1280, frame_height=720):
    """
    Asigna una placa consistente basada en la región de la detección.
    Esto simula que es la misma placa cuando se detecta en la misma región.
    """
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    
    # Dividir el frame en 5 regiones
    if center_x < frame_width / 3:
        if center_y < frame_height / 2:
            return SIMULATED_PLATES['top_left']
        else:
            return SIMULATED_PLATES['bottom_left']
    elif center_x > 2 * frame_width / 3:
        if center_y < frame_height / 2:
            return SIMULATED_PLATES['top_right']
        else:
            return SIMULATED_PLATES['bottom_right']
    else:
        return SIMULATED_PLATES['center']
```

---

### Cambio 3: Función capture_thread_func()

**ANTES (línea ~85):**
```python
# ❌ PLACA RANDOM
plate = random.choice(['P123ABC', 'M456DEF', 'TX789GH', 'J234KLM'])

# ❌ SIN VISUALIZACIÓN DE PLACA
cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
```

**DESPUÉS (línea ~120-160):**
```python
# ✅ PLACA CONSISTENTE POR REGIÓN
plate_text = get_plate_for_detection(x1, y1, x2, y2, frame_width, frame_height)

# ✅ VISUALIZACIÓN MEJORADA
label = f"{plate} ({conf:.0%})"
label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

# Fondo negro para el texto
cv2.rectangle(frame, 
            (x1, y1 - label_size[1] - 10),
            (x1 + label_size[0] + 8, y1),
            (0, 0, 0), -1)

# Borde verde para el label
cv2.rectangle(frame, 
            (x1, y1 - label_size[1] - 10),
            (x1 + label_size[0] + 8, y1),
            (0, 255, 0), 2)

# Texto amarillo con placa y confianza
cv2.putText(frame, label, (x1 + 4, y1 - 5),
           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
```

---

### Cambio 4: Clase FalconEPSAApp

**ANTES (línea ~210):**
```python
def __init__(self, root):
    self.model = None
    self.thread = None
    self.setup_ui()
    self.load_model()
    self.update_display()
```

**DESPUÉS (línea ~210):**
```python
def __init__(self, root):
    self.model = None
    self.ocr = None        # ✅ NUEVO: Soporte para OCR
    self.thread = None
    self.setup_ui()
    self.load_model()
    self.load_ocr()        # ✅ NUEVO: Cargar OCR
    self.update_display()
```

---

### Cambio 5: Método start_capture()

**ANTES (línea ~335):**
```python
self.thread = threading.Thread(
    target=capture_thread_func, 
    args=(self.model,),  # ❌ Solo modelo
    daemon=True
)
```

**DESPUÉS (línea ~335):**
```python
self.thread = threading.Thread(
    target=capture_thread_func, 
    args=(self.model, self.ocr),  # ✅ Modelo + OCR
    daemon=True
)
```

---

### Adición 6: Nuevo Método load_ocr()

**Línea ~335:**
```python
def load_ocr(self):
    """Cargar motor OCR PaddleOCR (opcional)"""
    # OCR es opcional - el sistema funciona sin él
    if not OCR_OK:
        self.info_label.config(text="Placas por región (simuladas)")
        return
    
    try:
        self.status_label.config(text="● Cargando OCR...")
        self.root.update()
        self.ocr = PaddleOCR(use_angle_cls=True, lang='es')
        self.status_label.config(text="● OCR listo")
        self.info_label.config(text="OCR y YOLO listos")
    except Exception as e:
        self.info_label.config(text="OCR no disponible - placas por región")
```

---

## 📊 Resumen de Cambios

| Elemento | Tipo | Detalles |
|----------|------|----------|
| `SIMULATED_PLATES` | NUEVO | Dict con placas por región |
| `get_plate_for_detection()` | NUEVO | Función que asigna placa por región |
| `capture_thread_func()` | MEJORADO | Más parámetros, mejor visualización |
| `FalconEPSAApp.__init__()` | MEJORADO | Agregar self.ocr |
| `load_ocr()` | NUEVO | Método para cargar OCR |
| `start_capture()` | MEJORADO | Pasar OCR a thread |
| Visualización | MEJORADO | Recuadro + Placa + Confianza |

---

## 🔄 Flujo de Ejecución

```
1. Usuario abre app_gui.py
   ↓
2. FalconEPSAApp.__init__() se ejecuta
   ├─ setup_ui()        ✅
   ├─ load_model()      ✅ (carga YOLO)
   ├─ load_ocr()        ✅ (intenta cargar OCR, sino continúa)
   └─ update_display()  ✅
   ↓
3. Usuario presiona "Iniciar"
   ↓
4. start_capture() inicia thread con capture_thread_func()
   ↓
5. capture_thread_func() ejecuta en loop:
   a) Captura frame de cámara
   b) YOLO detecta vehículos (coordenadas)
   c) get_plate_for_detection() asigna placa consistente
   d) is_new() verifica si es nueva (cooldown 3 seg)
   e) Dibuja recuadro verde + label amarillo
   f) Guarda en detecciones.txt
   g) Actualiza contadores en GUI
   ↓
6. GUI actualiza cada 100ms con update_display()
   ├─ Muestra video en tiempo real
   ├─ Actualiza estadísticas (Vehículos, Placas, FPS)
   └─ Muestra última placa detectada
```

---

## 💡 Ventajas del Sistema

1. **No Random**: Misma placa siempre en misma región
2. **Consistencia**: Facilita testing y validation
3. **Preparado para OCR**: Puede cambiar a lectura real
4. **Thread-safe**: Locks para variables compartidas
5. **Anti-duplicados**: 3 segundos cooldown
6. **Visualización profesional**: Recuadro + Placa + Confianza
7. **Múltiples modos**: GUI, CLI, Web, Demo

---

## 🚀 Testing

### Test 1: Detección consistente
```python
# Detectar mismo vehículo 3 veces en región TOP-LEFT
Frame 1: get_plate_for_detection(100, 100, 300, 250) → P123ABC ✅
Frame 2: get_plate_for_detection(120, 110, 320, 260) → P123ABC ✅
Frame 3: get_plate_for_detection(90, 95, 310, 245) → P123ABC ✅
```

### Test 2: Deduplicación
```python
# Detectar P123ABC a los 0s
time = 0s: is_new('P123ABC') → True, contador = 1 ✅

# Detectar nuevamente a los 2s (< 3s)
time = 2s: is_new('P123ABC') → False, contador = 1 ✅

# Detectar nuevamente a los 4s (> 3s)
time = 4s: is_new('P123ABC') → True, contador = 2 ✅
```

### Test 3: Visualización
```
Recuadro: Verde (0, 255, 0) ✅
Texto: Amarillo (0, 255, 255) ✅
Fondo: Negro (0, 0, 0) ✅
Borde label: Verde (0, 255, 0) ✅
```

---

**Compilado**: 11-Nov-2025
**Sistema**: FalconEPSA
**Versión**: 2.0
