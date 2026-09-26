"""
Essai « refaire autrement » : le coup chargé aérien façon Saitama / obari
punch, construit avec la méthode apprise des tutos et de l'obari punch
(corpus/tutos/SYNTHESE_ETUDE_COMPLETE.md, images de Milan) :

  1. ARMÉ TENU ~1 s (60 f) : pose « Serious Punch » en l'air au-dessus de la
     victime, corps d'abord (torse enroulé, détourné), poing armé derrière,
     l'autre bras vise ; tenue VIVANTE (petits cercles qui ralentissent) ;
     fond remplacé : aplat + lignes radiales ; la caméra avance lentement.
  2. LE POING VERS L'OBJECTIF en 6 f : la caméra est du point de vue de la
     victime (elle ne peut donc pas être entre l'objectif et le poing) ;
     grand angle ; le bras est aussi TRANSLATÉ vers l'objectif (bras
     « disloqué », permis par le moteur) : le poing finit à ~1 stud et
     remplit ~45 % de l'image. Rien n'est agrandi : c'est la perspective.
  3. COUPE sur le plan large de la conséquence.

Usage : python3 saitama_obari.py <dossier_sortie>
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "outils"))
import moon as M  # noqa: E402

VICTIM = np.array([0.0, 1.2, 0.0])
CAM_EYE = np.array([0.2, 1.9, -0.6])           # juste au-dessus de la victime, regarde vers le haut
ATT = np.array([0.0, 5.4, 1.2])               # attaquant en l'air, à ~4 studs de l'objectif : il REMPLIT le cadre


def attacker(yaw, pitch, roll, strike_dir, strike_tr, free_dir, knee, back_leg, root=ATT):
    p = M.neutral()
    p["root"] = (np.asarray(root, float), M.E(yaw, pitch, roll))
    rt = p["root"][1]
    p["Right Arm"] = (rt.T @ M.aim(strike_dir), rt.T @ np.asarray(strike_tr, float))
    p["Left Arm"] = (rt.T @ M.aim(free_dir), np.zeros(3))
    p["Left Leg"] = (rt.T @ M.aim(knee), np.zeros(3))
    p["Right Leg"] = (rt.T @ M.aim(back_leg), np.zeros(3))
    w = M.world(p)
    fwd = CAM_EYE - w["Head"][1]
    p["Head"] = (rt.T @ M._align(np.array([0, 0, -1.0]), fwd), np.zeros(3))   # regarde la victime (l'objectif)
    return p


def victim():
    p = M.neutral()
    p["root"] = (VICTIM, M.E(180, 85, 0))        # couchée sur le dos, regarde le ciel
    p["Right Arm"] = (M.E(0, 0, 40), np.zeros(3)); p["Left Arm"] = (M.E(0, 0, -40), np.zeros(3))
    return p


def to_cam(frm):
    d = CAM_EYE - frm
    return d / np.linalg.norm(d)


# --- clés (60 i/s). Le corps d'abord, puis les bras, puis la tête (déjà dans attacker()).
def keys():
    sh = ATT + np.array([1.0, 0.5, 0.0])
    # 2e passe (vue sur la planche) : le genou pointé vers l'objectif CACHAIT tout le corps ;
    # on le rentre sur le côté, jambe arrière qui traîne haut : la silhouette se lit de dessous
    # 3e passe : la charge se juge depuis SA caméra (3/4 face basse), pas depuis le point de vue du coup
    charge = attacker(35, -20, 12, strike_dir=(0.75, 0.6, 0.3), strike_tr=(0.25, 0.15, 0.2),
                      free_dir=to_cam(ATT), knee=(-0.45, -0.85, -0.3), back_leg=(0.5, -0.4, 0.75))
    K = [(0, charge)]
    for f in range(5, 61, 5):                  # tenue vivante : petits cercles qui ralentissent
        p = M.wiggle(charge, "root", f, amp_deg=2.0, period=14, decay=30)
        K.append((f, M.wiggle(p, "Right Arm", f, amp_deg=3.0, period=14, decay=30)))
    drag = attacker(30, -50, 0, strike_dir=(0.5, 0.3, 0.8), strike_tr=(0, 0, 0.3),
                    free_dir=(-0.6, 0.6, 0.5), knee=(0.0, -0.2, -0.9), back_leg=(0.1, 0.0, 1.0))
    K.append((62, drag))                        # le bras traîne derrière un corps qui a déjà tourné
    # le CORPS plonge vers l'objectif (d'abord), le bras suit et se déboîte
    hit = attacker(-35, -65, 0, strike_dir=to_cam(sh), strike_tr=to_cam(sh) * 0.7,
                   free_dir=(-0.7, 0.5, 0.5), knee=(0.0, 0.0, -1.0), back_leg=(0.15, 0.5, 0.85),
                   root=ATT + to_cam(ATT) * 0.7)
    K.append((65, hit))
    over = attacker(-40, -68, 0, strike_dir=to_cam(sh), strike_tr=to_cam(sh) * 1.0,
                    free_dir=(-0.75, 0.5, 0.45), knee=(0.0, 0.0, -1.0), back_leg=(0.15, 0.55, 0.8),
                    root=ATT + to_cam(ATT) * 1.05)
    K.append((67, over))                        # dépasse : le poing vient presque toucher l'objectif
    return K


def radial(color, center_fn, n=90, seed=3):
    rng = np.random.default_rng(seed)

    def draw(d, proj, W, H):
        d.rectangle([0, 0, W, H], fill=color)
        cx, cy = center_fn(proj)
        R = np.hypot(W, H)
        for _ in range(n):
            a = rng.uniform(0, 2 * np.pi); w = rng.uniform(0.003, 0.012); r0 = R * rng.uniform(0.18, 0.4)
            pts = [(cx + np.cos(a) * r0, cy + np.sin(a) * r0), (cx + np.cos(a + w) * R, cy + np.sin(a + w) * R),
                   (cx + np.cos(a - w) * R, cy + np.sin(a - w) * R)]
            d.polygon(pts, fill=(235, 240, 255))
    return draw


def main(out):
    from PIL import Image
    os.makedirs(out, exist_ok=True)
    fd = os.path.join(out, "frames"); os.makedirs(fd, exist_ok=True)
    frames = M.sample(keys(), 68)
    vw = M.world(victim())
    look = ATT + np.array([0.3, 0.2, 0.0])
    imgs = []
    CH_EYE = np.array([3.6, 3.1, -5.2])         # plan de la CHARGE : 3/4 face, en contre-plongée
    for f, fr in enumerate(frames):
        w = M.world(fr)
        fist = M.tip(w, "Right Arm")
        if f < 61:                               # 1. armé tenu, la caméra avance lentement (1,2 stud en 1 s)
            k = f / 60.0
            eye = CH_EYE + (ATT - CH_EYE) / np.linalg.norm(ATT - CH_EYE) * 1.2 * k
            bg = radial((40, 110, 220), lambda proj, c=w["Torso"][1]: proj(c)[0])
            imgs.append(M.render([w], eye=eye, target=ATT + np.array([0, 0.2, 0]), fov=50, backdrop=bg, ground=False))
        else:                                    # 2. COUPE sur le point de vue de la victime : le poing vient dans l'objectif
            bg = radial((210, 60, 40), lambda proj, fist=fist: proj(fist)[0])
            imgs.append(M.render([w], eye=CAM_EYE, target=look, fov=85, backdrop=bg, ground=False))
    # 3. coupe : plan large de la conséquence (6 f de flash blanc puis le plan)
    last = frames[-1]
    hitpose = attacker(-35, -70, 0, strike_dir=(0, -1, 0), strike_tr=(0, 0, 0), free_dir=(-0.7, 0.5, 0.5),
                       knee=(0, 0, -1), back_leg=(0.15, 0.55, 0.8), root=VICTIM + np.array([0, 3.4, 0.6]))
    for i in range(4):
        imgs.append(Image.new("RGB", (640, 360), (255, 255, 255)))

    def dome(d, proj, r):
        c, _z = proj(VICTIM * np.array([1, 0, 1]))
        d.ellipse([c[0] - r * 2.2, c[1] - r * 0.5, c[0] + r * 2.2, c[1] + r * 0.5], outline=(255, 240, 200), width=4)
    for i in range(40):
        imgs.append(M.render([M.world(hitpose), vw], eye=(16, 9, -22), target=(0, 2, 0), fov=40,
                             extra=lambda d, proj, i=i: dome(d, proj, 20 + 6 * i)))
    for i, im in enumerate(imgs):
        im.save(os.path.join(fd, f"f{i:04d}.png"))
    M.video(fd, os.path.join(out, "saitama_obari_essai.mp4"))
    pick = [0, 30, 60, 62, 64, 65, 66, 67, 71, 90]
    W, H = 320, 180
    S = Image.new("RGB", (W * 5, H * 2))
    for i, f in enumerate(pick):
        S.paste(imgs[f].resize((W, H)), ((i % 5) * W, (i // 5) * H))
    S.save(os.path.join(out, "saitama_obari_planche.png"))
    # part du cadre couverte par le poing à f67
    w = M.world(frames[-1]); fist = M.tip(w, "Right Arm")
    print("distance poing-objectif f67 :", round(float(np.linalg.norm(fist - CAM_EYE)), 2), "stud")


if __name__ == "__main__":
    main(sys.argv[1])
