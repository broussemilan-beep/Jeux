"""
Verification visuelle personnelle (pas de Blender/Studio graphique
disponible dans ce sandbox -- voir README). Deux sorties par cycle :
- poses.png : stick-figure 3D a des instants cles (silhouette du combo).
- curves.png : chaque composante d'angle (rx,ry,rz, deg) en fonction du
  temps par articulation, pour lire a l'oeil la fluidite / les
  inversions de sens.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from r6_rig import PART_ORDER, PARENT


def _world_positions_at(samples, sample_idx):
    return {part: samples[part][sample_idx][3] for part in PART_ORDER}


def plot_poses(samples, times_s, sample_hz, out_path, title):
    n_cols = len(times_s)
    fig = plt.figure(figsize=(4 * n_cols, 5))
    for i, t in enumerate(times_s):
        idx = int(round(t * sample_hz))
        idx = min(idx, len(samples["HumanoidRootPart"]) - 1)
        pos = _world_positions_at(samples, idx)
        ax = fig.add_subplot(1, n_cols, i + 1, projection="3d")
        for part in PART_ORDER:
            parent = PARENT.get(part)
            if parent is None:
                continue
            p0, p1 = pos[parent], pos[part]
            ax.plot([p0[0], p1[0]], [p0[2], p1[2]], [p0[1], p1[1]],
                    marker="o", linewidth=3, color="#2266cc")
        head = pos["Head"]
        ax.scatter([head[0]], [head[2]], [head[1]], s=200, color="#cc4422")
        ax.set_title(f"t={t:.2f}s")
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_zlim(-4, 3)
        ax.set_xlabel("X")
        ax.set_ylabel("Z (Roblox -Z=avant -> vers le haut de cet axe ecran)")
        ax.set_zlabel("Y (haut)")
        ax.view_init(elev=15, azim=-60)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def plot_curves(samples, sample_hz, out_path, title, joints=None):
    joints = joints or [p for p in PART_ORDER if p != "HumanoidRootPart"]
    fig, axes = plt.subplots(len(joints), 1, figsize=(9, 2.0 * len(joints)), sharex=True)
    if len(joints) == 1:
        axes = [axes]
    colors = {"x": "#2266cc", "y": "#22aa55", "z": "#cc4422"}
    for ax, part in zip(axes, joints):
        ts = np.array([s[0] for s in samples[part]])
        rot = np.array([s[1] for s in samples[part]])
        for i, axis_name in enumerate(("x", "y", "z")):
            ax.plot(ts, rot[:, i], color=colors[axis_name], label=axis_name, linewidth=1.3)
        ax.axhline(0, color="#999999", linewidth=0.7)
        ax.set_ylabel(part, fontsize=8)
        ax.grid(alpha=0.3)
    axes[0].legend(loc="upper right", fontsize=7, ncol=3)
    axes[-1].set_xlabel("temps (s)")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
