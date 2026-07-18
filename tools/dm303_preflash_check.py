#!/usr/bin/env python3
"""Pre-flash validation for a DM303 V4.0.1 beta SD-card root.

Run this against the final package folder, or against the actual SD-card root
after copying files. It is read-only and rejects the common dangerous layout
where the firmware folder is copied inside the SD card instead of its contents.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dm303_merge_final_package import (
    EXPECTED_CANDIDATE_SHA256_BY_PROFILE,
    EXPECTED_COMMAND_RETRY_BYTES_BY_PROFILE,
    EXPECTED_DM30XDB1_SHA256,
    EXPECTED_DM30XDB1_SIZE,
    EXPECTED_ICON_SP_SHA256,
    EXPECTED_LOW_IO_TIMEOUT_BYTES_BY_PROFILE,
    EXPECTED_LOW_IO_WRAPPER_BYTES_BY_PROFILE,
    EXPECTED_LOGO_SHA256,
    EXPECTED_MS_SHA256,
    EXPECTED_OFFICIAL_ICON_SP_SHA256,
    EXPECTED_OFFICIAL_SP_SHA256,
    EXPECTED_SP_SHA256,
    EXPECTED_INSTANT_SWITCH_BYTES_BY_PROFILE,
    EXPECTED_MODE_STATE_CLEAR_BYTES_BY_PROFILE,
    EXPECTED_STALE_ERROR_GATE_BYTES_BY_PROFILE,
    EXPECTED_STREAM_BUSY_GATE_BYTES_BY_PROFILE,
    EXPECTED_CURRENT_SWITCH_LATENCY_BYTES_BY_PROFILE,
    EXPECTED_STREAM_STATE_CLEAR_BYTES_BY_PROFILE,
    EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE,
    EXPECTED_VERSION_BYTES_BY_PROFILE,
    expected_sp_sha256,
    include_ms_icon_pack,
    replace_sp_with_ms_resource,
    validate_bmp_layout,
    validate_icon_pack,
    validate_logo,
    validate_menu_icon_set,
    sha256_file,
)
from dm303_repair_candidate_check import (
    EXPECTED as REPAIR_EXPECTED,
    validate_firmware as validate_repair_firmware,
    validate_official_system as validate_repair_official_system,
)
from dm303_ui_overlay_candidate_check import (
    EXPECTED_FIRMWARE_SHA256_BY_PROFILE as UI_MS_FIRMWARE_SHA256_BY_PROFILE,
    validate_firmware as validate_ui_ms_firmware,
    validate_system as validate_ui_ms_system,
)

UI_MS_PROFILES = set(UI_MS_FIRMWARE_SHA256_BY_PROFILE)


DEFAULT_ROOT = Path("dm303_firmware/DM303-V4.0.1-beta")
EXPECTED_ROOT_FILES = {
    "DM303V4.0.1-beta.bin",
    "QBtest.txt",
    "readme.txt",
}
IGNORABLE_SD_EXTRAS = {
    "System Volume Information",
    "$RECYCLE.BIN",
    "FOUND.000",
}


def fail(message: str) -> None:
    raise SystemExit(f"preflash_check=failed\nreason={message}")


def validate_stream_recovery(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE.get(
        profile, {}
    )
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"stream recovery bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_low_io_timeout(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_LOW_IO_TIMEOUT_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"low-IO timeout bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_command_retry(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_COMMAND_RETRY_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"command-retry bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_low_io_wrapper(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_LOW_IO_WRAPPER_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"low-IO wrapper bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_stream_state_clear(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STREAM_STATE_CLEAR_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"stream-state clear bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_mode_state_clear(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_MODE_STATE_CLEAR_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"mode-state clear bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_stream_busy_gate(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STREAM_BUSY_GATE_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"stream-busy gate bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_current_switch_latency(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_CURRENT_SWITCH_LATENCY_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"current-switch latency bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_instant_switch(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_INSTANT_SWITCH_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"instant-switch bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_stale_error_gate(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STALE_ERROR_GATE_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(
                f"stale-error gate bytes missing at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_version_marker(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_VERSION_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(f"version marker missing at 0x{offset:05x}: expected {expected!r}, got {actual!r}")


def validate_root_layout(root: Path, allow_sd_extras: bool) -> None:
    if not root.is_dir():
        fail(f"root folder does not exist: {root}")

    nested = root / "DM303-V4.0.1-beta" / "DM303V4.0.1-beta.bin"
    if nested.exists():
        fail(
            "firmware appears to be inside an extra DM303-V4.0.1-beta folder; "
            "copy the contents to the SD root instead"
        )

    if (root / "DM303V4.004.bin").exists():
        fail("original DM303V4.004.bin is present; root must contain only the beta firmware name")

    missing = sorted(name for name in EXPECTED_ROOT_FILES if not (root / name).is_file())
    if missing:
        fail(f"missing required root files: {missing}")
    if not (root / "system").is_dir():
        fail("missing required root folder: system")
    if (root / "system" / "system").exists():
        fail("invalid nested system/system folder exists")

    extras = sorted(
        path.name
        for path in root.iterdir()
        if path.name not in EXPECTED_ROOT_FILES and path.name != "system"
    )
    if extras and not allow_sd_extras:
        fail(f"unexpected root entries: {extras}")
    if extras and allow_sd_extras:
        unexpected = [name for name in extras if name not in IGNORABLE_SD_EXTRAS]
        if unexpected:
            fail(f"unexpected root entries: {unexpected}")


def validate_required_hashes(root: Path, expected_firmware_hash: str, profile: str) -> None:
    firmware = root / "DM303V4.0.1-beta.bin"
    if firmware.stat().st_size != 203260:
        fail(f"unexpected firmware size: {firmware.stat().st_size}")
    firmware_hash = sha256_file(firmware)
    if firmware_hash != expected_firmware_hash:
        fail(f"unexpected firmware hash: {firmware_hash}")
    if profile in EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE:
        validate_stream_recovery(firmware, profile)
    if profile in EXPECTED_LOW_IO_TIMEOUT_BYTES_BY_PROFILE:
        validate_low_io_timeout(firmware, profile)
    if profile in EXPECTED_COMMAND_RETRY_BYTES_BY_PROFILE:
        validate_command_retry(firmware, profile)
    if profile in EXPECTED_LOW_IO_WRAPPER_BYTES_BY_PROFILE:
        validate_low_io_wrapper(firmware, profile)
    if profile in EXPECTED_STREAM_STATE_CLEAR_BYTES_BY_PROFILE:
        validate_stream_state_clear(firmware, profile)
    if profile in EXPECTED_MODE_STATE_CLEAR_BYTES_BY_PROFILE:
        validate_mode_state_clear(firmware, profile)
    if profile in EXPECTED_STREAM_BUSY_GATE_BYTES_BY_PROFILE:
        validate_stream_busy_gate(firmware, profile)
    if profile in EXPECTED_CURRENT_SWITCH_LATENCY_BYTES_BY_PROFILE:
        validate_current_switch_latency(firmware, profile)
    if profile in EXPECTED_INSTANT_SWITCH_BYTES_BY_PROFILE:
        validate_instant_switch(firmware, profile)
    if profile in EXPECTED_STALE_ERROR_GATE_BYTES_BY_PROFILE:
        validate_stale_error_gate(firmware, profile)
    if profile in EXPECTED_VERSION_BYTES_BY_PROFILE:
        validate_version_marker(firmware, profile)

    system = root / "system"
    text_ms = system / "TEXT_MS.DAT"
    text_sp = system / "TEXT_SP.DAT"
    icon_sp = system / "icon-SP.dat"
    logo = system / "LOGO-1.bmp"
    dm30xdb1 = system / "DM30XDB1.dat"
    for path in [text_ms, text_sp, icon_sp, logo, dm30xdb1]:
        if not path.is_file():
            fail(f"missing required system file: {path.relative_to(root).as_posix()}")

    if sha256_file(text_ms) != EXPECTED_MS_SHA256:
        fail(f"unexpected TEXT_MS.DAT hash: {sha256_file(text_ms)}")
    expected_text_sp_hash = (
        expected_sp_sha256(profile)
        if replace_sp_with_ms_resource(profile)
        else EXPECTED_OFFICIAL_SP_SHA256
    )
    expected_icon_sp_hash = (
        EXPECTED_ICON_SP_SHA256
        if include_ms_icon_pack(profile)
        else EXPECTED_OFFICIAL_ICON_SP_SHA256
    )
    if sha256_file(text_sp) != expected_text_sp_hash:
        fail(f"unexpected TEXT_SP.DAT hash: {sha256_file(text_sp)}")
    validate_icon_pack(icon_sp, expected_icon_sp_hash)
    validate_logo(logo)
    if dm30xdb1.stat().st_size != EXPECTED_DM30XDB1_SIZE:
        fail(f"unexpected DM30XDB1.dat size: {dm30xdb1.stat().st_size}")
    if sha256_file(dm30xdb1) != EXPECTED_DM30XDB1_SHA256:
        fail(f"unexpected DM30XDB1.dat hash: {sha256_file(dm30xdb1)}")
    validate_menu_icon_set(root)

    # One explicit layout check keeps this script readable when import errors
    # or future refactors change the shared validator.
    validate_bmp_layout(logo, 320, -240, 153672)


def validate_repair_profile(root: Path, profile: str) -> None:
    validate_repair_firmware(root, profile)
    validate_repair_official_system(root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="final package folder or SD-card root")
    parser.add_argument(
        "--profile",
        choices=sorted(set(EXPECTED_CANDIDATE_SHA256_BY_PROFILE) | set(REPAIR_EXPECTED) | UI_MS_PROFILES),
        default="stability-exp20-ms-safe",
        help="expected firmware profile",
    )
    parser.add_argument(
        "--allow-sd-extras",
        action="store_true",
        help="allow common SD-card system folders such as System Volume Information",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    validate_root_layout(root, args.allow_sd_extras)
    if args.profile in REPAIR_EXPECTED and args.profile not in UI_MS_PROFILES:
        validate_repair_profile(root, args.profile)
        firmware_hash = sha256_file(root / "DM303V4.0.1-beta.bin")
        files = [path for path in root.rglob("*") if path.is_file()]
        print("preflash_check=ok")
        print(f"root={root}")
        print(f"profile={args.profile}")
        print(f"files={len(files)}")
        print(f"firmware_sha256={firmware_hash}")
        print("repair_system_resources=official_v4_plus_dm30xdb1")
        print(f"dm30xdb1_sha256={sha256_file(root / 'system' / 'DM30XDB1.dat')}")
        print("copy_rule=copy the contents of this root directly to the SD card root")
        return 0

    if args.profile in UI_MS_PROFILES:
        validate_ui_ms_firmware(root, args.profile)
        validate_ui_ms_system(root)
        files = [path for path in root.rglob("*") if path.is_file()]
        print("preflash_check=ok")
        print(f"root={root}")
        print(f"profile={args.profile}")
        print(f"files={len(files)}")
        print(f"firmware_sha256={sha256_file(root / 'DM303V4.0.1-beta.bin')}")
        print(f"text_sp_sha256={sha256_file(root / 'system' / 'TEXT_SP.DAT')}")
        print(f"icon_sp_sha256={sha256_file(root / 'system' / 'icon-SP.dat')}")
        print("ui_ms_system_resources=official_v4_plus_malay_dark_overlay")
        print("copy_rule=copy the contents of this root directly to the SD card root")
        return 0

    expected_firmware_hash = EXPECTED_CANDIDATE_SHA256_BY_PROFILE[args.profile]
    validate_required_hashes(root, expected_firmware_hash, args.profile)

    files = [path for path in root.rglob("*") if path.is_file()]
    print("preflash_check=ok")
    print(f"root={root}")
    print(f"profile={args.profile}")
    print(f"files={len(files)}")
    print(f"firmware_sha256={sha256_file(root / 'DM303V4.0.1-beta.bin')}")
    print(f"text_ms_sha256={sha256_file(root / 'system' / 'TEXT_MS.DAT')}")
    print(f"icon_sp_sha256={sha256_file(root / 'system' / 'icon-SP.dat')}")
    print(f"logo_sha256={sha256_file(root / 'system' / 'LOGO-1.bmp')}")
    print(f"dm30xdb1_sha256={sha256_file(root / 'system' / 'DM30XDB1.dat')}")
    print("copy_rule=copy the contents of this root directly to the SD card root")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
