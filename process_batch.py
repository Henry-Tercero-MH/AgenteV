# -*- coding: utf-8 -*-
"""
Script para procesar todas las imágenes y generar datos para el dashboard
"""
import os
import time
import json
import glob
from datetime import datetime
from models.detector import DetectorPlacas
from models.ocr_engine import MotorOCR
from core.pipeline import PipelineDeteccion
from config.settings import CARPETA_SALIDA

def procesar_batch(carpeta_entrada='Inputs', carpeta_salida='Outputs', modelo_placas='best.pt', modelo_camiones='best_truck.pt'):
    """
    Procesa todas las imágenes y genera un JSON con resultados y métricas.

    Returns:
        dict: Resultados completos con métricas de tiempo
    """
    print(f"[INFO] Iniciando procesamiento batch de {carpeta_entrada}")

    # Inicializar detector y OCR
    inicio_carga = time.time()
    detector = DetectorPlacas(
        ruta_modelo_placas=modelo_placas,
        ruta_modelo_camiones=modelo_camiones
    )
    motor_ocr = MotorOCR()
    tiempo_carga_modelos = time.time() - inicio_carga

    print(f"[INFO] Modelos cargados en {tiempo_carga_modelos:.2f}s")

    # Crear pipeline
    pipeline = PipelineDeteccion(detector, motor_ocr)

    # Buscar todas las imágenes
    extensiones = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp']
    archivos = []
    for ext in extensiones:
        archivos.extend(glob.glob(os.path.join(carpeta_entrada, ext)))
        archivos.extend(glob.glob(os.path.join(carpeta_entrada, ext.upper())))

    print(f"[INFO] Encontradas {len(archivos)} imágenes")

    # Procesar cada imagen
    resultados = []
    tiempo_total_procesamiento = 0
    total_placas = 0
    total_placas_con_texto = 0

    for idx, archivo in enumerate(archivos, 1):
        print(f"\n[{idx}/{len(archivos)}] Procesando: {os.path.basename(archivo)}")

        inicio = time.time()
        resultado = pipeline.procesar_imagen(
            ruta_imagen=archivo,
            umbral_confianza=0.3,
            guardar=True,
            carpeta_salida=carpeta_salida
        )
        tiempo_procesamiento = time.time() - inicio
        tiempo_total_procesamiento += tiempo_procesamiento

        if resultado:
            # Contar placas con texto exitoso
            placas_con_texto = sum(1 for det in resultado['detecciones'] if det['texto'])
            total_placas += resultado['cantidad_placas']
            total_placas_con_texto += placas_con_texto

            # Preparar datos para JSON
            nombre_imagen = os.path.basename(archivo)
            nombre_salida = os.path.basename(archivo)

            detecciones_json = []
            for i, det in enumerate(resultado['detecciones']):
                nombre_base = os.path.splitext(nombre_imagen)[0]
                # Buscar el archivo de placa correspondiente
                patron_placa = f"{nombre_base}_placa_*_{i}.jpg"
                archivos_placa = glob.glob(os.path.join(carpeta_salida, patron_placa))
                ruta_placa = archivos_placa[0] if archivos_placa else None

                detecciones_json.append({
                    'caja': det['caja'],
                    'texto': det['texto'],
                    'confianza_deteccion': float(det['confianza_deteccion']),
                    'confianza_ocr': float(det['confianza_ocr']),
                    'imagen_placa': os.path.basename(ruta_placa) if ruta_placa else None
                })

            resultados.append({
                'id': idx,
                'nombre_imagen': nombre_imagen,
                'ruta_imagen_original': f'Inputs/{nombre_imagen}',
                'ruta_imagen_anotada': f'Outputs/{nombre_salida}',
                'tiempo_procesamiento': round(tiempo_procesamiento, 3),
                'cantidad_placas': resultado['cantidad_placas'],
                'placas_con_texto': placas_con_texto,
                'detecciones': detecciones_json,
                'timestamp': datetime.now().isoformat()
            })

            print(f"  ✓ Tiempo: {tiempo_procesamiento:.2f}s | Placas: {resultado['cantidad_placas']} | Con texto: {placas_con_texto}")

    # Calcular estadísticas
    tiempo_promedio = tiempo_total_procesamiento / len(archivos) if archivos else 0
    tasa_exito_ocr = (total_placas_con_texto / total_placas * 100) if total_placas > 0 else 0

    datos_completos = {
        'metadatos': {
            'fecha_procesamiento': datetime.now().isoformat(),
            'total_imagenes': len(archivos),
            'tiempo_total': round(tiempo_total_procesamiento, 2),
            'tiempo_promedio': round(tiempo_promedio, 2),
            'tiempo_carga_modelos': round(tiempo_carga_modelos, 2),
            'total_placas_detectadas': total_placas,
            'total_placas_con_texto': total_placas_con_texto,
            'tasa_exito_ocr': round(tasa_exito_ocr, 1),
            'modelo_placas': modelo_placas,
            'modelo_camiones': modelo_camiones
        },
        'resultados': resultados
    }

    # Guardar JSON
    ruta_json = os.path.join(carpeta_salida, 'resultados_dashboard.json')
    with open(ruta_json, 'w', encoding='utf-8') as f:
        json.dump(datos_completos, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"[INFO] Procesamiento completado")
    print(f"  📊 Total imágenes: {len(archivos)}")
    print(f"  🎯 Total placas detectadas: {total_placas}")
    print(f"  ✅ Placas con texto OCR: {total_placas_con_texto}")
    print(f"  📈 Tasa de éxito OCR: {tasa_exito_ocr:.1f}%")
    print(f"  ⏱️  Tiempo total: {tiempo_total_procesamiento:.2f}s")
    print(f"  ⚡ Tiempo promedio: {tiempo_promedio:.2f}s por imagen")
    print(f"  💾 Resultados guardados en: {ruta_json}")
    print(f"{'='*60}\n")

    return datos_completos


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Procesamiento batch para dashboard')
    parser.add_argument('--input', default='Inputs', help='Carpeta de entrada')
    parser.add_argument('--output', default='Outputs', help='Carpeta de salida')
    parser.add_argument('--model', default='best.pt', help='Modelo de placas')
    parser.add_argument('--truck-model', default='best_truck.pt', help='Modelo de camiones')

    args = parser.parse_args()

    procesar_batch(
        carpeta_entrada=args.input,
        carpeta_salida=args.output,
        modelo_placas=args.model,
        modelo_camiones=args.truck_model
    )
