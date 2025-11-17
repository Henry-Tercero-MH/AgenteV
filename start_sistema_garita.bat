@echo off
echo ============================================
echo   FALCON EPSA - Sistema de Control de Garita
echo ============================================
echo.

echo [1/3] Iniciando API Backend...
start "API Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python api_dashboard.py"

timeout /t 3 /nobreak >nul

echo [2/3] Iniciando Dashboard React...
start "Dashboard React" cmd /k "cd /d %~dp0\dashboard-falcon && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo   Sistema iniciado exitosamente!
echo ============================================
echo.
echo   API Backend:  http://localhost:8001
echo   Dashboard:    http://localhost:5173
echo   WebSocket:    ws://localhost:8001/ws
echo.
echo   Documentacion API: http://localhost:8001/docs
echo.
echo ============================================
echo   Para probar detecciones:
echo   python test_garita.py
echo ============================================
echo.
pause
