import sys, json
sys.path.insert(0, "/home/user/Jeux/experiments/_shared/animator_brain/outils")
import geo_pose as G
import numpy as np
D = "/tmp/claude-0/-home-user-Jeux/4796ac9e-8e41-51f7-91c4-7b92a6a187d0/scratchpad/poing/"
OUT = D + "wf/recon_pew_b/rounds/"
REFS = {"4.0": D + "refs/pew/t_04.00.png", "4.4": D + "refs/pew/t_04.40.png",
        "9388": D + "wf/recon_pew_b/still_9388f709.png", "27b0": D + "wf/recon_pew_b/still_27b0a39e.png",
        "27f1": D + "wf/recon_pew_b/still_27f110ee.png", "3.9": D + "refs/pew/t_03.90.png",
        "4.5": D + "refs/pew/t_04.50.png", "4.6": D + "refs/pew/t_04.60.png", "4.2": D + "refs/pew/t_04.20.png"}

def run(name, ref, params, cam, avant=(0, 0, -1), cible=None):
    w = G.pose(params)
    if cible is None:
        cible = w["Torso"][1] + np.array([0, 0.3, 0])
    c = G.camera_orbite(cible, *cam, avant=avant) if len(cam) == 4 else G.camera_orbite(cible, *cam[:4], avant=avant)
    # optional screen offset: shift target in camera right/up
    G.cote_a_cote(REFS[ref], [w], c, sortie=OUT + name + ".png", titre=name)
    d = G.descripteurs(w, avant=avant)
    print(name, G.resume(d))
    return w, d

def cam2(w, az, el, dist, fov, dx=0.0, dy=0.0, avant=(0, 0, -1), cy=0.0):
    """orbit around torso centre (+cy up); then shift look-at by dx (cam right) dy (cam up) studs."""
    c0 = w["Torso"][1] + np.array([0, cy, 0])
    eye, tgt, fv = G.camera_orbite(c0, az, el, dist, fov, avant=avant)
    f = tgt - eye; f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r); u = np.cross(r, f)
    return (eye, tgt + dx * r + dy * u, fv)

def run2(name, ref, params, cam, avant=(0, 0, -1), quiet=False):
    w = G.pose(params)
    c = cam2(w, *cam, avant=avant)
    G.cote_a_cote(REFS[ref], [w], c, sortie=OUT + name + ".png", titre=name)
    d = G.descripteurs(w, avant=avant)
    if not quiet:
        print(name, G.resume(d))
    return w, d, c

L = D + "wf/recon_pew_b/"
REFS.update({"L3.9": L + "lev_t_03.90.png", "L4.0": L + "lev_t_04.00.png", "L4.4": L + "lev_t_04.40.png",
             "L4.5": L + "lev_t_04.50.png", "L4.2": L + "lev_t_04.20.png", "L9388": L + "lev_9388.png", "L27b0": L + "lev_27b0.png"})
FOV = 61.9
# measured from grid vanishing points: pitch (deg down), axis-A angle (deg right of heading)
CAMS = {"L3.9": (13.4, 45.0), "L9388": (13.4, 45.0), "L4.0": (14.2, 33.5), "L4.2": (15.8, 27.5), "L4.4": (15.5, 23.4),
        "L4.5": (16.6, 20.5), "L27b0": (16.8, 19.8)}

def cam3(w, az, el, dist, pitch, yawoff=0.0, fov=FOV, avant=(0, 0, -1), cy=0.0):
    """eye on an orbit around torso centre (az/el/dist, camera_orbite conventions);
    heading = horizontal direction eye->torso rotated by yawoff (deg, + = camera turns to its right);
    pitch = measured camera pitch (deg down)."""
    c0 = w["Torso"][1] + np.array([0, cy, 0])
    eye, _t, _f = G.camera_orbite(c0, az, el, dist, fov, avant=avant)
    h = c0 - eye; h[1] = 0; h /= np.linalg.norm(h)
    a = np.radians(-yawoff)   # rotate heading about +Y; + yawoff = to camera right (clockwise from above)
    Ry = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    h = Ry @ h
    p = np.radians(pitch)
    fwd = np.cos(p) * h + np.array([0, -np.sin(p), 0])
    return (eye, eye + fwd * 5.0, fov)

def run3(name, ref, params, az, el, dist, yawoff=0.0, avant=(0, 0, -1), pitch=None, quiet=False):
    w = G.pose(params)
    pt = CAMS[ref][0] if pitch is None else pitch
    c = cam3(w, az, el, dist, pt, yawoff, avant=avant)
    G.cote_a_cote(REFS[ref], [w], c, sortie=OUT + name + ".png", titre=name)
    d = G.descripteurs(w, avant=avant)
    if not quiet:
        print(name, G.resume(d))
    return w, d, c

def vers_cam(w, part, eye):
    """(az, el) in torso axes pointing from the limb pivot (approx: arm top) toward the camera eye."""
    Rt, pt = w["Torso"]
    top = G.haut(w, part)
    v = Rt.T @ (np.asarray(eye) - top)
    v /= np.linalg.norm(v)
    return G._dir_az_el(v, np.array([0, 0, -1.0]), np.array([1.0, 0, 0]))
