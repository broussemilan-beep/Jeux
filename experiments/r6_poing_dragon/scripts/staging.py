"""
Mise en scene du Poing du Dragon : piste CAMERA + chronologie des EFFETS,
calculees sur les FICHIERS exportes (relus par l'equation du moteur, comme
en jeu). Une seule source de verite pour le lecteur HTML et pour le module
Roblox (qui la recoit en table Luau).

Repere : celui de la scene = celui du HumanoidRootPart de l'attaquant au
lancement (attaquant a l'origine, regarde -Z). En jeu, tout point P de ce
fichier devient attaquantCFrame * P.

Grammaire tiree des references (corpus/REFERENCES_VIDEO.md) :
- rafale en plan moyen 3/4, qui accompagne ;
- coupe en contre-plongee basse pour l'anticipation (Black Flash) ;
- whip pan de 12 f vers un plan large en plongee pendant le temps suspendu
  (Serious Punch) ;
- dolly en contre-plongee pendant la plongee, gros plan au contact ;
- planches manga 3 x 2 f, ecran blanc, brouillard (Serious Punch) ;
- revelation de dos, tenue longue sur le cratere.

Usage : python3 staging.py   ->   ../output/staging.json
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "output")
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
sys.path.insert(0, HERE)

from animator_brain import roblox_export as X  # noqa: E402

SCENE = json.load(open(os.path.join(OUT, "scene.json")))
FPS = SCENE["fps"]
END = SCENE["end_f"]
D = SCENE["distance"]
M = dict(SCENE["markers"])
HITS = SCENE["hits"]

GOLD = "#ffc53d"
GOLD_DEEP = "#ff8a1f"
WHITE = "#fff6dc"
SMOKE = "#3b3530"
FLASH = "#ffb070"     # teinte plate du corps a l'impact : blanc-orange (l'or pur se confondait avec le jaune du noob)


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
    hv = (np.diag([-1.0, 1.0, -1.0]), np.array([0.0, 3.0, -D]))
    ka = X.read_kfseq(os.path.join(OUT, "dragon_attaquant.rbxmx"))
    kv = X.read_kfseq(os.path.join(OUT, "dragon_victime.rbxmx"))
    aw = [X.solve(resample(ka, f / FPS), root=ha) for f in range(END + 1)]
    vw = [X.solve(resample(kv, f / FPS), root=hv) for f in range(END + 1)]
    return aw, vw


def tip(w, part):
    r, p = w[part]
    return p + r @ np.array([0.0, -1.0, 0.0])


def v3(x):
    return [round(float(c), 3) for c in x]


def camera_keys(aw, vw):
    """(frame, oeil, cible, fov, entree) ; entree = "cut" (coupe franche a
    cette frame) ou "smooth" (interpolation douce depuis la cle precedente)."""
    A = lambda f: aw[f]["Torso"][1]  # noqa: E731
    Vt = lambda f: vw[f]["Torso"][1]  # noqa: E731
    mid = lambda f: (A(f) + Vt(f)) / 2  # noqa: E731
    K = []
    add = lambda f, eye, look, fov, mode="smooth": K.append((f, v3(eye), v3(look), fov, mode))  # noqa: E731
    # 1. rafale : plan moyen 3/4 avant-droit, qui accompagne le recul
    # v2 (retour de Milan, LECONS.md 2) : un angle different toutes les 2 frappes
    # plan A (coups 1-2) : moyen 3/4 avant-droit
    add(0, mid(0) + [10.5, 3.4, 3.0], mid(0) + [0, -0.2, 0], 46, "cut")
    add(50, mid(50) + [9.6, 3.0, 2.2], mid(50) + [0, -0.2, 0], 44)
    # plan B (coup 3, crochet) : contrechamp par-dessus l'epaule de la victime
    # (v2b : plein contrechamp bouche par le dos de la victime -> decale de cote)
    add(52, Vt(52) + [6.0, 1.9, -4.2], mid(52) + [0, 0.1, 0], 44, "cut")
    add(76, Vt(76) + [5.5, 1.7, -3.9], mid(76) + [0, 0.1, 0], 42)
    # plan C (coup 4 au corps, la victime decolle) : bas, cote gauche
    add(78, mid(78) + [-9.8, -1.7, 2.4], mid(78) + [0, 0.9, 0], 48, "cut")
    add(116, mid(116) + [-9.2, -1.5, 1.6], mid(116) + [0, 0.7, 0], 46)
    # 2. anticipation : COUPE, contre-plongee basse au ras du sol, pres de la fente
    a = A(132)
    add(118, [a[0] + 9.6, 1.0, a[2] + 0.6], a + [0, 1.0, -2.0], 44, "cut")
    add(146, [a[0] + 8.9, 0.9, a[2] + 0.3], a + [0, 0.9, -2.2], 42)
    # 3. uppercut : la camera suit la victime qui monte
    add(152, [a[0] + 9.0, 0.9, a[2] + 0.1], Vt(152) + [0, 0.5, 0], 50)
    add(172, [a[0] + 8.5, 1.8, a[2] - 2.4], mid(172) + [0, 1.0, 0], 56)
    add(196, mid(196) + [12.0, 1.0, 3.5], mid(196), 56)
    # 4. WHIP PAN (12 f) vers le plan large en plongee du temps suspendu
    add(208, A(208) + [5.4, 4.2, 7.2], A(208) + [0, -0.4, -0.8], 50)
    add(254, A(254) + [4.6, 3.4, 6.2], A(254) + [0, -0.2, -0.8], 46)
    # 5. plongee : dolly en contre-plongee depuis sous la victime
    add(258, Vt(258) + [6.8, -2.4, 2.2], A(258), 48, "cut")
    add(272, Vt(272) + [5.8, -1.6, 1.8], A(272) + [0, -1.0, 0], 44)
    c = tip(aw[SCENE["strike_f"]], "Right Arm")
    add(SCENE["strike_f"], c + [3.6, 1.0, 3.2], c, 42)
    imp = tip(aw[SCENE["impact_f"]], "Right Arm")
    add(SCENE["impact_f"], imp + [6.0, 2.6, 5.0], imp + [0, 0.6, 0], 46)
    # v2 (LECONS.md 3) : on RESTE sur l'impact 10 f, en reculant pour voir
    # l'onde de choc et les pics sortir du sol
    add(SCENE["manga_f"], imp + [9.0, 4.6, 7.6], imp + [0, 0.4, 0], 52)
    # 6. revelation (derriere l'ecran blanc) : de dos, un peu haut, cratere
    #    au premier plan, victime au loin
    r0 = A(SCENE["reveal_f"])
    far = Vt(END)
    add(SCENE["white"][0] + 10, r0 + [3.2, 4.4, 10.5], (r0 + far) / 2 + [0, -1.2, 0], 52, "cut")
    add(490, r0 + [2.7, 3.9, 9.0], (r0 + far) / 2 + [0, -1.0, 0], 50)
    add(END, r0 + [2.6, 4.0, 8.8], (r0 + far) / 2 + [0, -0.8, 0], 50)
    return K


def impact_dir(aw, f, side):
    """Sens du coup : de l'epaule vers le poing."""
    part = "Right Arm" if side == "R" else "Left Arm"
    r, p = aw[f][part]
    d = r @ np.array([0.0, -1.0, 0.0])
    return d / np.linalg.norm(d)


