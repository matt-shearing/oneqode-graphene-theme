#!/usr/bin/env bash
# Build & sign the OneQode icon pack APK without Android Studio / Gradle.
# Uses aapt2 + javac + d8 + zipalign + apksigner from the SDK bootstrapped by
# ../tools/bootstrap-sdk.sh. Idempotent.
set -euo pipefail

SDK_ROOT="${ANDROID_SDK_ROOT:-$HOME/.android-sdk-oneqode}"
BUILD_TOOLS_VER="${BUILD_TOOLS_VER:-35.0.0}"
PLATFORM="${PLATFORM:-android-36}"

BT="$SDK_ROOT/build-tools/$BUILD_TOOLS_VER"
ANDROID_JAR="$SDK_ROOT/platforms/$PLATFORM/android.jar"
AAPT2="$BT/aapt2"; D8="$BT/d8"; ZIPALIGN="$BT/zipalign"; APKSIGNER="$BT/apksigner"

HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$HERE/app"
SRC="$APP/src/main"
RES="$SRC/res"
MANIFEST="$SRC/AndroidManifest.xml"
OUT="$HERE/build"
DIST="$HERE/../dist"
KS="$HERE/keystore/oneqode-release.jks"
KS_PASS="${KS_PASS:-oneqode}"
KS_ALIAS="${KS_ALIAS:-oneqode}"

for t in "$AAPT2" "$D8" "$ZIPALIGN" "$APKSIGNER" "$ANDROID_JAR"; do
  [ -e "$t" ] || { echo "ERROR: missing $t — run tools/bootstrap-sdk.sh first"; exit 1; }
done
command -v javac >/dev/null || { echo "ERROR: javac (JDK) not found"; exit 1; }

rm -rf "$OUT"; mkdir -p "$OUT/compiled" "$OUT/gen" "$OUT/classes" "$DIST"

echo "==> keystore"
if [ ! -f "$KS" ]; then
  mkdir -p "$(dirname "$KS")"
  keytool -genkeypair -v -keystore "$KS" -storepass "$KS_PASS" -keypass "$KS_PASS" \
    -alias "$KS_ALIAS" -keyalg RSA -keysize 4096 -validity 10000 \
    -dname "CN=OneQode, O=OneQode, C=AU" >/dev/null 2>&1
  echo "    created $KS (password: $KS_PASS — rotate for production/Accrescent)"
else
  echo "    using existing $KS"
fi

echo "==> aapt2 compile resources"
"$AAPT2" compile --dir "$RES" -o "$OUT/compiled/res.zip"

echo "==> aapt2 link"
"$AAPT2" link \
  -o "$OUT/base-unsigned.apk" \
  -I "$ANDROID_JAR" \
  --manifest "$MANIFEST" \
  --java "$OUT/gen" \
  --min-sdk-version 26 \
  --target-sdk-version 36 \
  --version-code "${VERSION_CODE:-1}" \
  --version-name "${VERSION_NAME:-1.0.0}" \
  "$OUT/compiled/res.zip"

echo "==> javac"
RJAVA="$(find "$OUT/gen" -name R.java)"
javac --release 11 -classpath "$ANDROID_JAR" -d "$OUT/classes" \
  $RJAVA "$SRC/java/com/oneqode/iconpack/MainActivity.java"

echo "==> d8 -> dex"
CLASSFILES=$(find "$OUT/classes" -name "*.class")
"$D8" --release --lib "$ANDROID_JAR" --output "$OUT" $CLASSFILES

echo "==> add classes.dex to apk"
cp "$OUT/base-unsigned.apk" "$OUT/app-unaligned.apk"
python3 - "$OUT/app-unaligned.apk" "$OUT/classes.dex" <<'PY'
import sys, zipfile
apk, dex = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(apk, "a", zipfile.ZIP_DEFLATED) as z:
    z.write(dex, "classes.dex")
PY

echo "==> zipalign"
"$ZIPALIGN" -p -f 4 "$OUT/app-unaligned.apk" "$OUT/app-aligned.apk"

echo "==> apksigner (v2+v3)"
APK="$DIST/oneqode-iconpack-release.apk"
"$APKSIGNER" sign \
  --ks "$KS" --ks-pass "pass:$KS_PASS" --key-pass "pass:$KS_PASS" --ks-key-alias "$KS_ALIAS" \
  --v2-signing-enabled true --v3-signing-enabled true \
  --out "$APK" "$OUT/app-aligned.apk"

"$APKSIGNER" verify --verbose "$APK" | sed 's/^/    /'
echo
echo "BUILD OK -> $APK"
ls -lh "$APK" | awk '{print "    size:", $5}'
