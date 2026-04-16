# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

# In PyInstaller spec execution, __file__ is not guaranteed.
# SPECPATH points to the folder containing this spec file.
project_root = Path(SPECPATH).resolve()
manual_pdf = project_root / "docs" / "manual_simplificado.pdf"

datas = []
if manual_pdf.exists():
    datas.append((str(manual_pdf), "docs"))

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="DolceNeves",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
