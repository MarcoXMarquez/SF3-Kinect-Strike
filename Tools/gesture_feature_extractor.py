"""
Street Fighter III: 3rd Strike - Kinect Kinematic Feature Extractor
Módulo matemático para cálculo de características cinemáticas y espaciales
a partir de secuencias temporales de articulaciones del Azure Kinect Body Tracking SDK.
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
    "block"           # 7: Bloqueo defensivo / Brazos cruzados al pecho
]

ACTION_NAME_TO_ID = {name: idx for idx, name in enumerate(ACTION_CLASSES)}
ACTION_ID_TO_NAME = {idx: name for idx, name in enumerate(ACTION_CLASSES)}

FEATURE_NAMES = [
    # 1. Velocidades pico de extremidades (m/s)
    "peak_vel_wrist_r",
    "peak_vel_wrist_l",
    "peak_vel_hand_r",
    "peak_vel_hand_l",
    "peak_vel_ankle_r",
    "peak_vel_ankle_l",
    "peak_vel_foot_r",
    "peak_vel_foot_l",
    "peak_vel_pelvis_y",
    # 2. Desplazamientos netos (m)
    "net_disp_pelvis_y",     # Negativo = Agacharse, Positivo = Salto
    "max_disp_pelvis_y",
    "min_disp_pelvis_y",
    "net_reach_wrist_r_z",   # Alcance en profundidad hacia sensor (Z)
    "net_reach_wrist_l_z",
    "net_reach_hand_r_z",
    "net_reach_hand_l_z",
    "net_reach_ankle_r_z",
    "net_reach_ankle_l_z",
    # 3. Elevación máxima respecto a pelvis (m)
    "max_elev_ankle_r",
    "max_elev_ankle_l",
    "max_elev_foot_r",
    "max_elev_foot_l",
    "max_elev_wrist_r",
    "max_elev_wrist_l",
    # 4. Rangos de ángulos articulares 3D (grados)
    "min_elbow_angle_r",
    "max_elbow_angle_r",
    "min_elbow_angle_l",
    "max_elbow_angle_l",
    "min_knee_angle_r",
    "max_knee_angle_r",
    "min_knee_angle_l",
    "max_knee_angle_l",
    # 5. Inclinación y torsión del torso
    "torso_pitch_lean",
    "torso_roll_lean",
    # 6. Asimetría de actividad de extremidades
    "arm_activity_asymmetry",  # Positivo = Dominio Der, Negativo = Dominio Izq
    "leg_activity_asymmetry",  # Positivo = Dominio Der, Negativo = Dominio Izq
    # 7. Proximidad de muñecas y manos (detección de bloqueo / guardia)
    "min_wrist_distance",
    "mean_wrist_distance",
    "min_hand_distance",
    # 8. Normalización antropométrica y extensión biomecánica
    "torso_length",
    "max_arm_extension_r",
    "max_arm_extension_l",
    "max_leg_extension_r",
    "max_leg_extension_l"
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
    Filtra drásticamente el jitter de profundidad milimétrico en reposo/guardia sin retrasar
    la respuesta de picos cinemáticos explosivos (puñetazos y patadas).
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


def extract_clip_features(frames_joints_xyz: np.ndarray, fps: float = 30.0, apply_filter: bool = True) -> dict:
    """
    Extrae un vector tabular de características cinemáticas a partir de una secuencia temporal
    de frames 3D de articulaciones.

    Parámetros:
    -----------
    frames_joints_xyz : np.ndarray de forma (N_frames, 32, 3) o (N_frames, >=25, 3)
                        Coordenadas (x, y, z) en metros de cada articulación en cada frame.
    fps : float
          Tasa de muestreo (default: 30.0 FPS del Azure Kinect).
    apply_filter : bool
          Aplica filtro One-Euro para eliminar jitter de profundidad antes de derivar.

    Retorna:
    --------
    dict con las 44 características calculadas.
    """
    n_frames = len(frames_joints_xyz)
    if n_frames < 2:
        raise ValueError(f"Se requieren al menos 2 frames para cinemática, recibidos: {n_frames}")

    dt = 1.0 / fps

    # 0. Filtrado paso bajo adaptativo One-Euro contra jitter de sensor
    if apply_filter and n_frames >= 3:
        clean_frames = one_euro_filter_3d_clip(frames_joints_xyz, fps=fps)
    else:
        clean_frames = frames_joints_xyz

    # 1. Normalización espacial local: P_local = P_joint - P_pelvis
    pelvis = clean_frames[:, K4ABT_JOINT_PELVIS, :]
    local_joints = clean_frames - pelvis[:, np.newaxis, :]

    # 2. Articulaciones clave en coordenadas locales
    wrist_r = local_joints[:, K4ABT_JOINT_WRIST_RIGHT, :]
    wrist_l = local_joints[:, K4ABT_JOINT_WRIST_LEFT, :]
    elbow_r = local_joints[:, K4ABT_JOINT_ELBOW_RIGHT, :]
    elbow_l = local_joints[:, K4ABT_JOINT_ELBOW_LEFT, :]
    shoulder_r = local_joints[:, K4ABT_JOINT_SHOULDER_RIGHT, :]
    shoulder_l = local_joints[:, K4ABT_JOINT_SHOULDER_LEFT, :]

    ankle_r = local_joints[:, K4ABT_JOINT_ANKLE_RIGHT, :]
    ankle_l = local_joints[:, K4ABT_JOINT_ANKLE_LEFT, :]
    knee_r = local_joints[:, K4ABT_JOINT_KNEE_RIGHT, :]
    knee_l = local_joints[:, K4ABT_JOINT_KNEE_LEFT, :]
    hip_r = local_joints[:, K4ABT_JOINT_HIP_RIGHT, :]
    hip_l = local_joints[:, K4ABT_JOINT_HIP_LEFT, :]

    hand_r = local_joints[:, K4ABT_JOINT_HAND_RIGHT, :]
    hand_l = local_joints[:, K4ABT_JOINT_HAND_LEFT, :]
    foot_r = local_joints[:, K4ABT_JOINT_FOOT_RIGHT, :]
    foot_l = local_joints[:, K4ABT_JOINT_FOOT_LEFT, :]
    chest = local_joints[:, K4ABT_JOINT_SPINE_CHEST, :]

    # 3. Velocidades instantáneas (m/s)
    vel_wrist_r = np.linalg.norm(np.diff(wrist_r, axis=0), axis=1) / dt
    vel_wrist_l = np.linalg.norm(np.diff(wrist_l, axis=0), axis=1) / dt
    vel_hand_r = np.linalg.norm(np.diff(hand_r, axis=0), axis=1) / dt
    vel_hand_l = np.linalg.norm(np.diff(hand_l, axis=0), axis=1) / dt
    vel_ankle_r = np.linalg.norm(np.diff(ankle_r, axis=0), axis=1) / dt
    vel_ankle_l = np.linalg.norm(np.diff(ankle_l, axis=0), axis=1) / dt
    vel_foot_r = np.linalg.norm(np.diff(foot_r, axis=0), axis=1) / dt
    vel_foot_l = np.linalg.norm(np.diff(foot_l, axis=0), axis=1) / dt

    # Velocidad vertical de la pelvis (eje Y absoluto de la cámara)
    # En Azure Kinect SDK, Y positivo es hacia abajo (+Y = descender hacia el suelo).
    # Invertimos el signo de Y para que Y positivo represente subir / ascender (física estándar de Unity).
    pelvis_y_unity = -pelvis[:, 1]
    vel_pelvis_y = np.diff(pelvis_y_unity) / dt

    # 4. Desplazamientos verticales de la pelvis respecto al frame inicial
    disp_pelvis_y = pelvis_y_unity - pelvis_y_unity[0]

    # 5. Alcance en profundidad Z respecto a la pelvis (menor Z en Kinect = más cerca de la cámara)
    reach_wrist_r_z = -wrist_r[:, 2]
    reach_wrist_l_z = -wrist_l[:, 2]
    reach_hand_r_z = -hand_r[:, 2]
    reach_hand_l_z = -hand_l[:, 2]
    reach_ankle_r_z = -ankle_r[:, 2]
    reach_ankle_l_z = -ankle_l[:, 2]

    # 6. Elevación vertical respecto a la pelvis (en sistema Unity, pelvis = 0)
    elev_wrist_r = -wrist_r[:, 1]
    elev_wrist_l = -wrist_l[:, 1]
    elev_ankle_r = -ankle_r[:, 1]
    elev_ankle_l = -ankle_l[:, 1]
    elev_foot_r = -foot_r[:, 1]
    elev_foot_l = -foot_l[:, 1]

    # 7. Ángulos articulares 3D en cada frame
    angles_elbow_r = [
        compute_angle_3d(shoulder_r[t], elbow_r[t], wrist_r[t])
        for t in range(n_frames)
    ]
    angles_elbow_l = [
        compute_angle_3d(shoulder_l[t], elbow_l[t], wrist_l[t])
        for t in range(n_frames)
    ]
    angles_knee_r = [
        compute_angle_3d(hip_r[t], knee_r[t], ankle_r[t])
        for t in range(n_frames)
    ]
    angles_knee_l = [
        compute_angle_3d(hip_l[t], knee_l[t], ankle_l[t])
        for t in range(n_frames)
    ]

    # 8. Inclinación y torsión del torso respecto a la pelvis
    torso_pitch = float(np.mean(-chest[:, 2]))  # Positivo = Inclinado al frente
    torso_roll = float(np.mean(chest[:, 0]))    # Positivo = Inclinado a la derecha

    # 9. Asimetría de actividad
    peak_wr_r = float(np.max(vel_wrist_r))
    peak_wr_l = float(np.max(vel_wrist_l))
    peak_hd_r = float(np.max(vel_hand_r))
    peak_hd_l = float(np.max(vel_hand_l))
    peak_ak_r = float(np.max(vel_ankle_r))
    peak_ak_l = float(np.max(vel_ankle_l))
    peak_ft_r = float(np.max(vel_foot_r))
    peak_ft_l = float(np.max(vel_foot_l))

    arm_asym = (peak_hd_r - peak_hd_l) / (peak_hd_r + peak_hd_l + 1e-4)
    leg_asym = (peak_ft_r - peak_ft_l) / (peak_ft_r + peak_ft_l + 1e-4)

    # 10. Proximidad entre muñecas y manos (crucial para Bloqueo)
    wrist_dist = np.linalg.norm(wrist_r - wrist_l, axis=1)
    hand_dist = np.linalg.norm(hand_r - hand_l, axis=1)
    min_wrist_d = float(np.min(wrist_dist))
    mean_wrist_d = float(np.mean(wrist_dist))
    min_hand_d = float(np.min(hand_dist))

    # 11. Normalización Antropométrica y Extensión Biomecánica (Invariante a Estatura)
    # Longitud media del torso entre Pelvis y Pecho
    torso_len = float(np.mean(np.linalg.norm(chest, axis=1)))
    if torso_len < 0.15:
        torso_len = 0.45

    # Longitudes de segmentos óseos en el clip
    len_arm_r = float(np.mean(np.linalg.norm(shoulder_r - elbow_r, axis=1) + np.linalg.norm(elbow_r - wrist_r, axis=1)))
    len_arm_l = float(np.mean(np.linalg.norm(shoulder_l - elbow_l, axis=1) + np.linalg.norm(elbow_l - wrist_l, axis=1)))
    if len_arm_r < 0.20: len_arm_r = 0.65
    if len_arm_l < 0.20: len_arm_l = 0.65

    len_leg_r = float(np.mean(np.linalg.norm(hip_r - knee_r, axis=1) + np.linalg.norm(knee_r - ankle_r, axis=1)))
    len_leg_l = float(np.mean(np.linalg.norm(hip_l - knee_l, axis=1) + np.linalg.norm(knee_l - ankle_l, axis=1)))
    if len_leg_r < 0.30: len_leg_r = 0.85
    if len_leg_l < 0.30: len_leg_l = 0.85

    # Ratio de extensión del brazo (distancia hombro-muñeca / longitud total del brazo)
    # Cerca de 1.0 en puño totalmente estirado, ~0.4 en guardia reposo
    arm_ext_r = np.linalg.norm(wrist_r - shoulder_r, axis=1) / len_arm_r
    arm_ext_l = np.linalg.norm(wrist_l - shoulder_l, axis=1) / len_arm_l

    # Ratio de extensión de la pierna (distancia cadera-tobillo / longitud total de la pierna)
    leg_ext_r = np.linalg.norm(ankle_r - hip_r, axis=1) / len_leg_r
    leg_ext_l = np.linalg.norm(ankle_l - hip_l, axis=1) / len_leg_l

    features = {
        "peak_vel_wrist_r": peak_wr_r,
        "peak_vel_wrist_l": peak_wr_l,
        "peak_vel_hand_r": peak_hd_r,
        "peak_vel_hand_l": peak_hd_l,
        "peak_vel_ankle_r": peak_ak_r,
        "peak_vel_ankle_l": peak_ak_l,
        "peak_vel_foot_r": peak_ft_r,
        "peak_vel_foot_l": peak_ft_l,
        "peak_vel_pelvis_y": float(np.max(np.abs(vel_pelvis_y))),
        "net_disp_pelvis_y": float(disp_pelvis_y[-1]),
        "max_disp_pelvis_y": float(np.max(disp_pelvis_y)),
        "min_disp_pelvis_y": float(np.min(disp_pelvis_y)),
        "net_reach_wrist_r_z": float(np.max(reach_wrist_r_z)),
        "net_reach_wrist_l_z": float(np.max(reach_wrist_l_z)),
        "net_reach_hand_r_z": float(np.max(reach_hand_r_z)),
        "net_reach_hand_l_z": float(np.max(reach_hand_l_z)),
        "net_reach_ankle_r_z": float(np.max(reach_ankle_r_z)),
        "net_reach_ankle_l_z": float(np.max(reach_ankle_l_z)),
        "max_elev_ankle_r": float(np.max(elev_ankle_r)),
        "max_elev_ankle_l": float(np.max(elev_ankle_l)),
        "max_elev_foot_r": float(np.max(elev_foot_r)),
        "max_elev_foot_l": float(np.max(elev_foot_l)),
        "max_elev_wrist_r": float(np.max(elev_wrist_r)),
        "max_elev_wrist_l": float(np.max(elev_wrist_l)),
        "min_elbow_angle_r": float(np.min(angles_elbow_r)),
        "max_elbow_angle_r": float(np.max(angles_elbow_r)),
        "min_elbow_angle_l": float(np.min(angles_elbow_l)),
        "max_elbow_angle_l": float(np.max(angles_elbow_l)),
        "min_knee_angle_r": float(np.min(angles_knee_r)),
        "max_knee_angle_r": float(np.max(angles_knee_r)),
        "min_knee_angle_l": float(np.min(angles_knee_l)),
        "max_knee_angle_l": float(np.max(angles_knee_l)),
        "torso_pitch_lean": torso_pitch,
        "torso_roll_lean": torso_roll,
        "arm_activity_asymmetry": float(arm_asym),
        "leg_activity_asymmetry": float(leg_asym),
        "min_wrist_distance": min_wrist_d,
        "mean_wrist_distance": mean_wrist_d,
        "min_hand_distance": min_hand_d,
        "torso_length": torso_len,
        "max_arm_extension_r": float(np.max(arm_ext_r)),
        "max_arm_extension_l": float(np.max(arm_ext_l)),
        "max_leg_extension_r": float(np.max(leg_ext_r)),
        "max_leg_extension_l": float(np.max(leg_ext_l))
    }

    return features


def load_clip_from_csv(csv_path: str) -> np.ndarray:
    """
    Carga un archivo CSV grabado por el visualizador y lo convierte a un array (N_frames, 32, 3).
    Soporta formato con columnas etiquetadas (joint_0_x...) o formato tabular numérico directo.
    """
    df = pd.read_csv(csv_path)

    # Filtrar columnas de metadatos si existen
    meta_cols = [c for c in ["frame_idx", "timestamp", "timestamp_s", "subject_id", "action_id", "label"] if c in df.columns]
    data_df = df.drop(columns=meta_cols)

    arr = data_df.values.astype(np.float32)

    n_cols = arr.shape[1]
    if n_cols % 3 != 0:
        raise ValueError(f"El número de columnas de coordenadas ({n_cols}) no es múltiplo de 3.")

    n_joints = n_cols // 3
    n_frames = arr.shape[0]

    return arr.reshape((n_frames, n_joints, 3))
