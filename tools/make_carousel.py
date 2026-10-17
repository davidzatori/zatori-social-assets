#!/usr/bin/env python3
"""
ZATORI Social Autopilot – Karussell-Generator

Erzeugt aus einer JSON-Spezifikation Instagram-Slides (1080x1350, JPG)
im ZATORI-Look: Schwarz, Weiß, Rot. Inter-Schrift aus tools/fonts.

Aufruf:
    python3 tools/make_carousel.py spec.json posts/2026-10-18-softwarekosten

Spec-Format (JSON):
{
  "slides": [
    {"type": "hook",  "kicker": "SOFTWAREKOSTEN", "title": "745 € pro Mitarbeiter. Pro Monat.", "sub": "Und 36 % davon nutzt niemand."},
    {"type": "stat",  "value": "36 %", "label": "aller Software-Lizenzen werden nie benutzt"},
    {"type": "point", "n": 1, "title": "Niemand kündigt", "body": "Jemand hat gekauft, jemand ist gegangen, niemand hat gekündigt."},
    {"type": "quote", "text": "Software kündigt sich nicht von selbst."},
    {"type": "cta",   "title": "Kommentier AUTOMATION", "body": "und ich schick dir, wie wir das für Makler lösen."}
  ],
  "source": "Quelle: Zylo SaaS Management Index 2026"
}

Slide-Typen: hook, stat, point, quote, list, cta
"""
import json
import os
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
PAD = 96

BLACK = (11, 11, 14)
WHITE = (245, 245, 247)
GREY = (150, 150, 160)
DARK = (28, 28, 34)
RED = (227, 0, 15)

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")


def font(name, size):
    path = os.path.join(FONTS, name)
    return ImageFont.truetype(path, size)


F_DISPLAY = "InterDisplay-ExtraBold.otf"
F_DISPLAY_B = "InterDisplay-Bold.otf"
F_SEMI = "Inter-SemiBold.otf"
F_MED = "Inter-Medium.otf"
F_REG = "Inter-Regular.otf"


def text_width(draw, s, f):
    l, t, r, b = draw.textbbox((0, 0), s, font=f)
    return r - l


def wrap(draw, s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if text_width(draw, test, f) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, s, fname, max_w, max_h, start, minimum, line_gap=1.08):
    """Größte Schriftgröße, bei der der Text in max_w x max_h passt."""
    size = start
    while size >= minimum:
        f = font(fname, size)
        lines = wrap(draw, s, f, max_w)
        lh = int(size * line_gap)
        if len(lines) * lh <= max_h and all(text_width(draw, l, f) <= max_w for l in lines):
            return f, lines, lh
        size -= 4
    f = font(fname, minimum)
    return f, wrap(draw, s, f, max_w), int(minimum * line_gap)


def draw_lines(draw, lines, f, x, y, lh, fill):
    for l in lines:
        draw.text((x, y), l, font=f, fill=fill)
        y += lh
    return y


def base():
    img = Image.new("RGB", (W, H), BLACK)
    d = ImageDraw.Draw(img)
    # dünne rote Linie oben
    d.rectangle([PAD, 88, PAD + 72, 94], fill=RED)
    return img, d


def footer(d, idx, total, show_swipe=False):
    f = font(F_SEMI, 26)
    d.text((PAD, H - 120), "ZATORI AI", font=f, fill=WHITE)
    counter = f"{idx:02d} / {total:02d}"
    cw = text_width(d, counter, font(F_MED, 26))
    d.text((W - PAD - cw, H - 120), counter, font=font(F_MED, 26), fill=GREY)
    if show_swipe:
        f2 = font(F_MED, 26)
        s = "Wischen  →"
        sw = text_width(d, s, f2)
        d.text((W - PAD - sw, H - 170), s, font=f2, fill=RED)


def slide_hook(sl, idx, total):
    img, d = base()
    kicker = sl.get("kicker", "").upper()
    if kicker:
        d.text((PAD, 130), kicker, font=font(F_SEMI, 30), fill=RED)
    f, lines, lh = fit_font(d, sl["title"], F_DISPLAY, W - 2 * PAD, 560, 112, 56, 1.02)
    y = 420
    y = draw_lines(d, lines, f, PAD, y, lh, WHITE)
    if sl.get("sub"):
        f2, lines2, lh2 = fit_font(d, sl["sub"], F_MED, W - 2 * PAD, 200, 44, 30, 1.25)
        draw_lines(d, lines2, f2, PAD, y + 48, lh2, GREY)
    footer(d, idx, total, show_swipe=True)
    return img


def slide_stat(sl, idx, total):
    img, d = base()
    if sl.get("kicker"):
        d.text((PAD, 130), sl["kicker"].upper(), font=font(F_SEMI, 30), fill=RED)
    f, lines, lh = fit_font(d, sl["value"], F_DISPLAY, W - 2 * PAD, 300, 260, 120, 0.95)
    y = 400
    y = draw_lines(d, lines, f, PAD - 6, y, lh, RED)
    f2, lines2, lh2 = fit_font(d, sl["label"], F_DISPLAY_B, W - 2 * PAD, 360, 60, 36, 1.12)
    draw_lines(d, lines2, f2, PAD, y + 40, lh2, WHITE)
    footer(d, idx, total)
    return img


