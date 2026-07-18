#!/usr/bin/env python3
"""DM303 latency hunt, phase 2 — tick rate, xrefs, V3.16 AFE evidence.

Read-only on backup/. Output: analysis/v40-latency-hunt-phase2.txt
"""
import struct
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase2.txt"

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)


def disasm(buf, start, end):
    lines = []
    code = buf[start - BASE:end - BASE]
    for ins in md.disasm(code, start):
        if ins.address >= end:
            break
        line = f"{ins.address:08x}: {ins.bytes.hex():<10} {ins.mnemonic} {ins.op_str}"
        if ins.mnemonic in ("ldr", "ldr.w") and "[pc" in ins.op_str:
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
    return lines


def xref_imm32(buf, value):
    needle = struct.pack("<I", value)
    hits, i = [], buf.find(needle)
    while i != -1:
        hits.append(i + BASE)
        i = buf.find(needle, i + 1)
    return hits


def bl_callers(buf, target):
    """Alignment-proof scan for BL <target> (Thumb-2 32-bit BL encoding)."""
    out = []
    for off in range(0, len(buf) - 4, 2):
        hw1, hw2 = struct.unpack_from("<HH", buf, off)
        if (hw1 & 0xF800) != 0xF000:
            continue
        if (hw2 & 0xD000) != 0xD000:
            continue
        s = (hw1 >> 10) & 1
        imm10 = hw1 & 0x03FF
        j1 = (hw2 >> 13) & 1
        j2 = (hw2 >> 11) & 1
        imm11 = hw2 & 0x07FF
        i1 = (~(j1 ^ s)) & 1
        i2 = (~(j2 ^ s)) & 1
        imm32 = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
        if s:
            imm32 -= 1 << 25
        tgt = (off + BASE + 4) + imm32
        if tgt == target:
            out.append(off + BASE)
    return out


def main():
    v40 = V40.read_bytes()
    v316 = V316.read_bytes()
    o = []

    def sec(t):
        o.append("")
        o.append("=" * 76)
        o.append(t)
        o.append("=" * 76)

    # --- 1. tick incrementers ---
    sec("V4.0 xref sites of tick 0x200000ac (disasm around each imm32 hit)")
    for h in xref_imm32(v40, 0x200000AC):
        o.append(f"--- imm32 @0x{h:x} ---")
        o += disasm(v40, h - 24, h + 40)
    sec("V4.0 xref sites of delay tick 0x200000c0")
    for h in xref_imm32(v40, 0x200000C0):
        o.append(f"--- imm32 @0x{h:x} ---")
        o += disasm(v40, h - 24, h + 40)

    # --- 2. consumers of re-init shadow 0x2000008c ---
    sec("V4.0 xrefs of 0x2000008c (AFE re-init shadow store)")
    for h in xref_imm32(v40, 0x2000008C):
        o.append(f"--- imm32 @0x{h:x} ---")
        o += disasm(v40, h - 16, h + 24)

    # --- 3. all bl callers (alignment-proof) of key helpers ---
    sec("V4.0 alignment-proof BL callers")
    for t in [0x080170DC, 0x080171DE, 0x08016D34, 0x08016D5A, 0x08016D12, 0x08016FA4,
              0x08017ED8, 0x0801F316, 0x0802603A, 0x0802D190, 0x0802DFE0, 0x08017AD4]:
        cs = bl_callers(v40, t)
        o.append(f"bl -> 0x{t:x} ({len(cs)}): " + ", ".join(f"0x{c:x}" for c in cs))

    # --- 4. alignment-proof [sp,#0x10] store scan inside ammeter fn ---
    sec("V4.0 raw scan str rX,[sp,#0x10] in 0x0802d190-0x0802df8a")
    start, end = 0x0802D190 - BASE, 0x0802DF8A - BASE
    for off in range(start, end, 2):
        hw = struct.unpack_from("<H", v40, off)[0]
        # str (imm) T1: 1001 0ttt iiii iiii  -> str rt, [sp, #imm*4]
        if (hw & 0xF800) == 0x9000:
            rt = (hw >> 8) & 7
            imm = (hw & 0xFF) * 4
            if imm == 0x10:
                o.append(f"0x{off+BASE:x}: str r{rt}, [sp, #0x10]  (raw)")
        # str.w T4: 1111 1000 1100 1101 tttt 1000 iiii iiii
        if off + 4 <= end:
            hw1, hw2 = struct.unpack_from("<HH", v40, off)
            if hw1 == 0xF8CD and (hw2 & 0x0F00) == 0x0800 and (hw2 & 0xFF) == 0x10:
                o.append(f"0x{off+BASE:x}: str.w r{(hw2>>12)&0xF}, [sp, #0x10] (raw)")

    # --- 5. V3.16 ammeter fn: AC/DC switch handler ---
    sec("V3.16 ammeter fn 0x0802d7ca: search cmp #0x2d and surroundings")
    code = v316[0x0802D7CA - BASE:0x0802E200 - BASE]
    hits = []
    for ins in md.disasm(code, 0x0802D7CA):
        if ins.mnemonic == "cmp" and "#0x2d" in ins.op_str:
            hits.append(ins.address)
    for h in hits:
        o.append(f"--- cmp #0x2d @0x{h:x} ---")
        o += disasm(v316, h - 8, h + 150)

    # --- 6. V3.16 AFE config writes: find the byte-triple writes (16c2e-style) ---
    sec("V3.16 GPIO AFE pin usage (imm32 0x40010c00 / 0x40011000 xref count)")
    o.append(f"0x40010c00 hits: {len(xref_imm32(v316, 0x40010C00))}")
    o.append(f"0x40011000 hits: {len(xref_imm32(v316, 0x40011000))}")

    # --- 7. V4.0: who else writes AFE cmd bytes 0x37 / 0x16 via 16d34 ---
    sec("V4.0 callers of 16d34 with immediate arg")
    for c in bl_callers(v40, 0x08016D34):
        o += disasm(v40, c - 8, c + 4)

    OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(o)} lines)")


main()
