from __future__ import annotations

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from straki.ai import choose_turn
from straki.constants import RULES_DE
from straki.game import Game

STATIC_DIR = Path(__file__).resolve().parent / "static"
_lock = threading.Lock()
_game = Game()


def serve(
    host: str = "127.0.0.1",
    port: int = 8765,
    vs_ai: bool = False,
    open_browser: bool = True,
) -> None:
    global _game
    with _lock:
        _game = Game(vs_ai=vs_ai)
    httpd = ThreadingHTTPServer((host, port), StrakiHandler)
    url = f"http://{host}:{port}/"
    print(f"Straki läuft unter {url}", flush=True)
    print("Zum Beenden Strg+C drücken.", flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer beendet.")
    finally:
        httpd.server_close()


class StrakiHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/state":
            self._send_json(self._state())
            return
        if path == "/api/rules":
            self._send_json({"text": RULES_DE})
            return
        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        payload = self._read_json()
        with _lock:
            if path == "/api/click":
                _game.click(int(payload["row"]), int(payload["col"]))
                data = _game.to_dict()
            elif path == "/api/rotate":
                _game.rotate(str(payload.get("direction", "")))
                data = _game.to_dict()
            elif path == "/api/half":
                _game.claim_half_win()
                data = _game.to_dict()
            elif path == "/api/new":
                _game.reset(vs_ai=bool(payload.get("vsAi", _game.vs_ai)))
                data = _game.to_dict()
            elif path == "/api/ai":
                if (
                    _game.vs_ai
                    and _game.winner is None
                    and _game.turn is _game.ai_player
                ):
                    move = choose_turn(_game)
                    if move:
                        _game.apply_turn(move)
                data = _game.to_dict()
            else:
                data = None
        if data is None:
            self._send_bytes(b'{"error":"not found"}', 404, "application/json")
            return
        self._send_json(data)

    def _state(self) -> dict[str, object]:
        with _lock:
            return _game.to_dict()

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        data = json.loads(raw.decode("utf-8"))
        return data if isinstance(data, dict) else {}

    def _serve_static(self, path: str) -> None:
        rel = "index.html" if path in {"/", "/index.html"} else path.lstrip("/")
        candidate = (STATIC_DIR / rel).resolve()
        if not str(candidate).startswith(str(STATIC_DIR.resolve())) or not candidate.is_file():
            self._send_bytes(b"Not found", 404, "text/plain")
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".png": "image/png",
            ".svg": "image/svg+xml",
        }.get(candidate.suffix, "application/octet-stream")
        self._send_bytes(candidate.read_bytes(), 200, content_type)

    def _send_json(self, data: dict[str, object]) -> None:
        self._send_bytes(json.dumps(data).encode("utf-8"), 200, "application/json; charset=utf-8")

    def _send_bytes(self, body: bytes, status: int, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
