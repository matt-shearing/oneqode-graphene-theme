#!/usr/bin/env python3
"""
OneQode icon forge.

Generates a cohesive, line-style icon set in the OneQode design language:

  * Colour icons  -> complete square PNGs (dark "glass" tile + duotone glyph),
                     written to res/drawable-xxxhdpi/<name>.png  (referenced by
                     appfilter.xml). Launchers mask/round as needed.
  * Themed icons  -> monochrome Android VectorDrawables (white silhouette on
                     transparent), written to res/drawable/<name>_mono.xml and
                     mapped per-package in grayscale_icon_map.xml. The system
                     tints these via Material You, so they follow the OneQode
                     accent and day/night automatically.

Glyphs are universal category marks (phone, browser, mail, camera, …) drawn from
simple geometry — no third-party brand logos are reproduced. appfilter.py maps
real app components onto these glyphs.

Dependencies: rsvg-convert (librsvg), Pillow.
"""
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
PACK = HERE.parent  # iconpack/
RES = PACK / "app" / "src" / "main" / "res"
DRAW_XXX = RES / "drawable-xxxhdpi"
DRAW_VEC = RES / "drawable"

# OneQode palette (Night-Ride-flavoured colour set; themed mode handles light)
TILE_A = "#242d42"   # tile gradient top-left
TILE_B = "#11131d"   # tile gradient bottom-right
EDGE   = "#00c8ff"   # faint glass edge
CYAN   = "#34d6ff"   # primary glyph stroke
PINK   = "#ff4d9d"   # accent
GREEN  = "#5dffc0"   # secondary accent
INK    = "#dfeefc"   # near-white glyph detail

CANVAS = 108         # dp
PNG_PX = 432         # xxxhdpi (108dp * 4)

# ---------------------------------------------------------------------------
# tiny SVG builder
class S:
    def __init__(self, mono=False):
        self.mono = mono
        self.parts = []
        # palette resolves to white in mono mode
        self.cyan = "#ffffff" if mono else CYAN
        self.pink = "#ffffff" if mono else PINK
        self.green = "#ffffff" if mono else GREEN
        self.ink = "#ffffff" if mono else INK

    def line(self, x1, y1, x2, y2, w=7, c=None, cap="round"):
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{c or self.cyan}" stroke-width="{w}" stroke-linecap="{cap}"/>')

    def circ(self, cx, cy, r, w=7, c=None, fill="none"):
        self.parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{c or self.cyan}" stroke-width="{w}"/>')

    def dot(self, cx, cy, r, c=None):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c or self.cyan}"/>')

    def rrect(self, x, y, w_, h_, r=8, sw=7, c=None, fill="none"):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" rx="{r}" ry="{r}" '
            f'fill="{fill}" stroke="{c or self.cyan}" stroke-width="{sw}"/>')

    def path(self, d, w=7, c=None, fill="none", cap="round", join="round"):
        self.parts.append(
            f'<path d="{d}" fill="{fill}" stroke="{c or self.cyan}" '
            f'stroke-width="{w}" stroke-linecap="{cap}" stroke-linejoin="{join}"/>')

    def fpath(self, d, c=None):
        self.parts.append(f'<path d="{d}" fill="{c or self.cyan}"/>')

    def poly(self, pts, w=7, c=None, fill="none"):
        p = " ".join(f"{x},{y}" for x, y in pts)
        self.parts.append(
            f'<polyline points="{p}" fill="{fill}" stroke="{c or self.cyan}" '
            f'stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')

    def body(self):
        return "\n".join(self.parts)


# ---------------------------------------------------------------------------
# Glyphs. Each fn(s) draws into S, centred in the 108 canvas (safe ~24..84).
def g_phone(s):
    s.path("M36 30 q-8 0 -8 8 q0 40 42 42 q8 0 8 -8 l0 -10 l-14 -6 l-6 8 "
           "q-16 -8 -22 -22 l8 -6 l-6 -14 z", w=7, c=s.cyan)

def g_messages(s):
    s.path("M28 36 q0 -8 8 -8 l36 0 q8 0 8 8 l0 22 q0 8 -8 8 l-30 0 l-14 12 l0 -42 z", c=s.cyan)
    s.dot(44, 47, 3, s.pink); s.dot(54, 47, 3, s.cyan); s.dot(64, 47, 3, s.pink)

