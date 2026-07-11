#!/usr/bin/env python3
"""Static analysis helper for the supplied AUTOOL DM303 V4.0 firmware.

This tool is intentionally read-only. It never writes a patched firmware image.
It exists to make the first upgrade step repeatable before any v4.0.1 beta
binary is generated.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path

try:
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    from capstone.arm_const import ARM_OP_IMM, ARM_OP_REG
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(
        "Missing dependency: capstone. Install with "
        "`python -m pip install -r tools/requirements-analysis.txt`."
    ) from exc


DEFAULT_IMAGE = Path("DM303-V4.0/DM303V4.004.bin")
LOAD_BASE = 0x08010000
RAM_START = 0x20000000
RAM_END = 0x20040000
VECTOR_WORDS = 80

CORE_VECTOR_NAMES = [
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

PERIPHERAL_BASES = {
    0x40000000: "TIM2",
    0x40000400: "TIM3",
    0x40000800: "TIM4",
    0x40000C00: "TIM5",
    0x40001000: "TIM6",
    0x40001400: "TIM7",
    0x40002C00: "WWDG",
    0x40003000: "IWDG",
    0x40003800: "SPI2/I2S2",
    0x40003C00: "SPI3/I2S3",
    0x40004400: "USART2",
    0x40004800: "USART3",
    0x40004C00: "UART4",
    0x40005000: "UART5",
    0x40005400: "I2C1",
    0x40005800: "I2C2",
    0x40005C00: "USB/CAN SRAM",
    0x40006400: "CAN1",
    0x40006C00: "BKP",
    0x40007000: "PWR",
    0x40010000: "AFIO",
    0x40010400: "EXTI",
    0x40010800: "GPIOA",
    0x40010C00: "GPIOB",
    0x40011000: "GPIOC",
    0x40011400: "GPIOD",
    0x40011800: "GPIOE",
    0x40011C00: "GPIOF",
    0x40012000: "GPIOG",
    0x40012400: "ADC1",
    0x40012800: "ADC2",
    0x40012C00: "TIM1",
    0x40013000: "SPI1",
    0x40013400: "TIM8",
    0x40013800: "USART1",
    0x40013C00: "ADC3",
    0x40020000: "DMA1",
    0x40020400: "DMA2",
    0x40021000: "RCC",
    0x40022000: "FLASH",
    0x40023000: "CRC",
    0xE000E010: "SysTick",
    0xE000ED00: "SCB",
    0xE000ED08: "SCB_VTOR",
    0xE000ED0C: "SCB_AIRCR",
}

RESET_WATCHDOG_LITERALS = {
    0x40002C00: "WWDG base",
    0x40003000: "IWDG base",
    0xE000ED0C: "SCB AIRCR",
    0x05FA0000: "AIRCR VECTKEY",
    0x05FA0004: "AIRCR SYSRESETREQ value",
}


@dataclass(frozen=True)
class VectorEntry:
    index: int
    name: str
    value: int
    offset: int | None
    bytes2: bytes | None


def u32_at(buf: bytes, offset: int) -> int:
    return struct.unpack_from("<I", buf, offset)[0]


def addr_to_offset(addr: int, image_size: int) -> int | None:
    addr = addr & ~1
    if LOAD_BASE <= addr < LOAD_BASE + image_size:
        return addr - LOAD_BASE
    return None


def offset_to_addr(offset: int) -> int:
    return LOAD_BASE + offset


def is_ram_addr(addr: int) -> bool:
    return RAM_START <= addr < RAM_END


def name_for_vector(index: int) -> str:
    if index < len(CORE_VECTOR_NAMES):
        return CORE_VECTOR_NAMES[index]
    return f"irq{index - 16}"


def read_vectors(buf: bytes) -> list[VectorEntry]:
    entries: list[VectorEntry] = []
    max_words = min(VECTOR_WORDS, len(buf) // 4)
    for index in range(max_words):
        value = u32_at(buf, index * 4)
        offset = addr_to_offset(value, len(buf))
        bytes2 = None
        if offset is not None and offset + 2 <= len(buf):
            bytes2 = buf[offset : offset + 2]
        entries.append(VectorEntry(index, name_for_vector(index), value, offset, bytes2))
    return entries


def thumb_entries_from_vectors(vectors: list[VectorEntry]) -> list[int]:
    entries: list[int] = []
    for vector in vectors[1:]:
        if vector.offset is None:
            continue
        if vector.value & 1:
            entries.append(vector.value & ~1)
    return sorted(set(entries))


def extract_ascii_strings(buf: bytes, min_len: int = 6) -> list[tuple[int, str]]:
    strings: list[tuple[int, str]] = []
    start = None
    for index, byte in enumerate(buf + b"\x00"):
        printable = 0x20 <= byte <= 0x7E
        if printable and start is None:
            start = index
        elif not printable and start is not None:
            if index - start >= min_len:
                strings.append((start, buf[start:index].decode("ascii", "replace")))
            start = None
    return strings


def version_like_strings(strings: list[tuple[int, str]]) -> list[tuple[int, str]]:
    pattern = re.compile(r"(DM303|DM30|V\d|ver|version|beta|BT100|MT100)", re.IGNORECASE)
    return [(offset, text) for offset, text in strings if pattern.search(text)]


def find_runs(buf: bytes, byte_value: int, min_len: int = 16) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    index = 0
    target = bytes([byte_value])
    while index < len(buf):
        if buf[index : index + 1] != target:
            index += 1
            continue
        start = index
        while index < len(buf) and buf[index : index + 1] == target:
            index += 1
        length = index - start
        if length >= min_len:
            runs.append((start, length))
    return sorted(runs, key=lambda item: item[1], reverse=True)


def scan_u32_literals(buf: bytes) -> Counter[int]:
    counts: Counter[int] = Counter()
    for offset in range(0, len(buf) - 3, 4):
        counts[u32_at(buf, offset)] += 1
    return counts


def peripheral_name(value: int) -> str | None:
    if 0x40000000 <= value <= 0x40023FFF or 0xE000E000 <= value <= 0xE000EFFF:
        for base, name in PERIPHERAL_BASES.items():
            span = 0x100 if base >= 0xE0000000 else 0x400
            if base <= value < base + span:
                return name
        return "peripheral/reserved"
    return None


def scan_peripheral_literals(counts: Counter[int]) -> Counter[str]:
    result: Counter[str] = Counter()
    for value, count in counts.items():
        name = peripheral_name(value)
        if name is not None:
            result[f"{name} 0x{value:08x}"] += count
    return result


def reg_name(insn, reg_id: int) -> str:
    try:
        return insn.reg_name(reg_id) or ""
    except Exception:
        return ""


def first_op_is_pc(insn) -> bool:
    if not insn.operands:
        return False
    op = insn.operands[0]
    return op.type == ARM_OP_REG and reg_name(insn, op.reg) == "pc"


def operands_include_pc(insn) -> bool:
    for op in insn.operands:
        if op.type == ARM_OP_REG and reg_name(insn, op.reg) == "pc":
            return True
    return False


def immediate_targets(insn, image_size: int) -> list[int]:
    targets: list[int] = []
    for op in insn.operands:
        if op.type != ARM_OP_IMM:
            continue
        target = op.imm & ~1
        if addr_to_offset(target, image_size) is not None:
            targets.append(target)
    return targets


def thumb_walk(buf: bytes, entry_points: list[int], limit: int = 200_000) -> tuple[set[int], set[int]]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True

    queue: deque[int] = deque(entry_points)
    function_starts: set[int] = set()
    seen_instructions: set[int] = set()

    while queue and len(seen_instructions) < limit:
        start = queue.popleft() & ~1
        offset = addr_to_offset(start, len(buf))
        if offset is None:
            continue
        if start in function_starts:
            continue
        function_starts.add(start)

        addr = start
        while len(seen_instructions) < limit:
            offset = addr_to_offset(addr, len(buf))
            if offset is None or addr in seen_instructions:
                break

            insns = list(md.disasm(buf[offset : offset + 4], addr, count=1))
            if not insns:
                break
            insn = insns[0]
            seen_instructions.add(addr)

            mnemonic = insn.mnemonic.lower()
            targets = immediate_targets(insn, len(buf))
            for target in targets:
                if target not in function_starts:
                    queue.append(target)

            next_addr = addr + insn.size
            stop = False

            if mnemonic in {"b", "b.w"}:
                stop = True
            elif mnemonic == "bx" and any(
                op.type == ARM_OP_REG and reg_name(insn, op.reg) == "lr"
                for op in insn.operands
            ):
                stop = True
            elif mnemonic == "pop" and operands_include_pc(insn):
                stop = True
            elif mnemonic == "ldr" and first_op_is_pc(insn):
                stop = True
            elif mnemonic in {"udf", "bkpt"}:
                stop = True
            elif targets and len(targets) == 1 and targets[0] == addr:
                stop = True

            if stop:
                break
            addr = next_addr

    return function_starts, seen_instructions


def print_vector_summary(vectors: list[VectorEntry]) -> None:
    print("Vector table (selected)")
    for vector in vectors[:32]:
        if vector.index == 0:
            location = "ram" if is_ram_addr(vector.value) else "unknown"
        elif vector.offset is not None:
            location = f"off 0x{vector.offset:05x}"
        else:
            location = "not in image"
        loop = ""
        if vector.bytes2 == b"\xfe\xe7":
            loop = " self-loop"
        print(f"  {vector.index:02d} {vector.name:12s} 0x{vector.value:08x} {location}{loop}")

    loops = [v for v in vectors if v.bytes2 == b"\xfe\xe7"]
    print()
    print("Default/self-loop handlers")
    if not loops:
        print("  none detected at vector targets")
        return
    for vector in loops:
        print(f"  {vector.name:12s} vector {vector.index:02d} -> off 0x{vector.offset:05x}")


def print_literal_summary(buf: bytes) -> None:
    counts = scan_u32_literals(buf)

    print()
    print("Watchdog/reset related literal hits")
    for value, label in RESET_WATCHDOG_LITERALS.items():
        print(f"  0x{value:08x} {label:24s}: {counts[value]}")

    print()
    print("Peripheral-range literal-like words (top 24)")
    print("  note: raw 32-bit words in this range are clues, not proof of access")
    peripheral_counts = scan_peripheral_literals(counts)
    if not peripheral_counts:
        print("  none")
        return
    for label, count in peripheral_counts.most_common(24):
        print(f"  {count:3d} {label}")


def print_string_summary(buf: bytes) -> None:
    strings = extract_ascii_strings(buf)
    matches = version_like_strings(strings)

    print()
    print("Version/device-like ASCII strings")
    if not matches:
        print("  none")
        return
    for offset, text in matches[:24]:
        print(f"  off 0x{offset:05x}: {text}")


def print_run_summary(buf: bytes) -> None:
    print()
    print("Potential free-space runs (warning: not automatically safe code caves)")
    ff_runs = find_runs(buf, 0xFF)
    zero_runs = find_runs(buf, 0x00)
    print("  0xff runs >=16 bytes:")
    if ff_runs:
        for offset, length in ff_runs[:8]:
            print(f"    off 0x{offset:05x}, len {length}")
    else:
        print("    none")
    print("  0x00 runs >=16 bytes:")
    if zero_runs:
        for offset, length in zero_runs[:12]:
            print(f"    off 0x{offset:05x}, len {length}")
    else:
        print("    none")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--no-walk", action="store_true", help="skip recursive Thumb walk")
    args = parser.parse_args(argv)

    buf = args.image.read_bytes()
    digest = hashlib.sha256(buf).hexdigest()

    print("DM303 V4.0 internal static analysis")
    print(f"Image: {args.image}")
    print(f"Size: {len(buf)} bytes / 0x{len(buf):x}")
    print(f"SHA256: {digest}")
    print(f"Assumed load base: 0x{LOAD_BASE:08x}")
    print()

    vectors = read_vectors(buf)
    initial_sp = vectors[0].value if vectors else 0
    reset = vectors[1].value if len(vectors) > 1 else 0
    print(f"Initial SP: 0x{initial_sp:08x} ({'RAM-like' if is_ram_addr(initial_sp) else 'unexpected'})")
    reset_offset = addr_to_offset(reset, len(buf))
    if reset_offset is None:
        print(f"Reset vector: 0x{reset:08x} (not inside image)")
    else:
        print(f"Reset vector: 0x{reset:08x} -> off 0x{reset_offset:05x}")
    print()

    print_vector_summary(vectors)
    print_string_summary(buf)
    print_literal_summary(buf)
    print_run_summary(buf)

    if not args.no_walk:
        entry_points = thumb_entries_from_vectors(vectors)
        functions, instructions = thumb_walk(buf, entry_points)
        print()
        print("Recursive Thumb walk")
        print(f"  entry points from vectors: {len(entry_points)}")
        print(f"  discovered function starts: {len(functions)}")
        print(f"  decoded instruction addresses: {len(instructions)}")
        print("  note: this is static guidance only, not a full decompilation")

    print()
    print("Safety note")
    print("  This script does not create a firmware image and must not be treated as")
    print("  a flashable v4.0.1 beta patch.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
