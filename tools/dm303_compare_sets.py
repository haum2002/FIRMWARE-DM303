#!/usr/bin/env python3
"""Compare supplied DM303 firmware folders by path, size, and SHA-256."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


DEFAULT_CURRENT = Path("DM303-V4.0.1-beta")
DEFAULT_BACKUP = Path("backup")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inventory(root: Path) -> dict[str, dict[str, object]]:
    result: dict[str, dict[str, object]] = {}
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        result[rel.lower()] = {
            "rel": rel,
            "size": path.stat().st_size,
            "sha256": sha256(path),
        }
    return result


def print_set_summary(name: str, root: Path, files: dict[str, dict[str, object]]) -> None:
    total_bytes = sum(int(item["size"]) for item in files.values())
    firmware_bins = [
        item for key, item in sorted(files.items()) if key.endswith(".bin")
    ]

    print(f"== {name} ==")
    print(f"path={root}")
    print(f"files={len(files)} total_bytes={total_bytes}")
    for item in firmware_bins:
        print(
            f"bin={item['rel']} size={item['size']} "
            f"sha256={item['sha256']}"
        )
    print(f"has system/DM30XDB1.dat={'system/dm30xdb1.dat' in files}")
    print()


def print_comparison(
    current_name: str,
    current: dict[str, dict[str, object]],
    other_name: str,
    other: dict[str, dict[str, object]],
) -> None:
    current_keys = set(current)
    other_keys = set(other)
    common = sorted(current_keys & other_keys)
    different = [
        key for key in common
        if current[key]["size"] != other[key]["size"]
        or current[key]["sha256"] != other[key]["sha256"]
    ]
    same = len(common) - len(different)
    only_current = sorted(current_keys - other_keys)
    only_other = sorted(other_keys - current_keys)

    print(f"COMPARE {current_name} vs {other_name}")
    print(
        f"  common={len(common)} same={same} different={len(different)} "
        f"only_current={len(only_current)} only_other={len(only_other)}"
    )

    if different:
        print("  different first 12:")
        for key in different[:12]:
            left = current[key]
            right = other[key]
            print(
                f"    {left['rel']}: current size={left['size']} "
                f"sha256={left['sha256']} | other size={right['size']} "
                f"sha256={right['sha256']}"
            )
    if only_current:
        print("  only current first 12:")
        for key in only_current[:12]:
            item = current[key]
            print(f"    {item['rel']} size={item['size']} sha256={item['sha256']}")
    if only_other:
        print("  only other first 12:")
        for key in only_other[:12]:
            item = other[key]
            print(f"    {item['rel']} size={item['size']} sha256={item['sha256']}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--backup-root", type=Path, default=DEFAULT_BACKUP)
    args = parser.parse_args()

    if not args.current.is_dir():
        raise SystemExit(f"Current firmware folder not found: {args.current}")
    if not args.backup_root.is_dir():
        raise SystemExit(f"Backup root not found: {args.backup_root}")

    current = inventory(args.current)
    backups = [
        path for path in sorted(args.backup_root.iterdir())
        if path.is_dir()
    ]

    print_set_summary("current", args.current, current)
    for path in backups:
        files = inventory(path)
        print_set_summary(f"backup/{path.name}", path, files)

    for path in backups:
        files = inventory(path)
        print_comparison("current", current, f"backup/{path.name}", files)

    print("Safety note")
    print("  This tool is read-only and does not copy backup files into the final package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
