#!/usr/bin/env python3
"""DM303 latency hunt, phase 5 — V3.16 AFE config evidence + V4.0 TIM2 ISR."""
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
BASE = 0x08010000
OUT = ROOT / "analysis" / "v40-latency-hunt-phase5.txt"
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


v40 = V40.read_bytes()
v316 = V316.read_bytes()
o = []


def sec(t):
    o.append("")
    o.append("=" * 76)
    o.append(t)
    o.append("=" * 76)


# --- V3.16: locate AFE helpers via the command-byte constants ---
sec("V3.16 sites of orr r0, r4, #0x20/#0x40/#0x60 (bit-bang command bytes)")
for pat, name in [(b"\x44\xf0\x20\x00", "orr r0,r4,#0x20"), (b"\x44\xf0\x40\x00", "orr r0,r4,#0x40"),
                  (b"\x40\xf0\x60\x00", "orr r0,r0,#0x60"), (b"\x44\xf0\x60\x00", "orr r0,r4,#0x60")]:
    hits = []
    i = v316.find(pat)
    while i != -1:
        hits.append(i + BASE)
        i = v316.find(pat, i + 1)
    o.append(f"{name}: " + ", ".join(f"0x{h:x}" for h in hits))

# V3.16 AFE write3 equivalent: find function containing first 0x20-orr hit
sec("V3.16 around orr sites (identify helpers)")
for a in sorted(set([h for h in [i for i in range(len(v316)) if False]])):
    pass

# --- V3.16 disasm around movs r0,#0x37 / #0x16 hits (no address filter) ---
for enc, label in [(b"\x37\x20", "movs r0,#0x37"), (b"\x16\x20", "movs r0,#0x16")]:
    sec(f"V3.16 context around each {label}")
    i = v316.find(enc)
    while i != -1:
        a = i + BASE
        o.append(f"--- @0x{a:x} ---")
        o += disasm(v316, a - 16, a + 28)
        i = v316.find(enc, i + 1)

# --- V4.0 TIM2 ISR ---
sec("V4.0 TIM2 ISR 0x08017c27 (tick incrementer)")
o += disasm(v40, 0x08017C27, 0x08017D60)

# --- V4.0 ring filler irq28 0x08017ff3 ---
sec("V4.0 ring filler ISR 0x08017ff3")
o += disasm(v40, 0x08017FF3, 0x08018090)

# --- V4.0 0x08017ed8 tail already have; now: does it start TIM2? disasm 0x0803ac24 area briefly ---
sec("V4.0 TIM base-init wrapper 0x0803ac24 head")
o += disasm(v40, 0x0803AC24, 0x0803ACA0)

# --- V4.0 screen dispatcher ---
sec("V4.0 screen dispatcher 0x08013600-0x08013760")
o += disasm(v40, 0x08013600, 0x08013760)

OUT.write_text("\n".join(o) + "\n", encoding="utf-8")
print(f"wrote {OUT} ({len(o)} lines)")
