"""
Construit le LAB VFX : une page HTML autonome qui joue les recettes avec le
moteur d'aperçu. Textures et meshes sont intégrés à la page.

Usage : python3 build_lab.py [sortie.html]   (défaut : lab/studio_vfx.html)
"""
import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import formes  # noqa: E402
import meshes  # noqa: E402
import recettes  # noqa: E402

THREE = os.path.join(HERE, "..", "..", "r6_black_hole", "scripts", "vendor", "three.min.js")


def main(sortie=None):
    sortie = sortie or os.path.join(HERE, "lab", "studio_vfx.html")
    tex_dir, mesh_dir = os.path.join(HERE, "textures"), os.path.join(HERE, "meshes")
    formes.main(tex_dir)
    meshes.main(mesh_dir)
    cat = json.load(open(os.path.join(tex_dir, "catalogue.json")))["textures"]
    # les variantes décalées (défilement Roblox) ne sont pas intégrées : l'aperçu
    # décale la texture de base du même pas quantifié (moteur.js)
    textures = {t["nom"]: "data:image/png;base64," + base64.b64encode(open(os.path.join(tex_dir, t["fichier"]), "rb").read()).decode()
                for t in cat if not t.get("variante_de")}
    variantes = {}
    for t in cat:
        if t.get("variante_de"):
            variantes[t["variante_de"]] = variantes.get(t["variante_de"], 0) + 1
    data = {"textures": textures, "variantes": variantes, "meshes": json.load(open(os.path.join(mesh_dir, "meshes.json"))),
            "recettes": recettes.toutes()}
    html = open(os.path.join(HERE, "lab", "lab_template.html"), encoding="utf-8").read()
    html = html.replace("__THREE__", open(THREE, encoding="utf-8").read())
    html = html.replace("__MOTEUR__", open(os.path.join(HERE, "lab", "moteur.js"), encoding="utf-8").read())
    html = html.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    open(sortie, "w", encoding="utf-8").write(html)
    print(sortie, round(len(html) / 1024), "Ko")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
