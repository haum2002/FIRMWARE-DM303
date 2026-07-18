# DM303 V4.0.1r Combined Package (repair-j + Melayu/dark UI) — 2026-07-18

Status: **HOLD** — candidate package, not proven on-device. Do not flash
before explicit owner approval; bench/recovery validation is still required.

## Summary

`v401h-repair-j-ui-ms` combines the two previously gated lines into one
package:

1. **Measurement baseline** — `v401h-repair-j` (marker `V4.0.1q`): official
   V4.0 plus the ammeter AC/DC switch-state acquisition windows at `0x1df0c`
   (600 samples) and `0x1df40` (360 samples) lowered to the vendor's own
   240-sample normal-update window. Evidence:
   `docs/v313-v316-v40-switching-comparison-2026-07-17.md`.
2. **UI overlay** — the same Melayu/dark overlay shipped in `V4.0.1p`:
   full-Malay `TEXT_SP.DAT` (757/773 entries, official size and offset
   table), the `Melayu` language-slot name patch, and the dark RGB565 icon
   set (palette unchanged: `#0A233B` / `#EFF7FA` / `#FFCC48`).

The measurement bytes of repair-j are **not** modified; no new speculative
patch was added.

## Artifacts

| Item | Value |
|---|---|
| Profile | `v401h-repair-j-ui-ms` |
| Visible marker | `V4.0.1r` (device shows MT100MM/BT100MM V4.0.1r) |
| Firmware SHA-256 | `e75f8cbd8657c9a72f84ce454d5fc43298aead48c4053df00946eae3f99faf8c` |
| Firmware size | 203260 bytes (unchanged) |
| Candidate | `firmware-candidates/v4.0.1h-repair-j-ui-ms/` |
| Final package | `dm303_firmware/DM303-V4.0.1r-beta/` |
| TEXT_SP.DAT SHA-256 | `f955f4c83a57ac26150536a377f29b40c5d64fc5ceb2991e2c5fb7ef6c147fd9` |
| icon-SP.dat SHA-256 | `4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8` |
| DM30XDB1.dat SHA-256 | `846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79` |

## Exact patch content (firmware vs official V4.0)

