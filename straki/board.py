from __future__ import annotations

from straki.constants import BLACK_BACK_ROW, BLACK_FRONT_ROW, BOARD_SIZE, COLS, RED_BACK_ROW, RED_FRONT_ROW, ROWS
from straki.models import Direction, Piece, PieceKind, Player


def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def square_name(row: int, col: int) -> str:
    return f"{ROWS[row]}{col + 1}"


def parse_square(text: str) -> tuple[int, int]:
    raw = text.strip().upper().replace(" ", "")
    if len(raw) < 2 or raw[0] not in ROWS:
        raise ValueError(f"Ungültiges Feld: {text!r}")
    try:
        number = int(raw[1:])
    except ValueError as exc:
        raise ValueError(f"Ungültiges Feld: {text!r}") from exc
    row = ROWS.index(raw[0])
    col = number - 1
    if number not in COLS:
        raise ValueError(f"Ungültiges Feld: {text!r}")
    return row, col


class Board:
    def __init__(self, setup: bool = True) -> None:
        self.cells: list[list[Piece | None]] = [
            [None] * BOARD_SIZE for _ in range(BOARD_SIZE)
        ]
        if setup:
            self.setup_initial()

    def clear(self) -> None:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                self.cells[row][col] = None

    def get(self, row: int, col: int) -> Piece | None:
        if not in_bounds(row, col):
            return None
        return self.cells[row][col]

    def set(self, row: int, col: int, piece: Piece | None) -> None:
        self.cells[row][col] = piece

    def pieces(self, player: Player | None = None) -> list[tuple[int, int, Piece]]:
        found: list[tuple[int, int, Piece]] = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.cells[row][col]
                if piece is None:
                    continue
                if player is None or piece.player is player:
                    found.append((row, col, piece))
        return found

    def find(self, player: Player, kind: PieceKind) -> list[tuple[int, int, Piece]]:
        return [
            (row, col, piece)
            for row, col, piece in self.pieces(player)
            if piece.kind is kind
        ]

    def king_square(self, player: Player) -> tuple[int, int] | None:
        found = self.find(player, PieceKind.BIG)
        if not found:
            return None
        return found[0][0], found[0][1]

    def copy(self) -> Board:
        clone = Board(setup=False)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.cells[row][col]
                clone.cells[row][col] = piece.copy() if piece else None
        return clone

    def as_list(self) -> list[dict[str, object]]:
        data: list[dict[str, object]] = []
        for row, col, piece in self.pieces():
            data.append(
                {
                    "row": row,
                    "col": col,
                    "square": square_name(row, col),
                    "player": piece.player.value,
                    "kind": piece.kind.value,
                    "name": piece.kind.name_de,
                    "facing": piece.facing.value if piece.facing else None,
                }
            )
        return data

    def setup_initial(self) -> None:
        self.clear()
        self._place_side(
            Player.BLACK,
            back=BLACK_BACK_ROW,
            front=BLACK_FRONT_ROW,
            facing=Direction.N,
        )
        self._place_side(
            Player.RED,
            back=RED_BACK_ROW,
            front=RED_FRONT_ROW,
            facing=Direction.S,
        )

    def _place_side(
        self,
        player: Player,
        back: int,
        front: int,
        facing: Direction,
    ) -> None:
        # Hinterreihe: A 2 3 4 5 4 3 2 A in Spalten 2–10
        back_kinds = [
            PieceKind.SPEAR,
            PieceKind.FROG,
            PieceKind.SMALL,
            PieceKind.SCISSORS,
            PieceKind.BIG,
            PieceKind.SCISSORS,
            PieceKind.SMALL,
            PieceKind.FROG,
            PieceKind.SPEAR,
        ]
        for offset, kind in enumerate(back_kinds):
            col = 1 + offset
            face = facing if kind.has_facing else None
            self.set(back, col, Piece(player, kind, face))
        for col in range(1, 10):
            if col == 5:
                self.set(front, col, Piece(player, PieceKind.SHIELD))
            else:
                self.set(front, col, Piece(player, PieceKind.SOLDIER))
