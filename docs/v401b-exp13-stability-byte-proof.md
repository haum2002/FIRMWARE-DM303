# DM303 V4.0.1b exp13 stability byte proof

Status: current flashable package is `stream-recovery-exp13`.

Final firmware:

```text
fbe05118e33743fb56679d5edd1eb2019c1d82e39f499c1459fe89401ce8130b  dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
```

## New exp13 bytes

| Offset | Address | Bytes | Purpose |
|---:|---:|---|---|
| `0x0f19a` | `0x0801f19a` | `1e f0 34 ba` | Branch mode/range entry to the exp13 wrapper before relay/range switching. |
| `0x2d606` | `0x0803d606` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | Preserve original prologue, clear bits `0` and `1` of `0x2000022c`, then continue at `0x0801f19f`. |

## Kept from exp12

| Offset | Address | Bytes | Purpose |
|---:|---:|---|---|
| `0x06a06` | `0x08016a06` | `00 f0 23 b8` | Route low byte-IO helper to bounded wrapper. |
| `0x06a50` | `0x08016a50` | wrapper prefix `70 b5 05 46 40 f6 a0 76` | Return `0xff` if ready flag never appears inside the `0x0fa0` wait budget. |
| `0x09570` | `0x08019570` | `00 bf` | Stop repeated stream-read retry after lower timeout. |
| `0x09706` | `0x08019706` | `4c d1` | Route command `0x40` busy failure to existing error/clear path. |
| `0x09758` | `0x08019758` | `00 bf` | Stop command/status retry loop after helper failure. |
| `0x097be` | `0x080197be` | `00 bf` | Stop mode/status retry loop after helper failure. |
| `0x097e6` | `0x080197e6` | `20 f0 03 00` | Existing error cleanup clears stale status bits `0` and `1`. |

## Validation

```powershell
python tools/dm303_validate_final_package.py --profile stream-recovery-exp13
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stream-recovery-exp13
python tools/dm303_exp13_safety_audit.py
python tools/dm303_latency_guard_probe.py
```

This proves the exp13 firmware is changed at the intended guarded locations. It
does not claim analog accuracy is solved until the device is tested physically.
