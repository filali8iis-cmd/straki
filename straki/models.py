from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from straki.constants import BLACK_BACK_ROW, RED_BACK_ROW


class Player(Enum):
    RED = "red"
    BLACK = "black"

    @property
    def opponent(self) -> Player:
        return Player.BLACK if self is Player.RED else Player.RED

    @property
    def label_de(self) -> str:
        return "Rot" if self is Player.RED else "Schwarz"

    @property
    def forward(self) -> Direction:
        return Direction.S if self is Player.RED else Direction.N

    @property
    def back_row(self) -> int:
        return RED_BACK_ROW if self is Player.RED else BLACK_BACK_ROW


class Direction(Enum):
    N = "N"
    E = "E"
    S = "S"
    W = "W"

    @property
    def delta(self) -> tuple[int, int]:
        return {
            Direction.N: (1, 0),
            Direction.E: (0, 1),
            Direction.S: (-1, 0),
            Direction.W: (0, -1),
        }[self]

    @property
    def arrow(self) -> str:
        return {Direction.N: "↑", Direction.E: "→", Direction.S: "↓", Direction.W: "←"}[self]


class PieceKind(Enum):
    SOLDIER = "1"
    FROG = "2"
    SMALL = "3"
    SCISSORS = "4"
    BIG = "5"
    SHIELD = "B"
    SPEAR = "A"

    @property
    def name_de(self) -> str:
        return {
            PieceKind.SOLDIER: "Soldat",
            PieceKind.FROG: "Frosch",
            PieceKind.SMALL: "Kleiner Leuchtturm",
            PieceKind.SCISSORS: "Schere",
            PieceKind.BIG: "Großer Leuchtturm",
            PieceKind.SHIELD: "Schild",
            PieceKind.SPEAR: "Speer",
        }[self]

    @property
    def has_facing(self) -> bool:
        return self in {PieceKind.SMALL, PieceKind.BIG}


@dataclass
class Piece:
    player: Player
    kind: PieceKind
    facing: Direction | None = None

    def copy(self) -> Piece:
        return Piece(self.player, self.kind, self.facing)


@dataclass(frozen=True)
class Move:
    start: tuple[int, int]
    end: tuple[int, int]
    capture: bool = False
    rotate_to: Direction | None = None
