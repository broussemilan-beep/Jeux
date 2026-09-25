"""
Mise en scène v13 du Poing du Dragon (fiche : animator_brain/corpus/fiches/
POING_DU_DRAGON_V13.md) : tout ce qui suit l'apex (f200). Appelé par
staging.py quand scene.json dit « aerien = v13 ».

Le dragon d'or en trois couches (serpents = modèle 3D riggé, échantillonné
ici sur les pistes RÉELLES exportées, en temps de RECETTE) :
- A « invocation » (236-378) : jaillit du poing levé vers le ciel,
  s'enroule dans le ciel au-dessus de l'attaquant, rugit (gros plan), se
  tourne vers la victime, puis se RASSEMBLE dans le poing pendant le coup ;
- B « morsure » (378-440) : sort du poing, monte en fouet au-dessus de
  l'attaquant, plonge sur la victime gueule ouverte, la MANGE (f400), file
  vers le sol (cratère) ;
- C « remontée » (572-720) : ressort du cratère en spirale vers le ciel,
  recrache la victime (f584), rugit, se dissout.
Chaque corps = les positions PASSÉES de sa tête (il suit son propre
chemin), rééchantillonnées à la longueur du modèle (sinon le maillage
s'étire).
"""
import numpy as np

import recettes as R

NP = 28
L_MOD = 14.0                     # longueur du modèle (modeles/dragon.py)


def _catmull(keys, f):
    """keys = [(frame, point)] -> point en f (Catmull-Rom, bornée)."""
    fs = [k[0] for k in keys]
    if f <= fs[0]:
        return np.asarray(keys[0][1], float)
    if f >= fs[-1]:
        return np.asarray(keys[-1][1], float)
    i = max(0, min(len(fs) - 2, int(np.searchsorted(fs, f, side="right")) - 1))
    p0 = np.asarray(keys[max(0, i - 1)][1], float)
    p1, p2 = np.asarray(keys[i][1], float), np.asarray(keys[i + 1][1], float)
    p3 = np.asarray(keys[min(len(keys) - 1, i + 2)][1], float)
    u = (f - fs[i]) / (fs[i + 1] - fs[i])
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def _longueur(pts):
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1))) if len(pts) > 1 else 0.0


def _reech(pts, n):
    pts = np.asarray(pts, float)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    if d[-1] < 1e-9:
        return np.repeat(pts[:1], n, axis=0)
    u = np.linspace(0, d[-1], n)
    return np.stack([np.interp(u, d, pts[:, k]) for k in range(3)], axis=1)


def _coupe(pts_tete_dabord, lg):
    """Garde les `lg` premiers studs d'une polyligne (tête d'abord)."""
    out = [np.asarray(pts_tete_dabord[0], float)]
    reste = lg
    for a, b in zip(pts_tete_dabord, pts_tete_dabord[1:]):
        a, b = np.asarray(a, float), np.asarray(b, float)
        s = float(np.linalg.norm(b - a))
        if s >= reste:
            out.append(a + (b - a) * (reste / max(s, 1e-9)))
            return out
        out.append(b)
        reste -= s
    return out


def corps(traj, lb, origine, sens_origine):
    """Corps = les `lb` derniers studs de la trajectoire de la tête (tête
    d'abord). S'il en manque (naissance), il est prolongé DANS l'origine
    (le poing) selon `sens_origine` : cette partie est cachée (queue_visible)."""
    hist = list(traj[::-1])
    lg = _longueur(hist)
    if lg >= lb:
        return _reech(_coupe(hist, lb), NP), 1.0
    manque = lb - lg
    prolong = [np.asarray(origine, float) + np.asarray(sens_origine, float) * manque * k for k in (0.5, 1.0)]
    return _reech(hist + prolong, NP), max(0.02, lg / lb)


