# DM303 V4.0 latency hunt — pass 3: tick/delay units, cross-refs, 0x801febc, 0x802d158
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
BASE = 0x08010000
img = V40.read_bytes()
i316 = V316.read_bytes()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)

def find_bytes(buf, pat):
    out, i = [], 0
    while True:
        j = buf.find(pat, i)
        if j < 0: break
        out.append(j); i = j + 1
    return out

def disas_around(buf, addr, before=6, after=10, start=None):
    s = addr - before * 2 if start is None else start
    data = buf[s - BASE: addr + after * 2 - BASE]
    lines = []
    for ins in md.disasm(data, s):
        if ins.address > addr + after * 2: break
        lines.append(f"{ins.address:08x}: {ins.bytes.hex():<9} {ins.mnemonic} {ins.op_str}")
    return lines

print("########## (1) refs to tick global 0x200000ac ##########")
for off in find_bytes(img, struct.pack("<I", 0x200000ac)):
    a = BASE + off
    print(f"-- literal at {a:#x}")
    # find ldr sites whose pc+imm == a: scan backwards not reliable; just note offset

print("\n########## (2) refs to delay counter 0x200000c0 ##########")
for off in find_bytes(img, struct.pack("<I", 0x200000c0)):
    print(f"-- literal at {BASE+off:#x}")

print("\n########## (3) refs to 0x2000010c (mode global of 0x8017ed8) ##########")
for off in find_bytes(img, struct.pack("<I", 0x2000010c)):
    print(f"-- literal at {BASE+off:#x}")

print("\n########## (4) SysTick / core peripheral refs ##########")
for name, val in (("SYST_CSR",0xE000E010),("SYST_RVR",0xE000E014),("SYST_CVR",0xE000E018),
                  ("TIM2 base",0x40000000),("RCC_APB1ENR?",0x40021040),("RCC base",0x40021000)):
    hits = find_bytes(img, struct.pack("<I", val))
    print(f"{name} {val:#x}: {len(hits)} hits: {[hex(BASE+h) for h in hits[:12]]}")

print("\n########## (5) all bl sites to key helpers ##########")
targets = {
    0x080171de: "DRDY reader", 0x08016d34: "AFE cmd byte", 0x08016d5a: "AFE bits76",
    0x08016d12: "AFE byte2", 0x08016fa4: "AFE strobe", 0x080170dc: "AFE reinit?",
    0x08017ad4: "delay_ticks", 0x08017ed8: "TIM2 rate setup", 0x0801d18c: "get_state",
    0x0802603a: "fn2603a", 0x0801febc: "fn1febc", 0x0802d158: "fn2d158",
    0x0801f19a: "mode_routine", 0x0801f0f2: "selector",
}
# bl encoding: 11110 S imm10 | 11 J1 1 J2 imm10 ; target = pc+4 + SignExt(imm32)<<1
def bl_target(b, pc):
    h1, h2 = struct.unpack_from("<HH", b)
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3ff
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    imm11 = h2 & 0x7ff
    i1 = (~(j1 ^ s)) & 1
    i2 = (~(j2 ^ s)) & 1
    imm32 = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s: imm32 -= 1 << 25
    return pc + 4 + imm32

sites = {t: [] for t in targets}
for off in range(0, len(img) - 4, 2):
    h1 = struct.unpack_from("<H", img, off)[0]
    if (h1 & 0xF800) != 0xF000: continue
    h2 = struct.unpack_from("<H", img, off + 2)[0]
    if (h2 & 0xD000) != 0xD000: continue
    pc = BASE + off
    t = bl_target(img[off:off+4], pc)
    if t in sites:
        sites[t].append(pc)
for t, name in targets.items():
    print(f"{name} {t:#x}: {len(sites[t])} callers: {[hex(x) for x in sites[t]]}")

print("\n########## (6) fn 0x0801febc ##########")
data = img[0x0801febc - BASE: 0x08020040 - BASE]
for ins in md.disasm(data, 0x0801febc):
    print(f"{ins.address:08x}: {ins.bytes.hex():<9} {ins.mnemonic} {ins.op_str}")

print("\n########## (7) fn 0x0802d158 (used by state-0xe settle) ##########")
data = img[0x0802d158 - BASE: 0x0802d190 - BASE]
for ins in md.disasm(data, 0x0802d158):
    print(f"{ins.address:08x}: {ins.bytes.hex():<9} {ins.mnemonic} {ins.op_str}")
