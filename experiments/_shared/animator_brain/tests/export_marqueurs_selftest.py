"""
Auto-test des KeyframeMarker à l'export (roblox_export.write_kfseq, 2026-09-26).

Ce qu'il vérifie (contrôles TECHNIQUES, pas de style) :
1. OCTET POUR OCTET : sans marqueur, et avec des marqueurs posés sur des clés
   de pose (le cas de toutes nos productions : keep_times forcés), la sortie
   est identique à celle de l'export d'AVANT le changement (roblox_export.py
   du commit ec29327, relu dans git et exécuté tel quel) ;
2. marqueurs hors clé : un Keyframe VIDE (aucune Pose) est créé exactement au
   temps voulu, comme dans les fichiers TSB (corpus/etude_c4/A1 §V5, A2 §5) ;
   deux marqueurs au même temps partagent la clé vide ; ordre du fichier =
   ordre des temps ; noms et valeurs relus (read_markers + XML brut +
   outils/rapport_regard.lire_marqueurs) ;
3. aller-retour moteur inchangé : read_kfseq ignore les clés vides, donc
   roundtrip_error reste ~0 ;
4. marqueur invalide (temps négatif, nom vide) : ValueError ;
5. si l'export committé du Poing du Dragon est là : ses marqueurs sont
   relus sur des clés de pose.

Usage : python3 tests/export_marqueurs_selftest.py      (code 0 = tout passe)
"""
import hashlib
import os
import subprocess
import sys
import tempfile
import types
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.normpath(os.path.join(HERE, ".."))
SHARED = os.path.normpath(os.path.join(BRAIN, ".."))
ROOT = os.path.normpath(os.path.join(SHARED, "..", ".."))
sys.path.insert(0, SHARED)
sys.path.insert(0, os.path.join(BRAIN, "outils"))

from animator_brain import roblox_export as X  # noqa: E402

COMMIT_AVANT = "ec29327"          # dernier roblox_export.py avant les clés vides de marqueurs
REL = "experiments/_shared/animator_brain/roblox_export.py"
ECHECS = []


def verifier(cond, msg):
    print(("  ok    " if cond else "  ECHEC ") + msg)
    if not cond:
        ECHECS.append(msg)


def rot(ax, deg):
    a = np.radians(deg)
    c, s = np.cos(a), np.sin(a)
    if ax == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def cadres(n=13, fps=60):
    """Une petite anim déterministe (7 parts, racine qui avance)."""
    out = []
    for i in range(n):
        T = {"Torso": (rot("y", 3 * i) @ rot("x", -2 * i), np.array([0.0, -0.02 * i, -0.05 * i])),
             "Head": (rot("x", i), np.zeros(3)),
             "Right Arm": (rot("x", 7 * i) @ rot("z", 2 * i), np.zeros(3)),
             "Left Arm": (rot("x", -4 * i), np.zeros(3)),
             "Right Leg": (rot("x", 2 * i), np.zeros(3)),
             "Left Leg": (rot("x", -3 * i), np.zeros(3))}
        root = (rot("y", i), np.array([0.0, 3.0, -0.1 * i]))
        out.append((i / fps, X.solve(T, root=root)))
    return out


