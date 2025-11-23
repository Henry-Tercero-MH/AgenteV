# -*- coding: utf-8 -*-
"""
Módulo de corrección inteligente de placas con base de datos
Corrige errores comunes de OCR usando patrones y validación en BD
"""
import json
import os
from difflib import SequenceMatcher


class PlateCorrector:
    """Corrector inteligente de placas vehiculares"""

    def __init__(self, ruta_db="database/placas_db.json"):
        """
        Inicializa el corrector con la base de datos de placas.

        Args:
            ruta_db (str): Ruta al archivo JSON de placas
        """
        self.ruta_db = ruta_db
        self.placas_db = []
        self.placas_set = set()
        self._cargar_base_datos()

        # Patrones de placas guatemaltecas
        self.prefijos_comunes = ['P', 'C', 'M', 'A', 'O', 'T']  # Privado, Comercial, Moto, etc.

        # Diccionario de confusiones comunes en OCR
        self.confusiones_ocr = {
            # Letra real → Posibles confusiones
            'P': ['C', 'R', 'B'],
            'C': ['P', 'O', 'G'],
            'O': ['0', 'Q', 'D'],
            '0': ['O', 'D', 'Q'],
            'I': ['1', 'l', 'L'],
            '1': ['I', 'l', 'L'],
            'S': ['5', '8'],
            '5': ['S', '8'],
            '8': ['B', '3', '5'],
            'B': ['8', '3', 'P'],
            'Z': ['2', '7'],
            '2': ['Z'],
            'G': ['6', 'C'],
            '6': ['G', 'b'],
        }

        # Inversión del diccionario para búsqueda rápida
        self.puede_ser_confundido = {}
        for real, confusiones in self.confusiones_ocr.items():
            for conf in confusiones:
                if conf not in self.puede_ser_confundido:
                    self.puede_ser_confundido[conf] = []
                self.puede_ser_confundido[conf].append(real)

    def _cargar_base_datos(self):
        """Carga la base de datos de placas"""
        if not os.path.exists(self.ruta_db):
            print(f"[CORRECTOR] ⚠️  Base de datos no encontrada: {self.ruta_db}")
            return

        try:
            with open(self.ruta_db, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.placas_db = data.get('placas', [])
            self.placas_set = set(p['placa'].upper() for p in self.placas_db)

            print(f"[CORRECTOR] OK - {len(self.placas_set)} placas cargadas de BD")
        except Exception as e:
            print(f"[CORRECTOR] ❌ Error cargando BD: {e}")

    def corregir_placa(self, placa_detectada, confianza_ocr=0.0):
        """
        Corrige una placa detectada usando múltiples estrategias.

        Args:
            placa_detectada (str): Placa detectada por OCR
            confianza_ocr (float): Confianza del OCR (0.0-1.0)

        Returns:
            tuple: (placa_corregida, confianza_correccion, metodo_usado)
        """
        placa_upper = placa_detectada.upper().strip()

        if not placa_upper or len(placa_upper) < 4:
            return placa_detectada, confianza_ocr, "sin_correccion"

        # 1. Si la placa ya existe en BD exactamente, retornar
        if placa_upper in self.placas_set:
            return placa_upper, 1.0, "exacta_bd"

        # 2. Corrección específica para placas guatemaltecas
        placa_corregida, metodo = self._corregir_patron_guatemalteco(placa_upper)
        if placa_corregida and placa_corregida in self.placas_set:
            return placa_corregida, 0.95, f"patron_guatemala_{metodo}"

        # 3. Búsqueda de coincidencia con 1 carácter de diferencia
        placa_similar = self._buscar_similar_en_bd(placa_upper, max_diferencias=1)
        if placa_similar:
            return placa_similar, 0.90, "similar_1_char"

        # 4. Corrección basada en confusiones comunes de OCR
        placa_ocr_corregida = self._corregir_confusiones_ocr(placa_upper)
        if placa_ocr_corregida and placa_ocr_corregida in self.placas_set:
            return placa_ocr_corregida, 0.85, "confusiones_ocr"

        # 5. Búsqueda de coincidencia con 2 caracteres de diferencia
        if confianza_ocr < 0.7:  # Solo si confianza es baja
            placa_similar2 = self._buscar_similar_en_bd(placa_upper, max_diferencias=2)
            if placa_similar2:
                return placa_similar2, 0.75, "similar_2_chars"

        # Si no se encontró corrección, retornar original
        return placa_detectada, confianza_ocr, "sin_correccion"

    def _corregir_patron_guatemalteco(self, placa):
        """
        Aplica correcciones específicas para placas guatemaltecas.
        Formato típico: P###XXX, C###XXX, M###XX, etc.

        Args:
            placa (str): Placa a corregir

        Returns:
            tuple: (placa_corregida, metodo) o (None, None)
        """
        if len(placa) < 6 or len(placa) > 8:
            return None, None

        # CASO 1: C###XXX → P###XXX (confusión muy común)
        if placa[0] == 'C' and len(placa) >= 6:
            # Verificar si es patrón guatemalteco (letra + 3 números + letras)
            if placa[1:4].isdigit():
                placa_con_p = 'P' + placa[1:]
                if placa_con_p in self.placas_set:
                    print(f"[CORRECTOR] Corrección C→P: '{placa}' → '{placa_con_p}'")
                    return placa_con_p, "C_to_P"

        # CASO 2: P###XXX → C###XXX (menos común pero posible)
        if placa[0] == 'P' and len(placa) >= 6:
            if placa[1:4].isdigit():
                placa_con_c = 'C' + placa[1:]
                if placa_con_c in self.placas_set:
                    print(f"[CORRECTOR] Corrección P→C: '{placa}' → '{placa_con_c}'")
                    return placa_con_c, "P_to_C"

        # CASO 3: Otras confusiones en primera letra
        if placa[0] in self.puede_ser_confundido:
            posibles_letras = self.puede_ser_confundido[placa[0]]
            for letra_correcta in posibles_letras:
                if letra_correcta in self.prefijos_comunes:
                    placa_alternativa = letra_correcta + placa[1:]
                    if placa_alternativa in self.placas_set:
                        print(f"[CORRECTOR] Corrección prefijo: '{placa}' → '{placa_alternativa}'")
                        return placa_alternativa, f"prefix_{placa[0]}_to_{letra_correcta}"

        return None, None

    def _buscar_similar_en_bd(self, placa, max_diferencias=1):
        """
        Busca una placa similar en la base de datos.

        Args:
            placa (str): Placa a buscar
            max_diferencias (int): Máximo número de caracteres diferentes

        Returns:
            str: Placa similar encontrada, o None
        """
        if not self.placas_set:
            return None

        # Filtrar por longitud similar (±1 carácter)
        longitud_placa = len(placa)
        candidatos = [
            p for p in self.placas_set
            if abs(len(p) - longitud_placa) <= 1
        ]

        mejores_coincidencias = []

        for candidato in candidatos:
            diferencias = self._contar_diferencias(placa, candidato)

            if diferencias <= max_diferencias:
                # Calcular similitud (0.0 a 1.0)
                similitud = SequenceMatcher(None, placa, candidato).ratio()
                mejores_coincidencias.append((candidato, diferencias, similitud))

        if not mejores_coincidencias:
            return None

        # Ordenar por: menos diferencias primero, luego mayor similitud
        mejores_coincidencias.sort(key=lambda x: (x[1], -x[2]))

        mejor_candidato = mejores_coincidencias[0][0]
        print(f"[CORRECTOR] Coincidencia similar: '{placa}' → '{mejor_candidato}' "
              f"(dif: {mejores_coincidencias[0][1]}, sim: {mejores_coincidencias[0][2]:.2%})")

        return mejor_candidato

    def _contar_diferencias(self, texto1, texto2):
        """
        Cuenta el número de caracteres diferentes entre dos textos.

        Args:
            texto1 (str): Primer texto
            texto2 (str): Segundo texto

        Returns:
            int: Número de diferencias
        """
        if len(texto1) != len(texto2):
            # Si longitudes diferentes, considerar la diferencia + caracteres extra
            return abs(len(texto1) - len(texto2)) + \
                   sum(1 for a, b in zip(texto1, texto2) if a != b)

        return sum(1 for a, b in zip(texto1, texto2) if a != b)

    def _corregir_confusiones_ocr(self, placa):
        """
        Genera variaciones de la placa basándose en confusiones comunes de OCR.

        Args:
            placa (str): Placa original

        Returns:
            str: Placa corregida encontrada en BD, o None
        """
        # Generar variaciones sustituyendo caracteres confundibles
        variaciones = [placa]

        for i, char in enumerate(placa):
            if char in self.puede_ser_confundido:
                posibles = self.puede_ser_confundido[char]

                for reemplazo in posibles:
                    variacion = placa[:i] + reemplazo + placa[i+1:]
                    variaciones.append(variacion)

        # Buscar en BD
        for variacion in variaciones:
            if variacion in self.placas_set and variacion != placa:
                print(f"[CORRECTOR] Corrección OCR: '{placa}' → '{variacion}'")
                return variacion

        return None

    def validar_placa(self, placa):
        """
        Valida si una placa existe en la base de datos.

        Args:
            placa (str): Placa a validar

        Returns:
            dict: Información de la placa si existe, o None
        """
        placa_upper = placa.upper().strip()

        for placa_info in self.placas_db:
            if placa_info['placa'].upper() == placa_upper:
                return placa_info

        return None

    def obtener_info_placa(self, placa):
        """
        Obtiene información completa de una placa de la BD.

        Args:
            placa (str): Placa a buscar

        Returns:
            dict: Información de la placa, o None
        """
        return self.validar_placa(placa)

    def sugerir_correcciones(self, placa, max_sugerencias=5):
        """
        Sugiere múltiples correcciones posibles para una placa.

        Args:
            placa (str): Placa a corregir
            max_sugerencias (int): Máximo número de sugerencias

        Returns:
            list: Lista de tuplas (placa_sugerida, confianza, metodo)
        """
        sugerencias = []
        placa_upper = placa.upper().strip()

        # 1. Exacta
        if placa_upper in self.placas_set:
            sugerencias.append((placa_upper, 1.0, "exacta"))

        # 2. Patrón guatemalteco
        placa_gt, metodo_gt = self._corregir_patron_guatemalteco(placa_upper)
        if placa_gt and placa_gt not in [s[0] for s in sugerencias]:
            sugerencias.append((placa_gt, 0.95, f"patron_{metodo_gt}"))

        # 3. Similares (1 diferencia)
        similares = self._buscar_todas_similares(placa_upper, max_diferencias=1)
        for sim in similares:
            if sim not in [s[0] for s in sugerencias]:
                sugerencias.append((sim, 0.90, "similar_1"))

        # 4. Confusiones OCR
        placa_ocr = self._corregir_confusiones_ocr(placa_upper)
        if placa_ocr and placa_ocr not in [s[0] for s in sugerencias]:
            sugerencias.append((placa_ocr, 0.85, "ocr"))

        # 5. Similares (2 diferencias)
        similares2 = self._buscar_todas_similares(placa_upper, max_diferencias=2)
        for sim in similares2:
            if sim not in [s[0] for s in sugerencias] and len(sugerencias) < max_sugerencias:
                sugerencias.append((sim, 0.75, "similar_2"))

        # Ordenar por confianza
        sugerencias.sort(key=lambda x: x[1], reverse=True)

        return sugerencias[:max_sugerencias]

    def _buscar_todas_similares(self, placa, max_diferencias=1):
        """
        Busca todas las placas similares en BD.

        Args:
            placa (str): Placa a buscar
            max_diferencias (int): Máximo diferencias permitidas

        Returns:
            list: Lista de placas similares
        """
        if not self.placas_set:
            return []

        longitud_placa = len(placa)
        candidatos = [
            p for p in self.placas_set
            if abs(len(p) - longitud_placa) <= 1
        ]

        similares = []
        for candidato in candidatos:
            diferencias = self._contar_diferencias(placa, candidato)
            if diferencias <= max_diferencias:
                similares.append(candidato)

        return similares
