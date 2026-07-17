# DM303 V4.0.1b Current Status

Status: HOLD for device testing. The current folder is structurally valid, but
no claim is made that stability, accuracy, latency, AC zero, oscilloscope noise,
Malay UI, or dark theme are solved until the device confirms it.

## Current Controlled Candidate

```text
folder: dm303_firmware/DM303-V4.0.1-beta/
source candidate: firmware-candidates/v4.0.1h-repair-i/
profile: v401h-repair-i
visible marker: V4.0.1o
firmware sha256: 11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953
files: 69
system: official V4.0 system resources + DM30XDB1.dat
```

## Experimental UI/Melayu Overlay

```text
folder: firmware-candidates/v4.0.1h-repair-i-ui-ms/
profile: v401h-repair-i-ui-ms
visible marker: V4.0.1p
firmware sha256: a26edd279ae15a68c3f819b1e2dac10d91043a45f6faac64aa0bdfa504f38878
status: HOLD, not promoted to final folder
```

This overlay reuses the SP language slot as `Melayu`, rebuilds `TEXT_SP.DAT`
from the official SP 773-entry layout, and uses direct RGB565 dark nav/menu
assets. Validation passed with:

```text
ui_overlay_candidate_check=ok
non_overlay_system_resources=official_v4
```

Do not test `V4.0.1p` before `V4.0.1o` unless the user explicitly wants to mix
UI and measurement variables again.

`V4.0.1h` / `stability-exp20-ms-safe` is quarantined. It carried the failed
resource/UI layer and stream/IO recovery bytes; field feedback reported higher
noise, unchanged ammeter AC -> DC latency, and text smear/calit.

## What Repair-I Changes

- Keeps bootloader/updater untouched.
- Keeps fault/default handlers official.
- Keeps runtime fail-stop loops official.
- Keeps stream/read helper, lower byte-IO, command retries, stream state clear,
  mode state wrapper, relay settle, boot-logo delay, and UI render windows
  official.
- Keeps all `system` resources official V4.0, then adds only `DM30XDB1.dat`.
- Removes the failed Malay/dark/logo/SP resource layer from the flash folder.
- Marks the firmware internally as `V4.0.1o`.
- Keeps Repair-H latency guards and adds one ammeter-local acquisition window
  change at `0x1d1da`: `0xf0` / 240 samples -> `0x40` / 64 samples.

The new `0x1d1da` patch is in the function mapped by UI text to ammeter
labels `AC`, `20A(Yellow)`, and `mA(Green)`. It targets the reported long
AC -> DC blank in current mode. It is not an ADC calibration or True RMS math
proof.

## Validation

```powershell
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_measurement_candidate_gate.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_repair_candidate_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
```

Latest validation result:

```text
preflash_check=ok
repair_candidate_check=ok
measurement_candidate_gate=ok
official_v4_system_resources=match
ui_render_stream_io_relay_boot_windows=official
```

## Important Test Notes

- Copy the contents of `dm303_firmware/DM303-V4.0.1-beta/` directly to the SD
  card root.
- Do not copy the folder itself into the SD card.
- If latency improves but noise worsens, the `0x1d1da` acquisition window is
  too small and should be retuned upward.
- If calit remains even with this package, the smear is not from the modified
  system resources because this package uses official V4.0 resources.

## Quarantined Lines

- `stability-exp20-ms-safe` / `V4.0.1h`: failed field result.
- `v401h-repair-c`: failed field result, higher noise.
- `v401h-repair-e`: superseded because stream/IO recovery remained suspect.
- `v401h-repair-f`: superseded by `repair-g`.
- `v401h-repair-g`: superseded by `repair-h`.
- `v401h-repair-h`: superseded by `repair-i` to target the ammeter sample
  acquisition wait directly.
- `v401h-repair-i-ui-ms`: UI/Melayu overlay staged but not promoted; use only
  after clean `repair-i` display behavior is known.
