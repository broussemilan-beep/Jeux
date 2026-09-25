// FILME le lecteur du Poing du Dragon (output/dragon_player.html) : une image
// PNG par pas de temps RÉEL (hitstops compris). three.js est servi depuis la
// copie locale (le CDN est bloqué dans ce bac à sable ; r134 au lieu de r128).
// Usage : NODE_PATH=$(npm root -g) node filmer_lecteur.js <t0> <t1> <dossier> [camera=cinema] [fps=30]
const path = require("path"), fs = require("fs");
const { chromium } = require("playwright");
(async () => {
  const [t0, t1, out, cam, fpsArg] = process.argv.slice(2);
  const fps = parseFloat(fpsArg || "30");
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 900, height: 720 } });
  await p.route("**/three.min.js", (r) => r.fulfill({ path: path.join(__dirname, "..", "..", "r6_black_hole", "scripts", "vendor", "three.min.js"), contentType: "application/javascript" }));
  await p.route("**/fonts.googleapis.com/**", (r) => r.abort());
  await p.goto("file://" + path.join(__dirname, "..", "output", "dragon_player.html"));
  await p.waitForTimeout(2500);
  await p.evaluate(() => { document.getElementById("hud").style.display = "none"; });
  await p.evaluate((c) => window.__dragon.setCam(c), cam || "cinema");
  const a = parseFloat(t0), n = Math.round((parseFloat(t1) - a) * fps);
  for (let i = 0; i <= n; i++) {
    const k = Math.round(a * fps) + i, f = path.join(out, "f" + String(k).padStart(4, "0") + ".png");
    if (fs.existsSync(f)) continue;
    await p.evaluate((t) => window.__dragon.seekReal(t), k / fps);
    await p.locator("#stage").screenshot({ path: f, timeout: 120000 });
  }
  await b.close();
})();
