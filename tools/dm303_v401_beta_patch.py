#!/usr/bin/env python3
"""Create a direct DM303 V4.0.1 beta firmware candidate.

This patcher does not modify the source firmware in place. It emits a new
candidate binary and a byte-level report so every change can be audited before
any device-side test.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


SOURCE = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
MS_TEXT = Path("localization/ms_MY/TEXT_MS.DAT")
SP_TEXT = Path("localization/ms_MY/TEXT_SP.ms-slot-replacement.DAT")
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

DEFAULT_PROFILE = "force-enhanced-exp4"
PROFILES = {
    "boot-acceptance": {
        "fault_reset": False,
        "runtime_patches": False,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "minimal beta identity and resource build",
    },
    "anti-freeze-exp1": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "reset on fault/default handler and return from known fail-stop loops",
    },
    "relay-settle-exp1": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp1",
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "anti-freeze plus longer relay/range settling delays for zeroing and mode changes",
    },
    "force-stable-exp2": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp2",
        "mode_switch_profile": None,
        "boot_logo_delay": False,
        "description": "exp1 plus stronger relay/range settling for unstable AC/DC current switching",
    },
    "v316-switch-exp3": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": None,
        "mode_switch_profile": "v316-helper-wrapper",
        "boot_logo_delay": False,
        "description": "anti-freeze plus V3.16-style mode-switch helper wrapper with official relay timing",
    },
    "force-enhanced-exp4": {
        "fault_reset": True,
        "runtime_patches": True,
        "relay_settle_profile": "exp2",
        "mode_switch_profile": "v316-helper-wrapper",
        "boot_logo_delay": True,
        "description": "force-enhanced stability profile with V3.16 mode wrapper, stronger relay settling, and boot-logo stabilization delay",
    },
}

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
    0x02CA0: b"MT100MM V4.0.1b\x00",
    0x02CB0: b"BT100MM V4.0.1b\x00",
}

LANGUAGE_NAME_PATCHES = {
    # Existing language-name table at 0x08035be4. The Spanish slot is reused
    # for Malay text/resources because no spare add-only slot is confirmed.
    # Keep the payload exactly seven bytes so the following entries do not move.
    0x25BF8: (
        b"Espa\xc3\xb1a",
        b"Melayu ",
        "rename existing Spanish language menu slot to Melayu without changing table size",
    ),
}

RUNTIME_ANTI_FREEZE_PATCHES = {
    # These are fail-stop/assertion paths outside the vector table. Normal
    # successful execution already returns before reaching these bytes.
    0x09CA0: (
        bytes.fromhex("ff e7"),
        "convert runtime fail-stop loop after integrity check into fall-through return",
    ),
    0x0C6C8: (
        bytes.fromhex("ff e7"),
        "convert UI/render fail-stop loop into fall-through return",
    ),
    0x2C4EA: (
        bytes.fromhex("70 47"),
        "return from semihosting/debug fail-stop instead of looping forever",
    ),
}

RELAY_SETTLE_PATCHES = {
    "exp1": {
        # Function 0x0801f0f2 is a GPIO/timing relay or range-selector candidate.
        # It is called repeatedly by 0x0801f19a when the active measurement path is
        # changed. The patch only extends waits that already exist in the official
        # firmware; it does not alter pin order or final pin states.
        0x0F10A: (
            bytes.fromhex("02 20"),
            bytes.fromhex("05 20"),
            "increase relay selector pre-switch settle wait from 2 to 5 ticks",
        ),
        0x0F146: (
            bytes.fromhex("03 20"),
            bytes.fromhex("08 20"),
            "increase relay selector bit-settle wait from 3 to 8 ticks",
        ),
        0x0F192: (
            bytes.fromhex("0a 20"),
            bytes.fromhex("32 20"),
            "increase final post-relay settle wait from 10 to 50 ticks",
        ),
    },
    "exp2": {
        # Stronger wait profile requested after hardware feedback that exp1 still
        # leaves blanking/instability after DC -> AC -> DC current switching.
        # This remains a timing-only patch at proven wait instructions.
        0x0F10A: (
            bytes.fromhex("02 20"),
            bytes.fromhex("08 20"),
            "force-stable: increase relay selector pre-switch settle wait from 2 to 8 ticks",
        ),
        0x0F146: (
            bytes.fromhex("03 20"),
            bytes.fromhex("0c 20"),
            "force-stable: increase relay selector bit-settle wait from 3 to 12 ticks",
        ),
        0x0F192: (
            bytes.fromhex("0a 20"),
            bytes.fromhex("64 20"),
            "force-stable: increase final post-relay settle wait from 10 to 100 ticks",
        ),
    },
}

MODE_SWITCH_PATCHES = {
    "v316-helper-wrapper": {
        # Helper 0x0801f0ac is called only from the mode-switch tail at
        # 0x0801f304/0x0801f310. V3.16 keeps a separate sub-mode check and
        # falls back to selector(1, flag) outside sub-mode 4. V4.0 always uses
        # this helper. The wrapper makes the helper perform selector(1, flag)
        # directly while preserving the call sites and official relay timing.
        0x0F0AC: (
            bytes.fromhex("10 b5 04 46 01 2c 08 d1 02 21 5e 48 1a f0 6d f9"),
            bytes.fromhex("00 b5 01 46 01 20 00 f0 1e f8 00 bd 00 bf 00 bf"),
            "v316-switch-exp3: replace V4 helper-only tail with selector(1, flag) wrapper for smoother DC/AC mode recovery",
        ),
    },
}

BOOT_LOGO_DELAY_CALL_OFFSET = 0x045B2
BOOT_LOGO_DELAY_STUB_OFFSET = 0x2D5C0
BOOT_LOGO_ORIGINAL_LOAD = 0x08015EEE
BOOT_LOGO_DELAY_FUNCTION = 0x08017AC2
BOOT_LOGO_DELAY_TICKS = 0xC8
BOOT_LOGO_STUB_GUARD_SIZE = 32


def encode_thumb_bl(source_address: int, target_address: int) -> bytes:
    """Encode a Thumb-2 BL. Source is the address of the BL halfword pair."""
    offset = target_address - (source_address + 4)
    if offset % 2:
        raise ValueError("Thumb BL target must be halfword aligned")
    imm = offset >> 1
    if not (-(1 << 23) <= imm < (1 << 23)):
        raise ValueError("Thumb BL target is out of range")
    imm &= (1 << 24) - 1
    sign = (imm >> 23) & 1
    i1 = (imm >> 22) & 1
    i2 = (imm >> 21) & 1
    imm10 = (imm >> 11) & 0x03FF
    imm11 = imm & 0x07FF
    j1 = (~(i1 ^ sign)) & 1
    j2 = (~(i2 ^ sign)) & 1
    first = 0xF000 | (sign << 10) | imm10
    second = 0xF800 | (j1 << 13) | (j2 << 11) | imm11
    return first.to_bytes(2, "little") + second.to_bytes(2, "little")


def build_boot_logo_delay_stub() -> bytes:
    stub_address = LOAD_BASE + BOOT_LOGO_DELAY_STUB_OFFSET
    original_call = encode_thumb_bl(stub_address + 2, BOOT_LOGO_ORIGINAL_LOAD)
    delay_call = encode_thumb_bl(stub_address + 8, BOOT_LOGO_DELAY_FUNCTION)
    return (
        bytes.fromhex("10 b5")
        + original_call
        + bytes([BOOT_LOGO_DELAY_TICKS, 0x20])
        + delay_call
        + bytes.fromhex("10 bd")
    )


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


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


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


def write_report(
    records: list[PatchRecord],
    source_data: bytes,
    output_data: bytes,
    profile: str,
    fault_reset: bool,
    runtime_patches: bool,
    relay_settle_profile: str | None,
    mode_switch_profile: str | None,
    boot_logo_delay: bool,
    vector_count: int,
) -> None:
    fault_scope = (
        "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub."
        if fault_reset
        else "- Flashable profile keeps fault/default handlers unchanged."
    )
    runtime_scope = (
        "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever."
        if runtime_patches
        else "- Flashable profile keeps runtime fail-stop loops unchanged."
    )
    if relay_settle_profile == "exp1":
        relay_scope = "- Relay/range selector waits in function `0x0801f0f2` are extended to `5/8/50` ticks."
    elif relay_settle_profile == "exp2":
        relay_scope = "- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks for stronger AC/DC switching recovery."
    else:
        relay_scope = "- Relay/range selector timing is kept unchanged."
    if mode_switch_profile == "v316-helper-wrapper":
        mode_scope = (
            "- Mode-switch helper `0x0801f0ac` is wrapped to call "
            "`selector(1, flag)` directly, matching the smoother V3.16 "
            "non-sub-mode-4 path while leaving call sites unchanged."
        )
    else:
        mode_scope = "- Mode-switch helper behavior is kept unchanged."
    boot_scope = (
        "- Boot-logo resource load is routed through a guarded wrapper that adds a short stabilization delay after `LOGO-1.bmp` is loaded."
        if boot_logo_delay
        else "- Boot-logo resource load timing is kept unchanged."
    )
    lines = [
        "# DM303 V4.0.1 beta patch report",
        "",
        "Status: candidate firmware only. Bench validation is still required before flashing.",
        "",
        f"Profile: `{profile}` - {PROFILES[profile]['description']}.",
        "",
        "## Safety scope",
        "",
        "- Source firmware is not modified in place.",
        "- Output binary size is unchanged.",
        "- Bootloader/updater code and SD update procedure are not patched.",
        fault_scope,
        runtime_scope,
        relay_scope,
        mode_scope,
        boot_scope,
        f"- Patched self-loop vector entries: `{vector_count}`.",
        "- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`.",
        "- The existing Spanish `TEXT_SP.DAT` slot is replaced with the same Malay resource for device-side language selection.",
        "- The existing Spanish language-name string is renamed to `Melayu` in place, with byte length preserved.",
        "- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.",
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

    write_text_lf(OUT_REPORT, "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        choices=sorted(PROFILES),
        default=DEFAULT_PROFILE,
        help="patch profile to generate",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    profile = args.profile
    fault_reset = bool(PROFILES[profile]["fault_reset"])
    runtime_patches = bool(PROFILES[profile]["runtime_patches"])
    relay_settle_profile = PROFILES[profile]["relay_settle_profile"]
    mode_switch_profile = PROFILES[profile]["mode_switch_profile"]
    boot_logo_delay = bool(PROFILES[profile]["boot_logo_delay"])

    source_data = SOURCE.read_bytes()
    source_hash = sha256_bytes(source_data)
    if source_hash != SOURCE_SHA256:
        raise SystemExit(
            f"Refusing to patch unexpected source hash: {source_hash}"
        )

    if fault_reset:
        if source_data[FAULT_BLOCK_OFFSET : FAULT_BLOCK_OFFSET + FAULT_BLOCK_SIZE] != ORIGINAL_FAULT_BLOCK:
            raise SystemExit("Refusing to patch: fault handler block does not match expected V4.0 bytes")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_SYSTEM.mkdir(parents=True, exist_ok=True)

    image = bytearray(source_data)
    records: list[PatchRecord] = []

    vector_offsets: list[int] = []
    if fault_reset:
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
                "preserve model ID and mark candidate version as V4.0.1 beta",
            )
        )

    for offset, (expected, replacement, reason) in LANGUAGE_NAME_PATCHES.items():
        before = bytes(image[offset : offset + len(expected)])
        if before != expected:
            raise SystemExit(
                f"Refusing to patch language-name guard at 0x{offset:05x}: "
                f"expected {expected!r}, got {before!r}"
            )
        records.append(patch_bytes(image, offset, replacement, reason))

    if runtime_patches:
        for offset, (replacement, reason) in RUNTIME_ANTI_FREEZE_PATCHES.items():
            before = bytes(image[offset : offset + len(replacement)])
            if before != b"\xfe\xe7":
                raise SystemExit(
                    f"Refusing to patch anti-freeze guard at 0x{offset:05x}: "
                    f"unexpected bytes {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if relay_settle_profile is not None:
        for offset, (expected, replacement, reason) in RELAY_SETTLE_PATCHES[relay_settle_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch relay-settle guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if mode_switch_profile is not None:
        for offset, (expected, replacement, reason) in MODE_SWITCH_PATCHES[mode_switch_profile].items():
            before = bytes(image[offset : offset + len(expected)])
            if before != expected:
                raise SystemExit(
                    f"Refusing to patch mode-switch guard at 0x{offset:05x}: "
                    f"expected {expected.hex(' ')}, got {before.hex(' ')}"
                )
            records.append(patch_bytes(image, offset, replacement, reason))

    if boot_logo_delay:
        original_call = encode_thumb_bl(LOAD_BASE + BOOT_LOGO_DELAY_CALL_OFFSET, BOOT_LOGO_ORIGINAL_LOAD)
        before = bytes(image[BOOT_LOGO_DELAY_CALL_OFFSET : BOOT_LOGO_DELAY_CALL_OFFSET + len(original_call)])
        if before != original_call:
            raise SystemExit(
                f"Refusing to patch boot-logo call guard at 0x{BOOT_LOGO_DELAY_CALL_OFFSET:05x}: "
                f"expected {original_call.hex(' ')}, got {before.hex(' ')}"
            )
        stub_guard = bytes(
            image[BOOT_LOGO_DELAY_STUB_OFFSET : BOOT_LOGO_DELAY_STUB_OFFSET + BOOT_LOGO_STUB_GUARD_SIZE]
        )
        if stub_guard != b"\x00" * BOOT_LOGO_STUB_GUARD_SIZE:
            raise SystemExit(
                f"Refusing to patch boot-logo stub guard at 0x{BOOT_LOGO_DELAY_STUB_OFFSET:05x}: "
                "candidate code cave is not empty"
            )
        stub = build_boot_logo_delay_stub()
        if len(stub) > BOOT_LOGO_STUB_GUARD_SIZE:
            raise SystemExit("Boot-logo delay stub is larger than the guarded code cave")
        wrapper_call = encode_thumb_bl(
            LOAD_BASE + BOOT_LOGO_DELAY_CALL_OFFSET,
            LOAD_BASE + BOOT_LOGO_DELAY_STUB_OFFSET,
        )
        records.append(
            patch_bytes(
                image,
                BOOT_LOGO_DELAY_CALL_OFFSET,
                wrapper_call,
                "force-enhanced-exp4: route LOGO-1 resource load through boot stabilization delay wrapper",
            )
        )
        records.append(
            patch_bytes(
                image,
                BOOT_LOGO_DELAY_STUB_OFFSET,
                stub,
                "force-enhanced-exp4: call original LOGO-1 loader, wait 200 ticks, then return to boot loader",
            )
        )

    output_data = bytes(image)
    OUT_BIN.write_bytes(output_data)

    if MS_TEXT.exists():
        shutil.copy2(MS_TEXT, OUT_SYSTEM / "TEXT_MS.DAT")
    if SP_TEXT.exists():
        shutil.copy2(SP_TEXT, OUT_SYSTEM / "TEXT_SP.DAT")

    write_report(
        records,
        source_data,
        output_data,
        profile,
        fault_reset,
        runtime_patches,
        relay_settle_profile,
        mode_switch_profile,
        boot_logo_delay,
        len(vector_offsets),
    )

    sums = [
        f"{sha256_file(OUT_BIN)}  {OUT_BIN.name}",
    ]
    ms_candidate = OUT_SYSTEM / "TEXT_MS.DAT"
    if ms_candidate.exists():
        sums.append(f"{sha256_file(ms_candidate)}  system/TEXT_MS.DAT")
    sp_candidate = OUT_SYSTEM / "TEXT_SP.DAT"
    if sp_candidate.exists():
        sums.append(f"{sha256_file(sp_candidate)}  system/TEXT_SP.DAT")
    write_text_lf(OUT_SUMS, "\n".join(sums) + "\n")

    print(f"source={SOURCE}")
    print(f"source_sha256={source_hash}")
    print(f"output={OUT_BIN}")
    print(f"profile={profile}")
    print(f"output_size={len(output_data)}")
    print(f"output_sha256={sha256_file(OUT_BIN)}")
    print(f"patched_vectors={len(vector_offsets)}")
    print(f"patch_records={len(records)}")
    print(f"report={OUT_REPORT}")
    print("safety_note=candidate only; do not flash before bench/recovery validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
