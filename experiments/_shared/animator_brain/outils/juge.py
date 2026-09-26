"""
JUGE d'un ultime, sur des IMAGES en temps réel, contre les refs mesurées de
la même façon (architecture v13, demande de Milan : « vérifie le jugement »).

Né de deux ratés : la v12 présentée à 6/10 prédit (Milan : 4) alors que le
dragon ne vivait que 0,57 s et que l'abstraction plein écran durait 0,1 s ;
et des planches d'instants choisis qui cachaient les durées (CARNET 4b.12).
Le juge ne note pas la beauté : il vérifie les PROPORTIONS DE TEMPS qu'on
a mesurées sur les ultimes de référence (Last Breath, Goku, Serious Punch,
Stoic Bomb, Sunrise), avec le même outil (outils/durees.py, signaux) :

- part d'effet au PIC (lissée sur 0,1 s : un flash d'une image ne compte pas) ;
- plein écran : temps total où l'effet couvre >= 60 % de l'image, et la plus
  longue plage continue ;
- conséquence : temps entre la fin du dernier plein écran et la fin ;
- durée totale.

Seuils = 0,8 x la MÉDIANE des refs (donnée, pas un chiffre inventé) ; la
porte est franchie si toutes les mesures y sont. Un échec n'interdit pas de
montrer : il oblige à le DIRE dans le rapport.

Usage :
  python3 juge.py mesurer <video|gif> <sortie.json> [debut_s] [fin_s] [nom]
  python3 juge.py juger <notre.json> [refs.json]
      (refs par défaut : corpus/clips/juge_refs_ultimes.json)
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from durees import FPS, signaux  # noqa: E402
from planche_ref import extraire  # noqa: E402

REFS = os.path.join(HERE, "..", "corpus", "clips", "juge_refs_ultimes.json")
PLEIN = 0.6


def _runs(masque):
    out, i = [], 0
    while i < len(masque):
        if masque[i]:
            j = i
            while j < len(masque) and masque[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


def mesures_signal(e, fps=FPS):
    e = np.asarray(e, float)
    k = max(1, int(round(0.1 * fps)))
    lisse = np.convolve(e, np.ones(k) / k, mode="same")
    runs = [(a, b) for a, b in _runs(lisse >= PLEIN) if b - a >= 2]
    plein = sum(b - a for a, b in runs) / fps
    long_ = max([(b - a) / fps for a, b in runs], default=0.0)
    fin_plein = runs[-1][1] / fps if runs else None
    duree = len(e) / fps
    return {"duree_s": round(duree, 2), "effet_pic": round(float(lisse.max()), 3),
            "plein_ecran_s": round(plein, 2), "plein_ecran_plus_long_s": round(long_, 2),
            "consequence_s": round(duree - fin_plein, 2) if fin_plein is not None else 0.0}


def mesurer(src, sortie, debut=None, fin=None, nom=None):
    ims = extraire(src, fps=FPS, largeur=320)
    i0 = int((debut or 0) * FPS)
    i1 = int(fin * FPS) if fin else len(ims)
    sig = signaux(ims[i0:i1])
    m = mesures_signal([s["effet"] for s in sig])
    m["nom"] = nom or os.path.basename(src)
    json.dump(m, open(sortie, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(m, ensure_ascii=False))
    return m


CRITERES = ("effet_pic", "plein_ecran_s", "plein_ecran_plus_long_s", "consequence_s")


def juger(notre, refs=None):
    refs = json.load(open(refs or REFS))["refs"]
    n = json.load(open(notre)) if isinstance(notre, str) else notre
    lignes, ok = [], True
    for c in CRITERES:
        # la conséquence n'a de sens que pour un ultime QUI a un plein écran,
        # mesuré sur un extrait complet (pas un GIF coupé)
        rr = [r for r in refs if not (c == "consequence_s" and (r.get("clip_coupe") or r["plein_ecran_s"] <= 0))]
        vals = [r[c] for r in rr if r.get(c) is not None]
        seuil = round(0.8 * float(np.median(vals)), 2)
        passe = n[c] >= seuil
        ok &= passe
        lignes.append({"critere": c, "nous": n[c], "seuil": seuil, "refs": vals, "passe": passe})
    print(f"JUGE : {n.get('nom', notre)}")
    for L in lignes:
        print(f"  {'OK ' if L['passe'] else 'NON'} {L['critere']:26s} nous {L['nous']:6.2f}   seuil {L['seuil']:5.2f}   refs {L['refs']}")
    print("PORTE FRANCHIE" if ok else "PORTE NON FRANCHIE : à dire dans le rapport")
    return ok, lignes


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "mesurer":
        mesurer(a[1], a[2], float(a[3]) if len(a) > 3 else None, float(a[4]) if len(a) > 4 else None,
                a[5] if len(a) > 5 else None)
    elif a and a[0] == "juger":
        juger(a[1], a[2] if len(a) > 2 else None)
    else:
        print(__doc__)