def g_contacts(s):
    s.circ(54, 44, 12, c=s.cyan)
    s.path("M32 78 q0 -16 22 -16 q22 0 22 16", c=s.cyan)

def g_dialer(s):
    g_phone(s); s.dot(70, 34, 4, s.pink)

def g_camera(s):
    s.rrect(26, 38, 56, 38, r=8, c=s.cyan)
    s.path("M44 38 l4 -8 l12 0 l4 8", c=s.cyan)
    s.circ(54, 57, 11, c=s.pink)

def g_photos(s):
    s.rrect(28, 30, 52, 52, r=10, c=s.cyan)
    s.poly([(34, 72), (50, 54), (60, 64), (68, 56), (76, 72)], c=s.green)
    s.dot(42, 44, 5, s.pink)

def g_clock(s):
    s.circ(54, 54, 26, c=s.cyan)
    s.line(54, 54, 54, 38, w=6, c=s.ink); s.line(54, 54, 66, 60, w=6, c=s.pink)

def g_alarm(s):
    s.circ(54, 56, 22, c=s.cyan)
    s.line(54, 56, 54, 44, w=6, c=s.ink); s.line(54, 56, 64, 56, w=6, c=s.pink)
    s.line(34, 34, 42, 42, w=6, c=s.cyan); s.line(74, 34, 66, 42, w=6, c=s.cyan)

def g_calc(s):
    s.rrect(32, 26, 44, 56, r=8, c=s.cyan)
    s.rrect(40, 34, 28, 12, r=3, c=s.green)
    for i in range(3):
        for j in range(3):
            s.dot(44 + j*10, 58 + i*8, 2.6, s.pink if (i+j) % 2 else s.cyan)

def g_calendar(s):
    s.rrect(28, 32, 52, 48, r=8, c=s.cyan)
    s.line(28, 46, 80, 46, w=6, c=s.cyan)
    s.line(40, 26, 40, 38, w=6, c=s.pink); s.line(68, 26, 68, 38, w=6, c=s.pink)
    s.dot(46, 60, 3.4, s.green); s.dot(62, 60, 3.4, s.cyan); s.dot(46, 70, 3.4, s.cyan)

def g_settings(s):
    # gear: outer ring + teeth + center
    s.circ(54, 54, 14, c=s.cyan)
    s.dot(54, 54, 5, s.pink)
    for k in range(8):
        a = k * math.pi / 4
        x1 = 54 + 20*math.cos(a); y1 = 54 + 20*math.sin(a)
        x2 = 54 + 27*math.cos(a); y2 = 54 + 27*math.sin(a)
        s.line(x1, y1, x2, y2, w=6, c=s.cyan)

def g_files(s):
    s.path("M28 40 q0 -6 6 -6 l14 0 l6 8 l22 0 q6 0 6 6 l0 26 q0 6 -6 6 l-42 0 q-6 0 -6 -6 z", c=s.cyan)
    s.line(38, 58, 70, 58, w=5, c=s.pink)

def g_downloads(s):
    s.line(54, 30, 54, 62, w=7, c=s.cyan)
    s.poly([(42, 50), (54, 64), (66, 50)], c=s.pink)
    s.line(34, 76, 74, 76, w=7, c=s.green)

def g_browser(s):
    s.circ(54, 54, 26, c=s.cyan)
    s.path("M28 54 h52 M54 28 q14 12 0 52 q-14 -40 0 -52", w=5, c=s.green)
    s.dot(54, 54, 4, s.pink)

def g_mail(s):
    s.rrect(26, 36, 56, 38, r=8, c=s.cyan)
    s.poly([(28, 40), (54, 60), (80, 40)], w=6, c=s.pink)

def g_music(s):
    s.path("M44 70 a8 6 0 1 0 0.1 0 M44 70 l0 -34 l26 -6 l0 30", c=s.cyan)
    s.path("M70 60 a8 6 0 1 0 0.1 0", c=s.pink)

def g_video(s):
    s.rrect(26, 36, 56, 38, r=8, c=s.cyan)
    s.fpath("M48 48 l16 9 l-16 9 z", c=s.pink)

def g_play(s):
    s.circ(54, 54, 26, c=s.cyan)
    s.fpath("M47 42 l20 12 l-20 12 z", c=s.pink)

