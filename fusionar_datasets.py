# -*- coding: utf-8 -*-
"""
Script para fusionar dos datasets YOLO en uno solo
Ajusta automáticamente los class_id antes de subir a Google Colab

Uso:
    python fusionar_datasets.py --camiones dataset_camiones/ --placas dataset_placas/ --salida dataset_fusionado/
"""

import os
import shutil
import argparse
from pathlib import Path


def ajustar_clase_en_label(archivo_label, nueva_clase):
    """
    Lee un archivo .txt de labels YOLO y cambia el class_id.
    
    Formato YOLO: class_id x_center y_center width height
    Ejemplo: 0 0.5 0.5 0.2 0.3
    """
    with open(archivo_label, 'r') as f:
        lineas = f.readlines()
    
    lineas_ajustadas = []
    for linea in lineas:
        partes = linea.strip().split()
        if len(partes) >= 5:
            # Cambiar el class_id (primera columna)
            partes[0] = str(nueva_clase)
            lineas_ajustadas.append(' '.join(partes) + '\n')
    
    return lineas_ajustadas


def fusionar_datasets(dataset_camiones, dataset_placas, dataset_salida):
    """
    Fusiona dos datasets YOLO en uno solo.
    
    Args:
        dataset_camiones (str): Ruta al dataset de camiones
        dataset_placas (str): Ruta al dataset de placas
        dataset_salida (str): Ruta donde guardar el dataset fusionado
    """
    print("🔄 Iniciando fusión de datasets...")
    
    # Crear estructura de directorios
    subdirs = ['images/train', 'images/val', 'labels/train', 'labels/val']
    for subdir in subdirs:
        os.makedirs(os.path.join(dataset_salida, subdir), exist_ok=True)
    
    datasets = [
        {'nombre': 'camiones', 'ruta': dataset_camiones, 'clase_nueva': 0, 'prefijo': 'truck_'},
        {'nombre': 'placas', 'ruta': dataset_placas, 'clase_nueva': 1, 'prefijo': 'plate_'}
    ]
    
    stats = {'train': {'imagenes': 0, 'labels': 0}, 'val': {'imagenes': 0, 'labels': 0}}
    
    # Procesar cada dataset
    for dataset in datasets:
        nombre = dataset['nombre']
        ruta = dataset['ruta']
        clase_nueva = dataset['clase_nueva']
        prefijo = dataset['prefijo']
        
        print(f"\n📁 Procesando dataset de {nombre}...")
        print(f"   Clase asignada: {clase_nueva}")
        
        # Procesar train y val
        for split in ['train', 'val']:
            ruta_imagenes = os.path.join(ruta, 'images', split)
            ruta_labels = os.path.join(ruta, 'labels', split)
            
            if not os.path.exists(ruta_imagenes):
                print(f"   ⚠️  No se encontró {split}/images en {nombre}, saltando...")
                continue
            
            # Copiar imágenes
            archivos_imagen = list(Path(ruta_imagenes).glob('*'))
            for img_path in archivos_imagen:
                if img_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp']:
                    # Nuevo nombre con prefijo para evitar colisiones
                    nuevo_nombre = prefijo + img_path.name
                    destino = os.path.join(dataset_salida, 'images', split, nuevo_nombre)
                    shutil.copy2(img_path, destino)
                    stats[split]['imagenes'] += 1
            
            # Procesar y copiar labels
            if os.path.exists(ruta_labels):
                archivos_label = list(Path(ruta_labels).glob('*.txt'))
                for label_path in archivos_label:
                    # Ajustar class_id
                    lineas_ajustadas = ajustar_clase_en_label(label_path, clase_nueva)
                    
                    # Nuevo nombre con prefijo
                    nuevo_nombre = prefijo + label_path.name
                    destino = os.path.join(dataset_salida, 'labels', split, nuevo_nombre)
                    
                    with open(destino, 'w') as f:
                        f.writelines(lineas_ajustadas)
                    
                    stats[split]['labels'] += 1
    
    # Crear archivo YAML
    yaml_content = f"""# Dataset Fusionado: Camiones + Placas
path: {os.path.abspath(dataset_salida)}
train: images/train
val: images/val

# Clases
nc: 2
names: ['camion', 'placa']

# Estadísticas
# Train: {stats['train']['imagenes']} imágenes, {stats['train']['labels']} labels
# Val: {stats['val']['imagenes']} imágenes, {stats['val']['labels']} labels
"""
    
    yaml_path = os.path.join(dataset_salida, 'dataset.yaml')
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print("\n✅ Fusión completada!")
    print(f"\n📊 Estadísticas:")
    print(f"   Train: {stats['train']['imagenes']} imágenes, {stats['train']['labels']} labels")
    print(f"   Val: {stats['val']['imagenes']} imágenes, {stats['val']['labels']} labels")
    print(f"\n📄 Archivo YAML creado: {yaml_path}")
    print(f"\n📦 Listo para subir a Google Colab: {os.path.abspath(dataset_salida)}")
    print("\n💡 Siguiente paso:")
    print(f"   1. Comprime la carpeta: zip -r dataset_fusionado.zip {dataset_salida}")
    print(f"   2. Sube el .zip a Google Drive")
    print(f"   3. Usa el notebook de entrenamiento en Colab")


def main():
    parser = argparse.ArgumentParser(
        description='Fusiona datasets YOLO de camiones y placas para entrenar un modelo unificado'
    )
    
    parser.add_argument(
        '--camiones',
        required=True,
        help='Ruta al dataset de camiones (debe tener images/ y labels/)'
    )
    
    parser.add_argument(
        '--placas',
        required=True,
        help='Ruta al dataset de placas (debe tener images/ y labels/)'
    )
    
    parser.add_argument(
        '--salida',
        default='dataset_fusionado',
        help='Ruta donde guardar el dataset fusionado (default: dataset_fusionado)'
    )
    
    args = parser.parse_args()
    
    # Validar que existan los directorios
    for nombre, ruta in [('camiones', args.camiones), ('placas', args.placas)]:
        if not os.path.exists(ruta):
            print(f"❌ Error: No se encontró el dataset de {nombre}: {ruta}")
            return
    
    fusionar_datasets(args.camiones, args.placas, args.salida)
    
    print("\n🚀 ¡Todo listo para Google Colab!")


if __name__ == '__main__':
    main()
