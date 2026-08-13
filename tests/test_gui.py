from __future__ import annotations

import os
import unittest

from straki.game import Game
from straki.layout import cell_center, pixel_to_square


class GuiSmokeTests(unittest.TestCase):
    def test_clicking_cell_center_selects_opening_soldier(self) -> None:
        game = Game()
        square = pixel_to_square(*cell_center(8, 3))  # I4
        self.assertEqual(square, (8, 3))
        self.assertTrue(game.click(*square))
        self.assertEqual(game.selected, (8, 3))

    def test_pygame_can_draw_one_frame(self) -> None:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        try:
            import pygame
        except ImportError:
            self.skipTest("pygame ist nicht installiert")
        pygame.display.init()
        pygame.font.init()
        try:
            from straki.gui import _draw, _load_fonts, _load_logo, _make_buttons
            from straki.layout import WINDOW_SIZE

            screen = pygame.display.set_mode(WINDOW_SIZE)
            game = Game()
            _draw(screen, game, _load_fonts(), _load_logo(), _make_buttons(), False, False)
            self.assertGreater(screen.get_width(), 0)
        except pygame.error as exc:
            self.skipTest(f"Kein Dummy-Display: {exc}")
        finally:
            pygame.quit()


if __name__ == "__main__":
    unittest.main()
