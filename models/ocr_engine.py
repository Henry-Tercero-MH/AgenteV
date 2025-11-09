# -*- coding: utf-8 -*-
"""
Motor OCR con wrapper para PaddleOCR en Python 3.13
"""
from ocr_wrapper import PaddleOCR
from config.settings import IDIOMA_OCR, USAR_CLASIFICADOR_ANGULO
from utils.text_utils import es_placa_valida, deduplicar_textos, limpiar_texto


class MotorOCR:
    """Motor de OCR para reconocimiento de texto en placas"""
    
    def __init__(self):
        """Inicializa el motor OCR"""
        self.ocr = None
        self._inicializar_ocr()
    
    def _inicializar_ocr(self):
        """Inicializa PaddleOCR con configuración"""
        try:
            # El wrapper no usa parámetros en el constructor
            self.ocr = PaddleOCR(lang=IDIOMA_OCR)
            print("[INFO] Motor OCR inicializado correctamente")
        except Exception as e:
            print(f"[ERROR] No se pudo inicializar OCR: {e}")
            self.ocr = None
    
    def extraer_texto(self, imagen_placa):
        """
        Extrae texto de una imagen de placa.
        
        Args:
            imagen_placa (numpy.ndarray): Imagen de la placa
            
        Returns:
            tuple: (texto_limpio, confianza, textos_originales)
        """
        if self.ocr is None:
            return "", 0.0, []
        
        try:
            # Ejecutar OCR - el wrapper usa .predict()
            resultado_ocr = self.ocr.predict(imagen_placa)
            
            # Parsear resultado (formato wrapper: [[{'rec_texts': [...], 'rec_scores': [...]}]])
            textos_rec = []
            scores_rec = []
            
            if isinstance(resultado_ocr, list) and len(resultado_ocr) > 0:
                if isinstance(resultado_ocr[0], list) and len(resultado_ocr[0]) > 0:
                    primer_item = resultado_ocr[0][0]
                    if isinstance(primer_item, dict):
                        textos_rec = primer_item.get('rec_texts', [])
                        scores_rec = primer_item.get('rec_scores', [])
            
            if not textos_rec:
                return "", 0.0, []
            
            # Filtrar textos válidos (que parezcan placas)
            textos_filtrados = []
            scores_filtrados = []
            
            for idx, txt in enumerate(textos_rec):
                if es_placa_valida(txt):
                    textos_filtrados.append(txt)
                    if idx < len(scores_rec):
                        scores_filtrados.append(scores_rec[idx])
            
            # Si no quedó nada válido, usar textos originales
            if not textos_filtrados:
                textos_filtrados = textos_rec
                scores_filtrados = scores_rec
            
            # Deduplicar textos
            textos_dedup = deduplicar_textos(textos_filtrados)
            
            if textos_dedup:
                textos_filtrados = textos_dedup
            
            # Unir y limpiar textos
            texto_unido = ''.join(textos_filtrados).upper()
            texto_limpio = limpiar_texto(texto_unido)
            
            # Calcular confianza promedio
            confianza = sum(scores_filtrados) / len(scores_filtrados) if scores_filtrados else 0.0
            
            return texto_limpio, confianza, textos_rec
            
        except Exception as e:
            print(f"[ERROR] Error en OCR: {e}")
            return "", 0.0, []
    
    def esta_disponible(self):
        """Verifica si el motor OCR está disponible"""
        return self.ocr is not None
