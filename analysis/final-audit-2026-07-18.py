#!/usr/bin/env python3
"""Independent final audit of the DM303 V4.0.1o/p/q/r packages.

Fresh byte-level analysis written 2026-07-18, extended from
final-audit-2026-07-17.py. Deliberately does NOT import the project checker
modules: every expectation below is re-derived from the official V4.0 backup
and from first-principles Thumb-2 decoding, so the audit fails loudly if any
earlier assumption was wrong. Read-only against backup/.

Run from repo root with any stdlib Python 3:
    python analysis/final-audit-2026-07-18.py
"""

from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFICIAL_BIN = ROOT / "backup/DM303 V4.0-read only/DM303V4.004.bin"
OFFICIAL_SYS = ROOT / "backup/DM303 V4.0-read only/system"
US_UPDATE_SYS = ROOT / "backup/SD-file_DM303_update_US240104-read only/system"
REPAIR_ROOT = ROOT / "dm303_firmware/DM303-V4.0.1-beta"
UIM_ROOT = ROOT / "dm303_firmware/DM303-V4.0.1p-ms-beta"
REPAIR_J_ROOT = ROOT / "dm303_firmware/DM303-V4.0.1q-beta"
COMBINED_ROOT = ROOT / "dm303_firmware/DM303-V4.0.1r-beta"
CHECKSUMS = ROOT / "CHECKSUMS-SHA256.txt"

EXPECTED_OFFICIAL_SHA256 = (
    "64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158"
)
EXPECTED_REPAIR_I_SHA256 = (
    "11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953"
)
EXPECTED_UI_MS_SHA256 = (
    "a26edd279ae15a68c3f819b1e2dac10d91043a45f6faac64aa0bdfa504f38878"
)
EXPECTED_REPAIR_J_SHA256 = (
    "ecd7b5dc85158467ce9e2ffc8b71fd1523c934383c7d1e6677b7bd0f79e34642"
)
EXPECTED_COMBINED_SHA256 = (
    "e75f8cbd8657c9a72f84ce454d5fc43298aead48c4053df00946eae3f99faf8c"
)

FAILURES: list[str] = []


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(ok: bool, label: str, detail: str = "") -> None:
    mark = "ok" if ok else "FAIL"
    line = f"[{mark}] {label}"
    if detail:
        line += f" :: {detail}"
    print(line)
    if not ok:
        FAILURES.append(label)


def diff_ranges(base: bytes, other: bytes) -> list[tuple[int, int]]:
    assert len(base) == len(other), "size mismatch"
    ranges: list[list[int]] = []
    for i in range(len(base)):
        if base[i] != other[i]:
            if ranges and i == ranges[-1][1] + 1:
                ranges[-1][1] = i
            else:
                ranges.append([i, i])
    return [(s, e) for s, e in ranges]


def decode_movw(word4: bytes) -> tuple[int, int] | None:
    """Decode a Thumb-2 MOVW; return (rd, imm16) or None if not MOVW."""
    hw1 = word4[0] | (word4[1] << 8)
    hw2 = word4[2] | (word4[3] << 8)
    if hw1 & 0xFBF0 != 0xF240:
        return None
    imm4 = hw1 & 0x000F
    i = (hw1 >> 10) & 1
    imm3 = (hw2 >> 12) & 0x7
    rd = (hw2 >> 8) & 0xF
    imm8 = hw2 & 0xFF
    return rd, (imm4 << 12) | (i << 11) | (imm3 << 8) | imm8


