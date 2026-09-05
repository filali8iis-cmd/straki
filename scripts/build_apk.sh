#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export ANDROID_HOME="${ANDROID_HOME:-$HOME/android-sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-21-openjdk-amd64}"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

if [[ ! -d "$ANDROID_HOME/platforms" ]]; then
  echo "Android SDK fehlt unter $ANDROID_HOME" >&2
  exit 1
fi

python3 scripts/prepare_android_icons.py
npx cap sync android

KEY_DIR="$ROOT/android/keystore"
mkdir -p "$KEY_DIR"
KEYSTORE="$KEY_DIR/straki-upload.jks"
PROPS="$KEY_DIR/signing.properties"
if [[ -f "$PROPS" ]]; then
  # Bestehende Upload-Signatur wiederverwenden.
  STORE_PASS="$(sed -n 's/^storePassword=//p' "$PROPS")"
else
  STORE_PASS="${STRAKI_KEYSTORE_PASS:-$(openssl rand -base64 24)}"
fi
if [[ ! -f "$KEYSTORE" ]]; then
  keytool -genkeypair -v \
    -keystore "$KEYSTORE" \
    -alias upload \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass "$STORE_PASS" \
    -keypass "$STORE_PASS" \
    -dname "CN=STRAKI, OU=STRAKI, O=STRAKI, L=Unknown, ST=Unknown, C=DE"
fi
cat > "$PROPS" <<EOF
storeFile=$KEYSTORE
storePassword=$STORE_PASS
keyAlias=upload
keyPassword=$STORE_PASS
EOF

echo "sdk.dir=$ANDROID_HOME" > "$ROOT/android/local.properties"

cd "$ROOT/android"
./gradlew --no-daemon assembleRelease bundleRelease

mkdir -p "$ROOT/downloads"
cp -f "$ROOT/android/app/build/outputs/apk/release/app-release.apk" "$ROOT/downloads/STRAKI.apk"
cp -f "$ROOT/android/app/build/outputs/bundle/release/app-release.aab" "$ROOT/downloads/STRAKI.aab"
mkdir -p /opt/cursor/artifacts
cp -f "$ROOT/downloads/STRAKI.apk" /opt/cursor/artifacts/STRAKI.apk
cp -f "$ROOT/downloads/STRAKI.aab" /opt/cursor/artifacts/STRAKI.aab
cp -f "$KEYSTORE" /opt/cursor/artifacts/straki-play-upload.jks
printf '%s\n' \
  "Keystore-Alias: upload" \
  "Passwort: $STORE_PASS" \
  "Datei: straki-play-upload.jks" \
  "Diese Datei und das Passwort sicher aufbewahren. Ohne sie kannst du die App bei Google Play nicht aktualisieren." \
  > /opt/cursor/artifacts/STRAKI_Play_Upload_Key.txt

echo "Fertig:"
echo "  downloads/STRAKI.apk"
echo "  downloads/STRAKI.aab"
file "$ROOT/downloads/STRAKI.apk" "$ROOT/downloads/STRAKI.aab"
