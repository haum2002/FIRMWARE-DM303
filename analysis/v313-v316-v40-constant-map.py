#!/usr/bin/env python3
"""Three-way constant map: DM303 V3.13 vs V3.16 vs V4.0.

Read-only analysis. Scans the three firmware images for the timing/guard
constants implicated in the ammeter AC<->DC switch path and maps their
occurrence clusters per firmware.

Also scans for the DM30XDB1.dat resource-path string (ASCII + UTF-16LE).

Run from repo root with the portable Python:
    tools/_py/python.exe analysis/v313-v316-v40-constant-map.py
"""

from __future__ import annotations

import hashlib
import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x08010000

IMAGES = {
    "v3.13": Path(r"backup/SD-file_DM303_update_US240104-read only/DM303-V3.13.bin"),
    "v3.16": Path(r"backup/DM303 V3.16-read only/DM303V316.bin"),
    "v4.0": Path(r"backup/DM303 V4.0-read only/DM303V4.004.bin"),
}

# Constants to watch (decimal, hex). These are the settle/guard/sample
# constants seen in the V4.0 switching path plus nearby candidates.
WATCH = {
    0x40: "64 (patched sample window)",
    0x64: "100",
    0x6E: "110 (thr)",
    0x96: "150 (thr)",
    0xF0: "240 (official sample window)",
    0x118: "280 (thr)",
    0x12C: "300 (loop count)",
    0x15E: "350 (thr)",
    0x3E8: "1000",
    0x44C: "1100 (thr)",
    0x514: "1300 (thr)",
    0x5DC: "1500 (patched guard)",
    0x640: "1600 (patched gate)",
    0x1388: "5000",
    0x2710: "10000",
    0x3A98: "15000 (official guard)",
    0x3E80: "16000 (official gate)",
    0x4E20: "20000",
    0x7530: "30000",
}


def movw_encoding(imm16: int, rd: int) -> bytes:
    imm4 = (imm16 >> 12) & 0xF
    i = (imm16 >> 11) & 1
    imm3 = (imm16 >> 8) & 7
    imm8 = imm16 & 0xFF
    hw1 = 0xF240 | (i << 10) | imm4
    hw2 = (imm3 << 12) | (rd << 8) | imm8
    return struct.pack("<HH", hw1, hw2)


def movs_encoding(imm8: int, rd: int) -> bytes:
    return struct.pack("<H", 0x2000 | (rd << 8) | imm8)


def find_all(data: bytes, pat: bytes) -> list[int]:
    out = []
    start = 0
    while True:
        idx = data.find(pat, start)
        if idx < 0:
            return out
        out.append(idx)
        start = idx + 1


def scan_raw_patterns(name: str, data: bytes) -> dict[str, list[int]]:
    """Alignment-independent byte scan for movw/movs encodings."""
    results: dict[str, list[int]] = {}
    for imm, label in WATCH.items():
        if imm > 0xFF:
            for rd in range(16):
                pat = movw_encoding(imm, rd)
                for off in find_all(data, pat):
                    key = f"movw r{rd},#{imm} ({label})"
                    results.setdefault(key, []).append(off)
        else:
            for rd in range(8):
                pat = movs_encoding(imm, rd)
                for off in find_all(data, pat):
                    key = f"movs r{rd},#{imm} ({label})"
                    results.setdefault(key, []).append(off)
    return results


