"""
Captures de verification (Playwright, Chromium headless) du lecteur
solar_smite_viewer_final.html aux instants cles demandes -- meme
technique que les autres prototypes de ce depot (page --setSimTime/
__render exposes par le lecteur, aucune interaction, deterministe).

Convertit chaque instant chorégraphié (pose-time, constantes de
choreography.py/solar_track.py) en instant REEL via window.__poseToReal()
avant d'appeler __setSimTime() -- necessaire des qu'un hitstop precedent a
deja decale la grille temps reel (voir docstring de __poseToReal() dans le
lecteur), jamais une addition devinee a la main cote Python.

Ecrit dans /home/user/Jeux/captures_local/ (PAS captures/verification/ --
convention de commit qui appartient a l'utilisateur, voir CLAUDE.md).
"""
import json
import os

from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.join(SCRIPT_DIR, "..", "output", "solar_smite_viewer_final.html")
OUT_DIR = "/home/user/Jeux/captures_local"
DATE = "2026-09-05"

with open("/tmp/solar_smite_scene_data.json") as f:
    DATA = json.load(f)
KT = DATA["key_times"]
SOL = DATA["solar"]

# (nom_fichier, instant en TEMPS DE POSE)
SHOTS = [
    ("00-garde", 0.3),
    ("01-ouverture", KT["open_t"]),
    ("02-charge-particules", KT["charge_hold_t"] - 0.05),
    ("03-combo1-impact", KT["strike1_t"]),
    ("04-combo2-impact", KT["strike2_t"]),
    ("05-finisher-montee", KT["fin_coil_hold_t"]),
    ("06-finisher-impact-flash", KT["fin_strike_t"]),
    ("07-finisher-impact-apres", KT["fin_strike_t"]),  # +0.15s REEL ajoute plus bas
    ("08-mannequin-ecrase", KT["fin_strike_t"] + 0.5),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    url = "file://" + os.path.abspath(VIEWER)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        page.goto(url)
        page.wait_for_function("() => typeof window.__setSimTime === 'function'")
        page.evaluate("() => window.__setPlaying(false)")

        for name, pose_t in SHOTS:
            real_t = page.evaluate("(pt) => window.__poseToReal(pt)", pose_t)
            # -- capture "0.15s apres le flash" : le decalage est en temps
            # REEL (le flash/l'explosion jouent en temps reel meme pendant
            # le gel de la pose), jamais ajoute au temps de pose.
            if name == "07-finisher-impact-apres":
                real_t += 0.15
            page.evaluate("(t) => { window.__setSimTime(t); window.__render(); }", real_t)
            path = os.path.join(OUT_DIR, f"{DATE}-solar-smite-{name}.png")
            page.screenshot(path=path)
            print(f"  {name:28s} pose_t={pose_t:6.3f}  real_t={real_t:6.3f}  -> {path}")

        browser.close()


if __name__ == "__main__":
    main()
