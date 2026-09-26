import sys, json
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
REF = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/sp2/t_%s.png"
TSB = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/refs/tsb/t_%s.png"
OUT = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/wf/recon_sp2/r/"
def essai(t, nom, p, cam, cible=None, tsb=None):
    w = G.pose(p)
    if cible is None:
        cible = (p.get("x", 0), p.get("hanche", 3.0), p.get("z", 0))
    c = G.camera_orbite(cible, *cam)
    G.cote_a_cote(REF % t, [w], c, sortie=OUT + f"{t}_{nom}.png", titre=nom)
    if tsb:
        G.cote_a_cote(TSB % tsb, [w], c, sortie=OUT + f"{t}_{nom}_tsb.png", titre=nom)
    d = G.descripteurs(w)
    print(nom, G.resume(d))
    print("   pieds", d["pieds"], "tete", d.get("tete"))
    return w, d

from PIL import Image, ImageDraw
import numpy as np
def planche(t, cands, sortie, cols=3, alpha=0.45, ref=None):
    """cands: list of (label, params, cam(az,el,dist,fov), cible or None). overlay only, ref left top."""
    refp = ref or (REF % t)
    R = Image.open(refp).convert("RGB")
    W, H = 480, 270
    Rr = R.resize((W, H))
    tiles = [("REF " + t, Rr)]
    for lab, p, cam, cible in cands:
        w = G.pose(p)
        if cible is None:
            cible = (p.get("x", 0), p.get("hanche", 3.0), p.get("z", 0))
        c = G.camera_orbite(cible, *cam)
        im = G.rendre([w], c, (W, H), "")
        tiles.append((lab, Image.blend(Rr, im, alpha)))
    n = len(tiles); rows = (n + cols - 1) // cols
    out = Image.new("RGB", (cols * W, rows * H))
    d = ImageDraw.Draw(out)
    for i, (lab, im) in enumerate(tiles):
        x, y = (i % cols) * W, (i // cols) * H
        out.paste(im, (x, y)); d.rectangle([x, y, x + 8 * len(lab) + 6, y + 14], fill=(0, 0, 0)); d.text((x + 3, y + 2), lab, fill=(255, 255, 0))
    out.save(OUT + sortie)

def rend_decale(p, cam, cible=None, dxy=(0, 0), taille=(640, 360)):
    w = G.pose(p)
    if cible is None:
        cible = (p.get("x", 0), p.get("hanche", 3.0), p.get("z", 0))
    c = G.camera_orbite(cible, *cam)
    im = G.rendre([w], c, taille, "")
    if dxy != (0, 0):
        bg = Image.new("RGB", taille, (200, 205, 215))
        bg.paste(im, dxy)
        im = bg
    return w, im

def planche2(t, cands, sortie, box=(120, 60, 520, 360), cols=3, alpha=0.5, ref=None, k=1.2):
    """cands: (label, params, cam, dxy). crop box in 640x360 ref coords."""
    refp = ref or (REF % t)
    R = Image.open(refp).convert("RGB").resize((640, 360))
    bw, bh = box[2] - box[0], box[3] - box[1]
    W, H = int(bw * k), int(bh * k)
    tiles = [("REF " + t, R.crop(box).resize((W, H)))]
    for lab, p, cam, dxy in cands:
        w, im = rend_decale(p, cam, None, dxy)
        tiles.append((lab + " rendu", im.crop(box).resize((W, H))))
        tiles.append((lab, Image.blend(R, im, alpha).crop(box).resize((W, H))))
    n = len(tiles); rows = (n + cols - 1) // cols
    out = Image.new("RGB", (cols * W, rows * H))
    d = ImageDraw.Draw(out)
    for i, (lab, im) in enumerate(tiles):
        x, y = (i % cols) * W, (i // cols) * H
        out.paste(im, (x, y)); d.rectangle([x, y, x + 7 * len(lab) + 6, y + 14], fill=(0, 0, 0)); d.text((x + 3, y + 2), lab, fill=(255, 255, 0))
    out.save(OUT + sortie)

def dir_cam(az, el):
    """unit vector from character toward camera (punch frame f=-Z, r=+X)."""
    import numpy as np
    a, e = np.radians(az), np.radians(el)
    f = np.array([0, 0, -1.0]); r = np.array([1.0, 0, 0]); Y = np.array([0, 1.0, 0])
    return np.cos(e) * (np.cos(a) * f + np.sin(a) * r) + np.sin(e) * Y

def vers_torse(p, v):
    """world direction -> (az, el) in torso axes of pose p."""
    import numpy as np
    w = G.pose(p)
    Rt = w["Torso"][0]
    return G._dir_az_el(Rt.T @ np.asarray(v, float), np.array([0, 0, -1.0]), np.array([1.0, 0, 0]))

def monde(az, el):
    import numpy as np
    return G.az_el_vers_dir(az, el)
