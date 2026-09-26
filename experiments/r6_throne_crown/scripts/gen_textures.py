"""
Genere de vraies images de texture (color maps), seamless/tileables,
pour le trone/la couronne -- pas des Material tokens, de vraies images
PNG comme le texturing "niveau expert" le demande (voir README, section
"Texturing niveau expert").

Pourquoi generees et pas des Decal/Texture Roblox directement dans les
.rbxmx livres : `Texture`/`Decal` (le seul systeme qui marche sur un
`Part` -- `SurfaceAppearance`, le systeme PBR moderne, ne fonctionne QUE
sur `MeshPart`, verifie via recherche, voir README) exigent un
`rbxassetid://` pointant vers une image DEJA UPLOADEE sur le CDN de
Roblox. Cet upload demande un compte Roblox + Roblox Studio ou l'Open
Cloud API -- aucune des deux n'est accessible depuis ce sandbox. Les
PNG generes ici sont donc le livrable reel (a uploader par l'utilisateur
lui-meme, voir le guide dans le README), et sont EN PLUS utilises tels
quels par le lecteur HTML (lui, entierement sous mon controle) pour un
rendu par vraie texture plutot que par teinte plate.

Seamless SANS bord a raccorder a la main : chaque motif est une somme
d'ondes sin/cos a frequences ENTIERES sur la largeur/hauteur de l'image
-- une onde sin(2*pi*n*x/W) est exactement periodique sur W pixels par
construction, donc la mosaique est seamless par construction, pas par
un flou de bord approximatif.
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
        # rotation puis onde periodique -- toujours un nombre ENTIER de
        # cycles sur [0, size) dans chaque axe apres rotation entiere de
        # grille, donc toujours seamless.
        u = (x * np.cos(angle) - y * np.sin(angle))
        total += amp * np.sin(2 * np.pi * fx * u / size + phase)
        amp_sum += amp
        amp *= 0.55
    return total / amp_sum  # dans [-1, 1] environ


def to_u8(arr01):
    return np.clip(arr01 * 255.0, 0, 255).astype(np.uint8)


def save(name, rgb_u8):
    Image.fromarray(rgb_u8, mode="RGB").save(f"{OUT}/{name}.png")
    print(f"ecrit {OUT}/{name}.png")


def slate():
    n = periodic_noise(SIZE, 5, seed=1, freq_range=(3, 14))
    base = np.array([58, 56, 62], dtype=np.float64)
    dark = np.array([34, 33, 38], dtype=np.float64)
    t = (n + 1) / 2
    # bandes de clivage plus nettes (ardoise = strates), pas juste du
    # bruit lisse -- accentue les valeurs hautes de frequence via une
    # seconde couche de bruit fin qui vient strier localement.
    stripes = periodic_noise(SIZE, 2, seed=11, freq_range=(18, 30))
    t = np.clip(t + 0.15 * stripes, 0, 1)
    rgb = dark[None, None, :] + t[:, :, None] * (base - dark)[None, None, :]
    return to_u8(rgb / 255.0)


def marble():
    n1 = periodic_noise(SIZE, 4, seed=2, freq_range=(2, 6))
    n2 = periodic_noise(SIZE, 3, seed=3, freq_range=(6, 16))
    # veines classiques : |sin(turbulence)| donne des bandes fines qui
    # serpentent, motif marbre standard en synthese procedurale.
    veins = np.abs(np.sin((n1 * 6 + n2 * 2) * np.pi))
    veins = veins ** 4.5   # bandes plus fines et plus tranchees
    base = np.array([206, 200, 190], dtype=np.float64)
    vein_color = np.array([120, 108, 90], dtype=np.float64)   # contraste double vs 1re version
    rgb = base[None, None, :] * (1 - 0.55 * veins[:, :, None]) + vein_color[None, None, :] * (0.55 * veins[:, :, None])
    return to_u8(rgb / 255.0)


def metal_gold():
    # metal brosse : PEU de bandes, amples et nettes, plutot que
    # beaucoup de stries a des frequences proches qui s'annulent en
    # moyenne et donnent un aplat flou une fois tuile a petite echelle
    # (1re version : 40 stries quasi-aleatoires -> illisible une fois
    # affichee, corrige en revoyant a la baisse le nombre de bandes et
    # a la hausse leur amplitude individuelle -- trouve par capture
    # d'ecran reelle d'un test isole, pas suppose).
    x = np.mgrid[0:SIZE, 0:SIZE][1].astype(np.float64)
    rng = np.random.default_rng(4)
    stripes = np.zeros((SIZE, SIZE))
    n_bands = 6
    for _ in range(n_bands):
        fx = rng.integers(3, 9)
        phase = rng.uniform(0, 2 * np.pi)
        stripes += np.sin(2 * np.pi * fx * x / SIZE + phase)
    stripes /= n_bands
    n = periodic_noise(SIZE, 3, seed=5, freq_range=(2, 6))
    t = np.clip(0.5 + 0.55 * stripes + 0.12 * n, 0, 1)
    dark = np.array([98, 74, 22], dtype=np.float64)
    light = np.array([238, 202, 112], dtype=np.float64)
    rgb = dark[None, None, :] + t[:, :, None] * (light - dark)[None, None, :]
    return to_u8(rgb / 255.0)


def fabric():
    # tissage : grille periodique fine (motif exactement periodique,
    # pas du bruit) + une legere variation de teinte pour ne pas etre
    # plat.
    y, x = np.mgrid[0:SIZE, 0:SIZE]
    period = 8
    weave = 0.5 + 0.5 * np.sin(2 * np.pi * x / period) * np.sin(2 * np.pi * (y + x * 0.0) / period)
    weave2 = 0.5 + 0.5 * np.cos(2 * np.pi * (x + period / 2) / period) * np.cos(2 * np.pi * (y + period / 2) / period)
    t = 0.6 * weave + 0.4 * weave2
    n = periodic_noise(SIZE, 3, seed=6, freq_range=(4, 10))
    t = np.clip(t + 0.08 * n, 0, 1)
    dark = np.array([96, 24, 30], dtype=np.float64)
    light = np.array([150, 40, 46], dtype=np.float64)
    rgb = dark[None, None, :] + t[:, :, None] * (light - dark)[None, None, :]
    return to_u8(rgb / 255.0)


def wood():
    # Bois laque sombre (dais/pieds du trone, voir props.py apres passage
    # aux references visuelles utilisateur). Premier essai (7 bandes
    # proches en frequence + 15% de bruit isotrope) illisible une fois
    # rendu -- les bandes proches battaient entre elles ET contre le bruit
    # isotrope (qui varie en X ET en Y, contrairement au veinage qui ne
    # doit varier qu'en Y) au point de ressembler a un tissage/vannerie,
    # pas a du bois (trouve par capture d'ecran reelle, pas suppose --
    # meme categorie de bug que le metal a 40 bandes). Corrige : PEU de
    # bandes larges (contraste net, pas de quasi-annulation), des VEINES
    # fines et nettes (`|sin|` eleve a une puissance, meme technique que
    # marble()) toutes deux fonction de Y SEUL (paralleles au grain, donc
    # constantes selon X), et le bruit isotrope reduit a un flou tres
    # leger plutot qu'une composante dominante.
    y = np.mgrid[0:SIZE, 0:SIZE][0].astype(np.float64)
    rng = np.random.default_rng(8)
    stripes = np.zeros((SIZE, SIZE))
    amp, amp_sum, n_bands = 1.0, 0.0, 4
    for _ in range(n_bands):
        fy = rng.integers(3, 9)
        phase = rng.uniform(0, 2 * np.pi)
        stripes += amp * np.sin(2 * np.pi * fy * y / SIZE + phase)
        amp_sum += amp
        amp *= 0.7
    stripes /= amp_sum
    fine_veins = np.abs(np.sin(2 * np.pi * 23 * y / SIZE)) ** 6
    n = periodic_noise(SIZE, 2, seed=9, freq_range=(2, 5))
    t = np.clip(0.5 + 0.42 * stripes - 0.22 * fine_veins + 0.06 * n, 0, 1)
    dark = np.array([14, 9, 7], dtype=np.float64)
    light = np.array([70, 44, 28], dtype=np.float64)
    rgb = dark[None, None, :] + t[:, :, None] * (light - dark)[None, None, :]
    return to_u8(rgb / 255.0)


def cobblestone():
    n = periodic_noise(SIZE, 5, seed=7, freq_range=(4, 16))
    base = np.array([70, 66, 72], dtype=np.float64)
    dark = np.array([40, 38, 44], dtype=np.float64)
    t = (n + 1) / 2
    # "galets" : cellules grossieres via arrondi de bruit basse frequence
    # -- pas seamless-safe avec un simple floor(), donc on repasse par
    # une onde periodique en dents de scie plutot qu'un floor() direct.
    cell = periodic_noise(SIZE, 2, seed=17, freq_range=(6, 7))
    t = np.clip(t * 0.6 + (cell + 1) / 2 * 0.4, 0, 1)
    rgb = dark[None, None, :] + t[:, :, None] * (base - dark)[None, None, :]
    return to_u8(rgb / 255.0)


def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    save("slate_color", slate())
    save("marble_color", marble())
    save("metal_color", metal_gold())
    save("fabric_color", fabric())
    save("cobblestone_color", cobblestone())
    save("wood_color", wood())


if __name__ == "__main__":
    main()
