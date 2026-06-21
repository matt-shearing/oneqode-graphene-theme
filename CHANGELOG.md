# Changelog

All notable changes to the OneQode GrapheneOS / Android theme suite.

## [1.1.0] — 2026-06-21

### Added
- **OneQode Theme companion app** (`com.oneqode.theme`, `dist/oneqode-theme-release.apk`)
  — the native, no-launcher way to get automatic day/night:
  - Switches the Material You **accent** (cyan ↔ pink, via `WRITE_SECURE_SETTINGS`,
    granted once over ADB — no root) **and the wallpaper** (Light Glass ↔ Night Ride).
  - **Solar** (lat/long) or **fixed-time** schedule, reschedules on boot, plus a
    Quick Settings tile and manual Apply Day/Night buttons.
  - Pairs with GrapheneOS's built-in Dark-theme schedule for a fully synced look.
- **Emulator test harness** (`tools/bootstrap-emulator.sh`) and on-device
  verification screenshots in `docs/`.

### Verified
- Day/night switching tested end-to-end on **Android 16 (API 36)**: accent
  live-retints the system UI (pink ↔ cyan), wallpaper swaps, solar/fixed schedule
  fires (RTC_WAKEUP alarm). Both APKs install and the icon pack is recognised by
  the Nova/Lawnchair theme intents.

### Changed
- README reframed around the **native path** (companion app + wallpapers + accent);
  the Lawnchair icon pack is now documented as optional (only for custom *colored*
  icons), since the stock launcher already does themed monochrome icons.

## [1.0.0] — 2026-06-21

Initial release. Targets the Google Pixel 10 Pro Fold ("rango") on GrapheneOS,
Android 16 → forward-compatible with Android 17.

### Added
- **Wallpapers** — Light Glass + Night Ride, rendered for both foldable screens:
  inner (2304² square master) and cover (2160×2364, 20:9), crease- and
  hole-punch-aware. Generator: `wallpapers/src/generate_wallpapers.py`.
- **Icon pack** (`com.oneqode.iconpack`, signed APK in `dist/`):
  - 54 cohesive OneQode line glyphs on a dark-glass tile.
  - ~140 app components mapped across 126 packages (`appfilter.xml`).
  - **Monochrome themed icons** for Material You via `grayscale_icon_map.xml`
    (Lawnchair) + `<monochrome>` adaptive layers — auto-adapt to day/night.
  - `iconback` glass backplate for unmatched apps on Nova/Apex.
  - Branded adaptive launcher icon (knot on glass, with monochrome layer).
  - Minimal in-app dashboard with setup instructions.
- **Build system** — `tools/bootstrap-sdk.sh` (headless SDK) +
  `iconpack/build-cli.sh` (aapt2/javac/d8/zipalign/apksigner, no Android Studio);
  Gradle project + GitHub Actions workflow as alternatives.
- **ADB tools** — `oneqode-accent.sh` (pin Monet accent to exact OneQode hex),
  `apply-wallpapers.sh` (push wallpapers), `dump-components.sh` (extend the pack).
- **Docs** — GrapheneOS-specific README, Lawnchair setup guide, research notes,
  and `brand/palette.md` (shared design reference with the KDE suite).

### Known limitations (GrapheneOS / no root)
- Stock launcher can't use icon packs — Lawnchair required.
- System font, boot animation, system-wide overlays, and rich lock-screen clocks
  are not possible without root and are intentionally out of scope.
