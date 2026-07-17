#!/usr/bin/env python3
"""Probe DM303 firmware wait/retry loops relevant to measurement freeze.

The script is read-only. It disassembles selected firmware images and reports
backward branches, large delay constants, calls into the stream/byte-IO helpers,
and the current exp13 patch bytes. The output is meant to stop us from turning
guesses into flashable patches.
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM


LOAD_BASE = 0x08010000

DEFAULT_IMAGES = {
    "v3.16": Path("backup/DM303 V3.16-read only/DM303V316.bin"),
    "v4.0": Path("backup/DM303 V4.0-read only/DM303V4.004.bin"),
    "v4.0.1b": Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin"),
}

WATCH_RANGES_BY_IMAGE = {
    "v3.16": [
        (0x08016940, 0x08016aa0, "low byte-IO / hardware-ready waits"),
        (0x08018d60, 0x08019440, "measurement stream/status transaction helpers"),
        (0x0801e220, 0x0801e4c0, "relay/range and mode-switch helper"),
    ],
    "v4.0": [
        (0x08016980, 0x08016b00, "low byte-IO / hardware-ready waits"),
        (0x08019450, 0x08019b40, "measurement stream/status transaction helpers"),
        (0x0801f080, 0x0801f340, "relay/range and mode-switch helper"),
    ],
    "v4.0.1b": [
        (0x08016980, 0x08016b00, "low byte-IO / hardware-ready waits"),
        (0x08019450, 0x08019b40, "measurement stream/status transaction helpers"),
        (0x0801f080, 0x0801f340, "relay/range and mode-switch helper"),
    ],
}

HELPER_TARGETS_BY_IMAGE = {
    "v3.16": {
        0x080169C2,
        0x08018D80,
        0x08018E64,
        0x08018EB2,
        0x08018F1C,
        0x08018FC6,
        0x0801E254,
        0x0801E1AC,
        0x0801E29A,
    },
    "v4.0": {
        0x08016A06,
        0x0801946C,
        0x08019550,
        0x0801959E,
        0x08019608,
        0x080196B2,
        0x0801F0AC,
        0x0801F0F2,
        0x0801F19A,
    },
    "v4.0.1b": {
        0x08016A06,
        0x0801946C,
        0x08019550,
        0x0801959E,
        0x08019608,
        0x080196B2,
        0x0801F0AC,
        0x0801F0F2,
        0x0801F19A,
    },
}

PATCH_EXPECTATIONS = {
    0x09570: bytes.fromhex("00 bf"),
    0x09706: bytes.fromhex("4c d1"),
    0x09758: bytes.fromhex("00 bf"),
    0x097BE: bytes.fromhex("00 bf"),
    0x06A06: bytes.fromhex("00 f0 23 b8"),
    0x06A50: bytes.fromhex("70 b5 05 46 40 f6 a0 76"),
    0x0967C: bytes.fromhex("60 27"),
    0x09682: bytes.fromhex("60 27"),
    0x097E6: bytes.fromhex("20 f0 03 00"),
    0x0F19A: bytes.fromhex("1e f0 34 ba"),
    0x2D606: bytes.fromhex(
        "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
        "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
    ),
}

BRANCH_MNEMONICS = {
    "b",
    "b.w",
    "beq",
    "bne",
    "bcs",
    "bcc",
    "bhs",
    "blo",
    "bmi",
    "bpl",
    "bvs",
    "bvc",
    "bhi",
    "bls",
    "bge",
    "blt",
    "bgt",
    "ble",
    "cbz",
    "cbnz",
}


@dataclass(frozen=True)
class Branch:
    address: int
    mnemonic: str
    op_str: str
    target: int
    distance: int
    context: str


@dataclass(frozen=True)
class Call:
    address: int
    target: int
    context: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_image(path: Path) -> bytes:
    if not path.exists():
        raise SystemExit(f"Missing image: {path}")
    return path.read_bytes()


def range_name(address: int, ranges: list[tuple[int, int, str]]) -> str:
    for start, end, name in ranges:
        if start <= address < end:
            return name
    return "full image"


def disassemble_range(buf: bytes, start: int, end: int) -> list:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    start_offset = start - LOAD_BASE
    end_offset = end - LOAD_BASE
    if start_offset < 0 or end_offset > len(buf) or start_offset >= end_offset:
        return []
    return list(md.disasm(buf[start_offset:end_offset], start))


def disassemble_ranges(buf: bytes, ranges: list[tuple[int, int, str]]) -> list:
    insns = []
    for start, end, _name in ranges:
        insns.extend(disassemble_range(buf, start, end))
    return insns


def immediate_operand(insn) -> int | None:
    for operand in insn.operands:
        if operand.type == ARM_OP_IMM:
            return int(operand.imm)
    return None


def collect_backward_branches(insns: list, ranges: list[tuple[int, int, str]]) -> list[Branch]:
    rows: list[Branch] = []
    for insn in insns:
        if insn.mnemonic not in BRANCH_MNEMONICS:
            continue
        target = immediate_operand(insn)
        if target is None or target >= insn.address:
            continue
        context = range_name(insn.address, ranges)
        rows.append(
            Branch(
                address=insn.address,
                mnemonic=insn.mnemonic,
                op_str=insn.op_str,
                target=target,
                distance=insn.address - target,
                context=context,
            )
        )
    return rows


def collect_calls(insns: list, ranges: list[tuple[int, int, str]]) -> list[Call]:
    rows: list[Call] = []
    for insn in insns:
        if insn.mnemonic != "bl":
            continue
        target = immediate_operand(insn)
        if target is None:
            continue
        rows.append(Call(insn.address, target, range_name(insn.address, ranges)))
    return rows


def collect_large_constants(insns: list, ranges: list[tuple[int, int, str]]) -> list[tuple[int, str, str, int, str]]:
    rows: list[tuple[int, str, str, int, str]] = []
    for insn in insns:
        if insn.mnemonic not in {"movw", "mov.w", "movs"}:
            continue
        imm = immediate_operand(insn)
        if imm is None or imm < 0x80:
            continue
        rows.append((insn.address, insn.mnemonic, insn.op_str, imm, range_name(insn.address, ranges)))
    return rows


def format_addr(address: int) -> str:
    return f"0x{address:08x}"


def write_report(path: Path, images: dict[str, Path]) -> None:
    lines = [
        "# DM303 measurement loop probe",
        "",
        "Read-only static probe for wait/retry loops related to blank/freeze,",
        "latency, and measurement stream recovery. This report does not prove",
        "analog accuracy; it identifies firmware paths that are safe or unsafe",
        "to consider for further patching.",
        "",
    ]

    for label, image_path in images.items():
        buf = read_image(image_path)
        ranges = WATCH_RANGES_BY_IMAGE[label]
        insns = disassemble_ranges(buf, ranges)
        branches = collect_backward_branches(insns, ranges)
        calls = collect_calls(insns, ranges)
        constants = collect_large_constants(insns, ranges)

        lines.extend(
            [
                f"## {label}",
                "",
                f"- Path: `{image_path}`",
                f"- Size: `{len(buf)}` bytes",
                f"- SHA-256: `{sha256_file(image_path)}`",
                "",
                "### Backward branches in watched ranges",
                "",
                "| Address | Instruction | Target | Distance | Context |",
                "|---:|---|---:|---:|---|",
            ]
        )
        watched_branches = [row for row in branches if row.context != "full image"]
        for row in watched_branches:
            lines.append(
                f"| `{format_addr(row.address)}` | `{row.mnemonic} {row.op_str}` | "
                f"`{format_addr(row.target)}` | `{row.distance}` | {row.context} |"
            )
        if not watched_branches:
            lines.append("| | | | | none |")

        lines.extend(
            [
                "",
                "### Large constants in watched ranges",
                "",
                "| Address | Instruction | Immediate | Context |",
                "|---:|---|---:|---|",
            ]
        )
        watched_constants = [row for row in constants if row[4] != "full image"]
        for address, mnemonic, op_str, imm, context in watched_constants:
            lines.append(f"| `{format_addr(address)}` | `{mnemonic} {op_str}` | `0x{imm:x}` | {context} |")
        if not watched_constants:
            lines.append("| | | | none |")

        helper_targets = HELPER_TARGETS_BY_IMAGE[label]
        helper_calls = [call for call in calls if call.target in helper_targets]
        lines.extend(
            [
                "",
                "### Calls into watched helper targets",
                "",
                "| Caller | Target | Context |",
                "|---:|---:|---|",
            ]
        )
        for call in helper_calls:
            lines.append(f"| `{format_addr(call.address)}` | `{format_addr(call.target)}` | {call.context} |")
        if not helper_calls:
            lines.append("| | | none |")

        if label == "v4.0.1b":
            lines.extend(
                [
                    "",
                "### exp13 patch byte check",
                    "",
                    "| Offset | Expected | Actual | Match |",
                    "|---:|---|---|---|",
                ]
            )
            for offset, expected in PATCH_EXPECTATIONS.items():
                actual = buf[offset : offset + len(expected)]
                lines.append(
                    f"| `0x{offset:05x}` | `{expected.hex(' ')}` | `{actual.hex(' ')}` | `{actual == expected}` |"
                )

        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- The V3.16 and V4.0 stream transaction block still contains the same",
            "  large `0xfff0` inner delay and `0x200` retry limits. Because V3.16",
            "  can switch DC/AC more smoothly in the user's physical test, that",
            "  block is not the best first root-cause target for V4.0.1b.",
            "- The exp13 changes target the paths that can keep UI/status refresh",
            "  waiting after lower byte-IO timeout, while preserving official",
            "  relay/range timing and the original mode-switch helper. Command",
            "  `0x40` busy failure is routed to the existing error/clear path,",
            "  and low byte-IO now returns `0xff` if a ready flag never appears",
            "  within the bounded wrapper budget instead of continuing with a",
            "  stale read. Exp13 keeps the stream error cleanup from exp12 and",
            "  additionally routes the mode/range entry through a wrapper that",
            "  clears stale stream flag bits `0` and `1` before relay/range logic",
            "  continues.",
            "- Further accuracy/EMI/True RMS work still needs a confirmed",
            "  measurement-engine state hook before writing a safe patch.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("docs/v401b-measurement-loop-probe.md"))
    args = parser.parse_args()
    write_report(args.report, DEFAULT_IMAGES)
    print("measurement_loop_probe=ok")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
