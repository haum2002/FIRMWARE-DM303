#!/usr/bin/env python3
"""DM303 latency hunt, phase 8 - V3.16 ring filler ISR + AFE protocol hunt."""
import struct, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase8.txt"
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)

def disasm(buf, start, end):
    lines = []
    code = buf[start - BASE:end - BASE]
    for ins in md.disasm(code, start):
        if ins.address >= end:
            break
        line = f"{ins.address:08x}: {ins.bytes.hex():<10} {ins.mnemonic} {ins.op_str}"
        if ins.mnemonic in ("ldr", "ldr.w") and "[pc" in ins.op_str:
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

v316 = V316.read_bytes()
o = []
def sec(t):
    o.append(""); o.append("=" * 76); o.append(t); o.append("=" * 76)

sec("V3.16 ring filler ISR family 0x08017882-0x08017a40")
o += disasm(v316, 0x08017882, 0x08017A40)

sec("V3.16 movs r0,#0x22 / #0x42 / #0x60 sites (AFE command bytes)")
for enc, lab in [(b"\x22\x20", "movs r0,#0x22"), (b"\x42\x20", "movs r0,#0x42"), (b"\x60\x20", "movs r0,#0x60")]:
    hits = []
    i = v316.find(enc)
    while i != -1:
        hits.append(i + BASE)
        i = v316.find(enc, i + 1)
    o.append(f"{lab}: " + ", ".join(f"0x{h:x}" for h in hits[:30]))
    for h in hits[:8]:
        o.append(f"--- @0x{h:x} ---")
        o += disasm(v316, h - 12, h + 24)

OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
