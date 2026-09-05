# STRAKI bei Google Play hochladen

Paketname: `org.straki.android`  
Version: `1.0` (versionCode 1)

## Welche Datei wohin

| Datei | Zweck |
| --- | --- |
| `downloads/STRAKI.aab` | **Diese Datei bei Google Play hochladen** (Play Console → Produktion / Test) |
| `downloads/STRAKI.apk` | Zum Ausprobieren auf dem eigenen Android-Handy (nicht die Play-Datei) |
| `straki-play-upload.jks` | Upload-Schlüssel. **Privat behalten.** Ohne ihn keine Updates. |

Neue Apps bei Google Play brauchen ein **Android App Bundle (.aab)**, keine APK.

## Konto

1. [Google Play Console](https://play.google.com/console) öffnen.
2. Einmalig das Entwicklerkonto anlegen (Gebühr, Ausweis).
3. App erstellen: Name **STRAKI**, Kategorie Spiel / Brettspiel.
4. Standard-App (keine Gebühren in der App).

## Upload

1. Play Console → deine App → **Produktion** oder zuerst **Interner Test**.
2. Neuen Release anlegen.
3. `STRAKI.aab` hochladen.
4. Play App Signing aktivieren (empfohlen). Dein `straki-play-upload.jks` bleibt der **Upload-Key**.
5. Store-Eintrag ausfüllen: Kurztext, Beschreibung, Icon (512×512), Screenshots (Handy).
6. Jugendschutz-Fragebogen, Datenschutz-URL.
7. Zur Prüfung senden.

Datenschutz-Text liegt unter [`docs/privacy.de.html`](privacy.de.html). Nach dem Push kannst du diese URL verwenden:

`https://github.com/filali8iis-cmd/straki/blob/cursor/straki-android-apk-7437/docs/privacy.de.html`

## Neu bauen

```bash
export ANDROID_HOME="$HOME/android-sdk"
# vorhandenen Upload-Key und signing.properties nach android/keystore/ legen
bash scripts/build_apk.sh
```

Nächste Play-Version: in `android/app/build.gradle` `versionCode` erhöhen (2, 3, …) und `versionName` anpassen.
