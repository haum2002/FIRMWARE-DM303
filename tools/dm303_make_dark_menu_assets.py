#!/usr/bin/env python3
"""Restore original vendor nav-menu BMP assets for the DM303 V4.0.1 beta package.

The previous dark-theme experiment made the LCD assets look rough on hardware.
This compatibility script now copies the official V4.0 menu BMP files back into
the staging folder, preserving every byte of the vendor palette and glyphs.
"""

from __future__ import annotations

import hashlib
import shutil
import struct
from pathlib import Path


SOURCE_SYSTEM = Path("backup/DM303 V4.0-read only/system")
OUTPUT_SYSTEM = Path("firmware-candidates/v4.0.1-beta/system")
REPORT = Path("firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS.md")
SUMS = Path("firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS-SHA256.txt")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def validate_menu_bmp(path: Path) -> None:
    data = path.read_bytes()
    if data[:2] != b"BM":
        raise ValueError(f"not a BMP file: {path}")
    dib_size = struct.unpack_from("<I", data, 14)[0]
    width = struct.unpack_from("<i", data, 18)[0]
    height = struct.unpack_from("<i", data, 22)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    if dib_size != 56 or width != 92 or abs(height) != 92 or bpp != 16 or compression != 3:
        raise ValueError(f"unexpected BMP layout: {path}")


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

    OUTPUT_SYSTEM.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, int, str]] = []
    for source in icons:
        validate_menu_bmp(source)
        destination = OUTPUT_SYSTEM / source.name
        shutil.copy2(source, destination)
        rows.append((source.name, destination.stat().st_size, sha256_file(destination)))

    write_text_lf(
        SUMS,
        "".join(f"{digest}  system/{name}\n" for name, _, digest in rows),
    )

    lines = [
        "# DM303 vendor nav-menu asset report",
        "",
        "Status: dark-theme experiment removed for `v4.0.1 beta`.",
        "",
        "## Safety scope",
        "",
        "- Source assets in `backup/` are read-only.",
        "- Output menu BMP files are byte-for-byte copies of the official V4.0 resources.",
        "- Vendor color palette, anti-aliased glyph pixels, dimensions, headers, row layout, and file sizes are preserved.",
        "- Firmware code, bootloader, and updater are not touched by this tool.",
        "",
        "## Files",
        "",
        "| File | Size | SHA-256 |",
        "|---|---:|---|",
    ]
    for name, size, digest in rows:
        lines.append(f"| `{name}` | {size} | `{digest}` |")
    write_text_lf(REPORT, "\n".join(lines) + "\n")

    print(f"source={SOURCE_SYSTEM}")
    print(f"output={OUTPUT_SYSTEM}")
    print(f"icons_restored={len(rows)}")
    print(f"report={REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