def capstone_sweep(data: bytes) -> list[tuple[int, str, int]]:
    """Linear sweep; returns (file_off, text, imm) for instructions whose
    immediate is in the watch set, plus pc-literal ldr hits."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = False
    hits: list[tuple[int, str, int]] = []
    off = 0x200  # skip vector table
    n = len(data)
    while off < n - 4:
        chunk = data[off : off + 16]
        insns = list(md.disasm(chunk, BASE + off, count=1))
        if not insns:
            off += 2
            continue
        insn = insns[0]
        mnem = insn.mnemonic
        ops = insn.op_str
        imm_val = None
        if mnem in ("movw", "movs", "mov.w", "cmp", "cmp.w", "mov"):
            m = re.search(r"#(0x[0-9a-f]+|\d+)", ops)
            if m:
                imm_val = int(m.group(1), 0)
        elif mnem.startswith("ldr") and "[pc" in ops:
            m = re.search(r"\[pc, #(0x[0-9a-f]+|\d+)\]", ops)
            if m:
                lit_addr = (insn.address + 4) & ~3
                lit_addr += int(m.group(1), 0)
                lit_off = lit_addr - BASE
                if 0 <= lit_off < n - 4:
                    imm_val = struct.unpack_from("<I", data, lit_off)[0]
        if imm_val in WATCH:
            hits.append((off, f"{insn.address:#010x}: {mnem} {ops}", imm_val))
        off += insn.size
    return hits


def cluster(offsets: list[int], gap: int = 0x100) -> list[list[int]]:
    if not offsets:
        return []
    offsets = sorted(offsets)
    groups = [[offsets[0]]]
    for o in offsets[1:]:
        if o - groups[-1][-1] <= gap:
            groups[-1].append(o)
        else:
            groups.append([o])
    return groups


def main() -> None:
    images = {}
    for name, path in IMAGES.items():
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        sp, reset = struct.unpack_from("<II", data, 0)
        images[name] = data
        print(f"== {name}: {path}")
        print(f"   size={len(data)} sha256={sha}")
        print(f"   SP={sp:#010x} reset={reset:#010x} (reset file off {reset - BASE - 1:#x})")

    print("\n=== RAW PATTERN SCAN (alignment-independent) ===")
    raw = {}
    for name, data in images.items():
        print(f"\n--- {name} ---")
        res = scan_raw_patterns(name, data)
        raw[name] = res
        # Only print the guard/sample constants, not the small thresholds
        for key in sorted(res):
            offs = res[key]
            if any(c in key for c in ("15000", "1500 ", "16000", "240 ", "64 ", "30000", "20000", "10000", "5000", "1000")):
                print(f"  {key}: {len(offs)} hits at {[hex(o) for o in offs]}")

    print("\n=== CAPSTONE SWEEP: watch-immediate instructions ===")
    sweep = {}
    for name, data in images.items():
        print(f"\n--- {name} ---")
        hits = capstone_sweep(data)
        sweep[name] = hits
        by_cluster = cluster([h[0] for h in hits], gap=0x80)
        for grp in by_cluster:
            lo, hi = grp[0], grp[-1]
            members = [h for h in hits if lo <= h[0] <= hi]
            print(f"  cluster file {lo:#07x}..{hi:#07x} (addr {BASE+lo:#010x}..{BASE+hi:#010x}):")
            for off, text, imm in members:
                print(f"    off={off:#07x} {text}")

    print("\n=== DM30XDB1.dat string scan ===")
    for name, data in images.items():
        ascii_hits = [hex(m.start()) for m in re.finditer(rb"DM30XDB1\.dat", data)]
        utf16_hits = [hex(m.start()) for m in re.finditer(rb"D\x00M\x003\x000\x00X\x00D\x00B\x001\x00", data)]
        loading = [hex(m.start()) for m in re.finditer(rb"Loading DM30XDB1", data)]
        print(f"  {name}: ascii={ascii_hits} utf16={utf16_hits} loading_msg={loading}")

    print("\n=== key guard offsets cross-check (V4.0 known patch sites) ===")
    v40 = images["v4.0"]
    for off in (0x14B0E, 0x14B36, 0x15934, 0x1595C, 0x1D1A4, 0x1D1C0, 0x1D1DA, 0x1585E, 0x15888):
        print(f"  v4.0 off {off:#07x}: {v40[off:off+4].hex(' ')}")


if __name__ == "__main__":
    main()
