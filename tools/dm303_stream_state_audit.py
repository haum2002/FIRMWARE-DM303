#!/usr/bin/env python3
"""Audit the DM303 V4.0.1b stream/status state path.

This tool is read-only. It documents the RAM flags and patch bytes around the
measurement stream/status routine so recovery changes remain auditable.
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_MEM


LOAD_BASE = 0x08010000
DEFAULT_IMAGE = Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin")
DEFAULT_REPORT = Path("docs/v401b-stream-state-audit.md")
STATUS_START = 0x080196B2
STATUS_END = 0x080197F4

PATCH_BYTES = {
    0x09570: ("stream read retry", bytes.fromhex("00 bf")),
    0x09706: ("command-0x40 busy failure route", bytes.fromhex("4c d1")),
    0x09758: ("command-0xe9 retry", bytes.fromhex("00 bf")),
    0x097BE: ("mode/status retry", bytes.fromhex("00 bf")),
    0x06A06: ("low byte-IO branch to bounded wrapper", bytes.fromhex("00 f0 23 b8")),
    0x06A50: (
        "bounded low byte-IO wrapper prefix",
        bytes.fromhex("70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0"),
    ),
    0x0967C: ("command-0x40 retry count", bytes.fromhex("60 27")),
    0x09682: ("command-0x48 retry count", bytes.fromhex("60 27")),
    0x09694: ("fallback retry count", bytes.fromhex("0a 27")),
    0x097E6: ("stream error cleanup clears status bits 0 and 1", bytes.fromhex("20 f0 03 00")),
    0x0F19A: ("mode/range entry branch to stale state clear wrapper", bytes.fromhex("1e f0 34 ba")),
    0x2D606: (
        "mode/range wrapper clears status bits 0 and 1",
        bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    ),
}

RAM_ROLE_HINTS = {
    0x20000130: "shared busy/retry countdown word used by command/status recovery",
    0x2000022C: "shared status byte; bit 1 causes early return, bit 0 is cleared on nonzero result",
    0x2000022D: "status/result byte written from r6 at status-path exit",
}

PERIPHERAL_HINTS = {
    0x40011400: "GPIOD control path used during stream/status setup/cleanup",
}


@dataclass(frozen=True)
class LiteralUse:
    address: int
    instruction: str
    literal_address: int
    value: int
    role: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def offset_to_addr(offset: int) -> int:
    return LOAD_BASE + offset


def addr_to_offset(address: int, size: int) -> int | None:
    address &= ~1
    if LOAD_BASE <= address < LOAD_BASE + size:
        return address - LOAD_BASE
    return None


def reg_name(insn, reg_id: int) -> str:
    return insn.reg_name(reg_id) or ""


def role_for(value: int) -> str:
    if value in RAM_ROLE_HINTS:
        return RAM_ROLE_HINTS[value]
    if value in PERIPHERAL_HINTS:
        return PERIPHERAL_HINTS[value]
    if 0x20000000 <= value < 0x20040000:
        return "RAM state/global"
    if 0x40000000 <= value < 0x40024000:
        return "peripheral register base/literal"
    return "literal"


def disassemble_range(data: bytes, start: int, end: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    start_offset = addr_to_offset(start, len(data))
    end_offset = addr_to_offset(end, len(data))
    if start_offset is None or end_offset is None or start_offset >= end_offset:
        raise SystemExit("status range is outside the image")
    return list(md.disasm(data[start_offset:end_offset], start))


def literal_uses(data: bytes, insns) -> list[LiteralUse]:
    rows: list[LiteralUse] = []
    for insn in insns:
        if insn.mnemonic != "ldr" or len(insn.operands) < 2:
            continue
        operand = insn.operands[1]
        if operand.type != ARM_OP_MEM or reg_name(insn, operand.mem.base) != "pc":
            continue
        literal_address = ((insn.address + 4) & ~3) + operand.mem.disp
        literal_offset = addr_to_offset(literal_address, len(data))
        if literal_offset is None or literal_offset + 4 > len(data):
            continue
        value = int.from_bytes(data[literal_offset : literal_offset + 4], "little")
        rows.append(
            LiteralUse(
                address=insn.address,
                instruction=f"{insn.mnemonic} {insn.op_str}",
                literal_address=literal_address,
                value=value,
                role=role_for(value),
            )
        )
    return rows


def format_patch_rows(data: bytes) -> list[str]:
    rows = [
        "| Offset | Address | Expected | Actual | OK | Purpose |",
        "|---:|---:|---|---|---|---|",
    ]
    for offset, (purpose, expected) in PATCH_BYTES.items():
        actual = data[offset : offset + len(expected)]
        rows.append(
            f"| `0x{offset:05x}` | `0x{offset_to_addr(offset):08x}` | "
            f"`{expected.hex(' ')}` | `{actual.hex(' ')}` | `{actual == expected}` | {purpose} |"
        )
    return rows


def format_literal_rows(rows: list[LiteralUse]) -> list[str]:
    output = [
        "| Instruction address | Instruction | Literal address | Literal value | Role |",
        "|---:|---|---:|---:|---|",
    ]
    for row in rows:
        output.append(
            f"| `0x{row.address:08x}` | `{row.instruction}` | "
            f"`0x{row.literal_address:08x}` | `0x{row.value:08x}` | {row.role} |"
        )
    return output


def build_report(image: Path) -> tuple[str, bool]:
    data = image.read_bytes()
    insns = disassemble_range(data, STATUS_START, STATUS_END)
    literals = literal_uses(data, insns)
    patch_ok = all(data[offset : offset + len(expected)] == expected for offset, (_purpose, expected) in PATCH_BYTES.items())
    command_route = data[0x09706:0x09708] == bytes.fromhex("4c d1")
    state_clear = data[0x097E6:0x097EA] == bytes.fromhex("20 f0 03 00")
    mode_state_clear = data[0x0F19A:0x0F19E] == bytes.fromhex("1e f0 34 ba")

    lines = [
        "# DM303 V4.0.1b stream state audit",
        "",
        f"Image: `{image.as_posix()}`",
        f"SHA-256: `{sha256_file(image)}`",
        f"Status-path range: `0x{STATUS_START:08x}`-`0x{STATUS_END:08x}`",
        f"Patch bytes OK: `{patch_ok}`",
        "",
        "## Patch Byte Guard",
        "",
        *format_patch_rows(data),
        "",
        "## State Literals In Status Path",
        "",
        *format_literal_rows(literals),
        "",
        "## Exp13 Recovery Interpretation",
        "",
        "- `0x08019706` is now `bne 0x080197a2`, not a NOP.",
        "- This branch is only taken after command `0x40` fails and the shared",
        "  busy/retry word at `0x20000130` is still nonzero.",
        "- The target block at `0x080197a2` is existing firmware code: it sets",
        "  `r6=2`, selects command `0xe9`, then reaches the normal cleanup and",
        "  status write at `0x080197d4`.",
        "- `0x080197be` remains NOPed, so the existing error/clear path cannot",
        "  spin forever on the same busy flag.",
        "- `0x080197e6` now clears bits `0` and `1` from `0x2000022c` on the",
        "  existing nonzero-result cleanup path. This targets stale busy/status",
        "  after timeout, spike, overload, or failed mode transition without",
        "  clearing the other observed protection/status bits.",
        "- `0x0801f19a` now enters through a guarded wrapper at `0x0803d606`.",
        "  The wrapper preserves the original mode/range prologue, clears the",
        "  same stale bits `0` and `1`, then continues the original relay/range",
        "  switching code. This targets DC/AC/DC blanking before the relay path",
        "  can inherit a stale status state.",
        "- `0x08016a06` now branches to a bounded low byte-IO wrapper. The wrapper",
        "  preserves the SPI1 status/write/read calls but returns `0xff` if a",
        "  ready flag never appears within the `0x0fa0` budget.",
        "- This is still a recovery/state patch, not proof that ADC filtering,",
        "  True RMS math, or analog front-end noise has been solved.",
        "",
    ]
    return "\n".join(lines), patch_ok and command_route and state_clear and mode_state_clear


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, ok = build_report(args.image)
    write_text_lf(args.report, report)
    print(f"stream_state_audit_ok={ok}")
    print(f"image={args.image}")
    print(f"sha256={sha256_file(args.image)}")
    print(f"report={args.report}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
