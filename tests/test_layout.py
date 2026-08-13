from __future__ import annotations

import unittest

from straki.constants import BOARD_SIZE
from straki.layout import (
    BOARD_LEFT,
    BOARD_TOP,
    CELL,
    cell_center,
    cell_topleft,
    pixel_to_square,
)


class LayoutTests(unittest.TestCase):
    def test_bottom_left_is_a1(self) -> None:
        x, y = cell_topleft(0, 0)
        self.assertEqual(x, BOARD_LEFT)
        self.assertEqual(y, BOARD_TOP + (BOARD_SIZE - 1) * CELL)
        self.assertEqual(pixel_to_square(x + 4, y + 4), (0, 0))

    def test_top_left_is_k1(self) -> None:
        x, y = cell_topleft(10, 0)
        self.assertEqual(y, BOARD_TOP)
        self.assertEqual(pixel_to_square(x + CELL // 2, y + CELL // 2), (10, 0))

    def test_center_roundtrip(self) -> None:
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x, y = cell_center(row, col)
                self.assertEqual(pixel_to_square(x, y), (row, col))

    def test_outside_board_is_none(self) -> None:
        self.assertIsNone(pixel_to_square(0, 0))
        self.assertIsNone(pixel_to_square(BOARD_LEFT - 1, BOARD_TOP + 10))


if __name__ == "__main__":
    unittest.main()
