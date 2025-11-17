# -*- coding: utf-8 -*-
"""
Motor OCR con Tesseract en Python 3.13
"""
import pytesseract
from PIL import Image, ImageEnhance
from config.settings import IDIOMA_OCR, USAR_CLASIFICADOR_ANGULO
from utils.text_utils import es_placa_valida, deduplicar_textos, limpiar_texto


class MotorOCR:
    """Motor de OCR para reconocimiento de texto en placas"""
    
    def __init__(self):
        """Inicializa el motor OCR"""
        self.ocr = None
        self._inicializar_ocr()
    
    def _inicializar_ocr(self):
        """Inicializa Tesseract OCR con configuración"""
        try:
            # Configurar ruta de Tesseract
            import sys
            if sys.platform == 'win32':
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            # Verificar que Tesseract esté disponible
            version = pytesseract.get_tesseract_version()
            print(f"[INFO] Tesseract OCR v{version} inicializado correctamente")
            self.ocr = True  # Solo marcar como disponible
        except Exception as e:
            print(f"[ERROR] No se pudo inicializar OCR: {e}")
            self.ocr = None
    
    def extraer_texto(self, imagen_placa):
        """
        Extrae texto de una imagen de placa usando Tesseract.
        
        Args:
            imagen_placa (numpy.ndarray): Imagen de la placa
            
        Returns:
            tuple: (texto_limpio, confianza, textos_originales)
        """
        if self.ocr is None:
            return "", 0.0, []
        
        try:
            # Convertir numpy array a PIL Image
            pil_image = Image.fromarray(imagen_placa)
            
            # Pre-procesamiento
            pil_image = ImageEnhance.Contrast(pil_image).enhance(2.5)
            pil_image = ImageEnhance.Sharpness(pil_image).enhance(3.0)
            
            # Configuración OCR
            config = r'--psm 7 --oem 3 -c tesseract_create_pdf=0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
            
            # Ejecutar OCR
            texto = pytesseract.image_to_string(pil_image, config=config, lang='eng')
            texto = texto.strip().upper()
            
            # Limpiar texto
            texto_limpio = limpiar_texto(texto)
            
            # Verificar si es placa válida
            if es_placa_valida(texto_limpio):
                confianza = 0.92  # Confianza estimada para Tesseract
                return texto_limpio, confianza, [texto]
            else:
                return "", 0.0, []
            
        except Exception as e:
            print(f"[ERROR] Error en OCR: {e}")
            return "", 0.0, []
    
    def esta_disponible(self):
        """Verifica si el motor OCR está disponible"""
        return self.ocr is not None
