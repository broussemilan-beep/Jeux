"""Decoupe les feuilles de reference multi-vues (Milan, 2026-08-21) en
images individuelles par angle, pour alimentation Meshy image-to-3d /
multi-image-to-3d (qui attend une image nette par vue, pas une planche
avec titres/logo)."""

import os
from PIL import Image

SRC = "/root/.claude/uploads/e304835e-195c-5813-864a-d285531ad037"
OUT = "experiments/monsters_nuit/refs_v2"
os.makedirs(OUT, exist_ok=True)

JOBS = {
    "ranged": {
        "file": "a01b9e0e-30B39506F101417E9EF9D57F5C393BA0.png",
        "crops": {
            "face": (0, 190, 384, 1024),
            "threequarter": (384, 0, 768, 1024),
            "profile": (768, 0, 1152, 1024),
            "back": (1152, 0, 1536, 1024),
        },
    },
    "brute": {
        "file": "0462c03f-0E9B8545BCE741379D323E522C922FDB.png",
        "crops": {
            "face": (0, 170, 768, 512),
            "threequarter": (768, 0, 1536, 512),
            "profile": (0, 512, 768, 1024),
            "back": (768, 512, 1536, 1024),
        },
    },
    "crawler": {
        "file": "3e0018fc-8B8606C10CDF4D079836063752B65DA2.png",
        "crops": {
            "threequarter": (60, 150, 820, 650),
            "profile": (840, 150, 1536, 460),
            "threequarter_back": (560, 600, 1450, 1024),
        },
    },
}

for name, job in JOBS.items():
    im = Image.open(f"{SRC}/{job['file']}").convert("RGB")
    for angle, box in job["crops"].items():
        crop = im.crop(box)
        out_path = f"{OUT}/{name}_{angle}.png"
        crop.save(out_path)
        print("saved", out_path, crop.size)
