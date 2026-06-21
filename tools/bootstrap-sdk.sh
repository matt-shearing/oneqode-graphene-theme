#!/usr/bin/env bash
# Bootstrap a minimal headless Android SDK for building the OneQode icon pack.
# Installs into $ANDROID_SDK_ROOT (default: ~/.android-sdk-oneqode) so it never
# touches a system-wide SDK. Idempotent: safe to re-run.
set -euo pipefail

SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/.android-sdk-oneqode}"
CLT_VER="11076708"   # cmdline-tools 13.0 (latest stable as of 2026)
BUILD_TOOLS="35.0.0"
PLATFORM="android-36" # Android 16 = API 36
CLT_ZIP="commandlinetools-linux-${CLT_VER}_latest.zip"
CLT_URL="https://dl.google.com/android/repository/${CLT_ZIP}"

echo "==> SDK root: $SDK_ROOT"
mkdir -p "$SDK_ROOT/cmdline-tools"

if [ ! -x "$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" ]; then
  echo "==> Downloading command-line tools..."
  tmp="$(mktemp -d)"
  curl -fL --retry 3 -o "$tmp/$CLT_ZIP" "$CLT_URL"
  echo "==> Unpacking..."
  unzip -q "$tmp/$CLT_ZIP" -d "$tmp"
  rm -rf "$SDK_ROOT/cmdline-tools/latest"
  mv "$tmp/cmdline-tools" "$SDK_ROOT/cmdline-tools/latest"
  rm -rf "$tmp"
else
  echo "==> cmdline-tools already present"
fi

export ANDROID_SDK_ROOT="$SDK_ROOT"
export ANDROID_HOME="$SDK_ROOT"
SDKMGR="$SDK_ROOT/cmdline-tools/latest/bin/sdkmanager"

echo "==> Accepting licenses..."
yes | "$SDKMGR" --sdk_root="$SDK_ROOT" --licenses >/dev/null 2>&1 || true

echo "==> Installing platform-tools, build-tools $BUILD_TOOLS, platform $PLATFORM..."
"$SDKMGR" --sdk_root="$SDK_ROOT" \
  "platform-tools" \
  "build-tools;${BUILD_TOOLS}" \
  "platforms;${PLATFORM}"

echo "==> Done. Installed packages:"
"$SDKMGR" --sdk_root="$SDK_ROOT" --list_installed 2>/dev/null || true
echo "ANDROID_SDK_ROOT=$SDK_ROOT"
echo "BOOTSTRAP_OK"
