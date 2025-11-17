#!/bin/bash

echo "============================================"
echo "  Falcon EPSA - Dashboard de Placas"
echo "============================================"
echo ""

echo "[1/3] Procesando imágenes..."
python process_batch.py

echo ""
echo "[2/3] Iniciando API Backend..."
python api_dashboard.py &
API_PID=$!
sleep 3

echo ""
echo "[3/3] Iniciando Dashboard React..."
cd dashboard-falcon
npm run dev &
DASHBOARD_PID=$!

echo ""
echo "============================================"
echo "  Dashboard iniciado correctamente!"
echo "============================================"
echo ""
echo "  API:       http://localhost:8000"
echo "  Docs:      http://localhost:8000/docs"
echo "  Dashboard: http://localhost:5173"
echo ""
echo "============================================"
echo ""
echo "Presiona Ctrl+C para detener todos los servicios"

# Manejar Ctrl+C
trap "kill $API_PID $DASHBOARD_PID; exit" INT

wait
