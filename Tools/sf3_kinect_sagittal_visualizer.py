"""
Street Fighter III: 3rd Strike - Kinect ML Gesture Studio & Dataset Recorder
Estudio de captura para las 8 acciones de combate:
0: idle, 1: punch_right, 2: punch_left, 3: kick_right, 4: kick_left, 5: crouch, 6: jump, 7: block

Características:
- Gestión y edición de perfil para 10 Sujetos (Nombre, Estatura cm, Sexo).
- Grabación limpia de clips temporales (35 frames / ~1.1s a 30 FPS).
- Mini-Video Player continuo en bucle con Replay permanente, pausa, avance frame-a-frame y re-grabación instantánea [R].
- Modo Mockup (--mock) con cinemática procedural realista para las 8 acciones sin requerir hardware físico.
- Inferencia en tiempo real con modelo Random Forest / ONNX.
"""

import sys
import os
import time
import json
import argparse
import collections
import glob
import numpy as np
import pandas as pd
import cv2

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Importar extractor cinemático local
sys.path.append(os.path.dirname(__file__))
from gesture_feature_extractor import (
    ACTION_CLASSES,
    ACTION_NAME_TO_ID,
    ACTION_ID_TO_NAME,
    FEATURE_NAMES,
    extract_clip_features
)

try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False

# Importación condicional de Azure Kinect
pykinect = None
try:
    import pykinect_azure as pykinect
    HAS_PYKINECT = True
except ImportError:
    HAS_PYKINECT = False


# -------------------------------------------------------------
# 1. ARTICULACIONES ESENCIALES Y HUESOS MOTRICES (18 NODOS)
# -------------------------------------------------------------
SIMPLIFIED_JOINTS = {
    "pelvis": 0,
    "pecho": 2,           # SPINE_CHEST: Inclinación torácica y torsión
    "cuello": 3,
    "cabeza": 26,
    "hombro_izq": 5,
    "codo_izq": 6,
    "muneca_izq": 7,
    "mano_izq": 8,        # HAND_LEFT: Punto real de impacto de puños
    "hombro_der": 12,
    "codo_der": 13,
    "muneca_der": 14,
    "mano_der": 15,       # HAND_RIGHT: Punto real de impacto de puños
    "cadera_izq": 18,
    "rodilla_izq": 19,
    "tobillo_izq": 20,
    "pie_izq": 21,        # FOOT_LEFT: Alcance real de patadas
    "cadera_der": 22,
    "rodilla_der": 23,
    "tobillo_der": 24,
    "pie_der": 25         # FOOT_RIGHT: Alcance real de patadas
}

# Conexiones óseas (ROJO = DERECHO, AZUL = IZQUIERDO, CIAN = TRONCO)
# Formato BGR OpenCV: Azul=(255, 60, 0), Rojo=(0, 40, 255)
SIMPLIFIED_BONES = [
    # Tronco y Cabeza (Cian)
    ("pelvis", "pecho", (0, 220, 255)),
    ("pecho", "cuello", (0, 220, 255)),
    ("cuello", "cabeza", (0, 255, 255)),
    # Extremidad Superior Izquierda (Azul)
    ("pecho", "hombro_izq", (255, 120, 0)),
    ("hombro_izq", "codo_izq", (255, 80, 0)),
    ("codo_izq", "muneca_izq", (255, 40, 0)),
    ("muneca_izq", "mano_izq", (255, 20, 0)),
    # Extremidad Superior Derecha (Rojo)
    ("pecho", "hombro_der", (0, 100, 255)),
    ("hombro_der", "codo_der", (0, 60, 255)),
    ("codo_der", "muneca_der", (0, 20, 255)),
    ("muneca_der", "mano_der", (0, 10, 255)),
    # Extremidad Inferior Izquierda (Azul)
    ("pelvis", "cadera_izq", (255, 140, 30)),
    ("cadera_izq", "rodilla_izq", (255, 90, 0)),
    ("rodilla_izq", "tobillo_izq", (255, 40, 0)),
    ("tobillo_izq", "pie_izq", (255, 30, 0)),
    # Extremidad Inferior Derecha (Rojo)
    ("pelvis", "cadera_der", (30, 80, 255)),
    ("cadera_der", "rodilla_der", (0, 50, 255)),
    ("rodilla_der", "tobillo_der", (0, 20, 255)),
    ("tobillo_der", "pie_der", (0, 10, 255))
]

# -------------------------------------------------------------
# 2. LAS 8 CLASES MAESTRAS DE COMBATE OFICIALES
# -------------------------------------------------------------
COMBAT_ACTIONS = [
    {
        "id": "idle",
        "key": "0",
        "name": "Guardia Base",
        "sub": "Idle Stance",
        "desc": "Postura de combate en reposo con puños arriba",
        "side": "AMBOS"
    },
    {
        "id": "punch_right",
        "key": "1",
        "name": "Puño Derecho",
        "sub": "Cross / Fuerte",
        "desc": "Extensión rápida del puño derecho al frente",
        "side": "DERECHA"
    },
    {
        "id": "punch_left",
        "key": "2",
        "name": "Puño Izquierdo",
        "sub": "Jab / Ligero",
        "desc": "Jab rápido directo con el puño adelantado",
        "side": "IZQUIERDA"
    },
    {
        "id": "kick_right",
        "key": "3",
        "name": "Patada Derecha",
        "sub": "Media / Fuerte",
        "desc": "Elevación y extensión de pierna derecha",
        "side": "DERECHA"
    },
    {
        "id": "kick_left",
        "key": "4",
        "name": "Patada Izquierda",
        "sub": "Ligera / Frontal",
        "desc": "Patada rápida delantera con pierna izquierda",
        "side": "IZQUIERDA"
    },
    {
        "id": "crouch",
        "key": "5",
        "name": "Agacharse",
        "sub": "Crouch Stance",
        "desc": "Flexión de rodillas y descenso de pelvis",
        "side": "AMBOS"
    },
    {
        "id": "jump",
        "key": "6",
        "name": "Salto",
        "sub": "Vertical Jump",
        "desc": "Impulso vertical ascendente del cuerpo",
        "side": "AMBOS"
    },
    {
        "id": "block",
        "key": "7",
        "name": "Bloqueo",
        "sub": "Cross Guard",
        "desc": "Brazos juntos y cruzados cubriendo el pecho",
        "side": "AMBOS"
    }
]


# -------------------------------------------------------------
# 3. GESTOR DE PERFILES DE PARTICIPANTES (10 SUJETOS)
# -------------------------------------------------------------
PROFILES_FILE = os.path.join(os.path.dirname(__file__), "dataset_raw", "subject_profiles.json")

