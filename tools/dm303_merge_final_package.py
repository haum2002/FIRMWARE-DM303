#!/usr/bin/env python3
"""Merge staged DM303 V4.0.1 beta artifacts into the final flash folder.

Workflow:
1. Treat backup/ as read-only reference input.
2. Treat firmware-candidates/v4.0.1-beta/ as staging output.
3. Rebuild dm303_firmware/DM303-V4.0.1-beta/ as the clean final flash package.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
BACKUP_V4 = WORKSPACE / "backup" / "DM303 V4.0-read only"
CANDIDATE = WORKSPACE / "firmware-candidates" / "v4.0.1-beta"
FINAL = WORKSPACE / "dm303_firmware" / "DM303-V4.0.1-beta"

CANDIDATE_BIN = CANDIDATE / "DM303V4.0.1-beta.bin"
CANDIDATE_MS = CANDIDATE / "system" / "TEXT_MS.DAT"
CANDIDATE_SP = CANDIDATE / "system" / "TEXT_SP.DAT"
CANDIDATE_ICON_SP = CANDIDATE / "system" / "icon-SP.dat"
CANDIDATE_LOGO = CANDIDATE / "system" / "LOGO-1.bmp"
FINAL_BIN = FINAL / "DM303V4.0.1-beta.bin"
FINAL_MS = FINAL / "system" / "TEXT_MS.DAT"
FINAL_SP = FINAL / "system" / "TEXT_SP.DAT"
FINAL_ICON_SP = FINAL / "system" / "icon-SP.dat"
FINAL_LOGO = FINAL / "system" / "LOGO-1.bmp"
FINAL_REPORT = CANDIDATE / "FINAL-PACKAGE-REPORT.md"
FINAL_SUMS = CANDIDATE / "FINAL-PACKAGE-SHA256.txt"
WORKSPACE_SUMS = WORKSPACE / "CHECKSUMS-SHA256.txt"

DEFAULT_PROFILE = "force-enhanced-exp4"
EXPECTED_CANDIDATE_SHA256_BY_PROFILE = {
    "anti-freeze-exp1": "de953819e5d9804cbb66eb7bb2bd17ac24d2d80282816951db1dd9048e77e6ab",
    "boot-acceptance": "ea910e141c9ddb19b550e4769fa87228fb5601492ae412487c39dc6efbc304d5",
    "relay-settle-exp1": "2ff2575d2e5d8311f8e6da26c2acee90231badf6eb77b2b21ce60c03abd6ae65",
    "force-stable-exp2": "74d1c7d812798277859f2c6c45b5263d72ca420c5c8093d3578a58f9a6f67854",
    "v316-switch-exp3": "ce6dfd8ef9a624bac2f9bb20be1d231cfd1f1379673e2a66d604ffd773ef9981",
    "force-enhanced-exp4": "f09f9f43a156b62e90c708c858986ae57f6baa2102a307f5830999b0557249da",
}
EXPECTED_MS_SHA256 = "7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd"
EXPECTED_SP_SHA256 = EXPECTED_MS_SHA256
EXPECTED_ICON_SP_SHA256 = "cd47c7e59f38488d6ffd10617a5d90ab5c79791535a3f75d70fbaaae42c7c4b3"
INCLUDE_DARK_MENU_ICONS = False
INCLUDE_MS_RESOURCE = True
REPLACE_SP_WITH_MS_RESOURCE = True
INCLUDE_MS_ICON_PACK = True
INCLUDE_BETA_LOGO = True


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def ensure_inside_workspace(path: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(WORKSPACE)
    return resolved


def copy_tree_contents(source: Path, destination: Path) -> None:
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def staged_system_overlays() -> list[Path]:
    system = CANDIDATE / "system"
    overlays: list[Path] = []
    if INCLUDE_MS_RESOURCE:
        overlays.append(CANDIDATE_MS)
    if REPLACE_SP_WITH_MS_RESOURCE:
        overlays.append(CANDIDATE_SP)
    if INCLUDE_MS_ICON_PACK:
        overlays.append(CANDIDATE_ICON_SP)
    if INCLUDE_BETA_LOGO:
        overlays.append(CANDIDATE_LOGO)
    if INCLUDE_DARK_MENU_ICONS:
        overlays.extend(sorted(system.glob("icon-E*.bmp")))
        overlays.extend(sorted(system.glob("icon-C*.bmp")))
    return sorted({path for path in overlays if path.exists()})


def profile_report_lines(profile: str) -> list[str]:
    if profile == "anti-freeze-exp1":
        return [
            "- Firmware code uses the `anti-freeze-exp1` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
        ]
    if profile == "relay-settle-exp1":
        return [
            "- Firmware code uses the `relay-settle-exp1` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits in function `0x0801f0f2` are extended without changing GPIO order or final pin states.",
        ]
    if profile == "force-stable-exp2":
        return [
            "- Firmware code uses the `force-stable-exp2` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks without changing GPIO order or final pin states.",
            "- This is a stability-first timing profile; switching and zeroing may feel slower by design.",
        ]
    if profile == "v316-switch-exp3":
        return [
            "- Firmware code uses the `v316-switch-exp3` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks.",
            "- Mode-switch helper `0x0801f0ac` is wrapped to call `selector(1, flag)` directly, matching the smoother V3.16 non-sub-mode-4 path while leaving call sites unchanged.",
        ]
    if profile == "force-enhanced-exp4":
        return [
            "- Firmware code uses the `force-enhanced-exp4` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks for stronger settling after relay/range changes.",
            "- Mode-switch helper `0x0801f0ac` is wrapped to call `selector(1, flag)` directly, matching the smoother V3.16 non-sub-mode-4 path while leaving call sites unchanged.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is a stability-first test profile; switching and boot may feel slower by design.",
        ]
    return [
        "- Firmware code uses the `boot-acceptance` rollback/diagnostic profile.",
        "- Fault/default handlers are kept unchanged.",
        "- Runtime fail-stop loops are kept unchanged.",
    ]


def validate_inputs(expected_candidate_sha256: str) -> None:
    required = [BACKUP_V4, CANDIDATE, CANDIDATE_BIN]
    if INCLUDE_MS_RESOURCE:
        required.append(CANDIDATE_MS)
    if REPLACE_SP_WITH_MS_RESOURCE:
        required.append(CANDIDATE_SP)
    if INCLUDE_MS_ICON_PACK:
        required.append(CANDIDATE_ICON_SP)
    if INCLUDE_BETA_LOGO:
        required.append(CANDIDATE_LOGO)
    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required input: {path}")

    candidate_hash = sha256_file(CANDIDATE_BIN)
    if candidate_hash != expected_candidate_sha256:
        raise SystemExit(f"Unexpected candidate firmware hash: {candidate_hash}")

    if INCLUDE_MS_RESOURCE:
        ms_hash = sha256_file(CANDIDATE_MS)
        if ms_hash != EXPECTED_MS_SHA256:
            raise SystemExit(f"Unexpected Malay text resource hash: {ms_hash}")
    if REPLACE_SP_WITH_MS_RESOURCE:
        sp_hash = sha256_file(CANDIDATE_SP)
        if sp_hash != EXPECTED_SP_SHA256:
            raise SystemExit(f"Unexpected SP-slot Malay text resource hash: {sp_hash}")
    if INCLUDE_MS_ICON_PACK:
        icon_hash = sha256_file(CANDIDATE_ICON_SP)
        if EXPECTED_ICON_SP_SHA256 and icon_hash != EXPECTED_ICON_SP_SHA256:
            raise SystemExit(f"Unexpected SP-slot Malay icon pack hash: {icon_hash}")


def rebuild_final() -> None:
    final_resolved = ensure_inside_workspace(FINAL)
    backup_resolved = ensure_inside_workspace(BACKUP_V4)
    candidate_resolved = ensure_inside_workspace(CANDIDATE)

    if backup_resolved == final_resolved or candidate_resolved == final_resolved:
        raise SystemExit("Refusing to merge: final path overlaps input path")

    if final_resolved.exists():
        shutil.rmtree(final_resolved)
    final_resolved.mkdir(parents=True)

    copy_tree_contents(backup_resolved, final_resolved)

    original_bin = final_resolved / "DM303V4.004.bin"
    if original_bin.exists():
        original_bin.unlink()

    shutil.copy2(CANDIDATE_BIN, FINAL_BIN)
    for source in staged_system_overlays():
        rel = source.relative_to(CANDIDATE)
        destination = FINAL / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def inventory(root: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            rows.append((rel, path.stat().st_size, sha256_file(path)))
    return rows


def validate_final(expected_candidate_sha256: str) -> list[tuple[str, int, str]]:
    rows = inventory(FINAL)
    rels = {rel for rel, _, _ in rows}
    if "DM303V4.004.bin" in rels:
        raise SystemExit("Final folder still contains original DM303V4.004.bin")
    if "system/system/ASCII64.dat" in rels:
        raise SystemExit("Final folder contains invalid nested system/system tree")
    if "DM303V4.0.1-beta.bin" not in rels:
        raise SystemExit("Final folder is missing DM303V4.0.1-beta.bin")
    if INCLUDE_MS_RESOURCE and "system/TEXT_MS.DAT" not in rels:
        raise SystemExit("Final folder is missing system/TEXT_MS.DAT")
    if REPLACE_SP_WITH_MS_RESOURCE and "system/TEXT_SP.DAT" not in rels:
        raise SystemExit("Final folder is missing replacement system/TEXT_SP.DAT")
    if INCLUDE_MS_ICON_PACK and "system/icon-SP.dat" not in rels:
        raise SystemExit("Final folder is missing replacement system/icon-SP.dat")
    if INCLUDE_BETA_LOGO and "system/LOGO-1.bmp" not in rels:
        raise SystemExit("Final folder is missing beta system/LOGO-1.bmp")

    final_bin_hash = sha256_file(FINAL_BIN)
    if final_bin_hash != expected_candidate_sha256:
        raise SystemExit(f"Final firmware hash mismatch: {final_bin_hash}")
    if INCLUDE_MS_RESOURCE:
        final_ms_hash = sha256_file(FINAL_MS)
        if final_ms_hash != EXPECTED_MS_SHA256:
            raise SystemExit(f"Final TEXT_MS hash mismatch: {final_ms_hash}")
    if REPLACE_SP_WITH_MS_RESOURCE:
        final_sp_hash = sha256_file(FINAL_SP)
        if final_sp_hash != EXPECTED_SP_SHA256:
            raise SystemExit(f"Final TEXT_SP hash mismatch: {final_sp_hash}")
    if INCLUDE_MS_ICON_PACK:
        final_icon_hash = sha256_file(FINAL_ICON_SP)
        if EXPECTED_ICON_SP_SHA256 and final_icon_hash != EXPECTED_ICON_SP_SHA256:
            raise SystemExit(f"Final icon-SP hash mismatch: {final_icon_hash}")

    return rows


def write_reports(rows: list[tuple[str, int, str]], profile: str) -> None:
    write_text_lf(FINAL_SUMS, "".join(f"{digest}  {rel}\n" for rel, _, digest in rows))
    prefix = FINAL.relative_to(WORKSPACE).as_posix()
    write_text_lf(
        WORKSPACE_SUMS,
        "".join(f"{digest}  {prefix}/{rel}\n" for rel, _, digest in rows),
    )

    lines = [
        "# DM303 V4.0.1 beta final package report",
        "",
        "Final folder: `dm303_firmware/DM303-V4.0.1-beta/`",
        "",
        "## Source rules",
        "",
        "- `backup/` is read-only reference input.",
        "- `firmware-candidates/v4.0.1-beta/` is staging output.",
        "- `dm303_firmware/DM303-V4.0.1-beta/` is rebuilt as the clean flash package.",
        "",
        "## Final package checks",
        "",
        f"- File count: `{len(rows)}`",
        f"- Firmware: `DM303V4.0.1-beta.bin`",
        f"- Firmware SHA-256: `{sha256_file(FINAL_BIN)}`",
        f"- Malay UI resource SHA-256: `{sha256_file(FINAL_MS) if INCLUDE_MS_RESOURCE else f'not included in this {profile} package'}`",
        f"- SP language slot replacement SHA-256: `{sha256_file(FINAL_SP) if REPLACE_SP_WITH_MS_RESOURCE else 'not replaced'}`",
        f"- Malay SP icon-pack SHA-256: `{sha256_file(FINAL_ICON_SP) if INCLUDE_MS_ICON_PACK else 'not included'}`",
        f"- Beta logo overlay SHA-256: `{sha256_file(FINAL_LOGO) if INCLUDE_BETA_LOGO else 'not included'}`",
        f"- Staged system overlays copied: `{len(staged_system_overlays())}`",
        "- Main navmenu BMP icons are restored to the official vendor V4.0 palette and glyph pixels from `backup/`.",
        "- `system/icon-SP.dat` replaces the Spanish graphical label pack with Malay labels while preserving the official 17-frame file size.",
        "- `system/LOGO-1.bmp` is converted into the official 16-bit resource layout from the selected beta artwork.",
        *profile_report_lines(profile),
        "- Header clock/date, 12/24 hour setting, and battery percent/bar display are not included because no safe runtime header hook has been confirmed.",
        "- Root firmware filename is intentionally `DM303V4.0.1-beta.bin` so the updater must display the beta identity.",
        "- The `DM303V4.0.1-beta.bin` content hash matches the staged V4.0.1 beta candidate.",
        "- Original root name `DM303V4.004.bin` is not present in the final package.",
        "- Invalid nested `system/system/` tree is not present.",
        "",
        "## Files",
        "",
        "| Path | Size | SHA-256 |",
        "|---|---:|---|",
    ]
    for rel, size, digest in rows:
        lines.append(f"| `{rel}` | {size} | `{digest}` |")
    write_text_lf(FINAL_REPORT, "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        choices=sorted(EXPECTED_CANDIDATE_SHA256_BY_PROFILE),
        default=DEFAULT_PROFILE,
        help="expected candidate profile to merge",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_candidate_sha256 = EXPECTED_CANDIDATE_SHA256_BY_PROFILE[args.profile]
    validate_inputs(expected_candidate_sha256)
    rebuild_final()
    rows = validate_final(expected_candidate_sha256)
    write_reports(rows, args.profile)

    print(f"backup_reference={BACKUP_V4}")
    print(f"candidate={CANDIDATE}")
    print(f"final={FINAL}")
    print(f"profile={args.profile}")
    print(f"final_files={len(rows)}")
    print(f"final_firmware_sha256={sha256_file(FINAL_BIN)}")
    if INCLUDE_MS_RESOURCE:
        print(f"final_text_ms_sha256={sha256_file(FINAL_MS)}")
    else:
        print("final_text_ms_sha256=not-included")
    if REPLACE_SP_WITH_MS_RESOURCE:
        print(f"final_text_sp_sha256={sha256_file(FINAL_SP)}")
    if INCLUDE_MS_ICON_PACK:
        print(f"final_icon_sp_sha256={sha256_file(FINAL_ICON_SP)}")
    print(f"report={FINAL_REPORT}")
    print(f"workspace_checksums={WORKSPACE_SUMS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
