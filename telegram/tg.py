#!/usr/bin/env python3
"""ZATORI NATION – Telegram-Autopilot.

Der Bot-Token kommt ausschließlich aus der Umgebungsvariable TELEGRAM_BOT_TOKEN.
Dieses Skript gibt den Token nie aus, auch nicht in Fehlermeldungen.

Befehle:
  python3 telegram/tg.py check
      Zeigt, ob der Token gesetzt ist, ob config.json vollständig ist und was heute schon gepostet wurde.
  python3 telegram/tg.py discover
      Liest die letzten Bot-Updates und trägt Gruppen- und Themen-IDs in config.json ein.
      Voraussetzung: Bot ist Admin in beiden Gruppen und in jedem Thema wurde nach dem Hinzufügen
      des Bots mindestens eine Nachricht geschrieben.
  python3 telegram/tg.py send GRUPPE THEMA DATEI --kind ART --title "Kurztitel" [--dry-run]
      Sendet den Text aus DATEI in das Thema und protokolliert in log.json.
      Sperre: dieselbe GRUPPE + ART am selben Tag wird nicht ein zweites Mal gesendet.
"""
import json, os, sys, datetime, urllib.request, urllib.parse, urllib.error
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "config.json")
LOG = os.path.join(HERE, "log.json")
TZ = ZoneInfo("Europe/Berlin")


def token():
    t = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not t:
        sys.exit("FEHLER: TELEGRAM_BOT_TOKEN ist nicht gesetzt (Umgebungsvariable der Cloud-Umgebung).")
    return t


def api(method, params=None):
    url = f"https://api.telegram.org/bot{token()}/{method}"
    data = urllib.parse.urlencode(params or {}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=30) as r:
            res = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            res = json.loads(e.read().decode())
        except Exception:
            sys.exit(f"FEHLER: Telegram antwortet mit HTTP {e.code} bei {method}.")
    except Exception as e:  # Netzwerk; URL (mit Token) nicht ausgeben
        sys.exit(f"FEHLER: keine Verbindung zu api.telegram.org bei {method} ({type(e).__name__}).")
    if not res.get("ok"):
        sys.exit(f"FEHLER bei {method}: {res.get('error_code')} {res.get('description')}")
    return res["result"]


def load(p, default):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save(p, obj):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def today():
    return datetime.datetime.now(TZ).strftime("%Y-%m-%d")


def cmd_check():
    print("Token gesetzt:", "ja" if os.environ.get("TELEGRAM_BOT_TOKEN", "").strip() else "NEIN")
    cfg = load(CONFIG, {})
    for g, gc in cfg.get("groups", {}).items():
        missing = [k for k, t in gc["topics"].items() if t["thread_id"] is None]
        print(f"Gruppe {g}: chat_id={'ok' if gc['chat_id'] else 'FEHLT'}; Themen ohne ID: {', '.join(missing) or 'keine'}")
    d = today()
    done = [e for e in load(LOG, []) if e.get("date") == d]
    print(f"Heute ({d}) gepostet: {len(done)}")
    for e in done:
        print(f"  - {e['group']}/{e['topic']} [{e['kind']}] {e['title']}")
    if os.environ.get("TELEGRAM_BOT_TOKEN", "").strip():
        me = api("getMe")
        print("Bot:", "@" + me.get("username", "?"))


def cmd_discover():
    cfg = load(CONFIG, {})
    updates = api("getUpdates", {"limit": 100, "allowed_updates": json.dumps(["message", "my_chat_member"])})
    chats, topics = {}, {}  # chat_id -> title ; (chat_id, thread_id) -> name
    for u in updates:
        m = u.get("message") or {}
        mc = u.get("my_chat_member") or {}
        c = m.get("chat") or mc.get("chat")
        if not c or c.get("type") not in ("group", "supergroup"):
            continue
        chats[c["id"]] = c.get("title", "")
        if m.get("forum_topic_created") and m.get("message_thread_id"):
            topics[(c["id"], m["message_thread_id"])] = m["forum_topic_created"]["name"]
        r = m.get("reply_to_message") or {}
        if m.get("is_topic_message") and r.get("forum_topic_created"):
            topics[(c["id"], m["message_thread_id"])] = r["forum_topic_created"]["name"]
    print(f"Gefundene Gruppen: {len(chats)}, gefundene Themen: {len(topics)}")
    for cid, title in chats.items():
        print(f"  Gruppe: {title}")
    for g, gc in cfg["groups"].items():
        for cid, title in chats.items():
            if gc["title_contains"] in title and not (gc.get("exclude_title_contains") and gc["exclude_title_contains"] in title):
                gc["chat_id"] = cid
        for key, t in gc["topics"].items():
            for (cid, tid), name in topics.items():
                if cid == gc["chat_id"] and t["name_contains"].lower() in name.lower():
                    t["thread_id"] = tid
    save(CONFIG, cfg)
    for (cid, tid), name in topics.items():
        print(f"  Thema: {chats.get(cid, cid)} / {name}")
    cmd_check()


def cmd_send(args):
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    def opt(name):
        if name in args:
            i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return v
        sys.exit(f"FEHLER: {name} fehlt")
    kind, title = opt("--kind"), opt("--title")
    if len(args) != 3:
        sys.exit(__doc__)
    group, topic, path = args
    text = open(path, encoding="utf-8").read().strip()
    if not text:
        sys.exit("FEHLER: Text ist leer.")
    if len(text) > 4000:
        sys.exit(f"FEHLER: Text hat {len(text)} Zeichen, Telegram erlaubt 4096. Kürzen.")
    cfg = load(CONFIG, {})
    gc = cfg["groups"][group]
    tc = gc["topics"][topic]
    if (not gc["chat_id"] or not tc["thread_id"]) and not dry:
        sys.exit(f"FEHLER: IDs für {group}/{topic} fehlen. Erst 'discover' ausführen.")
    log = load(LOG, [])
    d = today()
    if any(e["date"] == d and e["group"] == group and e["kind"] == kind for e in log):
        print(f"SPERRE: {group} [{kind}] wurde heute schon gesendet. Nichts gesendet.")
        return
    if dry:
        print(f"PROBELAUF: würde {len(text)} Zeichen an {group}/{topic} senden.\n---\n{text}\n---")
        return
    res = api("sendMessage", {
        "chat_id": gc["chat_id"],
        "message_thread_id": tc["thread_id"],
        "text": text,
        "link_preview_options": json.dumps({"is_disabled": True}),
    })
    log.append({
        "date": d,
        "weekday": datetime.datetime.now(TZ).strftime("%A"),
        "group": group, "topic": topic, "kind": kind, "title": title,
        "message_id": res.get("message_id"), "chars": len(text),
    })
    save(LOG, log)
    print(f"GESENDET: {group}/{topic} [{kind}] message_id={res.get('message_id')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    c, rest = sys.argv[1], sys.argv[2:]
    {"check": lambda: cmd_check(), "discover": lambda: cmd_discover(), "send": lambda: cmd_send(rest)}.get(
        c, lambda: sys.exit(__doc__))()
