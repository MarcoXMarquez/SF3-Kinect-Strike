"""
SF3: 3rd Strike - Automated Zweifuss Sprite Extractor & LP Palette Converter
=============================================================================
This tool downloads 100% official Capcom LP (Light Punch / Player 1) sprites
directly from the Zweifuss repository (https://www.justnopoint.com/zweifuss/),
processes every frame to transparent RGBA PNG, and organizes them cleanly into
Assets/StreetFighter3_ThirdStrike/Characters/{Character}/{Action}/{Frame}.png.
"""

import os
import re
import sys
import time
import io
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CHARACTERS_DIR = os.path.join(PROJECT_ROOT, 'Assets', 'StreetFighter3_ThirdStrike', 'Characters')
SCRATCH_DIR = os.path.join(os.path.expanduser('~'), '.gemini', 'antigravity', 'brain', '39167e8e-c10a-47b4-b79d-be2d6ddc71ef', 'scratch')
os.makedirs(SCRATCH_DIR, exist_ok=True)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# 20 Playable & Boss Characters Configuration
CHAR_CONFIGS = [
    {
        'folder': '00_Gill',
        'slug': 'gill',
        'htm': 'gill.htm',
        'palette_bin': 'GillPalette.bin',
        'lp_pcolornum': 0,
        'special': 'gill'
    },
    {
        'folder': '01_Alex',
        'slug': 'alex',
        'htm': 'alex.htm',
        'palette_bin': 'AlexPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '02_Ryu',
        'slug': 'ryu',
        'htm': 'ryu.htm',
        'palette_bin': 'RyuPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '03_Yun',
        'slug': 'yun',
        'htm': 'yun.htm',
        'palette_bin': 'YunPalette.bin',
        'lp_pcolornum': 10
    },
    {
        'folder': '04_Dudley',
        'slug': 'dudley',
        'htm': 'dudley.htm',
        'palette_bin': 'DudleyPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '05_Necro',
        'slug': 'necro',
        'htm': 'necro.htm',
        'palette_bin': 'NecroPalette.bin',
        'lp_pcolornum': 13,
        'special': 'necro'
    },
    {
        'folder': '06_Hugo',
        'slug': 'hugo',
        'htm': 'hugo.htm',
        'palette_bin': 'HugoPalette.bin',
        'lp_pcolornum': 7,
        'special': 'hugo'
    },
    {
        'folder': '07_Ibuki',
        'slug': 'ibuki',
        'htm': 'ibuki.htm',
        'palette_bin': 'IbukiPalette.bin',
        'lp_pcolornum': 0,
        'special': 'ibuki'
    },
    {
        'folder': '08_Elena',
        'slug': 'elena',
        'htm': 'elena.htm',
        'palette_bin': 'ElenaPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '09_Oro',
        'slug': 'oro',
        'htm': 'oro.htm',
        'palette_bin': 'OroPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '10_Yang',
        'slug': 'yang',
        'htm': 'yang.htm',
        'palette_bin': 'YangPalette.bin',
        'lp_pcolornum': 10
    },
    {
        'folder': '11_Ken',
        'slug': 'ken',
        'htm': 'ken.htm',
        'palette_bin': 'KenPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '12_Sean',
        'slug': 'sean',
        'htm': 'sean.htm',
        'palette_bin': 'SeanPalette.bin',
        'lp_pcolornum': 13
    },
    {
        'folder': '13_Urien',
        'slug': 'urien',
        'htm': 'urien.htm',
        'palette_bin': 'UrienPalette.bin',
        'lp_pcolornum': 7
    },
    {
        'folder': '14_Akuma_Gouki',
        'slug': 'akuma',
        'htm': 'akuma.htm',
        'palette_bin': 'AkumaPalette.bin',
        'lp_pcolornum': 7
    },
    {
        'folder': '16_Chun_Li',
        'slug': 'chun-li',
        'htm': 'chun-li.htm',
        'palette_bin': 'Chun-liPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '17_Makoto',
        'slug': 'makoto',
        'htm': 'makoto.htm',
        'palette_bin': 'MakotoPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '18_Q',
        'slug': 'q',
        'htm': 'q.htm',
        'palette_bin': 'QPalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '19_Twelve',
        'slug': 'twelve',
        'htm': 'twelve.htm',
        'palette_bin': 'TwelvePalette.bin',
        'lp_pcolornum': 0
    },
    {
        'folder': '20_Remy',
        'slug': 'remy',
        'htm': 'remy.htm',
        'palette_bin': 'RemyPalette.bin',
        'lp_pcolornum': 0
    }
]

