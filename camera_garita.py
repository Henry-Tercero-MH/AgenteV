# -*- coding: utf-8 -*-
"""
Sistema de Cámara para Control de Garita
Detecta placas en tiempo real y las envía automáticamente al API
"""
import cv2
import numpy as np
from datetime import datetime, timedelta
import requests
import threading
import queue
import time
from pathlib import Path
from core.pipeline import PipelineDeteccion
from models.detector import DetectorPlacas
from models.ocr_engine import MotorOCR
from config.settings import MODELO_PLACAS_DEFAULT, MODELO_CAMIONES_DEFAULT

class CameraGarita:
    """
    Sistema de cámara para control de garita
    Detecta placas en tiempo real y registra automáticamente las entradas
    """

    def __init__(self, camera_source=0, api_url="http://localhost:8001"):
        """
        Inicializar sistema de cámara

        Args:
            camera_source: Índice de cámara (0 para webcam) o URL de IP camera
            api_url: URL del API backend
        """
        self.camera_source = camera_source
        self.api_url = api_url
        self.running = False

        # Pipeline de detección
        print("🔄 Inicializando modelos de detección...")
        self.detector = DetectorPlacas(
            ruta_modelo_placas=MODELO_PLACAS_DEFAULT,
            ruta_modelo_camiones=MODELO_CAMIONES_DEFAULT
        )
        self.motor_ocr = MotorOCR()
        self.pipeline = PipelineDeteccion(self.detector, self.motor_ocr)
        print("✅ Modelos inicializados correctamente")

        # Cola para procesamiento en segundo plano
        self.processing_queue = queue.Queue(maxsize=10)

        # Sistema de cooldown para evitar duplicados
        self.detecciones_recientes = {}  # {placa: timestamp}
        self.cooldown_seconds = 30  # No registrar la misma placa por 30 segundos

        # Estadísticas
        self.total_detecciones = 0
        self.total_enviadas = 0
        self.total_errores = 0

        # Thread para procesamiento
        self.processing_thread = None

        # Carpeta para guardar capturas
        self.output_dir = Path("Outputs/capturas_garita")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def iniciar(self):
        """Iniciar sistema de cámara"""
        print("=" * 70)
        print("  🦅 FALCON EPSA - Sistema de Cámara para Control de Garita")
        print("=" * 70)
        print(f"\n📹 Fuente de cámara: {self.camera_source}")
        print(f"🌐 API Backend: {self.api_url}")
        print(f"📁 Directorio capturas: {self.output_dir}")
        print(f"⏱️  Cooldown entre detecciones: {self.cooldown_seconds}s")

        # Verificar conexión con API
        if not self._verificar_api():
            print("\n❌ No se puede conectar con el API. Asegúrate de que esté corriendo.")
            return False

        # Abrir cámara
        self.cap = cv2.VideoCapture(self.camera_source)
        if not self.cap.isOpened():
            print(f"\n❌ Error: No se puede abrir la cámara {self.camera_source}")
            return False

        # Configurar resolución
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(self.cap.get(cv2.CAP_PROP_FPS))

        print(f"\n✅ Cámara iniciada:")
        print(f"   Resolución: {width}x{height}")
        print(f"   FPS: {fps}")

        # Iniciar thread de procesamiento
        self.running = True
        self.processing_thread = threading.Thread(target=self._procesar_cola, daemon=True)
        self.processing_thread.start()

        print("\n🚀 Sistema iniciado. Esperando vehículos...")
        print("\n📋 Controles:")
        print("   - ESPACIO: Capturar frame manualmente")
        print("   - 'q' o ESC: Salir")
        print("   - 's': Ver estadísticas")
        print("\n" + "=" * 70 + "\n")

        return True

    def _verificar_api(self):
        """Verificar que el API esté corriendo"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _procesar_cola(self):
        """Procesar frames en segundo plano"""
        while self.running:
            try:
                # Obtener frame de la cola (con timeout)
                item = self.processing_queue.get(timeout=1)
                if item is None:
                    break

                frame, timestamp = item
                self._procesar_frame(frame, timestamp)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Error en procesamiento: {e}")
                self.total_errores += 1

    def _procesar_frame(self, frame, timestamp):
        """
        Procesar un frame: detectar placa, extraer texto, enviar al API

        Args:
            frame: Frame de la cámara
            timestamp: Timestamp de la captura
        """
        try:
            # Guardar frame temporal
            temp_path = self.output_dir / f"temp_{timestamp}.jpg"
            cv2.imwrite(str(temp_path), frame)

            # Detectar placas
            resultados = self.pipeline.procesar_imagen(
                str(temp_path),
                umbral_confianza=0.5,
                guardar=False  # No guardar aquí, lo hacemos manualmente
            )

            if not resultados or resultados['cantidad_placas'] == 0:
                # No se detectaron placas, eliminar archivo temporal
                temp_path.unlink(missing_ok=True)
                return

            # Procesar cada placa detectada
            for idx, placa_data in enumerate(resultados['detecciones']):
                placa_texto = placa_data.get('texto', '').strip()

                if not placa_texto or len(placa_texto) < 4:
                    continue  # Texto muy corto, probablemente ruido

                # Verificar cooldown
                if self._esta_en_cooldown(placa_texto):
                    print(f"⏳ Placa {placa_texto} detectada recientemente, ignorando...")
                    continue

                # Registrar detección
                self.total_detecciones += 1

                # Extraer imagen de la placa del frame original usando las coordenadas
                imagen_placa = None
                caja = placa_data.get('caja', [])
                if len(caja) == 4:
                    x1, y1, x2, y2 = map(int, caja)
                    imagen_placa = frame[y1:y2, x1:x2]

                # Guardar imagen de la placa
                imagen_path = None
                if imagen_placa is not None and imagen_placa.size > 0:
                    imagen_nombre = f"{timestamp}_{placa_texto}_{idx}.jpg"
                    imagen_path_full = self.output_dir / imagen_nombre
                    cv2.imwrite(str(imagen_path_full), imagen_placa)
                    imagen_path = f"Outputs/capturas_garita/{imagen_nombre}"

                # Enviar al API
                self._enviar_al_api(
                    placa=placa_texto,
                    confianza=placa_data.get('confianza_deteccion', 0.0),
                    imagen_path=imagen_path
                )

                # Actualizar cooldown
                self._actualizar_cooldown(placa_texto)

            # Eliminar archivo temporal
            temp_path.unlink(missing_ok=True)

        except Exception as e:
            print(f"❌ Error procesando frame: {e}")
            self.total_errores += 1

    def _esta_en_cooldown(self, placa):
        """Verificar si una placa está en cooldown"""
        if placa not in self.detecciones_recientes:
            return False

        ultimo_registro = self.detecciones_recientes[placa]
        tiempo_transcurrido = (datetime.now() - ultimo_registro).total_seconds()

        return tiempo_transcurrido < self.cooldown_seconds

    def _actualizar_cooldown(self, placa):
        """Actualizar timestamp de última detección"""
        self.detecciones_recientes[placa] = datetime.now()

        # Limpiar detecciones antiguas (más de 1 hora)
        ahora = datetime.now()
        placas_a_eliminar = [
            p for p, t in self.detecciones_recientes.items()
            if (ahora - t).total_seconds() > 3600
        ]
        for p in placas_a_eliminar:
            del self.detecciones_recientes[p]

    def _enviar_al_api(self, placa, confianza, imagen_path=None):
        """
        Enviar detección al API

        Args:
            placa: Texto de la placa
            confianza: Confianza de la detección
            imagen_path: Path de la imagen (opcional)
        """
        try:
            endpoint = f"{self.api_url}/api/registros/entrada"

            payload = {
                "placa": placa,
                "confianza": confianza,
                "imagen_path": imagen_path
            }

            print(f"\n📤 Enviando detección al API:")
            print(f"   Placa: {placa}")
            print(f"   Confianza: {confianza * 100:.1f}%")

            response = requests.post(endpoint, json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.total_enviadas += 1

                print(f"✅ Registro exitoso (ID: {data['registro']['id']})")

                if data['registrada']:
                    info = data['placa_info']
                    print(f"   🚗 VEHÍCULO REGISTRADO")
                    print(f"   Propietario: {info['propietario']}")
                    print(f"   Tipo: {info['tipo_vehiculo']}")
                    print(f"   Estado: {info['estado']}")
                else:
                    print(f"   ⚠️  PLACA NO REGISTRADA EN EL SISTEMA")

                print(f"   Dashboard actualizado vía WebSocket ✓")

            else:
                print(f"❌ Error del API: {response.status_code}")
                self.total_errores += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión con API: {e}")
            self.total_errores += 1
        except Exception as e:
            print(f"❌ Error enviando al API: {e}")
            self.total_errores += 1

    def _mostrar_estadisticas(self):
        """Mostrar estadísticas del sistema"""
        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS DEL SISTEMA")
        print("=" * 70)
        print(f"Total de detecciones: {self.total_detecciones}")
        print(f"Total enviadas al API: {self.total_enviadas}")
        print(f"Total de errores: {self.total_errores}")
        print(f"Placas en cooldown: {len(self.detecciones_recientes)}")
        print(f"Items en cola: {self.processing_queue.qsize()}")
        print("=" * 70 + "\n")

    def ejecutar(self):
        """Loop principal de la cámara"""
        if not self.iniciar():
            return

        # Variables para FPS
        frame_count = 0
        start_time = time.time()
        fps = 0

        # Saltar frames para procesamiento (procesar 1 de cada N frames)
        skip_frames = 3
        frame_counter = 0

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error leyendo frame de la cámara")
                    break

                frame_counter += 1

                # Calcular FPS
                frame_count += 1
                if frame_count % 30 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0

                # Crear copia para visualización
                display_frame = frame.copy()

                # Agregar overlay con información
                self._agregar_overlay(display_frame, fps)

                # Mostrar frame
                cv2.imshow('Falcon EPSA - Control de Garita', display_frame)

                # Procesar frame cada N frames (para no saturar)
                if frame_counter % skip_frames == 0:
                    # Agregar a cola de procesamiento si no está llena
                    if not self.processing_queue.full():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                        self.processing_queue.put((frame.copy(), timestamp))

                # Controles de teclado
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q') or key == 27:  # 'q' o ESC
                    print("\n👋 Saliendo del sistema...")
                    break
                elif key == ord(' '):  # ESPACIO - Captura manual
                    print("\n📸 Captura manual solicitada...")
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    self.processing_queue.put((frame.copy(), timestamp))
                elif key == ord('s'):  # 's' - Estadísticas
                    self._mostrar_estadisticas()

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupción del usuario")
        finally:
            self.detener()

    def _agregar_overlay(self, frame, fps):
        """Agregar información en el frame"""
        h, w = frame.shape[:2]

        # Fondo semi-transparente para el texto
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (500, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Información del sistema
        y = 35
        cv2.putText(frame, "FALCON EPSA - Control de Garita", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        y += 30
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        y += 25
        cv2.putText(frame, f"Detecciones: {self.total_detecciones}", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y += 25
        cv2.putText(frame, f"Enviadas: {self.total_enviadas}", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        y += 25
        cv2.putText(frame, f"Cola: {self.processing_queue.qsize()}", (20, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Estado de conexión con API
        api_status = "CONECTADO" if self._verificar_api() else "DESCONECTADO"
        color = (0, 255, 0) if api_status == "CONECTADO" else (0, 0, 255)
        cv2.putText(frame, f"API: {api_status}", (w - 200, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def detener(self):
        """Detener sistema de cámara"""
        print("\n🛑 Deteniendo sistema...")

        self.running = False

        # Detener procesamiento
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_queue.put(None)  # Signal para terminar
            self.processing_thread.join(timeout=5)

        # Liberar cámara
        if hasattr(self, 'cap'):
            self.cap.release()

        cv2.destroyAllWindows()

        # Mostrar estadísticas finales
        self._mostrar_estadisticas()

        print("✅ Sistema detenido correctamente\n")


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Sistema de Cámara para Control de Garita")
    parser.add_argument('--camera', type=str, default='0',
                        help='Fuente de cámara (0 para webcam, URL para IP camera)')
    parser.add_argument('--api', type=str, default='http://localhost:8001',
                        help='URL del API backend')
    parser.add_argument('--cooldown', type=int, default=30,
                        help='Tiempo en segundos entre detecciones de la misma placa')

    args = parser.parse_args()

    # Convertir camera a int si es un número
    camera_source = args.camera
    if camera_source.isdigit():
        camera_source = int(camera_source)

    # Crear y ejecutar sistema
    sistema = CameraGarita(
        camera_source=camera_source,
        api_url=args.api
    )
    sistema.cooldown_seconds = args.cooldown
    sistema.ejecutar()


if __name__ == "__main__":
    main()
