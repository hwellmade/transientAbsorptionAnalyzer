# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas = [('transient_absorption_analyser/resources/*', 'resources/')]
binaries = [('C:\\Users\\jilin\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\transient-absorption-analyser-lJUUFmmh-py3.11\\Lib\\site-packages\\PySide6\\plugins\\platforms\\*', 'platforms/'), ('C:\\Users\\jilin\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\transient-absorption-analyser-lJUUFmmh-py3.11\\Lib\\site-packages\\PySide6\\plugins\\styles\\*', 'styles/'), ('C:\\Users\\jilin\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\transient-absorption-analyser-lJUUFmmh-py3.11\\Lib\\site-packages\\PySide6\\Qt6Core.dll', '.'), ('C:\\Users\\jilin\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\transient-absorption-analyser-lJUUFmmh-py3.11\\Lib\\site-packages\\PySide6\\Qt6Gui.dll', '.'), ('C:\\Users\\jilin\\AppData\\Local\\pypoetry\\Cache\\virtualenvs\\transient-absorption-analyser-lJUUFmmh-py3.11\\Lib\\site-packages\\PySide6\\Qt6Widgets.dll', '.')]
hiddenimports = ['numpy', 'pandas', 'matplotlib', 'scipy', 'PySide6', 'PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui']
datas += collect_data_files('matplotlib')
datas += collect_data_files('scipy')
datas += collect_data_files('numpy')
datas += collect_data_files('pandas')
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('matplotlib')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['transient_absorption_analyser\\src\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='TransientAbsorptionAnalyser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['transient_absorption_analyser\\resources\\icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TransientAbsorptionAnalyser',
)
