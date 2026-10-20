"""
Street Fighter III: 3rd Strike - Live Azure Kinect Static Posture Classifier
Detector somatosensorial en vivo con soporte para hardware físico Azure Kinect DK y simulador:
- Esqueleto Dual en tiempo real (Vista Frontal X-Y + Vista Sagital Z-Y de Perfil).
- Clasificación de Poses Sostenidas (Held Poses) invariante a la velocidad con 44 características geométricas.
- Periodo de Calibración/Estabilización inicial (1.5s) al detectar al jugador para evitar animaciones espontáneas.
- Validación biomecánica anti-falsos positivos y activación continua tras 0.5s de sostener la postura.
"""

import os
import sys
import time
import socket
import json
import argparse
import collections
import numpy as np
import pandas as pd
import cv2
import joblib

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Importar módulos posturales locales
sys.path.append(os.path.dirname(__file__))
from gesture_feature_extractor import (
    ACTION_CLASSES,
    ACTION_ID_TO_NAME,
    ACTION_NAME_TO_ID,
    FEATURE_NAMES,
    extract_clip_features,
    validate_posture_biomechanics
)

# Intentar importar pykinect_azure
HAS_PYKINECT = False
try:
    import pykinect_azure as pykinect
    HAS_PYKINECT = True
except ImportError:
    HAS_PYKINECT = False

# 18 articulaciones clave para visualización
SIMPLIFIED_JOINTS = {
    "pelvis": 0, "pecho": 2, "cuello": 3, "cabeza": 26,
    "hombro_izq": 5, "codo_izq": 6, "muneca_izq": 7, "mano_izq": 8,
    "hombro_der": 12, "codo_der": 13, "muneca_der": 14, "mano_der": 15,
    "cadera_izq": 18, "rodilla_izq": 19, "tobillo_izq": 20, "pie_izq": 21,
    "cadera_der": 22, "rodilla_der": 23, "tobillo_der": 24, "pie_der": 25
}

SIMPLIFIED_BONES = [
    ("pelvis", "pecho", (0, 220, 255)),
    ("pecho", "cuello", (0, 220, 255)),
    ("cuello", "cabeza", (0, 255, 255)),
    ("pecho", "hombro_izq", (255, 120, 0)),
    ("hombro_izq", "codo_izq", (255, 80, 0)),
    ("codo_izq", "muneca_izq", (255, 40, 0)),
    ("muneca_izq", "mano_izq", (255, 20, 0)),
    ("pecho", "hombro_der", (0, 100, 255)),
    ("hombro_der", "codo_der", (0, 60, 255)),
    ("codo_der", "muneca_der", (0, 20, 255)),
    ("muneca_der", "mano_der", (0, 10, 255)),
    ("pelvis", "cadera_izq", (255, 140, 30)),
    ("cadera_izq", "rodilla_izq", (255, 90, 0)),
    ("rodilla_izq", "tobillo_izq", (255, 40, 0)),
    ("tobillo_izq", "pie_izq", (255, 30, 0)),
    ("pelvis", "cadera_der", (30, 80, 255)),
    ("cadera_der", "rodilla_der", (0, 50, 255)),
    ("rodilla_der", "tobillo_der", (0, 20, 255)),
    ("tobillo_der", "pie_der", (0, 10, 255))
]


