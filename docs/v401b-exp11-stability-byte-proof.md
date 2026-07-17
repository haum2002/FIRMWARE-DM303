# DM303 V4.0.1b exp11 stability byte proof

Status: current flashable package is `stream-recovery-exp11`.

Final firmware:

```text
dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
SHA-256: d244ffd168dded8656a83e2cf62f663a2228d32803b4a7ee08a4b857b5b44526
Size: 203260 bytes
```

## What changed in firmware code

The exp11 build is not only a resource/UI rebuild. It contains runtime firmware
patches at fixed offsets in the V4.0 image.

| Offset | Address | Original bytes | Current bytes | Purpose |
|---:|---:|---|---|---|
| `0x09570` | `0x08019570` | `f5 d1` | `00 bf` | Stop repeated stream-read retry after lower helper timeout. |
| `0x09706` | `0x08019706` | `ec d1` | `4c d1` | Route command-0x40 busy failure to the existing error/clear block at `0x080197a2`. |
| `0x09758` | `0x08019758` | `f5 d1` | `00 bf` | Stop command-0xe9 retry when status clear fails. |
| `0x097be` | `0x080197be` | `f6 d1` | `00 bf` | Stop mode/status retry when command helper cannot recover. |
| `0x06a06` | `0x08016a06` | `70 b5 05 46` | `00 f0 23 b8` | Branch low byte-IO helper to bounded wrapper. |
| `0x06a50` | `0x08016a50` | setup function prefix | bounded wrapper prefix | Preserve SPI1 calls, wait up to `0x0fa0`, return `0xff` if ready flag never appears. |
| `0x0967c` | `0x0801967c` | `95 27` | `60 27` | Clamp command `0x40` retry count from `0x95` to `0x60`. |
| `0x09682` | `0x08019682` | `87 27` | `60 27` | Clamp command `0x48` retry count from `0x87` to `0x60`. |
| `0x09694` | `0x08019694` | `0a 27` | `0a 27` | Keep the small fallback retry count unchanged. |

## Why these offsets were chosen

The latest physical clue was that the numeric reading and the battery icon can
disappear together. That points to a shared runtime refresh path being blocked,
not only a missing value draw. Static disassembly found stream/status retry
loops above a lower byte-IO helper. If the lower helper has already timed out
but a busy/valid flag stays stuck after overload, spike, bad mode transition, or
digital-fuse/protection state, the higher loop can keep the UI/status path from
returning.

The exp11 patch keeps the original relay/range timing and mode helper, because
V3.16 and V4.0 both use the same observed `2/3/10` selector timing. Instead of
adding blind delay, exp11 changes the wait/retry behavior so the firmware
returns to the existing failure path faster. Compared with exp9, exp10 first
changes the command `0x40` busy-failure branch from simple fall-through to an
existing error/clear route, avoiding a false normal status update when the busy
flag is still set. Exp11 then makes low byte-IO timeout explicit by returning
`0xff` from a bounded wrapper instead of continuing with a stale byte read
after the ready flag fails to appear.

## What this does not claim

This is a recovery and latency patch. It does not claim that ADC averaging,
True RMS math, EMI filtering, calibration constants, injector waveform, or
hardware leakage are fully fixed. Those areas still need physical evidence and
a confirmed runtime hook before they can be patched safely.

## Verification commands

```powershell
python tools/dm303_validate_final_package.py --profile stream-recovery-exp11
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stream-recovery-exp11
python tools/dm303_latency_guard_probe.py
python tools/dm303_v316_v401_compare.py
```

Expected key results:

```text
dm303_final_validation=ok
preflash_check=ok
latency_guard_ok=True
firmware_sha256=d244ffd168dded8656a83e2cf62f663a2228d32803b4a7ee08a4b857b5b44526
```
