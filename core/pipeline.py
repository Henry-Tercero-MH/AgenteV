# -*- coding: utf-8 -*-
"""
Pipeline principal de detección y OCR de placas
"""
import cv2
import os
from utils.image_utils import redimensionar_placa, dibujar_deteccion
from config.settings import CARPETA_SALIDA


class PipelineDeteccion:
    """Pipeline completo de detección y reconocimiento de placas"""
    
    def __init__(self, detector, motor_ocr):
        """
        Inicializa el pipeline.
        
        Args:
            detector (DetectorPlacas): Instancia del detector
            motor_ocr (MotorOCR): Instancia del motor OCR
        """
        self.detector = detector
        self.motor_ocr = motor_ocr
    
    def procesar_imagen(self, ruta_imagen, umbral_confianza=0.5, guardar=True, carpeta_salida=CARPETA_SALIDA):
        """
        Procesa una imagen completa: detecta placas y extrae texto.
        
        Args:
            ruta_imagen (str): Ruta a la imagen
            umbral_confianza (float): Umbral de confianza
            guardar (bool): Si guardar resultados
            carpeta_salida (str): Carpeta donde guardar
            
        Returns:
            dict: Resultado con detecciones y textos
        """
        # Cargar imagen
        imagen = cv2.imread(ruta_imagen)
        if imagen is None:
            print(f'[ERROR] No se pudo cargar la imagen: {ruta_imagen}')
            return None
        
        print(f'[INFO] Procesando: {ruta_imagen}')
        
        # Detectar camiones
        cajas_camiones = self.detector.detectar_camiones(imagen, umbral_confianza)
        
        # Generar regiones de búsqueda
        regiones = self.detector.generar_regiones_busqueda(imagen, cajas_camiones)
        
        # Detectar placas en cada región
        todas_detecciones = []
        imagen_anotada = imagen.copy()
        
        for idx_region, region in enumerate(regiones):
            y1, x1, y2, x2 = region
            print(f'[DEBUG] Procesando región {idx_region}: crop size=({y2-y1}x{x2-x1})')
            
            detecciones = self.detector.detectar_placas_en_region(
                imagen, (x1, y1, x2, y2), umbral_confianza
            )
            
            print(f'[DEBUG] {len(detecciones)} detecciones de placas en región {idx_region}')
            
            # Procesar cada placa detectada
            for det in detecciones:
                fx1, fy1, fx2, fy2 = det['caja_completa']
                conf_placa = det['confianza']
                placa_img = det['imagen_recorte']
                
                print(f'[DEBUG] Placa detectada: full_box=[{fx1},{fy1},{fx2},{fy2}], conf={conf_placa:.3f}')
                
                # Redimensionar si es necesario
                placa_img = redimensionar_placa(placa_img, ancho_minimo=64)
                
                # Extraer texto con OCR
                texto, confianza_ocr, textos_originales = self.motor_ocr.extraer_texto(placa_img)
                
                print(f'[DEBUG] Textos OCR: {textos_originales} -> resultado: [{texto}], confianza: {confianza_ocr:.3f}')
                print(f'[DEBUG] Resultado OCR: "{texto}" conf={confianza_ocr:.3f} (tamaño placa: {placa_img.shape[1]}x{placa_img.shape[0]}px)')
                
                # Dibujar en imagen anotada
                imagen_anotada = dibujar_deteccion(
                    imagen_anotada, fx1, fy1, fx2, fy2, 
                    texto, conf_placa
                )
                
                # Guardar recorte de placa
                if guardar:
                    os.makedirs(carpeta_salida, exist_ok=True)
                    nombre_base = os.path.splitext(os.path.basename(ruta_imagen))[0]
                    nombre_placa = f"{nombre_base}_placa_{idx_region}_{len(todas_detecciones)}.jpg"
                    ruta_placa = os.path.join(carpeta_salida, nombre_placa)
                    cv2.imwrite(ruta_placa, placa_img)
                    print(f'[DEBUG] Guardado recorte de placa: {ruta_placa}')
                
                todas_detecciones.append({
                    'caja': [fx1, fy1, fx2, fy2],
                    'texto': texto,
                    'confianza_deteccion': conf_placa,
                    'confianza_ocr': confianza_ocr,
                    'textos_originales': textos_originales
                })
        
        # Guardar imagen anotada
        if guardar:
            nombre_salida = os.path.basename(ruta_imagen)
            ruta_salida = os.path.join(carpeta_salida, nombre_salida)
            cv2.imwrite(ruta_salida, imagen_anotada)
            print(f'[DEBUG] Guardada imagen anotada: {ruta_salida}')
        
        resultado = {
            'ruta_imagen': ruta_imagen,
            'detecciones': todas_detecciones,
            'cantidad_placas': len(todas_detecciones),
            'imagen_anotada': imagen_anotada
        }
        
        print(f'Procesado: {ruta_imagen} | placas encontradas: {len(todas_detecciones)}')
        
        return resultado
    
    def procesar_directorio(self, ruta_directorio, umbral_confianza=0.5, carpeta_salida=CARPETA_SALIDA):
        """
        Procesa todas las imágenes en un directorio.
        
        Args:
            ruta_directorio (str): Ruta al directorio
            umbral_confianza (float): Umbral de confianza
            carpeta_salida (str): Carpeta donde guardar
            
        Returns:
            list: Lista de resultados
        """
        import glob
        
        extensiones = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp']
        archivos = []
        
        for ext in extensiones:
            archivos.extend(glob.glob(os.path.join(ruta_directorio, ext)))
            archivos.extend(glob.glob(os.path.join(ruta_directorio, ext.upper())))
        
        print(f'[INFO] Encontradas {len(archivos)} imágenes en {ruta_directorio}')
        
        resultados = []
        imagenes_con_placas = 0
        
        for archivo in archivos:
            resultado = self.procesar_imagen(archivo, umbral_confianza, True, carpeta_salida)
            if resultado and resultado['cantidad_placas'] > 0:
                imagenes_con_placas += 1
            resultados.append(resultado)
        
        print(f'Procesadas {len(archivos)} imágenes. Placas detectadas en {imagenes_con_placas} imágenes.')
        
        return resultados
