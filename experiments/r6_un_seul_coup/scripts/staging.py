"""
Mise en scène de « Un seul coup » : caméra, décor (plaine, montagnes, nuages),
la DESTRUCTION (sillon de roches jusqu'à l'horizon, colonnes de fumée,
nuages qui se fendent), effets et sons. Calculée sur les FICHIERS exportés
(relus par l'équation du moteur, comme en jeu) : une seule source de vérité
pour le lecteur HTML et pour le module Roblox.

Conception : animator_brain/corpus/fiches/UN_SEUL_COUP.md.
Repère : celui du HumanoidRootPart de l'attaquant au lancement (origine,
regarde -Z). En jeu, tout point P devient attaquantCFrame * P.

Usage : python3 staging.py   ->   ../output/staging.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("USC_OUT") or os.path.join(HERE, "..", "output")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
from animator_brain import roblox_export as X  # noqa: E402

SCENE = json.load(open(os.path.join(OUT, "scene.json")))
FPS = SCENE["fps"]
END = SCENE["end_f"]
DV = SCENE["distance"]
M = dict(SCENE["markers"])
CF = SCENE["contact_f"]
T_CONTACT = CF / FPS

# la destruction (fiche §3) : la vague file à VITESSE studs/s jusqu'à PORTEE
VITESSE = 250.0
PORTEE = 470.0
MONTAGNE_Z = 520.0          # la montagne dans l'axe : la vague s'y écrase


def resample(keys, t):
    ts = [k[0] for k in keys]
    i = max(0, min(len(ts) - 2, int(np.searchsorted(ts, t, side="right")) - 1))
    u = min(1.0, max(0.0, (t - ts[i]) / (ts[i + 1] - ts[i])))
    out = {}
    for p in keys[i][1]:
        (ra, pa), (rb, pb) = keys[i][1][p], keys[i + 1][1][p]
        out[p] = (X._slerp_rot(ra, rb, u), pa + (pb - pa) * u)
    return out


def tracks():
    ha = (np.eye(3), np.array([0.0, 3.0, 0.0]))
    hv = (np.diag([-1.0, 1.0, -1.0]), np.array([0.0, 3.0, -DV]))
    ka = X.read_kfseq(os.path.join(OUT, "usc_attaquant.rbxmx"))
    kv = X.read_kfseq(os.path.join(OUT, "usc_victime.rbxmx"))
    aw = [X.solve(resample(ka, f / FPS), root=ha) for f in range(END + 1)]
    vw = [X.solve(resample(kv, f / FPS), root=hv) for f in range(END + 1)]
    return aw, vw


def tip(w, part):
    r, p = w[part]
    return p + r @ np.array([0.0, -1.0, 0.0])


def v3(x):
    return [round(float(c), 3) for c in x]


# ---------------------------------------------------------------- caméra
def camera_keys(aw, vw):
    """(frame, oeil, cible, fov, entree) ; entree = "cut" ou "smooth"."""
    A = lambda f: aw[f]["Torso"][1]  # noqa: E731
    Hd = lambda f: aw[f]["Head"][1]  # noqa: E731
    K = []
    add = lambda f, eye, look, fov, mode="smooth": K.append((f, v3(eye), v3(look), fov, mode))  # noqa: E731
    # 1. ENTRÉE : de dos, bas ; la plaine, la victime au loin ; la caméra
    #    pousse jusque DANS son dos (le dos remplit l'écran = transition)
    add(0, [3.4, 2.5, 11.5], [-0.4, 3.0, -16.0], 44, "cut")
    add(56, [1.0, 3.4, 3.4], [0.0, 3.4, -16.0], 50)
    add(M["calme"], [0.25, 3.6, 0.95], [0.0, 3.6, -12.0], 56)
    # 2. CALME : plan moyen de FACE, fixe, un peu en contre-plongée
    add(M["calme"] + 1, [1.3, 2.3, -7.6], [0.0, 3.7, 0.0], 38, "cut")
    add(M["depart"] - 1, [1.2, 2.35, -7.1], [0.0, 3.7, 0.0], 38)
    # 3. DÉPART (v2, retour de Milan : « il va ultra vite, tu casses le sol de
    #    son point de départ ») : plan serré et bas sur ses jambes ; il se
    #    ramasse, le sol CASSE, il n'est plus là ; on reste sur le trou
    #    (1er essai à 4,6 studs : on ne voyait que ses jambes, puis la
    #    poussière remplissait l'écran) ; cadré de profil, en entier, la
    #    destination hors champ à gauche (le sillage y file)
    add(M["depart"], [8.4, 1.8, 0.9], [0.0, 2.4, 0.9], 46, "cut")
    add(M["charge"] - 1, [9.0, 2.0, 1.2], [0.0, 2.0, 0.9], 48)
    # 4. LA CHARGE (v3) : de face / profil côté poitrine (il se met de
    #    profil, poitrine vers +x) : on voit l'arc se tendre, les deux bras
    #    alignés (poing derrière à gauche, l'autre bras vers la victime à
    #    droite) ; poussée lente pendant la tenue
    a = A(214)
    #    (1er cadrage à 7 studs : jambes coupées, victime qui mangeait le cadre)
    add(M["charge"], a + [10.5, 0.2, -0.6], a + [0.0, -0.1, -2.0], 42, "cut")
    add(M["frappe"], a + [8.6, 0.0, -0.6], a + [0.0, 0.0, -1.9], 40)
    # 6. FRAPPE : REGARD DE LA VICTIME (elle est masquée) ; la caméra est à
    #    hauteur du point touché : le poing arrive À PLAT dans l'objectif
    tg = np.asarray(SCENE["contact_tgt"], float)
    eye = tg + np.array([-0.25, 0.2, -0.6])
    for f in (M["frappe"] + 1, 276, 279, CF - 1):
        fist = tip(aw[f], "Right Arm")
        add(f, eye, fist * 0.6 + Hd(f) * 0.4, 70, "cut" if f == M["frappe"] + 1 else "smooth")
    # 7. images inversées : 1re = la fente de 3/4 au contact (le plan
    #    « poing vers l'objectif » donnait une image noire aux 2/3) ;
    #    2e = plan large, la ligne vers l'horizon
    add(CF, A(CF) + [13.0, 0.6, -3.5], A(CF) + [0.0, -0.3, -3.5], 40, "cut")
    add(286, A(CF) + [13.0, 0.6, -3.5], A(CF) + [0.0, -0.3, -3.5], 40)
    a_end = A(END)
    add(287, a_end + [16.0, 3.0, 6.0], a_end + [0.0, 2.0, -70.0], 48, "cut")
    add(290, a_end + [16.0, 3.0, 6.0], a_end + [0.0, 2.0, -70.0], 48)
    # 8. CONSÉQUENCE 1 : de DOS, un peu haut, fixe ; poussée très lente
    c1, c2, c3 = SCENE["consequence"]
    ac = A(c1)
    # (de dos dans l'axe, le sillon se referme en perspective : vu à 0,1 s,
    # il semblait s'arrêter à 60 studs ; de 3/4 haut, il file en diagonale
    # jusqu'à l'horizon, comme la 2e image inversée)
    add(291, ac + [12.0, 7.5, 17.0], ac + [-3.0, -3.0, -60.0], 48, "cut")
    add(c2 - 1, ac + [10.2, 6.8, 14.5], ac + [-3.0, -2.6, -60.0], 48)
    # 9. CONSÉQUENCE 2 : haut, derrière lui ; la ligne et le ciel qui se fend
    #    (au-dessus des nuages : le sillon apparaît DANS la fente du ciel)
    add(c2, ac + [8.0, 215.0, 75.0], ac + [0.0, 0.0, -230.0], 55, "cut")
    add(c3 - 1, ac + [6.0, 205.0, 52.0], ac + [0.0, 0.0, -240.0], 55)
    # 10. CONSÉQUENCE 3 : profil bas, lui à gauche, la ligne jusqu'à l'horizon
    add(c3, ac + [17.0, 0.2, 8.0], ac + [0.0, 1.2, -9.0], 40, "cut")
    add(END, ac + [15.0, 0.3, 6.6], ac + [0.0, 1.4, -8.0], 38)
    return K


# ---------------------------------------------------------------- décor
def decor(aw):
    rng = np.random.default_rng(7)
    fist = tip(aw[CF], "Right Arm")
    x0, z0 = float(fist[0]), float(fist[2])
    roches = []
    # deux MURS de dalles soulevées de part et d'autre d'un sillon ; la
    # vague part du poing et file le long de -Z (fiche : Pew, TSB)
    for cote in (-1, 1):
        d = 2.5
        while d < PORTEE:
            # le V s'OUVRE avec la distance (1er essai à taille presque
            # constante : vu de loin, la ligne n'était qu'un trait de fumée)
            taille = 2.0 + 3.2 * (1 - np.exp(-d / 20.0)) + 0.045 * d
            demi = 2.6 + 0.11 * d + 2.0 * (1 - np.exp(-d / 12.0))
            for couche in range(1 if d < 12 else (2 if d < 60 else 3)):
                s = taille * rng.uniform(0.7, 1.15) * (1.0 if couche == 0 else 0.7)
                x = x0 + cote * (demi + couche * 0.8 * taille + rng.uniform(-0.3, 0.6) * taille * 0.5)
                z = z0 - d + rng.uniform(-0.4, 0.4) * taille
                t = T_CONTACT + 0.02 + d / VITESSE + rng.uniform(0, 0.05)
                roches.append({
                    "p": [round(x, 2), round(z, 2)],
                    "s": [round(s * rng.uniform(0.8, 1.3), 2), round(s * rng.uniform(1.0, 1.6), 2), round(s * rng.uniform(0.8, 1.3), 2)],
                    # penchée VERS L'EXTÉRIEUR (poussée par le coup), tournée au hasard
                    "r": [round(float(rng.uniform(-12, 12)), 1), round(float(rng.uniform(0, 90)), 1),
                          round(float(-cote * rng.uniform(14, 38)), 1)],
                    "t": round(t, 3), "c": int(rng.integers(0, 3))})
            d += taille * rng.uniform(0.35, 0.55)
    # le fond du sillon (bande sombre qui s'ouvre avec la vague)
    sillon = {"x": round(x0, 2), "z0": round(z0, 2), "long": PORTEE, "l0": 2.4, "l1": 2.4 + 0.11 * PORTEE}
    # colonnes de fumée blanche : tous les ~14 studs, des deux côtés
    fumees = []
    d = 6.0
    while d < PORTEE:
        demi = 2.6 + 0.11 * d + 2.0
        for cote in (-1, 1):
            fumees.append({"p": [round(x0 + cote * demi * rng.uniform(0.9, 1.4), 2), round(z0 - d, 2)],
                           "t": round(T_CONTACT + d / VITESSE + rng.uniform(0.05, 0.3), 3),
                           "h": round(float(9 + 0.1 * d + rng.uniform(0, 6)), 1),
                           "r": round(float(2.5 + 0.045 * d + rng.uniform(0, 1.5)), 1)})
        d += rng.uniform(12, 20) + 0.04 * d
    # montagnes : un anneau loin, dont UNE dans l'axe du coup
    montagnes = []
    for k in range(34):
        a = 2 * np.pi * k / 34 + rng.uniform(-0.05, 0.05)
        R = rng.uniform(520, 680)
        montagnes.append({"p": [round(float(np.sin(a) * R), 1), round(float(-np.cos(a) * R), 1)],
                          "h": round(float(rng.uniform(45, 115)), 1), "r": round(float(rng.uniform(70, 130)), 1)})
    montagnes.append({"p": [round(x0 - 10, 1), round(-MONTAGNE_Z - 30, 1)], "h": 120.0, "r": 110.0})
    # nuages : amas de boules aplaties, couche à ~110-150 studs
    nuages = []
    for k in range(120):
        cx, cz = rng.uniform(-320, 320), rng.uniform(-700, 80)
        boules = [[round(float(rng.uniform(-22, 22)), 1), round(float(rng.uniform(-3, 5)), 1), round(float(rng.uniform(-14, 14)), 1),
                   round(float(rng.uniform(9, 20)), 1)] for _ in range(int(rng.integers(4, 8)))]
        nuages.append({"p": [round(float(cx), 1), round(float(rng.uniform(110, 150)), 1), round(float(cz), 1)], "b": boules})
    # les nuages dans l'axe s'écartent quand l'onde les atteint (sillon bleu)
    # (elle s'ouvre PENDANT le plan au-dessus des nuages, sinon on ne la voit pas s'ouvrir)
    fente = {"x": round(x0, 2), "t0": round(SCENE["consequence"][1] / FPS + 0.1, 3), "vitesse": 420.0, "largeur": 120.0,
             "ecart": 75.0, "duree": 2.4}
    return {"roches": roches, "sillon": sillon, "fumees": fumees, "montagnes": montagnes, "nuages": nuages,
            "fente": fente, "vitesse": VITESSE, "portee": PORTEE,
            "choc_montagne": {"p": [round(x0, 1), round(-MONTAGNE_Z, 1)], "t": round(T_CONTACT + (MONTAGNE_Z + z0) / VITESSE, 3)}}


# ---------------------------------------------------------------- effets
def events(aw, vw):
    E = []
    ev = lambda f, kind, **kw: E.append(dict(frame=f, kind=kind, **kw))  # noqa: E731
    # DÉPART : le sol casse sous lui (cratère, dalles soulevées, poussière),
    # et un sillage de poussière file jusqu'à la victime (il est passé là)
    lf = M["lance"]
    arr = aw[lf + 4]["Torso"][1]
    ev(lf, "depart_sol", pos=[0.0, 0.0, 0.3], rayon=2.6)
    ev(lf + 1, "sillage", de=[0.0, 0.3], a=[round(float(arr[0]), 2), round(float(arr[2]) + 1.2, 2)])
    # la CHARGE se voit : cailloux qui se soulèvent autour de ses pieds, vent
    # qui tourne autour du poing
    ev(M["charge"], "charge_sol", pos=v3([arr[0], 0.05, aw[M["charge"]]["Torso"][1][2]]), fin=CF)
    ev(M["charge"] + 4, "tourbillon", fin=CF + 3, bras="Right Arm")
    # impact : 2 images inversées, blanc, dissolution
    i0, i1 = SCENE["inverse"]
    b0, b1 = SCENE["blanc"]
    ev(i0, "inverse", fin=i1)
    ev(b0, "blanc", plein=b0 + 12, fin=b1)
    ev(lf, "secousse", fin=lf + 22, amp=0.3)
    ev(CF, "secousse", fin=CF + 150, amp=0.45)
    ev(CF, "souffle_sol", pos=v3([tip(aw[CF], "Right Arm")[0], 0.05, tip(aw[CF], "Right Arm")[2]]))
    ev(M["charge"], "cacher_victime", debut=470, pov=[M["frappe"] + 1, CF])
    ev(END - 20, "fondu_noir", fin=END)
    return E


def sons():
    """(temps réel s, son, volume, hauteur) -- sons du studio (vfx_studio/sons)."""
    t = T_CONTACT
    S = [(0.0, "vent_ambiant", 0.45, 1.0), (3.2, "vent_ambiant", 0.3, 0.9),
         # départ : le sol casse (grave), le vent de son passage
         (2.833, "impact_lourd", 0.75, 0.5), (2.853, "vent_arc", 0.8, 0.7), (2.883, "grondement", 0.45, 0.8),
         # la charge : un grondement sourd qui monte, puis l'aspiration
         (3.35, "grondement", 0.22, 0.4), (3.95, "grondement", 0.28, 0.45),
         (4.05, "aspiration", 0.9, 0.7),
         (t - 0.46, "souffle_projectile", 0.7, 0.85),
         (t, "impact_lourd", 1.0, 0.75), (t + 0.08, "grondement", 0.9, 0.7),
         (t + 0.6, "grondement", 0.75, 0.55), (t + 1.2, "vent_ambiant", 0.8, 1.0),
         (t + 1.3, "grondement", 0.5, 0.5), (t + 2.0, "grondement", 0.3, 0.45),
         (t + 3.9, "vent_ambiant", 0.45, 0.95), (t + 5.6, "vent_ambiant", 0.25, 0.9),
         (t + 4.1, "frappe_m1", 0.1, 1.6), (t + 4.7, "frappe_m1", 0.08, 1.8), (t + 6.2, "frappe_m1", 0.07, 1.7)]
    return [{"t": round(a, 3), "son": b, "volume": c, "hauteur": d} for a, b, c, d in S]


def main():
    aw, vw = tracks()
    data = {"fps": FPS, "end_f": END, "distance": DV, "markers": SCENE["markers"], "contact_f": CF,
            "camera": camera_keys(aw, vw), "events": events(aw, vw), "decor": decor(aw), "sons": sons(),
            "beats": [["Entrée", 0, M["calme"]], ["Calme", M["calme"], M["depart"]], ["Départ", M["depart"], M["charge"]],
                      ["Charge", M["charge"], M["frappe"]], ["Frappe", M["frappe"], CF],
                      ["Impact", CF, SCENE["consequence"][0]], ["Conséquence", SCENE["consequence"][0], SCENE["redresse"][0]],
                      ["Il se redresse", SCENE["redresse"][0], END + 1]]}
    json.dump(data, open(os.path.join(OUT, "staging.json"), "w"), indent=1)
    return data, aw, vw


if __name__ == "__main__":
    d, _a, _v = main()
    print(len(d["decor"]["roches"]), "roches,", len(d["decor"]["fumees"]), "fumées,", len(d["camera"]), "clés caméra")