def g_maps(s):
    s.path("M54 30 q-16 0 -16 16 q0 14 16 32 q16 -18 16 -32 q0 -16 -16 -16 z", c=s.cyan)
    s.dot(54, 46, 6, s.pink)

def g_store(s):
    s.path("M34 42 l4 -10 l32 0 l4 10 M32 42 l4 36 l36 0 l4 -36 z", c=s.cyan)
    s.path("M46 42 q0 12 8 12 q8 0 8 -12", w=5, c=s.pink)

def g_weather(s):
    s.circ(46, 46, 10, c=s.pink)
    s.path("M44 70 q-14 0 -14 -12 q0 -12 14 -12 q2 -12 16 -10 q14 2 12 16 q10 0 10 10 q0 8 -10 8 z", c=s.cyan)

def g_notes(s):
    s.rrect(32, 28, 44, 54, r=6, c=s.cyan)
    s.line(42, 44, 66, 44, w=5, c=s.pink)
    s.line(42, 56, 66, 56, w=5, c=s.cyan); s.line(42, 68, 56, 68, w=5, c=s.cyan)

def g_mic(s):
    s.rrect(46, 28, 16, 30, r=8, c=s.cyan, fill="none")
    s.path("M36 54 q0 18 18 18 q18 0 18 -18", w=6, c=s.pink)
    s.line(54, 72, 54, 82, w=6, c=s.cyan)

def g_search(s):
    s.circ(48, 48, 16, c=s.cyan)
    s.line(60, 60, 74, 74, w=8, c=s.pink)

def g_wallet(s):
    s.rrect(28, 38, 52, 34, r=8, c=s.cyan)
    s.line(28, 50, 80, 50, w=6, c=s.pink)
    s.dot(70, 61, 4, s.green)

def g_bank(s):
    s.poly([(30, 46), (54, 32), (78, 46)], c=s.cyan)
    for x in (40, 54, 68):
        s.line(x, 50, x, 70, w=6, c=s.cyan)
    s.line(30, 74, 78, 74, w=6, c=s.pink)

def g_chat(s):
    s.path("M28 36 q0 -8 8 -8 l36 0 q8 0 8 8 l0 22 q0 8 -8 8 l-30 0 l-14 12 l0 -42 z", c=s.cyan)

def g_secure_chat(s):
    g_chat(s)
    s.rrect(46, 42, 16, 14, r=3, c=s.pink)
    s.path("M49 42 q0 -6 5 -6 q5 0 5 6", w=4, c=s.pink)

def g_social(s):
    s.circ(44, 46, 9, c=s.cyan); s.path("M28 72 q0 -12 16 -12 q16 0 16 12", w=6, c=s.cyan)
    s.circ(68, 42, 7, c=s.pink); s.path("M58 64 q4 -8 14 -8 q12 0 12 12", w=5, c=s.pink)

def g_bird(s):
    s.fpath("M34 64 q22 6 36 -10 q6 -2 8 -8 q-4 1 -8 0 q4 -3 5 -8 q-5 3 -9 3 "
            "q-6 -7 -15 -3 q-8 4 -6 14 q-12 0 -20 -8 q-3 9 4 16 q-4 0 -6 -2 "
            "q0 8 10 11 z", c=s.cyan)

def g_book(s):
    s.path("M30 34 q12 -4 24 0 l0 44 q-12 -4 -24 0 z", c=s.cyan)
    s.path("M78 34 q-12 -4 -24 0 l0 44 q12 -4 24 0 z", c=s.pink)

def g_doc(s):
    s.path("M36 28 l24 0 l16 16 l0 36 q0 0 0 0 l-40 0 z", c=s.cyan)
    s.poly([(60, 28), (60, 44), (76, 44)], w=5, c=s.pink)
    s.line(44, 56, 68, 56, w=5, c=s.cyan); s.line(44, 66, 68, 66, w=5, c=s.cyan)

def g_sheet(s):
    s.rrect(30, 30, 48, 48, r=6, c=s.cyan)
    s.line(30, 46, 78, 46, w=5, c=s.green); s.line(54, 30, 54, 78, w=5, c=s.green)
    s.dot(42, 38, 2.5, s.pink)

