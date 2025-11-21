#!/bin/bash
echo "========================================"
echo "   FalconEPSA - GUI con OCR Integrado"
echo "========================================"
echo ""
echo "Iniciando aplicacion de escritorio..."
echo "Canal RTSP: 102 (OCR Optimizado)"
echo ""

# Ir al directorio del script
cd "$(dirname "$0")"

# Ejecutar la aplicación GUI
python3 app_gui.py