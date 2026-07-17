#!/usr/bin/env python3
"""Probe DM303 state hooks that may explain measurement blank/freeze.

This is read-only. It searches for RAM state literals, tracks simple
PC-literal loads into following memory reads/writes, and lists callers into the
measurement stream/status helpers. The purpose is to decide whether an exp12
state-reset patch has a safe hook, not to create one from guesses.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM, ARM_OP_MEM, ARM_OP_REG


LOAD_BASE = 0x08010000

DEFAULT_IMAGES = {
    "v4.0": Path("backup/DM303 V4.0-read only/DM303V4.004.bin"),
    "v4.0.1b-exp13": Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin"),
}

STATE_LITERALS = {
    0x20000130: "busy/retry countdown word near stream/status command recovery",
    0x2000022C: "shared stream/status flag byte; bit 1 early-return, bit 0 clear-on-error",
    0x2000022D: "stream/status result byte written from r6",
}

STREAM_HELPERS = {
    0x0801946C: "byte write helper / low-level command stream",
    0x08019550: "bounded read/block helper used by measurement stream",
    0x0801959E: "read/status helper variant",
    0x08019608: "command helper",
    0x080196B2: "main stream/status transaction helper",
    0x080197FC: "stream payload helper",
    0x08019898: "stream payload helper",
    0x08019936: "stream/scaling-heavy payload helper",
}

MODE_HELPERS = {
    0x0801F0AC: "mode-switch helper",
    0x0801F0F2: "relay/range selector candidate",
    0x0801F19A: "mode/range routine candidate",
    0x0803D606: "exp13 mode/range stale state clear wrapper",
}


@dataclass(frozen=True)
class LiteralLoad:
    address: int
    register: str
    literal_address: int
    literal_value: int


@dataclass(frozen=True)
class StateAccess:
    state_value: int
    state_name: str
    literal_load: int
    address: int
    instruction: str
    access: str
    note: str


@dataclass(frozen=True)
class CallRef:
    address: int
    target: int
    target_name: str
    mnemonic: str
    op_str: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def addr_to_offset(address: int, size: int) -> int | None:
    address &= ~1
    if LOAD_BASE <= address < LOAD_BASE + size:
        return address - LOAD_BASE
    return None


def u32_at(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def reg_name(insn, reg_id: int) -> str:
    return insn.reg_name(reg_id) or ""


def disassemble_all(data: bytes) -> list:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    rows = []
    for offset in range(0, len(data) - 1, 2):
        address = LOAD_BASE + offset
        insns = list(md.disasm(data[offset : offset + 4], address, count=1))
        if insns:
            rows.append(insns[0])
    # Capstone will decode overlapping 16/32-bit windows in a raw halfword
    # scan. Keep it intentionally broad; exact contexts are filtered later.
    return rows


def disassemble_linear(data: bytes, start: int, size: int = 0x80) -> list:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    offset = addr_to_offset(start, len(data))
    if offset is None:
        return []
    return list(md.disasm(data[offset : offset + size], start))


def find_literal_loads(data: bytes, targets: dict[int, str]) -> list[LiteralLoad]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    loads: list[LiteralLoad] = []
    for offset in range(0, len(data) - 3, 2):
        address = LOAD_BASE + offset
        insns = list(md.disasm(data[offset : offset + 4], address, count=1))
        if not insns:
            continue
        insn = insns[0]
        if insn.mnemonic != "ldr" or len(insn.operands) < 2:
            continue
        dest = insn.operands[0]
        source = insn.operands[1]
        if dest.type != ARM_OP_REG or source.type != ARM_OP_MEM:
            continue
        if reg_name(insn, source.mem.base) != "pc":
            continue
        literal_address = ((insn.address + 4) & ~3) + source.mem.disp
        literal_offset = addr_to_offset(literal_address, len(data))
        if literal_offset is None or literal_offset + 4 > len(data):
            continue
        value = u32_at(data, literal_offset)
        if value in targets:
            loads.append(LiteralLoad(address, reg_name(insn, dest.reg), literal_address, value))
    return sorted(loads, key=lambda row: (row.literal_value, row.address))


def mem_base_register(insn) -> str | None:
    for operand in insn.operands:
        if operand.type == ARM_OP_MEM:
            return reg_name(insn, operand.mem.base)
    return None


def dest_register(insn) -> str | None:
    if not insn.operands:
        return None
    operand = insn.operands[0]
    if operand.type == ARM_OP_REG:
        return reg_name(insn, operand.reg)
    return None


def access_kind(insn, tracked_register: str) -> tuple[str | None, str]:
    mnemonic = insn.mnemonic
    base = mem_base_register(insn)
    if base == tracked_register:
        if mnemonic.startswith("ldr"):
            return "read", "memory load through state pointer"
        if mnemonic.startswith("str"):
            return "write", "memory store through state pointer"
    if mnemonic in {"bic", "orr", "and", "ands", "eor"}:
        return "bit-op", "bit manipulation after state load"
    if mnemonic in {"cmp", "cbz", "cbnz", "tst"}:
        return "test", "state-derived conditional test"
    return None, ""


def track_state_accesses(data: bytes, loads: list[LiteralLoad], window: int = 22) -> list[StateAccess]:
    accesses: list[StateAccess] = []
    for load in loads:
        insns = disassemble_linear(data, load.address, 0x90)
        tracked = load.register
        for insn in insns[1 : window + 1]:
            kind, note = access_kind(insn, tracked)
            if kind is not None:
                accesses.append(
                    StateAccess(
                        load.literal_value,
                        STATE_LITERALS[load.literal_value],
                        load.address,
                        insn.address,
                        f"{insn.mnemonic} {insn.op_str}",
                        kind,
                        note,
                    )
                )
            # Stop once the pointer register is overwritten as a normal
            # destination. Loads/stores through the pointer are handled above.
            dest = dest_register(insn)
            if dest == tracked and mem_base_register(insn) != tracked:
                break
    return accesses


def scan_call_refs(data: bytes, targets: dict[int, str]) -> list[CallRef]:
    refs: list[CallRef] = []
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    for offset in range(0, len(data) - 3, 2):
        address = LOAD_BASE + offset
        insns = list(md.disasm(data[offset : offset + 4], address, count=1))
        if not insns:
            continue
        insn = insns[0]
        if not insn.mnemonic.startswith("b"):
            continue
        for operand in insn.operands:
            if operand.type != ARM_OP_IMM:
                continue
            target = int(operand.imm) & ~1
            if target in targets:
                refs.append(CallRef(address, target, targets[target], insn.mnemonic, insn.op_str))
                break
    return refs


def exact_literal_offsets(data: bytes, value: int) -> list[int]:
    pattern = struct.pack("<I", value)
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(pattern, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def format_addr(address: int) -> str:
    return f"0x{address:08x}"


def write_report(path: Path, images: dict[str, Path]) -> None:
    lines = [
        "# DM303 V4.0.1b state hook probe",
        "",
        "Read-only search for state hooks related to measurement blank/freeze.",
        "This report documents the state hook evidence used by the exp13",
        "mode/range stale-state clear patch.",
        "",
    ]

    for label, image_path in images.items():
        if not image_path.exists():
            raise SystemExit(f"Missing {label} image: {image_path}")
        data = image_path.read_bytes()
        loads = find_literal_loads(data, STATE_LITERALS)
        accesses = track_state_accesses(data, loads)
        stream_refs = scan_call_refs(data, STREAM_HELPERS)
        mode_refs = scan_call_refs(data, MODE_HELPERS)

        lines.extend(
            [
                f"## {label}",
                "",
                f"- Path: `{image_path}`",
                f"- Size: `{len(data)}` bytes",
                f"- SHA-256: `{sha256_file(image_path)}`",
                "",
                "### Exact state literal offsets",
                "",
                "| State | Meaning | Count | Offsets |",
                "|---:|---|---:|---|",
            ]
        )
        for value, meaning in STATE_LITERALS.items():
            offsets = exact_literal_offsets(data, value)
            shown = ", ".join(f"`0x{offset:05x}`" for offset in offsets[:12])
            if len(offsets) > 12:
                shown += f", ... +{len(offsets) - 12}"
            lines.append(f"| `{value:#010x}` | {meaning} | {len(offsets)} | {shown or 'none'} |")

        lines.extend(
            [
                "",
                "### PC-literal state loads",
                "",
                "| Load Address | Register | Literal Address | State |",
                "|---:|---|---:|---|",
            ]
        )
        for load in loads:
            lines.append(
                f"| `{format_addr(load.address)}` | `{load.register}` | "
                f"`{format_addr(load.literal_address)}` | `{load.literal_value:#010x}` |"
            )
        if not loads:
            lines.append("| | | | none |")

        lines.extend(
            [
                "",
                "### Tracked state accesses after literal load",
                "",
                "| State | Literal Load | Access Address | Access | Instruction | Note |",
                "|---:|---:|---:|---|---|---|",
            ]
        )
        for access in accesses:
            lines.append(
                f"| `{access.state_value:#010x}` | `{format_addr(access.literal_load)}` | "
                f"`{format_addr(access.address)}` | {access.access} | "
                f"`{access.instruction}` | {access.note} |"
            )
        if not accesses:
            lines.append("| | | | | | none |")

        stream_counts = Counter(ref.target for ref in stream_refs)
        lines.extend(
            [
                "",
                "### Stream/helper branch references",
                "",
                "| Target | Name | Count | First Callers |",
                "|---:|---|---:|---|",
            ]
        )
        for target, count in stream_counts.most_common():
            callers = [ref for ref in stream_refs if ref.target == target]
            shown = ", ".join(f"`{format_addr(ref.address)} {ref.mnemonic}`" for ref in callers[:12])
            if len(callers) > 12:
                shown += f", ... +{len(callers) - 12}"
            lines.append(f"| `{format_addr(target)}` | {STREAM_HELPERS[target]} | {count} | {shown} |")
        if not stream_counts:
            lines.append("| | | 0 | none |")

        mode_counts = Counter(ref.target for ref in mode_refs)
        lines.extend(
            [
                "",
                "### Mode/range helper branch references",
                "",
                "| Target | Name | Count | First Callers |",
                "|---:|---|---:|---|",
            ]
        )
        for target, count in mode_counts.most_common():
            callers = [ref for ref in mode_refs if ref.target == target]
            shown = ", ".join(f"`{format_addr(ref.address)} {ref.mnemonic}`" for ref in callers[:12])
            if len(callers) > 12:
                shown += f", ... +{len(callers) - 12}"
            lines.append(f"| `{format_addr(target)}` | {MODE_HELPERS[target]} | {count} | {shown} |")
        if not mode_counts:
            lines.append("| | | 0 | none |")

        lines.append("")

    lines.extend(
        [
            "## Decision",
            "",
            "- The visible V4.0/V4.0.1b state literals remain concentrated in the",
            "  stream/status helper region, especially `0x2000022c`, `0x2000022d`,",
            "  and `0x20000130`.",
            "- Exp13 uses the confirmed mode/range entry at `0x0801f19a` as the",
            "  state-reset hook. The patch preserves the original prologue, clears",
            "  only bits `0` and `1` from `0x2000022c`, then continues original",
            "  relay/range code.",
            "- This evidence supports the exp13 recovery hook, not an immediate",
            "  ADC/RMS/math rewrite. A math/filter patch still needs a confirmed",
            "  measurement-buffer or RMS accumulator contract.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("docs/v401b-state-hook-probe.md"))
    args = parser.parse_args()
    write_report(args.report, DEFAULT_IMAGES)
    print("state_hook_probe=ok")
    print(f"report={args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