def g_slides(s):
    s.rrect(28, 34, 52, 36, r=6, c=s.cyan)
    s.poly([(40, 60), (40, 46), (52, 46)], w=5, c=s.pink)
    s.line(54, 76, 54, 70, w=6, c=s.cyan)

def g_pdf(s):
    g_doc(s); s.fpath("M44 70 l0 8 m0 -8 l18 0 l0 8", c=s.pink)

def g_terminal(s):
    s.rrect(26, 32, 56, 44, r=8, c=s.cyan)
    s.poly([(36, 48), (46, 56), (36, 64)], w=6, c=s.green)
    s.line(52, 64, 68, 64, w=6, c=s.pink)

def g_code(s):
    s.poly([(44, 40), (30, 54), (44, 68)], w=7, c=s.cyan)
    s.poly([(64, 40), (78, 54), (64, 68)], w=7, c=s.pink)
    s.line(58, 36, 50, 72, w=6, c=s.green)

def g_git(s):
    s.line(40, 36, 40, 72, w=7, c=s.cyan)
    s.dot(40, 34, 6, s.cyan); s.dot(40, 74, 6, s.cyan); s.dot(68, 50, 6, s.pink)
    s.path("M40 50 q0 0 28 0", w=6, c=s.pink)

def g_cloud(s):
    s.path("M40 70 q-14 0 -14 -12 q0 -12 14 -12 q2 -12 16 -10 q14 2 12 16 q10 0 10 10 q0 8 -10 8 z", c=s.cyan)
    s.dot(54, 58, 3, s.pink)

def g_vpn(s):
    s.path("M54 28 l22 8 l0 22 q0 18 -22 26 q-22 -8 -22 -26 l0 -22 z", c=s.cyan)
    s.poly([(46, 54), (52, 60), (64, 46)], w=6, c=s.green)

def g_key(s):
    s.circ(42, 46, 12, c=s.cyan)
    s.line(50, 54, 74, 78, w=7, c=s.pink); s.line(66, 70, 72, 64, w=7, c=s.pink)

def g_auth(s):
    s.circ(54, 54, 24, c=s.cyan)
    s.line(54, 54, 54, 40, w=6, c=s.ink); s.line(54, 54, 64, 60, w=6, c=s.pink)
    s.dot(54, 54, 3.5, s.green)

def g_fitness(s):
    s.path("M54 74 q-26 -16 -26 -34 q0 -12 13 -12 q9 0 13 10 q4 -10 13 -10 q13 0 13 12 q0 18 -26 34 z", c=s.pink)

def g_podcast(s):
    s.circ(54, 44, 10, c=s.cyan)
    s.path("M38 60 q0 -10 16 -10 q16 0 16 10", w=6, c=s.cyan)
    s.line(54, 60, 54, 80, w=6, c=s.pink); s.dot(54, 80, 3, s.pink)

def g_news(s):
    s.rrect(28, 32, 52, 44, r=6, c=s.cyan)
    s.line(36, 42, 56, 42, w=5, c=s.pink)
    s.line(36, 54, 72, 54, w=4, c=s.cyan); s.line(36, 62, 72, 62, w=4, c=s.cyan)

def g_translate(s):
    s.path("M30 40 l18 0 M39 36 l0 4 M39 40 q0 14 -9 20 M33 48 q10 8 14 8", w=5, c=s.cyan)
    s.path("M58 76 l10 -26 l10 26 M61 68 l14 0", w=5, c=s.pink)

def g_qr(s):
    for (x, y) in [(30, 30), (62, 30), (30, 62)]:
        s.rrect(x, y, 16, 16, r=3, sw=5, c=s.cyan)
    s.dot(66, 66, 3, s.pink); s.dot(76, 66, 3, s.pink); s.dot(66, 76, 3, s.pink)

def g_compass(s):
    s.circ(54, 54, 26, c=s.cyan)
    s.fpath("M54 38 l8 16 l-8 16 l-8 -16 z", c=s.pink)

def g_flashlight(s):
    s.path("M44 30 l20 0 l-2 14 l-16 0 z", c=s.cyan)
    s.path("M46 44 l12 0 l-2 30 l-8 0 z", c=s.pink)

