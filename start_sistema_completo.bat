@echo off
echo ============================================
echo   FALCON EPSA - Sistema Completo de Garita
echo ============================================
echo.

echo [1/4] Iniciando API Backend...
start "API Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python api_dashboard.py"

timeout /t 5 /nobreak >nul

echo [2/4] Iniciando Dashboard React...
start "Dashboard React" cmd /k "cd /d %~dp0\dashboard-falcon && npm run dev"

timeout /t 5 /nobreak >nul

echo [3/4] Esperando que el sistema se estabilice...
timeout /t 3 /nobreak >nul

echo [4/4] Iniciando Sistema de Camara...
start "Camara Garita" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python camera_garita.py"

timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo   Sistema Completo Iniciado!
echo ============================================
echo.
echo   [1] API Backend:  http://localhost:8001
echo   [2] Dashboard:    http://localhost:5173
echo   [3] Camara:       Ventana OpenCV
echo   [4] WebSocket:    ws://localhost:8001/ws
echo.
echo   Documentacion API: http://localhost:8001/docs
echo.
echo ============================================
echo   El sistema esta detectando placas en
echo   tiempo real y enviando al dashboard!
echo ============================================
echo.
echo   Controles de la camara:
echo   - ESPACIO: Capturar frame manualmente
echo   - 'q' o ESC: Salir
echo   - 's': Ver estadisticas
echo.
pause
