#!/usr/bin/env python3
"""DM303 latency hunt, phase 7 - V3.16 AFE bit-bang driver + config bytes."""
import struct, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase7.txt"
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

buf = V316.read_bytes()
o = []
def sec(t):
    o.append(""); o.append("=" * 76); o.append(t); o.append("=" * 76)

# locate literal pools holding the GPIO bases, then the code that uses them
for gpio in (0x40010C00, 0x40011000):
    sec(f"V3.16 imm32 pools for 0x{gpio:x} and 24B of code before each")
    needle = struct.pack("<I", gpio)
    i = buf.find(needle)
    while i != -1:
        a = i + BASE
        o.append(f"--- pool @0x{a:x} ---")
        i = buf.find(needle, i + 1)

# disasm around the first few pools of GPIOC (0x40011000 = bit-bang port)
sec("V3.16 code around first GPIOC pools (find bit-bang helpers)")
pools = []
needle = struct.pack("<I", 0x40011000)
i = buf.find(needle)
while i != -1:
    pools.append(i + BASE)
    i = buf.find(needle, i + 1)
o.append(f"GPIOC pools: {', '.join(hex(p) for p in pools)}")
for p in pools[:6]:
    o.append(f"--- fn around pool 0x{p:x} ---")
    o += disasm(buf, p - 0x40, p)

OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
