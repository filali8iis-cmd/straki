"""Offizielle STRAKI-Konstanten nach straki.org / Athanasios Gakis."""

from __future__ import annotations

BOARD_SIZE = 11
ROWS = "ABCDEFGHIJK"  # A unten, K oben
COLS = tuple(range(1, BOARD_SIZE + 1))

# Rot steht oben (Reihen I/J), Schwarz unten (Reihen B/C).
RED_BACK_ROW = 9  # J
RED_FRONT_ROW = 8  # I
BLACK_BACK_ROW = 1  # B
BLACK_FRONT_ROW = 2  # C

KING_DIRS = (
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
)
ORTHO_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIAG_DIRS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
LEAP_DIRS = ((2, 2), (2, -2), (-2, 2), (-2, -2))

# Werte laut Regelwerk (Figur 5 ist die Königfigur und hat keinen Tauschwert).
PIECE_VALUE = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "B": 5,
    "A": 7,
    "5": 100,
}

SCISSORS_RANGE = 4
SMALL_RANGE = 3

RULES_DE = """
STRAKI (Athanasios Gakis) – Kurzregeln nach straki.org

Brett: 11×11 Felder (Spalten 1–11, Reihen A–K, A unten).
Jeder Spieler hat 18 Figuren. Rot steht oben, Schwarz unten. Rot beginnt.

Ziel: Nullus motus – die gegnerische Figur 5 so angreifen, dass sie
weder fliehen noch sich verteidigen kann.

Figuren je Seite:
  8× Figur 1 Soldat     ziehen: 1 Feld in jede Richtung; schlagen: 1 Feld vorwärts
  2× Figur 2 Frosch     ziehen: 1 Feld in jede Richtung; schlagen: Sprung 2 diagonal
  2× Figur 3 kl. Leuchtturm  ziehen: 1 Feld jede Richtung (unabhängig vom Kopf);
                               schlagen: nur in Blickrichtung, bis 3 Felder
  2× Figur 4 Schere     ziehen: 1 Feld orthogonal; schlagen: bis 4 diagonal
  1× Figur 5 gr. Leuchtturm  ziehen: 1 Feld jede Richtung (unabhängig vom Kopf);
                               schlagen: nur in Blickrichtung, beliebig weit
  1× Figur B Schild     ziehen: 1 Feld jede Richtung; schlägt nicht; schützt 3 Felder davor
  2× Figur A Speer      ziehen/schlagen: 1 Feld in jede Richtung; einzig gegen B wirksam

Besonderheiten:
  • Figur 3 und 5 können rotieren (Blickrichtung = Kopf). Der Zug ist unabhängig
    vom Kopf. Angreifen dürfen sie nur dort, wo der Kopf zeigt. Fusion, wenn
    beide gleich blicken und Figur 5 hinter Figur 3 steht – Figur 3 greift dann
    in Blickrichtung bis zum Brettrand an.
  • Figur B schützt die drei Felder vor sich. Nur Figur A darf geschützte Figuren
    oder B selbst schlagen. Wird B von gegnerischen Figuren umkreist (U-Form
    aus fünf Feldern, am Rand schließt das Brett), verliert sie den Schutz
    und wird aus dem Spiel entfernt.
  • Wer Figur 5 angreift, warnt („Angriff auf Figur 5“).
  • Beide gegnerischen Figuren A schlagen: 0,5 Punkte (Aufgabe möglich).
  • Nullus motus: 1,0 Punkte. Beides: perfekter Sieg 1,5 Punkte.
""".strip()
