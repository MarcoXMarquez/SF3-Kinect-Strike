"""
Street Fighter III: 3rd Strike - Calibrador de Poses Simplificado y Análisis de Patadas
Azure Kinect DK - Detección Sagital, Posturas Base y Análisis de Profundidad

Articulaciones simplificadas (13 clave):
- Cuello
- Hombros (izq / der)
- Codos (izq / der)
- Muñecas (izq / der)
- Pelvis (origen relativo)
- Caderas (izq / der)
- Rodillas (izq / der)
- Tobillos (izq / der)

Posturas Base Iniciales:
1. Perfil Izquierdo hacia el Kinect (Guardia Ortodoxa)
2. Perfil Derecho hacia el Kinect (Guardia Zurda)
3. De Frente hacia el Kinect (Frontal)

Análisis de Profundidad (Eje Z):
- Diferencia de profundidad (Delta Z) y elevación (Delta Y) de tobillos respecto a la pelvis
- Clasificación de patada adelantada/atrasada, ligera vs fuerte y empuje
"""

import sys
import os
import time
import math
import json
import numpy as np
import cv2

try:
    import pykinect_azure as pykinect
except ImportError:
    print("❌ Error: pykinect_azure no está instalado. Ejecuta: pip install pykinect_azure")
    sys.exit(1)


# -------------------------------------------------------------
# 1. ARTICULACIONES SIMPLIFICADAS Y HUESOS CLAVE
# -------------------------------------------------------------
# Mapeo a índices del Azure Kinect SDK (0 a 31)
SIMPLIFIED_JOINTS = {
    "pelvis": pykinect.K4ABT_JOINT_PELVIS,               # 0 (Raíz)
    "cuello": pykinect.K4ABT_JOINT_NECK,                 # 3
    "hombro_izq": pykinect.K4ABT_JOINT_SHOULDER_LEFT,    # 5
    "codo_izq": pykinect.K4ABT_JOINT_ELBOW_LEFT,        # 6
    "muneca_izq": pykinect.K4ABT_JOINT_WRIST_LEFT,      # 7
    "hombro_der": pykinect.K4ABT_JOINT_SHOULDER_RIGHT,   # 12
    "codo_der": pykinect.K4ABT_JOINT_ELBOW_RIGHT,       # 13
    "muneca_der": pykinect.K4ABT_JOINT_WRIST_RIGHT,     # 14
    "cadera_izq": pykinect.K4ABT_JOINT_HIP_LEFT,        # 18
    "rodilla_izq": pykinect.K4ABT_JOINT_KNEE_LEFT,      # 19
    "tobillo_izq": pykinect.K4ABT_JOINT_ANKLE_LEFT,     # 20
    "cadera_der": pykinect.K4ABT_JOINT_HIP_RIGHT,       # 22
    "rodilla_der": pykinect.K4ABT_JOINT_KNEE_RIGHT,     # 23
    "tobillo_der": pykinect.K4ABT_JOINT_ANKLE_RIGHT     # 24
}

# Conexiones óseas simplificadas (DERECHA = ROJO, IZQUIERDA = AZUL, TRONCO = CIAN/BLANCO)
# Formato de color OpenCV: BGR -> Azul=(255, 60, 0), Rojo=(0, 40, 255)
SIMPLIFIED_BONES = [
    # Tronco (Cian brillante)
    ("cuello", "pelvis", (0, 220, 255)),

    # Extremidad Superior Izquierda (AZUL)
    ("cuello", "hombro_izq", (255, 120, 0)),
    ("hombro_izq", "codo_izq", (255, 80, 0)),
    ("codo_izq", "muneca_izq", (255, 40, 0)),

    # Extremidad Superior Derecha (ROJO)
    ("cuello", "hombro_der", (0, 100, 255)),
    ("hombro_der", "codo_der", (0, 60, 255)),
    ("codo_der", "muneca_der", (0, 20, 255)),

    # Extremidad Inferior Izquierda (AZUL)
    ("pelvis", "cadera_izq", (255, 140, 30)),
    ("cadera_izq", "rodilla_izq", (255, 90, 0)),
    ("rodilla_izq", "tobillo_izq", (255, 40, 0)),

    # Extremidad Inferior Derecha (ROJO)
    ("pelvis", "cadera_der", (30, 80, 255)),
    ("cadera_der", "rodilla_der", (0, 50, 255)),
    ("rodilla_der", "tobillo_der", (0, 20, 255))
]

# -------------------------------------------------------------
# 2. POSTURAS BASE INICIALES
# -------------------------------------------------------------
BASE_STANCES = [
    {
        "id": "PERFIL_IZQUIERDO",
        "name": "Perfil Izquierdo",
        "lead": "Izquierda",
        "desc": "Perfil con hombro/pie izq. hacia el sensor (Ortodoxa)",
        "target_yaw_deg": 90,
        "yaw_range": (50, 130)
    },
    {
        "id": "PERFIL_DERECHO",
        "name": "Perfil Derecho",
        "lead": "Derecha",
        "desc": "Perfil con hombro/pie der. hacia el sensor (Zurda)",
        "target_yaw_deg": -90,
        "yaw_range": (-130, -50)
    },
    {
        "id": "DE_FRENTE",
        "name": "De Frente",
        "lead": "Frontal",
        "desc": "Cuerpo de frente con hombros paralelos a la camara",
        "target_yaw_deg": 0,
        "yaw_range": (-35, 35)
    }
]

