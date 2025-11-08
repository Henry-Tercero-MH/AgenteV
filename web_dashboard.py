# -*- coding: utf-8 -*-
"""
Dashboard web para elegir cámara, ver video en vivo y capturar imágenes con detección (YOLO + PaddleOCR).

Uso:
  python web_dashboard.py --model best.pt --host 0.0.0.0 --port 5000

Interfaz:
- Dropdown para seleccionar cámara disponible (se prueban índices 0..6)
- Checkbox para activar detección en tiempo real (ejecuta detección cada N frames)
- Botón Capturar para guardar el frame anotado en Outputs/

Notas:
- Para detección en tiempo real es recomendable usar GPU y reducir la tasa de inferencia (skip_frames).
- Requiere Flask: pip install flask
"""

import os
import io
import sys
import time
import threading
import argparse
from datetime import datetime
from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import csv
import json
from datetime import datetime as _dt
import time

# Import YOLO and PaddleOCR (manejo similar al app.py)
try:
    from ultralytics import YOLO
except Exception as e:
    YOLO = None
    _YOLO_IMPORT_ERROR = e

# PaddleOCR will be imported lazily to avoid startup issues
PaddleOCR = None
_PADDLE_IMPORT_ERROR = None

# Config
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'Outputs')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)

# State shared across requests
STATE = {
    'camera_index': 0,
    'cap': None,
    'cap_lock': threading.Lock(),
    'detect': False,
    'skip_frames': 3,
    'model': None,
    'ocr': None,
    'frame_id': 0,
    'last_matches': {},  # plate -> last timestamp saved
    'current_plate': '',
    'current_status': 'IDLE',  # IDLE | NO_PLATE | INVALID | VALID
    'last_saved': None,
}


def list_available_cameras(max_index=6):
    """Probar índices 0..max_index y devolver los que se abren correctamente."""
    available = []
    for i in range(0, max_index + 1):
        cap = cv2.VideoCapture(i)
        if cap is None:
            continue
        ret, _ = cap.read()
        try:
            cap.release()
        except Exception:
            pass
        if ret:
            available.append(i)
    return available


