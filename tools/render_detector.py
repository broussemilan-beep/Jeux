"""
render_detector.py
====================
Detecteur de rendu automatique pour pipeline headless Godot 4.

Objectif : verifier factuellement, a partir d'une sequence d'images capturees
pendant l'execution d'une action, que chaque "couche visuelle" attendue
(declaree dans un fichier de recette JSON) produit bien un changement de
pixels mesurable dans la region d'ecran et la fenetre de ticks attendues.

Ceci N'EST PAS un juge esthetique. Aucune IA de vision n'est utilisee.
Toutes les metriques sont deterministes : deltas de luminosite, deltas de
canaux de couleur (RGB), et deltas d'ecart-type (proxy de "texture/opacite
ajoutee") calcules avec numpy sur des tableaux de pixels (Pillow -> numpy).

Fonctionne 100% en local, sans GPU, sans reseau, sans dependance a un
rendu OpenGL/Vulkan reel pour l'analyse (seule la capture du jeu, faite en
amont par le pipeline existant, utilise le rendu logiciel llvmpipe).

Dependances : numpy, Pillow (deja utilisees dans le pipeline utilisateur).
"""

from __future__ import annotations

import json
import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# 1. Schema JSON des "couches attendues" (a ajouter aux recettes existantes)
# ---------------------------------------------------------------------------
#
# Exemple de bloc a inserer dans un fichier de recette d'effet existant :
#
# {
#   "expected_layers": [
#     {
#       "id": "ground_crack",
#       "description": "Fissure au sol sous la cible",
#       "region_pct": { "x0": 0.35, "y0": 0.55, "x1": 0.65, "y1": 0.85 },
#       "tick_window": { "start": 2, "end": 10 },
#       "detection": {
#         "metric": "luminance_delta",      // luminance_delta | channel_delta | stddev_delta
#         "channel": null,                    // "r"|"g"|"b" si metric == channel_delta
#         "min_delta": 12.0,                  // seuil (0-255) au-dessus duquel on considere un changement
#         "min_pixel_fraction": 0.02          // fraction min. de pixels de la region qui doivent depasser le seuil
#       }
#     },
#     {
#       "id": "dust_puff",
#       "description": "Nuage de poussiere a l'impact",
#       "region_pct": { "x0": 0.40, "y0": 0.60, "x1": 0.60, "y1": 0.80 },
#       "tick_window": { "start": 0, "end": 6 },
#       "detection": {
#         "metric": "stddev_delta",
#         "min_delta": 5.0,
#         "min_pixel_fraction": 0.01
#       }
#     }
#   ]
# }
#
# region_pct : coordonnees en fraction [0,1] de la largeur/hauteur de l'image,
#              (x0,y0) = coin haut-gauche, (x1,y1) = coin bas-droit.
# tick_window: fenetre de ticks (indices de frame capturee) pendant laquelle
#              le changement doit apparaitre, relative au tick de declenchement
#              de l'action (tick 0 = frame ou l'input a ete envoye).
# detection.metric:
#   - "luminance_delta": delta de luminosite moyenne perceptuelle (0.2126R+0.7152G+0.0722B)
#   - "channel_delta": delta sur un canal RGB specifique (utile pour flash blanc, teinte rouge, etc.)
#   - "stddev_delta": delta d'ecart-type des valeurs de pixels dans la region
#                     (detecte l'apparition de texture/detail meme sans changement
#                      de luminosite moyenne, utile pour particules/poussiere)


@dataclass
class Region:
    x0: float
    y0: float
    x1: float
    y1: float

    def to_pixel_box(self, width: int, height: int) -> Tuple[int, int, int, int]:
        px0 = max(0, int(round(self.x0 * width)))
        py0 = max(0, int(round(self.y0 * height)))
        px1 = min(width, int(round(self.x1 * width)))
        py1 = min(height, int(round(self.y1 * height)))
        if px1 <= px0 or py1 <= py0:
            raise ValueError(f"Region invalide apres conversion en pixels: {(px0, py0, px1, py1)}")
        return px0, py0, px1, py1


