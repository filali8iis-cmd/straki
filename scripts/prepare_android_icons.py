#!/usr/bin/env python3
"""Erzeugt Launcher- und Splash-Bilder aus straki/static/logo.png."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "straki" / "static" / "logo.png"
RES = ROOT / "android" / "app" / "src" / "main" / "res"
BG = (196, 69, 54, 255)
CREAM = (244, 241, 234, 255)

DENSITIES = {
    "mdpi": 1,
    "hdpi": 1.5,
    "xhdpi": 2,
    "xxhdpi": 3,
    "xxxhdpi": 4,
}


def fit(image: Image.Image, box: int, padding: float = 0.72) -> Image.Image:
    inner = max(1, int(box * padding))
    copy = image.convert("RGBA")
    copy.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    canvas.paste(copy, ((box - copy.width) // 2, (box - copy.height) // 2), copy)
    return canvas


def solid(size: int, color: tuple[int, int, int, int], overlay: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), color)
    canvas.alpha_composite(overlay)
    return canvas


def main() -> None:
    logo = Image.open(LOGO).convert("RGBA")
    for name, scale in DENSITIES.items():
        mip = RES / f"mipmap-{name}"
        mip.mkdir(parents=True, exist_ok=True)
        launcher = solid(int(48 * scale), BG, fit(logo, int(48 * scale), 0.78))
        launcher.save(mip / "ic_launcher.png")
        launcher.save(mip / "ic_launcher_round.png")
        fit(logo, int(108 * scale), 0.58).save(mip / "ic_launcher_foreground.png")

        splash = solid(int(320 * scale), CREAM, fit(logo, int(320 * scale), 0.7))
        for folder in (f"drawable-port-{name}", f"drawable-land-{name}"):
            dest = RES / folder
            dest.mkdir(parents=True, exist_ok=True)
            splash.save(dest / "splash.png")

    RES.joinpath("drawable").mkdir(parents=True, exist_ok=True)
    solid(1024, CREAM, fit(logo, 1024, 0.7)).save(RES / "drawable" / "splash.png")
    print("Android-Icons aktualisiert.")


if __name__ == "__main__":
    main()
