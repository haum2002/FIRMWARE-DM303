#!/usr/bin/env python3
"""DM303 latency hunt, phase 3 — tick rate, V3.16 AFE evidence, dispatcher.

Read-only on backup/. Output: analysis/v40-latency-hunt-phase3.txt
"""
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase3.txt"
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


def main():
    v40 = V40.read_bytes()
    v316 = V316.read_bytes()
    o = []

    def sec(t):
        o.append("")
        o.append("=" * 76)
        o.append(t)
        o.append("=" * 76)

    # --- 1. vector table + SysTick handler ---
    sec("V4.0 vector table (16 core entries)")
    for i in range(16):
        v = struct.unpack_from("<I", v40, i * 4)[0]
        o.append(f"vec[{i}] = 0x{v:08x}")
    stk = struct.unpack_from("<I", v40, 15 * 4)[0] & ~1
    if 0x08010000 <= stk < 0x08010000 + len(v40):
        sec(f"V4.0 SysTick handler @0x{stk:x}")
        o += disasm(v40, stk, stk + 0x120)

    sec("V4.0 code around tick pool 0x8017988 (fn containing it)")
    o += disasm(v40, 0x08017900, 0x080179F0)
    sec("V4.0 code around tick pool 0x8017e60")
    o += disasm(v40, 0x08017DC0, 0x08017E60)
    sec("V4.0 code around tick pool 0x801c3fc")
    o += disasm(v40, 0x0801C3A0, 0x0801C420)

    # SysTick LOAD writes
    sec("V4.0 xrefs of 0xE000E010/0xE000E014 (SysTick CTRL/LOAD)")
    for val in (0xE000E010, 0xE000E014):
        needle = struct.pack("<I", val)
        i = v40.find(needle)
        while i != -1:
            o.append(f"imm32 0x{val:x} @0x{i + BASE:x}")
            o += disasm(v40, i + BASE - 16, i + BASE + 12)
            i = v40.find(needle, i + 1)

    # --- 2. V4.0 screen dispatcher around 0x08013600 ---
    sec("V4.0 screen dispatcher 0x08013600-0x08013760")
    o += disasm(v40, 0x08013600, 0x08013760)

    # --- 3. V3.16 AFE evidence ---
    sec("V3.16 movs r0,#imm candidate function-code writes (0x03/05/12/16/37)")
    for imm, enc in [(0x37, b"\x37\x20"), (0x16, b"\x16\x20"), (0x05, b"\x05\x20"),
                     (0x12, b"\x12\x20"), (0x03, b"\x03\x20"), (0xdd, b"\xdd\x23"),
                     (0x89, b"\x89\x22")]:
        hits = []
        i = v316.find(enc)
        while i != -1:
            hits.append(i + BASE)
            i = v316.find(enc, i + 1)
        o.append(f"movs r{'0' if enc[1]==0x20 else ('2' if enc[1]==0x22 else '3')},#0x{imm:x}: "
                 + ", ".join(f"0x{h:x}" for h in hits[:40]))

    sec("V3.16 disasm around each movs r0,#0x37 / #0x16 hit")
    for enc in (b"\x37\x20", b"\x16\x20"):
        i = v316.find(enc)
        while i != -1:
            a = i + BASE
            if 0x08020000 <= a <= 0x0802F000:
                o.append(f"--- @0x{a:x} ---")
                o += disasm(v316, a - 8, a + 20)
            i = v316.find(enc, i + 1)

    sec("V3.16 ammeter fn: raw scan cmp #0x2d in 0x0802d7ca-0x0802e200")
    s, e = 0x0802D7CA - BASE, 0x0802E200 - BASE
    for off in range(s, e, 2):
        hw = struct.unpack_from("<H", v316, off)[0]
        # cmp rn,#0x2d : 00101 ttt iiiiiiii
        if (hw & 0xF800) == 0x2800 and (hw & 0xFF) == 0x2D:
            o.append(f"cmp r{(hw>>8)&7},#0x2d @0x{off+BASE:x}")
    o += disasm(v316, 0x0802D7CA, 0x0802D8C0)

    OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(o)} lines)")


main()
