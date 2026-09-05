"""
SF3: 3rd Strike - Character Animation Organizer & Hierarchy Restructurer
========================================================================
Organizes all character animations into 7 standard fighting game tiers:
  01_Movement
  02_Normals
  03_Specials_Supers
  04_Defense_Hit
  05_Throws
  06_Intros_Victories
  07_Secondary_Extras

Handles duplicate resolution, clean nomenclature, and Unity .meta file preservation.
"""

import os
import re
import sys
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHARACTERS_DIR = os.path.join(PROJECT_ROOT, 'Assets', 'StreetFighter3_ThirdStrike', 'Characters')

CATEGORIES = [
    '01_Movement',
    '02_Normals',
    '03_Specials_Supers',
    '04_Defense_Hit',
    '05_Throws',
    '06_Intros_Victories',
    '07_Secondary_Extras'
]

SF_NORMALS_MAP = {
    'jab': 'wp',
    'strong': 'mp',
    'fierce': 'hp',
    'short': 'wk',
    'forward': 'mk',
    'roundhouse': 'hk',
    'forwardc': 'mkc',
    'strongchop': 'mpc',
    'walkforward': 'walkf',
    'walkback': 'walkb',
    'crouchhit': 'crouch_hit',
    'crouchblock': 'crouch_block',
}

def clean_action_name(char_folder, folder_name):
    act = folder_name.lower()
    char_slug = re.sub(r'^\d+_', '', char_folder).lower()
    prefixes = [char_slug, char_slug.replace('_', ''), 'chun_li', 'chunli', 'chun', 'akuma', 'gouki', 'twelve_']
    for pre in prefixes:
        if act.startswith(pre) and len(act) > len(pre):
            act = act[len(pre):].strip('_')
            break
            
    # Apply SF normals mapping (e.g. alexjab -> jab -> wp)
    if act in SF_NORMALS_MAP:
        act = SF_NORMALS_MAP[act]
        
    return act

