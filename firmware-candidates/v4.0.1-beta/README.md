# DM303 V4.0.1 Beta Staging

Final flash package:

```text
dm303_firmware/DM303-V4.0.1-beta/
```

Current profile: `stability-exp20-ms-safe`

Visible firmware marker: `V4.0.1h`

## Contents

- `DM303V4.0.1-beta.bin` - patched firmware candidate.
- `system/TEXT_MS.DAT` - full Malay resource built from English layout, staged
  only.
- `system/TEXT_SP.DAT` - safer Malay replacement built from the official SP
  773-entry layout.
- `system/icon-SP.dat` - Malay/dark SP graphical label pack.
- `system/LOGO-1.bmp` - beta boot logo in the official 16-bit BMP layout.
- `PATCH-REPORT.md` - byte-level firmware patch report.
- `FINAL-PACKAGE-REPORT.md` - merged final-folder report.

## Direct Firmware Changes

Exp20 keeps the exp18 bounded recovery set and fixes the malformed SP text
resource from exp19:

- version strings: `MT100MM V4.0.1h` / `BT100MM V4.0.1h`;
- fault/default reset-request recovery;
- runtime fail-stop loop fall-through;
- bounded stream/status recovery;
- bounded low byte-IO fail return;
- command retry clamp;
- stale stream/status cleanup;
- mode/range stale-state entry clear;
- stream busy-gate bypass;
- two AC-to-DC long-switch gate caps;
- Spanish language-name slot renamed to `Melayu`.

## Safety Status

The updater/SD upgrade procedure is not patched. The root firmware filename
remains `DM303V4.0.1-beta.bin`.

Run:

```powershell
python tools/dm303_validate_final_package.py --profile stability-exp20-ms-safe
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stability-exp20-ms-safe
```

This build does not claim that ADC/True RMS/noise/latency is fixed.
