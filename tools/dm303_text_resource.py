#!/usr/bin/env python3
"""Inspect and rebuild DM303 TEXT_*.DAT UI text resources.

The tool is read-only unless an explicit output path is provided. It is meant
for language-resource work and does not touch firmware binaries or update code.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path


DEFAULT_TEXT = Path("DM303-V4.0/system/TEXT_EN.DAT")


@dataclass(frozen=True)
class TextEntry:
    index: int
    entry_offset: int
    entry_bytes: bytes
    offset: int
    record_length: int
    raw_text: bytes
    text: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decode_text(raw: bytes) -> str:
    for encoding in ("utf-8", "gbk", "latin1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("latin1", "replace")


def encode_text(text: str) -> bytes:
    return text.encode("utf-8")


def parse_text_dat(path: Path) -> tuple[bytes, int, list[TextEntry]]:
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError(f"{path} is too small")

    count = int.from_bytes(data[2:4], "big")
    entries: list[TextEntry] = []

    for index in range(1, count + 1):
        entry_offset = 8 + (index - 1) * 8
        if entry_offset + 5 > len(data):
            raise ValueError(f"entry {index} offset table is outside file")

        entry_bytes = data[entry_offset : min(entry_offset + 8, len(data))]
        offset = int.from_bytes(data[entry_offset + 1 : entry_offset + 5], "big")
        if offset + 2 > len(data):
            raise ValueError(f"entry {index} text offset 0x{offset:x} is outside file")

        record_length = int.from_bytes(data[offset : offset + 2], "big")
        if record_length < 2:
            raise ValueError(f"entry {index} has invalid record length {record_length}")
        if offset + record_length > len(data):
            raise ValueError(f"entry {index} record extends outside file")

        raw_text = data[offset + 2 : offset + record_length]
        entries.append(
            TextEntry(
                index=index,
                entry_offset=entry_offset,
                entry_bytes=entry_bytes,
                offset=offset,
                record_length=record_length,
                raw_text=raw_text,
                text=decode_text(raw_text),
            )
        )

    return data, count, entries


def rebuild(data: bytes, entries: list[TextEntry], replacements: dict[int, str] | None = None) -> bytes:
    replacements = replacements or {}
    text_start = min(entry.offset for entry in entries)
    output = bytearray(data[:text_start])

    table_positions: list[int] = []
    for entry in entries:
        table_positions.append(entry.entry_offset)

    records = bytearray()
    for entry, table_pos in zip(entries, table_positions):
        new_offset = text_start + len(records)
        raw_text = encode_text(replacements[entry.index]) if entry.index in replacements else entry.raw_text
        record_length = len(raw_text) + 2
        if record_length > 0xFFFF:
            raise ValueError(f"entry {entry.index} text is too long")
        records.extend(record_length.to_bytes(2, "big"))
        records.extend(raw_text)
        output[table_pos + 1 : table_pos + 5] = new_offset.to_bytes(4, "big")

    output.extend(records)
    return bytes(output)


def export_csv(entries: list[TextEntry], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "offset", "record_length", "text"])
        for entry in entries:
            writer.writerow([entry.index, f"0x{entry.offset:04x}", entry.record_length, entry.text])


def printable(value: str) -> str:
    return value.encode("ascii", "backslashreplace").decode("ascii")


def load_replacements(path: Path) -> dict[int, str]:
    replacements: dict[int, str] = {}
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not row.get("translation"):
                continue
            replacements[int(row["index"])] = row["translation"]
    return replacements


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_TEXT)
    parser.add_argument("--export-csv", type=Path)
    parser.add_argument("--rebuild", type=Path, help="write a rebuilt DAT file")
    parser.add_argument("--translations-csv", type=Path, help="CSV with index and translation columns")
    parser.add_argument("--verify-rebuild", action="store_true")
    args = parser.parse_args()

    data, count, entries = parse_text_dat(args.input)
    print(f"input={args.input}")
    print(f"size={len(data)} sha256={sha256(data)}")
    print(f"entries={count}")
    print(f"first_text={printable(repr(entries[0].text))}")
    print(f"last_text={printable(repr(entries[-1].text))}")

    if args.export_csv:
        export_csv(entries, args.export_csv)
        print(f"export_csv={args.export_csv}")

    if args.verify_rebuild:
        rebuilt = rebuild(data, entries)
        print(f"rebuilt_size={len(rebuilt)} sha256={sha256(rebuilt)}")
        if rebuilt == data:
            print("verify_rebuild=byte-identical")
        else:
            print("verify_rebuild=structure-compatible-but-not-identical")

    if args.rebuild:
        replacements = load_replacements(args.translations_csv) if args.translations_csv else {}
        rebuilt = rebuild(data, entries, replacements)
        args.rebuild.parent.mkdir(parents=True, exist_ok=True)
        args.rebuild.write_bytes(rebuilt)
        print(f"wrote={args.rebuild} size={len(rebuilt)} sha256={sha256(rebuilt)}")
        print("safety_note=resource file only; firmware binary was not modified")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
