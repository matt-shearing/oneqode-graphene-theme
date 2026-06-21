#!/usr/bin/env bash
# Install the Android emulator + an Android 16 (API 36) system image and create an
# AVD, so the OneQode theme can be tested headlessly on Linux (KVM-accelerated).
set -euo pipefail
SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/.android-sdk-oneqode}"
IMG="system-images;android-36;google_apis;x86_64"
AVD="${AVD_NAME:-oneqode}"
SDKMGR="$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager"
AVDMGR="$SDK_ROOT/cmdline-tools/latest/bin/avdmanager"
export ANDROID_SDK_ROOT="$SDK_ROOT" ANDROID_HOME="$SDK_ROOT"

echo "==> installing emulator + system image ($IMG) ..."
yes | "$SDKMGR" --sdk_root="$SDK_ROOT" --licenses >/dev/null 2>&1 || true
"$SDKMGR" --sdk_root="$SDK_ROOT" "emulator" "$IMG"

echo "==> creating AVD '$AVD' ..."
echo "no" | "$AVDMGR" create avd -n "$AVD" -k "$IMG" -d "pixel_6" --force

# enlarge a couple of settings for a snappier boot
CFG="$HOME/.android/avd/$AVD.avd/config.ini"
if [ -f "$CFG" ]; then
  sed -i 's/^hw.ramSize=.*/hw.ramSize=4096/' "$CFG" 2>/dev/null || true
  grep -q '^hw.ramSize' "$CFG" || echo 'hw.ramSize=4096' >> "$CFG"
fi
echo "EMULATOR_BOOTSTRAP_OK ($AVD)"
