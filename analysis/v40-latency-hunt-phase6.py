#!/usr/bin/env python3
"""DM303 latency hunt, phase 6 - tick ISR (aligned) + ring filler + dispatcher."""
import struct, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase6.txt"
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

v40 = V40.read_bytes()
o = []
def sec(t):
    o.append(""); o.append("=" * 76); o.append(t); o.append("=" * 76)

sec("V4.0 TIM2 ISR 0x08017c26 (tick incrementer, aligned)")
o += disasm(v40, 0x08017C26, 0x08017D40)
sec("V4.0 ring filler ISR 0x08017ff2 (aligned)")
o += disasm(v40, 0x08017FF2, 0x080180A0)
sec("V4.0 screen dispatcher 0x08013600-0x08013760")
o += disasm(v40, 0x08013600, 0x08013760)
sec("V4.0 SysTick setup: who writes 0x20000110-related + RCC/SysTick LOAD")
# find 0xe000e014 imm32 users
needle = struct.pack("<I", 0xE000E014)
i = v40.find(needle)
while i != -1:
    o.append(f"imm32 E000E014 @0x{i+BASE:x}")
    o += disasm(v40, i + BASE - 20, i + BASE + 16)
    i = v40.find(needle, i + 1)
OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
