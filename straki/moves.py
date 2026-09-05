from __future__ import annotations

from straki.board import Board, in_bounds
from straki.constants import (
    DIAG_DIRS,
    KING_DIRS,
    LEAP_DIRS,
    ORTHO_DIRS,
    SCISSORS_RANGE,
    SMALL_RANGE,
)
from straki.models import Direction, Move, Piece, PieceKind, Player


def apply_move(board: Board, move: Move) -> None:
    if move.rotate_to is not None:
        piece = board.get(*move.start)
        if piece is None or not piece.kind.has_facing:
            raise ValueError("Diese Figur kann nicht rotieren")
        piece.facing = move.rotate_to
        return
    piece = board.get(*move.start)
    if piece is None:
        raise ValueError("Kein Stein auf dem Startfeld")
    board.set(*move.start, None)
    board.set(*move.end, piece)


def quiet_destinations(board: Board, row: int, col: int) -> list[tuple[int, int]]:
    piece = board.get(row, col)
    if piece is None:
        return []
    dirs = ORTHO_DIRS if piece.kind is PieceKind.SCISSORS else KING_DIRS
    dests: list[tuple[int, int]] = []
    for d_row, d_col in dirs:
        dest = (row + d_row, col + d_col)
        if in_bounds(*dest) and board.get(*dest) is None:
            dests.append(dest)
    return dests


def attack_destinations(board: Board, row: int, col: int) -> list[tuple[int, int]]:
    piece = board.get(row, col)
    if piece is None or piece.kind is PieceKind.SHIELD:
        return []
    if piece.kind is PieceKind.SOLDIER:
        return _soldier_attacks(board, row, col, piece)
    if piece.kind is PieceKind.FROG:
        return _frog_attacks(board, row, col, piece.player)
    if piece.kind is PieceKind.SMALL:
        rng = _fused_range(board, row, col, piece) or SMALL_RANGE
        return _slide_captures(
            board, row, col, piece.player, _facing_dirs(piece), rng
        )
    if piece.kind is PieceKind.SCISSORS:
        return _slide_captures(board, row, col, piece.player, DIAG_DIRS, SCISSORS_RANGE)
    if piece.kind is PieceKind.BIG:
        return _slide_captures(
            board, row, col, piece.player, _facing_dirs(piece), BOARD_RANGE
        )
    if piece.kind is PieceKind.SPEAR:
        return _adjacent_captures(board, row, col, piece.player, KING_DIRS)
    return []


def attacked_squares(board: Board, row: int, col: int) -> set[tuple[int, int]]:
    """Felder, die diese Figur bedroht (auch leere, für Schach auf Figur 5)."""
    piece = board.get(row, col)
    if piece is None or piece.kind is PieceKind.SHIELD:
        return set()
    if piece.kind is PieceKind.SOLDIER:
        d_row, d_col = piece.player.forward.delta
        dest = (row + d_row, col + d_col)
        return {dest} if in_bounds(*dest) else set()
    if piece.kind is PieceKind.FROG:
        squares = set()
        for d_row, d_col in LEAP_DIRS:
            dest = (row + d_row, col + d_col)
            if in_bounds(*dest):
                squares.add(dest)
        return squares
    if piece.kind is PieceKind.SPEAR:
        return {
            (row + d_row, col + d_col)
            for d_row, d_col in KING_DIRS
            if in_bounds(row + d_row, col + d_col)
        }
    if piece.kind is PieceKind.SCISSORS:
        return _slide_squares(board, row, col, DIAG_DIRS, SCISSORS_RANGE)
    if piece.kind is PieceKind.SMALL:
        rng = _fused_range(board, row, col, piece) or SMALL_RANGE
        return _slide_squares(board, row, col, _facing_dirs(piece), rng)
    if piece.kind is PieceKind.BIG:
        return _slide_squares(board, row, col, _facing_dirs(piece), BOARD_RANGE)
    return set()


