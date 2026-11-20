#!/usr/bin/env python3
"""Render an original 18-story, 20 November 2026 news front page.

Build-time only: Pillow and local system fonts. The judged runtime stays
stdlib-only and copies entry.png. Layout: three leads, five picture briefs,
ten one-line briefs. Cobalt/terracotta two-ink print on neutral white.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (250, 250, 247)
BLUE = (33, 72, 184)
ORANGE = (198, 95, 56)
FONT_DIR = Path("C:/Windows/Fonts")
FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}
TEXT_BOXES: list[tuple[int, int, int, int, str]] = []


def screened(ink: tuple[int, int, int], coverage: float) -> tuple[int, int, int]:
    """Mix one assigned ink with paper; this is ink density, not a new ink."""
    return tuple(round(PAPER[i] + (ink[i] - PAPER[i]) * coverage) for i in range(3))


def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    key = (role, size)
    if key not in FONT_CACHE:
        choices = {
            "display": ["georgiab.ttf", "timesbd.ttf", "arialbd.ttf"],
            "serif": ["georgia.ttf", "times.ttf", "arial.ttf"],
            "sans": ["arial.ttf", "calibri.ttf", "tahoma.ttf"],
            "bold": ["arialbd.ttf", "calibrib.ttf", "tahomabd.ttf"],
            "mono": ["consolab.ttf", "consola.ttf"],
        }[role]
        for filename in choices:
            path = FONT_DIR / filename
            if path.is_file():
                FONT_CACHE[key] = ImageFont.truetype(str(path), size)
                break
        else:
            FONT_CACHE[key] = ImageFont.load_default(size=size)
    return FONT_CACHE[key]


def ink_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
             face: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
             tag: str, track: bool = True) -> tuple[int, int, int, int]:
    x, y = xy
    box = draw.textbbox((x, y), text, font=face)
    draw.text((x, y), text, font=face, fill=fill)
    if track:
        TEXT_BOXES.append((box[0], box[1], box[2], box[3], tag))
    return box


def wrap_words(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont,
               max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for word in paragraph.split():
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=face) <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def paragraph(draw: ImageDraw.ImageDraw, x: int, y: int, text: str,
              face: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
              max_width: int, line_gap: int, tag: str,
              max_lines: int | None = None) -> int:
    lines = wrap_words(draw, text, face, max_width)
    if max_lines is not None and len(lines) > max_lines:
        raise ValueError(f"{tag}: {len(lines)} lines exceed limit {max_lines}: {lines}")
    asc, desc = face.getmetrics()
    line_height = asc + desc + line_gap
    for i, line in enumerate(lines):
        if line:
            if draw.textlength(line, font=face) > max_width + 1:
                raise ValueError(f"{tag}: measured line exceeds its column: {line}")
            ink_text(draw, (x, y + i * line_height), line, face, fill, f"{tag}:{i}")
    return y + len(lines) * line_height


def fit_line(draw: ImageDraw.ImageDraw, text: str, x: int, y: int,
             max_width: int, max_size: int, min_size: int,
             fill: tuple[int, int, int], tag: str) -> int:
    for size in range(max_size, min_size - 1, -1):
        face = font("bold", size)
        if draw.textlength(text, font=face) <= max_width:
            ink_text(draw, (x, y), text, face, fill, tag)
            return size
    raise ValueError(f"{tag}: brief cannot fit even at {min_size}px: {text}")


def rule(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int],
         fill: tuple[int, int, int] = BLUE, width: int = 1) -> None:
    draw.line(xy, fill=fill, width=width)


def halftone(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int,
             ink: tuple[int, int, int], spacing: int = 8, radius: int = 1) -> None:
    for yy in range(y + 5, y + h - 3, spacing):
        for xx in range(x + 5, x + w - 3, spacing):
            draw.ellipse((xx - radius, yy - radius, xx + radius, yy + radius), fill=ink)


def thumb_frame(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int,
                wash: tuple[int, int, int]) -> None:
    draw.rectangle((x, y, x + w, y + h), fill=wash)
    rule(draw, (x, y, x + w, y), BLUE, 2)


def draw_bridge_city(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rectangle((x, y, x + 142, y + 132), fill=screened(BLUE, .10))
    for bx, bw, bh in ((x + 8, 22, 43), (x + 34, 19, 67), (x + 57, 26, 52),
                       (x + 88, 19, 76), (x + 111, 22, 46)):
        draw.rectangle((bx, y + 99 - bh, bx + bw, y + 99), fill=BLUE)
        for wx in range(bx + 5, bx + bw - 2, 8):
            draw.rectangle((wx, y + 99 - bh + 9, wx + 2, y + 99 - bh + 15), fill=PAPER)
    draw.rectangle((x, y + 101, x + 142, y + 132), fill=screened(BLUE, .18))
    for sx, ex in ((x + 6, x + 45), (x + 53, x + 91), (x + 99, x + 136)):
        rule(draw, (sx, y + 100, ex, y + 100), ORANGE, 4)
        for cx in range(sx + 5, ex, 13):
            draw.arc((cx - 6, y + 99, cx + 6, y + 122), 180, 360, fill=BLUE, width=2)
    rule(draw, (x + 45, y + 100, x + 51, y + 100), PAPER, 5)
    halftone(draw, x + 7, y + 9, 44, 24, ORANGE, 9, 1)


def draw_poland_airspace(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rectangle((x, y, x + 104, y + 85), fill=screened(BLUE, .08))
    rule(draw, (x + 10, y + 60, x + 95, y + 60), BLUE, 2)
    ink_text(draw, (x + 12, y + 63), "PL", font("mono", 12), BLUE, "pl-icon", False)
    ink_text(draw, (x + 70, y + 63), "UA", font("mono", 12), BLUE, "ua-icon", False)
    for xx, yy, color in ((x + 35, y + 26, ORANGE), (x + 57, y + 35, BLUE)):
        draw.polygon(((xx, yy - 9), (xx + 4, yy + 2), (xx, yy + 8), (xx - 4, yy + 2)), fill=color)
        rule(draw, (xx, yy + 8, xx, y + 50), color, 2)
    draw.ellipse((x + 76, y + 18, x + 88, y + 30), outline=ORANGE, width=2)
    rule(draw, (x + 82, y + 30, x + 82, y + 45), ORANGE, 2)
    draw.arc((x + 67, y + 8, x + 96, y + 37), 205, 335, fill=ORANGE, width=1)


def draw_trade_icon(draw: ImageDraw.ImageDraw, x: int, y: int) -> None:
    draw.rectangle((x, y, x + 104, y + 85), fill=screened(ORANGE, .12))
    draw.rectangle((x + 8, y + 34, x + 31, y + 58), outline=BLUE, width=2)
    rule(draw, (x + 8, y + 34, x + 31, y + 34), ORANGE, 3)
    draw.ellipse((x + 15, y + 16, x + 24, y + 25), fill=ORANGE)
    rule(draw, (x + 19, y + 25, x + 19, y + 34), BLUE, 2)
    rule(draw, (x + 39, y + 46, x + 65, y + 46), BLUE, 3)
    draw.polygon(((x + 65, y + 42), (x + 73, y + 46), (x + 65, y + 50)), fill=BLUE)
    draw.polygon(((x + 39, y + 42), (x + 31, y + 46), (x + 39, y + 50)), fill=ORANGE)
    draw.ellipse((x + 82, y + 22, x + 94, y + 34), outline=BLUE, width=2)
    draw.arc((x + 77, y + 32, x + 99, y + 62), 180, 360, fill=ORANGE, width=3)
    rule(draw, (x + 76, y + 64, x + 99, y + 64), BLUE, 2)


def draw_thumb_cyclone(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    thumb_frame(draw, x, y, w, h, screened(BLUE, .08))
    draw.polygon(((x, y), (x + 39, y), (x + 35, y + 19), (x + 27, y + 36),
                  (x + 20, y + 57), (x + 13, y + h), (x, y + h)), fill=PAPER)
    for a, b in (((39, 0), (35, 19)), ((35, 19), (27, 36)), ((27, 36), (20, 57))):
        rule(draw, (x + a[0], y + a[1], x + b[0], y + b[1]), ORANGE, 2)
    cx, cy = x + 75, y + 42
    for r in (10, 18, 26):
        draw.arc((cx - r, cy - r, cx + r, cy + r), 25, 320, fill=BLUE, width=3)
    draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=ORANGE)
    rule(draw, (x + 57, y + 44, x + 40, y + 44), ORANGE, 2)
    draw.ellipse((x + 36, y + 41, x + 42, y + 47), fill=ORANGE)
    halftone(draw, x + 48, y + 9, 50, 15, BLUE, 7, 1)


def draw_thumb_cop(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    thumb_frame(draw, x, y, w, h, screened(ORANGE, .10))
    draw.ellipse((x + 23, y + 31, x + 92, y + 68), outline=BLUE, width=3)
    for px in (x + 29, x + 72):
        draw.ellipse((px, y + 12, px + 13, y + 25), fill=ORANGE)
        draw.arc((px - 4, y + 19, px + 17, y + 47), 180, 360, fill=BLUE, width=3)
    draw.rectangle((x + 51, y + 12, x + 66, y + 31), fill=PAPER, outline=BLUE, width=2)
    rule(draw, (x + 54, y + 20, x + 63, y + 20), ORANGE, 2)
    rule(draw, (x + 50, y + 70, x + 68, y + 70), ORANGE, 2)
    halftone(draw, x + 8, y + 7, 28, 17, BLUE, 7, 1)


def draw_thumb_apec(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    thumb_frame(draw, x, y, w, h, screened(BLUE, .07))
    draw.ellipse((x + 19, y + 22, x + 34, y + 37), fill=BLUE)
    draw.ellipse((x + 78, y + 22, x + 93, y + 37), fill=ORANGE)
    draw.arc((x + 14, y + 31, x + 40, y + 61), 180, 360, fill=BLUE, width=4)
    draw.arc((x + 73, y + 31, x + 99, y + 61), 180, 360, fill=ORANGE, width=4)
    draw.ellipse((x + 30, y + 44, x + 82, y + 62), fill=screened(ORANGE, .35), outline=BLUE, width=2)
    ink_text(draw, (x + 8, y + 64), "AUS", font("mono", 10), BLUE, "aus-icon", False)
    ink_text(draw, (x + 80, y + 64), "CHN", font("mono", 10), ORANGE, "chn-icon", False)
    halftone(draw, x + 73, y + 8, 29, 15, ORANGE, 7, 1)


def draw_thumb_children(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    thumb_frame(draw, x, y, w, h, screened(BLUE, .08))
    draw.polygon(((x + 9, y + 35), (x + 45, y + 9), (x + 81, y + 35)), fill=ORANGE)
    draw.rectangle((x + 16, y + 34, x + 74, y + 65), fill=PAPER, outline=BLUE, width=2)
    for px in (x + 28, x + 44, x + 60):
        draw.ellipse((px - 4, y + 40, px + 4, y + 48), fill=BLUE)
        draw.rectangle((px - 3, y + 49, px + 3, y + 59), fill=BLUE)
    ink_text(draw, (x + 15, y + 65), "1,144", font("bold", 11), ORANGE, "child-total-icon", False)
    rule(draw, (x + 88, y + 20, x + 88, y + 62), ORANGE, 2)
    halftone(draw, x + 82, y + 8, 23, 14, BLUE, 7, 1)


def draw_thumb_gulf(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int) -> None:
    thumb_frame(draw, x, y, w, h, screened(ORANGE, .09))
    # Abstract coastline, one inbound object, and a shield/intercept arc.
    draw.polygon(((x, y + 8), (x + 27, y + 13), (x + 39, y + 26),
                  (x + 31, y + 40), (x + 42, y + 57), (x + 29, y + h),
                  (x, y + h)), fill=PAPER)
    rule(draw, (x + 28, y + 13, x + 40, y + 26), BLUE, 2)
    rule(draw, (x + 40, y + 26, x + 32, y + 40), BLUE, 2)
    draw.polygon(((x + 76, y + 12), (x + 81, y + 26), (x + 76, y + 32),
                  (x + 71, y + 26)), fill=ORANGE)
    rule(draw, (x + 76, y + 31, x + 76, y + 50), ORANGE, 2)
    draw.arc((x + 49, y + 27, x + 101, y + 76), 204, 332, fill=BLUE, width=3)
    draw.ellipse((x + 67, y + 47, x + 85, y + 65), outline=ORANGE, width=2)
    halftone(draw, x + 5, y + 7, 25, 14, BLUE, 7, 1)


def draw_header(draw: ImageDraw.ImageDraw) -> None:
    ink_text(draw, (32, 16), "WORLD NEWS", font("display", 46), BLUE, "masthead")
    ink_text(draw, (34, 67), "FRIDAY  /  20 NOVEMBER 2026", font("bold", 15), ORANGE, "date")
    ink_text(draw, (647, 28), "3 LEADS  ·  5 PICTURE BRIEFS", font("mono", 14), BLUE, "edition-top")
    ink_text(draw, (647, 53), "10 MORE STORIES  ·  6 REGIONS", font("mono", 13), ORANGE, "edition-bottom")
    rule(draw, (32, 96, 992, 96), BLUE, 3)
    rule(draw, (32, 101, 992, 101), ORANGE, 1)
    rule(draw, (34, 107, 206, 109), ORANGE, 2)


def draw_leads(draw: ImageDraw.ImageDraw) -> None:
    x, y, w, h = 32, 122, 472, 252
    rule(draw, (x, y, x + w, y), ORANGE, 4)
    ink_text(draw, (x + 16, y + 10), "01  /  EAST EUROPE", font("mono", 12), ORANGE, "lead-1-kicker")
    paragraph(draw, x + 16, y + 34, "8 KILLED\nIN UKRAINE", font("display", 38), BLUE,
              272, 0, "lead-1-head", 2)
    paragraph(draw, x + 16, y + 132,
              "Russia's overnight attack killed eight; three Kyiv bridges were hit.",
              font("sans", 17), BLUE, 280, 2, "lead-1-deck", 3)
    draw_bridge_city(draw, x + 318, y + 59)
    ink_text(draw, (x + 17, y + 218), "8 KILLED  ·  POWER INFRASTRUCTURE HIT", font("mono", 11), ORANGE, "lead-1-stat")
    rule(draw, (x, y + h, x + w, y + h), BLUE, 1)

    rx, rw = 528, 464
    y2, h2 = 122, 122
    rule(draw, (rx, y2, rx + rw, y2), BLUE, 3)
    ink_text(draw, (rx + 14, y2 + 8), "02  /  POLAND", font("mono", 11), ORANGE, "lead-2-kicker")
    paragraph(draw, rx + 14, y2 + 27, "MISSILES IN POLAND", font("display", 27), BLUE,
              333, 0, "lead-2-head", 2)
    paragraph(draw, rx + 14, y2 + 83, "Two missiles + suspected drone; Tusk says likely provocation.",
              font("sans", 14), BLUE, 335, 1, "lead-2-deck", 2)
    draw_poland_airspace(draw, rx + 354, y2 + 20)
    rule(draw, (rx, y2 + h2, rx + rw, y2 + h2), BLUE, 1)

    y3, h3 = 252, 122
    rule(draw, (rx, y3, rx + rw, y3), ORANGE, 3)
    ink_text(draw, (rx + 14, y3 + 8), "03  /  EUROPE", font("mono", 11), ORANGE, "lead-3-kicker")
    paragraph(draw, rx + 14, y3 + 27, "UK–EU AGREE THREE DEALS", font("display", 27), BLUE,
              333, 0, "lead-3-head", 2)
    paragraph(draw, rx + 14, y3 + 83, "Food trade · carbon-market link · youth mobility.",
              font("sans", 14), BLUE, 335, 1, "lead-3-deck", 2)
    draw_trade_icon(draw, rx + 354, y3 + 20)
    rule(draw, (rx, y3 + h3, rx + rw, y3 + h3), BLUE, 1)


def draw_picture_briefs(draw: ImageDraw.ImageDraw) -> None:
    x, colw = 32, 464
    ink_text(draw, (x, 394), "IN PICTURES  /  5", font("mono", 13), ORANGE, "pictures-heading")
    rule(draw, (x, 416, x + colw, 416), BLUE, 2)
    entries = [
        ("AKVAN CROSSES ODISHA", "372K evacuated; no casualties reported by publication.", draw_thumb_cyclone),
        ("COP31 DRAFT CLASH", "Fossil-fuel wording absent; countries demand stronger text.", draw_thumb_cop),
        ("XI–ALBANESE AT APEC", "Xi says Australia–China ties made a “full turnaround.”", draw_thumb_apec),
        ("UKRAINE'S CHILDREN", "1,144 killed or injured in Jan–Oct, UNICEF says.", draw_thumb_children),
        ("SAUDI–HOUTHI EXCHANGE", "Coalition reports five drones and one missile intercepted.", draw_thumb_gulf),
    ]
    row_h = 107
    for i, (title, body, art) in enumerate(entries):
        y = 422 + i * row_h
        art(draw, x + 2, y + 10, 118, 82)
        paragraph(draw, x + 134, y + 10, title, font("bold", 16), BLUE,
                  324, 1, f"thumb-{i+1}-head", 2)
        paragraph(draw, x + 134, y + 38, body, font("sans", 13), BLUE,
                  324, 1, f"thumb-{i+1}-deck", 3)
        if i < len(entries) - 1:
            rule(draw, (x, y + row_h - 1, x + colw, y + row_h - 1), screened(BLUE, .55), 1)


def draw_text_briefs(draw: ImageDraw.ImageDraw) -> None:
    x, colw = 520, 472
    ink_text(draw, (x, 394), "ALSO TODAY  /  10 BRIEFS", font("mono", 13), ORANGE, "briefs-heading")
    rule(draw, (x, 416, x + colw, 416), BLUE, 2)
    entries = [
        "Myanmar calls ICJ Rohingya ruling “unfair.”",
        "South Korea's first cholera case since 2016.",
        "AI sell-off: Nikkei −5.1%, Kospi −5.2%.",
        "Italy strike hits 100+ cities; schools and transit hit.",
        "AP: families allege guards pocketed detainee funds.",
        "Fiona the Cincinnati hippo dies at age 9.",
        "Mamdani plan: close Rikers by 2032.",
        "Nations League: Spain–France; Norway–England.",
        "NZ 368; India 159/1 at Day Two stumps.",
        "El Salvador's Bukele launches third-term bid.",
    ]
    tags = ("MYA", "KOR", "MKT", "ITA", "SUD", "US", "NYC", "UEFA", "NZ·IN", "SAL")
    row_h = 54
    for i, (title, tag) in enumerate(zip(entries, tags)):
        y = 422 + i * row_h
        ink_text(draw, (x + 1, y + 10), f"{i+9:02d}", font("mono", 12), ORANGE, f"brief-{i+9}-number")
        ink_text(draw, (x + 36, y + 10), tag, font("mono", 10), ORANGE, f"brief-{i+9}-tag")
        fit_line(draw, title, x + 95, y + 8, colw - 98, 17, 14, BLUE, f"brief-{i+9}-text")
        if i < len(entries) - 1:
            rule(draw, (x, y + row_h - 1, x + colw, y + row_h - 1), screened(BLUE, .55), 1)


def check_layout() -> None:
    issues: list[str] = []
    for i, (x0, y0, x1, y1, label) in enumerate(TEXT_BOXES):
        if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
            issues.append(f"out of canvas: {label} {(x0, y0, x1, y1)}")
        for a0, b0, a1, b1, other in TEXT_BOXES[i + 1:]:
            if x0 < a1 - 1 and a0 < x1 - 1 and y0 < b1 - 1 and b0 < y1 - 1:
                issues.append(f"text overlap: {label} / {other}")
    if issues:
        raise ValueError("layout validation failed:\n" + "\n".join(issues))


def render(out_path: Path, preview_path: Path | None = None) -> dict[str, object]:
    TEXT_BOXES.clear()
    image = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(image)
    draw_header(draw)
    draw_leads(draw)
    draw_picture_briefs(draw)
    draw_text_briefs(draw)
    rule(draw, (32, 964, 992, 964), BLUE, 2)
    ink_text(draw, (32, 972), "FRIDAY  ·  20 NOVEMBER 2026", font("mono", 11), BLUE, "footer-date")
    ink_text(draw, (619, 972), "18 STORIES  /  SOURCES IN NEWS.MD", font("mono", 11), ORANGE, "footer-sources")
    check_layout()
    image.save(out_path, "PNG", optimize=True)
    if preview_path:
        image.resize((300, 300), Image.Resampling.LANCZOS).save(preview_path, "PNG", optimize=True)
    data = out_path.read_bytes()
    return {"path": str(out_path), "width": W, "height": H, "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(), "text_boxes": len(TEXT_BOXES),
            "layout": "3 leads + 5 illustrated briefs + 10 text briefs"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(Path(__file__).resolve().parent / "entry.png"))
    parser.add_argument("--preview", default=None)
    args = parser.parse_args()
    result = render(Path(args.out), Path(args.preview) if args.preview else None)
    print("; ".join(f"{key}={value}" for key, value in result.items()))
