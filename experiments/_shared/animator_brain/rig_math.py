"""
Maths de rig partagees par tout le cerveau -- SANS bpy, sans dependance a
un prototype : la geometrie du rig est toujours passee en argument
(`Rig`), jamais importee en dur, pour que les memes outils servent a
n'importe quel rig R6 (ou a une animation Roblox importee).

Convention de rotation : `euler_xyz_matrix` = CFrame.Angles(x, y, z) de
Roblox (Rx @ Ry @ Rz, degres) -- la MEME definition que
anim_engine.euler_xyz_matrix de chaque prototype (voir sa note de module :
jamais la composition interne de Blender).

Format d'echantillons (celui de anim_engine.sample()) :
    samples[part] = [(t, (rx, ry, rz) deg locaux, local_pos, world_pos), ...]
"""
import math
from dataclasses import dataclass

import numpy as np


def euler_xyz_matrix(rx_deg, ry_deg, rz_deg):
    rx, ry, rz = math.radians(rx_deg), math.radians(ry_deg), math.radians(rz_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rx @ Ry @ Rz


def rotation_angle_deg(ra, rb):
    """Angle geodesique (deg) entre deux matrices de rotation -- la seule
    mesure de "combien ca a tourne" independante de l'ordre des axes
    d'Euler (une difference d'angles d'Euler canal par canal ment pres des
    blocages de cardan)."""
    c = (np.trace(ra.T @ rb) - 1.0) / 2.0
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


@dataclass
class Rig:
    part_order: list      # ordre topologique, racine en tete
    parent: dict          # part enfant -> part parent
    part_sizes: dict      # part -> (x, y, z) studs
    joints: dict = None   # joint -> {"part0","part1","C0":{"pos"},"C1":{"pos"}} (necessaire pour l'IK)
    root: str = "HumanoidRootPart"
    lateral_axis: int = 0  # axe lateral dans le repere racine (X pour R6 : bras droit a +X)

    @classmethod
    def from_module(cls, m):
        """Construit depuis un module r6_rig.py de prototype (PART_ORDER,
        PARENT, PART_SIZES, JOINTS)."""
        return cls(list(m.PART_ORDER), dict(m.PARENT), dict(m.PART_SIZES), dict(m.JOINTS))

    @property
    def root_children(self):
        return [p for p in self.part_order if self.parent.get(p) == self.root]

    def joint_of(self, part):
        for name, j in (self.joints or {}).items():
            if j["part1"] == part:
                return j
        return None

    def c0_c1(self, part):
        j = self.joint_of(part)
        return np.array(j["C0"]["pos"], dtype=float), np.array(j["C1"]["pos"], dtype=float)


def fk_pose(rig, local_rots, root_pos):
    """Cinematique directe d'UNE pose (meme equation que
    anim_engine._world_positions : Part1 = Part0 * C0 * T * C1^-1, partie
    translation `c0 - R.c1`, rotations C0/C1 ignorees -- convention
    "espace apercu" de ce depot, la conversion vers le repere du joint est
    faite a l'export). local_rots : part -> (rx, ry, rz) deg. Retourne
    (world_pos, world_rot) dicts."""
    wp, wr = {}, {}
    for part in rig.part_order:
        R = euler_xyz_matrix(*local_rots.get(part, (0.0, 0.0, 0.0)))
        par = rig.parent.get(part)
        if par is None:
            wp[part] = np.array(root_pos, dtype=float)
            wr[part] = R
        else:
            c0, c1 = rig.c0_c1(part)
            wp[part] = wp[par] + wr[par] @ (c0 - R @ c1)
            wr[part] = wr[par] @ R
    return wp, wr


def part_tip(rig, wp, wr, part, end="bottom"):
    half = rig.part_sizes[part][1] / 2.0
    sign = -1.0 if end == "bottom" else 1.0
    return wp[part] + wr[part] @ np.array([0.0, sign * half, 0.0])


def center_of_mass(rig, wp, parts=None):
    """Centre de masse (masse ~ volume de chaque part, densite uniforme --
    comme la physique Roblox par defaut)."""
    parts = parts or [p for p in rig.part_order if p != rig.root]
    tot, acc = 0.0, np.zeros(3)
    for p in parts:
        sx, sy, sz = rig.part_sizes[p]
        m = sx * sy * sz
        tot += m
        acc += m * wp[p]
    return acc / tot


class SampledClip:
    """Vue numpy d'un clip echantillonne : rotations locales/monde, positions
    monde, bouts de membres -- calcule une fois, reutilise par tous les
    metriques de audit.py."""

    def __init__(self, samples, rig):
        self.rig = rig
        parts = [p for p in rig.part_order if p in samples]
        self.parts = parts
        self.t = np.array([s[0] for s in samples[parts[0]]])
        n = len(self.t)
        self.dt = float(np.median(np.diff(self.t))) if n > 1 else 1.0
        self.hz = 1.0 / self.dt
        self.euler = {p: np.array([s[1] for s in samples[p]], dtype=float) for p in parts}
        self.world_pos = {p: np.array([s[3] for s in samples[p]], dtype=float) for p in parts}
        self.local_rot = {p: np.array([euler_xyz_matrix(*e) for e in self.euler[p]]) for p in parts}
        self.world_rot = {}
        for p in parts:
            par = rig.parent.get(p)
            if par is None or par not in self.world_rot:
                self.world_rot[p] = self.local_rot[p]
            else:
                self.world_rot[p] = np.einsum("nij,njk->nik", self.world_rot[par], self.local_rot[p])

    def __len__(self):
        return len(self.t)

    def idx(self, t):
        return int(np.clip(round((t - self.t[0]) / self.dt), 0, len(self.t) - 1))

    def tip(self, part, end="bottom"):
        """Position monde du bout d'un membre (main/pied pour bras/jambes au
        repos pendants) -- meme definition que calibrate.tip_world des
        prototypes (centre de la face du bas), donc les deux mesures
        restent comparables."""
        half = self.rig.part_sizes[part][1] / 2.0
        sign = -1.0 if end == "bottom" else 1.0
        off = np.array([0.0, sign * half, 0.0])
        return self.world_pos[part] + np.einsum("nij,j->ni", self.world_rot[part], off)

    def in_root_frame(self, pts):
        """Exprime des points monde (n,3) dans le repere de la racine (le
        repere "du corps") -- necessaire pour mesurer une symetrie
        gauche/droite qui ne depend pas de l'orientation du personnage."""
        r = self.world_rot[self.rig.root]
        p0 = self.world_pos[self.rig.root]
        return np.einsum("nji,nj->ni", r, pts - p0)

    def local_angular_speed(self, part):
        """Vitesse angulaire LOCALE (deg/s, par rapport au parent) -- c'est
        elle qui porte l'overlap : un bras qui "traine" derriere le torse
        est un bras dont la rotation locale demarre/culmine APRES celle du
        torse."""
        R = self.local_rot[part]
        out = np.zeros(len(R))
        for i in range(1, len(R)):
            out[i] = rotation_angle_deg(R[i - 1], R[i]) / self.dt
        out[0] = out[1] if len(R) > 1 else 0.0
        return out

    def linear_speed(self, part):
        p = self.world_pos[part]
        v = np.zeros(len(p))
        v[1:] = np.linalg.norm(np.diff(p, axis=0), axis=1) / self.dt
        v[0] = v[1] if len(p) > 1 else 0.0
        return v