def fetch_url(url, referer, retries=3, delay=1.0):
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': referer,
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
    }
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = resp.read()
                if len(data) > 100 and not data.startswith(b'<head>'):
                    return data
        except Exception as e:
            if attempt == retries - 1:
                return None
            time.sleep(delay * (attempt + 1))
    return None

def normalize_action_name(reveal_name, slug):
    name = reveal_name
    prefixes = [slug + '-', slug.replace('-', '') + '-', 'chun-', 'twelve_']
    for p in prefixes:
        if name.startswith(p):
            name = name[len(p):]
            break
    return name.replace('-', '_').strip('_').lower()

def match_existing_folder(target_dir, clean_name, orig_reveal):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        return clean_name

    existing = os.listdir(target_dir)
    existing_lower = {d.lower(): d for d in existing if os.path.isdir(os.path.join(target_dir, d))}
    
    # 1. Direct match on clean_name
    if clean_name in existing_lower:
        return existing_lower[clean_name]
    
    # 2. Match orig_reveal with underscores
    orig_clean = orig_reveal.replace('-', '_').lower()
    if orig_clean in existing_lower:
        return existing_lower[orig_clean]
    
    # 3. Match without underscores/hyphens
    stripped_clean = clean_name.replace('_', '')
    for k, v in existing_lower.items():
        if k.replace('_', '') == stripped_clean:
            return v

    return clean_name

def process_gif_frames(gif_bytes, dest_folder):
    """
    Decodes animated GIF bytes into individual transparent RGBA PNG frames.
    Saves frames as 0.png, 1.png, 2.png, etc. in dest_folder.
    """
    os.makedirs(dest_folder, exist_ok=True)
    im = Image.open(io.BytesIO(gif_bytes))
    
    im.seek(0)
    global_trans = im.info.get('transparency', None)
    pal = im.getpalette()
    
    frame_count = getattr(im, 'n_frames', 1)
    saved_frames = 0
    
    for i in range(frame_count):
        im.seek(i)
        if im.mode == 'P':
            arr = np.array(im)
            if pal is not None:
                p_arr = np.array(pal, dtype=np.uint8).reshape(-1, 3)
                rgba = np.zeros((im.height, im.width, 4), dtype=np.uint8)
                rgba[:, :, :3] = p_arr[arr]
                rgba[:, :, 3] = 255
                if global_trans is not None:
                    rgba[arr == global_trans, :] = 0
                res_im = Image.fromarray(rgba, 'RGBA')
            else:
                res_im = im.convert('RGBA')
        else:
            rgba = np.array(im.convert('RGBA'))
            # Zero out transparent pixels
            rgba[rgba[:, :, 3] == 0, :] = 0
            res_im = Image.fromarray(rgba, 'RGBA')
            
        out_path = os.path.join(dest_folder, f"{i}.png")
        res_im.save(out_path, 'PNG', optimize=False)
        saved_frames += 1
        
    return saved_frames

