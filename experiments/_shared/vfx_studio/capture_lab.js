// CAPTURE du labo VFX (lab/studio_vfx.html) à des instants donnés, pour les
// preuves (captures/verification/) et l'auto-évaluation.
// Chromium en rendu logiciel (swiftshader) : pas de GPU dans ce bac à sable.
//
// Usage : NODE_PATH=$(npm root -g) node capture_lab.js <recette> <camera> <t1,t2,...> <sortie.png> [bloom=1]
//         NODE_PATH=$(npm root -g) node capture_lab.js <recette> <camera> video:<fps>:<durée> <dossier> [bloom=1]
//         (images d'une vidéo ; video_recette.py y ajoute le son mixé)
// Sortie : une planche horizontale, une vignette par instant (étiquetée).
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const [recette, cam, ts, sortie, bl] = process.argv.slice(2);
  const temps = ts.startsWith("video:") ? [] : ts.split(",").map(Number);
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 960, height: 640 } });
  p.on("pageerror", (e) => console.log("ERREUR PAGE", String(e)));
  await p.goto("file://" + path.join(__dirname, "lab", "studio_vfx.html"));
  await p.waitForTimeout(1200);
  await p.evaluate(([r, c, bl]) => { window.__vfx.setRecette(r); window.__vfx.setCam(c); window.__vfx.setBloom(bl !== "0"); }, [recette, cam, bl || "1"]);
  // mode vidéo : « video:<fps>:<durée> » écrit une image PNG par pas dans le dossier <sortie>
  if (ts.startsWith("video:")) {
    const [, fps, duree] = ts.split(":").map(Number);
    const fs = require("fs");
    fs.mkdirSync(sortie, { recursive: true });
    for (let i = 0; i <= Math.round(duree * fps); i++) {
      await p.evaluate((t) => window.__vfx.seek(t), i / fps);
      await p.locator("#stage").screenshot({ path: path.join(sortie, "f" + String(i).padStart(4, "0") + ".png") });
    }
    console.log(sortie);
    await b.close();
    return;
  }
  const shots = [];
  for (const t of temps) {
    await p.evaluate((t) => window.__vfx.seek(t), t);
    shots.push((await p.locator("#stage").screenshot()).toString("base64"));
  }
  // planche : assemblée dans la page (canvas 2D), pas de dépendance image côté node
  const png = await p.evaluate(async ([shots, temps]) => {
    const ims = await Promise.all(shots.map((s) => new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = "data:image/png;base64," + s; })));
    const w = 480, h = Math.round((ims[0].height / ims[0].width) * w);
    const c = document.createElement("canvas"); c.width = w * ims.length; c.height = h + 26;
    const g = c.getContext("2d"); g.fillStyle = "#111"; g.fillRect(0, 0, c.width, c.height);
    ims.forEach((im, k) => { g.drawImage(im, k * w, 26, w, h); g.fillStyle = "#fff"; g.font = "16px monospace"; g.fillText("t = " + temps[k].toFixed(3) + " s", k * w + 8, 19); });
    return c.toDataURL("image/png").split(",")[1];
  }, [shots, temps]);
  require("fs").writeFileSync(sortie, Buffer.from(png, "base64"));
  console.log(sortie);
  await b.close();
})();
