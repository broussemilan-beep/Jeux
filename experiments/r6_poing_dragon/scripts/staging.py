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

sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared", "vfx_studio"))
import recettes as R  # noqa: E402  (studio VFX : les MÊMES recettes que le labo et le moteur Roblox)
import scene_v13  # noqa: E402  (v13 : tout ce qui suit l'apex)

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
V13 = SCENE.get("aerien") == "v13"
_SC13 = {}


def scene13(aw, vw):
    if "sc" not in _SC13:
        _SC13["sc"] = scene_v13.Scene13(aw, vw, SCENE, tip)
    return _SC13["sc"]


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
    if V13:
        scene_v13.camera(scene13(aw, vw), add, A, Vt, h)
        return K
    c = tip(aw[SCENE["strike_f"]], "Right Arm")
    if SCENE.get("aerien", "v8") == "v8":
        # 4. WHIP PAN (12 f) vers le plan large en plongee du temps suspendu
        add(208, A(208) + [5.4, 4.2, 7.2], A(208) + [0, -0.4, -0.8], 50)
        add(254, A(254) + [4.6, 3.4, 6.2], A(254) + [0, -0.2, -0.8], 46)
        # 5. plongee : dolly en contre-plongee depuis sous la victime
        add(258, Vt(258) + [6.8, -2.4, 2.2], A(258), 48, "cut")
        add(272, Vt(272) + [5.8, -1.6, 1.8], A(272) + [0, -1.0, 0], 44)
        add(SCENE["strike_f"], c + [3.6, 1.0, 3.2], c, 42)
    else:
        # v9 (fiche COUP_CHARGE.md, grammaire du Serious Punch) :
        # 4. le whip pan arrive sur le CALME : plan moyen de FACE, fixe,
        #    legerement en contre-plongee (il domine), presque rien ne bouge
        add(208, A(208) + [1.6, -1.2, -9.4], A(208) + [0, 0.1, 0], 40)
        add(227, A(227) + [1.5, -1.1, -9.0], A(227) + [0, 0.1, 0], 40)
        # 5. coupe SUR L'ACTION (milieu du depart) : l'arme, corps entier, de
        #    PROFIL cote du poing arme, un peu en contre-plongee. Le bras qui
        #    vise la victime part sur le cote du cadre, jamais vers l'objectif
        #    (1er essai de face : il cachait tout, repro/README.md lecon 5)
        if str(SCENE.get("aerien", "")).startswith("v10"):
            # v10 INVOCATION (Goku, GIF f254bee5) : contre-plongée de face, on
            # le voit d'en dessous lever le poing vers le ciel, le dragon
            # s'enroule autour du bras et dresse la tête au-dessus du poing
            # (v10a : trop bas et trop loin, -22° à 9 studs -> on voyait le
            # DESSOUS du corps, tête cachée, poing hors lecture) -> 3/4 face
            # côté poing levé, -10°, corps + poing + tête du dragon dans le cadre
            # (v10b : cadre trop serré, poing et tête du dragon hors champ)
            add(228, A(234) + [4.6, -1.0, -10.2], A(240) + [0.8, 2.5, 0.0], 58, "cut")
            add(255, A(255) + [4.0, -0.9, -9.0], A(255) + [0.8, 2.7, 0.0], 56)
        else:
            add(228, A(234) + [8.4, -1.2, -1.5], A(234) + [0, -0.2, -0.7], 46, "cut")
            add(255, A(255) + [7.4, -1.05, -1.3], A(255) + [0, -0.2, -0.7], 44)
        # 6. OBARI : la camera est chez la victime, a cote d'elle (jamais entre
        #    l'objectif et le poing) ; le poing vient VERS l'objectif et
        #    grossit jusqu'a remplir le cadre ; la visee suit le poing et la tete
        # v10 : le bras tendu d'Izuku traversait le plan proche de l'objectif
        # (vu : un « prisme » brun qui masquait tout) -> œil plus bas et plus
        # sur le côté : contre-plongée sur le poing qui arrive
        eye = Vt(SCENE["strike_f"]) + ([-2.0, 0.5, -1.3] if str(SCENE.get("aerien", "")).startswith("v10") else [-1.1, 1.3, -0.2])
        for f in (256, 260, 263, 266, 270, 274, SCENE["strike_f"]):
            fist = tip(aw[f], "Right Arm")
            add(f, eye, fist * 0.55 + h(f) * 0.45, 78, "cut" if f == 256 else "smooth")
        # 7. la chute, de cote (coupe apres le gel du contact)
        # (1er essai visant le poing : l'attaquant n'entrait dans le cadre
        #  qu'a mi-chute) -> visee entre les deux corps
        add(SCENE["strike_f"] + 1, mid(283) + [8.0, 0.8, 4.2], mid(283) + [0, -1.5, 0], 52, "cut")
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
    ev(170, "ground_burst", pos=v3([aw[170]["Torso"][1][0], 0.05, aw[170]["Torso"][1][2]]), color=WHITE, scale=1.2)
    if V13:
        scene_v13.evenements(scene13(aw, vw), ev, GOLD, WHITE, FLASH)
        for e in E:
            if e["kind"] == "impact":
                e["studio"] = True
        E += studio_events(aw, vw, E)
        return E
    ev(196, "whip", frames=12)
    if SCENE.get("aerien", "v8") == "v8":
        ev(200, "aura", who="attaquant", frames=56, color=GOLD, intensity=1.0)
        ev(206, "fist_glow", who="attaquant", side="R", frames=72, color=GOLD)
    else:
        # v9 : le CALME n'a pas d'aura ; elle s'allume avec l'arme
        ev(226, "aura", who="attaquant", frames=30, color=GOLD, intensity=1.0)
        ev(228, "fist_glow", who="attaquant", side="R", frames=50, color=GOLD)
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
    ev(imf, "smoke_cloud", pos=v3(ground), radius=9.0, frames=END - imf, color="#7d7468")
    ev(imf, "embers", pos=v3(ground), frames=END - imf, color=GOLD_DEEP)
    # studio VFX : les impacts sont désormais joués par ses recettes ; les
    # événements « impact » gardent hitstop, secousse et punch-in de FOV
    for e in E:
        if e["kind"] == "impact":
            e["studio"] = True
    E += studio_events(aw, vw, E)
    return E


