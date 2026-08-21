#!/usr/bin/env python3
"""experiments/blender_capture/quantize.py

Post-traitement pixel-art (Python pur : Pillow + numpy, AUCUNE
dépendance Godot/GPU) — deuxième étage du pipeline de repli Blender
(voir capture_pose.py). Porte la même logique visuelle que
experiments/bakeoff_voie_c/pixel_quantize.gdshader (pixelisation par
blocs, désaturation+quantification du Value HSV remappée dans une
bande, contour par détection de bords, dithering Bayer sur les
transitions ombre/lumière) mais calculée hors-GPU sur l'image déjà
rendue par Blender.

Différence assumée avec le shader original : le shader échantillonne
les bords/contours sur la texture haute résolution AVANT
pixelisation (texels voisins du bloc), ce script les calcule sur
l'image DÉJÀ pixelisée (pixels de sortie voisins) — plus simple, un
résultat visuellement proche mais pas un rendu identique au pixel
près. Seuils (edge_strength, dither_amount) à recalibrer à l'œil si
besoin, pas une garantie de parité exacte.

Usage :
    python3 quantize.py --in raw.png --out final.png \
        [--target_pixels=64] [--color_steps=8] \
        [--target_saturation=0.10] \
        [--value_band_min=0.165] [--value_band_max=0.90] \
        [--edge_strength=0.12] [--outline_thickness=3.0] \
        [--dither_amount=0.35]
"""

import argparse
import colorsys

import numpy as np
from PIL import Image


BAYER_4X4 = np.array([
    [0, 8, 2, 10],
    [12, 4, 14, 6],
    [3, 11, 1, 9],
    [15, 7, 13, 5],
], dtype=np.float32) / 15.0


def rgb_to_hsv_np(rgb: np.ndarray) -> np.ndarray:
    # rgb: (H, W, 3) in [0,1] -> hsv (H, W, 3) in [0,1]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    v = maxc
    delta = maxc - minc
    s = np.where(maxc > 1e-8, delta / np.maximum(maxc, 1e-8), 0.0)
    h = np.zeros_like(maxc)
    mask = delta > 1e-8
    rc = np.zeros_like(maxc)
    gc = np.zeros_like(maxc)
    bc = np.zeros_like(maxc)
    with np.errstate(divide="ignore", invalid="ignore"):
        rc = np.where(mask, (maxc - r) / np.maximum(delta, 1e-8), 0.0)
        gc = np.where(mask, (maxc - g) / np.maximum(delta, 1e-8), 0.0)
        bc = np.where(mask, (maxc - b) / np.maximum(delta, 1e-8), 0.0)
    h = np.where((maxc == r) & mask, (bc - gc), h)
    h = np.where((maxc == g) & mask, 2.0 + rc - bc, h)
    h = np.where((maxc == b) & mask, 4.0 + gc - rc, h)
    h = (h / 6.0) % 1.0
    return np.stack([h, s, v], axis=-1)


def hsv_to_rgb_np(hsv: np.ndarray) -> np.ndarray:
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i = i.astype(np.int32) % 6

    r = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [v, q, p, p, t, v],
    )
    g = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [t, v, v, q, p, p],
    )
    b = np.select(
        [i == 0, i == 1, i == 2, i == 3, i == 4, i == 5],
        [p, p, t, v, v, q],
    )
    return np.stack([r, g, b], axis=-1)


def pixelate_block_center(img: np.ndarray, target_pixels: int) -> np.ndarray:
    """Échantillonne le CENTRE de chaque bloc (comme le shader d'origine
    pixel_uv, pas une moyenne de bloc) pour rester fidèle au look
    "point-sample" de pixel_quantize.gdshader."""
    src_h, src_w = img.shape[0], img.shape[1]
    ys = (np.arange(target_pixels) + 0.5) / target_pixels * src_h
    xs = (np.arange(target_pixels) + 0.5) / target_pixels * src_w
    ys = np.clip(ys.astype(np.int32), 0, src_h - 1)
    xs = np.clip(xs.astype(np.int32), 0, src_w - 1)
    return img[np.ix_(ys, xs)]


def sobel_edges(rgb: np.ndarray) -> np.ndarray:
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    padded = np.pad(lum, 1, mode="edge")
    gx = (
        -padded[:-2, :-2] + padded[:-2, 2:]
        - 2 * padded[1:-1, :-2] + 2 * padded[1:-1, 2:]
        - padded[2:, :-2] + padded[2:, 2:]
    )
    gy = (
        -padded[:-2, :-2] - 2 * padded[:-2, 1:-1] - padded[:-2, 2:]
        + padded[2:, :-2] + 2 * padded[2:, 1:-1] + padded[2:, 2:]
    )
    return np.sqrt(gx * gx + gy * gy)


