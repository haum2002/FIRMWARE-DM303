#!/usr/bin/env python3
"""Safety audit for the DM303 V4.0.1b exp17 clean resource-restore image.

The audit is read-only. It proves that every byte changed from official V4.0
is inside a known patch interval, and that the exp17 clean-resource bytes are
present in the final flashable image.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path


LOAD_BASE = 0x08010000
VECTOR_WORDS = 80
FAULT_STUB_VECTOR = 0x08017555

DEFAULT_OFFICIAL = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
DEFAULT_CURRENT = Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin")
DEFAULT_REPORT = Path("docs/v401b-exp17-clean-resource-flash-safety-audit.md")

EXPECTED_OFFICIAL_SHA256 = "64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158"
EXPECTED_CURRENT_SHA256 = "d3760c42731a5fd6c0db508b51df85b1725046f028d767315916c4ee58904b77"

ALLOWED_INTERVALS = [
    (0x02CA0, 0x02CC0, "version identity strings"),
    (0x07554, 0x07568, "fault/default SYSRESETREQ recovery stub"),
    (0x09CA0, 0x09CA2, "runtime fail-stop loop fall-through"),
    (0x0C6C8, 0x0C6CA, "UI/render fail-stop loop fall-through"),
    (0x2C4EA, 0x2C4EC, "debug/semihosting fail-stop returns"),
]

CRITICAL_BYTES = {
    0x02CA0: ("visible main version marker", b"MT100MM V4.0.1e\x00"),
    0x02CB0: ("visible secondary version marker", b"BT100MM V4.0.1e\x00"),
    0x07554: ("SYSRESETREQ stub prefix", bytes.fromhex("02 48 02 49 01 60 bf f3 4f 8f")),
    0x09CA0: ("runtime fail-stop loop fall-through", bytes.fromhex("ff e7")),
    0x0C6C8: ("UI/render fail-stop loop fall-through", bytes.fromhex("ff e7")),
    0x2C4EA: ("debug/semihosting fail-stop returns", bytes.fromhex("70 47")),
}

STABLE_STRINGS = {
    0x0423B: " Loading GBK ...",
    0x0424C: "\\system\\HZK-ALL.GBK",
    0x04260: "Loading DM30XDB1 ...",
    0x04278: "\\system\\DM30XDB1.dat",
    0x04788: "Loading Start-LOGO-1 ...",
    0x047A4: "\\system\\LOGO-1.bmp",
    0x057F0: "VIEW VERSION",
}


@dataclass(frozen=True)
class DiffRange:
    start: int
    size: int
    label: str
    ok: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def u32_at(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def addr_to_offset(address: int, size: int) -> int | None:
    address &= ~1
    if LOAD_BASE <= address < LOAD_BASE + size:
        return address - LOAD_BASE
    return None


def is_original_self_loop_vector(data: bytes, vector_value: int) -> bool:
    offset = addr_to_offset(vector_value, len(data))
    return offset is not None and offset + 2 <= len(data) and data[offset : offset + 2] == b"\xfe\xe7"


def classify_offset(offset: int, official: bytes, current: bytes) -> tuple[str, bool]:
    if offset < VECTOR_WORDS * 4:
        word_offset = (offset // 4) * 4
        index = word_offset // 4
        before = u32_at(official, word_offset)
        after = u32_at(current, word_offset)
        ok = index != 1 and after == FAULT_STUB_VECTOR and is_original_self_loop_vector(official, before)
        return "self-loop vector redirected to shared recovery stub", ok
    for start, end, label in ALLOWED_INTERVALS:
        if start <= offset < end:
            return label, True
    return "unclassified firmware byte change", False


def diff_ranges(official: bytes, current: bytes) -> list[DiffRange]:
    rows: list[DiffRange] = []
    index = 0
    limit = min(len(official), len(current))
    while index < limit:
        if official[index] == current[index]:
            index += 1
            continue
        start = index
        labels = []
        ok = True
        while index < limit and official[index] != current[index]:
            label, row_ok = classify_offset(index, official, current)
            labels.append(label)
            ok = ok and row_ok
            index += 1
        rows.append(DiffRange(start, index - start, ", ".join(sorted(set(labels))), ok))
    return rows


def nul_terminated(data: bytes, offset: int) -> str:
    end = data.find(b"\x00", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("ascii", "replace")


def check_critical_bytes(current: bytes) -> list[tuple[int, str, bytes, bytes, bool]]:
    rows = []
    for offset, (name, expected) in CRITICAL_BYTES.items():
        actual = current[offset : offset + len(expected)]
        rows.append((offset, name, expected, actual, actual == expected))
    return rows


def bool_text(value: bool) -> str:
    return "PASS" if value else "FAIL"


def write_report(official_path: Path, current_path: Path, report_path: Path) -> bool:
    official = official_path.read_bytes()
    current = current_path.read_bytes()
    official_hash = sha256_bytes(official)
    current_hash = sha256_bytes(current)
    ranges = diff_ranges(official, current)
    criticals = check_critical_bytes(current)
    stable_rows = [
        (offset, expected, nul_terminated(official, offset), nul_terminated(current, offset))
        for offset, expected in STABLE_STRINGS.items()
    ]

    hash_ok = official_hash == EXPECTED_OFFICIAL_SHA256 and current_hash == EXPECTED_CURRENT_SHA256
    size_ok = len(official) == len(current) == 203260
    diff_ok = all(row.ok for row in ranges)
    critical_ok = all(row[-1] for row in criticals)
    stable_ok = all(before == expected and after == expected for _, expected, before, after in stable_rows)
    reset_ok = u32_at(official, 4) == u32_at(current, 4)
    ok = hash_ok and size_ok and diff_ok and critical_ok and stable_ok and reset_ok

    lines = [
        "# DM303 V4.0.1b exp17 clean resource flash safety audit",
        "",
        f"Official: `{official_path.as_posix()}`",
        f"Current: `{current_path.as_posix()}`",
        "",
        "## Result",
        "",
        f"- Overall: `{bool_text(ok)}`",
        f"- Official SHA-256: `{official_hash}`",
        f"- Current SHA-256: `{current_hash}`",
        f"- Size unchanged: `{bool_text(size_ok)}`",
        f"- Reset vector unchanged: `{bool_text(reset_ok)}`",
        f"- All changed bytes inside allowed exp17 clean-resource intervals: `{bool_text(diff_ok)}`",
        f"- Critical exp17 clean-resource byte guards present: `{bool_text(critical_ok)}`",
        f"- Startup/resource-loader strings unchanged: `{bool_text(stable_ok)}`",
        "",
        "## Critical Bytes",
        "",
        "| Offset | Name | Expected | Actual | OK |",
        "|---:|---|---|---|---|",
    ]
    for offset, name, expected, actual, row_ok in criticals:
        lines.append(
            f"| `0x{offset:05x}` | {name} | `{expected.hex(' ')}` | "
            f"`{actual.hex(' ')}` | `{bool_text(row_ok)}` |"
        )

    lines.extend(["", "## Changed Ranges", "", "| Offset | Size | Classification | OK |", "|---:|---:|---|---|"])
    for row in ranges:
        lines.append(f"| `0x{row.start:05x}` | `{row.size}` | {row.label} | `{bool_text(row.ok)}` |")

    lines.extend(["", "## Stable Strings", "", "| Offset | Expected | Official | Current | OK |", "|---:|---|---|---|---|"])
    for offset, expected, before, after in stable_rows:
        lines.append(
            f"| `0x{offset:05x}` | `{expected}` | `{before}` | `{after}` | "
            f"`{bool_text(before == expected and after == expected)}` |"
        )

    lines.extend(
        [
            "",
            "## Scope",
            "",
            "- This audit proves byte placement and startup/resource-loader integrity.",
            "- It does not prove analog accuracy, zero-noise measurement, or hardware-side calibration.",
            "- Device testing is still required for ammeter AC->DC latency, overload recovery, and UI visual quality.",
        ]
    )
    write_text_lf(report_path, "\n".join(lines) + "\n")
    return ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, default=DEFAULT_OFFICIAL)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ok = write_report(args.official, args.current, args.report)
    print(f"exp17_clean_resource_safety_audit_ok={ok}")
    print(f"official={args.official}")
    print(f"current={args.current}")
    print(f"report={args.report}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