def ancien_module():
    """roblox_export.py du commit d'avant, exécuté avec son vrai __file__
    (il charge data/r6_rig.json à côté de lui)."""
    try:
        src = subprocess.run(["git", "-C", ROOT, "show", f"{COMMIT_AVANT}:{REL}"], capture_output=True,
                             text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if src.returncode != 0:
        return None
    m = types.ModuleType("roblox_export_avant")
    m.__file__ = X.__file__
    exec(compile(src.stdout, f"{COMMIT_AVANT}:{REL}", "exec"), m.__dict__)
    return m


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    fr = cadres()
    tmp = tempfile.mkdtemp(prefix="export_marqueurs_")
    p = lambda n: os.path.join(tmp, n)  # noqa: E731

    print("1. octet pour octet contre l'export d'avant (commit %s)" % COMMIT_AVANT)
    A = ancien_module()
    if A is None:
        print("  (git ou le commit est indisponible : comparaison sautée)")
    else:
        cas = {"sans_marqueur": {},
               "marqueurs_sur_cles": {"markers": [(6 / 60, "hitreg", ""), (12 / 60, "end", "0")]},
               "poids_nul_et_boucle": {"zero_weight": ("Right Leg", "Left Leg"), "loop": True, "priority": 4,
                                       "markers": [(0.0, "debut", "debut")]}}
        for nom, kw in cas.items():
            X.write_kfseq(fr, p(f"nouveau_{nom}.rbxmx"), "Test", **kw)
            A.write_kfseq(fr, p(f"avant_{nom}.rbxmx"), "Test", **kw)
            a, b = open(p(f"nouveau_{nom}.rbxmx"), "rb").read(), open(p(f"avant_{nom}.rbxmx"), "rb").read()
            verifier(a == b, f"{nom} : identique ({len(a)} octets, sha {sha(p(f'nouveau_{nom}.rbxmx'))[:12]})")

    print("2. marqueurs hors clé -> Keyframe vide au temps exact (comme TSB)")
    mk = [(0.1733, "hitreg", ""), (6 / 60, "SmokeSlash", "fx"), (0.1733, "StartHitbox", "1"),
          (0.25, "End", "")]                       # 0.25 s : après la dernière clé de pose (0.2 s)
    out = p("hors_cle.rbxmx")
    X.write_kfseq(fr, out, "Test", markers=mk)
    seq = ET.parse(out).getroot().find("Item")
    kfs = [el for el in seq if el.get("class") == "Keyframe"]
    temps = [float(el.find("Properties/float[@name='Time']").text) for el in kfs]
    vides = [(t, el) for t, el in zip(temps, kfs) if not el.findall("Item[@class='Pose']")]
    verifier(len(kfs) == len(fr) + 2, f"{len(fr)} clés de pose + 2 clés vides (0,1733 partagée, 0,25) : {len(kfs)}")
    verifier(sorted(round(t, 4) for t, _ in vides) == [0.1733, 0.25], f"temps des clés vides : {[t for t, _ in vides]}")
    verifier(temps == sorted(temps), "Keyframes rangés par temps dans le fichier")
    v0 = dict(vides)[0.1733]
    noms_v0 = sorted(m.find("Properties/string[@name='Name']").text for m in v0.findall("Item[@class='KeyframeMarker']"))
    verifier(noms_v0 == ["StartHitbox", "hitreg"], f"deux marqueurs sous la même clé vide : {noms_v0}")
    verifier(all(el.find("Properties/string[@name='Name']").text == "Keyframe" for _t, el in vides),
             "clés vides nommées « Keyframe » (comme TSB)")
    back = X.read_markers(out)
    attendu = sorted([(float(t), n, v) for t, n, v in mk], key=lambda x: (x[0], x[1]))
    verifier([(round(t, 6), n, v) for t, n, v in back] == [(round(t, 6), n, v) for t, n, v in attendu],
             f"read_markers relit les 4 marqueurs (nom, valeur, temps) : {back}")
    sous_pose = [el for t, el in zip(temps, kfs) if abs(t - 6 / 60) < 1e-9][0]
    verifier(sous_pose.findall("Item[@class='Pose']") and sous_pose.findall("Item[@class='KeyframeMarker']"),
             "SmokeSlash (6/60 s, sur une clé de pose) reste sous la clé de pose")
    try:
        import rapport_regard as RR
        rr = RR.lire_marqueurs(out)
        verifier(sorted(n for _f, n in rr) == sorted(n for _t, n, _v in mk),
                 f"outils/rapport_regard.lire_marqueurs les retrouve aussi : {rr}")
    except ImportError as ex:
        print(f"  (rapport_regard non importable : {ex})")

    print("3. aller-retour moteur (les clés vides n'ont pas de pose)")
    lu = X.read_kfseq(out)
    verifier(len(lu) == len(fr), f"read_kfseq : {len(lu)} clés de pose (clés vides ignorées)")
    err = X.roundtrip_error(out, fr)
    pire = max(max(v) for v in err.values())
    verifier(pire < 1e-4, f"écart max aller-retour {pire:.2e} (studs / degrés)")

    print("4. marqueurs invalides refusés")
    for bad in [(-0.1, "x", ""), (0.1, "", "")]:
        try:
            X.write_kfseq(fr, p("bad.rbxmx"), "Test", markers=[bad])
            verifier(False, f"{bad} aurait dû lever ValueError")
        except ValueError:
            verifier(True, f"{bad} -> ValueError")

    print("5. export committé du Poing du Dragon (s'il est là)")
    dragon = os.path.join(ROOT, "experiments", "r6_poing_dragon", "output", "dragon_attaquant.rbxmx")
    if os.path.exists(dragon):
        md = X.read_markers(dragon)
        poses_t = {round(t, 6) for t, _ in X.read_kfseq(dragon)}
        verifier(len(md) > 0 and all(round(t, 6) in poses_t for t, _n, _v in md),
                 f"{len(md)} marqueurs relus, tous sur des clés de pose : {[n for _t, n, _v in md]}")
    else:
        print("  (absent : sauté)")

    print()
    if ECHECS:
        print(f"ÉCHEC : {len(ECHECS)} contrôle(s)")
        sys.exit(1)
    print("tous les contrôles passent")


if __name__ == "__main__":
    main()
