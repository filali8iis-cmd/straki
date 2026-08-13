from __future__ import annotations

import unittest

from straki.board import Board, parse_square, square_name
from straki.models import PieceKind, Player


class BoardTests(unittest.TestCase):
    def test_setup_has_eighteen_pieces_each(self) -> None:
        board = Board()
        self.assertEqual(len(board.pieces(Player.RED)), 18)
        self.assertEqual(len(board.pieces(Player.BLACK)), 18)
        red_king = board.king_square(Player.RED)
        black_king = board.king_square(Player.BLACK)
        self.assertEqual(red_king, parse_square("J6"))
        self.assertEqual(black_king, parse_square("B6"))
        self.assertEqual(board.get(*parse_square("I6")).kind, PieceKind.SHIELD)
        self.assertEqual(board.get(*parse_square("C6")).kind, PieceKind.SHIELD)
        self.assertEqual(board.get(*parse_square("J2")).kind, PieceKind.SPEAR)
        self.assertEqual(board.get(*parse_square("C4")).kind, PieceKind.SOLDIER)

    def test_square_names(self) -> None:
        self.assertEqual(parse_square("A1"), (0, 0))
        self.assertEqual(parse_square("H6"), (7, 5))
        self.assertEqual(parse_square("K11"), (10, 10))
        self.assertEqual(square_name(7, 5), "H6")
        with self.assertRaises(ValueError):
            parse_square("L1")
        with self.assertRaises(ValueError):
            parse_square("A12")


if __name__ == "__main__":
    unittest.main()
