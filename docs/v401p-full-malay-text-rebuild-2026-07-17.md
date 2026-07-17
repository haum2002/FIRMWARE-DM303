# DM303 V4.0.1p full-Malay text resource rebuild (2026-07-17)

Status: staged in `dm303_firmware/DM303-V4.0.1p-ms-beta/` (HOLD, not yet
device-tested). This document records the defect found by field feedback and
the corrective rebuild.

## 1. Field feedback (user device test, 2026-07-17)

The user flashed the V4.0.1p package and reported that the Malay UI "does not
work / is not complete": most screens still showed Spanish or English, and
some text appeared in wrong positions.

The user also confirmed the measurement symptoms (noise, unstable readings,
AC->DC latency, zero/calibration trouble) are still present on the repair-i
baseline — see section 5.

## 2. Root cause: EN/SP index misalignment

The previous SP-slot replacement (`TEXT_SP.safe-slot-replacement.DAT`, 137
entries) was built from `STATIC_TRANSLATIONS` in `tools/dm303_make_ms_pack.py`,
which is keyed by **TEXT_EN.DAT indices**. Fresh comparison of the official
resources shows the two files are **not index-aligned**:

- `TEXT_EN.DAT`: 815 entries. `TEXT_SP.DAT`: 773 entries.
- Indices 1–89 correspond (settings/menus region).
- From index 90 onward the content diverges: e.g. EN[90] =
  `Voltage Signal Output` while SP[90] is a blank spacer; EN[104] =
  `Drive the fuel injector: Choose ` while SP[104] =
  `negro a la plancha del vehículo,`.

Consequences for the old package:

- Only 137 of 773 SP entries (17.7%) were ever replaced.
- Replacements beyond the aligned region landed on **unrelated Spanish
  strings**, so Malay fragments could appear in the wrong help/manual
  positions.

This is exactly the "incomplete / not working" behavior reported on-device.

## 3. Corrective rebuild: full translation keyed by SP index

- New complete translation table: `localization/ms_MY/translations_ms_sp_full.csv`
  (773 rows, keyed by **SP entry index**, built from the official SP text
  itself). Produced with `localization/ms_MY/build_translations_ms_sp_full.py`
  and independently checked by
  `localization/ms_MY/validate_translations_ms_sp_full.py`.
- **757 entries translated** to Bahasa Melayu; **16 entries unchanged**
  (8 blank spacers, 5 pure symbols/units `% V div ON OFF`, `Normal`,
  `Hardware: `/`Software: ` kept by existing convention).
- Every translation is exactly its official entry's byte length (padded with
  trailing spaces, never longer), so the rebuilt resource preserves the vendor
  layout byte-for-byte:
  - rebuilt `TEXT_SP.DAT` size = official 32888 bytes;
  - header + entire offset table (bytes 0..6189) byte-identical to official;
  - only record text bytes differ.
- Device tokens kept verbatim (`<HOLD> <Fn> <F1> <F2> <ESC> <OK> <UP> <DOWN>
  <LEFT> <RIGHT>`); Spanish-only tokens `<Arriba>/<Abajo>/<Izquierdo>/
  <Derecho>` converted to the real device tokens. Translations are pure ASCII.
- Continuous help paragraphs (split by the vendor into fixed-size chunks) were
  translated as flowing Malay and re-wrapped across the same chunk boundaries.

Build command (stdlib, from repo root):

```powershell
python tools/dm303_text_resource.py --input "backup/DM303 V4.0-read only/system/TEXT_SP.DAT" --rebuild localization/ms_MY/TEXT_SP.full-slot-replacement.DAT --translations-csv localization/ms_MY/translations_ms_sp_full.csv
```

Output SHA-256:
`f955f4c83a57ac26150536a377f29b40c5d64fc5ceb2991e2c5fb7ef6c147fd9`
(registered as `EXPECTED_SAFE_SP_SHA256` in
`tools/dm303_ui_overlay_candidate_check.py`).

The new file replaces `system/TEXT_SP.DAT` in
`dm303_firmware/DM303-V4.0.1p-ms-beta/` and in the staging sd-root
`firmware-candidates/v4.0.1h-repair-i-ui-ms/sd-root/`. Firmware binary is
unchanged (still `a26edd...`, marker `V4.0.1p`).

## 4. Validation (all re-run 2026-07-17)

- `analysis/final-audit-2026-07-17.py` (independent, re-derives expectations
  from the official backup): **AUDIT PASSED** — including the new checks:
  757 byte-differing entries, size 32888, offset table identical,
  full-Malay SHA-256, no entry longer than its official slot.
- `dm303_ui_overlay_candidate_check.py`: `ui_overlay_candidate_check=ok`,
  `non_overlay_system_resources=official_v4`.
- `dm303_preflash_check.py --profile v401h-repair-i-ui-ms`: `preflash_check=ok`
  (69 files).
- Repair-i package regression gates: `repair_candidate_check=ok`,
  `measurement_candidate_gate=ok`, `preflash_check=ok`.

## 5. Measurement symptoms — honest status

The user reports noise, unstable readings, AC->DC latency, zero/calibration
trouble, and input/output cleanliness issues persist. The repair-i patch set
(ammeter guard caps 15000→1500 ticks + acquisition window 240→64 samples) is
the only measurement change in V4.0.1o/V4.0.1p, and this field result means it
is **not sufficient** — the acquisition-window theory for the ~30 s AC->DC
blank is disproved on-device.

No further speculative measurement patches have been added: the repair-c/d/e
failures showed that stacking unverified patches makes failures un-isolatable.
The documented next direction (note.txt) is a deeper sampling/math audit plus
hardware-evidence-guided checks (rail/reference/relay/input current), and a
V3.16-vs-V4.0 comparison of the switching path, since V3.16 switches more
smoothly. Any resulting candidate will be a single-change HOLD build requiring
device confirmation — stability, accuracy and latency cannot be claimed from
static analysis alone.

## 6. Rollback

- Restore Spanish: flash official V4.0 (`backup/DM303 V4.0-read only/`) or the
  `DM303-V4.0.1-beta` (V4.0.1o) package, both carry the official `TEXT_SP.DAT`.
- The previous partial-Malay resource is retained at
  `localization/ms_MY/TEXT_SP.safe-slot-replacement.DAT`.