def extract_character(cfg, selected_actions=None):
    """
    Extracts all animations for a given character config.
    """
    cfolder = cfg['folder']
    slug = cfg['slug']
    htm_file = cfg['htm']
    pbin = cfg['palette_bin']
    pnum = cfg['lp_pcolornum']
    special = cfg.get('special', None)
    
    char_dest = os.path.join(CHARACTERS_DIR, cfolder)
    os.makedirs(char_dest, exist_ok=True)
    
    # Read HTML from scratch or Zweifuss
    htm_path = os.path.join(SCRATCH_DIR, htm_file)
    if not os.path.exists(htm_path):
        url = f"https://www.justnopoint.com/zweifuss/{slug}/{htm_file}"
        raw_htm = fetch_url(url, f"https://www.justnopoint.com/zweifuss/")
        if raw_htm:
            with open(htm_path, 'wb') as f:
                f.write(raw_htm)
                
    if not os.path.exists(htm_path):
        print(f"[{cfolder}] Failed to load HTML {htm_file}")
        return 0, 0
        
    with open(htm_path, 'r', encoding='latin1') as f:
        content = f.read()
        
    reveals = sorted(list(set(re.findall(r'reveal\([\x22\x27]([^\x22\x27]+)[\x22\x27]\)', content))))
    if selected_actions:
        reveals = [r for r in reveals if any(a.lower() in r.lower() for a in selected_actions)]
        
    ref_url = f"https://www.justnopoint.com/zweifuss/{slug}/{htm_file}"
    
    # Import classifier and expander from helper scripts
    from sf3_organize_characters import classify_action, clean_action_name
    from sf3_rename_to_descriptive import expand_action_name

    tasks = []
    # Build list of download tasks (url, dest_folder, reveal_name)
    for r in reveals:
        if special == 'gill':
            if r in ['gill-cultmembers', 'gill-secretary']:
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring=GillPalette.bin&pcolornum=0&pname=gill/{r}.gif"
                clean_name = clean_action_name(cfolder, r)
                cat = classify_action(clean_name)
                cat, exp_name = expand_action_name(cat, clean_name)
                tasks.append((url, os.path.join(char_dest, cat, exp_name), r))
            else:
                # Left
                url_l = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring=GillPalette.bin&pcolornum=0&pname=gill/{r}-left.gif"
                clean_l = clean_action_name(cfolder, r) + '_left'
                cat_l = classify_action(clean_l)
                cat_l, exp_l = expand_action_name(cat_l, clean_l)
                tasks.append((url_l, os.path.join(char_dest, cat_l, exp_l), r + ' (left)'))
                
                # Right
                url_r = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring=GillPalette.bin&pcolornum=1&pname=gill/{r}-right.gif"
                clean_r = clean_action_name(cfolder, r) + '_right'
                cat_r = classify_action(clean_r)
                cat_r, exp_r = expand_action_name(cat_r, clean_r)
                tasks.append((url_r, os.path.join(char_dest, cat_r, exp_r), r + ' (right)'))
                
        elif special == 'necro':
            clean_name = clean_action_name(cfolder, r)
            cat = classify_action(clean_name)
            cat, exp_name = expand_action_name(cat, clean_name)
            if r.startswith('effie'):
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring=EffiePalette.bin&pcolornum=0&pname=necro/{r}.gif"
            else:
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring={pbin}&pcolornum={pnum}&pname={slug}/{r}.gif"
            tasks.append((url, os.path.join(char_dest, cat, exp_name), r))
            
        elif special == 'hugo':
            clean_name = clean_action_name(cfolder, r)
            cat = classify_action(clean_name)
            cat, exp_name = expand_action_name(cat, clean_name)
            if r.startswith('poison'):
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring=PoisonPalette.bin&pcolornum=0&pname=hugo/{r}.gif"
            else:
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring={pbin}&pcolornum={pnum}&pname={slug}/{r}.gif"
            tasks.append((url, os.path.join(char_dest, cat, exp_name), r))
            
        elif special == 'ibuki':
            clean_name = clean_action_name(cfolder, r)
            cat = classify_action(clean_name)
            cat, exp_name = expand_action_name(cat, clean_name)
            if r in ['ibuki-win2', 'ibuki-win7', 'ibuki-win9']:
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring=IbukiStreetPalette.bin&pcolornum=7&pname=ibuki/{r}.gif"
            else:
                url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring={pbin}&pcolornum={pnum}&pname={slug}/{r}.gif"
            tasks.append((url, os.path.join(char_dest, cat, exp_name), r))
            
        else:
            clean_name = clean_action_name(cfolder, r)
            cat = classify_action(clean_name)
            cat, exp_name = expand_action_name(cat, clean_name)
            url = f"https://www.justnopoint.com/zweifuss/colorswap.php?pcolorstring={pbin}&pcolornum={pnum}&pname={slug}/{r}.gif"
            tasks.append((url, os.path.join(char_dest, cat, exp_name), r))

    print(f"[{cfolder}] Starting extraction of {len(tasks)} animations...")
    
    total_frames = 0
    successful_anims = 0
    failed_anims = []
    
    def worker(task):
        url, dest_folder, r_name = task
        data = fetch_url(url, ref_url)
        if not data:
            return False, r_name, 0, "Download failed"
        try:
            frames = process_gif_frames(data, dest_folder)
            return True, r_name, frames, None
        except Exception as err:
            return False, r_name, 0, str(err)
            
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(worker, t): t for t in tasks}
        for future in as_completed(futures):
            ok, r_name, count, err = future.result()
            if ok:
                successful_anims += 1
                total_frames += count
            else:
                failed_anims.append((r_name, err))
                
    print(f"[{cfolder}] Completed: {successful_anims}/{len(tasks)} animations, {total_frames} frames saved.")
    if failed_anims:
        print(f"[{cfolder}] Warnings ({len(failed_anims)} failed): {failed_anims[:5]}")
        
    return successful_anims, total_frames

