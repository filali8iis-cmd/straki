# STRAKI

Python-Umsetzung des strategischen Brettspiels **STRAKI** von Athanasios Gakis, nach den offiziellen Regeln auf [straki.org](https://straki.org).

Zwei Spieler bewegen abwechselnd Figuren auf einem **11×11-Brett**. Ziel ist **Nullus motus**: die gegnerische Figur 5 so anzugreifen, dass sie weder fliehen noch sich verteidigen kann.

## Start

Es wird nur Python 3.10+ benötigt.

```bash
python3 -m straki
```

Das öffnet die Partie im Browser unter [http://127.0.0.1:8765](http://127.0.0.1:8765).

```bash
python3 -m straki --ai                 # gegen den Computer (Schwarz)
python3 -m straki --console            # im Terminal
python3 -m straki --console --ai
python3 -m straki --port 9000 --no-browser
```

## Regeln in Kürze

Jeder Spieler hat 18 Figuren. Rot steht oben (Reihen I/J), Schwarz unten (Reihen B/C). Rot beginnt. Ziehen und Schlagen sind getrennte Aktionen.

| Figur | Name | Zug | Angriff |
| --- | --- | --- | --- |
| 1 | Soldat | 1 Feld in jede Richtung | 1 Feld vorwärts |
| 2 | Frosch | 1 Feld in jede Richtung | Sprung 2 Felder diagonal |
| 3 | Kleiner Leuchtturm | 1 Feld in jede Richtung | bis 3 Felder orthogonal |
| 4 | Schere | 1 Feld orthogonal | bis 4 Felder diagonal |
| 5 | Großer Leuchtturm | 1 Feld in jede Richtung | beliebig weit orthogonal |
| B | Schild | 1 Feld in jede Richtung | schlägt nicht |
| A | Speer | 1 Feld in jede Richtung | 1 Feld in jede Richtung |

Besonderheiten laut [Strakiregeln](https://straki.org/zugregeln/):

- Figur 3 und 5 können **rotieren**. Stehen sie hintereinander mit gleicher Blickrichtung, entsteht eine **Fusion**.
- Figur B **schützt** die drei Felder vor sich. Nur Figur A darf geschützte Figuren oder B selbst schlagen. Wird B vorn umkreist, fällt sie aus dem Spiel.
- Ein Angriff auf Figur 5 wird angezeigt. Kann Figur 5 weder fliehen noch gedeckt werden, endet die Partie mit Nullus motus (**1,0 Punkt**).
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
