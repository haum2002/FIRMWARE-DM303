# DM303 V4.0 latency hunt — pass 5: 0x802603a end, 0x20000100/102 incrementers, TIM2 ISR + clock
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
BASE = 0x08010000
img = V40.read_bytes()
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)

def w32(addr):
    return struct.unpack_from("<I", img, addr - BASE)[0]

def dump(title, start, end):
    print(f"\n===== {title} {start:#x}-{end:#x} =====")
    data = img[start - BASE:end - BASE]
    for ins in md.disasm(data, start):
        print(f"{ins.address:08x}: {ins.bytes.hex():<9} {ins.mnemonic} {ins.op_str}")

def find_bytes(buf, pat):
    out, i = [], 0
    while True:
        j = buf.find(pat, i)
        if j < 0: break
        out.append(j); i = j + 1
    return out

def find_ldr_refs(target):
    hits = []
    for off in range(0, len(img) - 2, 2):
        hw = struct.unpack_from("<H", img, off)[0]
        if (hw & 0xF800) != 0x4800: continue
        imm = (hw & 0xFF) * 4
        pc = BASE + off
        if ((pc + 4) & ~3) + imm == target:
            hits.append(pc)
    return hits

dump("fn 0x802603a end", 0x8026560, 0x8026600)

print("\n== literal pools containing 0x20000100 / 0x20000102 ==")
for val in (0x20000100, 0x20000102):
    for off in find_bytes(img, struct.pack("<I", val)):
        pool = BASE + off
        refs = find_ldr_refs(pool)
        print(f"  {val:#x} pool@{pool:#x} loaded at: {[hex(r) for r in refs]}")

# TIM2 ISR body with literal resolution: 0x8017ff2 - 0x80180c0
dump("TIM2 ISR 0x8017ff2", 0x8017ff2, 0x80180d0)
print("\n== literals 0x8018298-0x80182c8 ==")
for a in range(0x8018298, 0x80182c8, 4):
    print(f"  {a:#x}: {w32(a):#010x}")

# code around tick literal pools for 0x200000ac: 0x8017988, 0x8017e60, 0x801c3fc
for pool in (0x08017988, 0x08017e60, 0x0801c3fc):
    for pc in find_ldr_refs(pool):
        print(f"\n== ldr {pool:#x} at {pc:#x} (context) ==")
        s = pc - 12
        data = img[s - BASE: pc + 40 - BASE]
        for ins in md.disasm(data, s):
            if ins.address > pc + 36: break
            print(f"{ins.address:08x}: {ins.bytes.hex():<9} {ins.mnemonic} {ins.op_str}")
