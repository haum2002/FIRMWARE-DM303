#!/usr/bin/env python3
"""Build an experimental DM303 UI overlay SD-root package.

This builder is separate from the measurement repair builder.  It starts from
the official V4.0 system folder, adds DM30XDB1.dat, and then overlays only the
UI files that are explicitly expected for the Melayu/dark-theme experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import struct
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
BACKUP_V4 = WORKSPACE / "backup" / "DM303 V4.0-read only"
OFFICIAL_SYSTEM = BACKUP_V4 / "system"
OFFICIAL_QBTEST = BACKUP_V4 / "QBtest.txt"
OFFICIAL_README = BACKUP_V4 / "readme.txt"
DM30XDB1_SOURCE = WORKSPACE / "backup" / "SD-file_DM303_update_US240104-read only" / "system" / "DM30xDB1.dat"
FIRMWARE_NAME = "DM303V4.0.1-beta.bin"
EXPECTED_DM30XDB1_SHA256 = "846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79"
EXPECTED_SAFE_SP_SHA256 = "96bde6bca8036d2a6d0647b85db76135fa4ef1f222db70860381c66aefaed76e"
EXPECTED_DARK_ICON_SP_SHA256 = "4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"ui_overlay_build=failed\nreason={message}")


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"missing required file: {path}")


def require_dir(path: Path) -> None:
    if not path.is_dir():
        fail(f"missing required folder: {path}")


def ensure_safe_output(candidate_dir: Path, output_dir: Path) -> None:
    candidate_resolved = candidate_dir.resolve()
    output_resolved = output_dir.resolve()
    if output_resolved == candidate_resolved:
        fail("refusing to use the candidate folder itself as sd-root")
    if candidate_resolved not in output_resolved.parents:
        fail(f"refusing to clean output outside candidate folder: {output_resolved}")


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


def validate_icon_pack(path: Path) -> None:
    data = path.read_bytes()
    if len(data) != 78336 or len(data) % 17 != 0 or len(data) // 17 != 4608:
        fail(f"unexpected icon-SP.dat layout: {path}")
    digest = sha256_file(path)
    if digest != EXPECTED_DARK_ICON_SP_SHA256:
        fail(f"unexpected icon-SP.dat hash: {digest}")


def overlay_ui_files(candidate_dir: Path, out_root: Path) -> None:
    overlay = candidate_dir / "system"
    require_dir(overlay)
    system = out_root / "system"

    text_sp = overlay / "TEXT_SP.DAT"
    icon_sp = overlay / "icon-SP.dat"
    require_file(text_sp)
    require_file(icon_sp)
    if sha256_file(text_sp) != EXPECTED_SAFE_SP_SHA256:
        fail(f"unexpected safe TEXT_SP.DAT hash: {sha256_file(text_sp)}")
    shutil.copy2(text_sp, system / "TEXT_SP.DAT")
    shutil.copy2(icon_sp, system / "icon-SP.dat")
    validate_icon_pack(system / "icon-SP.dat")

    expected_names = {f"icon-E{index}.bmp" for index in range(1, 19)}
    expected_names.update({f"icon-C{index}.bmp" for index in range(1, 17)})
    for name in sorted(expected_names):
        source = overlay / name
        require_file(source)
        validate_bmp_layout(source, 92, -92, 17000)
        shutil.copy2(source, system / name)


def validate_layout(root: Path) -> None:
    required = [root / FIRMWARE_NAME, root / "QBtest.txt", root / "readme.txt", root / "system"]
    for path in required:
        if not path.exists():
            fail(f"missing SD-root entry: {path}")
    if (root / "DM303-V4.0.1-beta" / FIRMWARE_NAME).exists():
        fail("firmware is inside an extra folder; copy SD-root contents only")


def write_hashes(root: Path, destination: Path) -> None:
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        rows.append(f"{sha256_file(path)}  {rel}")
    destination.write_text("\n".join(rows) + "\n", encoding="ascii")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--out-root", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate_dir = args.candidate_dir.resolve()
    out_root = (args.out_root or candidate_dir / "sd-root").resolve()
    ensure_safe_output(candidate_dir, out_root)

    require_file(candidate_dir / FIRMWARE_NAME)
    require_dir(OFFICIAL_SYSTEM)
    require_file(OFFICIAL_QBTEST)
    require_file(OFFICIAL_README)
    require_file(DM30XDB1_SOURCE)

    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    shutil.copy2(candidate_dir / FIRMWARE_NAME, out_root / FIRMWARE_NAME)
    shutil.copy2(OFFICIAL_QBTEST, out_root / "QBtest.txt")
    shutil.copy2(OFFICIAL_README, out_root / "readme.txt")
    shutil.copytree(OFFICIAL_SYSTEM, out_root / "system")
    shutil.copy2(DM30XDB1_SOURCE, out_root / "system" / "DM30XDB1.dat")
    overlay_ui_files(candidate_dir, out_root)

    validate_layout(out_root)
    if sha256_file(out_root / "system" / "DM30XDB1.dat") != EXPECTED_DM30XDB1_SHA256:
        fail("DM30XDB1.dat hash mismatch")
    write_hashes(out_root, candidate_dir / "SD-ROOT-SHA256SUMS.txt")

    print("ui_overlay_build=ok")
    print(f"candidate_dir={candidate_dir}")
    print(f"sd_root={out_root}")
    print(f"firmware_sha256={sha256_file(out_root / FIRMWARE_NAME)}")
    print("system_source=official_v4_plus_expected_ui_overlay")
    print("overlay_files=TEXT_SP.DAT,icon-SP.dat,icon-C*.bmp,icon-E*.bmp")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
