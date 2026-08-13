from __future__ import annotations

import random

from straki.constants import PIECE_VALUE
from straki.game import Game
from straki.models import Move, Player


def choose_turn(game: Game, depth: int = 1) -> Move | None:
    moves = game.all_legal_moves()
    if not moves:
        return None
    player = game.turn
    best = float("-inf")
    chosen: list[Move] = []
    for move in moves:
        snapshot = _snapshot(game)
        game.apply_turn(move)
        score = _evaluate(game, player) if depth <= 1 else -_minimax(game, depth - 1, player)
        _restore(game, snapshot)
        if score > best:
            best = score
            chosen = [move]
        elif score == best:
            chosen.append(move)
    return random.choice(chosen)


def _minimax(game: Game, depth: int, root: Player) -> float:
    if game.winner is not None or depth == 0:
        return _evaluate(game, root)
    moves = game.all_legal_moves()
    if not moves:
        return _evaluate(game, root)
    maximizing = game.turn is root
    value = float("-inf") if maximizing else float("inf")
    for move in moves:
        snapshot = _snapshot(game)
        game.apply_turn(move)
        score = _minimax(game, depth - 1, root)
        _restore(game, snapshot)
        if maximizing:
            value = max(value, score)
        else:
            value = min(value, score)
    return value


def _evaluate(game: Game, player: Player) -> float:
    if game.winner is player:
        return 10_000.0 + game.score * 100
    if game.winner is player.opponent:
        return -10_000.0
    score = 0.0
    for _row, _col, piece in game.board.pieces():
        value = PIECE_VALUE[piece.kind.value]
        score += value if piece.player is player else -value
    if game.in_check(player.opponent):
        score += 25.0
    if game.in_check(player):
        score -= 25.0
    if game.both_spears_captured(player):
        score += 40.0
    king = game.board.king_square(player)
    if king is None:
        score -= 500.0
    return score


def _snapshot(game: Game) -> dict[str, object]:
    return {
        "board": game.board.copy(),
        "turn": game.turn,
        "winner": game.winner,
        "win_reason": game.win_reason,
        "score": game.score,
        "message": game.message,
        "check": game.check,
        "selected": game.selected,
        "last_move": game.last_move,
        "captured": {
            Player.RED: list(game.captured[Player.RED]),
            Player.BLACK: list(game.captured[Player.BLACK]),
        },
    }


def _restore(game: Game, snap: dict[str, object]) -> None:
    game.board = snap["board"]  # type: ignore[assignment]
    game.turn = snap["turn"]  # type: ignore[assignment]
    game.winner = snap["winner"]  # type: ignore[assignment]
    game.win_reason = snap["win_reason"]  # type: ignore[assignment]
    game.score = snap["score"]  # type: ignore[assignment]
    game.message = snap["message"]  # type: ignore[assignment]
    game.check = snap["check"]  # type: ignore[assignment]
    game.selected = snap["selected"]  # type: ignore[assignment]
    game.last_move = snap["last_move"]  # type: ignore[assignment]
    game.captured = snap["captured"]  # type: ignore[assignment]
