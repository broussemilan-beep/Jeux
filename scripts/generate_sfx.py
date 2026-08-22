#!/usr/bin/env python3
"""Phase 2.1 (MANDAT SUITE v2) : génère les familles de SFX de combat
via pyfxr (T.1.4, retenu — cf. docs/worklog.md) en .wav mono 16-bit,
lus tels quels par Godot (AudioStreamWAV). Pas de variantes de pitch
baked ici : le mandat demande "pitch variants +-5%", appliqué au
runtime via AudioStreamPlayer.pitch_scale (src/gameplay/sfx.gd) plutôt
que de multiplier les fichiers sur disque pour un effet aussi simple.

Mandat "critique probabiliste" (verrouillé par Milan) : ajout de
critical_hit, "un signal sonore distinct" — voir sa docstring pour le
choix de conception (hauteur montante, pas descendante/plate comme
heavy_impact/light_impact).

Seeds fixes (random.seed) : reproductibilité de CETTE génération d'assets
(pouvoir regénérer un son identique si besoin), pas une contrainte de
déterminisme gameplay (RNDC) — ceci tourne une fois hors moteur, jamais
en combat réel.

Usage : python3 scripts/generate_sfx.py
"""
from __future__ import annotations

import os
import random

import pyfxr

OUT_DIR = "assets/processed/sfx"


def light_impact() -> pyfxr.SFX:
    random.seed(1)
    return pyfxr.hurt()


def heavy_impact() -> pyfxr.SFX:
    random.seed(2)
    return pyfxr.explosion()


def whoosh() -> pyfxr.SFX:
    # Recette jsfxr classique "whoosh" : bruit blanc, balayage de
    # fréquence descendant, filtre passe-bas qui suit la pente pour
    # donner l'impression d'air déplacé plutôt qu'un impact.
    return pyfxr.sfx(
        wave_type=pyfxr.WaveType.NOISE.value,
        p_base_freq=0.45,
        p_freq_ramp=-0.35,
        p_env_attack=0.0,
        p_env_sustain=0.12,
        p_env_decay=0.18,
        p_lpf_freq=0.55,
        p_lpf_ramp=-0.3,
    )


def spawn() -> pyfxr.SFX:
    random.seed(3)
    return pyfxr.powerup()


def death() -> pyfxr.SFX:
    # Descente de hauteur longue (trope "mort") plutôt que l'explosion
    # de heavy_impact déjà utilisée ailleurs — distinct, pas dupliqué.
    return pyfxr.sfx(
        wave_type=pyfxr.WaveType.SAW.value,
        p_base_freq=0.5,
        p_freq_ramp=-0.55,
        p_env_attack=0.0,
        p_env_sustain=0.15,
        p_env_decay=0.45,
        p_lpf_freq=0.7,
    )


def footstep() -> pyfxr.SFX:
    # Court, sourd, discret — bruit filtré très bref, pas un impact de
    # combat (jamais confondu avec light_impact au mixage).
    return pyfxr.sfx(
        wave_type=pyfxr.WaveType.NOISE.value,
        p_base_freq=0.25,
        p_env_attack=0.0,
        p_env_sustain=0.04,
        p_env_decay=0.08,
        p_lpf_freq=0.25,
    )


def critical_hit() -> pyfxr.SFX:
    # Signal distinct de TOUTE la famille existante (mandat critique
    # probabiliste, "un signal sonore distinct") : light_impact/
    # heavy_impact/death descendent ou restent plats (presets hurt/
    # explosion, rampe négative) — celui-ci MONTE en hauteur
    # (p_freq_ramp positif) avec un punch d'attaque marqué
    # (p_env_punch), lu comme une confirmation éclatante plutôt qu'un
    # impact de plus. Passe-haut léger (p_hpf_freq) pour rester brillant/
    # tranchant, jamais confondu au mixage avec le "boom" sourd de
    # heavy_impact.
    return pyfxr.sfx(
        wave_type=pyfxr.WaveType.SAW.value,
        p_base_freq=0.32,
        p_freq_ramp=0.45,
        p_env_attack=0.0,
        p_env_sustain=0.06,
        p_env_decay=0.28,
        p_env_punch=0.35,
        p_hpf_freq=0.15,
        p_lpf_freq=0.95,
    )


FAMILIES = {
    "light_impact": light_impact,
    "heavy_impact": heavy_impact,
    "whoosh": whoosh,
    "spawn": spawn,
    "death": death,
    "footstep": footstep,
    "critical_hit": critical_hit,
}


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, factory in FAMILIES.items():
        sfx = factory()
        # `pyfxr.sfx()` (paramétrique, utilisé pour whoosh/death/footstep)
        # renvoie directement un SoundBuffer ; les présets (hurt/explosion/
        # powerup) renvoient un SFX à construire via .build() — les deux
        # cohabitent dans FAMILIES, d'où ce duck-typing.
        buf = sfx.build() if hasattr(sfx, "build") else sfx
        out_path = os.path.join(OUT_DIR, f"{name}.wav")
        buf.save(out_path)
        print("SFX_GENERATED", name, out_path, "duration_s=", round(buf.duration, 3))


if __name__ == "__main__":
    main()