def main() -> int:
    official = OFFICIAL_BIN.read_bytes()
    repair = (REPAIR_ROOT / "DM303V4.0.1-beta.bin").read_bytes()
    uims = (UIM_ROOT / "DM303V4.0.1-beta.bin").read_bytes()
    repairj = (REPAIR_J_ROOT / "DM303V4.0.1-beta.bin").read_bytes()
    combined = (COMBINED_ROOT / "DM303V4.0.1-beta.bin").read_bytes()

    print("== A. source integrity ==")
    check(sha256(official) == EXPECTED_OFFICIAL_SHA256, "official V4.0 backup SHA-256")
    check(len(official) == len(repair) == len(uims) == len(repairj) == len(combined) == 203260,
          "firmware sizes 203260")
    check(sha256(repair) == EXPECTED_REPAIR_I_SHA256, "repair-i (V4.0.1o) SHA-256")
    check(sha256(uims) == EXPECTED_UI_MS_SHA256, "ui-ms (V4.0.1p) SHA-256")
    check(sha256(repairj) == EXPECTED_REPAIR_J_SHA256, "repair-j (V4.0.1q) SHA-256")
    check(sha256(combined) == EXPECTED_COMBINED_SHA256, "repair-j-ui-ms (V4.0.1r) SHA-256")

    print("== B. repair-i vs official: full diff ==")
    expected_diff = [
        (0x02CAC, 0x02CAE), (0x02CBC, 0x02CBE),
        (0x14B0E, 0x14B11), (0x14B36, 0x14B39),
        (0x15812, 0x15813), (0x15838, 0x15839),
        (0x15860, 0x15863), (0x1588A, 0x1588D),
        (0x15934, 0x15937), (0x1595C, 0x1595F),
        (0x1D1A4, 0x1D1A7), (0x1D1C0, 0x1D1C3),
        (0x1D1DA, 0x1D1DA),
    ]
    actual = diff_ranges(official, repair)
    check(actual == expected_diff, "repair-i diff set == documented 13 ranges",
          f"actual={[(hex(s), hex(e)) for s, e in actual]}")

    print("== C. MOVW guard patches decode (0x3a98 -> 0x05dc, same rd) ==")
    for off in (0x14B0E, 0x14B36, 0x15934, 0x1595C, 0x1D1A4, 0x1D1C0):
        old = decode_movw(official[off:off + 4])
        new = decode_movw(repair[off:off + 4])
        ok = (old is not None and new is not None
              and old[1] == 0x3A98 and new[1] == 0x05DC and old[0] == new[0])
        check(ok, f"movw at 0x{off:05x}", f"old={old} new={new}")

    print("== D. acquisition window patch ==")
    check(official[0x1D1DA:0x1D1DC] == bytes.fromhex("f0 20"),
          "official 0x1d1da is movs r0,#0xf0 (240)", official[0x1D1DA:0x1D1DC].hex(" "))
    check(repair[0x1D1DA:0x1D1DC] == bytes.fromhex("40 20"),
          "patched 0x1d1da is movs r0,#0x40 (64)", repair[0x1D1DA:0x1D1DC].hex(" "))

    print("== E. NOP patches: show what official had ==")
    for off in (0x15812, 0x15838, 0x15862, 0x1588C):
        check(repair[off:off + 2] == bytes.fromhex("00 bf"), f"0x{off:05x} patched to NOP",
              f"official={official[off:off + 2].hex(' ')}")
    print("== F. cmp-immediate regions 0x1585e / 0x15888 ==")
    for off in (0x1585E, 0x15888):
        print(f"     0x{off:05x}: official={official[off:off + 4].hex(' ')} "
              f"patched={repair[off:off + 4].hex(' ')}")
        check(repair[off:off + 4] == bytes.fromhex("b0 f5 c8 6f"),
              f"0x{off:05x} patched cmp.w r0")

    print("== G. safety fail-stop vectors unchanged ==")
    for off in (0x09CA0, 0x0C6C8, 0x2C4EA):
        check(all(fw[off:off + 2] == bytes.fromhex("fe e7")
                  for fw in (official, repair, uims, repairj, combined)),
              f"fail-stop b. at 0x{off:05x} official in all builds")

    print("== H. ui-ms vs repair-i: only marker + Melayu menu name ==")
    delta = diff_ranges(repair, uims)
    expected_delta = [(0x02CAE, 0x02CAE), (0x02CBE, 0x02CBE),
                      (0x25BF8, 0x25BFA), (0x25BFC, 0x25BFE)]
    check(delta == expected_delta, "ui-ms delta == 8 bytes",
          f"actual={[(hex(s), hex(e)) for s, e in delta]}")
    check(uims[0x25BF8:0x25C00] == b"Melayu \x00", "menu name Melayu",
          repr(uims[0x25BF8:0x25C00]))

    print("== I. version strings ==")
    check(repair[0x02CA0:0x02CB0] == b"MT100MM V4.0.1o\x00", "repair-i MT marker",
          repr(repair[0x02CA0:0x02CB0]))
    check(repair[0x02CB0:0x02CC0] == b"BT100MM V4.0.1o\x00", "repair-i BT marker")
    check(uims[0x02CA0:0x02CB0] == b"MT100MM V4.0.1p\x00", "ui-ms MT marker")
    check(uims[0x02CB0:0x02CC0] == b"BT100MM V4.0.1p\x00", "ui-ms BT marker")
    check(repairj[0x02CA0:0x02CB0] == b"MT100MM V4.0.1q\x00", "repair-j MT marker")
    check(repairj[0x02CB0:0x02CC0] == b"BT100MM V4.0.1q\x00", "repair-j BT marker")
    check(combined[0x02CA0:0x02CB0] == b"MT100MM V4.0.1r\x00", "combined MT marker")
    check(combined[0x02CB0:0x02CC0] == b"BT100MM V4.0.1r\x00", "combined BT marker")

    print("== J. repair-j vs official: full diff ==")
    expected_j = [
        (0x02CAC, 0x02CAE), (0x02CBC, 0x02CBE),
        (0x1DF0C, 0x1DF0F), (0x1DF40, 0x1DF43),
    ]
    actual_j = diff_ranges(official, repairj)
    check(actual_j == expected_j, "repair-j diff set == documented 4 ranges",
          f"actual={[(hex(s), hex(e)) for s, e in actual_j]}")

    print("== K. repair-j AC/DC switch-window patches decode ==")
    # Official uses the imm12 MOV.W form: 4f f4 16 70 = mov.w r0,#0x258 (600),
    # 4f f4 b4 70 = mov.w r0,#0x168 (360). Patched form is MOVW r0,#0xf0 (240).
    check(official[0x1DF0C:0x1DF10] == bytes.fromhex("4f f4 16 70"),
          "official 0x1df0c is mov.w r0,#0x258 (600)", official[0x1DF0C:0x1DF10].hex(" "))
    check(official[0x1DF40:0x1DF44] == bytes.fromhex("4f f4 b4 70"),
          "official 0x1df40 is mov.w r0,#0x168 (360)", official[0x1DF40:0x1DF44].hex(" "))
    for off in (0x1DF0C, 0x1DF40):
        for name, fw in (("repair-j", repairj), ("combined", combined)):
            decoded = decode_movw(fw[off:off + 4])
            check(decoded == (0, 0xF0), f"{name} 0x{off:05x} decodes movw r0,#0xf0 (240)",
                  f"bytes={fw[off:off + 4].hex(' ')} decoded={decoded}")

    print("== L. combined vs repair-j: only marker + Melayu menu name ==")
    delta_rc = diff_ranges(repairj, combined)
    expected_rc = [(0x02CAE, 0x02CAE), (0x02CBE, 0x02CBE),
                   (0x25BF8, 0x25BFA), (0x25BFC, 0x25BFE)]
    check(delta_rc == expected_rc, "combined-vs-repair-j delta == 8 bytes",
          f"actual={[(hex(s), hex(e)) for s, e in delta_rc]}")
    check(combined[0x25BF8:0x25C00] == b"Melayu \x00", "combined menu name Melayu",
          repr(combined[0x25BF8:0x25C00]))

    print("== M. combined vs official: full diff ==")
    expected_c = [
        (0x02CAC, 0x02CAE), (0x02CBC, 0x02CBE),
        (0x1DF0C, 0x1DF0F), (0x1DF40, 0x1DF43),
        (0x25BF8, 0x25BFA), (0x25BFC, 0x25BFE),
    ]
    actual_c = diff_ranges(official, combined)
    check(actual_c == expected_c, "combined diff set == 6 ranges (20 bytes)",
          f"actual={[(hex(s), hex(e)) for s, e in actual_c]}")

    print("== N. repair-i sd-root resources ==")
    overlay_names = {"TEXT_SP.DAT", "icon-SP.dat"}
    overlay_names |= {f"icon-C{i}.bmp" for i in range(1, 17)}
    overlay_names |= {f"icon-E{i}.bmp" for i in range(1, 19)}
    audit_sd_root(REPAIR_ROOT, expect_overlay=False, overlay_names=overlay_names)

    print("== O. repair-j sd-root resources ==")
    audit_sd_root(REPAIR_J_ROOT, expect_overlay=False, overlay_names=overlay_names)

    print("== P. ui-ms sd-root resources ==")
    audit_sd_root(UIM_ROOT, expect_overlay=True, overlay_names=overlay_names)

    print("== Q. combined sd-root resources ==")
    audit_sd_root(COMBINED_ROOT, expect_overlay=True, overlay_names=overlay_names)

    print("== R. TEXT_SP.DAT structure (ui-ms + combined) ==")
    audit_text_dat(OFFICIAL_SYS / "TEXT_SP.DAT", UIM_ROOT / "system/TEXT_SP.DAT", "ui-ms")
    audit_text_dat(OFFICIAL_SYS / "TEXT_SP.DAT", COMBINED_ROOT / "system/TEXT_SP.DAT", "combined")

    print("== S. overlay BMP layout (ui-ms + combined) ==")
    for name in sorted(n for n in overlay_names if n.endswith(".bmp")):
        audit_bmp(UIM_ROOT / "system" / name)
        audit_bmp(COMBINED_ROOT / "system" / name)
    check(sha256((UIM_ROOT / "system/icon-SP.dat").read_bytes())
          == sha256((COMBINED_ROOT / "system/icon-SP.dat").read_bytes())
          == "4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8",
          "icon-SP.dat dark pack identical in both overlay packages")

    print("== T. CHECKSUMS-SHA256.txt matches disk ==")
    bad = 0
    for line in CHECKSUMS.read_text().splitlines():
        if not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        if sha256((ROOT / rel).read_bytes()) != digest:
            bad += 1
            print(f"     mismatch: {rel}")
    check(bad == 0, "all checksum entries match")

    print()
    if FAILURES:
        print(f"AUDIT FAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("AUDIT PASSED: all independent checks ok")
    return 0


def audit_sd_root(root: Path, expect_overlay: bool, overlay_names: set[str]) -> None:
    official_files = {p.name: p for p in OFFICIAL_SYS.iterdir() if p.is_file()}
    cand_sys = root / "system"
    cand_names = {p.name for p in cand_sys.iterdir() if p.is_file()}
    expected_names = set(official_files) | {"DM30XDB1.dat"}
    check(cand_names == expected_names, f"{root.name}: file set == official + DM30XDB1",
          f"extra={sorted(cand_names - expected_names)} missing={sorted(expected_names - cand_names)}")
    us_dm30 = US_UPDATE_SYS / "DM30XDB1.dat"
    check(sha256((cand_sys / "DM30XDB1.dat").read_bytes()) == sha256(us_dm30.read_bytes()),
          f"{root.name}: DM30XDB1.dat == US240104 update copy")
    changed = []
    for name, off_path in official_files.items():
        if sha256((cand_sys / name).read_bytes()) != sha256(off_path.read_bytes()):
            changed.append(name)
    if expect_overlay:
        check(set(changed) == overlay_names, f"{root.name}: changed files == overlay set",
              f"changed={sorted(changed)}")
    else:
        check(changed == [], f"{root.name}: all official resources byte-identical",
              f"changed={sorted(changed)}")
    for extra in ("QBtest.txt", "readme.txt"):
        check((root / extra).read_bytes() == (ROOT / "backup/DM303 V4.0-read only" / extra).read_bytes(),
              f"{root.name}: {extra} == official")


def parse_text_dat(data: bytes) -> list[tuple[int, bytes]]:
    count = int.from_bytes(data[2:4], "big")
    entries = []
    for index in range(1, count + 1):
        entry_offset = 8 + (index - 1) * 8
        offset = int.from_bytes(data[entry_offset + 1:entry_offset + 5], "big")
        record_length = int.from_bytes(data[offset:offset + 2], "big")
        assert offset + record_length <= len(data), f"entry {index} out of bounds"
        entries.append((index, data[offset + 2:offset + record_length]))
    return entries


def audit_text_dat(official_path: Path, cand_path: Path, label: str) -> None:
    off_entries = parse_text_dat(official_path.read_bytes())
    cand_entries = parse_text_dat(cand_path.read_bytes())
    check(len(off_entries) == len(cand_entries) == 773, f"{label}: entry count 773 both files",
          f"official={len(off_entries)} candidate={len(cand_entries)}")
    replaced = 0
    too_long = []
    for (i, off_text), (j, cand_text) in zip(off_entries, cand_entries):
        if off_text != cand_text:
            replaced += 1
            if len(cand_text) > len(off_text):
                too_long.append(i)
    # Full-Malay rebuild 2026-07-17 (localization/ms_MY/translations_ms_sp_full.csv):
    # 757 entries translated to Malay, 16 unchanged (8 blank spacers, 5 pure
    # symbols/units, "Normal", "Hardware: "/"Software: " kept by convention).
    # Every translation is exactly its official entry's byte length, so the
    # rebuilt file keeps the official size and offset table byte-for-byte.
    check(replaced == 757, f"{label}: byte-differing entries == 757 (full Malay)",
          f"actual={replaced}")
    check(not too_long, f"{label}: no replacement longer than official slot",
          f"too_long={too_long[:10]}")
    off_data = official_path.read_bytes()
    cand_data = cand_path.read_bytes()
    check(len(off_data) == len(cand_data) == 32888, f"{label}: TEXT_SP.DAT size == official 32888")
    check(off_data[:6189] == cand_data[:6189], f"{label}: offset table byte-identical to official")
    check(sha256(cand_data) == "f955f4c83a57ac26150536a377f29b40c5d64fc5ceb2991e2c5fb7ef6c147fd9",
          f"{label}: TEXT_SP.DAT full-Malay SHA-256")


def audit_bmp(path: Path) -> None:
    data = path.read_bytes()
    ok = len(data) == 17000 and data[:2] == b"BM"
    if ok:
        file_size = struct.unpack_from("<I", data, 2)[0]
        pixel_offset = struct.unpack_from("<I", data, 10)[0]
        dib_size = struct.unpack_from("<I", data, 14)[0]
        width = struct.unpack_from("<i", data, 18)[0]
        height = struct.unpack_from("<i", data, 22)[0]
        planes = struct.unpack_from("<H", data, 26)[0]
        bpp = struct.unpack_from("<H", data, 28)[0]
        compression = struct.unpack_from("<I", data, 30)[0]
        masks = struct.unpack_from("<III", data, 54)
        ok = (file_size == 17000 and pixel_offset == 70 and dib_size == 56
              and width == 92 and height == -92 and planes == 1 and bpp == 16
              and compression == 3 and masks == (0xF800, 0x07E0, 0x001F))
    check(ok, f"BMP RGB565 layout {path.parent.parent.name}/{path.name}")


if __name__ == "__main__":
    sys.exit(main())
