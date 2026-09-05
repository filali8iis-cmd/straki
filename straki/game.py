from __future__ import annotations

from straki.board import Board, parse_square, square_name
from straki.models import Direction, Move, PieceKind, Player
from straki.moves import (
    apply_move,
    attacked_squares,
    is_protected_by_enemy,
    legal_moves as raw_legal_moves,
    shield_is_encircled,
)


class Game:
    def __init__(self, vs_ai: bool = False, setup: bool = True) -> None:
        self.board = Board(setup=setup)
        self.turn = Player.RED
        self.vs_ai = vs_ai
        self.ai_player = Player.BLACK
        self.selected: tuple[int, int] | None = None
        self.winner: Player | None = None
        self.win_reason: str | None = None
        self.score: float = 0.0
        self.message = "Rot beginnt."
        self.last_move: dict[str, object] | None = None
        self.check = False
        self.captured: dict[Player, list[str]] = {Player.RED: [], Player.BLACK: []}

    def reset(self, vs_ai: bool | None = None) -> None:
        self.__init__(vs_ai=self.vs_ai if vs_ai is None else vs_ai)

    def click(self, row: int, col: int) -> bool:
        if self.winner is not None:
            return False
        dests = {move.end for move in self.moves_for_selected() if move.rotate_to is None}
        if self.selected is not None and (row, col) in dests:
            return self._play(self._move_to(row, col))
        occupant = self.board.get(row, col)
        if occupant is not None and occupant.player is self.turn:
            self.selected = (row, col)
            self.message = (
                f"{self.turn.label_de} hat {square_name(row, col)} "
                f"({occupant.kind.name_de}) gewählt."
            )
            return True
        self.selected = None
        self.message = f"{self.turn.label_de} ist am Zug."
        return True

    def rotate(self, direction: str) -> bool:
        if self.selected is None or self.winner is not None:
            return False
        try:
            facing = Direction(direction)
        except ValueError:
            return False
        for move in self.moves_for_selected():
            if move.rotate_to is facing:
                return self._play(move)
        return False

    def claim_half_win(self) -> bool:
        if self.winner is not None:
            return False
        for player in (Player.RED, Player.BLACK):
            if self.both_spears_captured(player):
                self._set_winner(player, "half", 0.5)
                return True
        return False

    def play_text(self, start: str, end: str | None = None) -> bool:
        s_row, s_col = parse_square(start)
        if end is None:
            return self.click(s_row, s_col)
        e_row, e_col = parse_square(end)
        self.selected = (s_row, s_col)
        return self.click(e_row, e_col)

    def apply_turn(self, move: Move) -> None:
        self._play(move)

    def moves_for_selected(self) -> list[Move]:
        if self.selected is None:
            return []
        return self.legal_moves_from(*self.selected)

    def legal_moves_from(self, row: int, col: int) -> list[Move]:
        piece = self.board.get(row, col)
        if piece is None or piece.player is not self.turn:
            return []
        return [
            move
            for move in raw_legal_moves(self.board, row, col)
            if self._is_playable(move)
        ]

    def all_legal_moves(self) -> list[Move]:
        moves: list[Move] = []
        for row, col, piece in self.board.pieces(self.turn):
            moves.extend(self.legal_moves_from(row, col))
        return moves

    def both_spears_captured(self, player: Player) -> bool:
        return len(self.board.find(player.opponent, PieceKind.SPEAR)) == 0

    def in_check(self, player: Player) -> bool:
        king = self.board.king_square(player)
        if king is None:
            return True
        return self._square_attacked(king[0], king[1], player.opponent)

    def _play(self, move: Move | None) -> bool:
        if move is None or self.winner is not None:
            return False
        captured = self.board.get(*move.end) if move.rotate_to is None else None
        apply_move(self.board, move)
        if captured is not None:
            self.captured[self.turn].append(captured.kind.value)
        removed_shields = self._remove_encircled_shields()
        self.last_move = {
            "from": list(move.start),
            "to": list(move.end),
            "capture": move.capture,
            "rotate": move.rotate_to.value if move.rotate_to else None,
        }
        self.selected = None
        opponent = self.turn.opponent
        if self.board.king_square(opponent) is None or (
            self.in_check(opponent) and not self._has_legal_reply(opponent)
        ):
            score = 1.5 if self.both_spears_captured(self.turn) else 1.0
            if captured is not None and captured.kind is PieceKind.BIG:
                reason = "perfect" if score == 1.5 else "captured"
            else:
                reason = "perfect" if score == 1.5 else "nullus"
            self._set_winner(self.turn, reason, score)
            if removed_shields:
                self.message = (
                    "Figur B wurde umkreist und aus dem Spiel entfernt. "
                    + self.message
                )
            return True
        self.turn = opponent
        self.check = self.in_check(self.turn)
        if self.check:
            self.message = f"Angriff auf Figur 5! {self.turn.label_de} muss reagieren."
        else:
            self.message = f"{self.turn.label_de} ist am Zug."
            if self.both_spears_captured(self.turn.opponent):
                self.message += (
                    f" {self.turn.opponent.label_de} hat beide Speere geschlagen "
                    "(0,5 Punkte möglich)."
                )
        if removed_shields:
            self.message = (
                "Figur B wurde umkreist und aus dem Spiel entfernt. " + self.message
            )
        return True

    def _move_to(self, row: int, col: int) -> Move | None:
        for move in self.moves_for_selected():
            if move.end == (row, col) and move.rotate_to is None:
                return move
        return None

    def _is_playable(self, move: Move) -> bool:
        """Zug nach Figurenregeln. Figur 5 zieht ein Feld in jede Richtung."""
        return self._follows_piece_rules(move)

    def _follows_piece_rules(self, move: Move) -> bool:
        if move.rotate_to is not None:
            return True
        target = self.board.get(*move.end)
        if target is None:
            return True
        if target.player is self.turn:
            return False
        if target.kind is PieceKind.BIG:
            return True
        attacker = self.board.get(*move.start)
        if attacker is None:
            return False
        if target.kind is PieceKind.SHIELD and attacker.kind is not PieceKind.SPEAR:
            return False
        if (
            is_protected_by_enemy(self.board, *move.end, self.turn)
            and attacker.kind is not PieceKind.SPEAR
        ):
            return False
        return True

    def _escapes_check(self, move: Move) -> bool:
        clone = self.board.copy()
        apply_move(clone, move)
        probe = Game(setup=False)
        probe.board = clone
        probe._remove_encircled_shields()
        return not probe.in_check(self.turn)

    def _has_legal_reply(self, player: Player) -> bool:
        saved_turn = self.turn
        self.turn = player
        try:
            return any(
                self._follows_piece_rules(move) and self._escapes_check(move)
                for move in self._raw_moves(player)
            )
        finally:
            self.turn = saved_turn

    def _raw_moves(self, player: Player) -> list[Move]:
        moves: list[Move] = []
        for row, col, _piece in self.board.pieces(player):
            moves.extend(raw_legal_moves(self.board, row, col))
        return moves

    def _square_attacked(self, row: int, col: int, by_player: Player) -> bool:
        for a_row, a_col, attacker in self.board.pieces(by_player):
            if (row, col) not in attacked_squares(self.board, a_row, a_col):
                continue
            if attacker.kind is PieceKind.SHIELD:
                continue
            target = self.board.get(row, col)
            if target is not None and target.kind is PieceKind.SHIELD:
                if attacker.kind is not PieceKind.SPEAR:
                    continue
            if (
                target is not None
                and target.kind is not PieceKind.BIG
                and is_protected_by_enemy(self.board, row, col, by_player)
                and attacker.kind is not PieceKind.SPEAR
            ):
                continue
            return True
        return False

    def _remove_encircled_shields(self) -> int:
        doomed: list[tuple[int, int, Player]] = []
        for row, col, piece in self.board.pieces():
            if piece.kind is PieceKind.SHIELD and shield_is_encircled(self.board, row, col):
                doomed.append((row, col, piece.player))
        for row, col, owner in doomed:
            self.board.set(row, col, None)
            self.captured[owner.opponent].append(PieceKind.SHIELD.value)
        return len(doomed)

    def _set_winner(self, player: Player, reason: str, score: float) -> None:
        self.winner = player
        self.win_reason = reason
        self.score = score
        if reason == "captured":
            self.message = f"{player.label_de} gewinnt – Figur 5 wurde geschlagen (1,0 Punkt)!"
        elif reason == "nullus":
            self.message = f"{player.label_de} gewinnt durch Nullus motus (1,0 Punkt)!"
        elif reason == "perfect":
            self.message = (
                f"{player.label_de} gewinnt perfekt – Nullus motus und beide Speere (1,5 Punkte)!"
            )
        else:
            self.message = (
                f"{player.label_de} gewinnt mit 0,5 Punkten (beide gegnerischen Speere)."
            )

    def to_dict(self) -> dict[str, object]:
        moves = self.moves_for_selected()
        return {
            "size": 11,
            "pieces": self.board.as_list(),
            "turn": self.turn.value,
            "vsAi": self.vs_ai,
            "aiPlayer": self.ai_player.value,
            "selected": list(self.selected) if self.selected else None,
            "quietMoves": [
                list(m.end) for m in moves if not m.capture and m.rotate_to is None
            ],
            "captures": [list(m.end) for m in moves if m.capture],
            "rotations": [m.rotate_to.value for m in moves if m.rotate_to is not None],
            "winner": self.winner.value if self.winner else None,
            "winReason": self.win_reason,
            "score": self.score,
            "message": self.message,
            "check": self.check,
            "lastMove": self.last_move,
            "canClaimHalf": self.winner is None
            and (
                self.both_spears_captured(Player.RED)
                or self.both_spears_captured(Player.BLACK)
            ),
            "captured": {
                Player.RED.value: self.captured[Player.RED],
                Player.BLACK.value: self.captured[Player.BLACK],
            },
        }