def slide_point(sl, idx, total):
    img, d = base()
    n = sl.get("n")
    y = 130
    if n is not None:
        d.text((PAD, y), f"{int(n):02d}", font=font(F_DISPLAY, 120), fill=RED)
        y += 190
    else:
        y += 60
    f, lines, lh = fit_font(d, sl["title"], F_DISPLAY_B, W - 2 * PAD, 320, 76, 44, 1.08)
    y = draw_lines(d, lines, f, PAD, y + 40, lh, WHITE)
    if sl.get("body"):
        f2, lines2, lh2 = fit_font(d, sl["body"], F_REG, W - 2 * PAD, 420, 40, 28, 1.35)
        draw_lines(d, lines2, f2, PAD, y + 40, lh2, GREY)
    footer(d, idx, total)
    return img


def slide_quote(sl, idx, total):
    img, d = base()
    d.rectangle([PAD, 380, PAD + 8, 380 + 300], fill=RED)
    f, lines, lh = fit_font(d, sl["text"], F_DISPLAY_B, W - 2 * PAD - 48, 640, 84, 44, 1.1)
    total_h = len(lines) * lh
    y = 380 + (300 - total_h) // 2 if total_h < 300 else 380
    draw_lines(d, lines, f, PAD + 48, y, lh, WHITE)
    if sl.get("by"):
        d.text((PAD + 48, y + total_h + 36), sl["by"], font=font(F_MED, 30), fill=GREY)
    footer(d, idx, total)
    return img


def slide_list(sl, idx, total):
    img, d = base()
    if sl.get("title"):
        f, lines, lh = fit_font(d, sl["title"], F_DISPLAY_B, W - 2 * PAD, 200, 64, 40, 1.08)
        y = draw_lines(d, lines, f, PAD, 150, lh, WHITE) + 40
    else:
        y = 200
    items = sl.get("items", [])
    fi = font(F_MED, 40)
    for i, it in enumerate(items[:6]):
        d.rectangle([PAD, y + 16, PAD + 14, y + 30], fill=RED)
        ls = wrap(d, it, fi, W - 2 * PAD - 48)
        for l in ls:
            d.text((PAD + 48, y), l, font=fi, fill=WHITE)
            y += 54
        y += 26
    footer(d, idx, total)
    return img


def slide_cta(sl, idx, total):
    img, d = base()
    # roter Block
    d.rectangle([0, 0, W, H], fill=RED)
    d.rectangle([PAD, 88, PAD + 72, 94], fill=WHITE)
    f, lines, lh = fit_font(d, sl["title"], F_DISPLAY, W - 2 * PAD, 420, 104, 56, 1.02)
    y = draw_lines(d, lines, f, PAD, 420, lh, WHITE)
    if sl.get("body"):
        f2, lines2, lh2 = fit_font(d, sl["body"], F_MED, W - 2 * PAD, 260, 44, 30, 1.25)
        draw_lines(d, lines2, f2, PAD, y + 48, lh2, (255, 220, 222))
    fs = font(F_SEMI, 26)
    d.text((PAD, H - 120), "ZATORI AI", font=fs, fill=WHITE)
    handle = sl.get("handle", "@zatoriai")
    hw = text_width(d, handle, font(F_MED, 26))
    d.text((W - PAD - hw, H - 120), handle, font=font(F_MED, 26), fill=WHITE)
    return img


RENDERERS = {
    "hook": slide_hook,
    "stat": slide_stat,
    "point": slide_point,
    "quote": slide_quote,
    "list": slide_list,
    "cta": slide_cta,
}


def add_source(img, source):
    if not source:
        return
    d = ImageDraw.Draw(img)
    f = font(F_REG, 22)
    d.text((PAD, H - 72), source, font=f, fill=GREY)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    spec_path, out_dir = sys.argv[1], sys.argv[2]
    with open(spec_path, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    slides = spec["slides"]
    if not 2 <= len(slides) <= 10:
        sys.exit("Ein Karussell braucht 2 bis 10 Slides.")
    os.makedirs(out_dir, exist_ok=True)
    total = len(slides)
    paths = []
    for i, sl in enumerate(slides, start=1):
        r = RENDERERS.get(sl.get("type", "point"))
        if r is None:
            sys.exit(f"Unbekannter Slide-Typ: {sl.get('type')}")
        img = r(sl, i, total)
        if sl.get("type") != "cta" and i == total - 1 or (sl.get("type") != "cta" and total == 1):
            add_source(img, spec.get("source", ""))
        if sl.get("type") == "stat" and spec.get("source"):
            add_source(img, spec["source"])
        p = os.path.join(out_dir, f"{i:02d}.jpg")
        img.save(p, "JPEG", quality=92, optimize=True)
        paths.append(p)
    print("\n".join(paths))


if __name__ == "__main__":
    main()
