"""
OCR Wrapper - Usa PaddleOCR desde Python 3.13 via subprocess
Este wrapper permite usar Python 3.14 para todo excepto OCR
"""
import subprocess
import json
import sys
import os
from pathlib import Path

# Ruta al Python 3.13 con PaddleOCR
PYTHON313_PATH = Path(__file__).parent / "venv_old_3.13" / "Scripts" / "python.exe"

def run_ocr_via_subprocess(image_path):
    """
    Ejecuta OCR usando PaddleOCR desde el venv de Python 3.13
    
    Args:
        image_path: Ruta a la imagen o array de numpy
        
    Returns:
        Lista de textos detectados y confianzas
    """
    if not PYTHON313_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró Python 3.13 en: {PYTHON313_PATH}\n"
            f"El venv antiguo debe estar en: {PYTHON313_PATH.parent.parent}"
        )
    
    # Script para ejecutar OCR
    ocr_script = f"""
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
    print(json.dumps({{'error': 'No se pudo cargar la imagen'}}))
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
    result = {{
        'texts': rec_texts,
        'scores': rec_scores
    }}
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({{'error': str(e)}}))
    sys.exit(1)
"""
    
    # Guardar script temporal
    script_path = Path(__file__).parent / "temp_ocr_script.py"
    script_path.write_text(ocr_script)
    
    try:
        # Ejecutar script con Python 3.13 (timeout más largo por carga inicial de PaddleOCR)
        result = subprocess.run(
            [str(PYTHON313_PATH), str(script_path), str(image_path)],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutos para la primera carga
        )
        
        if result.returncode != 0:
            print(f"[ERROR OCR] stderr: {result.stderr}")
            return [], []
        
        # Parsear resultado JSON
        try:
            data = json.loads(result.stdout.strip())
            if 'error' in data:
                print(f"[ERROR OCR] {data['error']}")
                return [], []
            return data.get('texts', []), data.get('scores', [])
        except json.JSONDecodeError as e:
            print(f"[ERROR OCR] JSON decode error: {e}")
            print(f"[ERROR OCR] stdout: {result.stdout}")
            return [], []
            
    finally:
        # Limpiar script temporal
        if script_path.exists():
            script_path.unlink()


class OCRWrapper:
    """
    Wrapper compatible con la interfaz de PaddleOCR
    """
    def __init__(self, **kwargs):
        """Inicializa el wrapper (no hace nada, usa subprocess)"""
        if not PYTHON313_PATH.exists():
            print(f"⚠️  ADVERTENCIA: Python 3.13 no encontrado en {PYTHON313_PATH}")
            print(f"⚠️  El OCR no funcionará. Por favor verifica que venv_old_3.13 existe.")
    
    def predict(self, img):
        """
        Ejecuta OCR en una imagen
        
        Args:
            img: Puede ser ruta de archivo (str) o array de numpy
            
        Returns:
            Lista compatible con PaddleOCR format
        """
        import cv2
        import tempfile
        
        # Si es array de numpy, guardar temporalmente
        if hasattr(img, 'shape'):  # numpy array
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                temp_path = f.name
                success = cv2.imwrite(temp_path, img)
                if not success:
                    print(f"[ERROR OCR] No se pudo guardar imagen temporal: {temp_path}")
                    return [[]]
            
            try:
                texts, scores = run_ocr_via_subprocess(temp_path)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            # Es una ruta de archivo
            texts, scores = run_ocr_via_subprocess(img)
        
        # Retornar en formato compatible con PaddleOCR
        if not texts:
            return [[]]
        
        result = [[{
            'rec_texts': texts,
            'rec_scores': scores
        }]]
        return result


# Para compatibilidad, exportar como PaddleOCR
PaddleOCR = OCRWrapper


if __name__ == '__main__':
    # Test del wrapper
    print("🧪 Testing OCR Wrapper...")
    print(f"📍 Python 3.13 path: {PYTHON313_PATH}")
    print(f"✓ Exists: {PYTHON313_PATH.exists()}")
    
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
        print(f"\n🖼️  Testing with image: {test_image}")
        
        ocr = OCRWrapper()
        result = ocr.predict(test_image)
        
        print(f"\n📊 Results:")
        print(json.dumps(result, indent=2))
