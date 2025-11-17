# -*- coding: utf-8 -*-
"""
Script de prueba para simular detecciones de placas
y probar el flujo completo del sistema de control de garita
"""
import requests
import time
import random

API_URL = "http://localhost:8001"

# Placas de prueba (algunas registradas, otras no)
PLACAS_PRUEBA = [
    {"placa": "PO28GHQ", "confianza": 0.95},  # Registrada
    {"placa": "GC987D", "confianza": 0.92},   # Registrada
    {"placa": "NCV896", "confianza": 0.88},   # Registrada
    {"placa": "ABC123", "confianza": 0.91},   # No registrada
    {"placa": "XYZ789", "confianza": 0.89},   # No registrada
]

def simular_deteccion(placa_data):
    """
    Simula una detección de placa enviándola al API
    """
    endpoint = f"{API_URL}/api/registros/entrada"

    payload = {
        "placa": placa_data["placa"],
        "confianza": placa_data["confianza"],
        "imagen_path": None  # Opcional
    }

    print(f"\n🚗 Simulando detección de placa: {placa_data['placa']}")
    print(f"   Confianza: {placa_data['confianza'] * 100:.1f}%")

    try:
        response = requests.post(endpoint, json=payload)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Registro exitoso!")
            print(f"   ID Registro: {data['registro']['id']}")
            print(f"   Timestamp: {data['registro']['timestamp']}")
            print(f"   Registrada en DB: {'SÍ' if data['registrada'] else 'NO'}")

            if data['registrada']:
                info = data['placa_info']
                print(f"\n📋 Información del vehículo:")
                print(f"   Propietario: {info['propietario']}")
                print(f"   Tipo: {info['tipo_vehiculo']}")
                print(f"   Estado: {info['estado']}")
                print(f"   Departamento: {info['departamento']}")
            else:
                print(f"\n⚠️  {data['mensaje']}")

            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error al conectar con el API: {e}")
        return False

def verificar_conexion():
    """
    Verifica que el API esté corriendo
    """
    try:
        response = requests.get(f"{API_URL}/health")
        if response.status_code == 200:
            print("✅ API conectada correctamente")
            return True
        else:
            print("❌ API no responde correctamente")
            return False
    except:
        print("❌ No se puede conectar al API. ¿Está corriendo en el puerto 8001?")
        return False

def mostrar_historial():
    """
    Muestra el historial de registros
    """
    try:
        response = requests.get(f"{API_URL}/api/registros/historial?limit=10")
        if response.status_code == 200:
            data = response.json()
            print("\n📊 Últimos 10 registros:")
            print("-" * 80)
            for reg in data['registros'][:10]:
                estado = "✓ Registrada" if reg['registrada'] else "✗ No registrada"
                print(f"#{reg['id']:3d} | {reg['placa']:10s} | {reg['tipo_evento']:8s} | {estado}")
            print("-" * 80)
            print(f"Total de registros: {data['total']}")
    except Exception as e:
        print(f"Error al obtener historial: {e}")

def menu_principal():
    """
    Menú interactivo para pruebas
    """
    print("\n" + "="*60)
    print("🦅 FALCON EPSA - Sistema de Control de Garita")
    print("   Simulador de Detecciones")
    print("="*60)

    if not verificar_conexion():
        print("\n⚠️  Inicia el API primero con: python api_dashboard.py")
        return

    while True:
        print("\n" + "-"*60)
        print("Opciones:")
        print("  1. Simular detección de placa registrada")
        print("  2. Simular detección de placa NO registrada")
        print("  3. Simular múltiples detecciones (modo automático)")
        print("  4. Ver historial de registros")
        print("  5. Probar WebSocket (manual)")
        print("  0. Salir")
        print("-"*60)

        opcion = input("\nSelecciona una opción: ").strip()

        if opcion == "1":
            # Placa registrada
            placa = random.choice([p for p in PLACAS_PRUEBA if p["placa"] in ["PO28GHQ", "GC987D", "NCV896"]])
            simular_deteccion(placa)

        elif opcion == "2":
            # Placa NO registrada
            placa = random.choice([p for p in PLACAS_PRUEBA if p["placa"] in ["ABC123", "XYZ789"]])
            simular_deteccion(placa)

        elif opcion == "3":
            # Modo automático
            cantidad = input("¿Cuántas detecciones simular? (default: 5): ").strip()
            cantidad = int(cantidad) if cantidad.isdigit() else 5

            intervalo = input("¿Intervalo entre detecciones en segundos? (default: 3): ").strip()
            intervalo = float(intervalo) if intervalo else 3.0

            print(f"\n🚀 Simulando {cantidad} detecciones con intervalo de {intervalo}s")
            print("   Presiona Ctrl+C para detener\n")

            try:
                for i in range(cantidad):
                    placa = random.choice(PLACAS_PRUEBA)
                    print(f"\n[{i+1}/{cantidad}]", end=" ")
                    simular_deteccion(placa)

                    if i < cantidad - 1:
                        print(f"   ⏳ Esperando {intervalo}s...")
                        time.sleep(intervalo)

                print(f"\n✅ Simulación completada: {cantidad} detecciones enviadas")

            except KeyboardInterrupt:
                print("\n\n⚠️  Simulación detenida por el usuario")

        elif opcion == "4":
            mostrar_historial()

        elif opcion == "5":
            print("\n📡 Para probar WebSocket:")
            print("   1. Abre el dashboard React en el navegador")
            print("   2. Abre la consola del navegador (F12)")
            print("   3. Ejecuta esta opción (1, 2 o 3)")
            print("   4. Observa las actualizaciones en tiempo real en el dashboard")
            input("\nPresiona Enter para continuar...")

        elif opcion == "0":
            print("\n👋 ¡Hasta luego!")
            break

        else:
            print("\n❌ Opción no válida")

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
