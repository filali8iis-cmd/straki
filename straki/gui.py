"""Eigenes grafisches Spielfenster für STRAKI."""

from __future__ import annotations

import pygame

from straki.ai import choose_turn
from straki.constants import BOARD_SIZE, COLS, ROWS, RULES_DE
from straki.game import Game
from straki.layout import (
    BOARD_LEFT,
    BOARD_PIXELS,
    BOARD_TOP,
    CELL,
    LABEL,
    MARGIN,
    PANEL_LEFT,
    PANEL_WIDTH,
    WINDOW_SIZE,
    cell_center,
    cell_topleft,
    file_label_center,
    pixel_to_square,
    rank_label_center,
)
from straki.models import Direction, Piece, PieceKind, Player
from straki.moves import protected_squares
from straki.paths import static_dir

STATIC_DIR = static_dir()

WHITE = (255, 255, 255)
BG = (244, 241, 234)
INK = (28, 28, 28)
MUTED = (90, 90, 90)
GRID = (196, 69, 54)
GOLD = (138, 31, 20)
PANEL = (255, 255, 255)
SELECT = (255, 231, 168)
LAST = (248, 215, 212)
PROTECT = (255, 244, 200)
FREE = (198, 220, 186)
CHECK = (196, 69, 54)
BUTTON = (196, 69, 54)
BUTTON_HOVER = (150, 40, 32)

KIND_FILL = {
    PieceKind.SOLDIER: (227, 122, 181),
    PieceKind.FROG: (224, 90, 79),
    PieceKind.SMALL: (61, 90, 168),
    PieceKind.SCISSORS: (94, 196, 210),
    PieceKind.BIG: (90, 168, 90),
    PieceKind.SHIELD: (240, 210, 75),
    PieceKind.SPEAR: (43, 43, 43),
}
KIND_TEXT = {
    PieceKind.SMALL: WHITE,
    PieceKind.BIG: WHITE,
    PieceKind.SPEAR: WHITE,
}

ARROWS = {
    Direction.N: "↑",
    Direction.E: "→",
    Direction.S: "↓",
    Direction.W: "←",
}


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        key: str,
        ghost: bool = False,
    ) -> None:
        self.rect = rect
        self.label = label
        self.key = key
        self.ghost = ghost
        self.visible = True
        self.enabled = True

    def hit(self, pos: tuple[int, int]) -> bool:
        return self.visible and self.enabled and self.rect.collidepoint(pos)


