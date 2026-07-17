# DM303 V4.0.1b exp12 stability byte proof

Status: current flashable package is `stream-recovery-exp12`.

Final firmware:

```text
dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
SHA-256: 0a2090bf5c42cd89509f65881d8b54862d243c6b9d224478ab95bb3ef8e06a16
Size: 203260 bytes
```

## Firmware byte changes that matter for blank/freeze

| Offset | Address | Current bytes | Purpose |
|---:|---:|---|---|
| `0x09570` | `0x08019570` | `00 bf` | Stop repeated stream-read retry after lower helper timeout. |
| `0x09706` | `0x08019706` | `4c d1` | Route command `0x40` busy failure into the existing error/clear block. |
| `0x09758` | `0x08019758` | `00 bf` | Stop command/status retry when the lower helper cannot clear the path. |
| `0x097be` | `0x080197be` | `00 bf` | Stop mode/status retry from spinning on the same failed state. |
| `0x06a06` | `0x08016a06` | `00 f0 23 b8` | Route low byte-IO helper through bounded wrapper. |
| `0x06a50` | `0x08016a50` | `70 b5 05 46 40 f6 a0 76` | Wrapper prefix; waits up to `0x0fa0`, returns `0xff` on ready-timeout. |
| `0x0967c` | `0x0801967c` | `60 27` | Clamp command `0x40` retry count to `0x60`. |
| `0x09682` | `0x08019682` | `60 27` | Clamp command `0x48` retry count to `0x60`. |
| `0x09694` | `0x08019694` | `0a 27` | Keep fallback retry count unchanged. |
| `0x097e6` | `0x080197e6` | `20 f0 03 00` | Existing stream error cleanup now clears flag bits `0` and `1` from `0x2000022c`. |

## Why exp12 was added

Field evidence showed the number and battery icon can disappear together after
spike, overload, or DC/AC switching. Static tracing shows `0x2000022c` is a
shared stream/status flag byte; bit `1` can cause an early stale-status return,
while the original error cleanup only cleared bit `0`.

Exp12 changes only the existing nonzero-result cleanup instruction from
`bic r0, r0, #1` to `bic r0, r0, #3`. It clears stale error/busy bits `0` and
`1`, while leaving the other observed protection/status bits untouched.

## What this does not claim

This is a stream/status recovery patch. It does not claim ADC averaging, True
RMS math, EMI filtering, injector waveform quality, or analog leakage is fully
fixed. Those still need hardware test data and a confirmed measurement-engine
hook before safe patching.

## Verification

```powershell
python tools/dm303_validate_final_package.py --profile stream-recovery-exp12
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stream-recovery-exp12
python tools/dm303_latency_guard_probe.py
python tools/dm303_stream_state_audit.py
```
