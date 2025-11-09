# -*- coding: utf-8 -*-
"""
Sistema de Detección de Placas con YOLO + PaddleOCR

Uso:
  python app.py --source Inputs/imagen.jpg --model best.pt --truck-model best_truck.pt
  python app.py --source Inputs/ --model best.pt
  python app.py --webcam --model best.pt

Arquitectura modular profesional - Versión 2.0
"""

import argparse
import os
import sys

# Importar módulos propios
from models.detector import DetectorPlacas
from models.ocr_engine import MotorOCR
from core.pipeline import PipelineDeteccion
from config.settings import (
    MODELO_PLACAS_DEFAULT, UMBRAL_CONFIANZA_DEFAULT,
    CARPETA_SALIDA, SKIP_FRAMES_DEFAULT, INDICE_CAMARA_DEFAULT
)


def procesar_fuente(args):
    """Procesa una fuente (imagen o directorio)."""
    # Inicializar detector
    detector = DetectorPlacas(
        ruta_modelo_placas=args.model,
        ruta_modelo_camiones=args.truck_model
    )
    
    # Inicializar motor OCR
    motor_ocr = MotorOCR()
    
    if not motor_ocr.esta_disponible():
        print("[ERROR] Motor OCR no disponible.")
        sys.exit(1)
    
    # Crear pipeline
    pipeline = PipelineDeteccion(detector, motor_ocr)
    
    # Procesar según tipo de fuente
    if os.path.isfile(args.source):
        resultado = pipeline.procesar_imagen(
            ruta_imagen=args.source,
            umbral_confianza=args.conf,
            guardar=True,
            carpeta_salida=args.output
        )
    elif os.path.isdir(args.source):
        resultados = pipeline.procesar_directorio(
            ruta_directorio=args.source,
            umbral_confianza=args.conf,
            carpeta_salida=args.output
        )
    else:
        print(f"[ERROR] La fuente no existe: {args.source}")
        sys.exit(1)
    
    print("\n[INFO] Procesamiento completado")


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Detección de Placas con YOLO + OCR')
    
    parser.add_argument('--source', '-s', default=None, help='Ruta a imagen o carpeta')
    parser.add_argument('--model', '-m', default=MODELO_PLACAS_DEFAULT, help='Modelo YOLO de placas')
    parser.add_argument('--truck-model', default=None, help='Modelo YOLO de camiones (opcional)')
    parser.add_argument('--output', '-o', default=CARPETA_SALIDA, help='Carpeta de salida')
    parser.add_argument('--conf', '-c', type=float, default=UMBRAL_CONFIANZA_DEFAULT, help='Umbral de confianza')
    parser.add_argument('--webcam', action='store_true', help='Modo webcam')
    parser.add_argument('--cam-index', type=int, default=INDICE_CAMARA_DEFAULT, help='Índice de cámara')
    parser.add_argument('--skip-frames', type=int, default=SKIP_FRAMES_DEFAULT, help='Saltar frames')
    
    args = parser.parse_args()
    
    if args.webcam:
        print("[INFO] Modo webcam - Usa: python web_dashboard.py")
    else:
        if not args.source:
            parser.error("--source es requerido")
        procesar_fuente(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrumpido")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
