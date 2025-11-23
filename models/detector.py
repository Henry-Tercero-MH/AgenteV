# -*- coding: utf-8 -*-
"""
Detector de placas y camiones usando YOLO
"""
# Import lazy para evitar problemas de inicialización
ULTRALYTICS_AVAILABLE = False
YOLO = None

try:
    # Intentar importar solo si es necesario
    pass  # No importar aquí, hacerlo en el constructor
except ImportError as e:
    print(f"⚠️  Ultralytics no disponible: {e}")

from utils.image_utils import convertir_a_numpy, recortar_region
from config.settings import UMBRAL_CONFIANZA_DEFAULT, PADDING_RECORTE


class DetectorPlacas:
    """Detector de placas y camiones usando modelos YOLO"""
    
    def __init__(self, ruta_modelo_placas, ruta_modelo_camiones=None):
        """
        Inicializa los modelos de detección.
        
        Args:
            ruta_modelo_placas (str): Ruta al modelo YOLO de placas
            ruta_modelo_camiones (str, optional): Ruta al modelo YOLO de camiones
        """
        global YOLO, ULTRALYTICS_AVAILABLE
        
        # Importar ultralytics solo cuando se necesita
        if YOLO is None:
            try:
                from ultralytics import YOLO as YOLOClass
                YOLO = YOLOClass
                ULTRALYTICS_AVAILABLE = True
                print("✅ Ultralytics importado correctamente")
            except ImportError as e:
                raise ImportError(f"Ultralytics no está disponible. Instala ultralytics: pip install ultralytics. Error: {e}")
        
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError("Ultralytics no está disponible. Instala ultralytics: pip install ultralytics")
        
        try:
            print(f"[INFO] Cargando modelo de placas: {ruta_modelo_placas}")
            self.modelo_placas = YOLO(ruta_modelo_placas)
            print("[INFO] Modelo de placas cargado exitosamente")
        except Exception as e:
            print(f"[ERROR] Error cargando modelo de placas: {e}")
            raise RuntimeError(f"No se pudo cargar el modelo de placas: {e}")
        
        self.modelo_camiones = None
        if ruta_modelo_camiones:
            try:
                print(f"[INFO] Cargando modelo de camiones: {ruta_modelo_camiones}")
                self.modelo_camiones = YOLO(ruta_modelo_camiones)
                print("[INFO] Modelo de camiones cargado exitosamente")
            except Exception as e:
                print(f"[WARNING] Error cargando modelo de camiones: {e}. Continuando sin detección de camiones.")
                self.modelo_camiones = None
    
    def detectar_camiones(self, imagen, umbral_confianza=UMBRAL_CONFIANZA_DEFAULT):
        """
        Detecta camiones en una imagen.
        
        Args:
            imagen (numpy.ndarray): Imagen donde detectar
            umbral_confianza (float): Umbral mínimo de confianza
            
        Returns:
            list: Lista de cajas [(x1, y1, x2, y2), ...]
        """
        if self.modelo_camiones is None:
            return []
        
        print('[DEBUG] Ejecutando modelo de camiones...')
        cajas_camiones = []
        
        try:
            resultados = self.modelo_camiones(imagen)
            
            for resultado in resultados:
                if not hasattr(resultado, 'boxes'):
                    continue
                
                xyxy = convertir_a_numpy(resultado.boxes.xyxy)
                confianzas = convertir_a_numpy(resultado.boxes.conf).flatten() if hasattr(resultado.boxes, 'conf') else None
                clases = convertir_a_numpy(resultado.boxes.cls).astype(int).flatten() if hasattr(resultado.boxes, 'cls') else None
                
                if xyxy.size == 0:
                    continue
                
                # Asumir que la clase de camiones es 0, si no tomar todas
                if clases is None:
                    indices = range(xyxy.shape[0])
                else:
                    indices = [i for i in range(len(clases)) if clases[i] == 0]
                
                for idx in indices:
                    conf = float(confianzas[idx]) if confianzas is not None else 1.0
                    
                    if conf < umbral_confianza:
                        print(f'[DEBUG] Camión descartado (conf={conf:.3f} < {umbral_confianza})')
                        continue
                    
                    caja = [int(c) for c in xyxy[idx]]
                    print(f'[DEBUG] Camión detectado: box={caja}, conf={conf:.3f}')
                    cajas_camiones.append(caja)
        
        except Exception as e:
            print(f'[ERROR] Error en inferencia del modelo de camiones: {e}')
        
        return cajas_camiones
    
    def detectar_placas_en_region(self, imagen, region, umbral_confianza=UMBRAL_CONFIANZA_DEFAULT):
        """
        Detecta placas en una región específica de la imagen.
        
        Args:
            imagen (numpy.ndarray): Imagen completa
            region (tuple): (x1, y1, x2, y2) región donde buscar
            umbral_confianza (float): Umbral mínimo de confianza
            
        Returns:
            list: Lista de detecciones [{'caja_completa': [...], 'caja_region': [...], 'confianza': ..., 'imagen_recorte': ...}, ...]
        """
        x1_region, y1_region, x2_region, y2_region = region
        recorte_region = recortar_region(imagen, x1_region, y1_region, x2_region, y2_region)
        
        if recorte_region.size == 0:
            return []
        
        detecciones = []
        
        try:
            resultados = self.modelo_placas(recorte_region)
            
            for resultado in resultados:
                if not hasattr(resultado, 'boxes'):
                    continue
                
                xyxy = convertir_a_numpy(resultado.boxes.xyxy)
                confianzas = convertir_a_numpy(resultado.boxes.conf).flatten() if hasattr(resultado.boxes, 'conf') else None
                
                if xyxy.size == 0:
                    continue
                
                for idx in range(xyxy.shape[0]):
                    conf = float(confianzas[idx]) if confianzas is not None else 1.0
                    
                    if conf < umbral_confianza:
                        continue
                    
                    # Coordenadas en el recorte de la región
                    cx1, cy1, cx2, cy2 = [int(c) for c in xyxy[idx]]
                    
                    # Coordenadas en la imagen completa
                    fx1 = x1_region + cx1
                    fy1 = y1_region + cy1
                    fx2 = x1_region + cx2
                    fy2 = y1_region + cy2
                    
                    # Recortar la placa
                    placa_recorte = recortar_region(recorte_region, cx1, cy1, cx2, cy2)
                    
                    if placa_recorte.size == 0:
                        continue
                    
                    detecciones.append({
                        'caja_completa': [fx1, fy1, fx2, fy2],
                        'caja_region': [cx1, cy1, cx2, cy2],
                        'confianza': conf,
                        'imagen_recorte': placa_recorte
                    })
        
        except Exception as e:
            print(f'[ERROR] Error en inferencia YOLO (placas): {e}')
        
        return detecciones
    
    def generar_regiones_busqueda(self, imagen, cajas_camiones, padding=PADDING_RECORTE):
        """
        Genera regiones donde buscar placas basándose en detecciones de camiones.
        
        Args:
            imagen (numpy.ndarray): Imagen completa
            cajas_camiones (list): Lista de cajas de camiones
            padding (int): Padding a agregar a cada caja
            
        Returns:
            list: Lista de regiones [(y1, x1, y2, x2), ...]
        """
        alto, ancho = imagen.shape[:2]
        regiones = []
        
        if cajas_camiones:
            print(f'[DEBUG] {len(cajas_camiones)} camiones detectados. Buscando placas en regiones de camiones.')
            
            for caja in cajas_camiones:
                x1, y1, x2, y2 = caja
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(ancho, x2 + padding)
                y2 = min(alto, y2 + padding)
                regiones.append((y1, x1, y2, x2))
        else:
            print('[DEBUG] No se detectaron camiones. Buscando placas en la imagen completa.')
            regiones.append((0, 0, alto, ancho))
        
        return regiones
