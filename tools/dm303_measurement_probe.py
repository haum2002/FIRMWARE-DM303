#!/usr/bin/env python3
"""Probe DM303 firmware for measurement/noise related evidence.

This tool is read-only. It does not patch firmware. It collects UI text clues,
peripheral literal hits, and candidate low-level code areas that may relate to
measurement acquisition, mode switching, timers, GPIO, or output drive.
"""

from __future__ import annotations

import argparse
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM, ARM_OP_MEM

from dm303_text_resource import parse_text_dat
from dm303_v4_static_analysis import (
    LOAD_BASE,
    addr_to_offset,
    read_vectors,
    thumb_entries_from_vectors,
    thumb_walk,
)


DEFAULT_IMAGE = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
DEFAULT_TEXT = Path("backup/DM303 V4.0-read only/system/TEXT_EN.DAT")

KEYWORDS = (
    "zero",
    "calib",
    "voltage",
    "current",
    "oscillo",
    "waveform",
    "rms",
    "ac",
    "dc",
    "hold",
    "injector",
    "fuel",
    "frequency",
    "range",
    "f1",
    "fn",
)

PERIPHERAL_BASES = [
    (0x40000000, "TIM2"),
    (0x40000400, "TIM3"),
    (0x40000800, "TIM4"),
    (0x40000C00, "TIM5"),
    (0x40001000, "TIM6"),
    (0x40001400, "TIM7"),
    (0x40003800, "SPI2"),
    (0x40003C00, "SPI3"),
    (0x40004400, "USART2"),
    (0x40004800, "USART3"),
    (0x40004C00, "UART4"),
    (0x40005000, "UART5"),
    (0x40005400, "I2C1"),
    (0x40005800, "I2C2"),
    (0x40006400, "CAN1"),
    (0x40010000, "AFIO"),
    (0x40010400, "EXTI"),
    (0x40010800, "GPIOA"),
    (0x40010C00, "GPIOB"),
    (0x40011000, "GPIOC"),
    (0x40011400, "GPIOD"),
    (0x40011800, "GPIOE"),
    (0x40012400, "ADC1"),
    (0x40012800, "ADC2"),
    (0x40012C00, "TIM1"),
    (0x40013000, "SPI1"),
    (0x40013400, "TIM8"),
    (0x40013800, "USART1"),
    (0x40013C00, "ADC3"),
    (0x40020000, "DMA1"),
    (0x40020400, "DMA2"),
    (0x40021000, "RCC"),
    (0x40022000, "FLASH"),
    (0xE000E010, "SysTick"),
    (0xE000ED00, "SCB"),
]

WATCH_OFFSETS = [
    0x07BC4,
    0x07C26,
    0x07D32,
    0x07E90,
    0x08B56,
    0x08BCA,
]

RELAY_SELECTOR_ADDR = 0x0801F0F2
RELAY_MODE_ROUTINE_ADDR = 0x0801F19A
RELAY_SETTLE_DELAYS = [
    (0x0F10A, 2, 5, "pre-switch settle before selector bits are changed"),
    (0x0F146, 3, 8, "selector bit settle after relay/range bits are changed"),
    (0x0F192, 10, 50, "final post-relay settle before returning to acquisition"),
]

RELAY_HELPER_TARGETS = {
    RELAY_SELECTOR_ADDR: "relay/range selector candidate",
    0x08039396: "GPIO set",
    0x0803939E: "GPIO reset",
    0x08017AC2: "timer delay A",
    0x08017AD4: "timer delay B",
}


def safe_text(value: str) -> str:
    return value.encode("ascii", "backslashreplace").decode("ascii")


def peripheral_name(value: int) -> str | None:
    if not (0x40000000 <= value <= 0x40023FFF or 0xE000E000 <= value <= 0xE000EFFF):
        return None
    for base, name in PERIPHERAL_BASES:
        span = 0x100 if base >= 0xE0000000 else 0x400
        if base <= value < base + span:
            return f"{name}+0x{value - base:x}"
    return f"PERIPH 0x{value:08x}"


def print_text_clues(path: Path) -> None:
    _, count, entries = parse_text_dat(path)
    print("Measurement text clues")
    print(f"  text={path} entries={count}")
    for entry in entries:
        text_lower = entry.text.lower()
        if any(keyword in text_lower for keyword in KEYWORDS):
            print(f"  {entry.index:04d} len={entry.record_length:02d} {safe_text(entry.text)}")


def print_exact_peripheral_hits(image: Path, buf: bytes) -> None:
    print()
    print("Exact peripheral literal hits")
    print(f"  image={image}")
    for base, name in PERIPHERAL_BASES:
        pattern = struct.pack("<I", base)
        offsets: list[int] = []
        start = 0
        while True:
            offset = buf.find(pattern, start)
            if offset < 0:
                break
            offsets.append(offset)
            start = offset + 1
        if offsets:
            shown = ", ".join(f"0x{offset:05x}" for offset in offsets[:10])
            suffix = "" if len(offsets) <= 10 else f", ... +{len(offsets) - 10}"
            print(f"  {name:7s} 0x{base:08x} hits={len(offsets):2d} offs={shown}{suffix}")


