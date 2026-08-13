# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-Spezifikation: eine Datei STRAKI.exe (Windows) bzw. STRAKI (Linux)."""

from pathlib import Path

spec_dir = Path(SPECPATH)
datas = [(str(spec_dir / "straki" / "static"), "straki/static")]
icon = spec_dir / "build" / "STRAKI.ico"

a = Analysis(
    [str(spec_dir / "main.py")],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "straki",
        "straki.gui",
        "straki.game",
        "straki.ai",
        "straki.board",
        "straki.moves",
        "straki.layout",
        "straki.paths",
        "straki.models",
        "straki.constants",
        "pygame",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pygame.tests", "pygame.examples", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="STRAKI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon) if icon.is_file() else None,
)
