"""
Street Fighter III: 3rd Strike - Kinect Transition Graph Studio & Dataset Recorder
==================================================================================
Estudio visual interactivo con perspectiva DUAL (Frontal + Sagittal Profile),
telemetría cinemática en vivo, modo práctica previo a la grabación, gestión
dinámica e ilimitada de sujetos (creación de nuevos sujetos en la misma UI)
y seguimiento en tiempo real de la matriz 7x7 de transiciones (42 aristas).
"""

import sys
import os
import time
import json
import argparse
import glob
import collections
import numpy as np
import pandas as pd
import cv2

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        import winsound
        HAS_WINSOUND = True
    except ImportError:
        HAS_WINSOUND = False
else:
    HAS_WINSOUND = False

# Importación condicional de Azure Kinect SDK
pykinect = None
try:
    import pykinect_azure as pykinect
    HAS_PYKINECT = True
except ImportError:
    HAS_PYKINECT = False


# -----------------------------------------------------------------------------
# 1. ARTICULACIONES ESENCIALES Y HUESOS MOTRICES (18 NODOS)
# -----------------------------------------------------------------------------
SIMPLIFIED_JOINTS = {
    "pelvis": 0,
    "pecho": 2,           # SPINE_CHEST
    "cuello": 3,
    "cabeza": 26,
    "hombro_izq": 5,
    "codo_izq": 6,
    "muneca_izq": 7,
    "mano_izq": 8,        # HAND_LEFT
    "hombro_der": 12,
    "codo_der": 13,
    "muneca_der": 14,
    "mano_der": 15,       # HAND_RIGHT
    "cadera_izq": 18,
    "rodilla_izq": 19,
    "tobillo_izq": 20,
    "pie_izq": 21,        # FOOT_LEFT
    "cadera_der": 22,
    "rodilla_der": 23,
    "tobillo_der": 24,
    "pie_der": 25         # FOOT_RIGHT
}

# Huesos anatómicos: BGR OpenCV (Rojo = Derecho, Azul = Izquierdo, Cian = Tronco)
SIMPLIFIED_BONES = [
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
    ("pelvis", "cadera_izq", (255, 140, 0)),
    ("cadera_izq", "rodilla_izq", (255, 90, 0)),
    ("rodilla_izq", "tobillo_izq", (255, 50, 0)),
    ("tobillo_izq", "pie_izq", (255, 20, 0)),
    # Extremidad Inferior Derecha (Rojo)
    ("pelvis", "cadera_der", (0, 80, 255)),
    ("cadera_der", "rodilla_der", (0, 50, 255)),
    ("rodilla_der", "tobillo_der", (0, 30, 255)),
    ("tobillo_der", "pie_der", (0, 10, 255))
]


# -----------------------------------------------------------------------------
# 2. CATÁLOGO DE LAS 7 ACCIONES MAESTRAS Y 42 ARISTAS
# -----------------------------------------------------------------------------
ACTIONS = [
    "idle",           # 0
    "punch_right",    # 1
    "punch_left",     # 2
    "kick_right",     # 3
    "kick_left",      # 4
    "crouch",         # 5
    "block"           # 6
]

ACTION_LABELS = {
    "idle": "Reposo (Idle)",
    "punch_right": "Puño Der (HP)",
    "punch_left": "Puño Izq (LP)",
    "kick_right": "Patada Der (HK)",
    "kick_left": "Patada Izq (LK)",
    "crouch": "Agacharse (Crouch)",
    "block": "Bloqueo (Guard)"
}

ACTION_SHORT = {
    "idle": "IDL",
    "punch_right": "P_R",
    "punch_left": "P_L",
    "kick_right": "K_R",
    "kick_left": "K_L",
    "crouch": "CRO",
    "block": "BLK"
}

ACTION_COLORS = {
    "idle": (100, 220, 100),       # Verde
    "punch_right": (0, 140, 255),  # Naranja
    "punch_left": (255, 160, 40),  # Azul
    "kick_right": (40, 40, 240),   # Rojo
    "kick_left": (220, 80, 200),   # Magenta
    "crouch": (0, 220, 220),       # Amarillo/Cian
    "block": (180, 180, 180)       # Gris
}

ALL_EDGES = [
    (origin, target)
    for origin in ACTIONS
    for target in ACTIONS
    if origin != target
]

DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset_transitions")
PROFILES_FILE = os.path.join(os.path.dirname(__file__), "dataset_raw", "subject_profiles.json")


def play_tone(freq=880, duration_ms=90):
    if HAS_WINSOUND:
        try:
            winsound.Beep(int(freq), int(duration_ms))
        except Exception:
            pass


# -----------------------------------------------------------------------------
# 3. GESTOR DINÁMICO DE PERFILES (CREACIÓN ILIMITADA DE SUJETOS)
# -----------------------------------------------------------------------------
def load_subject_profiles():
    os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
    profiles = {}
    if os.path.exists(PROFILES_FILE):
        try:
            with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                profiles = json.load(f)
        except Exception:
            pass

    # Garantizar al menos los sujetos base si no hay nada
    if not profiles:
        for i in range(1, 15):
            profiles[str(i)] = {
                "id": i,
                "folder": f"subject_{i:02d}",
                "name": f"Participante {i}",
                "height_cm": 174,
                "gender": "M"
            }
        save_subject_profiles(profiles)
    return profiles


def save_subject_profiles(profiles):
    try:
        os.makedirs(os.path.dirname(PROFILES_FILE), exist_ok=True)
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
    except Exception as ex:
        print(f"⚠️ Error guardando perfiles: {ex}")


# -----------------------------------------------------------------------------
# 4. GENERADOR PROCEDURAL MOCK CON CINEMÁTICA CONTINUA DE TRANSICIÓN
# -----------------------------------------------------------------------------
class MockTransitionSensor:
    def __init__(self):
        self.base_skeleton = np.zeros((32, 3), dtype=np.float32)
        self._init_base_pose()
        self.is_playing_transition = False
        self.origin_act = "idle"
        self.target_act = "idle"
        self.current_frame = 0
        self.total_frames = 50

    def _init_base_pose(self):
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

    def trigger_transition(self, origin: str, target: str, duration_frames: int = 50):
        self.origin_act = origin
        self.target_act = target
        self.is_playing_transition = True
        self.current_frame = 0
        self.total_frames = duration_frames

    def _apply_pose_delta(self, frame: np.ndarray, action: str, intensity: float):
        if intensity <= 0.001:
            return

        if action == "punch_right":
            frame[14, 2] -= 620.0 * intensity
            frame[15, 2] -= 700.0 * intensity
            frame[14, 1] -= 220.0 * intensity
            frame[15, 1] -= 220.0 * intensity
        elif action == "punch_left":
            frame[7, 2] -= 620.0 * intensity
            frame[8, 2] -= 700.0 * intensity
            frame[7, 1] -= 220.0 * intensity
            frame[8, 1] -= 220.0 * intensity
        elif action == "kick_right":
            frame[24, 1] -= 650.0 * intensity
            frame[24, 2] -= 480.0 * intensity
            frame[25, 1] -= 700.0 * intensity
            frame[25, 2] -= 550.0 * intensity
            frame[23, 1] -= 400.0 * intensity
        elif action == "kick_left":
            frame[20, 1] -= 650.0 * intensity
            frame[20, 2] -= 480.0 * intensity
            frame[21, 1] -= 700.0 * intensity
            frame[21, 2] -= 550.0 * intensity
            frame[19, 1] -= 400.0 * intensity
        elif action == "crouch":
            frame[:, 1] += 360.0 * intensity
        elif action == "block":
            frame[7, 0] += 120.0 * intensity
            frame[7, 1] -= 240.0 * intensity
            frame[14, 0] -= 120.0 * intensity
            frame[14, 1] -= 240.0 * intensity
        elif action == "idle":
            frame[7, 1] -= 50.0 * intensity
            frame[14, 1] -= 50.0 * intensity

    def get_frame(self) -> np.ndarray:
        frame = self.base_skeleton.copy()
        noise = np.random.normal(0, 1.2, frame.shape)
        frame += noise

        if self.is_playing_transition and self.current_frame < self.total_frames:
            t = self.current_frame
            total = self.total_frames
            int_a = np.sin(np.pi * (t / 25.0)) if t < 25 else 0.0
            if t >= 18:
                prog_b = (t - 18) / float(total - 18)
                int_b = np.sin(np.pi * np.clip(prog_b, 0.0, 1.0))
            else:
                int_b = 0.0

            self._apply_pose_delta(frame, self.origin_act, max(0.0, int_a))
            self._apply_pose_delta(frame, self.target_act, max(0.0, int_b))
            self.current_frame += 1
            if self.current_frame >= self.total_frames:
                self.is_playing_transition = False
        else:
            self._apply_pose_delta(frame, "idle", 0.5)

        return frame