| Offset | Before | After | Meaning |
|---:|---|---|---|
| `0x02ca0` | `MT100MM V4.0 \0..` | `MT100MM V4.0.1r\0` | version marker (MT) |
| `0x02cb0` | `BT100MM V4.0 \0..` | `BT100MM V4.0.1r\0` | version marker (BT) |
| `0x1df0c` | `4f f4 16 70` (mov.w r0,#0x258) | `40 f2 f0 00` (movw r0,#0xf0) | AC->DC switch window 600 -> 240 |
| `0x1df40` | `4f f4 b4 70` (mov.w r0,#0x168) | `40 f2 f0 00` (movw r0,#0xf0) | DC->AC switch window 360 -> 240 |
| `0x25bf8` | `Espa\xc3\xb1a` | `Melayu ` | language-slot rename, length preserved |

Raw byte-diff ranges vs official (inclusive):

```text
0x02cac-0x02cae, 0x02cbc-0x02cbe, 0x1df0c-0x1df0f, 0x1df40-0x1df43,
0x25bf8-0x25bfa, 0x25bfc-0x25bfe
```

The `0x25bf8`-`0x25bfe` name patch appears as **two** diff ranges because byte
`0x25bfb` is `0x61` (`a`) in both the official and the patched string. Total:
20 differing bytes. Delta vs `v401h-repair-j` firmware is exactly 8 bytes
(two marker bytes + six name bytes), mirroring the repair-i -> repair-i-ui-ms
delta.

## Build provenance

1. `tools/dm303_v401_beta_patch.py --profile v401h-repair-j-ui-ms --out-dir
   firmware-candidates/v4.0.1h-repair-j-ui-ms` (new profile: repair-j patch
   set + `visible-repair-j-ui-ms` marker + `language_name_patch`).
2. Overlay staging: dark assets copied from the audited
   `v4.0.1h-repair-i-ui-ms` staging folder; `TEXT_SP.DAT` staged from
   `localization/ms_MY/TEXT_SP.full-slot-replacement.DAT` (built by
   `tools/dm303_text_resource.py --rebuild` from
   `translations_ms_sp_full.csv`).
3. `tools/dm303_build_ui_overlay_sdroot.py --candidate-dir
   firmware-candidates/v4.0.1h-repair-j-ui-ms` — official V4.0 system +
   DM30XDB1.dat + overlay files only. The builder's expected TEXT_SP hash was
   updated from the superseded safe-layout resource (`96bde6bc...`) to the
   full-Malay resource (`f955f4c8...`); the `v4.0.1h-repair-i-ui-ms` staging
   folder was aligned to the same file so both candidates rebuild the shipped
   sd-roots.
4. Promoted by copying the gated sd-root to
   `dm303_firmware/DM303-V4.0.1r-beta/`; all gates re-run there.

## Tooling registrations

- `tools/dm303_v401_beta_patch.py` — profile `v401h-repair-j-ui-ms`,
  version patch profile `visible-repair-j-ui-ms`.
- `tools/dm303_repair_candidate_check.py` — `EXPECTED["v401h-repair-j-ui-ms"]`
  (firmware hash + full byte map). Note: its system-resource check assumes an
  official system folder, so for overlay packages the firmware byte/hash map
  is consumed through the measurement gate (`--firmware-only`) and the UI
  overlay checker instead.
- `tools/dm303_measurement_candidate_gate.py` — `EXPECTED_DIFF_RANGES` entry
  (the 6 ranges above) and a new `--firmware-only` mode that skips the
  SD-root layout/official-system checks for overlay packages while keeping
  the exact-diff and `MUST_MATCH_OFFICIAL` window checks.
- `tools/dm303_ui_overlay_candidate_check.py` — per-profile firmware hash and
  byte maps (`--profile`, default `v401h-repair-i-ui-ms`).
- `tools/dm303_preflash_check.py` — delegates both UI overlay profiles to the
  overlay checker (UI profiles take precedence over the repair path).

## Gate evidence (2026-07-18)

Candidate sd-root and promoted folder, identical results:

```text
ui_overlay_candidate_check=ok   firmware_sha256=e75f8cbd...
                                text_sp_sha256=f955f4c8... icon_sp_sha256=4b3e3c59...
measurement_candidate_gate=ok   firmware_only=True
                                diff_ranges=0x02cac-0x02cae, 0x02cbc-0x02cbe,
                                0x1df0c-0x1df0f, 0x1df40-0x1df43,
                                0x25bf8-0x25bfa, 0x25bfc-0x25bfe
                                ui_render_stream_io_relay_boot_windows=official
preflash_check=ok               ui_ms_system_resources=official_v4_plus_malay_dark_overlay
```

Independent audit `analysis/final-audit-2026-07-18.py` (re-derives every
expectation from the official backup, imports no project checker):
**AUDIT PASSED** for all four final packages (V4.0.1o, V4.0.1p, V4.0.1q,
V4.0.1r), including fresh Thumb-2 decode of both window patches
(`movw r0,#0xf0`), full diff sets, TEXT_SP structure (773 entries, 757
differing, offset table byte-identical), BMP RGB565 layouts, and
CHECKSUMS-SHA256.txt vs disk.

## Limitations

- Not proven on-device. The repair-j window change is expected to reduce the
  post-switch blank from ~30 s toward ~12 s if the analysis holds; it cannot
  restore V3.x-instant switching (ISR-ring architecture difference).
- Spanish is sacrificed: the language table has no confirmed spare slot, so
  the SP slot carries Malay.
- If AC->DC vs DC->AC asymmetry is not 5:3 before patching, or normal updates
  are also slow, the next suspect remains the 10-tick AFE re-kick at
  `0x0802d48c`-`0x0802d4b4` (see the three-way comparison report, section e).
