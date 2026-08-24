"""Round 3 (materiau aplati) - reproduit EXACTEMENT la methode du 'dernier
test avant decision' (docs/worklog.md) : facteur LANCZOS 0.647 deja
mesure/valide sur Cendre, applique aux 6 frames de contact quantifiees a
112px, puis cuisson via le VRAI scripts/cook_character_frames.py
(repo-root isole en scratch, aucun fichier reel du depot touche)."""
import os
import subprocess
import sys
from PIL import Image

ROOT = "/home/user/jeux"
SRC = f"{ROOT}/experiments/blender_capture/cendre_pilot/combo_quantized_v4"
SCRATCH = "/tmp/claude-0/-home-user-Alpha-Project-Live/e304835e-195c-5813-864a-d285531ad037/scratchpad/cendre_cook_final_v4"
FACTOR = 0.647

PAIRS = {
    "coup1_contact": ["coup1_contact_00_mocapframe16", "coup1_contact_01_mocapframe18"],
    "coup2_contact": ["coup2_contact_00_mocapframe31", "coup2_contact_01_mocapframe33"],
    "coup3_contact": ["coup3_contact_00_impact_peak", "coup3_contact_01_impact_release"],
}

anim_args = []
for anim_name, frames in PAIRS.items():
    src_dir = os.path.join(SCRATCH, "src_anims", anim_name)
    os.makedirs(src_dir, exist_ok=True)
    for i, f in enumerate(frames):
        im = Image.open(os.path.join(SRC, f"{f}.png")).convert("RGBA")
        new_size = (round(im.width * FACTOR), round(im.height * FACTOR))
        resized = im.resize(new_size, Image.LANCZOS)
        resized.save(os.path.join(src_dir, f"{i}.png"))
    anim_args.append(f"{anim_name}:{src_dir}")

cmd = [
    sys.executable, os.path.join(ROOT, "scripts", "cook_character_frames.py"),
    "--character", "cendre_pilot_test_v4",
    "--out-canvas", "64x64",
    "--foot-margin-px", "3",
    "--repo-root", SCRATCH,
]
for a in anim_args:
    cmd += ["--anim", a]
subprocess.run(cmd, check=True)
print("SCRATCH_ROOT", SCRATCH)
