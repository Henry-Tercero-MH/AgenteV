# -*- coding: utf-8 -*-
"""
Motor OCR con Tesseract en Python 3.13
NOTA: Para mejor precisión, usar MotorOCRHibrido de models.ocr_engine_hybrid
"""
# Importación lazy para evitar problemas de dependencias al inicio
import cv2
from PIL import Image, ImageEnhance
from config.settings import IDIOMA_OCR, USAR_CLASIFICADOR_ANGULO
from utils.text_utils import es_placa_valida, deduplicar_textos, limpiar_texto


class MotorOCR:
    """Motor de OCR para reconocimiento de texto en placas"""

    def __init__(self, usar_hibrido=False):
        """
        Inicializa el motor OCR

        Args:
            usar_hibrido (bool): Si True, usa el motor híbrido avanzado (recomendado)
        """
        self.ocr = None
        self.pytesseract = None
        self.usar_hibrido = usar_hibrido
        self.motor_hibrido = None

        if usar_hibrido:
            try:
                from models.ocr_engine_hybrid import MotorOCRHibrido
                self.motor_hibrido = MotorOCRHibrido()
                print("[INFO] ✨ Motor OCR Híbrido activado")
                print(f"[INFO] Motores disponibles: {self.motor_hibrido.obtener_motores_activos()}")
            except Exception as e:
                print(f"[WARNING] No se pudo inicializar motor híbrido: {e}")
                print("[INFO] Usando Tesseract estándar como fallback")
                self.usar_hibrido = False
                self._inicializar_ocr()
        else:
            self._inicializar_ocr()
    
    def _inicializar_ocr(self):
        """Inicializa Tesseract OCR con configuración"""
        try:
            # Importación lazy
            import pytesseract
            
            # Configurar ruta de Tesseract
            import sys
            if sys.platform == 'win32':
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Verificar que Tesseract esté disponible
            version = pytesseract.get_tesseract_version()
            print(f"[INFO] Tesseract OCR v{version} inicializado correctamente")
            self.ocr = True
            self.pytesseract = pytesseract
        except Exception as e:
            print(f"[ERROR] No se pudo inicializar OCR: {e}")
            self.ocr = None
            self.pytesseract = None
    
    def extraer_texto(self, imagen_placa):
        """
        Extrae texto de una imagen de placa.
        Si usar_hibrido=True, usa el motor híbrido avanzado.
        Sino, usa Tesseract estándar.

        Args:
            imagen_placa (numpy.ndarray): Imagen de la placa

        Returns:
            tuple: (texto_limpio, confianza, textos_originales)
        """
        # Si está activado el motor híbrido, usarlo
        if self.usar_hibrido and self.motor_hibrido:
            try:
                texto, confianza, resultados_detallados = self.motor_hibrido.extraer_texto(imagen_placa)
                # Convertir formato de retorno para compatibilidad
                textos_originales = []
                for motor, resultados in resultados_detallados.items():
                    for res in resultados:
                        textos_originales.append(res.get("texto", ""))
                return texto, confianza, textos_originales
            except Exception as e:
                print(f"[WARNING] Error en motor híbrido, usando Tesseract: {e}")
                # Fallback a Tesseract
                pass

        # Modo Tesseract estándar
        if self.pytesseract is None:
            return "", 0.0, []

        try:
            # Convertir numpy array a PIL Image
            pil_image = Image.fromarray(imagen_placa)

            # Configuración OCR
            config = r'--psm 8 --oem 3 -c tesseract_create_pdf=0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'

            # Ejecutar OCR sin pre-procesamiento
            texto = self.pytesseract.image_to_string(pil_image, config=config, lang='eng')
            texto = texto.strip().upper()

            print(f"[DEBUG] Texto OCR crudo: '{texto}'")

            # Limpiar texto con filtros mejorados
            texto_limpio = self._post_procesar_texto(texto)

            print(f"[DEBUG] Texto procesado: '{texto_limpio}'")

            # Verificar si es placa válida
            if es_placa_valida(texto_limpio):
                confianza = 0.92  # Confianza estimada para Tesseract
                return texto_limpio, confianza, [texto]
            else:
                print(f"[DEBUG] Texto rechazado por validación: '{texto_limpio}'")
                return "", 0.0, []

        except Exception as e:
            print(f"[ERROR] Error en OCR: {e}")
            return "", 0.0, []
    
    def _post_procesar_texto(self, texto):
        """
        Post-procesa el texto OCR para eliminar caracteres extra.
        
        Args:
            texto (str): Texto crudo del OCR
            
        Returns:
            str: Texto procesado
        """
        import re
        from utils.text_utils import es_placa_valida
        
        # Limpiar caracteres no alfanuméricos primero
        texto = re.sub(r'[^A-Z0-9]', '', texto.upper())
        
        # Si está vacío, retornar vacío
        if not texto:
            return ""
        
        # Si es una placa válida tal cual, retornarla
        if es_placa_valida(texto):
            return texto
        
        # INTENTO AGRESIVO: Si tiene un caracter inicial que es número, quitarlo SIEMPRE
        # Esto es porque el OCR a menudo captura números sueltos al principio
        if len(texto) >= 6 and texto[0].isdigit():
            texto_sin_inicial = texto[1:]
            print(f"[DEBUG] Quitando caracter inicial '{texto[0]}' de '{texto}' -> '{texto_sin_inicial}' (intento agresivo)")
            texto = texto_sin_inicial
        
        # Si tiene un caracter final que parece ruido, intentar quitarlo
        if len(texto) > 4 and texto[-1].isdigit() and not texto[-2].isdigit():
            texto_sin_final = texto[:-1]
            if es_placa_valida(texto_sin_final):
                print(f"[DEBUG] Quitando caracter final '{texto[-1]}' -> '{texto_sin_final}'")
                return texto_sin_final
        
        # Si tiene longitud ideal después de limpieza, retornarlo
        if 4 <= len(texto) <= 8:
            return texto
        
        # Para textos más largos, buscar el patrón más probable
        if len(texto) > 8:
            # Buscar secuencias que parezcan placas
            patrones = [
                r'[A-Z]{2,4}\d{3,4}[A-Z]{0,2}',  # AB123, ABC123, ABCD123, etc.
                r'\d{3,4}[A-Z]{2,4}',            # 123AB, 123ABC
                r'[A-Z]\d{3,4}[A-Z]{1,3}',       # A123B, A123BC
            ]
            
            for patron in patrones:
                matches = re.findall(patron, texto)
                if matches:
                    # Filtrar por longitud válida
                    matches_validas = [m for m in matches if 4 <= len(m) <= 8]
                    if matches_validas:
                        candidato = max(matches_validas, key=len)
                        # Verificar si es válido
                        if es_placa_valida(candidato):
                            return candidato
            
            # Si no hay matches válidos, tomar caracteres centrales
            centro = len(texto) // 2
            inicio = max(0, centro - 4)
            fin = min(len(texto), centro + 4)
            candidato = texto[inicio:fin]
            if es_placa_valida(candidato):
                return candidato
        
        # Si nada funciona, retornar el texto original si tiene longitud razonable
        if 4 <= len(texto) <= 8:
            return texto
        
        return ""
    
    def esta_disponible(self):
        """Verifica si el motor OCR está disponible"""
        return self.pytesseract is not None