def g_game(s):
    s.rrect(26, 44, 56, 26, r=13, c=s.cyan)
    s.line(40, 57, 50, 57, w=5, c=s.green); s.line(45, 52, 45, 62, w=5, c=s.green)
    s.dot(66, 53, 3.5, s.pink); s.dot(72, 60, 3.5, s.cyan)

def g_video_call(s):
    s.rrect(26, 40, 38, 28, r=8, c=s.cyan)
    s.poly([(64, 50), (80, 42), (80, 66), (64, 58)], w=6, c=s.pink)

def g_shopping(s):
    s.path("M30 40 l8 0 l6 30 l30 0 l6 -22 l-40 0", w=6, c=s.cyan)
    s.dot(48, 78, 4, s.pink); s.dot(70, 78, 4, s.pink)

def g_ai(s):
    s.fpath("M54 28 l6 16 l16 6 l-16 6 l-6 16 l-6 -16 l-16 -6 l16 -6 z", c=s.cyan)
    s.fpath("M76 60 l3 8 l8 3 l-8 3 l-3 8 l-3 -8 l-8 -3 l8 -3 z", c=s.pink)

def g_knot(s):
    # OneQode mark approximated as concentric arcs (used for the pack icon + fallback)
    s.circ(54, 54, 24, w=8, c=s.cyan)
    s.circ(54, 54, 14, w=8, c=s.ink)
    s.path("M54 78 q24 -2 24 -24", w=8, c=s.pink)

GLYPHS = {
    "phone": g_phone, "dialer": g_dialer, "messages": g_messages, "contacts": g_contacts,
    "camera": g_camera, "photos": g_photos, "clock": g_clock, "alarm": g_alarm,
    "calc": g_calc, "calendar": g_calendar, "settings": g_settings, "files": g_files,
    "downloads": g_downloads, "browser": g_browser, "mail": g_mail, "music": g_music,
    "video": g_video, "play": g_play, "maps": g_maps, "store": g_store,
    "weather": g_weather, "notes": g_notes, "mic": g_mic, "search": g_search,
    "wallet": g_wallet, "bank": g_bank, "chat": g_chat, "secure_chat": g_secure_chat,
    "social": g_social, "bird": g_bird, "book": g_book, "doc": g_doc, "sheet": g_sheet,
    "slides": g_slides, "pdf": g_pdf, "terminal": g_terminal, "code": g_code, "git": g_git,
    "cloud": g_cloud, "vpn": g_vpn, "key": g_key, "auth": g_auth, "fitness": g_fitness,
    "podcast": g_podcast, "news": g_news, "translate": g_translate, "qr": g_qr,
    "compass": g_compass, "flashlight": g_flashlight, "game": g_game,
    "video_call": g_video_call, "shopping": g_shopping, "ai": g_ai, "knot": g_knot,
}

# ---------------------------------------------------------------------------
TILE_DEFS = f'''
  <defs>
    <linearGradient id="tile" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{TILE_A}"/>
      <stop offset="1" stop-color="{TILE_B}"/>
    </linearGradient>
    <radialGradient id="sheen" cx="0.32" cy="0.22" r="0.9">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.10"/>
      <stop offset="0.6" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>'''

def color_svg(name):
    s = S(mono=False)
    GLYPHS[name](s)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS}" height="{CANVAS}" viewBox="0 0 {CANVAS} {CANVAS}">
{TILE_DEFS}
  <rect x="0" y="0" width="{CANVAS}" height="{CANVAS}" rx="24" ry="24" fill="url(#tile)"/>
  <rect x="1.5" y="1.5" width="{CANVAS-3}" height="{CANVAS-3}" rx="23" ry="23" fill="none" stroke="{EDGE}" stroke-opacity="0.30" stroke-width="1.5"/>
  <rect x="0" y="0" width="{CANVAS}" height="{CANVAS}" rx="24" ry="24" fill="url(#sheen)"/>
  <g>{s.body()}</g>
</svg>'''

def mono_svg(name):
    s = S(mono=True)
    GLYPHS[name](s)
    # scale glyph up slightly for themed mode (fills more of the 66dp safe zone)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS}" height="{CANVAS}" viewBox="0 0 {CANVAS} {CANVAS}">
  <g>{s.body()}</g>
</svg>'''

# ---------------------------------------------------------------------------
def svg_to_png(svg, out, px):
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg); tmp = f.name
    subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), "-b", "none",
                    "-o", str(out), tmp], check=True)
    os.unlink(tmp)