@dataclass
class TickWindow:
    start: int
    end: int

    def contains(self, tick: int) -> bool:
        return self.start <= tick <= self.end


@dataclass
class Detection:
    metric: str  # "luminance_delta" | "channel_delta" | "stddev_delta"
    min_delta: float
    min_pixel_fraction: float = 0.01
    channel: Optional[str] = None  # "r" | "g" | "b"

    def __post_init__(self):
        valid_metrics = {"luminance_delta", "channel_delta", "stddev_delta"}
        if self.metric not in valid_metrics:
            raise ValueError(f"metric doit etre l'un de {valid_metrics}, recu: {self.metric}")
        if self.metric == "channel_delta" and self.channel not in {"r", "g", "b"}:
            raise ValueError("channel_delta requiert 'channel' parmi r/g/b")


@dataclass
class ExpectedLayer:
    id: str
    region: Region
    tick_window: TickWindow
    detection: Detection
    description: str = ""

    @staticmethod
    def from_dict(d: dict) -> "ExpectedLayer":
        r = d["region_pct"]
        region = Region(r["x0"], r["y0"], r["x1"], r["y1"])
        tw = d["tick_window"]
        tick_window = TickWindow(tw["start"], tw["end"])
        det = d["detection"]
        detection = Detection(
            metric=det["metric"],
            min_delta=det["min_delta"],
            min_pixel_fraction=det.get("min_pixel_fraction", 0.01),
            channel=det.get("channel"),
        )
        return ExpectedLayer(
            id=d["id"],
            region=region,
            tick_window=tick_window,
            detection=detection,
            description=d.get("description", ""),
        )


# ---------------------------------------------------------------------------
# 2. Metriques de bas niveau (numpy pur, pas de dependance GPU)
# ---------------------------------------------------------------------------

def _to_array(img: Union[Image.Image, np.ndarray]) -> np.ndarray:
    """Convertit une image Pillow en tableau numpy RGB float32 (H, W, 3)."""
    if isinstance(img, np.ndarray):
        arr = img
    else:
        arr = np.asarray(img.convert("RGB"))
    return arr.astype(np.float32)


def _luminance(arr: np.ndarray) -> np.ndarray:
    """Luminosite perceptuelle par pixel, formule ITU-R BT.709."""
    return 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]


def _crop(arr: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
    x0, y0, x1, y1 = box
    return arr[y0:y1, x0:x1, :]


def compute_metric(baseline_crop: np.ndarray, frame_crop: np.ndarray, detection: Detection) -> Dict[str, float]:
    """
    Calcule la metrique demandee entre une region "baseline" (avant l'effet,
    typiquement le tout premier frame capture) et la meme region dans un
    frame donne de la sequence.

    Retourne un dict avec les valeurs brutes utiles au rapport.
    """
    if detection.metric == "luminance_delta":
        base_lum = _luminance(baseline_crop)
        frame_lum = _luminance(frame_crop)
        delta = np.abs(frame_lum - base_lum)
        pixel_fraction = float(np.mean(delta >= detection.min_delta))
        return {
            "mean_delta": float(np.mean(delta)),
            "max_delta": float(np.max(delta)),
            "pixel_fraction_above_threshold": pixel_fraction,
        }

    if detection.metric == "channel_delta":
        ch_idx = {"r": 0, "g": 1, "b": 2}[detection.channel]
        base_ch = baseline_crop[..., ch_idx]
        frame_ch = frame_crop[..., ch_idx]
        delta = np.abs(frame_ch - base_ch)
        pixel_fraction = float(np.mean(delta >= detection.min_delta))
        return {
            "mean_delta": float(np.mean(delta)),
            "max_delta": float(np.max(delta)),
            "pixel_fraction_above_threshold": pixel_fraction,
        }

    if detection.metric == "stddev_delta":
        base_std = float(np.std(baseline_crop))
        frame_std = float(np.std(frame_crop))
        delta = abs(frame_std - base_std)
        # Pour stddev, la "fraction de pixels" n'a pas de sens pixel-a-pixel ;
        # on renvoie 1.0 si le delta global depasse le seuil, sinon 0.0,
        # et on expose delta pour transparence dans le rapport.
        pixel_fraction = 1.0 if delta >= detection.min_delta else 0.0
        return {
            "baseline_stddev": base_std,
            "frame_stddev": frame_std,
            "mean_delta": delta,
            "max_delta": delta,
            "pixel_fraction_above_threshold": pixel_fraction,
        }

    raise ValueError(f"Metrique inconnue: {detection.metric}")


# ---------------------------------------------------------------------------
# 3. Analyse d'une sequence de frames pour une couche attendue
# ---------------------------------------------------------------------------

@dataclass
class LayerVerdict:
    layer_id: str
    status: str  # "present" | "absent" | "incertain"
    best_tick: Optional[int]
    metrics_by_tick: Dict[int, Dict[str, float]]
    reason: str

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "status": self.status,
            "best_tick": self.best_tick,
            "reason": self.reason,
            "metrics_by_tick": self.metrics_by_tick,
        }


