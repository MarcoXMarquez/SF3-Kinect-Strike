"""
Street Fighter III: 3rd Strike - Live Azure Kinect Gesture Classifier & Bias Auditor
Detector somatosensorial en vivo con hardware Azure Kinect DK físico:
- Muestra el esqueleto en tiempo real (Frontal + Sagital)
- Predice la acción continua con el modelo Random Forest entrenado
- Grafica las probabilidades de las 7 poses para evaluar a cuál se parece
- Alerta en vivo si existe sesgo o ambigüedad entre dos movimientos
- Muestra telemetría cinemática de extremidades (velocidades m/s, distancia Z, desplazamiento pelvis)
"""

import os
import sys
import time
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
    FEATURE_NAMES,
    extract_clip_features
)

# Azure Kinect
import pykinect_azure as pykinect

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


def main():
    print("=" * 75)
    print("🥊 SF3 - DETECTOR EN VIVO CON AZURE KINECT FÍSICO + AUDITOR DE SESGOS")
    print("=" * 75)
    
    # 1. Cargar modelo ML
    model_path = os.path.join(os.path.dirname(__file__), "gesture_classifier.joblib")
    if not os.path.exists(model_path):
        print(f"❌ No se encontró el modelo: {model_path}")
        sys.exit(1)
        
    model = joblib.load(model_path)
    model_classes = model.classes_
    print(f"🤖 Modelo cargado exitosamente: {os.path.basename(model_path)}")
    print(f"   Clases registradas ({len(model_classes)}): {[ACTION_ID_TO_NAME[c] for c in model_classes]}")

    # 2. Iniciar hardware Azure Kinect
    k4a_path = r"C:\Program Files\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
    k4abt_path = r"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll"
    
    if not os.path.exists(k4a_path):
        k4a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k4a.dll"))
    if not os.path.exists(k4abt_path):
        k4abt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k4abt.dll"))
        
    pykinect.initialize_libraries(module_k4a_path=k4a_path, module_k4abt_path=k4abt_path, track_body=True)

    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
    device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

    print("🔌 Conectando con Azure Kinect DK...")
    device = pykinect.start_device(config=device_config)
    body_tracker = pykinect.start_body_tracker(model_type=pykinect.K4ABT_LITE_MODEL)
    print("✅ Azure Kinect DK conectado y rastreando a 30 FPS.")

    # 3. Variables de ventana e inferencia
    WINDOW_NAME = "SF3 Kinect - Live Gesture Classifier & Bias Auditor"
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

    WIDTH = 1360
    HEIGHT = 760
    LEFT_W = 760   # Área de esqueletos (Frontal + Sagital)
    RIGHT_W = 600  # Panel HUD de probabilidades y sesgos

    rolling_buffer = collections.deque(maxlen=35)
    last_ml_time = 0.0
    pred_action = "idle"
    pred_conf = 1.0
    pred_probs = np.zeros(len(model_classes), dtype=np.float32)
    current_feats = {}
    
    last_event_action = "idle"
    last_event_time = 0.0
    last_event_conf = 0.0
    last_printed_action = None
    
    fps_timer = time.time()
    frame_count = 0
    display_fps = 30.0

    print("\n🟢 TRANSMISIÓN EN VIVO INICIADA. Párate frente al sensor a unos 2.0 - 2.5 metros.")
    print("Presiona [Q] o [ESC] en la ventana gráfica para salir.\n")

    try:
        while True:
            capture = device.update()
            body_frame = body_tracker.update()
            
            frame_count += 1
            if time.time() - fps_timer >= 1.0:
                display_fps = frame_count / (time.time() - fps_timer)
                fps_timer = time.time()
                frame_count = 0

            has_body = (body_frame.get_num_bodies() > 0)
            joints_xyz_m = None

            if has_body:
                body = body_frame.get_body(0)
                joints_xyz_m = body.numpy()[:, :3] * 0.001  # Convertir mm a metros
                rolling_buffer.append(joints_xyz_m.copy())

            # Inferencia ML cada 80ms cuando el buffer tiene los 35 frames completos
            now = time.time()
            if has_body and len(rolling_buffer) == 35 and (now - last_ml_time) > 0.08:
                try:
                    buf_arr = np.array(rolling_buffer, dtype=np.float32)
                    current_feats = extract_clip_features(buf_arr, fps=30.0)
                    feat_vec = np.array([[current_feats[fn] for fn in FEATURE_NAMES]], dtype=np.float32)

                    # 1. Medir velocidad reciente de extremidades (últimos 6 frames ~ 200 ms)
                    recent_frames = buf_arr[-6:]
                    dt_r = 1.0 / 30.0
                    recent_v_wr_r = np.max(np.linalg.norm(np.diff(recent_frames[:, 14, :], axis=0), axis=1)) / dt_r
                    recent_v_wr_l = np.max(np.linalg.norm(np.diff(recent_frames[:, 7, :], axis=0), axis=1)) / dt_r
                    recent_v_ank_r = np.max(np.linalg.norm(np.diff(recent_frames[:, 24, :], axis=0), axis=1)) / dt_r
                    recent_v_ank_l = np.max(np.linalg.norm(np.diff(recent_frames[:, 20, :], axis=0), axis=1)) / dt_r
                    recent_v_pelvis = np.max(np.abs(np.diff(recent_frames[:, 0, 1]))) / dt_r

                    # ¿Extremidades en reposo / guardia en este instante?
                    is_recent_calm = (
                        recent_v_wr_r < 0.42 and
                        recent_v_wr_l < 0.42 and
                        recent_v_ank_r < 0.42 and
                        recent_v_ank_l < 0.42 and
                        recent_v_pelvis < 0.35
                    )

                    # Inferencia Random Forest sobre la ventana completa
                    raw_probs = model.predict_proba(feat_vec)[0]
                    sorted_p_idx = np.argsort(raw_probs)[::-1]
                    raw_top_idx = sorted_p_idx[0]
                    raw_class_id = model_classes[raw_top_idx]
                    raw_action = ACTION_ID_TO_NAME.get(raw_class_id, "unknown")
                    raw_conf = float(raw_probs[raw_top_idx])

                    # TRANSICIÓN RÁPIDA A GUARDIA / IDLE POST-MOVIMIENTO:
                    # Si el pico del golpe ya pasó y las extremidades volvieron a reposo:
                    if is_recent_calm:
                        last_frame = buf_arr[-1]
                        pelvis_y = last_frame[0, 1]
                        knee_r_y = last_frame[23, 1]
                        
                        # Comprobar si está sosteniendo agachado (rodillas flexionadas y pelvis baja)
                        is_holding_crouch = (current_feats.get("min_disp_pelvis_y", 0.0) < -0.16 and (pelvis_y - knee_r_y) > -0.40)
                        
                        # Comprobar si está sosteniendo bloqueo (muñecas juntas frente al pecho)
                        wrist_dist_now = np.linalg.norm(last_frame[14, :] - last_frame[7, :])
                        wrist_elev_r = last_frame[0, 1] - last_frame[14, 1]
                        wrist_elev_l = last_frame[0, 1] - last_frame[7, 1]
                        is_holding_block = (wrist_dist_now < 0.36 and wrist_elev_r > 0.40 and wrist_elev_l > 0.40)

                        if is_holding_crouch:
                            pred_action = "crouch"
                            pred_conf = 0.94
                            c_idx = list(model_classes).index(5) if 5 in model_classes else raw_top_idx
                            pred_probs = np.zeros_like(raw_probs)
                            pred_probs[c_idx] = 0.94
                            pred_probs[raw_top_idx] = 0.06
                        elif is_holding_block:
                            pred_action = "block"
                            pred_conf = 0.92
                            b_idx = list(model_classes).index(7) if 7 in model_classes else raw_top_idx
                            pred_probs = np.zeros_like(raw_probs)
                            pred_probs[b_idx] = 0.92
                            pred_probs[raw_top_idx] = 0.08
                        else:
                            # RETORNO INMEDIATO A IDLE / GUARDIA (< 200 ms)
                            pred_action = "idle"
                            pred_conf = 0.96
                            idle_idx = list(model_classes).index(0) if 0 in model_classes else 0
                            pred_probs = np.zeros_like(raw_probs)
                            pred_probs[idle_idx] = 0.96
                            rem_idx = raw_top_idx if raw_top_idx != idle_idx else (1 if len(raw_probs) > 1 else 0)
                            pred_probs[rem_idx] = 0.04
                    else:
                        # Fase activa del movimiento (golpe explosivo o subida/bajada activa)
                        pred_action = raw_action
                        pred_conf = raw_conf
                        pred_probs = raw_probs.copy()

                    # Registrar evento si es un golpe o bloqueo activo
                    if pred_action not in ("idle", "unknown") and pred_conf >= 0.55:
                        last_event_action = pred_action
                        last_event_time = now
                        last_event_conf = pred_conf
                        if last_printed_action != pred_action or (now - last_event_time) > 1.0:
                            s_idx = np.argsort(pred_probs)[::-1]
                            diff_2nd = (pred_probs[s_idx[0]] - pred_probs[s_idx[1]]) * 100.0
                            sec_name = ACTION_ID_TO_NAME.get(model_classes[s_idx[1]], "") if len(s_idx) > 1 else ""
                            print(f"🥊 [IMPACTO DETECTADO] {pred_action.upper()} ({pred_conf*100:.1f}%) | 2da opción: {sec_name} (+{diff_2nd:.1f}%)")
                            last_printed_action = pred_action

                    last_ml_time = now
                except Exception as ex:
                    pass

            # -------------------------------------------------------------
            # DIBUJAR LIENZO EN OPENCV
            # -------------------------------------------------------------
            canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
            canvas[:] = (18, 22, 28)

            # Separador vertical entre esqueleto y panel HUD
            cv2.line(canvas, (LEFT_W, 0), (LEFT_W, HEIGHT), (50, 60, 75), 2)

            # -------------------------------------------------------------
            # PANEL IZQUIERDO: VISUALIZACIÓN DUAL DEL ESQUELETO (3D)
            # -------------------------------------------------------------
            cv2.rectangle(canvas, (0, 0), (LEFT_W, 46), (28, 35, 48), -1)
            dist_z_str = f"Distancia Z: {joints_xyz_m[0, 2]:.2f}m" if has_body else "Buscando cuerpo..."
            z_col = (0, 255, 200) if has_body and (1.7 <= joints_xyz_m[0, 2] <= 2.8) else (0, 180, 255)
            
            cv2.putText(canvas, f"ESQUELETO EN VIVO (30 FPS) | {dist_z_str}", (16, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, z_col, 2, cv2.LINE_AA)
            cv2.putText(canvas, f"FPS: {display_fps:.1f}", (LEFT_W - 110, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (160, 175, 195), 1, cv2.LINE_AA)

            if has_body:
                pelvis_pos = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
                scale = 230.0
                cy = 400
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
                cv2.putText(canvas, "PÁRATE FRENTE AL KINECT PARA INICIAR", (120, 380),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 150, 255), 2, cv2.LINE_AA)

            # -------------------------------------------------------------
            # PANEL DERECHO: DETECCIÓN, PROBABILIDADES Y AUDITOR DE SESGOS
            # -------------------------------------------------------------
            rx = LEFT_W + 16
            
            # 1. TARJETA GIGANTE DE DETECCIÓN PRINCIPAL
            card_h = 105
            cv2.rectangle(canvas, (LEFT_W + 12, 12), (WIDTH - 12, 12 + card_h), (25, 32, 45), -1)
            
            conf_col = (0, 240, 120) if pred_conf >= 0.75 else ((0, 210, 255) if pred_conf >= 0.50 else (0, 100, 255))
            cv2.rectangle(canvas, (LEFT_W + 12, 12), (WIDTH - 12, 12 + card_h), conf_col, 2)

            cv2.putText(canvas, "MOVIMIENTO DETECTADO EN VIVO", (rx, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (170, 185, 205), 1, cv2.LINE_AA)
            cv2.putText(canvas, pred_action.upper(), (rx, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.05, conf_col, 3, cv2.LINE_AA)
            
            conf_str = f"Confianza: {pred_conf*100:.1f}%"
            cv2.putText(canvas, conf_str, (WIDTH - 210, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

            # Subtítulo explicativo
            if pred_action == "idle":
                if (now - last_event_time) < 2.5 and last_event_action != "idle":
                    cv2.putText(canvas, f"Ultimo golpe: {last_event_action.upper()} ({last_event_conf*100:.0f}%) hace {now - last_event_time:.1f}s -> Guardia recuperada",
                                (rx, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (0, 255, 200), 1, cv2.LINE_AA)
                else:
                    cv2.putText(canvas, "Guardia base activa (Reposo estatico) - En espera de golpe o bloqueo...",
                                (rx, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (140, 160, 185), 1, cv2.LINE_AA)
            elif pred_action == "block":
                cv2.putText(canvas, "BLOQUEO DINAMICO: Brazos elevados cubriendo pecho y cara",
                            (rx, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (0, 255, 220), 1, cv2.LINE_AA)
            else:
                cv2.putText(canvas, f"Ataque explosivo en progreso ({pred_action})",
                            (rx, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (200, 255, 220), 1, cv2.LINE_AA)

            # 2. GRÁFICO DE BARRAS DE PROBABILIDADES (¿A qué pose se parece?)
            bar_start_y = 135
            cv2.putText(canvas, "¿A QUÉ POSE SE ESTÁ PARECIENDO? (7 CLASES):", (rx, bar_start_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 220), 2, cv2.LINE_AA)

            sorted_idx = np.argsort(pred_probs)[::-1]
            max_bar_w = 340
            
            for i, idx in enumerate(sorted_idx):
                prob = float(pred_probs[idx])
                cid = model_classes[idx]
                act_str = ACTION_ID_TO_NAME.get(cid, "unknown")
                y_pos = bar_start_y + 24 + i * 36

                is_winner = (i == 0)
                b_color = (0, 220, 120) if is_winner else (55, 75, 100)
                txt_col = (255, 255, 255) if is_winner else (160, 175, 190)

                # Nombre de la pose
                cv2.putText(canvas, f"{act_str:12s}", (rx, y_pos + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.44, txt_col, 1, cv2.LINE_AA)

                # Barra de probabilidad
                bar_x = rx + 120
                bar_w = int(prob * max_bar_w)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + max_bar_w, y_pos + 20), (32, 40, 52), -1)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + bar_w, y_pos + 20), b_color, -1)
                cv2.rectangle(canvas, (bar_x, y_pos), (bar_x + max_bar_w, y_pos + 20), (60, 70, 85), 1)

                # Porcentaje numérico
                pct_str = f"{prob*100:4.1f}%"
                cv2.putText(canvas, pct_str, (bar_x + max_bar_w + 12, y_pos + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, txt_col, 1, cv2.LINE_AA)

            # 3. ALERTA DE SESGO / AMBIGÜEDAD
            bias_y = bar_start_y + 24 + len(sorted_idx) * 36 + 15
            top_prob = pred_probs[sorted_idx[0]]
            second_prob = pred_probs[sorted_idx[1]] if len(sorted_idx) > 1 else 0.0
            margin = top_prob - second_prob

            cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 60), (26, 32, 44), -1)

            if margin < 0.25:
                second_name = ACTION_ID_TO_NAME.get(model_classes[sorted_idx[1]], "")
                cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 60), (0, 120, 255), 2)
                cv2.putText(canvas, f"⚠️ ALERTA DE SESGO / AMBIGUEDAD (Margen: {margin*100:.1f}%)", (rx, bias_y + 24),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 180, 255), 2, cv2.LINE_AA)
                cv2.putText(canvas, f"El modelo duda entre '{pred_action}' ({top_prob*100:.0f}%) y '{second_name}' ({second_prob*100:.0f}%)",
                            (rx, bias_y + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 215, 230), 1, cv2.LINE_AA)
            else:
                cv2.rectangle(canvas, (LEFT_W + 12, bias_y), (WIDTH - 12, bias_y + 60), (0, 220, 120), 1)
                cv2.putText(canvas, f"🛡️ SIN SESGO: Decision clara (+{margin*100:.1f}% sobre la segunda opcion)", (rx, bias_y + 24),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 160), 2, cv2.LINE_AA)
                second_name = ACTION_ID_TO_NAME.get(model_classes[sorted_idx[1]], "")
                cv2.putText(canvas, f"Pose dominante firme sobre '{second_name}'. Prediccion solida.",
                            (rx, bias_y + 48), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (170, 190, 205), 1, cv2.LINE_AA)

            # 4. TELEMETRÍA CINEMÁTICA EN VIVO
            tele_y = bias_y + 72
            cv2.putText(canvas, "MÉTRICAS CINEMÁTICAS EN VIVO:", (rx, tele_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 220), 2, cv2.LINE_AA)

            v_wr = current_feats.get("peak_vel_wrist_r", 0.0)
            v_wl = current_feats.get("peak_vel_wrist_l", 0.0)
            v_fr = current_feats.get("peak_vel_foot_r", 0.0)
            v_fl = current_feats.get("peak_vel_foot_l", 0.0)
            d_pelvis = current_feats.get("net_disp_pelvis_y", 0.0) * 100.0
            w_dist = current_feats.get("min_wrist_distance", 0.0) * 100.0
            asym_arm = current_feats.get("arm_activity_asymmetry", 0.0)

            cv2.putText(canvas, f"• Puños: Der {v_wr:.2f} m/s | Izq {v_wl:.2f} m/s (Asim: {asym_arm:+.2f})",
                        (rx, tele_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"• Pies : Der {v_fr:.2f} m/s | Izq {v_fl:.2f} m/s",
                        (rx, tele_y + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"• Pelvis Y: {d_pelvis:+.1f} cm (Crouch < -15cm) | Muñecas: {w_dist:.1f} cm",
                        (rx, tele_y + 62), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (210, 220, 230), 1, cv2.LINE_AA)

            # Barra de estado inferior
            cv2.rectangle(canvas, (0, HEIGHT - 26), (WIDTH, HEIGHT), (14, 16, 22), -1)
            cv2.putText(canvas, "SF3 Live Kinect Detector | [Q] / [ESC] Salir | Haz un golpe o guardia para evaluar",
                        (16, HEIGHT - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (130, 145, 165), 1, cv2.LINE_AA)

            cv2.imshow(WINDOW_NAME, canvas)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord('q'), 27):
                break

    finally:
        print("\n🛑 Deteniendo Azure Kinect...")
        device.close()
        cv2.destroyAllWindows()
        print("✅ Sensor liberado exitosamente.")


if __name__ == "__main__":
    main()