def svg_to_png_centered(svg_path, out, px, frac):
    """Render an SVG glyph centred at `frac` of a transparent px*px canvas."""
    g = int(px * frac)
    raw = str(out).replace(".png", "_raw.png")
    subprocess.run(["rsvg-convert", "-w", str(g), "-h", str(g), "-b", "none",
                    "-o", raw, svg_path], check=True)
    canvas = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    im = Image.open(raw).convert("RGBA")
    off = (px - g) // 2
    canvas.alpha_composite(im, (off, off))
    canvas.save(out)
    os.remove(raw)


def svg_to_vectordrawable(svg, name):
    """Convert our controlled simple SVG to an Android VectorDrawable XML.
    We only emit <line>, <circle>, <rect>, <path>, <polyline> -> approximate each
    as VectorDrawable <path> with the same geometry. White, alpha preserved so the
    system can tint it for themed icons."""
    paths = []

    def stroke_path(d, w):
        paths.append(f'  <path android:strokeColor="#FFFFFFFF" android:strokeWidth="{w}" '
                     f'android:strokeLineCap="round" android:strokeLineJoin="round" '
                     f'android:fillColor="#00000000" android:pathData="{d}"/>')

    def fill_path(d):
        paths.append(f'  <path android:fillColor="#FFFFFFFF" android:pathData="{d}"/>')

    for el in re.findall(r"<(line|circle|rect|path|polyline)([^>]*)/>", svg):
        tag, attrs = el
        def gv(k, default=None):
            m = re.search(rf'{k}="([^"]*)"', attrs)
            return m.group(1) if m else default
        sw = gv("stroke-width", "6")
        if tag == "line":
            x1, y1, x2, y2 = (gv(k) for k in ("x1", "y1", "x2", "y2"))
            stroke_path(f"M{x1},{y1} L{x2},{y2}", sw)
        elif tag == "circle":
            cx, cy, r = float(gv("cx")), float(gv("cy")), float(gv("r"))
            d = (f"M{cx-r},{cy} a{r},{r} 0 1,0 {2*r},0 a{r},{r} 0 1,0 {-2*r},0")
            if gv("fill", "none") not in ("none", None) and "stroke" not in attrs:
                fill_path(d)
            elif gv("fill", "none") not in ("none", None):
                fill_path(d)
            else:
                stroke_path(d, sw)
        elif tag == "rect":
            x, y, w_, h_ = (float(gv(k)) for k in ("x", "y", "width", "height"))
            rx = float(gv("rx", "0"))
            d = (f"M{x+rx},{y} L{x+w_-rx},{y} Q{x+w_},{y} {x+w_},{y+rx} "
                 f"L{x+w_},{y+h_-rx} Q{x+w_},{y+h_} {x+w_-rx},{y+h_} "
                 f"L{x+rx},{y+h_} Q{x},{y+h_} {x},{y+h_-rx} "
                 f"L{x},{y+rx} Q{x},{y} {x+rx},{y} Z")
            if gv("fill", "none") not in ("none", None):
                fill_path(d)
            else:
                stroke_path(d, sw)
        elif tag == "polyline":
            pts = gv("points", "")
            coords = pts.split()
            if coords:
                d = "M" + " L".join(coords)
                if gv("fill", "none") not in ("none", None):
                    fill_path(d + " Z")
                else:
                    stroke_path(d, sw)
        elif tag == "path":
            d = gv("d", "")
            if gv("fill", "none") not in ("none", None):
                fill_path(d)
            else:
                stroke_path(d, sw)

    body = "\n".join(paths)
    return f'''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
{body}
</vector>
'''


