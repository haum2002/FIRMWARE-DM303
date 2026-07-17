# DM303 V4.0.1b exp15 stability byte proof

Status: current flashable package is `stream-recovery-exp15`.

```text
3a2db571a4c783d0df2a454ec13d8d38a3a22a0e6ad7cc9993a0afa1edd7f3a0  dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
3ff19be55a946a99613c46e5501b586fa8202d43a02a1af0f2d5f22f179c8e8d  dm303_firmware/DM303-V4.0.1-beta/system/icon-SP.dat
a847c346837164d25e882f0f10bb47815b43e9f381b130e2870447b20d6845a3  dm303_firmware/DM303-V4.0.1-beta/system/LOGO-1.bmp
```

## New exp15 bytes

| Offset | Address | Bytes | Purpose |
|---:|---:|---|---|
| `0x02ca0` | `0x08012ca0` | `MT100MM V4.0.1c\0` | Visible flash marker for the main firmware identity. |
| `0x02cb0` | `0x08012cb0` | `BT100MM V4.0.1c\0` | Visible flash marker for the secondary firmware identity. |
| `0x15812` | `0x08025812` | `00 bf` | Remove the first elapsed-time skip branch before a mode/range call. |
| `0x15838` | `0x08025838` | `00 bf` | Remove the second elapsed-time skip branch before a mode/range call. |
| `0x15862` | `0x08025862` | `00 bf` | Remove the first return-to-mode elapsed-time skip branch after AC/DC switch condition. |
| `0x1588c` | `0x0802588c` | `00 bf` | Remove the second return-to-mode elapsed-time skip branch after AC/DC switch condition. |
| `0x09818` | `0x08019818` | `01 e0` | Bypass stale bit0 early error in the first stream transfer helper and continue normal helper body. |
| `0x098b4` | `0x080198b4` | `01 e0` | Bypass stale bit0 early error in the second stream transfer helper and continue normal helper body. |
| `0x09950` | `0x08019950` | `03 e0` | Bypass stale bit0 early error in the parsed stream transfer helper and continue normal helper body. |

## Carried from exp14

- Stream transaction body forced past stale busy bit `1` at `0x080196be`.
- Long current/meter transition guards at `0x0802585e` and `0x08025888` capped from `0x3e80` to `0x0640`.
- Bounded low byte-IO wrapper at `0x08016a50`.
- Command retry clamp `0x95`/`0x87` to `0x60`.
- Command `0x40` busy failure routed to the existing error/clear path.
- Stream error cleanup clears bits `0` and `1` from `0x2000022c`.
- Mode/range entry wrapper at `0x0803d606` clears the same stale bits before relay/range switching.
- Boot-logo load wrapper waits 200 ticks after `LOGO-1.bmp` load.

## Validation

```powershell
python tools/dm303_validate_final_package.py --profile stream-recovery-exp15
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stream-recovery-exp15
python tools/dm303_exp15_safety_audit.py
python tools/dm303_latency_guard_probe.py
```

All commands above passed on this build.

## What this proves

This proves the firmware image really changed at the intended guarded byte
locations and that the final package validator recognizes those changes. It
does not prove analog accuracy, zero physical noise, or that the hidden
measurement MCU/peripheral path has accepted the new behavior. If the device
shows `V4.0.1c` and the AC -> DC ammeter delay remains unchanged, the next
investigation must move beyond these stream/mode gates.
