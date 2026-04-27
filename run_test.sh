#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

source .venv/bin/activate

python window_trim_dxf_generator.py
python view_dxf.py window_trim_elevation.dxf

if [[ "$(uname -s)" == "Darwin" ]] && [[ -d "/Applications/QCAD.app" ]]; then
  open -a /Applications/QCAD.app window_trim_elevation.dxf
fi
