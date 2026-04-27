#!/usr/bin/env python3
"""
Render a DXF to PNG for quick testing without opening a CAD app.

Usage:
    ./.venv/bin/python view_dxf.py window_trim_elevation.dxf
    ./.venv/bin/python view_dxf.py window_trim_elevation.dxf preview.png
"""

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
