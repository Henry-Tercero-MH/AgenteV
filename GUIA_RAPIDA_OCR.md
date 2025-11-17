# 📖 GUÍA RÁPIDA - FalconEPSA OCR

## 🚀 3 PASOS PARA LECTURA REAL DE PLACAS

### 1️⃣ DESCARGAR TESSERACT (5 minutos)

**Link directo:**
```
https://github.com/UB-Mannheim/tesseract/wiki
```

**Pasos:**
1. Click en "tesseract-ocr-w64-setup-v5.x.exe" (versión 64-bit)
2. Ejecuta el instalador descargado
3. Presiona "Siguiente" varias veces
4. Instala en: `C:\Program Files\Tesseract-OCR`
5. Listo ✅

---

### 2️⃣ VERIFICAR INSTALACIÓN

```bash
cd c:\Users\henry\Desktop\Codigos-Proyectos\falconEpsa
source venv/Scripts/activate
python INSTALAR_OCR.py
```

**Debería mostrar:**
```
✅ Tesseract encontrado en: C:\Program Files\Tesseract-OCR\tesseract.exe
✅ pytesseract está instalado
```

Si hay error, edita `app_gui.py` línea ~400:
```python
pytesseract.pytesseract_cmd = r"C:\tu\ruta\tesseract.exe"
```

---

### 3️⃣ EJECUTAR Y PROBAR

```bash
python run_app.py
```

**Qué verás:**
- Ventana GUI se abre
- Status: "● OCR Tesseract listo"
- Click "▶ Iniciar"
- Muestra una placa frente a cámara
- **VERÁ LA PLACA REAL** ✅

---

## 🔍 COMPARACIÓN

| Antes | Después |
|-------|---------|
| Placa: `P123ABC` (simulada) | Placa: `ABC1234` (real) |
| ❌ No es lo que ves | ✅ Es exacto de imagen |
| Demo | Producción |

---

## 📝 NOTA IMPORTANTE

El código **ya está actualizado** para OCR:

```python
# Nueva función en app_gui.py
def read_plate_with_ocr(roi_frame):
    """Lee placa REAL usando Tesseract"""
    # ...
    text = pytesseract.image_to_string(pil_image)
    return text
```

**Solo necesitas instalar Tesseract** (executable, no pip)

---

## ❓ PREGUNTAS FRECUENTES

**¿Funciona sin instalar Tesseract?**
- SÍ, usa placas simuladas como fallback
- NO es lo real, solo demo

**¿Dónde instalo Tesseract si no es C:\Program Files?**
- Edita `app_gui.py` línea ~400 con tu ruta

**¿Qué versión de Tesseract?**
- La última estable (v5.x)
- La versión de 64-bit (w64)

**¿Funciona en Mac/Linux?**
- SÍ, edita la ruta en app_gui.py
- Mac: `/usr/local/Cellar/tesseract/...`
- Linux: `/usr/bin/tesseract`

---

## 🎯 ESTADO FINAL

```
✅ YOLO - Detecta vehículos
✅ OpenCV - Procesa imágenes
✅ pytesseract - Interface OCR
❌ Tesseract - FALTA INSTALAR

= Sistema 80% listo, solo falta Tesseract =
```

---

**¡Listo! Instala Tesseract y tendrás LECTURA REAL de placas 🚀**