def main():
    DRAW_XXX.mkdir(parents=True, exist_ok=True)
    DRAW_VEC.mkdir(parents=True, exist_ok=True)
    contact = []
    for name in GLYPHS:
        csvg = color_svg(name)
        svg_to_png(csvg, DRAW_XXX / f"ic_{name}.png", PNG_PX)
        msvg = mono_svg(name)
        (DRAW_VEC / f"ic_{name}_mono.xml").write_text(svg_to_vectordrawable(msvg, name))
        contact.append(name)
    print(f"forged {len(contact)} glyphs -> PNG (xxxhdpi) + monochrome VectorDrawables")

    # iconback: the glass tile alone (backplate for unmatched apps in Nova/Apex)
    back = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS}" height="{CANVAS}" viewBox="0 0 {CANVAS} {CANVAS}">
{TILE_DEFS}
  <rect x="0" y="0" width="{CANVAS}" height="{CANVAS}" rx="24" ry="24" fill="url(#tile)"/>
  <rect x="1.5" y="1.5" width="{CANVAS-3}" height="{CANVAS-3}" rx="23" ry="23" fill="none" stroke="{EDGE}" stroke-opacity="0.30" stroke-width="1.5"/>
  <rect x="0" y="0" width="{CANVAS}" height="{CANVAS}" rx="24" ry="24" fill="url(#sheen)"/>
</svg>'''
    svg_to_png(back, DRAW_XXX / "iconback.png", PNG_PX)
    print("forged iconback")

    # ---- the pack's OWN launcher icon (adaptive) ----
    # background tile (full bleed), foreground OneQode knot, monochrome knot.
    bg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS}" height="{CANVAS}" viewBox="0 0 {CANVAS} {CANVAS}">
{TILE_DEFS}
  <rect x="0" y="0" width="{CANVAS}" height="{CANVAS}" fill="url(#tile)"/>
  <rect x="0" y="0" width="{CANVAS}" height="{CANVAS}" fill="url(#sheen)"/>
</svg>'''
    mip = RES / "mipmap-xxxhdpi"
    mip.mkdir(parents=True, exist_ok=True)
    svg_to_png(bg, mip / "ic_launcher_background.png", PNG_PX)

    # foreground knot from the real brand SVG, recoloured cyan, glow under it
    brand = (PACK.parent / "brand" / "oneqode-symbol-cyan.svg").read_text()
    fg_knot = re.sub(r"fill:\s*#[0-9a-fA-F]{3,6}", "fill:#34d6ff", brand)
    tmpb = tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False)
    tmpb.write(fg_knot); tmpb.close()
    fg_png = mip / "ic_launcher_foreground.png"
    # render knot at ~62dp centered on 108 -> 62/108 of 432 = 248px, centered
    knot_px = int(PNG_PX * 0.60)
    subprocess.run(["rsvg-convert", "-w", str(knot_px), "-h", str(knot_px), "-b", "none",
                    "-o", str(fg_png).replace(".png", "_raw.png"), tmpb.name], check=True)
    os.unlink(tmpb.name)
    canvas = Image.new("RGBA", (PNG_PX, PNG_PX), (0, 0, 0, 0))
    raw = Image.open(str(fg_png).replace(".png", "_raw.png")).convert("RGBA")
    from PIL import ImageFilter as _IF
    glow = raw.filter(_IF.GaussianBlur(knot_px // 18))
    off = (PNG_PX - knot_px) // 2
    canvas.alpha_composite(glow, (off, off))
    canvas.alpha_composite(raw, (off, off))
    canvas.save(fg_png)
    os.remove(str(fg_png).replace(".png", "_raw.png"))

    # monochrome launcher (white knot)
    mono_brand = re.sub(r"fill:\s*#[0-9a-fA-F]{3,6}", "fill:#ffffff", brand)
    tmpm = tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False)
    tmpm.write(mono_brand); tmpm.close()
    mono_dir = RES / "drawable"
    svg_to_png_centered(tmpm.name, mono_dir / "ic_launcher_monochrome.png", PNG_PX, 0.62)
    os.unlink(tmpm.name)
    print("forged pack launcher icon (adaptive: bg + knot + monochrome)")

    # contact sheet for visual QA
    cols = 9
    rows = (len(contact) + cols - 1) // cols
    cell = 120
    sheet = Image.new("RGB", (cols*cell, rows*cell), (245, 247, 250))
    for i, name in enumerate(contact):
        ic = Image.open(DRAW_XXX / f"ic_{name}.png").convert("RGBA").resize((104, 104))
        sheet.paste(ic, ((i % cols)*cell + 8, (i//cols)*cell + 8), ic)
    sheet.save(PACK.parent / "docs" / "iconpack-contact-sheet.png")
    print("wrote contact sheet -> docs/iconpack-contact-sheet.png")


if __name__ == "__main__":
    main()
