# DM303 V4.0.1b stream state audit

Image: `dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin`
SHA-256: `b9f54dbc46b25a8f9da7af85bc12c8eb591d7806372f10487b1aa717150ac45f`
Status-path range: `0x080196b2`-`0x080197f4`
Patch bytes OK: `True`

## Patch Byte Guard

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x09570` | `0x08019570` | `00 bf` | `00 bf` | `True` | stream read retry |
| `0x09706` | `0x08019706` | `4c d1` | `4c d1` | `True` | command-0x40 busy failure route |
| `0x09758` | `0x08019758` | `00 bf` | `00 bf` | `True` | command-0xe9 retry |
| `0x097be` | `0x080197be` | `00 bf` | `00 bf` | `True` | mode/status retry |
| `0x06a06` | `0x08016a06` | `00 f0 23 b8` | `00 f0 23 b8` | `True` | low byte-IO branch to bounded wrapper |
| `0x06a50` | `0x08016a50` | `70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0` | `70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0` | `True` | bounded low byte-IO wrapper prefix |
| `0x0967c` | `0x0801967c` | `60 27` | `60 27` | `True` | command-0x40 retry count |
| `0x09682` | `0x08019682` | `60 27` | `60 27` | `True` | command-0x48 retry count |
| `0x09694` | `0x08019694` | `0a 27` | `0a 27` | `True` | fallback retry count |
| `0x097e6` | `0x080197e6` | `20 f0 03 00` | `20 f0 03 00` | `True` | stream error cleanup clears status bits 0 and 1 |
| `0x0f19a` | `0x0801f19a` | `1e f0 34 ba` | `1e f0 34 ba` | `True` | mode/range entry branch to stale state clear wrapper |
| `0x2d606` | `0x0803d606` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `True` | mode/range wrapper clears status bits 0 and 1 |

## State Literals In Status Path

| Instruction address | Instruction | Literal address | Literal value | Role |
|---:|---|---:|---:|---|
| `0x080196b6` | `ldr r0, [pc, #0x1b4]` | `0x0801986c` | `0x2000022c` | shared status byte; bit 1 causes early return, bit 0 is cleared on nonzero result |
| `0x080196c0` | `ldr r0, [pc, #0x1a8]` | `0x0801986c` | `0x2000022c` | shared status byte; bit 1 causes early return, bit 0 is cleared on nonzero result |
| `0x080196d2` | `ldr r0, [pc, #0x190]` | `0x08019864` | `0x40011400` | GPIOD control path used during stream/status setup/cleanup |
| `0x080196dc` | `ldr r1, [pc, #0x188]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x08019700` | `ldr r0, [pc, #0x164]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x0801970c` | `ldr r1, [pc, #0x158]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x08019746` | `ldr r0, [pc, #0x120]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x0801975a` | `ldr r0, [pc, #0x10c]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x080197ae` | `ldr r0, [pc, #0xb8]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x080197c0` | `ldr r0, [pc, #0xa4]` | `0x08019868` | `0x20000130` | shared busy/retry countdown word used by command/status recovery |
| `0x080197d4` | `ldr r0, [pc, #0x98]` | `0x08019870` | `0x2000022d` | status/result byte written from r6 at status-path exit |
| `0x080197e2` | `ldr r0, [pc, #0x88]` | `0x0801986c` | `0x2000022c` | shared status byte; bit 1 causes early return, bit 0 is cleared on nonzero result |
| `0x080197ea` | `ldr r1, [pc, #0x80]` | `0x0801986c` | `0x2000022c` | shared status byte; bit 1 causes early return, bit 0 is cleared on nonzero result |
| `0x080197ee` | `ldr r0, [pc, #0x7c]` | `0x0801986c` | `0x2000022c` | shared status byte; bit 1 causes early return, bit 0 is cleared on nonzero result |

## Exp13 Recovery Interpretation

- `0x08019706` is now `bne 0x080197a2`, not a NOP.
- This branch is only taken after command `0x40` fails and the shared
  busy/retry word at `0x20000130` is still nonzero.
- The target block at `0x080197a2` is existing firmware code: it sets
  `r6=2`, selects command `0xe9`, then reaches the normal cleanup and
  status write at `0x080197d4`.
- `0x080197be` remains NOPed, so the existing error/clear path cannot
  spin forever on the same busy flag.
- `0x080197e6` now clears bits `0` and `1` from `0x2000022c` on the
  existing nonzero-result cleanup path. This targets stale busy/status
  after timeout, spike, overload, or failed mode transition without
  clearing the other observed protection/status bits.
- `0x0801f19a` now enters through a guarded wrapper at `0x0803d606`.
  The wrapper preserves the original mode/range prologue, clears the
  same stale bits `0` and `1`, then continues the original relay/range
  switching code. This targets DC/AC/DC blanking before the relay path
  can inherit a stale status state.
- `0x08016a06` now branches to a bounded low byte-IO wrapper. The wrapper
  preserves the SPI1 status/write/read calls but returns `0xff` if a
  ready flag never appears within the `0x0fa0` budget.
- This is still a recovery/state patch, not proof that ADC filtering,
  True RMS math, or analog front-end noise has been solved.
