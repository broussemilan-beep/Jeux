"""
BANQUE DE SONS du studio : chaque son est SYNTHÉTISÉ ici (numpy, graine
fixe), écrit en WAV mono 44,1 kHz, et c'est le MÊME fichier qui joue dans le
labo (WebAudio) et dans Roblox (Sound ; le .wav est un format d'envoi
accepté, <= 48 kHz, doc officielle audio/assets).

Ce qu'on a mesuré dans les refs de Milan (outils/ecoute.py,
corpus/ECOUTE_REFS_SFX_2026-09-25.md) :
- un impact = une ATTAQUE large bande très courte (craquement) + un corps
  médium + beaucoup de SUB (45 à 80 % de l'énergie des 300 ms qui suivent) ;
- le gros coup est précédé d'un VIDE (Stagnant Rage : 0,86 s où les aigus
  tombent de 25 dB, puis l'explosion) ; robloxIA dit 0,05-0,1 s de silence
  avant l'impact ;
- d'où la règle vérifiée par critique_son() : dans le mixage d'une recette,
  les 60 ms avant chaque son marqué « impact » sont au moins 12 dB sous son
  pic.

Chaque son de la banque est une couche : les recettes les empilent.

Usage : python3 sons.py [dossier]      -> sons/*.wav + sons/catalogue.json
"""
import json
import os
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100


# ------------------------------------------------------------ briques
def bruit(n, graine):
    return np.random.default_rng(graine).standard_normal(n)


def bande(x, lo, hi, pente=0.35):
    """Filtre passe-bande par masque FFT, à bords ADOUCIS (rampe en cosinus
    sur `pente` octave). Un masque à bords francs « sonne » : sur les clics
    du crépitement, il laissait deux tonalités à 1,8 et 7 kHz, visibles en
    lignes horizontales sur le spectrogramme du mixage du Dragon."""
    X = np.fft.rfft(x)
    f = np.maximum(np.fft.rfftfreq(len(x), 1 / SR), 1e-3)
    oct_lo, oct_hi = np.log2(f / lo), np.log2(f / hi)
    m = np.ones_like(f)
    m = np.where(oct_lo < -pente, 0, np.where(oct_lo < 0, 0.5 + 0.5 * np.cos(np.pi * oct_lo / pente), m))
    m = np.where(oct_hi > pente, 0, np.where(oct_hi > 0, m * (0.5 + 0.5 * np.cos(np.pi * oct_hi / pente)), m))
    return np.fft.irfft(X * m, len(x))


def balayage(n, graine, centres, largeur=0.6, grain=0.02):
    """Bruit dont la bande suit `centres(u)` (u de 0 à 1) : grains de 20 ms
    filtrés puis recollés en fondu (fenêtre de Hann, recouvrement 50 %)."""
    g = int(grain * SR)
    out = np.zeros(n + g)
    w = np.hanning(g)
    src = bruit(n + g, graine)
    for k, i in enumerate(range(0, n, g // 2)):
        c = centres(i / n)
        seg = bande(src[i:i + g] if i + g <= len(src) else np.pad(src[i:], (0, g - len(src[i:]))),
                    c * (1 - largeur / 2), c * (1 + largeur / 2))
        out[i:i + g] += seg * w
    return out[:n]


def env(n, attaque, tau, fin=None):
    t = np.arange(n) / SR
    e = (1 - np.exp(-t / max(attaque, 1e-4))) * np.exp(-t / tau)
    if fin:  # coupure franche : le silence avant l'impact
        e[int(fin * SR):] = 0
    return e


def sinus_chute(n, f0, f1, tau_f):
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / tau_f)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def norm(x, crete_db=-1.0):
    return x / (np.max(np.abs(x)) + 1e-12) * 10 ** (crete_db / 20)


def sat(x, k=1.6):
    return np.tanh(k * x) / np.tanh(k)


def n_(d):
    return int(d * SR)


# ------------------------------------------------------------ la banque
def craquement(d=0.035, graine=1, tau=0.006):
    """Attaque large bande, aiguë, 1-5 ms : le « clac » du contact."""
    n = n_(d)
    x = bande(bruit(n, graine), 1500, 16000) * env(n, 0.0003, tau)
    x[:24] += np.linspace(1, 0, 24) * 3  # clic de 0,5 ms
    return norm(x)


def corps(d=0.25, graine=2, lo=150, hi=1400, tau=0.05):
    n = n_(d)
    return norm(sat(norm(bande(bruit(n, graine), lo, hi)) * env(n, 0.002, tau), 2.0))


def sub(d=0.5, f0=110, f1=38, tau_f=0.07, tau=0.17):
    n = n_(d)
    return norm(sat(sinus_chute(n, f0, f1, tau_f) * env(n, 0.002, tau), 1.4))


def impact_lourd(g_sub=0.5, g_coup=0.55, g_corps=0.6, g_crac=0.9):
    """Craquement + corps + « coup » grave + sub. Réglé sur les refs mesurées
    (bandes des 300 ms après l'attaque) : sub ~0,6, grave ~0,2, médium ~0,1,
    aigu ~0,04 ; la 1re version (sub seul, 95 %) n'était qu'un grondement."""
    n = n_(0.6)
    x = np.zeros(n)
    c = craquement(0.06, 1, 0.012)
    b = corps(0.3, 2, 120, 1800, 0.08)
    k = norm(sinus_chute(n_(0.25), 190, 95, 0.04) * env(n_(0.25), 0.001, 0.06))
    s_ = sub(0.5, 90, 45, 0.06, 0.12)
    for g, y in ((g_crac, c), (g_corps, b), (g_coup, k), (g_sub, s_)):
        x[:len(y)] += g * y
    return norm(sat(x, 1.2))


def frappe_m1():
    """Tier 1 : court, sec, peu de sub (ne pas voler la vedette aux gros coups)."""
    n = n_(0.22)
    x = np.zeros(n)
    c, b = craquement(0.03, 11), corps(0.14, 12, 250, 2500, 0.035)
    k = norm(sinus_chute(n_(0.12), 240, 130, 0.02) * env(n_(0.12), 0.001, 0.03))
    s_ = sub(0.18, 95, 60, 0.03, 0.04)
    for g, y in ((0.8, c), (0.8, b), (0.5, k), (0.25, s_)):
        x[:len(y)] += g * y
    return norm(sat(x, 1.3))


def grondement(d=1.6, graine=3):
    """Queue d'explosion : grave qui roule + crépitement de débris qui
    s'espace (la fumée qui reste, en son)."""
    n = n_(d)
    t = np.arange(n) / SR
    brun = np.cumsum(bruit(n, graine))
    brun = bande(brun - np.convolve(brun, np.ones(2000) / 2000, "same"), 30, 500)
    x = norm(brun) * env(n, 0.012, 0.42)
    rng = np.random.default_rng(graine + 1)
    crepit = np.zeros(n)
    for _ in range(70):
        u = rng.random() ** 2.2  # plus dense au début
        i = int(u * (n - 400))
        crepit[i:i + 400] += rng.uniform(0.3, 1) * np.exp(-np.arange(400) / 40) * rng.standard_normal(400)
    crepit = bande(crepit, 1800, 7000) * np.exp(-t / 0.7)
    return norm(sat(0.9 * x + 0.35 * norm(crepit), 1.3))


def souffle_projectile(d=0.44, graine=4):
    """Le projectile qui arrive : bande qui monte (300 -> 2400 Hz), volume qui
    enfle, puis COUPURE nette 0 dB -> silence : le vide avant l'impact."""
    n = n_(d)
    u = np.linspace(0, 1, n)
    x = balayage(n, graine, lambda v: 300 * (2400 / 300) ** v, 0.8)
    e = u ** 2.2
    e[-n_(0.008):] *= np.linspace(1, 0, n_(0.008))
    return norm(x * e)


def aspiration(d=0.3, graine=5):
    """Énergie aspirée à la naissance de l'orbe : souffle qui monte en
    hauteur et en volume (son « à l'envers »), coupé net."""
    n = n_(d)
    u = np.linspace(0, 1, n)
    x = balayage(n, graine, lambda v: 900 * (3600 / 900) ** v, 0.5)
    e = u ** 3
    e[-n_(0.006):] *= np.linspace(1, 0, n_(0.006))
    return norm(x * e)


def naissance_orbe(d=0.4):
    """Tonalité d'énergie qui se forme : grappe de sinus qui monte d'un
    tiers, trémolo rapide ; reste sous le souffle (couche de couleur)."""
    n = n_(d)
    t = np.arange(n) / SR
    mont = 1 + 0.33 * (1 - np.exp(-t / 0.12))
    x = sum(a * np.sin(2 * np.pi * np.cumsum(f * mont) / SR) for f, a in ((330, 1), (495, 0.6), (660, 0.4), (990, 0.2)))
    x *= 0.75 + 0.25 * np.sin(2 * np.pi * 22 * t)
    return norm(x * env(n, 0.03, 0.2))


def vent_arc(d=0.28, graine=6):
    """Croissant de vent : « fwip » aigu en cloche."""
    n = n_(d)
    u = np.linspace(0, 1, n)
    x = balayage(n, graine, lambda v: 2600 - 1400 * v, 0.9)
    return norm(x * np.sin(np.pi * u) ** 2)


def fouet_m1(d=0.1, graine=7):
    """Le bras qui part (tier 1), coupé 15 ms avant le contact."""
    n = n_(d)
    u = np.linspace(0, 1, n)
    x = balayage(n, graine, lambda v: 800 + 2600 * v, 0.9, grain=0.01)
    return norm(x * u ** 1.5)


def vent_ambiant(d=3.6, graine=8):
    """Le calme après le coup (révélation) : vent grave qui respire, jamais
    un silence numérique (aucune ref n'en a : il y a toujours un fond)."""
    n = n_(d)
    t = np.arange(n) / SR
    x = bande(np.cumsum(bruit(n, graine)), 70, 900)
    x = norm(x - np.convolve(x, np.ones(4000) / 4000, "same"))
    lfo = 0.65 + 0.35 * np.sin(2 * np.pi * 0.45 * t + 1.3)
    fade = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 1.2)
    return norm(x * lfo * fade)


def crepitement(d=1.2, graine=9):
    """Éclairs verts d'Izuku : claquements électriques secs et irréguliers +
    bourdonnement grave léger."""
    n = n_(d)
    t = np.arange(n) / SR
    rng = np.random.default_rng(graine)
    x = np.zeros(n)
    for _ in range(46):
        i = int(rng.random() * (n - 600))
        ln = int(rng.uniform(80, 500))
        x[i:i + ln] += rng.uniform(0.4, 1) * rng.standard_normal(ln) * np.exp(-np.arange(ln) / (ln / 4))
    x = bande(x, 1800, 11000)
    buzz = 0.12 * np.sign(np.sin(2 * np.pi * 120 * t)) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
    return norm((norm(x) + bande(buzz, 100, 2000)) * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.15))


def rugissement(d=1.7, graine=10):
    """Le DRAGON rugit : grondement harmonique (~85 Hz) rendu rauque par une
    modulation rapide, formant de bruit qui s'ouvre puis se ferme, hauteur
    qui monte puis retombe."""
    n = n_(d)
    t = np.arange(n) / SR
    u = t / d
    f0 = 78 + 38 * np.sin(np.pi * np.clip(u * 1.2, 0, 1)) + 3 * np.sin(2 * np.pi * 6 * t)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    harm = sum(np.sin(k * ph) / k ** 0.9 for k in range(1, 14))
    rauque = 0.6 + 0.4 * np.sin(2 * np.pi * 27 * t + 3 * np.sin(2 * np.pi * 3 * t))
    souffle = balayage(n, graine, lambda v: 500 + 900 * np.sin(np.pi * min(1.0, v * 1.3)), 1.0, grain=0.03)
    env_ = np.minimum(1, t / 0.18) * np.clip((d - t) / 0.6, 0, 1)
    return norm(sat(norm(harm * rauque) * 0.8 + 0.45 * norm(souffle), 1.8) * env_)


