# -*- coding: utf-8 -*-
"""
Utilidades para procesamiento de imágenes
"""
import cv2
import numpy as np
import imutils


def convertir_a_numpy(tensor):
    """
    Convierte tensores/listas a numpy array de forma segura.
    
    Args:
        tensor: Tensor de PyTorch, lista o array
        
    Returns:
        numpy.ndarray: Array numpy
    """
    try:
        return tensor.cpu().numpy()
    except Exception:
        try:
            return np.array(tensor)
        except Exception:
            return np.array([])


def redimensionar_placa(imagen_placa, ancho_minimo=64):
    """
    Redimensiona una placa si es muy pequeña para mejorar OCR.
    
    Args:
        imagen_placa (numpy.ndarray): Imagen de la placa
        ancho_minimo (int): Ancho mínimo deseado
        
    Returns:
        numpy.ndarray: Imagen redimensionada
    """
    alto, ancho = imagen_placa.shape[:2]
    
    if ancho < ancho_minimo:
        factor = ancho_minimo / ancho
        imagen_placa = imutils.resize(imagen_placa, width=ancho_minimo)
    
    return imagen_placa


def recortar_region(imagen, x1, y1, x2, y2):
    """
    Recorta una región de la imagen con validación de límites.
    
    Args:
        imagen (numpy.ndarray): Imagen fuente
        x1, y1, x2, y2 (int): Coordenadas del recorte
        
    Returns:
        numpy.ndarray: Imagen recortada
    """
    alto, ancho = imagen.shape[:2]
    
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(ancho, int(x2))
    y2 = min(alto, int(y2))
    
    return imagen[y1:y2, x1:x2]


def dibujar_deteccion(imagen, x1, y1, x2, y2, texto, confianza, color=(0, 255, 0)):
    """
    Dibuja un cuadro de detección con texto en la imagen.
    
    Args:
        imagen (numpy.ndarray): Imagen donde dibujar
        x1, y1, x2, y2 (int): Coordenadas del cuadro
        texto (str): Texto a mostrar
        confianza (float): Confianza de la detección
        color (tuple): Color BGR del cuadro
        
    Returns:
        numpy.ndarray: Imagen con la detección dibujada
    """
    # Dibujar rectángulo
    cv2.rectangle(imagen, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
    
    # Preparar etiqueta
    if texto:
        etiqueta = f"{texto} ({confianza:.2f})"
    else:
        etiqueta = f"Placa ({confianza:.2f})"
    
    # Calcular tamaño del fondo de texto
    (ancho_txt, alto_txt), _ = cv2.getTextSize(etiqueta, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
    
    # Dibujar fondo del texto
    cv2.rectangle(imagen, (int(x1), int(y1) - alto_txt - 10), 
                  (int(x1) + ancho_txt, int(y1)), color, -1)
    
    # Dibujar texto
    cv2.putText(imagen, etiqueta, (int(x1), int(y1) - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    return imagen
