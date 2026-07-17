# DM303 V4.0.1b exp16 UI-safe byte proof

Status: current flashable package is `stream-recovery-exp16-ui-safe`.

```text
29a8bd71cba65538ba25d8e76aa5122234f9a28ad957287ba82fbf4fdf6c60af  dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
4b6b2fd9c6dee916390144815e7becc02549b7d6f1260b0551c8d939c3acf83e  dm303_firmware/DM303-V4.0.1-beta/system/TEXT_SP.DAT
96f2b294c7fad14a527eb96f1a8f09f7e0f33e2f02f7f43af305c9fa2df57394  dm303_firmware/DM303-V4.0.1-beta/system/icon-SP.dat
a847c346837164d25e882f0f10bb47815b43e9f381b130e2870447b20d6845a3  dm303_firmware/DM303-V4.0.1-beta/system/LOGO-1.bmp
```

## New exp16 facts

| Offset | Address | Bytes | Purpose |
|---:|---:|---|---|
| `0x02ca0` | `0x08012ca0` | `MT100MM V4.0.1d\0` | Visible flash marker for the main firmware identity. |
| `0x02cb0` | `0x08012cb0` | `BT100MM V4.0.1d\0` | Visible flash marker for the secondary firmware identity. |
| `0x25bf8` | `0x08035bf8` | `45 73 70 61 c3 b1 61 00` | Language name remains official `España`; no false Malay slot in this build. |
| `0x045b2` | `0x080145b2` | `01 f0 9c fc` | Boot-logo loader call is restored to the official call; no added delay wrapper. |
| `0x15812` | `0x08025812` | `05 d9` | Exp15 immediate-switch gate A removed. |
| `0x15838` | `0x08025838` | `34 d9` | Exp15 immediate-switch gate B removed. |
| `0x15862` | `0x08025862` | `06 d9` | Exp15 immediate-switch gate C removed. |
| `0x1588c` | `0x0802588c` | `05 d9` | Exp15 immediate-switch gate D removed. |
| `0x09818` | `0x08019818` | `08 b1` | Exp15 stale bit0 bypass A removed. |
| `0x098b4` | `0x080198b4` | `08 b1` | Exp15 stale bit0 bypass B removed. |
| `0x09950` | `0x08019950` | `18 b1` | Exp15 stale bit0 bypass C removed. |

## Still carried from exp14

- Stream transaction body forced past stale busy bit `1` at `0x080196be`.
- Long current/meter transition guards at `0x0802585e` and `0x08025888` capped from `0x3e80` to `0x0640`.
- Bounded low byte-IO wrapper at `0x08016a50`.
- Command retry clamp `0x95`/`0x87` to `0x60`.
- Command `0x40` busy failure routed to the existing error/clear path.
- Stream error cleanup clears bits `0` and `1` from `0x2000022c`.
- Mode/range entry wrapper at `0x0803d606` clears the same stale bits before relay/range switching.

## Validation

```powershell
python tools/dm303_validate_final_package.py --profile stream-recovery-exp16-ui-safe
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stream-recovery-exp16-ui-safe
python tools/dm303_exp16_ui_safe_safety_audit.py
python tools/dm303_latency_guard_probe.py
```

All commands above passed on this build.