def run_gui(vs_ai: bool = False) -> None:
    pygame.init()
    pygame.display.set_caption("STRAKI 1.5  –  B auf jedes leere Feld")
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    fonts = _load_fonts()
    logo = _load_logo()
    if logo is not None:
        pygame.display.set_icon(logo)
    game = Game(vs_ai=vs_ai)
    buttons = _make_buttons()
    show_rules = False
    pending_ai = False
    running = True

    while running:
        pending_ai = _maybe_queue_ai(game, pending_ai)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if show_rules:
                    show_rules = False
                else:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                show_rules, pending_ai = _handle_click(
                    game, buttons, event.pos, show_rules, pending_ai
                )

        if pending_ai and game.winner is None:
            pygame.event.pump()
            _draw(screen, game, fonts, logo, buttons, show_rules, thinking=True)
            pygame.display.flip()
            move = choose_turn(game)
            if move:
                game.apply_turn(move)
            pending_ai = False

        _draw(screen, game, fonts, logo, buttons, show_rules, thinking=False)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def _load_fonts() -> dict[str, pygame.font.Font]:
    def make(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont("dejavusans,freesans,arial,sans", size, bold=bold)

    return {
        "title": make(28, True),
        "body": make(20),
        "small": make(16),
        "tiny": make(14),
        "piece": make(22, True),
        "label": make(16, True),
    }


def _load_logo() -> pygame.Surface | None:
    path = STATIC_DIR / "logo.png"
    if not path.is_file():
        return None
    image = pygame.image.load(str(path)).convert_alpha()
    width = min(PANEL_WIDTH - 20, 260)
    height = int(image.get_height() * width / image.get_width())
    return pygame.transform.smoothscale(image, (width, height))


def _make_buttons() -> dict[str, Button]:
    x = PANEL_LEFT
    width = PANEL_WIDTH
    rot_y = 530
    y = 590
    buttons = {
        "new": Button(pygame.Rect(x, y, width, 44), "Neue Partie", "new"),
        "ai": Button(pygame.Rect(x, y + 54, width, 44), "Gegen den Computer", "ai", ghost=True),
        "half": Button(pygame.Rect(x, y + 108, width, 44), "0,5 Punkte nehmen", "half", ghost=True),
        "rules": Button(pygame.Rect(x, y + 162, width, 44), "Regeln", "rules", ghost=True),
    }
    span = 52
    start = x + (width - 4 * span) // 2
    for i, direction in enumerate(Direction):
        buttons[f"rot-{direction.value}"] = Button(
            pygame.Rect(start + i * span, rot_y, 44, 44),
            ARROWS[direction],
            f"rot-{direction.value}",
            ghost=True,
        )
    return buttons


def _maybe_queue_ai(game: Game, pending_ai: bool) -> bool:
    if pending_ai:
        return True
    return (
        game.vs_ai
        and game.winner is None
        and game.turn is game.ai_player
    )


def _handle_click(
    game: Game,
    buttons: dict[str, Button],
    pos: tuple[int, int],
    show_rules: bool,
    pending_ai: bool,
) -> tuple[bool, bool]:
    if show_rules:
        return False, pending_ai
    if pending_ai:
        return show_rules, pending_ai

    for button in buttons.values():
        if not button.hit(pos):
            continue
        if button.key == "new":
            game.reset()
            return show_rules, False
        if button.key == "ai":
            game.reset(vs_ai=not game.vs_ai)
            return show_rules, False
        if button.key == "half":
            game.claim_half_win()
            return show_rules, False
        if button.key == "rules":
            return True, pending_ai
        if button.key.startswith("rot-"):
            game.rotate(button.key.split("-", 1)[1])
            return show_rules, _maybe_queue_ai(game, False)
        return show_rules, pending_ai

    square = pixel_to_square(*pos)
    if square is not None and game.winner is None:
        if not (game.vs_ai and game.turn is game.ai_player):
            game.click(*square)
    return show_rules, _maybe_queue_ai(game, False)


def _draw(
    screen: pygame.Surface,
    game: Game,
    fonts: dict[str, pygame.font.Font],
    logo: pygame.Surface | None,
    buttons: dict[str, Button],
    show_rules: bool,
    thinking: bool,
) -> None:
    screen.fill(BG)
    _draw_board(screen, game, fonts)
    _draw_panel(screen, game, fonts, logo, buttons, thinking)
    if show_rules:
        _draw_rules(screen, fonts)


def _draw_board(
    screen: pygame.Surface,
    game: Game,
    fonts: dict[str, pygame.font.Font],
) -> None:
    board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_PIXELS, BOARD_PIXELS)
    pygame.draw.rect(screen, WHITE, board_rect)
    pygame.draw.rect(screen, GRID, board_rect, 3)

    moves = game.moves_for_selected()
    quiet = {m.end for m in moves if not m.capture and m.rotate_to is None}
    captures = {m.end for m in moves if m.capture}
    protected: set[tuple[int, int]] = set()
    chosen_is_shield = False
    if game.selected is not None:
        chosen = game.board.get(*game.selected)
        if chosen is not None and chosen.kind is PieceKind.SHIELD:
            protected = protected_squares(game.board, *game.selected)
            chosen_is_shield = True
    last = None
    if game.last_move:
        last = (tuple(game.last_move["from"]), tuple(game.last_move["to"]))

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            x, y = cell_topleft(row, col)
            rect = pygame.Rect(x, y, CELL, CELL)
            fill = WHITE
            if game.selected == (row, col):
                fill = SELECT
            elif (row, col) in quiet:
                fill = FREE
            elif (row, col) in protected:
                fill = PROTECT
            elif last and (row, col) in last:
                fill = LAST
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, GRID, rect, 1)
            if (row, col) in quiet:
                if chosen_is_shield:
                    inner = rect.inflate(-14, -14)
                    pygame.draw.rect(screen, (70, 130, 70), inner, 2)
                else:
                    pygame.draw.circle(screen, INK, cell_center(row, col), 6)
            if (row, col) in captures:
                pygame.draw.circle(screen, GRID, cell_center(row, col), CELL // 2 - 8, 3)

    for row, col, piece in game.board.pieces():
        _draw_piece(screen, fonts, row, col, piece)

    for row in range(BOARD_SIZE):
        _draw_badge(screen, fonts, rank_label_center(row), ROWS[row])
        right = (BOARD_LEFT + BOARD_PIXELS + LABEL // 2, rank_label_center(row)[1])
        _draw_badge(screen, fonts, right, ROWS[row])
    for col in COLS:
        _draw_badge(screen, fonts, file_label_center(col - 1), str(col))
        top = (file_label_center(col - 1)[0], BOARD_TOP - LABEL // 2)
        _draw_badge(screen, fonts, top, str(col))

    if chosen_is_shield:
        hint = fonts["tiny"].render("B gewählt: jedes grüne Feld ist erlaubt.", True, (40, 90, 40))
        screen.blit(hint, hint.get_rect(midtop=(BOARD_LEFT + BOARD_PIXELS // 2, 6)))


def _draw_badge(
    screen: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    center: tuple[int, int],
    text: str,
) -> None:
    pygame.draw.circle(screen, WHITE, center, 13)
    pygame.draw.circle(screen, INK, center, 13, 1)
    label = fonts["label"].render(text, True, INK)
    screen.blit(label, label.get_rect(center=center))


def _draw_piece(
    screen: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    row: int,
    col: int,
    piece: Piece,
) -> None:
    center = cell_center(row, col)
    fill = KIND_FILL[piece.kind]
    outline = GRID if piece.player is Player.RED else INK
    pygame.draw.circle(screen, fill, center, CELL // 2 - 6)
    pygame.draw.circle(screen, outline, center, CELL // 2 - 6, 3)
    text_color = KIND_TEXT.get(piece.kind, INK)
    glyph = piece.kind.value
    if piece.facing is not None:
        glyph += ARROWS[piece.facing]
    label = fonts["piece"].render(glyph, True, text_color)
    screen.blit(label, label.get_rect(center=center))


def _draw_panel(
    screen: pygame.Surface,
    game: Game,
    fonts: dict[str, pygame.font.Font],
    logo: pygame.Surface | None,
    buttons: dict[str, Button],
    thinking: bool,
) -> None:
    panel = pygame.Rect(PANEL_LEFT - 16, MARGIN, PANEL_WIDTH + 32, WINDOW_SIZE[1] - 2 * MARGIN)
    pygame.draw.rect(screen, PANEL, panel, border_radius=10)
    pygame.draw.rect(screen, (220, 220, 220), panel, 1, border_radius=10)

    y = panel.y + 16
    if logo is not None:
        screen.blit(logo, (PANEL_LEFT, y))
        y += logo.get_height() + 12
    else:
        title = fonts["title"].render("STRAKI", True, GOLD)
        screen.blit(title, (PANEL_LEFT, y))
        y += 40

    subtitle = fonts["tiny"].render("Figur B: jedes leere Feld  ·  straki.org", True, MUTED)
    screen.blit(subtitle, (PANEL_LEFT, y))
    y += 28

    message = "Computer denkt …" if thinking else game.message
    y = _blit_wrapped(screen, fonts["body"], message, PANEL_LEFT, y, PANEL_WIDTH, INK)
    y += 10

    if game.check and not thinking:
        banner = pygame.Rect(PANEL_LEFT, y, PANEL_WIDTH, 32)
        pygame.draw.rect(screen, CHECK, banner, border_radius=6)
        text = fonts["tiny"].render("ANGRIFF AUF FIGUR 5", True, WHITE)
        screen.blit(text, text.get_rect(center=banner.center))
        y += 42

    captured_red = " ".join(game.captured[Player.RED]) or "—"
    captured_black = " ".join(game.captured[Player.BLACK]) or "—"
    y = _blit_wrapped(
        screen,
        fonts["small"],
        f"Rot geschlagen: {captured_red}",
        PANEL_LEFT,
        y,
        PANEL_WIDTH,
        GRID,
    )
    y = _blit_wrapped(
        screen,
        fonts["small"],
        f"Schwarz geschlagen: {captured_black}",
        PANEL_LEFT,
        y + 4,
        PANEL_WIDTH,
        INK,
    )

    legend = [
        ("1 Soldat", KIND_FILL[PieceKind.SOLDIER]),
        ("2 Frosch", KIND_FILL[PieceKind.FROG]),
        ("3 Leuchtturm", KIND_FILL[PieceKind.SMALL]),
        ("4 Schere", KIND_FILL[PieceKind.SCISSORS]),
        ("5 Großer Leuchtturm", KIND_FILL[PieceKind.BIG]),
        ("B Schild", KIND_FILL[PieceKind.SHIELD]),
        ("A Speer", KIND_FILL[PieceKind.SPEAR]),
    ]
    y += 16
    for i, (name, color) in enumerate(legend):
        lx = PANEL_LEFT + (i % 2) * (PANEL_WIDTH // 2)
        ly = y + (i // 2) * 22
        pygame.draw.circle(screen, color, (lx + 8, ly + 8), 7)
        pygame.draw.circle(screen, INK, (lx + 8, ly + 8), 7, 1)
        label = fonts["tiny"].render(name, True, MUTED)
        screen.blit(label, (lx + 20, ly))

    rotations = {m.rotate_to.value for m in game.moves_for_selected() if m.rotate_to}
    mouse = pygame.mouse.get_pos()
    for key, button in buttons.items():
        if key.startswith("rot-"):
            direction = key.split("-", 1)[1]
            button.visible = bool(rotations)
            button.enabled = direction in rotations
        elif key == "half":
            button.visible = game.winner is None and (
                game.both_spears_captured(Player.RED)
                or game.both_spears_captured(Player.BLACK)
            )
            button.enabled = button.visible
        elif key == "ai":
            button.label = "Computer aus" if game.vs_ai else "Gegen den Computer"
        _draw_button(screen, fonts, button, mouse)


def _draw_button(
    screen: pygame.Surface,
    fonts: dict[str, pygame.font.Font],
    button: Button,
    mouse: tuple[int, int],
) -> None:
    if not button.visible:
        return
    hover = button.rect.collidepoint(mouse) and button.enabled
    if button.ghost:
        color = BUTTON if hover else WHITE
        text_color = WHITE if hover else BUTTON
        pygame.draw.rect(screen, color, button.rect, border_radius=22)
        pygame.draw.rect(screen, BUTTON, button.rect, 2, border_radius=22)
    else:
        color = BUTTON_HOVER if hover else BUTTON
        text_color = WHITE
        pygame.draw.rect(screen, color, button.rect, border_radius=22)
    label = fonts["body"].render(button.label, True, text_color)
    screen.blit(label, label.get_rect(center=button.rect.center))


def _draw_rules(screen: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
    overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
    overlay.fill((20, 20, 20, 180))
    screen.blit(overlay, (0, 0))
    box = pygame.Rect(80, 50, WINDOW_SIZE[0] - 160, WINDOW_SIZE[1] - 100)
    pygame.draw.rect(screen, WHITE, box, border_radius=12)
    y = box.y + 20
    title = fonts["title"].render("Strakiregeln", True, GOLD)
    screen.blit(title, (box.x + 24, y))
    y += 40
    for line in RULES_DE.splitlines():
        y = _blit_wrapped(screen, fonts["small"], line or " ", box.x + 24, y, box.width - 48, INK)
    hint = fonts["tiny"].render("Klick oder Esc schließt die Regeln.", True, MUTED)
    screen.blit(hint, (box.x + 24, box.bottom - 36))


def _blit_wrapped(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    width: int,
    color: tuple[int, int, int],
) -> int:
    words = text.split(" ")
    line = ""
    for word in words:
        trial = f"{line} {word}".strip()
        if font.size(trial)[0] <= width:
            line = trial
            continue
        if line:
            screen.blit(font.render(line, True, color), (x, y))
            y += font.get_linesize()
        line = word
    if line:
        screen.blit(font.render(line, True, color), (x, y))
        y += font.get_linesize()
    return y
