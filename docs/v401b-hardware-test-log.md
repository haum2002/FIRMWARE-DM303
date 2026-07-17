# DM303 V4.0.1b hardware test log

Use this file as the repeatable bench log for `stream-recovery-exp14`.

## Firmware identity

- Test date:
- Device model shown:
- Firmware shown:
- Firmware file hash:
- Package validator result:
- Internal battery bars before test:
- Internal battery measured by external DMM:
- Notes about SD card copy:

## Required pre-flash checks

```powershell
python tools/dm303_validate_final_package.py
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta
python tools/dm303_exp14_safety_audit.py
python tools/dm303_latency_guard_probe.py
```

After copying to the SD card root, run the same pre-flash check against the SD
drive letter, for example:

```powershell
python tools/dm303_preflash_check.py --root E:\ --allow-sd-extras
```

## Cranking / ghost voltage

| Test | Expected | Observed | Pass/Fail | Notes |
|---|---|---|---|---|
| Cranking input open | may float; do not treat as real battery voltage | | | |
| Cranking input shorted to correct negative clamp | close to `0 V` | | | |
| Cranking input on known `5.00 V` limited source | tracks source through expected scale | | | |
| Cranking input on known `12.00 V` limited source | tracks source through expected scale | | | |
| Internal cell during cranking screen | no heavy sag | | | |

If a shorted cranking input still reads around `2.88 V`, treat the fault as
likely hardware leakage/protection/mux/front-end until proven otherwise.

## Meter switching stability

| Mode | Test | Cycles | Expected | Observed | Pass/Fail |
|---|---|---:|---|---|---|
| Voltmeter | DC -> AC -> DC, probes shorted | 50 | no blank longer than 2 s | | |
| Ammeter green `A/mA/uA` | DC -> AC -> DC with safe dummy load | 50 | no blank longer than 2 s; AC -> DC must be far below old 30 s failure | | |
| Ohmmeter | enter mode with probes open | 20 | no self-beep, no blank | | |
| Continuity | open probes | 60 s | no false beep | | |

Record whether the battery icon disappears when numbers disappear. If both
vanish together, it still points to a shared status/display refresh stall.

## Noise and accuracy

Record numeric data in `docs/v401b-bench-measurements.csv`, then run:

```powershell
python tools/dm303_bench_analyzer.py --input docs\v401b-bench-measurements.csv
```

For oscilloscope noise, fill `noise_high` and `noise_low` directly. Example:
if the trace moves between `+0.07 V` and `-0.03 V`, enter `0.07` and `-0.03`;
the analyzer will calculate `0.10 V` peak-to-peak. For freeze/blank symptoms,
enter the total number of events in `blank_events` and the worst recovery time
in `latency_ms`.

| Function | Setup | Expected / baseline | Observed | Notes |
|---|---|---|---|---|
| Voltmeter DC zero | probes shorted, zeroing | stable near zero | | |
| Voltmeter AC zero | probes shorted, zeroing | stable near zero | | |
| Ammeter DC zero | safe input short/dummy load | stable near zero | | |
| Ammeter AC zero | safe input short/dummy load | stable near zero | | |
| Oscilloscope | input shorted, `0.1 V/div`, `12.5 us` | compare to V3.16 baseline | | |
| Oscilloscope | input open, same setting | should be noisier than short | | |

## Output functions safety

Do not test injector, relay, ignition, generator, or adjustable signal output on
a real vehicle/load until a dummy load and external oscilloscope confirm the
waveform.

| Output | Dummy load used | Scope result | Pass/Fail | Notes |
|---|---|---|---|---|
| Injector | | | | |
| Relay | | | | |
| Ignition | | | | |
| Generator/frequency | | | | |
| Adjustable voltage signal | | | | |

## Result summary

- Flash accepted:
- UI/logo/icon quality:
- Malay language option visible:
- Freeze improved:
- Cranking ghost voltage conclusion:
- Hardware repair suspected:
- Next firmware action:
