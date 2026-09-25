"""
Lance le test du moteur Roblox VFXStudio.luau avec l'interpréteur Luau
officiel : assemble mocks + recettes compilées + valeurs de référence de
l'aperçu (node references_apercu.js) + module + tests.

Usage : python3 run_test.py [chemin/vers/luau]   (défaut : $LUAU, puis `luau`)
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


def main(luau=None):
    luau = luau or os.environ.get("LUAU", "luau")
    compile_roblox.main()
    refs = json.loads(subprocess.check_output(["node", os.path.join(HERE, "references_apercu.js")]))
    test = open(os.path.join(HERE, "test_vfxstudio.luau"), encoding="utf-8").read()
    test = (test.replace("-- @@DATA@@", module(os.path.join(HERE, "VFXRecettes.luau"), "DATA"))
                .replace("-- @@REFS@@", "REFS = " + compile_roblox.lua(refs) + "\n")
                .replace("-- @@MODULE@@", module(os.path.join(HERE, "VFXStudio.luau"), "VFXStudio")))
    tmp = os.path.join(os.environ.get("TMPDIR", "/tmp"), "vfxstudio_test_assemble.luau")
    open(tmp, "w", encoding="utf-8").write(test)
    r = subprocess.run([luau, tmp], capture_output=True, text=True)
    print(r.stdout + r.stderr)
    return 0 if "TOUT OK" in r.stdout else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
