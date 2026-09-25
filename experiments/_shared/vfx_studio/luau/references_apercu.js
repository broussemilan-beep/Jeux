// Valeurs de RÉFÉRENCE calculées par l'aperçu (lab/moteur.js, le vrai code)
// pour le test du moteur Roblox : secousse caméra + interpolation des séquences.
// Usage : node references_apercu.js > references_apercu.json
const fs = require("fs");
const path = require("path");
const HERE = __dirname;
global.window = global;
// three.js en UMD : sans exports/module visibles, il se range dans window.THREE
new Function("exports", "module", "define", fs.readFileSync(path.join(HERE, "..", "..", "..", "r6_black_hole", "scripts", "vendor", "three.min.js"), "utf8"))();
eval(fs.readFileSync(path.join(HERE, "..", "lab", "moteur.js"), "utf8"));
const { execFileSync } = require("child_process");
const recs = JSON.parse(execFileSync("python3", [path.join(HERE, "..", "recettes.py")]).toString());
const out = { secousse: {}, bloom: {}, flash: {} };
for (const [nom, rec] of Object.entries(recs)) {
  const e = VFX.Effet(Object.assign({}, rec, { couches: [], projectile: null }), { add() {} });
  out.secousse[nom] = []; out.bloom[nom] = []; out.flash[nom] = [];
  for (let i = 0; i <= Math.round(rec.duree * 60); i += 3) {
    const t = i / 60, p = e.post(t);
    out.secousse[nom].push([t, p.secousse.x, p.secousse.y, p.secousse.z]);
    out.bloom[nom].push([t, p.intensite]);
    out.flash[nom].push([t, 1 - p.flash[3]]);
  }
}
process.stdout.write(JSON.stringify(out));