class Scene13:
    def __init__(self, aw, vw, scene, tip):
        self.aw, self.vw, self.S, self.tip = aw, vw, scene, tip
        self.sf, self.mf, self.rf = scene["strike_f"], scene["morsure_f"], scene["recrache_f"]
        D = scene["distance"]
        self.G = np.array([0.0, 0.0, -(D + scene["cratere_back"])])
        self.F0 = self.poing(236)
        self.ka, self.kb = 1.9, 1.4            # échelles des couches A et B (la tête d'A fait ~11 studs)
        self.la, self.lb = L_MOD * self.ka, L_MOD * self.kb
        self.MUSEAU = 3.28                     # museau devant l'os de tête (unités modèle, dragon.py X1)
        self.FUSION_F = 363                    # le museau touche le poing
        V = self.V = np.asarray(vw[self.mf]["Torso"][1], float)
        d = self.G - V
        self.d = d / np.linalg.norm(d)         # axe de la plongée : victime -> cratère
        F0 = self.F0
        # A : tête de l'invocation (décalages depuis le poing levé à f236).
        #  (1er essai : jaillissement droit vers le haut, vu d'en dessous = une
        #  boule de crinière hérissée) -> il monte en courbe vers la DROITE de
        #  la caméra (on le voit de profil) ; il finit DERRIÈRE l'attaquant
        #  (+Z) : la fusion dans le poing vient de derrière, jamais entre la
        #  caméra obari (chez la victime) et lui
        # (revue sans Milan : à la naissance la tête montait DEVANT lui, côté
        #  caméra (z < 0) : vue d'en dessous elle couvrait tout son corps)
        #  -> elle monte DERRIÈRE lui (z > 0), il reste lisible devant
        self.WA = [(236, F0), (240, F0 + (1.0, 4.6, 1.8)), (246, F0 + (3.0, 9.0, 2.2)), (256, F0 + (5.2, 10.6, 1.6)),
                   (268, F0 + (6.5, 10.8, -3.5)), (282, F0 + (3.5, 11.8, -8.5)), (296, F0 + (-3.0, 10.2, -8.0)),
                   (310, F0 + (-5.2, 9.2, -5.4)), (330, F0 + (-5.4, 8.8, -4.2)), (344, F0 + (-4.5, 12.5, 6.0)),
                   (356, F0 + (1.5, 10.5, 7.0))]
        # B : la tête SORT du poing (coup à distance) face à la victime, gueule
        #     qui s'ouvre (anticipation, 0,25 s), puis claque en avançant : à
        #     MORSURE_F le centre de la gueule (4,3 studs devant l'os de tête à
        #     l'échelle 1,4) est SUR la victime ; puis vers le cratère
        Fs = self.poing(self.sf)
        ax = V - Fs
        self.ax = ax / np.linalg.norm(ax)
        g = 4.3
        self.WB = [(self.sf, Fs + self.ax * 0.3), (386, Fs - self.ax * 0.9 + (0, 0.5, 0)), (394, Fs - self.ax * 1.1 + (0, 0.6, 0)),
                   (self.mf, V - self.ax * g), (408, V + self.d * 3.5), (426, self.G + self.d * 3.5)]

    def poing(self, f):
        a, u = int(np.floor(f)), f - np.floor(f)
        pa = self.tip(self.aw[a], "Right Arm")
        return pa if u < 1e-9 else pa + (self.tip(self.aw[a + 1], "Right Arm") - pa) * u

    def epaule(self, f):
        def e(k):
            r, p = self.aw[k]["Right Arm"]
            return p + r @ np.array([0.0, 1.0, 0.0])
        a, u = int(np.floor(f)), f - np.floor(f)
        return e(a) if u < 1e-9 else e(a) + (e(a + 1) - e(a)) * u

    # ---------------------------------------------------------- têtes
    def tete_a(self, f):
        if f <= 356:
            return _catmull(self.WA, f)
        # fusion (revue sans Milan, fix1-fix2 : l'OS de tête arrivait au poing
        # à f364 puis rentrait dans le bras ; or le museau est 6 studs DEVANT
        # l'os à l'échelle 1,9 : la tête de 11 studs restait posée sur
        # l'attaquant 14 images) -> c'est le MUSEAU qui touche le poing à
        # FUSION_F ; là, éclat d'or et le dragon s'engouffre (fondu 3 images),
        # le poing garde le feu jusqu'au coup
        u = self.WA[-1][1] - self.poing(self.FUSION_F)
        u /= np.linalg.norm(u)
        m = self.MUSEAU * self.ka
        keys = [(356, self.WA[-1][1]), (self.FUSION_F, self.poing(self.FUSION_F) + u * m),
                (self.FUSION_F + 4, self.poing(self.FUSION_F + 4) + u * m * 0.4)]
        if f <= self.FUSION_F + 4:
            return _catmull(keys, f)
        return self.poing(f) + u * m * 0.4

    def tete_b(self, f):
        return _catmull(self.WB, f)

    def dir_tete_a(self, f):
        a, b = self.tete_a(f), self.tete_a(f - 2)
        v = a - b
        return v / (np.linalg.norm(v) + 1e-9)

    # ---------------------------------------------------------- formes
    def forme_a(self, f):
        """(pts, s0, s1) de la couche A à la frame f."""
        traj = [self.tete_a(x) for x in np.arange(236, f + 1e-6, 0.5)] if f >= 236 else [self.F0]
        pts, s1 = corps(traj, self.la, self.F0, (0, -1, 0))
        return pts, 0.0, s1

    def forme_b(self, f):
        """Le coup DEVIENT le dragon : le corps sort du poing en ligne (il
        prolonge le bras) et ONDULE (vague qui court vers la queue). Après
        la morsure la queue quitte le poing (il file vers le cratère)."""
        Fs = self.poing(min(f, 420))
        sens = self.epaule(self.sf) - self.poing(self.sf)
        sens /= np.linalg.norm(sens)
        H = self.tete_b(f)
        base = Fs if f <= 404 else Fs + (H - Fs) * min(0.85, (f - 404) / 26.0)
        lg = float(np.linalg.norm(H - base))
        n = 60
        lat = np.cross(self.ax, [0.0, 1.0, 0.0])
        lat /= (np.linalg.norm(lat) + 1e-9)
        up = np.cross(lat, self.ax)
        t = (f - self.sf) / 60.0
        pts = []
        for i in range(n):
            u = i / (n - 1)
            p = H + (base - H) * u
            amp = 0.55 * np.sin(np.pi * u) * min(1.0, lg / 4.0)
            p = p + lat * amp * np.sin(2 * np.pi * (1.6 * u - 2.5 * t)) + up * 0.6 * amp * np.cos(2 * np.pi * (1.1 * u - 2.0 * t))
            pts.append(p)
        pts, s1 = corps(pts[::-1], self.lb, base, sens)
        return pts, 0.0, s1