def annotate_frame(frame):
    """Procesar un frame: detectar placas, ejecutar OCR, anotar y devolver (frame_anotado, detections).
    También actualiza STATE['current_plate'] y STATE['current_status'] y guarda auto-matches.
    """
    detections = []
    if not STATE['detect']:
        STATE['current_plate'] = ''
        STATE['current_status'] = 'IDLE'
        return frame, detections

    model = STATE.get('model')
    ocr = STATE.get('ocr')
    out = frame.copy()

    # To reduce CPU load, run inference on a resized copy (max dim controlled by STATE['infer_max_dim'])
    max_dim = STATE.get('infer_max_dim', 640)
    h, w = frame.shape[:2]
    scale = 1.0
    if max(h, w) > max_dim and max_dim > 0:
        scale = float(max_dim) / float(max(h, w))
    if scale != 1.0:
        small = cv2.resize(frame, (int(w * scale), int(h * scale)))
    else:
        small = frame

    # Si no hay modelo/ocr, no realizamos inferencia, retornamos frame
    if model is None:
        STATE['current_plate'] = ''
        STATE['current_status'] = 'NO_MODEL'
        return out, detections

    # Prepare plate detection sources: if a truck model is loaded, detect trucks first and
    # then only run plate detection inside each truck crop (on the downscaled 'small' image).
    p_results_sources = []  # list of tuples (p_results, plate_base_x, plate_base_y)
    truck_model = STATE.get('truck_model')
    try:
        if truck_model is not None:
            try:
                t_results = truck_model(small)
            except Exception as e:
                print('Error en inferencia del modelo de camiones:', e)
                t_results = []

            truck_boxes_small = []
            for tr in t_results:
                if not hasattr(tr, 'boxes'):
                    continue
                try:
                    t_xyxy = tr.boxes.xyxy.cpu().numpy() if hasattr(tr.boxes, 'xyxy') else np.array(tr.boxes.xyxy)
                    t_confs = tr.boxes.conf.cpu().numpy().flatten() if hasattr(tr.boxes, 'conf') else None
                    t_cls = tr.boxes.cls.cpu().numpy().astype(int).flatten() if hasattr(tr.boxes, 'cls') else None
                except Exception:
                    try:
                        t_xyxy = np.array(tr.boxes.xyxy)
                        t_confs = np.array(tr.boxes.conf).flatten() if hasattr(tr.boxes, 'conf') else None
                        t_cls = np.array(tr.boxes.cls).astype(int).flatten() if hasattr(tr.boxes, 'cls') else None
                    except Exception:
                        continue
                if t_xyxy is None or t_xyxy.size == 0:
                    continue
                t_indices = np.where(t_cls == 0)[0] if t_cls is not None else range(t_xyxy.shape[0])
                for ti in t_indices:
                    tc = float(t_confs[ti]) if t_confs is not None else 1.0
                    if tc < 0.3:
                        continue
                    tx1, ty1, tx2, ty2 = t_xyxy[ti].astype(int).tolist()
                    truck_boxes_small.append((tx1, ty1, tx2, ty2))

            for (tx1, ty1, tx2, ty2) in truck_boxes_small:
                try:
                    crop_small = small[ty1:ty2, tx1:tx2]
                    if crop_small.size == 0:
                        continue
                    p_results = model(crop_small)
                    p_results_sources.append((p_results, tx1, ty1))
                except Exception as e:
                    print('Error al ejecutar modelo de placas en crop:', e)
                    continue
        else:
            # no truck model: run plate model on full small image
            p_results = model(small)
            p_results_sources.append((p_results, 0, 0))
    except Exception as e:
        print('Error en inferencia combinada:', e)
        return out, detections

    # Iterate over all plate detection result sources (either whole image or crops)
    for (p_results, base_x, base_y) in p_results_sources:
        for r in p_results:
            if not hasattr(r, 'boxes'):
                continue
            try:
                xyxy = r.boxes.xyxy.cpu().numpy() if hasattr(r.boxes, 'xyxy') else None
                confs = r.boxes.conf.cpu().numpy().flatten() if hasattr(r.boxes, 'conf') else None
                cls = r.boxes.cls.cpu().numpy().astype(int).flatten() if hasattr(r.boxes, 'cls') else None
            except Exception:
                try:
                    xyxy = np.array(r.boxes.xyxy)
                    confs = np.array(r.boxes.conf).flatten() if hasattr(r.boxes, 'conf') else None
                    cls = np.array(r.boxes.cls).astype(int).flatten() if hasattr(r.boxes, 'cls') else None
                except Exception:
                    continue

            if xyxy is None or xyxy.size == 0:
                continue
            indices = np.where(cls == 0)[0] if cls is not None else range(xyxy.shape[0])
            for i in indices:
                try:
                    c = float(confs[i]) if confs is not None else 1.0
                except Exception:
                    c = 1.0
                if c < 0.3:
                    continue
                # coords are relative to the small image or crop; add base offsets then map to original frame
                if scale != 1.0:
                    coords_small = xyxy[i].astype(float)
                    coords_with_base = coords_small + np.array([base_x, base_y, base_x, base_y], dtype=float)
                    coords = (coords_with_base / scale).astype(int)
                else:
                    coords = (xyxy[i].astype(int) + np.array([base_x, base_y, base_x, base_y])).astype(int)
                x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                h, w = frame.shape[:2]
                pad = 10
                x1p = max(0, x1 - pad)
                y1p = max(0, y1 - pad)
                x2p = min(w - 1, x2 + pad)
                y2p = min(h - 1, y2 + pad)
                plate = frame[y1p:y2p, x1p:x2p]

                text = ''
                ocr_confidence = 0.0
                if plate.size != 0 and ocr is not None:
                    try:
                        # Resize plate if too small for better OCR
                        ph, pw = plate.shape[:2]
                        min_ocr_height = 64
                        if ph < min_ocr_height:
                            scale_ocr = min_ocr_height / ph
                            plate_for_ocr = cv2.resize(plate, None, fx=scale_ocr, fy=scale_ocr, interpolation=cv2.INTER_CUBIC)
                        else:
                            plate_for_ocr = plate
                        
                        plate_rgb = cv2.cvtColor(plate_for_ocr, cv2.COLOR_BGR2RGB)
                        ocr_res = ocr.predict(plate_rgb)
                        
                        # Extraer textos y confidencias del nuevo formato de PaddleOCR 3.x
                        rec_texts = []
                        rec_scores = []
                        if isinstance(ocr_res, list) and len(ocr_res) > 0 and isinstance(ocr_res[0], dict):
                            # Formato PaddleOCR 3.x con diccionarios
                            if 'rec_texts' in ocr_res[0]:
                                rec_texts = ocr_res[0]['rec_texts']
                            if 'rec_scores' in ocr_res[0]:
                                rec_scores = ocr_res[0]['rec_scores']
                        else:
                            # Formato antiguo
                            parsed = []
                            for item in ocr_res:
                                if isinstance(item, (list, tuple)):
                                    for el in item:
                                        if isinstance(el, (list, tuple)) and len(el) >= 2:
                                            rec = el[1]
                                            txt = rec[0] if isinstance(rec, (list, tuple)) else rec
                                            parsed.append(txt)
                                else:
                                    if isinstance(item, (list, tuple)) and len(item) >= 2:
                                        rec = item[1]
                                        txt = rec[0] if isinstance(rec, (list, tuple)) else rec
                                        parsed.append(txt)
                            rec_texts = parsed
                        
                        # Filtrar palabras de países/regiones comunes
                        country_filters = ['GUATEMALA', 'MEXICO', 'COLOMBIA', 'PERU', 'CHILE', 'ARGENTINA', 
                                          'BRASIL', 'ECUADOR', 'BOLIVIA', 'PARAGUAY', 'URUGUAY', 'VENEZUELA',
                                          'CENTROAMERICA', 'COSTA RICA', 'PANAMA', 'HONDURAS', 'NICARAGUA',
                                          'EL SALVADOR']
                        
                        filtered_texts = []
                        filtered_scores = []
                        for idx, txt in enumerate(rec_texts):
                            txt_upper = txt.upper().strip()
                            if txt_upper not in country_filters:
                                filtered_texts.append(txt)
                                if idx < len(rec_scores):
                                    filtered_scores.append(rec_scores[idx])
                        
                        # Si no quedó nada después del filtro, usar todo
                        if not filtered_texts:
                            filtered_texts = rec_texts
                            filtered_scores = rec_scores
                        
                        text = ''.join(filtered_texts).upper()
                        
                        # Calcular confianza promedio
                        if filtered_scores:
                            ocr_confidence = sum(filtered_scores) / len(filtered_scores)
                        
                    except Exception as e:
                        text = ''
                        ocr_confidence = 0.0

                try:
                    text_clean = ''.join([c for c in (text or '').upper() if c.isalnum()])
                except Exception:
                    text_clean = ''

                # Draw detection box and text with timestamp and confidence
                cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 3)
                display_text = text_clean if text_clean else '---'
                timestamp = datetime.now().strftime('%H:%M:%S')
                confidence_pct = f"{ocr_confidence*100:.0f}%" if ocr_confidence > 0 else ""
                full_text = f"{display_text} {confidence_pct} [{timestamp}]"
                
                # Background for text
                text_pos_x = max(5, x1 - 5)
                text_pos_y = max(25, y1 - 10)
                (tw, th), _ = cv2.getTextSize(full_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                cv2.rectangle(out, (text_pos_x - 5, text_pos_y - th - 5), (text_pos_x + tw + 5, text_pos_y + 5), (0, 255, 0), -1)
                cv2.putText(out, full_text, (text_pos_x, text_pos_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
            det = {'box': [int(x1), int(y1), int(x2), int(y2)], 'text': text_clean, 'conf': c}
            detections.append(det)

            # actualizar estado en tiempo real
            known = STATE.get('known_plates', set())
            if text_clean:
                if text_clean in known:
                    STATE['current_plate'] = text_clean
                    STATE['current_status'] = 'VALID'
                    matched_plate = text_clean
                else:
                    STATE['current_plate'] = text_clean
                    STATE['current_status'] = 'INVALID'
                    matched_plate = None
            else:
                STATE['current_plate'] = ''
                STATE['current_status'] = 'NO_PLATE'
                matched_plate = None

            # auto-save if matched and cooldown passed
            if matched_plate:
                now = time.time()
                last = STATE['last_matches'].get(matched_plate, 0)
                MATCH_COOLDOWN = 10.0
                if now - last > MATCH_COOLDOWN:
                    try:
                        ts = _dt.now().strftime('%Y%m%d_%H%M%S')
                        fname = os.path.join(OUTPUT_FOLDER, f'auto_match_{matched_plate}_{ts}.jpg')
                        cv2.imwrite(fname, out)
                        csv_path = os.path.join(OUTPUT_FOLDER, 'captures.csv')
                        header = ['timestamp', 'file', 'detections_json', 'matched_plate']
                        row = [ts, fname, json.dumps(detections, ensure_ascii=False), matched_plate]
                        write_header = not os.path.exists(csv_path)
                        with open(csv_path, 'a', encoding='utf-8', newline='') as fh:
                            writer = csv.writer(fh)
                            if write_header:
                                writer.writerow(header)
                            writer.writerow(row)
                        STATE['last_matches'][matched_plate] = now
                        print(f"Auto-match guardado: {fname} -> placa {matched_plate}")
                        # store last saved file
                        STATE['last_saved'] = fname
                    except Exception as e:
                        print('Error guardando auto-match:', e)

    # Add general timestamp overlay to frame
    timestamp_general = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(out, timestamp_general, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    
    return out, detections


def get_capture():
    with STATE['cap_lock']:
        cap = STATE.get('cap')
        if cap is None or not cap.isOpened():
            idx = STATE.get('camera_index', 0)
            # if camera_index is a string (rtsp/http url), open it directly
            try:
                if isinstance(idx, str) and (idx.startswith('rtsp://') or idx.startswith('http://') or idx.startswith('rtmp://')):
                    cap = cv2.VideoCapture(idx)
                else:
                    cap = cv2.VideoCapture(int(idx))
            except Exception:
                # fallback: try to open as index
                try:
                    cap = cv2.VideoCapture(int(idx))
                except Exception:
                    cap = cv2.VideoCapture(0)
            STATE['cap'] = cap
        return STATE['cap']


def close_capture():
    with STATE['cap_lock']:
        cap = STATE.get('cap')
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass
        STATE['cap'] = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list_cameras')
def route_list_cameras():
    # If a remote camera (RTSP/HTTP) was forced via args, only expose that
    cam_idx = STATE.get('camera_index')
    if isinstance(cam_idx, str) and (cam_idx.startswith('rtsp://') or cam_idx.startswith('http://') or cam_idx.startswith('rtmp://')):
        return jsonify({'cameras': [cam_idx]})
    cams = list_available_cameras(max_index=6)
    return jsonify({'cameras': cams})


@app.route('/set_camera', methods=['POST'])
def route_set_camera():
    data = request.json or {}
    idx = data.get('index', 0)
    # allow setting a URL (rtsp/http) or numeric index
    try:
        if isinstance(idx, str) and (idx.startswith('rtsp://') or idx.startswith('http://') or idx.startswith('rtmp://')):
            STATE['camera_index'] = idx
        else:
            # try numeric conversion
            STATE['camera_index'] = int(idx)
    except Exception:
        STATE['camera_index'] = idx
    close_capture()
    return jsonify({'ok': True, 'camera': idx})


@app.route('/set_detect', methods=['POST'])
def route_set_detect():
    data = request.json or {}
    detect = bool(data.get('detect', False))
    skip = int(data.get('skip_frames', 3))
    STATE['detect'] = detect
    STATE['skip_frames'] = max(1, skip)
    return jsonify({'ok': True, 'detect': detect, 'skip_frames': STATE['skip_frames']})


@app.route('/capture', methods=['POST'])
def route_capture():
    # capture one frame, run detection and save annotated image + return metadata
    cap = get_capture()
    ret, frame = cap.read()
    if not ret:
        return jsonify({'ok': False, 'error': 'No se pudo leer frame'}), 500
    STATE['frame_id'] += 1
    annotated, detections = annotate_frame(frame)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    fname = os.path.join(OUTPUT_FOLDER, f'capture_{ts}.jpg')
    cv2.imwrite(fname, annotated)
    # Guardar metadata en CSV
    csv_path = os.path.join(OUTPUT_FOLDER, 'captures.csv')
    header = ['timestamp', 'file', 'detections_json']
    row = [ts, fname, json.dumps(detections, ensure_ascii=False)]
    try:
        write_header = not os.path.exists(csv_path)
        with open(csv_path, 'a', encoding='utf-8', newline='') as fh:
            writer = csv.writer(fh)
            if write_header:
                writer.writerow(header)
            writer.writerow(row)
    except Exception as e:
        print('Error guardando CSV:', e)

    return jsonify({'ok': True, 'file': fname, 'detections': detections, 'csv': csv_path})


def gen_frames():
    while True:
        cap = get_capture()
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.1)
            continue
        STATE['frame_id'] += 1
        annotated, _ = annotate_frame(frame)
        # encode
        ret2, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def route_status():
    """Devuelve la placa actual y su estado: { current_plate, current_status }"""
    return jsonify({
        'current_plate': STATE.get('current_plate', ''),
        'current_status': STATE.get('current_status', 'IDLE')
    })


@app.route('/last_result')
def route_last_result():
    """Devuelve información de la última captura automática guardada (si existe)."""
    return jsonify({
        'last_saved': STATE.get('last_saved'),
        'last_matches': STATE.get('last_matches', {})
    })


def load_models(model_path, device='cpu', infer_max_dim=640):
    """Carga el modelo YOLO y PaddleOCR. Para máquinas sin GPU se recomienda pasar device='cpu'.
    infer_max_dim controla la dimensión máxima usada para inferencia (reduce carga en CPU).
    """
    if YOLO is None:
        print('Warning: ultralytics YOLO no está disponible:', _YOLO_IMPORT_ERROR)
        return
    try:
        # Load model
        STATE['model'] = YOLO(model_path)
        # Force device to CPU if requested (helps en máquinas sin GPU)
        if device and str(device).lower() == 'cpu':
            try:
                STATE['model'].to('cpu')
            except Exception:
                # model.to may not be supported for all ultralytics versions; ignore if fails
                pass
        else:
            try:
                STATE['model'].to(device)
            except Exception:
                pass
    except Exception as e:
        print('Error cargando modelo YOLO:', e)
        STATE['model'] = None

    # Lazy import OCR Wrapper (uses PaddleOCR from Python 3.13)
    global PaddleOCR, _PADDLE_IMPORT_ERROR
    if PaddleOCR is None:
        print('INFO: Intentando cargar OCR Wrapper...')
        try:
            from ocr_wrapper import PaddleOCR as PaddleOCR_class
            PaddleOCR = PaddleOCR_class
            print('INFO: OCR Wrapper cargado exitosamente (usando Python 3.13)')
        except Exception as e:
            _PADDLE_IMPORT_ERROR = e
            print('WARNING: OCR Wrapper no está disponible. El OCR no funcionará, pero la detección YOLO sí:', str(e)[:100])
            STATE['ocr'] = None
            STATE['infer_max_dim'] = int(infer_max_dim) if infer_max_dim else 640
            return
    
    try:
        print('INFO: Inicializando OCR...')
        # Simplified OCR initialization
        STATE['ocr'] = PaddleOCR(lang='en')
        print('INFO: PaddleOCR inicializado')
    except Exception as e:
        print('Error inicializando PaddleOCR:', e)
        STATE['ocr'] = None

    # Store inference size guidance in STATE
    STATE['infer_max_dim'] = int(infer_max_dim) if infer_max_dim else 640


def load_known_plates(path='known_plates.json'):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    STATE['known_plates'] = set([str(x).upper() for x in data])
                    print(f"Cargadas {len(STATE['known_plates'])} placas conocidas desde {path}")
                    return
    except Exception as e:
        print('Error cargando known_plates.json:', e)
    STATE['known_plates'] = set()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='best.pt')
    parser.add_argument('--truck-model', default=None, help='Ruta al modelo YOLO entrenado para detectar camiones (opcional)')
    # Use localhost by default on Windows to avoid socket permission issues
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--device', default='cpu', help='Device to run inference on: cpu or cuda:0 etc. Default: cpu')
    parser.add_argument('--infer-max-dim', type=int, default=640, help='Maximum image dimension for inference (scales down large frames to this max).')
    parser.add_argument('--skip-frames', type=int, default=3)
    parser.add_argument('--hikvision-url', default=None, help='IP or RTSP base for Hikvision camera (e.g. 10.10.7.64 or full rtsp://... )')
    parser.add_argument('--hikvision-user', default=None, help='Hikvision username')
    parser.add_argument('--hikvision-pass', default=None, help='Hikvision password')
    args = parser.parse_args()

    if os.path.exists(args.model):
        load_models(args.model, device=args.device, infer_max_dim=args.infer_max_dim)
    else:
        print('Modelo no encontrado; la detección estará deshabilitada hasta que proveas best.pt')

    # Cargar modelo de camiones opcional si se pasó por CLI
    if args.truck_model:
        try:
            STATE['truck_model'] = YOLO(args.truck_model)
            if args.device and str(args.device).lower() == 'cpu':
                try:
                    STATE['truck_model'].to('cpu')
                except Exception:
                    pass
            print(f"Modelo de camiones cargado: {args.truck_model}")
        except Exception as e:
            print('No se pudo cargar el modelo de camiones:', e)

    # If running on CPU, bump the default skip_frames to reduce CPU load unless user explicitly set higher
    if str(args.device).lower() == 'cpu' and args.skip_frames < 10:
        print('Ejecutando en CPU: ajustando skip_frames a 10 para reducir la carga de inferencia y mejorar fluidez del video.')
        args.skip_frames = 10
    STATE['skip_frames'] = max(1, args.skip_frames)

    # Cargar lista de placas conocidas (simulada DB)
    load_known_plates('known_plates.json')

    # If user provided Hikvision args, build an RTSP URL and use it as camera source
    # In this case we DO NOT probe local PC cameras and only expose the provided remote camera.
    if args.hikvision_url:
        hv = args.hikvision_url.strip()
        if hv.startswith('rtsp://') or hv.startswith('http://'):
            rtsp_url = hv
        else:
            user = args.hikvision_user or ''
            pwd = args.hikvision_pass or ''
            # Common Hikvision RTSP path for main stream channel 1. Adjust if your camera uses another channel/path.
            rtsp_url = f"rtsp://{user}:{pwd}@{hv}:554/Streaming/Channels/101"
        STATE['camera_index'] = rtsp_url
        # Mark that we're using a remote camera so UI and routes can adapt
        STATE['using_remote_camera'] = True
        print(f"Usando cámara Hikvision RTSP: {rtsp_url}")
    else:
        # Detectar cámaras disponibles localmente y seleccionar la primera como cámara por defecto
        try:
            cams = list_available_cameras(max_index=6)
            if cams:
                STATE['camera_index'] = cams[0]
                print(f"Cámara por defecto detectada y seteada al índice {cams[0]}")
            else:
                print('No se detectaron cámaras al iniciar la dashboard; usa el dropdown para reconectar.')
        except Exception as e:
            print('Error al detectar cámaras automáticamente:', e)

    # Try to bind to the requested port; if that fails (permission/port in use),
    # try the next ports up to +10 and print helpful messages.
    start_port = int(args.port)
    max_tries = 11
    bound = False
    for offset in range(max_tries):
        port_try = start_port + offset
        try:
            print(f"Intentando abrir servidor en {args.host}:{port_try} ...")
            app.run(host=args.host, port=port_try, threaded=True)
            bound = True
            break
        except OSError as e:
            # Permission error or address in use
            print(f"No se pudo enlazar en {args.host}:{port_try} -> {e}")
            # try next port
            continue
        except Exception as e:
            print(f"Error arrancando servidor en {args.host}:{port_try}: {e}")
            continue

    if not bound:
        print(f"Fallo al enlazar en puertos {start_port}..{start_port+max_tries-1}. Prueba ejecutar con otro puerto o con privilegios administrativos.")
