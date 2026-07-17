#!/usr/bin/env python3
"""Probe DM303 measurement math/scaling candidates.

This read-only probe scans firmware images for coherent VFP/float-heavy code
groups, PC-loaded float/double constants, and calls into known measurement
mode/range helpers. It is intended to prevent speculative ADC/RMS/filter
patches by recording the exact code areas that need proof before modification.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM, ARM_OP_MEM


LOAD_BASE = 0x08010000

DEFAULT_IMAGES = {
    "v3.16": Path("backup/DM303 V3.16-read only/DM303V316.bin"),
    "v4.0": Path("backup/DM303 V4.0-read only/DM303V4.004.bin"),
    "repair-i": Path("firmware-candidates/v4.0.1h-repair-i/DM303V4.0.1-beta.bin"),
}

HELPER_TARGETS = {
    "v3.16": {
        0x08018D80: "stream/read helper",
        0x08018F1C: "command/status helper",
        0x0801E1AC: "relay/range selector",
        0x0801E29A: "mode/range routine",
    },
    "v4.0": {
        0x08019550: "stream/read helper",
        0x08019608: "command/status helper",
        0x0801F0F2: "relay/range selector",
        0x0801F19A: "mode/range routine",
    },
    "repair-i": {
        0x08019550: "stream/read helper",
        0x08019608: "command/status helper",
        0x0801F0F2: "relay/range selector",
        0x0801F19A: "mode/range routine",
    },
}

FLOAT_OPS = {
    "vadd.f32",
    "vsub.f32",
    "vmul.f32",
    "vdiv.f32",
    "vcvt.u32.f32",
    "vcvt.s32.f32",
    "vcvt.f32.s32",
    "vsqrt.f32",
}

PROLOGUE_PREFIXES = (
    bytes.fromhex("2d e9"),
    bytes.fromhex("2d ed"),
    bytes.fromhex("10 b5"),
    bytes.fromhex("30 b5"),
    bytes.fromhex("70 b5"),
    bytes.fromhex("80 b5"),
    bytes.fromhex("f0 b5"),
)


@dataclass(frozen=True)
class VfpGroup:
    start_offset: int
    instructions: list

    @property
    def address(self) -> int:
        return LOAD_BASE + self.start_offset

    @property
    def float_op_count(self) -> int:
        return sum(1 for insn in self.instructions if insn.mnemonic in FLOAT_OPS)

    @property
    def mnemonic_counts(self) -> Counter[str]:
        return Counter(insn.mnemonic for insn in self.instructions)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_function_start(data: bytes, offset: int) -> int:
    best = None
    for candidate in range(max(0, offset - 0x300), offset + 1, 2):
        if any(data[candidate : candidate + len(prefix)] == prefix for prefix in PROLOGUE_PREFIXES):
            best = candidate
    return best if best is not None else offset


def scan_vfp_groups(data: bytes) -> list[VfpGroup]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    grouped: dict[int, list] = defaultdict(list)
    for offset in range(0, len(data) - 4, 2):
        insns = list(md.disasm(data[offset : offset + 4], LOAD_BASE + offset, count=1))
        if not insns:
            continue
        insn = insns[0]
        if not insn.mnemonic.startswith("v"):
            continue
        start = find_function_start(data, offset)
        grouped[start].append(insn)

    groups = [VfpGroup(start, insns) for start, insns in grouped.items()]
    return sorted(
        groups,
        key=lambda group: (group.float_op_count, len(group.instructions)),
        reverse=True,
    )


def reg_name(insn, reg_id: int) -> str:
    return insn.reg_name(reg_id) or ""


def pc_vldr_constants(data: bytes, group: VfpGroup) -> list[tuple[int, int, str, float]]:
    rows: list[tuple[int, int, str, float]] = []
    for insn in group.instructions:
        if insn.mnemonic != "vldr" or len(insn.operands) < 2:
            continue
        mem = insn.operands[1]
        if mem.type != ARM_OP_MEM or reg_name(insn, mem.mem.base) != "pc":
            continue
        literal_addr = ((insn.address + 4) & ~3) + mem.mem.disp
        literal_offset = literal_addr - LOAD_BASE
        if literal_offset < 0 or literal_offset + 4 > len(data):
            continue
        dest = reg_name(insn, insn.operands[0].reg)
        if dest.startswith("d") and literal_offset + 8 <= len(data):
            value = struct.unpack_from("<d", data, literal_offset)[0]
            kind = "f64"
        else:
            value = struct.unpack_from("<f", data, literal_offset)[0]
            kind = "f32"
        rows.append((insn.address, literal_addr, kind, value))
    return rows


def calls_in_window(data: bytes, start_offset: int, size: int, targets: dict[int, str]) -> list[tuple[int, str]]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    rows: list[tuple[int, str]] = []
    end = min(len(data), start_offset + size)
    for offset in range(start_offset, end - 4, 2):
        insns = list(md.disasm(data[offset : offset + 4], LOAD_BASE + offset, count=1))
        if not insns:
            continue
        insn = insns[0]
        if not insn.mnemonic.startswith("bl"):
            continue
        for operand in insn.operands:
            if operand.type == ARM_OP_IMM:
                target = int(operand.imm) & ~1
                if target in targets:
                    rows.append((insn.address, targets[target]))
    return rows


def format_float(value: float) -> str:
    if value == 0:
        return "0"
    if abs(value) >= 1e6 or abs(value) < 1e-4:
        return f"{value:.8e}"
    return f"{value:.8g}"


def build_report(images: dict[str, Path], limit: int) -> str:
    lines: list[str] = [
        "# DM303 measurement math/filter probe",
        "",
        "Read-only scan for float-heavy measurement, scaling, display, and",
        "possible filter/math functions. This report does not certify a safe",
        "patch point by itself; it narrows the candidates for the next manual",
        "disassembly pass.",
        "",
    ]

    for label, path in images.items():
        data = path.read_bytes()
        groups = scan_vfp_groups(data)
        targets = HELPER_TARGETS.get(label, {})
        lines.extend(
            [
                f"## {label}",
                "",
                f"- Path: `{path}`",
                f"- Size: `{len(data)}` bytes",
                f"- SHA256: `{sha256_file(path)}`",
                f"- VFP groups found: `{len(groups)}`",
                "",
                "| Function | VFP insns | Float ops | Top mnemonics | Helper calls | Constants |",
                "|---:|---:|---:|---|---|---|",
            ]
        )

        shown = 0
        for group in groups:
            if group.float_op_count < 4 and len(group.instructions) < 40:
                continue
            constants = pc_vldr_constants(data, group)
            interesting_constants = [
                (address, literal, kind, value)
                for address, literal, kind, value in constants
                if abs(value) in {0.1, 1.5, 2.47, 11.0, 20.0, 21.8, 90.9090909090909, 100.0, 1000.0, 2100.0, 3000.0, 4095.0, 10000.0}
                or 0.000001 <= abs(value) <= 30000.0
            ][:8]
            calls = calls_in_window(data, group.start_offset, 0x500, targets)
            top_mnems = ", ".join(f"{name}:{count}" for name, count in group.mnemonic_counts.most_common(6))
            call_text = ", ".join(f"0x{addr:08x} {name}" for addr, name in calls[:6]) or "-"
            const_text = ", ".join(
                f"0x{addr:08x}->{kind} {format_float(value)}"
                for addr, _literal, kind, value in interesting_constants
            ) or "-"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`0x{group.address:08x}`",
                        f"`{len(group.instructions)}`",
                        f"`{group.float_op_count}`",
                        top_mnems,
                        call_text,
                        const_text,
                    ]
                )
                + " |"
            )
            shown += 1
            if shown >= limit:
                break
        lines.append("")

    lines.extend(
        [
            "## Current Interpretation",
            "",
            "- The V4.0 and Repair-I math candidates are byte-identical except for",
            "  the latency guard offsets and the ammeter acquisition-window byte",
            "  already checked by `dm303_measurement_candidate_gate.py`.",
            "- Several V4.0 functions contain coherent float scaling constants such as",
            "  `2100`, `100`, `4095`, `0.1`, `1.5`, and `21.8`; these are likely",
            "  display/scaling/calibration paths, not confirmed ADC sampling hooks yet.",
            "- No safe zero-deadband, RMS, or oscilloscope filter patch is selected by",
            "  this probe alone. A patch must first prove which function maps to",
            "  voltage AC, current AC, scope, or cranking.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--report", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(DEFAULT_IMAGES, args.limit)
    if args.report is not None:
        args.report.write_text(report + "\n", encoding="utf-8", newline="\n")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
