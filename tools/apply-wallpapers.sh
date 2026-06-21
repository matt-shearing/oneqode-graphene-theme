#!/usr/bin/env bash
# Push the OneQode wallpapers to the Pixel 10 Pro Fold over ADB.
#
# Android has no reliable root-free shell command to *set* the wallpaper from a
# file, so this pushes the images to the phone and you pick them in the wallpaper
# picker. The foldable has two screens with very different shapes, so set each
# from the right physical state:
#   * Inner (near-square 2076x2152) -> set while UNFOLDED, use inner.png
#   * Cover (20:9 1080x2364)        -> set while FOLDED,   use cover.png
#
# Usage:
#   tools/apply-wallpapers.sh day     # push Light Glass pair
#   tools/apply-wallpapers.sh night   # push Night Ride pair
#   tools/apply-wallpapers.sh both    # push everything (default)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WP="$HERE/../wallpapers"
DEST="/sdcard/Pictures/OneQode"

command -v adb >/dev/null || { echo "adb not found"; exit 1; }
adb get-state >/dev/null 2>&1 || { echo "No device. Connect the phone and enable ADB debugging."; exit 1; }

variant="${1:-both}"
adb shell mkdir -p "$DEST" >/dev/null 2>&1 || true

push() {
  local v="$1"
  adb push "$WP/$v/inner.png" "$DEST/OneQode-${v}-inner.png" >/dev/null
  adb push "$WP/$v/cover.png" "$DEST/OneQode-${v}-cover.png" >/dev/null
  echo "  pushed $v (inner + cover)"
}

case "$variant" in
  day|light)  push light-glass ;;
  night|dark) push night-ride ;;
  both|*)     push light-glass; push night-ride ;;
esac

# make them show up in the gallery immediately
adb shell "content call --uri content://media/external/file --method scan_volume" >/dev/null 2>&1 \
  || adb shell "am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file://$DEST" >/dev/null 2>&1 || true

cat <<EOF

Wallpapers are on the phone in: Files/Gallery -> Pictures/OneQode

To set them:
  1. UNFOLD the phone. Long-press the home screen -> Wallpaper & style ->
     choose 'OneQode-<variant>-inner.png'. Position so the OneQode mark sits
     above the fold crease (vertical centre).
  2. FOLD the phone. Repeat on the cover screen with 'OneQode-<variant>-cover.png'.
  3. Enable Material You and (optionally) run tools/oneqode-accent.sh to pin the
     exact OneQode accent.
EOF
