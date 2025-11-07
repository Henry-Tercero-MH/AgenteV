#!/usr/bin/env python3
"""Script rápido para probar conexión RTSP con cámara Hikvision."""
import cv2
import sys

# URL RTSP de la cámara Hikvision
RTSP_URL = "rtsp://admin:Ccamar4.@10.10.7.64:554/Streaming/Channels/101"

print(f"Intentando conectar a: {RTSP_URL}")
print("Presiona 'q' para salir")

# Configurar opciones de captura para mejorar compatibilidad RTSP
cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menos latencia

if not cap.isOpened():
    print("ERROR: No se pudo conectar a la cámara RTSP")
    print("\nPosibles soluciones:")
    print("1. Verifica que la IP sea correcta: 10.10.7.64")
    print("2. Verifica las credenciales: admin / Ccamar4.")
    print("3. Verifica que el puerto 554 esté abierto")
    print("4. Prueba con VLC: Media > Open Network Stream > pega la URL")
    print("5. Intenta con canal 201 (stream secundario): /Streaming/Channels/201")
    sys.exit(1)

print("✓ Conexión exitosa!")
print("Leyendo frames...")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print(f"ERROR: No se pudo leer frame después de {frame_count} frames")
        break
    
    frame_count += 1
    
    # Mostrar info cada 30 frames
    if frame_count % 30 == 0:
        h, w = frame.shape[:2]
        print(f"Frame {frame_count}: {w}x{h} pixels")
    
    # Redimensionar para visualización
    display = cv2.resize(frame, (960, 540))
    cv2.putText(display, f"Frame: {frame_count}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Test Camara Hikvision - Presiona Q para salir', display)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(f"\nTest completado. Total frames: {frame_count}")
        break

cap.release()
cv2.destroyAllWindows()
print("Conexión cerrada exitosamente.")