BANQUE = {
    "impact_lourd": (impact_lourd, "craquement + corps + sub : le gros coup"),
    "frappe_m1": (frappe_m1, "tier 1 : court et sec"),
    "grondement": (grondement, "queue d'explosion : grave qui roule + débris"),
    "souffle_projectile": (souffle_projectile, "projectile qui arrive, coupé net avant l'impact"),
    "aspiration": (aspiration, "énergie aspirée, monte puis coupe"),
    "naissance_orbe": (naissance_orbe, "tonalité d'énergie qui se forme"),
    "vent_arc": (vent_arc, "croissant de vent autour de l'impact"),
    "fouet_m1": (fouet_m1, "le bras qui part (tier 1)"),
    "vent_ambiant": (vent_ambiant, "fond de vent grave, le calme après le coup"),
    "crepitement": (crepitement, "éclairs verts d'Izuku (One For All) qui crépitent"),
    "rugissement": (rugissement, "le dragon rugit"),
}


def ecrire_wav(x, chemin):
    y = np.clip(x, -1, 1)
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())


def lire_wav(chemin):
    with wave.open(chemin, "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32767


def main(sortie=None):
    sortie = sortie or os.path.join(HERE, "sons")
    os.makedirs(sortie, exist_ok=True)
    cat = []
    for nom, (fn, role) in BANQUE.items():
        x = fn()
        ecrire_wav(x, os.path.join(sortie, f"{nom}.wav"))
        cat.append({"nom": nom, "fichier": f"{nom}.wav", "duree": round(len(x) / SR, 3), "role": role})
    json.dump({"sons": cat, "rbxassetid": {}}, open(os.path.join(sortie, "catalogue.json"), "w"), indent=1, ensure_ascii=False)
    print(len(cat), "sons ->", sortie)
    return cat


# ------------------------------------------------------------ mixage
def mixer(rec, dossier=None):
    """Mixage mono d'une recette (liste `sons`) : pour les vidéos et pour la
    critique. Gain = volume, hauteur = vitesse de lecture (comme
    Sound.PlaybackSpeed : la durée change aussi)."""
    dossier = dossier or os.path.join(HERE, "sons")
    sons = rec.get("sons", [])
    fin = rec["duree"]
    pistes = []
    for s in sons:
        x = lire_wav(os.path.join(dossier, s["son"] + ".wav"))
        h = s.get("hauteur", 1.0)
        if h != 1.0:
            x = np.interp(np.arange(0, len(x) - 1, h), np.arange(len(x)), x)
        pistes.append((s["t0"], s.get("volume", 1.0) * x))
        fin = max(fin, s["t0"] + len(x) / SR)
    mix = np.zeros(n_(fin) + 1)
    for t0, x in pistes:
        i = n_(t0)
        mix[i:i + len(x)] += x
    return mix


def critique_son(rec, dossier=None):
    """Le vide avant l'impact : les 60 ms (ou `vide` s) avant chaque son
    « impact » sont au moins 12 dB sous le pic des 100 ms qui suivent."""
    err, info = [], []
    if not rec.get("sons"):
        return err, info
    mix = mixer(rec, dossier)
    crete = np.max(np.abs(mix))
    if crete > 1.0:
        info.append(f"{rec['nom']} : crête du mixage {20 * np.log10(crete):+.1f} dBFS (limiter ou baisser les volumes)")
    for s in rec["sons"]:
        if not s.get("impact"):
            continue
        i = n_(s["t0"])
        avant = mix[max(0, i - n_(s.get("vide", 0.06))):i]
        apres = mix[i:i + n_(0.1)]
        ra = 20 * np.log10(np.sqrt(np.mean(avant ** 2)) + 1e-9) if len(avant) else -120
        pa = 20 * np.log10(np.max(np.abs(apres)) + 1e-9)
        ecart = pa - ra
        txt = "silence total" if ra < -90 else f"{ecart:.1f} dB sous le pic"
        (info if ecart >= 12 else err).append(
            f"{rec['nom']} : {s['son']} à {s['t0']:.2f} s, vide avant l'impact : {txt} (règle >= 12 dB)")
    return err, info


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
