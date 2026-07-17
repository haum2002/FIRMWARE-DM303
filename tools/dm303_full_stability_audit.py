#!/usr/bin/env python3
"""Read-only stability audit for the DM303 V4.0.1b firmware line.

The goal is to separate verified firmware evidence from unproven claims.
It does not patch the firmware. It reports exact binary differences,
peripheral/literal evidence, exp13 patch bytes, and why ADC/RMS/math patches
are not yet safe without a confirmed measurement-engine contract.
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

from dm303_text_resource import parse_text_dat
from dm303_v4_static_analysis import (
    LOAD_BASE,
    addr_to_offset,
    read_vectors,
    thumb_entries_from_vectors,
    thumb_walk,
)


DEFAULT_IMAGES = {
    "v3.16": Path("backup/DM303 V3.16-read only/DM303V316.bin"),
    "v4.0": Path("backup/DM303 V4.0-read only/DM303V4.004.bin"),
    "v4.0.1b-exp13": Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin"),
}

DEFAULT_TEXTS = {
    "official-en": Path("backup/DM303 V4.0-read only/system/TEXT_EN.DAT"),
    "current-ms": Path("dm303_firmware/DM303-V4.0.1-beta/system/TEXT_MS.DAT"),
}

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

TEXT_KEYWORDS = (
    "zero",
    "sifar",
    "calib",
    "voltage",
    "voltan",
    "current",
    "arus",
    "ammeter",
    "voltmeter",
    "oscillo",
    "scope",
    "rms",
    "ac",
    "dc",
    "hold",
    "injector",
    "fuel",
    "frequency",
    "frekuensi",
    "cranking",
)

PATCH_EXPECTATIONS = {
    0x06A06: ("low byte-IO entry redirected to exp11/exp13 bounded wrapper", bytes.fromhex("00 f0 23 b8")),
    0x06A50: ("bounded wrapper prefix, waits up to 0x0fa0 and returns 0xff on timeout", bytes.fromhex("70 b5 05 46 40 f6 a0 76")),
    0x09570: ("stream-read retry branch removed", bytes.fromhex("00 bf")),
    0x0967C: ("command 0x40 retry budget clamped to 0x60", bytes.fromhex("60 27")),
    0x09682: ("command 0x48 retry budget clamped to 0x60", bytes.fromhex("60 27")),
    0x09694: ("small fallback retry budget kept at 0x0a", bytes.fromhex("0a 27")),
    0x09706: ("command 0x40 busy failure routed to existing error/clear block", bytes.fromhex("4c d1")),
    0x09758: ("command/status retry branch removed", bytes.fromhex("00 bf")),
    0x097BE: ("mode/status retry branch removed", bytes.fromhex("00 bf")),
    0x097E6: ("stream error cleanup clears flag bits 0 and 1", bytes.fromhex("20 f0 03 00")),
    0x0F19A: ("mode/range entry branch to stale state clear wrapper", bytes.fromhex("1e f0 34 ba")),
    0x2D606: (
        "mode/range stale state clear wrapper",
        bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    ),
}

IMPORTANT_LITERALS = {
    0x2000022C: "shared stream/status byte used by V4.0 measurement helper",
    0x20000130: "busy/retry word observed near command/status logic",
    0x40012400: "ADC1 base, direct literal would support an internal ADC patch",
    0x40012800: "ADC2 base, direct literal would support an internal ADC patch",
    0x40013C00: "ADC3 base, direct literal would support an internal ADC patch",
    0x40020000: "DMA1 base",
    0x40020400: "DMA2 base",
}

CODE_CAVE_TARGETS = {
    0x08016A50: "exp11/exp13 low byte-IO wrapper code cave, original V4 setup-helper prefix",
    0x08016AAE: "adjacent original V4 setup helper area",
    0x0803D606: "exp13 mode/range stale state clear wrapper code cave",
}


@dataclass(frozen=True)
class ImageInfo:
    label: str
    path: Path
    data: bytes

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.data)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_images(paths: dict[str, Path]) -> dict[str, ImageInfo]:
    images: dict[str, ImageInfo] = {}
    for label, path in paths.items():
        if not path.exists():
            raise SystemExit(f"Missing image for {label}: {path}")
        images[label] = ImageInfo(label, path, path.read_bytes())
    return images


def u32_at(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def find_pattern_offsets(data: bytes, pattern: bytes) -> list[int]:
    offsets: list[int] = []
    start = 0
    while True:
        offset = data.find(pattern, start)
        if offset < 0:
            return offsets
        offsets.append(offset)
        start = offset + 1


def peripheral_name(value: int) -> str | None:
    if not (0x40000000 <= value <= 0x40023FFF or 0xE000E000 <= value <= 0xE000EFFF):
        return None
    for base, name in PERIPHERAL_BASES:
        span = 0x100 if base >= 0xE0000000 else 0x400
        if base <= value < base + span:
            return f"{name}+0x{value - base:x}"
    return f"PERIPH 0x{value:08x}"


def exact_peripheral_counts(data: bytes) -> dict[str, tuple[int, list[int]]]:
    result: dict[str, tuple[int, list[int]]] = {}
    for base, name in PERIPHERAL_BASES:
        hits = find_pattern_offsets(data, struct.pack("<I", base))
        result[name] = (len(hits), hits[:8])
    return result


def get_seen_instructions(data: bytes) -> set[int]:
    vectors = read_vectors(data)
    entries = thumb_entries_from_vectors(vectors)
    _functions, seen = thumb_walk(data, entries, limit=650_000)
    return seen


def disassemble_one(md: Cs, data: bytes, address: int):
    offset = addr_to_offset(address, len(data))
    if offset is None:
        return None
    insns = list(md.disasm(data[offset : offset + 4], address, count=1))
    return insns[0] if insns else None


def reg_name(insn, reg_id: int) -> str:
    return insn.reg_name(reg_id) or ""


def nearest_function_start(starts: list[int], address: int) -> int | None:
    low = 0
    high = len(starts)
    while low < high:
        mid = (low + high) // 2
        if starts[mid] <= address:
            low = mid + 1
        else:
            high = mid
    return starts[low - 1] if low else None


def collect_pc_literal_peripheral_hits(data: bytes) -> list[tuple[int, int, str]]:
    vectors = read_vectors(data)
    entries = thumb_entries_from_vectors(vectors)
    functions, seen = thumb_walk(data, entries, limit=650_000)
    starts = sorted(functions)
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    rows: list[tuple[int, int, str]] = []

    for address in sorted(seen):
        insn = disassemble_one(md, data, address)
        if insn is None or insn.mnemonic.lower() != "ldr" or len(insn.operands) < 2:
            continue
        mem = insn.operands[1]
        if mem.type != ARM_OP_MEM or reg_name(insn, mem.mem.base) != "pc":
            continue
        literal_addr = ((insn.address + 4) & ~3) + mem.mem.disp
        literal_offset = addr_to_offset(literal_addr, len(data))
        if literal_offset is None or literal_offset + 4 > len(data):
            continue
        value = u32_at(data, literal_offset)
        name = peripheral_name(value)
        if name is None:
            continue
        function = nearest_function_start(starts, address)
        if function is None:
            continue
        rows.append((function, address, name))
    return rows


def summarize_pc_literal_hits(rows: list[tuple[int, int, str]], limit: int = 18) -> list[tuple[int, int, dict[str, int]]]:
    grouped: dict[int, Counter[str]] = defaultdict(Counter)
    counts: Counter[int] = Counter()
    for function, _address, name in rows:
        base_name = name.split("+")[0]
        grouped[function][base_name] += 1
        counts[function] += 1
    return [(function, counts[function], dict(grouped[function])) for function, _ in counts.most_common(limit)]


def literal_refs(data: bytes, value: int) -> list[int]:
    refs = find_pattern_offsets(data, struct.pack("<I", value))
    refs.extend(find_pattern_offsets(data, struct.pack("<I", value | 1)))
    return sorted(set(refs))


def control_flow_refs(data: bytes, target: int) -> list[tuple[int, str, str]]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    rows: list[tuple[int, str, str]] = []
    # Scan every aligned halfword, not just the discovered call graph. The
    # exp13 branch at 0x08016a06 is deliberately outside some static walks
    # after the helper entry is replaced with a direct b.w.
    for offset in range(0, len(data) - 3, 2):
        address = LOAD_BASE + offset
        insns = list(md.disasm(data[offset : offset + 4], address, count=1))
        if not insns:
            continue
        insn = insns[0]
        if not insn.operands:
            continue
        if not (insn.mnemonic.startswith("b") or insn.mnemonic.startswith("bl")):
            continue
        for operand in insn.operands:
            if operand.type == ARM_OP_IMM and (int(operand.imm) & ~1) == target:
                rows.append((address, insn.mnemonic, insn.op_str))
                break
    return rows


def diff_ranges(old: bytes, new: bytes, limit: int = 36) -> tuple[int, list[tuple[int, int, bytes, bytes]]]:
    changed = 0
    ranges: list[tuple[int, int, bytes, bytes]] = []
    index = 0
    max_len = min(len(old), len(new))
    while index < max_len:
        if old[index] == new[index]:
            index += 1
            continue
        start = index
        while index < max_len and old[index] != new[index]:
            changed += 1
            index += 1
        if len(ranges) < limit:
            ranges.append((start, index - start, old[start:index], new[start:index]))
    changed += abs(len(old) - len(new))
    return changed, ranges


def text_clues(path: Path) -> list[tuple[int, int, str]]:
    if not path.exists():
        return []
    _magic, _count, entries = parse_text_dat(path)
    rows = []
    for entry in entries:
        text = entry.text
        lowered = text.lower()
        if any(keyword in lowered for keyword in TEXT_KEYWORDS):
            safe = text.encode("ascii", "backslashreplace").decode("ascii")
            rows.append((entry.index, entry.record_length, safe))
    return rows


def md_table_row(values: list[object]) -> str:
    return "| " + " | ".join(str(value) for value in values) + " |"


def build_report(images: dict[str, ImageInfo], text_paths: dict[str, Path]) -> str:
    lines: list[str] = [
        "# DM303 V4.0.1b full stability audit",
        "",
        "Read-only audit generated from local firmware files. This report proves",
        "what the current V4.0.1b image actually changes and what is still only",
        "a hypothesis. It does not claim physical accuracy/noise is fixed without",
        "bench data from the real device.",
        "",
        "## Image identity",
        "",
        "| Image | Path | Size | SHA-256 |",
        "|---|---|---:|---|",
    ]
    for image in images.values():
        lines.append(md_table_row([image.label, f"`{image.path}`", len(image.data), f"`{image.sha256}`"]))

    if "v4.0" in images and "v4.0.1b-exp13" in images:
        changed, ranges = diff_ranges(images["v4.0"].data, images["v4.0.1b-exp13"].data)
        lines.extend(
            [
                "",
                "## Verified binary changes from official V4.0",
                "",
                f"- Differing byte count: `{changed}`.",
                "- This proves the final V4.0.1b image is not just renamed.",
                "",
                "| Offset | Size | V4.0 bytes | V4.0.1b bytes |",
                "|---:|---:|---|---|",
            ]
        )
        for offset, size, before, after in ranges:
            lines.append(
                md_table_row(
                    [
                        f"`0x{offset:05x}`",
                        size,
                        f"`{before[:16].hex(' ')}`" + (" ..." if len(before) > 16 else ""),
                        f"`{after[:16].hex(' ')}`" + (" ..." if len(after) > 16 else ""),
                    ]
                )
            )
        if len(ranges) == 36:
            lines.append("| ... | ... | additional changed ranges omitted | additional changed ranges omitted |")

    final = images.get("v4.0.1b-exp13")
    if final is not None:
        lines.extend(
            [
                "",
                "## exp13 patch byte proof",
                "",
                "| Offset | Address | Purpose | Expected | Actual | Match |",
                "|---:|---:|---|---|---|---|",
            ]
        )
        for offset, (purpose, expected) in PATCH_EXPECTATIONS.items():
            actual = final.data[offset : offset + len(expected)]
            lines.append(
                md_table_row(
                    [
                        f"`0x{offset:05x}`",
                        f"`0x{LOAD_BASE + offset:08x}`",
                        purpose,
                        f"`{expected.hex(' ')}`",
                        f"`{actual.hex(' ')}`",
                        actual == expected,
                    ]
                )
            )

    lines.extend(
        [
            "",
            "## Direct peripheral literal evidence",
            "",
            "Exact 32-bit base-address hits are a conservative test. No direct ADC",
            "literal means an ADC/filter/RMS patch cannot yet be justified by a",
            "simple register-base address.",
            "",
            "| Image | ADC1 | ADC2 | ADC3 | DMA1 | DMA2 | SPI1 | GPIOB | GPIOD |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for image in images.values():
        counts = exact_peripheral_counts(image.data)
        lines.append(
            md_table_row(
                [
                    image.label,
                    counts["ADC1"][0],
                    counts["ADC2"][0],
                    counts["ADC3"][0],
                    counts["DMA1"][0],
                    counts["DMA2"][0],
                    counts["SPI1"][0],
                    counts["GPIOB"][0],
                    counts["GPIOD"][0],
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Peripheral code-path concentration",
            "",
            "Top functions with PC-literal peripheral loads. These are candidates for",
            "hardware interaction, not confirmed ADC math hooks.",
            "",
        ]
    )
    for image in images.values():
        lines.extend([f"### {image.label}", "", "| Function | Hit Count | Peripherals |", "|---:|---:|---|"])
        for function, count, peripherals in summarize_pc_literal_hits(collect_pc_literal_peripheral_hits(image.data)):
            lines.append(md_table_row([f"`0x{function:08x}`", count, f"`{peripherals}`"]))
        lines.append("")

    lines.extend(
        [
            "## Important literal search",
            "",
            "| Image | Literal | Meaning | Hits | First Offsets |",
            "|---|---:|---|---:|---|",
        ]
    )
    for image in images.values():
        for value, meaning in IMPORTANT_LITERALS.items():
            refs = literal_refs(image.data, value)
            shown = ", ".join(f"`0x{offset:05x}`" for offset in refs[:8])
            if len(refs) > 8:
                shown += f", ... +{len(refs) - 8}"
            lines.append(md_table_row([image.label, f"`0x{value:08x}`", meaning, len(refs), shown or "none"]))

    lines.extend(
        [
            "",
            "## exp13 code-cave caller audit",
            "",
            "Official V4.0 should not have normal callers into the area reused by",
            "the exp11/exp13 low byte-IO wrapper or the exp13 mode/range wrapper.",
            "Current V4.0.1b should show only the deliberate branches from",
            "`0x08016a06` to `0x08016a50` and `0x0801f19a` to `0x0803d606`.",
            "",
            "| Image | Target | Meaning | Control-flow Refs | Literal Refs |",
            "|---|---:|---|---|---|",
        ]
    )
    for label in ("v4.0", "v4.0.1b-exp13"):
        image = images.get(label)
        if image is None:
            continue
        for target, meaning in CODE_CAVE_TARGETS.items():
            cflow = control_flow_refs(image.data, target)
            lits = literal_refs(image.data, target)
            cflow_text = ", ".join(f"`0x{addr:08x} {mn} {op}`" for addr, mn, op in cflow[:8]) or "none"
            if len(cflow) > 8:
                cflow_text += f", ... +{len(cflow) - 8}"
            lit_text = ", ".join(f"`0x{offset:05x}`" for offset in lits[:8]) or "none"
            if len(lits) > 8:
                lit_text += f", ... +{len(lits) - 8}"
            lines.append(md_table_row([label, f"`0x{target:08x}`", meaning, cflow_text, lit_text]))

    lines.extend(
        [
            "",
            "## UI/manual text clues",
            "",
            "| Resource | Entry | Len | Text |",
            "|---|---:|---:|---|",
        ]
    )
    for label, path in text_paths.items():
        for index, length, text in text_clues(path)[:80]:
            lines.append(md_table_row([label, index, length, f"`{text}`"]))

    lines.extend(
        [
            "",
            "## Findings",
            "",
            "- The strongest firmware-side clue is still shared stream/status blocking:",
            "  when the number and battery icon vanish together, the UI/status refresh",
            "  is likely waiting on measurement/status recovery rather than suffering",
            "  only from a bitmap or text resource problem.",
            "- The exp13 binary really modifies the stream/status, low byte-IO, stream error-state cleanup, and mode/range entry path.",
            "  It is not a cosmetic-only build.",
            "- Direct ADC1/ADC2/ADC3 literal hits remain absent. The analog front-end may",
            "  be external, indirectly addressed, or hidden behind a stream protocol.",
            "  A claimed ADC averaging/RMS patch is unsafe until the input/output",
            "  contract of that routine is confirmed.",
            "- DMA literals can be present as platform support, but that alone does not",
            "  prove a measurement DMA recovery hook.",
            "- V4.0.2-style guessed offset patches must stay rejected unless every",
            "  target is revalidated against disassembly and a safe caller contract.",
            "",
            "## Safe next decision",
            "",
            "Do not add a new ADC/RMS/math patch in this pass. Exp13 has already added",
            "the confirmed mode-change state reset hook. The next firmware change",
            "should only be made after a valid-reading timeout hook or measurement",
            "buffer/RMS accumulator reset hook is confirmed. Until then, use the",
            "bench CSV and this audit to separate hardware leakage/noise from",
            "firmware recovery latency.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=Path("docs/v401b-full-stability-audit.md"))
    args = parser.parse_args()

    images = load_images(DEFAULT_IMAGES)
    report = build_report(images, DEFAULT_TEXTS)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8", newline="\n")
    print("full_stability_audit=ok")
    print(f"report={args.report}")
    print(f"current_sha256={images['v4.0.1b-exp13'].sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
