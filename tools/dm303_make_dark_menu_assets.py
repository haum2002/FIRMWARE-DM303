#!/usr/bin/env python3
"""Build dark nav-menu BMP assets for the DM303 V4.0.1 beta package.

The firmware loads fixed 92x92 16-bit BMP files by filename. This tool keeps
the original BMP headers, dimensions, row layout, and file sizes intact while
recoloring only the blue menu-card background to a dark theme.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path


SOURCE_SYSTEM = Path("backup/DM303 V4.0-read only/system")
OUTPUT_SYSTEM = Path("firmware-candidates/v4.0.1-beta/system")
REPORT = Path("firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS.md")
SUMS = Path("firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS-SHA256.txt")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rgb565_to_rgb(value: int) -> tuple[int, int, int]:
    red = ((value >> 11) & 0x1F) * 255 // 31
    green = ((value >> 5) & 0x3F) * 255 // 63
    blue = (value & 0x1F) * 255 // 31
    return red, green, blue


def rgb_to_rgb565(red: int, green: int, blue: int) -> int:
    red5 = max(0, min(31, round(red * 31 / 255)))
    green6 = max(0, min(63, round(green * 63 / 255)))
    blue5 = max(0, min(31, round(blue * 31 / 255)))
    return (red5 << 11) | (green6 << 5) | blue5


def is_blue_menu_background(red: int, green: int, blue: int) -> bool:
    return (
        red <= 90
        and green <= 150
        and blue >= 70
        and blue >= red + 25
        and green >= red + 8
    )


def darken_background(red: int, green: int, blue: int) -> tuple[int, int, int]:
    luma = (red * 30 + green * 59 + blue * 11) // 100
    lift = min(22, luma // 8)
    return 12 + lift, 14 + lift, 17 + lift


def read_bmp_geometry(data: bytes, path: Path) -> tuple[int, int, int, int]:
    if data[:2] != b"BM":
        raise ValueError(f"not a BMP file: {path}")
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    dib_size = struct.unpack_from("<I", data, 14)[0]
    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    if dib_size != 56 or width != 92 or abs(height) != 92 or bpp != 16 or compression != 3:
        raise ValueError(f"unexpected BMP layout: {path}")
    return pixel_offset, width, height, bpp


def set_pixel(data: bytearray, pixel_offset: int, width: int, height: int, x: int, y: int, value: int) -> None:
    row_size = ((width * 16 + 31) // 32) * 4
    source_y = y if height < 0 else abs(height) - 1 - y
    offset = pixel_offset + source_y * row_size + x * 2
    struct.pack_into("<H", data, offset, value)


def transform_bmp(source: Path, destination: Path) -> tuple[int, str, str]:
    original = source.read_bytes()
    data = bytearray(original)
    pixel_offset, width, height, _ = read_bmp_geometry(original, source)
    row_size = ((width * 16 + 31) // 32) * 4
    changed_pixels = 0

    for y in range(abs(height)):
        row_offset = pixel_offset + y * row_size
        for x in range(width):
            offset = row_offset + x * 2
            value = struct.unpack_from("<H", data, offset)[0]
            red, green, blue = rgb565_to_rgb(value)
            if not is_blue_menu_background(red, green, blue):
                continue
            replacement = rgb_to_rgb565(*darken_background(red, green, blue))
            if replacement != value:
                struct.pack_into("<H", data, offset, replacement)
                changed_pixels += 1

    border = rgb_to_rgb565(42, 46, 52)
    for x in range(width):
        set_pixel(data, pixel_offset, width, height, x, 0, border)
        set_pixel(data, pixel_offset, width, height, x, abs(height) - 1, border)
    for y in range(abs(height)):
        set_pixel(data, pixel_offset, width, height, 0, y, border)
        set_pixel(data, pixel_offset, width, height, width - 1, y, border)

    if len(data) != len(original):
        raise ValueError(f"size changed unexpectedly: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return changed_pixels, sha256_bytes(original), sha256_bytes(data)


def icon_sort_key(path: Path) -> tuple[str, int]:
    stem = path.stem
    prefix = "E" if stem.startswith("icon-E") else "C"
    number_text = stem.removeprefix(f"icon-{prefix}")
    return prefix, int(number_text)


def main() -> int:
    if not SOURCE_SYSTEM.is_dir():
        raise SystemExit(f"Missing source system folder: {SOURCE_SYSTEM}")

    icons = sorted(
        [
            *SOURCE_SYSTEM.glob("icon-E*.bmp"),
            *SOURCE_SYSTEM.glob("icon-C*.bmp"),
        ],
        key=icon_sort_key,
    )
    if not icons:
        raise SystemExit("No menu BMP icons found")

    rows: list[tuple[str, int, str, str]] = []
    for source in icons:
        destination = OUTPUT_SYSTEM / source.name
        changed, source_hash, output_hash = transform_bmp(source, destination)
        rows.append((source.name, changed, source_hash, output_hash))

    SUMS.parent.mkdir(parents=True, exist_ok=True)
    with SUMS.open("w", encoding="utf-8", newline="\n") as handle:
        for name, _, _, output_hash in rows:
            handle.write(f"{output_hash}  system/{name}\n")

    lines = [
        "# DM303 dark nav-menu asset report",
        "",
        "Status: resource-level dark theme assets for `v4.0.1 beta`.",
        "",
        "## Safety scope",
        "",
        "- Source assets in `backup/` are read-only.",
        "- BMP dimensions, headers, row layout, and file sizes are preserved.",
        "- Only blue menu-card background pixels are recolored.",
        "- Firmware code, bootloader, and updater are not touched by this tool.",
        "",
        "## Files",
        "",
        "| File | Recolored pixels | Source SHA-256 | Output SHA-256 |",
        "|---|---:|---|---|",
    ]
    for name, changed, source_hash, output_hash in rows:
        lines.append(f"| `{name}` | {changed} | `{source_hash}` | `{output_hash}` |")
    with REPORT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")

    print(f"source={SOURCE_SYSTEM}")
    print(f"output={OUTPUT_SYSTEM}")
    print(f"icons={len(rows)}")
    print(f"report={REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