def legal_moves(board: Board, row: int, col: int) -> list[Move]:
    piece = board.get(row, col)
    if piece is None:
        return []
    moves = [Move((row, col), dest) for dest in quiet_destinations(board, row, col)]
    moves.extend(
        Move((row, col), dest, capture=True)
        for dest in attack_destinations(board, row, col)
    )
    if piece.kind.has_facing and piece.facing is not None:
        for direction in Direction:
            if direction is not piece.facing:
                moves.append(Move((row, col), (row, col), rotate_to=direction))
    return moves


def protected_squares(board: Board, row: int, col: int) -> set[tuple[int, int]]:
    piece = board.get(row, col)
    if piece is None or piece.kind is not PieceKind.SHIELD:
        return set()
    facing = piece.facing or piece.player.forward
    d_row, d_col = facing.delta
    squares: set[tuple[int, int]] = set()
    for side in (-1, 0, 1):
        if d_row != 0:
            dest = (row + d_row, col + side)
        else:
            dest = (row + side, col + d_col)
        if in_bounds(*dest):
            squares.add(dest)
    return squares


def is_protected_by_enemy(board: Board, row: int, col: int, attacker: Player) -> bool:
    defender = attacker.opponent
    for s_row, s_col, piece in board.pieces(defender):
        if piece.kind is PieceKind.SHIELD and (row, col) in protected_squares(
            board, s_row, s_col
        ):
            return True
    return False


# U-Form eine Reihe weiter vorn (Beispiel 6: B auf F5 nach Süden → E4, D4, D5, D6, E6).
_FAR_U_OFFSETS = ((1, -1), (2, -1), (2, 0), (2, 1), (1, 1))
# U-Form direkt an B: beide Seiten plus drei Felder auf einer Seite
# (B auf F6 nach Norden → F5, G5, G6, G7, F7).
_CLOSE_U_OFFSETS = ((0, -1), (1, -1), (1, 0), (1, 1), (0, 1))


def encirclement_squares(board: Board, row: int, col: int) -> set[tuple[int, int]]:
    """Felder der U-Form in Blickrichtung von Figur B (nur Felder auf dem Brett)."""
    piece = board.get(row, col)
    if piece is None or piece.kind is not PieceKind.SHIELD:
        return set()
    facing = piece.facing or piece.player.forward
    return {
        dest
        for dest in _encircle_slots(row, col, facing, _FAR_U_OFFSETS)
        if dest is not None
    }


def shield_is_encircled(board: Board, row: int, col: int) -> bool:
    """Figur B fällt, wenn gegnerische Figuren sie umkreisen."""
    piece = board.get(row, col)
    if piece is None or piece.kind is not PieceKind.SHIELD:
        return False
    if _orthogonally_boxed(board, row, col, piece.player):
        return True
    for facing in Direction:
        if _u_closed_by_enemy(board, row, col, piece.player, facing, _CLOSE_U_OFFSETS):
            return True
        if _u_closed_by_enemy(board, row, col, piece.player, facing, _FAR_U_OFFSETS):
            return True
    return False


def fusion_partner(
    board: Board, row: int, col: int, piece: Piece
) -> tuple[int, int, Piece] | None:
    if piece.kind not in {PieceKind.SMALL, PieceKind.BIG} or piece.facing is None:
        return None
    other_kind = PieceKind.BIG if piece.kind is PieceKind.SMALL else PieceKind.SMALL
    d_row, d_col = piece.facing.delta
    ahead = board.get(row + d_row, col + d_col)
    behind = board.get(row - d_row, col - d_col)
    if (
        ahead is not None
        and ahead.player is piece.player
        and ahead.kind is other_kind
        and ahead.facing is piece.facing
    ):
        return row + d_row, col + d_col, ahead
    if (
        behind is not None
        and behind.player is piece.player
        and behind.kind is other_kind
        and behind.facing is piece.facing
    ):
        return row - d_row, col - d_col, behind
    return None


def _fused_range(board: Board, row: int, col: int, piece: Piece) -> int | None:
    """Große Fusion: Figur 5 steht hinter Figur 3 → Figur 3 greift bis zum Rand an."""
    if piece.kind is not PieceKind.SMALL or piece.facing is None:
        return None
    partner = fusion_partner(board, row, col, piece)
    if partner is None:
        return None
    p_row, p_col, other = partner
    d_row, d_col = piece.facing.delta
    # Partner muss hinter dieser Figur 3 stehen.
    if (p_row, p_col) == (row - d_row, col - d_col) and other.kind is PieceKind.BIG:
        return BOARD_RANGE
    return None


