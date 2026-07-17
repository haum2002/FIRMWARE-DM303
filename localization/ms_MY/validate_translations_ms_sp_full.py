#!/usr/bin/env python3
"""Independent validator for translations_ms_sp_full.csv.

Re-reads analysis/sp_entries_source.csv and the generated
localization/ms_MY/translations_ms_sp_full.csv and checks, row by row:

  1. exactly 773 data rows, indices 1..773 in order
  2. translation UTF-8 byte length == record_length - 2 for every row
  3. translation is pure ASCII
  4. source column matches the export verbatim
  5. only known device tokens appear in translations
  6. unchanged entries (all-space or pure symbol/unit sources) are intact

Exits non-zero and lists every violation on failure.
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
# Exact pure symbol/unit contents (after stripping) that must stay verbatim.
SYMBOL_WORDS = {"%", "v", "a", "hz", "ma", "ω", "rpm", "div", "on", "off",
                "min:", "max:", "ohm"}


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

    unchanged = 0
    translated = 0
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
            errors.append(f"index {n}: source column altered: {o_src!r} != {s_text!r}")
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
            # pure symbol/unit entries must stay verbatim
            errors.append(f"index {n}: symbol-only entry changed: {s_text!r} -> {o_trans!r}")

    print(f"rows checked          : {len(data)}")
    print(f"unchanged (identical) : {unchanged}")
    print(f"changed (translated)  : {translated}")
    if errors:
        print(f"\nVALIDATION FAILED: {len(errors)} problem(s)")
        for e in errors[:60]:
            print(f"  {e}")
        return 1
    print("VALIDATION PASSED: all 773 rows exact-length, pure ASCII, tokens OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
