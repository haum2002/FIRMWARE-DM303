#!/usr/bin/env python3
"""Build a complete SD-root package for isolated DM303 repair candidates.

This intentionally copies the full official V4.0 `system` folder every time.
Candidate `system` folders are treated as overlays only and are never used as
the base SD-card system tree.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

from dm303_repair_candidate_check import (
    EXPECTED,
    validate_firmware,
    validate_layout,
    validate_official_system,
)


WORKSPACE = Path(__file__).resolve().parents[1]
BACKUP_V4 = WORKSPACE / "backup" / "DM303 V4.0-read only"
OFFICIAL_SYSTEM = BACKUP_V4 / "system"
OFFICIAL_QBTEST = BACKUP_V4 / "QBtest.txt"
OFFICIAL_README = BACKUP_V4 / "readme.txt"
DM30XDB1_SOURCE = WORKSPACE / "backup" / "SD-file_DM303_update_US240104-read only" / "system" / "DM30xDB1.dat"
FIRMWARE_NAME = "DM303V4.0.1-beta.bin"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"missing required file: {path}")


def require_dir(path: Path) -> None:
    if not path.is_dir():
        raise SystemExit(f"missing required folder: {path}")


def ensure_safe_output(candidate_dir: Path, output_dir: Path) -> None:
    candidate_resolved = candidate_dir.resolve()
    output_resolved = output_dir.resolve()
    if output_resolved == candidate_resolved:
        raise SystemExit("refusing to use the candidate folder itself as sd-root")
    if candidate_resolved not in output_resolved.parents:
        raise SystemExit(f"refusing to clean output outside candidate folder: {output_resolved}")


def write_hashes(root: Path, destination: Path) -> None:
    rows = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        rows.append(f"{sha256_file(path)}  {rel}")
    destination.write_text("\n".join(rows) + "\n", encoding="ascii")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--profile", choices=sorted(EXPECTED), required=True)
    parser.add_argument("--out-root", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidate_dir = args.candidate_dir.resolve()
    out_root = (args.out_root or candidate_dir / "sd-root").resolve()

    require_file(candidate_dir / FIRMWARE_NAME)
    require_dir(OFFICIAL_SYSTEM)
    require_file(OFFICIAL_QBTEST)
    require_file(OFFICIAL_README)
    require_file(DM30XDB1_SOURCE)
    ensure_safe_output(candidate_dir, out_root)

    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)

    shutil.copy2(candidate_dir / FIRMWARE_NAME, out_root / FIRMWARE_NAME)
    shutil.copy2(OFFICIAL_QBTEST, out_root / "QBtest.txt")
    shutil.copy2(OFFICIAL_README, out_root / "readme.txt")
    shutil.copytree(OFFICIAL_SYSTEM, out_root / "system")
    shutil.copy2(DM30XDB1_SOURCE, out_root / "system" / "DM30XDB1.dat")

    validate_layout(out_root)
    validate_firmware(out_root, args.profile)
    validate_official_system(out_root)
    write_hashes(out_root, candidate_dir / "SD-ROOT-SHA256SUMS.txt")

    print("repair_sdroot_build=ok")
    print(f"candidate_dir={candidate_dir}")
    print(f"sd_root={out_root}")
    print(f"profile={args.profile}")
    print(f"firmware_sha256={sha256_file(out_root / FIRMWARE_NAME)}")
    print("system_source=official_v4_full_system")
    print("dm30xdb1=added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