# -------------------------------------------------------------
# 3. CATÁLOGO DE MOVIMIENTOS CON DIFERENCIACIÓN IZQ / DER
#    Mapeo completo de las 51 animaciones de combate de Ryu
#    (Excluye caminatas/dash y poses especiales/victoria/derrota)
# -------------------------------------------------------------
MOVEMENTS_CATALOG = [
    # =========================================================
    # 1. PUÑOS DE PIE (9 animaciones)
    # =========================================================
    {
        "id": "light_punch",
        "title": "Light Punch (Jab)",
        "short": "Light Punch (LP)",
        "desc": "Jab directo y veloz con el puño adelantado.",
        "side": "IZQUIERDA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO IZQ",
        "icon": "LP-L"
    },
    {
        "id": "light_punch_close",
        "title": "Light Punch Close (Jab Corto)",
        "short": "LP Cercano",
        "desc": "Jab corto y compacto a corta distancia.",
        "side": "IZQUIERDA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO IZQ",
        "icon": "LPC-L"
    },
    {
        "id": "medium_punch",
        "title": "Medium Punch (Straight MP)",
        "short": "Medium Punch (MP)",
        "desc": "Golpe medio extendido al plexo solar.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "MP-R"
    },
    {
        "id": "medium_punch_close",
        "title": "Medium Punch Close (Gancho Corto)",
        "short": "MP Cercano",
        "desc": "Gancho medio ascendente al cuerpo a corta distancia.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "MPC-R"
    },
    {
        "id": "forward_medium_punch",
        "title": "Fwd Medium Punch (Collarbone Breaker)",
        "short": "Fwd MP (Clavícula)",
        "desc": "Golpe descendente con paso al frente rompe guardias.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "FMP-R"
    },
    {
        "id": "heavy_punch",
        "title": "Heavy Punch (Cross Fuerte)",
        "short": "Heavy Punch (HP)",
        "desc": "Puñetazo cruzado de máximo poder con torsión de torso.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "HP-R"
    },
    {
        "id": "heavy_punch_close",
        "title": "Heavy Punch Close (Uppercut)",
        "short": "HP Cercano (Uppercut)",
        "desc": "Uppercut vertical potente a corta distancia.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "HPC-R"
    },
    {
        "id": "forward_heavy_punch",
        "title": "Forward Heavy Punch (Solar Plexus Strike)",
        "short": "Fwd HP (Plexo)",
        "desc": "Avance con doble impacto potente al plexo solar.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "FHP-R"
    },
    {
        "id": "straight",
        "title": "Straight Punch",
        "short": "Straight Punch",
        "desc": "Puño directo sostenido a media distancia.",
        "side": "DERECHA",
        "category": "PUÑOS PIE",
        "limb": "BRAZO DER",
        "icon": "ST-R"
    },

    # =========================================================
    # 2. PATADAS DE PIE (4 animaciones)
    # =========================================================
    {
        "id": "light_kick",
        "title": "Light Kick (Patada Ligera Pie)",
        "short": "Light Kick (LK)",
        "desc": "Patada rápida baja con la pierna delantera.",
        "side": "IZQUIERDA",
        "category": "PATADAS PIE",
        "limb": "PIERNA IZQ",
        "icon": "LK-L"
    },
    {
        "id": "medium_kick",
        "title": "Medium Kick (Patada Media Pie)",
        "short": "Medium Kick (MK)",
        "desc": "Patada lateral media a la zona media del rival.",
        "side": "DERECHA",
        "category": "PATADAS PIE",
        "limb": "PIERNA DER",
        "icon": "MK-R"
    },
    {
        "id": "medium_kick_close",
        "title": "Medium Kick Close (Rodillazo)",
        "short": "MK Cercano (Rodilla)",
        "desc": "Elevación explosiva de rodilla a corta distancia.",
        "side": "DERECHA",
        "category": "PATADAS PIE",
        "limb": "PIERNA DER",
        "icon": "MKC-R"
    },
    {
        "id": "heavy_kick",
        "title": "Heavy Kick (Patada Fuerte Circular)",
        "short": "Heavy Kick (HK)",
        "desc": "Patada alta circular de máximo alcance e impacto.",
        "side": "DERECHA",
        "category": "PATADAS PIE",
        "limb": "PIERNA DER",
        "icon": "HK-R"
    },

    # =========================================================
    # 3. ATAQUES Y ESTADOS AGACHADO (8 animaciones)
    # =========================================================
    {
        "id": "crouch_idle",
        "title": "Crouch Idle (Guardia Agachado)",
        "short": "Guardia Agachado",
        "desc": "Postura defensiva baja con flexión de ambas rodillas.",
        "side": "AMBOS",
        "category": "AGACHADO",
        "limb": "AMBAS PIERNAS",
        "icon": "CR-IDL"
    },
    {
        "id": "crouch_down",
        "title": "Crouch Down (Transición Agacharse)",
        "short": "Bajar Agachado",
        "desc": "Descenso activo del centro de gravedad.",
        "side": "AMBOS",
        "category": "AGACHADO",
        "limb": "AMBAS PIERNAS",
        "icon": "CR-DWN"
    },
    {
        "id": "crouch_light_punch",
        "title": "Crouch Light Punch (Jab Agachado)",
        "short": "Crouch LP",
        "desc": "Puñetazo bajo y veloz desde posición agachada.",
        "side": "IZQUIERDA",
        "category": "AGACHADO",
        "limb": "BRAZO IZQ",
        "icon": "CLP-L"
    },
    {
        "id": "crouch_medium_punch",
        "title": "Crouch Medium Punch (Puño Medio Agachado)",
        "short": "Crouch MP",
        "desc": "Puño medio horizontal al torso desde posición baja.",
        "side": "DERECHA",
        "category": "AGACHADO",
        "limb": "BRAZO DER",
        "icon": "CMP-R"
    },
    {
        "id": "crouch_heavy_punch",
        "title": "Crouch Heavy Punch (Gancho Alto Agachado)",
        "short": "Crouch HP",
        "desc": "Uppercut ascendente anti-aéreo desde posición agachada.",
        "side": "DERECHA",
        "category": "AGACHADO",
        "limb": "BRAZO DER",
        "icon": "CHP-R"
    },
    {
        "id": "crouch_light_kick",
        "title": "Crouch Light Kick (Patada Ligera Agachado)",
        "short": "Crouch LK",
        "desc": "Punta de pie rápida a los tobillos del rival.",
        "side": "IZQUIERDA",
        "category": "AGACHADO",
        "limb": "PIERNA IZQ",
        "icon": "CLK-L"
    },
    {
        "id": "crouch_medium_kick",
        "title": "Crouch Medium Kick (Barrida Media)",
        "short": "Crouch MK",
        "desc": "Patada baja de gran alcance para control de espacio.",
        "side": "DERECHA",
        "category": "AGACHADO",
        "limb": "PIERNA DER",
        "icon": "CMK-R"
    },
    {
        "id": "crouch_heavy_kick",
        "title": "Crouch Heavy Kick (Barrida Fuerte / Sweep)",
        "short": "Crouch HK (Barrida)",
        "desc": "Barrida giratoria al ras del suelo que derriba al oponente.",
        "side": "DERECHA",
        "category": "AGACHADO",
        "limb": "PIERNA DER",
        "icon": "CHK-R"
    },

    # =========================================================
    # 4. MOVIMIENTOS AÉREOS (11 animaciones)
    # =========================================================
    {
        "id": "jump_neutral",
        "title": "Jump Neutral (Salto Vertical)",
        "short": "Salto Neutral",
        "desc": "Elevación vertical despegando ambos pies del suelo.",
        "side": "AMBOS",
        "category": "AÉREO",
        "limb": "AMBAS PIERNAS",
        "icon": "JP-NEU"
    },
    {
        "id": "jump_forward",
        "title": "Jump Forward (Salto Adelante)",
        "short": "Salto Adelante",
        "desc": "Salto con traslación e inercia hacia adelante.",
        "side": "AMBOS",
        "category": "AÉREO",
        "limb": "AMBAS PIERNAS",
        "icon": "JP-FWD"
    },
    {
        "id": "jump_backward",
        "title": "Jump Backward (Salto Atrás)",
        "short": "Salto Atrás",
        "desc": "Salto defensivo con despegue hacia atrás.",
        "side": "AMBOS",
        "category": "AÉREO",
        "limb": "AMBAS PIERNAS",
        "icon": "JP-BCK"
    },
    {
        "id": "jump_light_punch",
        "title": "Jump Light Punch (Aéreo LP)",
        "short": "Jump LP",
        "desc": "Puño ligero descendente en el aire.",
        "side": "IZQUIERDA",
        "category": "AÉREO",
        "limb": "BRAZO IZQ",
        "icon": "JLP-L"
    },
    {
        "id": "jump_medium_punch",
        "title": "Jump Medium Punch (Aéreo MP)",
        "short": "Jump MP",
        "desc": "Puñetazo horizontal en trayectoria aérea.",
        "side": "DERECHA",
        "category": "AÉREO",
        "limb": "BRAZO DER",
        "icon": "JMP-R"
    },
    {
        "id": "jump_forward_medium_punch",
        "title": "Jump Fwd Medium Punch (Aéreo Fwd MP)",
        "short": "Jump Fwd MP",
        "desc": "Puño medio proyectado en salto diagonal hacia adelante.",
        "side": "DERECHA",
        "category": "AÉREO",
        "limb": "BRAZO DER",
        "icon": "JFMP-R"
    },
    {
        "id": "jump_heavy_punch",
        "title": "Jump Heavy Punch (Aéreo HP)",
        "short": "Jump HP",
        "desc": "Martillazo descendente de puño de gran impacto aéreo.",
        "side": "DERECHA",
        "category": "AÉREO",
        "limb": "BRAZO DER",
        "icon": "JHP-R"
    },
    {
        "id": "jump_light_kick",
        "title": "Jump Light Kick (Aéreo LK)",
        "short": "Jump LK",
        "desc": "Patada rápida estirada en salto.",
        "side": "IZQUIERDA",
        "category": "AÉREO",
        "limb": "PIERNA IZQ",
        "icon": "JLK-L"
    },
    {
        "id": "jump_medium_kick",
        "title": "Jump Medium Kick (Aéreo MK Crossup)",
        "short": "Jump MK (Crossup)",
        "desc": "Patada aérea abierta con pierna flexionada para crossup.",
        "side": "DERECHA",
        "category": "AÉREO",
        "limb": "PIERNA DER",
        "icon": "JMK-R"
    },
    {
        "id": "jump_forward_medium_kick",
        "title": "Jump Fwd Medium Kick (Aéreo Fwd MK)",
        "short": "Jump Fwd MK",
        "desc": "Patada media extendida en salto diagonal ofensivo.",
        "side": "DERECHA",
        "category": "AÉREO",
        "limb": "PIERNA DER",
        "icon": "JFMK-R"
    },
    {
        "id": "jump_heavy_kick",
        "title": "Jump Heavy Kick (Aéreo HK)",
        "short": "Jump HK",
        "desc": "Patada fuerte descendente de máximo rango y daño aéreo.",
        "side": "DERECHA",
        "category": "AÉREO",
        "limb": "PIERNA DER",
        "icon": "JHK-R"
    },

    # =========================================================
    # 5. MOVIMIENTOS ESPECIALES Y SÚPERS (8 animaciones)
    # =========================================================
    {
        "id": "fireball",
        "title": "Hadouken (Fireball)",
        "short": "Hadouken",
        "desc": "Empuje frontal con ambas palmas juntas liberando energía.",
        "side": "AMBOS",
        "category": "ESPECIALES",
        "limb": "AMBOS BRAZOS",
        "icon": "HDK"
    },
    {
        "id": "shoryuken",
        "title": "Shoryuken (Dragon Punch)",
        "short": "Shoryuken",
        "desc": "Gancho vertical ascendente con puño al cielo.",
        "side": "DERECHA",
        "category": "ESPECIALES",
        "limb": "BRAZO DER",
        "icon": "SRK"
    },
    {
        "id": "hurricane",
        "title": "Tatsumaki Senpukyaku (Hurricane Kick)",
        "short": "Tatsumaki",
        "desc": "Giro horizontal con pierna extendida en molinete.",
        "side": "DERECHA",
        "category": "ESPECIALES",
        "limb": "PIERNA DER",
        "icon": "TATSU"
    },
    {
        "id": "halfcircle_forward_kick",
        "title": "Jodan Sokutou Geri (Mule Kick)",
        "short": "Mule Kick (HCF K)",
        "desc": "Patada de empuje penetrante con avance lateral enérgico.",
        "side": "DERECHA",
        "category": "ESPECIALES",
        "limb": "PIERNA DER",
        "icon": "MULE"
    },
    {
        "id": "crow",
        "title": "Crow Hop Strike",
        "short": "Crow Hop",
        "desc": "Salto táctico corto con impacto de avance.",
        "side": "DERECHA",
        "category": "ESPECIALES",
        "limb": "BRAZO DER",
        "icon": "CROW"
    },
    {
        "id": "super_art_2",
        "title": "Super Art II: Shin Shoryuken",
        "short": "Shin Shoryuken (SA2)",
        "desc": "Combinación demoledora de doble gancho cinemático devastador.",
        "side": "DERECHA",
        "category": "ESPECIALES",
        "limb": "AMBOS BRAZOS",
        "icon": "SA2"
    },
    {
        "id": "denjin",
        "title": "Super Art III: Denjin Hadouken",
        "short": "Denjin Hadouken (SA3)",
        "desc": "Concentración eléctrica concentrada con palmas sostenidas.",
        "side": "AMBOS",
        "category": "ESPECIALES",
        "limb": "AMBOS BRAZOS",
        "icon": "DENJIN"
    },
    {
        "id": "taunt",
        "title": "Taunt (Burlarse / Ajuste de Cinta)",
        "short": "Taunt (Provocación)",
        "desc": "Ajuste de la cinta de la cabeza que incrementa el daño.",
        "side": "AMBOS",
        "category": "ESPECIALES",
        "limb": "AMBOS BRAZOS",
        "icon": "TNT"
    },

    # =========================================================
    # 6. DEFENSA, PARRY Y AGARRES (11 animaciones)
    # =========================================================
    {
        "id": "idle_stance",
        "title": "Idle Stance (Guardia de Combate)",
        "short": "Guardia Base (Idle)",
        "desc": "Postura clásica de combate con respiración continua y puños arriba.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "IDLE"
    },
    {
        "id": "block_standing",
        "title": "Block Standing (Bloqueo Medio)",
        "short": "Bloqueo Pie",
        "desc": "Brazos juntos y cruzados al frente protegiendo el pecho.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "BLK-M"
    },
    {
        "id": "block_crouching",
        "title": "Block Crouching (Bloqueo Bajo Agachado)",
        "short": "Bloqueo Agachado",
        "desc": "Bloqueo compacto con rodillas flexionadas cubriendo piernas.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "BLK-CR"
    },
    {
        "id": "block_high",
        "title": "Block High (Bloqueo Alto Cabeza)",
        "short": "Bloqueo Alto",
        "desc": "Antebrazos elevados cubriendo cabeza y rostro de ataques altos.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "BLK-HI"
    },
    {
        "id": "parry_standing",
        "title": "Parry Standing (Desvío de Pie)",
        "short": "Parry de Pie",
        "desc": "Empuje seco hacia adelante con antebrazo adelantado en el impacto.",
        "side": "IZQUIERDA",
        "category": "DEFENSA",
        "limb": "BRAZO IZQ",
        "icon": "PRY-ST"
    },
    {
        "id": "parry_crouching",
        "title": "Parry Crouching (Desvío Agachado)",
        "short": "Parry Agachado",
        "desc": "Desvío bajo hacia abajo y al frente desde postura agachada.",
        "side": "IZQUIERDA",
        "category": "DEFENSA",
        "limb": "BRAZO IZQ",
        "icon": "PRY-CR"
    },
    {
        "id": "throw_forward",
        "title": "Throw Forward (Agarre Frontal Seoi Nage)",
        "short": "Agarre Adelante",
        "desc": "Proyección por encima del hombro tomando al rival con ambas manos.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "THW-F"
    },
    {
        "id": "throw_backward",
        "title": "Throw Backward (Agarre Atrás Tomoe Nage)",
        "short": "Agarre Atrás",
        "desc": "Proyección hacia atrás dejándose caer y usando palanca de pierna.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "THW-B"
    },
    {
        "id": "throw_miss",
        "title": "Throw Whiff (Intento de Agarre Fallido)",
        "short": "Agarre Fallido",
        "desc": "Extensión de brazos hacia adelante intentando atrapar al rival.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "AMBOS BRAZOS",
        "icon": "THW-M"
    },
    {
        "id": "hit_standing",
        "title": "Hit Standing (Impacto Recibido de Pie)",
        "short": "Hit de Pie",
        "desc": "Retroceso del cuerpo al recibir un impacto de pie.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "TRONCO",
        "icon": "HIT-ST"
    },
    {
        "id": "hit_crouching",
        "title": "Hit Crouching (Impacto Recibido Agachado)",
        "short": "Hit Agachado",
        "desc": "Retroceso al recibir un impacto en posición agachada.",
        "side": "AMBOS",
        "category": "DEFENSA",
        "limb": "TRONCO",
        "icon": "HIT-CR"
    }
]