def load_subject_profiles():
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    profiles = {}
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        except Exception:
            pass

    # Asegurar que existan los 40 perfiles para los 4 Sets (10 por set)
    updated = False
    for i in range(1, 41):
        set_idx = ((i - 1) // 10) + 1
        str_id = str(i)
        if str_id not in profiles:
            profiles[str_id] = {
                "id": i,
                "set_id": set_idx,
                "set_folder": f"set_{set_idx:02d}",
                "folder": f"subject_{i:02d}",
                "name": f"Persona {i}",
                "height_cm": 172,
                "gender": "M"  # M: Masculino, F: Femenino, O: Otro
            }
            updated = True
        else:
            # Asegurar claves de set
            p = profiles[str_id]
            if "set_id" not in p or "set_folder" not in p:
                p["set_id"] = set_idx
                p["set_folder"] = f"set_{set_idx:02d}"
                updated = True

    if updated or not os.path.exists(PROFILES_FILE):
        save_subject_profiles(profiles)
    return profiles

def save_subject_profiles(profiles):
    try:
        os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
    except Exception as ex:
        print(f"⚠️ Error guardando perfiles: {ex}")


# -------------------------------------------------------------
# 4. GENERADOR PROCEDIMENTAL DE ESQUELETO MOCK (30 FPS)
# -------------------------------------------------------------
class MockKinectSensor:
    """
    Simulador de Azure Kinect DK a 30 FPS con cinemática física realista
    para las 8 acciones de combate.
    """
    def __init__(self):
        self.base_skeleton = np.zeros((32, 3), dtype=np.float32)
        self._init_base_pose()
        self.active_action = None
        self.action_frame = 0
        self.total_action_frames = 35

    def _init_base_pose(self):
        # En mm: X=derecha (+), Y=abajo (+), Z=profundidad (+)
        self.base_skeleton[0] = [0.0, 950.0, 2200.0]     # Pelvis
        self.base_skeleton[1] = [0.0, 800.0, 2200.0]     # Spine Navel
        self.base_skeleton[2] = [0.0, 650.0, 2200.0]     # Spine Chest
        self.base_skeleton[3] = [0.0, 500.0, 2200.0]     # Neck
        self.base_skeleton[26] = [0.0, 350.0, 2200.0]    # Head
        self.base_skeleton[5] = [-180.0, 520.0, 2200.0]  # Shoulder Left
        self.base_skeleton[6] = [-260.0, 720.0, 2150.0]  # Elbow Left
        self.base_skeleton[7] = [-240.0, 880.0, 2050.0]  # Wrist Left
        self.base_skeleton[8] = [-240.0, 960.0, 2000.0]  # Hand Left
        self.base_skeleton[12] = [180.0, 520.0, 2200.0]  # Shoulder Right
        self.base_skeleton[13] = [260.0, 720.0, 2150.0]  # Elbow Right
        self.base_skeleton[14] = [240.0, 880.0, 2050.0]  # Wrist Right
        self.base_skeleton[15] = [240.0, 960.0, 2000.0]  # Hand Right
        self.base_skeleton[18] = [-100.0, 980.0, 2200.0] # Hip Left
        self.base_skeleton[19] = [-120.0, 1350.0, 2220.0]# Knee Left
        self.base_skeleton[20] = [-130.0, 1750.0, 2250.0]# Ankle Left
        self.base_skeleton[21] = [-130.0, 1850.0, 2180.0]# Foot Left
        self.base_skeleton[22] = [100.0, 980.0, 2200.0]  # Hip Right
        self.base_skeleton[23] = [120.0, 1350.0, 2220.0] # Knee Right
        self.base_skeleton[24] = [130.0, 1750.0, 2250.0] # Ankle Right
        self.base_skeleton[25] = [130.0, 1850.0, 2180.0] # Foot Right

    def trigger_action(self, action_name: str, duration_frames: int = 35):
        self.active_action = action_name
        self.action_frame = 0
        self.total_action_frames = duration_frames

    def get_frame(self) -> np.ndarray:
        t = time.time()
        frame = self.base_skeleton.copy()

        if self.active_action and self.action_frame < self.total_action_frames:
            progress = self.action_frame / float(self.total_action_frames - 1)
            phase = np.sin(np.pi * progress)
            act = self.active_action

            if act == "punch_right":
                frame[14, 2] -= 600.0 * phase  # Muñeca derecha hacia adelante (menor Z)
                frame[14, 1] -= 220.0 * phase  # Se eleva a nivel pectoral
                frame[15, 2] -= 680.0 * phase  # Mano derecha impacto máximo
                frame[15, 1] -= 220.0 * phase
                frame[13, 2] -= 320.0 * phase  # Codo acompaña
                frame[14, 0] += 40.0 * phase
                frame[15, 0] += 40.0 * phase
            elif act == "punch_left":
                frame[7, 2] -= 600.0 * phase   # Muñeca izquierda hacia adelante
                frame[7, 1] -= 220.0 * phase
                frame[8, 2] -= 680.0 * phase   # Mano izquierda impacto máximo
                frame[8, 1] -= 220.0 * phase
                frame[6, 2] -= 320.0 * phase
                frame[7, 0] -= 40.0 * phase
                frame[8, 0] -= 40.0 * phase
            elif act == "kick_right":
                frame[24, 1] -= 640.0 * phase  # Tobillo derecho sube
                frame[24, 2] -= 480.0 * phase  # Se proyecta al frente
                frame[25, 1] -= 680.0 * phase  # Pie derecho impacto de patada
                frame[25, 2] -= 540.0 * phase
                frame[23, 1] -= 400.0 * phase  # Rodilla sube
            elif act == "kick_left":
                frame[20, 1] -= 640.0 * phase  # Tobillo izquierdo sube
                frame[20, 2] -= 480.0 * phase
                frame[21, 1] -= 680.0 * phase  # Pie izquierdo impacto de patada
                frame[21, 2] -= 540.0 * phase
                frame[19, 1] -= 400.0 * phase
            elif act == "crouch":
                frame[:, 1] += 380.0 * phase   # Descenso en Y (+Y es abajo en Kinect)
                frame[19, 0] -= 70.0 * phase   # Rodillas abren
                frame[23, 0] += 70.0 * phase
            elif act == "jump":
                frame[:, 1] -= 460.0 * phase   # Ascenso en Y (-Y es arriba en Kinect)
                frame[20, 1] -= 120.0 * phase
                frame[24, 1] -= 120.0 * phase
                frame[21, 1] -= 120.0 * phase
                frame[25, 1] -= 120.0 * phase
            elif act == "block":
                # Brazos, muñecas y manos se cruzan frente al pecho
                frame[14, 0] -= 190.0 * phase  # Muñeca derecha al centro
                frame[15, 0] -= 190.0 * phase  # Mano derecha al centro
                frame[7, 0] += 190.0 * phase   # Muñeca izquierda al centro
                frame[8, 0] += 190.0 * phase   # Mano izquierda al centro
                frame[14, 1] -= 220.0 * phase  # Altura del pecho
                frame[15, 1] -= 220.0 * phase
                frame[7, 1] -= 220.0 * phase
                frame[8, 1] -= 220.0 * phase
                frame[14, 2] -= 160.0 * phase
                frame[15, 2] -= 160.0 * phase
                frame[7, 2] -= 160.0 * phase
                frame[8, 2] -= 160.0 * phase
                frame[13, 0] -= 80.0 * phase   # Codos compactados
                frame[6, 0] += 80.0 * phase

            self.action_frame += 1
            if self.action_frame >= self.total_action_frames:
                self.active_action = None
        else:
            # Respiración sutil en reposo
            breathe = np.sin(t * 3.0)
            frame[2, 1] += 8.0 * breathe
            frame[7, 1] += 5.0 * np.cos(t * 2.0)
            frame[14, 1] += 5.0 * np.cos(t * 2.0)

        frame += np.random.normal(0, 1.2, frame.shape)
        return frame


# -------------------------------------------------------------
# 5. UTILIDADES DE AUDIO, HEURÍSTICA Y CALIBRACIÓN
# -------------------------------------------------------------
def play_audio_tone(freq: int, duration_ms: int):
    """Emite un tono audible en Windows sin congelar el hilo de renderizado."""
    if sys.platform == "win32":
        import threading
        def _beep():
            try:
                import winsound
                winsound.Beep(int(freq), int(duration_ms))
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()


def evaluate_clip_quality(frames_arr: np.ndarray, action_info: dict) -> dict:
    """
    Analiza las propiedades cinemáticas del clip de 35 frames y produce
    un diagnóstico de calidad heurístico para asistir la auditoría manual del operador.
    """
    n_frames = len(frames_arr)
    act_id = action_info["id"]

    # Posición Z media (distancia al sensor en metros)
    pelvis_z = frames_arr[:, 0, 2]
    dist_z = float(np.mean(pelvis_z))

    # Velocidad de extremidades (m/s) a 30 FPS
    dt = 1.0 / 30.0
    vel_r_hand = np.linalg.norm(np.diff(frames_arr[:, 15, :], axis=0), axis=1) / dt
    vel_l_hand = np.linalg.norm(np.diff(frames_arr[:, 8, :], axis=0), axis=1) / dt
    vel_r_foot = np.linalg.norm(np.diff(frames_arr[:, 25, :], axis=0), axis=1) / dt
    vel_l_foot = np.linalg.norm(np.diff(frames_arr[:, 21, :], axis=0), axis=1) / dt

    # Velocidad y desplazamiento vertical de pelvis
    vel_pelvis_y = np.abs(np.diff(frames_arr[:, 0, 1])) / dt
    disp_pelvis_y = frames_arr[:, 0, 1] - frames_arr[0, 0, 1]

    # Proximidad de muñecas
    wrist_dist = np.linalg.norm(frames_arr[:, 14, :] - frames_arr[:, 7, :], axis=1)

    peak_vel = 0.0
    peak_frame = 0
    status = "GOOD"
    title = "OPTIMO"
    color = (0, 220, 100)  # BGR Verde
    issues = []

    if act_id == "punch_right":
        peak_vel = float(np.max(vel_r_hand))
        peak_frame = int(np.argmax(vel_r_hand))
        if peak_vel < 0.90:
            status = "POOR"
            title = "ALERTA: PUÑO MUY LENTO"
            color = (30, 40, 230)
            issues.append(f"Velocidad ({peak_vel:.2f} m/s) baja. Se recomienda > 1.2 m/s.")
        elif peak_vel < 1.30:
            status = "WARN"
            title = "AVISO: VELOCIDAD MODERADA"
            color = (0, 200, 240)
            issues.append(f"Velocidad ({peak_vel:.2f} m/s) aceptable pero moderada.")

    elif act_id == "punch_left":
        peak_vel = float(np.max(vel_l_hand))
        peak_frame = int(np.argmax(vel_l_hand))
        if peak_vel < 0.90:
            status = "POOR"
            title = "ALERTA: JAB MUY LENTO"
            color = (30, 40, 230)
            issues.append(f"Velocidad ({peak_vel:.2f} m/s) baja. Se recomienda > 1.2 m/s.")
        elif peak_vel < 1.30:
            status = "WARN"
            title = "AVISO: VELOCIDAD MODERADA"
            color = (0, 200, 240)
            issues.append(f"Velocidad ({peak_vel:.2f} m/s) aceptable.")

    elif act_id == "kick_right":
        peak_vel = float(np.max(vel_r_foot))
        peak_frame = int(np.argmax(vel_r_foot))
        if peak_vel < 1.10:
            status = "POOR"
            title = "ALERTA: PATADA LENTA O BAJA"
            color = (30, 40, 230)
            issues.append(f"Velocidad ({peak_vel:.2f} m/s) baja.")
        elif peak_vel < 1.50:
            status = "WARN"
            title = "AVISO: PATADA MODERADA"
            color = (0, 200, 240)

    elif act_id == "kick_left":
        peak_vel = float(np.max(vel_l_foot))
        peak_frame = int(np.argmax(vel_l_foot))
        if peak_vel < 1.10:
            status = "POOR"
            title = "ALERTA: PATADA LENTA O BAJA"
            color = (30, 40, 230)
            issues.append(f"Velocidad ({peak_vel:.2f} m/s) baja.")
        elif peak_vel < 1.50:
            status = "WARN"
            title = "AVISO: PATADA MODERADA"
            color = (0, 200, 240)

    elif act_id == "crouch":
        max_descend = float(np.max(disp_pelvis_y))  # +Y es abajo
        peak_vel = float(np.max(vel_pelvis_y))
        peak_frame = int(np.argmax(vel_pelvis_y))
        if max_descend < 0.12:
            status = "POOR"
            title = "ALERTA: AGACHADO INSUFICIENTE"
            color = (30, 40, 230)
            issues.append(f"Descenso ({max_descend*100:.1f} cm) menor a 15 cm.")

    elif act_id == "jump":
        max_ascend = float(np.abs(np.min(disp_pelvis_y)))  # -Y es arriba
        peak_vel = float(np.max(vel_pelvis_y))
        peak_frame = int(np.argmax(vel_pelvis_y))
        if max_ascend < 0.10:
            status = "POOR"
            title = "ALERTA: SALTO INSUFICIENTE"
            color = (30, 40, 230)
            issues.append(f"Elevación ({max_ascend*100:.1f} cm) menor a 12 cm.")

    elif act_id == "block":
        min_w_dist = float(np.min(wrist_dist))
        peak_vel = float(np.max([np.max(vel_r_hand), np.max(vel_l_hand)]))
        peak_frame = int(np.argmin(wrist_dist))
        if min_w_dist > 0.32:
            status = "POOR"
            title = "ALERTA: BRAZOS MUY SEPARADOS"
            color = (30, 40, 230)
            issues.append(f"Separación ({min_w_dist*100:.1f} cm) > 30 cm.")
        elif min_w_dist > 0.22:
            status = "WARN"
            title = "AVISO: BLOQUEO ABIERTO"
            color = (0, 200, 240)
            issues.append("Juntar más los antebrazos al pecho.")

    elif act_id == "idle":
        max_any_vel = float(np.max([np.max(vel_r_hand), np.max(vel_l_hand), np.max(vel_r_foot), np.max(vel_l_foot)]))
        peak_vel = max_any_vel
        peak_frame = 17
        if max_any_vel > 0.85:
            status = "WARN"
            title = "AVISO: MOVIMIENTO EN IDLE"
            color = (0, 200, 240)
            issues.append("Mantener postura quieta y estable.")

    # Centrado del pico cinemático en la ventana temporal
    if "punch" in act_id or "kick" in act_id:
        if peak_frame < 6:
            if status != "POOR":
                status = "WARN"
                title = "AVISO: GOLPE MUY TEMPRANO"
                color = (0, 200, 240)
            issues.append(f"Pico en frame {peak_frame+1} (inició antes de tiempo).")
        elif peak_frame > 29:
            status = "POOR"
            title = "ALERTA: GOLPE CORTADO AL FINAL"
            color = (30, 40, 230)
            issues.append(f"Pico en frame {peak_frame+1} (no terminó a tiempo).")

    # Encuadre en profundidad Z
    if dist_z < 1.70:
        issues.append(f"Sujeto muy cerca ({dist_z:.2f} m). Ideal: 2.1 - 2.5 m.")
    elif dist_z > 2.90:
        issues.append(f"Sujeto muy lejos ({dist_z:.2f} m). Ideal: 2.1 - 2.5 m.")

    advice = "Listo para guardar con [ENTER]" if status == "GOOD" else ("Revisa replay: [ENTER] Guardar  |  [R] Re-grabar" if status == "WARN" else "Recomendado: Presionar [R] para regrabar")

    return {
        "status": status,
        "title": title,
        "color": color,
        "peak_vel": peak_vel,
        "peak_frame": peak_frame,
        "dist_z": dist_z,
        "issues": issues,
        "advice": advice
    }


# -------------------------------------------------------------
# 6. ESTUDIO INTERACTIVO (GUI OPENCV + MINI-VIDEO + EDITOR)
# -------------------------------------------------------------
class GestureStudio:
    def __init__(self, is_mock: bool = False, initial_subject: int = 1):
        self.is_mock = is_mock
        self.profiles = load_subject_profiles()
        self.current_subject_id = max(1, min(40, initial_subject))  # 1 a 40
        self.current_set_id = ((self.current_subject_id - 1) // 10) + 1  # 1 a 4 (Set 1 a Set 4)
        self.selected_action_idx = 1  # default: punch_right

        # Edición de Nombre en Vivo
        self.is_editing_name = False
        self.edit_name_buffer = ""

        # Grabación de Clips
        self.is_recording = False
        self.recorded_frames = []
        self.target_clip_frames = 35
        self.recording_action = None

        # Countdown de 3 Segundos
        self.is_counting_down = False
        self.countdown_start_time = 0.0
        self.countdown_action = None
        self.countdown_beeps_played = set()

        # Mini-Video Replay (Permanente y en bucle)
        self.has_video = False
        self.video_frames = []          # Lista de 35 frames (shape: 32, 3) en metros
        self.video_action = None
        self.video_subject_info = None
        self.video_start_time = 0.0
        self.video_paused = False
        self.video_paused_frame = 0
        self.video_quality = None

        # Inferencia ML en Tiempo Real
        self.live_buffer = collections.deque(maxlen=35)
        self.ml_model = None
        self.ml_pred_label = "idle"
        self.ml_confidence = 0.0
        self.last_ml_time = 0.0

        # Zonas interactivas (Mouse)
        self.set_btn_rects = []         # [(rect, set_id)] para los 4 Sets
        self.action_btn_rects = []
        self.subj_prev_rect = (0, 0, 0, 0)
        self.subj_next_rect = (0, 0, 0, 0)
        self.name_box_rect = (0, 0, 0, 0)
        self.h_dec_rect = (0, 0, 0, 0)
        self.h_inc_rect = (0, 0, 0, 0)
        self.gender_rect = (0, 0, 0, 0)
        self.record_main_btn_rect = (0, 0, 0, 0)
        self.save_clip_btn_rect = (0, 0, 0, 0)
        self.rerecord_btn_rect = (0, 0, 0, 0)
        self.discard_btn_rect = (0, 0, 0, 0)
        self.pause_btn_rect = (0, 0, 0, 0)
        self.apose_btn_rect = (0, 0, 0, 0)

        # Cuotas por acción del sujeto (X / 20)
        self.quota_counts = {}
        self.total_subject_clips = 0
        self.update_quota_counts()

        # Resumen global de los 40 sujetos (10 por set)
        self.all_subjects_summary = {}
        self.subj_tile_rects = []
        self.update_all_subjects_summary()

        # Auditoría de guardado confirmado en disco
        self.last_saved_info = None
        self.last_saved_action_id = None
        self.last_saved_time = 0.0

        # Calibración A-Pose Biomecánica (Medidas corporales en A-Pose)
        self.is_calibrating = False
        self.calibration_start_time = 0.0
        self.calibration_frames = []

        self.last_msg = ""
        self.flash_until = 0.0

        self._load_ml_model()

    def _load_ml_model(self):
        model_path = os.path.join(os.path.dirname(__file__), "gesture_classifier.joblib")
        if HAS_JOBLIB and os.path.exists(model_path):
            try:
                self.ml_model = joblib.load(model_path)
                print(f"🤖 Modelo ML cargado: {model_path}")
            except Exception as ex:
                print(f"⚠️ Error cargando ML: {ex}")

    def get_current_profile(self):
        set_idx = ((self.current_subject_id - 1) // 10) + 1
        return self.profiles.get(str(self.current_subject_id), {
            "id": self.current_subject_id,
            "set_id": set_idx,
            "set_folder": f"set_{set_idx:02d}",
            "folder": f"subject_{self.current_subject_id:02d}",
            "name": f"Persona {self.current_subject_id}",
            "height_cm": 172,
            "gender": "M"
        })

    def get_subject_dir(self, subject_id=None):
        if subject_id is None:
            subject_id = self.current_subject_id
        set_idx = ((subject_id - 1) // 10) + 1
        p_obj = self.profiles.get(str(subject_id), {})
        s_folder = p_obj.get("folder", f"subject_{subject_id:02d}")
        set_folder = p_obj.get("set_folder", f"set_{set_idx:02d}")

        # Buscar primero en dataset_raw/set_XX/subject_YY
        path_set = os.path.join(os.path.dirname(__file__), "dataset_raw", set_folder, s_folder)
        if os.path.exists(path_set):
            return path_set
        # Fallback a dataset_raw/subject_YY
        path_flat = os.path.join(os.path.dirname(__file__), "dataset_raw", s_folder)
        if os.path.exists(path_flat):
            return path_flat
        return path_set

    def update_quota_counts(self):
        self.quota_counts = {}
        self.total_subject_clips = 0
        subj_dir = self.get_subject_dir(self.current_subject_id)
        for act in COMBAT_ACTIONS:
            act_id = act["id"]
            act_dir = os.path.join(subj_dir, act_id)
            if os.path.exists(act_dir):
                cnt = len([f for f in os.listdir(act_dir) if f.endswith(".csv")])
            else:
                cnt = 0
            self.quota_counts[act_id] = cnt
            self.total_subject_clips += cnt

    def update_all_subjects_summary(self):
        self.all_subjects_summary = {}
        for s_id in range(1, 41):
            s_dir = self.get_subject_dir(s_id)
            tot_clips = 0
            poses_with_data = 0
            if os.path.exists(s_dir):
                for act in COMBAT_ACTIONS:
                    act_d = os.path.join(s_dir, act["id"])
                    if os.path.exists(act_d):
                        try:
                            c = len([f for f in os.listdir(act_d) if f.endswith(".csv")])
                        except Exception:
                            c = 0
                        tot_clips += c
                        if c > 0:
                            poses_with_data += 1
            self.all_subjects_summary[s_id] = {
                "total_clips": tot_clips,
                "poses_with_data": poses_with_data
            }

    def get_subject_clip_count(self) -> int:
        return self.total_subject_clips

    def trigger_countdown(self, action_info=None):
        if self.is_recording or self.is_calibrating:
            return
        if action_info is None:
            action_info = COMBAT_ACTIONS[self.selected_action_idx]

        self.countdown_action = action_info
        self.countdown_start_time = time.time()
        self.countdown_beeps_played = set()
        self.is_counting_down = True
        prof = self.get_current_profile()
        self.last_msg = f"⏳ Preparando '{action_info['name']}' ({prof['name']})... ¡Cuenta 3.. 2.. 1!"

    def cancel_countdown(self):
        self.is_counting_down = False
        self.countdown_action = None
        self.last_msg = "Grabación cancelada."

    def start_recording(self, action_info=None):
        if action_info is None:
            action_info = COMBAT_ACTIONS[self.selected_action_idx]

        self.recording_action = action_info
        self.recorded_frames = []
        self.is_recording = True
        prof = self.get_current_profile()
        self.last_msg = f"🔴 Grabando '{action_info['name']}' ({prof['name']})..."
        print(f"🔴 [REC] {prof['name']} | Acción: {action_info['id']}")

    def finish_recording(self):
        self.is_recording = False
        if len(self.recorded_frames) < 15:
            self.last_msg = "⚠️ Grabación muy corta, descartada."
            return

        # Guardar en memoria de video para reproducción inmediata
        self.video_frames = list(self.recorded_frames)
        self.video_action = self.recording_action
        self.video_subject_info = dict(self.get_current_profile())
        self.video_start_time = time.time()
        self.video_paused = False
        self.has_video = True

        # Auditoría de Calidad Heurística instantánea
        frames_arr = np.array(self.video_frames, dtype=np.float32)
        self.video_quality = evaluate_clip_quality(frames_arr, self.video_action)

        self.last_msg = f"🎥 Video listo: {self.video_quality['title']} | [ENTER] Guardar (Reemplaza previa)  |  [R] Re-grabar"
        print(f"🎥 [VIDEO LISTO] {len(self.video_frames)} frames. Estado: {self.video_quality['title']}")

    def confirm_save_video(self):
        if not self.has_video or not self.video_frames:
            return

        act = self.video_action
        prof = self.video_subject_info or self.get_current_profile()
        subj_id = prof.get("id", self.current_subject_id)
        set_id = prof.get("set_id", ((subj_id - 1) // 10) + 1)
        set_folder = f"set_{set_id:02d}"
        subj_folder = prof.get("folder", f"subject_{subj_id:02d}")

        out_dir = os.path.join(os.path.dirname(__file__), "dataset_raw", set_folder, subj_folder, act["id"])
        os.makedirs(out_dir, exist_ok=True)

        # REEMPLAZO DETERMINISTA AISLADO:
        # Eliminar cualquier muestra previa (.csv) exclusivamente en la carpeta de este movimiento y este participante
        # (ej. el crouch de Jeremy solo reemplaza al crouch previo de Jeremy, dejando intactos sus otros golpes y a otros sujetos)
        existing_csvs = [f for f in os.listdir(out_dir) if f.endswith(".csv")]
        for old_f in existing_csvs:
            try:
                os.remove(os.path.join(out_dir, old_f))
                print(f"🔄 Reemplazando muestra previa de '{act['name']}': {old_f}")
            except Exception as ex:
                print(f"⚠️ Error al reemplazar muestra previa {old_f}: {ex}")

        sample_id = int(time.time() * 1000)
        csv_path = os.path.join(out_dir, f"sample_{sample_id}.csv")

        frames_arr = np.array(self.video_frames, dtype=np.float32)
        n_frames = len(frames_arr)
        flat_data = frames_arr.reshape((n_frames, 32 * 3))

        cols = [f"joint_{j}_{ax}" for j in range(32) for ax in ("x", "y", "z")]
        df_clip = pd.DataFrame(flat_data, columns=cols)
        df_clip.insert(0, "frame_idx", list(range(n_frames)))
        df_clip.insert(1, "subject_id", subj_folder)
        df_clip.insert(2, "subject_name", prof.get("name", ""))
        df_clip.insert(3, "subject_height_cm", prof.get("height_cm", 172))
        df_clip.insert(4, "subject_gender", prof.get("gender", "M"))
        df_clip.insert(5, "action_id", act["id"])

        df_clip.to_csv(csv_path, index=False)

        # Snapshot de auditoría (eliminar snapshot anterior de este sujeto y acción)
        review_dir = os.path.join(os.path.dirname(__file__), "captured_pose_reviews")
        os.makedirs(review_dir, exist_ok=True)
        for old_snap in glob.glob(os.path.join(review_dir, f"{subj_folder}_{act['id']}_*.png")):
            try:
                os.remove(old_snap)
            except Exception:
                pass

        img_path = os.path.join(review_dir, f"{subj_folder}_{act['id']}_{sample_id}.png")
        mid_idx = n_frames // 2
        snap = self.render_snapshot(frames_arr[mid_idx], act, prof["name"])
        cv2.imwrite(img_path, snap)

        # Verificar escritura física en disco
        file_saved_ok = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
        file_size_kb = (os.path.getsize(csv_path) / 1024.0) if file_saved_ok else 0.0

        # Actualizar cuotas locales y globales
        self.update_quota_counts()
        self.update_all_subjects_summary()

        cur_cnt = self.quota_counts.get(act["id"], 0)
        self.last_saved_info = {
            "success": file_saved_ok,
            "action_id": act["id"],
            "action_name": act["name"],
            "subject_id": subj_id,
            "subject_name": prof.get("name", ""),
            "set_id": set_id,
            "filename": os.path.basename(csv_path),
            "csv_path": csv_path,
            "time_str": time.strftime("%H:%M:%S"),
            "timestamp": time.time(),
            "count_now": cur_cnt,
            "size_kb": file_size_kb
        }
        self.last_saved_action_id = act["id"]
        self.last_saved_time = time.time()
        play_audio_tone(1500, 180)

        # Auto-avanzar a la siguiente acción si ya se completó
        if cur_cnt >= 1:
            for idx, a in enumerate(COMBAT_ACTIONS):
                if self.quota_counts.get(a["id"], 0) < 1:
                    self.selected_action_idx = idx
                    break

        self.last_msg = f"✅ Reemplazado con éxito: '{act['name']}' [{prof['name']} / Set {set_id}] ({file_size_kb:.1f} KB)"
        self.flash_until = time.time() + 0.6
        print(f"💾 ✅ [REEMPLAZO GUARDADO] {prof['name']} (Set {set_id} / {subj_folder}) | Acción: {act['id']} | Archivo: {os.path.basename(csv_path)}")

    def trigger_apose_calibration(self):
        if self.is_recording or self.is_counting_down:
            return
        self.is_calibrating = True
        self.calibration_start_time = time.time()
        self.calibration_frames = []
        play_audio_tone(700, 160)
        self.last_msg = "📐 CALIBRACIÓN A-POSE: Brazos a 45° y piernas abiertas. Sostén 2 segundos..."

    def finish_apose_calibration(self):
        self.is_calibrating = False
        if len(self.calibration_frames) < 15:
            self.last_msg = "⚠️ Calibración cancelada: Pocos frames capturados."
            return

        calib_arr = np.mean(self.calibration_frames, axis=0)  # Shape: (32, 3) en metros
        arm_r = float(np.linalg.norm(calib_arr[12] - calib_arr[13]) + np.linalg.norm(calib_arr[13] - calib_arr[14])) * 100.0
        arm_l = float(np.linalg.norm(calib_arr[5] - calib_arr[6]) + np.linalg.norm(calib_arr[6] - calib_arr[7])) * 100.0
        leg_r = float(np.linalg.norm(calib_arr[22] - calib_arr[23]) + np.linalg.norm(calib_arr[23] - calib_arr[24])) * 100.0
        leg_l = float(np.linalg.norm(calib_arr[18] - calib_arr[19]) + np.linalg.norm(calib_arr[19] - calib_arr[20])) * 100.0
        torso = float(np.linalg.norm(calib_arr[0] - calib_arr[3])) * 100.0
        arm_span = float(np.linalg.norm(calib_arr[14] - calib_arr[7])) * 100.0

        prof = self.get_current_profile()
        prof["calibrated_biometrics"] = {
            "arm_r_cm": round(arm_r, 1),
            "arm_l_cm": round(arm_l, 1),
            "leg_r_cm": round(leg_r, 1),
            "leg_l_cm": round(leg_l, 1),
            "torso_cm": round(torso, 1),
            "arm_span_cm": round(arm_span, 1),
            "calibrated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.profiles[str(self.current_subject_id)] = prof
        save_subject_profiles(self.profiles)

        play_audio_tone(1200, 280)
        self.last_msg = f"✅ Calibración guardada: Brazo {arm_r:.0f}cm | Pierna {leg_r:.0f}cm | Torso {torso:.0f}cm"
        print(f"📐 [CALIBRACIÓN A-POSE] {prof['name']} -> Brazo:{arm_r:.1f}cm, Pierna:{leg_r:.1f}cm, Torso:{torso:.1f}cm, Envergadura:{arm_span:.1f}cm")

    def render_snapshot(self, joints_xyz_m, act, subj_name):
        snap_w, snap_h = 560, 380
        snap = np.zeros((snap_h, snap_w, 3), dtype=np.uint8)
        snap[:] = (18, 22, 28)

        cv2.rectangle(snap, (0, 0), (snap_w, 42), (32, 45, 62), -1)
        cv2.putText(snap, f"AUDIT: {act['name'].upper()} ({subj_name})", (14, 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 200), 1, cv2.LINE_AA)

        pelvis = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
        scale = 160.0
        cy = 200
        cx_f, cx_s = 140, 420

        cv2.line(snap, (280, 48), (280, snap_h - 10), (45, 52, 65), 1)

        f_pts = {}
        for j_n, j_i in SIMPLIFIED_JOINTS.items():
            rx = (joints_xyz_m[j_i, 0] - pelvis[0]) * scale
            ry = (joints_xyz_m[j_i, 1] - pelvis[1]) * scale
            f_pts[j_n] = np.array([cx_f + rx, cy + ry])
        draw_simplified_skeleton(snap, f_pts)

        s_pts = {}
        for j_n, j_i in SIMPLIFIED_JOINTS.items():
            rz = (joints_xyz_m[j_i, 2] - pelvis[2]) * scale
            ry = (joints_xyz_m[j_i, 1] - pelvis[1]) * scale
            s_pts[j_n] = np.array([cx_s + rz, cy + ry])
        draw_simplified_skeleton(snap, s_pts)

        return snap

    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # 0. Clic en Tabs de Sets (SET 1 a SET 4)
            for rect, set_num in self.set_btn_rects:
                bx, by, bw, bh = rect
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.current_set_id = set_num
                    first_in_set = (set_num - 1) * 10 + 1
                    last_in_set = set_num * 10
                    if not (first_in_set <= self.current_subject_id <= last_in_set):
                        self.current_subject_id = first_in_set
                    self.update_quota_counts()
                    self.update_all_subjects_summary()
                    self.last_msg = f"📁 Set cambiado a: SET {set_num} (Sujetos {first_in_set:02d} - {last_in_set:02d})"
                    return

            # 0.1. Clic en los 10 sujetos del Set activo
            for rect, s_id in self.subj_tile_rects:
                sx, sy, sw, sh = rect
                if sx <= x <= sx + sw and sy <= y <= sy + sh:
                    self.current_subject_id = s_id
                    self.current_set_id = ((s_id - 1) // 10) + 1
                    self.update_quota_counts()
                    self.update_all_subjects_summary()
                    self.last_msg = f"👤 Sujeto cambiado a: Sujeto {s_id:02d} ({self.get_current_profile()['name']}) [SET {self.current_set_id}]"
                    return

            # 1. Selector de Sujeto: Anterior / Siguiente (1 a 40 con sincronización de Set)
            px, py, pw, ph = self.subj_prev_rect
            if px <= x <= px + pw and py <= y <= py + ph:
                self.current_subject_id = max(1, self.current_subject_id - 1)
                self.current_set_id = ((self.current_subject_id - 1) // 10) + 1
                self.update_quota_counts()
                self.update_all_subjects_summary()
                self.last_msg = f"👤 Sujeto cambiado a: Sujeto {self.current_subject_id:02d} [SET {self.current_set_id}]"
                return

            nx, ny, nw, nh = self.subj_next_rect
            if nx <= x <= nx + nw and ny <= y <= ny + nh:
                self.current_subject_id = min(40, self.current_subject_id + 1)
                self.current_set_id = ((self.current_subject_id - 1) // 10) + 1
                self.update_quota_counts()
                self.update_all_subjects_summary()
                self.last_msg = f"👤 Sujeto cambiado a: Sujeto {self.current_subject_id:02d} [SET {self.current_set_id}]"
                return

            # 2. Clic en Caja de Nombre para editar
            bx, by, bw, bh = self.name_box_rect
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.is_editing_name = True
                self.edit_name_buffer = self.get_current_profile()["name"]
                self.last_msg = "✏️ Escribe el nuevo nombre y presiona [ENTER] para confirmar."
                return
            elif self.is_editing_name:
                self.is_editing_name = False

            # 3. Estatura: [-] y [+]
            dx, dy, dw, dh = self.h_dec_rect
            if dx <= x <= dx + dw and dy <= y <= dy + dh:
                prof = self.get_current_profile()
                prof["height_cm"] = max(140, prof["height_cm"] - 2)
                save_subject_profiles(self.profiles)
                return

            ix, iy, iw, ih = self.h_inc_rect
            if ix <= x <= ix + iw and iy <= y <= iy + ih:
                prof = self.get_current_profile()
                prof["height_cm"] = min(210, prof["height_cm"] + 2)
                save_subject_profiles(self.profiles)
                return

            # 4. Sexo / Género: [M] -> [F] -> [O]
            gx, gy, gw, gh = self.gender_rect
            if gx <= x <= gx + gw and gy <= y <= gy + gh:
                prof = self.get_current_profile()
                g_cycle = {"M": "F", "F": "O", "O": "M"}
                prof["gender"] = g_cycle.get(prof.get("gender", "M"), "M")
                save_subject_profiles(self.profiles)
                return

            # 4.1. Calibración A-Pose
            ax, ay, aw, ah = self.apose_btn_rect
            if ax <= x <= ax + aw and ay <= y <= ay + ah:
                self.trigger_apose_calibration()
                return

            # 5. Clic en las 8 Acciones de Combate
            for rect, idx in self.action_btn_rects:
                ax, ay, aw, ah = rect
                if ax <= x <= ax + aw and ay <= y <= ay + ah:
                    self.selected_action_idx = idx
                    return

            # 6. Botón Principal de Grabar
            rx, ry, rw, rh = self.record_main_btn_rect
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.trigger_countdown()
                return

            # 7. Botones del Mini-Video Player
            if self.has_video:
                sx, sy, sw, sh = self.save_clip_btn_rect
                if sx <= x <= sx + sw and sy <= y <= sy + sh:
                    self.confirm_save_video()
                    return

                rx, ry, rw, rh = self.rerecord_btn_rect
                if rx <= x <= rx + rw and ry <= y <= ry + rh:
                    self.trigger_countdown(self.video_action)
                    return

                dx, dy, dw, dh = self.discard_btn_rect
                if dx <= x <= dx + dw and dy <= y <= dy + dh:
                    self.has_video = False
                    self.video_frames = []
                    self.last_msg = "🗑️ Video descartado."
                    return

                px, py, pw, ph = self.pause_btn_rect
                if px <= x <= px + pw and py <= y <= py + ph:
                    self.video_paused = not self.video_paused
                    return


def draw_simplified_skeleton(canvas, joint_screen_pts, color_override=None):
    """
    Dibuja los 18 huesos motrices esenciales con código cromático limpio.
    """
    for start_name, end_name, b_color in SIMPLIFIED_BONES:
        if start_name in joint_screen_pts and end_name in joint_screen_pts:
            pt1 = tuple(joint_screen_pts[start_name].astype(int))
            pt2 = tuple(joint_screen_pts[end_name].astype(int))
            col = color_override if color_override else b_color
            cv2.line(canvas, pt1, pt2, col, 3, cv2.LINE_AA)

    for name, pt in joint_screen_pts.items():
        c = tuple(pt.astype(int))
        if "mano_der" in name or "pie_der" in name:
            cv2.circle(canvas, c, 7, (0, 30, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
        elif "mano_izq" in name or "pie_izq" in name:
            cv2.circle(canvas, c, 7, (255, 50, 0), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
        elif "_der" in name:
            cv2.circle(canvas, c, 5, (0, 40, 255), -1, cv2.LINE_AA)
        elif "_izq" in name:
            cv2.circle(canvas, c, 5, (255, 60, 0), -1, cv2.LINE_AA)
        elif "cabeza" in name:
            cv2.circle(canvas, c, 8, (0, 255, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 10, (255, 255, 255), 1, cv2.LINE_AA)
        elif "cuello" in name or "pelvis" in name or "pecho" in name:
            cv2.circle(canvas, c, 6, (0, 240, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 8, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, c, 5, (220, 220, 220), -1, cv2.LINE_AA)


def main():
    parser = argparse.ArgumentParser(description="SF3 Azure Kinect - ML Gesture Studio (8 Clases)")
    parser.add_argument("--mock", action="store_true", help="Inicia en modo simulación procedural sin sensor físico")
    parser.add_argument("--subject", type=int, default=1, help="ID inicial del sujeto (1 a 10)")
    args = parser.parse_args()

    print("=" * 75)
    print("🥊 SF3 - KINECT GESTURE STUDIO (8 ACCIONES DE COMBATE + MINI-VIDEO)")
    print("=" * 75)
    print(f"Modo: {'MOCKUP PROCEDURAL (Simulación)' if args.mock else 'AZURE KINECT SDK FÍSICO'}")
    print(f"Sujeto inicial: Sujeto {args.subject:02d} (Atajos: '[' y ']' para cambiar)")
    print("Atajos rápidos: Teclas 0 a 7 para seleccionar/grabar las 8 acciones de combate")
    print("=" * 75)

    use_mock = args.mock
    device = None
    body_tracker = None
    mock_sensor = None

    if use_mock or not HAS_PYKINECT:
        use_mock = True
        mock_sensor = MockKinectSensor()
    else:
        k4a_path = r"C:\Program Files\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
        k4abt_path = r"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll"

        try:
            pykinect.initialize_libraries(
                module_k4a_path=k4a_path,
                module_k4abt_path=k4abt_path,
                track_body=True
            )
            device_config = pykinect.default_configuration
            device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
            device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
            device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

            device = pykinect.start_device(config=device_config)
            body_tracker = pykinect.start_body_tracker(model_type=pykinect.K4ABT_LITE_MODEL)
            print("✅ Conectado exitosamente con Azure Kinect DK.")
        except Exception as ex:
            print(f"⚠️ No se pudo iniciar Azure Kinect físico ({ex}). Activando MODO MOCKUP...")
            use_mock = True
            mock_sensor = MockKinectSensor()

    studio = GestureStudio(is_mock=use_mock, initial_subject=args.subject)

    WINDOW_NAME = "SF3 - Kinect ML Gesture Studio (8 Clases + Mini-Video Replay)"
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, studio.on_mouse_click)

    WIDTH = 1420
    HEIGHT = 840
    LEFT_W = 390
    RIGHT_W = 410

    fps_timer = time.time()
    frame_count = 0
    display_fps = 30.0

    while True:
        has_body = False
        joints_xyz_m = None

        if use_mock:
            joints_raw_mm = mock_sensor.get_frame()
            joints_xyz_m = joints_raw_mm * 0.001
            has_body = True
        else:
            capture = device.update()
            body_frame = body_tracker.update()
            if body_frame.get_num_bodies() > 0:
                body = body_frame.get_body(0)
                joints_xyz_m = body.numpy()[:, :3] * 0.001
                has_body = True

        # FPS
        frame_count += 1
        if time.time() - fps_timer >= 1.0:
            display_fps = frame_count / (time.time() - fps_timer)
            fps_timer = time.time()
            frame_count = 0

        # Lienzo principal
        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        canvas[:] = (20, 22, 28)

        if time.time() < studio.flash_until:
            canvas[:] = (25, 60, 35)

        # -------------------------------------------------------------
        # 1. PANEL LATERAL IZQUIERDO: SUJETO (EDITABLE) Y LAS 8 ACCIONES
        # -------------------------------------------------------------
        cv2.rectangle(canvas, (0, 0), (LEFT_W, HEIGHT), (26, 30, 38), -1)
        cv2.line(canvas, (LEFT_W, 0), (LEFT_W, HEIGHT), (55, 62, 78), 2)

        # TARJETA DEL SUJETO ACTIVO (Panel Izquierdo Superior)
        cv2.rectangle(canvas, (12, 8), (LEFT_W - 12, 222), (30, 36, 48), -1)
        cv2.rectangle(canvas, (12, 8), (LEFT_W - 12, 222), (0, 200, 255), 1)

        prof = studio.get_current_profile()

        # Selector de Sujeto: [<] SUJETO XX / 40 [SET Y] [>]
        sb_y = 12
        studio.subj_prev_rect = (18, sb_y, 26, 24)
        cv2.rectangle(canvas, (18, sb_y), (44, sb_y + 24), (45, 58, 76), -1)
        cv2.rectangle(canvas, (18, sb_y), (44, sb_y + 24), (0, 200, 255), 1)
        cv2.putText(canvas, "<", (24, sb_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)

        mid_bx = 48
        mid_bw = LEFT_W - 96
        cv2.rectangle(canvas, (mid_bx, sb_y), (mid_bx + mid_bw, sb_y + 24), (36, 46, 62), -1)
        subj_title = f"S{studio.current_subject_id:02d}/40 [SET {studio.current_set_id}] {prof['name'][:13]}"
        cv2.putText(canvas, subj_title, (mid_bx + 8, sb_y + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 220), 2, cv2.LINE_AA)

        next_x = mid_bx + mid_bw + 4
        studio.subj_next_rect = (next_x, sb_y, 26, 24)
        cv2.rectangle(canvas, (next_x, sb_y), (next_x + 26, sb_y + 24), (45, 58, 76), -1)
        cv2.rectangle(canvas, (next_x, sb_y), (next_x + 26, sb_y + 24), (0, 200, 255), 1)
        cv2.putText(canvas, ">", (next_x + 7, sb_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)

        # TABS DE LOS 4 SETS (SET 1 a SET 4)
        studio.set_btn_rects.clear()
        tab_y = 40
        tab_h = 20
        tab_w = 85
        for s_idx in range(1, 5):
            tab_x = 18 + (s_idx - 1) * (tab_w + 5)
            tab_rect = (tab_x, tab_y, tab_w, tab_h)
            studio.set_btn_rects.append((tab_rect, s_idx))

            is_active_set = (s_idx == studio.current_set_id)
            set_start = (s_idx - 1) * 10 + 1
            set_end = s_idx * 10
            set_clips = sum(studio.all_subjects_summary.get(sid, {}).get("total_clips", 0) for sid in range(set_start, set_end + 1))

            if is_active_set:
                s_bg = (60, 95, 140)
                s_bdr = (0, 255, 220)
                s_thick = 2
            else:
                s_bg = (24, 28, 36)
                s_bdr = (55, 65, 80)
                s_thick = 1

            cv2.rectangle(canvas, (tab_x, tab_y), (tab_x + tab_w, tab_y + tab_h), s_bg, -1)
            cv2.rectangle(canvas, (tab_x, tab_y), (tab_x + tab_w, tab_y + tab_h), s_bdr, s_thick)
            set_txt = f"SET {s_idx} ({set_clips})"
            cv2.putText(canvas, set_txt, (tab_x + 6, tab_y + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.31,
                        (255, 255, 255) if is_active_set else (150, 165, 185), 1, cv2.LINE_AA)

        # MATRIZ RÁPIDA DE LOS 10 MODELOS DEL SET ACTIVO (2 filas x 5 columnas clicables)
        studio.subj_tile_rects.clear()
        t_w = 67
        t_h = 19
        start_s = (studio.current_set_id - 1) * 10 + 1
        end_s = studio.current_set_id * 10
        tile_base_y = 64

        for i, s_idx in enumerate(range(start_s, end_s + 1)):
            c_col = i % 5
            c_row = i // 5
            tx = 18 + c_col * (t_w + 5)
            ty = tile_base_y + c_row * (t_h + 3)
            s_rect = (tx, ty, t_w, t_h)
            studio.subj_tile_rects.append((s_rect, s_idx))

            s_info = studio.all_subjects_summary.get(s_idx, {"total_clips": 0, "poses_with_data": 0})
            s_clips = s_info["total_clips"]

            is_cur_s = (s_idx == studio.current_subject_id)
            if is_cur_s:
                t_bg = (60, 95, 140)
                t_bdr = (0, 255, 220)
                bdr_thick = 2
            elif s_clips >= 7:
                t_bg = (20, 80, 40)
                t_bdr = (0, 230, 100)
                bdr_thick = 1
            elif s_clips > 0:
                t_bg = (34, 52, 72)
                t_bdr = (0, 200, 255)
                bdr_thick = 1
            else:
                t_bg = (24, 28, 36)
                t_bdr = (50, 58, 70)
                bdr_thick = 1

            cv2.rectangle(canvas, (tx, ty), (tx + t_w, ty + t_h), t_bg, -1)
            cv2.rectangle(canvas, (tx, ty), (tx + t_w, ty + t_h), t_bdr, bdr_thick)

            t_label = f"S{s_idx:02d}:{s_clips}"
            cv2.putText(canvas, t_label, (tx + 5, ty + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.31,
                        (255, 255, 255) if (is_cur_s or s_clips > 0) else (140, 150, 165), 1, cv2.LINE_AA)

        # Resumen global de dataset de los 40 sujetos
        tot_all_clips = sum(s["total_clips"] for s in studio.all_subjects_summary.values())
        subjs_with_data = sum(1 for s in studio.all_subjects_summary.values() if s["total_clips"] > 0)
        active_set_clips = sum(studio.all_subjects_summary.get(sid, {}).get("total_clips", 0) for sid in range(start_s, end_s + 1))
        cv2.putText(canvas, f"Set {studio.current_set_id}: {active_set_clips}/70 clips | Total 40: {tot_all_clips}/280 ({subjs_with_data}/40)",
                    (18, 114), cv2.FONT_HERSHEY_SIMPLEX, 0.31, (170, 195, 220), 1, cv2.LINE_AA)

        # Campo: Nombre / Alias (Clic o tecla 'E' para editar)
        ny = 124
        cv2.putText(canvas, "Nombre:", (18, ny + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)
        studio.name_box_rect = (76, ny, LEFT_W - 96, 22)
        name_bg = (50, 75, 110) if studio.is_editing_name else (22, 26, 34)
        name_bdr = (0, 255, 200) if studio.is_editing_name else (55, 65, 80)
        cv2.rectangle(canvas, (76, ny), (LEFT_W - 20, ny + 22), name_bg, -1)
        cv2.rectangle(canvas, (76, ny), (LEFT_W - 20, ny + 22), name_bdr, 2 if studio.is_editing_name else 1)

        disp_name = (studio.edit_name_buffer + "_") if studio.is_editing_name else prof["name"]
        cv2.putText(canvas, disp_name[:18], (82, ny + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (255, 255, 255), 1, cv2.LINE_AA)

        # Campo: Estatura, Sexo y Calibración A-Pose
        hy = 150
        cv2.putText(canvas, "Estatura:", (18, hy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)

        # Botón [-]
        studio.h_dec_rect = (76, hy, 22, 22)
        cv2.rectangle(canvas, (76, hy), (98, hy + 22), (40, 50, 65), -1)
        cv2.rectangle(canvas, (76, hy), (98, hy + 22), (60, 75, 95), 1)
        cv2.putText(canvas, "-", (83, hy + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.putText(canvas, f"{prof['height_cm']}cm", (104, hy + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 200), 1, cv2.LINE_AA)

        # Botón [+]
        studio.h_inc_rect = (158, hy, 22, 22)
        cv2.rectangle(canvas, (158, hy), (180, hy + 22), (40, 50, 65), -1)
        cv2.rectangle(canvas, (158, hy), (180, hy + 22), (60, 75, 95), 1)
        cv2.putText(canvas, "+", (163, hy + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2, cv2.LINE_AA)

        # Sexo / Género Toggle
        cv2.putText(canvas, "Sexo:", (190, hy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)
        studio.gender_rect = (230, hy, 52, 22)
        cv2.rectangle(canvas, (230, hy), (282, hy + 22), (40, 60, 85), -1)
        cv2.rectangle(canvas, (230, hy), (282, hy + 22), (0, 200, 255), 1)
        g_label = "Masc" if prof["gender"] == "M" else ("Fem" if prof["gender"] == "F" else "Otro")
        cv2.putText(canvas, g_label, (237, hy + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (255, 255, 255), 1, cv2.LINE_AA)

        # Botón Calibrar A-Pose [C]
        studio.apose_btn_rect = (290, hy, 78, 22)
        cv2.rectangle(canvas, (290, hy), (368, hy + 22), (35, 55, 75), -1)
        cv2.rectangle(canvas, (290, hy), (368, hy + 22), (0, 255, 200), 1)
        cv2.putText(canvas, "[C] A-Pose", (295, hy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 200), 1, cv2.LINE_AA)

        # Medidas Biométricas (A-Pose) y Progreso de Sujeto Activo
        cb = prof.get("calibrated_biometrics")
        if cb:
            cal_txt = f"A-Pose: B={cb['arm_r_cm']:.0f} P={cb['leg_r_cm']:.0f} T={cb['torso_cm']:.0f}cm"
            cv2.putText(canvas, cal_txt, (18, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.33, (0, 255, 200), 1, cv2.LINE_AA)
        else:
            cv2.putText(canvas, "A-Pose: Sin calibrar aún (Presiona [C])", (18, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.32, (150, 165, 185), 1, cv2.LINE_AA)

        pct = min(100, int((studio.total_subject_clips / 7.0) * 100))
        cv2.putText(canvas, f"Progreso Sujeto {studio.current_subject_id:02d}: {studio.total_subject_clips}/7 acciones ({pct}%)",
                    (18, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 230, 180), 1, cv2.LINE_AA)

        # LISTA DE LAS ACCIONES DE COMBATE
        cv2.putText(canvas, "ACCIONES DE COMBATE (Teclas 0 - 6):", (14, 236),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 220, 255), 2, cv2.LINE_AA)

        studio.action_btn_rects.clear()
        act_y_start = 244
        act_h = 56

        for a_idx, act in enumerate(COMBAT_ACTIONS):
            by = act_y_start + a_idx * (act_h + 6)
            rect = (12, by, LEFT_W - 24, act_h)
            studio.action_btn_rects.append((rect, a_idx))

            is_selected = (a_idx == studio.selected_action_idx)
            cnt = studio.quota_counts.get(act["id"], 0)
            is_recent = (studio.last_saved_action_id == act["id"]) and ((time.time() - studio.last_saved_time) < 18.0)

            # Fondo y bordes
            if is_recent:
                bg_col = (20, 60, 40)
                bdr_col = (0, 255, 120)
                bdr_w = 3
            elif is_selected:
                bg_col = (60, 95, 140)
                bdr_col = (0, 255, 220)
                bdr_w = 2
            else:
                bg_col = (30, 36, 48)
                bdr_col = (50, 60, 75)
                bdr_w = 1

            cv2.rectangle(canvas, (12, by), (LEFT_W - 12, by + act_h), bg_col, -1)
            cv2.rectangle(canvas, (12, by), (LEFT_W - 12, by + act_h), bdr_col, bdr_w)

            # Badge numérico [0] .. [7]
            cv2.rectangle(canvas, (18, by + 8), (52, by + 48), (20, 25, 35), -1)
            cv2.putText(canvas, f"[{act['key']}]", (22, by + 33),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 200) if is_selected else (160, 170, 180), 2, cv2.LINE_AA)

            # Nombre y Subtítulo
            cv2.putText(canvas, act["name"], (58, by + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, act["sub"], (58, by + 44),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (180, 200, 220) if is_selected else (130, 145, 160), 1, cv2.LINE_AA)

            # BADGE PERMANENTE DE ESTADO DE LA POSE (Para no depender de memoria)
            pill_x = LEFT_W - 148
            pill_y = by + 28
            pill_w = 132
            pill_h = 22

            if cnt == 0:
                p_bg = (24, 28, 36)
                p_bdr = (60, 70, 85)
                p_col = (140, 150, 165)
                p_txt = "[-] PENDIENTE"
            else:
                p_bg = (15, 65, 32)
                p_bdr = (0, 240, 120)
                p_col = (0, 255, 130)
                p_txt = f"[OK] GUARDADO ({cnt})"

            cv2.rectangle(canvas, (pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h), p_bg, -1)
            cv2.rectangle(canvas, (pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h), p_bdr, 1)
            cv2.putText(canvas, p_txt, (pill_x + 8, pill_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, p_col, 1, cv2.LINE_AA)

            # Etiqueta de lado [DER] / [IZQ] / [AMB]
            side_col = (0, 140, 255) if act["side"] == "DERECHA" else ((255, 120, 0) if act["side"] == "IZQUIERDA" else (0, 255, 180))
            cv2.putText(canvas, f"[{act['side'][:3]}]", (LEFT_W - 48, by + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.33, side_col, 1, cv2.LINE_AA)

            # Resaltado si fue recién guardado
            if is_recent:
                sec_ago = int(time.time() - studio.last_saved_time)
                cv2.putText(canvas, f">> RECIEN GUARDADO ({sec_ago}s)", (pill_x - 10, by + 18),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.31, (0, 255, 140), 1, cv2.LINE_AA)

        # Botón Grande de Captura al pie izquierdo
        rec_y = HEIGHT - 92
        studio.record_main_btn_rect = (12, rec_y, LEFT_W - 24, 56)
        cv2.rectangle(canvas, (12, rec_y), (LEFT_W - 12, rec_y + 56), (0, 120, 220), -1)
        cv2.rectangle(canvas, (12, rec_y), (LEFT_W - 12, rec_y + 56), (255, 255, 255), 2)
        cv2.putText(canvas, "[REC] GRABAR GESTO [ESPACIO]", (26, rec_y + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 2, cv2.LINE_AA)

        # -------------------------------------------------------------
        # 2. ÁREA CENTRAL: ESQUELETO EN VIVO (FRONTAL Y SAGITAL)
        # -------------------------------------------------------------
        center_x = LEFT_W + 15
        center_w = WIDTH - LEFT_W - RIGHT_W - 30
        view_y = 100
        view_h = HEIGHT - 200
        half_w = center_w // 2
        mid_x = center_x + half_w

        # ENCABEZADO SUPERIOR
        sel_act = COMBAT_ACTIONS[studio.selected_action_idx]
        cur_pose_cnt = studio.quota_counts.get(sel_act["id"], 0)
        cv2.rectangle(canvas, (center_x, 10), (WIDTH - 15, 90), (28, 34, 46), -1)
        cv2.rectangle(canvas, (center_x, 10), (WIDTH - 15, 90), (0, 200, 255), 2)

        # Línea 1: Gesto activo y Participante
        h_title = f"GESTO ACTIVO: {sel_act['name'].upper()} ({sel_act['sub']})  |  PARTICIPANTE: {prof['name'].upper()} (Sujeto {studio.current_subject_id:02d})"
        cv2.putText(canvas, h_title, (center_x + 16, 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.54, (255, 255, 255), 2, cv2.LINE_AA)

        # Línea 2: ESTADO EXPLÍCITO DE LA POSE SELECCIONADA (Para no dudar jamás)
        if cur_pose_cnt == 0:
            pose_st_txt = f"[-] ESTADO POSE: SIN CLIPS EN DISCO AUN (0/20) - Presiona [ESPACIO] para grabar el primero"
            pose_st_col = (180, 195, 215)
        elif cur_pose_cnt < 20:
            pose_st_txt = f"[SAVE] ESTADO POSE: YA TIENE {cur_pose_cnt} CLIPS EN DISCO ({cur_pose_cnt}/20 OK) - Faltan {20 - cur_pose_cnt} repeticiones"
            pose_st_col = (0, 230, 255)
        else:
            pose_st_txt = f"[OK] ESTADO POSE: CUOTA COMPLETA CON EXITO ({cur_pose_cnt}/20 OK) - Pose lista para ML!"
            pose_st_col = (0, 255, 120)

        cv2.putText(canvas, pose_st_txt, (center_x + 16, 56),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, pose_st_col, 1, cv2.LINE_AA)

        # Línea 3: Modo de ejecución y FPS + ML en vivo
        mode_badge = "MODO: SIMULACIÓN PROCEDURAL (30 FPS)" if studio.is_mock else "MODO: AZURE KINECT FÍSICO (30 FPS)"
        b_col = (0, 200, 255) if studio.is_mock else (0, 255, 120)
        cv2.putText(canvas, f"{mode_badge} | FPS: {display_fps:.1f}", (center_x + 16, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, b_col, 1, cv2.LINE_AA)

        if studio.ml_model is not None:
            ml_tag = f"[ML] PREDICCION: {studio.ml_pred_label.upper()} ({studio.ml_confidence*100:.0f}%)"
            cv2.putText(canvas, ml_tag, (center_x + 350, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 200), 1, cv2.LINE_AA)

        # Captura de frames continuos (35 frames)
        if studio.is_recording and has_body:
            studio.recorded_frames.append(joints_xyz_m.copy())
            if len(studio.recorded_frames) >= studio.target_clip_frames:
                studio.finish_recording()

        # Buffer rodante para inferencia en tiempo real
        if has_body and not studio.is_recording:
            studio.live_buffer.append(joints_xyz_m.copy())
            if studio.ml_model is not None and len(studio.live_buffer) == 35 and (time.time() - studio.last_ml_time) > 0.10:
                try:
                    buf_arr = np.array(studio.live_buffer, dtype=np.float32)
                    feats = extract_clip_features(buf_arr, fps=30.0)
                    feat_vec = np.array([[feats[fn] for fn in FEATURE_NAMES]], dtype=np.float32)

                    # Si muñecas están muy juntas frente al pecho = Bloqueo
                    if feats.get("min_wrist_distance", 1.0) < 0.14:
                        studio.ml_pred_label = "block"
                        studio.ml_confidence = 0.95
                    elif feats["peak_vel_wrist_r"] < 0.9 and feats["peak_vel_wrist_l"] < 0.9 and feats["peak_vel_ankle_r"] < 0.9 and feats["peak_vel_ankle_l"] < 0.9 and feats["peak_vel_pelvis_y"] < 0.7:
                        studio.ml_pred_label = "idle"
                        studio.ml_confidence = 0.98
                    else:
                        probs = studio.ml_model.predict_proba(feat_vec)[0]
                        top_idx = int(np.argmax(probs))
                        studio.ml_pred_label = ACTION_ID_TO_NAME.get(top_idx, "unknown")
                        studio.ml_confidence = float(probs[top_idx])

                    studio.last_ml_time = time.time()
                except Exception:
                    pass

        # Dibujar Esqueleto en Vivo en Área Central
        if has_body:
            pelvis_raw = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
            scale = 230.0
            cy = view_y + (view_h // 2)

            cv2.line(canvas, (mid_x, view_y), (mid_x, view_y + view_h), (45, 52, 65), 1)

            # Vista Frontal
            cx_front = center_x + (half_w // 2)
            f_pts = {}
            for j_n, j_i in SIMPLIFIED_JOINTS.items():
                rx = (joints_xyz_m[j_i, 0] - pelvis_raw[0]) * scale
                ry = (joints_xyz_m[j_i, 1] - pelvis_raw[1]) * scale
                f_pts[j_n] = np.array([cx_front + rx, cy + ry])

            draw_simplified_skeleton(canvas, f_pts)
            cv2.putText(canvas, "VISTA FRONTAL (X-Y)", (cx_front - 75, view_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 255, 200), 1, cv2.LINE_AA)

            # Vista Sagital
            cx_sag = mid_x + (half_w // 2)
            s_pts = {}
            for j_n, j_i in SIMPLIFIED_JOINTS.items():
                rz = (joints_xyz_m[j_i, 2] - pelvis_raw[2]) * scale
                ry = (joints_xyz_m[j_i, 1] - pelvis_raw[1]) * scale
                s_pts[j_n] = np.array([cx_sag + rz, cy + ry])

            draw_simplified_skeleton(canvas, s_pts)
            cv2.putText(canvas, "VISTA SAGITAL (Z-Y)", (cx_sag - 75, view_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (0, 200, 255), 1, cv2.LINE_AA)

        # Barra de progreso mientras se graba
        if studio.is_recording:
            progress = len(studio.recorded_frames) / float(studio.target_clip_frames)
            bw = 440
            bh = 40
            bx = center_x + (center_w - bw) // 2
            by = view_y + view_h - 60

            cv2.rectangle(canvas, (bx, by), (bx + bw, by + bh), (20, 25, 35), -1)
            cv2.rectangle(canvas, (bx, by), (bx + int(bw * progress), by + bh), (0, 40, 220), -1)
            cv2.rectangle(canvas, (bx, by), (bx + bw, by + bh), (255, 255, 255), 2)

            r_txt = f"🔴 GRABANDO: Frame {len(studio.recorded_frames)}/{studio.target_clip_frames} (~30 FPS)"
            cv2.putText(canvas, r_txt, (bx + 25, by + 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2, cv2.LINE_AA)

        # Manejo de Cuenta Regresiva de 3 Segundos
        if studio.is_counting_down:
            elapsed_cd = time.time() - studio.countdown_start_time
            sec_left = max(1, 3 - int(elapsed_cd))

            if sec_left in (3, 2, 1) and sec_left not in studio.countdown_beeps_played:
                studio.countdown_beeps_played.add(sec_left)
                play_audio_tone(850, 110)

            if elapsed_cd >= 3.0:
                studio.is_counting_down = False
                play_audio_tone(1350, 240)
                target_act = studio.countdown_action
                if use_mock:
                    mock_sensor.trigger_action(target_act["id"], duration_frames=35)
                studio.start_recording(target_act)
            else:
                # Dibujar Overlay de Cuenta Regresiva
                target_act = studio.countdown_action
                cd_w, cd_h = 580, 210
                cd_x = center_x + (center_w - cd_w) // 2
                cd_y = view_y + (view_h - cd_h) // 2

                sub_rect = canvas[cd_y:cd_y+cd_h, cd_x:cd_x+cd_w]
                overlay = sub_rect.copy()
                cv2.rectangle(overlay, (0, 0), (cd_w, cd_h), (14, 18, 28), -1)
                cv2.addWeighted(overlay, 0.90, sub_rect, 0.10, 0, sub_rect)
                cv2.rectangle(canvas, (cd_x, cd_y), (cd_x + cd_w, cd_y + cd_h), (0, 220, 255), 2)

                act_txt = f"PREPARATE: {target_act['name'].upper()} ({target_act['sub']})"
                cv2.putText(canvas, act_txt, (cd_x + 28, cd_y + 38),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.60, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(canvas, target_act["desc"], (cd_x + 28, cd_y + 64),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 200, 220), 1, cv2.LINE_AA)

                # Gran número central 3, 2, 1
                num_col = (0, 100, 255) if sec_left == 1 else ((0, 210, 255) if sec_left == 2 else (0, 255, 140))
                cv2.putText(canvas, str(sec_left), (cd_x + (cd_w // 2) - 24, cd_y + 150),
                            cv2.FONT_HERSHEY_SIMPLEX, 2.6, num_col, 5, cv2.LINE_AA)

                cv2.putText(canvas, "¡Lanza el movimiento en el pitido agudo! [ESC] Cancelar", (cd_x + 75, cd_y + 190),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 220), 1, cv2.LINE_AA)

        # Manejo de Calibración A-Pose
        if studio.is_calibrating and has_body:
            studio.calibration_frames.append(joints_xyz_m.copy())
            elapsed_cal = time.time() - studio.calibration_start_time
            if elapsed_cal >= 2.0 or len(studio.calibration_frames) >= 60:
                studio.finish_apose_calibration()
            else:
                cal_w, cal_h = 580, 130
                cal_x = center_x + (center_w - cal_w) // 2
                cal_y = view_y + (view_h - cal_h) // 2

                sub_rect = canvas[cal_y:cal_y+cal_h, cal_x:cal_x+cal_w]
                overlay = sub_rect.copy()
                cv2.rectangle(overlay, (0, 0), (cal_w, cal_h), (18, 28, 40), -1)
                cv2.addWeighted(overlay, 0.90, sub_rect, 0.10, 0, sub_rect)
                cv2.rectangle(canvas, (cal_x, cal_y), (cal_x + cal_w, cal_y + cal_h), (0, 255, 200), 2)

                cv2.putText(canvas, "📐 CALIBRANDO MEDIDAS BIOMÉTRICAS (A-POSE)", (cal_x + 24, cal_y + 34),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 220), 2, cv2.LINE_AA)
                cv2.putText(canvas, "Brazos a 45° del cuerpo, piernas abiertas. Mantente quieto...", (cal_x + 24, cal_y + 64),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

                cal_prog = min(1.0, elapsed_cal / 2.0)
                cv2.rectangle(canvas, (cal_x + 24, cal_y + 85), (cal_x + cal_w - 24, cal_y + 108), (35, 45, 60), -1)
                cv2.rectangle(canvas, (cal_x + 24, cal_y + 85), (cal_x + 24 + int((cal_w - 48) * cal_prog), cal_y + 108), (0, 220, 120), -1)
                cv2.rectangle(canvas, (cal_x + 24, cal_y + 85), (cal_x + cal_w - 24, cal_y + 108), (255, 255, 255), 1)

        # COMPROBANTE PERMANENTE DE ESCRITURA EN DISCO (Área Central Inferior)
        rc_y = view_y + view_h + 8
        rc_h = 50
        if studio.last_saved_info is not None:
            info = studio.last_saved_info
            cv2.rectangle(canvas, (center_x, rc_y), (center_x + center_w, rc_y + rc_h), (18, 42, 28), -1)
            cv2.rectangle(canvas, (center_x, rc_y), (center_x + center_w, rc_y + rc_h), (0, 230, 100), 2)
            cv2.putText(canvas, f"[COMPROBANTE DISCO] {info['time_str']} | {info['action_name'].upper()} ({info['count_now']}/20) | Sujeto {info['subject_id']:02d}: {info['subject_name']}",
                        (center_x + 14, rc_y + 19), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 160), 1, cv2.LINE_AA)
            cv2.putText(canvas, f"Archivo: {info['filename']} ({info['size_kb']:.1f} KB)  ->  ESCRITURA FISICA VERIFICADA EN DISCO [OK]",
                        (center_x + 14, rc_y + 38), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (230, 255, 240), 1, cv2.LINE_AA)
        else:
            cv2.rectangle(canvas, (center_x, rc_y), (center_x + center_w, rc_y + rc_h), (22, 26, 34), -1)
            cv2.rectangle(canvas, (center_x, rc_y), (center_x + center_w, rc_y + rc_h), (48, 58, 72), 1)
            cv2.putText(canvas, "[AUDITORIA DE DISCO] Al presionar [ENTER], aqui aparecera el comprobante de archivo y tamano fisico.",
                        (center_x + 14, rc_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 155, 175), 1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # 3. PANEL DERECHO: MINI-VIDEO REPLAYER PERMANENTE EN BUCLE
        # -------------------------------------------------------------
        rev_x = WIDTH - RIGHT_W - 10
        rev_w = RIGHT_W
        rev_y = 100
        rev_h = HEIGHT - 200

        cv2.rectangle(canvas, (rev_x, rev_y), (rev_x + rev_w, rev_y + rev_h), (18, 22, 30), -1)
        cv2.rectangle(canvas, (rev_x, rev_y), (rev_x + rev_w, rev_y + rev_h), (0, 200, 255), 2)

        cv2.rectangle(canvas, (rev_x, rev_y), (rev_x + rev_w, rev_y + 36), (32, 45, 62), -1)
        cv2.putText(canvas, "MINI-VIDEO PLAYER (AUDITORIA)", (rev_x + 14, rev_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 200), 2, cv2.LINE_AA)

        if studio.has_video and studio.video_frames:
            n_v_frames = len(studio.video_frames)

            # Cálculo de frame para reproducción continua en bucle a 30 FPS
            if not studio.video_paused:
                elapsed = time.time() - studio.video_start_time
                curr_frame_idx = int(elapsed * 30.0) % n_v_frames
                studio.video_paused_frame = curr_frame_idx
            else:
                curr_frame_idx = studio.video_paused_frame % n_v_frames

            v_joints = studio.video_frames[curr_frame_idx]
            pelvis_v = v_joints[SIMPLIFIED_JOINTS["pelvis"]]

            # Centros mini-video
            vr_scale = 145.0
            vr_cy = rev_y + 175
            vr_cx_f = rev_x + (rev_w // 4)
            vr_cx_s = rev_x + 3 * (rev_w // 4)

            cv2.line(canvas, (rev_x + rev_w // 2, rev_y + 45), (rev_x + rev_w // 2, rev_y + 300), (45, 52, 65), 1)

            # Frontal Mini
            rf_pts = {}
            for j_n, j_i in SIMPLIFIED_JOINTS.items():
                rx = (v_joints[j_i, 0] - pelvis_v[0]) * vr_scale
                ry = (v_joints[j_i, 1] - pelvis_v[1]) * vr_scale
                rf_pts[j_n] = np.array([vr_cx_f + rx, vr_cy + ry])
            draw_simplified_skeleton(canvas, rf_pts)
            cv2.putText(canvas, "FRONTAL", (vr_cx_f - 30, rev_y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 200), 1, cv2.LINE_AA)

            # Sagital Mini
            rs_pts = {}
            for j_n, j_i in SIMPLIFIED_JOINTS.items():
                rz = (v_joints[j_i, 2] - pelvis_v[2]) * vr_scale
                ry = (v_joints[j_i, 1] - pelvis_v[1]) * vr_scale
                rs_pts[j_n] = np.array([vr_cx_s + rz, vr_cy + ry])
            draw_simplified_skeleton(canvas, rs_pts)
            cv2.putText(canvas, "PERFIL Z", (vr_cx_s - 30, rev_y + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 200, 255), 1, cv2.LINE_AA)

            # Scrubber timeline interactivo
            sc_y = rev_y + 325
            sc_prog = curr_frame_idx / float(n_v_frames - 1)
            cv2.rectangle(canvas, (rev_x + 16, sc_y), (rev_x + rev_w - 16, sc_y + 10), (35, 40, 52), -1)
            cv2.rectangle(canvas, (rev_x + 16, sc_y), (rev_x + 16 + int((rev_w - 32) * sc_prog), sc_y + 10), (0, 220, 255), -1)

            pause_txt = "[PAUSADO]" if studio.video_paused else "[BUCLE 30 FPS]"
            p_col = (0, 200, 255) if studio.video_paused else (0, 255, 120)
            status_txt = f"Frame {curr_frame_idx + 1:02d}/{n_v_frames:02d}  {pause_txt}  (Duracion: {n_v_frames/30.0:.2f}s)"
            cv2.putText(canvas, status_txt, (rev_x + 16, sc_y + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, p_col, 1, cv2.LINE_AA)

            v_act_name = studio.video_action["name"] if studio.video_action else "Desconocido"
            v_prof_name = studio.video_subject_info.get("name", "") if studio.video_subject_info else ""
            cv2.putText(canvas, f"Clip: {v_act_name} | {v_prof_name}", (rev_x + 16, sc_y + 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)

            # PANEL HEURÍSTICO DE CALIDAD (Quality Gatekeeper)
            if studio.video_quality is not None:
                q = studio.video_quality
                q_y = sc_y + 58
                q_h = 72
                cv2.rectangle(canvas, (rev_x + 14, q_y), (rev_x + rev_w - 14, q_y + q_h), (25, 32, 44), -1)
                cv2.rectangle(canvas, (rev_x + 14, q_y), (rev_x + rev_w - 14, q_y + q_h), q["color"], 2 if q["status"] == "POOR" else 1)

                cv2.putText(canvas, f"AUDITORÍA: {q['title']}", (rev_x + 22, q_y + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, q["color"], 2, cv2.LINE_AA)
                m_str = f"Vel: {q['peak_vel']:.2f} m/s | Frame pico: {q['peak_frame']+1}/35 | Z: {q['dist_z']:.2f}m"
                cv2.putText(canvas, m_str, (rev_x + 22, q_y + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (210, 220, 235), 1, cv2.LINE_AA)
                cv2.putText(canvas, q["advice"], (rev_x + 22, q_y + 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.34, (0, 255, 200) if q["status"] == "GOOD" else (190, 205, 220), 1, cv2.LINE_AA)

            # BOTONES DE DECISIÓN DEL REPRODUCTOR
            # Fila 1: GUARDAR [ENTER] y RE-GRABAR [R]
            b_w = (rev_w - 40) // 2
            b_h = 42
            b1_y = rev_y + rev_h - 100

            studio.save_clip_btn_rect = (rev_x + 16, b1_y, b_w, b_h)
            cv2.rectangle(canvas, (rev_x + 16, b1_y), (rev_x + 16 + b_w, b1_y + b_h), (0, 140, 70), -1)
            cv2.rectangle(canvas, (rev_x + 16, b1_y), (rev_x + 16 + b_w, b1_y + b_h), (255, 255, 255), 2)
            cv2.putText(canvas, "💾 GUARDAR", (rev_x + 24, b1_y + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, "[ENTER]", (rev_x + 36, b1_y + 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (200, 255, 220), 1, cv2.LINE_AA)

            studio.rerecord_btn_rect = (rev_x + 24 + b_w, b1_y, b_w, b_h)
            cv2.rectangle(canvas, (rev_x + 24 + b_w, b1_y), (rev_x + rev_w - 16, b1_y + b_h), (0, 110, 200), -1)
            cv2.rectangle(canvas, (rev_x + 24 + b_w, b1_y), (rev_x + rev_w - 16, b1_y + b_h), (255, 255, 255), 2)
            cv2.putText(canvas, "🔄 RE-GRABAR", (rev_x + 32 + b_w, b1_y + 22),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, "Tecla [R]", (rev_x + 50 + b_w, b1_y + 36),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (200, 230, 255), 1, cv2.LINE_AA)

            # Fila 2: DESCARTAR [DEL] y PAUSAR / REANUDAR [P]
            b2_y = rev_y + rev_h - 50
            studio.discard_btn_rect = (rev_x + 16, b2_y, b_w, 38)
            cv2.rectangle(canvas, (rev_x + 16, b2_y), (rev_x + 16 + b_w, b2_y + 38), (38, 44, 56), -1)
            cv2.rectangle(canvas, (rev_x + 16, b2_y), (rev_x + 16 + b_w, b2_y + 38), (80, 90, 110), 1)
            cv2.putText(canvas, "❌ Descartar [DEL]", (rev_x + 22, b2_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 210, 220), 1, cv2.LINE_AA)

            studio.pause_btn_rect = (rev_x + 24 + b_w, b2_y, b_w, 38)
            cv2.rectangle(canvas, (rev_x + 24 + b_w, b2_y), (rev_x + rev_w - 16, b2_y + 38), (38, 44, 56), -1)
            cv2.rectangle(canvas, (rev_x + 24 + b_w, b2_y), (rev_x + rev_w - 16, b2_y + 38), (80, 90, 110), 1)
            p_btn_label = "▶️ Reanudar [P]" if studio.video_paused else "⏸️ Pausar [P]"
            cv2.putText(canvas, p_btn_label, (rev_x + 32 + b_w, b2_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 210, 220), 1, cv2.LINE_AA)

        else:
            if studio.last_saved_info is not None:
                info = studio.last_saved_info
                # Tarjeta Verde de Último Guardado en Disco
                box_y = rev_y + 55
                box_h = 108
                cv2.rectangle(canvas, (rev_x + 16, box_y), (rev_x + rev_w - 16, box_y + box_h), (20, 52, 32), -1)
                cv2.rectangle(canvas, (rev_x + 16, box_y), (rev_x + rev_w - 16, box_y + box_h), (0, 255, 120), 2)

                cv2.putText(canvas, "[OK] ULTIMO GUARDADO EXITOSO", (rev_x + 28, box_y + 26),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 140), 2, cv2.LINE_AA)
                cv2.putText(canvas, f"Accion: {info['action_name']} ({info['count_now']}/20)", (rev_x + 28, box_y + 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"Archivo: {info['filename']}", (rev_x + 28, box_y + 72),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, (190, 245, 210), 1, cv2.LINE_AA)
                cv2.putText(canvas, f"Verificado en disco ({info['size_kb']:.1f} KB) - {info['time_str']}", (rev_x + 28, box_y + 92),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.34, (140, 220, 160), 1, cv2.LINE_AA)

                guide_y = box_y + box_h + 30
            else:
                cv2.putText(canvas, "Sin video grabado aun.", (rev_x + 40, rev_y + 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.48, (140, 150, 165), 1, cv2.LINE_AA)
                guide_y = rev_y + 150

            cv2.putText(canvas, "INSTRUCCIONES DE CAPTURA:", (rev_x + 24, guide_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 220, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, "1. Selecciona la accion en la izquierda [0..7].", (rev_x + 24, guide_y + 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (200, 210, 220), 1, cv2.LINE_AA)
            cv2.putText(canvas, "2. Presiona [ESPACIO] para cuenta 3.. 2.. 1.", (rev_x + 24, guide_y + 54),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 200), 1, cv2.LINE_AA)
            cv2.putText(canvas, "3. El video de 35 frames se reproducira", (rev_x + 24, guide_y + 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)
            cv2.putText(canvas, "   aqui en bucle las veces que quieras.", (rev_x + 24, guide_y + 102),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1, cv2.LINE_AA)
            cv2.putText(canvas, "4. Revisa calidad: [ENTER] Guardar  |  [R] Re-grabar", (rev_x + 24, guide_y + 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 140), 1, cv2.LINE_AA)

        # BARRA DE ESTADO INFERIOR
        status_bar_y = HEIGHT - 28
        cv2.rectangle(canvas, (0, status_bar_y), (WIDTH, HEIGHT), (16, 18, 24), -1)
        footer_msg = studio.last_msg if studio.last_msg else "SF3 Kinect ML Studio listo | [0..7] Grabar | [R] Re-grabar | [ENTER] Guardar | [Q] Salir"
        cv2.putText(canvas, footer_msg, (16, status_bar_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 160), 1, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, canvas)

        # -------------------------------------------------------------
        # 4. MANEJO DE TECLADO INTERACTIVO
        # -------------------------------------------------------------
        raw_key = cv2.waitKey(1)
        if raw_key == -1:
            continue
        key = raw_key & 0xFF

        # Si el usuario está editando el nombre con el teclado
        if studio.is_editing_name:
            if key in (13, 10):  # ENTER: Confirmar nuevo nombre
                prof = studio.get_current_profile()
                if studio.edit_name_buffer.strip():
                    prof["name"] = studio.edit_name_buffer.strip()
                    save_subject_profiles(studio.profiles)
                studio.is_editing_name = False
                studio.last_msg = f"✅ Nombre actualizado: {prof['name']}"
            elif key in (8, 255):  # BACKSPACE
                studio.edit_name_buffer = studio.edit_name_buffer[:-1]
            elif key == 27:  # ESC: Cancelar edición
                studio.is_editing_name = False
                studio.last_msg = "Edición de nombre cancelada."
            elif 32 <= key <= 126:
                if len(studio.edit_name_buffer) < 20:
                    studio.edit_name_buffer += chr(key)
            continue

        # Teclas de control general
        if key in (ord('q'), 27):  # ESC o Q
            if studio.is_counting_down:
                studio.cancel_countdown()
            else:
                break
        elif key in (ord('c'), ord('C')):  # C: Calibración Biomecánica A-Pose
            studio.trigger_apose_calibration()
        elif key == ord('e'):      # E: Editar nombre del sujeto actual
            studio.is_editing_name = True
            studio.edit_name_buffer = studio.get_current_profile()["name"]
            studio.last_msg = "✏️ Escribe el nuevo nombre y presiona [ENTER] para confirmar."
        elif key == ord('h'):      # H: Incrementar estatura (+2 cm)
            prof = studio.get_current_profile()
            prof["height_cm"] = min(210, prof["height_cm"] + 2)
            save_subject_profiles(studio.profiles)
        elif key == ord('H'):      # Shift+H: Disminuir estatura (-2 cm)
            prof = studio.get_current_profile()
            prof["height_cm"] = max(140, prof["height_cm"] - 2)
            save_subject_profiles(studio.profiles)
        elif key == ord('g'):      # G: Alternar género M / F / O
            prof = studio.get_current_profile()
            g_cycle = {"M": "F", "F": "O", "O": "M"}
            prof["gender"] = g_cycle.get(prof.get("gender", "M"), "M")
            save_subject_profiles(studio.profiles)
        elif key == ord('['):      # Sujeto anterior (1 a 40)
            studio.current_subject_id = max(1, studio.current_subject_id - 1)
            studio.current_set_id = ((studio.current_subject_id - 1) // 10) + 1
            studio.update_quota_counts()
            studio.update_all_subjects_summary()
            studio.last_msg = f"👤 Sujeto cambiado a: Sujeto {studio.current_subject_id:02d} [SET {studio.current_set_id}]"
        elif key == ord(']'):      # Sujeto siguiente (1 a 40)
            studio.current_subject_id = min(40, studio.current_subject_id + 1)
            studio.current_set_id = ((studio.current_subject_id - 1) // 10) + 1
            studio.update_quota_counts()
            studio.update_all_subjects_summary()
            studio.last_msg = f"👤 Sujeto cambiado a: Sujeto {studio.current_subject_id:02d} [SET {studio.current_set_id}]"
        elif key in (ord('{'), ord('(')):  # Set anterior (1 a 4)
            studio.current_set_id = max(1, studio.current_set_id - 1)
            studio.current_subject_id = (studio.current_set_id - 1) * 10 + 1
            studio.update_quota_counts()
            studio.update_all_subjects_summary()
            studio.last_msg = f"📁 Set cambiado a: SET {studio.current_set_id} (Sujetos {(studio.current_set_id - 1)*10 + 1:02d} - {studio.current_set_id*10:02d})"
        elif key in (ord('}'), ord(')')):  # Set siguiente (1 a 4)
            studio.current_set_id = min(4, studio.current_set_id + 1)
            studio.current_subject_id = (studio.current_set_id - 1) * 10 + 1
            studio.update_quota_counts()
            studio.update_all_subjects_summary()
            studio.last_msg = f"📁 Set cambiado a: SET {studio.current_set_id} (Sujetos {(studio.current_set_id - 1)*10 + 1:02d} - {studio.current_set_id*10:02d})"
        elif key in (ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7')):
            act_num = int(chr(key))
            studio.selected_action_idx = act_num
            act_obj = COMBAT_ACTIONS[act_num]
            studio.trigger_countdown(act_obj)
        elif key == ord(' '):      # Espacio: Grabar acción con cuenta regresiva de 3 seg
            act_obj = COMBAT_ACTIONS[studio.selected_action_idx]
            studio.trigger_countdown(act_obj)
        elif key in (ord('r'), ord('R')):  # R: Re-grabar el video con cuenta regresiva
            target_act = studio.video_action if studio.has_video else COMBAT_ACTIONS[studio.selected_action_idx]
            studio.trigger_countdown(target_act)
        elif key in (13, 10):      # Enter: Guardar clip de video
            if studio.has_video:
                studio.confirm_save_video()
        elif key in (8, 255):      # Backspace / Del: Descartar video
            if studio.has_video:
                studio.has_video = False
                studio.video_frames = []
                studio.video_quality = None
                studio.last_msg = "🗑️ Video descartado."
        elif key in (ord('p'), ord('P')):  # P: Pausar / Reanudar video
            if studio.has_video:
                studio.video_paused = not studio.video_paused

    cv2.destroyAllWindows()
    print("👋 SF3 Gesture Studio cerrado.")


if __name__ == "__main__":
    main()
