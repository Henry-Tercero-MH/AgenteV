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
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio en mayúsculas
    """
    lista_permitida = re.compile(r"[A-Z0-9]")
    texto = (texto or "").upper()
    filtrado = ''.join([c for c in texto if lista_permitida.match(c)])
    return filtrado


def es_placa_valida(texto):
    """
    Valida si un texto parece ser una placa válida usando patrones inteligentes.
    
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
