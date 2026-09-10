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
import struct
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


def dib_frame(im: Image.Image) -> bytes:
    """One ICO frame as a 32-bit BGRA DIB.

    Pillow's ICO writer emits PNG-compressed frames at every size, but PNG inside
    ICO is only dependably supported at 256x256. Decoders that miss it at 16-48px
    fall back or flatten the alpha onto a solid ground, which loses the
    transparency. BMP/DIB is the encoding those sizes are expected to use.
    """
    w, h = im.size
    px = im.load()

    # XOR bitmap: BGRA, bottom-up.
    xor = bytearray()
    for y in range(h - 1, -1, -1):
        for x in range(w):
            r, g, b, a = px[x, y]
            xor += bytes((b, g, r, a))

    # AND mask: 1bpp, bottom-up, each row padded to 4 bytes. Alpha already carries
    # the transparency, so the mask stays clear; it is required to be present.
    row_bytes = ((w + 31) // 32) * 4
    and_mask = bytes(row_bytes * h)

    header = struct.pack(
        "<IiiHHIIiiII",
        40,        # biSize
        w,         # biWidth
        h * 2,     # biHeight, doubled to cover XOR + AND
        1,         # biPlanes
        32,        # biBitCount
        0,         # biCompression = BI_RGB
        len(xor) + len(and_mask),
        0, 0, 0, 0,
    )
    return header + bytes(xor) + and_mask


def build_ico(frames: list[Image.Image]) -> bytes:
    """Pack frames into an ICO with a directory entry per size."""
    blobs = [dib_frame(f.convert("RGBA")) for f in frames]
    offset = 6 + 16 * len(blobs)
    directory = b""
    for frame, blob in zip(frames, blobs):
        w, h = frame.size
        directory += struct.pack(
            "<BBBBHHII",
            w if w < 256 else 0,
            h if h < 256 else 0,
            0,      # palette entries
            0,      # reserved
            1,      # colour planes
            32,     # bits per pixel
            len(blob),
            offset,
        )
        offset += len(blob)
    return struct.pack("<HHH", 0, 1, len(blobs)) + directory + b"".join(blobs)


def main() -> None:
    master = render_master()
    print(f"master render: {master.size[0]}x{master.size[1]} from {SOURCE.name}")

    for rel, size in PNG_TARGETS.items():
        out = ROOT / rel
        down(master, size).save(out, format="PNG", optimize=True)
        print(f"  {rel:<32} {size}x{size}  {out.stat().st_size:>6,}B")

    frames = [down(master, s) for s in ICO_SIZES]
    ico = ROOT / "favicon.ico"
    ico.write_bytes(build_ico(frames))
    print(f"  {'favicon.ico':<32} {'+'.join(map(str, ICO_SIZES))}  {ico.stat().st_size:>6,}B")


if __name__ == "__main__":
    main()
