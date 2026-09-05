"""
SF3: 3rd Strike - Expand Character Animation Folder Names to Fully Descriptive
==============================================================================
Expands abbreviations across all 20 characters into human-readable English names:
  - hk, mk, wk/lk, hp, mp, wp/lp -> heavy_kick, medium_kick, light_kick, etc.
  - jumpf, jumpb, jump -> jump_forward, jump_backward, jump_neutral
  - walkf, walkb -> walk_forward, walk_backward
  - dashf, dashb -> dash_forward, dash_backward
  - crouch_hk, jump_hk, jumpf_hp -> crouch_heavy_kick, jump_heavy_kick, jump_forward_heavy_punch
  - fhp, fmp -> forward_heavy_punch, forward_medium_punch
  - win1, win2 -> victory_pose_1, victory_pose_2
  - block, parry, hit, slam -> block_standing, parry_standing, hit_standing, knockdown_slam

Preserves Unity .meta files cleanly.
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

def expand_action_name(cat, name):
    suffix = ''
    if name.endswith('_left'):
        suffix = '_left'
        name = name[:-5]
    elif name.endswith('_right'):
        suffix = '_right'
        name = name[:-6]

    # Specific unique actions
    if name == 'kneeslam':
        return '04_Defense_Hit', 'knockdown_knee_slam' + suffix
    if name == 'airthrow2':
        return '05_Throws', 'throw_air_2' + suffix
    if name == 'throw_reverse':
        return '05_Throws', 'throw_backward_reverse' + suffix
    if name == 'roll':
        return '01_Movement', 'roll_forward' + suffix

    # Map normals abbreviations
    PUNCH_MAP = {'wp': 'light_punch', 'lp': 'light_punch', 'mp': 'medium_punch', 'hp': 'heavy_punch'}
    KICK_MAP = {'wk': 'light_kick', 'lk': 'light_kick', 'mk': 'medium_kick', 'hk': 'heavy_kick'}
    CLOSE_MAP = {
        'wpc': 'light_punch_close', 'lpc': 'light_punch_close',
        'mpc': 'medium_punch_close', 'hpc': 'heavy_punch_close',
        'wkc': 'light_kick_close', 'lkc': 'light_kick_close',
        'mkc': 'medium_kick_close', 'hkc': 'heavy_kick_close'
    }
    
    # 1. Close normals
    if name in CLOSE_MAP:
        return '02_Normals', CLOSE_MAP[name] + suffix
        
    # 2. Standing normals
    if name in PUNCH_MAP:
        return '02_Normals', PUNCH_MAP[name] + suffix
    if name in KICK_MAP:
        return '02_Normals', KICK_MAP[name] + suffix
        
    # 3. Command normals
    cmd_prefixes = [
        ('dfhk', 'downforward_heavy_kick'),
        ('dfhp', 'downforward_heavy_punch'),
        ('crouch_fhp', 'crouch_forward_heavy_punch'),
        ('crouch_fmk', 'crouch_forward_medium_kick'),
        ('crouch_bhp', 'crouch_back_heavy_punch'),
        ('fhp', 'forward_heavy_punch'),
        ('fmp', 'forward_medium_punch'),
        ('fmk', 'forward_medium_kick'),
        ('flk', 'forward_light_kick'),
        ('flp', 'forward_light_punch'),
        ('fhk', 'forward_heavy_kick'),
        ('bmp', 'back_medium_punch'),
        ('bmk', 'back_medium_kick'),
        ('bhk', 'back_heavy_kick'),
        ('bhp', 'back_heavy_punch'),
        ('blk', 'back_light_kick'),
        ('blp', 'back_light_punch'),
        ('uo', 'universal_overhead'),
        ('axe_air', 'axe_kick_air')
    ]
    for cp, exp in cmd_prefixes:
        if name == cp:
            return '02_Normals', exp + suffix

    # 4. Crouching normals
    if name.startswith('crouch_'):
        sub = name[7:]
        if sub in PUNCH_MAP:
            return '02_Normals', f'crouch_{PUNCH_MAP[sub]}' + suffix
        if sub in KICK_MAP:
            return '02_Normals', f'crouch_{KICK_MAP[sub]}' + suffix
            
    # 5. Jumping normals
    jump_m = re.match(r'^jump([fb])?_(d)?([wmlh][pk])$', name)
    if jump_m:
        dir_char = jump_m.group(1)
        down_char = jump_m.group(2)
        attack = jump_m.group(3)
        parts = ['jump']
        if dir_char == 'f': parts.append('forward')
        elif dir_char == 'b': parts.append('backward')
        if down_char == 'd': parts.append('down')
        att_name = PUNCH_MAP.get(attack, KICK_MAP.get(attack, attack))
        parts.append(att_name)
        return '02_Normals', '_'.join(parts) + suffix

    if name in ['jumpingelbow', 'jump_elbow']:
        return '02_Normals', 'jump_elbow' + suffix
    if name in ['jump_dk']:
        return '02_Normals', 'jump_down_kick' + suffix
    if name in ['jump_fmp']:
        return '02_Normals', 'jump_forward_medium_punch' + suffix
    if name in ['jumpdhp']:
        return '02_Normals', 'jump_down_heavy_punch' + suffix

    # 6. Movement expansions
    if name in ['stance', 'idle']:
        return '01_Movement', 'idle_stance' + suffix
    if name in ['walkf', 'walkforward', 'walk']:
        return '01_Movement', 'walk_forward' + suffix
    if name in ['walkb', 'walkback']:
        return '01_Movement', 'walk_backward' + suffix
    if name in ['dashf', 'dashforward']:
        return '01_Movement', 'dash_forward' + suffix
    if name in ['dashb', 'dashback']:
        return '01_Movement', 'dash_backward' + suffix
    if name in ['jump']:
        return '01_Movement', 'jump_neutral' + suffix
    if name in ['jumpf']:
        return '01_Movement', 'jump_forward' + suffix
    if name in ['jumpb']:
        return '01_Movement', 'jump_backward' + suffix
    if name in ['crouch', 'crouch_down']:
        return '01_Movement', 'crouch_down' + suffix
    if name in ['crouching', 'crouch_idle']:
        return '01_Movement', 'crouch_idle' + suffix
    if name in ['quickroll', 'wakeupquickroll']:
        return '01_Movement', 'quick_roll' + suffix
    if name in ['quickrise']:
        return '01_Movement', 'quick_rise' + suffix
    if name in ['wakeup']:
        return '01_Movement', 'wakeup_recovery' + suffix

    # 7. Defense & Hit expansions
    if name in ['block']:
        return '04_Defense_Hit', 'block_standing' + suffix
    if name in ['block_low', 'block_crouch', 'crouch_block']:
        return '04_Defense_Hit', 'block_crouching' + suffix
    if name in ['block_high']:
        return '04_Defense_Hit', 'block_high' + suffix
    if name in ['parry']:
        return '04_Defense_Hit', 'parry_standing' + suffix
    if name in ['parry_low', 'parry_crouch']:
        return '04_Defense_Hit', 'parry_crouching' + suffix
    if name in ['stand_hit', 'hit_standing']:
        return '04_Defense_Hit', 'hit_standing' + suffix
    if name in ['crouch_hit', 'hit_crouching']:
        return '04_Defense_Hit', 'hit_crouching' + suffix
    if name in ['slam']:
        return '04_Defense_Hit', 'knockdown_slam' + suffix
    if name in ['twist']:
        return '04_Defense_Hit', 'knockdown_twist' + suffix
    if name in ['shocked']:
        return '04_Defense_Hit', 'hit_electrocuted' + suffix

    # 8. Throws
    if name in ['throw', 'throw_forward', 'throwf']:
        return '05_Throws', 'throw_forward' + suffix
    if name in ['throw_back', 'throwb']:
        return '05_Throws', 'throw_backward' + suffix
    if name in ['throw_miss', 'grabmiss', 'throw_fail', 'missedpowerbomb']:
        return '05_Throws', 'throw_miss' + suffix
    if name in ['airthrow', 'throwair']:
        return '05_Throws', 'throw_air' + suffix
    if name in ['sleeperhold']:
        return '05_Throws', 'sleeper_hold' + suffix
    if name in ['spiralddt']:
        return '05_Throws', 'spiral_ddt' + suffix
    if name in ['powerbomb', 'powerbomb_reverse']:
        return '05_Throws', name + suffix

    # 9. Intros & Victories
    if re.match(r'^win(\d+)$', name):
        w_num = re.match(r'^win(\d+)$', name).group(1)
        return '06_Intros_Victories', f'victory_pose_{w_num}' + suffix
    if name in ['smilewin', 'bendwin', 'handstandwin']:
        return '06_Intros_Victories', f'victory_{name[:-3]}' + suffix
    if name == 'intro':
        return '06_Intros_Victories', 'intro_default' + suffix
    if re.match(r'^intro(\d+)$', name):
        i_num = re.match(r'^intro(\d+)$', name).group(1)
        return '06_Intros_Victories', f'intro_{i_num}' + suffix
    if name in ['ken_intro', 'alex_intro', 'hugo_intro', 'ibuki_intro', 'makoto_intro', 'ryu_intro']:
        return '06_Intros_Victories', 'special_' + name + suffix
    if name in ['taunt', 'taunt1']:
        return '06_Intros_Victories', 'taunt' + suffix
    if name in ['ripshirt']:
        return '06_Intros_Victories', 'intro_rip_shirt' + suffix

    # 10. Secondary Extras
    if name in ['chipdeath']:
        return '07_Secondary_Extras', 'defeat_chip_death' + suffix
    if name in ['timeout', 'timeloss']:
        return '07_Secondary_Extras', 'defeat_timeout' + suffix
    if name in ['crying']:
        return '07_Secondary_Extras', 'defeat_crying' + suffix
    if name in ['cultmembers']:
        return '07_Secondary_Extras', 'assistant_cultmembers' + suffix
    if name in ['secretary']:
        return '07_Secondary_Extras', 'assistant_secretary' + suffix
    if name.startswith('effie'):
        return '07_Secondary_Extras', 'assistant_' + name + suffix
    if name.startswith('poison'):
        return '07_Secondary_Extras', 'assistant_' + name + suffix
    if any(k in name for k in ['bg', 'house', 'leaves', 'person', 'flags', 'horses', 'statue']):
        return '07_Secondary_Extras', 'stage_prop_' + name + suffix

    # 11. Specials: Motion abbreviations
    MOTION_MAP = {
        'qcf': 'quartercircle_forward',
        'qcb': 'quartercircle_back',
        'hcf': 'halfcircle_forward',
        'hcb': 'halfcircle_back',
        'bf': 'charge_back_forward',
        'db': 'down_back'
    }
    for m_short, m_long in MOTION_MAP.items():
        if name.startswith(m_short):
            rest = name[len(m_short):]
            if rest == 'p': rest = '_punch'
            elif rest == 'k': rest = '_kick'
            elif rest == 'pp': rest = '_ex_punch'
            elif rest == 'kk': rest = '_ex_kick'
            return '03_Specials_Supers', f'{m_long}{rest}' + suffix
            
    if name.startswith('sa') and re.match(r'^sa\d', name):
        return '03_Specials_Supers', 'super_art_' + name[2:] + suffix

    return cat, name + suffix

def move_folder_with_meta(src_dir, dst_dir):
    src_meta = src_dir + '.meta'
    dst_meta = dst_dir + '.meta'
    
    if os.path.exists(dst_dir):
        for item in os.listdir(src_dir):
            s_item = os.path.join(src_dir, item)
            d_item = os.path.join(dst_dir, item)
            if os.path.exists(d_item):
                if os.path.isdir(s_item):
                    move_folder_with_meta(s_item, d_item)
                else:
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

def process_character(char_folder, dry_run=False):
    char_path = os.path.join(CHARACTERS_DIR, char_folder)
    if not os.path.isdir(char_path): return
    
    # Gather all folders under the 7 categories
    tasks = []
    dest_map = {}
    deletions = []
    
    for cat in CATEGORIES:
        cat_p = os.path.join(char_path, cat)
        if not os.path.isdir(cat_p): continue
        for d in sorted(os.listdir(cat_p)):
            dp = os.path.join(cat_p, d)
            if not os.path.isdir(dp): continue
            
            new_cat, new_name = expand_action_name(cat, d)
            key = (new_cat, new_name)
            
            # Check modification time
            pngs = [f for f in os.listdir(dp) if f.endswith('.png')]
            mtime = os.path.getmtime(os.path.join(dp, pngs[0])) if pngs else 0
            
            if key in dest_map:
                prev_cat, prev_orig, prev_mtime = dest_map[key]
                # Compare mtime: newer rip survives, older morning rip discarded
                if mtime >= prev_mtime:
                    # New one wins, discard prev
                    deletions.append((prev_cat, prev_orig))
                    dest_map[key] = (cat, d, mtime)
                else:
                    # Prev was newer, discard current
                    deletions.append((cat, d))
            else:
                dest_map[key] = (cat, d, mtime)
                
    # Build list of moves from dest_map
    for (new_cat, new_name), (orig_cat, orig_name, _) in dest_map.items():
        if new_cat != orig_cat or new_name != orig_name:
            tasks.append((orig_cat, orig_name, new_cat, new_name))
            
    if dry_run:
        print(f"[{char_folder}] Dry run: {len(tasks)} renames, {len(deletions)} obsolete duplicate deletions.")
        return
        
    # Execute deletions of obsolete duplicates
    for c_cat, c_name in deletions:
        dp = os.path.join(char_path, c_cat, c_name)
        shutil.rmtree(dp, ignore_errors=True)
        meta = dp + '.meta'
        if os.path.exists(meta):
            try: os.remove(meta)
            except Exception: pass
            
    # Execute moves
    renamed = 0
    for orig_cat, orig_name, new_cat, new_name in tasks:
        src = os.path.join(char_path, orig_cat, orig_name)
        dst_dir = os.path.join(char_path, new_cat)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, new_name)
        
        move_folder_with_meta(src, dst)
        renamed += 1
        
    print(f"[{char_folder}] Renamed {renamed} folders to fully descriptive names.")

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
    print("SF3: 3RD STRIKE - DESCRIPTIVE ANIMATION RENAMER")
    print(f"Target characters: {len(chars)}")
    if dry_run:
        print("MODE: DRY RUN")
    print("=" * 70)
    
    for c in chars:
        process_character(c, dry_run=dry_run)
        
    print("=" * 70)
    print("ALL CHARACTERS SUCCESSFULLY RENAMED!")
    print("=" * 70)

if __name__ == '__main__':
    main()
