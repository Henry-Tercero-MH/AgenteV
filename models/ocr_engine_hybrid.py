# -*- coding: utf-8 -*-
"""
Motor OCR Híbrido - Utiliza múltiples engines (Tesseract, EasyOCR, PaddleOCR)
y sistema de votación para obtener el mejor resultado
"""
import cv2
import numpy as np
from PIL import Image
from utils.image_preprocessing import PreprocessorPlacas
from utils.text_utils import es_placa_valida, limpiar_texto
import re


class MotorOCRHibrido:
    """Motor OCR híbrido con múltiples engines y sistema de votación"""

    def __init__(self, usar_easyocr=True, usar_paddleocr=True, usar_tesseract=True, usar_corrector=True):
        """
        Inicializa el motor OCR híbrido.

        Args:
            usar_easyocr (bool): Activar EasyOCR
            usar_paddleocr (bool): Activar PaddleOCR
            usar_tesseract (bool): Activar Tesseract
            usar_corrector (bool): Activar corrector inteligente con BD
        """
        self.preprocessor = PreprocessorPlacas()
        self.usar_easyocr = usar_easyocr
        self.usar_paddleocr = usar_paddleocr
        self.usar_tesseract = usar_tesseract
        self.usar_corrector = usar_corrector

        # Motores OCR
        self.tesseract = None
        self.easyocr_reader = None
        self.paddleocr_reader = None

        # Corrector inteligente
        self.corrector = None
        if usar_corrector:
            try:
                from utils.plate_correction import PlateCorrector
                self.corrector = PlateCorrector()
                print("[OCR-HYBRID] OK - Corrector inteligente activado")
            except Exception as e:
                print(f"[OCR-HYBRID] ⚠️  Corrector no disponible: {e}")
                self.corrector = None

        # Inicializar motores
        self._inicializar_motores()

    def _inicializar_motores(self):
        """Inicializa los motores OCR disponibles"""

        # 1. Tesseract
        if self.usar_tesseract:
            try:
                import pytesseract
                import sys
                if sys.platform == 'win32':
                    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

                version = pytesseract.get_tesseract_version()
                self.tesseract = pytesseract
                print(f"[OCR-HYBRID] ✅ Tesseract v{version} inicializado")
            except Exception as e:
                print(f"[OCR-HYBRID] ⚠️  Tesseract no disponible: {e}")
                self.tesseract = None

        # 2. EasyOCR
        if self.usar_easyocr:
            try:
                import easyocr
                # Inicializar con inglés y español, GPU si está disponible
                self.easyocr_reader = easyocr.Reader(['en', 'es'], gpu=False)
                print("[OCR-HYBRID] ✅ EasyOCR inicializado")
            except Exception as e:
                print(f"[OCR-HYBRID] ⚠️  EasyOCR no disponible: {e}")
                print("[OCR-HYBRID] Para instalar: pip install easyocr")
                self.easyocr_reader = None

        # 3. PaddleOCR
        if self.usar_paddleocr:
            try:
                from paddleocr import PaddleOCR
                # Inicializar con inglés, sin mostrar logs
                self.paddleocr_reader = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    use_gpu=False,
                    show_log=False
                )
                print("[OCR-HYBRID] ✅ PaddleOCR inicializado")
            except Exception as e:
                print(f"[OCR-HYBRID] ⚠️  PaddleOCR no disponible: {e}")
                print("[OCR-HYBRID] Para instalar: pip install paddlepaddle paddleocr")
                self.paddleocr_reader = None

        # Verificar que al menos un motor esté disponible
        if not any([self.tesseract, self.easyocr_reader, self.paddleocr_reader]):
            print("[OCR-HYBRID] ❌ ERROR: No hay motores OCR disponibles")

    def extraer_texto(self, imagen_placa):
        """
        Extrae texto usando múltiples motores y sistema de votación.

        Args:
            imagen_placa (numpy.ndarray): Imagen de la placa

        Returns:
            tuple: (texto_final, confianza, textos_por_motor)
        """
        # 1. Analizar calidad de imagen
        calidad = self.preprocessor.analizar_calidad(imagen_placa)
        print(f"[OCR-HYBRID] Calidad de imagen: nitidez={calidad['nitidez']:.1f}, "
              f"contraste={calidad['contraste']:.1f}, apta={calidad['apta_ocr']}")

        # 2. Detectar región de texto (ROI)
        roi = self.preprocessor.detectar_region_texto(imagen_placa)
        print(f"[OCR-HYBRID] ROI detectada: {roi.shape}")

        # 3. Generar variaciones de preprocesamiento
        variaciones = self.preprocessor.preprocesar_multiple(roi)
        print(f"[OCR-HYBRID] Generadas {len(variaciones)} variaciones de imagen")

        # 4. Ejecutar cada motor OCR sobre todas las variaciones
        resultados_por_motor = {
            "tesseract": [],
            "easyocr": [],
            "paddleocr": []
        }

        for nombre_variacion, img_variacion in variaciones:
            # Tesseract
            if self.tesseract:
                texto_tess = self._ocr_tesseract(img_variacion)
                if texto_tess:
                    resultados_por_motor["tesseract"].append({
                        "texto": texto_tess,
                        "variacion": nombre_variacion
                    })

            # EasyOCR
            if self.easyocr_reader:
                texto_easy, conf_easy = self._ocr_easyocr(img_variacion)
                if texto_easy:
                    resultados_por_motor["easyocr"].append({
                        "texto": texto_easy,
                        "confianza": conf_easy,
                        "variacion": nombre_variacion
                    })

            # PaddleOCR
            if self.paddleocr_reader:
                texto_paddle, conf_paddle = self._ocr_paddleocr(img_variacion)
                if texto_paddle:
                    resultados_por_motor["paddleocr"].append({
                        "texto": texto_paddle,
                        "confianza": conf_paddle,
                        "variacion": nombre_variacion
                    })

        # 5. Sistema de votación y selección del mejor resultado
        texto_final, confianza_final = self._votar_mejor_resultado(resultados_por_motor)

        # 6. Aplicar corrección de errores comunes (básica)
        if texto_final:
            texto_corregido = self._corregir_errores_comunes(texto_final)
            if texto_corregido != texto_final:
                print(f"[OCR-HYBRID] Corrección básica: '{texto_final}' -> '{texto_corregido}'")
                texto_final = texto_corregido

        # 7. Aplicar corrector inteligente con base de datos
        if texto_final and self.corrector:
            placa_corregida, conf_correccion, metodo = self.corrector.corregir_placa(
                texto_final,
                confianza_ocr=confianza_final
            )

            if placa_corregida != texto_final:
                print(f"[OCR-HYBRID] ✨ Corrección inteligente ({metodo}): '{texto_final}' -> '{placa_corregida}' (conf: {conf_correccion:.2f})")
                texto_final = placa_corregida
                confianza_final = max(confianza_final, conf_correccion)  # Usar la mayor confianza

        print(f"[OCR-HYBRID] 🎯 Resultado final: '{texto_final}' (confianza: {confianza_final:.2f})")

        return texto_final, confianza_final, resultados_por_motor

    def _ocr_tesseract(self, imagen):
        """
        Ejecuta OCR con Tesseract.

        Args:
            imagen (numpy.ndarray): Imagen preprocesada

        Returns:
            str: Texto extraído
        """
        if not self.tesseract:
            return ""

        try:
            # Convertir a PIL Image
            pil_image = Image.fromarray(imagen)

            # Configuración optimizada para placas
            # PSM 7 = línea de texto única
            # PSM 8 = palabra única
            # Probar ambos
            configs = [
                r'--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                r'--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
            ]

            mejores_resultados = []

            for config in configs:
                texto = self.tesseract.image_to_string(pil_image, config=config, lang='eng')
                texto_limpio = limpiar_texto(texto)

                if texto_limpio and len(texto_limpio) >= 4:
                    mejores_resultados.append(texto_limpio)

            # Retornar el más largo si hay varios
            if mejores_resultados:
                return max(mejores_resultados, key=len)

            return ""

        except Exception as e:
            print(f"[OCR-HYBRID] Error en Tesseract: {e}")
            return ""

    def _ocr_easyocr(self, imagen):
        """
        Ejecuta OCR con EasyOCR.

        Args:
            imagen (numpy.ndarray): Imagen preprocesada

        Returns:
            tuple: (texto, confianza)
        """
        if not self.easyocr_reader:
            return "", 0.0

        try:
            # EasyOCR espera BGR o RGB
            if len(imagen.shape) == 2:
                imagen_color = cv2.cvtColor(imagen, cv2.COLOR_GRAY2RGB)
            else:
                imagen_color = imagen

            # Ejecutar OCR con configuración para placas
            resultados = self.easyocr_reader.readtext(
                imagen_color,
                detail=1,
                paragraph=False,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            )

            if not resultados:
                return "", 0.0

            # Tomar el resultado con mayor confianza
            mejor_resultado = max(resultados, key=lambda x: x[2])
            texto = mejor_resultado[1]
            confianza = mejor_resultado[2]

            texto_limpio = limpiar_texto(texto)

            return texto_limpio, confianza

        except Exception as e:
            print(f"[OCR-HYBRID] Error en EasyOCR: {e}")
            return "", 0.0

    def _ocr_paddleocr(self, imagen):
        """
        Ejecuta OCR con PaddleOCR.

        Args:
            imagen (numpy.ndarray): Imagen preprocesada

        Returns:
            tuple: (texto, confianza)
        """
        if not self.paddleocr_reader:
            return "", 0.0

        try:
            # PaddleOCR espera BGR
            if len(imagen.shape) == 2:
                imagen_color = cv2.cvtColor(imagen, cv2.COLOR_GRAY2BGR)
            else:
                imagen_color = imagen

            # Ejecutar OCR
            resultados = self.paddleocr_reader.ocr(imagen_color, cls=True)

            if not resultados or not resultados[0]:
                return "", 0.0

            # Extraer textos y confianzas
            textos = []
            confianzas = []

            for linea in resultados[0]:
                if linea:
                    texto = linea[1][0]
                    confianza = linea[1][1]
                    textos.append(texto)
                    confianzas.append(confianza)

            if not textos:
                return "", 0.0

            # Combinar todos los textos
            texto_completo = ''.join(textos)
            confianza_promedio = sum(confianzas) / len(confianzas)

            texto_limpio = limpiar_texto(texto_completo)

            return texto_limpio, confianza_promedio

        except Exception as e:
            print(f"[OCR-HYBRID] Error en PaddleOCR: {e}")
            return "", 0.0

    def _votar_mejor_resultado(self, resultados_por_motor):
        """
        Sistema de votación para seleccionar el mejor resultado.
        Combina frecuencia, confianza y validación de formato.

        Args:
            resultados_por_motor (dict): Resultados de cada motor

        Returns:
            tuple: (texto_ganador, confianza)
        """
        # Recopilar todos los candidatos
        candidatos = {}

        for motor, resultados in resultados_por_motor.items():
            for resultado in resultados:
                texto = resultado["texto"]

                if not texto or len(texto) < 4:
                    continue

                # Inicializar candidato si no existe
                if texto not in candidatos:
                    candidatos[texto] = {
                        "votos": 0,
                        "confianzas": [],
                        "motores": [],
                        "es_valida": es_placa_valida(texto)
                    }

                # Incrementar votos
                candidatos[texto]["votos"] += 1
                candidatos[texto]["motores"].append(motor)

                # Agregar confianza si está disponible
                if "confianza" in resultado:
                    candidatos[texto]["confianzas"].append(resultado["confianza"])

        if not candidatos:
            return "", 0.0

        # Calcular score para cada candidato
        for texto, info in candidatos.items():
            # Score base: número de votos
            score = info["votos"] * 10

            # Bonus por confianza promedio
            if info["confianzas"]:
                conf_promedio = sum(info["confianzas"]) / len(info["confianzas"])
                score += conf_promedio * 5

            # Bonus grande si es placa válida
            if info["es_valida"]:
                score += 20

            # Bonus por longitud (placas típicas: 5-8 caracteres)
            if 5 <= len(texto) <= 8:
                score += 5

            # Bonus si múltiples motores coinciden
            motores_unicos = len(set(info["motores"]))
            if motores_unicos >= 2:
                score += 15

            candidatos[texto]["score"] = score

        # Ordenar por score
        candidatos_ordenados = sorted(
            candidatos.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        # Seleccionar el ganador
        texto_ganador = candidatos_ordenados[0][0]
        info_ganador = candidatos_ordenados[0][1]

        # Calcular confianza final
        if info_ganador["confianzas"]:
            confianza_final = sum(info_ganador["confianzas"]) / len(info_ganador["confianzas"])
        else:
            confianza_final = 0.85 if info_ganador["es_valida"] else 0.60

        print(f"[OCR-HYBRID] Votación: {len(candidatos)} candidatos, "
              f"ganador: '{texto_ganador}' (score: {info_ganador['score']:.1f}, "
              f"votos: {info_ganador['votos']}, motores: {set(info_ganador['motores'])})")

        return texto_ganador, confianza_final

    def _corregir_errores_comunes(self, texto):
        """
        Corrige errores comunes de OCR en placas.

        Args:
            texto (str): Texto a corregir

        Returns:
            str: Texto corregido
        """
        if not texto:
            return texto

        texto_corregido = texto

        # Diccionario de correcciones comunes
        correcciones = {
            # Letras confundidas con números
            'O': '0',  # O -> 0 si está entre números
            'I': '1',  # I -> 1 si está entre números
            'S': '5',  # S -> 5 en ciertos contextos
            'Z': '2',  # Z -> 2 en ciertos contextos
            'B': '8',  # B -> 8 en ciertos contextos

            # Números confundidos con letras (menos común, aplicar con cuidado)
            # '0': 'O',  # 0 -> O si está entre letras (deshabilitado por ahora)
            # '1': 'I',  # 1 -> I si está entre letras
        }

        # Aplicar correcciones contextuales
        # Ejemplo: Si hay un patrón ABC0123, no corregir
        # Pero si hay AB0O123, corregir O -> 0

        # Corrección para números rodeados de otros números
        for i in range(len(texto_corregido)):
            char = texto_corregido[i]

            # Si el carácter anterior y siguiente son dígitos
            if i > 0 and i < len(texto_corregido) - 1:
                prev_es_digito = texto_corregido[i-1].isdigit()
                next_es_digito = texto_corregido[i+1].isdigit()

                if prev_es_digito and next_es_digito:
                    if char == 'O':
                        texto_corregido = texto_corregido[:i] + '0' + texto_corregido[i+1:]
                    elif char == 'I':
                        texto_corregido = texto_corregido[:i] + '1' + texto_corregido[i+1:]
                    elif char == 'S':
                        texto_corregido = texto_corregido[:i] + '5' + texto_corregido[i+1:]

        return texto_corregido

    def esta_disponible(self):
        """Verifica si hay al menos un motor disponible"""
        return any([self.tesseract, self.easyocr_reader, self.paddleocr_reader])

    def obtener_motores_activos(self):
        """Retorna lista de motores activos"""
        activos = []
        if self.tesseract:
            activos.append("Tesseract")
        if self.easyocr_reader:
            activos.append("EasyOCR")
        if self.paddleocr_reader:
            activos.append("PaddleOCR")
        return activos
