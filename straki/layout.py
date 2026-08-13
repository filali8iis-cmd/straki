"""Geometrie des STRAKI-Fensters – unabhängig von pygame testbar."""

from __future__ import annotations

from straki.constants import BOARD_SIZE

WINDOW_SIZE = (1280, 840)
MARGIN = 28
LABEL = 32
CELL = 56
BOARD_LEFT = MARGIN + LABEL
BOARD_TOP = MARGIN + LABEL
BOARD_PIXELS = BOARD_SIZE * CELL
PANEL_LEFT = BOARD_LEFT + BOARD_PIXELS + LABEL + 36
PANEL_WIDTH = WINDOW_SIZE[0] - PANEL_LEFT - MARGIN


def cell_topleft(row: int, col: int) -> tuple[int, int]:
    """Pixel-Ecke oben links; Reihe K liegt oben im Fenster."""
    return (BOARD_LEFT + col * CELL, BOARD_TOP + (BOARD_SIZE - 1 - row) * CELL)


def cell_center(row: int, col: int) -> tuple[int, int]:
    x, y = cell_topleft(row, col)
    return x + CELL // 2, y + CELL // 2


def pixel_to_square(x: int, y: int) -> tuple[int, int] | None:
    if not (
        BOARD_LEFT <= x < BOARD_LEFT + BOARD_PIXELS
        and BOARD_TOP <= y < BOARD_TOP + BOARD_PIXELS
    ):
        return None
    col = (x - BOARD_LEFT) // CELL
    display_row = (y - BOARD_TOP) // CELL
    row = BOARD_SIZE - 1 - display_row
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None


def rank_label_center(row: int) -> tuple[int, int]:
    _x, y = cell_topleft(row, 0)
    return MARGIN + LABEL // 2, y + CELL // 2


def file_label_center(col: int) -> tuple[int, int]:
    x, _y = cell_topleft(0, col)
    return x + CELL // 2, BOARD_TOP + BOARD_PIXELS + LABEL // 2
