"""
Detecta cámaras disponibles intentando índices 0..N y varios backends (útil en Windows).
Ejecuta:
  python detect_cams.py

Salida: lista de (indice, backend, status) y resolución leída.
"""
import cv2
import sys
import platform


def preferred_backends():
    b = []
    plat = sys.platform.lower()
    if plat.startswith('win'):
        if hasattr(cv2, 'CAP_DSHOW'):
            b.append(('CAP_DSHOW', cv2.CAP_DSHOW))
        if hasattr(cv2, 'CAP_MSMF'):
            b.append(('CAP_MSMF', cv2.CAP_MSMF))
        if hasattr(cv2, 'CAP_FFMPEG'):
            b.append(('CAP_FFMPEG', cv2.CAP_FFMPEG))
    elif plat.startswith('darwin'):
        if hasattr(cv2, 'CAP_AVFOUNDATION'):
            b.append(('CAP_AVFOUNDATION', cv2.CAP_AVFOUNDATION))
        if hasattr(cv2, 'CAP_QT'):
            b.append(('CAP_QT', cv2.CAP_QT))
    else:
        if hasattr(cv2, 'CAP_V4L2'):
            b.append(('CAP_V4L2', cv2.CAP_V4L2))
        if hasattr(cv2, 'CAP_FFMPEG'):
            b.append(('CAP_FFMPEG', cv2.CAP_FFMPEG))
    return b


def try_open(index, api=None, timeout_frames=3):
    try:
        if api is None:
            cap = cv2.VideoCapture(index)
        else:
            cap = cv2.VideoCapture(index, api)
        if not cap or not cap.isOpened():
            try:
                cap.release()
            except Exception:
                pass
            return None
        # grab a few frames to let camera warm up
        for _ in range(timeout_frames):
            ret, frame = cap.read()
            if ret and frame is not None:
                h, w = frame.shape[:2]
                return cap, (w, h)
        # if we couldn't read a frame, treat as failure
        try:
            cap.release()
        except Exception:
            pass
        return None
    except Exception:
        return None


def main(max_index=6):
    print('Platform:', platform.platform())
    print('Python:', sys.version.replace('\n',''))
    print('OpenCV:', cv2.__version__)
    backends = preferred_backends()
    print('Backends to try:', [name for name, _ in backends])
    print('\nProbing camera indices 0..{} (and trying backends)'.format(max_index))

    found = []
    for idx in range(0, max_index+1):
        # try default first
        res = try_open(idx, None)
        if res:
            cap, size = res
            w,h = size
            print(f"Index {idx} - DEFAULT -> OK ({w}x{h})")
            found.append((idx, 'DEFAULT', (w,h)))
            cap.release()
            continue
        # try each backend
        ok = False
        for name, api in backends:
            res = try_open(idx, api)
            if res:
                cap, size = res
                w,h = size
                print(f"Index {idx} - {name} -> OK ({w}x{h})")
                found.append((idx, name, (w,h)))
                try:
                    cap.release()
                except Exception:
                    pass
                ok = True
                break
        if not ok:
            print(f"Index {idx} -> not available")

    if not found:
        print('\nNo se detectaron cámaras con índices 0..{} y backends probados.'.format(max_index))
        print('Si usas WSL o entornos virtualizados, recuerda que la cámara puede no estar disponible. En Windows, cierra apps que puedan estar usando la cámara (Teams/Zoom) y asegúrate de permitir el acceso a la cámara en Configuración > Privacidad.')
    else:
        print('\nCámaras detectadas:')
        for idx, backend, size in found:
            print(f" - Index {idx} via {backend} at {size[0]}x{size[1]}")

    print('\nSi encuentras un índice OK, úsalo con --cam-index en la dashboard o en app.py (ej: --cam-index', found[0][0] if found else 0, ')')

if __name__ == '__main__':
    main(max_index=8)
