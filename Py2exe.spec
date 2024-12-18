a = Analysis(
    ['PSgui.py'],
    pathex=[],
    binaries=[
        (r'C:\WINDOWS\Microsoft.Net\assembly\GAC_MSIL\System.Management.Automation\v4.0_3.0.0.0__31bf3856ad364e35\System.Management.Automation.dll', '.')
    ],
    datas=[],
    hiddenimports=['clr', 'System.Management.Automation'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,  # This can remain but is not used in this case
    noarchive=False,
    console=False,  # Hide console window
    windowed=True   # Ensure windowed mode
)

pyz = PYZ(a.pure, a.zipped_data)  # Updated to remove cipher

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PSgui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_hooks=[],
    console=False,  # Explicitly set console to False
    onefile=True,   # Create single-file executable
    icon='powershell_folder_icon_250656.ico'
)