def events(aw, vw):
    """Chronologie des effets. `scale` suit le corpus VFX (coups legers au
    bas de la plage pro, finisher au p90)."""
    E = []
    ev = lambda f, kind, **kw: E.append(dict(frame=f, kind=kind, **kw))  # noqa: E731
    ev(0, "body_flash", who="attaquant", color=WHITE, frames=4)
    ev(0, "ground_burst", pos=v3([0, 0.05, 0]), color=GOLD, scale=0.8)
    # v2 : escalade (rules.check_escalade) -- hitstop, secousse et taille montent
    for i, (c, s, kind) in enumerate(HITS):
        p = tip(aw[c], "Right Arm" if s == "R" else "Left Arm")
        ev(c, "body_flash", who="attaquant", color=FLASH, frames=2)
        ev(c, "impact", pos=v3(p), dir=v3(impact_dir(aw, c, s)), scale=SCENE["hit_scale"][i], color=GOLD,
           hitstop=SCENE["hit_hitstop"][i], shake=SCENE["hit_shake"][i], name=f"hit{i + 1}")
    ev(122, "dust_trail", who="attaquant", frames=24)
    ev(126, "aura", who="attaquant", frames=24, color=GOLD, intensity=0.6)
    ev(126, "fist_glow", who="attaquant", side="R", frames=24, color=GOLD)
    u = SCENE["upper_f"]
    p = tip(aw[u], "Right Arm")
    ev(u, "body_flash", who="attaquant", color=FLASH, frames=3)
    ev(u, "impact", pos=v3(p), dir=v3(impact_dir(aw, u, "R")), scale=1.35, color=GOLD, hitstop=0.1, shake=0.5,
       name="uppercut")
    ev(170, "ground_burst", pos=v3([aw[170]["Torso"][1][0], 0.05, aw[170]["Torso"][1][2]]), color=WHITE, scale=1.2)
    ev(196, "whip", frames=12)
    ev(200, "aura", who="attaquant", frames=56, color=GOLD, intensity=1.0)
    ev(206, "fist_glow", who="attaquant", side="R", frames=72, color=GOLD)
    ev(236, "dragon", who="attaquant", side="R", frames=52, color=GOLD, smoke=SMOKE)
    sf = SCENE["strike_f"]
    p = tip(aw[sf], "Right Arm")
    ev(sf, "body_flash", who="attaquant", color=FLASH, frames=3)
    ev(sf, "impact", pos=v3(p), dir=v3(impact_dir(aw, sf, "R")), scale=1.6, color=GOLD, hitstop=0.13, shake=0.6,
       name="strike")
    imf = SCENE["impact_f"]
    ground = tip(aw[imf], "Right Arm")
    ground[1] = 0.0
    mf, wf = SCENE["manga_f"], SCENE["white"]
    ev(mf, "manga", frames=[mf, mf + 2, mf + 4, mf + 6])
    ev(wf[0], "white", frames=[wf[0], wf[0] + 12, wf[1]])
    ev(imf, "crater", pos=v3(ground), radius=7.5, spikes=34, seed=11)
    # l'impact au sol se VOIT : gel de 0,16 s puis onde de choc en dome
    ev(imf, "impact", pos=v3(ground + [0, 0.6, 0]), dir=[0, -1, 0], scale=2.4, color=GOLD, hitstop=0.16, shake=1.0,
       name="impact")
    ev(imf, "dome", pos=v3(ground), radius=11.0, frames=40, color=GOLD)
    ev(imf, "smoke_cloud", pos=v3(ground), radius=9.0, frames=END - imf, color="#7d7468")
    ev(imf, "embers", pos=v3(ground), frames=END - imf, color=GOLD_DEEP)
    return E


def main():
    aw, vw = tracks()
    data = {
        "fps": FPS, "end_f": END, "markers": M, "distance": D,
        "camera": camera_keys(aw, vw),
        "events": events(aw, vw),
        "palette": {"gold": GOLD, "gold_deep": GOLD_DEEP, "white": WHITE, "smoke": SMOKE},
    }
    json.dump(data, open(os.path.join(OUT, "staging.json"), "w"), indent=1)
    print("camera :", len(data["camera"]), "cles ;", len(data["events"]), "evenements")
    return data, aw, vw


if __name__ == "__main__":
    main()