# -----------------------------------------------------------------------------
# SIMULADOR PROCEDURAL (FALLBACK / MOCK)
# -----------------------------------------------------------------------------
class MockKinematicSensor:
    def __init__(self):
        self.base_skeleton = np.zeros((32, 3), dtype=np.float32)
        self._init_base_pose()
        self.current_action = "idle"
        self.target_action = "idle"

    def _init_base_pose(self):
        # Coordenadas en metros estilo Azure Kinect (+Y hacia abajo, +Z profundidad)
        self.base_skeleton[0] = [0.0, 0.05, 2.20]     # Pelvis
        self.base_skeleton[1] = [0.0, -0.12, 2.19]    # Spine Navel
        self.base_skeleton[2] = [0.0, -0.28, 2.18]    # Spine Chest
        self.base_skeleton[3] = [0.0, -0.44, 2.18]    # Neck
        self.base_skeleton[26] = [0.0, -0.58, 2.16]   # Head
        # Brazo izquierdo en guardia neutral relajada
        self.base_skeleton[5] = [-0.18, -0.38, 2.18]  # Shoulder Left
        self.base_skeleton[6] = [-0.24, -0.12, 2.12]  # Elbow Left
        self.base_skeleton[7] = [-0.18, -0.24, 1.98]  # Wrist Left
        self.base_skeleton[8] = [-0.16, -0.26, 1.92]  # Hand Left
        # Brazo derecho en guardia neutral relajada
        self.base_skeleton[12] = [0.18, -0.38, 2.18]  # Shoulder Right
        self.base_skeleton[13] = [0.24, -0.12, 2.12]  # Elbow Right
        self.base_skeleton[14] = [0.18, -0.22, 2.02]  # Wrist Right
        self.base_skeleton[15] = [0.16, -0.24, 1.96]  # Hand Right
        # Piernas de pie
        self.base_skeleton[18] = [-0.10, 0.05, 2.20]  # Hip Left
        self.base_skeleton[19] = [-0.12, 0.44, 2.20]  # Knee Left
        self.base_skeleton[20] = [-0.13, 0.82, 2.22]  # Ankle Left
        self.base_skeleton[21] = [-0.13, 0.88, 2.12]  # Foot Left
        self.base_skeleton[22] = [0.10, 0.05, 2.20]   # Hip Right
        self.base_skeleton[23] = [0.12, 0.44, 2.20]   # Knee Right
        self.base_skeleton[24] = [0.13, 0.82, 2.22]   # Ankle Right
        self.base_skeleton[25] = [0.13, 0.88, 2.12]   # Foot Right

    def trigger_action(self, target_act: str):
        self.current_action = target_act
        self.target_action = target_act

    def get_frame(self) -> np.ndarray:
        frame = self.base_skeleton.copy()
        t = time.time()
        frame[:, 1] += np.sin(t * 2.2) * 0.003

        act = self.target_action
        if act == "punch_right":
            frame[13] = [0.22, -0.36, 1.92]
            frame[14] = [0.20, -0.38, 1.62]
            frame[15] = [0.20, -0.38, 1.54]
        elif act == "punch_left":
            frame[6] = [-0.22, -0.36, 1.92]
            frame[7] = [-0.20, -0.38, 1.62]
            frame[8] = [-0.20, -0.38, 1.54]
        elif act == "kick_right":
            frame[23] = [0.14, 0.15, 1.92]
            frame[24] = [0.15, 0.25, 1.65]
            frame[25] = [0.15, 0.22, 1.55]
        elif act == "kick_left":
            frame[19] = [-0.14, 0.15, 1.92]
            frame[20] = [-0.15, 0.25, 1.65]
            frame[21] = [-0.15, 0.22, 1.55]
        elif act == "crouch":
            # Pelvis y torso bajan (+Y), tobillos permanecen en el piso
            frame[[0, 1, 2, 3, 5, 6, 7, 8, 12, 13, 14, 15, 18, 22, 26], 1] += 0.36
            frame[19] = [-0.18, 0.58, 2.02]
            frame[23] = [0.18, 0.58, 2.02]
        elif act == "block":
            # Ambos brazos arriba cubriendo pecho y cabeza
            frame[13] = [0.22, -0.28, 1.95]
            frame[14] = [0.10, -0.48, 1.90]
            frame[15] = [0.08, -0.54, 1.88]
            frame[6] = [-0.22, -0.28, 1.95]
            frame[7] = [-0.10, -0.48, 1.90]
            frame[8] = [-0.08, -0.54, 1.88]

        return frame


def draw_skeleton(canvas, joint_screen_pts):
    for start_name, end_name, b_color in SIMPLIFIED_BONES:
        if start_name in joint_screen_pts and end_name in joint_screen_pts:
            pt1 = tuple(joint_screen_pts[start_name].astype(int))
            pt2 = tuple(joint_screen_pts[end_name].astype(int))
            cv2.line(canvas, pt1, pt2, b_color, 3, cv2.LINE_AA)

    for name, pt in joint_screen_pts.items():
        c = tuple(pt.astype(int))
        if "_der" in name:
            cv2.circle(canvas, c, 5, (0, 40, 255), -1, cv2.LINE_AA)
        elif "_izq" in name:
            cv2.circle(canvas, c, 5, (255, 60, 0), -1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, c, 6, (0, 240, 255), -1, cv2.LINE_AA)


