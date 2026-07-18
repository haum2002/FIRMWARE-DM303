# DM303 V4.0 latency hunt — pass 4: rest of 0x802603a, tick incrementer, 0x2000010c writers
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

print("== literals 0x8026304-0x8026330 ==")
for a in range(0x8026304, 0x8026330, 4):
    print(f"  {a:#x}: {w32(a):#010x}")

dump("fn 0x802603a tail (from 0x802637c)", 0x802637c, 0x8026600)

# tick global 0x200000ac: find code that REFERENCES the literal sites.
# literal sites from pass3: 0x8017988, 0x8017e60, 0x801c3fc, ...
# disassemble around the code that loads from those pools (search ldr pc-relative resolving)
def find_ldr_refs(target):
    hits = []
    for off in range(0, len(img) - 2, 2):
        hw = struct.unpack_from("<H", img, off)[0]
        # ldr rN, [pc, #imm]  : 01001 NNN iiiiiiii
        if (hw & 0xF800) != 0x4800:
            continue
        imm = (hw & 0xFF) * 4
        pc = BASE + off
        addr = ((pc + 4) & ~3) + imm
        if addr == target:
            hits.append(pc)
    return hits

for tgt, name in ((0x08017988, "tick@0x8017988"), (0x08017e60, "tick@0x8017e60"),
                  (0x0801c3fc, "tick@0x801c3fc")):
    print(f"\n== ldr sites for literal {name} ==")
    for pc in find_ldr_refs(tgt):
        print(f"  {pc:#x}")

# writers of 0x2000010c: search for str rN,[rM] patterns is hard; instead list ldr refs to its literal pools
print("\n== ldr sites for 0x2000010c literals (mode global) ==")
pools = (0x080141f4, 0x080182a4, 0x08018b1c, 0x0801f70c)
for p in pools:
    for pc in find_ldr_refs(p):
        print(f"  pool {p:#x} loaded at {pc:#x}")
