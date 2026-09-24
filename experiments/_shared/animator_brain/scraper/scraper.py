"""
Scrapeur de references du cerveau v2 (CERVEAU_V2.md) : cherche des clips,
les fait passer dans clip_analyzer, garde la FICHE (et une planche locale pour
le jugement des poses), JAMAIS la video.

Sources (sources.json) :
- sakugabooru : API moebooru (post.json) par etiquettes, triee par score des
  fans d'animation -- le signal « qualite d'animation », pas seulement « ce
  dont on a besoin » ;
- youtube : recherche yt-dlp (extrait des premieres secondes, basse definition) ;
- gallery_dl : images (Danbooru, Reddit, Webtoons...) -> metadonnees + planche ;
- local : un dossier ou des fichiers (les clips envoyes par Milan).

Tout est idempotent : un index (corpus/refs/index.jsonl) evite de retraiter
un clip deja vu (md5 / id source). Debit limite (1 requete/s par defaut).
Le reseau du sandbox peut refuser un domaine : `acces` le dit, domaine par
domaine, avant de lancer quoi que ce soit.

Usage :
  python3 scraper.py acces
  python3 scraper.py sakuga [--max 20] [--requete "fighting impact_frames"]
  python3 scraper.py youtube [--max 5]
  python3 scraper.py images [--max 30]
  python3 scraper.py local <fichier_ou_dossier> ... [--source milan]
  python3 scraper.py classement [--top 15]
Tests hors ligne : python3 test_scraper.py
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BRAIN = os.path.dirname(HERE)
sys.path.insert(0, BRAIN)
import clip_analyzer as CA  # noqa: E402

REFS = os.environ.get("REFS_DIR", os.path.join(BRAIN, "corpus", "refs"))
INDEX = os.path.join(REFS, "index.jsonl")
SHEETS = os.environ.get("REFS_SHEETS", "/tmp/refs_sheets")        # planches : locales, jamais committees
UA = "animator-brain-research/0.1 (usage personnel, fiches derivees uniquement)"
MAX_MB = 60
VIDEO_EXT = {"mp4", "webm", "gif", "mov", "mkv"}
IMAGE_EXT = {"jpg", "jpeg", "png", "webp"}


def load_sources():
    return json.load(open(os.path.join(HERE, "sources.json")))


# ------------------------------------------------------------------ index

def index_load():
    seen = {}
    if os.path.exists(INDEX):
        for line in open(INDEX):
            if line.strip():
                r = json.loads(line)
                seen[r["cle"]] = r
    return seen


def index_add(rec):
    os.makedirs(REFS, exist_ok=True)
    with open(INDEX, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ reseau

class Http:
    """GET avec debit limite. `base_override` permet aux tests de rediriger
    un domaine vers un faux serveur local."""

    def __init__(self, delay=1.0, base_override=None):
        self.delay, self.last = delay, 0.0
        self.base_override = base_override or {}

    def _url(self, url):
        for real, fake in self.base_override.items():
            if url.startswith(real):
                return fake + url[len(real):]
        return url

    def get(self, url, timeout=30):
        wait = self.delay - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        self.last = time.time()
        req = urllib.request.Request(self._url(url), headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read()

    def json(self, url):
        return json.loads(self.get(url).decode("utf-8"))

    def download(self, url, path, max_mb=MAX_MB):
        data = self.get(url, timeout=120)
        if len(data) > max_mb * 1e6:
            raise ValueError(f"fichier trop gros ({len(data) / 1e6:.0f} Mo)")
        open(path, "wb").write(data)
        return path


def check_access(domains, timeout=10):
    """{domaine: 'ok' | raison}. Un 4xx/5xx HTTP prouve que le domaine repond
    (le proxy laisse passer) ; un refus du proxy leve une erreur de tunnel."""
    out = {}
    for d in domains:
        try:
            urllib.request.urlopen(urllib.request.Request(f"https://{d}/", headers={"User-Agent": UA}),
                                   timeout=timeout)
            out[d] = "ok"
        except urllib.error.HTTPError as e:
            out[d] = f"ok (repond HTTP {e.code})"
        except Exception as e:  # noqa: BLE001 -- on rapporte la cause telle quelle
            msg = str(e)
            out[d] = "refuse par la politique reseau" if "403" in msg or "Tunnel" in msg else f"injoignable : {msg[:80]}"
    return out


# ------------------------------------------------------------------ fiche

def _analyse_et_range(path, source, cle, meta, garder_planche=True):
    """clip_analyzer -> corpus/refs/<source>/<cle>.json ; supprime la video."""
    out_dir = os.path.join(REFS, source)
    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(cle))[:80]
    fiche = CA.analyze(path, SHEETS if garder_planche else None, label=f"{source}_{safe}")
    fiche["source"] = {"nom": source, **meta}
    json.dump(fiche, open(os.path.join(out_dir, safe + ".json"), "w"), indent=1, ensure_ascii=False)
    index_add({"cle": cle, "source": source, "fiche": os.path.relpath(os.path.join(out_dir, safe + ".json"), REFS),
               "pourquoi": meta.get("pourquoi"), "score_source": meta.get("score"),
               "interet": fiche["interet_heuristique"]["score_100"], "date": time.strftime("%Y-%m-%d")})
    return fiche


# ------------------------------------------------------------------ sakugabooru

def sakuga(http, requetes, max_par_requete=10, pages=1, dry=False):
    seen = index_load()
    base = "https://www.sakugabooru.com"
    done = []
    for rq in requetes:
        tags = rq["tags"] if "order:" in rq["tags"] else rq["tags"] + " order:score"
        n = 0
        for page in range(1, pages + 1):
            url = f"{base}/post.json?" + urllib.parse.urlencode({"tags": tags, "limit": 40, "page": page})
            posts = http.json(url)
            for p in posts:
                if n >= max_par_requete:
                    break
                ext = (p.get("file_ext") or p.get("file_url", "").rsplit(".", 1)[-1]).lower()
                cle = f"sakuga:{p['id']}"
                if ext not in VIDEO_EXT or cle in seen:
                    continue
                if (p.get("file_size") or 0) > MAX_MB * 1e6:      # trop gros : on ne le telecharge meme pas
                    continue
                meta = {"id": p["id"], "tags": p.get("tags", ""), "score": p.get("score"),
                        "source_oeuvre": p.get("source", ""), "url": f"{base}/post/show/{p['id']}",
                        "requete": rq["tags"], "pourquoi": rq["pourquoi"]}
                if dry:
                    done.append(meta)
                    n += 1
                    continue
                tmp = tempfile.mkdtemp()
                try:
                    f = http.download(p["file_url"], os.path.join(tmp, f"{p['id']}.{ext}"))
                    _analyse_et_range(f, "sakugabooru", cle, meta)
                    seen[cle] = True
                    done.append(meta)
                    n += 1
                except Exception as e:  # noqa: BLE001
                    print(f"  saute {cle} : {e}")
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
    return done


# ------------------------------------------------------------------ danbooru (clips animes)

def danbooru(http, requetes, max_par_requete=10, dry=False):
    """Posts animes de Danbooru. Le filtre rating:g (general) est IMPOSE ici,
    quelle que soit la requete : aucun contenu adulte n'entre dans le corpus."""
    seen = index_load()
    base = "https://danbooru.donmai.us"
    done = []
    for rq in requetes:
        tags = " ".join(t for t in rq["tags"].split() if not t.startswith("rating:"))
        # un visiteur anonyme a droit a 2 etiquettes (rating: est gratuit,
        # order: ne l'est pas) : on trie par score de notre cote
        tags = " ".join(t for t in tags.split() if not t.startswith("order:"))
        tags = f"{tags} animated rating:g"
        posts = []
        for page in (1, 2):
            posts += http.json(f"{base}/posts.json?" + urllib.parse.urlencode({"tags": tags, "limit": 100, "page": page}))
        posts.sort(key=lambda p: -(p.get("score") or 0))
        n = 0
        for p in posts:
            if n >= max_par_requete:
                break
            ext = (p.get("file_ext") or "").lower()
            cle = f"danbooru:{p.get('id')}"
            if p.get("rating") != "g" or ext not in VIDEO_EXT or cle in seen or not p.get("file_url"):
                continue
            if (p.get("file_size") or 0) > MAX_MB * 1e6:
                continue
            meta = {"id": p["id"], "tags": p.get("tag_string", ""), "score": p.get("score"),
                    "source_oeuvre": p.get("tag_string_copyright", ""), "artiste": p.get("tag_string_artist", ""),
                    "url": f"{base}/posts/{p['id']}", "requete": rq["tags"], "pourquoi": rq["pourquoi"]}
            if dry:
                done.append(meta)
                n += 1
                continue
            tmp = tempfile.mkdtemp()
            try:
                f = http.download(p["file_url"], os.path.join(tmp, f"{p['id']}.{ext}"))
                _analyse_et_range(f, "danbooru", cle, meta)
                seen[cle] = True
                done.append(meta)
                n += 1
            except Exception as e:  # noqa: BLE001
                print(f"  saute {cle} : {e}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    return done


# ------------------------------------------------------------------ youtube (yt-dlp)

def youtube(requetes, par_requete=5, extrait_s=40, dry=False):
    seen = index_load()
    done = []
    for rq in requetes:
        search = f"ytsearch{par_requete}:{rq['q']}"
        lst = subprocess.run(["yt-dlp", "--flat-playlist", "-J", search], capture_output=True, text=True)
        if lst.returncode:
            print(f"  youtube inaccessible : {lst.stderr.strip()[:160]}")
            return done
        for e in json.loads(lst.stdout).get("entries", []):
            cle = f"youtube:{e['id']}"
            if cle in seen:
                continue
            meta = {"id": e["id"], "titre": e.get("title"), "chaine": e.get("channel") or e.get("uploader"),
                    "url": f"https://www.youtube.com/watch?v={e['id']}", "requete": rq["q"], "pourquoi": rq["pourquoi"]}
            if dry:
                done.append(meta)
                continue
            tmp = tempfile.mkdtemp()
            try:
                out = os.path.join(tmp, "clip.mp4")
                r = subprocess.run(["yt-dlp", "-q", "-f", "bv*[height<=480][ext=mp4]/b[height<=480]", "--download-sections",
                                    f"*0-{extrait_s}", "-o", out, meta["url"]], capture_output=True, text=True)
                if r.returncode or not os.path.exists(out):
                    raise RuntimeError(r.stderr.strip()[:160])
                _analyse_et_range(out, "youtube", cle, meta)
                done.append(meta)
            except Exception as ex:  # noqa: BLE001
                print(f"  saute {cle} : {ex}")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    return done


# ------------------------------------------------------------------ images (gallery-dl)

def images(urls, max_par_url=30):
    """Poses et cases : pas de mouvement a mesurer. On garde les metadonnees
    (etiquettes, source) et une planche LOCALE pour le jugement des poses."""
    done = []
    for u in urls:
        tmp = tempfile.mkdtemp()
        try:
            r = subprocess.run(["gallery-dl", "--range", f"1-{max_par_url}", "--write-metadata", "-D", tmp, u["url"]],
                               capture_output=True, text=True)
            if r.returncode and not os.listdir(tmp):
                print(f"  inaccessible : {u['url']} ({r.stderr.strip()[:120]})")
                continue
            metas = []
            for fn in sorted(os.listdir(tmp)):
                if fn.endswith(".json"):
                    m = json.load(open(os.path.join(tmp, fn)))
                    metas.append({k: m.get(k) for k in ("id", "tag_string", "tags", "title", "score", "source", "url")
                                  if m.get(k) is not None})
            out_dir = os.path.join(REFS, "images")
            os.makedirs(out_dir, exist_ok=True)
            name = hashlib.sha1(u["url"].encode()).hexdigest()[:12]
            json.dump({"url": u["url"], "pourquoi": u["pourquoi"], "elements": metas},
                      open(os.path.join(out_dir, name + ".json"), "w"), indent=1, ensure_ascii=False)
            imgs = [os.path.join(tmp, f) for f in sorted(os.listdir(tmp)) if f.rsplit(".", 1)[-1].lower() in IMAGE_EXT]
            if imgs:
                _planche_images(imgs, os.path.join(SHEETS, f"images_{name}.png"))
            done.append({"url": u["url"], "n": len(metas)})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return done


def _planche_images(paths, out, w=220, cols=6):
    from PIL import Image
    os.makedirs(os.path.dirname(out), exist_ok=True)
    ims = []
    for p in paths[:36]:
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail((w, w))
            ims.append(im)
        except Exception:  # noqa: BLE001
            continue
    if not ims:
        return
    rows = (len(ims) + cols - 1) // cols
    s = Image.new("RGB", (w * cols, w * rows), "white")
    for k, im in enumerate(ims):
        s.paste(im, ((k % cols) * w, (k // cols) * w))
    s.save(out)


# ------------------------------------------------------------------ local

def local(paths, source="milan"):
    seen = index_load()
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p))]
        else:
            files.append(p)
    done = []
    for f in files:
        if f.rsplit(".", 1)[-1].lower() not in VIDEO_EXT:
            continue
        md5 = hashlib.md5(open(f, "rb").read()).hexdigest()
        cle = f"{source}:{md5}"
        if cle in seen:
            continue
        _analyse_et_range(f, source, cle, {"fichier": os.path.basename(f), "md5": md5, "pourquoi": "envoye par Milan"})
        seen[cle] = True
        done.append(f)
    return done


# ------------------------------------------------------------------ classement

def classement(top=15):
    """Classe les fiches pour MA revue (le jugement des poses se fait a
    l'oeil) par le score de la source, normalise par source. L'« interet »
    heuristique de clip_analyzer n'entre PLUS dans le classement : confronte
    aux premiers vrais clips (2026-09-24), il donnait 74/100 a notre v1 et
    45-51 a des plans de Yutaka Nakamura -- il recompense les tenues et le
    rythme d'impacts, pas la qualite. Il reste affiche pour information."""
    rows = [r for r in index_load().values()]
    if not rows:
        return []
    by_src = {}
    for r in rows:
        by_src.setdefault(r["source"], []).append(r.get("score_source") or 0)
    ranked = [((r.get("score_source") or 0) / max(1, max(by_src[r["source"]])), r) for r in rows]
    ranked.sort(key=lambda x: -x[0])
    return [(round(v, 3), r) for v, r in ranked[:top]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["acces", "sakuga", "danbooru", "youtube", "images", "local", "classement"])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--requete")
    ap.add_argument("--source", default="milan")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--dry", action="store_true", help="liste sans telecharger")
    a = ap.parse_args()
    src = load_sources()
    if a.cmd == "acces":
        doms = [src["sakugabooru"]["domaine"], src["youtube"]["domaine"], "danbooru.donmai.us", "www.reddit.com",
                "www.webtoons.com", "api.mangadex.org", "ultimateframedata.com", "mocap.cs.cmu.edu", "github.com",
                "huggingface.co", "devforum.roblox.com"]
        for d, s in check_access(doms).items():
            print(f"{d:28s} {s}")
    elif a.cmd == "sakuga":
        rq = [r for r in src["sakugabooru"]["requetes"] if not a.requete or r["tags"] == a.requete]
        for m in sakuga(Http(), rq, a.max, dry=a.dry):
            print(f"  + sakuga {m['id']} score {m['score']} ({m['requete']})")
    elif a.cmd == "danbooru":
        for m in danbooru(Http(), src["danbooru"]["requetes"], a.max, dry=a.dry):
            print(f"  + danbooru {m['id']} score {m['score']} ({m['requete']})")
    elif a.cmd == "youtube":
        for m in youtube(src["youtube"]["requetes"], a.max, src["youtube"]["extrait_s"], dry=a.dry):
            print(f"  + youtube {m['id']} {m.get('titre')}")
    elif a.cmd == "images":
        for m in images(src["gallery_dl"]["urls"], a.max):
            print(f"  + {m['n']} images de {m['url']}")
    elif a.cmd == "local":
        for f in local(a.paths, a.source):
            print(f"  + {f}")
    else:
        for v, r in classement(a.top):
            print(f"{v:.3f}  {r['cle']:32s} interet {r['interet']:3d}  score_source {r.get('score_source')}  {r.get('pourquoi')}")


if __name__ == "__main__":
    main()
