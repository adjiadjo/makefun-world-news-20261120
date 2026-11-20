#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261120 entry artwork.

Draws an original front-page-style illustration summarising world news of
Friday 20 November 2026 (six sourced stories; see SOURCES.md). Build-time
only: requires Pillow and system fonts (Georgia/Arial on Windows, DejaVu
fallback). The submitted runtime (main.py) is stdlib-only and copies the
committed entry.png, so sandbox runs need none of this.

Usage: python render.py [--out entry.png] [--preview preview-300.png]
Deterministic: fixed seeds, no clocks, no network.
"""

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
M = 24                      # page margin
GAP = 16                    # gap between lead panels
SGAP = 14                   # gap between supporting panels

INK = (34, 37, 42)
CREAM = (247, 242, 230)
CARD = (252, 249, 240)
RED = (179, 56, 44)
BLUE = (46, 94, 140)
GOLD = (217, 164, 65)
GREEN = (76, 122, 76)
GRAY = (138, 133, 120)
RULE = (90, 86, 76)

FONT_DIR = Path("C:/Windows/Fonts")
_FONT_CACHE = {}
TEXT_BOXES = []             # (x0, y0, x1, y1, label) for overlap checks


def font(kind, size):
    key = (kind, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    candidates = {
        "serifb": ["georgiab.ttf", "timesbd.ttf", "DejaVuSerif-Bold.ttf"],
        "serif": ["georgia.ttf", "times.ttf", "DejaVuSerif.ttf"],
        "sans": ["arial.ttf", "DejaVuSans.ttf"],
        "sansb": ["arialbd.ttf", "DejaVuSans-Bold.ttf"],
    }[kind]
    f = None
    for name in candidates:
        p = FONT_DIR / name
        if p.is_file():
            f = ImageFont.truetype(str(p), size)
            break
    if f is None:
        f = ImageFont.load_default(size)
    _FONT_CACHE[key] = f
    return f


def wrap(draw, text, f, maxw):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, text, f, fill, maxw, maxlines, lh, label, align="left"):
    lines = wrap(draw, text, f, maxw)[:maxlines]
    for i, ln in enumerate(lines):
        tw = draw.textlength(ln, font=f)
        tx = x + (maxw - tw) / 2 if align == "center" else x
        ty = y + i * lh
        draw.text((tx, ty), ln, font=f, fill=fill)
        asc, desc = f.getmetrics()
        TEXT_BOXES.append((tx, ty, tx + tw, ty + asc + desc, f"{label}:{i}"))
    return y + len(lines) * lh


def chip(draw, x, y, text, f, bg, fg, label, pad=5):
    tw = draw.textlength(text, font=f)
    asc, desc = f.getmetrics()
    h = asc + desc + 2 * pad
    draw.rounded_rectangle([x, y, x + tw + 2 * pad, y + h], radius=4, fill=bg)
    draw.text((x + pad, y + pad), text, font=f, fill=fg)
    TEXT_BOXES.append((x + pad, y + pad, x + pad + tw, y + pad + asc + desc, label))
    return x + tw + 2 * pad, y + h


def star(draw, cx, cy, r, fill, rot=-90):
    pts = []
    for i in range(10):
        ang = math.radians(rot + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def dashed_line(draw, p0, p1, fill, width=2, dash=9, gap=6):
    x0, y0 = p0
    x1, y1 = p1
    dist = math.hypot(x1 - x0, y1 - y0)
    n = int(dist // (dash + gap)) + 1
    for i in range(n):
        t0 = (i * (dash + gap)) / dist
        t1 = min((i * (dash + gap) + dash) / dist, 1.0)
        if t0 >= 1:
            break
        draw.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                   (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)], fill=fill, width=width)


# ---------------------------------------------------------------- lead art

def art_kyiv(d, x, y, w, h):
    """Night sky over Kyiv: missile trails, air-defence burst, city lights."""
    rng = random.Random(20)
    for i in range(24):                       # night-sky gradient bands
        t = i / 23
        col = tuple(int(a + (b - a) * t) for a, b in zip((14, 24, 48), (38, 56, 94)))
        d.rectangle([x, y + i * h // 24, x + w, y + (i + 1) * h // 24 + 1], fill=col)
    for _ in range(40):                       # stars
        sx, sy = x + rng.uniform(4, w - 4), y + rng.uniform(4, h * 0.55)
        d.point((sx, sy), fill=(200, 212, 235))
    base = y + h
    bx = x
    while bx < x + w - 8:                     # skyline with lit windows
        bw = min(rng.randint(26, 52), x + w - bx)
        bh = rng.randint(42, 96)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(9, 14, 30))
        for wy in range(base - bh + 7, base - 6, 11):
            for wx in range(bx + 5, bx + bw - 5, 9):
                if rng.random() < 0.30:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(244, 201, 93))
        bx += bw + rng.randint(2, 7)
    for k, (tx, ty) in enumerate([(x + 90, base - 70), (x + 205, base - 95), (x + 330, base - 55)]):
        sx, sy = x + w - 20 - k * 30, y + 8 + k * 12   # trails from upper right
        pts = [(sx + (tx - sx) * t, sy + (ty - sy) * t * t) for t in [i / 24 for i in range(25)]]
        d.line(pts, fill=(120, 60, 40), width=7)
        d.line(pts, fill=(232, 112, 58), width=3)
        d.ellipse([tx - 4, ty - 4, tx + 4, ty + 4], fill=(255, 210, 122))
    cx, cy = x + 250, y + 78                  # air-defence burst
    for a in range(0, 360, 30):
        ang = math.radians(a)
        d.line([(cx + 6 * math.cos(ang), cy + 6 * math.sin(ang)),
                (cx + 16 * math.cos(ang), cy + 16 * math.sin(ang))], fill=(159, 216, 255), width=2)
    for i, r in enumerate([13, 10, 8]):       # smoke over one block
        d.ellipse([x + 118 - r + i * 7, base - 108 - i * 13 - r,
                   x + 118 + r + i * 7, base - 108 - i * 13 + r], fill=(85, 90, 102))
    chip(d, x + 8, y + 8, "01:25  ·  KYIV", font("sansb", 13), (10, 14, 26), (240, 234, 220), "kyiv-chip")


def art_akvan(d, x, y, w, h):
    """Satellite view: cyclone spiral over the Bay of Bengal, track to coast."""
    d.rectangle([x, y, x + w, y + h], fill=(29, 78, 121))
    for i in range(5):                        # swell arcs
        d.arc([x + 40 + i * 70, y + h - 26, x + 130 + i * 70, y + h + 18], 200, 340,
              fill=(52, 104, 148), width=2)
    coast = [(x, y), (x + 150, y), (x + 122, y + 58), (x + 92, y + 118),
             (x + 62, y + 168), (x + 44, y + h), (x, y + h)]
    d.polygon(coast, fill=(107, 143, 94))
    d.line(coast[1:-1], fill=(217, 197, 139), width=3)
    cx, cy = x + 305, y + 128                 # cyclone spiral
    for i, r in enumerate(range(18, 86, 9)):
        start = 20 + i * 42
        col = (232, 238, 242) if i % 2 == 0 else (176, 196, 210)
        d.arc([cx - r, cy - r, cx + r, cy + r], start, start + 210, fill=col, width=8)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(15, 51, 85))
    lx, ly = x + 96, y + 92                   # forecast track + landfall marker
    dashed_line(d, (cx - 60, cy - 40), (lx + 10, ly + 6), (255, 214, 140), width=3)
    d.polygon([(lx, ly - 9), (lx - 8, ly + 6), (lx + 8, ly + 6)], fill=RED)
    d.text((lx - 66, ly - 26), "GOPALPUR", font=font("sansb", 12), fill=(20, 30, 20))
    TEXT_BOXES.append((lx - 66, ly - 26, lx - 66 + 62, ly - 12, "gopalpur"))
    chip(d, x + w - 150, y + 8, "LANDFALL ~ NOON", font("sansb", 13), RED, (255, 248, 240), "akvan-chip")

# ---------------------------------------------------------- supporting art

def _flag_au(d, x, y, w=46, h=30):
    d.rectangle([x, y, x + w, y + h], fill=(27, 58, 107))
    cw, ch = w * 0.42, h * 0.50               # simplified Union Jack canton
    d.rectangle([x, y, x + cw, y + ch], fill=(240, 240, 245))
    d.line([(x, y + ch / 2), (x + cw, y + ch / 2)], fill=(200, 40, 40), width=3)
    d.line([(x + cw / 2, y), (x + cw / 2, y + ch)], fill=(200, 40, 40), width=3)
    d.line([(x, y), (x + cw, y + ch)], fill=(27, 58, 107), width=2)
    d.line([(x + cw, y), (x, y + ch)], fill=(27, 58, 107), width=2)
    star(d, x + w * 0.22, y + h * 0.78, 5.5, (245, 245, 250))
    for fx, fy, r in [(0.70, 0.18, 3.4), (0.88, 0.42, 3.2), (0.68, 0.55, 3.2),
                      (0.82, 0.82, 3.4), (0.58, 0.36, 2.4)]:
        star(d, x + w * fx, y + h * fy, r, (245, 245, 250))


def _flag_cn(d, x, y, w=46, h=30):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(d, x + w * 0.20, y + h * 0.32, 6.5, (255, 222, 80))
    for fx, fy in [(0.40, 0.12), (0.48, 0.26), (0.48, 0.44), (0.40, 0.58)]:
        star(d, x + w * fx, y + h * fy, 2.3, (255, 222, 80))


def art_apec(d, x, y, w, h):
    """Bilateral meeting: two delegations at a table, AU and CN flags."""
    d.rectangle([x, y, x + w, y + h], fill=(239, 231, 210))
    d.text((x + 10, y + 8), "APEC · SHENZHEN", font=font("sansb", 12), fill=RULE)
    TEXT_BOXES.append((x + 10, y + 8, x + 122, y + 22, "apec-banner"))
    for px in (x + 34, x + w - 38):           # flag poles
        d.line([(px, y + 30), (px, y + h - 26)], fill=(110, 100, 86), width=3)
    _flag_au(d, x + 36, y + 32)
    _flag_cn(d, x + w - 84, y + 32)
    ty = y + h - 34                           # table + two seated figures
    d.ellipse([x + w / 2 - 62, ty, x + w / 2 + 62, ty + 24], fill=(138, 90, 51))
    for fx, face in [(x + w / 2 - 40, 1), (x + w / 2 + 40, -1)]:
        d.ellipse([fx - 9, ty - 40, fx + 9, ty - 22], fill=INK)
        d.pieslice([fx - 16, ty - 24, fx + 16, ty + 8], 180, 360, fill=INK)
    chip(d, x + w - 92, y + 6, "TRADE TALKS", font("sansb", 11), BLUE, (245, 248, 252), "apec-chip")


def art_children(d, x, y, w, h):
    """Pictogram: one in four children highlighted — conflict-zone record."""
    d.rectangle([x, y, x + w, y + h], fill=(253, 248, 236))
    n, pw = 4, 34
    x0 = x + (w - n * pw - (n - 1) * 12) / 2
    for i in range(n):
        cx = x0 + i * (pw + 12) + pw / 2
        col = RED if i == 1 else (110, 123, 138)
        cy = y + 46
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=col)
        d.polygon([(cx - 13, cy + 44), (cx + 13, cy + 44), (cx + 8, cy + 14),
                   (cx - 8, cy + 14)], fill=col)
    f = font("sansb", 22)
    tw = d.textlength("1 IN 4", font=f)
    d.text((x + (w - tw) / 2, y + h - 38), "1 IN 4", font=f, fill=INK)
    TEXT_BOXES.append((x + (w - tw) / 2, y + h - 38, x + (w + tw) / 2, y + h - 12, "children-1in4"))


def art_iowa(d, x, y, w, h):
    """Controlled detonation: drums, hazard mark, lead-dust plume, town."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 208))
    gy = y + h - 26
    d.rectangle([x, gy, x + w, y + h], fill=(150, 140, 116))
    for i, (hx, hw, hh) in enumerate([(x + w - 78, 26, 22), (x + w - 46, 30, 30), (x + w - 12, 22, 18)]):
        d.rectangle([hx, gy - hh, hx + hw, gy], fill=(74, 78, 86))
        d.polygon([(hx - 3, gy - hh), (hx + hw + 3, gy - hh), (hx + hw / 2, gy - hh - 12)], fill=(52, 56, 64))
    for i, r in enumerate([16, 13, 11, 9]):   # rising plume
        px = x + 58 + i * 16
        py = gy - 44 - i * 22
        col = (154, 149, 138) if i < 2 else (178, 173, 162)
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)
    for dx in (x + 26, x + 52):               # drums
        d.rectangle([dx, gy - 32, dx + 22, gy], fill=(90, 107, 90))
        d.ellipse([dx, gy - 37, dx + 22, gy - 27], fill=(112, 130, 112))
    hx, hy = x + 48, gy - 66                  # hazard diamond
    d.polygon([(hx, hy - 13), (hx + 13, hy), (hx, hy + 13), (hx - 13, hy)], fill=(232, 185, 58))
    d.text((hx - 3, hy - 8), "!", font=font("sansb", 14), fill=INK)
    TEXT_BOXES.append((hx - 3, hy - 8, hx + 5, hy + 8, "iowa-bang"))
    for i in range(0, w, 16):                 # caution stripe
        d.polygon([(x + i, y + h), (x + i + 8, y + h), (x + i + 16, y + h - 8),
                   (x + i + 8, y + h - 8)], fill=(232, 185, 58) if (i // 16) % 2 == 0 else INK)
    chip(d, x + 8, y + 8, "5 TONS · NOON", font("sansb", 12), INK, (245, 240, 228), "iowa-chip")


def art_cricket(d, x, y, w, h):
    """Basin Reserve: stumps, bat, ball and the overnight score."""
    d.rectangle([x, y, x + w, y + h], fill=(76, 122, 76))
    d.rectangle([x + w / 2 - 24, y + 18, x + w / 2 + 24, y + h - 12], fill=(196, 178, 130))
    sx = x + w / 2 - 10
    for i in range(3):                        # stumps + bails
        d.rectangle([sx + i * 8, y + 52, sx + i * 8 + 4, y + h - 22], fill=(240, 232, 210))
    d.rectangle([sx - 2, y + 48, sx + 22, y + 52], fill=(228, 214, 180))
    d.polygon([(x + 30, y + h - 20), (x + 40, y + h - 20), (x + 52, y + 66),
               (x + 44, y + 64)], fill=(217, 179, 108))          # bat blade
    d.line([(x + 48, y + 66), (x + 56, y + 40)], fill=(120, 90, 50), width=5)
    bx, by = x + w - 52, y + h - 40           # ball + seam
    d.ellipse([bx - 9, by - 9, bx + 9, by + 9], fill=(168, 44, 36))
    d.arc([bx - 6, by - 9, bx + 6, by + 9], 120, 240, fill=(240, 230, 210), width=2)
    d.rounded_rectangle([x + w - 86, y + 10, x + w - 10, y + 52], radius=4, fill=(30, 36, 48))
    d.text((x + w - 78, y + 14), "243/5", font=font("sansb", 17), fill=(245, 245, 248))
    d.text((x + w - 78, y + 35), "NZ · OVERNIGHT", font=font("sansb", 8), fill=(170, 180, 196))
    TEXT_BOXES.append((x + w - 78, y + 14, x + w - 24, y + 46, "cricket-score"))


# ------------------------------------------------------------------ layout

LEADS = [
    ("KYIV UNDER MISSILE ATTACK",
     "Russia's overnight revenge barrage for the Crimean Bridge strike", art_kyiv),
    ("CYCLONE AKVAN: LANDFALL TODAY",
     "Odisha-Andhra coast near Gopalpur around noon · ~50,000 evacuated", art_akvan),
]
SUPPORTS = [
    ("ALBANESE MEETS XI AT APEC",
     "Beef trade tops agenda after superpowers' 'peace declaration'", art_apec),
    ("WORLD CHILDREN'S DAY",
     "Record 589M children in conflict zones - 1 in 4 worldwide", art_children),
    ("IOWA: ARMY BLASTS 5 TONS",
     "Noon detonation at Middletown plant · lead-dust fear · schools shut", art_iowa),
    ("WELLINGTON TEST: DAY 2",
     "NZ 243/5 overnight · Nicholls 113* · Bumrah 3-52", art_cricket),
]


def panel(d, x, y, w, h, head, sub, art, illo_h, head_size, sub_size, tag):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=2)
    art(d, x + 10, y + 10, w - 20, illo_h)
    ty = y + 10 + illo_h + 12
    ty = text_block(d, x + 12, ty, head, font("serifb", head_size), INK,
                    w - 24, 3, head_size + 4, tag + "-head")
    ty += 4
    text_block(d, x + 12, ty, sub, font("sans", sub_size), (70, 66, 58),
               w - 24, 3, sub_size + 4, tag + "-sub")


def check_layout():
    problems = []
    for i, (a0, b0, a1, b1, la) in enumerate(TEXT_BOXES):
        if a0 < 0 or b0 < 0 or a1 > W or b1 > H:
            problems.append(f"out of canvas: {la}")
        for c0, d0, c1, d1, lb in TEXT_BOXES[i + 1:]:
            if a0 < c1 - 1 and c0 < a1 - 1 and b0 < d1 - 1 and d0 < b1 - 1:
                problems.append(f"overlap: {la} x {lb}")
    return problems


def render(out_path, preview_path=None):
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=RULE, width=2)
    text_block(d, M, 26, "WORLD NEWS · ONE IMAGE", font("sansb", 15), GRAY,
               W - 2 * M, 1, 18, "kicker", align="center")
    text_block(d, M, 48, "THE WORLD TODAY", font("serifb", 58), INK,
               W - 2 * M, 1, 66, "masthead", align="center")
    d.line([(M, 122), (W - M, 122)], fill=INK, width=3)
    d.line([(M, 127), (W - M, 127)], fill=INK, width=1)
    text_block(d, M, 136, "FRIDAY · 20 NOVEMBER 2026", font("sansb", 36), RED,
               W - 2 * M, 1, 42, "date", align="center")
    d.line([(M, 184), (W - M, 184)], fill=INK, width=2)

    lw = (W - 2 * M - GAP) // 2
    for i, (head, sub, art) in enumerate(LEADS):
        panel(d, M + i * (lw + GAP), 196, lw, 364, head, sub, art, 210, 30, 17, f"lead{i}")
    sw = (W - 2 * M - 3 * SGAP) // 4
    for i, (head, sub, art) in enumerate(SUPPORTS):
        panel(d, M + i * (sw + SGAP), 576, sw, 344, head, sub, art, 150, 23, 14, f"sup{i}")

    d.line([(M, 936), (W - M, 936)], fill=INK, width=2)
    text_block(d, M, 946, "Sources: Kyiv Independent · IMD / Down To Earth · ABC News / AAP · Save the Children (ReliefWeb) · U.S. Army / AP · AFP / RNZ",
               font("sans", 14), (70, 66, 58), W - 2 * M, 2, 18, "sources")
    text_block(d, M, 986, "Original illustration · six stories of Friday 20 November 2026 · full source list in repository SOURCES.md",
               font("sans", 13), GRAY, W - 2 * M, 1, 16, "credit")

    problems = check_layout()
    if problems:
        raise SystemExit("layout problems:\n" + "\n".join(problems))
    img.save(out_path, "PNG", optimize=True)
    if preview_path:
        img.resize((300, 300), Image.Resampling.LANCZOS).save(preview_path, "PNG")
    print(f"saved {out_path} ({Path(out_path).stat().st_size} bytes); "
          f"{len(TEXT_BOXES)} text blocks, no overlaps")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "entry.png"))
    ap.add_argument("--preview", default=None)
    args = ap.parse_args()
    render(args.out, args.preview)
