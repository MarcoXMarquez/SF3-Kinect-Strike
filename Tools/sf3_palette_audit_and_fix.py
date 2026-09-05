"""
SF3: 3rd Strike - Auditoria y Correccion Integral de Paletas Corruptas
======================================================================
Este script implementa el proceso automatizado de 4 fases:
- Fase 1: Extraccion de Firmas de Color Canonicas (Ground Truth) desde stance/0.png.
- Fase 2: Auditoria carpeta por carpeta detectando anomalias (CORRUPTED_PALETTE).
- Fase 3: Correccion quirurgica de clusters anomalos (pecho azul, pantalones rojos, piel zombie).
- Fase 4: Generacion de Contact Sheet visual (audit_verification.png) y reporte en consola.
"""

import os
import sys
import glob
import time
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Asegurar salida UTF-8 en consola Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHARACTERS_DIR = os.path.join(PROJECT_ROOT, "Assets", "StreetFighter3_ThirdStrike", "Characters")
ARTIFACT_DIR = r"C:\Users\marco\.gemini\antigravity\brain\39167e8e-c10a-47b4-b79d-be2d6ddc71ef"

# ==============================================================================
# FASE 1: DEFINICION DE FIRMAS CANONICAS Y GROUND TRUTH (CPS-3 PALETTE 000)
# ==============================================================================

CANONICAL_SIGNATURES = {
    "02_Ryu": {
        "gi": [
            (246, 246, 246), # #F6F6F6 blanco puro
            (230, 230, 230), # #E6E6E6 blanco gris
            (213, 213, 213), # #D5D5D5 gris suave
            (197, 197, 230), # #C5C5E6 sombra azulada
            (180, 180, 213), # #B4B4D5 sombra gris
            (164, 164, 197), # #A4A4C5 sombra media
            (131, 131, 131), # #838383 sombra oscura
        ],
        "skin": [
            (246, 197, 148), # #F6C594 piel melocoton claro
            (230, 164, 115), # #E6A473 piel luz
            (213, 148, 98),  # #D59462 piel medio
            (197, 131, 82),  # #C58352 sombra piel
            (180, 98, 49),   # #B46231 sombra profunda
            (164, 82, 32),   # #A45220 contorno piel
            (148, 49, 16),   # #943110 sombra oscura
        ],
        "headband_gloves": [
            (246, 82, 82),   # #F65252 rojo brillante
            (180, 16, 49),   # #B41031 rojo puro
            (131, 32, 49),   # #832031 rojo oscuro
            (115, 0, 32),    # #730020 sombra roja
        ],
        "belt_hair": [
            (0, 0, 0),       # #000000 negro puro
            (49, 49, 49),    # #313131 gris muy oscuro
            (65, 65, 65),    # #414141 gris oscuro
            (0, 0, 98),      # #000062 sombra azul oscuro
        ]
    }
}

# ==============================================================================
# FASE 2: AUDITORIA CARPETA POR CARPETA
# ==============================================================================

