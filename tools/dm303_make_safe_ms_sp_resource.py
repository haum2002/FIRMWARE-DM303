#!/usr/bin/env python3
"""Build a safer Malay replacement for the existing SP text slot.

The previous Malay SP replacement reused the English TEXT_EN.DAT structure.
That file has more entries than TEXT_SP.DAT, which can make the SP language
loader reject or misread the resource. This tool starts from the official
TEXT_SP.DAT layout and only replaces entries that exist in that slot and fit
inside the original entry byte length.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from dm303_make_ms_pack import STATIC_TRANSLATIONS
from dm303_text_resource import parse_text_dat, rebuild, sha256


DEFAULT_SOURCE = Path("backup/DM303 V4.0-read only/system/TEXT_SP.DAT")
DEFAULT_OUTPUT = Path("localization/ms_MY/TEXT_SP.safe-slot-replacement.DAT")
DEFAULT_REPORT = Path("localization/ms_MY/TEXT_SP.safe-slot-replacement.csv")


def build_safe_replacements(entries) -> tuple[dict[int, str], list[tuple[int, str, str, int, int]]]:
    lengths = {entry.index: len(entry.raw_text) for entry in entries}
    replacements: dict[int, str] = {}
    report: list[tuple[int, str, str, int, int]] = []
    for index, text in sorted(STATIC_TRANSLATIONS.items()):
        if index not in lengths:
            report.append((index, "missing", text, 0, len(text.encode("utf-8"))))
            continue
        encoded_len = len(text.encode("utf-8"))
        limit = lengths[index]
        if encoded_len > limit:
            report.append((index, "too-long", text, limit, encoded_len))
            continue
        replacements[index] = text
        report.append((index, "replaced", text, limit, encoded_len))
    return replacements, report


def write_report(path: Path, report: list[tuple[int, str, str, int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "status", "text", "source_limit", "encoded_length"])
        writer.writerows(report)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    data, count, entries = parse_text_dat(args.source)
    replacements, report = build_safe_replacements(entries)
    rebuilt = rebuild(data, entries, replacements)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(rebuilt)
    write_report(args.report, report)

    replaced = sum(1 for _, status, _, _, _ in report if status == "replaced")
    skipped = len(report) - replaced
    print(f"source={args.source}")
    print(f"source_entries={count}")
    print(f"source_size={len(data)} source_sha256={sha256(data)}")
    print(f"output={args.output}")
    print(f"output_size={len(rebuilt)} output_sha256={sha256(rebuilt)}")
    print(f"replaced={replaced}")
    print(f"skipped={skipped}")
    print(f"report={args.report}")
    print("safety_note=SP-slot structure preserved; only fitting entries replaced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
