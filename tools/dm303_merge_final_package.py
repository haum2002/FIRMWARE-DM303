#!/usr/bin/env python3
"""Merge staged DM303 V4.0.1 beta artifacts into the final flash folder.

Workflow:
1. Treat backup/ as read-only reference input.
2. Treat firmware-candidates/v4.0.1-beta/ as staging output.
3. Rebuild DM303-V4.0.1-beta/ as the clean final flash package.
"""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
BACKUP_V4 = WORKSPACE / "backup" / "DM303 V4.0-read only"
CANDIDATE = WORKSPACE / "firmware-candidates" / "v4.0.1-beta"
FINAL = WORKSPACE / "DM303-V4.0.1-beta"

CANDIDATE_BIN = CANDIDATE / "DM303V4.0.1-beta.bin"
CANDIDATE_MS = CANDIDATE / "system" / "TEXT_MS.DAT"
FINAL_BIN = FINAL / "DM303V4.0.1-beta.bin"
FINAL_MS = FINAL / "system" / "TEXT_MS.DAT"
FINAL_REPORT = CANDIDATE / "FINAL-PACKAGE-REPORT.md"
FINAL_SUMS = CANDIDATE / "FINAL-PACKAGE-SHA256.txt"

EXPECTED_CANDIDATE_SHA256 = "05cc815fe003e49db3673d3c99f8a585d9744a0e90317e5c3ba5094b52bdeda1"
EXPECTED_MS_SHA256 = "7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def ensure_inside_workspace(path: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(WORKSPACE)
    return resolved


def copy_tree_contents(source: Path, destination: Path) -> None:
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def staged_system_overlays() -> list[Path]:
    system = CANDIDATE / "system"
    overlays = [CANDIDATE_MS]
    overlays.extend(sorted(system.glob("icon-E*.bmp")))
    overlays.extend(sorted(system.glob("icon-C*.bmp")))
    return sorted({path for path in overlays if path.exists()})


def validate_inputs() -> None:
    for path in [BACKUP_V4, CANDIDATE, CANDIDATE_BIN, CANDIDATE_MS]:
        if not path.exists():
            raise SystemExit(f"Missing required input: {path}")

    candidate_hash = sha256_file(CANDIDATE_BIN)
    if candidate_hash != EXPECTED_CANDIDATE_SHA256:
        raise SystemExit(f"Unexpected candidate firmware hash: {candidate_hash}")

    ms_hash = sha256_file(CANDIDATE_MS)
    if ms_hash != EXPECTED_MS_SHA256:
        raise SystemExit(f"Unexpected Malay text resource hash: {ms_hash}")


def rebuild_final() -> None:
    final_resolved = ensure_inside_workspace(FINAL)
    backup_resolved = ensure_inside_workspace(BACKUP_V4)
    candidate_resolved = ensure_inside_workspace(CANDIDATE)

    if backup_resolved == final_resolved or candidate_resolved == final_resolved:
        raise SystemExit("Refusing to merge: final path overlaps input path")

    if final_resolved.exists():
        shutil.rmtree(final_resolved)
    final_resolved.mkdir(parents=True)

    copy_tree_contents(backup_resolved, final_resolved)

    original_bin = final_resolved / "DM303V4.004.bin"
    if original_bin.exists():
        original_bin.unlink()

    shutil.copy2(CANDIDATE_BIN, FINAL_BIN)
    for source in staged_system_overlays():
        rel = source.relative_to(CANDIDATE)
        destination = FINAL / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def inventory(root: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            rows.append((rel, path.stat().st_size, sha256_file(path)))
    return rows


def validate_final() -> list[tuple[str, int, str]]:
    rows = inventory(FINAL)
    rels = {rel for rel, _, _ in rows}
    if "DM303V4.004.bin" in rels:
        raise SystemExit("Final folder still contains original DM303V4.004.bin")
    if "system/system/ASCII64.dat" in rels:
        raise SystemExit("Final folder contains invalid nested system/system tree")
    if "DM303V4.0.1-beta.bin" not in rels:
        raise SystemExit("Final folder is missing DM303V4.0.1-beta.bin")
    if "system/TEXT_MS.DAT" not in rels:
        raise SystemExit("Final folder is missing system/TEXT_MS.DAT")

    final_bin_hash = sha256_file(FINAL_BIN)
    if final_bin_hash != EXPECTED_CANDIDATE_SHA256:
        raise SystemExit(f"Final firmware hash mismatch: {final_bin_hash}")
    final_ms_hash = sha256_file(FINAL_MS)
    if final_ms_hash != EXPECTED_MS_SHA256:
        raise SystemExit(f"Final TEXT_MS hash mismatch: {final_ms_hash}")

    return rows


def write_reports(rows: list[tuple[str, int, str]]) -> None:
    write_text_lf(FINAL_SUMS, "".join(f"{digest}  {rel}\n" for rel, _, digest in rows))

    lines = [
        "# DM303 V4.0.1 beta final package report",
        "",
        "Final folder: `DM303-V4.0.1-beta/`",
        "",
        "## Source rules",
        "",
        "- `backup/` is read-only reference input.",
        "- `firmware-candidates/v4.0.1-beta/` is staging output.",
        "- `DM303-V4.0.1-beta/` is rebuilt as the clean flash package.",
        "",
        "## Final package checks",
        "",
        f"- File count: `{len(rows)}`",
        f"- Firmware: `DM303V4.0.1-beta.bin`",
        f"- Firmware SHA-256: `{sha256_file(FINAL_BIN)}`",
        f"- Malay UI resource SHA-256: `{sha256_file(FINAL_MS)}`",
        f"- Staged system overlays copied: `{len(staged_system_overlays())}`",
        "- Original `DM303V4.004.bin` is not present in final package.",
        "- Invalid nested `system/system/` tree is not present.",
        "",
        "## Files",
        "",
        "| Path | Size | SHA-256 |",
        "|---|---:|---|",
    ]
    for rel, size, digest in rows:
        lines.append(f"| `{rel}` | {size} | `{digest}` |")
    write_text_lf(FINAL_REPORT, "\n".join(lines) + "\n")


def main() -> int:
    validate_inputs()
    rebuild_final()
    rows = validate_final()
    write_reports(rows)

    print(f"backup_reference={BACKUP_V4}")
    print(f"candidate={CANDIDATE}")
    print(f"final={FINAL}")
    print(f"final_files={len(rows)}")
    print(f"final_firmware_sha256={sha256_file(FINAL_BIN)}")
    print(f"final_text_ms_sha256={sha256_file(FINAL_MS)}")
    print(f"report={FINAL_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
