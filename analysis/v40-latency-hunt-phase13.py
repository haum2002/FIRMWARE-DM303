#!/usr/bin/env python3
"""DM303 latency hunt, phase 13 - 0x0801ed12 + 0x0801cd6a region + 0x200000e2 readers."""
import struct, re
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase13.txt"
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

def ldr_literal_sites(buf, value):
    sites = []
    for off in range(0, len(buf) - 2, 2):
        hw = struct.unpack_from("<H", buf, off)[0]
        if (hw & 0xF800) != 0x4800:
            continue
        imm = (hw & 0xFF) * 4
        pc = ((off + BASE + 4) & ~3)
        pool = pc + imm
        if 0 <= pool - BASE <= len(buf) - 4:
            if struct.unpack_from("<I", buf, pool - BASE)[0] == value:
                sites.append(off + BASE)
    return sites

buf = V40.read_bytes()
o = []
def sec(t):
    o.append(""); o.append("=" * 76); o.append(t); o.append("=" * 76)

sec("0x0801ed12 (settle/valid check?)")
o += disasm(buf, 0x0801ED12, 0x0801EE04)
sec("caller-of-1f316 region 0x0801cd00-0x0801ce00")
o += disasm(buf, 0x0801CD00, 0x0801CE00)
sec("code refs to countdown byte 0x200000e2")
for s in ldr_literal_sites(buf, 0x200000E2):
    o.append(f"--- ldr site @0x{s:x} ---")
    o += disasm(buf, s - 10, s + 22)
OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
