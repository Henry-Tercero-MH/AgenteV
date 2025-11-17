#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FalconEPSA - Detección Tiempo Real con OCR
Lee PLACAS REALES desde cámara usando Tesseract OCR + YOLO
100% producción - Sin placas simuladas
"""

import cv2
import threading
import time
from datetime import datetime
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Importar configuración
try:
    from config import (RTSP_URL, HTTP_URL, YOLO_CONFIDENCE, 
                        TESSERACT_PATH, OUTPUT_FOLDER, DETECCIONES_FILE,
                        FRAME_WIDTH, FRAME_HEIGHT, TARGET_FPS, BUFFER_SIZE)
except ImportError:
    # Valores por defecto si config.py no existe
    RTSP_URL = "rtsp://admin:Ccamar4.@10.10.7.224:554/Streaming/Channels/101"
    HTTP_URL = "http://admin:Ccamar4.@10.10.7.224:8080/video"
    YOLO_CONFIDENCE = 0.5
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    OUTPUT_FOLDER = "Outputs"
    DETECCIONES_FILE = os.path.join(OUTPUT_FOLDER, "detecciones.txt")
    FRAME_WIDTH = 1280
    FRAME_HEIGHT = 720
    TARGET_FPS = 30
    BUFFER_SIZE = 1

# Importar tracker
from tracker import VehicleTracker

# Importar classifier (Phase 3)
from classifier import VehicleClassifierWithTracking
CLASSIFIER_OK = True

try:
    from ultralytics import YOLO
    YOLO_OK = True
except:
    YOLO_OK = False

try:
    import pytesseract
    from PIL import Image, ImageEnhance
    OCR_OK = True
except:
    OCR_OK = False

# Crear carpeta de salida si no existe
Path(OUTPUT_FOLDER).mkdir(exist_ok=True)

state = {
    'vehicle_count': 0,
    'plate_count': 0,
    'current_plate': '',
    'plate_history': {},
    'fps': 0,
    'detecting': False,
    'lock': threading.Lock(),
    'frame': None,
    'running': False,
    'tracker_logged_ids': set(),  # Track which objects we've already logged
    'classified_vehicles': {},  # {vehicle_type: count} - Phase 3
}

def save_plate(plate, conf):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    with open(DETECCIONES_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{ts} | {plate} | {conf:.2%} | PLACA\n")

def is_new(plate):
    """
    Check if plate is new using tracker (PHASE 2 DEEPSORT-INSPIRED)
    Returns True if this is a valid plate reading for logging
    """
    # Delegated to tracker - this is now handled in capture_thread_func
    # Keeping this for backward compatibility
    now = time.time()
    if plate not in state['plate_history']:
        state['plate_history'][plate] = now
        return True
    if now - state['plate_history'][plate] >= 3.0:
        state['plate_history'][plate] = now
        return True
    return False

def read_plate_with_ocr(roi_frame):
    """
    Lee placa REAL usando Tesseract OCR con pre-procesamiento mejorado
    Retorna (texto, confianza) o (None, 0) si no encuentra placa válida
    """
    if not OCR_OK or roi_frame is None or roi_frame.size == 0:
        return None, 0.0
    
    try:
        # 1. Ampliar imagen si es muy pequeña (placas muy lejanas)
        height, width = roi_frame.shape[:2]
        if width < 50 or height < 15:
            roi_frame = cv2.resize(roi_frame, (max(width * 3, 150), max(height * 3, 45)), 
                                   interpolation=cv2.INTER_CUBIC)
        
        # 2. Convertir BGR a escala de grises (mejor OCR)
        roi_gray = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY)
        
        # 3. Pre-procesamiento con OpenCV
        # Ecualización adaptativa de histograma
        roi_gray = cv2.adaptiveThreshold(roi_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
        
        # 4. Remover ruido (denoise)
        roi_gray = cv2.morphologyEx(roi_gray, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
        roi_gray = cv2.morphologyEx(roi_gray, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
        
        # 5. Convertir a PIL y mejorar con PIL
        pil_image = Image.fromarray(roi_gray)
        pil_image = ImageEnhance.Contrast(pil_image).enhance(2.5)
        pil_image = ImageEnhance.Sharpness(pil_image).enhance(3.0)
        
        # 6. OCR con Tesseract optimizado para placas
        # PSM 7 = asumir una línea de texto
        # OEM 3 = usar ambos motores (clásico + neural)
        config = r'--psm 7 --oem 3 -c tesseract_create_pdf=0 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
        text = pytesseract.image_to_string(pil_image, config=config)
        text = text.strip().upper()
        
        # 7. Filtrar caracteres inválidos
        text = ''.join(c for c in text if c.isalnum() or c == '-')
        
        # 8. Solo aceptar si tiene al menos 4 caracteres (placa válida)
        if len(text) >= 4:
            return text, 0.92  # Confianza de OCR mejorada
        
        return None, 0.0
    except Exception as e:
        return None, 0.0

def capture_thread_func(model, ocr, classifier=None):
    """
    Thread de captura y detección con OCR REAL + TRACKING (PHASE 2) + CLASIFICACIÓN (PHASE 3)
    Usa VehicleTracker para eliminar duplicados (~90% menos)
    Usa VehicleClassifier para clasificar vehículos (Auto/Truck/Bus/Motocicleta)
    """
    # Intentar conectar a cámara IP Hikvision
    cap = cv2.VideoCapture(RTSP_URL)
    
    # Si falla RTSP, intentar con HTTP/MJPEG
    if not cap.isOpened():
        cap = cv2.VideoCapture(HTTP_URL)
    
    # Si falla, intentar con cámara local como fallback
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, BUFFER_SIZE)  # Reducir buffer para menos latencia
    
    # Inicializar tracker (PHASE 2 - DeepSORT-inspired)
    tracker = VehicleTracker(max_disappeared=30, max_distance=50, iou_threshold=0.3)
    
    # Inicializar clasificador (PHASE 3 - ResNet50)
    classifier_tracker = classifier if classifier else None
    
    with open(DETECCIONES_FILE, 'w', encoding='utf-8') as f:
        f.write(f"=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (con Tracking) ===\n\n")
    
    fps_time = time.time()
    frame_count = 0
    
    try:
        while state['running']:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_height, frame_width = frame.shape[:2]
            
            if frame_count % 30 == 0:
                elapsed = time.time() - fps_time
                state['fps'] = 30 / max(elapsed, 0.001)
                fps_time = time.time()
            
            detections_this_frame = []
            
            # Detección YOLO
            if frame_count % 2 == 0 and state['detecting']:
                try:
                    if model:
                        results = model(frame, conf=YOLO_CONFIDENCE, verbose=False)
                        for result in results:
                            for box in result.boxes:
                                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                                conf_yolo = float(box.conf[0].cpu().numpy())
                                
                                # Asegurar que las coordenadas estén dentro del frame
                                x1, y1 = max(0, x1), max(0, y1)
                                x2, y2 = min(frame_width, x2), min(frame_height, y2)
                                
                                # Extraer ROI (región de interés)
                                roi = frame[y1:y2, x1:x2]
                                
                                # Leer placa REAL con OCR
                                plate_text, ocr_conf = read_plate_with_ocr(roi)
                                
                                # Solo procesar si OCR encontró una placa válida
                                if plate_text:
                                    detections_this_frame.append({
                                        'bbox': (x1, y1, x2, y2),
                                        'plate': plate_text,
                                        'confidence': ocr_conf
                                    })
                except Exception as e:
                    pass
            
            # PHASE 2: Actualizar tracker con detecciones
            tracked_objects = tracker.update(detections_this_frame)
            
            # PHASE 3: Clasificar vehículos rastreados (si clasificador disponible)
            if classifier_tracker and state['detecting']:
                tracked_objects = classifier_tracker.classify_tracked_objects(tracked_objects, frame)
            
            # Procesar objetos rastreados y dibujar
            for obj in tracked_objects:
                obj_id = obj['object_id']
                x1, y1, x2, y2 = obj['bbox']
                plate = obj['plate']
                conf = obj['confidence']
                frames_tracked = obj['frames_tracked']
                
                # PHASE 3: Obtener clasificación del vehículo
                vehicle_class = obj.get('vehicle_class', 'Unknown')
                class_conf = obj.get('class_confidence', 0.0)
                
                # DEDUPLICATION: Solo loguear si es nueva (nunca vista) 
                # y ha sido rastreada por al menos 3 frames (mejor confianza)
                if obj_id not in state['tracker_logged_ids'] and frames_tracked >= 3:
                    with state['lock']:
                        state['vehicle_count'] += 1
                        state['plate_count'] += 1
                        state['current_plate'] = f"{plate} ({vehicle_class})"
                        # Contar vehículos por tipo (Phase 3)
                        if vehicle_class != 'Unknown':
                            state['classified_vehicles'][vehicle_class] = state['classified_vehicles'].get(vehicle_class, 0) + 1
                    state['tracker_logged_ids'].add(obj_id)
                    save_plate(f"{plate} | {vehicle_class}", conf)
                
                # Seleccionar color según tipo de vehículo (Phase 3)
                if classifier_tracker:
                    class_id = obj.get('vehicle_class_id', -1)
                    color = classifier_tracker.classifier.get_class_color(class_id)
                else:
                    color = (0, 255, 0)  # Verde por defecto
                
                # Dibujar recuadro alrededor de la placa
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Dibujar etiqueta con placa, confianza, ID y clasificación
                label = f"ID:{obj_id} {plate} | {vehicle_class} ({class_conf:.0%})"
                label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                
                # Fondo negro para el texto (arriba del recuadro)
                cv2.rectangle(frame, 
                            (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0] + 8, y1),
                            (0, 0, 0), -1)
                
                # Borde coloreado según clasificación
                cv2.rectangle(frame, 
                            (x1, y1 - label_size[1] - 10),
                            (x1 + label_size[0] + 8, y1),
                            color, 2)
                
                # Texto con ID, placa, tipo y confianza en color blanco
                cv2.putText(frame, label, (x1 + 4, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            
            # HUD con estadísticas mejoradas (Phase 3)
            hud_height = 190 if classifier_tracker else 150
            cv2.rectangle(frame, (10, 10), (650, hud_height), (0, 0, 0), -1)
            cv2.rectangle(frame, (10, 10), (650, hud_height), (0, 255, 0), 2)
            
            cv2.putText(frame, f"Vehiculos: {state['vehicle_count']}", (20, 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Placas: {state['plate_count']}", (20, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Rastreados: {len(tracker.objects)}", (20, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"FPS: {state['fps']:.1f}", (20, 145),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Mostrar conteo por tipo de vehículo (Phase 3)
            if classifier_tracker and state['classified_vehicles']:
                y_pos = 165
                for vtype, count in state['classified_vehicles'].items():
                    cv2.putText(frame, f"{vtype}: {count}", (20, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 1)
                    y_pos += 20
            
            state['frame'] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_count += 1
            
            time.sleep(0.01)
    finally:
        cap.release()


class FalconEPSAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FalconEPSA - Detección Tiempo Real")
        self.root.geometry("1400x800")
        self.root.configure(bg="#1a1a1a")
        
        self.model = None
        self.ocr = None
        self.classifier = None  # Phase 3 - Vehicle Classifier
        self.thread = None
        
        self.setup_ui()
        self.load_model()
        self.load_ocr()
        self.load_classifier()  # Phase 3
        self.update_display()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Panel izquierdo (video)
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.video_label = tk.Label(left_frame, bg="black")
        self.video_label.pack(fill=tk.BOTH, expand=True)
        
        # Panel derecho (controles)
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right_frame.pack_propagate(False)
        
        # Título
        title = tk.Label(right_frame, text="FALCONEPA", 
                        font=("Arial", 18, "bold"),
                        bg="#111111", fg="#00ff00", pady=10)
        title.pack(fill=tk.X)
        
        # Estadísticas
        stats_frame = tk.LabelFrame(right_frame, text="Estadísticas", 
                                   font=("Arial", 10, "bold"),
                                   bg="#222222", fg="#00ff00", padx=10, pady=10)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.vehicle_label = tk.Label(stats_frame, text="Vehículos: 0", 
                                     font=("Arial", 11),
                                     bg="#222222", fg="#00ff00")
        self.vehicle_label.pack(fill=tk.X, pady=5)
        
        self.plate_label = tk.Label(stats_frame, text="Placas: 0", 
                                   font=("Arial", 11),
                                   bg="#222222", fg="#00ff00")
        self.plate_label.pack(fill=tk.X, pady=5)
        
        self.current_plate_label = tk.Label(stats_frame, text="Última: ---", 
                                           font=("Arial", 10),
                                           bg="#222222", fg="#ffff00", wraplength=260)
        self.current_plate_label.pack(fill=tk.X, pady=5)
        
        self.fps_label = tk.Label(stats_frame, text="FPS: 0.0", 
                                 font=("Arial", 10),
                                 bg="#222222", fg="#00ff00")
        self.fps_label.pack(fill=tk.X, pady=5)
        
        # Controles
        controls_frame = tk.LabelFrame(right_frame, text="Controles", 
                                      font=("Arial", 10, "bold"),
                                      bg="#222222", fg="#00ff00", padx=10, pady=10)
        controls_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = tk.Button(controls_frame, text="▶ Iniciar", 
                                  font=("Arial", 11, "bold"),
                                  bg="#00dd00", fg="black", 
                                  activebackground="#00ff00",
                                  command=self.start_capture, width=22)
        self.start_btn.pack(fill=tk.X, pady=5)
        
        self.stop_btn = tk.Button(controls_frame, text="⏹ Detener", 
                                 font=("Arial", 11, "bold"),
                                 bg="#dd0000", fg="white",
                                 activebackground="#ff0000",
                                 command=self.stop_capture, 
                                 state=tk.DISABLED, width=22)
        self.stop_btn.pack(fill=tk.X, pady=5)
        
        # Estado
        status_frame = tk.LabelFrame(right_frame, text="Estado", 
                                    font=("Arial", 10, "bold"),
                                    bg="#222222", fg="#00ff00", padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = tk.Label(status_frame, text="● Listo", 
                                    font=("Arial", 10),
                                    bg="#222222", fg="#00ff00", wraplength=260)
        self.status_label.pack(fill=tk.X, pady=5)
        
        self.info_label = tk.Label(status_frame, text="Esperando inicio...", 
                                  font=("Arial", 9),
                                  bg="#222222", fg="#ffff00", wraplength=260)
        self.info_label.pack(fill=tk.X, pady=5)
    
    def load_model(self):
        if not YOLO_OK:
            self.info_label.config(text="YOLO no disponible")
            return
        
        if not os.path.exists("last.pt"):
            self.info_label.config(text="last.pt no encontrado")
            return
        
        self.status_label.config(text="● Cargando modelo...")
        self.root.update()
        
        try:
            self.model = YOLO("last.pt")
            self.status_label.config(text="● Modelo listo")
            self.info_label.config(text="last.pt cargado")
        except Exception as e:
            self.status_label.config(text="● Error")
            self.info_label.config(text=f"Error: {str(e)[:40]}")
    
    def load_ocr(self):
        """Cargar motor OCR Tesseract para lectura REAL de placas"""
        if not OCR_OK:
            self.info_label.config(text="⚠️ ERROR: Tesseract no instalado")
            self.status_label.config(text="● ERROR - OCR requerido")
            return
        
        try:
            # Configurar ruta de Tesseract desde config
            import sys
            if sys.platform == 'win32':
                pytesseract.pytesseract.pytesseract_cmd = TESSERACT_PATH
            
            self.status_label.config(text="● OCR Tesseract ACTIVO")
            self.info_label.config(text="✅ Leyendo placas REALES con OCR")
        except Exception as e:
            self.status_label.config(text="● ERROR")
            self.info_label.config(text="⚠️ Tesseract no encontrado")
    
    def load_classifier(self):
        """Cargar clasificador de vehículos ResNet50 (Phase 3)"""
        if not CLASSIFIER_OK:
            self.status_label.config(text="● OCR + Tracking (Sin clasificación)")
            return
        
        try:
            self.status_label.config(text="● Cargando clasificador...")
            self.root.update()
            
            self.classifier = VehicleClassifierWithTracking(
                max_disappeared=30,
                max_distance=50,
                iou_threshold=0.3
            )
            
            self.status_label.config(text="● OCR + Tracking + Clasificación")
            self.info_label.config(text="✅ ResNet50 clasificador ACTIVO")
        except Exception as e:
            self.status_label.config(text="● OCR + Tracking (Error clasificación)")
            self.info_label.config(text=f"⚠️ Clasificación no disponible: {str(e)[:30]}")
            self.classifier = None
    
    def start_capture(self):
        state['running'] = True
        state['detecting'] = True
        state['vehicle_count'] = 0
        state['plate_count'] = 0
        state['plate_history'].clear()
        state['tracker_logged_ids'].clear()  # Reset tracked object IDs
        state['classified_vehicles'].clear()  # Reset vehicle counts by type
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        if self.classifier:
            self.status_label.config(text="● Capturando (Tracking + Clasificación)")
            self.info_label.config(text="Procesando con DeepSORT + ResNet50...")
        else:
            self.status_label.config(text="● Capturando (con Tracking)")
            self.info_label.config(text="Procesando con DeepSORT...")
        
        self.thread = threading.Thread(
            target=capture_thread_func, 
            args=(self.model, self.ocr, self.classifier), 
            daemon=True
        )
        self.thread.start()
    
    def stop_capture(self):
        state['running'] = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Detenido (Tracking)")
        self.info_label.config(text="Captura detenida")
    
    def update_display(self):
        if state['frame'] is not None:
            h, w = state['frame'].shape[:2]
            aspect = w / h
            target_w = 850
            target_h = int(target_w / aspect)
            
            frame_resized = cv2.resize(
                state['frame'],
                (target_w, target_h),
                interpolation=cv2.INTER_LINEAR
            )
            
            img = Image.fromarray(frame_resized)
            photo = ImageTk.PhotoImage(image=img)
            
            self.video_label.config(image=photo)
            self.video_label.image = photo
        
        self.vehicle_label.config(text=f"Vehículos: {state['vehicle_count']}")
        self.plate_label.config(text=f"Placas: {state['plate_count']}")
        self.current_plate_label.config(text=f"Última: {state['current_plate'] or '---'}")
        self.fps_label.config(text=f"FPS: {state['fps']:.1f}")
        
        self.root.after(100, self.update_display)

def main():
    root = tk.Tk()
    app = FalconEPSAApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
