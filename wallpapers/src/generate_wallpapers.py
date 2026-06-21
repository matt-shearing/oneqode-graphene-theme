#!/usr/bin/env python3
"""
OneQode foldable wallpaper generator (Pixel 10 Pro Fold).

Produces four wallpapers in the OneQode design language:
  night-ride/inner.png   2304x2304  (square master, covers both inner orientations)
  night-ride/cover.png   2160x2364  (20:9 cover, 2x width for scroll headroom)
  light-glass/inner.png  2304x2304
  light-glass/cover.png  2160x2364

Night Ride  -> synthwave: gradient sky, perspective grid, neon sun, glowing knot.
Light Glass -> frosted glass: soft gradient, blurred cyan orbs, faint knot watermark.

The dominant on-screen colour is tuned so GrapheneOS's wallpaper-derived Monet
accent already lands near the OneQode accent (cyan for day, pink for night).

Dependencies: Pillow, rsvg-convert (librsvg). No numpy required.
"""
import math
import os
import re
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
BRAND_SVG = ROOT / "brand" / "oneqode-symbol-cyan.svg"
OUT = HERE.parent  # wallpapers/

# ---- palette ---------------------------------------------------------------
LG = dict(
    bg_top=(250, 252, 255), bg_mid=(240, 244, 248), bg_bot=(224, 236, 243),
    accent=(0, 180, 200), accent2=(0, 149, 168), ink=(35, 45, 55),
)
NR = dict(
    sky_top=(10, 11, 20), sky_mid=(20, 22, 38), horizon=(40, 22, 52),
    pink=(255, 0, 128), cyan=(0, 200, 255), green=(80, 255, 180),
    grid=(0, 200, 255),
)

# ---------------------------------------------------------------------------
def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def render_logo(hex_fill, size):
    """Render the OneQode knot SVG to an RGBA PIL image at `size` px, recoloured."""
    svg = BRAND_SVG.read_text()
    svg = re.sub(r"fill:\s*#[0-9a-fA-F]{3,6}", f"fill:{hex_fill}", svg)
    svg = re.sub(r'fill="#[0-9a-fA-F]{3,6}"', f'fill="{hex_fill}"', svg)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg)
        tmp = f.name
    png = tmp + ".png"
    subprocess.run(
        ["rsvg-convert", "-w", str(size), "-h", str(size),
         "-b", "none", "-o", png, tmp],
        check=True,
    )
    img = Image.open(png).convert("RGBA")
    os.unlink(tmp)
    os.unlink(png)
    return img


def glow_layer(hex_fill, size, blur, pad=0.4):
    """A blurred logo glow on a PADDED transparent canvas so the blur never
    clamps against the bounding box (which would leave a visible rectangle).
    Returns (layer, offset) — composite at (target_x - offset, target_y - offset)."""
    off = int(size * pad)
    canvas = size + off * 2
    base = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    base.alpha_composite(render_logo(hex_fill, size), (off, off))
    return base.filter(ImageFilter.GaussianBlur(blur)), off


def vgradient(size, stops):
    """Vertical gradient. stops = [(pos0..1, rgb), ...] sorted by pos."""
    w, h = size
    base = Image.new("RGB", (1, h))
    px = base.load()
    for y in range(h):
        t = y / (h - 1)
        # find segment
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                lt = (t - p0) / (p1 - p0) if p1 > p0 else 0
                px[0, y] = lerp(c0, c1, lt)
                break
        else:
            px[0, y] = stops[-1][1]
    return base.resize((w, h))


def radial_glow(size, center, radius, color, max_alpha=255):
    """A soft radial glow as an RGBA layer."""
    w, h = size
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    # draw on a smaller buffer then blur+upscale for speed
    scale = 4
    sw, sh = w // scale, h // scale
    small = Image.new("L", (sw, sh), 0)
    d = ImageDraw.Draw(small)
    cx, cy = center[0] / scale, center[1] / scale
    r = radius / scale
    steps = 60
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(max_alpha * (1 - i / steps) ** 2)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=a)
    small = small.filter(ImageFilter.GaussianBlur(radius / scale / 6))
    mask = small.resize((w, h))
    solid = Image.new("RGBA", size, color + (0,))
    solid.putalpha(mask)
    return solid


