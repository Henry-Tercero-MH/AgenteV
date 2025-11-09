"""
Script de diagnóstico avanzado para analizar por qué una placa no se reconoce
"""
import cv2
import numpy as np
from paddleocr import PaddleOCR
import argparse

def preprocess_plate(img):
    """Aplica diferentes preprocesos a la imagen de la placa"""
    results = {}
    
    # Original
    results['original'] = img.copy()
    
    # Upscale agresivo (4x)
    h, w = img.shape[:2]
    upscaled_4x = cv2.resize(img, (w*4, h*4), interpolation=cv2.INTER_CUBIC)
    results['upscaled_4x'] = upscaled_4x
    
    # Upscale 6x
    upscaled_6x = cv2.resize(img, (w*6, h*6), interpolation=cv2.INTER_CUBIC)
    results['upscaled_6x'] = upscaled_6x
    
    # Escala de grises + binarización adaptativa
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY, 11, 2)
    binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    results['binary'] = binary_bgr
    
    # Upscale del binario
    binary_up = cv2.resize(binary_bgr, (w*4, h*4), interpolation=cv2.INTER_CUBIC)
    results['binary_upscaled'] = binary_up
    
    # Contraste mejorado (CLAHE)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    results['clahe'] = enhanced_bgr
    
    # CLAHE upscaled
    clahe_up = cv2.resize(enhanced_bgr, (w*4, h*4), interpolation=cv2.INTER_CUBIC)
    results['clahe_upscaled'] = clahe_up
    
    # Sharpening
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(img, -1, kernel)
    results['sharpened'] = sharpened
    
    # Sharpened upscaled
    sharp_up = cv2.resize(sharpened, (w*4, h*4), interpolation=cv2.INTER_CUBIC)
    results['sharpened_upscaled'] = sharp_up
    
    # Denoising + upscale
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    denoised_up = cv2.resize(denoised, (w*4, h*4), interpolation=cv2.INTER_CUBIC)
    results['denoised_upscaled'] = denoised_up
    
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plate-crop', required=True, help='Ruta al recorte de la placa')
    parser.add_argument('--output-dir', default='Outputs/analysis', help='Directorio para guardar análisis')
    args = parser.parse_args()
    
    # Cargar imagen
    img = cv2.imread(args.plate_crop)
    if img is None:
        print(f"❌ No se pudo cargar: {args.plate_crop}")
        return
    
    print(f"📸 Imagen cargada: {img.shape[1]}x{img.shape[0]}px")
    
    # Inicializar OCR
    print("🔧 Inicializando PaddleOCR...")
    ocr = PaddleOCR(use_textline_orientation=True, lang='en', device='cpu')
    
    # Aplicar preprocesos
    print("\n🔍 Probando diferentes preprocesos...\n")
    preprocessed = preprocess_plate(img)
    
    # Crear directorio de salida
    import os
    os.makedirs(args.output_dir, exist_ok=True)
    
    results_summary = []
    
    for name, proc_img in preprocessed.items():
        print(f"➤ Procesando: {name} ({proc_img.shape[1]}x{proc_img.shape[0]}px)")
        
        # Guardar imagen procesada
        output_path = os.path.join(args.output_dir, f"{name}.jpg")
        cv2.imwrite(output_path, proc_img)
        
        # Ejecutar OCR
        try:
            ocr_result = ocr.predict(proc_img)
            
            if ocr_result and ocr_result[0]:
                data = ocr_result[0]
                
                # Extraer textos y confianzas
                if isinstance(data, dict) and 'rec_texts' in data:
                    rec_texts = data['rec_texts']
                    rec_scores = data.get('rec_scores', [])
                elif isinstance(data, list):
                    rec_texts = [line[1][0] if len(line) > 1 else '' for line in data]
                    rec_scores = [line[1][1] if len(line) > 1 else 0.0 for line in data]
                else:
                    rec_texts = []
                    rec_scores = []
                
                if rec_texts:
                    avg_conf = sum(rec_scores) / len(rec_scores) if rec_scores else 0.0
                    text_result = ' '.join(rec_texts)
                    print(f"   ✅ Texto: '{text_result}' (conf: {avg_conf:.3f})")
                    results_summary.append({
                        'method': name,
                        'text': text_result,
                        'confidence': avg_conf,
                        'size': f"{proc_img.shape[1]}x{proc_img.shape[0]}"
                    })
                else:
                    print(f"   ⚠️  OCR no encontró texto")
            else:
                print(f"   ⚠️  OCR no encontró texto")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Mostrar resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*70)
    
    if results_summary:
        # Ordenar por confianza
        results_summary.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"\n{'Método':<25} {'Tamaño':<15} {'Confianza':<12} {'Texto'}")
        print("-"*70)
        for r in results_summary:
            print(f"{r['method']:<25} {r['size']:<15} {r['confidence']:<12.1%} {r['text']}")
        
        print(f"\n🏆 MEJOR RESULTADO: {results_summary[0]['method']}")
        print(f"   Texto: '{results_summary[0]['text']}'")
        print(f"   Confianza: {results_summary[0]['confidence']:.1%}")
    else:
        print("\n❌ Ningún método pudo extraer texto de la placa")
        print("\nPosibles causas:")
        print("  • La placa está muy borrosa o pixelada")
        print("  • El ángulo es demasiado pronunciado")
        print("  • El contraste es insuficiente")
        print("  • El texto es demasiado pequeño incluso después del upscaling")
    
    print(f"\n💾 Imágenes procesadas guardadas en: {args.output_dir}/")

if __name__ == '__main__':
    main()
