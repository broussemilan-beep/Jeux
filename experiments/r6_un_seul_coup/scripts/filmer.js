// FILME le lecteur de « Un seul coup » (output/un_seul_coup.html) : une image
// PNG par pas de temps réel. Usage : NODE_PATH=$(npm root -g) node filmer.js <t0> <t1> <dossier> [fps=30]
const path = require("path"), fs = require("fs");
const { chromium } = require("playwright");
(async () => {
  const [t0, t1, out, fpsArg] = process.argv.slice(2);
  const fps = parseFloat(fpsArg || "30");
  fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 900, height: 720 } });
  await p.goto("file://" + path.join(__dirname, "..", "output", "un_seul_coup.html"));
  await p.waitForTimeout(2000);
  await p.evaluate(() => { document.getElementById("hud").style.display = "none"; });
  const a = parseFloat(t0), n = Math.round((parseFloat(t1) - a) * fps);
  for (let i = 0; i <= n; i++) {
    const k = Math.round(a * fps) + i, f = path.join(out, "f" + String(k).padStart(4, "0") + ".png");
    if (fs.existsSync(f)) continue;
    await p.evaluate((t) => window.__usc.seekReal(t), k / fps);
    await p.locator("#stage").screenshot({ path: f, timeout: 120000 });
  }
  await b.close();
})();
