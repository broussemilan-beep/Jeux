"""
CÔTE À CÔTE à VITESSE RÉELLE, calé sur le CONTACT, avec le son.

Pourquoi il existe (2026-09-26, chantier « nouveaux yeux », SYNTHESE_YEUX
rang 1) : le cerveau regardait des IMAGES une par une et des planches, pas le
mouvement à la vitesse où Milan le voit, au cadrage où il le voit, à côté de
la version d'avant (faiblesses 1, 3 et 5 ; motif « je vois aucun changement »,
4 fois). Milan juge en regardant la vidéo avec le son : cet outil met les
versions l'une à côté de l'autre dans ces conditions.

Deux modes :

1. `--video chemin.mp4@t` (2 à 4 fois) : des vidéos déjà rendues, chacune
   décalée pour que son instant `t` (en secondes : le contact) tombe au même
   moment ; lues à leur vraie cadence (vérifiée par ffprobe), le son de la
   PREMIÈRE ; incrustés : le nom, l'image et le temps relatifs au contact ; un
   cadre rouge sur l'image du contact (on voit si la synchro tient).
2. `--export nom=attaquant.rbxmx[,victime.rbxmx][,staging.json][,scene.json]`
   (2 à 4 fois) : NOS exports rendus par le moteur de `moon.py` (même
   interpolation que Roblox), sous DEUX caméras, calés sur le contact :
   - la caméra du PLAN (staging.json de la version ; sans secousse) ;
   - une caméra FIXE de JEU (derrière l'épaule, distance de jeu :
     `geo_pose.CAMERA_JEU`, FOV 70°, 12,5 studs ; hypothèse à mesurer dans
     Studio), ancrée là où est le torse de la version AU CONTACT et fixe sur
     toute la fenêtre (la victime n'y est jamais cachée). Deux caméras parce qu'un côte à côte de versions finales mêle
     changement de caméra et changement de pose (SYNTHESE_YEUX piège 7).
   Sous chaque rendu : la lisibilité de la profondeur depuis cette caméra
   (`geo_pose.profondeur_ambigue` : « BD? » = devant/derrière le torse ne se
   lit pas). `--son` : le mixage des sons du staging de la première version.
   `--planche png` : les mêmes rendus en images fixes à quelques instants
   (pour relire, pas pour juger).

Ce qu'il mesure : rien de plus que le décalage appliqué (affiché) ; il MONTRE.
Ce qu'il NE voit PAS : il ne compare pas et ne dit pas ce qui est mieux
(« juxtaposer n'est pas comparer » : regarder à vitesse réelle, écrire une
phrase en mots de corps, puis mesurer : `outils/carte_changements.py`). En
mode exports : pas d'effets, pas de décor, pas de secousse, pas les images
inversées ni le blanc ; la caméra de jeu est une hypothèse. En mode vidéos :
les vidéos gardent leurs coupes et leurs effets mêlés au mouvement.
Jamais de ref sous droits dans le dépôt : un côte à côte ref | nous reste
dans le scratchpad.

Usage :
  python3 outils/cote_a_cote.py --video v5.mp4@4.717 --video v6.mp4@4.717 --sortie cote.mp4 [--avant 2 --apres 1.5]
  python3 outils/cote_a_cote.py --export v5=A5.rbxmx,V5.rbxmx,st5.json,sc5.json --export v6=... \\
        --sortie cote.mp4 [--avant 2 --apres 1] [--fps 30] [--son] [--faces] [--planche p.png]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import geo_pose as G  # noqa: E402
import moon as M  # noqa: E402
import vues as VU  # noqa: E402

POLICE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sonde(chemin):
    """-> {"fps", "duree", "largeur", "hauteur", "son"} (ffprobe, jamais à l'œil)."""
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,r_frame_rate,width,height:format=duration", "-of", "json", chemin],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    n, q = v["r_frame_rate"].split("/")
    return {"fps": float(n) / float(q), "duree": float(d["format"]["duration"]), "largeur": v["width"],
            "hauteur": v["height"], "son": any(s["codec_type"] == "audio" for s in d["streams"])}


def _echappe(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")


# ------------------------------------------------------------ mode 1 : vidéos
def videos(entrees, sortie, avant=None, apres=None, hauteur=360, fps=None, titres=None):
    """entrees : [(chemin, t_contact)] (2 à 4). -> dict (décalages, durée, vérif)."""
    if not 2 <= len(entrees) <= 4:
        raise ValueError("2 à 4 vidéos")
    infos = [sonde(c) for c, _t in entrees]
    fps = fps or infos[0]["fps"]
    if avant is None:
        avant = min(t for _c, t in entrees)
    if apres is None:
        apres = min(i["duree"] - t for i, (_c, t) in zip(infos, entrees))
    for (c, t), i in zip(entrees, infos):
        if t - avant < -1e-6 or t + apres > i["duree"] + 1e-6:
            raise ValueError(f"{c} : la fenêtre [{t - avant:.2f}, {t + apres:.2f}] s sort de la vidéo ({i['duree']:.2f} s)")
    duree = avant + apres
    n0 = int(round(avant * fps))
    titres = titres or [os.path.splitext(os.path.basename(c))[0] for c, _t in entrees]
    filtres = []
    for k, ((c, t), titre) in enumerate(zip(entrees, titres)):
        debut = t - avant
        txt = _echappe(f"{titre}  (contact à {t:.3f} s)")
        filtres.append(
            f"[{k}:v]trim=start={debut:.6f}:duration={duree:.6f},setpts=PTS-STARTPTS,fps={fps},"
            f"scale=-2:{hauteur},setsar=1,"
            f"drawbox=x=0:y=0:w=iw:h=ih:color=red@0.9:t=8:enable='eq(n\\,{n0})',"
            f"drawtext=fontfile={POLICE}:text='{txt}':x=6:y=6:fontsize=16:fontcolor=white:box=1:boxcolor=black@0.6,"
            f"drawtext=fontfile={POLICE}:text='image %{{eif\\:n-{n0}\\:d}} / %{{eif\\:(t-{avant:.6f})*1000\\:d}} ms du contact':"
            f"x=6:y=h-26:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6[v{k}]")
    lab = "".join(f"[v{k}]" for k in range(len(entrees)))
    if len(entrees) == 4:
        filtres.append(f"{lab}xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[v]")
    else:
        filtres.append(f"{lab}hstack=inputs={len(entrees)}[v]")
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for c, _t in entrees:
        cmd += ["-i", c]
    carte = ["-map", "[v]"]
    if infos[0]["son"]:
        filtres.append(f"[0:a]atrim=start={entrees[0][1] - avant:.6f}:duration={duree:.6f},asetpts=PTS-STARTPTS[a]")
        carte += ["-map", "[a]", "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-filter_complex", ";".join(filtres)] + carte + ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                                                             "-r", str(fps), sortie]
    subprocess.run(cmd, check=True)
    o = sonde(sortie)
    return {"entrees": [{"video": c, "contact_s": t, "debut_s": round(t - avant, 3), "fps": i["fps"]}
                        for (c, t), i in zip(entrees, infos)],
            "decalages_s": [round(t - entrees[0][1], 3) for _c, t in entrees],
            "avant_s": avant, "apres_s": apres, "image_contact_sortie": n0, "sortie": o,
            "son": "celui de " + entrees[0][0] if infos[0]["son"] else "aucun (la première vidéo n'a pas de son)"}


# ------------------------------------------------------------ mode 2 : nos exports
def charger_export(spec):
    """'nom=att.rbxmx[,vic.rbxmx][,staging.json][,scene.json]' -> dict."""
    nom, reste = spec.split("=", 1) if "=" in spec else (None, spec)
    ch = reste.split(",")
    att = ch[0]
    vic = next((c for c in ch[1:] if c.endswith(".rbxmx")), None)
    js = [json.load(open(c)) for c in ch[1:] if c.endswith(".json")]
    staging = next((j for j in js if "camera" in j), None)
    scene = next((j for j in js if "camera" not in j), None)
    src = scene or staging or {}
    contact = src.get("contact_f") or dict(src.get("markers", [])).get("contact")
    dist = src.get("distance", 16.0)
    A = VU.lire_kfseq(att, 60)
    V = VU.lire_kfseq(vic, 60, root=G.racine_victime(dist)) if vic else None
    cacher = next((e for e in (staging or {}).get("events", []) if e.get("kind") == "cacher_victime"), None)
    return {"nom": nom or os.path.basename(att), "A": A, "V": V, "staging": staging, "contact": contact,
            "cacher": cacher, "distance": dist}


def _victime_visible(ex, f):
    c = ex["cacher"]
    if ex["V"] is None:
        return False
    if not c:
        return True
    return f < c.get("debut", 10 ** 9) and not (c["pov"][0] <= f < c["pov"][1])


def _police(t):
    try:
        return ImageFont.truetype(POLICE, t)
    except OSError:
        return None


def rendre_case(ex, f, cam, taille, titre, faces=False, cacher=True):
    fa = int(min(max(f, 0), len(ex["A"]) - 1))
    mondes = [ex["A"][fa]]
    if (_victime_visible(ex, fa) if cacher else ex["V"] is not None):
        mondes.append(ex["V"][min(fa, len(ex["V"]) - 1)])
    im = M.render(mondes, cam[0], cam[1], cam[2], taille, sky=(185, 200, 220), faces=faces,
                  ground=(-16, 16, -ex["distance"] - 16, 16))
    d = ImageDraw.Draw(im)
    fnt = _police(13)
    d.rectangle([0, 0, taille[0], 18], fill=(0, 0, 0))
    d.text((4, 2), titre, fill=(255, 230, 120), font=fnt)
    pr = G.profondeur_ambigue(ex["A"][fa], cam)
    amb = [k for k, v in pr.items() if not k.startswith("_") and v["lecture"] == "ambigu"]
    txt = "profondeur : " + G.resume_profondeur(pr, court=True) + ("  (ambigu : " + ", ".join(amb) + ")" if amb else "")
    d.rectangle([0, taille[1] - 18, taille[0], taille[1]], fill=(0, 0, 0))
    d.text((4, taille[1] - 16), txt, fill=(255, 210, 150), font=fnt)
    return im, pr


def image_composite(exs, rel60, taille, faces=False):
    """Une image : colonnes = versions, lignes = (caméra du plan, caméra de jeu)."""
    W, H = taille
    out = Image.new("RGB", (W * len(exs), H * 2), (0, 0, 0))
    prof = {}
    for k, ex in enumerate(exs):
        f = ex["contact"] + rel60
        # caméra de jeu ANCRÉE à l'endroit où est le torse au contact (fixe sur
        # toute la fenêtre) : l'anim de nos scènes déplace le torse de 11 studs
        # (départ) ; une caméra restée au point de départ ne verrait qu'un point.
        tc = ex["A"][min(ex["contact"], len(ex["A"]) - 1)]["Torso"][1]
        cj = G.camera_jeu(hrp=(float(tc[0]), 3.0, float(tc[2])))
        if ex["staging"]:
            cp = G.camera_plan(ex["staging"], max(0, f))
            tp = "plan écrit"
        else:
            cp = G.camera_orbite(ex["A"][int(min(max(f, 0), len(ex["A"]) - 1))]["Torso"][1], 35, 12, 12.0)
            tp = "3/4 face (pas de staging)"
        rel = f"{rel60:+d} i60 ({rel60 / 60 * 1000:+.0f} ms)"
        im1, p1 = rendre_case(ex, f, cp, taille, f"{ex['nom']} | {tp} | contact {rel}", faces)
        im2, p2 = rendre_case(ex, f, cj, taille, f"{ex['nom']} | caméra de jeu (FOV {cj[2]:.0f}°, "
                              f"{G.CAMERA_JEU['distance']} studs, épaule) | {rel}", faces, cacher=False)
        out.paste(im1, (k * W, 0))
        out.paste(im2, (k * W, H))
        prof[ex["nom"]] = {"plan": p1, "jeu": p2}
    return out, prof


def mixage(staging, debut, duree, sr=None):
    sys.path.insert(0, os.path.join(HERE, "..", "..", "vfx_studio"))
    import sons  # noqa: E402
    sr = sr or sons.SR
    base = os.path.join(HERE, "..", "..", "vfx_studio", "sons")
    tot = int((debut + duree + 4) * sr)
    mix = np.zeros(tot)
    for so in staging.get("sons", []):
        x = sons.lire_wav(os.path.join(base, so["son"] + ".wav"))
        h = so.get("hauteur", 1.0)
        if h != 1.0:
            x = np.interp(np.arange(0, len(x) - 1, h), np.arange(len(x)), x)
        i = int(so["t"] * sr)
        if i >= tot:
            continue
        mix[i:i + len(x)] += so.get("volume", 1.0) * x[: tot - i]
    c = np.max(np.abs(mix)) if len(mix) else 0
    if c > 0.98:
        mix = mix / c * 0.98
    a = int(max(0.0, debut) * sr)
    return mix[a:a + int(duree * sr)], sons


def exports(specs, sortie, avant=2.0, apres=1.0, fps=30, taille=(480, 270), son=False, faces=False, planche=None,
            instants=(-1.5, -1.0, -0.5, -0.25, -0.1, 0.0, 0.25)):
    exs = [charger_export(s) for s in specs]
    for ex in exs:
        if ex["contact"] is None:
            raise ValueError(f"{ex['nom']} : contact inconnu (donner scene.json ou staging.json)")
    d = tempfile.mkdtemp(prefix="cote_")
    n = int(round((avant + apres) * fps)) + 1
    prof_contact = None
    try:
        for k in range(n):
            rel60 = int(round((-avant + k / fps) * 60))
            im, prof = image_composite(exs, rel60, taille, faces)
            if rel60 == 0:
                prof_contact = prof
                ImageDraw.Draw(im).rectangle([0, 0, im.width - 1, im.height - 1], outline=(255, 0, 0), width=6)
            im.save(os.path.join(d, f"f{k:04d}.png"))
        cmd = ["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(d, "f%04d.png")]
        if son and exs[0]["staging"]:
            x, sons = mixage(exs[0]["staging"], exs[0]["contact"] / 60 - avant, n / fps)
            wav = os.path.join(d, "son.wav")
            sons.ecrire_wav(x, wav)
            cmd += ["-i", wav, "-c:a", "aac", "-b:a", "160k", "-shortest"]
        cmd += ["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", sortie]
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if planche:
        rangs = [image_composite(exs, int(round(t * 60)), (taille[0] // 2 + 80, taille[1] // 2 + 45), faces)[0]
                 for t in instants]
        P = Image.new("RGB", (rangs[0].width, sum(r.height for r in rangs)), (0, 0, 0))
        y = 0
        for r in rangs:
            P.paste(r, (0, y))
            y += r.height
        P.save(planche)
    return {"versions": [ex["nom"] for ex in exs], "contacts_i60": [ex["contact"] for ex in exs],
            "avant_s": avant, "apres_s": apres, "images": n, "fps": fps, "camera_jeu": G.CAMERA_JEU,
            "profondeur_au_contact": {v: {c: G.resume_profondeur(p) for c, p in pc.items()}
                                      for v, pc in (prof_contact or {}).items()},
            "sortie": sonde(sortie)}


def main():
    ap = argparse.ArgumentParser(description="côte à côte à vitesse réelle, calé sur le contact")
    ap.add_argument("--video", action="append", default=[], help="chemin.mp4@t_contact_en_secondes")
    ap.add_argument("--titre", action="append", default=[])
    ap.add_argument("--export", action="append", default=[],
                    help="nom=attaquant.rbxmx[,victime.rbxmx][,staging.json][,scene.json]")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--avant", type=float)
    ap.add_argument("--apres", type=float)
    ap.add_argument("--fps", type=float)
    ap.add_argument("--hauteur", type=int, default=360)
    ap.add_argument("--son", action="store_true", help="mode exports : sons du staging de la 1re version")
    ap.add_argument("--faces", action="store_true", help="mode exports : faces colorées et lettrées F/B/R/L/U/D")
    ap.add_argument("--planche", help="mode exports : images fixes à quelques instants (PNG)")
    a = ap.parse_args()
    if a.video:
        ent = []
        for v in a.video:
            c, t = v.rsplit("@", 1)
            ent.append((c, float(t)))
        r = videos(ent, a.sortie, a.avant, a.apres, a.hauteur, a.fps, a.titre or None)
    elif a.export:
        r = exports(a.export, a.sortie, 2.0 if a.avant is None else a.avant, 1.0 if a.apres is None else a.apres,
                    int(a.fps or 30), son=a.son, faces=a.faces, planche=a.planche)
    else:
        sys.exit("--video ou --export")
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str))
    print("Ceci MONTRE, ne juge pas : regarder à vitesse réelle, écrire une phrase en mots de corps, puis mesurer.")


if __name__ == "__main__":
    main()