# -----------------------------------------------------------------------------
# 5. GESTOR DE LA MATRIZ 7x7 DE TRANSICIONES
# -----------------------------------------------------------------------------
class TransitionMatrixTracker:
    def __init__(self, dataset_root: str):
        self.dataset_root = dataset_root
        self.counts = {edge: 0 for edge in ALL_EDGES}
        self.subject_counts = {}
        self.scan_dataset()

    def scan_dataset(self, current_subject_folder=None):
        for edge in ALL_EDGES:
            self.counts[edge] = 0

        if not os.path.exists(self.dataset_root):
            return

        pattern = os.path.join(self.dataset_root, "**", "*.csv")
        files = glob.glob(pattern, recursive=True)
        for filepath in files:
            filename = os.path.basename(filepath)
            for (origin, target) in ALL_EDGES:
                tag = f"trans_{origin}_to_{target}"
                if tag in filename:
                    self.counts[(origin, target)] = 1
                    break

        if current_subject_folder:
            self.subject_counts = {edge: 0 for edge in ALL_EDGES}
            s_dir = os.path.join(self.dataset_root, current_subject_folder)
            if os.path.exists(s_dir):
                s_files = glob.glob(os.path.join(s_dir, "*.csv"))
                for filepath in s_files:
                    filename = os.path.basename(filepath)
                    for (origin, target) in ALL_EDGES:
                        tag = f"trans_{origin}_to_{target}"
                        if tag in filename:
                            self.subject_counts[(origin, target)] = 1
                            break

    def get_count(self, origin: str, target: str, subject_only: bool = False) -> int:
        if subject_only:
            return self.subject_counts.get((origin, target), 0)
        return self.counts.get((origin, target), 0)

    def set_recorded(self, origin: str, target: str):
        self.counts[(origin, target)] = 1
        self.subject_counts[(origin, target)] = 1

    def increment(self, origin: str, target: str):
        self.set_recorded(origin, target)