def analyze_layer(
    frames: List[Image.Image],
    layer: ExpectedLayer,
    baseline_tick: int = 0,
) -> LayerVerdict:
    """
    frames: liste ordonnee d'images (tick 0 = frame juste avant/au moment du
            declenchement de l'action, tick i = frame capturee i ticks plus tard).
    layer:  specification de la couche attendue (region, fenetre, seuils).
    baseline_tick: index du frame de reference "avant effet" (par defaut le premier).
    """
    if not frames:
        raise ValueError("La liste de frames est vide.")

    width, height = frames[0].size
    box = layer.region.to_pixel_box(width, height)

    baseline_arr = _to_array(frames[baseline_tick])
    baseline_crop = _crop(baseline_arr, box)

    metrics_by_tick: Dict[int, Dict[str, float]] = {}
    detected_ticks: List[int] = []

    for tick, frame in enumerate(frames):
        if not layer.tick_window.contains(tick):
            continue
        frame_arr = _to_array(frame)
        frame_crop = _crop(frame_arr, box)
        m = compute_metric(baseline_crop, frame_crop, layer.detection)
        metrics_by_tick[tick] = m

        meets_delta = m["mean_delta"] >= layer.detection.min_delta or m["max_delta"] >= layer.detection.min_delta
        meets_fraction = m["pixel_fraction_above_threshold"] >= layer.detection.min_pixel_fraction
        if meets_delta and meets_fraction:
            detected_ticks.append(tick)

    if not metrics_by_tick:
        return LayerVerdict(
            layer_id=layer.id,
            status="incertain",
            best_tick=None,
            metrics_by_tick={},
            reason=(
                f"Aucun frame capture ne tombe dans la fenetre de ticks "
                f"[{layer.tick_window.start}, {layer.tick_window.end}]. "
                f"Verifier la frequence de capture ou la fenetre declaree."
            ),
        )

    if detected_ticks:
        best_tick = max(detected_ticks, key=lambda t: metrics_by_tick[t]["mean_delta"])
        return LayerVerdict(
            layer_id=layer.id,
            status="present",
            best_tick=best_tick,
            metrics_by_tick=metrics_by_tick,
            reason=(
                f"Changement mesurable detecte au tick {best_tick} "
                f"(mean_delta={metrics_by_tick[best_tick]['mean_delta']:.2f}, "
                f"fraction={metrics_by_tick[best_tick]['pixel_fraction_above_threshold']:.3f})."
            ),
        )

    max_delta_tick = max(metrics_by_tick, key=lambda t: metrics_by_tick[t]["mean_delta"])
    max_delta_val = metrics_by_tick[max_delta_tick]["mean_delta"]
    close_ratio = max_delta_val / layer.detection.min_delta if layer.detection.min_delta else 0
    if close_ratio >= 0.6:
        status = "incertain"
        reason = (
            f"Delta maximal observe ({max_delta_val:.2f}) proche du seuil "
            f"({layer.detection.min_delta}) sans le depasser avec assez de pixels "
            f"(tick {max_delta_tick}). Revision manuelle recommandee."
        )
    else:
        status = "absent"
        reason = (
            f"Aucun changement significatif detecte dans la region/fenetre attendues. "
            f"Delta maximal observe: {max_delta_val:.2f} (seuil: {layer.detection.min_delta})."
        )

    return LayerVerdict(
        layer_id=layer.id,
        status=status,
        best_tick=max_delta_tick,
        metrics_by_tick=metrics_by_tick,
        reason=reason,
    )