CATEGORIES = ["PUÑOS PIE", "PATADAS PIE", "AGACHADO", "AÉREO", "ESPECIALES", "DEFENSA"]


class InteractivePoseStudio:
    def __init__(self):
        self.selected_mov_idx = 0
        self.selected_stance_idx = 0  # 0: Perfil Izq, 1: Perfil Der, 2: De Frente
        self.selected_category_idx = 0  # 0: PUÑOS PIE, 1: PATADAS PIE, ...
        self.captured_poses = {}

        # Áreas clicables
        self.stance_btn_rects = []
        self.category_btn_rects = []
        self.mov_btn_rects = []
        self.capture_btn_rect = (0, 0, 0, 0)
        self.save_btn_rect = (0, 0, 0, 0)

        self.last_capture_message = ""
        self.flash_screen_until = 0
        self.request_capture = False

        # Datos para panel de revisión (Review de la pose capturada)
        self.last_review_img = None
        self.last_review_title = ""
        self.last_review_path = ""
        self.last_review_time = 0

    def get_filtered_movements(self):
        cat = CATEGORIES[self.selected_category_idx]
        if cat == "TODOS":
            return list(enumerate(MOVEMENTS_CATALOG))
        return [(i, m) for i, m in enumerate(MOVEMENTS_CATALOG) if m["category"] == cat]

    def on_mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # 1. Clic en botones de Postura Base
            for rect, idx in self.stance_btn_rects:
                bx, by, bw, bh = rect
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.selected_stance_idx = idx
                    print(f"🥋 Postura Base cambiada a: {BASE_STANCES[idx]['name']}")
                    return

            # 2. Clic en pestañas de Categoría
            for rect, idx in self.category_btn_rects:
                bx, by, bw, bh = rect
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.selected_category_idx = idx
                    filtered = self.get_filtered_movements()
                    if filtered and not any(i == self.selected_mov_idx for i, _ in filtered):
                        self.selected_mov_idx = filtered[0][0]
                    return

            # 3. Clic en botones de Movimiento
            for rect, idx in self.mov_btn_rects:
                bx, by, bw, bh = rect
                if bx <= x <= bx + bw and by <= y <= by + bh:
                    self.selected_mov_idx = idx
                    print(f"👉 Movimiento seleccionado: {MOVEMENTS_CATALOG[idx]['title']}")
                    return

            # 4. Clic en botón de Captura
            cx, cy, cw, ch = self.capture_btn_rect
            if cx <= x <= cx + cw and cy <= y <= cy + ch:
                self.request_capture = True
                return

            # 5. Clic en botón de Guardar JSON
            sx, sy, sw, sh = self.save_btn_rect
            if sx <= x <= sx + sw and sy <= y <= sy + sh:
                self.export_poses_to_json()
                return

    def save_current_pose(self, joints_xyz_m, torso_yaw, kick_analysis, limb_activity):
        mov = MOVEMENTS_CATALOG[self.selected_mov_idx]
        stance = BASE_STANCES[self.selected_stance_idx]
        pelvis_raw = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]

        JOINT_NAME_MAP = {
            "pelvis": "pelvis",
            "cuello": "neck",
            "hombro_izq": "left shoulder",
            "codo_izq": "left elbow",
            "muneca_izq": "left wrist",
            "hombro_der": "right shoulder",
            "codo_der": "right elbow",
            "muneca_der": "right wrist",
            "cadera_izq": "left hip",
            "rodilla_izq": "left knee",
            "tobillo_izq": "left ankle",
            "cadera_der": "right hip",
            "rodilla_der": "right knee",
            "tobillo_der": "right ankle"
        }

        joints_dict = {}
        for j_name, j_idx in SIMPLIFIED_JOINTS.items():
            rel = joints_xyz_m[j_idx] - pelvis_raw
            std_name = JOINT_NAME_MAP.get(j_name, j_name)
            joints_dict[std_name] = {
                "x": round(float(rel[0]), 4),
                "y": round(float(rel[1]), 4),
                "z": round(float(rel[2]), 4)
            }

        pose_data = {
            "id": mov["id"],
            "title": mov["title"],
            "side": mov["side"],
            "target_limb": mov["limb"],
            "base_stance_id": stance["id"],
            "base_stance_name": stance["name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "torso_yaw_deg": round(float(torso_yaw), 1),
            "pelvis_depth_m": round(float(pelvis_raw[2]), 3),
            "limb_activity": {
                "active_arm": limb_activity["active_arm"],
                "active_leg": limb_activity["active_leg"],
                "left_wrist_depth_dz": round(float(limb_activity["arm_izq_reach"]), 3),
                "right_wrist_depth_dz": round(float(limb_activity["arm_der_reach"]), 3),
                "left_ankle_depth_dz": round(float(limb_activity["leg_izq_reach"]), 3),
                "right_ankle_depth_dz": round(float(limb_activity["leg_der_reach"]), 3)
            },
            "kick_telemetry": {
                "left_ankle_delta_z": round(float(kick_analysis["la_dz"]), 3),
                "right_ankle_delta_z": round(float(kick_analysis["ra_dz"]), 3),
                "left_ankle_elevation": round(float(kick_analysis["la_elev"]), 3),
                "right_ankle_elevation": round(float(kick_analysis["ra_elev"]), 3),
                "detected_kick": kick_analysis["label"],
                "active_leg": kick_analysis["active_leg"]
            },
            "relative_joints_m": joints_dict
        }

        # ---------------------------------------------------------
        # GENERACIÓN Y GUARDADO DE LA IMAGEN DE REVISIÓN DEL ESQUELETO
        # (Vista Frontal X-Y y Perfil Sagital Z-Y con huesos Rojo/Azul)
        # ---------------------------------------------------------
        snap_w, snap_h = 560, 380
        snapshot = np.zeros((snap_h, snap_w, 3), dtype=np.uint8)
        snapshot[:] = (18, 22, 28)

        # Encabezado del snapshot
        cv2.rectangle(snapshot, (0, 0), (snap_w, 42), (32, 40, 52), -1)
        side_tag = f"[{mov['side']}]"
        cv2.putText(snapshot, f"REVIEW: {mov['title'].upper()} {side_tag}", (12, 26),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 200), 1, cv2.LINE_AA)
        cv2.putText(snapshot, f"Base: {stance['name']} | Yaw: {torso_yaw:.0f} deg", (12, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.32, (180, 190, 200), 1, cv2.LINE_AA)

        # Leyenda de color
        cv2.putText(snapshot, "[ROJO = DERECHO]", (snap_w - 240, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 40, 255), 1, cv2.LINE_AA)
        cv2.putText(snapshot, "[AZUL = IZQUIERDO]", (snap_w - 125, 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 100, 0), 1, cv2.LINE_AA)

        # Centros de las dos vistas en el snapshot
        snap_scale = 160.0
        snap_cy = 200
        snap_cx_f = 140
        snap_cx_s = 420

        # Línea divisoria
        cv2.line(snapshot, (280, 48), (280, snap_h - 10), (45, 52, 65), 1)

        # Vista Frontal
        snap_front_pts = {}
        for j_n, j_i in SIMPLIFIED_JOINTS.items():
            rx = (joints_xyz_m[j_i, 0] - pelvis_raw[0]) * snap_scale
            ry = (joints_xyz_m[j_i, 1] - pelvis_raw[1]) * snap_scale
            snap_front_pts[j_n] = np.array([snap_cx_f + rx, snap_cy + ry])

        draw_simplified_skeleton(snapshot, snap_front_pts)
        cv2.putText(snapshot, "FRONTAL (X-Y)", (snap_cx_f - 55, 66),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 200), 1, cv2.LINE_AA)

        # Vista Sagital
        snap_sag_pts = {}
        for j_n, j_i in SIMPLIFIED_JOINTS.items():
            rz = (joints_xyz_m[j_i, 2] - pelvis_raw[2]) * snap_scale
            ry = (joints_xyz_m[j_i, 1] - pelvis_raw[1]) * snap_scale
            snap_sag_pts[j_n] = np.array([snap_cx_s + rz, snap_cy + ry])

        draw_simplified_skeleton(snapshot, snap_sag_pts)
        cv2.putText(snapshot, "PERFIL (Z-Y)", (snap_cx_s - 50, 66),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 200, 255), 1, cv2.LINE_AA)

        # Borde exterior del snapshot
        cv2.rectangle(snapshot, (0, 0), (snap_w - 1, snap_h - 1), (0, 200, 255), 2)

        # Guardar archivo de imagen en disco para auditoría
        review_dir = os.path.join(os.path.dirname(__file__), "captured_pose_reviews")
        os.makedirs(review_dir, exist_ok=True)
        img_filename = f"{mov['id']}_{mov['side'].lower()}.png"
        img_path = os.path.join(review_dir, img_filename)
        cv2.imwrite(img_path, snapshot)

        # Guardar en memoria para mostrar al costado en la interfaz
        self.last_review_img = snapshot
        self.last_review_title = f"{mov['title']} [{mov['side']}]"
        self.last_review_path = img_path
        self.last_review_time = time.time()
        pose_data["review_image_path"] = img_path

        self.captured_poses[mov["id"]] = pose_data
        self.last_capture_message = f"¡Pose '{mov['title']}' ({mov['side']}) guardada! Imagen: {img_filename}"
        self.flash_screen_until = time.time() + 0.8
        print(f"📸 ✅ Pose guardada: {mov['title']} | Lado: {mov['side']} | Base: {stance['name']}")
        print(f"🖼️ Imagen de review guardada en: {img_path}")

        self.export_poses_to_json()

    def export_poses_to_json(self):
        output_paths = [
            os.path.join(os.path.dirname(__file__), "calibrated_poses.json"),
            os.path.join(os.path.dirname(__file__), "..", "Assets", "StreetFighter3_ThirdStrike", "Scenes", "calibrated_poses.json")
        ]

        data = {
            "game": "Street Fighter III: 3rd Strike",
            "module": "Azure Kinect Somatosensory Classifier (Left/Right Calibrated Poses)",
            "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
            "poses_count": len(self.captured_poses),
            "poses": self.captured_poses
        }

        for path in output_paths:
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception as ex:
                print(f"⚠️ Error al guardar en {path}: {ex}")

        print("💾 [JSON] Poses con diferenciación Izq/Der guardadas exitosamente.")


