# -*- coding: utf-8 -*-
"""
Detección de placas usando YOLO (best.pt) + PaddleOCR.
Uso:
  python app.py --source Inputs/image_001.jpg --model best.pt

Genera imagen(es) con los recuadros y el texto OCR en Outputs/.
"""

import os
import argparse
import re
import cv2
import imutils
import numpy as np
import sys
from ultralytics import YOLO
# PaddleOCR puede fallar si paddlepaddle no está instalado (importa 'paddle').
try:
    from paddleocr import PaddleOCR
    _PADDLE_IMPORT_ERROR = None
except Exception as e:
    PaddleOCR = None
    _PADDLE_IMPORT_ERROR = e


def _to_numpy(x):
    """Convierte tensores/listas a numpy array de forma segura."""
    try:
        return x.cpu().numpy()
    except Exception:
        try:
            return np.array(x)
        except Exception:
            return np.array([])


def sanitize_text(text):
    """Mantener solo mayúsculas y dígitos (whitelist) y quitar espacios.
    Devuelve texto en mayúsculas.
    """
    whitelist = re.compile(r"[A-Z0-9]")
    text = (text or "").upper()
    filtered = ''.join([c for c in text if whitelist.match(c)])
    return filtered


def parse_ocr_result(ocr_result):
    """Extrae una lista de tuplas (bbox, text) desde las distintas estructuras que
    PaddleOCR puede devolver. Maneja anidamientos y varios formatos.
    """
    items = []
    
    # Nuevo formato de PaddleOCR 3.3.1: lista de diccionarios con 'rec_texts'
    if isinstance(ocr_result, list) and len(ocr_result) > 0:
        if isinstance(ocr_result[0], dict) and 'rec_texts' in ocr_result[0]:
            # Formato nuevo: [{'rec_texts': ['text1', 'text2'], 'dt_polys': [...], 'rec_scores': [...]}]
            for item in ocr_result:
                texts = item.get('rec_texts', [])
                bboxes = item.get('dt_polys', [])
                for i, text in enumerate(texts):
                    bbox = bboxes[i] if i < len(bboxes) else []
                    items.append((bbox, text))
            return items

    # Formato antiguo: intentar extraer recursivamente
    def _try_extract(obj):
        # caso simple: (bbox, (text, conf)) o (bbox, text)
        if not isinstance(obj, (list, tuple)):
            return False
        if len(obj) == 2:
            a, b = obj
            # b puede ser ('text', conf) o 'text' o [ ('text', conf), ... ]
            text = None
            if isinstance(b, (list, tuple)):
                # si b es una tupla tipo (text, conf)
                if len(b) >= 1 and isinstance(b[0], str):
                    text = b[0]
            elif isinstance(b, str):
                text = b

            if text is not None:
                # a debe ser el bbox (lista de 4 puntos)
                return (a, text)

        return False

    # Recorrer recursivamente y buscar pares extraíbles
    stack = [ocr_result]
    while stack:
        cur = stack.pop()
        if cur is None:
            continue
        if isinstance(cur, (list, tuple)):
            # intentar extraer directamente
            ext = _try_extract(cur)
            if ext:
                items.append(ext)
                continue
            # si no, expandir elementos
            for el in cur:
                stack.append(el)

    # Normalizar bbox/text: bbox como lista de puntos, text como str
    normalized = []
    for bbox, txt in items:
        try:
            # bbox puede venir como array, convertir a lista
            b = [[int(p[0]), int(p[1])] for p in bbox]
        except Exception:
            b = bbox
        normalized.append((b, str(txt)))

    return normalized


def _preferred_backends():
    """Devuelve una lista de backends preferidos según la plataforma."""
    backends = []
    plat = sys.platform.lower()
    # Windows: DirectShow y MSMF suelen funcionar mejor
    if plat.startswith('win'):
        if hasattr(cv2, 'CAP_DSHOW'):
            backends.append(cv2.CAP_DSHOW)
        if hasattr(cv2, 'CAP_MSMF'):
            backends.append(cv2.CAP_MSMF)
        # Fallback
        if hasattr(cv2, 'CAP_FFMPEG'):
            backends.append(cv2.CAP_FFMPEG)
    # macOS
    elif plat.startswith('darwin'):
        if hasattr(cv2, 'CAP_AVFOUNDATION'):
            backends.append(cv2.CAP_AVFOUNDATION)
        if hasattr(cv2, 'CAP_QT'):
            backends.append(cv2.CAP_QT)
    # Linux
    else:
        if hasattr(cv2, 'CAP_V4L2'):
            backends.append(cv2.CAP_V4L2)
        if hasattr(cv2, 'CAP_FFMPEG'):
            backends.append(cv2.CAP_FFMPEG)
    return backends