# -----------------------------------------------------------------------------
# PROGRAMA PRINCIPAL
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SF3 Live Azure Kinect Static Posture Classifier")
    parser.add_argument("--mock", action="store_true", default=False,
                        help="Forzar modo simulador procedural (sin sensor físico)")
    parser.add_argument("--model", type=str, default=os.path.join(os.path.dirname(__file__), "gesture_classifier.joblib"),
                        help="Ruta al modelo entrenado (.joblib)")
    parser.add_argument("--unity-ip", type=str, default="127.0.0.1",
                        help="Dirección IP de destino para transmisión UDP a Unity (default: 127.0.0.1)")
    parser.add_argument("--unity-port", type=int, default=5005,
                        help="Puerto UDP de destino para Unity (default: 5005)")
    parser.add_argument("--hold-time", type=float, default=0.5,
                        help="Tiempo en segundos manteniendo una pose continua para activarla en Unity (default: 0.5s)")
    parser.add_argument("--warmup-time", type=float, default=1.5,
                        help="Tiempo de estabilización inicial al detectar cuerpo para evitar animaciones falsas (default: 1.5s)")
    parser.add_argument("--min-conf", type=float, default=0.48,
                        help="Confianza mínima requerida del clasificador postural (default: 0.48)")
    parser.add_argument("--no-stream", action="store_true", default=False,
                        help="Desactivar transmisión de paquetes UDP a Unity")
    args = parser.parse_args()

    print("=" * 80)
    print("🥊 SF3 - DETECTOR EN VIVO: CLASIFICADOR GEOMÉTRICO DE POSES SOSTENIDAS")
    print("=" * 80)

    # 1. Cargar modelo ML entrenado
    if not os.path.exists(args.model):
        print(f"❌ No se encontró el modelo: {args.model}")
        print("💡 Ejecuta primero: python Tools/train_gesture_classifier.py")
        sys.exit(1)

    model = joblib.load(args.model)
    model_classes = model.classes_
    print(f"🤖 Modelo ML cargado: {os.path.basename(args.model)}")
    print(f"   Clases registradas ({len(model_classes)}): {[ACTION_ID_TO_NAME[c] for c in model_classes]}")

    # 2. Inicializar Sensor (Azure Kinect DK o Mockup)
    use_mock = args.mock
    device = None
    body_tracker = None
    mock_sensor = MockKinematicSensor()

    if not use_mock and HAS_PYKINECT:
        k4a_path = r"C:\Program Files\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
        k4abt_path = r"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll"

        if not os.path.exists(k4a_path):
            k4a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k4a.dll"))
        if not os.path.exists(k4abt_path):
            k4abt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k4abt.dll"))

        try:
            print("🔌 Inicializando librerías del Azure Kinect SDK...")
            pykinect.initialize_libraries(module_k4a_path=k4a_path, module_k4abt_path=k4abt_path, track_body=True)
            device_config = pykinect.default_configuration
            device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
            device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
            device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

            print("🔌 Conectando con el hardware Azure Kinect DK...")
            device = pykinect.start_device(config=device_config)
            body_tracker = pykinect.start_body_tracker(model_type=pykinect.K4ABT_LITE_MODEL)
            print("✅ Azure Kinect DK físico conectado y rastreando a 30 FPS.")
        except Exception as ex:
            print(f"⚠️ No se pudo inicializar Azure Kinect físico ({ex}).")
            print("🔄 Activando automáticamente el simulador procedural interactivo (--mock).")
            use_mock = True
    else:
        use_mock = True
        print("🎮 Iniciando en modo simulador procedural (--mock).")

    # Configuración de transmisión UDP en tiempo real a Unity
    stream_sock = None
    if not args.no_stream:
        try:
            stream_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print(f"📡 Transmisor UDP hacia Unity inicializado -> {args.unity_ip}:{args.unity_port}")
        except Exception as ex:
            print(f"⚠️ Error al crear socket UDP ({ex}). Transmisión desactivada.")
            stream_sock = None
    else:
        print("ℹ️ Transmisión UDP desactivada (--no-stream).")
    last_stream_time = 0.0

    # 3. Variables de ventana e inferencia
    WINDOW_NAME = "KINECT STRIKE - Static Posture Studio"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    WIDTH = 1380
    HEIGHT = 780
    LEFT_W = 750
    RIGHT_W = 630

    rolling_buffer = collections.deque(maxlen=12)
    last_ml_time = 0.0

    # Estado actual
    pred_action = "idle"
    pred_conf = 1.0
    pred_probs = np.zeros(len(model_classes), dtype=np.float32)
    current_feats = {}

    # Estabilización inicial cuando el Kinect detecta un cuerpo por primera vez
    body_detected_since = 0.0
    warmup_duration = max(0.5, float(args.warmup_time))
    is_calibrating = True

    # Seguimiento de Pose Sostenida (0.5s para activar ataque continuo)
    current_held_action = "idle"
    hold_start_time = time.time()
    held_duration = 0.0
    pose_activated = False
    required_hold_time = max(0.1, float(args.hold_time))

    fps_timer = time.time()
    frame_count = 0
    display_fps = 30.0

    print("\n🟢 TRANSMISIÓN EN VIVO INICIADA.")
    if use_mock:
        print("🎮 Teclas numéricas en ventana para probar poses sostenidas:")
        print("   [1] Idle  [2] Puño Der  [3] Puño Izq  [4] Patada Der  [5] Patada Izq  [6] Crouch  [7] Block")
    else:
        print("🥋 Colócate frente al sensor a 1.8m - 2.8m y mantén cualquier pose de combate por 0.5s.")
    print("Presiona [Q] o [ESC] para salir.\n")

    try:
        while True:
            frame_count += 1
            now = time.time()
            if now - fps_timer >= 1.0:
                display_fps = frame_count / (now - fps_timer)
                fps_timer = now
                frame_count = 0

            # Obtener articulaciones
            has_body = False
            joints_xyz_m = None

            if not use_mock and device and body_tracker:
                try:
                    capture = device.update()
                    body_frame = body_tracker.update()
                    if body_frame.get_num_bodies() > 0:
                        body = body_frame.get_body(0)
                        joints_xyz_m = body.numpy()[:, :3] * 0.001  # Convertir mm a metros
                        has_body = True
                except Exception:
                    has_body = False
            else:
                has_body = True
                joints_xyz_m = mock_sensor.get_frame()

            if has_body and joints_xyz_m is not None:
                if body_detected_since <= 0.0:
                    body_detected_since = now
                    rolling_buffer.clear()
                rolling_buffer.append(joints_xyz_m.copy())
                is_calibrating = (now - body_detected_since) < warmup_duration
            else:
                body_detected_since = 0.0
                is_calibrating = True
                rolling_buffer.clear()
                pred_action = "idle"
                pred_conf = 1.0
                current_held_action = "idle"
                held_duration = 0.0
                pose_activated = False

            # -------------------------------------------------------------
            # MOTOR DE INFERENCIA DE POSTURA ESTÁTICA (CADA ~50ms)
            # -------------------------------------------------------------
            if has_body and len(rolling_buffer) >= 4 and (now - last_ml_time) > 0.050:
                try:
                    buf_arr = np.array(rolling_buffer, dtype=np.float32)
                    current_feats = extract_clip_features(buf_arr, fps=30.0)
                    feat_vec = np.array([[current_feats[fn] for fn in FEATURE_NAMES]], dtype=np.float32)

                    raw_probs = model.predict_proba(feat_vec)[0]
                    sorted_p_idx = np.argsort(raw_probs)[::-1]
                    raw_top_idx = sorted_p_idx[0]
                    raw_class_id = model_classes[raw_top_idx]
                    raw_action = ACTION_ID_TO_NAME.get(raw_class_id, "idle")
                    raw_conf = float(raw_probs[raw_top_idx])

                    pred_probs = raw_probs.copy()

                    # 1. Bloqueo de seguridad durante la estabilización inicial del cuerpo (1.5s)
                    if is_calibrating:
                        pred_action = "idle"
                        pred_conf = 1.0
                        current_held_action = "idle"
                        hold_start_time = now
                        held_duration = 0.0
                        pose_activated = False
                    else:
                        # 2. Validación de umbral de confianza + Geometría Biomecánica
                        is_biomechanically_valid = validate_posture_biomechanics(raw_action, current_feats)
                        if raw_action != "idle" and (raw_conf < args.min_conf or not is_biomechanically_valid):
                            pred_action = "idle"
                            pred_conf = float(raw_probs[list(model_classes).index(0)]) if 0 in model_classes else raw_conf
                        else:
                            pred_action = raw_action
                            pred_conf = raw_conf

                        # 3. Evaluador de Pose Sostenida (0.5s para activar bucle continuo en Unity)
                        if pred_action != current_held_action:
                            current_held_action = pred_action
                            hold_start_time = now
                            held_duration = 0.0
                            pose_activated = False
                        else:
                            if pred_action != "idle":
                                held_duration = now - hold_start_time
                                if held_duration >= required_hold_time:
                                    if not pose_activated:
                                        print(f"🔥 [POSE FIJADA]: {pred_action.upper()} ({pred_conf*100:.0f}%) sostenida por {held_duration:.2f}s -> ¡Bucle continuo en Unity!")
                                    pose_activated = True
                            else:
                                held_duration = 0.0
                                pose_activated = False

                    last_ml_time = now
                except Exception:
                    pass

            # -------------------------------------------------------------
            # TRANSMISIÓN UDP EN TIEMPO REAL HACIA UNITY (~30 FPS)
            # -------------------------------------------------------------
            if stream_sock is not None and (now - last_stream_time) >= 0.030:
                last_stream_time = now
                # Mientras no haya cumplido el tiempo de retención o esté calibrando,
                # enviamos la acción actual pero marcamos is_holding_active según corresponda
                payload = {
                    "action": "idle" if is_calibrating else pred_action,
                    "action_id": 0 if is_calibrating else int(ACTION_NAME_TO_ID.get(pred_action, 0)),
                    "confidence": float(round(pred_conf, 3)),
                    "has_body": bool(has_body and not is_calibrating),
                    "timestamp": float(now),
                    "hold_duration": float(round(held_duration, 2)),
                    "is_holding_active": bool(pose_activated and not is_calibrating),
                    "z_distance": float(round(joints_xyz_m[0, 2], 2)) if (has_body and joints_xyz_m is not None) else 0.0
                }
                try:
                    payload_bytes = json.dumps(payload).encode("utf-8")
                    stream_sock.sendto(payload_bytes, (args.unity_ip, args.unity_port))
                except Exception:
                    pass

            # -------------------------------------------------------------
            # DIBUJAR LIENZO EN OPENCV
            # -------------------------------------------------------------
            canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            canvas[:] = (18, 22, 28)

            cv2.line(canvas, (LEFT_W, 0), (LEFT_W, HEIGHT), (50, 60, 75), 2)

            # -------------------------------------------------------------
            # PANEL IZQUIERDO: VISUALIZACIÓN DUAL DEL ESQUELETO (3D)
            # -------------------------------------------------------------
            cv2.rectangle(canvas, (0, 0), (LEFT_W, 46), (28, 35, 48), -1)
            dist_z_str = f"Distancia Z: {joints_xyz_m[0, 2]:.2f}m" if (has_body and joints_xyz_m is not None) else "Buscando jugador..."
            z_col = (0, 255, 200) if has_body and joints_xyz_m is not None and (1.5 <= joints_xyz_m[0, 2] <= 3.0) else (0, 180, 255)

            mode_tag = "SIMULADOR (--mock)" if use_mock else "AZURE KINECT DK (ONLINE)"
            stream_tag = f"UDP: {args.unity_ip}:{args.unity_port}" if stream_sock is not None else "UDP: OFF"
            cv2.putText(canvas, f"{mode_tag} | {dist_z_str} | {stream_tag}", (16, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, z_col, 1, cv2.LINE_AA)
            cv2.putText(canvas, f"FPS: {display_fps:.1f}", (LEFT_W - 110, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (160, 175, 195), 1, cv2.LINE_AA)

            if has_body and joints_xyz_m is not None:
                pelvis_pos = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
                scale = 230.0
                cy = 410
                half_left = LEFT_W // 2

                cv2.line(canvas, (half_left, 46), (half_left, HEIGHT), (40, 48, 60), 1)

                # 1. Vista Frontal (X-Y)
                cx_front = half_left // 2
                cv2.putText(canvas, "VISTA FRONTAL (X-Y)", (cx_front - 80, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 200), 1, cv2.LINE_AA)
                f_pts = {}
                for j_name, j_id in SIMPLIFIED_JOINTS.items():
                    rx_pt = (joints_xyz_m[j_id, 0] - pelvis_pos[0]) * scale
                    ry_pt = (joints_xyz_m[j_id, 1] - pelvis_pos[1]) * scale
                    f_pts[j_name] = np.array([cx_front + rx_pt, cy + ry_pt])
                draw_skeleton(canvas, f_pts)

                # 2. Vista Sagital / Perfil (Z-Y)
                cx_sag = half_left + (half_left // 2)
                cv2.putText(canvas, "VISTA SAGITAL (Z-Y)", (cx_sag - 80, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 200, 255), 1, cv2.LINE_AA)
                s_pts = {}
                for j_name, j_id in SIMPLIFIED_JOINTS.items():
                    rz_pt = (joints_xyz_m[j_id, 2] - pelvis_pos[2]) * scale
                    ry_pt = (joints_xyz_m[j_id, 1] - pelvis_pos[1]) * scale
                    s_pts[j_name] = np.array([cx_sag + rz_pt, cy + ry_pt])
                draw_skeleton(canvas, s_pts)
            else:
                cv2.putText(canvas, "PARATE FRENTE AL AZURE KINECT PARA INICIAR", (80, 380),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 150, 255), 2, cv2.LINE_AA)

            # -------------------------------------------------------------
            # PANEL DERECHO: DETECCIÓN, BARRA DE RETENCIÓN Y PROBABILIDADES
            # -------------------------------------------------------------
            rx = LEFT_W + 16

            # 1. TARJETA PRINCIPAL DE DETECCIÓN
            card_h = 92
            cv2.rectangle(canvas, (LEFT_W + 12, 12), (WIDTH - 12, 12 + card_h), (25, 32, 45), -1)
            conf_col = (0, 190, 255) if is_calibrating else ((0, 240, 120) if pred_conf >= 0.70 else (0, 210, 255))
            cv2.rectangle(canvas, (LEFT_W + 12, 12), (WIDTH - 12, 12 + card_h), conf_col, 2)

            cv2.putText(canvas, "POSTURA DETECTADA EN VIVO:", (rx, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (170, 185, 205), 1, cv2.LINE_AA)
            disp_title = "CALIBRANDO..." if is_calibrating else pred_action.upper()
            cv2.putText(canvas, disp_title, (rx, 72),
                        cv2.FONT_HERSHEY_DUPLEX, 1.0, conf_col, 2, cv2.LINE_AA)

            conf_str = f"Certeza: {pred_conf*100:.1f}%"
            cv2.putText(canvas, conf_str, (WIDTH - 230, 72),
                        cv2.FONT_HERSHEY_DUPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)

            # 2. CRONÓMETRO DE POSE SOSTENIDA (0.5s PARA ACTIVAR BUCLE CONTINUO)
            trans_y = 12 + card_h + 10
            trans_h = 74
            cv2.rectangle(canvas, (LEFT_W + 12, trans_y), (WIDTH - 12, trans_y + trans_h), (22, 28, 38), -1)

            hold_bdr_col = (0, 255, 120) if pose_activated else ((0, 190, 255) if held_duration > 0.1 else (60, 70, 85))
            cv2.rectangle(canvas, (LEFT_W + 12, trans_y), (WIDTH - 12, trans_y + trans_h), hold_bdr_col, 2 if pose_activated else 1)

            if is_calibrating and has_body:
                cal_elapsed = now - body_detected_since
                pct_cal = min(1.0, cal_elapsed / warmup_duration)
                bar_w = int((WIDTH - LEFT_W - 50) * pct_cal)
                cv2.rectangle(canvas, (rx, trans_y + 46), (rx + bar_w, trans_y + 62), (0, 180, 255), -1)
                cv2.rectangle(canvas, (rx, trans_y + 46), (WIDTH - 30, trans_y + 62), (70, 80, 95), 1)
                cv2.putText(canvas, f"ESTABILIZANDO ESQUELETO INICIAL ({cal_elapsed:.1f}s / {warmup_duration:.1f}s)",
                            (rx, trans_y + 24), cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 210, 255), 1, cv2.LINE_AA)
                cv2.putText(canvas, "Evitando animaciones fantasma al entrar al campo del Kinect...",
                            (rx, trans_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (160, 180, 200), 1, cv2.LINE_AA)
            else:
                pct_hold = min(1.0, held_duration / max(0.1, required_hold_time))
                bar_w = int((WIDTH - LEFT_W - 50) * pct_hold)
                bar_color = (0, 240, 100) if pose_activated else (0, 200, 255)
                cv2.rectangle(canvas, (rx, trans_y + 46), (rx + bar_w, trans_y + 62), bar_color, -1)
                cv2.rectangle(canvas, (rx, trans_y + 46), (WIDTH - 30, trans_y + 62), (70, 80, 95), 1)

                if pred_action != "idle":
                    if pose_activated:
                        cv2.putText(canvas, f"POSE FIJADA: REPITIENDO ATAQUE EN UNITY ({held_duration:.1f}s)",
                                    (rx, trans_y + 24), cv2.FONT_HERSHEY_DUPLEX, 0.44, (0, 255, 120), 1, cv2.LINE_AA)
                        cv2.putText(canvas, "Bucle continuo activo. Cambiar de posicion detiene el ataque.",
                                    (rx, trans_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (180, 230, 200), 1, cv2.LINE_AA)
                    else:
                        cv2.putText(canvas, f"MANTEN LA POSE: {held_duration:.2f}s / {required_hold_time:.1f}s ({int(pct_hold*100)}%)",
                                    (rx, trans_y + 24), cv2.FONT_HERSHEY_DUPLEX, 0.44, (0, 210, 255), 1, cv2.LINE_AA)
                        cv2.putText(canvas, f"Sosteniendo postura por {required_hold_time:.1f}s para activar repeticion constante.",
                                    (rx, trans_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (160, 180, 200), 1, cv2.LINE_AA)
                else:
                    cv2.putText(canvas, f"REPOSO (IDLE): Haz una pose y mantenla {required_hold_time:.1f}s",
                                (rx, trans_y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 170, 190), 1, cv2.LINE_AA)
                    cv2.putText(canvas, "Ryu permanece en guardia neutral sin disparar golpes solos.",
                                (rx, trans_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (130, 145, 165), 1, cv2.LINE_AA)

            # 3. GRÁFICO DE BARRAS DE PROBABILIDAD (7 CLASES DE COMBATE)
            bar_start_y = trans_y + trans_h + 18
            cv2.putText(canvas, "DISTRIBUCION DE PROBABILIDAD (% POR POSE):", (rx, bar_start_y),
                        cv2.FONT_HERSHEY_DUPLEX, 0.44, (0, 220, 255), 1, cv2.LINE_AA)

            sorted_idx = np.argsort(pred_probs)[::-1]
            max_bar_w = 360

            for i, idx in enumerate(sorted_idx):
                prob = float(pred_probs[idx])
                cid = model_classes[idx]
                act_str = ACTION_ID_TO_NAME.get(cid, "unknown")
                y_pos = bar_start_y + 14 + i * 32

                is_winner = (i == 0)
                is_runner_up = (i == 1)

                if is_winner:
                    b_color = (0, 220, 120) if pose_activated else (0, 200, 255)
                    txt_col = (255, 255, 255)
                elif is_runner_up:
                    b_color = (0, 140, 200)
                    txt_col = (0, 200, 240)
                else:
                    b_color = (45, 60, 80)
                    txt_col = (160, 175, 190)

                cv2.putText(canvas, f"{act_str:12s}", (rx, y_pos + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, txt_col, 1, cv2.LINE_AA)

                bar_x = rx + 120
                bar_w = int(prob * max_bar_w)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + max_bar_w, y_pos + 18), (30, 36, 48), -1)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + bar_w, y_pos + 18), b_color, -1)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + max_bar_w, y_pos + 18), (55, 65, 80), 1)

                pct_str = f"{prob*100:5.1f}%"
                cv2.putText(canvas, pct_str, (bar_x + max_bar_w + 10, y_pos + 14),
                            cv2.FONT_HERSHEY_DUPLEX, 0.40, txt_col, 1, cv2.LINE_AA)

            # 4. AUDITOR DE CERTEZA Y SEPARABILIDAD POSTURAL
            bias_y = bar_start_y + 14 + len(sorted_idx) * 32 + 10
            top_prob = float(pred_probs[sorted_idx[0]]) if len(sorted_idx) > 0 else 0.0
            second_prob = float(pred_probs[sorted_idx[1]]) if len(sorted_idx) > 1 else 0.0
            margin = top_prob - second_prob

            cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 48), (25, 30, 42), -1)

            if margin < 0.20:
                second_name = ACTION_ID_TO_NAME.get(model_classes[sorted_idx[1]], "") if len(sorted_idx) > 1 else ""
                cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 48), (0, 140, 255), 2)
                cv2.putText(canvas, f"POSTURA EN TRANSICION (Margen: {margin*100:.1f}%)", (rx, bias_y + 20),
                            cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 180, 255), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"Entre '{pred_action}' ({top_prob*100:.0f}%) y '{second_name}' ({second_prob*100:.0f}%)",
                            (rx, bias_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (200, 215, 230), 1, cv2.LINE_AA)
            else:
                cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 48), (0, 200, 100), 1)
                second_name = ACTION_ID_TO_NAME.get(model_classes[sorted_idx[1]], "") if len(sorted_idx) > 1 else ""
                cv2.putText(canvas, f"POSTURA DEFINIDA (+{margin*100:.1f}% sobre '{second_name}')", (rx, bias_y + 20),
                            cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 255, 140), 1, cv2.LINE_AA)
                cv2.putText(canvas, "Geometria estatica validada (Invariante a velocidad).",
                            (rx, bias_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (170, 190, 205), 1, cv2.LINE_AA)

            # 5. TELEMETRÍA GEOMÉTRICA POSTURAL EN VIVO
            tele_y = bias_y + 60
            cv2.putText(canvas, "GEOMETRIA POSTURAL EN VIVO (SIN DEPENDENCIA DE VELOCIDAD):", (rx, tele_y),
                        cv2.FONT_HERSHEY_DUPLEX, 0.40, (0, 220, 255), 1, cv2.LINE_AA)

            h_wr_r = current_feats.get("horiz_wr_r_mean", 0.0)
            h_wr_l = current_feats.get("horiz_wr_l_mean", 0.0)
            ank_asym = current_feats.get("ank_elevation_asym", 0.0)
            max_ank_d = current_feats.get("max_ank_depth", 0.90)
            wr_chest = current_feats.get("mean_wr_rel_chest", 0.0)

            cv2.putText(canvas, f"• Extension Horiz. Punos: Der {h_wr_r:.2f} | Izq {h_wr_l:.2f} (Umbral >= 0.50)",
                        (rx, tele_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"• Asimetria Piernas (Patadas): {ank_asym:+.2f} (Der > +0.14 | Izq < -0.14)",
                        (rx, tele_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"• Altura Pelvis-Piso: {max_ank_d:.2f} (Crouch <= 0.72) | Guardia Pecho: {wr_chest:+.2f}",
                        (rx, tele_y + 56), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)

            # Barra inferior con ayuda
            cv2.rectangle(canvas, (0, HEIGHT - 26), (WIDTH, HEIGHT), (14, 16, 22), -1)
            help_txt = "SF3 Static Posture Studio | [Q]/[ESC] Salir | En modo Mock: [1-7] Fijar postura sostenida"
            cv2.putText(canvas, help_txt, (16, HEIGHT - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 155, 175), 1, cv2.LINE_AA)

            cv2.imshow(WINDOW_NAME, canvas)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break

            if use_mock:
                action_keys = {
                    ord('1'): "idle",
                    ord('2'): "punch_right",
                    ord('3'): "punch_left",
                    ord('4'): "kick_right",
                    ord('5'): "kick_left",
                    ord('6'): "crouch",
                    ord('7'): "block"
                }
                if key in action_keys:
                    mock_sensor.trigger_action(action_keys[key])

    finally:
        print("\n🛑 Deteniendo Live Classifier...")
        if stream_sock is not None:
            try:
                stream_sock.close()
            except Exception:
                pass
        if not use_mock and device:
            try:
                device.close()
            except Exception:
                pass
        cv2.destroyAllWindows()
        print("✅ Sensor y ventana liberados exitosamente.")


if __name__ == "__main__":
    main()
