"""
Street Fighter III: 3rd Strike - Kinect Static Posture & Kinematic Feature Extractor
Módulo matemático para cálculo de características posturales y geométricas 3D
a partir de secuencias de articulaciones del Azure Kinect Body Tracking SDK.
Optimizado para detección de Poses Sostenidas (Held Poses) invariante a la velocidad.
"""

import numpy as np
import pandas as pd

# Mapeo oficial de índices de articulaciones del Azure Kinect SDK (0 a 31)
K4ABT_JOINT_PELVIS = 0
K4ABT_JOINT_SPINE_NAVEL = 1
K4ABT_JOINT_SPINE_CHEST = 2
K4ABT_JOINT_NECK = 3
K4ABT_JOINT_SHOULDER_LEFT = 5
K4ABT_JOINT_ELBOW_LEFT = 6
K4ABT_JOINT_WRIST_LEFT = 7
K4ABT_JOINT_HAND_LEFT = 8
K4ABT_JOINT_SHOULDER_RIGHT = 12
K4ABT_JOINT_ELBOW_RIGHT = 13
K4ABT_JOINT_WRIST_RIGHT = 14
K4ABT_JOINT_HAND_RIGHT = 15
K4ABT_JOINT_HIP_LEFT = 18
K4ABT_JOINT_KNEE_LEFT = 19
K4ABT_JOINT_ANKLE_LEFT = 20
K4ABT_JOINT_FOOT_LEFT = 21
K4ABT_JOINT_HIP_RIGHT = 22
K4ABT_JOINT_KNEE_RIGHT = 23
K4ABT_JOINT_ANKLE_RIGHT = 24
K4ABT_JOINT_FOOT_RIGHT = 25
K4ABT_JOINT_HEAD = 26

# Catálogo de las 8 clases maestras de combate
ACTION_CLASSES = [
    "idle",           # 0: Reposo / Guardia de combate
    "punch_right",    # 1: Puñetazo con brazo derecho
    "punch_left",     # 2: Puñetazo con brazo izquierdo
    "kick_right",     # 3: Patada con pierna derecha
    "kick_left",      # 4: Patada con pierna izquierda
    "crouch",         # 5: Agacharse / Posición baja
    "jump",           # 6: Salto vertical / aéreo
    "block"           # 7: Bloqueo defensivo / Brazos levantados cubriendo pecho/rostro
]

ACTION_NAME_TO_ID = {name: idx for idx, name in enumerate(ACTION_CLASSES)}
ACTION_ID_TO_NAME = {idx: name for idx, name in enumerate(ACTION_CLASSES)}

# 44 Características Geométricas de Postura Estática (Invariantes a estatura y velocidad)
FEATURE_NAMES = [
    "horiz_wr_r_mean",
    "horiz_wr_r_max",
    "horiz_wr_l_mean",
    "horiz_wr_l_max",
    "horiz_hd_r_mean",
    "horiz_hd_r_max",
    "horiz_hd_l_mean",
    "horiz_hd_l_max",
    "horiz_pelvis_wr_r",
    "horiz_pelvis_wr_l",
    "arm_ext_r_mean",
    "arm_ext_l_mean",
    "elev_wr_r_mean",
    "elev_wr_l_mean",
    "elev_hd_r_mean",
    "elev_hd_l_mean",
    "wr_rel_chest_r",
    "wr_rel_chest_l",
    "wr_rel_head_r",
    "wr_rel_head_l",
    "min_wr_rel_chest",
    "mean_wr_rel_chest",
    "ank_depth_r",
    "ank_depth_l",
    "ft_depth_r",
    "ft_depth_l",
    "kn_depth_r",
    "kn_depth_l",
    "max_ank_depth",
    "min_ank_depth",
    "ank_elevation_asym",
    "ft_elevation_asym",
    "kn_elevation_asym",
    "horiz_ank_r",
    "horiz_ank_l",
    "elbow_angle_r",
    "elbow_angle_l",
    "knee_angle_r",
    "knee_angle_l",
    "horiz_wr_asym",
    "horiz_hd_asym",
    "arm_ext_asym",
    "elbow_angle_asym",
    "wrist_distance_norm"
]


