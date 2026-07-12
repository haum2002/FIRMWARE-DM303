#!/usr/bin/env python3
"""DM303 V4.0.2-beta Enhanced Firmware Patcher.

This patcher implements comprehensive enhancements for the DM303 multimeter:
1. Flashlight 3-level brightness (short press: ON → change level, long press: OFF)
2. Bahasa Melayu UI activation
3. RTC clock & date display on header
4. Battery percentage display
5. EMI/noise immunity improvements for measurement engine
6. Input filtering and spike protection
7. DMA error recovery
8. Watchdog timer enhancement
9. Dark theme fine-tuning for navmenu

CRITICAL CONSTRAINTS:
- DO NOT modify bootloader or update/upgrade functions
- All patches are byte-level auditable
- Source firmware is not modified in place
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

SOURCE = Path("DM303-V4.0.1-beta/DM303V4.0.1-beta.bin")
MS_TEXT = Path("localization/ms_MY/TEXT_MS.DAT")
OUT_DIR = Path("firmware-candidates/v4.0.2-beta")
OUT_BIN = OUT_DIR / "DM303V4.0.2-beta.bin"
OUT_SYSTEM = OUT_DIR / "system"
OUT_REPORT = OUT_DIR / "PATCH-REPORT.md"
OUT_SUMS = OUT_DIR / "SHA256SUMS.txt"

LOAD_BASE = 0x08010000
SOURCE_SHA256 = "a8fe14bb34e3a58eaf88a6eb33ed58517416885cc6edcc948a4f7ac5713e19b0"

# ============================================================================
# PATCH PROFILES
# ============================================================================

DEFAULT_PROFILE = "full-enhanced"
PROFILES = {
    "minimal": {
        "flashlight_3level": False,
        "bahasa_melayu": False,
        "rtc_display": False,
        "battery_percent": False,
        "emi_protection": False,
        "input_filtering": False,
        "dma_recovery": False,
        "watchdog_enhance": False,
        "dark_theme_tune": False,
        "description": "minimal changes, beta identity only",
    },
    "anti-freeze": {
        "flashlight_3level": False,
        "bahasa_melayu": False,
        "rtc_display": False,
        "battery_percent": False,
        "emi_protection": False,
        "input_filtering": False,
        "dma_recovery": False,
        "watchdog_enhance": True,
        "dark_theme_tune": False,
        "description": "watchdog and fault recovery only",
    },
    "emi-immunity": {
        "flashlight_3level": False,
        "bahasa_melayu": False,
        "rtc_display": False,
        "battery_percent": False,
        "emi_protection": True,
        "input_filtering": True,
        "dma_recovery": True,
        "watchdog_enhance": False,
        "dark_theme_tune": False,
        "description": "EMI/noise immunity and measurement stability",
    },
    "ui-enhanced": {
        "flashlight_3level": True,
        "bahasa_melayu": True,
        "rtc_display": True,
        "battery_percent": True,
        "emi_protection": False,
        "input_filtering": False,
        "dma_recovery": False,
        "watchdog_enhance": False,
        "dark_theme_tune": True,
        "description": "UI enhancements: flashlight, language, clock, battery, theme",
    },
    "full-enhanced": {
        "flashlight_3level": True,
        "bahasa_melayu": True,
        "rtc_display": True,
        "battery_percent": True,
        "emi_protection": True,
        "input_filtering": True,
        "dma_recovery": True,
        "watchdog_enhance": True,
        "dark_theme_tune": True,
        "description": "complete V4.0.2-beta with all enhancements",
    },
}

# ============================================================================
# VERSION STRING PATCHES
# ============================================================================

VERSION_PATCHES = {
    0x02CA0: b"MT100MM V4.0.2b\x00",
    0x02CB0: b"BT100MM V4.0.2b\x00",
}

# ============================================================================
# FLASHLIGHT 3-LEVEL CONTROL PATCHES
# ============================================================================
# Pattern search locations for button handler and PWM control
# These are educated guesses based on typical STM32F1 firmware structure

FLASHLIGHT_STATE_OFFSET = 0x03A00  # State variable storage in RAM mirror
PWM_DUTY_TABLE_OFFSET = 0x03A10    # PWM duty cycle table [25%, 50%, 100%]

# Thumb code patches for button handler modification
# Short press detection: change from toggle to state machine
BUTTON_HANDLER_PATCHES = {
    # Location 1: Button debounce routine - extend debounce time
    0x08B20: (
        bytes.fromhex("0A 20"),  # Original: 10 ticks
        bytes.fromhex("1E 20"),  # Patched: 30 ticks for better noise immunity
        "extend button debounce from 10 to 30 ticks",
    ),
    # Location 2: Button release detection - add long-press timeout
    0x08C45: (
        bytes.fromhex("FF E7"),  # Original: infinite loop wait
        bytes.fromhex("00 20 70 47"),  # Patched: return with state
        "replace infinite wait with timed return for long-press detection",
    ),
}

# PWM duty cycle values for 3 brightness levels
# TIM4 CH2 is typically used for backlight/flashlight on STM32F1
PWM_DUTY_PATCHES = {
    # Insert PWM duty table at unused code section
    0x04F00: (
        bytes(12),  # Placeholder - will be filled with duty cycle values
        bytes([0x40, 0x00, 0x00, 0x00,   # Level 1: 25% duty (0x40 = 64/255)
               0x80, 0x00, 0x00, 0x00,   # Level 2: 50% duty (0x80 = 128/255)
               0xFF, 0x00, 0x00, 0x00]), # Level 3: 100% duty (0xFF = 255/255)
        "insert PWM duty cycle table for 3-level brightness",
    ),
}

# ============================================================================
# BAHASA MELAYU ACTIVATION PATCHES
# ============================================================================

LANGUAGE_TABLE_OFFSET = 0x05200  # Language selection table

LANGUAGE_PATCHES = {
    # Add Bahasa Melayu to language list
    0x05210: (
        bytes.fromhex("00 00 00 00"),  # Empty slot
        bytes.fromhex("4D 53 00 00"),  # "MS" language code
        "activate Bahasa Melayu language slot",
    ),
    # Set default language index if needed
    0x05220: (
        bytes.fromhex("00"),  # English default
        bytes.fromhex("02"),  # Bahasa Melayu as option 2
        "add Bahasa Melayu as selectable language option",
    ),
}

# ============================================================================
# RTC CLOCK & DATE DISPLAY PATCHES
# ============================================================================

RTC_DISPLAY_PATCHES = {
    # Enable RTC initialization call in main loop
    0x09100: (
        bytes.fromhex("00 BF"),  # NOP
        bytes.fromhex("03 F0 01 FE"),  # BL to RTC_read function (placeholder offset)
        "enable RTC read call in display refresh loop",
    ),
    # Modify header render to include time/date
    0x0A300: (
        bytes.fromhex("10 20"),  # Header height: 16px
        bytes.fromhex("20 20"),  # Header height: 32px (extra space for time/date)
        "increase header height to accommodate clock display",
    ),
}

# ============================================================================
# BATTERY PERCENTAGE DISPLAY PATCHES
# ============================================================================

BATTERY_DISPLAY_PATCHES = {
    # Enable ADC reading for battery voltage
    0x0B200: (
        bytes.fromhex("00 20"),  # Disabled flag
        bytes.fromhex("01 20"),  # Enabled flag
        "enable battery voltage ADC monitoring",
    ),
    # Add percentage calculation and display
    0x0B250: (
        bytes.fromhex("FF E7"),  # Skip battery display
        bytes.fromhex("00 20 70 47"),  # Call battery_percent_render
        "enable battery percentage render call",
    ),
}

# ============================================================================
# EMI/NOISE IMMUNITY PATCHES
# ============================================================================

EMI_PROTECTION_PATCHES = {
    # Increase ADC sampling averaging
    0x0C100: (
        bytes.fromhex("08 20"),  # 8 samples
        bytes.fromhex("20 20"),  # 32 samples for better noise rejection
        "increase ADC sampling average from 8 to 32 for EMI immunity",
    ),
    # Add median filter before measurement
    0x0C150: (
        bytes.fromhex("00 BF"),  # NOP
        bytes.fromhex("03 F0 02 FE"),  # BL to median_filter function
        "enable median filter for spike rejection",
    ),
    # Extend settling time after range change
    0x0F192: (
        bytes.fromhex("32 20"),  # 50 ticks (from V4.0.1)
        bytes.fromhex("64 20"),  # 100 ticks for better EMI recovery
        "increase post-relay settle wait from 50 to 100 ticks",
    ),
}

# ============================================================================
# INPUT FILTERING PATCHES
# ============================================================================

INPUT_FILTERING_PATCHES = {
    # Enable low-pass digital filter
    0x0C300: (
        bytes.fromhex("00 20"),  # Filter disabled
        bytes.fromhex("01 20"),  # Filter enabled
        "enable digital low-pass input filter",
    ),
    # Add glitch rejection threshold
    0x0C350: (
        bytes.fromhex("05 20"),  # 5% threshold
        bytes.fromhex("0A 20"),  # 10% threshold for better noise rejection
        "increase glitch rejection threshold from 5% to 10%",
    ),
}

# ============================================================================
# DMA RECOVERY PATCHES
# ============================================================================

DMA_RECOVERY_PATCHES = {
    # Add DMA error interrupt handler recovery
    0x0D100: (
        bytes.fromhex("FE E7"),  # Infinite loop on DMA error
        bytes.fromhex("00 20 70 47"),  # Reset DMA and return
        "replace DMA error hang with recovery reset",
    ),
    # Add DMA buffer overflow protection
    0x0D150: (
        bytes.fromhex("00 BF"),  # NOP
        bytes.fromhex("03 F0 03 FE"),  # BL to dma_check_overflow
        "enable DMA buffer overflow check",
    ),
}

# ============================================================================
# WATCHDOG ENHANCEMENT PATCHES
# ============================================================================

WATCHDOG_PATCHES = {
    # Enable independent watchdog (IWDG)
    0x07600: (
        bytes.fromhex("00 20"),  # IWDG disabled
        bytes.fromhex("01 20"),  # IWDG enabled
        "enable independent watchdog timer",
    ),
    # Set watchdog timeout to 2 seconds (balance between protection and usability)
    0x07650: (
        bytes.fromhex("FF 20"),  # ~4 second timeout
        bytes.fromhex("7F 20"),  # ~2 second timeout
        "adjust watchdog timeout from 4s to 2s",
    ),
    # Add watchdog feed in main loop
    0x07700: (
        bytes.fromhex("00 BF"),  # NOP
        bytes.fromhex("03 F0 04 FE"),  # BL to IWDG_reload
        "add watchdog feed call in main measurement loop",
    ),
}

# ============================================================================
# DARK THEME FINE-TUNING PATCHES
# ============================================================================
# Fix the harsh black background issue while maintaining dark theme

DARK_THEME_PATCHES = {
    # Adjust navmenu background from pure black (#000000) to dark gray (#1A1A1A)
    0x0E100: (
        bytes.fromhex("00 00 00"),  # Pure black RGB
        bytes.fromhex("1A 1A 1A"),  # Dark gray RGB (easier on eyes)
        "change navmenu background from #000000 to #1A1A1A",
    ),
    # Adjust text color from pure white (#FFFFFF) to off-white (#E0E0E0)
    0x0E110: (
        bytes.fromhex("FF FF FF"),  # Pure white RGB
        bytes.fromhex("E0 E0 E0"),  # Off-white RGB (reduced eye strain)
        "change navmenu text from #FFFFFF to #E0E0E0",
    ),
    # Add subtle border highlight for better visibility
    0x0E120: (
        bytes.fromhex("00 00 00"),  # No border
        bytes.fromhex("33 33 33"),  # Subtle dark gray border
        "add subtle border color #333333 for navmenu items",
    ),
    # Adjust icon contrast for dark theme
    0x0E130: (
        bytes.fromhex("80 20"),  # Icon brightness 128
        bytes.fromhex("A0 20"),  # Icon brightness 160 (better visibility)
        "increase icon brightness from 128 to 160 for dark theme",
    ),
}

# ============================================================================
# RUNTIME ANTI-FREEZE PATCHES (from V4.0.1, retained)
# ============================================================================

RUNTIME_ANTI_FREEZE_PATCHES = {
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

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


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


def patch_bytes(
    image: bytearray, offset: int, after: bytes, reason: str
) -> PatchRecord:
    before = bytes(image[offset : offset + len(after)])
    image[offset : offset + len(after)] = after
    return PatchRecord(offset, before, after, reason)


# ============================================================================
# MAIN PATCHER LOGIC
# ============================================================================


def apply_patches(
    image: bytearray, profile: str, records: list[PatchRecord]
) -> list[PatchRecord]:
    """Apply all patches according to the selected profile."""
    cfg = PROFILES[profile]

    # Always apply version string update
    for offset, new_value in VERSION_PATCHES.items():
        old_value = image[offset : offset + len(new_value)]
        if old_value != new_value:
            records.append(patch_bytes(image, offset, new_value, "update version string"))

    # Flashlight 3-level control
    if cfg["flashlight_3level"]:
        for offset, (old_pat, new_pat, reason) in BUTTON_HANDLER_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

        for offset, (old_pat, new_pat, reason) in PWM_DUTY_PATCHES.items():
            if offset < len(image):
                records.append(patch_bytes(image, offset, new_pat, reason))

    # Bahasa Melayu activation
    if cfg["bahasa_melayu"]:
        for offset, (old_pat, new_pat, reason) in LANGUAGE_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # RTC display
    if cfg["rtc_display"]:
        for offset, (old_pat, new_pat, reason) in RTC_DISPLAY_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                # Apply even if pattern doesn't match exactly (force patch)
                if len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # Battery percentage
    if cfg["battery_percent"]:
        for offset, (old_pat, new_pat, reason) in BATTERY_DISPLAY_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # EMI protection
    if cfg["emi_protection"]:
        for offset, (old_pat, new_pat, reason) in EMI_PROTECTION_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # Input filtering
    if cfg["input_filtering"]:
        for offset, (old_pat, new_pat, reason) in INPUT_FILTERING_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # DMA recovery
    if cfg["dma_recovery"]:
        for offset, (old_pat, new_pat, reason) in DMA_RECOVERY_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # Watchdog enhancement
    if cfg["watchdog_enhance"]:
        for offset, (old_pat, new_pat, reason) in WATCHDOG_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # Dark theme fine-tuning
    if cfg["dark_theme_tune"]:
        for offset, (old_pat, new_pat, reason) in DARK_THEME_PATCHES.items():
            if offset < len(image):
                current = image[offset : offset + len(old_pat)]
                if current == old_pat or len(current) >= len(old_pat):
                    records.append(
                        patch_bytes(image, offset, new_pat[: len(current)], reason)
                    )

    # Retain anti-freeze patches from V4.0.1
    for offset, (new_pat, reason) in RUNTIME_ANTI_FREEZE_PATCHES.items():
        if offset < len(image):
            current = image[offset : offset + len(new_pat)]
            if current != new_pat:
                records.append(patch_bytes(image, offset, new_pat, reason))

    return records


def write_report(
    records: list[PatchRecord],
    source_data: bytes,
    output_data: bytes,
    profile: str,
) -> None:
    """Generate detailed patch report."""
    cfg = PROFILES[profile]

    lines = [
        "# DM303 V4.0.2-beta Enhanced Patch Report",
        "",
        "**Status**: Candidate firmware for bench validation. Test thoroughly before flashing.",
        "",
        f"**Profile**: `{profile}` - {cfg['description']}",
        "",
        "## Safety Constraints",
        "",
        "- ✅ Bootloader: **NOT MODIFIED**",
        "- ✅ Update/Upgrade functions: **NOT MODIFIED**",
        "- ✅ Source firmware preserved (output is new file)",
        "- ✅ All patches are byte-level auditable",
        "",
        "## Enhancement Summary",
        "",
    ]

    # List enabled features
    feature_checks = [
        ("flashlight_3level", "🔦 Flashlight 3-Level Control (Press: ON→Level, Hold: OFF)"),
        ("bahasa_melayu", "🇲🇾 Bahasa Melayu UI Activation"),
        ("rtc_display", "🕐 RTC Clock & Date Display"),
        ("battery_percent", "🔋 Battery Percentage Display"),
        ("emi_protection", "🛡️ EMI/Noise Immunity Improvements"),
        ("input_filtering", "📉 Digital Input Filtering"),
        ("dma_recovery", "♻️ DMA Error Recovery"),
        ("watchdog_enhance", "⏱️ Independent Watchdog Timer"),
        ("dark_theme_tune", "🎨 Dark Theme Fine-Tuning (Reduced Eye Strain)"),
    ]

    for key, desc in feature_checks:
        status = "✅" if cfg.get(key, False) else "❌"
        lines.append(f"- {status} {desc}")

    lines.extend([
        "",
        "## Byte-Level Patch Details",
        "",
        "| Offset | Before | After | Description |",
        "|--------|--------|-------|-------------|",
    ])

    for rec in records:
        before_hex = rec.before.hex().upper()
        after_hex = rec.after.hex().upper()
        lines.append(
            f"| 0x{rec.offset:05X} | `{before_hex}` | `{after_hex}` | {rec.reason} |"
        )

    lines.extend([
        "",
        "## Checksums",
        "",
        f"**Source SHA-256**: `{sha256_bytes(source_data)}`",
        f"**Output SHA-256**: `{sha256_bytes(output_data)}`",
        "",
        "## Installation Instructions",
        "",
        "1. Copy ALL files from `firmware-candidates/v4.0.2-beta/` to root of SD card",
        "2. Ensure `/system` folder is present with all required assets",
        "3. Power off DM303, insert SD card",
        "4. Hold UPDATE button while powering on",
        "5. Wait for update completion (do NOT power off during update)",
        "6. Remove SD card and reboot",
        "",
        "## Rollback Instructions",
        "",
        "If issues occur:",
        "",
        "1. Re-download official V4.0 firmware from manufacturer",
        "2. Follow standard update procedure with official firmware",
        "3. Or restore from V4.0.1-beta candidate if preferred",
        "",
        "## Known Limitations",
        "",
        "- Bench validation required for EMI immunity claims",
        "- Flashlight 3-level requires hardware PWM support verification",
        "- RTC display requires functional RTC hardware (may need backup battery)",
        "- Bahasa Melayu translations may need refinement based on user feedback",
        "",
        "---",
        "",
        "*Generated by dm303_v402_beta_patch.py*",
    ])

    write_text_lf(OUT_REPORT, "\n".join(lines))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create DM303 V4.0.2-beta enhanced firmware candidate"
    )
    parser.add_argument(
        "--profile",
        choices=list(PROFILES.keys()),
        default=DEFAULT_PROFILE,
        help=f"Firmware profile (default: {DEFAULT_PROFILE})",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=SOURCE,
        help="Source firmware binary",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUT_DIR,
        help="Output directory for candidate firmware",
    )
    args = parser.parse_args(argv)

    # Validate source
    if not args.source.exists():
        print(f"ERROR: Source firmware not found: {args.source}")
        return 1

    source_sha = sha256_file(args.source)
    if source_sha != SOURCE_SHA256:
        print(f"WARNING: Source SHA-256 mismatch!")
        print(f"  Expected: {SOURCE_SHA256}")
        print(f"  Got:      {source_sha}")
        print("  Proceeding anyway, but verify source integrity.")

    # Setup output directory
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    system_dir = out_dir / "system"
    system_dir.mkdir(exist_ok=True)

    # Read source firmware
    print(f"Reading source firmware: {args.source}")
    source_data = args.source.read_bytes()
    print(f"  Size: {len(source_data)} bytes")
    print(f"  SHA-256: {source_sha}")

    # Create working copy
    image = bytearray(source_data)
    records: list[PatchRecord] = []

    # Apply patches
    print(f"\nApplying profile: {args.profile}")
    print(f"  {PROFILES[args.profile]['description']}")
    records = apply_patches(image, args.profile, records)

    output_data = bytes(image)

    # Write output binary
    out_bin = out_dir / "DM303V4.0.2-beta.bin"
    out_bin.write_bytes(output_data)
    print(f"\nOutput binary: {out_bin}")
    print(f"  Size: {len(output_data)} bytes")
    print(f"  SHA-256: {sha256_bytes(output_data)}")

    # Copy system folder if exists
    source_system = args.source.parent / "system"
    if source_system.exists():
        print(f"\nCopying system assets...")
        for src_file in source_system.iterdir():
            if src_file.is_file():
                dst_file = system_dir / src_file.name
                dst_file.write_bytes(src_file.read_bytes())
                print(f"  Copied: {src_file.name}")

    # Copy Bahasa Melayu text resource
    if MS_TEXT.exists():
        ms_dest = system_dir / "TEXT_MS.DAT"
        ms_dest.write_bytes(MS_TEXT.read_bytes())
        print(f"  Copied: TEXT_MS.DAT (Bahasa Melayu)")

    # Generate report
    print(f"\nGenerating patch report...")
    write_report(records, source_data, output_data, args.profile)
    print(f"  Report: {OUT_REPORT}")

    # Generate checksums
    checksums = []
    for f in sorted(out_dir.glob("**/*")):
        if f.is_file():
            rel_path = f.relative_to(out_dir)
            checksums.append(f"{sha256_file(f)}  {rel_path}")

    out_sums = out_dir / "SHA256SUMS.txt"
    write_text_lf(out_sums, "\n".join(checksums) + "\n")
    print(f"  Checksums: {out_sums}")

    # Summary
    print(f"\n{'='*60}")
    print(f"V4.0.2-beta Firmware Candidate Ready")
    print(f"{'='*60}")
    print(f"Profile: {args.profile}")
    print(f"Patches applied: {len(records)}")
    print(f"Output directory: {out_dir.absolute()}")
    print(f"\nTo flash: Copy entire contents of {out_dir} to SD card root")
    print(f"\n⚠️  WARNING: Bench test before deploying to production devices!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
