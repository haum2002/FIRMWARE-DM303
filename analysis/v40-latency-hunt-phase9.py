#!/usr/bin/env python3
"""DM303 latency hunt, phase 9 - full dump of 0x0802603a + flag90/bank-1 users."""
import struct, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase9.txt"
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

def bl_callers(buf, target):
    out = []
    for off in range(0, len(buf) - 4, 2):
        hw1, hw2 = struct.unpack_from("<HH", buf, off)
        if (hw1 & 0xF800) != 0xF000 or (hw2 & 0xD000) != 0xD000:
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
        if (off + BASE + 4) + imm32 == target:
            out.append(off + BASE)
    return out

buf = V40.read_bytes()
o = []
def sec(t):
    o.append(""); o.append("=" * 76); o.append(t); o.append("=" * 76)

sec("0x0802603a full dump (to 0x08026340)")
o += disasm(buf, 0x0802603A, 0x08026340)

sec("callers of bank-1 AFE helpers 0x08016d88 / 0x08016dae / 0x08016dd6")
for t in (0x08016D88, 0x08016DAE, 0x08016DD6):
    cs = bl_callers(buf, t)
    o.append(f"bl -> 0x{t:x} ({len(cs)}): " + ", ".join(f"0x{c:x}" for c in cs))
    for c in cs[:10]:
        o += disasm(buf, c - 10, c + 4)

sec("readers/writers of 0x20000090 (checksum-enable flag)")
needle = struct.pack("<I", 0x20000090)
i = buf.find(needle)
while i != -1:
    o.append(f"pool @0x{i+BASE:x}")
    i = buf.find(needle, i + 1)

OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