def _reechantillonne(pts, n):
    """Polyligne -> n points équidistants (abscisse curviligne)."""
    pts = np.asarray(pts, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    if d[-1] < 1e-9:
        return np.repeat(pts[:1], n, axis=0)
    u = np.linspace(0, d[-1], n)
    return np.stack([np.interp(u, d, pts[:, k]) for k in range(3)], axis=1)


def _helice(a, b, rayon, tours, phase, n=40, rayon_fin=None):
    """Hélice autour du segment a -> b (de a vers b)."""
    ax = b - a
    ln = np.linalg.norm(ax)
    ax = ax / ln
    ref = np.array([0.0, 1, 0]) if abs(ax[1]) < 0.9 else np.array([1.0, 0, 0])
    e1 = np.cross(ax, ref)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    out = []
    for k in range(n):
        u = k / (n - 1)
        r = rayon + ((rayon_fin if rayon_fin is not None else rayon) - rayon) * u
        ang = phase + 2 * np.pi * tours * u
        out.append(a + ax * ln * u + r * (np.cos(ang) * e1 + np.sin(ang) * e2))
    return out


def dragon_events(aw, vw, rt, studio):
    """Le DRAGON (Goku) + les ÉCLAIRS VERTS (Izuku), en trois temps : il sort
    du poing et s'enroule autour du bras puis du corps (armé), part avec le
    poing (plongée), puis sort du tourbillon de l'impact et monte vers le
    ciel (révélation). Forme calculée ici, sur les pistes réelles, à 30 Hz."""
    NP = 28
    fa0, sf, imf = 236, SCENE["strike_f"], SCENE["impact_f"]
    vict = vw[sf]["Torso"][1]

    def poing(f):
        return tip(aw[f], "Right Arm")

    def epaule(f):
        r, p = aw[f]["Right Arm"]
        return p + r @ np.array([0.0, 1.0, 0.0])

    def enroule(f, t):
        """Armé : tête au-dessus-devant du poing, hélice autour du bras,
        puis grande hélice qui descend derrière le corps."""
        F, Sh = poing(f), epaule(f)
        rt_, T = aw[f]["Torso"]
        up = rt_ @ np.array([0.0, 1, 0])
        vis = (vict - F) / np.linalg.norm(vict - F)
        if str(SCENE.get("aerien", "")).startswith("v10"):
            # v10 : poing levé au ciel -> la tête se dresse AU-DESSUS du poing,
            # tournée vers la victime (l'affiche e92ac0d7)
            # v10b : la 1re version dressait le cou à la VERTICALE (un pilier
            # doré, gueule vers le ciel) ; sur l'affiche le cou monte puis la
            # tête se COURBE vers l'adversaire, gueule ouverte sur lui
            # (2e essai : visée vers la victime, qui est EN BAS -> tête piquée
            # vers le sol, on ne voyait que le haut du crâne et la crinière
            # emmêlée au poing) -> tête HORIZONTALE, de profil, devant et
            # au-dessus du poing, détachée de lui
            y = np.array([0.0, 1.0, 0.0])
            vh = np.array([vis[0], 0.0, vis[2]])
            vh = vh / (np.linalg.norm(vh) + 1e-9)
            H = F + y * 2.1 + vh * 1.5
            pts = [H, H - vh * 1.1 + y * 0.25, F + y * 1.3 - vh * 0.2]
        else:
            H = F + vis * 1.2 + up * 0.7
            pts = [H, (H + F) / 2 + up * 0.3]
        phi = 2.4 * t
        haut, bas = T + up * 1.6, T - up * 3.2
        if str(SCENE.get("aerien", "")).startswith("v10"):
            # l'affiche : le perso DEVANT, le dragon DERRIÈRE lui (3e essai : les
            # spires autour du bras passaient devant le visage) -> spires
            # décalées vers l'arrière (loin de la victime et de la caméra)
            recul = -vh * 1.7
            pts += [p + recul * 0.6 for p in _helice(F, Sh, 0.7, 1.2, phi, 30)]
            pts += [p + recul for p in _helice(haut, bas, 2.2, 1.3, phi * 0.6 + 2.0, 50, rayon_fin=1.7)]
        else:
            pts += _helice(F, Sh, 1.0, 1.5, phi, 30)
            pts += _helice(haut, bas, 2.4, 1.3, phi * 0.6 + 2.0, 50, rayon_fin=1.7)
        return _reechantillonne(pts, NP)

    def file(f, t):
        """Plongée : tête devant le poing (à CÔTÉ, pour ne pas cacher le poing
        en caméra obari), corps sur le trajet réel du poing, en spirale."""
        F = poing(f)
        d = poing(min(sf, f + 1)) - poing(max(fa0, f - 1))
        d = d / (np.linalg.norm(d) + 1e-9)
        lat = np.cross(d, [0.0, 1, 0])
        lat = lat / (np.linalg.norm(lat) + 1e-9)
        # (essais d*1,4 + lat*1,1 puis d*2,1 : la tête DEVANT le poing passe
        # derrière la caméra obari, qui est chez la victime -> à côté et
        # au-dessus du poing, un peu en retrait)
        # plus le poing approche (caméra obari chez la victime), plus la tête
        # s'ÉCARTE vers le haut : elle ne doit jamais cacher le poing au contact
        w = np.clip((f - 256) / (sf - 256), 0, 1) ** 1.5
        H = F - d * 0.3 - lat * (1.1 + 2.2 * w) + np.array([0.0, 1.3 + 3.0 * w, 0.0])
        hist = [poing(max(fa0, f - k)) for k in range(0, 24)]
        # le cou prolonge le SENS DE LA PLONGÉE (sinon la tête se dressait à
        # la verticale) : 2e point juste derrière la tête, dans l'axe du coup
        base = _reechantillonne([H, H - d * 0.9] + hist, NP)
        base[1] = H - d * (np.linalg.norm(base[1] - base[0]))
        out = []
        for k, p in enumerate(base):
            s_ = k / (NP - 1)
            tan = base[min(NP - 1, k + 1)] - base[max(0, k - 1)]
            tan = tan / (np.linalg.norm(tan) + 1e-9)
            e1 = np.cross(tan, [0.0, 1, 0]); e1 /= (np.linalg.norm(e1) + 1e-9)
            e2 = np.cross(tan, e1)
            ang = 2 * np.pi * 2.2 * s_ + 3.0 * t
            r = 1.2 * s_ * (1 - 0.4 * s_)
            out.append(p + r * (np.cos(ang) * e1 + np.sin(ang) * e2))
        return np.array(out)

    def armes(tc, rel):
        # le serpent naît à 236 (dans l'armé) ; l'événement démarre à 226 avec
        # les éclairs (l'arme s'allume) : tous les temps sont relatifs à 226
        # plongée : essais vus à l'écran -> en caméra obari (chez la victime),
        # tête ou cou passent entre l'objectif et l'attaquant et cachent tout.
        # Le dragon RENTRE donc dans le poing au début de la plongée (dernière
        # image de la tête à ~f262), et RESSORT à l'impact (comme le film)
        f_fin = 270
        images = []
        for f in range(fa0, f_fin + 1, 2):
            t = rel(f)
            if f <= 256:
                pts = enroule(f, t)
            else:
                w = min(1.0, (f - 256) / 8)
                pts = (1 - w) * enroule(256, t) + w * file(f, t)
            images.append([round(t, 4), [v3(p) for p in pts]])
        t_n, t_c = rel(fa0), rel(sf)
        duree = rel(f_fin) - t_n
        # (bug trouvé à la relecture v10b : les images étaient rendues
        # RELATIVES au début de la couche alors que le moteur les lit en temps
        # de RECETTE -> la forme du dragon avait 10 images d'avance sur le
        # corps ; il plongeait avant le perso)
        # dissolution depuis la queue : le corps se ramasse dans le poing
        corps = R.serpent(images, round(t_n, 4), round(duree, 4), naissance=0.18,
                          mort=((rel(258) - t_n) / duree, "queue"), vitesse=2.0, taille_tete=(3.4, 1.7), echelle=0.5)
        c = [corps] + R.flammes_corps(corps, n=6, rate=14)
        ch_poing = [[rel(f)] + v3(poing(f)) for f in range(226, sf + 1, 2)]
        ch_corps = [[rel(f)] + v3(aw[f]["Torso"][1]) for f in range(226, sf + 1, 2)]
        # (éclairs verts d'Izuku retirés, 2026-09-25 : Milan voulait la POSE
        # d'Izuku mélangée à celle de Goku, pas ses éclairs)
        sons = [{"son": "rugissement", "t0": round(t_n, 4), "volume": 0.45, "hauteur": 1.15}]
        return c, sons
    studio(226, "dragon_arme", armes)

    # IMPACT : tourbillon de feu (7a2b4ae8), éclairs verts et or, puis le
    # dragon SORT du cratère et monte en spirale vers le ciel ; il se dissout
    # pendant la révélation (la conséquence reste à l'écran)
    G = tip(aw[imf], "Right Arm")
    G[1] = 0.0

    def monte(tc, rel):
        fin = rel(470)
        t_dep = tc + 0.12
        duree = fin - t_dep
        tete = []
        n_t = 120
        for k in range(n_t + 1):
            u = k / n_t
            # 1er essai : colonne de 15 studs, tête toujours hors du cadre de la
            # révélation -> spirale LARGE et BASSE autour du cratère (7 studs)
            e = 1 - (1 - min(1.0, u * 1.4)) ** 2
            ang = 2 * np.pi * 1.25 * u + 0.6
            r = 2.0 + 2.7 * e
            tete.append((u, G + np.array([r * np.cos(ang), 0.5 + 4.2 * e, r * np.sin(ang)])))

        def forme(u):
            # corps = les positions PASSÉES de la tête (il suit son propre chemin)
            hist = [p for (uu, p) in tete if uu <= u + 1e-9][::-1][:40]
            if len(hist) < 2:
                hist = [G + np.array([0, 0.5, 0]), G]
            return _reechantillonne(hist + [G - np.array([0, 1.0, 0])], NP)
        images = [[round(t_dep + u * duree, 4), [v3(p) for p in forme(u)]] for u in np.linspace(0, 1, 46)]   # temps de RECETTE
        c = [R.serpent(images, round(t_dep, 4), round(duree, 4), naissance=0.2, mort=(0.72, "queue"), vitesse=2.5,
                       taille_tete=(7.0, 3.5), largeur=[[0, 2.2], [0.08, 2.5], [0.5, 1.9], [0.85, 1.0], [1, 0.2]],
                       echelle=0.85)]
        c += R.flammes_corps(c[0], n=8, rate=18)
        c.append({"type": "mesh", "nom": "tourbillon_feu", "t0": tc, "duree": 0.9, "ancre": {"pos": v3(G)},
                  "mesh": "tourbillon", "texture": "bruit_energie", "defilement": [2.5, 0],
                  "echelle": [[0, [1.5, 0.6, 1.5]], [0.3, [7, 5, 7]], [1, [9, 7, 9]]],
                  "transparency": [[0, 0.1], [0.6, 0.35], [1, 1]], "color": [[0, "#fff6dc"], [0.5, "#ff8a1f"], [1, "#c8401a"]],
                  "rotation_vitesse": 420, "light_emission": 1})
        sons = [{"son": "rugissement", "t0": round(t_dep + 0.15, 4), "volume": 0.9}]
        return c, sons
    studio(imf, "dragon_monte", monte)
    return []


def temps_reel(E):
    """Temps réel d'une frame (s), hitstops compris : même calcul que
    realTimeOf() du lecteur (un hitstop à la frame fs compte pour f > fs)."""
    stops = sorted((e["frame"], e["hitstop"]) for e in E if e["kind"] == "impact" and e.get("hitstop", 0) > 0)
    return lambda f: f / FPS + sum(h for fs, h in stops if fs < f)


def studio_events(aw, vw, E):
    """Événements « studio » : une recette du studio VFX (vfx_studio/recettes.py)
    jouée au temps RÉEL de sa frame, dans le repère de la scène. Le temps
    interne d'une recette est en secondes réelles depuis son déclenchement
    (les effets continuent pendant les hitstops, comme en jeu). Une recette
    peut commencer AVANT son contact (le souffle qui arrive) : `avance` frames."""
    rt = temps_reel(E)
    out = []

    def studio(f_contact, nom, construire, avance=0):
        f0 = max(0, f_contact - avance)
        t_c = round(rt(f_contact) - rt(f0), 4)
        couches, sons = construire(t_c, lambda f: round(rt(f) - rt(f0), 4))
        rec = R.recette(f"dragon_{nom}", couches, sons)
        out.append(dict(frame=f0, kind="studio", name=nom, recette=rec))

    def chemin(track, part, fa, fb, rel, tete=True):
        return [[rel(f)] + v3(tip(track[f], part) if tete else track[f][part][1]) for f in range(fa, fb + 1)]

    # 1. RAFALE : palier 1 (hits 1-3) et 2 (h4), le fouet 8 f avant le contact
    tiers = [1, 1, 1, 2]
    for i, (c, sd, _k) in enumerate(HITS):
        p = tip(aw[c], "Right Arm" if sd == "R" else "Left Arm")
        d = impact_dir(aw, c, sd)
        studio(c, f"hit{i + 1}", lambda tc, rel, p=p, d=d, i=i: R.impact_palier(v3(p), v3(d), tier=tiers[i], t0=tc,
                                                                               echelle=0.8 + 0.25 * SCENE["hit_scale"][i],
                                                                               hauteur=(1.04, 0.96, 1.08, 0.92)[i]),
               avance=8)
    # 2. COUP CHARGÉ : craquement au contact, SILENCE pendant le noir, boum
    #    quand les cartes tombent ; l'explosion du monde sort du blanc, dans
    #    l'axe du coup ; la victime projetée laisse un sillage d'air et de fumée
    u = SCENE["upper_f"]
    p = tip(aw[u], "Right Arm")
    d = impact_dir(aw, u, "R")

    def coup_charge(tc, rel):
        c, sons = R.impact_palier(v3(p), v3(d), tier=2, t0=tc, echelle=1.2)
        t_ex = rel(u + 1)                      # après le gel des cartes (0,43 s)
        anc = {"pos": v3(p + 1.6 * d), "dir": v3(d), "coup": v3(d)}
        c += R.impact_couches(anc, palette=R.DRAGON, echelle=0.9, t0=t_ex, sol=False)
        g = p + 1.6 * d
        g[1] = 0.0
        c += [L for L in R.impact_couches({"pos": v3(g)}, palette=R.DRAGON, echelle=1.3, t0=t_ex) if L["nom"] in ("anneau_sol", "vague")]
        c += R.sillage(chemin(vw, "Torso", u + 1, 170, rel, tete=False), largeur=2.2, fumee=True)
        sons = [x for x in sons if x["son"] != "impact_lourd"] + [
            {"son": "impact_lourd", "t0": round(tc + 0.15, 4), "volume": 1.0, "impact": True, "vide": 0.08},
            {"son": "grondement", "t0": round(tc + 0.16, 4), "volume": 0.7},
            {"son": "vent_arc", "t0": t_ex, "volume": 0.5},
        ]
        return c, sons
    studio(u, "coup_charge", coup_charge, avance=8)
    if V13:
        scene_v13.studio(scene13(aw, vw), studio)
        return out
    # 3. AÉRIEN : l'arme s'allume (son d'énergie), la plongée laisse un sillage
    #    d'air, le souffle est coupé 60 ms avant le contact, contact EN L'AIR
    studio(226, "arme", lambda tc, rel: ([], [{"son": "aspiration", "t0": 0.0, "volume": 0.5},
                                                {"son": "naissance_orbe", "t0": 0.02, "volume": 0.4}]))
    sf = SCENE["strike_f"]

    def plongee(tc, rel):
        return R.sillage(chemin(aw, "Right Arm", 256, sf, rel), largeur=1.6), [R.souffle_avant(tc, volume=0.8)]
    # le souffle (0,44 s) dure plus que la plongée (22 f = 0,37 s) : la recette
    # démarre 12 f avant l'élan pour qu'il arrive sur le contact sans le couvrir
    studio(sf, "plongee", plongee, avance=sf - 256 + 12)
    ps, ds = tip(aw[sf], "Right Arm"), impact_dir(aw, sf, "R")
    studio(sf, "contact_aerien", lambda tc, rel: (
        R.impact_couches({"pos": v3(ps), "dir": v3(ds), "coup": v3(ds)}, palette=R.DRAGON, echelle=0.55, t0=tc, sol=False),
        [{"son": "impact_lourd", "t0": tc, "volume": 0.8, "impact": True}]))
    # échelles vues à l'écran (1er essai 1,1 / 2,1 / 1,3) : la caméra obari est
    # à 1,5 stud du contact et le feu cel à 2,1 fait 11 studs par particule,
    # l'effet avalait tout le cadre et cachait les corps
    # 4. IMPACT AU SOL : le plus gros (escalade), son plus grave, grondement long
    imf = SCENE["impact_f"]
    gr = tip(aw[imf], "Right Arm")
    gr[1] = 0.0
    studio(imf, "impact_sol", lambda tc, rel: (
        R.impact_couches({"pos": v3(gr)}, palette=R.DRAGON, echelle=1.4, t0=tc),
        [{"son": "impact_lourd", "t0": tc, "volume": 1.0, "hauteur": 0.8, "impact": True, "vide": 0.03},
         {"son": "grondement", "t0": round(tc + 0.01, 4), "volume": 0.9, "hauteur": 0.85}]))
    # 6. AURA DRAGON (fiches/AURA_DRAGON.md) : Goku x Izuku
    out += dragon_events(aw, vw, rt, studio)
    # 5. RÉVÉLATION : un fond de vent sous le calme (aucune ref n'a de
    #    silence numérique ; le 1er mixage laissait 3 s de silence total)
    wf = SCENE["white"]
    studio(wf[0] + 10, "calme", lambda tc, rel: ([], [{"son": "vent_ambiant", "t0": 0.0, "volume": 0.3}]))
    return out


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
