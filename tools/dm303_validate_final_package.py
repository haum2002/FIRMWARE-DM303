#!/usr/bin/env python3
"""Validate the current DM303 V4.0.1 beta staging and final flash package.

This script is read-only. It reuses the same guards as the merge tool and adds a
small final-folder sanity summary so a package can be checked immediately before
copying to an SD card.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from dm303_merge_final_package import (
    EXPECTED_CANDIDATE_SHA256_BY_PROFILE,
    FINAL,
    FINAL_BIN,
    FINAL_ICON_SP,
    FINAL_LOGO,
    FINAL_MS,
    FINAL_SP,
    validate_final,
    validate_inputs,
    sha256_file,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        choices=sorted(EXPECTED_CANDIDATE_SHA256_BY_PROFILE),
        default="stability-exp20-ms-safe",
        help="expected firmware profile",
    )
    return parser.parse_args()


def require_no_nested_system(root: Path) -> None:
    bad = root / "system" / "system"
    if bad.exists():
        raise SystemExit(f"Invalid nested system folder exists: {bad}")


def main() -> int:
    args = parse_args()
    expected_hash = EXPECTED_CANDIDATE_SHA256_BY_PROFILE[args.profile]
    validate_inputs(expected_hash, args.profile)
    rows = validate_final(expected_hash, args.profile)
    require_no_nested_system(FINAL)

    print("dm303_final_validation=ok")
    print(f"profile={args.profile}")
    print(f"final={FINAL}")
    print(f"final_files={len(rows)}")
    print(f"firmware_sha256={sha256_file(FINAL_BIN)}")
    print(f"text_ms_sha256={sha256_file(FINAL_MS)}")
    print(f"text_sp_sha256={sha256_file(FINAL_SP)}")
    print(f"icon_sp_sha256={sha256_file(FINAL_ICON_SP)}")
    print(f"logo_sha256={sha256_file(FINAL_LOGO)}")
    print("checked=firmware_hash,version_marker,dm30xdb1_resource,text_hashes,icon_pack_hash,logo_hash,bmp_rgb565_layout,icon_count,no_nested_system")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