def analyze_limb_activity(joints_xyz_m):
    """
    Determina con precisión qué extremidad (izquierda o derecha) está ejecutando
    la acción comparando profundidad (Z), extensión y altura (Y).
    """
    pelvis = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
    m_izq = joints_xyz_m[SIMPLIFIED_JOINTS["muneca_izq"]]
    m_der = joints_xyz_m[SIMPLIFIED_JOINTS["muneca_der"]]
    t_izq = joints_xyz_m[SIMPLIFIED_JOINTS["tobillo_izq"]]
    t_der = joints_xyz_m[SIMPLIFIED_JOINTS["tobillo_der"]]

    # Proyección hacia adelante en profundidad (menor Z = más adelante)
    arm_izq_reach = pelvis[2] - m_izq[2]
    arm_der_reach = pelvis[2] - m_der[2]
    leg_izq_reach = pelvis[2] - t_izq[2]
    leg_der_reach = pelvis[2] - t_der[2]

    # Elevación respecto a la pelvis (menor Y en Kinect = más alto)
    arm_izq_elev = pelvis[1] - m_izq[1]
    arm_der_elev = pelvis[1] - m_der[1]
    leg_izq_elev = pelvis[1] - t_izq[1]
    leg_der_elev = pelvis[1] - t_der[1]

    # Detección de brazo activo
    active_arm = "NEUTRO"
    if (arm_izq_reach > arm_der_reach + 0.12) or (arm_izq_elev > arm_der_elev + 0.20):
        active_arm = "IZQUIERDA"
    elif (arm_der_reach > arm_izq_reach + 0.12) or (arm_der_elev > arm_izq_elev + 0.20):
        active_arm = "DERECHA"

    # Detección de pierna activa
    active_leg = "NEUTRO"
    score_leg_izq = leg_izq_reach * 0.55 + leg_izq_elev * 0.45
    score_leg_der = leg_der_reach * 0.55 + leg_der_elev * 0.45

    if score_leg_izq > score_leg_der + 0.14:
        active_leg = "IZQUIERDA"
    elif score_leg_der > score_leg_izq + 0.14:
        active_leg = "DERECHA"

    return {
        "arm_izq_reach": arm_izq_reach,
        "arm_der_reach": arm_der_reach,
        "leg_izq_reach": leg_izq_reach,
        "leg_der_reach": leg_der_reach,
        "arm_izq_elev": arm_izq_elev,
        "arm_der_elev": arm_der_elev,
        "leg_izq_elev": leg_izq_elev,
        "leg_der_elev": leg_der_elev,
        "active_arm": active_arm,
        "active_leg": active_leg
    }


