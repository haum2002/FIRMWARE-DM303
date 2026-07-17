# DM303 V4.0.1b latency guard report

Image: `dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin`
SHA-256: `29a8bd71cba65538ba25d8e76aa5122234f9a28ad957287ba82fbf4fdf6c60af`
Expected SHA-256: `29a8bd71cba65538ba25d8e76aa5122234f9a28ad957287ba82fbf4fdf6c60af`
Overall OK: `True`

## Visible version marker

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x02ca0` | `0x08012ca0` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `True` | visible exp16 UI-safe marker for main firmware identity |
| `0x02cb0` | `0x08012cb0` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `True` | visible exp16 UI-safe marker for secondary firmware identity |

Exp16 intentionally marks both internal version strings as `V4.0.1d`.
The SD-card firmware filename remains `DM303V4.0.1-beta.bin`, but the
device version screen must show the new marker if this exact build flashed.

## Stream recovery patch bytes

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x09570` | `0x08019570` | `00 bf` | `00 bf` | `True` | stream-read retry after lower helper timeout |
| `0x09706` | `0x08019706` | `4c d1` | `4c d1` | `True` | command-0x40 busy failure routes to existing error/clear path |
| `0x09758` | `0x08019758` | `00 bf` | `00 bf` | `True` | command-0xe9 retry while status clear fails |
| `0x097be` | `0x080197be` | `00 bf` | `00 bf` | `True` | mode/status retry while command helper fails |

Three branches are changed to `NOP` so that the firmware returns
through its existing failure/status path after the lower helper has
already timed out. The command-0x40 busy-failure branch is not a NOP
in exp10/exp11/exp12/exp13/exp14/exp15/exp16; it routes into the existing error/clear sequence so the
status path is not treated as normal fall-through.

## Bounded low byte-IO helper

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x06a06` | `0x08016a06` | `00 f0 23 b8` | `00 f0 23 b8` | `True` | low byte-IO helper branch to bounded wrapper |
| `0x06a50` | `0x08016a50` | `70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 70 bd 00 bf 00 30 01 40` | `70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 70 bd 00 bf 00 30 01 40` | `True` | bounded low byte-IO wrapper; returns 0xff on ready-timeout |

Exp16 keeps the exp11 route from `0x08016a06` to a local wrapper at `0x08016a50`.
The wrapper keeps the SPI1 status/write/read HAL calls and a `0x0fa0`
ready-wait budget, but returns `0xff` if either ready flag never
appears. This is intended to expose timeout to the upper stream
recovery instead of continuing with a stale byte read.

## Command retry counters

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x0967c` | `0x0801967c` | `60 27` | `60 27` | `True` | command 0x40 bounded retry count, 0x60 |
| `0x09682` | `0x08019682` | `60 27` | `60 27` | `True` | command 0x48 bounded retry count, 0x60 |
| `0x09694` | `0x08019694` | `0a 27` | `0a 27` | `True` | fallback bounded retry count, 0x0a |

The two long command-specific bounded retry counts are reduced to
`0x60`; the fallback count remains `0x0a`. This lowers worst-case
status latency while preserving the same polling and failure path.

## Stream state clear

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x097e6` | `0x080197e6` | `20 f0 03 00` | `20 f0 03 00` | `True` | stream error cleanup clears flag bits 0 and 1 from 0x2000022c |

Exp12/exp13/exp14/exp15/exp16 changes the existing nonzero-result cleanup from `bic #1` to
`bic #3`. It clears only bits `0` and `1` of `0x2000022c`, leaving
the other observed protection/status bits untouched. This targets the
field symptom where the numeric reading and battery icon disappear
together after spike, overload, or AC/DC switching.

## Mode/range state clear

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x0f19a` | `0x0801f19a` | `1e f0 34 ba` | `1e f0 34 ba` | `True` | mode/range entry routes to stale stream-state clear wrapper |
| `0x2d606` | `0x0803d606` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `True` | mode/range wrapper clears bits 0 and 1 of 0x2000022c then continues original function |

Exp13/exp14/exp15/exp16 adds a guarded entry wrapper to the mode/range function. The
wrapper runs the original prologue, clears the same stale stream bits
`0` and `1`, then returns to the original function before relay/range
logic continues. This is intended to stop stale busy/status state from
surviving a DC/AC/DC transition.

## Stream busy gate

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x096be` | `0x080196be` | `02 e0` | `02 e0` | `True` | force stream transaction body instead of stale-busy early return |

Exp14 changes the entry stale-busy check at `0x080196be` from a
conditional skip/return path to an unconditional branch into the
normal transaction body. This targets the measured case where AC->DC
ammeter recovery stays blank while the firmware waits for a stale
busy gate to expire.

## Current switch latency caps

| Offset | Address | Expected | Actual | OK | Purpose |
|---:|---:|---|---|---|---|
| `0x1585e` | `0x0802585e` | `b0 f5 c8 6f` | `b0 f5 c8 6f` | `True` | cap first long meter/current switch gate from 0x3e80 to 0x0640 |
| `0x15888` | `0x08025888` | `b0 f5 c8 6f` | `b0 f5 c8 6f` | `True` | cap second long meter/current switch gate from 0x3e80 to 0x0640 |

Exp14 caps two long transition gates from `0x3e80` to `0x0640`. The
original value matches the reported roughly 30-second blank window
when the scheduler tick is near 2ms, so this is a direct latency
mitigation while keeping a bounded settle guard.


## Exp16 rollback note

Exp16 intentionally removes exp15's four immediate-switch gates and
three stale bit0 bypass gates because the device showed the `V4.0.1c`
marker with no performance improvement and possible regression. The
remaining latency guard is the less aggressive exp14 cap plus the
stream/state recovery bytes.