def reg_name(insn, reg_id: int) -> str:
    return insn.reg_name(reg_id) or ""


def nearest_function(starts: list[int], address: int) -> int | None:
    low = 0
    high = len(starts)
    while low < high:
        middle = (low + high) // 2
        if starts[middle] <= address:
            low = middle + 1
        else:
            high = middle
    return starts[low - 1] if low else None


def print_candidate_code_paths(buf: bytes) -> None:
    vectors = read_vectors(buf)
    entries = thumb_entries_from_vectors(vectors)
    functions, seen = thumb_walk(buf, entries, limit=500_000)
    starts = sorted(functions)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    hits: list[tuple[int | None, int, str]] = []

    for address in sorted(seen):
        offset = addr_to_offset(address, len(buf))
        if offset is None:
            continue
        insns = list(md.disasm(buf[offset : offset + 4], address, count=1))
        if not insns:
            continue
        insn = insns[0]
        if insn.mnemonic.lower() != "ldr" or len(insn.operands) < 2:
            continue
        mem = insn.operands[1]
        if mem.type != ARM_OP_MEM or reg_name(insn, mem.mem.base) != "pc":
            continue
        literal_addr = ((insn.address + 4) & ~3) + mem.mem.disp
        literal_offset = addr_to_offset(literal_addr, len(buf))
        if literal_offset is None or literal_offset + 4 > len(buf):
            continue
        literal_value = struct.unpack_from("<I", buf, literal_offset)[0]
        name = peripheral_name(literal_value)
        if name is not None:
            hits.append((nearest_function(starts, address), address, name))

    by_function: dict[int | None, list[tuple[int | None, int, str]]] = defaultdict(list)
    for hit in hits:
        by_function[hit[0]].append(hit)

    print()
    print("Candidate peripheral code paths")
    print(f"  functions={len(functions)} seen_instructions={len(seen)}")
    for function, items in sorted(by_function.items(), key=lambda item: (len(item[1]), item[0] or 0), reverse=True)[:40]:
        if function is None:
            continue
        names = Counter(name.split("+")[0] for _, _, name in items)
        print(f"  func=0x{function:08x} off=0x{function - LOAD_BASE:05x} hits={len(items)} peripherals={dict(names)}")

    print()
    print("Manual-watch candidate offsets")
    for offset in WATCH_OFFSETS:
        print(f"  off=0x{offset:05x} addr=0x{LOAD_BASE + offset:08x}")


def disassemble_one(buf: bytes, address: int):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    offset = addr_to_offset(address, len(buf))
    if offset is None:
        return None
    insns = list(md.disasm(buf[offset : offset + 4], address, count=1))
    return insns[0] if insns else None


def find_bl_calls(buf: bytes, target: int) -> list[int]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    calls: list[int] = []
    for offset in range(0, len(buf) - 4, 2):
        address = LOAD_BASE + offset
        insns = list(md.disasm(buf[offset : offset + 4], address, count=1))
        if not insns:
            continue
        insn = insns[0]
        if not insn.mnemonic.startswith("bl"):
            continue
        if not insn.operands or insn.operands[0].type != ARM_OP_IMM:
            continue
        if (insn.operands[0].imm & ~1) == target:
            calls.append(address)
    return calls


def print_relay_settle_evidence(buf: bytes) -> None:
    print()
    print("Relay/range settling candidate")
    print(
        f"  selector=0x{RELAY_SELECTOR_ADDR:08x} "
        f"mode_routine=0x{RELAY_MODE_ROUTINE_ADDR:08x}"
    )
    print("  evidence: selector toggles GPIOB/GPIOD bits and already contains timer waits")
    print("  note: this is a relay/range candidate, not a proven analog accuracy fix")
    print("  official delay bytes:")
    for offset, old_ticks, new_ticks, reason in RELAY_SETTLE_DELAYS:
        address = LOAD_BASE + offset
        insn = disassemble_one(buf, address)
        if insn is None:
            print(f"    off=0x{offset:05x} addr=0x{address:08x} undecoded")
            continue
        print(
            f"    off=0x{offset:05x} addr=0x{address:08x} "
            f"{insn.bytes.hex(' ')} {insn.mnemonic} {insn.op_str} "
            f"official={old_ticks} patched={new_ticks} - {reason}"
        )

    selector_calls = find_bl_calls(buf, RELAY_SELECTOR_ADDR)
    print(f"  calls to selector: {len(selector_calls)}")
    for address in selector_calls[:24]:
        marker = " mode routine" if RELAY_MODE_ROUTINE_ADDR <= address < RELAY_MODE_ROUTINE_ADDR + 0x180 else ""
        print(f"    0x{address:08x}{marker}")
    if len(selector_calls) > 24:
        print(f"    ... {len(selector_calls) - 24} more")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--text", type=Path, default=DEFAULT_TEXT)
    args = parser.parse_args(argv)

    buf = args.image.read_bytes()
    print_text_clues(args.text)
    print_exact_peripheral_hits(args.image, buf)
    print_candidate_code_paths(buf)
    print_relay_settle_evidence(buf)
    print()
    print("Safety note")
    print("  This tool is read-only and does not identify confirmed safe patch points.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
