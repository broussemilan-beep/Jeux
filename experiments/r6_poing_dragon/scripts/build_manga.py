"""
Les 3 planches manga du Poing du Dragon (1 image = 2 frames a 60 i/s),
generees depuis NOTRE pose (silhouette rendue dans Blender pendant la
plongee), jamais copiees d'une reference. Grammaire du Serious Punch (TSB) :
1. croquis au trait de la pose + hachures + lignes de vitesse ;
2. silhouette noire au centre d'une explosion de lignes radiales ;
3. grand X blanc sur hachures noires.
Noir et blanc pur, graines fixes (determinisme).

Usage : python3 build_manga.py /chemin/Blender_R6.blend  ->  ../output/manga_1..3.png
"""
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))
import dragon_clip as M  # noqa: E402

W, H = 960, 540


def r2b(v):
    return (float(v[0]), float(-v[2]), float(v[1]))


def render_silhouette(blend, frame=283, direction=(3.4, -2.2, 3.0), tag="manga_sil"):
    """Alpha de l'attaquant seul, vu en contre-plongee de trois-quarts."""
    import bpy
    from mathutils import Vector
    a, b, aw, vw = M.main(blend)
    S = bpy.context.scene
    S.frame_set(frame)
    # la victime n'apparait pas sur la planche. hide_render ne tient pas (les
    # maillages du rig ont des pilotes de visibilite) : on l'eloigne.
    b.primary.location = (b.primary.location[0] + 500.0, b.primary.location[1], b.primary.location[2])
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        if o.type in ("ARMATURE", "EMPTY", "LIGHT"):
            o.hide_render = True
    torso = aw[frame]["Torso"][1]
    fist = M.V.limb_tip(aw[frame], "Right Arm")
    look = (torso * 0.55 + fist * 0.45)
    cam = bpy.data.objects.new("MangaCam", bpy.data.cameras.new("MangaCam"))
    S.collection.objects.link(cam)
    cam.data.lens = 32
    S.camera = cam
    S.render.resolution_x, S.render.resolution_y = W, H
    from bpy_extras.object_utils import world_to_camera_view
    corners = []
    for p, (r, c) in aw[frame].items():
        if p == "HumanoidRootPart":
            continue
        h = np.array(M.SIZES[p]) / 2
        corners += [c + r @ (h * [x, y, z]) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    direction = np.asarray(direction, float) / np.linalg.norm(direction)
    # cadrage : on recule jusqu'a ce que la pose tienne dans 70 % de l'image
    for dist in np.arange(4.0, 40.0, 0.5):
        cam.location = Vector(r2b(look + direction * dist))
        cam.rotation_euler = (Vector(r2b(look)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        pts = [world_to_camera_view(S, cam, Vector(r2b(q))) for q in corners]
        if all(0.15 < q.x < 0.85 and 0.15 < q.y < 0.85 for q in pts):
            break
    S.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in
                                                                        bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "CYCLES"
    if S.render.engine == "CYCLES":
        S.cycles.samples = 4
        S.cycles.device = "CPU"
    S.render.film_transparent = True
    path = os.path.join(M.OUT, "_frames", f"{tag}.png")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    S.render.filepath = path
    bpy.ops.render.render(write_still=True)
    # point du poing a l'ecran (pour centrer les lignes radiales)
    co = world_to_camera_view(S, cam, Vector(r2b(fist)))
    return path, (co.x * W, (1 - co.y) * H)


def speed_lines(draw, center, n, r0, r1, width, color, rng, jitter=0.02):
    cx, cy = center
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        ra = rng.uniform(r0, r0 * 1.6)
        rb = rng.uniform(r1 * 0.8, r1)
        w = rng.uniform(width * 0.4, width)
        a2 = a + rng.uniform(-jitter, jitter)
        p1 = (cx + ra * math.cos(a), cy + ra * math.sin(a))
        p2 = (cx + rb * math.cos(a2), cy + rb * math.sin(a2))
        # trait effile : triangle fin
        nx, ny = -math.sin(a), math.cos(a)
        draw.polygon([p1, (p2[0] + nx * w, p2[1] + ny * w), (p2[0] - nx * w, p2[1] - ny * w)], fill=color)


def hatch(size, spacing, angle_deg, width, color, bg):
    from PIL import Image, ImageDraw
    im = Image.new("L", size, bg)
    d = ImageDraw.Draw(im)
    L = int(math.hypot(*size)) + 10
    a = math.radians(angle_deg)
    cx, cy = size[0] / 2, size[1] / 2
    for k in range(-L, L, spacing):
        ox, oy = cx + k * math.cos(a + math.pi / 2), cy + k * math.sin(a + math.pi / 2)
        d.line([(ox - L * math.cos(a), oy - L * math.sin(a)), (ox + L * math.cos(a), oy + L * math.sin(a))],
               fill=color, width=width)
    return im


def panels(sil_path, fist_px):
    from PIL import Image, ImageChops, ImageDraw, ImageFilter
    alpha = Image.open(sil_path).convert("RGBA").split()[3].point(lambda v: 255 if v > 40 else 0)
    rng = random.Random(7)
    out = []
    # --- 1. croquis : contour epais tremble + hachures dans la silhouette + lignes de vitesse
    p1 = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(p1)
    speed_lines(d, fist_px, 170, 240, 1100, 5, 0, rng, 0.01)
    inner = hatch((W, H), 7, 35, 2, 0, 255)
    p1.paste(inner, (0, 0), alpha)
    edge = alpha.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(7))
    p1.paste(0, (0, 0), edge)
    edge2 = ImageChops.offset(edge, 3, -2)
    p1.paste(0, (0, 0), edge2.point(lambda v: 255 if v > 0 and rng.random() < 0.7 else 0))
    out.append(p1)
    # --- 2. silhouette noire pleine au coeur d'une explosion de lignes radiales
    p2 = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(p2)
    d.ellipse([fist_px[0] - 260, fist_px[1] - 200, fist_px[0] + 260, fist_px[1] + 200], fill=255)
    speed_lines(d, fist_px, 260, 150, 1200, 7, 255, random.Random(3), 0.015)
    speed_lines(d, fist_px, 120, 90, 700, 4, 0, random.Random(4), 0.02)
    p2.paste(0, (0, 0), alpha.filter(ImageFilter.MaxFilter(5)))
    out.append(p2)
    # --- 3. grand X blanc sur hachures noires croisees
    p3 = hatch((W, H), 6, 72, 3, 0, 40)
    p3 = ImageChops.darker(p3, hatch((W, H), 9, 108, 2, 0, 255))
    d = ImageDraw.Draw(p3)
    cx, cy = W / 2, H / 2
    for sgn in (1, -1):
        a = math.atan2(H * 0.95, sgn * W * 0.62)
        ux, uy = math.cos(a), math.sin(a)
        nx, ny = -uy, ux
        Lh, w = 560, 46
        tipA = (cx - ux * Lh, cy - uy * Lh)
        tipB = (cx + ux * Lh, cy + uy * Lh)
        d.polygon([tipA, (cx + nx * w, cy + ny * w), tipB, (cx - nx * w, cy - ny * w)], fill=255)
    out.append(p3)
    paths = []
    for i, p in enumerate(out):
        path = os.path.join(M.OUT, f"manga_{i + 1}.png")
        p.convert("RGB").save(path, optimize=True)
        paths.append(path)
    return paths


if __name__ == "__main__":
    sil, fist = render_silhouette(sys.argv[1], 288, (1.0, -0.2, 0.15))
    print(panels(sil, fist), "poing a l'ecran :", [round(v) for v in fist])
