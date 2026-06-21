#!/usr/bin/env bash
# Build & sign the OneQode Theme companion app (aapt2 + javac + d8 + apksigner).
# Reuses the headless SDK from tools/bootstrap-sdk.sh and the shared keystore.
set -euo pipefail

SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/.android-sdk-oneqode}"
BUILD_TOOLS_VER="${BUILD_TOOLS_VER:-35.0.0}"
PLATFORM="${PLATFORM:-android-36}"

BT="$SDK_ROOT/build-tools/$BUILD_TOOLS_VER"
ANDROID_JAR="$SDK_ROOT/platforms/$PLATFORM/android.jar"
AAPT2="$BT/aapt2"; D8="$BT/d8"; ZIPALIGN="$BT/zipalign"; APKSIGNER="$BT/apksigner"

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/app/src/main"
RES="$SRC/res"; ASSETS="$SRC/assets"; MANIFEST="$SRC/AndroidManifest.xml"
OUT="$HERE/build"; DIST="$HERE/../dist"
KS="$HERE/../iconpack/keystore/oneqode-release.jks"
KS_PASS="${KS_PASS:-oneqode}"; KS_ALIAS="${KS_ALIAS:-oneqode}"

for t in "$AAPT2" "$D8" "$ZIPALIGN" "$APKSIGNER" "$ANDROID_JAR"; do
  [ -e "$t" ] || { echo "ERROR: missing $t — run tools/bootstrap-sdk.sh first"; exit 1; }
done
[ -f "$KS" ] || { echo "ERROR: keystore $KS missing — build the icon pack once first"; exit 1; }

rm -rf "$OUT"; mkdir -p "$OUT/compiled" "$OUT/gen" "$OUT/classes" "$DIST"

echo "==> aapt2 compile"
"$AAPT2" compile --dir "$RES" -o "$OUT/compiled/res.zip"

echo "==> aapt2 link"
"$AAPT2" link -o "$OUT/base-unsigned.apk" -I "$ANDROID_JAR" \
  --manifest "$MANIFEST" --java "$OUT/gen" -A "$ASSETS" \
  --min-sdk-version 26 --target-sdk-version 36 \
  --version-code "${VERSION_CODE:-1}" --version-name "${VERSION_NAME:-1.0.0}" \
  "$OUT/compiled/res.zip"

echo "==> javac"
RJAVA="$(find "$OUT/gen" -name R.java)"
javac --release 11 -classpath "$ANDROID_JAR" -d "$OUT/classes" \
  $RJAVA $(find "$SRC/java" -name "*.java")

echo "==> d8 -> dex"
"$D8" --release --lib "$ANDROID_JAR" --output "$OUT" $(find "$OUT/classes" -name "*.class")

echo "==> add classes.dex"
cp "$OUT/base-unsigned.apk" "$OUT/app-unaligned.apk"
python3 - "$OUT/app-unaligned.apk" "$OUT/classes.dex" <<'PY'
import sys, zipfile
with zipfile.ZipFile(sys.argv[1], "a", zipfile.ZIP_DEFLATED) as z:
    z.write(sys.argv[2], "classes.dex")
PY

echo "==> zipalign + sign"
"$ZIPALIGN" -p -f 4 "$OUT/app-unaligned.apk" "$OUT/app-aligned.apk"
APK="$DIST/oneqode-theme-release.apk"
"$APKSIGNER" sign --ks "$KS" --ks-pass "pass:$KS_PASS" --key-pass "pass:$KS_PASS" \
  --ks-key-alias "$KS_ALIAS" --v2-signing-enabled true --v3-signing-enabled true \
  --out "$APK" "$OUT/app-aligned.apk"
"$APKSIGNER" verify "$APK" >/dev/null && echo "    signature OK"
echo "BUILD OK -> $APK"; ls -lh "$APK" | awk '{print "    size:", $5}'
