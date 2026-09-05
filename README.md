# STRAKI

Python-Umsetzung des strategischen Brettspiels **STRAKI** von Athanasios Gakis, nach den offiziellen Regeln auf [straki.org](https://straki.org).

Zwei Spieler bewegen abwechselnd Figuren auf einem **11×11-Brett**. Ziel ist **Nullus motus**: die gegnerische Figur 5 so anzugreifen, dass sie weder fliehen noch sich verteidigen kann.

## STRAKI.exe herunterladen (Windows)

Fertige Datei, **kein Python** nötig: doppelklicken und spielen.

**[STRAKI.exe herunterladen](https://github.com/filali8iis-cmd/straki/raw/cursor/straki-windows-exe-7437/downloads/STRAKI.exe)**

Dieselbe Datei liegt im Repository unter [`downloads/STRAKI.exe`](https://github.com/filali8iis-cmd/straki/blob/cursor/straki-windows-exe-7437/downloads/STRAKI.exe) (Button **Download raw file**).

Nach dem Merge nach `main` gilt zusätzlich:

- [Release-Download](https://github.com/filali8iis-cmd/straki/releases/latest/download/STRAKI.exe)
- GitHub → **Actions** → Workflow **Build STRAKI.exe** → Artefakt **STRAKI-Windows**

Windows kann beim ersten Start SmartScreen anzeigen, weil die Datei nicht digital signiert ist: *Weitere Informationen* → *Trotzdem ausführen*.

Lokal selbst bauen (auf einem Windows-PC):

```powershell
pip install -r requirements.txt pyinstaller pillow
python scripts/build_exe.py
```

Die fertige Datei liegt dann in `dist/STRAKI.exe`.

## Start mit Python

```bash
pip install -r requirements.txt
python3 -m straki
```

Das öffnet ein **eigenes Spielfenster** (pygame): Brett, Figuren, Klicks, Rotation und Computergegner.

```bash
python3 -m straki --ai          # gegen den Computer (Schwarz)
python3 -m straki --console     # nur Terminal
python3 -m straki --web         # optional im Browser
```

Steuerung im Fenster: Figur anklicken, Ziel anklicken. Figuren 3 und 5 lassen sich über die Pfeil-Buttons rotieren. Esc beendet, bzw. schließt die Regeln.

## Regeln in Kürze

Jeder Spieler hat 18 Figuren. Rot steht oben (Reihen I/J), Schwarz unten (Reihen B/C). Rot beginnt. Ziehen und Schlagen sind getrennte Aktionen.

| Figur | Name | Zug | Angriff |
| --- | --- | --- | --- |
| 1 | Soldat | 1 Feld in jede Richtung | 1 Feld vorwärts |
| 2 | Frosch | 1 Feld in jede Richtung | Sprung 2 Felder diagonal |
| 3 | Kleiner Leuchtturm | 1 Feld in jede Richtung (unabhängig vom Kopf) | nur in Blickrichtung, bis 3 Felder |
| 4 | Schere | 1 Feld orthogonal | bis 4 Felder diagonal |
| 5 | Großer Leuchtturm | 1 Feld in jede Richtung (unabhängig vom Kopf) | nur in Blickrichtung, beliebig weit |
| B | Schild | beliebiges leeres Feld | schlägt nicht |
| A | Speer | 1 Feld in jede Richtung | 1 Feld in jede Richtung |

Besonderheiten laut [Strakiregeln](https://straki.org/zugregeln/):

- Figur 3 und 5 können **rotieren**. Der **Zug** ist unabhängig vom Kopf, der **Angriff** geht nur dorthin, wo der Kopf zeigt. Stehen sie hintereinander mit gleicher Blickrichtung, entsteht eine **Fusion**.
- Figur B **schützt** die drei Felder vor sich. Nur Figur A darf geschützte Figuren oder B selbst schlagen. Wird B von gegnerischen Figuren **umkreist** (alle vier Seiten oder die U-Form), verliert sie den Schutz und wird aus dem Spiel entfernt.
- Ein Angriff auf Figur 5 wird angezeigt. Figur 5 kann von **jeder** gegnerischen Figur (außer B) geschlagen werden, wenn die Linie frei ist. Schlagen oder Nullus motus: **1,0 Punkt**.
- Beide gegnerischen Speere schlagen: **0,5 Punkte**. Beides zusammen: perfekter Sieg **1,5 Punkte**.

Die vollständigen Regeln, Figurenbilder und Beispiele stehen auf der Website:

- [Das Brett](https://straki.org/das-brett/)
- [Die Figuren](https://straki.org/figuren/)
- [Strakiregeln (PDF)](https://straki.org/wp-content/uploads/2021/04/STRAKI.pdf)
- [Beispiel 1](https://straki.org/beispiel-1/)

## Terminal

Felder werden als Reihe + Spalte geschrieben, z. B. `C6` oder `J4`.

```
C6 D6       Figur von C6 nach D6
C6          Figur wählen und Ziele anzeigen
rotier N    Blickrichtung der gewählten Figur 3 oder 5
halb        0,5 Punkte nehmen, wenn beide Speere geschlagen sind
ki          Computer ein/aus
neu         neue Partie
hilfe       Regeln
ende        Beenden
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```