def v3(x):
    return [round(float(c), 3) for c in x]


def camera(sc, add, A, Vt, h):
    """Plans v13 (fiche §4) à partir de f208."""
    add(208, A(208) + [1.6, -1.2, -9.4], A(208) + [0, 0.1, 0], 40)
    add(224, A(224) + [1.5, -1.1, -9.0], A(224) + [0, 0.1, 0], 40)
    # jaillissement : contre-plongée 3/4 face, assez loin pour voir le poing
    # ET le dragon qui monte en courbe (1er essai : trop près, la tête vue
    # d'en dessous remplissait le cadre)
    # (2e essai, relu à 0,1 s : l'attaquant coupé par le bas du cadre et caché
    # par le dragon, la pose de Goku ne se lisait pas) -> plus loin, le corps
    # ENTIER en bas du cadre, le dragon monte à côté de lui
    add(226, A(226) + [9.5, -2.5, -17.0], A(226) + [2.0, 4.0, 0.0], 56, "cut")
    add(250, A(250) + [9.0, -2.4, -16.0], A(250) + [2.5, 5.0, 0.0], 56)
    # le dragon s'enroule dans le ciel : TRÈS large, contre-plongée (échelle)
    ciel = sc.F0 + np.array([0.0, 8.0, -3.0])
    # (revue : l'attaquant coupé à la taille par le bas du cadre) -> visée
    # plus basse et plus ouvert : il est entier, petit, sous le dragon
    add(252, A(252) + [15.0, -9.0, -20.0], ciel - [0, 1.8, 0], 64, "cut")
    add(298, A(298) + [13.0, -8.4, -18.0], ciel - [0, 1.2, 0], 62)
    # gros plan : la tête RUGIT (devant le museau, un peu dessous, de côté)
    H = sc.tete_a(304)
    dvec = sc.dir_tete_a(304)
    cote = np.cross(dvec, [0.0, 1.0, 0.0])
    cote /= (np.linalg.norm(cote) + 1e-9)
    museau = H + dvec * 3.5
    # (1er essai à 9 studs : la mâchoire seule remplissait le cadre)
    add(300, museau + dvec * 15.0 + cote * 6.0 + [0, -2.5, 0], museau, 50, "cut")
    add(334, museau + dvec * 13.0 + cote * 5.2 + [0, -2.2, 0], sc.tete_a(334) + sc.dir_tete_a(334) * 3.5, 50)
    # regard : contre-plongée sur l'attaquant, le dragon DERRIÈRE lui
    # (1er essai à 5 studs : bras et crinière collés à l'objectif)
    # (2e essai : la tête du dragon se posait SUR celle de l'attaquant à
    # l'image) -> tête du dragon plus haut et derrière, cadre plus haut
    add(336, A(336) + [5.5, -4.5, -9.5], A(336) + [0.5, 4.5, 0.5], 62, "cut")
    add(354, A(354) + [5.0, -4.2, -8.8], A(354) + [0.5, 4.5, 0.5], 60)
    # obari : chez la victime, le poing arrive vers l'objectif
    sf = sc.sf
    # (obari, 2 essais : le dragon qui rentre dans le poing passait contre
    # l'objectif et remplissait l'écran, ni l'attaquant ni son poing ne se
    # voyaient) -> 3/4 de côté : l'attaquant plonge, le dragon se VERSE
    # dans son poing, la victime en bas du cadre
    V = sc.V
    m3 = (A(366) + V) / 2
    # (3e essai à 13 studs : la tête, longue de 11 studs à l'échelle 1,9,
    # remplissait encore le cadre) -> 26 studs
    add(356, m3 + [24.0, 3.0, 10.0], m3 + [0.0, 2.5, 0.5], 52, "cut")
    add(sf, m3 + [21.0, 2.6, 8.8], m3 + [0.0, 1.5, 0.0], 50)
    # le coup DEVIENT le dragon : même axe (on voit le poing ET la victime),
    # caméra plus BASSE qui regarde un peu vers le haut (2e essai en plongée :
    # la victime, à 12 studs du sol, semblait couchée PAR TERRE, le sol
    # lointain derrière elle) -> le ciel derrière elle
    mil = (sc.poing(sf) + V) / 2
    add(sf + 1, mil + [12.5, -3.5, 3.0], mil + [0.0, 0.6, 0.0], 58, "cut")
    add(398, mil + [11.0, -3.2, 2.6], mil + [0.0, 0.2, -0.2], 56)
    add(418, mil + [12.0, -3.0, 2.4], mil + [0.0, -1.5, -0.6], 58)
    # conséquence (derrière les planches et le blanc) : très large
    G = sc.G
    add(562, G + [17.0, 6.5, 15.0], G + [0.0, 4.5, 0.0], 56, "cut")
    # la caméra SUIT le dragon qui jaillit vers le ciel et la victime
    # recrachée qui retombe (1er essai fixe : il sortait du cadre en 0,5 s)
    # (revue : l'attaquant qui atterrit à G+7,5 en z était coupé à mi-corps
    # par le bas du cadre) -> plus loin, visée plus proche de lui
    add(596, G + [20.0, 5.0, 19.5], G + [0.0, 8.5, 2.0], 60)
    add(626, G + [19.5, 4.8, 20.0], G + [0.0, 8.0, 0.5], 60)
    add(652, G + [15.6, 5.0, 16.6], G + [-2.0, 8.0, -8.0], 58)
    add(700, G + [15.0, 4.6, 17.5], G + [-6.0, 9.0, -18.0], 56)
    # plan moyen sur les deux corps (1er essai : plan large tenu 2 s sur un
    # cratère sombre où rien ne bougeait)
    # (de CÔTÉ : l'attaquant, maintenant au bord du cratère, et la victime au
    # centre sont tous les deux dans le cadre)
    add(716, G + [11.0, 3.2, 4.5], G + [0.0, 1.2, 4.0], 50, "cut")
    add(758, G + [10.0, 3.0, 4.3], G + [0.0, 1.2, 4.0], 48)
    r0 = A(760)
    far = Vt(sc.S["end_f"])
    # (2 essais de dos : le dos de l'attaquant cachait la victime) -> de
    # 3/4 côté, il se relève face à elle
    mp = (r0 + far) / 2
    add(760, mp + [11.0, 3.5, 4.5], mp + [0, 0.8, 0], 50, "cut")
    add(sc.S["end_f"], mp + [9.6, 3.1, 4.0], mp + [0, 0.9, 0], 48)


