#!/usr/bin/env python3
"""Read-only validation for isolated DM303 repair candidates."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


EXPECTED = {
    "v401h-repair-a": {
        "sha256": "66315b32c079842251143450bb853c5f60a29bb27c93b73f03389a9813b1cd36",
        "bytes": {
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x15934: bytes.fromhex("43 f6 98 21"),
            0x1595C: bytes.fromhex("43 f6 98 21"),
        },
    },
    "v401h-repair-b": {
        "sha256": "3ef4cfd80a86f984a8679c3e340eb17a3441e8d761b16046693eb18c230d5613",
        "bytes": {
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
        },
    },
    "v401h-repair-c": {
        "sha256": "70b98735978f711c2203c0b907927aded22eb91ca03fdc601ebdfb33f56b117d",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1i\x00",
            0x02CB0: b"BT100MM V4.0.1i\x00",
            0x0F10A: bytes.fromhex("05 20"),
            0x0F146: bytes.fromhex("08 20"),
            0x0F192: bytes.fromhex("32 20"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
        },
    },
    "v401h-repair-d": {
        "sha256": "0d0899258a5167e34e56485aeb7a72d74211dd9c40ec2faa5e9412fe8107b41c",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1j\x00",
            0x02CB0: b"BT100MM V4.0.1j\x00",
            0x0C6C8: bytes.fromhex("fe e7"),
            0x0F10A: bytes.fromhex("02 20"),
            0x0F146: bytes.fromhex("03 20"),
            0x0F192: bytes.fromhex("0a 20"),
            0x15812: bytes.fromhex("00 bf"),
            0x15838: bytes.fromhex("00 bf"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15862: bytes.fromhex("00 bf"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x1588C: bytes.fromhex("00 bf"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
        },
    },
    "v401h-repair-e": {
        "sha256": "75dffe2bbe1ed3193c3073f39d018c888f4a684440e17647645bd18d7ef40216",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1k\x00",
            0x02CB0: b"BT100MM V4.0.1k\x00",
            0x09CA0: bytes.fromhex("fe e7"),
            0x0C6C8: bytes.fromhex("fe e7"),
            0x2C4EA: bytes.fromhex("fe e7"),
            0x0F10A: bytes.fromhex("02 20"),
            0x0F146: bytes.fromhex("03 20"),
            0x0F192: bytes.fromhex("0a 20"),
            0x15812: bytes.fromhex("00 bf"),
            0x15838: bytes.fromhex("00 bf"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15862: bytes.fromhex("00 bf"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x1588C: bytes.fromhex("00 bf"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
        },
    },
    "v401h-repair-f": {
        "sha256": "a324b9dfc0647601a7775685f15d17185da01d8443b1b2cd67aa7ea7709d4de3",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1l\x00",
            0x02CB0: b"BT100MM V4.0.1l\x00",
            0x09CA0: bytes.fromhex("fe e7"),
            0x0C6C8: bytes.fromhex("fe e7"),
            0x2C4EA: bytes.fromhex("fe e7"),
            0x0F10A: bytes.fromhex("02 20"),
            0x0F146: bytes.fromhex("03 20"),
            0x0F192: bytes.fromhex("0a 20"),
            0x06A06: bytes.fromhex("70 b5 05 46"),
            0x096BE: bytes.fromhex("10 b1"),
            0x097E8: bytes.fromhex("01"),
            0x0F19A: bytes.fromhex("10 b5 04 46"),
            0x15812: bytes.fromhex("00 bf"),
            0x15838: bytes.fromhex("00 bf"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15862: bytes.fromhex("00 bf"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x1588C: bytes.fromhex("00 bf"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
        },
    },
    "v401h-repair-g": {
        "sha256": "a84dda5e7f3d675d0985bde4c431a0d86c21d063d7c2dfd56a68726690566c7d",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1m\x00",
            0x02CB0: b"BT100MM V4.0.1m\x00",
            0x09CA0: bytes.fromhex("fe e7"),
            0x0C6C8: bytes.fromhex("fe e7"),
            0x2C4EA: bytes.fromhex("fe e7"),
            0x0F10A: bytes.fromhex("02 20"),
            0x0F146: bytes.fromhex("03 20"),
            0x0F192: bytes.fromhex("0a 20"),
            0x06A06: bytes.fromhex("70 b5 05 46"),
            0x096BE: bytes.fromhex("10 b1"),
            0x097E8: bytes.fromhex("01"),
            0x0F19A: bytes.fromhex("10 b5 04 46"),
            0x14B0E: bytes.fromhex("40 f2 dc 50"),
            0x14B36: bytes.fromhex("40 f2 dc 50"),
            0x15812: bytes.fromhex("00 bf"),
            0x15838: bytes.fromhex("00 bf"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15862: bytes.fromhex("00 bf"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x1588C: bytes.fromhex("00 bf"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
        },
    },
    "v401h-repair-h": {
        "sha256": "52c49425aa655999982bce98e8ebd39221b5c2208d168785dbb56a48730dac92",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1n\x00",
            0x02CB0: b"BT100MM V4.0.1n\x00",
            0x09CA0: bytes.fromhex("fe e7"),
            0x0C6C8: bytes.fromhex("fe e7"),
            0x2C4EA: bytes.fromhex("fe e7"),
            0x0F10A: bytes.fromhex("02 20"),
            0x0F146: bytes.fromhex("03 20"),
            0x0F192: bytes.fromhex("0a 20"),
            0x06A06: bytes.fromhex("70 b5 05 46"),
            0x096BE: bytes.fromhex("10 b1"),
            0x097E8: bytes.fromhex("01"),
            0x0F19A: bytes.fromhex("10 b5 04 46"),
            0x14B0E: bytes.fromhex("40 f2 dc 50"),
            0x14B36: bytes.fromhex("40 f2 dc 50"),
            0x15812: bytes.fromhex("00 bf"),
            0x15838: bytes.fromhex("00 bf"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15862: bytes.fromhex("00 bf"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x1588C: bytes.fromhex("00 bf"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
            0x1D1A4: bytes.fromhex("40 f2 dc 50"),
            0x1D1C0: bytes.fromhex("40 f2 dc 50"),
        },
    },
    "v401h-repair-i": {
        "sha256": "11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953",
        "bytes": {
            0x02CA0: b"MT100MM V4.0.1o\x00",
            0x02CB0: b"BT100MM V4.0.1o\x00",
            0x09CA0: bytes.fromhex("fe e7"),
            0x0C6C8: bytes.fromhex("fe e7"),
            0x2C4EA: bytes.fromhex("fe e7"),
            0x0F10A: bytes.fromhex("02 20"),
            0x0F146: bytes.fromhex("03 20"),
            0x0F192: bytes.fromhex("0a 20"),
            0x06A06: bytes.fromhex("70 b5 05 46"),
            0x096BE: bytes.fromhex("10 b1"),
            0x097E8: bytes.fromhex("01"),
            0x0F19A: bytes.fromhex("10 b5 04 46"),
            0x14B0E: bytes.fromhex("40 f2 dc 50"),
            0x14B36: bytes.fromhex("40 f2 dc 50"),
            0x15812: bytes.fromhex("00 bf"),
            0x15838: bytes.fromhex("00 bf"),
            0x1585E: bytes.fromhex("b0 f5 c8 6f"),
            0x15862: bytes.fromhex("00 bf"),
            0x15888: bytes.fromhex("b0 f5 c8 6f"),
            0x1588C: bytes.fromhex("00 bf"),
            0x15934: bytes.fromhex("40 f2 dc 51"),
            0x1595C: bytes.fromhex("40 f2 dc 51"),
            0x1D1A4: bytes.fromhex("40 f2 dc 50"),
            0x1D1C0: bytes.fromhex("40 f2 dc 50"),
            0x1D1DA: bytes.fromhex("40 20"),
        },
    },
}

EXPECTED_DM30XDB1_SHA256 = "846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79"
OFFICIAL_SYSTEM = Path("backup/DM303 V4.0-read only/system")
ROOT_FILES = {"DM303V4.0.1-beta.bin", "QBtest.txt", "readme.txt"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"repair_candidate_check=failed\nreason={message}")


def validate_layout(root: Path) -> None:
    if not root.is_dir():
        fail(f"root folder does not exist: {root}")
    if (root / "DM303-V4.0.1-beta" / "DM303V4.0.1-beta.bin").exists():
        fail("firmware is inside an extra folder; copy SD-root contents only")
    if (root / "DM303V4.004.bin").exists():
        fail("official DM303V4.004.bin must not be present in repair SD-root")
    missing = sorted(name for name in ROOT_FILES if not (root / name).is_file())
    if missing:
        fail(f"missing root files: {missing}")
    if not (root / "system").is_dir():
        fail("missing system folder")
    extras = sorted(path.name for path in root.iterdir() if path.name not in ROOT_FILES and path.name != "system")
    if extras:
        fail(f"unexpected root entries: {extras}")


def validate_firmware(root: Path, profile: str) -> None:
    firmware = root / "DM303V4.0.1-beta.bin"
    if firmware.stat().st_size != 203260:
        fail(f"unexpected firmware size: {firmware.stat().st_size}")
    digest = sha256_file(firmware)
    if digest != EXPECTED[profile]["sha256"]:
        fail(f"unexpected firmware hash: {digest}")
    data = firmware.read_bytes()
    for offset, expected in EXPECTED[profile]["bytes"].items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            fail(f"byte mismatch at 0x{offset:05x}: expected {expected.hex(' ')}, got {actual.hex(' ')}")


def validate_official_system(root: Path) -> None:
    system = root / "system"
    for official in OFFICIAL_SYSTEM.iterdir():
        if not official.is_file():
            continue
        candidate = system / official.name
        if not candidate.is_file():
            fail(f"missing official system file: {official.name}")
        if sha256_file(candidate) != sha256_file(official):
            fail(f"system file differs from official V4.0: {official.name}")
    dm30xdb1 = system / "DM30XDB1.dat"
    if not dm30xdb1.is_file():
        fail("missing added DM30XDB1.dat")
    if sha256_file(dm30xdb1) != EXPECTED_DM30XDB1_SHA256:
        fail(f"unexpected DM30XDB1.dat hash: {sha256_file(dm30xdb1)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--profile", choices=sorted(EXPECTED), required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    validate_layout(root)
    validate_firmware(root, args.profile)
    validate_official_system(root)
    print("repair_candidate_check=ok")
    print(f"root={root}")
    print(f"profile={args.profile}")
    print(f"firmware_sha256={sha256_file(root / 'DM303V4.0.1-beta.bin')}")
    print(f"dm30xdb1_sha256={sha256_file(root / 'system' / 'DM30XDB1.dat')}")
    print("official_v4_system_resources=match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
