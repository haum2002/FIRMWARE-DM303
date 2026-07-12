#!/usr/bin/env python3
"""Create a direct DM303 V4.0.1 beta firmware candidate.

This patcher does not modify the source firmware in place. It emits a new
candidate binary and a byte-level report so every change can be audited before
any device-side test.
"""

from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


SOURCE = Path("DM303-V4.0/DM303V4.004.bin")
MS_TEXT = Path("localization/ms_MY/TEXT_MS.DAT")
OUT_DIR = Path("firmware-candidates/v4.0.1-beta")
OUT_BIN = OUT_DIR / "DM303V4.0.1-beta.bin"
OUT_SYSTEM = OUT_DIR / "system"
OUT_REPORT = OUT_DIR / "PATCH-REPORT.md"
OUT_SUMS = OUT_DIR / "SHA256SUMS.txt"

LOAD_BASE = 0x08010000
SOURCE_SHA256 = "64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158"
FAULT_BLOCK_OFFSET = 0x7554
FAULT_BLOCK_SIZE = 20
FAULT_STUB_VECTOR = 0x08017555
VECTOR_WORDS = 80

ORIGINAL_FAULT_BLOCK = bytes.fromhex("fe e7 " * 10)

# Thumb code at 0x08017554:
#   ldr r0, [pc, #8]      ; r0 = 0xE000ED0C (SCB AIRCR)
#   ldr r1, [pc, #8]      ; r1 = 0x05FA0004 (VECTKEY | SYSRESETREQ)
#   str r1, [r0]
#   dsb sy
#   b .
#   .word 0xE000ED0C
#   .word 0x05FA0004
FAULT_RESET_STUB = (
    bytes.fromhex("02 48 02 49 01 60 bf f3 4f 8f fe e7")
    + (0xE000ED0C).to_bytes(4, "little")
    + (0x05FA0004).to_bytes(4, "little")
)

VERSION_PATCHES = {
    0x02CA0: b"V4.0.1 beta\x00\x00\x00\x00\x00",
    0x02CB0: b"V4.0.1 beta\x00\x00\x00\x00\x00",
}


@dataclass(frozen=True)
class PatchRecord:
    offset: int
    before: bytes
    after: bytes
    reason: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def u32_at(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "little")


def patch_bytes(image: bytearray, offset: int, after: bytes, reason: str) -> PatchRecord:
    before = bytes(image[offset : offset + len(after)])
    image[offset : offset + len(after)] = after
    return PatchRecord(offset, before, after, reason)


def find_self_loop_vectors(data: bytes) -> list[int]:
    vector_offsets: list[int] = []
    for index in range(1, min(VECTOR_WORDS, len(data) // 4)):
        entry_offset = index * 4
        value = u32_at(data, entry_offset)
        target = (value & ~1) - LOAD_BASE
        if not (0 <= target + 2 <= len(data)):
            continue
        if data[target : target + 2] != b"\xfe\xe7":
            continue
        if FAULT_BLOCK_OFFSET <= target < FAULT_BLOCK_OFFSET + FAULT_BLOCK_SIZE:
            vector_offsets.append(entry_offset)
    return vector_offsets


def write_report(records: list[PatchRecord], source_data: bytes, output_data: bytes) -> None:
    lines = [
        "# DM303 V4.0.1 beta patch report",
        "",
        "Status: candidate firmware only. Bench validation is still required before flashing.",
        "",
        "## Safety scope",
        "",
        "- Source firmware is not modified in place.",
        "- Output binary size is unchanged.",
        "- Bootloader/updater code and SD update procedure are not patched.",
        "- Fault/default self-loop handlers are redirected to a hardware reset request.",
        "- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`.",
        "- True add-only language menu activation is not patched yet because the hardcoded language table has no confirmed spare slot.",
        "",
        "## Hashes",
        "",
        f"- Source SHA-256: `{sha256_bytes(source_data)}`",
        f"- Output SHA-256: `{sha256_bytes(output_data)}`",
        f"- Source size: `{len(source_data)}` bytes",
        f"- Output size: `{len(output_data)}` bytes",
        "",
        "## Byte patches",
        "",
        "| Offset | Size | Before | After | Reason |",
        "|---:|---:|---|---|---|",
    ]
    for record in records:
        lines.append(
            f"| `0x{record.offset:05x}` | {len(record.after)} | "
            f"`{record.before.hex(' ')}` | `{record.after.hex(' ')}` | "
            f"{record.reason} |"
        )

    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    source_data = SOURCE.read_bytes()
    source_hash = sha256_bytes(source_data)
    if source_hash != SOURCE_SHA256:
        raise SystemExit(
            f"Refusing to patch unexpected source hash: {source_hash}"
        )

    if source_data[FAULT_BLOCK_OFFSET : FAULT_BLOCK_OFFSET + FAULT_BLOCK_SIZE] != ORIGINAL_FAULT_BLOCK:
        raise SystemExit("Refusing to patch: fault handler block does not match expected V4.0 bytes")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SYSTEM.mkdir(parents=True, exist_ok=True)

    image = bytearray(source_data)
    records: list[PatchRecord] = []

    vector_offsets = find_self_loop_vectors(source_data)
    if not vector_offsets:
        raise SystemExit("No self-loop vectors found; refusing to patch")

    for entry_offset in vector_offsets:
        before_value = u32_at(source_data, entry_offset)
        if before_value == FAULT_STUB_VECTOR:
            continue
        records.append(
            patch_bytes(
                image,
                entry_offset,
                FAULT_STUB_VECTOR.to_bytes(4, "little"),
                "redirect self-loop exception/IRQ vector to shared reset-recovery stub",
            )
        )

    records.append(
        patch_bytes(
            image,
            FAULT_BLOCK_OFFSET,
            FAULT_RESET_STUB,
            "replace permanent fault/default loops with SCB_AIRCR SYSRESETREQ stub",
        )
    )

    for offset, replacement in VERSION_PATCHES.items():
        records.append(
            patch_bytes(
                image,
                offset,
                replacement,
                "mark candidate UI/version string as V4.0.1 beta",
            )
        )

    output_data = bytes(image)
    OUT_BIN.write_bytes(output_data)

    if MS_TEXT.exists():
        shutil.copy2(MS_TEXT, OUT_SYSTEM / "TEXT_MS.DAT")

    write_report(records, source_data, output_data)

    sums = [
        f"{sha256_file(OUT_BIN)}  {OUT_BIN.name}",
    ]
    ms_candidate = OUT_SYSTEM / "TEXT_MS.DAT"
    if ms_candidate.exists():
        sums.append(f"{sha256_file(ms_candidate)}  system/TEXT_MS.DAT")
    OUT_SUMS.write_text("\n".join(sums) + "\n", encoding="utf-8")

    print(f"source={SOURCE}")
    print(f"source_sha256={source_hash}")
    print(f"output={OUT_BIN}")
    print(f"output_size={len(output_data)}")
    print(f"output_sha256={sha256_file(OUT_BIN)}")
    print(f"patched_vectors={len(vector_offsets)}")
    print(f"patch_records={len(records)}")
    print(f"report={OUT_REPORT}")
    print("safety_note=candidate only; do not flash before bench/recovery validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
