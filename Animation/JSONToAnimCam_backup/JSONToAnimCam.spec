# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

alembic_datas, alembic_binaries, alembic_hidden = collect_all("alembic3d")
imath_datas, imath_binaries, imath_hidden = collect_all("imath")

analysis = Analysis(
    ["JSONToAnimCam.py"],
    pathex=[],
    binaries=alembic_binaries + imath_binaries,
    datas=alembic_datas + imath_datas,
    hiddenimports=alembic_hidden + imath_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="JSONToAnimCam",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
)

collect = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="JSONToAnimCam",
)
