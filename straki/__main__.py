from __future__ import annotations

import argparse

from straki.console import play_console
from straki.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(
        description="STRAKI – strategisches Brettspiel nach straki.org."
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Im Terminal spielen statt im Browser",
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
        help="Browser nicht automatisch öffnen",
    )
    args = parser.parse_args()
    if args.console:
        play_console(vs_ai=args.ai)
        return
    serve(
        host=args.host,
        port=args.port,
        vs_ai=args.ai,
        open_browser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
