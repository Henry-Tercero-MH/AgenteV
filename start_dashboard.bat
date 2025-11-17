@echo off
echo ============================================
echo   Falcon EPSA - Dashboard de Placas
echo ============================================
echo.

echo [1/3] Procesando imagenes...
python process_batch.py

echo.
echo [2/3] Iniciando API Backend...
start "Falcon EPSA API" cmd /k "python api_dashboard.py"
timeout /t 3 /nobreak > nul

echo.
echo [3/3] Iniciando Dashboard React...
cd dashboard-falcon
start "Falcon EPSA Dashboard" cmd /k "npm run dev"

echo.
echo ============================================
echo   Dashboard iniciado correctamente!
echo ============================================
echo.
echo   API:       http://localhost:8000
echo   Docs:      http://localhost:8000/docs
echo   Dashboard: http://localhost:5173
echo.
echo ============================================
echo.
pause
