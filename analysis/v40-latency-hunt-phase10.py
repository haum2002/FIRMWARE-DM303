#!/usr/bin/env python3
"""DM303 latency hunt, phase 10 - rest of 0x0802603a (auto-zero) + 0x0801febc."""
import struct, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase10.txt"
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

buf = V40.read_bytes()
o = []
def sec(t):
    o.append(""); o.append("=" * 76); o.append(t); o.append("=" * 76)

sec("0x0802637c onward (rest of auto-zero fn)")
o += disasm(buf, 0x0802637C, 0x08026640)
sec("0x0801febc (called by auto-zero fn)")
o += disasm(buf, 0x0801FEBC, 0x0801FF80)
sec("0x0801f0f2 selector (full)")
o += disasm(buf, 0x0801F0F2, 0x0801F19A)
OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