def apply_dithering(color: np.ndarray, lum: np.ndarray, dither_amount: float,
                     dither_threshold: float, dither_color: np.ndarray,
                     shadow_sensitivity: float) -> np.ndarray:
    if dither_amount <= 0.0:
        return color
    padded = np.pad(lum, 1, mode="edge")
    grad_x = np.abs(padded[1:-1, 2:] - padded[1:-1, :-2]) * 0.5
    grad_y = np.abs(padded[2:, 1:-1] - padded[:-2, 1:-1]) * 0.5
    gradient = np.sqrt(grad_x * grad_x + grad_y * grad_y) * shadow_sensitivity
    transition = np.clip((gradient - 0.05) / (0.2 - 0.05), 0.0, 1.0)
    transition = transition * transition * (3 - 2 * transition)  # smoothstep

    h, w = lum.shape
    bayer_tile = np.tile(BAYER_4X4, (h // 4 + 1, w // 4 + 1))[:h, :w]
    threshold = dither_threshold + (bayer_tile - 0.5) * dither_amount
    is_dot = (lum >= threshold).astype(np.float32)[..., None]

    dot_color = dither_color[None, None, :] * (1 - lum[..., None]) + color * 1.2 * lum[..., None]
    dithered = dot_color * (1 - is_dot) + color * is_dot
    return color * (1 - transition[..., None]) + dithered * transition[..., None]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="in_path", required=True)
    p.add_argument("--out", dest="out_path", required=True)
    p.add_argument("--target_pixels", type=int, default=64)
    p.add_argument("--color_steps", type=int, default=8)
    p.add_argument("--target_saturation", type=float, default=0.10)
    p.add_argument("--value_band_min", type=float, default=0.165)
    p.add_argument("--value_band_max", type=float, default=0.90)
    p.add_argument("--edge_strength", type=float, default=0.12)
    p.add_argument("--outline_thickness", type=float, default=3.0)
    p.add_argument("--outline_color", default="0.17,0.17,0.185")
    p.add_argument("--dither_amount", type=float, default=0.35)
    p.add_argument("--dither_threshold", type=float, default=0.5)
    p.add_argument("--dither_color", default="0.17,0.17,0.185")
    p.add_argument("--shadow_sensitivity", type=float, default=1.0)
    args = p.parse_args()

    src = Image.open(args.in_path).convert("RGBA")
    arr = np.asarray(src).astype(np.float32) / 255.0
    rgb_full = arr[..., :3]
    alpha_full = arr[..., 3]

    block = pixelate_block_center(rgb_full, args.target_pixels)
    alpha_block = pixelate_block_center(alpha_full[..., None], args.target_pixels)[..., 0]

    hsv = rgb_to_hsv_np(block)
    hsv[..., 1] = args.target_saturation
    if args.color_steps < 32:
        step_size = 1.0 / float(args.color_steps - 1)
        step_index = np.floor(hsv[..., 2] / step_size)
        v_norm = step_index * step_size
        hsv[..., 2] = args.value_band_min + v_norm * (args.value_band_max - args.value_band_min)
    color = hsv_to_rgb_np(hsv)

    outline_rgb = np.array([float(x) for x in args.outline_color.split(",")], dtype=np.float32)
    if args.outline_thickness > 0.0:
        edges = sobel_edges(block)
        outline_intensity = np.clip(args.outline_thickness / 10.0, 0.0, 1.0)
        mask = (edges > args.edge_strength).astype(np.float32)[..., None]
        color = color * (1 - mask * outline_intensity) + outline_rgb[None, None, :] * (mask * outline_intensity)

    dither_rgb = np.array([float(x) for x in args.dither_color.split(",")], dtype=np.float32)
    lum = 0.299 * block[..., 0] + 0.587 * block[..., 1] + 0.114 * block[..., 2]
    color = apply_dithering(color, lum, args.dither_amount, args.dither_threshold,
                             dither_rgb, args.shadow_sensitivity)

    color = np.clip(color, 0.0, 1.0)
    out_arr = np.concatenate([color, alpha_block[..., None]], axis=-1)
    out_img = Image.fromarray((out_arr * 255.0 + 0.5).astype(np.uint8), mode="RGBA")
    out_img.save(args.out_path)
    print(f"QUANTIZE_RESULT out={args.out_path} size={out_img.size}")


if __name__ == "__main__":
    main()
