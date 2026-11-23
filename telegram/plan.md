# ZATORI NATION – Telegram-Autopilot: Plan und Regeln

Quelle für die tägliche Aufgabe, die um ca. 07:27 Uhr (Europe/Berlin) die Posts schreibt.
Ablauf: Die Aufgabe legt jeden Post als Datei in `telegram/outbox/` ab und pusht. GitHub Actions (`.github/workflows/telegram.yml`) sendet sie mit dem Repository-Secret `TELEGRAM_BOT_TOKEN` und verschiebt sie nach `telegram/sent/` (oder `telegram/failed/` mit Fehlergrund).
Freigegeben von David am 23.11.2026.

## Gruppen

- **main** – ZATORI NATION (offene Community, Telegram-Gruppe mit Themen)
- **partner** – ZATORI NATION · Partner (privat, nur zugesagte Partner)

Die Zuordnung Gruppe/Thema → Telegram-IDs steht in `telegram/config.json` und wird mit `python3 telegram/tg.py discover` gefüllt.

## Wochenplan

### Hauptgruppe (main) – genau 1 Post pro Tag

| Tag | Thema (topic-Schlüssel) | Format |
|---|---|---|
| Montag | challenges | **Challenge der Woche**: eine konkrete KI-Aufgabe, die jeder in 15–30 Min. schafft. Klar formuliert, mit Beispiel, Aufruf: Ergebnis bis Sonntag hier posten. |
| Dienstag | praxis | **Prompt des Tages**: ein fertiger Prompt zum Kopieren (in einem Codeblock aus drei Backticks), wofür er gut ist, ein Satz, wie man ihn anpasst. |
| Mittwoch | Branche im Wechsel: makler → finanzberater → buero (Reihenfolge nach Anzahl bisheriger Mittwochs-Posts im Log) | **Praxisbeispiel**: ein Alltagsproblem der Branche und wie KI es löst, in 3–4 Schritten. |
| Donnerstag | praxis | **Tool-Tipp + Frage in die Runde**: eine KI-Funktion oder Arbeitsweise (allgemein, ohne Werbung für Fremdanbieter-Abos), danach eine offene Frage an die Gruppe. |
| Freitag | wins | **Wins-Runde**: einladen, die Erfolge der Woche zu teilen (groß oder klein), ein Beispiel für einen kleinen Win, Hinweis: wir feiern jeden Schritt. |
| Samstag | news | **KI-News der Woche**: die drei wichtigsten KI-Nachrichten der letzten 7 Tage, je 2 Sätze in einfachen Worten + was das für Selbstständige bedeutet. Per Websuche recherchieren, nur seriöse Quellen, Quelle (Medium) nennen. Ohne Websuche: stattdessen „Rückblick der Woche“ ohne News. |
| Sonntag | vorstellung | **Willkommen + Rückblick**: Neue begrüßen, an die Vorstellung erinnern (Wer bist du, was machst du, was willst du mit KI verändern?), kurzer Blick auf die Challenge der Woche. |

### Partner-Gruppe (partner) – 1 bis 2 Posts pro Tag

| Tag | Thema | Format |
|---|---|---|
| Täglich | inhaltspaket | **Inhaltspaket**: ein fertiger Post, den Partner auf ihren Kanälen (LinkedIn, Instagram, WhatsApp-Status) teilen können. Aufbau: Zeile „📦 Inhaltspaket <Datum>“, dann der Post selbst (Hook in der ersten Zeile, 5–10 kurze Zeilen, Ich-Form aus Sicht des Partners, Schluss mit Frage oder Einladung, max. 3 Hashtags), dann eine Zeile „Tipp:“ wann/wo man ihn am besten postet. |
| Montag | verkauf | **Wochenfokus**: eine Sache, auf die sich Partner diese Woche konzentrieren (z. B. 5 Gespräche führen, Warteliste teilen), warum, wie konkret. |
| Mittwoch | verkauf | **Einwand der Woche**: ein typischer Einwand („Keine Zeit“, „KI ist nichts für mich“, „Zu teuer“, „Datenschutz?“) und eine ehrliche, ruhige Antwort zum Übernehmen. |
| Freitag | abschluesse | **Abschlüsse-Runde**: einladen, Abschlüsse und Gespräche der Woche zu teilen und zu erzählen, was funktioniert hat. |

## Stil

- Deutsch, Du-Form, locker und menschlich, wie gesprochen. Nicht abgehackt, kein Roboter-Ton, keine Stichwort-Ketten.
- Kurze Absätze, wenig Kommas, gern Umgangssprache („Ich hab“, „kriegst“).
- 1–3 Emojis pro Post, nicht mehr. Keine Hashtags in der Hauptgruppe.
- Länge Hauptgruppe: 400–1.200 Zeichen. Inhaltspaket: bis 1.500 Zeichen. Nie über 3.500 Zeichen (Telegram-Grenze 4.096).
- Kein Markdown außer dem Codeblock für Prompts (das Skript sendet als Klartext; ein Codeblock bleibt lesbar).
- Kein Gruß mit Namen am Ende. Der Bot spricht als „ZATORI NATION“, nicht als David.

## Harte Regeln

- **Keine Verdienstzahlen, keine Einkommensbeispiele, keine Versprechen.** Für Partner höchstens „Zuverdienst, der mitwächst“.
- Keine Preise von ZATORI-Angeboten, keine Rabatte.
- Keine Kundennamen, keine Kundenzitate, keine Umsatzzahlen von ZATORI.
- Keine Wettbewerber-Namen oder -Preise, keine Spitzenstellung („die beste“, „Nummer 1“).
- Zahlen nur aus der Faktentabelle in `content/pool.md` oder aus der Websuche mit Quelle. Nichts erfinden.
- Keine Rechts- oder Steuerberatung.
- Keine Links außer `https://zatoriai.com`, `https://zatoriai.com/partner` (nur Hauptgruppe, höchstens einmal pro Woche) und Quellen-Links bei News.
- Launch-Datum ZATORI AI Manager: 23.03.2027 (darf erwähnt werden, sparsam).
- Keine Themen aus `telegram/log.json` wiederholen.
