"""
Apercu de la technique COMPLETE telle que M1Technique.luau la joue en jeu :
hitstop, flash, etincelles, onde de choc, trainee du poing, recul de la
victime, secousse de camera -- memes parametres que M1.CONFIG (lus dans le
source Luau, pas recopies a la main), memes marqueurs (trail_on / hit /
trail_off) que le .rbxmx.

C'est une APPROXIMATION du rendu Roblox des particules (Cycles, sans ecran) :
formes et couleurs simplifiees, mais positions, directions et timings
calcules comme dans le module. Sortie : output/m1_technique_apercu.gif

Usage : python3 render_vfx_preview.py /chemin/Blender_R6.blend
"""
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "_shared"))

import m1_clip as M  # noqa: E402
from animator_brain import v222_rig as V  # noqa: E402
from animator_brain.roblox_export import B2R  # noqa: E402

LUAU = open(os.path.join(HERE, "..", "luau", "M1Technique.luau")).read()


def cfg(name):
    m = re.search(rf"\b{name}\s*=\s*([0-9.]+)", LUAU)
    return float(m.group(1))


def cfg_color(name):
    m = re.search(rf"{name}\s*=\s*Color3\.fromRGB\((\d+),\s*(\d+),\s*(\d+)\)", LUAU)
    return tuple(int(x) / 255.0 for x in m.groups())


HITSTOP, KB, KB_T = cfg("HITSTOP"), cfg("KNOCKBACK"), cfg("KNOCKBACK_TIME")
SHAKE_A, SHAKE_T = cfg("SHAKE_AMPLITUDE"), cfg("SHAKE_DURATION")
FLASH_C, SPARK_C, RING_C, TRAIL_C = (cfg_color(n) for n in ("FLASH_COLOR", "SPARK_COLOR", "RING_COLOR", "TRAIL_COLOR"))
T_HIT, T_ON, T_OFF = M.IMPACT_F / 60, 10 / 60, 21 / 60
GIF_FPS = 30


def r2b(v):
    return B2R.T @ np.asarray(v, float)


def emissive(name, color, strength):
    import bpy
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1.0)
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs["Fac"].default_value = 1.0          # 1 = opaque (emission), 0 = transparent
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return mat, mix


def scene_frame(t):
    """Horloge de l'animation avec hitstop (les deux pistes figees)."""
    if t < T_HIT:
        return t * 60
    if t < T_HIT + HITSTOP:
        return T_HIT * 60
    return (t - HITSTOP) * 60


