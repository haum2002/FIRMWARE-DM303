#!/usr/bin/env python3
"""Read-only latency guard probe for DM303 V4.0.1b.

The purpose is to keep the low-latency/stability work auditable. It verifies the
current stream-recovery bytes and records the remaining lower-level bounded
timeouts instead of pretending that every measurement/math path is already
known.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


DEFAULT_IMAGE = Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin")
DEFAULT_REPORT = Path("docs/v401b-latency-guard-report.md")
LOAD_BASE = 0x08010000

EXPECTED_SHA256 = "29a8bd71cba65538ba25d8e76aa5122234f9a28ad957287ba82fbf4fdf6c60af"
VERSION_MARKERS = {
    0x02CA0: ("0x08012ca0", b"MT100MM V4.0.1d\x00", "visible exp16 UI-safe marker for main firmware identity"),
    0x02CB0: ("0x08012cb0", b"BT100MM V4.0.1d\x00", "visible exp16 UI-safe marker for secondary firmware identity"),
}
STREAM_PATCHES = {
    0x09570: ("0x08019570", bytes.fromhex("00 bf"), "stream-read retry after lower helper timeout"),
    0x09706: ("0x08019706", bytes.fromhex("4c d1"), "command-0x40 busy failure routes to existing error/clear path"),
    0x09758: ("0x08019758", bytes.fromhex("00 bf"), "command-0xe9 retry while status clear fails"),
    0x097BE: ("0x080197be", bytes.fromhex("00 bf"), "mode/status retry while command helper fails"),
}
LOW_HELPER_WRAPPER = {
    0x06A06: ("0x08016a06", bytes.fromhex("00 f0 23 b8"), "low byte-IO helper branch to bounded wrapper"),
    0x06A50: (
        "0x08016a50",
        bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
        "bounded low byte-IO wrapper; returns 0xff on ready-timeout",
    ),
}
COMMAND_RETRY_COUNTS = {
    0x0967C: ("0x0801967c", bytes.fromhex("60 27"), "command 0x40 bounded retry count, 0x60"),
    0x09682: ("0x08019682", bytes.fromhex("60 27"), "command 0x48 bounded retry count, 0x60"),
    0x09694: ("0x08019694", bytes.fromhex("0a 27"), "fallback bounded retry count, 0x0a"),
}
STREAM_STATE_CLEAR = {
    0x097E6: (
        "0x080197e6",
        bytes.fromhex("20 f0 03 00"),
        "stream error cleanup clears flag bits 0 and 1 from 0x2000022c",
    ),
}
MODE_STATE_CLEAR = {
    0x0F19A: (
        "0x0801f19a",
        bytes.fromhex("1e f0 34 ba"),
        "mode/range entry routes to stale stream-state clear wrapper",
    ),
    0x2D606: (
        "0x0803d606",
        bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
        "mode/range wrapper clears bits 0 and 1 of 0x2000022c then continues original function",
    ),
}
STREAM_BUSY_GATE = {
    0x096BE: (
        "0x080196be",
        bytes.fromhex("02 e0"),
        "force stream transaction body instead of stale-busy early return",
    ),
}
CURRENT_SWITCH_LATENCY = {
    0x1585E: (
        "0x0802585e",
        bytes.fromhex("b0 f5 c8 6f"),
        "cap first long meter/current switch gate from 0x3e80 to 0x0640",
    ),
    0x15888: (
        "0x08025888",
        bytes.fromhex("b0 f5 c8 6f"),
        "cap second long meter/current switch gate from 0x3e80 to 0x0640",
    ),
}
INSTANT_SWITCH_GATES = {
    0x15812: (
        "0x08025812",
        bytes.fromhex("00 bf"),
        "first mode/range elapsed-time skip branch replaced with NOP",
    ),
    0x15838: (
        "0x08025838",
        bytes.fromhex("00 bf"),
        "second mode/range elapsed-time skip branch replaced with NOP",
    ),
    0x15862: (
        "0x08025862",
        bytes.fromhex("00 bf"),
        "first return-to-mode elapsed-time skip branch replaced with NOP",
    ),
    0x1588C: (
        "0x0802588c",
        bytes.fromhex("00 bf"),
        "second return-to-mode elapsed-time skip branch replaced with NOP",
    ),
}
STALE_ERROR_GATES = {
    0x09818: (
        "0x08019818",
        bytes.fromhex("01 e0"),
        "first stream helper stale bit0 early error converted to continue branch",
    ),
    0x098B4: (
        "0x080198b4",
        bytes.fromhex("01 e0"),
        "second stream helper stale bit0 early error converted to continue branch",
    ),
    0x09950: (
        "0x08019950",
        bytes.fromhex("03 e0"),
        "parsed stream helper stale bit0 early error converted to continue branch",
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def read_bytes(data: bytes, offset: int, size: int) -> bytes:
    return data[offset : offset + size]


def check_table(data: bytes, table: dict[int, tuple[str, bytes, str]]) -> list[tuple[int, str, bytes, bytes, str, bool]]:
    rows: list[tuple[int, str, bytes, bytes, str, bool]] = []
    for offset, (address, expected, purpose) in table.items():
        actual = read_bytes(data, offset, len(expected))
        rows.append((offset, address, expected, actual, purpose, actual == expected))
    return rows


def format_rows(rows: list[tuple[int, str, bytes, bytes, str, bool]]) -> list[str]:
    output = [
        "| Offset | Address | Expected | Actual | OK | Purpose |",
        "|---:|---:|---|---|---|---|",
    ]
    for offset, address, expected, actual, purpose, ok in rows:
        output.append(
            f"| `0x{offset:05x}` | `{address}` | `{expected.hex(' ')}` | "
            f"`{actual.hex(' ')}` | `{ok}` | {purpose} |"
        )
    return output


def build_report(image: Path, data: bytes) -> tuple[str, bool]:
    digest = sha256_file(image)
    version_rows = check_table(data, VERSION_MARKERS)
    stream_rows = check_table(data, STREAM_PATCHES)
    wrapper_rows = check_table(data, LOW_HELPER_WRAPPER)
    retry_rows = check_table(data, COMMAND_RETRY_COUNTS)
    state_rows = check_table(data, STREAM_STATE_CLEAR)
    mode_state_rows = check_table(data, MODE_STATE_CLEAR)
    busy_gate_rows = check_table(data, STREAM_BUSY_GATE)
    current_latency_rows = check_table(data, CURRENT_SWITCH_LATENCY)
    all_ok = (
        digest == EXPECTED_SHA256
        and all(row[-1] for row in version_rows)
        and all(row[-1] for row in stream_rows)
        and all(row[-1] for row in wrapper_rows)
        and all(row[-1] for row in retry_rows)
        and all(row[-1] for row in state_rows)
        and all(row[-1] for row in mode_state_rows)
        and all(row[-1] for row in busy_gate_rows)
        and all(row[-1] for row in current_latency_rows)
    )

    lines = [
        "# DM303 V4.0.1b latency guard report",
        "",
        f"Image: `{image.as_posix()}`",
        f"SHA-256: `{digest}`",
        f"Expected SHA-256: `{EXPECTED_SHA256}`",
        f"Overall OK: `{all_ok}`",
        "",
        "## Visible version marker",
        "",
        *format_rows(version_rows),
        "",
        "Exp16 intentionally marks both internal version strings as `V4.0.1d`.",
        "The SD-card firmware filename remains `DM303V4.0.1-beta.bin`, but the",
        "device version screen must show the new marker if this exact build flashed.",
        "",
        "## Stream recovery patch bytes",
        "",
        *format_rows(stream_rows),
        "",
        "Three branches are changed to `NOP` so that the firmware returns",
        "through its existing failure/status path after the lower helper has",
        "already timed out. The command-0x40 busy-failure branch is not a NOP",
        "in exp10/exp11/exp12/exp13/exp14/exp15/exp16; it routes into the existing error/clear sequence so the",
        "status path is not treated as normal fall-through.",
        "",
        "## Bounded low byte-IO helper",
        "",
        *format_rows(wrapper_rows),
        "",
        "Exp16 keeps the exp11 route from `0x08016a06` to a local wrapper at `0x08016a50`.",
        "The wrapper keeps the SPI1 status/write/read HAL calls and a `0x0fa0`",
        "ready-wait budget, but returns `0xff` if either ready flag never",
        "appears. This is intended to expose timeout to the upper stream",
        "recovery instead of continuing with a stale byte read.",
        "",
        "## Command retry counters",
        "",
        *format_rows(retry_rows),
        "",
        "The two long command-specific bounded retry counts are reduced to",
        "`0x60`; the fallback count remains `0x0a`. This lowers worst-case",
        "status latency while preserving the same polling and failure path.",
        "",
        "## Stream state clear",
        "",
        *format_rows(state_rows),
        "",
        "Exp12/exp13/exp14/exp15/exp16 changes the existing nonzero-result cleanup from `bic #1` to",
        "`bic #3`. It clears only bits `0` and `1` of `0x2000022c`, leaving",
        "the other observed protection/status bits untouched. This targets the",
        "field symptom where the numeric reading and battery icon disappear",
        "together after spike, overload, or AC/DC switching.",
        "",
        "## Mode/range state clear",
        "",
        *format_rows(mode_state_rows),
        "",
        "Exp13/exp14/exp15/exp16 adds a guarded entry wrapper to the mode/range function. The",
        "wrapper runs the original prologue, clears the same stale stream bits",
        "`0` and `1`, then returns to the original function before relay/range",
        "logic continues. This is intended to stop stale busy/status state from",
        "surviving a DC/AC/DC transition.",
        "",
        "## Stream busy gate",
        "",
        *format_rows(busy_gate_rows),
        "",
        "Exp14 changes the entry stale-busy check at `0x080196be` from a",
        "conditional skip/return path to an unconditional branch into the",
        "normal transaction body. This targets the measured case where AC->DC",
        "ammeter recovery stays blank while the firmware waits for a stale",
        "busy gate to expire.",
        "",
        "## Current switch latency caps",
        "",
        *format_rows(current_latency_rows),
        "",
        "Exp14 caps two long transition gates from `0x3e80` to `0x0640`. The",
        "original value matches the reported roughly 30-second blank window",
        "when the scheduler tick is near 2ms, so this is a direct latency",
        "mitigation while keeping a bounded settle guard.",
        "",
        "",
        "## Exp16 rollback note",
        "",
        "Exp16 intentionally removes exp15's four immediate-switch gates and",
        "three stale bit0 bypass gates because the device showed the `V4.0.1c`",
        "marker with no performance improvement and possible regression. The",
        "remaining latency guard is the less aggressive exp14 cap plus the",
        "stream/state recovery bytes.",
    ]
    return "\n".join(lines) + "\n", all_ok


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--write-report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = args.image.read_bytes()
    report, ok = build_report(args.image, data)
    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        write_text_lf(args.write_report, report)
    print(f"latency_guard_ok={ok}")
    print(f"image={args.image}")
    print(f"sha256={sha256_file(args.image)}")
    if args.write_report:
        print(f"report={args.write_report}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
