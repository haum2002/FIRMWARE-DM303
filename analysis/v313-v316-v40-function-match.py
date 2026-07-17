#!/usr/bin/env python3
"""Three-way function matching: DM303 V3.13 vs V3.16 vs V4.0.

Read-only analysis. Locates the V3.13/V3.16 counterparts of the V4.0
ammeter screen function (0x0802d194) and the mode/range helper cluster
(0x0801f19a / selector 0x0801f0f2), then dumps comparable disassembly
windows to docs/ for the switching-path comparison.

Run from repo root:
    tools/_py/python.exe analysis/v313-v316-v40-function-match.py
"""

from __future__ import annotations

import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x08010000

IMAGES = {
    "v3.13": Path(r"backup/SD-file_DM303_update_US240104-read only/DM303-V3.13.bin"),
    "v3.16": Path(r"backup/DM303 V3.16-read only/DM303V316.bin"),
    "v4.0": Path(r"backup/DM303 V4.0-read only/DM303V4.004.bin"),
}

md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)


def disasm_window(data: bytes, off: int, length: int) -> list[str]:
    """Linear disassembly of [off, off+length); resyncs +2 on failure."""
    lines = []
    end = min(off + length, len(data))
    p = off
    while p < end:
        chunk = data[p : p + 16]
        insns = list(md.disasm(chunk, BASE + p, count=1))
        if not insns:
            lines.append(f"{BASE+p:08x}: {data[p]:02x} {data[p+1]:02x}        <decode-fail>")
            p += 2
            continue
        insn = insns[0]
        raw = data[p : p + insn.size].hex(" ")
        lines.append(f"{insn.address:08x}: {raw:<14} {insn.mnemonic} {insn.op_str}")
        p += insn.size
    return lines


def bl_targets(data: bytes, off: int, length: int) -> list[tuple[int, int]]:
    """All bl instructions and their targets in a window."""
    out = []
    end = min(off + length, len(data))
    p = off
    while p < end:
        chunk = data[p : p + 16]
        insns = list(md.disasm(chunk, BASE + p, count=1))
        if not insns:
            p += 2
            continue
        insn = insns[0]
        if insn.mnemonic == "bl":
            tgt = int(insn.op_str.replace("#", ""), 16)
            out.append((insn.address, tgt))
        p += insn.size
    return out


def find_fn_start(data: bytes, anchor: int, max_back: int = 0x600) -> int:
    """Heuristic: walk backwards from anchor for a push prologue whose
    preceding halfword looks like a return/pool boundary."""
    best = None
    p = anchor - 2
    stop = anchor - max_back
    while p > stop:
        hw = struct.unpack_from("<H", data, p)[0]
        # push {..lr}: 0xb5xx ; push.w: 0x2de9
        if (hw & 0xFF00) == 0xB500 or hw == 0xE92D or hw == 0xB510:
            prev2 = struct.unpack_from("<H", data, p - 2)[0]
            # common tails: bx lr (0x4770), pop {..pc} (0xbdxx), b <..> (0xe000-0xe7ff), pool (0x0000)
            if (prev2 & 0xFF00) in (0xBD00, 0xBC00) or prev2 in (0x4770, 0x46C0) or (prev2 & 0xF000) == 0xE000 or prev2 == 0x0000:
                best = p
        p -= 2
    return best if best is not None else anchor


def main() -> None:
    imgs = {k: v.read_bytes() for k, v in IMAGES.items()}

    print("== byte identity check: V3.16 known anchors vs V3.13 same addresses ==")
    for name, addr in (("selector", 0x0801E1AC), ("helper", 0x0801E254), ("mode_routine", 0x0801E29A)):
        off = addr - BASE
        a = imgs["v3.13"][off : off + 64]
        b = imgs["v3.16"][off : off + 64]
        print(f"  {name} @ {addr:#010x}: v3.13==v3.16 first64 = {a == b}")

    # bl targets inside each firmware's guard cluster -> mode routine
    print("\n== bl targets inside the 0x3a98/0x3e80 guard clusters ==")
    clusters = {
        "v3.13": [0x14000, 0x14D12],
        "v3.16": [0x142B0, 0x14FB0],
        "v4.0":  [0x14AB0, 0x157B0],
    }
    for name, starts in clusters.items():
        for s in starts:
            tgts = bl_targets(imgs[name], s, 0x200)
            uniq = {}
            for site, tgt in tgts:
                uniq.setdefault(tgt, []).append(site)
            print(f"  {name} cluster @{s:#07x}:")
            for tgt, sites in sorted(uniq.items()):
                print(f"    bl -> {tgt:#010x}  from {[hex(x) for x in sites]}")

    # ammeter function windows
    print("\n== ammeter function disassembly (window around the 0x3a98 anchor) ==")
    amm = {
        "v3.13": 0x1D526,
        "v3.16": 0x1D7DE,
        "v4.0":  0x1D1A4,
    }
    out_files = {}
    for name, anchor in amm.items():
        data = imgs[name]
        start = find_fn_start(data, anchor)
        print(f"  {name}: anchor {anchor:#07x}, fn_start_guess {BASE+start:#010x}")
        lines = disasm_window(data, start, 0x320)
        out_files[name] = lines
        bls = bl_targets(data, start, 0x320)
        for site, tgt in bls:
            print(f"    bl @{site:#010x} -> {tgt:#010x}")

    for name, lines in out_files.items():
        tag = name.replace(".", "")
        path = Path(f"docs/disasm-{tag}-ammeter-fn.txt")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  wrote {path}")

    # mode routine disasm (first 0x200 bytes) for the three firmwares
    mode = {
        "v3.13": 0x0801E29A,  # provisional: same as v3.16, verified by byte check
        "v3.16": 0x0801E29A,
        "v4.0":  0x0801F19A,
    }
    for name, addr in mode.items():
        off = addr - BASE
        lines = disasm_window(imgs[name], off, 0x200)
        tag = name.replace(".", "")
        path = Path(f"docs/disasm-{tag}-mode-routine.txt")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