def main(blend):
    import bpy
    from mathutils import Euler, Vector
    from PIL import Image
    a, b, wa, wb, d = M.main(blend)
    S = bpy.context.scene
    rng = np.random.default_rng(7)

    # contact et sens du coup, EXACTEMENT comme le module : bout du bras droit
    # et LookVector du HumanoidRootPart de l'attaquant, a la frame du marqueur hit
    wi = wa[M.IMPACT_F][1]
    contact_r = V.limb_tip(wi, "Right Arm")
    dir_r = wi["HumanoidRootPart"][0] @ np.array([0.0, 0.0, -1.0])
    contact, dirb = r2b(contact_r), r2b(dir_r)
    print("contact (Roblox)", np.round(contact_r, 3), "sens du coup (Roblox)", np.round(dir_r, 3))

    # objets VFX
    flash_mat, flash_mix = emissive("fx_flash", FLASH_C, 25.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=tuple(contact))
    flash = bpy.context.active_object
    flash.data.materials.append(flash_mat)
    ring_mat, ring_mix = emissive("fx_ring", RING_C, 12.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.5, minor_radius=0.06, location=tuple(contact + dirb * 0.3))
    ring = bpy.context.active_object
    ring.rotation_mode = "QUATERNION"
    ring.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(dirb))   # axe du tore = sens du coup
    ring.data.materials.append(ring_mat)
    spark_mat, spark_mix = emissive("fx_spark", SPARK_C, 20.0)
    sparks = []
    for _ in range(16):
        # cone de 38 deg autour du sens du coup (EmissionDirection = Front)
        th = math.radians(38) * math.sqrt(rng.random())
        ph = rng.random() * 2 * math.pi
        perp1 = np.cross(dirb, [0, 0, 1.0])
        perp1 /= np.linalg.norm(perp1)
        perp2 = np.cross(dirb, perp1)
        vdir = math.cos(th) * dirb + math.sin(th) * (math.cos(ph) * perp1 + math.sin(ph) * perp2)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(contact))
        sp = bpy.context.active_object
        sp.data.materials.append(spark_mat)
        sparks.append((sp, vdir, rng.uniform(28, 46), rng.uniform(0.16, 0.3)))
    trail_mat, trail_mix = emissive("fx_trail", TRAIL_C, 6.0)
    trail_mix.inputs["Fac"].default_value = 0.55
    trail_me = bpy.data.meshes.new("fx_trail")
    trail = bpy.data.objects.new("fx_trail", trail_me)
    trail.data.materials.append(trail_mat)
    S.collection.objects.link(trail)

    # historique de la trainee : segment milieu -> bout du bras droit (comme
    # les attachments M1_TrailTop (0,-0.2,0) et M1_TrailFist (0,-1,0))
    def arm_segment():
        w = V.current_parts(a)
        r, p = w["Right Arm"]
        return r2b(p + r @ np.array([0, -0.2, 0.0])), r2b(p + r @ np.array([0, -1.0, 0.0]))

    victim_home = b.primary.location.copy()
    cam_base = None
    tmp = os.path.join(M.OUT, "_fx")
    os.makedirs(tmp, exist_ok=True)
    frames = []
    history = []
    t_end = M.ATT_END_F / 60 + HITSTOP + 0.1
    n = int(round(t_end * GIF_FPS)) + 1
    for k in range(n):
        t = k / GIF_FPS
        sf = scene_frame(t)
        S.frame_set(int(math.floor(sf)), subframe=sf - math.floor(sf))
        # recul de la victime : apres le hitstop, dans le sens du coup
        tk = t - (T_HIT + HITSTOP)
        u = 0.0 if tk <= 0 else min(1.0, tk / KB_T)
        u = 1 - (1 - u) ** 2                                   # Quad Out
        b.primary.location = victim_home + Vector(tuple(dirb * KB * u))
        bpy.context.view_layer.update()
        # trainee : segments echantillonnes, visibles 0,1 s
        anim_t = sf / 60
        if T_ON <= anim_t <= T_OFF:
            history.append((t, *arm_segment()))
        history = [h for h in history if t - h[0] <= 0.1]
        verts, faces = [], []
        for i, (_th, top, fist) in enumerate(history):
            verts += [tuple(top), tuple(fist)]
            if i:
                faces.append((2 * i - 2, 2 * i - 1, 2 * i + 1, 2 * i))
        trail_me.clear_geometry()
        if len(history) > 1:
            trail_me.from_pydata(verts, [], faces)
        trail.hide_render = len(history) < 2
        # impact : age depuis le marqueur hit (le temps reel continue pendant le hitstop)
        age = t - T_HIT
        on = age >= 0
        fa = age / 0.1
        flash.hide_render = not (on and fa < 1)
        if on and fa < 1:
            size = 0.5 + (3.4 - 0.5) * fa / 0.25 if fa < 0.25 else 3.4 * (1 - (fa - 0.25) / 0.75)
            flash.scale = (size, size, size)
            flash_mix.inputs["Fac"].default_value = 1 - 0.6 * fa
        ra = age / 0.2
        ring.hide_render = not (on and ra < 1)
        if on and ra < 1:
            e = 1 - (1 - ra) ** 2
            s = (0.8 + (7 - 0.8) * e) / 1.0
            ring.scale = (s, s, 1.0)
            ring_mix.inputs["Fac"].default_value = (1 - 0.25) * (1 - e)
        for sp, vdir, v0, life in sparks:
            alive = on and age < life
            sp.hide_render = not alive
            if alive:
                # Drag : la vitesse perd la moitie tous les 1/Drag s ; gravite -35 studs/s^2 (Y)
                drag = 9.0
                dist = v0 * (1 - 2 ** (-drag * age)) / (drag * math.log(2))
                pos = contact + vdir * dist + np.array([0, 0, -0.5 * 35 * age * age])
                sp.location = tuple(pos)
                sz = 0.32 * (1 - age / life)
                sp.scale = (sz * 0.35, sz * 0.35, sz * 1.6)
                sp.rotation_mode = "QUATERNION"
                sp.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(Vector(vdir))
        # camera de jeu + secousse (decroissance quadratique, comme le module)
        p = V.review_render(os.path.join(tmp, "probe"), views=(), res=360, samples=10, target=(0.0, d / 2),
                            center_z=2.6, ortho=7.5, aspect=1.2) if k == 0 else None
        cam = bpy.data.objects["ReviewCam"]
        if cam_base is None:
            dist_c = 12.0
            loc = Vector((0.0 + dist_c * 0.8, d / 2 - dist_c * 0.55, 2.6 + dist_c * 0.3))
            cam.location = loc
            cam.rotation_euler = (Vector((0.0, d / 2, 2.6)) - loc).to_track_quat("-Z", "Y").to_euler()
            cam_base = (cam.location.copy(), cam.rotation_euler.copy())
        cam.location, cam.rotation_euler = cam_base[0].copy(), cam_base[1].copy()
        ks = age / SHAKE_T
        if on and ks < 1:
            amp = SHAKE_A * (1 - ks) ** 2
            off = Vector(((rng.random() * 2 - 1) * amp, (rng.random() * 2 - 1) * amp, 0.0))
            cam.location = cam.location + cam.matrix_world.to_3x3() @ off
        S.render.filepath = os.path.join(tmp, f"fx{k:03d}.png")
        bpy.ops.render.render(write_still=True)
        frames.append(Image.open(S.render.filepath).convert("RGB"))
    pal = frames[int(T_HIT * GIF_FPS) + 1].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
    out = os.path.join(M.OUT, "m1_technique_apercu.gif")
    q[0].save(out, save_all=True, append_images=q[1:] + [q[-1]] * 10, duration=33, loop=0, disposal=2,
              optimize=False)
    # planche : l'impact et ses suites
    keys = [int(round(x * GIF_FPS)) for x in (T_ON + 0.05, T_HIT, T_HIT + 0.05, T_HIT + 0.1, T_HIT + 0.17, T_HIT + 0.3)]
    w, h = frames[0].size
    sheet = Image.new("RGB", (3 * w, 2 * h), (255, 255, 255))
    for i, kk in enumerate(keys):
        sheet.paste(frames[min(kk, len(frames) - 1)], ((i % 3) * w, (i // 3) * h))
    sheet.save(os.path.join(M.OUT, "m1_technique_impact.png"))
    print("gif :", out, len(q), "images ; planche : m1_technique_impact.png")


if __name__ == "__main__":
    main(sys.argv[1])
