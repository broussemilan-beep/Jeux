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
OUT = os.environ.get("DRAGON_OUT") or os.path.join(HERE, "..", "output")  # DRAGON_OUT : variante A/B
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


CINEMA_DOSE = 0.7


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
    # 1. v6 RAFALE : TOUJOURS du cote +x (bras droit), jamais de passage de
    # l'autre cote de l'axe. Verifie a l'ecran (captures v5 et essais v6) :
    # de +x, les coups des DEUX bras se lisent (le bras part devant le torse) ;
    # de -x (v5 h3/h4) ou de dos (essai v6 « camera d'epaule »), le dos de
    # l'attaquant cache le poing. Camera vivante : un plan par coup, hauteur
    # et distance differentes, lente poussee dans chaque plan.
    add(0, mid(14) + [10.5, 3.0, 3.0], mid(14) + [0, -0.2, 0], 46, "cut")
    add(26, mid(26) + [9.6, 2.7, 2.6], mid(26) + [0, -0.2, 0], 44)
    add(28, mid(40) + [8.6, 1.3, 4.0], mid(40) + [0, 0.0, 0], 44, "cut")          # bas, 3/4 arriere
    add(50, mid(50) + [8.0, 1.2, 3.6], mid(50) + [0, 0.0, 0], 42)
    add(52, mid(64) + [9.2, 4.6, 1.4], mid(64) + [0, -0.4, 0], 44, "cut")         # plongee
    add(76, mid(76) + [8.6, 4.2, 1.2], mid(76) + [0, -0.4, 0], 42)
    # h4 (fente qui ferme la rafale, coup moyen) : profil franc, tenu sur les
    # deux pas de la charge
    add(78, mid(90) + [11.5, 1.2, 1.4], mid(90) + [0, -0.2, 0], 42, "cut")
    add(116, mid(116) + [10.4, 1.0, 1.0], mid(116) + [0, -0.2, 0], 42)
    # 2. v6 CHARGE : plan SERRE de profil, tete et epaules, la victime au bout
    # du regard (espace devant le visage). Le gros plan de face est ecarte : le
    # visage R6 a un sourire fixe, il ne porte aucune tension (essai v6 vu a
    # l'ecran). Le regard se lit par l'orientation de la tete. Lente poussee.
    h = lambda f: aw[f]["Head"][1]  # noqa: E731
    # v7 : le poing est arme HAUT au-dessus de la tete (charge « Serious
    # Punch ») ; cadre v6 (visee 1,2 sous la tete) -> le poing sortait du cadre
    # par le haut (vu sur la video v7). Visee a 0,5 sous la tete, un peu plus large.
    def regard(f):
        t = h(f) * 0.6 + Vt(f) * 0.4
        t[1] = h(f)[1] - 0.5
        return t
    add(126, h(126) + [8.6, -0.1, 1.0], regard(126), 46, "cut")
    add(145, h(145) + [7.6, -0.1, 0.8], regard(145), 44)
    # 3. COUP CHARGE : coupe sur l'action au depart (f146), profil moyen qui
    # montre le trajet A PLAT du poing ; gele au contact sous les cartes.
    # (Essai v6 « poing vers la camera » ecarte : dans l'axe du coup, le corps
    # de la victime est toujours entre l'objectif et le poing.)
    a = A(132)
    m2 = (a + Vt(150)) / 2
    add(146, m2 + [8.8, 0.6, 1.0], m2 + [0, -0.1, 0], 40, "cut")
    add(150, m2 + [8.2, 0.5, 0.9], m2 + [0, -0.1, 0], 38)
    # la consequence en TRES large (le coup a decide du combat), puis retour
    # sur l'attaquant pour l'envol
    add(151, mid(151) + [26.0, 6.0, 6.0], mid(151) + [0, 2.0, -1.0], 42, "cut")
    add(165, mid(165) + [24.0, 6.0, 5.0], mid(165) + [0, 3.0, -1.0], 42)
    add(166, [a[0] + 9.0, 1.2, a[2] - 1.0], A(166) + [0, 1.6, -0.8], 54, "cut")
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
    # v6 HIERARCHIE (ETUDE_VISUELLE.md) : l'effet est proportionnel au coup.
    # tier 1 = coup de base : eclat d'une image + un anneau, rien d'autre ;
    # tier 2 = coup moyen : + halo, etincelles, flash du corps, fond de vitesse
    tiers = [1, 1, 1, 2]
    for i, (c, s, kind) in enumerate(HITS):
        p = tip(aw[c], "Right Arm" if s == "R" else "Left Arm")
        if tiers[i] >= 2:
            ev(c, "body_flash", who="attaquant", color=FLASH, frames=2)
            ev(c, "vitesse", duration=0.1)
        ev(c, "impact", pos=v3(p), dir=v3(impact_dir(aw, c, s)), scale=SCENE["hit_scale"][i], color=GOLD,
           hitstop=SCENE["hit_hitstop"][i], shake=SCENE["hit_shake"][i], name=f"hit{i + 1}", tier=tiers[i])
    # v5 COUP CHARGE : aura et poing qui brillent PENDANT la tenue (la charge
    # se voit), poussiere au depart
    ev(124, "aura", who="attaquant", frames=24, color=GOLD, intensity=0.7)
    ev(124, "fist_glow", who="attaquant", side="R", frames=26, color=GOLD)
    ev(146, "dust_trail", who="attaquant", frames=14)
    u = SCENE["upper_f"]
    p = tip(aw[u], "Right Arm")
    d = impact_dir(aw, u, "R")
    # v6 IMPACT RACONTE (cartes d'impact, 24 refs sur 93) : le contact se voit
    # 3 f, puis noir + etoile, 3 cartes tirees de NOTRE pose, blanc ; l'animation
    # est gelee pendant toute la sequence (hitstop = sa duree), le blanc se
    # dissout sur la consequence. Plus courte que la sequence de l'aerien
    # (l'escalade garde f288 au-dessus).
    seq = [["contact", 0.05], ["noir", 0.10], ["carte", 0.067], ["carte", 0.067], ["carte", 0.067],
           ["blanc", 0.08]]
    gel = round(sum(x[1] for x in seq), 3)
    ev(u, "body_flash", who="attaquant", color=FLASH, frames=3)
    ev(u, "impact", pos=v3(p), dir=v3(d), scale=1.6, color=GOLD, hitstop=gel, shake=0.65, name="coup_charge", tier=3)
    # tenue_blanc : le blanc reste plein 0,02 s APRES le gel, le temps que
    # l'animation atteigne f151 et la coupe vers le plan large (vu a 60 i/s :
    # sans elle, 1 image du plan du contact passait sous le fondu)
    ev(u, "cartes", sequence=seq, fade=0.15, tenue_blanc=0.02)
    # l'explosion APRES le choc (sakuga 12/32 clips) : 2e souffle dans l'axe du
    # coup, derriere la victime, et onde au sol ; elle sort du blanc
    ev(u + 1, "impact", pos=v3(p + 1.6 * d), dir=v3(d), scale=1.9, color=WHITE, hitstop=0.0, shake=0.3,
       name="coup_charge_souffle", tier=3)
    g = p.copy()
    g[1] = 0.05
    ev(u + 1, "ground_burst", pos=v3(g), color=GOLD, scale=1.4)
    ev(u + 1, "dome", pos=v3(g), radius=5.0, frames=22, color=GOLD)
    ev(170, "ground_burst", pos=v3([aw[170]["Torso"][1][0], 0.05, aw[170]["Torso"][1][2]]), color=WHITE, scale=1.2)
    ev(196, "whip", frames=12)
    ev(200, "aura", who="attaquant", frames=56, color=GOLD, intensity=1.0)
    ev(206, "fist_glow", who="attaquant", side="R", frames=72, color=GOLD)
    ev(236, "dragon", who="attaquant", side="R", frames=52, color=GOLD, smoke=SMOKE)
    sf = SCENE["strike_f"]
    p = tip(aw[sf], "Right Arm")
    ev(sf, "body_flash", who="attaquant", color=FLASH, frames=3)
    ev(sf, "impact", pos=v3(p), dir=v3(impact_dir(aw, sf, "R")), scale=1.6, color=GOLD, hitstop=0.13, shake=0.6,
       name="strike", tier=3)
    imf = SCENE["impact_f"]
    ground = tip(aw[imf], "Right Arm")
    ground[1] = 0.0
    mf, wf = SCENE["manga_f"], SCENE["white"]
    ev(mf, "manga", frames=[mf, mf + 2, mf + 4, mf + 6])
    ev(wf[0], "white", frames=[wf[0], wf[0] + 12, wf[1]])
    ev(imf, "crater", pos=v3(ground), radius=7.5, spikes=34, seed=11)
    # l'impact au sol se VOIT : gel de 0,16 s puis onde de choc en dome
    ev(imf, "impact", pos=v3(ground + [0, 0.6, 0]), dir=[0, -1, 0], scale=2.4, color=GOLD, hitstop=0.16, shake=1.0,
       name="impact", tier=3)
    ev(imf, "dome", pos=v3(ground), radius=11.0, frames=40, color=GOLD)
    ev(imf, "smoke_cloud", pos=v3(ground), radius=9.0, frames=END - imf, color="#7d7468")
    ev(imf, "embers", pos=v3(ground), frames=END - imf, color=GOLD_DEEP)
    return E


def main():
    aw, vw = tracks()
    data = {
        "fps": FPS, "end_f": END, "markers": M, "distance": D,
        "camera": camera_keys(aw, vw),
        # v7 (Milan sur la v6 : camera cine « un peu trop abusee, mais leger ») :
        # secousse et punch-in de FOV doses a 70 % sous la camera CINEMATIQUE
        # seulement ; la camera de jeu (aimee) garde 100 %
        "cinema_dose": CINEMA_DOSE,
        "events": events(aw, vw),
        "palette": {"gold": GOLD, "gold_deep": GOLD_DEEP, "white": WHITE, "smoke": SMOKE},
    }
    json.dump(data, open(os.path.join(OUT, "staging.json"), "w"), indent=1)
    print("camera :", len(data["camera"]), "cles ;", len(data["events"]), "evenements")
    return data, aw, vw


if __name__ == "__main__":
    main()
