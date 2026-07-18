# DM303 V4.0.1r Repair-J UI/Melayu Overlay Report

Status: HOLD — experimental combined package. Not proven on-device. Do not
flash before explicit owner approval; bench/recovery validation is still
required.

## Package

```text
candidate: firmware-candidates/v4.0.1h-repair-j-ui-ms/
sd-root: firmware-candidates/v4.0.1h-repair-j-ui-ms/sd-root/
promoted: dm303_firmware/DM303-V4.0.1r-beta/
profile: v401h-repair-j-ui-ms
visible marker: V4.0.1r
firmware sha256: e75f8cbd8657c9a72f84ce454d5fc43298aead48c4053df00946eae3f99faf8c
```

## What Is Added Over Repair-J (V4.0.1q)

- Spanish language-name slot is renamed in-place to `Melayu`
  (`0x25bf8`-`0x25bfe`, byte length preserved).
- `TEXT_SP.DAT` is the full-Malay SP-slot rebuild (757/773 entries translated,
  official 32888-byte size and offset table byte-identical), sha256
  `f955f4c83a57ac26150536a377f29b40c5d64fc5ceb2991e2c5fb7ef6c147fd9`.
- Dark nav/menu icon assets (34 RGB565 BMPs, palette unchanged: background
  `#0A233B`, text `#EFF7FA`, amber `#FFCC48`) plus dark `icon-SP.dat` sha256
  `4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8`.

## What Stays Vendor/Official

- All repair-j measurement bytes are untouched: this package carries exactly
  the repair-j single change (AC/DC switch-state acquisition windows 600/360
  lowered to the vendor's own 240 at `0x1df0c`/`0x1df40`) and nothing else.
- Firmware updater/bootloader path.
- Font resources: `ASCII64.dat`, `ASCII96.dat`, `HZK-ALL.GBK`.
- Logo resources.
- All non-overlay official V4.0 system resources.
- Stream/IO, relay settle, UI render, and boot-logo timing windows.
- Fail-stop vectors at `0x09ca0`/`0x0c6c8`/`0x2c4ea` (byte-identical to
  official).

## Firmware Diff vs Official V4.0 (complete)

```text
0x02cac-0x02cae  version marker MT100MM V4.0.1r
0x02cbc-0x02cbe  version marker BT100MM V4.0.1r
0x1df0c-0x1df0f  mov.w r0,#0x258 -> movw r0,#0xf0 (AC->DC window 600 -> 240)
0x1df40-0x1df43  mov.w r0,#0x168 -> movw r0,#0xf0 (DC->AC window 360 -> 240)
0x25bf8-0x25bfa  language slot name "Espan~a" -> "Melayu " (part 1)
0x25bfc-0x25bfe  language slot name "Espan~a" -> "Melayu " (part 2)
```

Note: the name patch spans `0x25bf8`-`0x25bfe` but byte `0x25bfb` is `0x61`
('a') in both the official "España" and "Melayu ", so the raw diff splits
into two ranges. Total differing bytes: 20.

## Validation

```text
ui_overlay_candidate_check=ok        (sd-root + promoted folder)
measurement_candidate_gate=ok        (--firmware-only; exact 6-range diff,
                                      all MUST_MATCH_OFFICIAL windows official)
preflash_check=ok                    (sd-root + promoted folder)
final-audit-2026-07-18.py            AUDIT PASSED (independent, no project
                                      checkers imported; covers o/p/q/r)
```

## Important Limit

This is still not true add-only language activation. The hardcoded language
table has no confirmed spare slot, so the SP slot is reused and Spanish is
sacrificed in this overlay. The repair-j measurement change itself is also
unproven on-device: expected effect if the analysis holds is post-switch
blank ~30 s -> ~12 s (not V3.x-instant). See
`docs/v401r-combined-package-2026-07-18.md` and
`docs/v313-v316-v40-switching-comparison-2026-07-17.md`.
