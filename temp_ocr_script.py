
import sys
import cv2
import numpy as np
from paddleocr import PaddleOCR
import json

# Inicializar OCR
ocr = PaddleOCR(use_textline_orientation=True, lang='en', device='cpu')

# Leer imagen
img_path = sys.argv[1]
img = cv2.imread(img_path)

if img is None:
    print(json.dumps({'error': 'No se pudo cargar la imagen'}))
    sys.exit(1)

# Ejecutar OCR
try:
    ocr_result = ocr.predict(img)
    
    # Extraer textos y confianzas
    rec_texts = []
    rec_scores = []
    
    if ocr_result and ocr_result[0]:
        data = ocr_result[0]
        if isinstance(data, dict) and 'rec_texts' in data:
            rec_texts = data['rec_texts']
            rec_scores = data.get('rec_scores', [])
        elif isinstance(data, list):
            for line in data:
                if len(line) > 1:
                    rec_texts.append(line[1][0] if line[1] else '')
                    rec_scores.append(line[1][1] if len(line[1]) > 1 else 0.0)
    
    # Retornar resultado en JSON
    result = {
        'texts': rec_texts,
        'scores': rec_scores
    }
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({'error': str(e)}))
    sys.exit(1)
