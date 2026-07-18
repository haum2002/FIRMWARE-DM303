# DM303 V4.0 AC->DC latency hunt — disassembly probes (read-only on backup/)
# Runs with tools/_py/python.exe (capstone 5.0.7)
import struct, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent.parent
V40 = ROOT / "backup" / "DM303 V4.0-read only" / "DM303V4.004.bin"
V316 = ROOT / "backup" / "DM303 V3.16-read only" / "DM303V316.bin"
BASE = 0x08010000

def load(p):
    return p.read_bytes()

img = load(V40)
img316 = load(V316)

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
md.detail = False

def disas(data, addr, count=200):
    out = []
    for ins in md.disasm(data, addr):
        out.append(f"{ins.address:08x}: {ins.bytes.hex():<9} {ins.mnemonic} {ins.op_str}")
        if len(out) >= count:
            break
    return out

def region(buf, start, end):
    off = start - BASE
    return buf[off:end - BASE]

def dump(title, buf, start, end):
    print(f"\n===== {title} {start:#x}-{end:#x} =====")
    for line in disas(region(buf, start, end), start, (end - start) // 2):
        print(line)

# ---- 1. rate/setup helper called at ammeter entry
dump("V4.0 helper 0x08017ed8 full", img, 0x08017ed8, 0x08018060)
# ---- 2. 0x080170dc (called at ammeter entry and at re-kick)
dump("V4.0 helper 0x080170dc", img, 0x080170dc, 0x080171de)
# ---- 3. 0x0801d18c (get state) and around
dump("V4.0 helper 0x0801d18c", img, 0x0801d18c, 0x0801d220)
# ---- 4. 0x0802603a / 0x0802600c (direction-B query / exit check)
dump("V4.0 helper 0x0802603a", img, 0x0802603a, 0x080260d0)
dump("V4.0 helper 0x0802600c", img, 0x0802600c, 0x0802603a)
# ---- 5. 0x08017ad4 (delay fn candidate)
dump("V4.0 helper 0x08017ad4", img, 0x08017ad4, 0x08017b60)
