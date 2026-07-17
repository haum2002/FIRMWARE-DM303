# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `v401h-repair-g` - expanded latency isolation candidate: repair-f plus the earlier mode/range helper cluster that still used 0x3a98 state-2 guards.

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
- Six mode/range transition guards are capped across two helper clusters: the original four current/meter guards plus two earlier state-2 `0x3a98` guards that also call `0x0801f19a`. All are lowered to vendor-adjacent bounded settle values without touching stream/IO or ADC math.
- Four elapsed-time skip branches immediately before mode/range calls are replaced with NOPs. Direction/state checks remain, but the mode/range call is no longer delayed once the switch condition is detected.
- Stream transfer helper bit0 error gates are kept unchanged.
- Version strings are marked `V4.0.1m` as a visible repair-g expanded latency-isolation flash marker.
- Boot-logo resource load timing is kept unchanged.
- Patched self-loop vector entries: `0`.
- Malay text/resource staging is disabled for this repair profile so official UI resources can be preserved.
- The existing language resources are not staged or replaced by this patcher profile.
- The Spanish language-name string is kept unchanged for this repair profile.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `a84dda5e7f3d675d0985bde4c431a0d86c21d063d7c2dfd56a68726690566c7d`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6d 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6d 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x14b0e` | 4 | `43 f6 98 20` | `40 f2 dc 50` | v401h-repair-g: lower earlier mode/range state-2 guard from 0x3a98 to 0x05dc |
| `0x14b36` | 4 | `43 f6 98 20` | `40 f2 dc 50` | v401h-repair-g: lower second earlier mode/range state-2 guard from 0x3a98 to 0x05dc |
| `0x1585e` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-g: cap first long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15888` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-g: cap second long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15934` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-g: lower remaining current/meter state-2 guard from 0x3a98 to 0x05dc |
| `0x1595c` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-g: lower second remaining current/meter state-2 guard from 0x3a98 to 0x05dc |
| `0x15812` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay first immediate mode/range call after switch condition |
| `0x15838` | 2 | `34 d9` | `00 bf` | stream-recovery-exp15: do not delay second immediate mode/range call after switch condition |
| `0x15862` | 2 | `06 d9` | `00 bf` | stream-recovery-exp15: do not delay first return-to-mode call after AC/DC switch condition |
| `0x1588c` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay second return-to-mode call after AC/DC switch condition |
