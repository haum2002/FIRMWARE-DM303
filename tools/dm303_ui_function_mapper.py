#!/usr/bin/env python3
"""Map DM303 UI-heavy firmware functions to TEXT_EN entries and timing constants.

This is a read-only helper for reverse engineering.  It scans selected Thumb
function windows, tracks simple immediate moves into r0/r1/r2/r3, and reports
calls that look like UI text drawing or mode/range transitions.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM, ARM_OP_REG

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dm303_text_resource import parse_text_dat  # noqa: E402


LOAD_BASE = 0x08010000
TEXT_DRAW_TARGETS = {
    0x0801BF84: "draw_text_id",
    0x0801B744: "draw_text_id_v316",
}
HELPER_TARGETS = {
    0x0801F0F2: "relay/range selector",
    0x0801F19A: "mode/range routine",
    0x08019550: "stream/read helper",
    0x08019608: "command/status helper",
}
WATCH_CONSTANTS = {0x40, 0x64, 0xC8, 0xF0, 0x258, 0x536, 0x5DC, 0x640, 0x2710, 0x2EE0, 0x3A98, 0x3E80}
DEFAULT_FUNCTIONS = [
    0x0802600C,
    0x08029F94,
    0x0802D194,
    0x080324FC,
    0x08032DBA,
]


@dataclass(frozen=True)
class FunctionSummary:
    address: int
    text_rows: list[str]
    helper_rows: list[str]
    constant_rows: list[str]


def reg_name(insn, reg_id: int) -> str:
    return insn.reg_name(reg_id) or ""


def imm_from_operand(insn, index: int) -> int | None:
    if len(insn.operands) <= index:
        return None
    operand = insn.operands[index]
    if operand.type != ARM_OP_IMM:
        return None
    return int(operand.imm)


def dest_reg(insn) -> str | None:
    if not insn.operands:
        return None
    operand = insn.operands[0]
    if operand.type != ARM_OP_REG:
        return None
    return reg_name(insn, operand.reg)


def track_immediate(insn, regs: dict[str, int]) -> None:
    dest = dest_reg(insn)
    if dest is None:
        return
    imm = None
    if insn.mnemonic in {"movs", "mov.w", "movw"}:
        imm = imm_from_operand(insn, 1)
    if imm is None:
        regs.pop(dest, None)
        return
    regs[dest] = imm


def call_target(insn) -> int | None:
    if not insn.mnemonic.startswith("bl"):
        return None
    for operand in insn.operands:
        if operand.type == ARM_OP_IMM:
            return int(operand.imm) & ~1
    return None


def summarize_function(data: bytes, address: int, size: int, texts: dict[int, str]) -> FunctionSummary:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    regs: dict[str, int] = {}
    text_rows: list[str] = []
    helper_rows: list[str] = []
    constant_rows: list[str] = []
    start = address - LOAD_BASE
    for insn in md.disasm(data[start : start + size], address):
        track_immediate(insn, regs)
        target = call_target(insn)
        if target in TEXT_DRAW_TARGETS:
            index = regs.get("r0")
            text = texts.get(index, "") if index is not None else ""
            text_rows.append(f"0x{insn.address:08x}: {TEXT_DRAW_TARGETS[target]} r0={index} {text!r}")
        elif target in HELPER_TARGETS:
            helper_rows.append(f"0x{insn.address:08x}: {HELPER_TARGETS[target]}")

        if insn.mnemonic in {"movs", "mov.w", "movw", "cmp", "cmp.w"}:
            for operand in insn.operands:
                if operand.type == ARM_OP_IMM and int(operand.imm) in WATCH_CONSTANTS:
                    constant_rows.append(f"0x{insn.address:08x}: {insn.mnemonic} {insn.op_str}")
                    break

    return FunctionSummary(address, text_rows, helper_rows, constant_rows)


def parse_functions(values: list[str]) -> list[int]:
    if not values:
        return DEFAULT_FUNCTIONS
    return [int(value, 0) for value in values]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=Path("backup/DM303 V4.0-read only/DM303V4.004.bin"))
    parser.add_argument("--text", type=Path, default=Path("backup/DM303 V4.0-read only/system/TEXT_EN.DAT"))
    parser.add_argument("--function", action="append", default=[])
    parser.add_argument("--size", type=lambda value: int(value, 0), default=0x700)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    data = args.image.read_bytes()
    _, _, entries = parse_text_dat(args.text)
    texts = {entry.index: entry.text for entry in entries}
    summaries = [summarize_function(data, address, args.size, texts) for address in parse_functions(args.function)]

    lines: list[str] = [
        "# DM303 UI function mapper",
        "",
        f"- Image: `{args.image}`",
        f"- Text: `{args.text}`",
        "",
    ]
    for summary in summaries:
        lines.extend([f"## 0x{summary.address:08x}", ""])
        lines.extend(["### Text calls", ""])
        lines.extend(f"- {row}" for row in summary.text_rows or ["none"])
        lines.extend(["", "### Helper calls", ""])
        lines.extend(f"- {row}" for row in summary.helper_rows or ["none"])
        lines.extend(["", "### Watched constants", ""])
        lines.extend(f"- {row}" for row in summary.constant_rows or ["none"])
        lines.append("")

    output = "\n".join(lines)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8", newline="\n")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
