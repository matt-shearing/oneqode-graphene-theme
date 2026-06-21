# OneQode — GrapheneOS / Android Theme Suite

The OneQode look for the **Google Pixel 10 Pro Fold** (codename *rango*) running
**GrapheneOS** — a companion to the [OneQode KDE theme suite](https://github.com/matt-shearing/oneqode-kde-themes).
Same design language, two variants:

- **OneQode Light Glass** — light, glassy, ice-cyan (`#00b4c8`) for daytime.
- **OneQode Night Ride** — dark synthwave, neon pink (`#ff0080`) + cyan (`#00c8ff`) for night.

[![Latest release](https://img.shields.io/github/v/release/matt-shearing/oneqode-graphene-theme?label=release&color=00b4c8)](https://github.com/matt-shearing/oneqode-graphene-theme/releases/latest)
[![Install with Obtainium](https://img.shields.io/badge/Install_with-Obtainium-ff0080?logo=android&logoColor=white)](https://apps.obtainium.imranr.dev/redirect.html?r=obtainium://add/https://github.com/matt-shearing/oneqode-graphene-theme)
[![Download APK](https://img.shields.io/badge/Download-APK-00c8ff?logo=android&logoColor=white)](https://github.com/matt-shearing/oneqode-graphene-theme/releases/latest/download/oneqode-iconpack-release.apk)

> **Install in one tap:** on the phone, tap **Install with Obtainium** above (needs the
> [Obtainium](https://obtainium.imranr.dev) app). Full steps in [Install](#install).

| Light Glass (inner) | Night Ride (inner) |
|---|---|
| ![Light Glass](docs/wp-light-glass-inner.jpg) | ![Night Ride](docs/wp-night-ride-inner.jpg) |

![Icon set](docs/iconpack-contact-sheet.png)

## What's in the box

| Component | What it is | Auto day/night? |
|-----------|-----------|-----------------|
| **Wallpapers** | Light + dark, rendered for **both** foldable screens (near-square inner + 20:9 cover), crease- and hole-punch-aware | Manual / via Material You |
| **Icon pack** (`dist/…apk`) | ~125 apps mapped to cohesive OneQode line icons on a glass tile, **+ monochrome themed icons** for Material You | Themed icons follow Material You |
| **Accent lock** (`tools/oneqode-accent.sh`) | Pins the system Monet accent to the exact OneQode hex over ADB | — |
| **Lawnchair guide** (`lawnchair/`) | How to apply the pack + recommended settings | — |

## Reality check: what's possible on GrapheneOS (read this first)

GrapheneOS is hardened AOSP with **no root**, and that sets a hard ceiling on
theming. This suite does everything that's possible *without* root and is honest
about the rest:

**✅ Done here (no root):**
- Wallpapers for both screens.
- A full icon pack with **themed/monochrome icons** — which is exactly where
  Android is heading: **Android 16 QPR2+ auto-themes every icon**, so our pack is
  forward-compatible into Android 17.
- Exact Material You accent via ADB (`settings put secure …` — no root needed).

**❌ Not possible without root (so not faked):**
- System **font** replacement, custom **boot animation**, system-wide overlays
  (Substratum/RRO), rich lock-screen clock faces. GrapheneOS doesn't support root
  and these need system-partition or root access. See `docs/grapheneos-notes.md`.

**Launcher:** the **stock GrapheneOS launcher cannot use icon packs** — install
**Lawnchair** (FOSS) to apply OneQode. See `lawnchair/README.md`.

## Install

Four steps: get the pack, apply it in Lawnchair, set the wallpapers, lock the
accent. Everything you need is below — no other page required.

### A · Install the icon pack

**Easiest — Obtainium (auto-updates):**

[![Install with Obtainium](https://img.shields.io/badge/Install_with-Obtainium-ff0080?logo=android&logoColor=white)](https://apps.obtainium.imranr.dev/redirect.html?r=obtainium://add/https://github.com/matt-shearing/oneqode-graphene-theme)

1. Install **[Obtainium](https://obtainium.imranr.dev)** on the phone.
2. Tap the badge above **or** open Obtainium → **Add App** and paste:
   `https://github.com/matt-shearing/oneqode-graphene-theme`
3. Obtainium grabs the latest release and installs it. Allow “install unknown
   apps” once. It tracks future releases automatically.

**Or manually:**
- **Direct download** on the phone:
  [oneqode-iconpack-release.apk](https://github.com/matt-shearing/oneqode-graphene-theme/releases/latest/download/oneqode-iconpack-release.apk)
  → tap to install, **or**
- **ADB** from a computer: `adb install dist/oneqode-iconpack-release.apk`
  (enable *Settings → System → Developer options → Wireless/USB debugging* first).

### B · Apply it in Lawnchair

The stock GrapheneOS launcher **cannot use icon packs**, so install **Lawnchair**
from **https://lawnchair.app** (not the Play/F-Droid “v2” — that one's abandoned).

1. Long-press the home screen → **Home settings**.
2. **General → Icon Pack → OneQode**.
3. Enable **Themed icons** (*General → Icon Style / Themed icons*).
   - On Android 16 QPR2+ this themes *every* app; OneQode ships hand-tuned
     monochrome icons for ~125 common apps so they look intentional, not auto-traced.
4. Themed icons follow Material You, so they re-tint automatically when you switch
   wallpaper/accent between Light Glass and Night Ride.

> Nova / Action / Apex instead? Settings → Look & feel → **Icon theme → OneQode**.
> More tuning tips in [`lawnchair/README.md`](lawnchair/README.md).

### C · Set the wallpapers

Push them to the phone over ADB:

```bash
tools/apply-wallpapers.sh night        # or: day | both
```

Then set each from the wallpaper picker — the foldable's two screens have very
different shapes, so set each from the matching physical state:

- **Unfold** the phone → set the **inner** screen with `OneQode-<variant>-inner.png`.
  Position the OneQode mark **above the vertical fold crease** (centre line).
- **Fold** the phone → set the **cover** screen with `OneQode-<variant>-cover.png`.

> No ADB? Copy the PNGs from `wallpapers/light-glass/` and `wallpapers/night-ride/`
> onto the phone and pick them in the wallpaper app.

### D · Lock the Material You accent (optional, no root)

GrapheneOS's on-device picker only offers preset accents. To pin the exact OneQode
colour, run over ADB:

```bash
tools/oneqode-accent.sh night          # Night Ride  → #ff0080
tools/oneqode-accent.sh day            # Light Glass → #00b4c8
tools/oneqode-accent.sh reset          # back to wallpaper-derived colour
```

### Day / night

There's no automatic icon-pack switch, but because themed icons follow Material
You, switching the **wallpaper + accent** flips the whole home screen between the
two looks:

- **Day:** Light Glass wallpaper + `tools/oneqode-accent.sh day`
- **Night:** Night Ride wallpaper + `tools/oneqode-accent.sh night`

## Building the icon pack yourself

A prebuilt, signed APK ships in `dist/`. To rebuild from source:

```bash
# one-time: fetch a minimal headless Android SDK into ~/.android-sdk-oneqode
tools/bootstrap-sdk.sh

# regenerate icons + mappings, then build & sign (aapt2 + javac + d8 + apksigner)
python3 iconpack/tools/forge.py        # forges icons + monochrome vectors
python3 iconpack/tools/appfilter.py    # generates appfilter / grayscale / drawable xml
iconpack/build-cli.sh                   # -> dist/oneqode-iconpack-release.apk
```

No Android Studio required. (Android Studio users can instead open `iconpack/`
as a Gradle project — `build.gradle` is provided. CI builds via
`.github/workflows/build.yml`.)

> **Signing:** `build-cli.sh` auto-creates a dev keystore at
> `iconpack/keystore/oneqode-release.jks` (password `oneqode`). **Rotate this for
> any real distribution** — and note that updating an installed APK requires the
> *same* signing key. For Accrescent distribution you sign with your own key and
> ship split APKs.

## Regenerating / extending

| To change… | Edit… | Then run |
|------------|-------|----------|
| Wallpaper art | `wallpapers/src/generate_wallpapers.py` | `python3 wallpapers/src/generate_wallpapers.py` |
| Icon glyphs / colours | `iconpack/tools/forge.py` | `forge.py` → `appfilter.py` → `build-cli.sh` |
| App → icon mappings | `iconpack/tools/appfilter.py` | `appfilter.py` → `build-cli.sh` |
| Add an app it misses | `tools/dump-components.sh <kw>` to find the component, add to `appfilter.py` | rebuild |

## Repository layout

```
oneqode-graphene-theme/
├── brand/                  OneQode logo SVGs + palette.md (single source of truth)
├── wallpapers/
│   ├── src/                generator
│   ├── light-glass/        inner.png + cover.png
│   └── night-ride/         inner.png + cover.png
├── iconpack/
│   ├── app/src/main/       AndroidManifest, res/ (icons, appfilter, grayscale map), MainActivity
│   ├── tools/              forge.py (icons), appfilter.py (mappings)
│   ├── build-cli.sh        no-Gradle build (aapt2/javac/d8/apksigner)
│   └── build.gradle …      Android Studio / Gradle path
├── tools/
│   ├── bootstrap-sdk.sh    fetch headless Android SDK
│   ├── oneqode-accent.sh   pin Monet accent over ADB
│   ├── apply-wallpapers.sh push wallpapers over ADB
│   └── dump-components.sh  list device components for extending the pack
├── lawnchair/README.md     launcher setup + recommended settings
├── docs/                   previews + grapheneos-notes.md
└── dist/                   built, signed APK
```

## Design reference

See `brand/palette.md` for the full colour system, the foldable canvas sizes, and
safe-zone rules — kept in lockstep with the OneQode KDE suite.

## License

MIT — see `LICENSE`. OneQode brand mark © OneQode. Icon glyphs are original
geometric category marks; no third-party brand logos are reproduced.
