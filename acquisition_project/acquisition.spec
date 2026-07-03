# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ["acquisition/main.py"],
    pathex=["."],
    binaries=[],
    datas=[
        ("acquisition/assets/AVDataCollector.png", "acquisition/assets"),
        ("acquisition/assets/AVDataCollector_AppIcon.ico", "acquisition/assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AVDataCollector",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon="acquisition/assets/AVDataCollector_AppIcon.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AVDataCollector",
)
