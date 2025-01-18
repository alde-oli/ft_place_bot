# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ft_place_bot/__main__.py'],
    pathex=['ft_place_bot'],
    binaries=[],
    datas=[('README.md', '.')],
    hiddenimports=['ft_place_bot.client.client_api', 'ft_place_bot.config', 'ft_place_bot.core.color_config', 'ft_place_bot.core.image_monitor', 'ft_place_bot.utils.utils'],
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
    a.binaries,
    a.datas,
    [],
    name='ft_place_bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
