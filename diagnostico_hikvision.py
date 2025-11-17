#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnóstico de Cámara Hikvision
Prueba diferentes configuraciones de conexión
"""

import cv2
import time
import socket

CAMERA_IP = "10.10.7.224"

def test_ping():
    """Probar si la cámara responde a ping"""
    print("[1/5] Probando conectividad de red...")
    try:
        socket.gethostbyaddr(CAMERA_IP)
        print(f"[OK] Cámara accesible en {CAMERA_IP}")
        return True
    except:
        print(f"[ERROR] No se puede alcanzar {CAMERA_IP}")
        return False

def test_connection(url, description):
    """Probar conexión a un URL específico"""
    print(f"[*] Probando: {description}")
    print(f"    URL: {url}")
    
    cap = cv2.VideoCapture(url)
    time.sleep(1)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            print(f"[OK] FUNCIONANDO - {w}x{h}")
            cap.release()
            return True
        else:
            print(f"[WARN] Conectado pero sin frames")
            cap.release()
            return False
    else:
        print(f"[ERROR] No se pudo conectar")
        cap.release()
        return False

# Test 1: Ping
print("=" * 60)
print("DIAGNÓSTICO DE CÁMARA HIKVISION")
print("=" * 60)
print()

if not test_ping():
    print("\n[ERROR] Cámara no accesible. Verifica la IP y conexión de red.")
    exit(1)

print()
print("[2/5] Probando diferentes canales RTSP...")
print()

# Diferentes combinaciones de URL
urls_to_test = [
    # Canal 101 (estándar)
    ("rtsp://admin:admin@10.10.7.224:554/Streaming/Channels/101", 
     "Canal 101 (estándar Hikvision)"),
    
    # Canal 1
    ("rtsp://admin:admin@10.10.7.224:554/Streaming/Channels/1", 
     "Canal 1"),
    
    # H264
    ("rtsp://admin:admin@10.10.7.224:554/Streaming/Channels/101/H264",
     "Canal 101 H264"),
    
    # Stream 1
    ("rtsp://admin:admin@10.10.7.224:554/stream1",
     "Stream 1"),
    
    # Sin puerto (por defecto 554)
    ("rtsp://admin:admin@10.10.7.224/Streaming/Channels/101",
     "Sin puerto especificado"),
]

results = []
for url, desc in urls_to_test:
    if test_connection(url, desc):
        results.append((url, desc))
    print()

print("[3/5] Probando HTTP...")
http_urls = [
    ("http://admin:admin@10.10.7.224:8080/video", "HTTP Stream"),
    ("http://admin:admin@10.10.7.224:8000/video", "HTTP Port 8000"),
]

for url, desc in http_urls:
    if test_connection(url, desc):
        results.append((url, desc))
    print()

print("=" * 60)
print("RESULTADOS")
print("=" * 60)

if results:
    print(f"\n[OK] Se encontro {len(results)} conexion(es) funcionando:\n")
    for url, desc in results:
        print(f"  - {desc}")
        print(f"    URL: {url}\n")
    
    print("Usa esta URL en config.py:")
    print(f'RTSP_URL = "{results[0][0]}"')
else:
    print("\n[ERROR] No se encontro ninguna conexion funcionando.")
    print("\nPosibles soluciones:")
    print("1. Verificar que la camara esta encendida")
    print("2. Verificar que la IP 10.10.7.224 es correcta")
    print("3. Verificar credenciales (usuario: admin, contrasena: ?)")
    print("4. Acceder a http://10.10.7.224 en navegador para verificar")
    print("5. Verificar que el puerto RTSP (554) no esta bloqueado")

print("\n" + "=" * 60)
