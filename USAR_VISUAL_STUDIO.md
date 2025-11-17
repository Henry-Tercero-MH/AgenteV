# 🐍 Usar Python en Visual Studio (Morado)

## ✅ Sí, es posible

Visual Studio 2022 (de color morado) tiene soporte nativo para Python.

---

## 📥 Instalación

### Paso 1: Descargar Visual Studio 2022
**Link:** https://visualstudio.microsoft.com/downloads/

### Paso 2: Ejecutar el instalador
1. Abre `Visual Studio Installer`
2. Haz clic en **Modificar** si ya está instalado
3. O en **Instalar** si es nuevo

### Paso 3: Seleccionar Python
En la ventana de selección de cargas de trabajo:
- ✅ Busca: **"Python"**
- ✅ Marca: **"Python development"**
- ✅ Marca: **"Python web development"** (opcional)

### Paso 4: Instalar
- Haz clic en **Instalar**
- Espera a que se complete (~10-20 minutos)

---

## 🚀 Crear Proyecto Python en VS 2022

### Método 1: Nuevo Proyecto desde Cero

1. Abre Visual Studio 2022
2. **File** → **New** → **Project**
3. Busca: **"Python"**
4. Selecciona: **"Python Application"** o **"Flask Web Project"**
5. Configura:
   - **Project name:** `falconEpsa`
   - **Location:** `C:\Users\henry\Desktop\Codigos-Proyectos\`
   - Haz clic en **Create**

### Método 2: Abrir Proyecto Existente

1. **File** → **Open** → **Folder**
2. Selecciona: `C:\Users\henry\Desktop\Codigos-Proyectos\falconEpsa`
3. VS creará automáticamente un proyecto Python

---

## 🐍 Configurar Entorno Virtual en VS

### Paso 1: Abrir Terminal
**View** → **Terminal** (o presiona `Ctrl + ~`)

### Paso 2: Crear Entorno Virtual
```bash
python -m venv .venv
```

### Paso 3: Activar Entorno
```bash
.venv\Scripts\activate
```

### Paso 4: Instalar Dependencias
```bash
pip install opencv-python ultralytics pytesseract pillow
```

### Paso 5: VS Detectará Automáticamente el Entorno
Visual Studio mostrará una notificación:
> **"A Python environment has been detected"**

Haz clic en **"Use this environment"**

---

## 📂 Estructura de Proyecto en VS

```
falconEpsa/
├── .venv/                    # Entorno virtual
├── app_gui.py               # Código principal
├── run_app.py              # Launcher
├── config.py               # Configuración
├── best.pt                 # Modelo YOLO
├── Outputs/
│   └── detecciones.txt    # Detecciones
├── requirements.txt        # Dependencias
└── .gitignore             # Git ignore
```

---

## 🎮 Características de VS para Python

### ✅ IntelliSense (Autocompletado)
- Escribe `cv2.` y VS sugiere automáticamente
- Presiona `Ctrl + Space` para completar

### ✅ Depuración (Debug)
```python
# Haz clic a la izquierda de la línea para poner breakpoint
cap = cv2.VideoCapture(RTSP_URL)  # ← Clic aquí para detener
```

Luego presiona **F5** para depurar

### ✅ Integración Git
- **Source Control** (Ctrl + Shift + G)
- Commit, Push, Pull directamente

### ✅ Integrated Terminal
- **Terminal** (Ctrl + ~)
- Ejecuta comandos sin salir de VS

### ✅ Extensiones Python
- **Python Extension Pack** (por Microsoft)
- **Pylance** (IntelliSense avanzado)

---

## ▶️ Ejecutar Código en VS

### Método 1: F5 (Depuración)
Presiona **F5** para ejecutar con debugger

### Método 2: Ctrl + F5 (Sin Debugger)
Ejecuta más rápido sin parar en breakpoints

### Método 3: Terminal
```bash
python run_app.py
```

### Método 4: Clic Derecho
- Haz clic derecho en `run_app.py`
- Selecciona: **"Run Python File in Terminal"**

---

## 🔧 Configuración Recomendada

### Crear `requirements.txt`
En la terminal:
```bash
pip freeze > requirements.txt
```

Contenido:
```
opencv-python==4.8.1.78
ultralytics==8.0.201
pillow==10.0.1
pytesseract==0.3.13
```

### Crear `.gitignore`
```
.venv/
__pycache__/
*.pyc
.env
Outputs/
.DS_Store
```

### Crear `launch.json` (Debug Config)
**Debug** → **Add Configuration** → **Python**

---

## 🎨 Temas y Personalización

### Cambiar Tema a "Morado"
1. **Tools** → **Options**
2. **Environment** → **General**
3. **Color theme:** 
   - **Dark (Default)** - Gris oscuro
   - **Blue** - Azul
   - **Light** - Claro

Para un tema más morado:
- Ve a **Extensions** → **Manage Extensions**
- Busca: **"Dracula"** o **"Purple"**
- Instala y aplica

---

## 🚀 Ejecutar FalconEPSA en VS

### Paso 1: Abrir el Proyecto
```bash
cd C:\Users\henry\Desktop\Codigos-Proyectos\falconEpsa
```

### Paso 2: Abrir en VS
**File** → **Open Folder** → Selecciona `falconEpsa`

### Paso 3: Abrir Terminal
**View** → **Terminal** (Ctrl + ~)

### Paso 4: Activar Entorno
```bash
.venv\Scripts\activate
```

### Paso 5: Ejecutar
```bash
python run_app.py
```

O simplemente presiona **F5**

---

## 🐛 Depuración en VS

### Poner Breakpoint
1. Haz clic en el margen izquierdo de una línea
2. Aparecerá un punto rojo

### Ejecutar hasta Breakpoint
- Presiona **F5** (Debug)
- El código se detiene en el breakpoint

### Ver Variables
En la ventana **Locals** aparecen:
- `frame` → imagen actual
- `plate` → placa detectada
- `conf` → confianza

### Pasos de Depuración
- **F10** → Siguiente línea
- **F11** → Entrar en función
- **Shift+F11** → Salir de función
- **F5** → Continuar ejecución

---

## 📊 Ventajas de Usar VS para Python

| Característica | VS Code | Visual Studio |
|---|---|---|
| **IntelliSense** | Bueno | Excelente |
| **Depuración** | Buena | Excelente |
| **Tamaño** | 50 MB | 1 GB+ |
| **Velocidad** | Rápido | Un poco lento |
| **UI** | Moderna | Clásica pero potente |
| **Integración Git** | Buena | Excelente |
| **Debugger** | PyDebug | PTVSD |

---

## ⚙️ Configuración Recomendada para FalconEPSA

### settings.json (VS Code JSON)
Si usas VS 2022 con extensiones:
```json
{
    "python.defaultInterpreterPath": ".venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

### launch.json (Configuración de Debug)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FalconEPSA",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run_app.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

---

## 💡 Tips Útiles

### 1. Ejecutar Solo una Función
```python
# Presiona Ctrl+Shift+P
# Escribe: "Run Selection"
# VS ejecutará solo lo seleccionado
```

### 2. Ver Documentación
```python
cv2.VideoCapture()
# Coloca el cursor aquí y presiona Ctrl+Q
# Aparecerá la documentación
```

### 3. Refactorización
```python
# Clic derecho en variable
# "Rename Symbol" → Cambia en todo el proyecto
```

### 4. Autoformatear
```python
# Selecciona código
# Presiona Ctrl+K, Ctrl+F
# VS formatea automáticamente
```

---

## 🎯 Próximos Pasos

1. **Descargar VS 2022:** https://visualstudio.microsoft.com/
2. **Instalar extensión Python**
3. **Abrir tu proyecto** `falconEpsa`
4. **Configurar entorno virtual** `.venv`
5. **Ejecutar:** `python run_app.py` o presiona **F5**

---

## 📚 Recursos

- **Visual Studio Docs:** https://docs.microsoft.com/en-us/visualstudio/
- **Python in VS:** https://docs.microsoft.com/en-us/visualstudio/python/
- **Getting Started:** https://code.visualstudio.com/docs/python/python-tutorial

---

**¿Necesitas ayuda instalando Visual Studio o configurando el proyecto?**
