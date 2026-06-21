#!/usr/bin/env bash
# Dump every launchable app component on the connected phone, in appfilter.xml
# format, so you can extend the OneQode icon pack to cover apps it doesn't map yet.
#
# Usage:
#   tools/dump-components.sh                 # print all launchable components
#   tools/dump-components.sh signal whats    # filter by keyword(s)
#
# Each line is ready to paste into iconpack/tools/appfilter.py (assign a glyph),
# then re-run forge.py + appfilter.py + build-cli.sh.
set -euo pipefail
command -v adb >/dev/null || { echo "adb not found"; exit 1; }
adb get-state >/dev/null 2>&1 || { echo "No device. Connect the phone and enable ADB debugging."; exit 1; }

# resolve-activity per package gives the launch component
adb shell cmd package query-activities -a android.intent.action.MAIN \
    -c android.intent.category.LAUNCHER 2>/dev/null \
  | grep -oE '[a-zA-Z0-9_.]+/[a-zA-Z0-9_.$]+' \
  | sort -u \
  | while IFS=/ read -r pkg act; do
      [ -z "$act" ] && continue
      line="    <item component=\"ComponentInfo{${pkg}/${act}}\" drawable=\"ic_REPLACE\"/>"
      if [ "$#" -gt 0 ]; then
        for kw in "$@"; do
          if echo "$pkg" | grep -qi "$kw"; then echo "$line"; break; fi
        done
      else
        echo "$line"
      fi
    done
