# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None

# In PyInstaller spec execution, __file__ is not guaranteed.
# SPECPATH points to the folder containing this spec file.
project_root = Path(SPECPATH).resolve()
manual_pdf = project_root / "docs" / "manual_simplificado.pdf"
app_icon_png = project_root / "assets" / "icon.png"
app_icon_ico = project_root / "assets" / "icon.ico"

if app_icon_png.exists() and Image is not None:
    Image.open(app_icon_png).save(
        app_icon_ico,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (256, 256)],
    )

datas = []
if manual_pdf.exists():
    datas.append((str(manual_pdf), "docs"))
if app_icon_png.exists():
    datas.append((str(app_icon_png), "assets"))

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
    icon=str(app_icon_ico) if app_icon_ico.exists() else None,
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
