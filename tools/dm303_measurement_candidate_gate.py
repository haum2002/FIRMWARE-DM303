#!/usr/bin/env python3
"""Strict byte-diff gate for DM303 measurement repair candidates.

This is intentionally narrower than the general repair candidate checker.  It
proves that a candidate only carries the exact byte ranges approved for the
selected measurement experiment, and that known UI/render, stream/IO, relay,
and boot-logo areas remain official.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dm303_repair_candidate_check import (
    EXPECTED,
    validate_firmware,
    validate_layout,
    validate_official_system,
)


SOURCE = Path("backup/DM303 V4.0-read only/DM303V4.004.bin")
FIRMWARE_NAME = "DM303V4.0.1-beta.bin"

EXPECTED_DIFF_RANGES = {
    "v401h-repair-f": [
        (0x02CAC, 0x02CAF),
        (0x02CBC, 0x02CBF),
        (0x15812, 0x15814),
        (0x15838, 0x1583A),
        (0x15860, 0x15864),
        (0x1588A, 0x1588E),
        (0x15934, 0x15938),
        (0x1595C, 0x15960),
    ],
    "v401h-repair-g": [
        (0x02CAC, 0x02CAF),
        (0x02CBC, 0x02CBF),
        (0x14B0E, 0x14B12),
        (0x14B36, 0x14B3A),
        (0x15812, 0x15814),
        (0x15838, 0x1583A),
        (0x15860, 0x15864),
        (0x1588A, 0x1588E),
        (0x15934, 0x15938),
        (0x1595C, 0x15960),
    ],
    "v401h-repair-h": [
        (0x02CAC, 0x02CAF),
        (0x02CBC, 0x02CBF),
        (0x14B0E, 0x14B12),
        (0x14B36, 0x14B3A),
        (0x15812, 0x15814),
        (0x15838, 0x1583A),
        (0x15860, 0x15864),
        (0x1588A, 0x1588E),
        (0x15934, 0x15938),
        (0x1595C, 0x15960),
        (0x1D1A4, 0x1D1A8),
        (0x1D1C0, 0x1D1C4),
    ],
    "v401h-repair-i": [
        (0x02CAC, 0x02CAF),
        (0x02CBC, 0x02CBF),
        (0x14B0E, 0x14B12),
        (0x14B36, 0x14B3A),
        (0x15812, 0x15814),
        (0x15838, 0x1583A),
        (0x15860, 0x15864),
        (0x1588A, 0x1588E),
        (0x15934, 0x15938),
        (0x1595C, 0x15960),
        (0x1D1A4, 0x1D1A8),
        (0x1D1C0, 0x1D1C4),
        (0x1D1DA, 0x1D1DB),
    ],
    "v401h-repair-j": [
        (0x02CAC, 0x02CAF),
        (0x02CBC, 0x02CBF),
        (0x1DF0C, 0x1DF10),
        (0x1DF40, 0x1DF44),
    ],
    # repair-j measurement bytes + V4.0.1r marker + Melayu language-slot name.
    # The name patch occupies 0x25bf8-0x25bfe but byte 0x25bfb is 0x61 ('a')
    # in both "Espa\xc3\xb1a" and "Melayu ", so the diff splits into two ranges.
    "v401h-repair-j-ui-ms": [
        (0x02CAC, 0x02CAF),
        (0x02CBC, 0x02CBF),
        (0x1DF0C, 0x1DF10),
        (0x1DF40, 0x1DF44),
        (0x25BF8, 0x25BFB),
        (0x25BFC, 0x25BFF),
    ],
}

MUST_MATCH_OFFICIAL = {
    "fault_vector_window": (0x00000, 0x00140),
    "boot_logo_call": (0x045B2, 0x045B6),
    "low_io_entry": (0x06A06, 0x06A0A),
    "low_io_wrapper_cave": (0x06A50, 0x06AA0),
    "fault_handler_block": (0x07554, 0x07568),
    "stream_retry_loop_1": (0x09570, 0x09572),
    "command_retry_counters": (0x0967C, 0x09683),
    "stream_busy_gate": (0x096BE, 0x096C0),
    "stream_retry_loop_2": (0x09758, 0x0975A),
    "stream_retry_loop_3": (0x097BE, 0x097C0),
    "stream_state_byte": (0x097E8, 0x097E9),
    "runtime_guard": (0x09CA0, 0x09CA2),
    "ui_render_guard": (0x0C6C8, 0x0C6CA),
    "relay_settle_a": (0x0F10A, 0x0F10C),
    "relay_settle_b": (0x0F146, 0x0F148),
    "relay_settle_c": (0x0F192, 0x0F194),
    "mode_state_entry": (0x0F19A, 0x0F19E),
    "debug_guard": (0x2C4EA, 0x2C4EC),
    "boot_logo_delay_cave": (0x2D5C0, 0x2D5E0),
    "mode_state_wrapper_cave": (0x2D606, 0x2D624),
}


def fail(message: str) -> None:
    raise SystemExit(f"measurement_candidate_gate=failed\nreason={message}")


def diff_ranges(source: bytes, candidate: bytes) -> list[tuple[int, int]]:
    if len(source) != len(candidate):
        fail(f"size differs: source={len(source)} candidate={len(candidate)}")
    ranges: list[tuple[int, int]] = []
    index = 0
    while index < len(source):
        if source[index] == candidate[index]:
            index += 1
            continue
        start = index
        index += 1
        while index < len(source) and source[index] != candidate[index]:
            index += 1
        ranges.append((start, index))
    return ranges


def format_ranges(ranges: list[tuple[int, int]]) -> str:
    return ", ".join(f"0x{start:05x}-0x{end - 1:05x}" for start, end in ranges)


def validate_exact_diff(profile: str, source: bytes, candidate: bytes) -> list[tuple[int, int]]:
    actual = diff_ranges(source, candidate)
    expected = EXPECTED_DIFF_RANGES[profile]
    if actual != expected:
        fail(
            "unexpected firmware diff ranges: "
            f"expected [{format_ranges(expected)}], got [{format_ranges(actual)}]"
        )
    return actual


def validate_official_windows(source: bytes, candidate: bytes) -> None:
    for label, (start, end) in MUST_MATCH_OFFICIAL.items():
        if source[start:end] != candidate[start:end]:
            fail(f"{label} differs from official bytes at 0x{start:05x}-0x{end - 1:05x}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--profile", choices=sorted(EXPECTED_DIFF_RANGES), required=True)
    parser.add_argument(
        "--firmware-only",
        action="store_true",
        help="skip SD-root layout and official-system checks; validate only the "
        "firmware bytes (exact diff vs official plus official windows). Needed "
        "for UI-overlay packages whose system folder intentionally differs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    firmware = root / FIRMWARE_NAME
    if args.profile not in EXPECTED:
        fail(f"profile is not known to repair checker: {args.profile}")

    if not args.firmware_only:
        validate_layout(root)
        validate_official_system(root)
    elif not firmware.is_file():
        fail(f"missing firmware file: {firmware}")
    validate_firmware(root, args.profile)

    source = SOURCE.read_bytes()
    candidate = firmware.read_bytes()
    ranges = validate_exact_diff(args.profile, source, candidate)
    validate_official_windows(source, candidate)

    print("measurement_candidate_gate=ok")
    print(f"root={root}")
    print(f"profile={args.profile}")
    print(f"firmware_only={args.firmware_only}")
    print(f"diff_ranges={format_ranges(ranges)}")
    if not args.firmware_only:
        print("official_system_resources=match")
    print("ui_render_stream_io_relay_boot_windows=official")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
