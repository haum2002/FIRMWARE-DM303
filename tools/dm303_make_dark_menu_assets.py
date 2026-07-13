#!/usr/bin/env python3
"""Build Soft Eye nav-menu BMP assets for the DM303 V4.0.1 beta package.

The firmware loads fixed 92x92 16-bit BMP files by filename. This tool keeps
the original BMP headers, dimensions, row layout, and file sizes intact while
recoloring the connected menu-card background and softening harsh foreground
whites/yellows without rescaling any glyphs.
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


def soft_eye_background_color(x: int, y: int, width: int, height: int) -> tuple[int, int, int]:
    # Muted charcoal/green-gray keeps contrast usable without pure black or
    # harsh white. The lift keeps the fixed 92x92 asset from looking flat.
    vertical = int(8 * y / max(1, height - 1))
    cx = abs(x - (width - 1) / 2) / max(1, width / 2)
    cy = abs(y - (height - 1) / 2) / max(1, height / 2)
    center = max(0, int(7 * (1.0 - min(1.0, (cx * cx + cy * cy) ** 0.5))))
    lift = vertical + center
    return 18 + lift, 23 + lift, 24 + lift


def soft_eye_foreground_color(red: int, green: int, blue: int) -> tuple[int, int, int] | None:
    if red >= 210 and green >= 210 and blue >= 200:
        return 213, 211, 198
    if red >= 195 and green >= 155 and blue <= 95:
        return 232, 190, 56
    return None


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


def get_pixel(data: bytes | bytearray, pixel_offset: int, width: int, height: int, x: int, y: int) -> int:
    row_size = ((width * 16 + 31) // 32) * 4
    source_y = y if height < 0 else abs(height) - 1 - y
    offset = pixel_offset + source_y * row_size + x * 2
    return struct.unpack_from("<H", data, offset)[0]


def connected_background_mask(data: bytes, pixel_offset: int, width: int, height: int) -> set[tuple[int, int]]:
    abs_height = abs(height)
    mask: set[tuple[int, int]] = set()
    queue: list[tuple[int, int]] = []

    def maybe_add(x: int, y: int) -> None:
        if not (0 <= x < width and 0 <= y < abs_height) or (x, y) in mask:
            return
        red, green, blue = rgb565_to_rgb(get_pixel(data, pixel_offset, width, height, x, y))
        if is_blue_menu_background(red, green, blue):
            mask.add((x, y))
            queue.append((x, y))

    for x in range(width):
        maybe_add(x, 0)
        maybe_add(x, abs_height - 1)
    for y in range(abs_height):
        maybe_add(0, y)
        maybe_add(width - 1, y)

    index = 0
    while index < len(queue):
        x, y = queue[index]
        index += 1
        maybe_add(x + 1, y)
        maybe_add(x - 1, y)
        maybe_add(x, y + 1)
        maybe_add(x, y - 1)
    return mask


def transform_bmp(source: Path, destination: Path) -> tuple[int, str, str]:
    original = source.read_bytes()
    data = bytearray(original)
    pixel_offset, width, height, _ = read_bmp_geometry(original, source)
    changed_pixels = 0
    bg_mask = connected_background_mask(original, pixel_offset, width, height)

    for x, y in bg_mask:
        value = get_pixel(data, pixel_offset, width, height, x, y)
        replacement = rgb_to_rgb565(*soft_eye_background_color(x, y, width, abs(height)))
        if replacement != value:
            set_pixel(data, pixel_offset, width, height, x, y, replacement)
            changed_pixels += 1

    for y in range(abs(height)):
        for x in range(width):
            if (x, y) in bg_mask:
                continue
            value = get_pixel(data, pixel_offset, width, height, x, y)
            replacement_rgb = soft_eye_foreground_color(*rgb565_to_rgb(value))
            if replacement_rgb is None:
                continue
            replacement = rgb_to_rgb565(*replacement_rgb)
            if replacement != value:
                set_pixel(data, pixel_offset, width, height, x, y, replacement)
                changed_pixels += 1

    outer = rgb_to_rgb565(12, 15, 16)
    inner = rgb_to_rgb565(48, 57, 56)
    highlight = rgb_to_rgb565(89, 96, 85)
    shadow = rgb_to_rgb565(24, 30, 31)
    max_y = abs(height) - 1
    max_x = width - 1
    for x in range(width):
        for y, color in [(0, outer), (1, highlight), (max_y - 1, shadow), (max_y, outer)]:
            before = get_pixel(data, pixel_offset, width, height, x, y)
            set_pixel(data, pixel_offset, width, height, x, y, color)
            if before != color:
                changed_pixels += 1
    for y in range(abs(height)):
        for x, color in [(0, outer), (1, inner), (max_x - 1, shadow), (max_x, outer)]:
            before = get_pixel(data, pixel_offset, width, height, x, y)
            set_pixel(data, pixel_offset, width, height, x, y, color)
            if before != color:
                changed_pixels += 1

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
        "# DM303 Soft Eye nav-menu asset report",
        "",
        "Status: resource-level Soft Eye theme assets for `v4.0.1 beta`.",
        "",
        "## Safety scope",
        "",
        "- Source assets in `backup/` are read-only.",
        "- BMP dimensions, headers, row layout, and file sizes are preserved.",
        "- Connected menu-card background pixels and the card border are recolored.",
        "- Harsh white/yellow foreground pixels are tone-mapped to softer ivory/amber.",
        "- Icon glyphs and label pixels are not rescaled or blurred.",
        "- Palette avoids pure black, pure white, and flat high-glare grays.",
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
