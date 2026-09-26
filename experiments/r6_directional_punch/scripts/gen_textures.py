"""
Genere de vraies images de texture (PNG), seamless/tileables, pour la
place d'entrainement du lecteur -- pas des teintes plates ("texturing
decore", retour utilisateur explicite). Meme technique que
r6_throne_crown/scripts/gen_textures.py (sommes d'ondes sin a
frequences ENTIERES -> seamless par construction, RNG seede -> images
deterministes, reproductibles a l'identique).

Contrairement au trone/couronne, ces textures ne sont PAS destinees a
un Material Roblox sur un Part exporte -- la place d'entrainement (sol,
mur en ruine, arriere-plan) est une mise en scene du LECTEUR seulement
(le livrable reel est le KeyframeSequence des deux personnages, voir
README "mise en scene du lecteur"), donc pas de pipeline SurfaceAppearance/
MeshPart ici : juste des PNG embarques tels quels dans le HTML.
"""
import numpy as np
from PIL import Image

OUT = "../textures"
SIZE = 256


def periodic_noise(size, octaves, seed, freq_range=(2, 10)):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:size, 0:size].astype(np.float64)
    total = np.zeros((size, size))
    amp = 1.0
    amp_sum = 0.0
    for _ in range(octaves):
        fx = rng.integers(*freq_range)
        fy = rng.integers(*freq_range)
        phase = rng.uniform(0, 2 * np.pi)
        angle = rng.uniform(0, 2 * np.pi)
        u = (x * np.cos(angle) - y * np.sin(angle))
        total += amp * np.sin(2 * np.pi * fx * u / size + phase)
        amp_sum += amp
        amp *= 0.55
    return total / amp_sum


def to_u8(arr01):
    return np.clip(arr01 * 255.0, 0, 255).astype(np.uint8)


def save(name, rgb_u8):
    import os
    os.makedirs(OUT, exist_ok=True)
    Image.fromarray(rgb_u8, mode="RGB").save(f"{OUT}/{name}.png")
    print(f"ecrit {OUT}/{name}.png")


def stone_ground():
    """Dallage de pierre : grille de dalles (joints sombres, PERIODIQUE
    -- un nombre entier de dalles sur SIZE pixels) + mouchetis de bruit
    par-dessus pour casser la repetition visuelle sans casser le
    seamless (le bruit lui-meme est periodique, voir periodic_noise)."""
    n_tiles = 8
    y, x = np.mgrid[0:SIZE, 0:SIZE]
    tile_x = (x % (SIZE // n_tiles))
    tile_y = (y % (SIZE // n_tiles))
    edge = np.minimum(np.minimum(tile_x, SIZE // n_tiles - 1 - tile_x),
                       np.minimum(tile_y, SIZE // n_tiles - 1 - tile_y))
    joint = (edge < 2).astype(np.float64)

    base = 0.62 + 0.10 * periodic_noise(SIZE, 4, seed=11, freq_range=(3, 9))
    speckle = 0.05 * periodic_noise(SIZE, 3, seed=12, freq_range=(14, 28))
    gray = np.clip(base + speckle, 0, 1)
    gray = gray * (1 - 0.55 * joint)  # joints assombris

    r = gray * 0.92
    g = gray * 0.90
    b = gray * 0.86
    rgb = np.stack([to_u8(r), to_u8(g), to_u8(b)], axis=-1)
    save("stone_ground", rgb)


def ruin_wall():
    """Mur de pierre use : bandes de blocs horizontales + bruit de
    fissures (contraste fort, sombre) -- silhouette de ruines a
    l'arriere-plan, pas un mur destine a un gros plan."""
    n_rows = 6
    y, x = np.mgrid[0:SIZE, 0:SIZE]
    row_h = SIZE // n_rows
    row = (y // row_h) % 2
    block_w = SIZE // 5
    offset = row * (block_w // 2)
    block_x = (x + offset) % block_w
    joint = ((block_x < 2) | (y % row_h < 2)).astype(np.float64)

    base = 0.42 + 0.12 * periodic_noise(SIZE, 5, seed=21, freq_range=(2, 7))
    crack = periodic_noise(SIZE, 3, seed=22, freq_range=(9, 18))
    crack_mask = (np.abs(crack) > 0.93).astype(np.float64)
    gray = np.clip(base - 0.5 * joint - 0.30 * crack_mask, 0.05, 1)

    r = gray * 0.88
    g = gray * 0.85
    b = gray * 0.83
    rgb = np.stack([to_u8(r), to_u8(g), to_u8(b)], axis=-1)
    save("ruin_wall", rgb)


if __name__ == "__main__":
    stone_ground()
    ruin_wall()
