# DM303 V4.0.1b exp14 stability byte proof

Status: current flashable package is `stream-recovery-exp14`.

```text
57204ff3219fe2bbb06df116ce6ffd87593605c66b1e0fd40b803f61d08dcab9  dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
3ff19be55a946a99613c46e5501b586fa8202d43a02a1af0f2d5f22f179c8e8d  dm303_firmware/DM303-V4.0.1-beta/system/icon-SP.dat
a847c346837164d25e882f0f10bb47815b43e9f381b130e2870447b20d6845a3  dm303_firmware/DM303-V4.0.1-beta/system/LOGO-1.bmp
```

## New exp14 bytes

| Offset | Address | Bytes | Purpose |
|---:|---:|---|---|
| `0x096be` | `0x080196be` | `02 e0` | Force the stream transaction body instead of returning early when stale busy bit `1` is set in `0x2000022c`. |
| `0x1585e` | `0x0802585e` | `b0 f5 c8 6f` | Cap the first long meter/current switch gate from `0x3e80` to `0x0640`. |
| `0x15888` | `0x08025888` | `b0 f5 c8 6f` | Cap the second long meter/current switch gate from `0x3e80` to `0x0640`. |

## Carried from exp13

- Bounded low byte-IO wrapper at `0x08016a50`.
- Command retry clamp `0x95`/`0x87` to `0x60`.
- Command `0x40` busy failure routed to the existing error/clear path.
- Stream error cleanup clears bits `0` and `1` from `0x2000022c`.
- Mode/range entry wrapper at `0x0803d606` clears the same stale bits before relay/range switching.
- Boot-logo load wrapper waits 200 ticks after `LOGO-1.bmp` load.

## Validation

```powershell
python tools/dm303_validate_final_package.py --profile stream-recovery-exp14
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stream-recovery-exp14
python tools/dm303_exp14_safety_audit.py
python tools/dm303_latency_guard_probe.py
python tools/dm303_v4_static_analysis.py --image dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin --no-walk
```

All commands above passed on this build.

## What this proves

This proves the firmware image really changed at the intended guarded byte
locations and that the final package validator recognizes those changes.
It does not prove analog accuracy or zero physical noise. The next required
device-side test is ammeter green `A/mA/uA` AC -> DC latency, blank/freeze
recovery after spike/overload, and UI logo/icon visual inspection.
