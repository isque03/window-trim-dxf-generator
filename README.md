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
```

## Example with custom dimensions

```console
$ python window_trim_dxf_generator.py

Output DXF file [window_trim_elevation.dxf]: front_window.dxf
Overall outside trim width [75.0]: 80
Overall outside trim height, including sill/apron [72.5]: 74
Left/right casing width [5.5]: 5
Top/head casing height [5.5]: 5
Bottom sill/apron height [4.5]: 4
Sill projection past side casing, each side [2.0]: 2
Center mullion width between two windows [3.5]: 3.5
Sash/frame border width [2.0]: 2
Meeting rail height [2.0]: 2
Muntin line width [0.75]: 0.75
Glass columns per sash [3]: 3
Glass rows per full window unit [6]: 6
Horizontal lap siding exposure [4.0]: 4
Siding field margin around window [12.0]: 12

Created DXF: /path/to/front_window.dxf
```

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
