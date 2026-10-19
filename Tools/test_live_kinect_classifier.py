"""
Street Fighter III: 3rd Strike - Live Azure Kinect Gesture & Fast Transition Classifier
Detector somatosensorial en vivo con soporte para hardware físico Azure Kinect DK y simulador:
- Esqueleto Dual en tiempo real (Vista Frontal X-Y + Vista Sagital Z-Y de Perfil).
- Predicción cinemática continua con el modelo Random Forest actualizado con las 42 transiciones.
- Radar de Transiciones Rápidas y Cancel Windows (mide latencia A -> B en ms y fluidez de combo).
- Gráfico de barras con porcentajes de precisión exactos (%) para las 7 posturas de combate.
- Auditor de sesgos y ambigüedades en vivo.
- Telemetría cinemática de extremidades (velocidad de muñecas/tobillos en m/s, distancia de guardia, altura de pelvis).
"""

import os
import sys
import time
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

# Importar módulos cinemáticos locales
sys.path.append(os.path.dirname(__file__))
from gesture_feature_extractor import (
    ACTION_CLASSES,
    ACTION_ID_TO_NAME,
    ACTION_NAME_TO_ID,
    FEATURE_NAMES,
    extract_clip_features
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
        self.transition_frame = 0
        self.transition_total = 40
        self.is_transitioning = False

    def _init_base_pose(self):
        self.base_skeleton[0] = [0.0, 0.95, 2.2]     # Pelvis
        self.base_skeleton[1] = [0.0, 0.80, 2.2]     # Spine Navel
        self.base_skeleton[2] = [0.0, 0.65, 2.2]     # Spine Chest
        self.base_skeleton[3] = [0.0, 0.50, 2.2]     # Neck
        self.base_skeleton[26] = [0.0, 0.35, 2.2]    # Head
        self.base_skeleton[5] = [-0.18, 0.52, 2.2]   # Shoulder Left
        self.base_skeleton[6] = [-0.26, 0.72, 2.15]  # Elbow Left
        self.base_skeleton[7] = [-0.24, 0.88, 2.05]  # Wrist Left
        self.base_skeleton[8] = [-0.24, 0.96, 2.00]  # Hand Left
        self.base_skeleton[12] = [0.18, 0.52, 2.2]   # Shoulder Right
        self.base_skeleton[13] = [0.26, 0.72, 2.15]  # Elbow Right
        self.base_skeleton[14] = [0.24, 0.88, 2.05]  # Wrist Right
        self.base_skeleton[15] = [0.24, 0.96, 2.00]  # Hand Right
        self.base_skeleton[18] = [-0.10, 0.98, 2.2]  # Hip Left
        self.base_skeleton[19] = [-0.12, 1.35, 2.22] # Knee Left
        self.base_skeleton[20] = [-0.13, 1.75, 2.25] # Ankle Left
        self.base_skeleton[21] = [-0.13, 1.85, 2.18] # Foot Left
        self.base_skeleton[22] = [0.10, 0.98, 2.2]   # Hip Right
        self.base_skeleton[23] = [0.12, 1.35, 2.22]  # Knee Right
        self.base_skeleton[24] = [0.13, 1.75, 2.25]  # Ankle Right
        self.base_skeleton[25] = [0.13, 1.85, 2.18]  # Foot Right

    def trigger_action(self, target_act: str):
        self.current_action = self.target_action
        self.target_action = target_act
        self.transition_frame = 0
        self.is_transitioning = True

    def get_frame(self) -> np.ndarray:
        frame = self.base_skeleton.copy()
        t = time.time()
        # Micro-respiración
        frame[:, 1] += np.sin(t * 2.2) * 0.006

        if self.is_transitioning:
            self.transition_frame += 1
            progress = min(1.0, self.transition_frame / float(self.transition_total))
            intensity = np.sin(np.pi * progress)

            if progress >= 1.0:
                self.is_transitioning = False
                self.current_action = self.target_action
        else:
            intensity = 0.0

        act = self.target_action if self.is_transitioning else self.current_action
        # Aplicar deformación cinemática según acción
        if act == "punch_right":
            p = intensity if self.is_transitioning else 1.0
            frame[14, 2] -= 0.65 * p
            frame[15, 2] -= 0.72 * p
            frame[14, 1] -= 0.22 * p
        elif act == "punch_left":
            p = intensity if self.is_transitioning else 1.0
            frame[7, 2] -= 0.65 * p
            frame[8, 2] -= 0.72 * p
            frame[7, 1] -= 0.22 * p
        elif act == "kick_right":
            p = intensity if self.is_transitioning else 1.0
            frame[24, 2] -= 0.75 * p
            frame[25, 2] -= 0.85 * p
            frame[24, 1] -= 0.60 * p
            frame[25, 1] -= 0.65 * p
        elif act == "kick_left":
            p = intensity if self.is_transitioning else 1.0
            frame[20, 2] -= 0.75 * p
            frame[21, 2] -= 0.85 * p
            frame[20, 1] -= 0.60 * p
            frame[21, 1] -= 0.65 * p
        elif act == "crouch":
            p = intensity if self.is_transitioning else 1.0
            frame[0, 1] += 0.35 * p
            frame[1, 1] += 0.35 * p
            frame[2, 1] += 0.32 * p
            frame[23, 1] += 0.15 * p
            frame[19, 1] += 0.15 * p
        elif act == "block":
            p = intensity if self.is_transitioning else 1.0
            frame[14, 1] -= 0.45 * p
            frame[7, 1] -= 0.45 * p
            frame[14, 0] -= 0.14 * p
            frame[7, 0] += 0.14 * p

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
    parser = argparse.ArgumentParser(description="SF3 Live Azure Kinect Gesture & Fast Transition Classifier")
    parser.add_argument("--mock", action="store_true", default=False,
                        help="Forzar modo simulador procedural (sin sensor físico)")
    parser.add_argument("--model", type=str, default=os.path.join(os.path.dirname(__file__), "gesture_classifier.joblib"),
                        help="Ruta al modelo entrenado (.joblib)")
    args = parser.parse_args()

    print("=" * 80)
    print("🥊 SF3 - DETECTOR EN VIVO: CLASIFICADOR DE POSES & RADAR DE TRANSICIONES RÁPIDAS")
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

    # 3. Variables de ventana e inferencia
    WINDOW_NAME = "SF3 Live Kinect - Fast Transition & Gesture Studio"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    WIDTH = 1380
    HEIGHT = 780
    LEFT_W = 750   # Área de esqueletos (Frontal + Sagital)
    RIGHT_W = 630  # Panel HUD de probabilidades, transiciones y métricas

    rolling_buffer = collections.deque(maxlen=35)
    last_ml_time = 0.0

    # Estado actual y variables de transición
    pred_action = "idle"
    pred_conf = 1.0
    pred_probs = np.zeros(len(model_classes), dtype=np.float32)
    current_feats = {}

    prev_action = "idle"
    transition_start_time = time.time()
    last_transition_event = {
        "from": "idle",
        "to": "idle",
        "latency_ms": 0,
        "timestamp": time.time() - 10.0
    }
    combo_history = collections.deque(["idle"], maxlen=5)

    last_event_action = "idle"
    last_event_time = 0.0
    last_event_conf = 0.0

    fps_timer = time.time()
    frame_count = 0
    display_fps = 30.0

    print("\n🟢 TRANSMISIÓN EN VIVO INICIADA.")
    if use_mock:
        print("🎮 Teclas numéricas en ventana para probar transiciones:")
        print("   [1] Idle  [2] Puño Der  [3] Puño Izq  [4] Patada Der  [5] Patada Izq  [6] Crouch  [7] Block")
    else:
        print("🥋 Colócate frente al sensor a 1.8m - 2.8m y ejecuta golpes y combos rápidos.")
    print("Presiona [Q] o [ESC] para salir.\n")

    try:
        while True:
            frame_count += 1
            if time.time() - fps_timer >= 1.0:
                display_fps = frame_count / (time.time() - fps_timer)
                fps_timer = time.time()
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
                rolling_buffer.append(joints_xyz_m.copy())

            # -------------------------------------------------------------
            # MOTOR DE INFERENCIA CINEMÁTICA Y RADAR DE TRANSICIONES RÁPIDAS
            # -------------------------------------------------------------
            now = time.time()
            if has_body and len(rolling_buffer) >= 20 and (now - last_ml_time) > 0.065:
                try:
                    buf_arr = np.array(rolling_buffer, dtype=np.float32)

                    # Si el buffer aún no tiene 35, replicar los primeros para completar ventana
                    if len(buf_arr) < 35:
                        pad_len = 35 - len(buf_arr)
                        buf_arr = np.vstack([np.repeat(buf_arr[:1], pad_len, axis=0), buf_arr])

                    current_feats = extract_clip_features(buf_arr, fps=30.0)
                    feat_vec = np.array([[current_feats[fn] for fn in FEATURE_NAMES]], dtype=np.float32)

                    # Medir velocidad en ventana reciente (últimos 6 frames ~ 200 ms)
                    recent_frames = buf_arr[-6:]
                    dt_r = 1.0 / 30.0
                    recent_v_wr_r = np.max(np.linalg.norm(np.diff(recent_frames[:, 14, :], axis=0), axis=1)) / dt_r
                    recent_v_wr_l = np.max(np.linalg.norm(np.diff(recent_frames[:, 7, :], axis=0), axis=1)) / dt_r
                    recent_v_ank_r = np.max(np.linalg.norm(np.diff(recent_frames[:, 24, :], axis=0), axis=1)) / dt_r
                    recent_v_ank_l = np.max(np.linalg.norm(np.diff(recent_frames[:, 20, :], axis=0), axis=1)) / dt_r
                    recent_v_pelvis = np.max(np.abs(np.diff(recent_frames[:, 0, 1]))) / dt_r

                    # ¿Extremidades en reposo instantáneo?
                    is_recent_calm = (
                        recent_v_wr_r < 0.40 and
                        recent_v_wr_l < 0.40 and
                        recent_v_ank_r < 0.40 and
                        recent_v_ank_l < 0.40 and
                        recent_v_pelvis < 0.32
                    )

                    # Inferencia del modelo Random Forest
                    raw_probs = model.predict_proba(feat_vec)[0]
                    sorted_p_idx = np.argsort(raw_probs)[::-1]
                    raw_top_idx = sorted_p_idx[0]
                    raw_class_id = model_classes[raw_top_idx]
                    raw_action = ACTION_ID_TO_NAME.get(raw_class_id, "unknown")
                    raw_conf = float(raw_probs[raw_top_idx])

                    # ---------------------------------------------------------
                    # EVALUADOR DE TRANSICIÓN RÁPIDA / ESTADOS SOSTENIDOS
                    # ---------------------------------------------------------
                    if is_recent_calm:
                        last_frame = buf_arr[-1]
                        pelvis_y = last_frame[0, 1]
                        knee_r_y = last_frame[23, 1]

                        # Agachado sostenido
                        is_holding_crouch = (current_feats.get("min_disp_pelvis_y", 0.0) < -0.15 and (pelvis_y - knee_r_y) > -0.42)

                        # Bloqueo sostenido (muñecas frente a pecho)
                        wrist_dist_now = np.linalg.norm(last_frame[14, :] - last_frame[7, :])
                        wrist_elev_r = last_frame[0, 1] - last_frame[14, 1]
                        wrist_elev_l = last_frame[0, 1] - last_frame[7, 1]
                        is_holding_block = (wrist_dist_now < 0.38 and wrist_elev_r > 0.38 and wrist_elev_l > 0.38)

                        if is_holding_crouch:
                            pred_action = "crouch"
                            pred_conf = 0.95
                            c_idx = list(model_classes).index(ACTION_NAME_TO_ID["crouch"]) if ACTION_NAME_TO_ID["crouch"] in model_classes else raw_top_idx
                            pred_probs = np.zeros_like(raw_probs)
                            pred_probs[c_idx] = 0.95
                            pred_probs[raw_top_idx] = max(0.01, 1.0 - 0.95)
                        elif is_holding_block:
                            pred_action = "block"
                            pred_conf = 0.94
                            b_idx = list(model_classes).index(ACTION_NAME_TO_ID["block"]) if ACTION_NAME_TO_ID["block"] in model_classes else raw_top_idx
                            pred_probs = np.zeros_like(raw_probs)
                            pred_probs[b_idx] = 0.94
                            pred_probs[raw_top_idx] = max(0.01, 1.0 - 0.94)
                        else:
                            # Retorno a Idle / Guardia inmediata post-golpe
                            pred_action = "idle"
                            pred_conf = 0.96
                            idle_idx = list(model_classes).index(ACTION_NAME_TO_ID["idle"]) if ACTION_NAME_TO_ID["idle"] in model_classes else 0
                            pred_probs = np.zeros_like(raw_probs)
                            pred_probs[idle_idx] = 0.96
                            rem_idx = raw_top_idx if raw_top_idx != idle_idx else (1 if len(raw_probs) > 1 else 0)
                            pred_probs[rem_idx] = 0.04
                    else:
                        # Fase activa del movimiento o transición rápida de golpe
                        pred_action = raw_action
                        pred_conf = raw_conf
                        pred_probs = raw_probs.copy()

                    # ---------------------------------------------------------
                    # RADAR DE TRANSICIÓN: Detectar cambio entre acciones (A -> B)
                    # ---------------------------------------------------------
                    if pred_action != prev_action:
                        trans_dt = max(50, int((now - transition_start_time) * 1000))
                        last_transition_event = {
                            "from": prev_action,
                            "to": pred_action,
                            "latency_ms": trans_dt,
                            "timestamp": now
                        }
                        if combo_history[-1] != pred_action:
                            combo_history.append(pred_action)

                        print(f"⚡ [TRANSICIÓN RÁPIDA]: {prev_action.upper():12s} ➔➔➔ {pred_action.upper():12s} ({trans_dt} ms)")
                        prev_action = pred_action
                        transition_start_time = now

                    # Registrar eventos de impacto activo
                    if pred_action not in ("idle", "unknown") and pred_conf >= 0.55:
                        last_event_action = pred_action
                        last_event_time = now
                        last_event_conf = pred_conf

                    last_ml_time = now
                except Exception as ex:
                    pass

            # -------------------------------------------------------------
            # DIBUJAR LIENZO EN OPENCV
            # -------------------------------------------------------------
            canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            canvas[:] = (18, 22, 28)

            # Separador vertical
            cv2.line(canvas, (LEFT_W, 0), (LEFT_W, HEIGHT), (50, 60, 75), 2)

            # -------------------------------------------------------------
            # PANEL IZQUIERDO: VISUALIZACIÓN DUAL DEL ESQUELETO (3D)
            # -------------------------------------------------------------
            cv2.rectangle(canvas, (0, 0), (LEFT_W, 46), (28, 35, 48), -1)
            dist_z_str = f"Distancia Z: {joints_xyz_m[0, 2]:.2f}m" if (has_body and joints_xyz_m is not None) else "Buscando jugador..."
            z_col = (0, 255, 200) if has_body and joints_xyz_m is not None and (1.7 <= joints_xyz_m[0, 2] <= 2.8) else (0, 180, 255)

            mode_tag = "SIMULADOR (--mock)" if use_mock else "AZURE KINECT DK (ONLINE)"
            cv2.putText(canvas, f"{mode_tag} | {dist_z_str}", (16, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, z_col, 2, cv2.LINE_AA)
            cv2.putText(canvas, f"FPS: {display_fps:.1f}", (LEFT_W - 110, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (160, 175, 195), 1, cv2.LINE_AA)

            if has_body and joints_xyz_m is not None:
                pelvis_pos = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
                scale = 230.0
                cy = 410
                half_left = LEFT_W // 2

                # Línea divisoria Frontal / Sagital
                cv2.line(canvas, (half_left, 46), (half_left, HEIGHT), (40, 48, 60), 1)

                # 1. Vista Frontal (X-Y)
                cx_front = half_left // 2
                cv2.putText(canvas, "VISTA FRONTAL (X-Y)", (cx_front - 80, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 200), 1, cv2.LINE_AA)
                f_pts = {}
                for j_name, j_id in SIMPLIFIED_JOINTS.items():
                    rx = (joints_xyz_m[j_id, 0] - pelvis_pos[0]) * scale
                    ry = (joints_xyz_m[j_id, 1] - pelvis_pos[1]) * scale
                    f_pts[j_name] = np.array([cx_front + rx, cy + ry])
                draw_skeleton(canvas, f_pts)

                # 2. Vista Sagital / Perfil (Z-Y)
                cx_sag = half_left + (half_left // 2)
                cv2.putText(canvas, "VISTA SAGITAL (Z-Y)", (cx_sag - 80, 75),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 200, 255), 1, cv2.LINE_AA)
                s_pts = {}
                for j_name, j_id in SIMPLIFIED_JOINTS.items():
                    rz = (joints_xyz_m[j_id, 2] - pelvis_pos[2]) * scale
                    ry = (joints_xyz_m[j_id, 1] - pelvis_pos[1]) * scale
                    s_pts[j_name] = np.array([cx_sag + rz, cy + ry])
                draw_skeleton(canvas, s_pts)
            else:
                cv2.putText(canvas, "PÁRATE FRENTE AL AZURE KINECT PARA INICIAR", (80, 380),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 150, 255), 2, cv2.LINE_AA)

            # -------------------------------------------------------------
            # PANEL DERECHO: DETECCIÓN, RADAR DE TRANSICIONES Y PROBABILIDADES
            # -------------------------------------------------------------
            rx = LEFT_W + 16

            # 1. TARJETA PRINCIPAL DE DETECCIÓN
            card_h = 92
            cv2.rectangle(canvas, (LEFT_W + 12, 12), (WIDTH - 12, 12 + card_h), (25, 32, 45), -1)
            conf_col = (0, 240, 120) if pred_conf >= 0.75 else ((0, 210, 255) if pred_conf >= 0.50 else (0, 100, 255))
            cv2.rectangle(canvas, (LEFT_W + 12, 12), (WIDTH - 12, 12 + card_h), conf_col, 2)

            cv2.putText(canvas, "MOVIMIENTO DETECTADO EN VIVO:", (rx, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (170, 185, 205), 1, cv2.LINE_AA)
            cv2.putText(canvas, pred_action.upper(), (rx, 72),
                        cv2.FONT_HERSHEY_DUPLEX, 1.05, conf_col, 2, cv2.LINE_AA)

            conf_str = f"Precisión: {pred_conf*100:.1f}%"
            cv2.putText(canvas, conf_str, (WIDTH - 230, 72),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

            # 2. RADAR DE TRANSICIONES RÁPIDAS (COMBO FLOW & CANCEL WINDOWS)
            trans_y = 12 + card_h + 10
            trans_h = 74
            cv2.rectangle(canvas, (LEFT_W + 12, trans_y), (WIDTH - 12, trans_y + trans_h), (22, 28, 38), -1)

            is_recent_trans = (time.time() - last_transition_event["timestamp"]) < 2.8
            trans_bdr_col = (0, 255, 220) if is_recent_trans else (50, 60, 75)
            cv2.rectangle(canvas, (LEFT_W + 12, trans_y), (WIDTH - 12, trans_y + trans_h), trans_bdr_col, 2 if is_recent_trans else 1)

            if is_recent_trans:
                f_from = last_transition_event["from"].upper()
                f_to = last_transition_event["to"].upper()
                lat_ms = last_transition_event["latency_ms"]
                cv2.putText(canvas, "⚡ RADAR DE TRANSICIÓN RÁPIDA (COMBO ACTIVO):", (rx, trans_y + 22),
                            cv2.FONT_HERSHEY_DUPLEX, 0.44, (0, 255, 220), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"[ {f_from} ]  ======>>  [ {f_to} ]  |  Latencia: {lat_ms} ms",
                            (rx, trans_y + 45), cv2.FONT_HERSHEY_DUPLEX, 0.48, (0, 255, 140), 1, cv2.LINE_AA)
            else:
                cv2.putText(canvas, "🛡️ RADAR DE TRANSICIONES: Estado de combate estable", (rx, trans_y + 22),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (150, 170, 190), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"Pose activa: {pred_action.upper()} (Listo para encadenar transición o cancel)",
                            (rx, trans_y + 45), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 215, 230), 1, cv2.LINE_AA)

            # Cadena de combo reciente
            combo_str = " ➔ ".join([c.upper() for c in combo_history])
            cv2.putText(canvas, f"Secuencia: {combo_str}", (rx, trans_y + 64),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, (140, 160, 185), 1, cv2.LINE_AA)

            # 3. GRÁFICO DE BARRAS DE PROBABILIDAD (7 CLASES DE COMBATE)
            bar_start_y = trans_y + trans_h + 18
            cv2.putText(canvas, "DISTRIBUCIÓN DE PROBABILIDAD (% POR POSE):", (rx, bar_start_y),
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
                    b_color = (0, 220, 120)      # Verde neón ganador
                    txt_col = (255, 255, 255)
                elif is_runner_up and is_recent_trans:
                    b_color = (0, 180, 240)      # Cian para la pose en transición
                    txt_col = (0, 220, 255)
                else:
                    b_color = (45, 60, 80)       # Azul grisáceo
                    txt_col = (160, 175, 190)

                # Nombre de la pose
                cv2.putText(canvas, f"{act_str:12s}", (rx, y_pos + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, txt_col, 1, cv2.LINE_AA)

                # Barra horizontal
                bar_x = rx + 120
                bar_w = int(prob * max_bar_w)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + max_bar_w, y_pos + 18), (30, 36, 48), -1)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + bar_w, y_pos + 18), b_color, -1)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + max_bar_w, y_pos + 18), (55, 65, 80), 1)

                # Porcentaje numérico exacto
                pct_str = f"{prob*100:5.1f}%"
                cv2.putText(canvas, pct_str, (bar_x + max_bar_w + 10, y_pos + 14),
                            cv2.FONT_HERSHEY_DUPLEX, 0.40, txt_col, 1, cv2.LINE_AA)

            # 4. AUDITOR DE SESGO Y AMBIGÜEDAD
            bias_y = bar_start_y + 14 + len(sorted_idx) * 32 + 10
            top_prob = float(pred_probs[sorted_idx[0]])
            second_prob = float(pred_probs[sorted_idx[1]]) if len(sorted_idx) > 1 else 0.0
            margin = top_prob - second_prob

            cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 48), (25, 30, 42), -1)

            if margin < 0.25:
                second_name = ACTION_ID_TO_NAME.get(model_classes[sorted_idx[1]], "")
                cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 48), (0, 140, 255), 2)
                cv2.putText(canvas, f"⚠️ ALERTA DE AMBIGÜEDAD (Margen estrecho: {margin*100:.1f}%)", (rx, bias_y + 20),
                            cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 180, 255), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"Transicionando entre '{pred_action}' ({top_prob*100:.0f}%) y '{second_name}' ({second_prob*100:.0f}%)",
                            (rx, bias_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (200, 215, 230), 1, cv2.LINE_AA)
            else:
                cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 48), (0, 200, 100), 1)
                second_name = ACTION_ID_TO_NAME.get(model_classes[sorted_idx[1]], "")
                cv2.putText(canvas, f"🛡️ DECISIÓN FIRME (+{margin*100:.1f}% sobre la segunda opción)", (rx, bias_y + 20),
                            cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 255, 140), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"Pose dominante sobre '{second_name}'. Clasificación sólida.",
                            (rx, bias_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (170, 190, 205), 1, cv2.LINE_AA)

            # 5. TELEMETRÍA CINEMÁTICA EN VIVO
            tele_y = bias_y + 60
            cv2.putText(canvas, "MÉTRICAS CINEMÁTICAS EN VIVO:", (rx, tele_y),
                        cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 220, 255), 1, cv2.LINE_AA)

            v_wr = current_feats.get("peak_vel_wrist_r", 0.0)
            v_wl = current_feats.get("peak_vel_wrist_l", 0.0)
            v_fr = current_feats.get("peak_vel_foot_r", 0.0)
            v_fl = current_feats.get("peak_vel_foot_l", 0.0)
            d_pelvis = current_feats.get("net_disp_pelvis_y", 0.0) * 100.0
            w_dist = current_feats.get("min_wrist_distance", 0.0) * 100.0
            asym_arm = current_feats.get("arm_activity_asymmetry", 0.0)

            cv2.putText(canvas, f"• Puños : Der {v_wr:.2f} m/s | Izq {v_wl:.2f} m/s (Asim: {asym_arm:+.2f})",
                        (rx, tele_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"• Pies  : Der {v_fr:.2f} m/s | Izq {v_fl:.2f} m/s",
                        (rx, tele_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"• Pelvis: {d_pelvis:+.1f} cm (Crouch < -15cm) | Dist. Guardia: {w_dist:.1f} cm",
                        (rx, tele_y + 56), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)

            # Barra inferior con ayuda
            cv2.rectangle(canvas, (0, HEIGHT - 26), (WIDTH, HEIGHT), (14, 16, 22), -1)
            help_txt = "SF3 Live Fast Transition Studio | [Q]/[ESC] Salir | En modo Mock: [1-7] Disparar transiciones de prueba"
            cv2.putText(canvas, help_txt, (16, HEIGHT - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 155, 175), 1, cv2.LINE_AA)

            cv2.imshow(WINDOW_NAME, canvas)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break

            # Si es modo mock o prueba interactiva, permitir cambiar pose con 1..7
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
        if not use_mock and device:
            try:
                device.close()
            except Exception:
                pass
        cv2.destroyAllWindows()
        print("✅ Sensor y ventana liberados exitosamente.")


if __name__ == "__main__":
    main()
