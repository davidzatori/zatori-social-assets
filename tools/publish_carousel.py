#!/usr/bin/env python3
"""
ZATORI Social Autopilot – Karussell auf Instagram veröffentlichen

Nimmt einen Ordner mit Slides (01.jpg, 02.jpg, …), die bereits auf GitHub
gepusht sind, und eine Caption-Datei. Legt die Item-Container an, dann den
Karussell-Container, wartet auf FINISHED und veröffentlicht.

Der Instagram-Token wird NICHT übergeben: Der Proxy der Cloud-Umgebung setzt ihn
automatisch für graph.instagram.com ein.

Aufruf:
    python3 tools/publish_carousel.py posts/2026-10-18-softwarekosten caption.txt
    python3 tools/publish_carousel.py posts/2026-10-18-softwarekosten caption.txt --dry-run

--dry-run legt Container an, veröffentlicht aber nicht.
Schreibt bei Erfolg einen Eintrag in posts/log.json (Datum, Ordner, Media-ID, Permalink).
"""
import glob
import json
import os
import subprocess
import sys
import time

API = "https://graph.instagram.com/v21.0"
RAW = "https://raw.githubusercontent.com/davidzatori/zatori-social-assets/main"


def curl(args):
    out = subprocess.run(["curl", "-sS"] + args, capture_output=True, text=True, timeout=60)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"error": {"message": f"Keine JSON-Antwort: {out.stdout[:300]} {out.stderr[:300]}"}}


def post(path, data):
    args = ["-X", "POST", f"{API}/{path}"]
    for k, v in data.items():
        args += ["--data-urlencode", f"{k}={v}"]
    return curl(args)


def get(path, fields):
    return curl([f"{API}/{path}?fields={fields}"])


def fail(msg, payload=None):
    print("FEHLER:", msg)
    if payload is not None:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(1)


def wait_finished(container_id, tries=12, delay=5):
    for _ in range(tries):
        st = get(container_id, "status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            return st
        if code in ("ERROR", "EXPIRED"):
            fail(f"Container {container_id} im Status {code}", st)
        time.sleep(delay)
    fail(f"Container {container_id} wurde nicht fertig", st)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    folder = sys.argv[1].rstrip("/")
    caption_file = sys.argv[2]
    dry = "--dry-run" in sys.argv

    slides = sorted(glob.glob(os.path.join(folder, "[0-9][0-9].jpg")))
    if not 2 <= len(slides) <= 10:
        fail(f"{len(slides)} Slides gefunden, erlaubt sind 2 bis 10")
    with open(caption_file, "r", encoding="utf-8") as fh:
        caption = fh.read().strip()
    if len(caption) > 2200:
        fail(f"Caption zu lang ({len(caption)} Zeichen, max. 2200)")
    if caption.count("#") > 5:
        fail("Mehr als 5 Hashtags in der Caption")

    # Vorab prüfen, dass jedes Bild öffentlich erreichbar ist
    rel = os.path.relpath(folder, start=os.getcwd()) if not folder.startswith("posts/") else folder
    urls = [f"{RAW}/{rel}/{os.path.basename(p)}" for p in slides]
    for u in urls:
        code = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", u],
                              capture_output=True, text=True, timeout=30).stdout.strip()
        if code != "200":
            fail(f"Bild nicht öffentlich erreichbar (HTTP {code}): {u}. Wurde gepusht?")
    print(f"{len(urls)} Bilder öffentlich erreichbar.")

    # Item-Container
    items = []
    for u in urls:
        r = post("me/media", {"image_url": u, "is_carousel_item": "true"})
        if "id" not in r:
            fail("Item-Container fehlgeschlagen", r)
        items.append(r["id"])
        time.sleep(1)
    print("Item-Container:", ", ".join(items))
    for cid in items:
        wait_finished(cid)

    # Karussell-Container
    r = post("me/media", {"media_type": "CAROUSEL", "children": ",".join(items), "caption": caption})
    if "id" not in r:
        fail("Karussell-Container fehlgeschlagen", r)
    carousel = r["id"]
    wait_finished(carousel)
    print("Karussell-Container fertig:", carousel)

    if dry:
        print("DRY RUN: nicht veröffentlicht. Container verfällt nach 24 h.")
        return

    r = post("me/media_publish", {"creation_id": carousel})
    if "id" not in r:
        fail("Veröffentlichung fehlgeschlagen", r)
    media_id = r["id"]
    info = get(media_id, "permalink,timestamp")
    entry = {
        "date": time.strftime("%Y-%m-%d"),
        "folder": folder,
        "media_id": media_id,
        "permalink": info.get("permalink"),
        "caption_first_line": caption.splitlines()[0][:120],
    }
    log_path = "posts/log.json"
    log = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as fh:
            log = json.load(fh)
    log.append(entry)
    with open(log_path, "w", encoding="utf-8") as fh:
        json.dump(log, fh, ensure_ascii=False, indent=2)
    print("VERÖFFENTLICHT:", json.dumps(entry, ensure_ascii=False))


if __name__ == "__main__":
    main()