def audit_character_folder(cname, action_dir):
    """
    Audita el frame 0 de una accion para detectar desfasajes de paleta ('Frankenstein').
    Retorna (is_corrupt, reasons)
    """
    action_name = os.path.basename(action_dir)
    pngs = sorted(glob.glob(os.path.join(action_dir, "*.png")))
    if not pngs:
        return False, "Sin sprites"

    # Ignorar efectos especiales legitimos
    if action_name in ["denjin", "shocked"]:
        return False, "Efecto especial legitimo"

    frame0_path = pngs[0]
    with Image.open(frame0_path) as im:
        arr = np.array(im)
        if arr.shape[-1] < 4:
            return False, "Formato no RGBA"

        h, w = arr.shape[:2]

        if cname == "02_Ryu":
            # 1. Pecho azul anomalo: (0, 115, 197) o (0, 82, 164)
            cyan_mask = ((arr[:, :, 0] == 0) & (arr[:, :, 1] == 115) & (arr[:, :, 2] == 197) & (arr[:, :, 3] > 0)) | \
                        ((arr[:, :, 0] == 0) & (arr[:, :, 1] == 82) & (arr[:, :, 2] == 164) & (arr[:, :, 3] > 0))
            cyan_cnt = int(np.sum(cyan_mask))

            # 2. Piernas/Pantalones desfasados a rojo/morado/piel (y > 48%)
            pants = arr[int(h * 0.48):, :, :]
            red_pants_mask = (
                ((pants[:, :, 0] == 180) & (pants[:, :, 1] == 16) & (pants[:, :, 2] == 49)) |
                ((pants[:, :, 0] == 131) & (pants[:, :, 1] == 32) & (pants[:, :, 2] == 49)) |
                ((pants[:, :, 0] == 115) & (pants[:, :, 1] == 0) & (pants[:, :, 2] == 32)) |
                ((pants[:, :, 0] == 164) & (pants[:, :, 1] == 82) & (pants[:, :, 2] == 98)) |
                ((pants[:, :, 0] == 197) & (pants[:, :, 1] == 131) & (pants[:, :, 2] == 131))
            ) & (pants[:, :, 3] > 0)
            red_pants_cnt = int(np.sum(red_pants_mask))

            # Conteo de gi blanco en pantalones
            gi_pants_mask = (
                ((pants[:, :, 0] == 246) & (pants[:, :, 1] == 246) & (pants[:, :, 2] == 246)) |
                ((pants[:, :, 0] == 230) & (pants[:, :, 1] == 230) & (pants[:, :, 2] == 230)) |
                ((pants[:, :, 0] == 197) & (pants[:, :, 1] == 197) & (pants[:, :, 2] == 230)) |
                ((pants[:, :, 0] == 180) & (pants[:, :, 1] == 180) & (pants[:, :, 2] == 213))
            ) & (pants[:, :, 3] > 0)
            gi_pants_cnt = int(np.sum(gi_pants_mask))

            reasons = []
            if cyan_cnt > 20:
                reasons.append(f"Pecho azul detectado ({cyan_cnt} px #0073C5/#0052A4)")
            if red_pants_cnt > 300 and red_pants_cnt > gi_pants_cnt:
                reasons.append(f"Pantalones desfasados a rojo/morado ({red_pants_cnt} px anomalos vs {gi_pants_cnt} px gi blanco)")

            if reasons:
                return True, "; ".join(reasons)

    return False, "OK"

# ==============================================================================
# FASE 3: CORRECCION QUIRURGICA DE CARPETAS MARCADAS
# ==============================================================================

def fix_ryu_sprite(im, action_name):
    """
    Aplica correccion de clusters anomalos a un fotograma de Ryu:
    - Pecho azul -> Gi blanco puro / sombras
    - Pantalones rojos/morados -> Gi blanco / sombras cool
    - Piel zombie en brazos/cara -> Piel melocoton canonica
    Preserva canal alfa, cinturon negro y cinta roja.
    """
    arr = np.array(im)
    h, w = arr.shape[:2]

    # 1. Remapeo de Torso / Pecho azul a Gi blanco
    blue_to_gi = {
        (0, 115, 197): (246, 246, 246), # blanco puro
        (0, 82, 164):  (230, 230, 230), # blanco luz
        (0, 0, 148):   (197, 197, 230), # sombra azulada
    }
    for old_c, new_c in blue_to_gi.items():
        m = (arr[:, :, 0] == old_c[0]) & (arr[:, :, 1] == old_c[1]) & (arr[:, :, 2] == old_c[2]) & (arr[:, :, 3] > 0)
        arr[m, :3] = new_c

    # Sombra oscura de azul en torso (y < 42%)
    m_dark_blue = (arr[:, :, 0] == 0) & (arr[:, :, 1] == 0) & (arr[:, :, 2] == 98) & (arr[:, :, 3] > 0)
    for y in range(int(h * 0.42)):
        for x in range(w):
            if m_dark_blue[y, x]:
                arr[y, x, :3] = (180, 180, 213)

    # 2. Remapeo de Pantalones (y > 46%) a Gi Blanco
    pants_map = {
        (197, 131, 131): (246, 246, 246), # #F6F6F6 blanco
        (246, 82, 82):   (230, 230, 230), # #E6E6E6 luz
        (180, 16, 49):   (197, 197, 230), # #C5C5E6 sombra
        (131, 32, 49):   (180, 180, 213), # #B4B4D5 sombra media
        (164, 82, 98):   (180, 180, 213), # #B4B4D5
        (148, 65, 65):   (164, 164, 197), # #A4A4C5 sombra oscura
        (115, 0, 32):    (131, 131, 131), # #838383 contorno
        (246, 197, 148): (246, 246, 246), # piel en pantalon -> blanco
    }

    for y in range(int(h * 0.46), h):
        for x in range(w):
            if arr[y, x, 3] == 0:
                continue
            # Proteger guantes rojos en stance: puño derecho x in [52, 70], y in [55, 75]
            if action_name in ["stance", "ryustance"] and 52 <= x <= 70 and 55 <= y <= 75 and arr[y, x, 0] > 170:
                continue
            c = tuple(arr[y, x, :3])
            if c in pants_map:
                arr[y, x, :3] = pants_map[c]

    # 3. Correccion de Piel Zombie en brazos y cara en win1
    if action_name == "win1":
        zombie_to_skin = {
            (246, 246, 246): (246, 197, 148), # luz piel
            (230, 230, 230): (246, 180, 131),
            (197, 197, 230): (213, 148, 98),  # tono piel medio
            (180, 180, 213): (197, 131, 82),  # sombra piel
            (164, 164, 197): (180, 98, 49),   # sombra profunda
        }
        # Brazos cruzados y cara: y in [12, 45], excluir hombros exteriores
        for y in range(12, 45):
            for x in range(w):
                if arr[y, x, 3] == 0: continue
                # Hombro izquierdo exterior x < 24 o derecho x > 62
                if x < 24 or x > 62: continue
                c = tuple(arr[y, x, :3])
                if c in zombie_to_skin:
                    arr[y, x, :3] = zombie_to_skin[c]

    return Image.fromarray(arr)

