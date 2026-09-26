"""Assemble mocks + source EXACT de M1Technique.luau + tests, et l'execute
avec l'interpreteur Luau officiel (le CLI ne partage pas les globales avec
les modules requis). Usage : python3 run_sens_test.py [chemin/vers/luau]"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
luau = sys.argv[1] if len(sys.argv) > 1 else "luau"
test = open(os.path.join(HERE, "sens_test.luau")).read()
mod = open(os.path.join(HERE, "M1Technique.luau")).read()
body = mod.replace("--!nonstrict", "", 1).rstrip()
assert body.endswith("return M1")
body = body[: -len("return M1")]
combined = test.replace("-- @@MODULE@@  (run_sens_test.py insere ici le source EXACT de M1Technique.luau)",
                        "do end\n" + body)
with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False) as f:
    f.write(combined)
r = subprocess.run([luau, f.name], capture_output=True, text=True)
print(r.stdout + r.stderr)
sys.exit(0 if "SENS OK" in r.stdout else 1)
