#!/usr/bin/env bash
# Lock the Material You (Monet) system accent to an exact OneQode colour over ADB.
#
# GrapheneOS's on-device picker only offers preset accents and wallpaper-derived
# colours; the exact OneQode hex can only be pinned via this secure setting. No
# root required — `settings put secure` works through ADB on a normal device.
#
# Usage:
#   tools/oneqode-accent.sh day      # Light Glass  -> ice cyan  #00b4c8
#   tools/oneqode-accent.sh night    # Night Ride   -> neon pink #ff0080
#   tools/oneqode-accent.sh <hex>    # arbitrary, e.g. 00c8ff
#   tools/oneqode-accent.sh reset    # back to wallpaper-derived colour
#
# Requires: adb, with the phone connected and USB/wireless debugging authorised
# (GrapheneOS: Settings -> System -> Developer options -> USB/Wireless debugging).
set -euo pipefail

style="${STYLE:-VIBRANT}"   # TONAL_SPOT | VIBRANT | EXPRESSIVE | RAINBOW | FRUIT_SALAD | SPRITZ | MONOCHROMATIC

case "${1:-}" in
  day|light)   hex="00b4c8" ;;
  night|dark)  hex="ff0080" ;;
  cyan)        hex="00c8ff" ;;
  reset|wallpaper)
      adb shell settings put secure theme_customization_overlay_packages \
        '{"android.theme.customization.color_source":"home_wallpaper"}'
      echo "Accent reset to wallpaper-derived colour."
      exit 0 ;;
  ""|-h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *)  hex="${1#\#}" ;;   # arbitrary hex, strip leading #
esac

command -v adb >/dev/null || { echo "adb not found"; exit 1; }
adb get-state >/dev/null 2>&1 || { echo "No device. Connect the phone and enable ADB debugging."; exit 1; }

json="{\"android.theme.customization.system_palette\":\"$hex\",\"android.theme.customization.accent_color\":\"$hex\",\"android.theme.customization.theme_style\":\"$style\",\"android.theme.customization.color_source\":\"preset\"}"

echo "Setting OneQode accent seed #$hex (style $style)…"
adb shell settings put secure theme_customization_overlay_packages "'$json'"
echo "Done. If it doesn't take effect immediately, toggle the screen off/on or"
echo "re-open the launcher. Run with 'reset' to return to wallpaper colours."
