#!/bin/bash
# Script para ejecutar FalconEPSA de forma simple

echo "============================================================"
echo "FalconEPSA - Sistema de Detección de Placas en Vivo"
echo "============================================================"
echo ""
echo "Activando ambiente virtual..."

cd "$(dirname "$0")" || exit 1

# Activar venv
source venv/Scripts/activate 2>/dev/null || . venv/Scripts/activate

echo ""
echo "Opciones disponibles:"
echo ""
echo "1) Modo CLI (Recomendado - sin GUI)"
echo "   $ python camera_live_cli.py"
echo ""
echo "2) Modo Web Dashboard"
echo "   $ python web_dashboard.py --model best.pt --port 5001"
echo ""
echo "3) Prueba Rápida (10 segundos)"
echo "   $ python test_tiempo_real.py"
echo ""
echo "============================================================"
echo "Selecciona opción (presiona Ctrl+C para salir):"
echo ""

# Ejecutar por defecto el modo CLI
echo "[INICIANDO] Modo CLI..."
python camera_live_cli.py
