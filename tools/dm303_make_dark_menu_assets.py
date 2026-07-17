#!/usr/bin/env python3
"""Build safe dark nav-menu BMP assets for the DM303 V4.0.1 beta package.

The tool edits only RGB565 pixels in the official BMP layout. It does not use an
image encoder, does not resize, and does not rewrite BMP headers, masks, row
layout, or file sizes. This avoids the compression/bit-depth artifacts seen in
the earlier dark-theme experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path


SOURCE_SYSTEM = Path("backup/DM303 V4.0-read only/system")
OUTPUT_SYSTEM = Path("firmware-candidates/v4.0.1-beta/system")
REPORT = Path("firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS.md")
SUMS = Path("firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS-SHA256.txt")
LABEL_PACK = OUTPUT_SYSTEM / "icon-SP.dat"
LABEL_PACK_SOURCE = Path("localization/ms_MY/icon-SP.dat")
LABEL_REPORT = OUTPUT_SYSTEM / "MS-ICON-PACK.md"

BACKGROUND_SHADOW_RGB = (5, 18, 33)
BACKGROUND_RGB = (10, 35, 59)      # brighter deep blue, not pure black
BACKGROUND_HIGHLIGHT_RGB = (26, 70, 105)
TEXT_DIM_RGB = (196, 214, 224)
TEXT_RGB = (239, 247, 250)         # clear soft white, not #fff/#eee
AMBER_RGB = (255, 204, 72)         # brighter amber for the DM303 LCD
AMBER_HIGHLIGHT_RGB = (255, 226, 110)


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
class BmpLayout:
    file_size: int
    pixel_offset: int
    width: int
    height: int
    pixel_count: int
    pixel_bytes: int


def rgb565_to_rgb(value: int) -> tuple[int, int, int]:
    r = (value >> 11) & 0x1F
    g = (value >> 5) & 0x3F
    b = value & 0x1F
    return (
        round(r * 255 / 31),
        round(g * 255 / 63),
        round(b * 255 / 31),
    )


def rgb_to_rgb565(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    r5 = max(0, min(31, round(r * 31 / 255)))
    g6 = max(0, min(63, round(g * 63 / 255)))
    b5 = max(0, min(31, round(b * 31 / 255)))
    return (r5 << 11) | (g6 << 5) | b5


def blend(
    background: tuple[int, int, int],
    foreground: tuple[int, int, int],
    alpha: float,
) -> tuple[int, int, int]:
    alpha = max(0.0, min(1.0, alpha))
    return tuple(round(bg + (fg - bg) * alpha) for bg, fg in zip(background, foreground))


def smoothstep(edge0: float, edge1: float, value: float) -> float:
    if edge0 == edge1:
        return 1.0 if value >= edge1 else 0.0
    x = max(0.0, min(1.0, (value - edge0) / (edge1 - edge0)))
    return x * x * (3.0 - 2.0 * x)


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def vendor_dark_background(rgb: tuple[int, int, int], lum: float) -> tuple[int, int, int]:
    t = smoothstep(0, 95, lum)
    base = blend(BACKGROUND_SHADOW_RGB, BACKGROUND_HIGHLIGHT_RGB, t)
    # Keep a small amount of the original subpixel variation so vendor
    # anti-aliasing and card shadows do not collapse into a flat block.
    adjusted = []
    for channel, source_channel in zip(base, rgb):
        delta = (source_channel - lum) / 18
        adjusted.append(round(max(0, min(255, channel + delta))))
    return tuple(adjusted)


def classify_and_tint(value: int) -> tuple[int, str]:
    rgb = rgb565_to_rgb(value)
    r, g, b = rgb
    lum = luminance(rgb)
    is_yellow = r >= 96 and g >= 72 and b <= 112 and r >= g * 0.78

    if is_yellow:
        alpha = smoothstep(45, 225, lum)
        target = blend(AMBER_RGB, AMBER_HIGHLIGHT_RGB, smoothstep(160, 255, lum))
        return rgb_to_rgb565(blend(BACKGROUND_RGB, target, 0.25 + 0.75 * alpha)), "amber"

    if lum >= 88:
        alpha = smoothstep(70, 245, lum)
        target = blend(TEXT_DIM_RGB, TEXT_RGB, alpha)
        return rgb_to_rgb565(blend(BACKGROUND_RGB, target, 0.24 + 0.76 * alpha)), "text"

    return rgb_to_rgb565(vendor_dark_background(rgb, lum)), "background"


def validate_bmp_bytes(data: bytes, label: str, expected_width: int, expected_abs_height: int) -> BmpLayout:
    if data[:2] != b"BM":
        raise ValueError(f"not a BMP file: {label}")
    file_size = struct.unpack_from("<I", data, 2)[0]
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    dib_size = struct.unpack_from("<I", data, 14)[0]
    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    planes = struct.unpack_from("<H", data, 26)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    masks = struct.unpack_from("<III", data, 54)
    if (
        dib_size != 56
        or width != expected_width
        or abs(height) != expected_abs_height
        or planes != 1
        or bpp != 16
        or compression != 3
        or pixel_offset != 70
        or masks != (0xF800, 0x07E0, 0x001F)
    ):
        raise ValueError(f"unexpected BMP layout: {label}")
    pixel_count = width * abs(height)
    pixel_bytes = pixel_count * 2
    if pixel_offset + pixel_bytes > len(data) or file_size > len(data):
        raise ValueError(f"truncated BMP payload: {label}")
    return BmpLayout(file_size, pixel_offset, width, height, pixel_count, pixel_bytes)


def tint_bmp_bytes(data: bytes, label: str, expected_width: int, expected_abs_height: int) -> tuple[bytes, dict[str, int]]:
    layout = validate_bmp_bytes(data, label, expected_width, expected_abs_height)
    output = bytearray(data)
    counts = {"background": 0, "text": 0, "amber": 0}
    for index in range(layout.pixel_count):
        offset = layout.pixel_offset + index * 2
        before = struct.unpack_from("<H", data, offset)[0]
        after, bucket = classify_and_tint(before)
        struct.pack_into("<H", output, offset, after)
        counts[bucket] += 1
    if len(output) != len(data):
        raise AssertionError("internal size changed")
    if output[: layout.pixel_offset] != data[: layout.pixel_offset]:
        raise AssertionError(f"header changed unexpectedly: {label}")
    return bytes(output), counts


def unique_rgb565_count(data: bytes, expected_width: int, expected_abs_height: int, label: str) -> int:
    layout = validate_bmp_bytes(data, label, expected_width, expected_abs_height)
    return len(
        {
            struct.unpack_from("<H", data, layout.pixel_offset + index * 2)[0]
            for index in range(layout.pixel_count)
        }
    )


def icon_sort_key(path: Path) -> tuple[str, int]:
    stem = path.stem
    prefix = "E" if stem.startswith("icon-E") else "C"
    number_text = stem.removeprefix(f"icon-{prefix}")
    return prefix, int(number_text)


def tint_label_pack(source: Path, destination: Path) -> tuple[int, dict[str, int]]:
    if not source.exists():
        return 0, {"background": 0, "text": 0, "amber": 0}
    data = source.read_bytes()
    frame_len = len(data) // 17
    if len(data) % 17 or frame_len != 4608:
        raise ValueError(f"unexpected icon-SP.dat length: {source}")
    output = bytearray(data)
    totals = {"background": 0, "text": 0, "amber": 0}
    for frame in range(17):
        start = frame * frame_len
        frame_data = bytes(data[start : start + frame_len])
        tinted, counts = tint_bmp_bytes(frame_data, f"{source.name}[{frame}]", 92, 24)
        output[start : start + frame_len] = tinted
        for key, value in counts.items():
            totals[key] += value
    destination.write_bytes(bytes(output))
    return 17, totals


def update_label_report(final_hash: str | None) -> None:
    if not final_hash or not LABEL_REPORT.exists():
        return
    marker = "\n## Safe dark tint\n"
    existing = LABEL_REPORT.read_text(encoding="utf-8")
    base = existing.split(marker, 1)[0].rstrip()
    write_text_lf(
        LABEL_REPORT,
        base
        + marker
        + "\n"
        + "- Applied by `tools/dm303_make_dark_menu_assets.py` after the Malay label pack is generated.\n"
        + "- Final dark Malay label SHA-256: "
        + f"`{final_hash}`\n",
    )


def main() -> int:
    global SOURCE_SYSTEM, OUTPUT_SYSTEM, REPORT, SUMS, LABEL_PACK, LABEL_PACK_SOURCE, LABEL_REPORT

    parser = argparse.ArgumentParser()
    parser.add_argument("--source-system", type=Path, default=SOURCE_SYSTEM)
    parser.add_argument("--output-system", type=Path, default=OUTPUT_SYSTEM)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--sums", type=Path, default=SUMS)
    parser.add_argument("--label-pack-source", type=Path, default=LABEL_PACK_SOURCE)
    parser.add_argument("--label-report", type=Path, default=LABEL_REPORT)
    args = parser.parse_args()

    SOURCE_SYSTEM = args.source_system
    OUTPUT_SYSTEM = args.output_system
    REPORT = args.report
    SUMS = args.sums
    LABEL_PACK = OUTPUT_SYSTEM / "icon-SP.dat"
    LABEL_PACK_SOURCE = args.label_pack_source
    LABEL_REPORT = args.label_report

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

    OUTPUT_SYSTEM.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, int, str, dict[str, int], int, int]] = []
    for source in icons:
        source_data = source.read_bytes()
        before_unique = unique_rgb565_count(source_data, 92, 92, source.name)
        tinted, counts = tint_bmp_bytes(source_data, source.name, 92, 92)
        destination = OUTPUT_SYSTEM / source.name
        destination.write_bytes(tinted)
        if destination.stat().st_size != source.stat().st_size:
            raise SystemExit(f"Size changed unexpectedly: {destination}")
        after_unique = unique_rgb565_count(tinted, 92, 92, source.name)
        rows.append((source.name, destination.stat().st_size, sha256_file(destination), counts, before_unique, after_unique))

    label_source = LABEL_PACK_SOURCE if LABEL_PACK_SOURCE.exists() else LABEL_PACK
    label_frames, label_counts = tint_label_pack(label_source, LABEL_PACK)
    label_hash = sha256_file(LABEL_PACK) if LABEL_PACK.exists() else None
    update_label_report(label_hash)

    write_text_lf(
        SUMS,
        "".join(f"{digest}  system/{name}\n" for name, _, digest, _, _, _ in rows)
        + (f"{label_hash}  system/icon-SP.dat\n" if label_hash else ""),
    )

    lines = [
        "# DM303 safe dark nav-menu asset report",
        "",
        "Status: safe dark theme generated for `v4.0.1 beta`.",
        "",
        "## Safety scope",
        "",
        "- Source assets in `backup/` are read-only.",
        "- Output menu BMP files keep the official V4.0 BMP headers, RGB565 masks, dimensions, row layout, and file sizes.",
        "- Pixels are rewritten directly as RGB565 values; no image encoder, scaling, compression, or external palette remapping tool is used.",
        "- Vendor dark gradients and anti-alias levels are preserved as deep-blue variants instead of being flattened.",
        "- Icon yellow becomes softer amber, and text/anti-alias pixels become a soft high-contrast white.",
        "- Firmware code, bootloader, and updater are not touched by this tool.",
        "",
        "## Palette",
        "",
        f"- Background: `#{BACKGROUND_RGB[0]:02X}{BACKGROUND_RGB[1]:02X}{BACKGROUND_RGB[2]:02X}`",
        f"- Text: `#{TEXT_RGB[0]:02X}{TEXT_RGB[1]:02X}{TEXT_RGB[2]:02X}`",
        f"- Amber: `#{AMBER_RGB[0]:02X}{AMBER_RGB[1]:02X}{AMBER_RGB[2]:02X}`",
        "",
        "## Label pack",
        "",
        f"- `system/icon-SP.dat` frames tinted: `{label_frames}`",
        f"- `system/icon-SP.dat` SHA-256: `{label_hash or 'not present'}`",
        "",
        "## Files",
        "",
        "| File | Size | SHA-256 | Original colors | Final colors | Background px | Text px | Amber px |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for name, size, digest, counts, before_unique, after_unique in rows:
        lines.append(
            f"| `{name}` | {size} | `{digest}` | "
            f"{before_unique} | {after_unique} | "
            f"{counts['background']} | {counts['text']} | {counts['amber']} |"
        )
    write_text_lf(REPORT, "\n".join(lines) + "\n")

    print(f"source={SOURCE_SYSTEM}")
    print(f"output={OUTPUT_SYSTEM}")
    print(f"icons_tinted={len(rows)}")
    print(f"label_pack_frames_tinted={label_frames}")
    if label_hash:
        print(f"icon_sp_sha256={label_hash}")
    print(f"report={REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