def analyze_kick_depth_and_elevation(joints_xyz_m, stance_id):
    """
    Analiza la profundidad (Eje Z) y la elevación (Eje Y) de ambos tobillos
    para clasificar y diferenciar patadas de forma precisa.
    """
    pelvis = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
    cad_l = joints_xyz_m[SIMPLIFIED_JOINTS["cadera_izq"]]
    cad_r = joints_xyz_m[SIMPLIFIED_JOINTS["cadera_der"]]
    tob_l = joints_xyz_m[SIMPLIFIED_JOINTS["tobillo_izq"]]
    tob_r = joints_xyz_m[SIMPLIFIED_JOINTS["tobillo_der"]]

    # En Kinect, menor Z = más cerca de la cámara (hacia adelante en profundidad)
    # delta_z > 0 significa que el pie se adelantó respecto a la cadera/pelvis
    la_dz = pelvis[2] - tob_l[2]
    ra_dz = pelvis[2] - tob_r[2]

    # En Kinect, menor Y = más alto (elevación positiva = pie subiendo hacia la cadera)
    la_elev = pelvis[1] - tob_l[1]
    ra_elev = pelvis[1] - tob_r[1]

    # Determinar qué pierna tiene mayor actividad
    left_activity = la_dz * 0.6 + la_elev * 0.4
    right_activity = ra_dz * 0.6 + ra_elev * 0.4

    active_leg = "Ninguna"
    label = "En Apoyo / Guardia"
    kick_type = "NONE"

    if max(la_elev, ra_elev) > 0.15 or max(la_dz, ra_dz) > 0.22:
        if left_activity > right_activity:
            active_leg = "Pierna Izquierda"
            active_dz = la_dz
            active_elev = la_elev
        else:
            active_leg = "Pierna Derecha"
            active_dz = ra_dz
            active_elev = ra_elev

        if active_elev > 0.40 and active_dz > 0.28:
            label = f"⚡ PATADA FUERTE / ALTA (HK) [{active_leg}]"
            kick_type = "HK"
        elif active_dz > 0.35 and active_elev > 0.20:
            label = f"⚡ PATADA FRONTAL EMPUJE (Push Kick) [{active_leg}]"
            kick_type = "PUSH"
        elif active_elev > 0.18 or active_dz > 0.20:
            label = f"⚡ PATADA LIGERA (LK) [{active_leg}]"
            kick_type = "LK"

    return {
        "la_dz": la_dz,
        "ra_dz": ra_dz,
        "la_elev": la_elev,
        "ra_elev": ra_elev,
        "active_leg": active_leg,
        "label": label,
        "kick_type": kick_type
    }


