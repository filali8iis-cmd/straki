from __future__ import annotations

import argparse

from straki.console import play_console
from straki.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STRAKI – strategisches Brettspiel mit eigenem Spielfenster."
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Im Terminal spielen",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Im Browser spielen statt im eigenen Fenster",
    )
    parser.add_argument(
        "--ai",
        action="store_true",
        help="Gegen den Computer starten (Computer spielt Schwarz)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Beim Webmodus den Browser nicht automatisch öffnen",
    )
    args = parser.parse_args()
    if args.console:
        play_console(vs_ai=args.ai)
        return
    if args.web:
        serve(
            host=args.host,
            port=args.port,
            vs_ai=args.ai,
            open_browser=not args.no_browser,
        )
        return
    try:
        from straki.gui import run_gui
    except ImportError as exc:
        raise SystemExit(
            "Für das Spielfenster wird pygame benötigt.\n"
            "Bitte installieren:  pip install -r requirements.txt"
        ) from exc
    run_gui(vs_ai=args.ai)


if __name__ == "__main__":
    main()