# -----------------------------------------------------------------------------
# 6. ESTUDIO VISUAL Y DE PRÁCTICA CON GESTIÓN DE SUJETOS Y DUAL VIEW
# -----------------------------------------------------------------------------
class TransitionStudio:
    def __init__(self, use_mock: bool = True, subject_id: int = 1, target_reps: int = 1):
        self.use_mock = use_mock
        self.target_reps = target_reps

        self.profiles = load_subject_profiles()
        valid_ids = sorted([int(k) for k in self.profiles.keys() if k.isdigit()])
        self.current_subject_id = subject_id if subject_id in valid_ids else (valid_ids[0] if valid_ids else 1)

        self.matrix_tracker = TransitionMatrixTracker(DATASET_DIR)
        self.update_matrix_for_current_subject()

        # Selección activa de arista (0: idle ➔ 1: punch_right por defecto)
        self.origin_idx = 0
        self.target_idx = 1

        # Sensor
        self.mock_sensor = MockTransitionSensor()
        self.kinect_device = None
        self.body_tracker = None
        if not self.use_mock and HAS_PYKINECT:
            self._init_real_kinect()

        # Estados: "PRACTICE" (Modo Práctica Libre), "COUNTDOWN", "RECORDING", "REVIEW"
        self.state = "PRACTICE"
        self.countdown_start = 0.0
        self.countdown_seconds = 3
        self.recorded_frames = []
        self.clip_duration_frames = 50

        # Review Player en bucle
        self.review_frame_idx = 0
        self.last_review_tick = time.time()
        self.last_saved_file = ""
        self.last_saved_time = 0.0
        self.last_saved_edge = None
        self.flash_until = 0.0

        # Edición de Nombre de Sujeto en pantalla
        self.is_editing_name = False
        self.name_edit_buffer = ""

        # Telemetría de velocidad en vivo
        self.prev_skeleton = None
        self.prev_skel_time = time.time()
        self.wrist_r_speed = 0.0
        self.wrist_l_speed = 0.0
        self.ankle_r_speed = 0.0
        self.ankle_l_speed = 0.0
        self.torso_yaw_deg = 0.0

        # Regiones interactivas de Mouse
        self.rect_prev_subj = (0, 0, 0, 0)
        self.rect_next_subj = (0, 0, 0, 0)
        self.rect_new_subj = (0, 0, 0, 0)
        self.rect_name_box = (0, 0, 0, 0)
        self.rect_h_dec = (0, 0, 0, 0)
        self.rect_h_inc = (0, 0, 0, 0)
        self.rect_gender = (0, 0, 0, 0)
        self.rect_record_btn = (0, 0, 0, 0)
        self.rect_next_edge_btn = (0, 0, 0, 0)
        self.origin_btn_rects = []
        self.target_btn_rects = []
        self.matrix_cell_rects = []

    def _init_real_kinect(self):
        k4a_path = r"C:\Program Files\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
        k4abt_path = r"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll"

        if not os.path.exists(k4a_path):
            k4a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k4a.dll"))
        if not os.path.exists(k4abt_path):
            k4abt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "k4abt.dll"))

        print("=" * 65)
        print(f"🔌 Conectando con hardware Azure Kinect DK...")
        print(f"   k4a: {k4a_path}")
        print(f"   k4abt: {k4abt_path}")
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
            self.kinect_device = pykinect.start_device(config=device_config)
            self.body_tracker = pykinect.start_body_tracker(model_type=pykinect.K4ABT_LITE_MODEL)
            self.use_mock = False
            print("✅ Azure Kinect DK CONECTADO y rastreando a 30 FPS.")
            print("=" * 65)
        except Exception as e:
            print(f"⚠️ No se pudo iniciar Azure Kinect físico ({e}).")
            print("💡 Verifica conexión USB 3.0, alimentación eléctrica y que KinectViewer esté cerrado.")
            print("   -> Activando MODO SIMULADOR MOCK como respaldo.")
            print("=" * 65)
            self.use_mock = True

    def get_current_profile(self):
        return self.profiles.get(str(self.current_subject_id), {
            "id": self.current_subject_id,
            "folder": f"subject_{self.current_subject_id:02d}",
            "name": f"Participante {self.current_subject_id}",
            "height_cm": 174,
            "gender": "M"
        })

    def update_matrix_for_current_subject(self):
        prof = self.get_current_profile()
        self.matrix_tracker.scan_dataset(prof.get("folder"))

    def create_new_subject(self):
        """Crea un nuevo sujeto dinámico con ID incremental ilimitado."""
        existing_ids = [int(k) for k in self.profiles.keys() if k.isdigit()]
        new_id = max(existing_ids, default=0) + 1
        new_str_id = str(new_id)

        self.profiles[new_str_id] = {
            "id": new_id,
            "folder": f"subject_{new_id:02d}",
            "name": f"Participante {new_id}",
            "height_cm": 174,
            "gender": "M"
        }
        save_subject_profiles(self.profiles)
        self.current_subject_id = new_id
        self.update_matrix_for_current_subject()

        # Activar edición inmediata del nombre para comodidad del usuario
        self.is_editing_name = True
        self.name_edit_buffer = ""
        print(f"✨ Creado nuevo sujeto: ID {new_id} ({self.profiles[new_str_id]['folder']}). ¡Escribe su nombre!")
        play_tone(1318, 140)

    def select_prev_subject(self):
        valid_ids = sorted([int(k) for k in self.profiles.keys() if k.isdigit()])
        if not valid_ids:
            return
        idx = valid_ids.index(self.current_subject_id) if self.current_subject_id in valid_ids else 0
        self.current_subject_id = valid_ids[(idx - 1) % len(valid_ids)]
        self.update_matrix_for_current_subject()
        play_tone(700, 50)

    def select_next_subject(self):
        valid_ids = sorted([int(k) for k in self.profiles.keys() if k.isdigit()])
        if not valid_ids:
            return
        idx = valid_ids.index(self.current_subject_id) if self.current_subject_id in valid_ids else 0
        self.current_subject_id = valid_ids[(idx + 1) % len(valid_ids)]
        self.update_matrix_for_current_subject()
        play_tone(850, 50)

    @property
    def current_origin(self) -> str:
        return ACTIONS[self.origin_idx]

    @property
    def current_target(self) -> str:
        return ACTIONS[self.target_idx]

    def set_origin(self, idx: int):
        if 0 <= idx < len(ACTIONS):
            self.origin_idx = idx
            if self.origin_idx == self.target_idx:
                self.target_idx = (self.origin_idx + 1) % len(ACTIONS)

    def set_target(self, idx: int):
        if 0 <= idx < len(ACTIONS) and idx != self.origin_idx:
            self.target_idx = idx

    def next_uncompleted_edge(self):
        for edge in ALL_EDGES:
            if self.matrix_tracker.get_count(edge[0], edge[1], subject_only=True) < self.target_reps:
                self.origin_idx = ACTIONS.index(edge[0])
                self.target_idx = ACTIONS.index(edge[1])
                play_tone(1046, 80)
                return
        play_tone(1318, 200)

    def start_countdown(self):
        if self.state != "PRACTICE":
            return
        self.state = "COUNTDOWN"
        self.countdown_start = time.time()
        play_tone(660, 90)

    def start_recording(self):
        self.state = "RECORDING"
        self.recorded_frames = []
        if self.use_mock:
            self.mock_sensor.trigger_transition(
                self.current_origin, self.current_target, self.clip_duration_frames
            )
        play_tone(880, 150)

    def finish_recording(self):
        self.state = "REVIEW"
        self.review_frame_idx = 0
        play_tone(1174, 180)

    def save_recorded_clip(self):
        if not self.recorded_frames:
            return

        prof = self.get_current_profile()
        sub_folder = prof.get("folder", f"subject_{self.current_subject_id:02d}")
        out_dir = os.path.join(DATASET_DIR, sub_folder)
        os.makedirs(out_dir, exist_ok=True)

        # Regla: Solo 1 grabación por transición. Si se graba de nuevo, reemplaza la anterior.
        edge_tag = f"trans_{self.current_origin}_to_{self.current_target}"
        existing = glob.glob(os.path.join(out_dir, f"*{edge_tag}*.csv"))
        for old_f in existing:
            try:
                os.remove(old_f)
            except Exception as ex:
                print(f"⚠️ Aviso al eliminar clip previo: {ex}")

        filename = f"S{self.current_subject_id:02d}_{edge_tag}.csv"
        filepath = os.path.join(out_dir, filename)

        rows = []
        for f_idx, skeleton in enumerate(self.recorded_frames):
            row = {
                "frame_idx": f_idx,
                "subject_id": sub_folder,
                "subject_name": prof.get("name", "anon"),
                "subject_height_cm": prof.get("height_cm", 174),
                "subject_gender": prof.get("gender", "M"),
                "origin_action": self.current_origin,
                "target_action": self.current_target
            }
            for j in range(32):
                pos_m = skeleton[j] / 1000.0 if np.max(np.abs(skeleton)) > 10.0 else skeleton[j]
                row[f"joint_{j}_x"] = pos_m[0]
                row[f"joint_{j}_y"] = pos_m[1]
                row[f"joint_{j}_z"] = pos_m[2]
            rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
        self.last_saved_file = filename
        self.last_saved_time = time.time()
        self.last_saved_edge = (self.current_origin, self.current_target)
        self.flash_until = time.time() + 0.45  # Flash verde en todo el lienzo

        # Actualizar matriz y sincronizar
        self.matrix_tracker.set_recorded(self.current_origin, self.current_target)
        self.update_matrix_for_current_subject()

        print(f"✅ ¡GUARDADO EXITOSO (REEMPLAZO/NUEVO)!: {filename} ({len(rows)} frames)")
        play_tone(1318, 90)
        play_tone(1760, 150)  # Doble tono de confirmación arcade
        self.state = "PRACTICE"

    def get_current_skeleton(self):
        """
        Retorna (has_body, joints_xyz_mm).
        Extrae las 32 articulaciones 3D usando body.numpy()[:, :3].
        """
        if self.use_mock:
            return True, self.mock_sensor.get_frame()

        if self.kinect_device and self.body_tracker:
            try:
                capture = self.kinect_device.update()
                body_frame = self.body_tracker.update()
                num_bodies = body_frame.get_num_bodies()
                if num_bodies > 0:
                    body = body_frame.get_body(0)
                    # body.numpy()[:, :3] contiene las coordenadas (X, Y, Z) en milímetros
                    joints_raw_mm = body.numpy()[:, :3].astype(np.float32)
                    return True, joints_raw_mm
                else:
                    return False, None
            except Exception as ex:
                return False, None

        return True, self.mock_sensor.get_frame()

    def update_telemetry(self, current_skel: np.ndarray):
        if current_skel is None:
            return
        now = time.time()
        dt = max(0.001, now - self.prev_skel_time)

        if self.prev_skeleton is not None:
            curr_m = current_skel / 1000.0 if np.max(np.abs(current_skel)) > 10.0 else current_skel
            prev_m = self.prev_skeleton / 1000.0 if np.max(np.abs(self.prev_skeleton)) > 10.0 else self.prev_skeleton

            # Muñeca Der (14), Izq (7), Tobillo Der (24), Izq (20)
            self.wrist_r_speed = float(np.linalg.norm(curr_m[14] - prev_m[14]) / dt)
            self.wrist_l_speed = float(np.linalg.norm(curr_m[7] - prev_m[7]) / dt)
            self.ankle_r_speed = float(np.linalg.norm(curr_m[24] - prev_m[24]) / dt)
            self.ankle_l_speed = float(np.linalg.norm(curr_m[20] - prev_m[20]) / dt)

            # Ángulo Yaw del Torso (rotación sagital hombro der vs izq)
            dx = float(curr_m[12, 0] - curr_m[5, 0])
            dz = float(curr_m[12, 2] - curr_m[5, 2])
            self.torso_yaw_deg = float(np.arctan2(dz, dx) * (180.0 / np.pi))

        self.prev_skeleton = current_skel.copy()
        self.prev_skel_time = now

    # -------------------------------------------------------------------------
    # RENDERIZADO VISUAL OPENCV (PERSPECTIVA DUAL: FRONTAL + SAGITAL)
    # -------------------------------------------------------------------------
    def draw_skeleton_dual(self, canvas: np.ndarray, skeleton: np.ndarray, has_body: bool,
                           center_x: int, center_y: int, width: int, height: int, scale: float = 230.0):
        """
        Dibuja el esqueleto de 18 articulaciones simultáneamente en Vista Frontal (X-Y)
        y Vista Sagital de Perfil (Z-Y). Si has_body es False, muestra alerta visual de búsqueda.
        """
        half_w = width // 2
        mid_split_x = center_x + half_w
        cy = center_y + (height // 2)

        # Línea divisoria central
        cv2.line(canvas, (mid_split_x, center_y + 10), (mid_split_x, center_y + height - 10), (50, 58, 70), 1)

        cx_front = center_x + (half_w // 2)
        cx_sag = mid_split_x + (half_w // 2)

        cv2.putText(canvas, "VISTA FRONTAL (X-Y)", (cx_front - 70, center_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 200), 1, cv2.LINE_AA)
        cv2.putText(canvas, "VISTA SAGITAL (Z-Y)", (cx_sag - 70, center_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1, cv2.LINE_AA)

        if not has_body or skeleton is None:
            # Guía visual para colocarse frente a la cámara
            cv2.rectangle(canvas, (center_x + 60, cy - 80), (center_x + width - 60, cy + 80), (25, 30, 45), -1)
            cv2.rectangle(canvas, (center_x + 60, cy - 80), (center_x + width - 60, cy + 80), (0, 180, 255), 2)
            cv2.putText(canvas, "BUSCANDO JUGADOR EN CÁMARA...", (center_x + 110, cy - 20),
                        cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 220, 255), 1, cv2.LINE_AA)
            cv2.putText(canvas, "Colóquese frente al Azure Kinect (distancia: 1.8m a 2.8m)",
                        (center_x + 90, cy + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (200, 220, 240), 1, cv2.LINE_AA)
            cv2.putText(canvas, "Asegúrese de que el cuerpo completo sea visible para el sensor",
                        (center_x + 80, cy + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (150, 170, 190), 1, cv2.LINE_AA)
            return

        skel_m = skeleton / 1000.0 if np.max(np.abs(skeleton)) > 10.0 else skeleton
        pelvis = skel_m[SIMPLIFIED_JOINTS["pelvis"]]

        half_w = width // 2
        mid_split_x = center_x + half_w
        cy = center_y + (height // 2)

        # Línea divisoria central
        cv2.line(canvas, (mid_split_x, center_y + 10), (mid_split_x, center_y + height - 10), (50, 58, 70), 1)

        # 1. Vista Frontal (Izquierda del área central)
        cx_front = center_x + (half_w // 2)
        f_pts = {}
        for j_name, j_idx in SIMPLIFIED_JOINTS.items():
            rx = (skel_m[j_idx, 0] - pelvis[0]) * scale
            ry = (skel_m[j_idx, 1] - pelvis[1]) * scale
            f_pts[j_name] = np.array([cx_front + rx, cy + ry])

        # Huesos Frontal
        for s_n, e_n, col in SIMPLIFIED_BONES:
            if s_n in f_pts and e_n in f_pts:
                p1 = tuple(f_pts[s_n].astype(int))
                p2 = tuple(f_pts[e_n].astype(int))
                cv2.line(canvas, p1, p2, col, 3, cv2.LINE_AA)

        # Articulaciones Frontal
        for j_name, pt in f_pts.items():
            c = tuple(pt.astype(int))
            if "mano_der" in j_name or "pie_der" in j_name:
                cv2.circle(canvas, c, 7, (0, 30, 255), -1, cv2.LINE_AA)
                cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
            elif "mano_izq" in j_name or "pie_izq" in j_name:
                cv2.circle(canvas, c, 7, (255, 50, 0), -1, cv2.LINE_AA)
                cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.circle(canvas, c, 4, (220, 220, 220), -1, cv2.LINE_AA)

        cv2.putText(canvas, "VISTA FRONTAL (X-Y)", (cx_front - 70, center_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 200), 1, cv2.LINE_AA)

        # 2. Vista Sagital / Perfil (Derecha del área central)
        cx_sag = mid_split_x + (half_w // 2)
        s_pts = {}
        for j_name, j_idx in SIMPLIFIED_JOINTS.items():
            rz = (skel_m[j_idx, 2] - pelvis[2]) * scale
            ry = (skel_m[j_idx, 1] - pelvis[1]) * scale
            s_pts[j_name] = np.array([cx_sag + rz, cy + ry])

        # Huesos Sagital
        for s_n, e_n, col in SIMPLIFIED_BONES:
            if s_n in s_pts and e_n in s_pts:
                p1 = tuple(s_pts[s_n].astype(int))
                p2 = tuple(s_pts[e_n].astype(int))
                cv2.line(canvas, p1, p2, col, 3, cv2.LINE_AA)

        # Articulaciones Sagital
        for j_name, pt in s_pts.items():
            c = tuple(pt.astype(int))
            if "mano_der" in j_name or "pie_der" in j_name:
                cv2.circle(canvas, c, 7, (0, 30, 255), -1, cv2.LINE_AA)
                cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
            elif "mano_izq" in j_name or "pie_izq" in j_name:
                cv2.circle(canvas, c, 7, (255, 50, 0), -1, cv2.LINE_AA)
                cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.circle(canvas, c, 4, (220, 220, 220), -1, cv2.LINE_AA)

        cv2.putText(canvas, "VISTA SAGITAL (Z-Y)", (cx_sag - 70, center_y + 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1, cv2.LINE_AA)

    def draw_subject_panel(self, canvas: np.ndarray, top_x: int, top_y: int, width: int):
        """Tarjeta superior de gestión de sujetos con soporte para crear nuevos sujetos."""
        prof = self.get_current_profile()

        cv2.rectangle(canvas, (top_x, top_y), (top_x + width, top_y + 160), (28, 34, 46), -1)
        cv2.rectangle(canvas, (top_x, top_y), (top_x + width, top_y + 160), (0, 200, 255), 1)

        # Línea 1: [<] SUJETO XX [>] y Botón [+ NUEVO]
        btn_y = top_y + 10
        self.rect_prev_subj = (top_x + 10, btn_y, 28, 24)
        cv2.rectangle(canvas, (top_x + 10, btn_y), (top_x + 38, btn_y + 24), (45, 58, 76), -1)
        cv2.rectangle(canvas, (top_x + 10, btn_y), (top_x + 38, btn_y + 24), (0, 200, 255), 1)
        cv2.putText(canvas, "<", (top_x + 17, btn_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        subj_tag = f"S{self.current_subject_id:02d} ({len(self.profiles)} Tot)"
        cv2.rectangle(canvas, (top_x + 42, btn_y), (top_x + 165, btn_y + 24), (36, 46, 62), -1)
        cv2.putText(canvas, subj_tag, (top_x + 48, btn_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 220), 1)

        self.rect_next_subj = (top_x + 169, btn_y, 28, 24)
        cv2.rectangle(canvas, (top_x + 169, btn_y), (top_x + 197, btn_y + 24), (45, 58, 76), -1)
        cv2.rectangle(canvas, (top_x + 169, btn_y), (top_x + 197, btn_y + 24), (0, 200, 255), 1)
        cv2.putText(canvas, ">", (top_x + 177, btn_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # BOTÓN [+ NUEVO SUJETO]
        self.rect_new_subj = (top_x + 205, btn_y, width - 215, 24)
        cv2.rectangle(canvas, (top_x + 205, btn_y), (top_x + width - 10, btn_y + 24), (20, 90, 50), -1)
        cv2.rectangle(canvas, (top_x + 205, btn_y), (top_x + width - 10, btn_y + 24), (0, 255, 120), 1)
        cv2.putText(canvas, "+ NUEVO SUJETO [N]", (top_x + 212, btn_y + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        # Línea 2: Nombre editable
        ny = top_y + 44
        cv2.putText(canvas, "Nombre:", (top_x + 10, ny + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1)
        self.rect_name_box = (top_x + 75, ny, width - 85, 24)
        n_bg = (50, 75, 110) if self.is_editing_name else (22, 26, 34)
        n_bdr = (0, 255, 200) if self.is_editing_name else (55, 65, 80)
        cv2.rectangle(canvas, (top_x + 75, ny), (top_x + width - 10, ny + 24), n_bg, -1)
        cv2.rectangle(canvas, (top_x + 75, ny), (top_x + width - 10, ny + 24), n_bdr, 2 if self.is_editing_name else 1)

        disp_name = (self.name_edit_buffer + "_") if self.is_editing_name else prof.get("name", "anon")
        cv2.putText(canvas, disp_name[:18], (top_x + 82, ny + 17),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

        # Línea 3: Altura y Género
        hy = top_y + 76
        cv2.putText(canvas, "Altura:", (top_x + 10, hy + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1)

        self.rect_h_dec = (top_x + 65, hy, 22, 22)
        cv2.rectangle(canvas, (top_x + 65, hy), (top_x + 87, hy + 22), (40, 50, 65), -1)
        cv2.putText(canvas, "-", (top_x + 72, hy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        h_val = f"{prof.get('height_cm', 174)}cm"
        cv2.rectangle(canvas, (top_x + 91, hy), (top_x + 150, hy + 22), (22, 26, 34), -1)
        cv2.putText(canvas, h_val, (top_x + 96, hy + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 200), 1)

        self.rect_h_inc = (top_x + 154, hy, 22, 22)
        cv2.rectangle(canvas, (top_x + 154, hy), (top_x + 176, hy + 22), (40, 50, 65), -1)
        cv2.putText(canvas, "+", (top_x + 160, hy + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

        cv2.putText(canvas, "Sexo:", (top_x + 190, hy + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 190, 200), 1)
        self.rect_gender = (top_x + 235, hy, 32, 22)
        cv2.rectangle(canvas, (top_x + 235, hy), (top_x + 267, hy + 22), (40, 50, 65), -1)
        cv2.putText(canvas, f"[{prof.get('gender', 'M')}]", (top_x + 238, hy + 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 220, 255), 1)

        # Línea 4: Carpeta y estadísticas del sujeto
        sy = top_y + 108
        s_folder = prof.get("folder", f"subject_{self.current_subject_id:02d}")
        s_clips = sum(self.matrix_tracker.subject_counts.values())
        cv2.putText(canvas, f"Carpeta: dataset_transitions/{s_folder}", (top_x + 10, sy + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.34, (140, 160, 180), 1)
        cv2.putText(canvas, f"Clips de este sujeto: {s_clips} guardados", (top_x + 10, sy + 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 140), 1)

    def draw_action_selectors(self, canvas: np.ndarray, top_x: int, top_y: int, width: int):
        """Selector de Nodo Origen A y Nodo Destino B con botones interactivos y estado permanente."""
        # Contenedor panel izquierdo (altura ampliada para encerrar todos los botones)
        cv2.rectangle(canvas, (top_x, top_y), (top_x + width, top_y + 456), (22, 26, 34), -1)
        cv2.rectangle(canvas, (top_x, top_y), (top_x + width, top_y + 456), (55, 65, 80), 1)

        cv2.putText(canvas, "NODO ORIGEN (A) - Teclas [1 - 7]:", (top_x + 10, top_y + 22),
                    cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 220, 255), 1)

        self.origin_btn_rects.clear()
        btn_h = 24
        for idx, act in enumerate(ACTIONS):
            by = top_y + 32 + idx * (btn_h + 3)
            is_sel = (idx == self.origin_idx)

            # Cuántos destinos desde este origen ya han sido grabados por el sujeto activo
            rec_count = sum(1 for tgt in ACTIONS if tgt != act and self.matrix_tracker.get_count(act, tgt, subject_only=True) > 0)
            is_all_recorded = (rec_count == 6)

            if is_all_recorded:
                # -------------------------------------------------------------
                # ¡VERDE!: Todas las 6 transiciones de este origen están grabadas
                # -------------------------------------------------------------
                if is_sel:
                    bg_col = (20, 120, 52)      # Verde esmeralda vivo seleccionado
                    bdr_col = (0, 255, 140)     # Borde neón fluorescente
                    bdr_thick = 2
                    txt_col = (255, 255, 255)
                else:
                    bg_col = (14, 80, 34)       # Verde permanente completo
                    bdr_col = (0, 200, 80)
                    bdr_thick = 1
                    txt_col = (235, 255, 240)
                orig_badge = "[6/6 OK]"
                badge_col = (0, 255, 120)

            else:
                # -------------------------------------------------------------
                # ¡GRIS!: Incompleto (falta al menos una arista por grabar)
                # -------------------------------------------------------------
                if is_sel:
                    bg_col = (50, 54, 64)       # Gris medio seleccionado
                    bdr_col = (190, 200, 215)   # Borde gris claro seleccionado
                    bdr_thick = 2
                    txt_col = (255, 255, 255)
                    badge_col = (190, 200, 215)
                else:
                    bg_col = (28, 30, 36)       # Gris neutral
                    bdr_col = (48, 52, 60)      # Borde gris tenue
                    bdr_thick = 1
                    txt_col = (140, 145, 155)
                    badge_col = (90, 95, 105)
                orig_badge = f"[{rec_count}/6]"

            rect = (top_x + 10, by, width - 20, btn_h)
            self.origin_btn_rects.append((rect, idx))

            cv2.rectangle(canvas, (top_x + 10, by), (top_x + width - 10, by + btn_h), bg_col, -1)
            cv2.rectangle(canvas, (top_x + 10, by), (top_x + width - 10, by + btn_h), bdr_col, bdr_thick)
            txt = f"[{idx + 1}] {ACTION_LABELS[act]}"
            cv2.putText(canvas, txt, (top_x + 18, by + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, txt_col, 1, cv2.LINE_AA)

            (b_w, _), _ = cv2.getTextSize(orig_badge, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)
            cv2.putText(canvas, orig_badge, (top_x + width - 16 - b_w, by + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, badge_col, 1, cv2.LINE_AA)

        # Flecha divisoria de transición
        arrow_y = top_y + 228
        cv2.putText(canvas, "============ TRANSICION A ➔ B ============", (top_x + 15, arrow_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 255), 1)

        cv2.putText(canvas, "NODO DESTINO (B) - Teclas [Q, W, E, R, T, Y, U]:", (top_x + 10, arrow_y + 22),
                    cv2.FONT_HERSHEY_DUPLEX, 0.42, (0, 220, 255), 1)

        self.target_btn_rects.clear()
        dest_keys = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U']
        for idx, act in enumerate(ACTIONS):
            by = arrow_y + 32 + idx * (btn_h + 3)
            is_sel = (idx == self.target_idx)
            is_disabled = (idx == self.origin_idx)

            cnt_subj = self.matrix_tracker.get_count(self.current_origin, act, subject_only=True)
            is_recorded = (cnt_subj > 0)
            is_just_saved = (self.last_saved_edge == (self.current_origin, act)) and ((time.time() - self.last_saved_time) < 8.0)

            if is_disabled:
                # Nodo deshabilitado (no se puede transicionar al mismo nodo)
                bg_col = (20, 20, 24)
                bdr_col = (35, 38, 45)
                bdr_thick = 1
                txt_col = (65, 70, 80)
                badge_txt = "- Mismo -"
                badge_col = (65, 70, 80)

            elif is_recorded:
                # -------------------------------------------------------------
                # ¡VERDE!: Ya está grabado para este sujeto
                # -------------------------------------------------------------
                if is_sel:
                    bg_col = (20, 130, 52)      # Verde esmeralda vivo seleccionado
                    bdr_col = (0, 255, 140)     # Borde neón fluorescente grueso
                    bdr_thick = 2
                    txt_col = (255, 255, 255)
                    badge_txt = "[✓ OK]"
                    badge_col = (0, 255, 220)
                else:
                    bg_col = (14, 85, 35)       # Verde bosque permanente
                    bdr_col = (0, 210, 85)      # Borde verde permanente visible
                    bdr_thick = 1
                    txt_col = (235, 255, 240)
                    badge_txt = "[✓ OK]"
                    badge_col = (0, 255, 120)

                if is_just_saved:
                    bdr_col = (0, 255, 255)
                    bdr_thick = 2
                    badge_txt = "[✓ GUARDADO!]"
                    badge_col = (0, 255, 255)

            else:
                # -------------------------------------------------------------
                # ¡GRIS!: NO está grabado todavía (pendiente)
                # -------------------------------------------------------------
                if is_sel:
                    bg_col = (50, 54, 64)       # Gris medio seleccionado
                    bdr_col = (190, 200, 215)   # Borde gris claro seleccionado
                    bdr_thick = 2
                    txt_col = (255, 255, 255)
                    badge_txt = "[PENDIENTE]"
                    badge_col = (190, 200, 215)
                else:
                    bg_col = (28, 30, 36)       # Gris oscuro neutral
                    bdr_col = (48, 52, 60)      # Borde gris tenue
                    bdr_thick = 1
                    txt_col = (140, 145, 155)   # Texto gris apagado
                    badge_txt = "[PENDIENTE]"
                    badge_col = (90, 95, 105)

            rect = (top_x + 10, by, width - 20, btn_h)
            self.target_btn_rects.append((rect, idx))

            cv2.rectangle(canvas, (top_x + 10, by), (top_x + width - 10, by + btn_h), bg_col, -1)
            cv2.rectangle(canvas, (top_x + 10, by), (top_x + width - 10, by + btn_h), bdr_col, bdr_thick)
            txt = f"[{dest_keys[idx]}] {ACTION_LABELS[act]}"
            cv2.putText(canvas, txt, (top_x + 18, by + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.38, txt_col, 1, cv2.LINE_AA)

            # Badge de estado de destino a la derecha del botón
            (b_w, _), _ = cv2.getTextSize(badge_txt, cv2.FONT_HERSHEY_SIMPLEX, 0.34, 1)
            cv2.putText(canvas, badge_txt, (top_x + width - 16 - b_w, by + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, badge_col, 1, cv2.LINE_AA)

        # Botón Tab Siguiente Arista Incompleta
        tab_y = top_y + 462
        self.rect_next_edge_btn = (top_x + 10, tab_y, width - 20, 30)
        cv2.rectangle(canvas, (top_x + 10, tab_y), (top_x + width - 10, tab_y + 30), (30, 45, 65), -1)
        cv2.rectangle(canvas, (top_x + 10, tab_y), (top_x + width - 10, tab_y + 30), (0, 200, 255), 1)
        cv2.putText(canvas, ">> PROXIMA ARISTA INCOMPLETA [TAB]", (top_x + 22, tab_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 220), 1, cv2.LINE_AA)

    def draw_matrix_panel(self, canvas: np.ndarray, top_x: int, top_y: int, width: int):
        """Matriz 7x7 de las 42 aristas dirigidas."""
        cv2.putText(canvas, "MATRIZ DE CONTINUIDAD 7x7 (42 ARISTAS):", (top_x, top_y - 12),
                    cv2.FONT_HERSHEY_DUPLEX, 0.44, (0, 220, 255), 1)

        cell_w, cell_h = 44, 22
        self.matrix_cell_rects.clear()

        # Encabezados Columnas (Destino)
        for col_idx, act_target in enumerate(ACTIONS):
            cx = top_x + 55 + col_idx * cell_w
            cv2.putText(canvas, ACTION_SHORT[act_target], (cx + 8, top_y + 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.34, (180, 180, 180), 1)

        for row_idx, act_origin in enumerate(ACTIONS):
            ry = top_y + 22 + row_idx * cell_h
            cv2.putText(canvas, ACTION_SHORT[act_origin], (top_x + 2, ry + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, (180, 180, 180), 1)

            for col_idx, act_target in enumerate(ACTIONS):
                rx = top_x + 50 + col_idx * cell_w
                is_selected = (row_idx == self.origin_idx and col_idx == self.target_idx)

                if row_idx == col_idx:
                    cv2.rectangle(canvas, (rx, ry), (rx + cell_w - 3, ry + cell_h - 3), (30, 30, 30), -1)
                    cv2.putText(canvas, "-", (rx + 16, ry + 13), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (60, 60, 60), 1)
                else:
                    cnt_subj = self.matrix_tracker.get_count(act_origin, act_target, subject_only=True)
                    cnt_tot = self.matrix_tracker.get_count(act_origin, act_target, subject_only=False)

                    is_just_saved = (self.last_saved_edge == (act_origin, act_target)) and ((time.time() - self.last_saved_time) < 8.0)

                    if is_just_saved:
                        bg_col = (10, 120, 45)      # Verde neón brillante recién guardado
                        border_col = (0, 255, 255)  # Resplandor cian
                        thick = 2
                        txt = "OK!"
                        txt_col = (255, 255, 255)
                    elif cnt_subj > 0:
                        bg_col = (14, 85, 35)       # VERDE: grabado
                        border_col = (0, 255, 140) if is_selected else (0, 180, 80)
                        thick = 2 if is_selected else 1
                        txt = "OK"
                        txt_col = (0, 255, 120)
                    else:
                        bg_col = (26, 28, 34)       # GRIS: no grabado
                        border_col = (190, 200, 215) if is_selected else (45, 48, 55)
                        thick = 2 if is_selected else 1
                        txt = "-"
                        txt_col = (85, 90, 100)

                    cell_rect = (rx, ry, cell_w - 3, cell_h - 3)
                    self.matrix_cell_rects.append((cell_rect, row_idx, col_idx))

                    cv2.rectangle(canvas, (rx, ry), (rx + cell_w - 3, ry + cell_h - 3), bg_col, -1)
                    cv2.rectangle(canvas, (rx, ry), (rx + cell_w - 3, ry + cell_h - 3), border_col, thick)
                    txt_x = rx + 12 if txt in ["OK", "OK!"] else rx + 16
                    cv2.putText(canvas, txt, (txt_x, ry + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.33, txt_col, 1)

        # Resumen Global
        tot_clips = sum(self.matrix_tracker.counts.values())
        cv2.putText(canvas, f"Total clips en dataset (Todos los sujetos): {tot_clips}", (top_x, top_y + 195),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (180, 200, 220), 1)

        if self.last_saved_file:
            sec_ago = int(time.time() - self.last_saved_time)
            save_txt = f">> RECIÉN GUARDADO ({sec_ago}s): {self.last_saved_file[:24]}..."
            cv2.putText(canvas, save_txt, (top_x, top_y + 220),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.36, (0, 255, 140), 1)

    def render(self):
        WIDTH = 1420
        HEIGHT = 860
        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

        # Si acaba de guardarse (< 0.45s), generar un flash verde en todo el lienzo
        if time.time() < self.flash_until:
            canvas[:] = (20, 65, 32)
        else:
            canvas[:] = (20, 22, 28)

        # Obtener esqueleto en vivo (has_body, skel)
        has_body, skel = self.get_current_skeleton()
        if has_body and skel is not None:
            self.update_telemetry(skel)

        # 1. Cabecera Arcade Superior con Diagnóstico de Hardware
        cv2.rectangle(canvas, (0, 0), (WIDTH, 56), (30, 22, 18), -1)
        cv2.line(canvas, (0, 56), (WIDTH, 56), (0, 160, 255), 2)
        cv2.putText(canvas, "KINET STRIKE - TRANSITION STUDIO & PRACTICE", (20, 36),
                    cv2.FONT_HERSHEY_DUPLEX, 0.72, (0, 220, 255), 1, cv2.LINE_AA)

        if self.use_mock:
            sensor_tag = "SIMULADOR PROCEDURAL (--mock)"
            sensor_col = (0, 200, 255)
        elif has_body:
            sensor_tag = "AZURE KINECT: RASTREANDO CUERPO (ONLINE)"
            sensor_col = (0, 255, 100)
        else:
            sensor_tag = "AZURE KINECT: BUSCANDO JUGADOR..."
            sensor_col = (0, 160, 255)

        cv2.putText(canvas, f"[{sensor_tag}]", (WIDTH - 420, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.44, sensor_col, 1)

        # 2. Panel Izquierdo: Gestión de Sujetos y Selectores de Acción
        LEFT_W = 340
        self.draw_subject_panel(canvas, top_x=15, top_y=68, width=LEFT_W)
        self.draw_action_selectors(canvas, top_x=15, top_y=240, width=LEFT_W)

        # Botón Grande de Captura al pie izquierdo
        rec_y = HEIGHT - 80
        self.rect_record_btn = (15, rec_y, LEFT_W, 60)
        cv2.rectangle(canvas, (15, rec_y), (15 + LEFT_W, rec_y + 60), (0, 110, 220), -1)
        cv2.rectangle(canvas, (15, rec_y), (15 + LEFT_W, rec_y + 60), (255, 255, 255), 2)
        cv2.putText(canvas, "🔴 GRABAR COMBO [ESPACIO]", (28, rec_y + 38),
                    cv2.FONT_HERSHEY_DUPLEX, 0.56, (255, 255, 255), 2, cv2.LINE_AA)

        # 3. Área Central: Visor Dual Frontal + Sagital (Modo Práctica / Countdown / Recording / Review)
        CENTER_X = LEFT_W + 30
        CENTER_W = 660
        VIEW_Y = 68
        VIEW_H = 590

        # Marco del visor central: Borde verde fluorescente si se acaba de guardar un clip
        is_recent_save = (time.time() - self.last_saved_time) < 8.0
        center_bdr_col = (0, 255, 120) if is_recent_save else (50, 58, 70)
        center_bdr_thick = 3 if is_recent_save else 1

        cv2.rectangle(canvas, (CENTER_X, VIEW_Y), (CENTER_X + CENTER_W, VIEW_Y + VIEW_H), (15, 16, 20), -1)
        cv2.rectangle(canvas, (CENTER_X, VIEW_Y), (CENTER_X + CENTER_W, VIEW_Y + VIEW_H), center_bdr_col, center_bdr_thick)

        orig_lbl = ACTION_LABELS.get(self.current_origin, self.current_origin)
        targ_lbl = ACTION_LABELS.get(self.current_target, self.current_target)

        # Banner superior: Gran cartel verde brillante tras guardar, o título de la transición activa
        banner_y = VIEW_Y + 10
        if is_recent_save:
            sec_ago = int(time.time() - self.last_saved_time)
            cv2.rectangle(canvas, (CENTER_X + 10, banner_y), (CENTER_X + CENTER_W - 10, banner_y + 36), (15, 80, 35), -1)
            cv2.rectangle(canvas, (CENTER_X + 10, banner_y), (CENTER_X + CENTER_W - 10, banner_y + 36), (0, 255, 120), 2)
            cv2.putText(canvas, f"✅ ¡GUARDADO CON ÉXITO! ({self.last_saved_file}) [hace {sec_ago}s]",
                        (CENTER_X + 22, banner_y + 24), cv2.FONT_HERSHEY_DUPLEX, 0.46, (0, 255, 180), 1, cv2.LINE_AA)
        else:
            cv2.putText(canvas, f"TRANSICION ACTIVA: [ {orig_lbl} ]  ===>>  [ {targ_lbl} ]",
                        (CENTER_X + 20, banner_y + 18), cv2.FONT_HERSHEY_DUPLEX, 0.54, (0, 255, 255), 1, cv2.LINE_AA)

        # Estados de Visualización
        if self.state == "PRACTICE":
            self.draw_skeleton_dual(canvas, skel, has_body, CENTER_X, VIEW_Y + 40, CENTER_W, VIEW_H - 100, scale=230.0)

            if has_body:
                cv2.putText(canvas, "🥊 MODO PRÁCTICA LIBRE: Prueba la transición antes de grabar",
                            (CENTER_X + 65, VIEW_Y + VIEW_H - 35), cv2.FONT_HERSHEY_DUPLEX, 0.48, (0, 255, 180), 1)
                cv2.putText(canvas, "Presiona [ESPACIO] cuando estés listo para grabar el clip de 50 frames",
                            (CENTER_X + 85, VIEW_Y + VIEW_H - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 190, 200), 1)
            else:
                cv2.putText(canvas, "⚠️ Buscando usuario: Colóquese a 1.8m - 2.8m frente al sensor",
                            (CENTER_X + 95, VIEW_Y + VIEW_H - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 180, 255), 1)

        elif self.state == "COUNTDOWN":
            elapsed = time.time() - self.countdown_start
            rem = int(self.countdown_seconds - elapsed) + 1
            self.draw_skeleton_dual(canvas, skel, has_body, CENTER_X, VIEW_Y + 40, CENTER_W, VIEW_H - 100, scale=230.0)

            cv2.putText(canvas, f"PREPARATE EN 3.. 2.. 1.. : {rem}", (CENTER_X + 160, VIEW_Y + 70),
                        cv2.FONT_HERSHEY_DUPLEX, 0.85, (0, 255, 255), 2)
            cv2.putText(canvas, f"¡Ejecuta {orig_lbl} y conecta de inmediato {targ_lbl}!",
                        (CENTER_X + 80, VIEW_Y + VIEW_H - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)

            if elapsed >= self.countdown_seconds:
                self.start_recording()

        elif self.state == "RECORDING":
            if has_body and skel is not None:
                self.recorded_frames.append(skel.copy())
            self.draw_skeleton_dual(canvas, skel, has_body, CENTER_X, VIEW_Y + 40, CENTER_W, VIEW_H - 100, scale=230.0)

            prog = len(self.recorded_frames) / float(self.clip_duration_frames)
            cv2.putText(canvas, f"🔴 GRABANDO: Frame {len(self.recorded_frames)}/{self.clip_duration_frames}",
                        (CENTER_X + 160, VIEW_Y + 70), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 40, 255), 2)

            # Barra de progreso roja
            cv2.rectangle(canvas, (CENTER_X + 40, VIEW_Y + VIEW_H - 45),
                          (CENTER_X + CENTER_W - 40, VIEW_Y + VIEW_H - 20), (30, 30, 40), -1)
            cv2.rectangle(canvas, (CENTER_X + 40, VIEW_Y + VIEW_H - 45),
                          (CENTER_X + 40 + int((CENTER_W - 80) * prog), VIEW_Y + VIEW_H - 20), (0, 50, 255), -1)
            cv2.rectangle(canvas, (CENTER_X + 40, VIEW_Y + VIEW_H - 45),
                          (CENTER_X + CENTER_W - 40, VIEW_Y + VIEW_H - 20), (255, 255, 255), 2)

            if len(self.recorded_frames) >= self.clip_duration_frames:
                self.finish_recording()

        elif self.state == "REVIEW":
            if self.recorded_frames:
                now = time.time()
                if now - self.last_review_tick > 0.033:
                    self.review_frame_idx = (self.review_frame_idx + 1) % len(self.recorded_frames)
                    self.last_review_tick = now

                rev_skel = self.recorded_frames[self.review_frame_idx]
                self.draw_skeleton_dual(canvas, rev_skel, True, CENTER_X, VIEW_Y + 40, CENTER_W, VIEW_H - 100, scale=230.0)

                cv2.putText(canvas, f"REPLAY EN BUCLE: Frame {self.review_frame_idx + 1}/{len(self.recorded_frames)}",
                            (CENTER_X + 160, VIEW_Y + 70), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 220, 255), 1)
                cv2.putText(canvas, "[ENTER / S] Guardar Clip  |  [R] Reintentar  |  [ESC] Descartar",
                            (CENTER_X + 70, VIEW_Y + VIEW_H - 25), cv2.FONT_HERSHEY_DUPLEX, 0.54, (0, 255, 120), 1)

        # Panel Inferior de Telemetría (Área Central Abajo)
        telem_y = VIEW_Y + VIEW_H + 15
        telem_h = HEIGHT - telem_y - 20
        cv2.rectangle(canvas, (CENTER_X, telem_y), (CENTER_X + CENTER_W, telem_y + telem_h), (25, 30, 40), -1)
        cv2.rectangle(canvas, (CENTER_X, telem_y), (CENTER_X + CENTER_W, telem_y + telem_h), (50, 60, 75), 1)

        cv2.putText(canvas, "TELEMETRÍA CINEMÁTICA EN VIVO:", (CENTER_X + 15, telem_y + 22),
                    cv2.FONT_HERSHEY_DUPLEX, 0.44, (0, 220, 255), 1)

        if has_body and skel is not None:
            skel_m = skel / 1000.0 if np.max(np.abs(skel)) > 10.0 else skel
            z_pelvis = skel_m[0, 2]
            z_status = "ÓPTIMO" if (1.7 <= z_pelvis <= 3.2) else ("MUY CERCA" if z_pelvis < 1.7 else "MUY LEJOS")
            t_l1 = f"Vel. Muñeca Der: {self.wrist_r_speed:.2f} m/s  |  Izq: {self.wrist_l_speed:.2f} m/s  |  Yaw Torso: {self.torso_yaw_deg:.1f}°"
            t_l2 = f"Vel. Tobillo Der: {self.ankle_r_speed:.2f} m/s  |  Izq: {self.ankle_l_speed:.2f} m/s  |  Distancia Z: {z_pelvis:.2f}m ({z_status})"
        else:
            t_l1 = "Vel. Muñeca Der: 0.00 m/s  |  Izq: 0.00 m/s  |  Yaw Torso: 0.0°"
            t_l2 = "Sensor esperando detección de articulaciones (Póngase frente al Azure Kinect DK)"

        cv2.putText(canvas, t_l1, (CENTER_X + 15, telem_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        cv2.putText(canvas, t_l2, (CENTER_X + 15, telem_y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 220, 200), 1)
        cv2.putText(canvas, t_l1, (CENTER_X + 15, telem_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
        cv2.putText(canvas, t_l2, (CENTER_X + 15, telem_y + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 220, 200), 1)

        # 4. Panel Derecho: Matriz 7x7 de Transiciones y Progreso
        RIGHT_X = CENTER_X + CENTER_W + 20
        RIGHT_W = WIDTH - RIGHT_X - 15
        self.draw_matrix_panel(canvas, top_x=RIGHT_X, top_y=100, width=RIGHT_W)

        # 5. Barra Inferior de Ayuda
        cv2.rectangle(canvas, (0, HEIGHT - 22), (WIDTH, HEIGHT), (15, 12, 12), -1)
        help_txt = "ATAJOS: [1-7] Origen A | [Q-U] Destino B | [TAB] Sig. Pendiente | [N] Nuevo Sujeto | [E] Editar Nombre | [ESPACIO] Grabar | [ESC] Salir"
        cv2.putText(canvas, help_txt, (20, HEIGHT - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1)

        return canvas

    def handle_mouse_click(self, x: int, y: int):
        # 1. Sujeto: Anterior / Siguiente
        px, py, pw, ph = self.rect_prev_subj
        if px <= x <= px + pw and py <= y <= py + ph:
            self.select_prev_subject()
            return

        nx, ny, nw, nh = self.rect_next_subj
        if nx <= x <= nx + nw and ny <= y <= ny + nh:
            self.select_next_subject()
            return

        # 2. Sujeto: Nuevo
        new_x, new_y, new_w, new_h = self.rect_new_subj
        if new_x <= x <= new_x + new_w and new_y <= y <= new_y + new_h:
            self.create_new_subject()
            return

        # 3. Sujeto: Editar Nombre
        bx, by, bw, bh = self.rect_name_box
        if bx <= x <= bx + bw and by <= y <= by + bh:
            self.is_editing_name = True
            prof = self.get_current_profile()
            self.name_edit_buffer = prof.get("name", "")
            return

        # 4. Sujeto: Altura +/-
        dx, dy, dw, dh = self.rect_h_dec
        if dx <= x <= dx + dw and dy <= y <= dy + dh:
            prof = self.get_current_profile()
            prof["height_cm"] = max(140, prof.get("height_cm", 174) - 2)
            save_subject_profiles(self.profiles)
            return

        ix, iy, iw, ih = self.rect_h_inc
        if ix <= x <= ix + iw and iy <= y <= iy + ih:
            prof = self.get_current_profile()
            prof["height_cm"] = min(210, prof.get("height_cm", 174) + 2)
            save_subject_profiles(self.profiles)
            return

        # 5. Sujeto: Sexo
        gx, gy, gw, gh = self.rect_gender
        if gx <= x <= gx + gw and gy <= y <= gy + gh:
            prof = self.get_current_profile()
            cycle = {"M": "F", "F": "O", "O": "M"}
            prof["gender"] = cycle.get(prof.get("gender", "M"), "M")
            save_subject_profiles(self.profiles)
            return

        # 6. Selección de Origen A
        for rect, idx in self.origin_btn_rects:
            rx, ry, rw, rh = rect
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.set_origin(idx)
                play_tone(700, 30)
                return

        # 7. Selección de Destino B
        for rect, idx in self.target_btn_rects:
            rx, ry, rw, rh = rect
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.set_target(idx)
                play_tone(850, 30)
                return

        # 8. Clic en celdas de la Matriz 7x7
        for rect, r_idx, c_idx in self.matrix_cell_rects:
            rx, ry, rw, rh = rect
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                self.set_origin(r_idx)
                self.set_target(c_idx)
                play_tone(900, 40)
                return

        # 9. Botón Siguiente Pendiente
        tx, ty, tw, th = self.rect_next_edge_btn
        if tx <= x <= tx + tw and ty <= y <= ty + th:
            self.next_uncompleted_edge()
            return

        # 10. Botón Grabar Combo
        rx, ry, rw, rh = self.rect_record_btn
        if rx <= x <= rx + rw and ry <= y <= ry + rh:
            if self.state == "PRACTICE":
                self.start_countdown()
            return

    def handle_key(self, key: int) -> bool:
        if key == 27:  # ESC
            if self.is_editing_name:
                self.is_editing_name = False
                return True
            if self.state == "REVIEW":
                self.state = "PRACTICE"
                return True
            return False

        # Modo de edición de nombre
        if self.is_editing_name:
            if key == 13:  # ENTER
                prof = self.get_current_profile()
                if self.name_edit_buffer.strip():
                    prof["name"] = self.name_edit_buffer.strip()
                    save_subject_profiles(self.profiles)
                self.is_editing_name = False
                play_tone(1000, 60)
            elif key == 8:  # BACKSPACE
                self.name_edit_buffer = self.name_edit_buffer[:-1]
            elif 32 <= key <= 126:
                if len(self.name_edit_buffer) < 22:
                    self.name_edit_buffer += chr(key)
            return True

        # Controles prioritarios durante el modo de REVISIÓN (REVIEW)
        if self.state == "REVIEW":
            if key in [13, ord('s'), ord('S')]:  # Guardar clip
                self.save_recorded_clip()
                return True
            if key in [ord('r'), ord('R')]:      # Reintentar de inmediato
                self.state = "PRACTICE"
                self.start_countdown()
                return True
            if key == 27:                        # Descartar y volver a práctica
                self.state = "PRACTICE"
                return True

        # Crear nuevo sujeto con 'N' o '+'
        if key in [ord('n'), ord('N'), ord('+')]:
            self.create_new_subject()
            return True

        # Editar nombre del sujeto activo con 'E'
        if key in [ord('e'), ord('E')]:
            self.is_editing_name = True
            prof = self.get_current_profile()
            self.name_edit_buffer = prof.get("name", "")
            return True

        # Navegar sujetos con '[' y ']'
        if key == ord('['):
            self.select_prev_subject()
            return True
        if key == ord(']'):
            self.select_next_subject()
            return True

        # Selección de Origen A: Teclas 1 a 7
        if ord('1') <= key <= ord('7'):
            idx = key - ord('1')
            self.set_origin(idx)
            play_tone(700, 30)
            return True

        # Selección de Destino B: Teclas Q, W, E, R, T, Y, U
        dest_keys = [ord('q'), ord('w'), ord('e'), ord('r'), ord('t'), ord('y'), ord('u')]
        if key in dest_keys:
            target_idx = dest_keys.index(key)
            self.set_target(target_idx)
            play_tone(850, 30)
            return True

        # Siguiente arista incompleta con TAB
        if key == 9:  # TAB
            self.next_uncompleted_edge()
            return True

        # Iniciar Grabación con Barra Espaciadora
        if key == 32:  # SPACE
            if self.state == "PRACTICE":
                self.start_countdown()
            return True

        # Alternar Mock / Kinect con 'M'
        if key in [ord('m'), ord('M')]:
            self.use_mock = not self.use_mock
            print(f"🔄 Modo sensor cambiado: use_mock = {self.use_mock}")
            return True

        return True

    def run(self):
        WINDOW_NAME = "SF3 Kinect Transition Studio & Practice (Dual View)"
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)

        def on_mouse(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                self.handle_mouse_click(x, y)

        cv2.setMouseCallback(WINDOW_NAME, on_mouse)

        print("=" * 80)
        print("🥋 SF3 - KINECT TRANSITION STUDIO (DUAL VIEW + PRÁCTICA + SUJETOS ILIMITADOS)")
        print("=" * 80)
        print("✨ Práctica libre: Prueba la transición en tiempo real con las vistas Frontal y Sagital.")
        print("✨ Nuevo Sujeto: Presiona [N] o haz clic en '+ NUEVO SUJETO' para crear tantos como necesites.")
        print("✨ Grabar: Presiona [ESPACIO] para cuenta 3.. 2.. 1.. y grabar el clip de 50 frames.")
        print("=" * 80)

        while True:
            canvas = self.render()
            cv2.imshow(WINDOW_NAME, canvas)

            key = cv2.waitKey(15) & 0xFF
            if key != 255:
                if not self.handle_key(key):
                    break

        cv2.destroyAllWindows()


# -----------------------------------------------------------------------------
# 7. GENERADOR SINTÉTICO EN LOTE (--generate-synthetic)
# -----------------------------------------------------------------------------
def generate_synthetic_dataset(output_dir: str, n_subjects: int = 10, reps_per_edge: int = 3):
    print(f"🛠️ Generando dataset sintético ({n_subjects} sujetos, {reps_per_edge} reps/arista, 42 aristas)...")
    total_clips = n_subjects * len(ALL_EDGES) * reps_per_edge
    os.makedirs(output_dir, exist_ok=True)
    profiles = load_subject_profiles()
    mock = MockTransitionSensor()

    generated_count = 0
    for s_idx in range(1, n_subjects + 1):
        sub_folder = f"subject_{s_idx:02d}"
        sub_dir = os.path.join(output_dir, sub_folder)
        os.makedirs(sub_dir, exist_ok=True)
        sub_info = profiles.get(str(s_idx), {
            "name": f"Participante {s_idx}",
            "height_cm": 174,
            "gender": "M"
        })

        for (origin, target) in ALL_EDGES:
            for rep in range(1, reps_per_edge + 1):
                filename = f"S{s_idx:02d}_trans_{origin}_to_{target}_rep{rep:02d}.csv"
                filepath = os.path.join(sub_dir, filename)

                mock.trigger_transition(origin, target, duration_frames=50)
                rows = []
                for f_idx in range(50):
                    skel = mock.get_frame()
                    row = {
                        "frame_idx": f_idx,
                        "subject_id": sub_folder,
                        "subject_name": sub_info.get("name", "anon"),
                        "subject_height_cm": sub_info.get("height_cm", 174),
                        "subject_gender": sub_info.get("gender", "M"),
                        "origin_action": origin,
                        "target_action": target
                    }
                    for j in range(32):
                        pos_m = skel[j] / 1000.0
                        row[f"joint_{j}_x"] = pos_m[0]
                        row[f"joint_{j}_y"] = pos_m[1]
                        row[f"joint_{j}_z"] = pos_m[2]
                    rows.append(row)

                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False)
                generated_count += 1

                if generated_count % 100 == 0 or generated_count == total_clips:
                    print(f"  [{generated_count}/{total_clips}] Clips generados ({generated_count*100.0/total_clips:.1f}%)...")

    print(f"✅ Generación sintética completada exitosamente en {output_dir}.")


# -----------------------------------------------------------------------------
# 8. PUNTO DE ENTRADA CLI
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="SF3 Kinect Transition Studio & Practice")
    parser.add_argument("--mock", action="store_true", default=False,
                        help="Forzar modo simulador procedural (sin hardware físico)")
    parser.add_argument("--kinect", action="store_true", default=False,
                        help="Usar sensor Azure Kinect físico (prioridad por defecto)")
    parser.add_argument("--subject", type=int, default=1,
                        help="ID inicial del sujeto (1 en adelante)")
    parser.add_argument("--target-reps", type=int, default=1,
                        help="Repeticiones meta por arista (por defecto: 1)")
    parser.add_argument("--generate-synthetic", action="store_true", default=False,
                        help="Generar dataset sintético para las 42 aristas en batch y salir")

    args = parser.parse_args()

    if args.generate_synthetic:
        generate_synthetic_dataset(DATASET_DIR, n_subjects=10, reps_per_edge=3)
        return

    # Si se pasa --mock, usa el simulador procedural.
    # De lo contrario, intenta conectar automáticamente con el sensor Azure Kinect DK físico.
    use_mock = args.mock
    studio = TransitionStudio(use_mock=use_mock, subject_id=args.subject, target_reps=args.target_reps)
    studio.run()


if __name__ == "__main__":
    main()