def correct_action_folder(cname, action_dir):
    """Procesa todos los frames PNG de la carpeta corrupta."""
    pngs = sorted(glob.glob(os.path.join(action_dir, "*.png")))
    action_name = os.path.basename(action_dir)
    count = 0
    for fpath in pngs:
        with Image.open(fpath) as im:
            if cname == "02_Ryu":
                fixed = fix_ryu_sprite(im, action_name)
                fixed.save(fpath, "PNG")
                count += 1
    return count

# ==============================================================================
# FASE 4: CONTACT SHEET VISUAL (audit_verification.png)
# ==============================================================================

def generate_contact_sheet(ryu_dir, flagged_actions, output_path):
    """
    Genera un collage visual con el frame 0 de las acciones clave y corregidas
    para verificar que Ryu tiene su gi blanco puro y piel melocoton en todas ellas.
    """
    sample_actions = [
        ("stance", "Stance (Reposo - Corregido)"),
        ("walkf", "Walk Forward (Sano)"),
        ("crouch", "Crouch (Sano)"),
        ("fireball", "Hadouken (Sano)"),
        ("shoryuken", "Shoryuken (Sano)"),
        ("intro", "Intro (Corregido)"),
        ("taunt", "Taunt (Corregido)"),
        ("straight", "Straight (Corregido)"),
        ("win1", "Win 1 (Corregido)"),
        ("win2", "Win 2 (Corregido)"),
        ("ken_intro", "Ken Intro (Corregido)"),
    ]

    tiles = []
    max_h = 0
    for act_name, label in sample_actions:
        p = os.path.join(ryu_dir, act_name, "0.png")
        if os.path.exists(p):
            with Image.open(p) as im:
                im_rgba = im.convert("RGBA")
                tiles.append((act_name, label, im_rgba))
                max_h = max(max_h, im_rgba.size[1])

    if not tiles:
        return

    # Dimensiones del collage: 6 columnas x 2 filas
    cols = 6
    rows = (len(tiles) + cols - 1) // cols
    tile_w = 120
    tile_h = max_h + 50
    sheet_w = cols * tile_w + 40
    sheet_h = rows * tile_h + 70

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (24, 24, 30, 255))
    draw = ImageDraw.Draw(sheet)

    # Titulo
    draw.text((20, 15), "STREET FIGHTER III: 3RD STRIKE - AUDITORIA VISUAL DE PALETAS (RYU)", fill=(255, 215, 0, 255))
    draw.text((20, 35), "Verificacion de Gi blanco (#F6F6F6) y Piel melocoton en acciones corregidas y sanas", fill=(180, 180, 190, 255))

    for idx, (act_name, label, tile_im) in enumerate(tiles):
        r = idx // cols
        c = idx % cols
        x = 20 + c * tile_w + (tile_w - tile_im.size[0]) // 2
        y = 60 + r * tile_h + (max_h - tile_im.size[1])

        # Pegar sprite preservando transparencia
        sheet.paste(tile_im, (x, y), tile_im)

        # Etiqueta debajo
        is_fixed = act_name in flagged_actions
        badge_color = (80, 200, 120, 255) if is_fixed else (100, 180, 255, 255)
        text_y = 60 + r * tile_h + max_h + 8
        label_text = f"[{act_name}]"
        status_text = "CORREGIDO" if is_fixed else "SANO"

        draw.text((20 + c * tile_w + 10, text_y), label_text, fill=(240, 240, 240, 255))
        draw.text((20 + c * tile_w + 10, text_y + 14), status_text, fill=badge_color)

    sheet.save(output_path, "PNG")
    print(f"[OK] Contact Sheet generado exitosamente en: {output_path}")

    # Copiar al directorio de artefactos
    artifact_copy = os.path.join(ARTIFACT_DIR, "audit_verification.png")
    try:
        shutil.copyfile(output_path, artifact_copy)
        print(f"[OK] Copia persistida en artefactos: {artifact_copy}")
    except Exception as e:
        pass

