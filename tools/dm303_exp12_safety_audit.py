#!/usr/bin/env python3
"""Safety audit for the DM303 V4.0.1b exp12 firmware image.

This is read-only. It compares the final flashable image against the official
V4.0 reference and proves that every changed byte falls inside a known exp12
patch area. It also checks that reset/startup identity and important resource
loader strings are unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


LOAD_BASE = 0x08010000
VECTOR_WORDS = 80
FAULT_STUB_VECTOR = 0x08017555

DEFAULT_OFFICIAL = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
DEFAULT_CURRENT = Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin")
DEFAULT_REPORT = Path("docs/v401b-exp12-flash-safety-audit.md")

EXPECTED_CURRENT_SHA256 = "0a2090bf5c42cd89509f65881d8b54862d243c6b9d224478ab95bb3ef8e06a16"
EXPECTED_OFFICIAL_SHA256 = "64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158"

ALLOWED_INTERVALS = [
    (0x02CA0, 0x02CC0, "version identity strings"),
    (0x045B2, 0x045B6, "boot-logo load call routed through delay wrapper"),
    (0x06A06, 0x06A0A, "low byte-IO entry branch to bounded wrapper"),
    (0x06A50, 0x06AA0, "bounded low byte-IO wrapper code"),
    (0x07554, 0x07568, "fault/default SYSRESETREQ recovery stub"),
    (0x09570, 0x09572, "stream-read retry branch removed"),
    (0x0967C, 0x0967D, "command 0x40 retry clamp"),
    (0x09682, 0x09683, "command 0x48 retry clamp"),
    (0x09706, 0x09707, "command 0x40 busy failure error route"),
    (0x09758, 0x0975A, "command/status retry branch removed"),
    (0x097BE, 0x097C0, "mode/status retry branch removed"),
    (0x097E6, 0x097EA, "stream error cleanup clears status bits 0 and 1"),
    (0x09CA0, 0x09CA1, "runtime fail-stop loop fall-through"),
    (0x0C6C8, 0x0C6C9, "UI/render fail-stop loop fall-through"),
    (0x25BF8, 0x25C00, "language menu name renamed to Melayu"),
    (0x2C4EA, 0x2C4EC, "debug/semihosting fail-stop returns"),
    (0x2D5C0, 0x2D5E0, "boot-logo delay wrapper code cave"),
]

CRITICAL_BYTES = {
    0x06A06: ("low byte-IO entry branch", bytes.fromhex("00 f0 23 b8")),
    0x06A50: ("bounded wrapper prefix", bytes.fromhex("70 b5 05 46 40 f6 a0 76")),
    0x07554: ("SYSRESETREQ stub prefix", bytes.fromhex("02 48 02 49 01 60 bf f3 4f 8f")),
    0x09570: ("stream-read retry removed", bytes.fromhex("00 bf")),
    0x0967C: ("command 0x40 retry clamp", bytes.fromhex("60")),
    0x09682: ("command 0x48 retry clamp", bytes.fromhex("60")),
    0x09706: ("command 0x40 busy failure route", bytes.fromhex("4c")),
    0x09758: ("command/status retry removed", bytes.fromhex("00 bf")),
    0x097BE: ("mode/status retry removed", bytes.fromhex("00 bf")),
    0x097E6: ("stream error cleanup clears bits 0 and 1", bytes.fromhex("20 f0 03 00")),
    0x2C4EA: ("debug/semihosting fail-stop returns", bytes.fromhex("70 47")),
    0x2D5C0: ("boot-logo delay wrapper prefix", bytes.fromhex("10 b5")),
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

VECTOR_NAMES = [
    "initial_sp",
    "reset",
    "nmi",
    "hardfault",
    "memmanage",
    "busfault",
    "usagefault",
    "reserved7",
    "reserved8",
    "reserved9",
    "reserved10",
    "svcall",
    "debugmon",
    "reserved13",
    "pendsv",
    "systick",
]


@dataclass(frozen=True)
class DiffByte:
    offset: int
    before: int
    after: int
    classification: str
    ok: bool


@dataclass(frozen=True)
class VectorChange:
    index: int
    name: str
    before: int
    after: int
    self_loop_target: bool
    ok: bool


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32_at(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def vector_name(index: int) -> str:
    if index < len(VECTOR_NAMES):
        return VECTOR_NAMES[index]
    return f"irq{index - 16}"


def addr_to_offset(address: int, size: int) -> int | None:
    address &= ~1
    if LOAD_BASE <= address < LOAD_BASE + size:
        return address - LOAD_BASE
    return None


def is_original_self_loop_vector(data: bytes, vector_value: int) -> bool:
    offset = addr_to_offset(vector_value, len(data))
    if offset is None or offset + 2 > len(data):
        return False
    return data[offset : offset + 2] == bytes.fromhex("fe e7")


def vector_diff_classification(offset: int, official: bytes, current: bytes) -> tuple[str, bool]:
    word_offset = (offset // 4) * 4
    index = word_offset // 4
    before = u32_at(official, word_offset)
    after = u32_at(current, word_offset)
    if index == 1:
        return "reset vector change is not allowed", False
    if after == FAULT_STUB_VECTOR and is_original_self_loop_vector(official, before):
        return "self-loop vector redirected to shared recovery stub", True
    return "unexpected vector-table change", False


def interval_classification(offset: int) -> tuple[str, bool]:
    for start, end, name in ALLOWED_INTERVALS:
        if start <= offset < end:
            return name, True
    return "unclassified firmware byte change", False


def classify_diff_byte(offset: int, before: int, after: int, official: bytes, current: bytes) -> DiffByte:
    if offset < VECTOR_WORDS * 4:
        classification, ok = vector_diff_classification(offset, official, current)
    else:
        classification, ok = interval_classification(offset)
    return DiffByte(offset, before, after, classification, ok)


def diff_bytes(official: bytes, current: bytes) -> list[DiffByte]:
    return [
        classify_diff_byte(index, before, after, official, current)
        for index, (before, after) in enumerate(zip(official, current))
        if before != after
    ]


def diff_ranges(official: bytes, current: bytes) -> list[tuple[int, int, bytes, bytes, str, bool]]:
    rows: list[tuple[int, int, bytes, bytes, str, bool]] = []
    index = 0
    while index < min(len(official), len(current)):
        if official[index] == current[index]:
            index += 1
            continue
        start = index
        classifications = []
        ok = True
        while index < min(len(official), len(current)) and official[index] != current[index]:
            diff = classify_diff_byte(index, official[index], current[index], official, current)
            classifications.append(diff.classification)
            ok = ok and diff.ok
            index += 1
        label = ", ".join(sorted(set(classifications)))
        rows.append((start, index - start, official[start:index], current[start:index], label, ok))
    return rows


def changed_vectors(official: bytes, current: bytes) -> list[VectorChange]:
    rows: list[VectorChange] = []
    for index in range(min(VECTOR_WORDS, len(official) // 4, len(current) // 4)):
        offset = index * 4
        before = u32_at(official, offset)
        after = u32_at(current, offset)
        if before == after:
            continue
        self_loop = is_original_self_loop_vector(official, before)
        ok = index != 1 and after == FAULT_STUB_VECTOR and self_loop
        rows.append(VectorChange(index, vector_name(index), before, after, self_loop, ok))
    return rows


def nul_terminated(data: bytes, offset: int) -> str:
    end = data.find(b"\x00", offset)
    if end < 0:
        end = len(data)
    return data[offset:end].decode("ascii", "replace")


def stable_string_rows(official: bytes, current: bytes) -> list[tuple[int, str, str, str, bool]]:
    rows = []
    for offset, expected in STABLE_STRINGS.items():
        before = nul_terminated(official, offset)
        after = nul_terminated(current, offset)
        rows.append((offset, expected, before, after, before == expected and after == expected))
    return rows


def critical_byte_rows(current: bytes) -> list[tuple[int, str, bytes, bytes, bool]]:
    rows = []
    for offset, (name, expected) in CRITICAL_BYTES.items():
        actual = current[offset : offset + len(expected)]
        rows.append((offset, name, expected, actual, actual == expected))
    return rows


def format_bytes(data: bytes, limit: int = 18) -> str:
    shown = data[:limit].hex(" ")
    if len(data) > limit:
        shown += " ..."
    return shown


def bool_text(value: bool) -> str:
    return "PASS" if value else "FAIL"


def write_report(path: Path, official_path: Path, current_path: Path) -> bool:
    official = official_path.read_bytes()
    current = current_path.read_bytes()
    official_hash = sha256_bytes(official)
    current_hash = sha256_bytes(current)
    diffs = diff_bytes(official, current)
    ranges = diff_ranges(official, current)
    vectors = changed_vectors(official, current)
    criticals = critical_byte_rows(current)
    stable_strings = stable_string_rows(official, current)
    classification_counts = Counter(diff.classification for diff in diffs)

    size_ok = len(official) == len(current) == 203260
    official_hash_ok = official_hash == EXPECTED_OFFICIAL_SHA256
    current_hash_ok = current_hash == EXPECTED_CURRENT_SHA256
    initial_sp_ok = u32_at(official, 0) == u32_at(current, 0)
    reset_vector_ok = u32_at(official, 4) == u32_at(current, 4)
    all_diff_bytes_ok = all(diff.ok for diff in diffs)
    vectors_ok = all(row.ok for row in vectors)
    critical_ok = all(row[-1] for row in criticals)
    strings_ok = all(row[-1] for row in stable_strings)
    overall_ok = all(
        [
            size_ok,
            official_hash_ok,
            current_hash_ok,
            initial_sp_ok,
            reset_vector_ok,
            all_diff_bytes_ok,
            vectors_ok,
            critical_ok,
            strings_ok,
        ]
    )

    lines = [
        "# DM303 V4.0.1b exp12 flash safety audit",
        "",
        "Read-only comparison of the final flashable image against the official",
        "V4.0 reference. This report proves whether every changed byte belongs",
        "to the known exp12 patch set and whether startup/resource-loader strings",
        "remain stable.",
        "",
        "## Overall",
        "",
        f"- Result: `{bool_text(overall_ok)}`",
        f"- Official image: `{official_path}`",
        f"- Current image: `{current_path}`",
        f"- Official SHA-256: `{official_hash}`",
        f"- Current SHA-256: `{current_hash}`",
        f"- Differing bytes: `{len(diffs)}`",
        f"- Differing ranges: `{len(ranges)}`",
        "",
        "## Safety gates",
        "",
        "| Gate | Result | Evidence |",
        "|---|---|---|",
        f"| Official hash matches V4.0 reference | `{bool_text(official_hash_ok)}` | `{official_hash}` |",
        f"| Current hash matches exp12 final | `{bool_text(current_hash_ok)}` | `{current_hash}` |",
        f"| Firmware size unchanged | `{bool_text(size_ok)}` | official `{len(official)}`, current `{len(current)}` |",
        f"| Initial SP unchanged | `{bool_text(initial_sp_ok)}` | `0x{u32_at(current, 0):08x}` |",
        f"| Reset vector unchanged | `{bool_text(reset_vector_ok)}` | `0x{u32_at(current, 4):08x}` |",
        f"| Every changed byte is allowlisted | `{bool_text(all_diff_bytes_ok)}` | `{len(diffs)}` changed bytes classified |",
        f"| Vector changes are only self-loop recovery redirects | `{bool_text(vectors_ok)}` | `{len(vectors)}` vector entries changed |",
        f"| Critical exp12 patch bytes present | `{bool_text(critical_ok)}` | `{len(criticals)}` byte guards checked |",
        f"| Resource-loader strings unchanged | `{bool_text(strings_ok)}` | `{len(stable_strings)}` strings checked |",
        "",
        "## Diff classification counts",
        "",
        "| Classification | Bytes |",
        "|---|---:|",
    ]
    for label, count in sorted(classification_counts.items()):
        lines.append(f"| {label} | {count} |")

    lines.extend(
        [
            "",
            "## Changed vector entries",
            "",
            "Reset vector is intentionally not listed because it is unchanged.",
            "Changed entries below point to the shared fault/default recovery stub",
            "only when the official target was a `fe e7` self-loop.",
            "",
            "| Index | Name | Before | After | Official target self-loop | OK |",
            "|---:|---|---:|---:|---|---|",
        ]
    )
    for row in vectors:
        lines.append(
            f"| {row.index} | {row.name} | `0x{row.before:08x}` | "
            f"`0x{row.after:08x}` | `{row.self_loop_target}` | `{row.ok}` |"
        )

    lines.extend(
        [
            "",
            "## Critical byte guards",
            "",
            "| Offset | Address | Purpose | Expected | Actual | OK |",
            "|---:|---:|---|---|---|---|",
        ]
    )
    for offset, name, expected, actual, ok in criticals:
        lines.append(
            f"| `0x{offset:05x}` | `0x{LOAD_BASE + offset:08x}` | {name} | "
            f"`{expected.hex(' ')}` | `{actual.hex(' ')}` | `{ok}` |"
        )

    lines.extend(
        [
            "",
            "## Stable resource-loader strings",
            "",
            "| Offset | Expected | Official | Current | OK |",
            "|---:|---|---|---|---|",
        ]
    )
    for offset, expected, before, after, ok in stable_strings:
        lines.append(f"| `0x{offset:05x}` | `{expected}` | `{before}` | `{after}` | `{ok}` |")

    lines.extend(
        [
            "",
            "## Changed byte ranges",
            "",
            "| Offset | Size | Classification | OK | Official bytes | Current bytes |",
            "|---:|---:|---|---|---|---|",
        ]
    )
    for offset, size, before, after, label, ok in ranges:
        lines.append(
            f"| `0x{offset:05x}` | {size} | {label} | `{ok}` | "
            f"`{format_bytes(before)}` | `{format_bytes(after)}` |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The bootloader below application load base `0x08010000` is not present",
            "  in this firmware image, so this package cannot directly overwrite it.",
            "- The application reset vector is unchanged. Exp12 does not redirect",
            "  normal boot/startup.",
            "- The SD/resource loader strings for `DM30XDB1`, `LOGO-1.bmp`, and core",
            "  system files remain byte-identical.",
            "- Vector-table changes are limited to official self-loop fault/default",
            "  entries redirected to a shared reset-request recovery stub.",
            "- This audit does not prove analog accuracy. It proves the exp12 binary",
            "  is a tightly scoped runtime recovery build rather than an updater or",
            "  bootloader modification.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return overall_ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official", type=Path, default=DEFAULT_OFFICIAL)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ok = write_report(args.report, args.official, args.current)
    print(f"exp12_safety_audit_ok={ok}")
    print(f"official={args.official}")
    print(f"current={args.current}")
    print(f"report={args.report}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