# ---------------------------------------------------------------------------
# 4. Point d'entree haut niveau : recette JSON + frames -> rapport JSON
# ---------------------------------------------------------------------------

def load_recipe(recipe_path: Union[str, Path]) -> List[ExpectedLayer]:
    with open(recipe_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    layers_raw = data.get("expected_layers", [])
    return [ExpectedLayer.from_dict(l) for l in layers_raw]


def load_frames_from_dir(frames_dir: Union[str, Path], pattern: str = "frame_*.png") -> List[Image.Image]:
    """
    Charge des frames PNG depuis un repertoire, tries par ordre alphabetique
    (donc nommage recommande: frame_0000.png, frame_0001.png, ...).
    """
    frames_dir = Path(frames_dir)
    paths = sorted(frames_dir.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"Aucun fichier correspondant a {pattern} dans {frames_dir}")
    return [Image.open(p) for p in paths]


def run_detection(
    frames: List[Image.Image],
    layers: List[ExpectedLayer],
    action_id: str = "unknown_action",
) -> dict:
    """
    Execute la detection pour toutes les couches attendues d'une action et
    produit un rapport JSON-serialisable.
    """
    verdicts = [analyze_layer(frames, layer) for layer in layers]

    summary = {
        "present": sum(1 for v in verdicts if v.status == "present"),
        "absent": sum(1 for v in verdicts if v.status == "absent"),
        "incertain": sum(1 for v in verdicts if v.status == "incertain"),
    }

    report = {
        "action_id": action_id,
        "num_frames_analyzed": len(frames),
        "image_size": frames[0].size if frames else None,
        "summary": summary,
        "layers": [v.to_dict() for v in verdicts],
    }
    return report


def run_detection_from_paths(
    frames_dir: Union[str, Path],
    recipe_path: Union[str, Path],
    action_id: str = "unknown_action",
    frame_pattern: str = "frame_*.png",
) -> dict:
    frames = load_frames_from_dir(frames_dir, frame_pattern)
    layers = load_recipe(recipe_path)
    return run_detection(frames, layers, action_id=action_id)


def save_report(report: dict, output_path: Union[str, Path]) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 5. Utilitaire CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detecteur de rendu automatique pour effets Godot headless."
    )
    parser.add_argument("--frames-dir", required=True, help="Repertoire contenant les frames PNG captures.")
    parser.add_argument("--recipe", required=True, help="Chemin vers le fichier JSON de recette contenant expected_layers.")
    parser.add_argument("--action-id", default="unknown_action", help="Identifiant de l'action analysee.")
    parser.add_argument("--out", default="render_detection_report.json", help="Chemin du rapport JSON de sortie.")
    parser.add_argument("--pattern", default="frame_*.png", help="Motif glob des fichiers de frame.")
    args = parser.parse_args()

    report = run_detection_from_paths(
        frames_dir=args.frames_dir,
        recipe_path=args.recipe,
        action_id=args.action_id,
        frame_pattern=args.pattern,
    )
    save_report(report, args.out)
    print(f"Rapport ecrit dans {args.out}")
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
