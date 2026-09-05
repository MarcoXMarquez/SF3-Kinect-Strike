import os
import re

p = r'C:\Users\marco\2026 B\Desarrollo de Juegos\StreetFighter3_ThirdStrike\Assets\StreetFighter3_ThirdStrike\Characters'

def clean_action_name(char_folder, folder_name):
    act = folder_name.lower()
    
    # Character prefixes to strip
    # e.g. '01_Alex' -> 'alex', '14_Akuma_Gouki' -> 'akuma', 'gouki'
    char_slug = re.sub(r'^\d+_', '', char_folder).lower()
    prefixes = [char_slug, char_slug.replace('_', ''), 'chun_li', 'chunli', 'chun', 'akuma', 'gouki', 'twelve_']
    for pre in prefixes:
        if act.startswith(pre) and len(act) > len(pre):
            act = act[len(pre):].strip('_')
            break
            
    return act

def classify_action(char_folder, folder_name):
    act = clean_action_name(char_folder, folder_name)
    base_act = re.sub(r'_(left|right)$', '', act)

    # 1. Menos Esenciales / Secundarios / Extras (Props, Escenarios, Asistentes, Derrotas no interactivas)
    if any(k in base_act for k in ['bg', 'house', 'leaves', 'person', 'flags', 'horses', 'test', 'carintro', 'portrait', 'shadow', 'smoke']):
        return '07_Secondary_Extras'
    if any(k in base_act for k in ['cultmember', 'secretary', 'poison', 'effie', 'judgement', 'chair', 'bird', 'dog']):
        return '07_Secondary_Extras'
    if base_act in ['chipdeath', 'timeout', 'timeloss', 'crying']:
        return '07_Secondary_Extras'

    # 2. Cinemáticas, Intros, Burlas y Victorias
    if any(k in base_act for k in ['intro', 'taunt', 'win', 'thumb', 'ripshirt', 'pose', 'victory', 'arms']):
        return '06_Intros_Victories'

    # 3. Agarres / Proyecciones
    if any(k in base_act for k in ['throw', 'grab', 'sleeper', 'powerbomb', 'spiralddt', 'airthrow', 'ddt', 'suplex']):
        return '05_Throws'

    # 4. Defensa y Reacciones a Golpes
    if any(k in base_act for k in ['block', 'parry', 'hit', 'slam', 'twist', 'shocked', 'dizzy', 'stun']):
        return '04_Defense_Hit'

    # 5. Movimiento Básico y Reposo (Locomoción y Posturas)
    if any(k in base_act for k in ['walk', 'dash', 'run', 'crouch', 'jump', 'teleport', 'backflip', 'quickroll', 'quickrise', 'roll', 'wakeup', 'getup', 'turn']):
        return '01_Movement'
    if base_act in ['stance', 'gillstance', 'idle']:
        return '01_Movement'

    # 6. Ataques Normales (de pie, agachado, aéreo, comandos)
    normals_tokens = [
        'wp', 'mp', 'hp', 'wk', 'mk', 'hk', 'lp', 'lk',
        'jab', 'strong', 'fierce', 'short', 'forward', 'roundhouse',
        'fhp', 'fmp', 'fmk', 'flk', 'dfhk', 'dfhp',
        'hpc', 'mpc', 'wpc', 'mkc', 'wkc', 'hkc',
        'bmp', 'bmk', 'bhk', 'axe_air', 'uo'
    ]
    if base_act in normals_tokens:
        return '02_Normals'
    if any(base_act.startswith(x) for x in ['crouch_', 'jump_', 'jumpf_', 'jumpb_', 'jumpu_']):
        sub = re.sub(r'^(crouch_|jump_|jumpf_|jumpb_|jumpu_)', '', base_act)
        if sub in normals_tokens:
            return '02_Normals'

    # 7. Ataques Especiales y Supers (Especiales de combate, proyectiles, antiaéreos, Super Arts)
    return '03_Specials_Supers'

if __name__ == '__main__':
    all_folders = set()
    for c in sorted(os.listdir(p)):
        cp = os.path.join(p, c)
        if os.path.isdir(cp):
            for d in os.listdir(cp):
                if os.path.isdir(os.path.join(cp, d)):
                    all_folders.add((c, d))
                    
    classified = {}
    for c, d in all_folders:
        cat = classify_action(c, d)
        classified.setdefault(cat, []).append((c, d))
        
    for cat in sorted(classified.keys()):
        print(f"{cat:25s}: {len(classified[cat])} folders")
