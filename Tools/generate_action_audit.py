import os
from PIL import Image

PROJECT_ROOT = r'C:\Users\marco\2026 B\Desarrollo de Juegos\StreetFighter3_ThirdStrike'
CHARACTERS_DIR = os.path.join(PROJECT_ROOT, 'Assets', 'StreetFighter3_ThirdStrike', 'Characters')

# Select notable action frames across the new 7-category hierarchy with descriptive names
sample_actions = [
    ('00_Gill', '03_Specials_Supers/resurrection_left', 0),
    ('01_Alex', '03_Specials_Supers/flashchop', 3),
    ('02_Ryu', '06_Intros_Victories/victory_pose_1', 10),
    ('02_Ryu', '03_Specials_Supers/shoryuken', 4),
    ('02_Ryu', '03_Specials_Supers/fireball', 5),
    ('03_Yun', '03_Specials_Supers/palm', 2),
    ('04_Dudley', '06_Intros_Victories/victory_pose_1', 5),
    ('05_Necro', '06_Intros_Victories/victory_pose_1', 4),
    ('06_Hugo', '03_Specials_Supers/hammer', 3),
    ('07_Ibuki', '06_Intros_Victories/victory_pose_1', 4),
    ('08_Elena', '06_Intros_Victories/victory_pose_1', 3),
    ('09_Oro', '02_Normals/forward_medium_punch', 3),
    ('10_Yang', '03_Specials_Supers/slash', 2),
    ('11_Ken', '03_Specials_Supers/shoryuken', 4),
    ('12_Sean', '03_Specials_Supers/shoryuken', 4),
    ('13_Urien', '03_Specials_Supers/headbutt', 3),
    ('14_Akuma_Gouki', '03_Specials_Supers/fireball', 3),
    ('16_Chun_Li', '06_Intros_Victories/victory_pose_1', 5),
    ('17_Makoto', '06_Intros_Victories/victory_pose_1', 4),
    ('20_Remy', '06_Intros_Victories/victory_pose_1', 4)
]

cols = 5
rows = 4
cell_w = 180
cell_h = 180

sheet = Image.new('RGBA', (cols * cell_w, rows * cell_h), (25, 25, 28, 255))

for idx, (cfolder, subpath, frame) in enumerate(sample_actions):
    cdir = os.path.join(CHARACTERS_DIR, cfolder, subpath)
    fpath = os.path.join(cdir, f"{frame}.png")
    if not os.path.exists(fpath):
        fpath = os.path.join(cdir, "0.png")
    if os.path.exists(fpath):
        im = Image.open(fpath)
        c = idx % cols
        r = idx // cols
        x = c * cell_w + (cell_w - im.width) // 2
        y = r * cell_h + (cell_h - im.height - 12)
        sheet.alpha_composite(im, (x, y))

out_path = os.path.join(PROJECT_ROOT, 'Assets', 'StreetFighter3_ThirdStrike', 'audit_actions_verification.png')
sheet.save(out_path, 'PNG')
print(f"Action verification sheet saved to {out_path}")
