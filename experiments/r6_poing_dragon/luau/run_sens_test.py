"""Assemble mocks + DragonFistData + source EXACT de DragonFist.luau + tests,
et l'execute avec l'interpreteur Luau officiel (le CLI ne partage pas les
globales avec les modules requis). Usage : python3 run_sens_test.py [luau]"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
luau = sys.argv[1] if len(sys.argv) > 1 else "luau"
test = open(os.path.join(HERE, "sens_test.luau")).read()
mod = open(os.path.join(HERE, "DragonFist.luau")).read().replace("--!nonstrict", "", 1).rstrip()
assert mod.endswith("return DragonFist")
mod = mod[: -len("return DragonFist")]
data = open(os.path.join(HERE, "DragonFistData.luau")).read().replace("--!nonstrict", "", 1)
combined = test.replace("-- @@DATA@@", "local DATA = (function()\n" + data + "\nend)()") \
               .replace("-- @@MODULE@@", "do end\n" + mod)
with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False) as f:
    f.write(combined)
r = subprocess.run([luau, f.name], capture_output=True, text=True)
print(r.stdout + r.stderr)
sys.exit(0 if "SENS OK" in r.stdout else 1)
