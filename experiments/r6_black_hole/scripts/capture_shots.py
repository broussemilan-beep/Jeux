"""
Captures de verification (Playwright, Chromium headless) du lecteur
black_hole_viewer_final.html aux instants cles demandes -- meme technique
que les autres prototypes de ce depot (page __setSimTime/__render exposes
par le lecteur, aucune interaction, deterministe).

Convertit chaque instant chorégraphié (pose-time, constantes de
choreography.py/black_hole_track.py) en instant REEL via
window.__poseToReal() avant d'appeler __setSimTime() -- ce prototype n'a
pas de hitstop (poseToReal est l'identite ici), mais on suit quand meme le
meme chemin que r6_solar_smite pour rester coherent avec l'API attendue,
jamais une addition devinee a la main cote Python.

Ecrit dans /home/user/Jeux/captures_local/ (PAS captures/verification/ --
convention de commit qui appartient a l'utilisateur, voir CLAUDE.md).
"""
import json
import os

from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.join(SCRIPT_DIR, "..", "output", "black_hole_viewer_final.html")
OUT_DIR = "/home/user/Jeux/captures_local"
DATE = "2026-09-23"
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

with open("/tmp/black_hole_scene_data.json") as f:
    DATA = json.load(f)
KT = DATA["key_times"]
VFX = DATA["black_hole"]["vfx_events"]

# (nom_fichier, instant en TEMPS DE POSE)
SHOTS = [
    ("00-garde", 0.3),
    ("01-crouch", KT["crouch_hold_t"]),
    ("02-liftoff", KT["rise_t"] + 0.05),
    ("03-hold-debris", KT["rise_t"] + (KT["hold_end_t"] - KT["rise_t"]) * 0.5),
    ("04-disk-forming", VFX["disk_form"]["t0"] + 0.3),
    ("05-climax", KT["climax_t"]),
    ("06-collapse", VFX["collapse"]["t0"] + 0.2),
    ("07-landing", KT["land_t"] + 0.1),
    ("08-recover", KT["recover_t"] + 0.3),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    url = "file://" + os.path.abspath(VIEWER)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(url)
        page.wait_for_function("() => typeof window.__setSimTime === 'function'")
        page.evaluate("() => window.__setPlaying(false)")

        for name, pose_t in SHOTS:
            real_t = page.evaluate("(pt) => window.__poseToReal(pt)", pose_t)
            page.evaluate("(t) => { window.__setSimTime(t); window.__render(); }", real_t)
            path = os.path.join(OUT_DIR, f"{DATE}-black-hole-{name}.png")
            page.screenshot(path=path)
            print(f"  {name:16s} pose_t={pose_t:6.3f}  real_t={real_t:6.3f}  -> {path}")

        browser.close()


if __name__ == "__main__":
    main()
