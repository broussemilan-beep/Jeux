"""
test_render_detector.py — recréé depuis le contenu fourni par Milan.
"""

import json
import numpy as np
from PIL import Image

from render_detector import (
    ExpectedLayer,
    run_detection,
)


def make_sequence_with_effect(num_frames, width, height, effect_box, effect_start, effect_end, effect_color):
    frames = []
    base = np.full((height, width, 3), (30, 30, 30), dtype=np.uint8)
    x0, y0, x1, y1 = effect_box
    for t in range(num_frames):
        arr = base.copy()
        if effect_start <= t <= effect_end:
            arr[y0:y1, x0:x1] = effect_color
        frames.append(Image.fromarray(arr, mode="RGB"))
    return frames


def make_sequence_without_effect(num_frames, width, height):
    base = np.full((height, width, 3), (30, 30, 30), dtype=np.uint8)
    return [Image.fromarray(base.copy(), mode="RGB") for _ in range(num_frames)]


def test_case_present():
    width, height = 200, 150
    layer = ExpectedLayer.from_dict({
        "id": "ground_crack",
        "description": "Fissure au sol (test synthetique, cas present)",
        "region_pct": {"x0": 0.35, "y0": 0.55, "x1": 0.65, "y1": 0.85},
        "tick_window": {"start": 2, "end": 10},
        "detection": {
            "metric": "luminance_delta",
            "min_delta": 12.0,
            "min_pixel_fraction": 0.5,
        },
    })
    box = layer.region.to_pixel_box(width, height)
    frames = make_sequence_with_effect(
        num_frames=15, width=width, height=height,
        effect_box=box, effect_start=4, effect_end=8,
        effect_color=(200, 180, 120),
    )
    report = run_detection(frames, [layer], action_id="test_slash_crack")
    verdict = report["layers"][0]
    assert verdict["status"] == "present", f"Attendu 'present', obtenu: {verdict}"
    print("[OK] test_case_present -> status =", verdict["status"], "| best_tick =", verdict["best_tick"])
    return report


def test_case_absent():
    width, height = 200, 150
    layer = ExpectedLayer.from_dict({
        "id": "dust_puff",
        "description": "Nuage de poussiere (test synthetique, cas absent = bug reel)",
        "region_pct": {"x0": 0.40, "y0": 0.60, "x1": 0.60, "y1": 0.80},
        "tick_window": {"start": 0, "end": 6},
        "detection": {
            "metric": "stddev_delta",
            "min_delta": 5.0,
            "min_pixel_fraction": 0.01,
        },
    })
    frames = make_sequence_without_effect(num_frames=10, width=width, height=height)
    report = run_detection(frames, [layer], action_id="test_dash_dust")
    verdict = report["layers"][0]
    assert verdict["status"] == "absent", f"Attendu 'absent', obtenu: {verdict}"
    print("[OK] test_case_absent -> status =", verdict["status"])
    return report


def test_case_white_flash_channel_delta():
    width, height = 200, 150
    layer = ExpectedLayer.from_dict({
        "id": "impact_white_flash",
        "description": "Flash blanc d'impact (test synthetique, channel_delta)",
        "region_pct": {"x0": 0.30, "y0": 0.30, "x1": 0.70, "y1": 0.70},
        "tick_window": {"start": 0, "end": 3},
        "detection": {
            "metric": "channel_delta",
            "channel": "r",
            "min_delta": 100.0,
            "min_pixel_fraction": 0.8,
        },
    })
    box = layer.region.to_pixel_box(width, height)
    frames = make_sequence_with_effect(
        num_frames=8, width=width, height=height,
        effect_box=box, effect_start=0, effect_end=1,
        effect_color=(255, 255, 255),
    )
    report = run_detection(frames, [layer], action_id="test_impact_flash")
    verdict = report["layers"][0]
    assert verdict["status"] == "present", f"Attendu 'present', obtenu: {verdict}"
    print("[OK] test_case_white_flash_channel_delta -> status =", verdict["status"], "| best_tick =", verdict["best_tick"])
    return report


def test_case_incertain_borderline():
    width, height = 200, 150
    layer = ExpectedLayer.from_dict({
        "id": "faint_smoke",
        "description": "Effet tres subtil, sous le seuil mais proche (test incertain)",
        "region_pct": {"x0": 0.35, "y0": 0.55, "x1": 0.65, "y1": 0.85},
        "tick_window": {"start": 2, "end": 10},
        "detection": {
            "metric": "luminance_delta",
            "min_delta": 30.0,
            "min_pixel_fraction": 0.5,
        },
    })
    box = layer.region.to_pixel_box(width, height)
    frames = make_sequence_with_effect(
        num_frames=15, width=width, height=height,
        effect_box=box, effect_start=4, effect_end=8,
        effect_color=(50, 50, 50),
    )
    report = run_detection(frames, [layer], action_id="test_borderline")
    verdict = report["layers"][0]
    print("[INFO] test_case_incertain_borderline -> status =", verdict["status"])
    return report


if __name__ == "__main__":
    r1 = test_case_present()
    r2 = test_case_absent()
    r3 = test_case_white_flash_channel_delta()
    r4 = test_case_incertain_borderline()
    print("\nTous les tests ont passe.")
