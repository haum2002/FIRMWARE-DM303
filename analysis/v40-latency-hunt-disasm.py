#!/usr/bin/env python3
"""DM303 V4.0 AC<->DC latency hunt — disassembly + xref tool.

Read-only against backup/. Dumps annotated disassembly for a fixed set of
ranges, resolves ldr [pc] literals, scans for constants, and finds xrefs
to helper functions and globals. Output: analysis/v40-latency-hunt-disasm.txt
"""
import struct
import sys
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
V313 = ROOT / "backup" / "SD-file_DM303_update_US240104-read only" / "DM303-V3.13.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-disasm.txt"

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
md.detail = False


def load(p):
    return p.read_bytes()


def disasm(buf, start, end, annotate_lit=True):
    """Linear disassembly of [start,end) (addresses), resolving ldr [pc] literals."""
    lines = []
    off = start - BASE
    code = buf[off:end - BASE]
    for ins in md.disasm(code, start):
        if ins.address >= end:
            break
        line = f"{ins.address:08x}: {ins.bytes.hex():<10} {ins.mnemonic} {ins.op_str}"
        # resolve ldr rx, [pc, #imm]
        if annotate_lit and ins.mnemonic == "ldr" and "[pc" in ins.op_str:
            # compute PC-relative target: pc = (addr+4) & ~3
            import re
            m = re.search(r"\[pc, #(-?0x[0-9a-f]+|\d+)\]", ins.op_str)
            if m:
                imm = int(m.group(1), 0)
                pc = (ins.address + 4) & ~3
                tgt = pc + imm
                if 0 <= tgt - BASE < len(buf) - 3:
                    val = struct.unpack_from("<I", buf, tgt - BASE)[0]
                    line += f" ; lit@0x{tgt:x}=0x{val:x}"
        lines.append(line)
        if ins.address + ins.size >= end:
            break
    return lines


def find_xrefs_imm32(buf, value):
    """Find every 4-byte aligned/unaligned occurrence of value as a word."""
    hits = []
    needle = struct.pack("<I", value)
    i = buf.find(needle)
    while i != -1:
        hits.append(i + BASE)
        i = buf.find(needle, i + 1)
    return hits


def main():
    buf = load(V40)
    out = []

    def section(title):
        out.append("")
        out.append("=" * 78)
        out.append(title)
        out.append("=" * 78)

    # --- helper functions around the AFE transport ---
    section("AFE transport/delay helpers 0x08016b00-0x08016caa")
    out += disasm(buf, 0x08016b00, 0x08016caa)

    section("0x08016c2e write3 + neighbors to 0x08016d12")
    out += disasm(buf, 0x08016c2e, 0x08016d12)

    section("0x080170dc re-kick prefix fn + 0x0801710e bitbang reader + 0x080171de")
    out += disasm(buf, 0x080170dc, 0x08017248)

    section("0x08017ed8 AFE-rate setup (full, to 0x08018040)")
    out += disasm(buf, 0x08017ed8, 0x08018040)

    section("0x0801aa86 (called at ammeter entry and loop head)")
    out += disasm(buf, 0x0801aa86, 0x0801ab60)

    section("0x0802603a query fn (called in state-0x2d path B)")
    out += disasm(buf, 0x0802603a, 0x080260e0)

    section("0x0802600c (called before ammeter exit)")
    out += disasm(buf, 0x0802600c, 0x0802603a)

    section("0x0801d18c key/event scan")
    out += disasm(buf, 0x0801d18c, 0x0801d260)

    section("0x08017ad4 delay fn")
    out += disasm(buf, 0x08017ad4, 0x08017b60)

    section("0x080160d0 (display enable?)")
    out += disasm(buf, 0x080160d0, 0x08016160)

    section("0x0802d158 (read fn used by range-change state 0xe)")
    out += disasm(buf, 0x0802d158, 0x0802d190)

    section("0x0801f316 mode-entry orchestrator (full)")
    out += disasm(buf, 0x0801f316, 0x0801f4c0)

    # --- scan ammeter fn for all writes to [sp,#0x10] ---
    section("All str .., [sp, #0x10] inside ammeter fn 0x0802d190-0x0802df8a")
    code = buf[0x0802d190 - BASE:0x0802df8a - BASE]
    for ins in md.disasm(code, 0x0802d190):
        if "[sp, #0x10]" in ins.op_str and ins.mnemonic.startswith("str"):
            out.append(f"{ins.address:08x}: {ins.mnemonic} {ins.op_str}")

    # --- tick global: literal at 0x0802d478 (ldr r0,[pc,#0x3c4]) ---
    section("Tick counter global + incrementer hunt")
    pc = (0x0802d478 + 4) & ~3
    lit_addr = pc + 0x3c4
    tick_ptr = struct.unpack_from("<I", buf, lit_addr - BASE)[0]
    out.append(f"literal @0x{lit_addr:x} = 0x{tick_ptr:x} (tick counter ptr)")
    # also the one at 0x0802d480 (same?)
    for site, imm in [(0x0802d454, 0x3e8), (0x0802d478, 0x3c4), (0x0802d480, 0x3bc), (0x0802d4b8, 0x384)]:
        pc = (site + 4) & ~3
        la = pc + imm
        val = struct.unpack_from("<I", buf, la - BASE)[0]
        out.append(f"  site 0x{site:x}: lit@0x{la:x} = 0x{val:x}")
    hits = find_xrefs_imm32(buf, tick_ptr)
    out.append(f"xrefs to tick ptr 0x{tick_ptr:x} as imm32: " + ", ".join(f"0x{h:x}" for h in hits[:60]))

    # --- find every bl to helpers of interest ---
    section("Callers (bl imm) of AFE helpers in whole image")
    def bl_target(ins):
        if ins.mnemonic.startswith("bl") and ins.op_str.startswith("#0x"):
            return int(ins.op_str[1:], 16)
        return None
    targets = {0x08016d34: [], 0x08016d5a: [], 0x08016d12: [], 0x08016fa4: [],
               0x080171de: [], 0x080170dc: [], 0x08017ed8: [], 0x0801f316: [],
               0x08016caa: [], 0x08016d88: [], 0x08016dae: [], 0x08016dd6: []}
    off = 0
    # whole-image sweep in 2-byte steps is slow; use capstone linear sweep on full image
    for ins in md.disasm(buf, BASE):
        t = bl_target(ins)
        if t in targets:
            targets[t].append(ins.address)
    for t, callers in sorted(targets.items()):
        out.append(f"bl -> 0x{t:x}: " + ", ".join(f"0x{c:x}" for c in callers))

    # --- constants scan in ammeter fn + state machine region ---
    section("mov/movw immediates of interest in 0x0802d190-0x0802e200")
    interesting = {0xf0, 0x168, 0x258, 0x320, 0x3e8, 0x4b0, 0x5dc, 0x640, 0x3a98, 0x2710, 0x2d, 0x27, 0xa}
    code = buf[0x0802d190 - BASE:0x0802e200 - BASE]
    for ins in md.disasm(code, 0x0802d190):
        if ins.mnemonic in ("movs", "mov", "mov.w", "movw", "cmp", "cmp.w", "movs.w"):
            parts = ins.op_str.split("#")
            if len(parts) == 2:
                try:
                    v = int(parts[1].rstrip("]"), 0)
                except ValueError:
                    continue
                if v in interesting:
                    out.append(f"{ins.address:08x}: {ins.mnemonic} {ins.op_str}")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(out)} lines)")


if __name__ == "__main__":
    main()
