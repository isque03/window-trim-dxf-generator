# Window Trim DXF Generator

Interactive Python CLI for generating a 2D DXF front-elevation drawing of a window, trim, muntins, and lap siding.

The output DXF can be opened in CAD tools such as LibreCAD, QCAD, FreeCAD, AutoCAD, or imported into other CAD workflows.

## Quick start

```bash
chmod +x setup_window_dxf_dev.sh
./setup_window_dxf_dev.sh --no-cad

source .venv/bin/activate
python window_trim_dxf_generator.py
python view_dxf.py window_trim_elevation.dxf
```

On macOS, to install LibreCAD too:

```bash
./setup_window_dxf_dev.sh
```
## Windows 11 setup

Open PowerShell in the repo folder:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_window_dxf_dev_windows.ps1

## Full test

```bash
./run_test.sh
```

This will:

1. Generate a DXF.
2. Render a PNG preview.
3. Open LibreCAD on macOS if installed.

## Files

| File | Purpose |
|---|---|
| `window_trim_dxf_generator.py` | Interactive DXF generator |
| `setup_window_dxf_dev.sh` | Creates local `.venv`, installs dependencies, optionally installs LibreCAD |
| `view_dxf.py` | Created by setup script; renders DXF to PNG |
| `run_test.sh` | Created by setup script; generates and previews a DXF |

## Dimensions

The generator asks for dimensions in inches:

- overall outside trim width
- overall outside trim height
- side casing width
- head casing height
- sill/apron height
- sill projection
- center mullion width
- sash/frame border width
- meeting rail height
- muntin width
- glass grid layout
- lap siding exposure
- siding field margin

## Notes

This is intended for layout, communication, and CAD import testing. Verify field measurements before using output for fabrication.
