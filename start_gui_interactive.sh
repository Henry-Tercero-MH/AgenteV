#!/bin/bash
# FalconEPSA - Script de inicio interactivo con sistema multi-hilo

echo "🦅 FalconEPSA v2.2 - Sistema Multi-Hilo"
echo "🧵 Arquitectura: Captura + Procesamiento IA + GUI"
echo "============================================"
echo ""
echo "Modos disponibles:"
echo "1) 🔍 Análisis Completo (IA + OCR) - RTSP Canal 102 [Multi-hilo]"
echo "2) 👁️ Solo Visualización - RTSP Canal 102 [Sin congelamiento]"
echo "3) 🔍 Análisis Completo (IA + OCR) - Webcam Local [Multi-hilo]"
echo "4) 👁️ Solo Visualización - Webcam Local [Sin congelamiento]"
echo ""
echo "Beneficios del sistema multi-hilo:"
echo "✅ Interfaz siempre fluida (sin congelamiento)"
echo "✅ Modo visualización a 30 FPS"
echo "✅ Procesamiento IA en hilo separado"
echo "✅ Colas thread-safe para comunicación"
echo ""
read -p "Selecciona modo (1-4): " mode

case $mode in
    1)
        echo "🚀 Iniciando Análisis Completo con RTSP (Multi-hilo)..."
        echo "🧵 Hilos: Captura(30FPS) + IA(2-5FPS) + GUI(20FPS)"
        python app_gui.py --mode analysis --source rtsp
        ;;
    2)
        echo "👁️ Iniciando Solo Visualización con RTSP (Sin congelamiento)..."
        echo "🧵 Hilo único: Captura+Display (30 FPS constantes)"
        python app_gui.py --mode view_only --source rtsp
        ;;
    3)
        echo "🚀 Iniciando Análisis Completo con Webcam (Multi-hilo)..."
        echo "🧵 Hilos: Captura(30FPS) + IA(2-5FPS) + GUI(20FPS)"
        python app_gui.py --mode analysis --source webcam
        ;;
    4)
        echo "👁️ Iniciando Solo Visualización con Webcam (Sin congelamiento)..."
        echo "🧵 Hilo único: Captura+Display (30 FPS constantes)"
        python app_gui.py --mode view_only --source webcam
        ;;
    *)
        echo "❌ Opción inválida. Usando modo por defecto (Análisis RTSP Multi-hilo)."
        python app_gui.py
        ;;
esac