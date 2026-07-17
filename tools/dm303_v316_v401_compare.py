#!/usr/bin/env python3
"""Compare DM303 V3.16, official V4.0, and V4.0.1 beta evidence.

This helper is read-only. It does not patch or rewrite firmware. Its purpose is
to keep the V3.16 physical-test comparison repeatable before deciding whether a
V4.0.1 beta timing/profile change is worth testing on the device.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import re
import struct
from dataclasses import dataclass
from pathlib import Path


LOAD_BASE = 0x08010000

DEFAULT_IMAGES = {
    "v3.16": Path("backup/DM303 V3.16-read only/DM303V316.bin"),
    "v4.0": Path("backup/DM303 V4.0-read only/DM303V4.004.bin"),
    "v4.0.1f": Path("dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin"),
}
DEFAULT_REPORT = Path("docs/v316-v401-v401f-comparison-report.md")

KNOWN_POINTS = {
    "v3.16": {
        "selector": 0x0E1AC,
        "helper": 0x0E254,
        "mode_routine": 0x0E29A,
        "delays": {
            "pre_switch": 0x0E1C4,
            "bit_settle": 0x0E200,
            "post_switch": 0x0E24C,
        },
    },
    "v4.0": {
        "selector": 0x0F0F2,
        "helper": 0x0F0AC,
        "mode_routine": 0x0F19A,
        "delays": {
            "pre_switch": 0x0F10A,
            "bit_settle": 0x0F146,
            "post_switch": 0x0F192,
        },
    },
    "v4.0.1f": {
        "selector": 0x0F0F2,
        "helper": 0x0F0AC,
        "mode_routine": 0x0F19A,
        "delays": {
            "pre_switch": 0x0F10A,
            "bit_settle": 0x0F146,
            "post_switch": 0x0F192,
        },
    },
}

V4_ORIGINAL_HELPER_PREFIX = bytes.fromhex("10 b5 04 46 01 2c 08 d1 02 21 5e 48 1a f0 6d f9")
V316_HELPER_WRAPPER_PREFIX = bytes.fromhex("00 b5 01 46 01 20 00 f0 1e f8 00 bd 00 bf 00 bf")


@dataclass(frozen=True)
class ImageInfo:
    label: str
    path: Path
    data: bytes

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.data).hexdigest()

    @property
    def reset_vector(self) -> int:
        return u32_at(self.data, 4)

    @property
    def reset_offset(self) -> int | None:
        return addr_to_offset(self.reset_vector, len(self.data))


def u32_at(buf: bytes, offset: int) -> int:
    return struct.unpack_from("<I", buf, offset)[0]


def addr_to_offset(addr: int, image_size: int) -> int | None:
    addr &= ~1
    if LOAD_BASE <= addr < LOAD_BASE + image_size:
        return addr - LOAD_BASE
    return None


def offset_to_addr(offset: int) -> int:
    return LOAD_BASE + offset


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def extract_version_strings(buf: bytes) -> list[tuple[int, str]]:
    results: list[tuple[int, str]] = []
    pattern = re.compile(rb"[ -~]{6,}")
    wanted = re.compile(rb"(DM303|DM30|BT100|MT100|V[0-9])", re.IGNORECASE)
    for match in pattern.finditer(buf):
        raw = match.group(0)
        if wanted.search(raw):
            results.append((match.start(), raw.decode("ascii", "replace")))
    return results


def read_delay_value(buf: bytes, offset: int) -> int | None:
    if offset + 2 > len(buf):
        return None
    opcode = buf[offset : offset + 2]
    # Thumb MOVS Rd, #imm8 is 00 20 for R0 immediate.
    if opcode[1] != 0x20:
        return None
    return opcode[0]


def format_delay(value: int | None) -> str:
    return "?" if value is None else str(value)


def helper_status(info: ImageInfo, offset: int) -> str:
    prefix = info.data[offset : offset + len(V316_HELPER_WRAPPER_PREFIX)]
    if prefix == V316_HELPER_WRAPPER_PREFIX:
        return "v316-wrapper"
    if prefix == V4_ORIGINAL_HELPER_PREFIX:
        return "v4-original"
    if info.label == "v3.16":
        return "v3-original"
    return "unknown"


def load_images(paths: dict[str, Path]) -> list[ImageInfo]:
    images: list[ImageInfo] = []
    for label, path in paths.items():
        if not path.exists():
            raise SystemExit(f"Missing {label} image: {path}")
        images.append(ImageInfo(label, path, path.read_bytes()))
    return images


def print_summary(images: list[ImageInfo]) -> None:
    print("# DM303 V3.16 / V4.0 / V4.0.1f comparison")
    print()
    print("Read-only comparison; no firmware image is modified.")
    print()
    print("## Image identity")
    print()
    print("| Image | Path | Size | SHA-256 | Reset vector | Reset offset |")
    print("|---|---|---:|---|---:|---:|")
    for info in images:
        reset_offset = "n/a" if info.reset_offset is None else f"`0x{info.reset_offset:05x}`"
        print(
            f"| {info.label} | `{info.path.as_posix()}` | {len(info.data)} | "
            f"`{info.sha256}` | `0x{info.reset_vector:08x}` | {reset_offset} |"
        )

    print()
    print("## Version-like strings")
    print()
    for info in images:
        print(f"### {info.label}")
        strings = extract_version_strings(info.data)
        if not strings:
            print("- none found")
            continue
        for offset, text in strings[:12]:
            print(f"- `0x{offset:05x}`: `{text}`")
        if len(strings) > 12:
            print(f"- ... {len(strings) - 12} more")

    print()
    print("## Known relay/range selector timing evidence")
    print()
    print("| Image | Selector addr | Helper addr | Mode routine addr | Helper status | Pre-switch | Bit-settle | Post-switch |")
    print("|---|---:|---:|---:|---|---:|---:|---:|")
    for info in images:
        points = KNOWN_POINTS[info.label]
        delays = points["delays"]
        pre = read_delay_value(info.data, delays["pre_switch"])
        bit = read_delay_value(info.data, delays["bit_settle"])
        post = read_delay_value(info.data, delays["post_switch"])
        print(
            f"| {info.label} | `0x{offset_to_addr(points['selector']):08x}` | "
            f"`0x{offset_to_addr(points['helper']):08x}` | "
            f"`0x{offset_to_addr(points['mode_routine']):08x}` | "
            f"{helper_status(info, points['helper'])} | "
            f"{format_delay(pre)} | {format_delay(bit)} | {format_delay(post)} |"
        )

    print()
    print("## Interpretation guardrails")
    print()
    print("- V3.16 and official V4.0 use the same observed selector waits: `2/3/10` ticks.")
    print("- If V3.16 switches DC/AC smoothly, the improvement is probably not from longer relay waits.")
    print("- Current V4.0.1f should be `stability-exp18-resource` with original helper behavior, official/V3.16 `2/3/10` timing, complete `DM30XDB1.dat` resources, fail-fast/error-route stream recovery, low byte-IO routed through a bounded `0x0fa0` failure-return wrapper, command 0x40/0x48 retry clamp `0x60`, stream cleanup that clears stale flag bits `0` and `1`, a guarded mode/range entry wrapper that clears the same stale bits before relay/range switching, stale-busy stream early-return bypass, and two current-switch long-gate caps.")
    print("- Old long-delay or wrapper profiles are diagnostic comparisons, not proven analog math or True RMS fixes.")
    print("- Do not blindly port V3.16 behavior: the user observed weaker battery, ohmmeter, and continuity stability there.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--v316", type=Path, default=DEFAULT_IMAGES["v3.16"])
    parser.add_argument("--v40", type=Path, default=DEFAULT_IMAGES["v4.0"])
    parser.add_argument("--v401", type=Path, default=DEFAULT_IMAGES["v4.0.1f"])
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    images = load_images(
        {
            "v3.16": args.v316,
            "v4.0": args.v40,
            "v4.0.1f": args.v401,
        }
    )
    if args.report:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_summary(images)
        text = buffer.getvalue()
        write_text_lf(args.report, text)
        print(text, end="")
        print(f"\nreport={args.report}")
    else:
        print_summary(images)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
