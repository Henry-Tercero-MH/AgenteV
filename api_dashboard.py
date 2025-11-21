# -*- coding: utf-8 -*-
"""
API FastAPI para servir datos al dashboard React
Control de Garita con WebSocket en tiempo real
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
import subprocess
from pathlib import Path
import asyncio
import shutil

# Modelos Pydantic para validación
class DeteccionPlaca(BaseModel):
    placa: str
    imagen_path: Optional[str] = None
    confianza: Optional[float] = None

class RegistroEntrada(BaseModel):
    placa: str
    timestamp: str
    imagen_path: Optional[str] = None
    tipo_evento: str = "ENTRADA"  # ENTRADA o SALIDA

# WebSocket Manager para conexiones en tiempo real
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f">> Cliente conectado. Total conexiones: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f">> Cliente desconectado. Total conexiones: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Enviar mensaje a todos los clientes conectados"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Error enviando mensaje, cliente desconectado: {e}")
                disconnected.append(connection)

        # Limpiar conexiones muertas
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()

app = FastAPI(
    title="Falcon EPSA - Dashboard API",
    description="API para visualización de detección de placas - Sistema de Control de Garita",
    version="2.0.0"
)

# Configurar CORS para permitir requests desde React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los origenes para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory="Outputs"), name="outputs")
app.mount("/inputs", StaticFiles(directory="Inputs"), name="inputs")
# Montar carpeta HLS para servir el stream
if not os.path.exists("hls"):
    os.makedirs("hls")
app.mount("/hls", StaticFiles(directory="hls"), name="hls")

# Configuración de la cámara Hikvision y HLS
try:
    from config import RTSP_URL
except ImportError:
    # Fallback a configuración por defecto
    RTSP_URL = 'rtsp://admin:Ccamar4.@10.10.7.224:554/Streaming/Channels/2'
HLS_DIR = os.path.join(os.getcwd(), 'hls')
HLS_PLAYLIST = 'stream.m3u8'
HLS_PATH = os.path.join(HLS_DIR, HLS_PLAYLIST)

# Comando ffmpeg para convertir RTSP a HLS
FFMPEG_CMD = [
    'ffmpeg',
    '-i', RTSP_URL,
    '-c:v', 'copy',
    '-c:a', 'aac',
    '-f', 'hls',
    '-hls_time', '2',
    '-hls_list_size', '3',
    '-hls_flags', 'delete_segments',
    HLS_PATH
]

def start_ffmpeg():
    os.makedirs(HLS_DIR, exist_ok=True)
    # Si ya hay un proceso ffmpeg corriendo, no lanzar otro
    # Solo en Windows: buscar ffmpeg en procesos
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'ffmpeg' in proc.info['name']:
                return
    except ImportError:
        pass
    subprocess.Popen(FFMPEG_CMD)

# Endpoint para obtener la URL HLS
@app.get("/api/hls-url")
def get_hls_url():
    return {"hls_url": f"/hls/{HLS_PLAYLIST}"}

# Rutas del API
@app.get("/")
def read_root():
    """Endpoint raíz - Sistema de Control de Garita"""
    return {
        "message": "Falcon EPSA - Sistema de Control de Garita",
        "version": "2.0.0",
        "descripcion": "API para detección y registro de placas vehiculares en tiempo real",
        "endpoints": {
            "general": [
                "/health",
                "/docs",
                "/redoc"
            ],
            "registros": [
                "POST /api/registros/entrada",
                "GET /api/registros/historial",
                "GET /api/registros/placa/{placa}"
            ],
            "placas": [
                "GET /api/placas/validar/{placa}",
                "GET /api/placas/todas"
            ],
            "procesamiento": [
                "GET /api/resultados",
                "GET /api/estadisticas",
                "POST /api/procesar-batch"
            ],
            "websocket": [
                "ws://localhost:8001/ws"
            ]
        },
        "documentacion": "http://localhost:8001/docs"
    }

@app.get("/api/resultados")
def obtener_resultados():
    """
    Obtiene todos los resultados del procesamiento.

    Returns:
        dict: Datos completos con resultados y metadatos
    """
    ruta_json = "Outputs/resultados_dashboard.json"

    if not os.path.exists(ruta_json):
        raise HTTPException(
            status_code=404,
            detail="No se encontraron resultados. Ejecuta primero: python process_batch.py"
        )

    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer resultados: {str(e)}")

@app.get("/api/estadisticas")
def obtener_estadisticas():
    """
    Obtiene solo las estadísticas generales.

    Returns:
        dict: Metadatos y estadísticas
    """
    ruta_json = "Outputs/resultados_dashboard.json"

    if not os.path.exists(ruta_json):
        raise HTTPException(
            status_code=404,
            detail="No se encontraron resultados."
        )

    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        return datos.get('metadatos', {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer estadísticas: {str(e)}")

@app.get("/api/resultados/{imagen_id}")
def obtener_resultado_por_id(imagen_id: int):
    """
    Obtiene el resultado de una imagen específica por ID.

    Args:
        imagen_id (int): ID de la imagen

    Returns:
        dict: Resultado de la imagen
    """
    ruta_json = "Outputs/resultados_dashboard.json"

    if not os.path.exists(ruta_json):
        raise HTTPException(status_code=404, detail="No se encontraron resultados.")

    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        # Buscar imagen por ID
        for resultado in datos.get('resultados', []):
            if resultado['id'] == imagen_id:
                return resultado

        raise HTTPException(status_code=404, detail=f"No se encontró imagen con ID {imagen_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/imagen/{tipo}/{nombre}")
def obtener_imagen(tipo: str, nombre: str):
    """
    Sirve una imagen (input u output).

    Args:
        tipo (str): 'input' o 'output'
        nombre (str): Nombre del archivo

    Returns:
        FileResponse: Archivo de imagen
    """
    if tipo == 'input':
        ruta = Path("Inputs") / nombre
    elif tipo == 'output':
        ruta = Path("Outputs") / nombre
    else:
        raise HTTPException(status_code=400, detail="Tipo debe ser 'input' o 'output'")

    if not ruta.exists():
        raise HTTPException(status_code=404, detail=f"Imagen no encontrada: {nombre}")

    return FileResponse(ruta)

@app.get("/api/placas/validar/{placa}")
def validar_placa(placa: str):
    """
    Valida si una placa existe en la base de datos y retorna su información.

    Args:
        placa (str): Número de placa a validar

    Returns:
        dict: Información de la placa si existe, o estado no registrado
    """
    ruta_db = "database/placas_db.json"

    if not os.path.exists(ruta_db):
        raise HTTPException(
            status_code=404,
            detail="Base de datos de placas no encontrada. Ejecuta: python generar_db_placas.py"
        )

    try:
        with open(ruta_db, 'r', encoding='utf-8') as f:
            db = json.load(f)

        # Buscar placa en la base de datos (búsqueda case-insensitive)
        placa_upper = placa.upper()
        for placa_info in db.get('placas', []):
            if placa_info['placa'].upper() == placa_upper:
                return {
                    "registrada": True,
                    "placa": placa_info['placa'],
                    "estado": placa_info['estado'],
                    "tipo_vehiculo": placa_info['tipo_vehiculo'],
                    "propietario": placa_info['propietario'],
                    "departamento": placa_info['departamento'],
                    "vigencia": placa_info['vigencia'],
                    "observaciones": placa_info['observaciones']
                }

        # Si no se encuentra
        return {
            "registrada": False,
            "placa": placa,
            "mensaje": "Placa no registrada en el sistema"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al validar placa: {str(e)}")

@app.get("/api/placas/todas")
def obtener_todas_placas():
    """
    Obtiene toda la base de datos de placas.

    Returns:
        dict: Base de datos completa de placas
    """
    ruta_db = "database/placas_db.json"

    if not os.path.exists(ruta_db):
        raise HTTPException(
            status_code=404,
            detail="Base de datos de placas no encontrada."
        )

    try:
        with open(ruta_db, 'r', encoding='utf-8') as f:
            db = json.load(f)
        return db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer base de datos: {str(e)}")

@app.post("/api/registros/entrada")
async def registrar_entrada(deteccion: DeteccionPlaca):
    """
    Registra una nueva detección de placa (entrada automática).
    Valida la placa en la DB y registra el evento con timestamp.

    Args:
        deteccion: Datos de la detección (placa, imagen, confianza)

    Returns:
        dict: Información completa del vehículo + registro guardado
    """
    ruta_db = "database/placas_db.json"
    ruta_logs = "database/logs_entrada_salida.json"

    # Validar si la placa existe en la DB
    placa_info = None
    registrada = False

    if os.path.exists(ruta_db):
        try:
            with open(ruta_db, 'r', encoding='utf-8') as f:
                db = json.load(f)

            placa_upper = deteccion.placa.upper()
            for placa in db.get('placas', []):
                if placa['placa'].upper() == placa_upper:
                    placa_info = placa
                    registrada = True
                    break
        except Exception as e:
            print(f"Error al leer DB: {e}")

    # Crear registro del evento
    timestamp = datetime.now().isoformat()
    registro = {
        "id": None,  # Se asignará después
        "placa": deteccion.placa,
        "timestamp": timestamp,
        "tipo_evento": "ENTRADA",
        "imagen_path": deteccion.imagen_path,
        "confianza": deteccion.confianza,
        "registrada": registrada
    }

    # Guardar en logs
    logs = {"registros": []}
    if os.path.exists(ruta_logs):
        try:
            with open(ruta_logs, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = {"registros": []}

    # Asignar ID
    registro["id"] = len(logs.get("registros", [])) + 1
    logs["registros"].append(registro)

    # Guardar logs actualizados
    os.makedirs("database", exist_ok=True)
    with open(ruta_logs, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    # Preparar respuesta completa
    respuesta = {
        "registro": registro,
        "placa_info": placa_info if registrada else None,
        "registrada": registrada,
        "mensaje": "Vehículo registrado" if registrada else "Placa no registrada en el sistema"
    }

    # Broadcast a todos los clientes WebSocket
    await manager.broadcast({
        "tipo": "nueva_deteccion",
        "data": respuesta
    })

    return respuesta

@app.get("/api/registros/historial")
def obtener_historial(limit: int = 50):
    """
    Obtiene el historial de entradas/salidas.

    Args:
        limit: Número máximo de registros a retornar (default: 50)

    Returns:
        dict: Historial de registros
    """
    ruta_logs = "database/logs_entrada_salida.json"

    if not os.path.exists(ruta_logs):
        return {"registros": [], "total": 0}

    try:
        with open(ruta_logs, 'r', encoding='utf-8') as f:
            logs = json.load(f)

        registros = logs.get("registros", [])
        # Retornar los últimos N registros (más recientes primero)
        registros_recientes = list(reversed(registros[-limit:]))

        return {
            "registros": registros_recientes,
            "total": len(registros)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer historial: {str(e)}")

@app.get("/api/registros/placa/{placa}")
def obtener_historial_placa(placa: str):
    """
    Obtiene el historial de una placa específica.

    Args:
        placa: Número de placa

    Returns:
        dict: Historial de registros de esa placa
    """
    ruta_logs = "database/logs_entrada_salida.json"

    if not os.path.exists(ruta_logs):
        return {"registros": [], "total": 0}

    try:
        with open(ruta_logs, 'r', encoding='utf-8') as f:
            logs = json.load(f)

        placa_upper = placa.upper()
        registros_placa = [
            r for r in logs.get("registros", [])
            if r['placa'].upper() == placa_upper
        ]

        return {
            "placa": placa,
            "registros": list(reversed(registros_placa)),  # Más recientes primero
            "total": len(registros_placa)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer historial: {str(e)}")

@app.post("/api/procesar-captura")
async def procesar_captura(file: UploadFile = File(...)):
    """
    Procesa una imagen capturada desde el dashboard React.
    Detecta placas, valida contra DB y registra automáticamente.

    Args:
        file: Imagen capturada (JPG/PNG)

    Returns:
        dict: Resultado completo del procesamiento
    """
    try:
        # Guardar archivo temporal
        temp_dir = Path("Outputs/temp_capturas")
        temp_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        temp_path = temp_dir / f"captura_{timestamp}.jpg"

        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"[CAPTURA] Captura recibida: {temp_path}")

        # Procesar imagen con el pipeline
        from core.pipeline import PipelineDeteccion
        from models.detector import DetectorPlacas
        from models.ocr_engine import MotorOCR
        from config.settings import MODELO_PLACAS_DEFAULT, MODELO_CAMIONES_DEFAULT

        # Inicializar pipeline (esto debería ser singleton en producción)
        detector = DetectorPlacas(
            ruta_modelo_placas=MODELO_PLACAS_DEFAULT,
            ruta_modelo_camiones=MODELO_CAMIONES_DEFAULT
        )
        motor_ocr = MotorOCR()
        pipeline = PipelineDeteccion(detector, motor_ocr)

        # Procesar imagen
        resultados = pipeline.procesar_imagen(
            str(temp_path),
            umbral_confianza=0.5,
            guardar=True,
            carpeta_salida="Outputs/capturas_dashboard"
        )

        if not resultados or resultados['cantidad_placas'] == 0:
            # Limpiar archivo temporal
            temp_path.unlink(missing_ok=True)

            return {
                "success": False,
                "mensaje": "No se detectaron placas en la imagen",
                "detecciones": []
            }

        # Procesar cada placa detectada y registrarla
        detecciones_procesadas = []

        for idx, placa_data in enumerate(resultados['detecciones']):
            placa_texto = placa_data.get('texto', '').strip()

            if not placa_texto or len(placa_texto) < 4:
                continue

            # Crear registro automático
            deteccion = DeteccionPlaca(
                placa=placa_texto,
                confianza=placa_data.get('confianza_deteccion', 0.0),
                imagen_path=f"Outputs/capturas_dashboard/captura_{timestamp}.jpg"
            )

            # Registrar en el sistema (reutilizar lógica existente)
            resultado_registro = await registrar_entrada(deteccion)

            detecciones_procesadas.append({
                "placa": placa_texto,
                "confianza": placa_data.get('confianza_deteccion', 0.0),
                "registro": resultado_registro
            })

        # Limpiar archivo temporal
        temp_path.unlink(missing_ok=True)

        return {
            "success": True,
            "mensaje": f"Se detectaron {len(detecciones_procesadas)} placa(s)",
            "detecciones": detecciones_procesadas,
            "total": len(detecciones_procesadas)
        }

    except Exception as e:
        print(f"[ERROR] Error procesando captura: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al procesar imagen: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint para actualizaciones en tiempo real.
    Los clientes se conectan aquí y reciben notificaciones cuando hay nuevas detecciones.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Mantener la conexión abierta
            data = await websocket.receive_text()
            # Opcionalmente procesar mensajes del cliente
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)

@app.post("/api/procesar-batch")
async def procesar_batch_endpoint():
    """
    Ejecuta el procesamiento batch de todas las imágenes en Inputs.

    Returns:
        dict: Estado del procesamiento
    """
    import subprocess

    try:
        # Ejecutar el script de procesamiento batch
        proceso = subprocess.Popen(
            ['python', 'process_batch.py', '--input', 'Inputs', '--output', 'Outputs',
             '--model', 'best.pt', '--truck-model', 'best_truck.pt'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return {
            "status": "iniciado",
            "mensaje": "Procesamiento batch iniciado en segundo plano",
            "pid": proceso.pid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar procesamiento: {str(e)}")

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Falcon EPSA Dashboard API"}


if __name__ == "__main__":
    print(">> Iniciando API Dashboard...")
    print(">> Servidor: http://localhost:8001")
    print(">> Documentacion: http://localhost:8001/docs")
    print(">> Redoc: http://localhost:8001/redoc")
    start_ffmpeg()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
