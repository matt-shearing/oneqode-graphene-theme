# OneQode on Lawnchair (recommended launcher)

GrapheneOS's stock launcher does **not** support icon packs, so to get the full
OneQode look you need a launcher that does. **Lawnchair** is the right choice: it
is FOSS (Apache-2.0), supports the icon-pack standard *and* Material You themed
icons, and its nightly builds have Private Space parity with the stock launcher.

> Don't install Lawnchair from the Play Store / Aurora / default F-Droid — those
> are the abandoned 2019 "v2". Get a current build from **https://lawnchair.app**
> or the GitHub releases: https://github.com/LawnchairLauncher/lawnchair/releases

## 1. Install the icon pack

Sideload `dist/oneqode-iconpack-release.apk`:

```bash
adb install dist/oneqode-iconpack-release.apk
# or copy the APK to the phone and tap it (allow "install unknown apps" once)
```

## 2. Apply it in Lawnchair

1. Long-press the home screen → **Home settings**.
2. **General → Icon Pack → OneQode**.
3. **General → Icon Style** (or *Themed icons*): turn **Themed icons ON**.
   - On Android 16 QPR2+, themed icons apply to *every* app (the system
     auto-generates monochrome icons for apps that don't ship one), so coverage
     is total. OneQode's pack supplies hand-tuned monochrome icons for ~125
     common apps so those look intentional rather than auto-traced.
4. Themed icons follow Material You, so they re-tint automatically when you
   switch between the Light Glass and Night Ride wallpapers/accent.

## 3. Recommended Lawnchair settings for the OneQode feel

These mirror the clean, glassy OneQode desktop aesthetic:

| Setting | Value |
|---------|-------|
| Icon Pack | OneQode |
| Themed icons | On |
| Icon shape | Squircle (or System) |
| Home grid | 5 × 5 (inner) — Lawnchair keeps a separate grid per screen on foldables |
| Dock | Transparent background, 5 icons |
| Search bar | Themed / transparent |
| Folder background | Blurred / accent-tinted |
| Background blur (Lab) | On — gives the "glass" depth over the wallpaper |
| Font | System (system font can't be changed without root on GrapheneOS) |
| Color | Match wallpaper / Material You |

## 4. Pair with the matching wallpaper + accent

- Light Glass day look → `wallpapers/light-glass/` + `tools/oneqode-accent.sh day`
- Night Ride night look → `wallpapers/night-ride/` + `tools/oneqode-accent.sh night`

Lawnchair has no automatic day/night *icon-pack* switch, but because the themed
icons follow Material You, switching the wallpaper + accent flips the whole home
screen between the two OneQode looks without changing the icon pack.

## Notes / limitations on Lawnchair

- Lawnchair does **not** implement the `iconback`/`iconmask` fallback, so
  *unmatched* apps fall back to their themed (monochrome) icon or original icon
  rather than getting the OneQode glass backplate. With themed icons on, unmatched
  apps still look consistent. (Nova/Apex *do* use the backplate we ship.)
- If an app you use has the wrong/no icon, dump its component with
  `tools/dump-components.sh <keyword>` and add a line to
  `iconpack/tools/appfilter.py`, then rebuild.
