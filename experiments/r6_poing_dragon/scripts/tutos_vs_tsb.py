"""
Confronter aux fichiers les affirmations chiffrées des tutos lus par Gemini
(corpus/tutos/gemini_transcriptions_2026-09-25.md), au moment de la frappe
(extension max du bras vers l'avant), sur TSB, sur le pack battleground et
sur notre v7 :
- avance_studs : déplacement du torse vers la cible entre f-15 et f+3
  (Sikasisi : « avancer de 1 à 2 studs à la frappe » ; bizfr : avancer
  puis reculer) ;
- rot_torse_deg : rotation NETTE du torse (lacet, début -> fin de fenêtre) ;
- amp_torse_deg : AMPLITUDE du lacet (max - min) sur la même fenêtre
  (Wimshurst : les hanches tournent). ATTENTION (2026-09-25) : comparer
  les amplitudes, pas les nettes. Notre torse part en contre-rotation puis
  revient, donc sa nette est petite alors que son amplitude est au niveau
  de TSB. Conclure sur la nette avait fait écrire à tort « deux fois moins
  que TSB ».
- fouet_images : image du pic de vitesse du poing moins image du pic de
  rotation du torse (> 0 : le torse mène, « whip frame ») ;
- écart médian entre clés (Sikasisi : 2 à 4 images ; Thundey : 5).
Le fichier TSB (de Milan) n'est jamais versionné ; seules les mesures sortent.
Usage (depuis experiments/_shared) : python3 ../r6_poing_dragon/scripts/tutos_vs_tsb.py <tsb.rbxm> <pack.rbxm>
"""
import sys, numpy as np
sys.path.insert(0, '.'); sys.path.insert(0, 'animator_brain/outils')
from animator_brain import corpus as C, perception as P
import vues as V
AV = np.array([0, 0, -1.0]); B = ("Right Arm", "Left Arm")
def yaw(R):
    f = R @ AV; return np.degrees(np.arctan2(-f[0], -f[2]))
def mes(w, f, h):
    lo = max(0, f - 15); hi = min(len(w) - 1, f + 3)
    avance = float((w[hi]["Torso"][1] - w[lo]["Torso"][1]) @ AV)
    ys = np.unwrap(np.radians([yaw(x["Torso"][0]) for x in w])); vy = np.abs(np.diff(ys, prepend=ys[0]))
    vf = [0.0] + [float(np.linalg.norm(P.tip(b, h) - P.tip(a, h))) for a, b in zip(w, w[1:])]
    pt = lo + int(np.argmax(vy[lo:f + 2])); pf = lo + int(np.argmax(vf[lo:f + 2]))
    rot = float(np.degrees(abs(ys[min(f+1,len(w)-1)] - ys[lo])))
    amp = float(np.degrees(ys[lo:hi + 1].max() - ys[lo:hi + 1].min()))
    return dict(avance_studs=round(avance, 2), rot_torse_deg=round(rot), amp_torse_deg=round(amp), fouet_images=pf - pt)
def cles(s):
    t = np.array([x[0] for x in s["frames"]]) * 60
    return round(float(np.median(np.diff(t))), 1) if len(t) > 1 else None
for path, tag in ((sys.argv[1], "TSB"),
                  (sys.argv[2], "PACK")):
    for s in C.load_rbxm_sequences(path):
        if not any(k in s["name"] for k in ("M1", "M2", "M3", "M4", "Collateral", "Uppercut", "Downslam")): continue
        w = [x[1] for x in C.resample_linear(s["frames"])]
        reach = [max((P.tip(x, h) - x["Torso"][1]) @ AV for h in B) for x in w]
        f = int(np.argmax(reach)); h = max(B, key=lambda h: (P.tip(w[f], h) - w[f]["Torso"][1]) @ AV)
        print(tag, s["name"], "f", f, mes(w, f, h), "ecart_cles_median", cles(s))
W = V.lire_kfseq("../r6_poing_dragon/output/dragon_attaquant.rbxmx")
from animator_brain import roblox_export as X
fr = X.read_kfseq("../r6_poing_dragon/output/dragon_attaquant.rbxmx"); t = np.array([x[0] for x in fr]) * 60
print("v7 ecart cles median", np.median(np.diff(t)), "(rafale f0-110:", np.median(np.diff(t[t < 110])), ")")
for n, f in (("h1", 14), ("h2", 40), ("h3", 64), ("h4", 90), ("coup_charge", 150)):
    h = "Right Arm" if n == "coup_charge" else max(B, key=lambda h: (P.tip(W[f], h) - W[f]["Torso"][1]) @ AV)
    print("v7", n, mes(W, f, h))