def generate_verification_audit():
    """
    Generates a verification contact sheet of stance frame 0 for all 20 characters
    and saves to Assets/StreetFighter3_ThirdStrike/audit_verification.png.
    """
    cols = 5
    rows = 4
    cell_w = 180
    cell_h = 180
    sheet = Image.new('RGBA', (cols * cell_w, rows * cell_h), (25, 25, 28, 255))
    
    idx = 0
    for cfg in CHAR_CONFIGS:
        cfolder = cfg['folder']
        cpath = os.path.join(CHARACTERS_DIR, cfolder)
        # Find stance 0.png in 01_Movement or legacy root
        fpath = None
        for cand in [
            '01_Movement/idle_stance/0.png', '01_Movement/idle_stance_left/0.png',
            '01_Movement/stance/0.png', '01_Movement/stance_left/0.png'
        ]:
            p = os.path.join(cpath, cand)
            if os.path.exists(p):
                fpath = p
                break
        if fpath:
            im = Image.open(fpath)
            c = idx % cols
            r = idx // cols
            x = c * cell_w + (cell_w - im.width) // 2
            y = r * cell_h + (cell_h - im.height - 12)
            sheet.alpha_composite(im, (x, y))
            idx += 1
            
    audit_path = os.path.join(PROJECT_ROOT, 'Assets', 'StreetFighter3_ThirdStrike', 'audit_verification.png')
    sheet.save(audit_path, 'PNG')
    print(f"Audit verification sheet generated at: {audit_path}")

def main():
    target_char = None
    if len(sys.argv) > 1:
        target_char = sys.argv[1]
        
    configs_to_run = CHAR_CONFIGS
    if target_char:
        configs_to_run = [c for c in CHAR_CONFIGS if target_char.lower() in c['folder'].lower() or target_char.lower() in c['slug'].lower()]
        
    print("=" * 70)
    print("STREET FIGHTER III: 3RD STRIKE - AUTONOMOUS ZWEIFUSS INGESTION")
    print(f"Target characters: {len(configs_to_run)}")
    print("=" * 70)
    
    start_time = time.time()
    grand_total_anims = 0
    grand_total_frames = 0
    
    for cfg in configs_to_run:
        anims, frames = extract_character(cfg)
        grand_total_anims += anims
        grand_total_frames += frames
        
    generate_verification_audit()
    
    elapsed = time.time() - start_time
    print("=" * 70)
    print(f"ALL DONE in {elapsed:.1f}s!")
    print(f"Total animations converted: {grand_total_anims}")
    print(f"Total frames written: {grand_total_frames}")
    print("=" * 70)

if __name__ == '__main__':
    main()
