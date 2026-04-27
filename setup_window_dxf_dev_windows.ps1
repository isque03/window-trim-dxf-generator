# setup_window_dxf_dev_windows.ps1
#
# Windows 11 setup script for Window Trim DXF Generator.
#
# Run from PowerShell in the same folder as window_trim_dxf_generator.py:
#
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\setup_window_dxf_dev_windows.ps1
#
# Optional:
#   .\setup_window_dxf_dev_windows.ps1 -NoCad
#   .\setup_window_dxf_dev_windows.ps1 -CadApp LibreCAD
#
# What it does:
#   - Installs Python 3 via winget if Python is missing
#   - Creates .venv in the current folder
#   - Installs Python dependencies
#   - Creates view_dxf.py for PNG preview rendering
#   - Optionally installs LibreCAD using winget
#   - Creates run_test_windows.ps1

param(
    [switch]$NoCad,
    [ValidateSet("LibreCAD", "QCAD")]
    [string]$CadApp = "LibreCAD"
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $RootDir ".venv"

Set-Location $RootDir

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Refresh-Path {
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
}

if (-not (Test-CommandExists "winget")) {
    Write-Host "winget is required. Install App Installer from Microsoft Store, then rerun this script."
    exit 1
}

$pythonCmd = $null

if (Test-CommandExists "py") {
    $pythonCmd = "py -3"
} elseif (Test-CommandExists "python") {
    $pythonCmd = "python"
} else {
    Write-Host "Python not found. Installing Python 3 via winget..."
    winget install --id Python.Python.3.12 --source winget --accept-package-agreements --accept-source-agreements
    Refresh-Path

    if (Test-CommandExists "py") {
        $pythonCmd = "py -3"
    } elseif (Test-CommandExists "python") {
        $pythonCmd = "python"
    } else {
        Write-Host "Python was installed, but it is not available in PATH yet."
        Write-Host "Close and reopen PowerShell, then rerun this script."
        exit 1
    }
}

Write-Host "Using Python command: $pythonCmd"

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating local Python environment: $VenvDir"
    Invoke-Expression "$pythonCmd -m venv `"$VenvDir`""
} else {
    Write-Host "Using existing environment: $VenvDir"
}

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

& $VenvPython -m pip install --upgrade pip

if (Test-Path "requirements.txt") {
    & $VenvPython -m pip install -r requirements.txt
} else {
    & $VenvPython -m pip install ezdxf matplotlib
}

$ViewDxfPath = Join-Path $RootDir "view_dxf.py"

@'
#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import ezdxf
from ezdxf.addons.drawing import matplotlib
from ezdxf.addons.drawing.config import Configuration
from ezdxf.addons.drawing.frontend import Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend


def render_dxf(input_path: Path, output_path: Path) -> None:
    doc = ezdxf.readfile(input_path)
    msp = doc.modelspace()

    fig = matplotlib.plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")
    ax.axis("off")

    ctx = ezdxf.addons.drawing.RenderContext(doc)
    backend = MatplotlibBackend(ax)
    Frontend(ctx, backend, config=Configuration()).draw_layout(msp, finalize=True)

    fig.savefig(output_path, dpi=200, bbox_inches="tight", pad_inches=0.25)
    matplotlib.plt.close(fig)


def main() -> None:
    if len(sys.argv) not in (2, 3):
        raise SystemExit("Usage: view_dxf.py input.dxf [output.png]")

    input_path = Path(sys.argv[1]).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"DXF not found: {input_path}")

    output_path = (
        Path(sys.argv[2]).expanduser().resolve()
        if len(sys.argv) == 3
        else input_path.with_suffix(".png")
    )

    render_dxf(input_path, output_path)
    print(f"Rendered: {output_path}")


if __name__ == "__main__":
    main()
'@ | Set-Content -Path $ViewDxfPath -Encoding UTF8

if (-not $NoCad) {
    if ($CadApp -eq "LibreCAD") {
        Write-Host "Installing LibreCAD via winget..."
        winget install --id LibreCAD.LibreCAD --source winget --accept-package-agreements --accept-source-agreements
    } elseif ($CadApp -eq "QCAD") {
        Write-Host "Installing QCAD via winget..."
        winget install --id RibbonSoft.QCAD --source winget --accept-package-agreements --accept-source-agreements
    }
} else {
    Write-Host "Skipping CAD install."
}

$RunTestPath = Join-Path $RootDir "run_test_windows.ps1"

@'
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$Python = Join-Path $RootDir ".venv\Scripts\python.exe"

& $Python window_trim_dxf_generator.py
& $Python view_dxf.py window_trim_elevation.dxf

if (Test-Path "window_trim_elevation.png") {
    Start-Process "window_trim_elevation.png"
}

if (Test-Path "window_trim_elevation.dxf") {
    Start-Process "window_trim_elevation.dxf"
}
'@ | Set-Content -Path $RunTestPath -Encoding UTF8

Write-Host ""
Write-Host "Setup complete."
Write-Host ""
Write-Host "Use:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python window_trim_dxf_generator.py"
Write-Host "  python view_dxf.py window_trim_elevation.dxf"
Write-Host ""
Write-Host "Or run:"
Write-Host "  .\run_test_windows.ps1"
