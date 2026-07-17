# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `v401h-repair-h` - ammeter-mapped latency candidate: repair-g plus the AC/20A/mA function's own 0x3a98 state-2 guards.

## Safety scope

- Source firmware is not modified in place.
- Output binary size is unchanged.
- Bootloader/updater code and SD update procedure are not patched.
- Flashable profile keeps fault/default handlers unchanged.
- Flashable profile keeps runtime fail-stop loops unchanged.
- Relay/range selector timing is kept unchanged.
- Mode-switch helper behavior is kept unchanged.
- High-level measurement stream/status retry loops are kept unchanged.
- Lower byte-IO hardware-ready timeout is kept unchanged.
- Command helper retry counters are kept unchanged.
- Stream error-state cleanup is kept unchanged.
- Mode/range entry state is kept unchanged.
- Stream busy early-return gate is kept unchanged.
- Eight transition guards are capped: Repair-G's six mode/range guards plus two `0x3a98` state-2 guards in the function mapped by UI text to `AC`, `20A(Yellow)`, and `mA(Green)`. This directly targets the reported ammeter green AC -> DC latency while keeping stream/IO, ADC math, relay settle, and UI resources official.
- Four elapsed-time skip branches immediately before mode/range calls are replaced with NOPs. Direction/state checks remain, but the mode/range call is no longer delayed once the switch condition is detected.
- Stream transfer helper bit0 error gates are kept unchanged.
- Version strings are marked `V4.0.1n` as a visible repair-h ammeter-mapped latency flash marker.
- Boot-logo resource load timing is kept unchanged.
- Patched self-loop vector entries: `0`.
- Malay text/resource staging is disabled for this repair profile so official UI resources can be preserved.
- The existing language resources are not staged or replaced by this patcher profile.
- The Spanish language-name string is kept unchanged for this repair profile.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `52c49425aa655999982bce98e8ebd39221b5c2208d168785dbb56a48730dac92`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6e 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6e 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x14b0e` | 4 | `43 f6 98 20` | `40 f2 dc 50` | v401h-repair-h: lower earlier mode/range state-2 guard from 0x3a98 to 0x05dc |
| `0x14b36` | 4 | `43 f6 98 20` | `40 f2 dc 50` | v401h-repair-h: lower second earlier mode/range state-2 guard from 0x3a98 to 0x05dc |
| `0x1585e` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-h: cap first long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15888` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-h: cap second long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15934` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-h: lower remaining current/meter state-2 guard from 0x3a98 to 0x05dc |
| `0x1595c` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-h: lower second remaining current/meter state-2 guard from 0x3a98 to 0x05dc |
| `0x1d1a4` | 4 | `43 f6 98 20` | `40 f2 dc 50` | v401h-repair-h: lower ammeter AC/20A/mA state-2 guard from 0x3a98 to 0x05dc |
| `0x1d1c0` | 4 | `43 f6 98 20` | `40 f2 dc 50` | v401h-repair-h: lower second ammeter AC/20A/mA state-2 guard from 0x3a98 to 0x05dc |
| `0x15812` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay first immediate mode/range call after switch condition |
| `0x15838` | 2 | `34 d9` | `00 bf` | stream-recovery-exp15: do not delay second immediate mode/range call after switch condition |
| `0x15862` | 2 | `06 d9` | `00 bf` | stream-recovery-exp15: do not delay first return-to-mode call after AC/DC switch condition |
| `0x1588c` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay second return-to-mode call after AC/DC switch condition |
