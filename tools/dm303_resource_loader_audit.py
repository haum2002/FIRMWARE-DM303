#!/usr/bin/env python3
"""Audit DM303 firmware resource-loader paths against a system folder."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


DEFAULT_IMAGE = Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin")
DEFAULT_ROOT = Path("dm303_firmware/DM303-V4.0.1-beta")
DEFAULT_REPORT = Path("docs/v401b-resource-loader-audit.md")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def extract_ascii_strings(buf: bytes, min_len: int = 6) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    start: int | None = None
    for index, byte in enumerate(buf + b"\x00"):
        printable = 0x20 <= byte <= 0x7E
        if printable and start is None:
            start = index
        elif not printable and start is not None:
            if index - start >= min_len:
                rows.append((start, buf[start:index].decode("ascii", "replace")))
            start = None
    return rows


def resource_paths(buf: bytes) -> list[tuple[int, str]]:
    pattern = re.compile(r"\\system\\[^\\\0]+", re.IGNORECASE)
    paths = []
    for offset, text in extract_ascii_strings(buf):
        if pattern.fullmatch(text):
            paths.append((offset, text))
    return sorted(paths, key=lambda row: row[1].lower())


def resolve_case_insensitive(root: Path, resource_path: str) -> Path | None:
    parts = [part for part in resource_path.replace("/", "\\").split("\\") if part]
    current = root
    for part in parts:
        if not current.is_dir():
            return None
        matches = [child for child in current.iterdir() if child.name.lower() == part.lower()]
        if not matches:
            return None
        current = matches[0]
    return current


def build_report(image: Path, root: Path) -> tuple[str, bool]:
    data = image.read_bytes()
    rows = resource_paths(data)
    checked = []
    for offset, resource in rows:
        actual = resolve_case_insensitive(root, resource)
        exists = actual is not None and actual.is_file()
        size = actual.stat().st_size if exists else ""
        digest = sha256_file(actual) if exists else ""
        checked.append((offset, resource, actual, exists, size, digest))

    ok = all(row[3] for row in checked)
    lines = [
        "# DM303 resource-loader audit",
        "",
        f"Image: `{image.as_posix()}`",
        f"Root: `{root.as_posix()}`",
        f"Image SHA-256: `{sha256_file(image)}`",
        f"Resource paths referenced: `{len(checked)}`",
        f"All referenced resources present: `{ok}`",
        "",
        "| Offset | Firmware path | Resolved file | Exists | Size | SHA-256 |",
        "|---:|---|---|---|---:|---|",
    ]
    for offset, resource, actual, exists, size, digest in checked:
        resolved = actual.as_posix() if actual else ""
        lines.append(f"| `0x{offset:05x}` | `{resource}` | `{resolved}` | `{exists}` | `{size}` | `{digest}` |")
    return "\n".join(lines) + "\n", ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, ok = build_report(args.image, args.root)
    write_text_lf(args.report, report)
    print(f"resource_loader_audit_ok={ok}")
    print(f"image={args.image}")
    print(f"root={args.root}")
    print(f"report={args.report}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
