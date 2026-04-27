#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
CAD_APP="librecad"
INSTALL_CAD="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-cad)
      INSTALL_CAD="false"
      shift
      ;;
    --cad)
      CAD_APP="${2:-librecad}"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--no-cad] [--cad librecad|qcad]"
      exit 1
      ;;
  esac
done

cd "$ROOT_DIR"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Install it first:"
  echo "  brew install python"
  exit 1
fi

python3 -m venv "$VENV_DIR"
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

cat > "${ROOT_DIR}/view_dxf.py" <<'PY'
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
PY

chmod +x "${ROOT_DIR}/view_dxf.py"

if [[ "$INSTALL_CAD" == "true" ]]; then
  if [[ "$(uname -s)" == "Darwin" ]] && command -v brew >/dev/null 2>&1; then
    case "$CAD_APP" in
      librecad) brew install --cask librecad ;;
      qcad) brew install --cask qcad ;;
      *)
        echo "Unsupported CAD app: ${CAD_APP}"
        echo "Supported: librecad, qcad"
        exit 1
        ;;
    esac
  else
    echo "Skipping CAD install. Auto-install is configured for macOS/Homebrew only."
  fi
fi

cat > "${ROOT_DIR}/run_test.sh" <<'RUN'
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
source .venv/bin/activate

python window_trim_dxf_generator.py
python view_dxf.py window_trim_elevation.dxf

if [[ "$(uname -s)" == "Darwin" ]] && [[ -d "/Applications/LibreCAD.app" ]]; then
  open -a LibreCAD window_trim_elevation.dxf
fi
RUN

chmod +x "${ROOT_DIR}/run_test.sh"

echo "Setup complete."
