from __future__ import annotations

import sys
from pathlib import Path


def package_dir() -> Path:
    """Wurzel des straki-Pakets, auch in einer gepackten .exe."""
    meipass = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and meipass:
        return Path(meipass) / "straki"
    return Path(__file__).resolve().parent


def static_dir() -> Path:
    return package_dir() / "static"
