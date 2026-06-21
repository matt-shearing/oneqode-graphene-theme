# OneQode — Color & Design Reference (Android / GrapheneOS)

This mirrors the OneQode KDE theme suite so the phone and desktop feel like one
system. Two variants: **Light Glass** (day) and **Night Ride** (night).

## Light Glass

| Role | Hex | RGB |
|------|-----|-----|
| Background primary | `#fafcff` | 250,252,255 |
| Background secondary | `#f0f4f8` | 240,244,248 |
| Background tertiary | `#e8f0f5` | 232,240,245 |
| Text primary | `#232d37` | 35,45,55 |
| Text secondary | `#5a6570` | 90,101,112 |
| Text muted | `#8090a0` | 128,144,160 |
| **Accent primary** | `#00b4c8` | 0,180,200 |
| Accent secondary | `#0095a8` | 0,149,168 |
| Border | `#d8e0e8` | 216,224,232 |

## Night Ride

| Role | Hex | RGB |
|------|-----|-----|
| Background primary | `#191c2a` | 25,28,42 |
| Background secondary | `#12141f` | 18,20,31 |
| Background tertiary | `#282d3c` | 40,45,60 |
| Text primary | `#e6ebf5` | 230,235,245 |
| Text secondary | `#a0a8b8` | 160,168,184 |
| Text muted | `#6a7080` | 106,112,128 |
| **Accent primary (pink)** | `#ff0080` | 255,0,128 |
| **Accent secondary (cyan)** | `#00c8ff` | 0,200,255 |
| Accent green | `#50ffb4` | 80,255,180 |
| Border | `#282d3c` | 40,45,60 |

## Brand mark

OneQode Celtic-knot symbol. Canonical fills:
- Celtic Blue `#1774e0` (primary brand)
- Cyan `#00b4c8` (Light Glass accent / light-on-dark usage)
- White `#ffffff` (monochrome / themed-icon silhouette)

## Material You (Monet) accent targets

GrapheneOS derives the system palette from the wallpaper and only exposes preset
accents in the on-device picker. To pin the exact OneQode accent, use the ADB
helper in `tools/oneqode-accent.sh`:

- Light Glass → system palette seed `#00b4c8` (ice cyan)
- Night Ride → system palette seed `#ff0080` (neon pink)

The wallpapers are deliberately tuned so the *automatic* wallpaper-derived accent
already lands close to these seeds, so the look is on-brand even without ADB.

## Typography

System font cannot be replaced without root on GrapheneOS. OneQode uses **Inter**
(UI) and **JetBrains Mono** (mono) on the desktop; on Android we match the spirit
with the system default (Roboto/Google Sans flavour) and reserve Inter/JetBrains
Mono for any in-app surfaces we control (e.g. KWGT widgets, if used).

## Foldable canvas (Pixel 10 Pro Fold — codename "rango")

| Screen | Native px | Aspect | Wallpaper master |
|--------|-----------|--------|------------------|
| Inner (8.0") | 2076 × 2152 | ~1:1 | 2304 × 2304 square (covers both orientations) |
| Cover (6.4") | 1080 × 2364 | 20:9 | 2160 × 2364 (2× width for scroll headroom) |

Design safe zones:
- **Inner:** avoid the vertical centre line (fold crease) and the **top-right**
  hole-punch. Keep focal content off-centre-vertical.
- **Cover:** avoid the **top-centre** hole-punch. Generous rounded-corner margins.
- Keep the logo/focal element clear of the top ~12% (status bar + clock) and the
  bottom ~18% (dock / gesture bar) on both screens.
