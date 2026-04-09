#!/usr/bin/env python3
"""
SentinelFlow Edge - LogicalSolutions
Talent Hackathon 2026 | Qualcomm Sustainable Power Cities
"""

import cv2
import sys
import time
import signal
import os
import subprocess
import serial
from edge_impulse_linux.image import ImageImpulseRunner

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
MODEL_PATH      = "/app/python/modelo.eim"
MODEL_URL       = "https://studio.edgeimpulse.com/v1/api/953412/deployment/history/2/download"
API_KEY         = "ei_906947574aeb8f064146eddf5d91fb18772e6df1f1650192"
CAMERA_INDEX    = 0
ALERT_LABEL     = "rio_peligro"
ALERT_THRESHOLD = 0.75

SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUD = 115200

def ensure_model():
    """Descarga el modelo si no existe o no es ejecutable."""
    if os.path.exists(MODEL_PATH):
        # Verificar que es ELF leyendo los primeros bytes
        with open(MODEL_PATH, 'rb') as f:
            magic = f.read(4)
        if magic == b'\x7fELF':
            print("[Modelo] ✅ Ya existe y es válido.")
            return
        else:
            print("[Modelo] Archivo corrupto, re-descargando...")
            os.remove(MODEL_PATH)

    print("[Modelo] Descargando desde Edge Impulse...")
    ret = os.system(
        f'curl -H "x-api-key: {API_KEY}" "{MODEL_URL}" -L -o {MODEL_PATH} --silent'
    )
    if ret != 0:
        print("[ERROR] Falló la descarga del modelo")
        sys.exit(1)

    os.chmod(MODEL_PATH, 0o755)

    with open(MODEL_PATH, 'rb') as f:
        magic = f.read(4)

    if magic != b'\x7fELF':
        print("[ERROR] El archivo descargado no es un ELF válido")
        sys.exit(1)

    print("[Modelo] ✅ Descarga exitosa")

def init_serial():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        time.sleep(2)
        print("[Serial] Conectado OK")
        return ser
    except Exception as e:
        print(f"[Serial] Sin conexión serial: {e}")
        return None

def send_command(ser, level):
    if ser and ser.is_open:
        try:
            ser.write(f"{level}\n".encode())
        except Exception as e:
            print(f"[Serial] Error: {e}")

def run():
    print("========================================")
    print("   SentinelFlow Edge - ARRANCANDO")
    print("========================================")

    ensure_model()
    ser = init_serial()

    with ImageImpulseRunner(MODEL_PATH) as runner:
        info = runner.init()
        print(f"[Modelo] {info['project']['name']}")
        print(f"[Modelo] Labels: {info['model_parameters']['labels']}")

        w = info['model_parameters']['image_input_width']
        h = info['model_parameters']['image_input_height']
        print(f"[Modelo] Input: {w}x{h} px")

        cap = cv2.VideoCapture(CAMERA_INDEX)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print(f"[ERROR] Cámara no encontrada en índice {CAMERA_INDEX}")
            sys.exit(1)

        print("[Cámara] Logitech Brio lista")
        print("[Sistema] Corriendo... Ctrl+C para detener\n")

        last_state = "NORMAL"

        def cleanup(sig, frame):
            print("\n[Sistema] Apagando...")
            send_command(ser, "NORMAL")
            cap.release()
            if ser:
                ser.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, cleanup)

        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.3)
                continue

            img = cv2.resize(frame, (w, h))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            features, _ = runner.get_features_from_image(img_rgb)
            result = runner.classify(features)

            if "classification" in result["result"]:
                preds = result["result"]["classification"]
                line = "  ".join([f"{k}: {v:.2f}" for k, v in preds.items()])
                print(f"[Inferencia] {line}")

                top = max(preds, key=preds.get)
                conf = preds[top]

                if top == ALERT_LABEL and conf >= ALERT_THRESHOLD:
                    state = "DANGER"
                    print(f"  🚨 RIO EN PELIGRO — {conf:.1%}")
                elif top == ALERT_LABEL and conf >= 0.50:
                    state = "WARNING"
                    print(f"  ⚠️  ANOMALÍA — {conf:.1%}")
                else:
                    state = "NORMAL"

                if state != last_state:
                    send_command(ser, state)
                    last_state = state

            time.sleep(0.1)

if __name__ == "__main__":
    run()