# -*- coding: utf-8 -*-
"""
Utilidades para procesamiento y validación de texto de placas
"""
import re
from config.settings import (
    LONGITUD_MIN_PLACA, LONGITUD_MAX_PLACA,
    DIGITOS_MIN_PLACA_ANTIGUA, PALABRAS_CLAVE_PAIS
)


def limpiar_texto(texto):
    """
    Mantener solo mayúsculas y dígitos (whitelist) y quitar espacios.
    Filtra caracteres sueltos al principio y final que no formen parte de una placa válida.

    Args:
        texto (str): Texto a limpiar

    Returns:
        str: Texto limpio en mayúsculas
    """
    lista_permitida = re.compile(r"[A-Z0-9]")
    texto = (texto or "").upper()
    filtrado = ''.join([c for c in texto if lista_permitida.match(c)])

    # Si el texto es muy largo, intentar extraer la placa más probable
    if len(filtrado) > LONGITUD_MAX_PLACA:
        # Buscar patrones de placa comunes (ej: ABC123, AB123CD, etc.)
        # Patrón típico: 3 letras + 3 números, o 2 letras + 3 números + 2 letras, etc.
        patrones = [
            r'[A-Z]{2,3}\d{3,4}[A-Z]{0,2}',  # AB123, ABC123, AB123C, ABC123D
            r'\d{3,4}[A-Z]{2,3}',            # 123AB, 123ABC
            r'[A-Z]\d{3,4}[A-Z]{1,2}',       # A123B, A123BC
        ]

        for patron in patrones:
            matches = re.findall(patron, filtrado)
            if matches:
                # Tomar el match más largo que esté en rango válido
                matches_validas = [m for m in matches if LONGITUD_MIN_PLACA <= len(m) <= LONGITUD_MAX_PLACA]
                if matches_validas:
                    return max(matches_validas, key=len)  # El más largo

        # Si no encontramos patrones, tomar una subcadena central
        if len(filtrado) > LONGITUD_MAX_PLACA:
            start = (len(filtrado) - LONGITUD_MAX_PLACA) // 2
            filtrado = filtrado[start:start + LONGITUD_MAX_PLACA]

    return filtrado


def es_placa_valida(texto):
    """
    Valida si un texto parece ser una placa válida usando patrones inteligentes.
    Rechaza textos que empiecen con números si el resto forma una placa válida.
    
    Args:
        texto (str): Texto a validar
        
    Returns:
        bool: True si parece una placa válida
    """
    txt = texto.strip().upper()
    
    # Filtrar textos vacíos o muy cortos
    if len(txt) < 3:
        return False
    
    # Filtrar años solos (4 dígitos exactos)
    if re.match(r'^\d{4}$', txt):
        return False
    
    # Filtrar palabras de país/región comunes
    if any(keyword in txt for keyword in PALABRAS_CLAVE_PAIS):
        return False
    
    # Extraer solo caracteres alfanuméricos
    alfanumerico = re.sub(r'[^A-Z0-9]', '', txt)
    
    if len(alfanumerico) < LONGITUD_MIN_PLACA or len(alfanumerico) > LONGITUD_MAX_PLACA:
        return False
    
    # REGLA ESPECIAL: Si empieza con número y el resto forma una placa válida, rechazar
    if alfanumerico[0].isdigit() and len(alfanumerico) > 4:
        resto = alfanumerico[1:]
        if len(resto) >= LONGITUD_MIN_PLACA and es_placa_valida_basico(resto):
            return False  # Es ruido al inicio
    
    # Verificar formato de placa usando función auxiliar
    return es_placa_valida_basico(alfanumerico)


def es_placa_valida_basico(alfanumerico):
    """
    Función auxiliar para validar el formato básico de placa.
    
    Args:
        alfanumerico (str): Texto solo con caracteres alfanuméricos
        
    Returns:
        bool: True si el formato es válido
    """
    # Verificar formato de placa
    tiene_letra = bool(re.search(r'[A-Z]', alfanumerico))
    cantidad_digitos = len(re.findall(r'\d', alfanumerico))
    
    # Válido si: tiene letras Y números (moderno), O solo números con 5+ dígitos (antiguo)
    es_moderna = tiene_letra and cantidad_digitos >= 1
    es_antigua_numerica = not tiene_letra and cantidad_digitos >= DIGITOS_MIN_PLACA_ANTIGUA
    
    return es_moderna or es_antigua_numerica


def deduplicar_textos(lista_textos):
    """
    Elimina textos duplicados y subcadenas de textos más largos.
    
    Args:
        lista_textos (list): Lista de textos a deduplicar
        
    Returns:
        list: Lista deduplicada
    """
    textos_dedup = []
    
    for i, txt in enumerate(lista_textos):
        txt_limpio = txt.strip()
        if not txt_limpio:
            continue
        
        # Verificar si este texto es subcadena de otro texto más largo
        es_subcadena = False
        for j, otro_txt in enumerate(lista_textos):
            if i != j and txt_limpio in otro_txt and len(txt_limpio) < len(otro_txt):
                es_subcadena = True
                break
        
        if not es_subcadena and txt_limpio not in textos_dedup:
            textos_dedup.append(txt_limpio)
    
    return textos_dedup
