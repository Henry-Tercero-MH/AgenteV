#!/usr/bin/env python3
"""Debug helper to run truck and plate models on a single image and print/save detections.

Usage:
  python debug_models.py --image Inputs/truck.jpg --truck best_truck.pt --plate best.pt --out Outputs

This will print detected boxes, classes and confidences and save annotated images.
"""
import os
import argparse
import cv2
import numpy as np
from ultralytics import YOLO


def draw_boxes(img, boxes, confs=None, classes=None, color=(0,255,0), label_prefix=''):
    out = img.copy()
    for i, b in enumerate(boxes):
        x1, y1, x2, y2 = [int(v) for v in b]
        cv2.rectangle(out, (x1,y1), (x2,y2), color, 2)
        lab = ''
        if classes is not None:
            lab += f"{classes[i]}"
        if confs is not None:
            lab += f" {confs[i]:.2f}"
        if lab:
            cv2.putText(out, label_prefix + lab, (x1, max(12, y1-4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)
    return out


def to_numpy(x):
    try:
        return x.cpu().numpy()
    except Exception:
        try:
            return np.array(x)
        except Exception:
            return np.array([])


def run_debug(image_path, truck_model_path, plate_model_path, out_dir, conf_thresh=0.3, show=False):
    os.makedirs(out_dir, exist_ok=True)
    img = cv2.imread(image_path)
    if img is None:
        print('ERROR: could not read image', image_path)
        return

    print('Image:', image_path, 'shape=', img.shape)

    plate_model = None
    truck_model = None
    if plate_model_path and os.path.exists(plate_model_path):
        plate_model = YOLO(plate_model_path)
        print('Loaded plate model:', plate_model_path)
    else:
        print('Plate model not provided or not found:', plate_model_path)

    if truck_model_path and os.path.exists(truck_model_path):
        truck_model = YOLO(truck_model_path)
        print('Loaded truck model:', truck_model_path)
    else:
        print('Truck model not provided or not found:', truck_model_path)

    # Run truck model if available
    truck_boxes = []
    if truck_model is not None:
        print('\n=== Running truck model ===')
        t_res = truck_model(img)
        for r in t_res:
            if not hasattr(r, 'boxes'):
                continue
            xyxy = to_numpy(r.boxes.xyxy)
            confs = to_numpy(r.boxes.conf).flatten() if hasattr(r.boxes, 'conf') else None
            cls = to_numpy(r.boxes.cls).astype(int).flatten() if hasattr(r.boxes, 'cls') else None
            print('Raw truck detections count =', 0 if xyxy is None else xyxy.shape[0])
            if xyxy is None or xyxy.size == 0:
                continue
            for i in range(xyxy.shape[0]):
                c = float(confs[i]) if confs is not None else 1.0
                label = cls[i] if cls is not None else None
                print(f'  truck #{i}: box={xyxy[i].tolist()} conf={c:.3f} class={label}')
                if c >= conf_thresh:
                    truck_boxes.append(xyxy[i].astype(int).tolist())

        debug_truck = draw_boxes(img, truck_boxes, confs=[1.0]*len(truck_boxes), classes=[0]*len(truck_boxes), color=(0,128,255), label_prefix='T:')
        truck_outp = os.path.join(out_dir, 'debug_truck.jpg')
        cv2.imwrite(truck_outp, debug_truck)
        print('Saved truck annotated image ->', truck_outp)

    # If truck boxes found, run plate model inside each; otherwise run on full image
    regions = []
    if truck_boxes:
        h, w = img.shape[:2]
        for (x1,y1,x2,y2) in truck_boxes:
            x1p = max(0, x1 - 10)
            y1p = max(0, y1 - 10)
            x2p = min(w-1, x2 + 10)
            y2p = min(h-1, y2 + 10)
            regions.append((x1p,y1p,x2p,y2p))
    else:
        regions.append((0,0,img.shape[1], img.shape[0]))

    all_plate_boxes = []
    for ridx, (rx1,ry1,rx2,ry2) in enumerate(regions):
        crop = img[ry1:ry2, rx1:rx2]
        if crop.size == 0:
            continue
        if plate_model is None:
            continue
        print(f'\n=== Running plate model on region {ridx} size={crop.shape} ===')
        p_res = plate_model(crop)
        for r in p_res:
            if not hasattr(r, 'boxes'):
                continue
            xyxy = to_numpy(r.boxes.xyxy)
            confs = to_numpy(r.boxes.conf).flatten() if hasattr(r.boxes, 'conf') else None
            cls = to_numpy(r.boxes.cls).astype(int).flatten() if hasattr(r.boxes, 'cls') else None
            print('Raw plate detections count =', 0 if xyxy is None else xyxy.shape[0])
            if xyxy is None or xyxy.size == 0:
                continue
            for i in range(xyxy.shape[0]):
                c = float(confs[i]) if confs is not None else 1.0
                label = cls[i] if cls is not None else None
                bx = xyxy[i].astype(int).tolist()
                # map to full image coords
                bx_full = [bx[0]+rx1, bx[1]+ry1, bx[2]+rx1, bx[3]+ry1]
                print(f'  plate #{i}: box={bx_full} conf={c:.3f} class={label}')
                if c >= conf_thresh:
                    all_plate_boxes.append((bx_full, c, label))

    # Draw plates
    if all_plate_boxes:
        boxes = [b for (b,_,_) in all_plate_boxes]
        confs = [c for (_,c,_) in all_plate_boxes]
        classes = [cl for (_,_,cl) in all_plate_boxes]
        debug_plate = draw_boxes(img, boxes, confs=confs, classes=classes, color=(0,255,0), label_prefix='P:')
        plate_outp = os.path.join(out_dir, 'debug_plates.jpg')
        cv2.imwrite(plate_outp, debug_plate)
        print('Saved plate annotated image ->', plate_outp)
    else:
        print('\nNo plates with conf >=', conf_thresh)

    if show:
        try:
            cv2.imshow('Debug truck', debug_truck if truck_boxes else img)
            if all_plate_boxes:
                cv2.imshow('Debug plates', debug_plate)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image', default='Inputs/truck.jpg')
    parser.add_argument('--truck', default='best_truck.pt')
    parser.add_argument('--plate', default='best.pt')
    parser.add_argument('--out', default='Outputs')
    parser.add_argument('--conf', type=float, default=0.3)
    parser.add_argument('--show', action='store_true')
    args = parser.parse_args()
    run_debug(args.image, args.truck, args.plate, args.out, conf_thresh=args.conf, show=args.show)
