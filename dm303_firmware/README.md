# DM303 Firmware Package Folder

## Status: HOLD for controlled device test

Current package:

```text
dm303_firmware/DM303-V4.0.1-beta/
```

Profile: `v401h-repair-i`

Visible firmware marker: `V4.0.1o`

Firmware hash:

```text
11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953  DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
```

## Package Facts

- Rebuilt from `firmware-candidates/v4.0.1h-repair-i/sd-root`.
- Uses official V4.0 `system` resources, plus restored `DM30XDB1.dat`.
- Removes the failed `V4.0.1h` Malay/dark/logo/SP resource layer.
- Keeps updater/bootloader, stream/IO, relay settle, UI render, and boot-logo
  timing windows official.
- Adds a targeted ammeter latency patch: the `AC / 20A / mA` function's sample
  acquisition window is reduced from 240 to 64 samples.

## Validation

```powershell
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_measurement_candidate_gate.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_repair_candidate_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
```

For SD card, replace `E:\` with the actual drive:

```powershell
python tools/dm303_preflash_check.py --root E:\ --profile v401h-repair-i --allow-sd-extras
```

Copy the contents of `DM303-V4.0.1-beta`, not the folder itself, to the SD card
root.

## Not Yet Claimed

This is not a confirmed stability, accuracy, latency, EMI, True RMS, Malay UI,
or dark-theme fix until the device confirms it. If noise gets worse, retune the
sample window upward before adding any broader math/filter patch.

## Second Package: DM303-V4.0.1p-ms-beta (HOLD)

Combined Malay + dark-theme package built on the full repair-i measurement
baseline:

```text
dm303_firmware/DM303-V4.0.1p-ms-beta/
```

Profile: `v401h-repair-i-ui-ms`, visible marker `V4.0.1p`.

Firmware hash:

```text
a26edd279ae15a68c3f819b1e2dac10d91043a45f6faac64aa0bdfa504f38878  DM303-V4.0.1p-ms-beta/DM303V4.0.1-beta.bin
```

- Byte-identical copy of `firmware-candidates/v4.0.1h-repair-i-ui-ms/sd-root`.
- Firmware differs from repair-i in exactly 8 bytes: version marker
  (`0x02cae`, `0x02cbe`) and the `Español` -> `Melayu` menu name
  (`0x25bf8`-`0x25bfe`). Every repair-i measurement patch byte is unchanged.
- `TEXT_SP.DAT` rebuilt on the official SP 773-entry layout with **full Malay
  coverage: 757 translated entries** (16 unchanged blanks/symbols), every
  entry exactly its official byte length so the offset table is byte-identical
  to vendor. Corrects the 2026-07-16 partial build (137 entries, some
  misaligned — see `docs/v401p-full-malay-text-rebuild-2026-07-17.md`).
  `TEXT_SP.DAT` SHA-256:
  `f955f4c83a57ac26150536a377f29b40c5d64fc5ceb2991e2c5fb7ef6c147fd9`.
- Dark nav/menu assets are direct RGB565 tints with official BMP
  headers/sizes (palette: background `#0A233B`, text `#EFF7FA`, amber
  `#FFCC48`). All other system resources are official V4.0.
- Spanish is sacrificed (no spare language slot exists); it is restorable by
  flashing official V4.0 or the `V4.0.1o` package.

Validation:

```powershell
python tools/dm303_ui_overlay_candidate_check.py --root dm303_firmware\DM303-V4.0.1p-ms-beta
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1p-ms-beta --profile v401h-repair-i-ui-ms
```

Status: HOLD, not device-tested. Recommended flash order: prove `V4.0.1o`
first; only if calit/noise are gone, test `V4.0.1p` for the Malay/dark UI.

## Third Package: DM303-V4.0.1q-beta (HOLD)

Single-change AC/DC switch-window candidate from the three-way vendor
comparison (`docs/v313-v316-v40-switching-comparison-2026-07-17.md`):

```text
dm303_firmware/DM303-V4.0.1q-beta/
```

Profile: `v401h-repair-j`, visible marker `V4.0.1q`.

Firmware hash:

```text
ecd7b5dc85158467ce9e2ffc8b71fd1523c934383c7d1e6677b7bd0f79e34642  DM303-V4.0.1q-beta/DM303V4.0.1-beta.bin
```

- Official V4.0 + exactly 8 patched bytes: the ammeter AC<->DC switch-state
  acquisition windows at `0x1df0c` (600 -> 240) and `0x1df40` (360 -> 240),
  using the vendor's own 240-sample normal-update constant
  (`movw r0,#0xf0`, flag-safe).
- V3.13/V3.16 share V4.0's guard structure and switch smoothly, so the
  repair-i guard caps are deliberately absent; everything else is official.
- Expected effect if the analysis holds: post-switch blank ~30 s -> ~12 s.
  Not proven on-device yet.

Validation:

```powershell
python tools/dm303_repair_candidate_check.py --root dm303_firmware\DM303-V4.0.1q-beta --profile v401h-repair-j
python tools/dm303_measurement_candidate_gate.py --root dm303_firmware\DM303-V4.0.1q-beta --profile v401h-repair-j
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1q-beta --profile v401h-repair-j
```

## Fourth Package: DM303-V4.0.1r-beta (HOLD)

Combined package: repair-j measurement baseline + full Melayu/dark UI overlay:

```text
dm303_firmware/DM303-V4.0.1r-beta/
```

Profile: `v401h-repair-j-ui-ms`, visible marker `V4.0.1r`.

Firmware hash:

```text
e75f8cbd8657c9a72f84ce454d5fc43298aead48c4053df00946eae3f99faf8c  DM303-V4.0.1r-beta/DM303V4.0.1-beta.bin
```

- Byte-identical copy of `firmware-candidates/v4.0.1h-repair-j-ui-ms/sd-root`.
- Firmware differs from repair-j (V4.0.1q) in exactly 8 bytes: version marker
  (`0x02cae`, `0x02cbe`) and the `Español` -> `Melayu` menu name
  (`0x25bf8`-`0x25bfe`). Every repair-j measurement byte is unchanged: the
  only measurement change vs official remains the two AC/DC switch-state
  acquisition windows 600/360 -> 240 at `0x1df0c`/`0x1df40`.
- Same overlay resources as V4.0.1p: full-Malay `TEXT_SP.DAT` (757/773
  entries, official size/offset table) SHA-256
  `f955f4c83a57ac26150536a377f29b40c5d64fc5ceb2991e2c5fb7ef6c147fd9`, dark
  `icon-SP.dat` SHA-256
  `4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8`, and the
  34 dark RGB565 BMPs (palette unchanged). All other system resources are
  official V4.0 plus `DM30XDB1.dat`.
- Spanish is sacrificed (no spare language slot exists); it is restorable by
  flashing official V4.0 or the `V4.0.1q` package.
- Full write-up: `docs/v401r-combined-package-2026-07-18.md`.

Validation:

```powershell
python tools/dm303_ui_overlay_candidate_check.py --root dm303_firmware\DM303-V4.0.1r-beta --profile v401h-repair-j-ui-ms
python tools/dm303_measurement_candidate_gate.py --root dm303_firmware\DM303-V4.0.1r-beta --profile v401h-repair-j-ui-ms --firmware-only
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1r-beta --profile v401h-repair-j-ui-ms
```

Status: HOLD, not device-tested. Recommended flash order: prove `V4.0.1q`
first; only if the switch-window change shortens the blank on-device, use
`V4.0.1r` for the same measurement with the Malay/dark UI.
