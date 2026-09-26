"""Assemble mocks (Poing du Dragon) + UnSeulCoupData + source EXACT de
UnSeulCoup.luau + tests, et l'exécute avec l'interpréteur Luau officiel.
Usage : python3 run_sens_test.py <luau>"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
luau = sys.argv[1] if len(sys.argv) > 1 else "luau"
dragon = open(os.path.join(HERE, "..", "..", "r6_poing_dragon", "luau", "sens_test.luau")).read()
mocks = dragon[dragon.index("local V = {}"): dragon.index("-- @@DATA@@")]
mocks = mocks.replace("local Color3 = {", "local Color3 = { new = function(r, g, b) return { r, g, b } end,")
test = open(os.path.join(HERE, "sens_test.luau")).read()
mod = open(os.path.join(HERE, "UnSeulCoup.luau")).read().replace("--!nonstrict", "", 1).rstrip()
assert mod.endswith("return UnSeulCoup")
mod = mod[: -len("return UnSeulCoup")]
data = open(os.path.join(HERE, "UnSeulCoupData.luau")).read().replace("--!nonstrict", "", 1)
combined = test.replace("-- @@MOCKS@@", mocks).replace("-- @@DATA@@", "local DATA = (function()\n" + data + "\nend)()") \
               .replace("-- @@MODULE@@", "do end\n" + mod)
with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False) as f:
    f.write(combined)
r = subprocess.run([luau, f.name], capture_output=True, text=True)
print(r.stdout + r.stderr)
sys.exit(0 if "SENS OK" in r.stdout else 1)
