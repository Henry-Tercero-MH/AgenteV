# -*- coding: utf-8 -*-
"""
Configuración centralizada del sistema de detección de placas
"""

# Carpetas del proyecto
CARPETA_SALIDA = 'Outputs'
CARPETA_ENTRADA = 'Inputs'

# Modelos por defecto
MODELO_PLACAS_DEFAULT = 'best.pt'
MODELO_CAMIONES_DEFAULT = 'best_truck.pt'

# Parámetros de detección
UMBRAL_CONFIANZA_DEFAULT = 0.5
PADDING_RECORTE = 15

# Parámetros de OCR
IDIOMA_OCR = 'en'
USAR_CLASIFICADOR_ANGULO = True

# Parámetros de video/webcam
SKIP_FRAMES_DEFAULT = 3
INDICE_CAMARA_DEFAULT = 0

# Validación de placas
LONGITUD_MIN_PLACA = 4
LONGITUD_MAX_PLACA = 10
DIGITOS_MIN_PLACA_ANTIGUA = 5

# Palabras clave para filtrar (países/regiones)
PALABRAS_CLAVE_PAIS = [
    'GUATEMALA', 'MEXICO', 'CENTRO', 'AMÉRICA', 'AMERICA'
]
