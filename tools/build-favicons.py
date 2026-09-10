#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["cairosvg", "pillow"]
# ///
"""Rasterize Images/favicon.svg into every icon the site ships.

The SVG is the single source of truth. Run this after editing it so the rasters
can never drift:

    uv run tools/build-favicons.py

Needs the cairo system library (macOS: `brew install cairo`).
"""
from __future__ import annotations

import io
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Images" / "favicon.svg"

# Largest raster we emit. Everything else is a Lanczos reduction of the same
# supersampled master, so no size is rendered at its final resolution.
MASTER = 512
SUPERSAMPLE = 4

# ICO carries the small sizes browsers ask for; Google reads any of them.
ICO_SIZES = [16, 32, 48]
PNG_TARGETS = {
    "Images/icon-512.png": 512,
    "Images/icon-192.png": 192,
    "Images/apple-touch-icon.png": 180,
}


def render_master() -> Image.Image:
    """Rasterize the SVG at 4x the master size for antialiasing headroom."""
    png = cairosvg.svg2png(
        url=str(SOURCE),
        output_width=MASTER * SUPERSAMPLE,
        output_height=MASTER * SUPERSAMPLE,
    )
    return Image.open(io.BytesIO(png)).convert("RGBA")


def down(master: Image.Image, size: int) -> Image.Image:
    return master.resize((size, size), Image.Resampling.LANCZOS)


def main() -> None:
    master = render_master()
    print(f"master render: {master.size[0]}x{master.size[1]} from {SOURCE.name}")

    for rel, size in PNG_TARGETS.items():
        out = ROOT / rel
        down(master, size).save(out, format="PNG", optimize=True)
        print(f"  {rel:<32} {size}x{size}  {out.stat().st_size:>6,}B")

    # Pillow would resize internally on ICO save; pass pre-reduced frames so every
    # entry goes through Lanczos rather than the default filter.
    frames = [down(master, s) for s in ICO_SIZES]
    ico = ROOT / "favicon.ico"
    frames[-1].save(
        ico, format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
        append_images=frames[:-1],
    )
    print(f"  {'favicon.ico':<32} {'+'.join(map(str, ICO_SIZES))}  {ico.stat().st_size:>6,}B")


if __name__ == "__main__":
    main()
