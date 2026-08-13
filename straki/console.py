from __future__ import annotations

from straki.board import parse_square, square_name
from straki.constants import BOARD_SIZE, ROWS, RULES_DE
from straki.game import Game
from straki.models import Direction, PieceKind, Player

RESET = "\033[0m"
RED = "\033[91m"
BLACK = "\033[90m"
GOLD = "\033[93m"
BOLD = "\033[1m"
DIM = "\033[2m"

KIND_GLYPH = {
    PieceKind.SOLDIER: "1",
    PieceKind.FROG: "2",
    PieceKind.SMALL: "3",
    PieceKind.SCISSORS: "4",
    PieceKind.BIG: "5",
    PieceKind.SHIELD: "B",
    PieceKind.SPEAR: "A",
}


def play_console(vs_ai: bool = False) -> None:
    game = Game(vs_ai=vs_ai)
    print(f"{BOLD}{GOLD}STRAKI{RESET} – nach den Regeln von straki.org")
    print(RULES_DE)
    print()
    while True:
        _print_board(game)
        if game.winner is not None:
            print(f"{BOLD}{game.message}{RESET}")
            answer = input("Neue Partie? [j/n] ").strip().lower()
            if answer in {"j", "ja", "y", "yes"}:
                game.reset()
                continue
            return
        if game.vs_ai and game.turn is game.ai_player:
            print("Computer denkt …")
            from straki.ai import choose_turn

            move = choose_turn(game)
            if move is None:
                print("Der Computer hat keinen Zug.")
                return
            game.apply_turn(move)
            continue
        try:
            raw = input(f"{game.turn.label_de}> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAuf Wiedersehen.")
            return
        if not raw:
            continue
        command = raw.lower()
        if command in {"ende", "quit", "exit"}:
            print("Auf Wiedersehen.")
            return
        if command in {"hilfe", "help", "regeln"}:
            print(RULES_DE)
            continue
        if command == "neu":
            game.reset()
            continue
        if command == "ki":
            game.vs_ai = not game.vs_ai
            print("Computergegner", "an" if game.vs_ai else "aus")
            continue
        if command.startswith("rotier"):
            parts = command.split()
            if len(parts) != 2 or parts[1].upper() not in Direction._value2member_map_:
                print("Bitte z. B. „rotier N“ (N/E/S/W).")
                continue
            if not game.rotate(parts[1].upper()):
                print("Rotation nicht möglich.")
            continue
        if command in {"0.5", "halb"}:
            if not game.claim_half_win():
                print("Halbsieg ist gerade nicht möglich.")
            continue
        try:
            _handle_move(game, raw)
        except ValueError as exc:
            print(f"{RED}{exc}{RESET}")


def _handle_move(game: Game, raw: str) -> None:
    parts = raw.replace(",", " ").replace("-", " ").split()
    if len(parts) == 1:
        row, col = parse_square(parts[0])
        game.click(row, col)
        moves = game.moves_for_selected()
        dests = [square_name(*m.end) for m in moves if m.rotate_to is None]
        if dests:
            print("Ziele:", ", ".join(dests))
        return
    if len(parts) != 2:
        raise ValueError("Zug als „H6 G5“ eingeben.")
    if not game.play_text(parts[0], parts[1]):
        raise ValueError("Ungültiger Zug.")
    print(game.message)


def _print_board(game: Game) -> None:
    print()
    files = " ".join(f"{n:>2}"[-2:] for n in range(1, BOARD_SIZE + 1))
    print("   " + files)
    for display in range(BOARD_SIZE - 1, -1, -1):
        cells = [_glyph(game, display, col) for col in range(BOARD_SIZE)]
        print(f"{ROWS[display]}  " + " ".join(cells) + f"  {ROWS[display]}")
    print("   " + files)
    print(game.message)


def _glyph(game: Game, row: int, col: int) -> str:
    piece = game.board.get(row, col)
    selected = game.selected == (row, col)
    dests = {m.end for m in game.moves_for_selected() if m.rotate_to is None}
    if piece is None:
        mark = "+" if (row, col) in dests else "."
        return f"{GOLD}{mark}{RESET}" if mark == "+" else f"{DIM}{mark}{RESET}"
    glyph = KIND_GLYPH[piece.kind]
    if piece.facing is not None:
        glyph = glyph + piece.facing.arrow
    else:
        glyph = glyph + " "
    color = RED if piece.player is Player.RED else BLACK
    if selected:
        return f"{BOLD}{color}{glyph[0]}{RESET}"
    return f"{color}{glyph[0]}{RESET}"