def draw_simplified_skeleton(canvas, joint_screen_pts, color_override=None):
    """
    Dibuja únicamente los 13 huesos y nodos simplificados con colores limpios.
    """
    # 1. Dibujar conexiones de huesos
    for start_name, end_name, b_color in SIMPLIFIED_BONES:
        if start_name in joint_screen_pts and end_name in joint_screen_pts:
            pt1 = tuple(joint_screen_pts[start_name].astype(int))
            pt2 = tuple(joint_screen_pts[end_name].astype(int))
            col = color_override if color_override else b_color
            cv2.line(canvas, pt1, pt2, col, 3, cv2.LINE_AA)

    # 2. Dibujar nodos de articulaciones (DERECHO = ROJO, IZQUIERDO = AZUL, CENTRO = CIAN)
    for name, pt in joint_screen_pts.items():
        c = tuple(pt.astype(int))
        if "_der" in name:
            cv2.circle(canvas, c, 6, (0, 40, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 8, (255, 255, 255), 1, cv2.LINE_AA)
        elif "_izq" in name:
            cv2.circle(canvas, c, 6, (255, 60, 0), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 8, (255, 255, 255), 1, cv2.LINE_AA)
        elif "cuello" in name or "pelvis" in name:
            cv2.circle(canvas, c, 7, (0, 240, 255), -1, cv2.LINE_AA)
            cv2.circle(canvas, c, 9, (255, 255, 255), 1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, c, 5, (220, 220, 220), -1, cv2.LINE_AA)


def main():
    print("=" * 75)
    print("🥊 SF3 - CALIBRADOR SIMPLIFICADO CON ANÁLISIS DE PATADAS Y POSTURA BASE")
    print("=" * 75)
    print("1. Selecciona la POSTURA BASE inicial (Perfil Izq, Perfil Der o De Frente).")
    print("2. Selecciona el MOVIMIENTO en la lista de la izquierda.")
    print("3. Adopta la pose frente al sensor (el HUD te guiará en distancia y ángulo).")
    print("4. Presiona [ESPACIO] o haz clic en [📸 CAPTURAR POSE].")
    print("=" * 75)

    k4a_path = r"C:\Program Files\Azure Kinect SDK v1.4.1\sdk\windows-desktop\amd64\release\bin\k4a.dll"
    k4abt_path = r"C:\Program Files\Azure Kinect Body Tracking SDK\sdk\windows-desktop\amd64\release\bin\k4abt.dll"

    try:
        pykinect.initialize_libraries(
            module_k4a_path=k4a_path,
            module_k4abt_path=k4abt_path,
            track_body=True
        )
    except Exception as ex:
        print(f"❌ Error al cargar librerías: {ex}")
        return

    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_NFOV_UNBINNED
    device_config.camera_fps = pykinect.K4A_FRAMES_PER_SECOND_30

    try:
        device = pykinect.start_device(config=device_config)
    except Exception as ex:
        print(f"❌ Error al abrir sensor: {ex}")
        return

    try:
        body_tracker = pykinect.start_body_tracker(model_type=pykinect.K4ABT_LITE_MODEL)
    except Exception:
        body_tracker = pykinect.start_body_tracker(model_type=pykinect.K4ABT_DEFAULT_MODEL)

    studio = InteractivePoseStudio()

    WINDOW_NAME = "SF3 - Calibrador Simplificado (Posturas Base + Patadas 3D)"
    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, studio.on_mouse_click)

    WIDTH = 1380
    HEIGHT = 800
    MENU_W = 350

    while True:
        capture = device.update()
        body_frame = body_tracker.update()

        canvas = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        canvas[:] = (20, 22, 28)

        # Destello verde al capturar
        if time.time() < studio.flash_screen_until:
            canvas[:] = (25, 55, 35)

        # -------------------------------------------------------------
        # PANEL IZQUIERDO: POSTURAS BASE + MENÚ DE MOVIMIENTOS
        # -------------------------------------------------------------
        cv2.rectangle(canvas, (0, 0), (MENU_W, HEIGHT), (26, 30, 38), -1)
        cv2.line(canvas, (MENU_W, 0), (MENU_W, HEIGHT), (55, 62, 78), 2)

        # --- SECCIÓN A: SELECTOR DE POSTURA BASE INICIAL ---
        cv2.putText(canvas, "POSTURA BASE INICIAL:", (14, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 200), 2, cv2.LINE_AA)

        studio.stance_btn_rects.clear()
        stance_h = 36
        stance_w = (MENU_W - 28) // 3
        for i, stance in enumerate(BASE_STANCES):
            bx = 14 + i * (stance_w + 4)
            by = 35
            rect = (bx, by, stance_w, stance_h)
            studio.stance_btn_rects.append((rect, i))

            is_sel = (i == studio.selected_stance_idx)
            bg_col = (70, 110, 160) if is_sel else (38, 44, 56)
            bdr_col = (0, 220, 255) if is_sel else (60, 68, 85)

            cv2.rectangle(canvas, (bx, by), (bx + stance_w, by + stance_h), bg_col, -1)
            cv2.rectangle(canvas, (bx, by), (bx + stance_w, by + stance_h), bdr_col, 2 if is_sel else 1)

            short_name = ["Perfil Izq", "Perfil Der", "De Frente"][i]
            cv2.putText(canvas, short_name, (bx + 8, by + 23),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255) if is_sel else (180, 190, 200), 1, cv2.LINE_AA)

        # --- SECCIÓN B: PESTAÑAS DE CATEGORÍA (2 FILAS DE 3 BOTONES) ---
        studio.category_btn_rects.clear()
        cat_y_start = 82
        cat_h = 24
        cols = 3
        cat_w = (MENU_W - 28) // cols

        for ci, cat_name in enumerate(CATEGORIES):
            col_i = ci % cols
            row_i = ci // cols
            cx_b = 14 + col_i * cat_w
            cy_b = cat_y_start + row_i * (cat_h + 3)
            c_rect = (cx_b, cy_b, cat_w - 3, cat_h)
            studio.category_btn_rects.append((c_rect, ci))

            is_cat_sel = (ci == studio.selected_category_idx)
            cat_bg = (55, 85, 120) if is_cat_sel else (32, 36, 46)
            cat_bdr = (0, 220, 255) if is_cat_sel else (50, 58, 70)

            cv2.rectangle(canvas, (cx_b, cy_b), (cx_b + cat_w - 3, cy_b + cat_h), cat_bg, -1)
            cv2.rectangle(canvas, (cx_b, cy_b), (cx_b + cat_w - 3, cy_b + cat_h), cat_bdr, 2 if is_cat_sel else 1)

            cv2.putText(canvas, cat_name, (cx_b + 4, cy_b + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.33, (255, 255, 255) if is_cat_sel else (170, 180, 190), 1, cv2.LINE_AA)

        # --- SECCIÓN C: LISTA DE MOVIMIENTOS FILTRADOS ---
        studio.mov_btn_rects.clear()
        filtered_movs = studio.get_filtered_movements()

        btn_y_start = 138
        max_visible = 11
        btn_h = 44 if len(filtered_movs) <= 8 else 38
        btn_spacing = 4

        for slot_idx, (real_idx, mov) in enumerate(filtered_movs[:max_visible]):
            by = btn_y_start + slot_idx * (btn_h + btn_spacing)
            rect = (12, by, MENU_W - 24, btn_h)
            studio.mov_btn_rects.append((rect, real_idx))

            is_selected = (real_idx == studio.selected_mov_idx)
            is_captured = (mov["id"] in studio.captured_poses)

            if is_selected:
                bg_color = (60, 95, 140)
                border_color = (0, 220, 255)
            elif is_captured:
                bg_color = (32, 52, 42)
                border_color = (0, 200, 100)
            else:
                bg_color = (36, 40, 52)
                border_color = (52, 60, 75)

            cv2.rectangle(canvas, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), bg_color, -1)
            cv2.rectangle(canvas, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), border_color, 2 if is_selected else 1)

            # Badge de Estado y Lado (IZQ / DER)
            badge_status = "[OK]" if is_captured else "[  ]"
            side_tag = f"[{mov['side'][:3]}]"
            side_col = (0, 240, 255) if mov["side"] == "IZQUIERDA" else ((0, 160, 255) if mov["side"] == "DERECHA" else (255, 120, 220))

            cv2.putText(canvas, badge_status, (rect[0] + 6, rect[1] + 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 255, 120) if is_captured else (140, 150, 160), 1, cv2.LINE_AA)
            cv2.putText(canvas, side_tag, (rect[0] + 42, rect[1] + 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, side_col, 1, cv2.LINE_AA)

            title_str = mov.get("short", mov["title"])
            cv2.putText(canvas, title_str, (rect[0] + 90, rect[1] + 19),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255) if is_selected else (200, 210, 220), 1, cv2.LINE_AA)

            if btn_h >= 40:
                cv2.putText(canvas, mov['desc'], (rect[0] + 8, rect[1] + 34),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.31, (140, 150, 165), 1, cv2.LINE_AA)

        # Botón Guardar JSON al pie
        save_btn_y = HEIGHT - 52
        studio.save_btn_rect = (14, save_btn_y, MENU_W - 28, 40)
        cv2.rectangle(canvas, (14, save_btn_y), (MENU_W - 14, save_btn_y + 40), (45, 65, 90), -1)
        cv2.rectangle(canvas, (14, save_btn_y), (MENU_W - 14, save_btn_y + 40), (0, 200, 255), 1)
        saved_count = len(studio.captured_poses)
        cv2.putText(canvas, f"💾 GUARDAR JSON ({saved_count}/{len(MOVEMENTS_CATALOG)} Poses)", (30, save_btn_y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # PANEL SUPERIOR DERECHO: INDICADOR DE POSTURA Y ORIENTACIÓN
        # -------------------------------------------------------------
        current_mov = MOVEMENTS_CATALOG[studio.selected_mov_idx]
        current_stance = BASE_STANCES[studio.selected_stance_idx]

        header_x = MENU_W + 15
        header_w = WIDTH - header_x - 15
        header_h = 100

        cv2.rectangle(canvas, (header_x, 10), (header_x + header_w, 10 + header_h), (28, 32, 42), -1)
        cv2.rectangle(canvas, (header_x, 10), (header_x + header_w, 10 + header_h), (0, 200, 255), 2)

        side_str = f"[{current_mov['side']}]" if current_mov['side'] != 'NEUTRO' else ''
        title_text = f"POSE: {current_mov['title'].upper()} {side_str}  |  BASE: {current_stance['name'].upper()}"
        cv2.putText(canvas, title_text, (header_x + 18, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        # -------------------------------------------------------------
        # LECTURA Y PROCESAMIENTO DEL ESQUELETO SIMPLIFICADO
        # -------------------------------------------------------------
        num_bodies = body_frame.get_num_bodies()

        if num_bodies > 0:
            body = body_frame.get_body(0)
            joints_data = body.numpy()
            joints_xyz_m = joints_data[:, :3] * 0.001

            pelvis_raw = joints_xyz_m[SIMPLIFIED_JOINTS["pelvis"]]
            sh_l = joints_xyz_m[SIMPLIFIED_JOINTS["hombro_izq"]]
            sh_r = joints_xyz_m[SIMPLIFIED_JOINTS["hombro_der"]]

            # Ángulo sagital de orientación del torso
            dx = sh_r[0] - sh_l[0]
            dz = sh_r[2] - sh_l[2]
            torso_yaw = math.degrees(math.atan2(dz, dx))

            # Verificación de alineación con la postura base seleccionada
            y_min, y_max = current_stance["yaw_range"]
            stance_ok = (y_min <= torso_yaw <= y_max)

            # Análisis cinemático de extremidades activas (Izquierda vs Derecha)
            limb_activity = analyze_limb_activity(joints_xyz_m)
            kick_info = analyze_kick_depth_and_elevation(joints_xyz_m, current_stance["id"])

            # Verificación de correspondencia de lado (Izquierdo vs Derecho)
            side_mismatch = False
            side_feedback = ""
            req_side = current_mov["side"]

            if req_side in ("IZQUIERDA", "DERECHA"):
                if current_mov["category"] == "PUÑOS":
                    act = limb_activity["active_arm"]
                    if act != "NEUTRO" and act != req_side:
                        side_mismatch = True
                        side_feedback = f"⚠️ ATENCIÓN: Brazo {act} activo (Debes usar el brazo {req_side})"
                elif current_mov["category"] == "PATADAS":
                    act = limb_activity["active_leg"]
                    if act != "NEUTRO" and act != req_side:
                        side_mismatch = True
                        side_feedback = f"⚠️ ATENCIÓN: Pierna {act} activa (Debes usar la pierna {req_side})"

            # Telemetría de distancia estilo app de banco
            z_dist = pelvis_raw[2]
            x_pos = pelvis_raw[0]

            if z_dist > 2.6:
                feed_text = f"⚠️ ACÉRCATE (Distancia: {z_dist:.2f}m - Objetivo: 2.0m - 2.4m)"
                feed_col = (0, 180, 255)
            elif z_dist < 1.7:
                feed_text = f"⚠️ ALÉJATE (Distancia: {z_dist:.2f}m - Objetivo: 2.0m - 2.4m)"
                feed_col = (0, 180, 255)
            elif not stance_ok:
                if current_stance["id"] == "PERFIL_IZQUIERDO":
                    feed_text = f"⚠️ GIRA: Coloca tu HOMBRO IZQUIERDO hacia la cámara (Yaw: {torso_yaw:.0f}°)"
                elif current_stance["id"] == "PERFIL_DERECHO":
                    feed_text = f"⚠️ GIRA: Coloca tu HOMBRO DERECHO hacia la cámara (Yaw: {torso_yaw:.0f}°)"
                else:
                    feed_text = f"⚠️ COLÓCATE DE FRENTE a la cámara (Yaw: {torso_yaw:.0f}°)"
                feed_col = (0, 220, 255)
            elif side_mismatch:
                feed_text = side_feedback
                feed_col = (0, 160, 255)
            else:
                feed_text = f"✅ POSTURA Y LADO CORRECTOS ({current_mov['side']} | {current_stance['name']} | Dist: {z_dist:.2f}m)"
                feed_col = (0, 255, 120)

            cv2.putText(canvas, feed_text, (header_x + 18, 66),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.58, feed_col, 2, cv2.LINE_AA)

            hud_action = (f"Brazo Activo: {limb_activity['active_arm']} (ΔZ: {limb_activity['arm_izq_reach']:+.2f}m / {limb_activity['arm_der_reach']:+.2f}m)  |  "
                          f"Pierna Activa: {limb_activity['active_leg']} (Elev: {limb_activity['leg_izq_elev']:+.2f}m / {limb_activity['leg_der_elev']:+.2f}m)")
            cv2.putText(canvas, hud_action, (header_x + 18, 93),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 220) if not side_mismatch else (0, 160, 255), 1, cv2.LINE_AA)

            # Captura de pose al presionar espacio o botón
            if studio.request_capture:
                studio.save_current_pose(joints_xyz_m, torso_yaw, kick_info, limb_activity)
                studio.request_capture = False

            # -------------------------------------------------------------
            # VISTAS DUALES CON ESQUELETO SIMPLIFICADO
            # -------------------------------------------------------------
            center_area_w = (WIDTH - MENU_W) // 2
            view_y = 120
            view_h = HEIGHT - 240
            mid_x = MENU_W + center_area_w

            # Línea divisoria central
            cv2.line(canvas, (mid_x, view_y), (mid_x, view_y + view_h), (45, 52, 65), 1)

            scale = 230.0
            cy = view_y + (view_h // 2)

            # 1. Panel Frontal (X-Y)
            cx_front = MENU_W + (center_area_w // 2)
            front_screen_pts = {}
            for j_name, j_idx in SIMPLIFIED_JOINTS.items():
                rel_x = (joints_xyz_m[j_idx, 0] - pelvis_raw[0]) * scale
                rel_y = (joints_xyz_m[j_idx, 1] - pelvis_raw[1]) * scale
                front_screen_pts[j_name] = np.array([cx_front + rel_x, cy + rel_y])

            draw_simplified_skeleton(canvas, front_screen_pts)
            cv2.putText(canvas, "VISTA FRONTAL (X-Y)", (cx_front - 85, view_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 255, 200), 1, cv2.LINE_AA)

            # 2. Panel Perfil Sagital / Profundidad (Z-Y)
            cx_sagittal = mid_x + (center_area_w // 2)
            sagittal_screen_pts = {}
            for j_name, j_idx in SIMPLIFIED_JOINTS.items():
                rel_z = (joints_xyz_m[j_idx, 2] - pelvis_raw[2]) * scale
                rel_y = (joints_xyz_m[j_idx, 1] - pelvis_raw[1]) * scale
                sagittal_screen_pts[j_name] = np.array([cx_sagittal + rel_z, cy + rel_y])

            draw_simplified_skeleton(canvas, sagittal_screen_pts)
            cv2.putText(canvas, "VISTA PERFIL / PROFUNDIDAD (Z-Y)", (cx_sagittal - 120, view_y + 24),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 200, 255), 1, cv2.LINE_AA)

            # -------------------------------------------------------------
            # TELEMETRÍA DE PROFUNDIDAD Y PATADAS (BARRA INFERIOR)
            # -------------------------------------------------------------
            telemetry_y = view_y + view_h + 10
            telemetry_h = 42
            cv2.rectangle(canvas, (header_x, telemetry_y), (header_x + header_w, telemetry_y + telemetry_h), (25, 30, 40), -1)
            cv2.rectangle(canvas, (header_x, telemetry_y), (header_x + header_w, telemetry_y + telemetry_h), (50, 60, 75), 1)

            t_str = (f"Tobillo Izq -> Profundidad ΔZ: {kick_info['la_dz']:+.3f}m | Elevación ΔY: {kick_info['la_elev']:+.3f}m    ///    "
                     f"Tobillo Der -> Profundidad ΔZ: {kick_info['ra_dz']:+.3f}m | Elevación ΔY: {kick_info['ra_elev']:+.3f}m")
            cv2.putText(canvas, t_str, (header_x + 15, telemetry_y + 26),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200, 220, 240), 1, cv2.LINE_AA)

        else:
            cv2.putText(canvas, "⚠️ ESPERANDO LUCHADOR FRENTE AL AZURE KINECT...", (header_x + 40, 65),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (0, 160, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, "Párate a ~2.2 metros para calibrar el esqueleto simplificado.", (header_x + 40, 92),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.46, (160, 170, 180), 1, cv2.LINE_AA)

        # -------------------------------------------------------------
        # BOTÓN GRANDE DE CAPTURA [ESPACIO]
        # -------------------------------------------------------------
        btn_cap_w = 480
        btn_cap_h = 48
        btn_cap_x = MENU_W + ((WIDTH - MENU_W - btn_cap_w) // 2)
        btn_cap_y = HEIGHT - 58

        studio.capture_btn_rect = (btn_cap_x, btn_cap_y, btn_cap_w, btn_cap_h)
        is_captured_cur = current_mov["id"] in studio.captured_poses
        cap_bg = (0, 150, 75) if is_captured_cur else (0, 120, 200)

        cv2.rectangle(canvas, (btn_cap_x, btn_cap_y), (btn_cap_x + btn_cap_w, btn_cap_y + btn_cap_h), cap_bg, -1)
        cv2.rectangle(canvas, (btn_cap_x, btn_cap_y), (btn_cap_x + btn_cap_w, btn_cap_y + btn_cap_h), (255, 255, 255), 2)

        cap_title = "📸 CAPTURAR POSE (ESPACIO)" if not is_captured_cur else "🔄 RE-CAPTURAR POSE (ESPACIO)"
        cv2.putText(canvas, cap_title, (btn_cap_x + 65, btn_cap_y + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 255, 255), 2, cv2.LINE_AA)

        # -------------------------------------------------------------
        # PANEL DE REVISIÓN AL COSTADO (REVIEW DE LA POSE CAPTURADA)
        # -------------------------------------------------------------
        if studio.last_review_img is not None:
            # Mostrar tarjeta flotante de revisión en el sector derecho
            rev_w = 330
            rev_h = 224
            rev_x = WIDTH - rev_w - 20
            rev_y = 125

            # Fondo con sombra y borde cian
            cv2.rectangle(canvas, (rev_x - 3, rev_y - 28), (rev_x + rev_w + 3, rev_y + rev_h + 3), (12, 16, 22), -1)
            cv2.rectangle(canvas, (rev_x - 3, rev_y - 28), (rev_x + rev_w + 3, rev_y + rev_h + 3), (0, 200, 255), 2)

            # Título de revisión
            cv2.rectangle(canvas, (rev_x - 3, rev_y - 28), (rev_x + rev_w + 3, rev_y - 2), (32, 45, 62), -1)
            cv2.putText(canvas, "🔍 REVIEW POSE GUARDADA", (rev_x + 8, rev_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 200), 1, cv2.LINE_AA)

            # Redimensionar e incrustar la imagen del snapshot
            resized_snap = cv2.resize(studio.last_review_img, (rev_w, rev_h))
            canvas[rev_y:rev_y + rev_h, rev_x:rev_x + rev_w] = resized_snap

            # Leyenda de ayuda
            cv2.putText(canvas, studio.last_review_title, (rev_x + 6, rev_y + rev_h - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        if studio.last_capture_message:
            cv2.putText(canvas, studio.last_capture_message, (header_x + 15, HEIGHT - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 120), 1, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # ESC o 'q'
            break
        elif key == ord(' '):  # Espacio: capturar
            studio.request_capture = True
        elif key == ord('1'):  # Atajo postura base 1
            studio.selected_stance_idx = 0
        elif key == ord('2'):  # Atajo postura base 2
            studio.selected_stance_idx = 1
        elif key == ord('3'):  # Atajo postura base 3
            studio.selected_stance_idx = 2
        elif key == 9:  # Tecla TAB: cambiar de categoría
            studio.selected_category_idx = (studio.selected_category_idx + 1) % len(CATEGORIES)
            filtered = studio.get_filtered_movements()
            if filtered and not any(i == studio.selected_mov_idx for i, _ in filtered):
                studio.selected_mov_idx = filtered[0][0]
        elif key == ord('n') or key == ord('j'):
            filtered = studio.get_filtered_movements()
            if filtered:
                curr_pos = next((pos for pos, (r_idx, _) in enumerate(filtered) if r_idx == studio.selected_mov_idx), 0)
                next_pos = (curr_pos + 1) % len(filtered)
                studio.selected_mov_idx = filtered[next_pos][0]
        elif key == ord('b') or key == ord('k'):
            filtered = studio.get_filtered_movements()
            if filtered:
                curr_pos = next((pos for pos, (r_idx, _) in enumerate(filtered) if r_idx == studio.selected_mov_idx), 0)
                prev_pos = (curr_pos - 1) % len(filtered)
                studio.selected_mov_idx = filtered[prev_pos][0]
        elif key == ord('s'):
            studio.export_poses_to_json()

    cv2.destroyAllWindows()
    print("👋 Calibrador simplificado cerrado.")


if __name__ == "__main__":
    main()