def planches_sequence():
    """Plein écran (fiche §5) : carte manga de la gueule, puis tourbillon de
    feu, rouge radial, soleil à silhouette. Durées réelles (s)."""
    return [
        {"duree": 0.3, "images": ["gueule_encre"], "echelle": [[0, 1.12], [1, 1.0]], "secousse": 0.018},
        {"duree": 0.2, "images": ["gueule_inverse"], "echelle": [[0, 1.0], [1, 1.04]], "secousse": 0.03},
        {"duree": 0.83, "images": ["spirale_0", "spirale_1", "spirale_2"], "cadence": 12,
         "rotation": [[0, 0], [1, 150]], "echelle": [[0, 1.25], [1, 1.7]]},
        {"duree": 0.72, "images": ["rouge_0", "rouge_1"], "cadence": 12, "echelle": [[0, 1.0], [1, 1.12]]},
        # (1er essai 0,28 s : 4 images du vrai décor passaient avant le blanc)
        {"duree": 0.4, "images": ["soleil"], "echelle": [[0, 1.02], [1, 1.12]]},
    ]


def evenements(sc, ev, GOLD, WHITE, FLASH):
    """Événements non-studio de la v13 (f196 et après)."""
    S = sc.S
    ev(196, "whip", frames=12)
    ev(226, "aura", who="attaquant", frames=150, color=GOLD, intensity=1.0)
    ev(226, "fist_glow", who="attaquant", side="R", frames=152, color=GOLD)
    sf, mf = sc.sf, sc.mf
    p = sc.poing(sf)
    ev(sf, "body_flash", who="attaquant", color=FLASH, frames=3)
    ev(sf, "impact", pos=v3(p), dir=v3(sc.ax), scale=1.6, color=GOLD, hitstop=0.1, shake=0.6, name="strike", tier=3,
       studio=True)
    ev(mf, "impact", pos=v3(sc.V), dir=v3(sc.d), scale=2.0, color=WHITE, hitstop=0.12, shake=0.9, name="morsure",
       tier=3, studio=True)
    ev(mf, "cacher", who="victime", frames=[mf, S["recrache_f"]])
    # flash de 2 images qui MASQUE la disparition (1er essai : ses jambes
    # dépassaient encore de la gueule quand elle disparaissait d'un coup)
    ev(mf - 1, "flash_ecran", duree=round(3 / 60, 4), couleur="#fff6dc")
    ev(S["manga_f"], "planches", sequence=planches_sequence())
    w = S["white"]
    ev(w[0], "white", frames=[w[0], w[0] + 4, w[1] + 4])
    imf = S["impact_f"]
    G = sc.G
    ev(imf, "crater", pos=v3(G), radius=8.5, spikes=40, seed=13)
    ev(imf, "impact", pos=v3(G + [0, 0.6, 0]), dir=[0, -1, 0], scale=2.6, color=GOLD, hitstop=0.0, shake=1.0,
       name="impact", tier=3, studio=True)
    ev(imf, "smoke_cloud", pos=v3(G), radius=10.0, frames=S["end_f"] - imf, color="#7d7468")
    ev(imf, "embers", pos=v3(G), frames=S["end_f"] - imf, color="#ff8a1f")


