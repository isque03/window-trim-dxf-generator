#!/usr/bin/env python3
"""
Interactive CLI that asks for window, trim, and siding dimensions and generates
a DXF front-elevation drawing that can be imported into CAD systems.

Install:
    pip install -r requirements.txt

Run:
    python window_trim_dxf_generator.py

Units:
    Inches by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ezdxf


@dataclass
class WindowSpec:
    output_file: str
    overall_width: float
    overall_height: float
    side_casing: float
    head_casing: float
    sill_height: float
    sill_projection: float
    center_mullion: float
    sash_frame: float
    meeting_rail: float
    muntin_width: float
    columns_per_sash: int
    rows_per_sash: int
    siding_exposure: float
    siding_margin: float


def ask_float(prompt: str, default: float) -> float:
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    return float(raw)


def ask_int(prompt: str, default: int) -> int:
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    return int(raw)


def ask_str(prompt: str, default: str) -> str:
    raw = input(f"{prompt} [{default}]: ").strip()
    return raw or default


def collect_spec() -> WindowSpec:
    print("\nWindow + Trim DXF Generator")
    print("Enter dimensions in inches. Press Enter to accept defaults.\n")

    return WindowSpec(
        output_file=ask_str("Output DXF file", "window_trim_elevation.dxf"),
        overall_width=ask_float("Overall outside trim width", 75.0),
        overall_height=ask_float("Overall outside trim height, including sill/apron", 72.5),
        side_casing=ask_float("Left/right casing width", 5.5),
        head_casing=ask_float("Top/head casing height", 5.5),
        sill_height=ask_float("Bottom sill/apron height", 4.5),
        sill_projection=ask_float("Sill projection past side casing, each side", 2.0),
        center_mullion=ask_float("Center mullion width between two windows", 3.5),
        sash_frame=ask_float("Sash/frame border width", 2.0),
        meeting_rail=ask_float("Meeting rail height", 2.0),
        muntin_width=ask_float("Muntin line width", 0.75),
        columns_per_sash=ask_int("Glass columns per sash", 3),
        rows_per_sash=ask_int("Glass rows per full window unit", 6),
        siding_exposure=ask_float("Horizontal lap siding exposure", 4.0),
        siding_margin=ask_float("Siding field margin around window", 12.0),
    )


def add_rect(msp, x: float, y: float, w: float, h: float, layer: str):
    points = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    msp.add_lwpolyline(points, dxfattribs={"layer": layer})


def add_text(msp, value: str, x: float, y: float, height: float = 1.25, layer: str = "TEXT"):
    msp.add_text(value, dxfattribs={"height": height, "layer": layer}).set_placement((x, y))


def add_dim_h(msp, x1: float, x2: float, y: float, label: str):
    msp.add_line((x1, y), (x2, y), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x1, y - 0.6), (x1, y + 0.6), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x2, y - 0.6), (x2, y + 0.6), dxfattribs={"layer": "DIMENSIONS"})
    add_text(msp, label, (x1 + x2) / 2 - len(label) * 0.25, y + 0.8, 1.0, "DIMENSIONS")


def add_dim_v(msp, x: float, y1: float, y2: float, label: str):
    msp.add_line((x, y1), (x, y2), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x - 0.6, y1), (x + 0.6, y1), dxfattribs={"layer": "DIMENSIONS"})
    msp.add_line((x - 0.6, y2), (x + 0.6, y2), dxfattribs={"layer": "DIMENSIONS"})
    add_text(msp, label, x + 0.8, (y1 + y2) / 2, 1.0, "DIMENSIONS")


def generate_dxf(spec: WindowSpec) -> Path:
    doc = ezdxf.new("R2010")
    doc.units = ezdxf.units.IN

    for layer, color in [
        ("SIDING", 8),
        ("TRIM", 5),
        ("WINDOW_FRAME", 1),
        ("GLASS", 4),
        ("MUNTINS", 3),
        ("DIMENSIONS", 2),
        ("TEXT", 7),
    ]:
        doc.layers.add(name=layer, color=color)

    msp = doc.modelspace()

    ow = spec.overall_width
    oh = spec.overall_height

    sx = -spec.siding_margin
    sy = -spec.siding_margin
    sw = ow + spec.siding_margin * 2
    sh = oh + spec.siding_margin * 2

    y = sy
    while y <= sy + sh:
        msp.add_line((sx, y), (sx + sw, y), dxfattribs={"layer": "SIDING"})
        y += spec.siding_exposure

    add_rect(msp, 0, 0, ow, oh, "TRIM")
    add_rect(msp, 0, oh - spec.head_casing, ow, spec.head_casing, "TRIM")

    inner_x = spec.side_casing
    inner_y = spec.sill_height
    inner_w = ow - 2 * spec.side_casing
    inner_h = oh - spec.head_casing - spec.sill_height

    add_rect(msp, 0, inner_y, spec.side_casing, inner_h, "TRIM")
    add_rect(msp, ow - spec.side_casing, inner_y, spec.side_casing, inner_h, "TRIM")
    add_rect(msp, -spec.sill_projection, 0, ow + spec.sill_projection * 2, spec.sill_height, "TRIM")
    add_rect(msp, inner_x, inner_y, inner_w, inner_h, "WINDOW_FRAME")

    unit_w = (inner_w - spec.center_mullion) / 2
    unit_h = inner_h
    mullion_x = inner_x + unit_w
    add_rect(msp, mullion_x, inner_y, spec.center_mullion, unit_h, "TRIM")

    for ux in [inner_x, inner_x + unit_w + spec.center_mullion]:
        uy = inner_y
        add_rect(msp, ux, uy, unit_w, unit_h, "WINDOW_FRAME")

        gx = ux + spec.sash_frame
        gy = uy + spec.sash_frame
        gw = unit_w - 2 * spec.sash_frame
        gh = unit_h - 2 * spec.sash_frame

        add_rect(msp, gx, gy, gw, gh, "GLASS")

        meeting_y = gy + gh / 2 - spec.meeting_rail / 2
        add_rect(msp, gx, meeting_y, gw, spec.meeting_rail, "WINDOW_FRAME")

        if spec.columns_per_sash > 1:
            for i in range(1, spec.columns_per_sash):
                mx = gx + gw * i / spec.columns_per_sash
                add_rect(msp, mx - spec.muntin_width / 2, gy, spec.muntin_width, gh, "MUNTINS")

        if spec.rows_per_sash > 1:
            for i in range(1, spec.rows_per_sash):
                my = gy + gh * i / spec.rows_per_sash
                add_rect(msp, gx, my - spec.muntin_width / 2, gw, spec.muntin_width, "MUNTINS")

    add_dim_h(msp, 0, ow, oh + 4, f'Overall width: {ow:g}"')
    add_dim_h(msp, inner_x, inner_x + inner_w, oh + 7, f'Inside casing opening: {inner_w:g}"')
    add_dim_h(msp, inner_x, inner_x + unit_w, oh + 10, f'Each unit: {unit_w:g}"')
    add_dim_h(msp, mullion_x, mullion_x + spec.center_mullion, oh + 13, f'Mullion: {spec.center_mullion:g}"')

    add_dim_v(msp, ow + 4, 0, oh, f'Overall height: {oh:g}"')
    add_dim_v(msp, ow + 8, inner_y, inner_y + inner_h, f'Inside height: {inner_h:g}"')
    add_dim_v(msp, -4, oh - spec.head_casing, oh, f'Head: {spec.head_casing:g}"')
    add_dim_v(msp, -8, 0, spec.sill_height, f'Sill/apron: {spec.sill_height:g}"')
    add_dim_v(msp, -12, 0, spec.siding_exposure, f'Siding exposure: {spec.siding_exposure:g}"')

    add_text(msp, "WINDOW + TRIM FRONT ELEVATION", 0, oh + 17, 1.5)
    add_text(msp, "Units: inches. Verify field measurements before fabrication.", 0, -8, 1.0)

    path = Path(spec.output_file).expanduser().resolve()
    doc.saveas(path)
    return path


def main():
    spec = collect_spec()

    if spec.overall_width <= 0 or spec.overall_height <= 0:
        raise ValueError("Overall width and height must be positive.")

    if spec.side_casing * 2 + spec.center_mullion >= spec.overall_width:
        raise ValueError("Casing + mullion are wider than the total window width.")

    if spec.head_casing + spec.sill_height >= spec.overall_height:
        raise ValueError("Head casing + sill/apron are taller than the total window height.")

    path = generate_dxf(spec)
    print(f"\nCreated DXF: {path}")


if __name__ == "__main__":
    main()