def compute_angle_3d(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Calcula el ángulo en grados en la articulación B formada por los vectores BA y BC.
    theta = arccos((BA . BC) / (||BA|| * ||BC||))
    """
    ba = a - b
    bc = c - b
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)

    if norm_ba < 1e-6 or norm_bc < 1e-6:
        return 180.0

    cosine = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


def one_euro_filter_3d_clip(frames_xyz: np.ndarray, fps: float = 30.0, min_cutoff: float = 1.0, beta: float = 0.007) -> np.ndarray:
    """
    Aplica el filtro adaptativo One-Euro ($1€$) a lo largo del eje temporal para cada articulación.
    """
    n_frames = len(frames_xyz)
    if n_frames < 3:
        return frames_xyz.copy()

    dt = 1.0 / max(1.0, fps)
    filtered = np.zeros_like(frames_xyz, dtype=np.float32)
    filtered[0] = frames_xyz[0]

    d_cutoff = 1.0
    tau_d = 1.0 / (2.0 * np.pi * d_cutoff)
    alpha_d = 1.0 / (1.0 + tau_d / dt)

    prev_x = frames_xyz[0].copy()
    prev_d = np.zeros_like(frames_xyz[0], dtype=np.float32)

    for t in range(1, n_frames):
        curr_x = frames_xyz[t]
        dx = (curr_x - prev_x) / dt
        d = alpha_d * dx + (1.0 - alpha_d) * prev_d
        prev_d = d

        cutoff = min_cutoff + beta * np.abs(d)
        tau = 1.0 / (2.0 * np.pi * np.maximum(cutoff, 1e-4))
        alpha = 1.0 / (1.0 + tau / dt)

        filtered[t] = alpha * curr_x + (1.0 - alpha) * filtered[t - 1]
        prev_x = curr_x

    return filtered


def extract_peak_pose_window(frames_xyz: np.ndarray, action_name: str, window_size: int = 6) -> np.ndarray:
    """
    Localiza el frame de máxima expresión postural (peak pose) dentro de un clip de 35 frames
    y retorna una ventana estática de `window_size` frames centrada en la postura sostenida.
    Esto permite entrenar el clasificador sobre la geometría exacta de la pose mantenida.
    """
    n_frames = len(frames_xyz)
    if n_frames <= 1:
        return np.repeat(frames_xyz, window_size, axis=0)

    pelvis = frames_xyz[:, K4ABT_JOINT_PELVIS, :]
    local = frames_xyz - pelvis[:, np.newaxis, :]

    sh_r = local[:, K4ABT_JOINT_SHOULDER_RIGHT, :]
    wr_r = local[:, K4ABT_JOINT_WRIST_RIGHT, :]
    sh_l = local[:, K4ABT_JOINT_SHOULDER_LEFT, :]
    wr_l = local[:, K4ABT_JOINT_WRIST_LEFT, :]
    ank_r = local[:, K4ABT_JOINT_ANKLE_RIGHT, :]
    ank_l = local[:, K4ABT_JOINT_ANKLE_LEFT, :]

    horiz_r = np.linalg.norm(wr_r[:, [0, 2]] - sh_r[:, [0, 2]], axis=1)
    horiz_l = np.linalg.norm(wr_l[:, [0, 2]] - sh_l[:, [0, 2]], axis=1)

    if action_name == "punch_right":
        idx = int(np.argmax(horiz_r - 0.5 * horiz_l))
    elif action_name == "punch_left":
        idx = int(np.argmax(horiz_l - 0.5 * horiz_r))
    elif action_name == "kick_right":
        idx = int(np.argmax(ank_l[:, 1] - ank_r[:, 1]))
    elif action_name == "kick_left":
        idx = int(np.argmax(ank_r[:, 1] - ank_l[:, 1]))
    elif action_name == "crouch":
        idx = int(np.argmin(0.5 * (ank_r[:, 1] + ank_l[:, 1])))
    elif action_name == "block":
        idx = int(np.argmin(wr_r[:, 1] + wr_l[:, 1]))
    elif action_name == "jump":
        idx = int(np.argmin(pelvis[:, 1]))
    else:
        idx = n_frames // 2

    return np.repeat(frames_xyz[idx:idx + 1], window_size, axis=0)


def extract_clip_features(frames_joints_xyz: np.ndarray, fps: float = 30.0, apply_filter: bool = True) -> dict:
    """
    Extrae las 44 características geométricas de postura estática a partir de la ventana reciente
    de frames 3D de articulaciones (evalúa los últimos 6 frames ~200ms para respuesta inmediata
    al sostener una pose sin depender de la velocidad de transición).
    """
    n_frames = len(frames_joints_xyz)
    if n_frames < 1:
        raise ValueError("Se requiere al menos 1 frame para extraer características posturales.")

    if apply_filter and n_frames >= 3:
        clean_frames = one_euro_filter_3d_clip(frames_joints_xyz, fps=fps)
    else:
        clean_frames = frames_joints_xyz

    # Evaluar únicamente los últimos 6 frames (~0.2s) para que la postura sostenida
    # sea independiente del historial antiguo del buffer
    w = clean_frames[-6:] if len(clean_frames) > 6 else clean_frames
    n_f = len(w)

    pelvis = w[:, K4ABT_JOINT_PELVIS, :]
    local = w - pelvis[:, np.newaxis, :]

    sh_r = local[:, K4ABT_JOINT_SHOULDER_RIGHT, :]
    el_r = local[:, K4ABT_JOINT_ELBOW_RIGHT, :]
    wr_r = local[:, K4ABT_JOINT_WRIST_RIGHT, :]
    hd_r = local[:, K4ABT_JOINT_HAND_RIGHT, :]

    sh_l = local[:, K4ABT_JOINT_SHOULDER_LEFT, :]
    el_l = local[:, K4ABT_JOINT_ELBOW_LEFT, :]
    wr_l = local[:, K4ABT_JOINT_WRIST_LEFT, :]
    hd_l = local[:, K4ABT_JOINT_HAND_LEFT, :]

    hip_r = local[:, K4ABT_JOINT_HIP_RIGHT, :]
    kn_r = local[:, K4ABT_JOINT_KNEE_RIGHT, :]
    ank_r = local[:, K4ABT_JOINT_ANKLE_RIGHT, :]
    ft_r = local[:, K4ABT_JOINT_FOOT_RIGHT, :]

    hip_l = local[:, K4ABT_JOINT_HIP_LEFT, :]
    kn_l = local[:, K4ABT_JOINT_KNEE_LEFT, :]
    ank_l = local[:, K4ABT_JOINT_ANKLE_LEFT, :]
    ft_l = local[:, K4ABT_JOINT_FOOT_LEFT, :]

    chest = local[:, K4ABT_JOINT_SPINE_CHEST, :]
    head = local[:, K4ABT_JOINT_HEAD, :]

    # Longitudes óseas para normalización antropométrica invariante a la estatura
    torso_len = float(np.mean(np.linalg.norm(chest, axis=1)))
    if torso_len < 0.15:
        torso_len = 0.45

    len_arm_r = float(np.mean(np.linalg.norm(sh_r - el_r, axis=1) + np.linalg.norm(el_r - wr_r, axis=1)))
    len_arm_l = float(np.mean(np.linalg.norm(sh_l - el_l, axis=1) + np.linalg.norm(el_l - wr_l, axis=1)))
    if len_arm_r < 0.20:
        len_arm_r = 0.55
    if len_arm_l < 0.20:
        len_arm_l = 0.55

    len_leg_r = float(np.mean(np.linalg.norm(hip_r - kn_r, axis=1) + np.linalg.norm(kn_r - ank_r, axis=1)))
    len_leg_l = float(np.mean(np.linalg.norm(hip_l - kn_l, axis=1) + np.linalg.norm(kn_l - ank_l, axis=1)))
    if len_leg_r < 0.30:
        len_leg_r = 0.80
    if len_leg_l < 0.30:
        len_leg_l = 0.80

    # 1. Extensión horizontal en el plano X-Z desde el hombro (evita confundir brazos caídos con puñetazos)
    horiz_wr_r = np.linalg.norm(wr_r[:, [0, 2]] - sh_r[:, [0, 2]], axis=1) / len_arm_r
    horiz_wr_l = np.linalg.norm(wr_l[:, [0, 2]] - sh_l[:, [0, 2]], axis=1) / len_arm_l
    horiz_hd_r = np.linalg.norm(hd_r[:, [0, 2]] - sh_r[:, [0, 2]], axis=1) / len_arm_r
    horiz_hd_l = np.linalg.norm(hd_l[:, [0, 2]] - sh_l[:, [0, 2]], axis=1) / len_arm_l

    horiz_pelvis_wr_r = np.linalg.norm(wr_r[:, [0, 2]], axis=1) / len_arm_r
    horiz_pelvis_wr_l = np.linalg.norm(wr_l[:, [0, 2]], axis=1) / len_arm_l

    arm_ext_r = np.linalg.norm(wr_r - sh_r, axis=1) / len_arm_r
    arm_ext_l = np.linalg.norm(wr_l - sh_l, axis=1) / len_arm_l

    # 2. Elevación vertical de muñecas y manos (-Y es hacia arriba en Azure Kinect)
    elev_wr_r = -wr_r[:, 1] / torso_len
    elev_wr_l = -wr_l[:, 1] / torso_len
    elev_hd_r = -hd_r[:, 1] / torso_len
    elev_hd_l = -hd_l[:, 1] / torso_len

    wr_rel_chest_r = (chest[:, 1] - wr_r[:, 1]) / torso_len
    wr_rel_chest_l = (chest[:, 1] - wr_l[:, 1]) / torso_len
    wr_rel_head_r = (head[:, 1] - wr_r[:, 1]) / torso_len
    wr_rel_head_l = (head[:, 1] - wr_l[:, 1]) / torso_len
    min_wr_rel_chest = np.minimum(wr_rel_chest_r, wr_rel_chest_l)
    mean_wr_rel_chest = 0.5 * (wr_rel_chest_r + wr_rel_chest_l)

    # 3. Métricas verticales y horizontales de piernas/tobillos (Crouch vs Kick vs Idle)
    ank_depth_r = ank_r[:, 1] / len_leg_r
    ank_depth_l = ank_l[:, 1] / len_leg_l
    ft_depth_r = ft_r[:, 1] / len_leg_r
    ft_depth_l = ft_l[:, 1] / len_leg_l
    kn_depth_r = kn_r[:, 1] / len_leg_r
    kn_depth_l = kn_l[:, 1] / len_leg_l

    max_ank_depth = np.maximum(ank_depth_r, ank_depth_l)
    min_ank_depth = np.minimum(ank_depth_r, ank_depth_l)
    ank_elevation_asym = ank_depth_l - ank_depth_r
    ft_elevation_asym = ft_depth_l - ft_depth_r
    kn_elevation_asym = kn_depth_l - kn_depth_r

    horiz_ank_r = np.linalg.norm(ank_r[:, [0, 2]], axis=1) / len_leg_r
    horiz_ank_l = np.linalg.norm(ank_l[:, [0, 2]], axis=1) / len_leg_l

    # 4. Ángulos articulares 3D
    ang_el_r = np.array([compute_angle_3d(sh_r[t], el_r[t], wr_r[t]) for t in range(n_f)])
    ang_el_l = np.array([compute_angle_3d(sh_l[t], el_l[t], wr_l[t]) for t in range(n_f)])
    ang_kn_r = np.array([compute_angle_3d(hip_r[t], kn_r[t], ank_r[t]) for t in range(n_f)])
    ang_kn_l = np.array([compute_angle_3d(hip_l[t], kn_l[t], ank_l[t]) for t in range(n_f)])

    # 5. Asimetrías bilaterales y distancia entre muñecas
    horiz_wr_asym = horiz_wr_r - horiz_wr_l
    horiz_hd_asym = horiz_hd_r - horiz_hd_l
    arm_ext_asym = arm_ext_r - arm_ext_l
    el_ang_asym = ang_el_r - ang_el_l
    wr_dist = np.linalg.norm(wr_r - wr_l, axis=1) / torso_len

    features = {
        "horiz_wr_r_mean": float(np.mean(horiz_wr_r)),
        "horiz_wr_r_max": float(np.max(horiz_wr_r)),
        "horiz_wr_l_mean": float(np.mean(horiz_wr_l)),
        "horiz_wr_l_max": float(np.max(horiz_wr_l)),
        "horiz_hd_r_mean": float(np.mean(horiz_hd_r)),
        "horiz_hd_r_max": float(np.max(horiz_hd_r)),
        "horiz_hd_l_mean": float(np.mean(horiz_hd_l)),
        "horiz_hd_l_max": float(np.max(horiz_hd_l)),
        "horiz_pelvis_wr_r": float(np.mean(horiz_pelvis_wr_r)),
        "horiz_pelvis_wr_l": float(np.mean(horiz_pelvis_wr_l)),
        "arm_ext_r_mean": float(np.mean(arm_ext_r)),
        "arm_ext_l_mean": float(np.mean(arm_ext_l)),
        "elev_wr_r_mean": float(np.mean(elev_wr_r)),
        "elev_wr_l_mean": float(np.mean(elev_wr_l)),
        "elev_hd_r_mean": float(np.mean(elev_hd_r)),
        "elev_hd_l_mean": float(np.mean(elev_hd_l)),
        "wr_rel_chest_r": float(np.mean(wr_rel_chest_r)),
        "wr_rel_chest_l": float(np.mean(wr_rel_chest_l)),
        "wr_rel_head_r": float(np.mean(wr_rel_head_r)),
        "wr_rel_head_l": float(np.mean(wr_rel_head_l)),
        "min_wr_rel_chest": float(np.mean(min_wr_rel_chest)),
        "mean_wr_rel_chest": float(np.mean(mean_wr_rel_chest)),
        "ank_depth_r": float(np.mean(ank_depth_r)),
        "ank_depth_l": float(np.mean(ank_depth_l)),
        "ft_depth_r": float(np.mean(ft_depth_r)),
        "ft_depth_l": float(np.mean(ft_depth_l)),
        "kn_depth_r": float(np.mean(kn_depth_r)),
        "kn_depth_l": float(np.mean(kn_depth_l)),
        "max_ank_depth": float(np.mean(max_ank_depth)),
        "min_ank_depth": float(np.mean(min_ank_depth)),
        "ank_elevation_asym": float(np.mean(ank_elevation_asym)),
        "ft_elevation_asym": float(np.mean(ft_elevation_asym)),
        "kn_elevation_asym": float(np.mean(kn_elevation_asym)),
        "horiz_ank_r": float(np.mean(horiz_ank_r)),
        "horiz_ank_l": float(np.mean(horiz_ank_l)),
        "elbow_angle_r": float(np.mean(ang_el_r)),
        "elbow_angle_l": float(np.mean(ang_el_l)),
        "knee_angle_r": float(np.mean(ang_kn_r)),
        "knee_angle_l": float(np.mean(ang_kn_l)),
        "horiz_wr_asym": float(np.mean(horiz_wr_asym)),
        "horiz_hd_asym": float(np.mean(horiz_hd_asym)),
        "arm_ext_asym": float(np.mean(arm_ext_asym)),
        "elbow_angle_asym": float(np.mean(el_ang_asym)),
        "wrist_distance_norm": float(np.mean(wr_dist))
    }

    return features


def validate_posture_biomechanics(action_name: str, feats: dict) -> bool:
    """
    Filtro biomecánico de seguridad para descartar falsos positivos cuando el jugador
    entra en escena, camina o tiene los brazos relajados a los lados.
    """
    if action_name == "idle":
        return True

    horiz_r = feats.get("horiz_wr_r_mean", 0.0)
    horiz_l = feats.get("horiz_wr_l_mean", 0.0)
    wr_chest_r = feats.get("wr_rel_chest_r", 0.0)
    wr_chest_l = feats.get("wr_rel_chest_l", 0.0)
    min_wr_chest = feats.get("min_wr_rel_chest", -1.0)
    mean_wr_chest = feats.get("mean_wr_rel_chest", -1.0)
    max_ank_d = feats.get("max_ank_depth", 0.90)
    ank_asym = feats.get("ank_elevation_asym", 0.0)

    if action_name == "punch_right":
        # Puño derecho extendido horizontalmente y por encima de la cintura
        return horiz_r >= 0.48 and (horiz_r - horiz_l) >= 0.04 and wr_chest_r >= -0.35

    if action_name == "punch_left":
        # Puño izquierdo extendido horizontalmente y por encima de la cintura
        return horiz_l >= 0.50 and (horiz_l - horiz_r) >= 0.04 and wr_chest_l >= -0.35

    if action_name == "kick_right":
        # Tobillo derecho más elevado que el izquierdo (en Idle está entre -0.03 y +0.04)
        return ank_asym >= 0.06

    if action_name == "kick_left":
        # Tobillo izquierdo más elevado que el derecho (en Idle está entre -0.03 y +0.04)
        return ank_asym <= -0.06

    if action_name == "crouch":
        # Pelvis descendida respecto a ambos tobillos (en Idle es >= 0.97, en Crouch <= 0.83)
        return max_ank_d <= 0.86

    if action_name == "block":
        # Ambos brazos levantados frente al pecho/cabeza y de pie
        return mean_wr_chest >= 0.35 and max_ank_d >= 0.80

    return True


def load_clip_from_csv(csv_path: str) -> np.ndarray:
    """
    Carga un archivo CSV grabado por el visualizador y lo convierte a un array (N_frames, 32, 3).
    """
    df = pd.read_csv(csv_path)

    joint_cols = [c for c in df.columns if c.startswith("joint_")]
    if joint_cols:
        data_df = df[joint_cols]
    else:
        meta_cols = [
            c for c in [
                "frame_idx", "timestamp", "timestamp_s", "subject_id",
                "subject_name", "subject_height_cm", "subject_gender",
                "action_id", "label"
            ] if c in df.columns
        ]
        data_df = df.drop(columns=meta_cols)

    arr = data_df.values.astype(np.float32)

    n_cols = arr.shape[1]
    if n_cols % 3 != 0:
        raise ValueError(f"El número de columnas de coordenadas ({n_cols}) no es múltiplo de 3.")

    n_joints = n_cols // 3
    n_frames = arr.shape[0]

    return arr.reshape((n_frames, n_joints, 3))
