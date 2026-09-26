"""
Lance le test du moteur Roblox VFXStudio.luau avec l'interpréteur Luau
officiel : assemble mocks + recettes compilées + valeurs de référence de
l'aperçu (node references_apercu.js) + module + tests.

Usage : python3 run_test.py [chemin/vers/luau] [--recettes autres.json]
        (défaut : $LUAU, puis `luau`)
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import compile_roblox  # noqa: E402


def module(chemin, nom):
    src = open(chemin, encoding="utf-8").read().replace("--!nonstrict", "")
    return f"{nom} = (function()\n{src}\nend)()\n"


def main(luau=None, extra=None):
    """extra : JSON {nom: recette} (ex. les recettes du Poing du Dragon) à
    faire passer AUSSI dans le banc de test, compilées comme en jeu."""
    luau = luau or os.environ.get("LUAU", "luau")
    compile_roblox.main()
    if extra:
        base = open(os.path.join(HERE, "VFXRecettes.luau"), encoding="utf-8").read()
        recs = {k: compile_roblox.compiler(v) for k, v in json.load(open(extra)).items()}
        data = {"recettes": {**{k: compile_roblox.compiler(v) for k, v in compile_roblox.recettes.toutes().items()}, **recs},
                "assets": compile_roblox.assets()}
        open(os.path.join(HERE, "VFXRecettes.luau"), "w", encoding="utf-8").write(
            "--!nonstrict\nreturn " + compile_roblox.lua(data) + "\n")
    refs = json.loads(subprocess.check_output(["node", os.path.join(HERE, "references_apercu.js")]))
    test = open(os.path.join(HERE, "test_vfxstudio.luau"), encoding="utf-8").read()
    test = (test.replace("-- @@DATA@@", module(os.path.join(HERE, "VFXRecettes.luau"), "DATA"))
                .replace("-- @@REFS@@", "REFS = " + compile_roblox.lua(refs) + "\n")
                .replace("-- @@MODULE@@", module(os.path.join(HERE, "VFXStudio.luau"), "VFXStudio")))
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "vfxstudio_test_assemble.luau")
    open(tmp, "w", encoding="utf-8").write(test)
    r = subprocess.run([luau, tmp], capture_output=True, text=True)
    if extra:  # remettre le module généré tel que le studio le livre
        open(os.path.join(HERE, "VFXRecettes.luau"), "w", encoding="utf-8").write(base)
    print(r.stdout + r.stderr)
    return 0 if "TOUT OK" in r.stdout else 1


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    ex = sys.argv[sys.argv.index("--recettes") + 1] if "--recettes" in sys.argv else None
    if ex in a:
        a.remove(ex)
    sys.exit(main(a[0] if a else None, ex))