# ---------------------------------------------------------------------------
def make_night(size, tag):
    w, h = size
    img = vgradient(size, [
        (0.0, NR["sky_top"]),
        (0.38, NR["sky_mid"]),
        (0.58, NR["horizon"]),
        (0.62, (70, 28, 70)),
        (0.66, NR["sky_mid"]),
        (1.0, (8, 9, 16)),
    ]).convert("RGBA")

    horizon_y = int(h * 0.62)
    cx = w // 2

    # --- stars (deterministic, no RNG dependency) ---
    star = Image.new("RGBA", size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(star)
    seed = 12345
    for i in range(220):
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        x = seed % w
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        y = (seed % horizon_y)
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        s = 1 + seed % 3
        a = 40 + (seed % 150)
        sd.ellipse([x, y, x + s, y + s], fill=(220, 235, 255, a))
    img = Image.alpha_composite(img, star)

    # --- neon sun glow behind horizon ---
    sun_r = int(w * 0.30)
    img = Image.alpha_composite(img, radial_glow(size, (cx, horizon_y - int(h*0.02)), int(sun_r*2.2), NR["pink"], 150))
    img = Image.alpha_composite(img, radial_glow(size, (cx, horizon_y - int(h*0.02)), int(sun_r*1.3), (255, 90, 170), 120))

    # sun disc with scanline gaps
    sun = Image.new("RGBA", size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sun)
    sun_top = horizon_y - sun_r
    sun_grad = vgradient((sun_r*2, sun_r*2), [
        (0.0, (255, 220, 120)), (0.45, NR["pink"]), (1.0, (150, 0, 90)),
    ]).convert("RGBA")
    mask = Image.new("L", (sun_r*2, sun_r*2), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, sun_r*2, sun_r*2], fill=255)
    sun_grad.putalpha(mask)
    # scanline gaps in lower half
    sg = ImageDraw.Draw(sun_grad)
    gap = max(6, sun_r // 18)
    yy = sun_r  # from middle down
    n = 0
    while yy < sun_r*2:
        thick = int(gap * (0.25 + 0.9 * n / 10))
        sg.rectangle([0, yy, sun_r*2, yy + thick], fill=(0, 0, 0, 0))
        yy += gap + thick
        n += 1
    sun.alpha_composite(sun_grad, (cx - sun_r, sun_top))
    img = Image.alpha_composite(img, sun)

    # --- perspective grid below horizon ---
    grid = Image.new("RGBA", size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(grid)
    gc = NR["grid"]
    # vertical converging lines
    spread = w * 1.6
    nlines = 22
    for i in range(-nlines, nlines + 1):
        bx = cx + (i / nlines) * spread
        gd.line([(cx, horizon_y), (bx, h)], fill=gc + (90,), width=2)
    # horizontal lines with perspective spacing
    rows = 26
    for j in range(rows):
        t = j / rows
        y = horizon_y + (h - horizon_y) * (t ** 1.9)
        a = int(120 * (0.25 + t))
        gd.line([(0, y), (w, y)], fill=gc + (min(a, 160),), width=2)
    grid = grid.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.alpha_composite(img, grid)
    # fade grid into horizon
    fade = vgradient(size, [(0.0,(0,0,0)),(1.0,(0,0,0))]).convert("RGBA")
    fmask = Image.new("L", size, 0)
    fdraw = ImageDraw.Draw(fmask)
    for y in range(horizon_y, min(horizon_y + int(h*0.06), h)):
        t = (y - horizon_y) / max(1, int(h*0.06))
        fdraw.line([(0, y), (w, y)], fill=int(180 * (1 - t)))
    fade.putalpha(fmask)
    fade2 = Image.new("RGBA", size, NR["sky_mid"] + (0,))
    fade2.putalpha(fmask)
    img = Image.alpha_composite(img, fade2)

    # --- glowing knot, upper third, horizontally centred ---
    logo_size = int(w * (0.34 if tag == "inner" else 0.52))
    ly = int(h * (0.30 if tag == "inner" else 0.34))
    lx = cx - logo_size // 2
    lyy = ly - logo_size // 2
    pg, off = glow_layer("#ff0080", logo_size, logo_size // 12, 0.5)
    img.alpha_composite(pg, (lx - off, lyy - off))
    cg, off = glow_layer("#00c8ff", logo_size, logo_size // 24, 0.32)
    img.alpha_composite(cg, (lx - off, lyy - off))
    knot = render_logo("#eafcff", logo_size)
    img.alpha_composite(knot, (lx, lyy))

    # --- vignette ---
    vig = Image.new("L", size, 0)
    ImageDraw.Draw(vig).rectangle([0, 0, w, h], fill=0)
    vmask = radial_glow(size, (cx, h//2), int(max(w, h)*0.85), (0,0,0), 255).split()[3]
    vmask = vmask.point(lambda p: 255 - p)
    dark = Image.new("RGBA", size, (4, 5, 10, 0))
    dark.putalpha(vmask.point(lambda p: int(p*0.55)))
    img = Image.alpha_composite(img, dark)

    return img.convert("RGB")


def make_light(size, tag):
    w, h = size
    img = vgradient(size, [
        (0.0, LG["bg_top"]),
        (0.5, LG["bg_mid"]),
        (1.0, LG["bg_bot"]),
    ]).convert("RGBA")
    cx = w // 2

    # soft cyan glass orbs (blurred radial blobs), off the crease centreline
    orbs = [
        (int(w*0.20), int(h*0.22), int(w*0.46), LG["accent"], 55),
        (int(w*0.84), int(h*0.74), int(w*0.54), LG["accent2"], 50),
        (int(w*0.74), int(h*0.16), int(w*0.26), (120, 220, 235), 42),
        (int(w*0.26), int(h*0.84), int(w*0.30), (150, 228, 240), 38),
    ]
    for ox, oy, orad, col, al in orbs:
        img = Image.alpha_composite(img, radial_glow(size, (ox, oy), orad, col, al))

    # frosted-glass bubbles: faint fill + thin cyan ring outline (bokeh feel)
    bubbles = [
        (int(w*0.16), int(h*0.30), int(w*0.10)),
        (int(w*0.80), int(h*0.20), int(w*0.07)),
        (int(w*0.88), int(h*0.56), int(w*0.13)),
        (int(w*0.10), int(h*0.66), int(w*0.05)),
        (int(w*0.72), int(h*0.86), int(w*0.085)),
    ]
    bl = Image.new("RGBA", size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(bl)
    for bx, by, br in bubbles:
        bd.ellipse([bx-br, by-br, bx+br, by+br], fill=(255, 255, 255, 26))
        bd.ellipse([bx-br, by-br, bx+br, by+br], outline=LG["accent"] + (60,), width=max(2, br//28))
        # little highlight
        hr = int(br*0.5)
        bd.ellipse([bx-br+hr//3, by-br+hr//3, bx-br+hr, by-br+hr],
                   fill=(255, 255, 255, 40))
    bl = bl.filter(ImageFilter.GaussianBlur(0.6))
    img = Image.alpha_composite(img, bl)

    # centred knot watermark — soft, low opacity, single mark
    logo_size = int(w * (0.50 if tag == "inner" else 0.66))
    knot = render_logo("#00b4c8", logo_size)
    alpha = knot.split()[3].point(lambda p: int(p * 0.16))
    knot.putalpha(alpha)
    soft = knot.filter(ImageFilter.GaussianBlur(1.5))
    lx = cx - logo_size // 2
    ly = int(h * 0.46) - logo_size // 2
    img.alpha_composite(soft, (lx, ly))

    # top sheen
    sheen = vgradient(size, [(0.0,(255,255,255)),(0.18,(255,255,255)),(0.4,LG["bg_mid"])]).convert("RGBA")
    smask = Image.new("L", size, 0)
    sdraw = ImageDraw.Draw(smask)
    for y in range(int(h*0.22)):
        t = y/(h*0.22)
        sdraw.line([(0,y),(w,y)], fill=int(70*(1-t)))
    sheen.putalpha(smask)
    img = Image.alpha_composite(img, sheen)

    return img.convert("RGB")


def main():
    jobs = [
        ("night-ride", "inner", (2304, 2304), make_night),
        ("night-ride", "cover", (2160, 2364), make_night),
        ("light-glass", "inner", (2304, 2304), make_light),
        ("light-glass", "cover", (2160, 2364), make_light),
    ]
    for variant, tag, size, fn in jobs:
        print(f"  rendering {variant}/{tag} {size[0]}x{size[1]} ...", flush=True)
        im = fn(size, tag)
        out = OUT / variant / f"{tag}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        im.save(out, "PNG", optimize=True)
        # also a downscaled JPG preview for docs
        prev = im.copy()
        prev.thumbnail((900, 900))
        (ROOT / "docs").mkdir(exist_ok=True)
        prev.save(ROOT / "docs" / f"wp-{variant}-{tag}.jpg", "JPEG", quality=86)
        print(f"    -> {out}")
    print("DONE")


if __name__ == "__main__":
    main()
