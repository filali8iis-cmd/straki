#!/usr/bin/env python3
"""Baut STRAKI als einzelne ausführbare Datei (unter Windows: STRAKI.exe)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "straki" / "static" / "logo.png"
ICON = ROOT / "build" / "STRAKI.ico"


def _write_icon() -> None:
    ICON.parent.mkdir(parents=True, exist_ok=True)
    if not LOGO.is_file():
        return
    try:
        from PIL import Image
    except ImportError:
        return
    image = Image.open(LOGO).convert("RGBA")
    image.save(
        ICON,
        sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)],
    )


def main() -> None:
    _write_icon()
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        str(ROOT / "STRAKI.spec"),
    ]
    print(" ", " ".join(cmd), flush=True)
    subprocess.check_call(cmd, cwd=ROOT)
    dist = ROOT / "dist"
    built = list(dist.glob("STRAKI*"))
    if not built:
        raise SystemExit("Build fertig, aber keine Datei in dist/ gefunden.")
    print("Fertig:", ", ".join(str(path) for path in built), flush=True)


if __name__ == "__main__":
    main()
