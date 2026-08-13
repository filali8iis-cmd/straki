from __future__ import annotations

import random
import unittest

from straki.ai import choose_turn
from straki.game import Game
from straki.models import Player


class AiTests(unittest.TestCase):
    def test_ai_returns_legal_opening_move(self) -> None:
        random.seed(1)
        game = Game()
        move = choose_turn(game, depth=1)
        self.assertIsNotNone(move)
        assert move is not None
        legal = game.all_legal_moves()
        self.assertIn(move, legal)

    def test_apply_turn_switches_player(self) -> None:
        game = Game()
        move = game.all_legal_moves()[0]
        game.apply_turn(move)
        self.assertIs(game.turn, Player.BLACK)
        self.assertIsNone(game.winner)


if __name__ == "__main__":
    unittest.main()
