# -*- coding: utf-8 -*-
"""
Script para generar base de datos de placas registradas
Extrae todas las placas detectadas y las guarda en un JSON simulando una DB
"""
import json
from datetime import datetime
import random

def generar_db_placas():
    """
    Genera base de datos de placas a partir de los resultados del procesamiento
    """
    # Leer resultados del procesamiento
    with open('Outputs/resultados_dashboard.json', 'r', encoding='utf-8') as f:
        datos = json.load(f)

    placas_db = []
    placa_id = 1

    # Estados posibles
    estados = ['AUTORIZADO', 'RESTRINGIDO', 'SUSPENDIDO', 'NORMAL']
    tipos_vehiculo = ['PARTICULAR', 'COMERCIAL', 'TRANSPORTE', 'OFICIAL', 'DIPLOMATICO']
    departamentos = ['Guatemala', 'Sacatepéquez', 'Chimaltenango', 'Escuintla', 'Quetzaltenango',
                     'Huehuetenango', 'Alta Verapaz', 'Petén', 'Izabal', 'Jalapa']

    # Extraer todas las placas con texto
    for resultado in datos['resultados']:
        if resultado['detecciones']:
            for deteccion in resultado['detecciones']:
                if deteccion['texto']:
                    # Generar datos simulados para la placa
                    estado = random.choice(estados)

                    placa_info = {
                        "id": placa_id,
                        "placa": deteccion['texto'],
                        "estado": estado,
                        "tipo_vehiculo": random.choice(tipos_vehiculo),
                        "propietario": f"Propietario {placa_id}",
                        "departamento": random.choice(departamentos),
                        "fecha_registro": datetime.now().strftime("%Y-%m-%d"),
                        "vigencia": "2025-12-31" if estado != "SUSPENDIDO" else "2024-12-31",
                        "observaciones": "Sin observaciones" if estado == "NORMAL" else f"Estado: {estado}",
                        "ultima_deteccion": resultado['timestamp'],
                        "imagen_origen": resultado['nombre_imagen']
                    }

                    placas_db.append(placa_info)
                    placa_id += 1

    # Crear estructura de la base de datos
    db = {
        "metadata": {
            "fecha_generacion": datetime.now().isoformat(),
            "total_placas": len(placas_db),
            "version": "1.0"
        },
        "placas": placas_db
    }

    # Guardar en archivo JSON
    with open('database/placas_db.json', 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

    print(f">> Base de datos generada exitosamente")
    print(f">> Total de placas registradas: {len(placas_db)}")
    print(f">> Archivo: database/placas_db.json")

    # Mostrar resumen por estado
    print("\nResumen por estado:")
    for estado in estados:
        count = sum(1 for p in placas_db if p['estado'] == estado)
        print(f"  - {estado}: {count} placas")

if __name__ == "__main__":
    import os

    # Crear directorio database si no existe
    if not os.path.exists('database'):
        os.makedirs('database')

    generar_db_placas()
