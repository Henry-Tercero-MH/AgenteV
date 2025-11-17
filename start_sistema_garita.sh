#!/bin/bash

echo "============================================"
echo "  FALCON EPSA - Sistema de Control de Garita"
echo "============================================"
echo ""

# Detectar directorio del script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "[1/3] Iniciando API Backend..."
cd "$SCRIPT_DIR"
source .venv/bin/activate
gnome-terminal -- bash -c "cd '$SCRIPT_DIR' && source .venv/bin/activate && python api_dashboard.py; exec bash" 2>/dev/null || \
xterm -e "cd '$SCRIPT_DIR' && source .venv/bin/activate && python api_dashboard.py; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$SCRIPT_DIR"' && source .venv/bin/activate && python api_dashboard.py"' 2>/dev/null &

sleep 3

echo "[2/3] Iniciando Dashboard React..."
cd "$SCRIPT_DIR/dashboard-falcon"
gnome-terminal -- bash -c "cd '$SCRIPT_DIR/dashboard-falcon' && npm run dev; exec bash" 2>/dev/null || \
xterm -e "cd '$SCRIPT_DIR/dashboard-falcon' && npm run dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '"$SCRIPT_DIR/dashboard-falcon"' && npm run dev"' 2>/dev/null &

sleep 3

echo ""
echo "============================================"
echo "  Sistema iniciado exitosamente!"
echo "============================================"
echo ""
echo "  API Backend:  http://localhost:8001"
echo "  Dashboard:    http://localhost:5173"
echo "  WebSocket:    ws://localhost:8001/ws"
echo ""
echo "  Documentacion API: http://localhost:8001/docs"
echo ""
echo "============================================"
echo "  Para probar detecciones:"
echo "  python test_garita.py"
echo "============================================"
echo ""
