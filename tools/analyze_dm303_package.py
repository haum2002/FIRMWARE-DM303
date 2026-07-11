#!/usr/bin/env python3
"""Read-only checks for an AUTOOL DM303 firmware package."""

from __future__ import annotations

import argparse
import hashlib
import math
import re
import struct
from pathlib import Path


FIRMWARE_CANDIDATES = ("DM303V4.004.bin", "DM303-V3.13.bin")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = [0] * 256
    for byte in data:
        counts[byte] += 1
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in counts if count)


def find_firmware(root: Path) -> Path:
    for name in FIRMWARE_CANDIDATES:
        candidate = root / name
        if candidate.exists():
            return candidate
    bins = sorted(root.glob("*.bin"))
    if len(bins) == 1:
        return bins[0]
    raise SystemExit(f"Could not identify firmware .bin in {root}")


def system_files(root: Path) -> dict[str, Path]:
    system = root / "system"
    if not system.exists():
        return {}
    return {
        str(path.relative_to(root)).replace("\\", "/").lower(): path
        for path in system.rglob("*")
        if path.is_file()
    }


def embedded_system_paths(data: bytes) -> list[tuple[int, str]]:
    paths: list[tuple[int, str]] = []
    seen: set[str] = set()
    for match in re.finditer(rb"\\system\\[A-Za-z0-9_.-]+", data):
        path = match.group().decode("ascii").replace("\\", "/").lstrip("/")
        key = path.lower()
        if key not in seen:
            seen.add(key)
            paths.append((match.start(), path))
    return paths


def ascii_strings(data: bytes, minimum: int = 6) -> list[tuple[int, str]]:
    pattern = rb"[ -~]{" + str(minimum).encode("ascii") + rb",}"
    return [(m.start(), m.group().decode("ascii", "replace")) for m in re.finditer(pattern, data)]


def analyze(root: Path) -> int:
    root = root.resolve()
    firmware = find_firmware(root)
    data = firmware.read_bytes()
    sp, reset = struct.unpack_from("<II", data, 0)

    print(f"Package: {root}")
    print(f"Firmware: {firmware.name}")
    print(f"Firmware size: {len(data)} bytes ({len(data):#x})")
    print(f"Firmware SHA-256: {sha256(firmware)}")
    print(f"Initial SP: {sp:#010x}")
    print(f"Reset handler: {reset:#010x}")
    if 0x08000000 <= (reset & ~1) < 0x08100000:
        print(f"Reset offset @ 0x08000000: {(reset & ~1) - 0x08000000:#x}")

    blocks = [data[i : i + 4096] for i in range(0, len(data), 4096)]
    entropies = [entropy(block) for block in blocks]
    print(f"Entropy 4 KiB blocks: min={min(entropies):.3f} max={max(entropies):.3f}")

    actual = system_files(root)
    expected = embedded_system_paths(data)
    print(f"Embedded system paths: {len(expected)}")
    missing = []
    for offset, path in expected:
        ok = path.lower() in actual
        status = "OK" if ok else "MISSING"
        print(f"  {offset:06x} {status:7} {path}")
        if not ok:
            missing.append(path)

    interesting_terms = ("DM30", "MT100", "BT100", "VERSION", "ERROR", "FAT", "CAN")
    interesting = [
        (offset, text)
        for offset, text in ascii_strings(data)
        if any(term.lower() in text.lower() for term in interesting_terms)
    ]
    print("Interesting strings:")
    for offset, text in interesting[:60]:
        print(f"  {offset:06x} {text}")

    return 1 if missing else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_root", nargs="?", default="DM303-V4.0")
    args = parser.parse_args()
    return analyze(Path(args.package_root))


if __name__ == "__main__":
    raise SystemExit(main())
