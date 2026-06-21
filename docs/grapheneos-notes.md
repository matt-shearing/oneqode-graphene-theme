# GrapheneOS theming notes (research summary, 2026)

Background for why the suite is shaped the way it is. Sources are GrapheneOS
official docs / issue tracker / forums and Android developer docs.

## Device — Pixel 10 Pro Fold ("rango")

- Announced Aug 20 2025; retail Oct 9 2025; shipped with **Android 16**; Tensor G5.
- **Inner display:** 2076 × 2152 px, ~1:1, 8.0", 373 ppi, 120 Hz LTPO.
- **Cover display:** 1080 × 2364 px, 20:9, 6.4", 408 ppi.
- **GrapheneOS:** supported (codename *rango*); experimental support landed
  2025-11-26, now in stable channels.
- Wallpaper gotchas: vertical **fold crease** down the inner panel's centre;
  hole-punch **top-right (inner)** and **top-centre (cover)**; pronounced rounded
  corners. One image can't serve both screens — we ship a square inner master
  (2304²) and a tall 20:9 cover (2160×2364, 2× width for scroll headroom).

## Launcher & icon packs

- GrapheneOS ships a fork of **AOSP Launcher3** (not the Pixel Launcher). It does
  **not** support third-party icon packs (request closed `NOT_PLANNED`).
- It **does** support Material You themed (monochrome) icons on the home screen.
- Third-party launchers install/run fine. **Lawnchair** (FOSS) is the practical
  choice: icon-pack + themed-icon support, Private Space parity in nightlies.

## Material You / Monet

- Wallpaper-driven dynamic colour is the default. The on-device picker offers
  preset accents + a limited "other colours" set; **arbitrary hex needs ADB**:
  `settings put secure theme_customization_overlay_packages '{…system_palette…}'`
  (no root). This is what `tools/oneqode-accent.sh` does.

## Themed icons & Android 16/17

- `<monochrome>` adaptive-icon layer (Android 13+) drives themed icons; system
  tints it via Material You.
- **Android 16 QPR2+** auto-themes *all* app icons (apps can't opt out), so themed
  mode gives total coverage. Android 17 documents no icon-format changes — our
  pack is forward-compatible.
- Lawnchair reads icon-pack themed icons via a `grayscale_icon_map.xml`
  (package → monochrome drawable), which this pack ships. Lawnchair does **not**
  implement the `iconback`/`iconmask` fallback; Nova/Apex do (we ship `iconback`).

## Not possible without root (GrapheneOS doesn't support root)

- **System font** replacement (removed from AOSP since Android 12).
- **Boot animation** (GrapheneOS has only a logo mask; changeable only by
  building from source).
- **System-wide overlays** (Substratum/RRO) and OEM theme engines.
- **Rich lock-screen clock faces** (depend on non-AOSP Google apps).

These are documented rather than worked around, by design.
