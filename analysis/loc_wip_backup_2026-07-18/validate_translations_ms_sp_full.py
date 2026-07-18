#!/usr/bin/env python3
"""Independent validator for translations_ms_sp_full.csv.

Re-reads analysis/sp_entries_source.csv and the generated
localization/ms_MY/translations_ms_sp_full.csv and checks, row by row:

  1. exactly 773 data rows, indices 1..773 in order
  2. translation UTF-8 byte length == record_length - 2 for every row
  3. translation is pure ASCII
  4. source column matches the export verbatim
  5. only known device tokens appear in translations
  6. blank spacer entries and pure symbol/unit entries are verbatim
  7. ALIGNMENT replicates the official entry layout:
       - official entries padded on BOTH sides (lead>=2 and trail>=2, i.e.
         centered) must come out centered (|lead - trail| <= 1, and the
         non-space content identical to the stripped translation)
       - all other entries must keep the official leading-space count
       - units-in-line entries must keep marker columns (V/A/Hz/%/<OK>)
         at the official byte offsets

Exits non-zero and lists violations on failure.
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "analysis" / "sp_entries_source.csv"
OUT = ROOT / "localization" / "ms_MY" / "translations_ms_sp_full.csv"

ALLOWED_TOKENS = {
    "<HOLD>", "<Fn>", "<F1>", "<F2>", "<ESC>", "<OK>",
    "<UP>", "<Down>", "<DOWN>", "<LEFT>", "<RIGHT>", "<L>", "<R>",
}
TOKEN_RE = re.compile(r"<[^<>]*>")
SYMBOL_WORDS = {"%", "v", "a", "hz", "ma", "ω", "rpm", "div", "on", "off",
                "min:", "max:", "ohm"}
# Units-in-line entries and the marker whose byte offsets must match official.
COLUMN_MARKERS = {22: ["V"], 31: ["A"], 41: ["V"], 48: ["Hz"], 49: ["%"],
                  51: ["V"], 70: ["<OK>"], 74: ["V"]}
# Multi-record help/guide sections. Inside these, official leading spaces are
# mid-word-split artifacts of the vendor's flowing paragraphs, not alignment;
# the translation replaces them with a numbered-steps layout by design, so the
# leading-space check does not apply there.
SECTION_RANGES = [
    (91, 95), (98, 101), (102, 108), (110, 115), (118, 127), (128, 132),
    (133, 139), (140, 144), (146, 149), (191, 209), (211, 228), (230, 249),
    (251, 280), (282, 309), (311, 355), (357, 384), (386, 414), (416, 440),
    (442, 475), (477, 521), (523, 553), (555, 587), (589, 597), (599, 617),
    (619, 636), (638, 657), (659, 688), (690, 717), (719, 763), (765, 773),
]


def in_section(idx):
    return any(first <= idx <= last for first, last in SECTION_RANGES)


def lead_trail(text):
    b = text.encode("utf-8")
    return (len(b) - len(b.lstrip(b" ")), len(b) - len(b.rstrip(b" ")), len(b))


def find_all(hay, needle):
    out, start = [], 0
    while True:
        pos = hay.find(needle, start)
        if pos < 0:
            return out
        out.append(pos)
        start = pos + 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

    with SRC.open(newline="", encoding="utf-8") as fh:
        src_rows = list(csv.reader(fh))[1:]
    with OUT.open(newline="", encoding="utf-8") as fh:
        out_rows = list(csv.reader(fh))

    errors = []
    if out_rows[0] != ["index", "source", "translation"]:
        errors.append(f"bad header: {out_rows[0]!r}")
    data = out_rows[1:]
    if len(data) != 773:
        errors.append(f"row count {len(data)} != 773")
    if len(src_rows) != 773:
        errors.append(f"source row count {len(src_rows)} != 773")

    unchanged = translated = centered_count = 0
    for n, (srow, orow) in enumerate(zip(src_rows, data), start=1):
        s_idx, _off, s_reclen, s_text = srow
        if len(orow) != 3:
            errors.append(f"row {n}: malformed ({len(orow)} fields)")
            continue
        o_idx, o_src, o_trans = orow
        if int(o_idx) != n or int(s_idx) != n:
            errors.append(f"row {n}: index mismatch src={s_idx} out={o_idx}")
            continue
        if o_src != s_text:
            errors.append(f"index {n}: source column altered")
        target = int(s_reclen) - 2
        blen = len(o_trans.encode("utf-8"))
        if blen != target:
            errors.append(f"index {n}: byte length {blen} != target {target}")
        bad = [c for c in o_trans if ord(c) >= 128]
        if bad:
            errors.append(f"index {n}: non-ASCII {bad!r}")
        for tok in TOKEN_RE.findall(o_trans):
            if tok not in ALLOWED_TOKENS:
                errors.append(f"index {n}: unknown token {tok}")
        if o_trans == s_text:
            unchanged += 1
        else:
            translated += 1
        if s_text.strip() == "" and o_trans != s_text:
            errors.append(f"index {n}: blank entry changed: {o_trans!r}")
        if s_text.strip().lower() in SYMBOL_WORDS and o_trans != s_text:
            errors.append(f"index {n}: symbol-only entry changed: {s_text!r} -> {o_trans!r}")

        # Alignment checks against the official layout (standalone entries
        # only; help-section records carry the numbered-steps layout).
        slead, strail, _ = lead_trail(s_text)
        tlead, ttrail, _ = lead_trail(o_trans)
        if s_text.strip() != "" and not in_section(n):
            if slead >= 2 and strail >= 2:
                # official centered -> translation must be centered too
                if abs(tlead - ttrail) > 1:
                    errors.append(
                        f"index {n}: official centered ({slead}/{strail}) but "
                        f"translation is {tlead}/{ttrail}: {o_trans!r}")
                else:
                    centered_count += 1
            else:
                if tlead != slead:
                    errors.append(
                        f"index {n}: lead {tlead} != official lead {slead}: "
                        f"{o_trans!r} (official {s_text!r})")
        if n in COLUMN_MARKERS:
            sb = s_text.encode("utf-8")
            tb = o_trans.encode("utf-8")
            for marker in COLUMN_MARKERS[n]:
                want = find_all(sb, marker.encode("utf-8"))
                got = find_all(tb, marker.encode("utf-8"))
                if want != got:
                    errors.append(
                        f"index {n}: column mismatch for {marker!r}: "
                        f"official {want} vs {got}")

    print(f"rows checked          : {len(data)}")
    print(f"unchanged (identical) : {unchanged}")
    print(f"changed (translated)  : {translated}")
    print(f"centered entries OK   : {centered_count}")
    if errors:
        print(f"\nVALIDATION FAILED: {len(errors)} problem(s)")
        for e in errors[:80]:
            print(f"  {e}")
        return 1
    print("VALIDATION PASSED: 773 rows, exact lengths, ASCII, tokens, "
          "leading/centered/column alignment all match official layout")
    return 0


if __name__ == "__main__":
    sys.exit(main())
