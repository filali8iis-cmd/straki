from __future__ import annotations

import unittest

from straki.board import Board, parse_square
from straki.game import Game
from straki.models import Direction, Piece, PieceKind, Player
from straki.moves import (
    attack_destinations,
    fusion_partner,
    protected_squares,
    quiet_destinations,
    shield_is_encircled,
)


def place(game: Game, square: str, player: Player, kind: PieceKind, facing: Direction | None = None) -> None:
    row, col = parse_square(square)
    game.board.set(row, col, Piece(player, kind, facing))


def kings(game: Game) -> None:
    place(game, "K1", Player.RED, PieceKind.BIG, Direction.S)
    place(game, "A11", Player.BLACK, PieceKind.BIG, Direction.N)


class RulesTests(unittest.TestCase):
    def test_opening_soldier_moves(self) -> None:
        game = Game()
        game.click(*parse_square("I5"))
        dests = {move.end for move in game.moves_for_selected() if move.rotate_to is None}
        self.assertIn(parse_square("H5"), dests)
        self.assertIn(parse_square("H4"), dests)
        self.assertNotIn(parse_square("J5"), dests)

    def test_scissors_moves_only_orthogonally(self) -> None:
        game = Game(setup=False)
        game.turn = Player.RED
        kings(game)
        place(game, "F6", Player.RED, PieceKind.SCISSORS)
        game.click(*parse_square("F6"))
        quiet = {move.end for move in game.moves_for_selected() if not move.capture}
        self.assertEqual(
            quiet,
            {parse_square("G6"), parse_square("E6"), parse_square("F5"), parse_square("F7")},
        )

    def test_scissors_attacks_four_diagonally(self) -> None:
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "F6", Player.RED, PieceKind.SCISSORS)
        place(game, "B2", Player.BLACK, PieceKind.SOLDIER)
        attacks = attack_destinations(game.board, *parse_square("F6"))
        self.assertIn(parse_square("B2"), attacks)
        place(game, "A1", Player.BLACK, PieceKind.SOLDIER)
        attacks = attack_destinations(game.board, *parse_square("F6"))
        self.assertNotIn(parse_square("A1"), attacks)

    def test_frog_leaps_two_diagonally(self) -> None:
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "E7", Player.RED, PieceKind.FROG)
        place(game, "G5", Player.BLACK, PieceKind.SOLDIER)
        attacks = attack_destinations(game.board, *parse_square("E7"))
        self.assertEqual(attacks, [parse_square("G5")])

    def test_small_lighthouse_attacks_only_where_head_points(self) -> None:
        game = Game(setup=False)
        place(game, "G6", Player.RED, PieceKind.SMALL, Direction.S)
        place(game, "D6", Player.BLACK, PieceKind.SOLDIER)
        place(game, "C6", Player.BLACK, PieceKind.SOLDIER)
        place(game, "G9", Player.BLACK, PieceKind.SOLDIER)
        place(game, "J6", Player.BLACK, PieceKind.SOLDIER)
        attacks = attack_destinations(game.board, *parse_square("G6"))
        self.assertEqual(attacks, [parse_square("D6")])
        quiet = set(quiet_destinations(game.board, *parse_square("G6")))
        self.assertIn(parse_square("H6"), quiet)
        self.assertIn(parse_square("F5"), quiet)
        self.assertIn(parse_square("H7"), quiet)

    def test_big_lighthouse_attacks_only_where_head_points(self) -> None:
        game = Game(setup=False)
        place(game, "F6", Player.RED, PieceKind.BIG, Direction.S)
        place(game, "B6", Player.BLACK, PieceKind.SOLDIER)
        place(game, "F2", Player.BLACK, PieceKind.SOLDIER)
        place(game, "J6", Player.BLACK, PieceKind.SOLDIER)
        attacks = attack_destinations(game.board, *parse_square("F6"))
        self.assertEqual(attacks, [parse_square("B6")])
        quiet = set(quiet_destinations(game.board, *parse_square("F6")))
        self.assertIn(parse_square("G6"), quiet)
        self.assertIn(parse_square("E5"), quiet)

    def test_soldier_captures_only_forward(self) -> None:
        game = Game(setup=False)
        game.turn = Player.BLACK
        place(game, "D5", Player.BLACK, PieceKind.SOLDIER)
        place(game, "E5", Player.RED, PieceKind.FROG)
        place(game, "D6", Player.RED, PieceKind.FROG)
        attacks = attack_destinations(game.board, *parse_square("D5"))
        self.assertEqual(attacks, [parse_square("E5")])

    def test_shield_moves_one_square_like_king(self) -> None:
        """Abbildung 16: Figur B zieht nur ein Feld orthogonal oder diagonal."""
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "G6", Player.RED, PieceKind.SHIELD, Direction.S)
        place(game, "K1", Player.RED, PieceKind.BIG, Direction.S)
        place(game, "A11", Player.BLACK, PieceKind.BIG, Direction.N)
        game.click(*parse_square("G6"))
        quiet = {m.end for m in game.moves_for_selected() if not m.capture and m.rotate_to is None}
        self.assertEqual(
            quiet,
            {
                parse_square("F5"),
                parse_square("F6"),
                parse_square("F7"),
                parse_square("G5"),
                parse_square("G7"),
                parse_square("H5"),
                parse_square("H6"),
                parse_square("H7"),
            },
        )
        self.assertNotIn(parse_square("A1"), quiet)
        self.assertNotIn(parse_square("K11"), quiet)
        self.assertNotIn(parse_square("D2"), quiet)
        game.click(*parse_square("A1"))
        self.assertEqual(game.board.get(*parse_square("G6")).kind, PieceKind.SHIELD)
        self.assertIsNone(game.board.get(*parse_square("A1")))
        game.click(*parse_square("G6"))
        game.click(*parse_square("H7"))
        self.assertEqual(game.board.get(*parse_square("H7")).kind, PieceKind.SHIELD)
        self.assertIsNone(game.board.get(*parse_square("G6")))

    def test_shield_protects_three_squares_ahead(self) -> None:
        game = Game(setup=False)
        place(game, "I6", Player.RED, PieceKind.SHIELD)
        protected = protected_squares(game.board, *parse_square("I6"))
        self.assertEqual(
            protected,
            {parse_square("H5"), parse_square("H6"), parse_square("H7")},
        )

    def test_shield_blocks_scissors_but_not_spear(self) -> None:
        game = Game(setup=False)
        game.turn = Player.BLACK
        place(game, "I6", Player.RED, PieceKind.SHIELD)
        place(game, "H6", Player.RED, PieceKind.SMALL, Direction.S)
        place(game, "E9", Player.BLACK, PieceKind.SCISSORS)
        place(game, "G6", Player.BLACK, PieceKind.SPEAR)
        game.board.set(*parse_square("J6"), Piece(Player.RED, PieceKind.BIG, Direction.S))
        game.board.set(*parse_square("B6"), Piece(Player.BLACK, PieceKind.BIG, Direction.N))
        game.click(*parse_square("E9"))
        dests = {move.end for move in game.moves_for_selected() if move.capture}
        self.assertNotIn(parse_square("H6"), dests)
        game.selected = None
        game.click(*parse_square("G6"))
        spear_caps = {move.end for move in game.moves_for_selected() if move.capture}
        self.assertIn(parse_square("H6"), spear_caps)

    def test_only_spear_can_capture_shield(self) -> None:
        game = Game(setup=False)
        game.turn = Player.BLACK
        place(game, "F5", Player.RED, PieceKind.SHIELD)
        place(game, "E5", Player.BLACK, PieceKind.SOLDIER)
        place(game, "E6", Player.BLACK, PieceKind.SPEAR)
        kings(game)
        game.click(*parse_square("E5"))
        self.assertNotIn(parse_square("F5"), {m.end for m in game.moves_for_selected()})
        game.click(*parse_square("E6"))
        self.assertIn(parse_square("F5"), {m.end for m in game.moves_for_selected() if m.capture})

    def test_any_piece_can_capture_figur_5(self) -> None:
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "E5", Player.RED, PieceKind.SPEAR)
        place(game, "E6", Player.BLACK, PieceKind.BIG, Direction.N)
        place(game, "J6", Player.RED, PieceKind.BIG, Direction.S)
        place(game, "A1", Player.BLACK, PieceKind.SPEAR)
        place(game, "A11", Player.BLACK, PieceKind.SPEAR)
        attacks = attack_destinations(game.board, *parse_square("E5"))
        self.assertIn(parse_square("E6"), attacks)
        game.click(*parse_square("E5"))
        self.assertIn(parse_square("E6"), {m.end for m in game.moves_for_selected() if m.capture})
        game.click(*parse_square("E6"))
        self.assertEqual(game.winner, Player.RED)
        self.assertEqual(game.win_reason, "captured")

    def test_soldier_can_capture_figur_5_along_forward_file(self) -> None:
        """Stellung wie im Spiel: Soldat D5, Figur 5 auf G5, Bahn frei."""
        game = Game(setup=False)
        game.turn = Player.BLACK
        place(game, "D5", Player.BLACK, PieceKind.SOLDIER)
        place(game, "G5", Player.RED, PieceKind.BIG, Direction.S)
        place(game, "B6", Player.BLACK, PieceKind.BIG, Direction.N)
        place(game, "K1", Player.RED, PieceKind.SPEAR)
        place(game, "K11", Player.RED, PieceKind.SPEAR)
        attacks = attack_destinations(game.board, *parse_square("D5"))
        self.assertIn(parse_square("G5"), attacks)
        game.click(*parse_square("D5"))
        self.assertIn(parse_square("G5"), {m.end for m in game.moves_for_selected() if m.capture})
        game.click(*parse_square("G5"))
        self.assertEqual(game.board.get(*parse_square("G5")).kind, PieceKind.SOLDIER)
        self.assertEqual(game.winner, Player.BLACK)
        self.assertEqual(game.win_reason, "captured")

    def test_rotating_lighthouse_changes_attack_line(self) -> None:
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "E6", Player.RED, PieceKind.SMALL, Direction.S)
        place(game, "B6", Player.BLACK, PieceKind.SOLDIER)
        place(game, "E9", Player.BLACK, PieceKind.SOLDIER)
        kings(game)
        self.assertEqual(
            attack_destinations(game.board, *parse_square("E6")),
            [parse_square("B6")],
        )
        game.click(*parse_square("E6"))
        self.assertTrue(game.rotate("E"))
        self.assertEqual(game.board.get(*parse_square("E6")).facing, Direction.E)
        self.assertEqual(
            attack_destinations(game.board, *parse_square("E6")),
            [parse_square("E9")],
        )

    def test_fusion_extends_small_lighthouse(self) -> None:
        game = Game(setup=False)
        place(game, "E3", Player.RED, PieceKind.SMALL, Direction.E)
        place(game, "E2", Player.RED, PieceKind.BIG, Direction.E)
        place(game, "E11", Player.BLACK, PieceKind.SOLDIER)
        partner = fusion_partner(game.board, *parse_square("E3"), game.board.get(*parse_square("E3")))
        self.assertIsNotNone(partner)
        attacks = attack_destinations(game.board, *parse_square("E3"))
        self.assertIn(parse_square("E11"), attacks)

    def test_encircled_shield_is_removed(self) -> None:
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "F5", Player.BLACK, PieceKind.SHIELD, Direction.N)
        for square in ("E4", "D4", "D5", "D6", "E6"):
            place(game, square, Player.RED, PieceKind.SOLDIER)
        place(game, "C1", Player.RED, PieceKind.SOLDIER)
        place(game, "C2", Player.BLACK, PieceKind.SOLDIER)
        place(game, "J6", Player.RED, PieceKind.BIG, Direction.S)
        place(game, "B6", Player.BLACK, PieceKind.BIG, Direction.N)
        self.assertTrue(shield_is_encircled(game.board, *parse_square("F5")))
        game.click(*parse_square("C1"))
        game.click(*parse_square("B1"))
        self.assertIsNone(game.board.get(*parse_square("F5")))
        self.assertIn("umkreist", game.message)

    def test_edge_encircled_shield_is_removed(self) -> None:
        """Beispiel 7: Figur B am Rand, U-Form schließt über den Brettrand."""
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "B9", Player.BLACK, PieceKind.SHIELD, Direction.N)
        place(game, "A8", Player.RED, PieceKind.SOLDIER)
        place(game, "A10", Player.RED, PieceKind.SOLDIER)
        place(game, "C1", Player.RED, PieceKind.SOLDIER)
        place(game, "C2", Player.BLACK, PieceKind.SOLDIER)
        kings(game)
        self.assertTrue(shield_is_encircled(game.board, *parse_square("B9")))
        game.click(*parse_square("C1"))
        game.click(*parse_square("B1"))
        self.assertIsNone(game.board.get(*parse_square("B9")))

    def test_close_u_around_shield_is_removed(self) -> None:
        """B auf F6, Gegner auf F5/F7/G5/G6/G7: enge U-Form, muss fallen."""
        game = Game(setup=False)
        game.turn = Player.BLACK
        place(game, "F6", Player.RED, PieceKind.SHIELD, Direction.S)
        for square in ("F5", "F7", "G5", "G6", "G7"):
            place(game, square, Player.BLACK, PieceKind.SOLDIER)
        place(game, "C1", Player.BLACK, PieceKind.SOLDIER)
        place(game, "C2", Player.RED, PieceKind.SOLDIER)
        kings(game)
        self.assertTrue(shield_is_encircled(game.board, *parse_square("F6")))
        game.click(*parse_square("C1"))
        game.click(*parse_square("B1"))
        self.assertIsNone(game.board.get(*parse_square("F6")))
        self.assertIn("umkreist", game.message)

    def test_orthogonally_surrounded_shield_is_removed(self) -> None:
        """B auf F8, Gegner auf E8/G8/F7/F9: direkt umkreist, muss fallen."""
        game = Game(setup=False)
        game.turn = Player.RED
        place(game, "F8", Player.BLACK, PieceKind.SHIELD, Direction.N)
        place(game, "G8", Player.RED, PieceKind.SOLDIER)
        place(game, "E8", Player.RED, PieceKind.SCISSORS)
        place(game, "F7", Player.RED, PieceKind.SOLDIER)
        place(game, "F9", Player.RED, PieceKind.SOLDIER)
        place(game, "C1", Player.RED, PieceKind.SOLDIER)
        place(game, "C2", Player.BLACK, PieceKind.SOLDIER)
        kings(game)
        self.assertTrue(shield_is_encircled(game.board, *parse_square("F8")))
        game.click(*parse_square("C1"))
        game.click(*parse_square("B1"))
        self.assertIsNone(game.board.get(*parse_square("F8")))
        self.assertIn("umkreist", game.message)

    def test_opening_shields_are_not_encircled(self) -> None:
        game = Game()
        self.assertFalse(shield_is_encircled(game.board, *parse_square("I6")))
        self.assertFalse(shield_is_encircled(game.board, *parse_square("C6")))
        self.assertEqual(game.board.get(*parse_square("I6")).facing, Direction.S)
        self.assertEqual(game.board.get(*parse_square("C6")).facing, Direction.N)

    def test_quiet_destinations_blocked_by_own_piece(self) -> None:
        board = Board()
        dests = quiet_destinations(board, *parse_square("J6"))
        self.assertNotIn(parse_square("J5"), dests)
        self.assertNotIn(parse_square("J7"), dests)


if __name__ == "__main__":
    unittest.main()
