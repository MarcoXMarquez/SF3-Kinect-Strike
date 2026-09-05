import os
import re

p = r'C:\Users\marco\2026 B\Desarrollo de Juegos\StreetFighter3_ThirdStrike\Assets\StreetFighter3_ThirdStrike\Characters'

all_folders = set()
for c in sorted(os.listdir(p)):
    cp = os.path.join(p, c)
    if os.path.isdir(cp):
        folders = [d for d in os.listdir(cp) if os.path.isdir(os.path.join(cp, d))]
        for d in folders:
            all_folders.add((c, d))

def classify_action(c, action_name):
    act = action_name.lower()
    
    # Clean character prefixes if present (e.g. alexstance -> stance)
    slug = c[3:].lower()
    if act.startswith(slug):
        act = act[len(slug):].strip('_')
    for pre in ['chun_li', 'chunli', 'twelve_', 'akuma']:
        if act.startswith(pre):
            act = act[len(pre):].strip('_')

    # Remove direction suffix for Gill / Urien if present
    base_act = re.sub(r'_(left|right)$', '', act)

    # 1. Menos Esenciales / Secundarios / Extras
    # Props, stages, effects, external assistants
    if any(k in base_act for k in ['bg', 'house', 'leaves', 'person', 'flags', 'horses', 'test', 'carintro', 'portrait', 'shadow', 'smoke']):
        return '07_Secondary_Extras'
    if any(k in base_act for k in ['cultmember', 'secretary', 'poison', 'effie', 'judgement', 'chair']):
        return '07_Secondary_Extras'
    if base_act in ['chipdeath', 'timeout', 'timeloss', 'crying']:
        return '07_Secondary_Extras'

    # 2. Cinemáticas, Intros, Burlas y Victorias
    if 'intro' in base_act or 'taunt' in base_act or 'win' in base_act or 'thumb' in base_act or 'ripshirt' in base_act or 'pose' in base_act:
        return '06_Intros_Victories'

    # 3. Agarres / Proyecciones
    if any(k in base_act for k in ['throw', 'grab', 'sleeper', 'powerbomb', 'spiralddt', 'airthrow']):
        return '05_Throws'

    # 4. Defensa y Reacciones a Golpes
    if any(k in base_act for k in ['block', 'parry', 'hit', 'slam', 'twist', 'shocked', 'dizzy', 'stun']):
        return '04_Defense_Hit'

    # 5. Movimiento Básico y Reposo
    if base_act in ['stance', 'gillstance', 'idle', 'walkf', 'walkb', 'walk', 'dashf', 'dashb', 'dash', 'crouch', 'crouching', 'jump', 'jumpf', 'jumpb', 'jumpub', 'jumpuf', 'wakeup', 'quickroll', 'roll', 'quickrise', 'teleport', 'backflip']:
        return '01_Movement'

    # 6. Ataques Normales (de pie, agachado, aéreo, comandos)
    normals_regex = r'^(crouch_|jump_|jumpf_)?(wp|mp|hp|wk|mk|hk|jab|strong|fierce|short|forward|roundhouse|fhp|fmp|fmk|hpc|mpc|wpc|mkc|bmp|uo|axe_air)$'
    if re.match(normals_regex, base_act):
        return '02_Normals'
    if any(base_act.startswith(x) for x in ['crouch_', 'jump_', 'jumpf_']):
        # If it has crouch_ or jump_ and ends in normals
        sub = re.sub(r'^(crouch_|jump_|jumpf_)', '', base_act)
        if sub in ['wp', 'mp', 'hp', 'wk', 'mk', 'hk', 'lp', 'lk']:
            return '02_Normals'

    # 7. Ataques Especiales y Supers (todo lo demás son movimientos de combate especiales)
    return '03_Specials_Supers'

classified = {}
for c, d in all_folders:
    cat = classify_action(c, d)
    classified.setdefault(cat, []).append((c, d))

for cat in sorted(classified.keys()):
    print(f"{cat:25s}: {len(classified[cat])} folders")