def _open_camera_with_fallback(cam_index=None, max_index_search=4):
    """Intentar abrir la cámara usando el índice dado o buscando índices comunes y varios backends.

    Devuelve un objeto VideoCapture abierto o None si falla.
    """
    def try_open(idx, api=None):
        try:
            if api is None:
                cap = cv2.VideoCapture(idx)
            else:
                cap = cv2.VideoCapture(idx, api)
            if cap is not None and cap.isOpened():
                return cap
            try:
                cap.release()
            except Exception:
                pass
            return None
        except Exception:
            return None

    backends = _preferred_backends()

    # If user provided an index, try it first with preferred backends
    if cam_index is not None:
        # try raw index without api first
        cap = try_open(int(cam_index), None)
        if cap:
            return cap
        for api in backends:
            cap = try_open(int(cam_index), api)
            if cap:
                return cap

    # Try common indices 0..max_index_search
    for idx in range(0, max_index_search + 1):
        cap = try_open(idx, None)
        if cap:
            return cap
        for api in backends:
            cap = try_open(idx, api)
            if cap:
                return cap

    return None


def run_on_image(image_path, model_path, output_folder, conf_thresh=0.5, pad=15, show=False):
    """Run plate detection + OCR on an image.
    If an environment variable TRUCK_MODEL_PATH is set, the function will first run the truck
    detector and then run the plate model inside each truck crop to limit false positives.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Cargar imagen
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {image_path}")

    # Cargar modelo YOLO (placas)
    model = YOLO(model_path)

    # Cargar modelo de camiones si fue especificado via variable de entorno
    truck_model_path = os.environ.get('TRUCK_MODEL_PATH')
    truck_model = YOLO(truck_model_path) if truck_model_path else None

    # Inicializar OCR (PaddleOCR)
    if PaddleOCR is None:
        msg = (
            "PaddleOCR no está disponible porque falló la importación. "
            "Asegúrate de instalar 'paddlepaddle' y 'paddleocr'. "
            f"Import error: {_PADDLE_IMPORT_ERROR}\n\n"
            "Ejemplo (Windows CPU, en bash):\n"
            "  pip install paddlepaddle -f https://www.paddlepaddle.org.cn/whl/windows/mkl/avx/stable.html\n"
            "  pip install paddleocr\n\n"
            "Si tienes GPU, instala la variante GPU de paddlepaddle siguiendo las instrucciones en https://www.paddlepaddle.org.cn/."
        )
        raise RuntimeError(msg)

    ocr = PaddleOCR(lang='en')

    out_img = img.copy()
    found_any = False

    # Detect trucks first (if truck model provided)
    truck_boxes = []
    if truck_model is not None:
        print(f'[DEBUG] Ejecutando modelo de camiones...')
        try:
            t_results = truck_model(img)
            for tr in t_results:
                if not hasattr(tr, 'boxes'):
                    continue
                t_xyxy = _to_numpy(tr.boxes.xyxy)
                t_confs = _to_numpy(tr.boxes.conf).flatten() if hasattr(tr.boxes, 'conf') else None
                t_cls = _to_numpy(tr.boxes.cls).astype(int).flatten() if hasattr(tr.boxes, 'cls') else None
                if t_xyxy.size == 0:
                    continue
                # assume trucks class is 0 if available, otherwise take all
                if t_cls is None:
                    t_indices = range(t_xyxy.shape[0])
                else:
                    t_indices = np.where(t_cls == 0)[0]
                for ti in t_indices:
                    tc = float(t_confs[ti]) if t_confs is not None else 1.0
                    if tc < conf_thresh:
                        print(f'[DEBUG] Camión descartado (conf={tc:.3f} < {conf_thresh})')
                        continue
                    tb = t_xyxy[ti].astype(int).tolist()
                    truck_boxes.append(tb)
                    print(f'[DEBUG] Camión detectado: box={tb}, conf={tc:.3f}')
        except Exception as e:
            print('Error en inferencia del modelo de camiones:', e)
            import traceback
            traceback.print_exc()

    # Build regions to search plates: either each truck crop or whole image
    regions = []
    if truck_boxes:
        print(f'[DEBUG] {len(truck_boxes)} camiones detectados. Buscando placas en regiones de camiones.')
        h, w = img.shape[:2]
        for (x1, y1, x2, y2) in truck_boxes:
            x1p = max(0, x1 - pad)
            y1p = max(0, y1 - pad)
            x2p = min(w - 1, x2 + pad)
            y2p = min(h - 1, y2 + pad)
            regions.append((x1p, y1p, x2p, y2p))
    else:
        print(f'[DEBUG] No se detectaron camiones. Buscando placas en la imagen completa.')
        regions.append((0, 0, img.shape[1], img.shape[0]))

    # For each region run plate detector and OCR
    for ridx, (rx1, ry1, rx2, ry2) in enumerate(regions):
        print(f'[DEBUG] Procesando región {ridx}: crop size=({ry2-ry1}x{rx2-rx1})')
        crop = img[ry1:ry2, rx1:rx2]
        if crop.size == 0:
            continue
        try:
            p_results = model(crop)
        except Exception as e:
            print('Error en inferencia YOLO (placas):', e)
            import traceback
            traceback.print_exc()
            continue

        for r in p_results:
            if not hasattr(r, 'boxes'):
                continue
            xyxy = _to_numpy(r.boxes.xyxy)
            confs = _to_numpy(r.boxes.conf).flatten() if hasattr(r.boxes, 'conf') else None
            cls = _to_numpy(r.boxes.cls).astype(int).flatten() if hasattr(r.boxes, 'cls') else None
            if xyxy.size == 0:
                print(f'[DEBUG] No hay detecciones de placas en región {ridx}')
                continue

            print(f'[DEBUG] {xyxy.shape[0]} detecciones de placas en región {ridx}')

            if cls is None:
                indices = range(xyxy.shape[0])
            else:
                indices = np.where(cls == 0)[0]

            for i in indices:
                c = float(confs[i]) if confs is not None else 1.0
                if c < conf_thresh:
                    print(f'[DEBUG] Placa descartada (conf={c:.3f} < {conf_thresh})')
                    continue

                cx1, cy1, cx2, cy2 = xyxy[i].astype(int).tolist()
                x1 = rx1 + cx1
                y1 = ry1 + cy1
                x2 = rx1 + cx2
                y2 = ry1 + cy2

                print(f'[DEBUG] Placa detectada: crop_box=[{cx1},{cy1},{cx2},{cy2}], full_box=[{x1},{y1},{x2},{y2}], conf={c:.3f}')

                h, w = img.shape[:2]
                x1p = max(0, x1 - pad)
                y1p = max(0, y1 - pad)
                x2p = min(w - 1, x2 + pad)
                y2p = min(h - 1, y2 + pad)
                plate = img[y1p:y2p, x1p:x2p]
                if plate.size == 0:
                    print(f'[DEBUG] Placa crop vacío, saltando')
                    continue

                # Preprocesar placa para mejor OCR: resize si es muy pequeña
                ph, pw = plate.shape[:2]
                min_ocr_height = 64
                if ph < min_ocr_height:
                    scale = min_ocr_height / ph
                    plate_for_ocr = cv2.resize(plate, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                else:
                    plate_for_ocr = plate

                plate_rgb = cv2.cvtColor(plate_for_ocr, cv2.COLOR_BGR2RGB)
                
                output_text = ""
                ocr_confidence = 0.0
                try:
                    ocr_result = ocr.predict(plate_rgb)
                    
                    # Extraer textos y confidencias del nuevo formato de PaddleOCR 3.x
                    rec_texts = []
                    rec_scores = []
                    if isinstance(ocr_result, list) and len(ocr_result) > 0 and isinstance(ocr_result[0], dict):
                        # Formato PaddleOCR 3.x con diccionarios
                        if 'rec_texts' in ocr_result[0]:
                            rec_texts = ocr_result[0]['rec_texts']
                        if 'rec_scores' in ocr_result[0]:
                            rec_scores = ocr_result[0]['rec_scores']
                    else:
                        # Formato antiguo, usar parser
                        parsed = parse_ocr_result(ocr_result)
                        rec_texts = [t for _, t in parsed]
                    
                    # Filtrar palabras de países/regiones comunes
                    country_filters = ['GUATEMALA', 'MEXICO', 'COLOMBIA', 'PERU', 'CHILE', 'ARGENTINA', 
                                      'BRASIL', 'ECUADOR', 'BOLIVIA', 'PARAGUAY', 'URUGUAY', 'VENEZUELA',
                                      'CENTROAMERICA', 'COSTA RICA', 'PANAMA', 'HONDURAS', 'NICARAGUA',
                                      'EL SALVADOR']
                    
                    filtered_texts = []
                    filtered_scores = []
                    for idx, txt in enumerate(rec_texts):
                        txt_upper = txt.upper().strip()
                        # Filtrar si el texto es solo un país conocido
                        if txt_upper not in country_filters:
                            filtered_texts.append(txt)
                            if idx < len(rec_scores):
                                filtered_scores.append(rec_scores[idx])
                    
                    # Si no quedó nada después del filtro, usar todo
                    if not filtered_texts:
                        filtered_texts = rec_texts
                        filtered_scores = rec_scores
                    
                    # Unir textos filtrados
                    joined = ''.join(filtered_texts).upper()
                    output_text = sanitize_text(joined)
                    
                    # Calcular confianza promedio
                    if filtered_scores:
                        ocr_confidence = sum(filtered_scores) / len(filtered_scores)
                    
                    if not output_text:
                        all_chars = ''.join([ch for ch in joined if re.match(r'[A-Z0-9]', ch)])
                        output_text = all_chars
                    
                    print(f'[DEBUG] OCR texts: {rec_texts} -> filtered: {filtered_texts}, confidence: {ocr_confidence:.3f}')
                    
                except Exception as e:
                    print(f'[DEBUG] Error en OCR: {e}')
                    import traceback
                    traceback.print_exc()
                    output_text = "ERROR-OCR"
                    ocr_confidence = 0.0

                print(f'[DEBUG] OCR resultado: "{output_text}" conf={ocr_confidence:.3f} (tamaño placa: {pw}x{ph}px)')

                # Dibujar rectángulo de detección
                cv2.rectangle(out_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                
                # Preparar texto a mostrar: placa + confianza
                text_pos_x = max(5, x1 - 10)
                text_pos_y = max(30, y1 - 10)
                display_text = output_text if output_text else '---'
                confidence_text = f"{display_text} ({ocr_confidence*100:.1f}%)"
                
                # Fondo para el texto
                (tw, th), _ = cv2.getTextSize(confidence_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                cv2.rectangle(out_img, (text_pos_x - 5, text_pos_y - th - 5), (text_pos_x + tw + 5, text_pos_y + 5), (0, 255, 0), -1)
                cv2.putText(out_img, confidence_text, (text_pos_x, text_pos_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

                base_name = os.path.splitext(os.path.basename(image_path))[0]
                plate_filename = os.path.join(output_folder, f"{base_name}_plate_{ridx}_{i}.jpg")
                cv2.imwrite(plate_filename, plate)
                print(f'[DEBUG] Guardado recorte de placa: {plate_filename}')

                found_any = True

    out_name = os.path.join(output_folder, os.path.basename(image_path))
    cv2.imwrite(out_name, out_img)
    print(f'[DEBUG] Guardada imagen anotada: {out_name}')

    if show:
        try:
            cv2.imshow('Result', imutils.resize(out_img, width=900))
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception:
            print('No se pudo mostrar ventana (entorno sin GUI). Imagen guardada en:', out_name)

    return found_any, out_name


def run_batch(source, model, output, conf, pad, show):
    if os.path.isdir(source):
        files = [os.path.join(source, f) for f in os.listdir(source) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    else:
        files = [source]
    if len(files) == 0:
        print(f"No se encontraron imágenes en la carpeta: {source}")
        return

    successes = 0
    for f in files:
        try:
            ok, out = run_on_image(f, model, output, conf_thresh=conf, pad=pad, show=show)
            if ok:
                successes += 1
            print(f"Procesado: {f} -> {out} | placa encontrada: {ok}")
        except Exception as e:
            print(f"Error procesando {f}: {e}")

    print(f"Procesadas {len(files)} imágenes. Placas detectadas en {successes} imágenes.")


def run_webcam(model_path, output_folder, cam_index=0, conf_thresh=0.5, pad=15, skip_frames=3):
    """Abrir la cámara y procesar en tiempo real.

    Controles de teclado mientras la ventana está activa:
    - 'q' : salir
    - 'c' o SPACE : capturar y guardar el frame anotado en Outputs/

    Parámetros:
    - skip_frames: ejecutar inferencia una vez cada N frames para reducir carga.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Cargar modelo y OCR
    model = YOLO(model_path)
    truck_model_path = os.environ.get('TRUCK_MODEL_PATH')
    truck_model = YOLO(truck_model_path) if truck_model_path else None
    if PaddleOCR is None:
        msg = (
            "PaddleOCR no está disponible porque falló la importación. "
            "Instala 'paddlepaddle' y 'paddleocr' antes de usar la cámara."
        )
        raise RuntimeError(msg)
    ocr = PaddleOCR(lang='en')

    cap = cv2.VideoCapture(int(cam_index))
    if not cap.isOpened():
        raise RuntimeError(f"No se pudo abrir la cámara con índice {cam_index}")

    frame_id = 0
    annotated = None
    print("Cámara abierta. Presiona 'c' o SPACE para capturar, 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer frame desde la cámara")
            break

        display = frame.copy()

        # Ejecutar inferencia cada skip_frames
        if frame_id % max(1, skip_frames) == 0:
            # If truck model is provided, detect trucks first and then plates inside truck crops
            truck_boxes = []
            if truck_model is not None:
                try:
                    t_results = truck_model(frame)
                    for tr in t_results:
                        if not hasattr(tr, 'boxes'):
                            continue
                        t_xyxy = _to_numpy(tr.boxes.xyxy)
                        t_confs = _to_numpy(tr.boxes.conf).flatten() if hasattr(tr.boxes, 'conf') else None
                        t_cls = _to_numpy(tr.boxes.cls).astype(int).flatten() if hasattr(tr.boxes, 'cls') else None
                        if t_xyxy.size == 0:
                            continue
                        if t_cls is None:
                            t_indices = range(t_xyxy.shape[0])
                        else:
                            t_indices = np.where(t_cls == 0)[0]
                        for ti in t_indices:
                            tc = float(t_confs[ti]) if t_confs is not None else 1.0
                            if tc < conf_thresh:
                                continue
                            tb = t_xyxy[ti].astype(int).tolist()
                            truck_boxes.append(tb)
                except Exception as e:
                    print(f"Error inferencia modelo camiones: {e}")

            plate_regions = []
            if truck_boxes:
                h, w = frame.shape[:2]
                for (x1, y1, x2, y2) in truck_boxes:
                    x1p = max(0, x1 - pad)
                    y1p = max(0, y1 - pad)
                    x2p = min(w - 1, x2 + pad)
                    y2p = min(h - 1, y2 + pad)
                    plate_regions.append((x1p, y1p, x2p, y2p))
            else:
                plate_regions.append((0, 0, frame.shape[1], frame.shape[0]))

            # Run plate detection in each region
            for (rx1, ry1, rx2, ry2) in plate_regions:
                crop = frame[ry1:ry2, rx1:rx2]
                if crop.size == 0:
                    continue
                try:
                    p_results = model(crop)
                except Exception as e:
                    print(f"Error inferencia YOLO placas (webcam): {e}")
                    p_results = []

                for r in p_results:
                    if not hasattr(r, 'boxes'):
                        continue
                    xyxy = _to_numpy(r.boxes.xyxy)
                    confs = _to_numpy(r.boxes.conf).flatten() if hasattr(r.boxes, 'conf') else None
                    cls = _to_numpy(r.boxes.cls).astype(int).flatten() if hasattr(r.boxes, 'cls') else None
                    if xyxy.size == 0:
                        continue
                    if cls is None:
                        indices = range(xyxy.shape[0])
                    else:
                        indices = np.where(cls == 0)[0]
                    for i in indices:
                        c = float(confs[i]) if confs is not None else 1.0
                        if c < conf_thresh:
                            continue
                        cx1, cy1, cx2, cy2 = xyxy[i].astype(int).tolist()
                        x1 = rx1 + cx1
                        y1 = ry1 + cy1
                        x2 = rx1 + cx2
                        y2 = ry1 + cy2

                        plate = frame[max(0, y1 - pad):min(frame.shape[0], y2 + pad), max(0, x1 - pad):min(frame.shape[1], x2 + pad)]
                        if plate.size == 0:
                            continue

                        plate_rgb = cv2.cvtColor(plate, cv2.COLOR_BGR2RGB)
                        try:
                            ocr_result = ocr.predict(plate_rgb, cls=True)
                        except Exception:
                            try:
                                ocr_result = ocr.predict(plate_rgb)
                            except Exception:
                                ocr_result = []

                        parsed = parse_ocr_result(ocr_result)
                        parsed = sorted(parsed, key=lambda it: min([p[0] for p in it[0]]) if it[0] else 0)
                        texts = [t for _, t in parsed]
                        joined = ''.join(texts).upper()
                        output_text = sanitize_text(joined)

                        cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        text_pos_x = max(0, x1 - 10)
                        text_pos_y = max(0, y1 - 5)
                        (tw, th), _ = cv2.getTextSize(output_text or '---', cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
                        cv2.rectangle(display, (text_pos_x - 5, text_pos_y - th - 5), (text_pos_x + tw + 5, text_pos_y + 5), (0, 255, 0), -1)
                        cv2.putText(display, output_text or '---', (text_pos_x, text_pos_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

            annotated = display.copy()

        # Mostrar
        try:
            cv2.imshow('Webcam - Presiona c o SPACE para capturar, q para salir', imutils.resize(display, width=900))
        except Exception:
            cv2.imshow('Webcam', display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('c') or key == 32:  # 'c' o SPACE
            # Guardar la imagen anotada actual (si no hay anotada, guardar el frame)
            base = 'webcam_capture'
            idx = 0
            while True:
                fname = os.path.join(output_folder, f"{base}_{idx}.jpg")
                if not os.path.exists(fname):
                    break
                idx += 1
            to_save = annotated if annotated is not None else frame
            cv2.imwrite(fname, to_save)
            print(f"Captura guardada en: {fname}")

        frame_id += 1

    cap.release()
    cv2.destroyAllWindows()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detección de placas con YOLO + PaddleOCR')
    parser.add_argument('--source', '-s', required=False, default=None, help='Ruta a imagen o carpeta (ej. Inputs/image_001.jpg)')
    parser.add_argument('--model', '-m', default='best.pt', help='Ruta al modelo YOLO (ej. best.pt)')
    parser.add_argument('--output', '-o', default='Outputs', help='Carpeta de salida')
    parser.add_argument('--conf', '-c', type=float, default=0.5, help='Umbral de confianza para detecciones')
    parser.add_argument('--pad', type=int, default=15, help='Padding al recortar la placa')
    parser.add_argument('--show', action='store_true', help='Mostrar ventana con el resultado (si el entorno permite GUI)')
    parser.add_argument('--webcam', action='store_true', help='Abrir cámara en modo realtime')
    parser.add_argument('--cam-index', type=int, default=0, help='Índice de la cámara (default 0)')
    parser.add_argument('--skip-frames', type=int, default=3, help='Saltar frames entre inferencias para realtime')
    parser.add_argument('--truck-model', default=None, help='Ruta al modelo YOLO entrenado para detectar camiones (opcional)')

    args = parser.parse_args()
    if args.webcam:
        # If a truck model was provided, expose it via env var so helper functions pick it up
        if args.truck_model:
            os.environ['TRUCK_MODEL_PATH'] = args.truck_model
        run_webcam(args.model, args.output, cam_index=args.cam_index, conf_thresh=args.conf, pad=args.pad, skip_frames=args.skip_frames)
    else:
        # --source es requerido a menos que se use --webcam
        if not args.source:
            parser.error("the following arguments are required: --source/-s (use --webcam to open the camera instead)")
        if args.truck_model:
            os.environ['TRUCK_MODEL_PATH'] = args.truck_model
        run_batch(args.source, args.model, args.output, args.conf, args.pad, args.show)
