# DM303 V4.0.1o Repair-I Package Report

Status: HOLD for controlled device test.

## Package

```text
candidate: firmware-candidates/v4.0.1h-repair-i/
sd-root: firmware-candidates/v4.0.1h-repair-i/sd-root/
promoted final folder: dm303_firmware/DM303-V4.0.1-beta/
profile: v401h-repair-i
visible marker: V4.0.1o
firmware sha256: 11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953
```

## Why This Exists

The `V4.0.1h` package was field-reported as worse: higher noise, ammeter
AC -> DC still slow, and text smear/calit remained. Audit showed that package
still carried the failed resource/UI layer and stream/IO recovery bytes.

Repair-I rebuilds from official V4.0, restores official system resources, adds
`DM30XDB1.dat`, and keeps only narrow latency patches.

## Measurement Patch Scope

- `0x14b0e`, `0x14b36`: lower another mode/range helper cluster's `0x3a98`
  guards to `0x05dc`.
- `0x15812`, `0x15838`, `0x15862`, `0x1588c`: remove elapsed-time skip branches
  immediately before mode/range calls.
- `0x1585e`, `0x15888`: cap long current/meter switch compares from `0x3e80`
  to `0x0640`.
- `0x15934`, `0x1595c`: lower current/meter state-2 guards from `0x3a98` to
  `0x05dc`.
- `0x1d1a4`, `0x1d1c0`: lower ammeter-local `0x3a98` guards to `0x05dc`.
- `0x1d1da`: reduce ammeter-local acquisition window from `0xf0` / 240 samples
  to `0x40` / 64 samples.

The `0x0802d194` function is mapped by UI text and helper calls to the ammeter
screen: it draws `AC`, `20A(Yellow)`, `mA(Green)`, calls relay/range selector
`0x0801f0f2`, and calls mode/range routine `0x0801f19a`.

## Kept Official

- bootloader/updater path;
- fault/default handlers;
- runtime fail-stop loops;
- lower byte-IO hardware-ready helper;
- stream/read helper;
- command retry counters;
- stream state clear;
- mode state wrapper;
- stream busy gate;
- relay settle timing;
- UI render guard;
- boot-logo timing;
- all official V4.0 system resources.

## Validation

```text
preflash_check=ok
repair_candidate_check=ok
measurement_candidate_gate=ok
official_v4_system_resources=match
ui_render_stream_io_relay_boot_windows=official
```

## Test Interpretation

- If AC -> DC ammeter latency improves but noise worsens, `0x1d1da` should be
  retuned upward, for example to `0x80`.
- If latency does not change, the wait is not controlled by the ammeter sample
  acquisition window and the next analysis should move deeper into the
  acquisition/status helper path.
- If text smear remains with this package, it is not caused by the modified UI
  resources because this package uses official V4.0 resources.

No claim is made that ADC accuracy, AC zero, oscilloscope noise, EMI filtering,
or True RMS math has been fixed.
