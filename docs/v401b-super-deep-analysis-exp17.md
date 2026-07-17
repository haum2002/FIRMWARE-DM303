# DM303 V4.0.1b super deep analysis and clean fix

Date: 2026-07-14

Current build: `clean-resource-exp17`

## Hard field evidence

- `V4.0.1c` was visible on the device after exp15. This proves the modified
  firmware image really booted.
- Exp15 still gave no performance improvement, and the user reported possible
  UI/loading regression.
- `V4.0.1d` was visible after exp16. Exp16 removed the most aggressive exp15
  gates and restored official SP text/icon resources, but the user still
  reported no meaningful improvement.

Conclusion: the previous stream/mode byte patches were not on the real path
causing the observed ammeter AC -> DC delay, blank/freeze, noise, or zeroing
instability.

## Why the earlier patches are no longer trusted

The previous builds touched these areas:

- high-level stream/status retry branches,
- low byte-IO helper timeout wrapper,
- command retry counts,
- stale status bit cleanup,
- mode/range entry stale-state clear,
- stale-busy transaction gate,
- current-switch long gate cap,
- exp15 immediate mode/range gates,
- exp15 stale bit0 helper bypass.

Because the device showed the exp15 version marker and still behaved the same,
the evidence now says these patched locations are either:

- not the active path for the physical meter symptom,
- not sufficient because another controller/peripheral owns acquisition,
- or only involved in UI/resource loading rather than analog conversion.

Keeping those patches would add risk without evidence. Exp17 removes the
ineffective stream/mode latency patches and returns measurement/control flow to
official V4.0 behavior.

## The major new finding: missing `DM30XDB1.dat`

Every inspected firmware image references:

```text
\system\DM30XDB1.dat
```

The string appears in:

- V3.13 firmware,
- V3.16 firmware,
- V4.0 firmware,
- current V4.0.1 beta firmware.

Resource-loader audit result before exp17:

```text
backup/DM303 V4.0-read only:
Resource paths referenced: 64
All referenced resources present: False
Missing: \system\DM30XDB1.dat
```

Resource-loader audit result after exp17:

```text
dm303_firmware/DM303-V4.0.1-beta:
Resource paths referenced: 64
All referenced resources present: True
```

The restored file is:

```text
system/DM30XDB1.dat
size: 1179648
sha256: 846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79
```

This file starts with a `BM` header and contains RGB565 92x92-style image
frames, so it is treated as a resource database, not executable firmware.

## What exp17 changes

Firmware binary:

- version marker: `MT100MM V4.0.1e` / `BT100MM V4.0.1e`,
- fault/default self-loop vectors redirect to SYSRESETREQ recovery,
- three runtime fail-stop loops return/fall through instead of hanging forever,
- measurement/control stream and mode/range byte patches are removed.

System resources:

- `system/DM30XDB1.dat` is restored,
- `TEXT_SP.DAT` is official V4.0,
- `icon-SP.dat` is official V4.0,
- language name table remains official,
- boot-logo loader call is official,
- main menu BMP icons remain direct RGB565 dark-blue resources,
- `TEXT_MS.DAT` remains staged but is not forced into the SP slot.

## What exp17 intentionally does not claim

Exp17 does not claim:

- analog ADC filtering is fixed,
- True RMS math is improved,
- oscilloscope noise is physically removed,
- ammeter AC -> DC latency is solved,
- overload/spike recovery is solved.

Those claims require either a confirmed measurement-engine hook or hardware
test proof. The static firmware image still does not expose a safe ADC/True RMS
math contract. Blindly writing filter code to guessed offsets previously caused
corruption in the unsafe V4.0.2 work, so exp17 avoids that failure mode.

## Why this is still a valid upgrade step

Exp17 is a clean baseline repair:

- it removes byte patches now proven ineffective,
- it keeps only low-risk crash recovery,
- it restores a firmware-referenced resource that was absent from the V4.0
  support folder,
- it makes all referenced boot resources present,
- it creates a cleaner test baseline for the next physical result.

If exp17 changes the loading/progress animation or text rendering, the missing
resource was part of the UI/resource problem.

If exp17 still gives the same meter latency/noise, the next step must not be
more blind patching. It must be one of:

- protocol tracing between UI MCU and measurement engine,
- hardware inspection of analog/reference/fuse/current path,
- known-source calibration data collection,
- identifying a real measurement buffer/RMS accumulator before patching math.

## Test gate for exp17

After flashing, the device must show:

```text
V4.0.1e
```

Then test in this order:

1. Boot/loading progress: check whether the `Loading...... 00%` animation bar
   returns.
2. Text smear: check menu text and mode text before changing measurement modes.
3. Ammeter green `A/mA/uA`: DC -> AC -> DC, record AC -> DC delay.
4. Voltmeter zero: DC/AC shorted probes, record zero drift.
5. Oscilloscope: input shorted and open at `0.1 V/div`, `12.5 us`.
6. Record whether battery icon disappears together with numeric readings.
