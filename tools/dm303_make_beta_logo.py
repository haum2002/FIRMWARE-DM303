#!/usr/bin/env python3
"""Convert the supplied beta logo BMP directly into the DM303 LOGO-1 layout.

The firmware resource is a 320x240 top-down RGB565 BMP with BITFIELDS masks.
The user-supplied artwork is kept at the same 320x240 pixel geometry and is
decoded directly from BMP bytes. No image library, resampling, encoder,
compression, or header rewrite is used.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path


TEMPLATE = Path("backup/DM303 V4.0-read only/system/LOGO-1.bmp")
SOURCE = Path("C:/Users/Administrator/Downloads/image_(1).bmp")
DESTINATION = Path("firmware-candidates/v4.0.1-beta/system/LOGO-1.bmp")
REPORT = Path("firmware-candidates/v4.0.1-beta/system/BETA-LOGO-REPORT.md")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


@dataclass(frozen=True)
class BmpInfo:
    path: Path
    data: bytes
    file_size: int
    pixel_offset: int
    dib_size: int
    width: int
    height: int
    bpp: int
    compression: int
    masks: tuple[int, int, int, int]
    row_size: int

    @property
    def abs_height(self) -> int:
        return abs(self.height)


def read_bmp(path: Path) -> BmpInfo:
    data = path.read_bytes()
    if data[:2] != b"BM":
        raise ValueError(f"not a BMP file: {path}")
    file_size = struct.unpack_from("<I", data, 2)[0]
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    dib_size = struct.unpack_from("<I", data, 14)[0]
    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    planes = struct.unpack_from("<H", data, 26)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    if planes != 1 or width <= 0 or height == 0:
        raise ValueError(f"unsupported BMP geometry: {path}")
    masks = (0, 0, 0, 0)
    if compression == 3:
        if dib_size >= 108:
            masks = struct.unpack_from("<IIII", data, 54)
        elif dib_size >= 56 or len(data) >= 70:
            masks = (*struct.unpack_from("<III", data, 54), 0)
    row_size = ((width * bpp + 31) // 32) * 4
    if pixel_offset + row_size * abs(height) > len(data):
        raise ValueError(f"truncated BMP pixel data: {path}")
    if file_size > len(data):
        raise ValueError(f"declared BMP size exceeds file length: {path}")
    return BmpInfo(path, data, file_size, pixel_offset, dib_size, width, height, bpp, compression, masks, row_size)


def mask_shift_and_bits(mask: int) -> tuple[int, int]:
    if mask == 0:
        return 0, 0
    shift = 0
    value = mask
    while value & 1 == 0:
        shift += 1
        value >>= 1
    bits = 0
    while value & 1:
        bits += 1
        value >>= 1
    return shift, bits


def scale_from_mask(value: int, mask: int) -> int:
    shift, bits = mask_shift_and_bits(mask)
    if bits == 0:
        return 255
    raw = (value & mask) >> shift
    return round(raw * 255 / ((1 << bits) - 1))


def rgb_to_rgb565(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    r5 = max(0, min(31, round(r * 31 / 255)))
    g6 = max(0, min(63, round(g * 63 / 255)))
    b5 = max(0, min(31, round(b * 31 / 255)))
    return (r5 << 11) | (g6 << 5) | b5


def sanitize_screen_noise(rgb: tuple[int, int, int]) -> tuple[tuple[int, int, int], bool]:
    """Snap near-black residue to exact black for the DM303 RGB565 panel."""
    r, g, b = rgb
    if max(r, g, b) <= 12 or r + g + b <= 24:
        return (0, 0, 0), rgb != (0, 0, 0)
    return rgb, False


def read_source_rgb(source: BmpInfo, x: int, y: int) -> tuple[int, int, int]:
    source_y = y if source.height < 0 else source.abs_height - 1 - y
    offset = source.pixel_offset + source_y * source.row_size
    if source.bpp == 32:
        raw = struct.unpack_from("<I", source.data, offset + x * 4)[0]
        if source.compression == 3 and source.masks[:3] != (0, 0, 0):
            r = scale_from_mask(raw, source.masks[0])
            g = scale_from_mask(raw, source.masks[1])
            b = scale_from_mask(raw, source.masks[2])
            a = scale_from_mask(raw, source.masks[3]) if source.masks[3] else 255
        else:
            b = raw & 0xFF
            g = (raw >> 8) & 0xFF
            r = (raw >> 16) & 0xFF
            a = (raw >> 24) & 0xFF
        if a < 255:
            r = round(r * a / 255)
            g = round(g * a / 255)
            b = round(b * a / 255)
        return r, g, b
    if source.bpp == 24:
        b, g, r = source.data[offset + x * 3 : offset + x * 3 + 3]
        return r, g, b
    if source.bpp == 16 and source.compression == 3:
        raw = struct.unpack_from("<H", source.data, offset + x * 2)[0]
        return (
            scale_from_mask(raw, source.masks[0]),
            scale_from_mask(raw, source.masks[1]),
            scale_from_mask(raw, source.masks[2]),
        )
    raise ValueError(f"unsupported source BMP pixel format: bpp={source.bpp} compression={source.compression}")


def validate_template(template: BmpInfo) -> None:
    expected = (
        template.dib_size == 56
        and template.width == 320
        and template.height == -240
        and template.bpp == 16
        and template.compression == 3
        and template.pixel_offset == 70
        and template.masks[:3] == (0xF800, 0x07E0, 0x001F)
    )
    if not expected:
        raise ValueError(f"unexpected LOGO-1 template layout: {template.path}")


def convert_logo(template_path: Path, source_path: Path, destination: Path) -> tuple[int, int, int]:
    template = read_bmp(template_path)
    source = read_bmp(source_path)
    validate_template(template)
    if source.width != 320 or source.abs_height != 240:
        raise ValueError(f"source artwork must be exactly 320x240: {source.path}")

    output = bytearray(template.data)
    changed = 0
    sanitized = 0
    unique_rgb565: set[int] = set()
    for y in range(240):
        target_y = y if template.height < 0 else template.abs_height - 1 - y
        target_row = template.pixel_offset + target_y * template.row_size
        for x in range(320):
            rgb, was_sanitized = sanitize_screen_noise(read_source_rgb(source, x, y))
            if was_sanitized:
                sanitized += 1
            rgb565 = rgb_to_rgb565(rgb)
            unique_rgb565.add(rgb565)
            offset = target_row + x * 2
            before = struct.unpack_from("<H", output, offset)[0]
            if before != rgb565:
                changed += 1
            struct.pack_into("<H", output, offset, rgb565)

    if output[: template.pixel_offset] != template.data[: template.pixel_offset]:
        raise AssertionError("template BMP header changed unexpectedly")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(bytes(output))
    return changed, len(unique_rgb565), sanitized


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--destination", type=Path, default=DESTINATION)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed_pixels, unique_colors, sanitized_pixels = convert_logo(args.template, args.source, args.destination)
    template_info = read_bmp(args.template)
    source_info = read_bmp(args.source)
    output_info = read_bmp(args.destination)

    lines = [
        "# DM303 V4.0.1 beta logo report",
        "",
        "Status: direct BMP-to-RGB565 LOGO-1 overlay for `v4.0.1 beta`.",
        "",
        "## Safety scope",
        "",
        "- Source artwork pixels are decoded directly from the BMP byte payload.",
        "- No image library, resampling, encoder, compression, dithering, or scaling is used.",
        "- Firmware BMP header, dimensions, bit depth, compression mode, RGB565 masks, row layout, and file size are preserved from the official V4.0 template.",
        "- Near-black residue pixels are snapped to exact black before RGB565 packing to avoid LCD speckle without changing geometry or header format.",
        "- Firmware code, bootloader, and updater are not touched by this tool.",
        "",
        "## Input",
        "",
        f"- Template: `{args.template.as_posix()}`",
        f"- Template SHA-256: `{sha256_file(args.template)}`",
        f"- Source artwork: `{args.source.as_posix()}`",
        f"- Source artwork SHA-256: `{sha256_file(args.source)}`",
        f"- Source layout: `{source_info.width}x{source_info.height}`, `{source_info.bpp}` bpp, compression `{source_info.compression}`, pixel offset `{source_info.pixel_offset}`",
        "",
        "## Output",
        "",
        f"- File: `{args.destination.as_posix()}`",
        f"- Output SHA-256: `{sha256_file(args.destination)}`",
        f"- Output layout: `{output_info.width}x{output_info.height}`, `{output_info.bpp}` bpp, compression `{output_info.compression}`, pixel offset `{output_info.pixel_offset}`",
        f"- Changed pixels vs template: `{changed_pixels}`",
        f"- Unique RGB565 colors: `{unique_colors}`",
        f"- Near-black pixels sanitized: `{sanitized_pixels}`",
        f"- Output size matches template: `{output_info.file_size == template_info.file_size and len(output_info.data) == len(template_info.data)}`",
    ]
    write_text_lf(REPORT, "\n".join(lines) + "\n")

    print(f"template={args.template}")
    print(f"source={args.source}")
    print(f"destination={args.destination}")
    print(f"source_sha256={sha256_file(args.source)}")
    print(f"output_sha256={sha256_file(args.destination)}")
    print(f"changed_pixels={changed_pixels}")
    print(f"unique_rgb565_colors={unique_colors}")
    print(f"near_black_pixels_sanitized={sanitized_pixels}")
    print(f"report={REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