def studio(sc, studio_fn):
    """Recettes du studio VFX pour la v13."""
    sf, mf = sc.sf, sc.mf
    S = sc.S

    # 1. INVOCATION : le dragon jaillit du poing levé ; il s'enroule, rugit,
    #    se tourne vers la victime, puis rentre dans le poing pendant le coup
    def invocation(tc, rel):
        images = []
        tv, qv = [], []
        t_n, t_f = rel(236), rel(sf)
        duree = t_f - t_n
        for f in range(236, sf + 1, 2):
            pts, s0, s1 = sc.forme_a(f)
            t = rel(f)
            images.append([round(t, 4), [v3(p) for p in pts]])
            a = (t - t_n) / duree
            tv.append([round(a, 4), round(s0, 4)])
            qv.append([round(a, 4), round(s1, 4)])
        aa = lambda f: round((rel(f) - t_n) / duree, 4)  # noqa: E731
        mach = [[0, 20], [aa(244), 34], [aa(256), 14], [aa(300), 14], [aa(304), 44], [aa(326), 46], [aa(334), 16],
                [aa(350), 26], [aa(362), 36], [1, 36]]
        L = R.serpent(images, round(t_n, 4), round(duree, 4), echelle=sc.ka, machoire=mach, nom="dragon_a", tete=False)
        # il s'engouffre dans le poing : fondu de 3 images sous l'éclat, et
        # la partie visible se vide (les flammes du corps s'éteignent avec lui)
        ff = sc.FUSION_F
        tv = [x for x in tv if x[0] < aa(ff + 3)] + [[aa(ff + 3), 0.999], [1, 0.999]]
        L["tete_visible"], L["queue_visible"] = tv, qv
        L["transparency"] = [[0, 0], [aa(ff), 0], [aa(ff + 3), 1], [1, 1]]
        c = [L] + R.flammes_corps(L, n=8, rate=16)
        F0 = sc.F0
        pf = sc.poing(ff)
        c += R.jaillissement_dessine("feu", t0=round(rel(ff), 4), pos=v3(pf - [0, 0.9, 0]), echelle=1.0, suffixe="_fusion")
        c.append({"type": "particules", "nom": "eclat_fusion", "t0": round(rel(ff), 4), "ancre": {"pos": v3(pf)},
                  "texture": "halo", "emit": 1, "lifetime": [0.22, 0.22], "speed": [0, 0],
                  "size": [[0, 3.0], [0.3, 9.0], [1, 11.0]], "transparency": [[0, 0.1], [1, 1]], "color": "#fff3c4",
                  "light_emission": 1, "zoffset": 2})
        # le poing garde le feu du dragon jusqu'au coup
        chem = [[round(rel(f), 4)] + v3(sc.poing(f)) for f in range(ff, sf + 1)]
        c.append({"type": "particules", "nom": "feu_poing", "t0": round(rel(ff), 4), "duree_emission": round(rel(sf) - rel(ff), 4),
                  "rate": 40, "ancre": {"chemin": chem}, "texture": "flamme_aura",
                  "flipbook": {"grille": 4, "mode": "Loop", "fps": 24, "depart_aleatoire": True},
                  "lifetime": [0.2, 0.35], "speed": [1.0, 3.0], "spread": [180, 180], "drag": 2.5, "accel": [0, 6, 0],
                  "size": [[0, 1.2], [0.35, 2.4], [1, 0.5]], "transparency": [[0, 0.3], [0.25, 0.05], [1, 1]],
                  "color": [[0, "#fff4c8"], [0.45, "#ffb02e"], [1, "#ff4d12"]], "light_emission": 1,
                  "rotation": [-25, 25], "rotspeed": [-40, 40], "zoffset": 0.3})
        c += R.jaillissement_dessine("feu", t0=round(rel(236), 4), pos=v3(F0 - [0, 1.0, 0]), echelle=1.3, suffixe="_poing")
        # RAYONS de lumière qui tombent du ciel sur lui (Goku 656d965b : les
        # rayons dans les nuages pendant l'invocation tenue)
        for i in range(6):
            ang = 2 * np.pi * i / 6 + 0.4
            haut = F0 + np.array([7.0 * np.cos(ang), 42.0, 7.0 * np.sin(ang) - 3.0])
            bas = F0 + np.array([1.4 * np.cos(ang), -7.0, 1.4 * np.sin(ang)])
            c.append({"type": "beam", "nom": f"rayon_{i}", "t0": round(rel(240) + 0.04 * i, 4),
                      "duree": round(rel(350) - rel(240), 4), "de": v3(haut), "a": v3(bas), "segments": 6,
                      "texture": "halo", "largeur": [[0, 6.0], [1, 1.6]], "transparency": [[0, 0.5], [0.75, 0.62], [1, 1]],
                      "transparency_temps": [[0, 1], [0.12, 0.3], [0.85, 0.4], [1, 1]], "color": "#fff0bf",
                      "light_emission": 1})
        sons = [{"son": "aspiration", "t0": 0.0, "volume": 0.5}, {"son": "naissance_orbe", "t0": 0.02, "volume": 0.4},
                {"son": "rugissement", "t0": round(rel(238), 4), "volume": 0.7, "hauteur": 1.1},
                {"son": "rugissement", "t0": round(rel(303), 4), "volume": 1.0, "hauteur": 0.85},
                {"son": "vent_arc", "t0": round(rel(252), 4), "volume": 0.4}]
        return c, sons
    studio_fn(226, "invocation", invocation)

    # 2. LE COUP : sillage du poing, souffle coupé avant la sortie du dragon
    def coup(tc, rel):
        chem = [[rel(f)] + v3(sc.poing(f)) for f in range(356, sf + 1)]
        return R.sillage(chem, largeur=1.6), [R.souffle_avant(tc, volume=0.8)]
    studio_fn(sf, "coup", coup, avance=sf - 356 + 8)

    # 3. SORTIE + MORSURE : la tête sort du poing (éclat dessiné), monte en
    #    fouet, plonge et mange la victime (gueule 58° puis claque en 2 images)
    def morsure(tc, rel):
        images = []
        t_n, t_f = rel(sf), rel(440)
        duree = t_f - t_n
        qv = []
        for f in range(sf, 441):
            pts, _s0, s1 = sc.forme_b(f)
            t = rel(f)
            images.append([round(t, 4), [v3(p) for p in pts]])
            qv.append([round((t - t_n) / duree, 4), round(s1, 4)])
        aa = lambda f: round((rel(f) - t_n) / duree, 4)  # noqa: E731
        mach = [[0, 16], [aa(384), 40], [aa(392), 50], [aa(mf - 2), 52], [aa(mf), 3], [1, 3]]
        L = R.serpent(images, round(t_n, 4), round(duree, 4), echelle=sc.kb, machoire=mach, nom="dragon_b", tete=False)
        L["queue_visible"] = qv
        c = [L] + R.flammes_corps(L, n=7, rate=18)
        p = sc.poing(sf)
        c += R.jaillissement_dessine("feu", t0=tc, pos=v3(p - [0, 0.8, 0]), echelle=1.5, suffixe="_sortie")
        c += R.tornade_dessinee("feu", t0=tc, pos=v3(p - [0, 1.2, 0]), echelle=1.1)
        # la morsure : tornade et lames DESSINÉES (1er essai : explosion de
        # feu cel à contours = « cartoon », ce que Milan refuse)
        c += R.tornade_dessinee("feu", t0=round(rel(mf), 4), pos=v3(sc.V - [0, 1.0, 0]), echelle=1.3)
        c += R.jaillissement_dessine("feu", t0=round(rel(mf) + 0.02, 4), pos=v3(sc.V - [0, 0.6, 0]), echelle=1.2,
                                     suffixe="_morsure")
        sons = [{"son": "impact_lourd", "t0": tc, "volume": 0.9, "impact": True, "vide": 0.05},
                {"son": "rugissement", "t0": round(rel(384), 4), "volume": 0.9, "hauteur": 1.0},
                {"son": "impact_lourd", "t0": round(rel(mf), 4), "volume": 1.0, "hauteur": 1.55, "impact": True},
                {"son": "vent_arc", "t0": round(rel(mf) + 0.02, 4), "volume": 0.6}]
        return c, sons
    studio_fn(sf, "morsure", morsure)

    # 4. PLEIN ÉCRAN : grondement et feu sous les planches
    studio_fn(S["manga_f"], "plein_ecran", lambda tc, rel: ([], [
        {"son": "grondement", "t0": 0.0, "volume": 0.9, "hauteur": 0.8},
        {"son": "crepitement", "t0": round(rel(S["plein_f"][0]), 4), "volume": 0.7},
        {"son": "grondement", "t0": round(rel(500), 4), "volume": 0.8, "hauteur": 0.7}]))

    # 5. LE RÉEL REVIENT : cratère, explosion dessinée, le dragon remonte
    G = sc.G
    imf = S["impact_f"]

    def impact_sol(tc, rel):
        # (sans le feu cel en boules : trop « cartoon » ; le feu est dessiné)
        c = [L for L in R.impact_couches({"pos": v3(G)}, palette=R.DRAGON, echelle=2.0, t0=tc) if L["nom"] not in ("feu", "fumee")]
        c += R.tornade_dessinee("feu", t0=tc, pos=v3(G), echelle=2.4)
        c += R.jaillissement_dessine("feu", t0=round(tc + 0.05, 4), pos=v3(G), echelle=2.8, suffixe="_sol")
        return c, [{"son": "impact_lourd", "t0": tc, "volume": 1.0, "hauteur": 0.75, "impact": True, "vide": 0.03},
                   {"son": "grondement", "t0": round(tc + 0.01, 4), "volume": 0.9, "hauteur": 0.8}]
    studio_fn(imf, "impact_sol", impact_sol)

    def remonte(tc, rel):
        fin = rel(760)
        t_dep = tc + 0.03
        duree = fin - t_dep
        tete = []
        n_t = 150
        # (1er essai : il tournait au ras du sol pendant 1 s) -> il JAILLIT ;
        # (2e essai, bande à 0,1 s : il montait à 26 studs et sortait du cadre
        # en 0,8 s, puis 2 s de plan vide et sombre) -> il monte à 16 studs
        # en spirale (0,9 s) puis s'ENVOLE en grand arc au-dessus du cratère,
        # visible, vers l'horizon (Last Breath v3 : le dragon s'en va au loin)
        P1 = None
        for k in range(n_t + 1):
            u = k / n_t
            if u <= 0.3:
                e = 1 - (1 - u / 0.3) ** 2
                ang = 2 * np.pi * 1.0 * (u / 0.3) + 0.4
                r = 2.5 + 3.5 * e
                p = G + np.array([r * np.cos(ang), -1.0 + 17.0 * e, r * np.sin(ang)])
                P1 = p
            else:
                v = (u - 0.3) / 0.7
                b = [P1, P1 + np.array([0.0, 7.0, 0.0]), G + np.array([12.0, 22.0, -18.0]), G + np.array([-24.0, 21.0, -42.0])]
                p = ((1 - v) ** 3 * b[0] + 3 * (1 - v) ** 2 * v * b[1] + 3 * (1 - v) * v * v * b[2] + v ** 3 * b[3]
                     + np.array([0.0, 1.5 * np.sin(v * 9.0), 0.0]))
            tete.append((u, p))

        def forme(u):
            hist = [p for (uu, p) in tete if uu <= u + 1e-9]
            pts, _s1 = corps(hist, L_MOD * 1.6, G - np.array([0.0, 1.0, 0.0]), (0, -1, 0))
            return pts
        images = [[round(t_dep + u * duree, 4), [v3(p) for p in forme(u)]] for u in np.linspace(0, 1, 60)]
        aa = lambda f: round(max(0.0, (rel(f) - t_dep) / duree), 4)  # noqa: E731
        mach = [[0, 20], [aa(578), 50], [aa(590), 52], [aa(600), 18], [aa(630), 44], [aa(660), 46], [aa(680), 16], [1, 16]]
        c = [R.serpent(images, round(t_dep, 4), round(duree, 4), naissance=0.18, mort=(0.82, "queue"), echelle=1.6,
                       machoire=mach, nom="dragon_c", tete=False)]
        c += R.flammes_corps(c[0], n=8, rate=18)
        sons = [{"son": "rugissement", "t0": round(rel(630), 4), "volume": 1.0, "hauteur": 0.8}]
        return c, sons
    studio_fn(imf, "dragon_remonte", remonte)
    lx, lz = 0.4, float(G[2]) + 7.5
    def atterrissage(tc, rel):
        c, _sons = R.impact_palier([lx, 0.2, lz], [0, -1, 0], tier=1, t0=tc, echelle=1.3)
        return c, [{"son": "impact_lourd", "t0": tc, "volume": 0.6, "hauteur": 1.2, "impact": True}]
    studio_fn(604, "atterrissage", atterrissage)
    # (1er essai : 1,5 s de silence TOTAL à la fin) -> le vent tient jusqu'au bout
    studio_fn(600, "calme", lambda tc, rel: ([], [{"son": "vent_ambiant", "t0": 0.0, "volume": 0.35},
                                                   {"son": "vent_ambiant", "t0": round(rel(690), 4), "volume": 0.35, "hauteur": 0.92},
                                                   {"son": "grondement", "t0": round(rel(740), 4), "volume": 0.25, "hauteur": 0.6},
                                                   {"son": "vent_ambiant", "t0": round(rel(770), 4), "volume": 0.3, "hauteur": 0.85}]))