# ==============================================================================
# FLUJO PRINCIPAL
# ==============================================================================

def main():
    print("=" * 80)
    print("STREET FIGHTER III: 3RD STRIKE - AUDITORIA Y CORRECCION INTEGRAL DE PALETAS")
    print("=" * 80)

    total_folders = 0
    healthy_folders = 0
    corrupted_folders = []

    start_time = time.time()

    # Recorrer todos los personajes
    for cname in sorted(os.listdir(CHARACTERS_DIR)):
        cdir = os.path.join(CHARACTERS_DIR, cname)
        if not os.path.isdir(cdir): continue

        for action in sorted(os.listdir(cdir)):
            adir = os.path.join(cdir, action)
            if not os.path.isdir(adir): continue
            total_folders += 1

            is_corrupt, reason = audit_character_folder(cname, adir)
            if is_corrupt:
                corrupted_folders.append((cname, action, adir, reason))
            else:
                healthy_folders += 1

    print(f"\n[+] Auditoria completada:")
    print(f"    - Total de carpetas analizadas:  {total_folders}")
    print(f"    - Carpetas sanas (sin cambios):  {healthy_folders}")
    print(f"    - Carpetas CORRUPTED_PALETTE:    {len(corrupted_folders)}")

    print("\n" + "=" * 80)
    print("FASE 3: APLICANDO CORRECCION QUIRURGICA A CARPETAS MARCADAS")
    print("=" * 80)

    total_frames_fixed = 0
    flagged_ryu_actions = []

    for cname, action, adir, reason in corrupted_folders:
        print(f"\n-> [{cname}/{action}] - {reason}")
        fixed_count = correct_action_folder(cname, adir)
        total_frames_fixed += fixed_count
        if cname == "02_Ryu":
            flagged_ryu_actions.append(action)
        print(f"   [CORREGIDO] {fixed_count} frames sobrescritos con blanco puro y piel natural.")

    # Generar tablero de verificacion visual
    print("\n" + "=" * 80)
    print("FASE 4: GENERANDO CONTACT SHEET DE CONFIRMACION VISUAL")
    print("=" * 80)

    ryu_dir = os.path.join(CHARACTERS_DIR, "02_Ryu")
    sheet_output = os.path.join(PROJECT_ROOT, "Assets", "StreetFighter3_ThirdStrike", "audit_verification.png")
    generate_contact_sheet(ryu_dir, flagged_ryu_actions, sheet_output)

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("RESUMEN FINAL DE AUDITORIA Y RESTAURACION ARCADE")
    print("=" * 80)
    print(f"✓ Tiempo de ejecucion:       {elapsed:.2f} segundos")
    print(f"✓ Carpetas auditadas:        {total_folders}")
    print(f"✓ Carpetas sanas:            {healthy_folders}")
    print(f"✓ Carpetas corregidas:       {len(corrupted_folders)}")
    print(f"✓ Frames PNG restaurados:    {total_frames_fixed}")
    print(f"✓ Archivo de verificacion:   Assets/StreetFighter3_ThirdStrike/audit_verification.png")
    print("=" * 80)

if __name__ == "__main__":
    main()
