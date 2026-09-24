"""
Test hors ligne du scrapeur : un faux Sakugabooru (serveur HTTP local) sert
un post.json et deux clips generes par ffmpeg (un vrai .mp4, une image .jpg
qui doit etre ignoree). Verifie : requete, telechargement, fiche ecrite,
video supprimee, index, deduplication au 2e passage, classement, ingestion
locale.
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

TMP = tempfile.mkdtemp()
os.environ["REFS_DIR"] = os.path.join(TMP, "refs")
os.environ["REFS_SHEETS"] = os.path.join(TMP, "sheets")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scraper as S  # noqa: E402

SITE = os.path.join(TMP, "site")
os.makedirs(os.path.join(SITE, "data"))
# un « coup » : carre qui avance lentement, freine, flash blanc 2 images, puis part vite
subprocess.run(["ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i",
                "color=c=gray:s=320x180:d=2:r=24", "-vf",
                "drawbox=x='if(lt(t,1),40+40*t,if(lt(t,1.1),80,300))':y=60:w=40:h=40:c=black:t=fill,"
                "drawbox=x=0:y=0:w=320:h=180:c=white:t=fill:enable='between(t,1.0,1.08)'",
                "-pix_fmt", "yuv420p", os.path.join(SITE, "data", "a.mp4")], check=True)
shutil.copy(os.path.join(SITE, "data", "a.mp4"), os.path.join(SITE, "data", "b.mp4"))
open(os.path.join(SITE, "data", "c.jpg"), "wb").write(b"\xff\xd8 pas une video")
posts = [{"id": 1, "tags": "fighting impact_frames", "score": 90, "file_ext": "mp4", "file_url": "BASE/data/a.mp4", "source": "Test"},
         {"id": 2, "tags": "fighting smears", "score": 30, "file_ext": "mp4", "file_url": "BASE/data/b.mp4", "source": "Test"},
         {"id": 3, "tags": "fighting", "score": 99, "file_ext": "jpg", "file_url": "BASE/data/c.jpg", "source": "Test"}]
requests = []


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=SITE, **k)

    def do_GET(self):
        requests.append(self.path)
        if self.path.startswith("/post.json"):
            base = f"http://127.0.0.1:{self.server.server_port}"
            body = json.dumps([{**p, "file_url": p["file_url"].replace("BASE", base)} for p in posts]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def log_message(self, *a):
        pass


srv = http.server.HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
fake = f"http://127.0.0.1:{srv.server_port}"
http_ = S.Http(delay=0.0, base_override={"https://www.sakugabooru.com": fake})
rq = [{"tags": "fighting impact_frames", "pourquoi": "test"}]
ok = True


def check(cond, msg):
    global ok
    print(("OK   " if cond else "ECHEC") + " " + msg)
    ok &= bool(cond)


try:
    done = S.sakuga(http_, rq, max_par_requete=10)
    check(len(done) == 2, f"2 clips retenus (image ignoree) : {[d['id'] for d in done]}")
    check(any("order%3Ascore" in r for r in requests), "la requete ajoute order:score")
    fiches = sorted(os.listdir(os.path.join(TMP, "refs", "sakugabooru")))
    check(fiches == ["sakuga_1.json", "sakuga_2.json"], f"fiches ecrites : {fiches}")
    f = json.load(open(os.path.join(TMP, "refs", "sakugabooru", "sakuga_1.json")))
    check(f["source"]["score"] == 90 and "impact_frames" in f["source"]["tags"], "metadonnees de la source dans la fiche")
    check(f["impacts"]["nombre"] >= 1, f"le flash blanc est vu comme impact ({f['impacts']['nombre']})")
    check(not any(fn.endswith((".mp4", ".webm", ".gif")) for _, _, fs in os.walk(os.path.join(TMP, "refs")) for fn in fs),
          "aucune video gardee")
    n_req = len(requests)
    again = S.sakuga(http_, rq, max_par_requete=10)
    check(again == [] and len(requests) == n_req + 1, "2e passage : rien retelecharge (index)")
    rk = S.classement()
    check(rk[0][1]["cle"] == "sakuga:1", f"classement : le mieux note en tete ({rk[0][1]['cle']})")
    loc = S.local([os.path.join(SITE, "data")], source="milan")
    check(len(loc) == 1, "ingestion locale : a.mp4 et b.mp4 identiques -> 1 seule fiche (md5)")
    check(S.local([os.path.join(SITE, "data")], source="milan") == [], "ingestion locale dedupliquee par md5")
    acc = S.check_access(["127.0.0.1:%d" % srv.server_port], timeout=3)
    check(list(acc.values())[0] != "", f"verification d'acces repond : {acc}")
finally:
    srv.shutdown()
    shutil.rmtree(TMP, ignore_errors=True)
print("TOUT BON" if ok else "DES ECHECS")
sys.exit(0 if ok else 1)
