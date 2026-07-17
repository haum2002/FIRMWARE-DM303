#!/usr/bin/env python3
"""Validate the experimental DM303 repair-i UI overlay package."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path


SOURCE = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
OFFICIAL_SYSTEM = Path("backup/DM303 V4.0-read only/system")
FIRMWARE_NAME = "DM303V4.0.1-beta.bin"
EXPECTED_FIRMWARE_SHA256 = "a26edd279ae15a68c3f819b1e2dac10d91043a45f6faac64aa0bdfa504f38878"
EXPECTED_SAFE_SP_SHA256 = "96bde6bca8036d2a6d0647b85db76135fa4ef1f222db70860381c66aefaed76e"
EXPECTED_DARK_ICON_SP_SHA256 = "4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8"
EXPECTED_DM30XDB1_SHA256 = "846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79"

EXPECTED_BYTES = {
    0x02CA0: b"MT100MM V4.0.1p\x00",
    0x02CB0: b"BT100MM V4.0.1p\x00",
    0x25BF8: b"Melayu ",
    0x09CA0: bytes.fromhex("fe e7"),
    0x0C6C8: bytes.fromhex("fe e7"),
    0x2C4EA: bytes.fromhex("fe e7"),
    0x06A06: bytes.fromhex("70 b5 05 46"),
    0x096BE: bytes.fromhex("10 b1"),
    0x097E8: bytes.fromhex("01"),
    0x0F19A: bytes.fromhex("10 b5 04 46"),
    0x14B0E: bytes.fromhex("40 f2 dc 50"),
    0x14B36: bytes.fromhex("40 f2 dc 50"),
    0x15812: bytes.fromhex("00 bf"),
    0x15838: bytes.fromhex("00 bf"),
    0x1585E: bytes.fromhex("b0 f5 c8 6f"),
    0x15862: bytes.fromhex("00 bf"),
    0x15888: bytes.fromhex("b0 f5 c8 6f"),
    0x1588C: bytes.fromhex("00 bf"),
    0x15934: bytes.fromhex("40 f2 dc 51"),
    0x1595C: bytes.fromhex("40 f2 dc 51"),
    0x1D1A4: bytes.fromhex("40 f2 dc 50"),
    0x1D1C0: bytes.fromhex("40 f2 dc 50"),
    0x1D1DA: bytes.fromhex("40 20"),
}

OVERLAY_FILES = {"TEXT_SP.DAT", "icon-SP.dat"}
OVERLAY_FILES.update({f"icon-E{index}.bmp" for index in range(1, 19)})
OVERLAY_FILES.update({f"icon-C{index}.bmp" for index in range(1, 17)})
ROOT_FILES = {FIRMWARE_NAME, "QBtest.txt", "readme.txt"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"ui_overlay_candidate_check=failed\nreason={message}")


def validate_layout(root: Path) -> None:
    if not root.is_dir():
        fail(f"root folder does not exist: {root}")
    if (root / "DM303-V4.0.1-beta" / FIRMWARE_NAME).exists():
        fail("firmware is inside an extra folder; copy SD-root contents only")
    missing = sorted(name for name in ROOT_FILES if not (root / name).is_file())
    if missing:
        fail(f"missing root files: {missing}")
    if not (root / "system").is_dir():
        fail("missing system folder")
    extras = sorted(path.name for path in root.iterdir() if path.name not in ROOT_FILES and path.name != "system")
    if extras:
        fail(f"unexpected root entries: {extras}")


def validate_firmware(root: Path) -> None:
    firmware = root / FIRMWARE_NAME
    if firmware.stat().st_size != 203260:
        fail(f"unexpected firmware size: {firmware.stat().st_size}")
    digest = sha256_file(firmware)
    if digest != EXPECTED_FIRMWARE_SHA256:
        fail(f"unexpected firmware hash: {digest}")
    data = firmware.read_bytes()
    for offset, expected in EXPECTED_BYTES.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(f"byte mismatch at 0x{offset:05x}: expected {expected.hex(' ')}, got {actual.hex(' ')}")


def validate_bmp_layout(path: Path, width: int, height: int, size: int) -> None:
    data = path.read_bytes()
    if len(data) != size or data[:2] != b"BM":
        fail(f"invalid BMP size/header: {path}")
    file_size = struct.unpack_from("<I", data, 2)[0]
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    dib_size = struct.unpack_from("<I", data, 14)[0]
    actual_width = struct.unpack_from("<i", data, 18)[0]
    actual_height = struct.unpack_from("<i", data, 22)[0]
    planes = struct.unpack_from("<H", data, 26)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    masks = struct.unpack_from("<III", data, 54)
    if (
        file_size != len(data)
        or pixel_offset != 70
        or dib_size != 56
        or actual_width != width
        or actual_height != height
        or planes != 1
        or bpp != 16
        or compression != 3
        or masks != (0xF800, 0x07E0, 0x001F)
    ):
        fail(f"unexpected RGB565 BMP layout: {path}")


def validate_system(root: Path) -> None:
    system = root / "system"
    for official in OFFICIAL_SYSTEM.iterdir():
        if not official.is_file():
            continue
        candidate = system / official.name
        if not candidate.is_file():
            fail(f"missing official system file: {official.name}")
        if official.name in OVERLAY_FILES:
            continue
        if sha256_file(candidate) != sha256_file(official):
            fail(f"unexpected non-overlay system difference: {official.name}")

    if sha256_file(system / "TEXT_SP.DAT") != EXPECTED_SAFE_SP_SHA256:
        fail(f"unexpected TEXT_SP.DAT hash: {sha256_file(system / 'TEXT_SP.DAT')}")
    if sha256_file(system / "icon-SP.dat") != EXPECTED_DARK_ICON_SP_SHA256:
        fail(f"unexpected icon-SP.dat hash: {sha256_file(system / 'icon-SP.dat')}")
    for name in sorted(name for name in OVERLAY_FILES if name.endswith(".bmp")):
        validate_bmp_layout(system / name, 92, -92, 17000)

    dm30xdb1 = system / "DM30XDB1.dat"
    if not dm30xdb1.is_file():
        fail("missing DM30XDB1.dat")
    if sha256_file(dm30xdb1) != EXPECTED_DM30XDB1_SHA256:
        fail(f"unexpected DM30XDB1.dat hash: {sha256_file(dm30xdb1)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    validate_layout(root)
    validate_firmware(root)
    validate_system(root)
    print("ui_overlay_candidate_check=ok")
    print(f"root={root}")
    print("profile=v401h-repair-i-ui-ms")
    print(f"firmware_sha256={sha256_file(root / FIRMWARE_NAME)}")
    print(f"text_sp_sha256={sha256_file(root / 'system' / 'TEXT_SP.DAT')}")
    print(f"icon_sp_sha256={sha256_file(root / 'system' / 'icon-SP.dat')}")
    print("non_overlay_system_resources=official_v4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