def classify_action(clean_name):
    base_act = re.sub(r'_(left|right)$', '', clean_name).lower()

    # 1. Menos Esenciales / Secundarios / Extras (Props, Escenarios, Asistentes, Derrotas no interactivas)
    if any(k in base_act for k in ['bg', 'house', 'leaves', 'person', 'flags', 'horses', 'test', 'carintro', 'portrait', 'shadow', 'smoke']):
        return '07_Secondary_Extras'
    if any(k in base_act for k in ['cultmember', 'secretary', 'poison', 'effie', 'judgement', 'chair', 'bird', 'dog', 'seraphic_']):
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

    # 5. Ataques Normales (de pie, agachado, aéreo, comandos de ataque básico)
    normals_tokens = [
        'wp', 'mp', 'hp', 'wk', 'mk', 'hk', 'lp', 'lk',
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

    # 6. Movimiento Básico y Reposo (Locomoción, Saltos y Posturas sin ataque)
    if any(k in base_act for k in ['walk', 'dash', 'run', 'crouch', 'jump', 'teleport', 'backflip', 'quickroll', 'quickrise', 'roll', 'wakeup', 'getup', 'turn']):
        return '01_Movement'
    if base_act in ['stance', 'gillstance', 'idle']:
        return '01_Movement'

    # 7. Ataques Especiales y Supers (Especiales de combate, proyectiles, antiaéreos, Super Arts)
    return '03_Specials_Supers'

def move_folder_with_meta(src_dir, dst_dir):
    """
    Moves src_dir to dst_dir, and moves src_dir.meta to dst_dir.meta if present.
    If dst_dir already exists, merges contents.
    """
    src_meta = src_dir + '.meta'
    dst_meta = dst_dir + '.meta'
    
    if os.path.exists(dst_dir):
        # Merge contents
        for item in os.listdir(src_dir):
            s_item = os.path.join(src_dir, item)
            d_item = os.path.join(dst_dir, item)
            if os.path.exists(d_item):
                if os.path.isdir(s_item):
                    move_folder_with_meta(s_item, d_item)
                else:
                    # overwrite file if newer
                    if os.path.getmtime(s_item) > os.path.getmtime(d_item):
                        shutil.copy2(s_item, d_item)
            else:
                shutil.move(s_item, d_item)
        shutil.rmtree(src_dir, ignore_errors=True)
        if os.path.exists(src_meta) and not os.path.exists(dst_meta):
            shutil.move(src_meta, dst_meta)
        elif os.path.exists(src_meta):
            os.remove(src_meta)
    else:
        shutil.move(src_dir, dst_dir)
        if os.path.exists(src_meta):
            shutil.move(src_meta, dst_meta)

def organize_character(char_folder, dry_run=False):
    char_path = os.path.join(CHARACTERS_DIR, char_folder)
    if not os.path.isdir(char_path):
        return
        
    print(f"[{char_folder}] Processing character...")
    
    # Get direct subdirectories excluding the CATEGORIES if already present
    subdirs = [d for d in os.listdir(char_path) if os.path.isdir(os.path.join(char_path, d)) and d not in CATEGORIES]
    
    # Identify duplicates vs unique
    # First pass: map each folder to (clean_name, category)
    folder_map = []
    for d in subdirs:
        clean_name = clean_action_name(char_folder, d)
        cat = classify_action(clean_name)
        folder_map.append((d, clean_name, cat))
        
    # Group by (cat, clean_name)
    grouped = {}
    for orig, clean, cat in folder_map:
        grouped.setdefault((cat, clean), []).append(orig)
        
    moves = []
    deletions = []
    
    for (cat, clean), orig_list in grouped.items():
        if len(orig_list) == 1:
            moves.append((orig_list[0], cat, clean))
        else:
            # Multiple folders map to same clean name (e.g. 'stance' and 'alexstance')
            # Choose the one that has the newest modification time (our recent 14:46 rip)
            scored = []
            for orig in orig_list:
                dp = os.path.join(char_path, orig)
                pngs = [f for f in os.listdir(dp) if f.endswith('.png')]
                mtime = 0
                if pngs:
                    mtime = os.path.getmtime(os.path.join(dp, pngs[0]))
                scored.append((mtime, len(pngs), orig))
            scored.sort(reverse=True)
            keeper = scored[0][2]
            moves.append((keeper, cat, clean))
            for _, _, discard in scored[1:]:
                deletions.append(discard)
                
    if dry_run:
        print(f"  Dry run: {len(moves)} moves, {len(deletions)} obsolete duplicates to delete.")
        return
        
    # Delete obsolete duplicates
    for disc in deletions:
        dp = os.path.join(char_path, disc)
        shutil.rmtree(dp, ignore_errors=True)
        meta = dp + '.meta'
        if os.path.exists(meta):
            try:
                os.remove(meta)
            except Exception:
                pass
                
    # Execute moves into categories
    moved_count = 0
    for orig, cat, clean in moves:
        src = os.path.join(char_path, orig)
        cat_dir = os.path.join(char_path, cat)
        os.makedirs(cat_dir, exist_ok=True)
        dst = os.path.join(cat_dir, clean)
        
        move_folder_with_meta(src, dst)
        moved_count += 1
        
    print(f"[{char_folder}] Successfully organized {moved_count} animations into 7 categories (cleaned {len(deletions)} duplicates).")

def main():
    dry_run = '--dry-run' in sys.argv
    target_char = None
    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            target_char = arg
            break
            
    chars = sorted([d for d in os.listdir(CHARACTERS_DIR) if os.path.isdir(os.path.join(CHARACTERS_DIR, d)) and d.startswith(('0', '1', '2'))])
    if target_char:
        chars = [c for c in chars if target_char.lower() in c.lower()]
        
    print("=" * 70)
    print("SF3: 3RD STRIKE - CHARACTER ANIMATION REORGANIZER")
    print(f"Target characters: {len(chars)}")
    if dry_run:
        print("MODE: DRY RUN (No files will be modified)")
    print("=" * 70)
    
    for c in chars:
        organize_character(c, dry_run=dry_run)
        
    print("=" * 70)
    print("REORGANIZATION COMPLETE!")
    print("=" * 70)

if __name__ == '__main__':
    main()