def _soldier_attacks(
    board: Board, row: int, col: int, piece: Piece
) -> list[tuple[int, int]]:
    d_row, d_col = piece.player.forward.delta
    dest = (row + d_row, col + d_col)
    target = board.get(*dest) if in_bounds(*dest) else None
    if target is not None and target.player is not piece.player:
        return [dest]
    return []


def _frog_attacks(
    board: Board, row: int, col: int, player: Player
) -> list[tuple[int, int]]:
    dests: list[tuple[int, int]] = []
    for d_row, d_col in LEAP_DIRS:
        dest = (row + d_row, col + d_col)
        target = board.get(*dest) if in_bounds(*dest) else None
        if target is not None and target.player is not player:
            dests.append(dest)
    return dests


def _adjacent_captures(
    board: Board,
    row: int,
    col: int,
    player: Player,
    dirs: tuple[tuple[int, int], ...],
) -> list[tuple[int, int]]:
    dests: list[tuple[int, int]] = []
    for d_row, d_col in dirs:
        dest = (row + d_row, col + d_col)
        target = board.get(*dest) if in_bounds(*dest) else None
        if target is not None and target.player is not player:
            dests.append(dest)
    return dests


BOARD_RANGE = 11


def _facing_dirs(piece: Piece) -> tuple[tuple[int, int], ...]:
    """Leuchttürme greifen nur in die Richtung, in die der Kopf zeigt."""
    facing = piece.facing or piece.player.forward
    return (facing.delta,)


def _encircle_slots(
    row: int,
    col: int,
    facing: Direction,
    offsets: tuple[tuple[int, int], ...],
) -> tuple[tuple[int, int] | None, ...]:
    d_row, d_col = facing.delta
    slots: list[tuple[int, int] | None] = []
    for dist, side in offsets:
        if d_row != 0:
            dest = (row + dist * d_row, col + side)
        else:
            dest = (row + side, col + dist * d_col)
        slots.append(dest if in_bounds(*dest) else None)
    return tuple(slots)


def _orthogonally_boxed(board: Board, row: int, col: int, owner: Player) -> bool:
    """B ist orthogonal umkreist: jedes Nachbarfeld Gegner oder außerhalb."""
    saw_enemy = False
    for d_row, d_col in ORTHO_DIRS:
        dest = (row + d_row, col + d_col)
        if not in_bounds(*dest):
            continue
        occupant = board.get(*dest)
        if occupant is None or occupant.player is owner:
            return False
        saw_enemy = True
    return saw_enemy


def _u_closed_by_enemy(
    board: Board,
    row: int,
    col: int,
    owner: Player,
    facing: Direction,
    offsets: tuple[tuple[int, int], ...],
) -> bool:
    saw_enemy = False
    for dest in _encircle_slots(row, col, facing, offsets):
        if dest is None:
            continue
        occupant = board.get(*dest)
        if occupant is None or occupant.player is owner:
            return False
        saw_enemy = True
    return saw_enemy


def _slide_captures(
    board: Board,
    row: int,
    col: int,
    player: Player,
    dirs: tuple[tuple[int, int], ...],
    max_range: int,
) -> list[tuple[int, int]]:
    dests: list[tuple[int, int]] = []
    for d_row, d_col in dirs:
        for step in range(1, max_range + 1):
            dest = (row + step * d_row, col + step * d_col)
            if not in_bounds(*dest):
                break
            occupant = board.get(*dest)
            if occupant is None:
                continue
            if occupant.player is not player:
                dests.append(dest)
            break
    return dests


def _slide_squares(
    board: Board,
    row: int,
    col: int,
    dirs: tuple[tuple[int, int], ...],
    max_range: int,
) -> set[tuple[int, int]]:
    squares: set[tuple[int, int]] = set()
    for d_row, d_col in dirs:
        for step in range(1, max_range + 1):
            dest = (row + step * d_row, col + step * d_col)
            if not in_bounds(*dest):
                break
            squares.add(dest)
            if board.get(*dest) is not None:
                break
    return squares
