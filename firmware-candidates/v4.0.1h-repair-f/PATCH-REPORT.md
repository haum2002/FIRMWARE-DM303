# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `v401h-repair-f` - noise rollback and latency isolation candidate: official app vectors, official stream/IO paths, official UI resources, and only the AC/DC current-switch timing cluster patches.

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
- Four meter/current transition guards in the same timing cluster are capped: two `0x3e80` compares are changed to `0x0640`, and two remaining state-2 `0x3a98` guards are changed to the vendor-adjacent `0x05dc` settle budget.
- Four elapsed-time skip branches immediately before mode/range calls are replaced with NOPs. Direction/state checks remain, but the mode/range call is no longer delayed once the switch condition is detected.
- Stream transfer helper bit0 error gates are kept unchanged.
- Version strings are marked `V4.0.1l` as a visible repair-f noise-rollback latency-isolation flash marker.
- Boot-logo resource load timing is kept unchanged.
- Patched self-loop vector entries: `0`.
- Malay text/resource staging is disabled for this repair profile so official UI resources can be preserved.
- The existing language resources are not staged or replaced by this patcher profile.
- The Spanish language-name string is kept unchanged for this repair profile.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `a324b9dfc0647601a7775685f15d17185da01d8443b1b2cd67aa7ea7709d4de3`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6c 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6c 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x1585e` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-b: cap first long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15888` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-b: cap second long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15934` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-b: lower remaining state-2 current/meter switch guard from 0x3a98 to vendor-adjacent 0x05dc |
| `0x1595c` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-b: lower second remaining state-2 current/meter switch guard from 0x3a98 to vendor-adjacent 0x05dc |
| `0x15812` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay first immediate mode/range call after switch condition |
| `0x15838` | 2 | `34 d9` | `00 bf` | stream-recovery-exp15: do not delay second immediate mode/range call after switch condition |
| `0x15862` | 2 | `06 d9` | `00 bf` | stream-recovery-exp15: do not delay first return-to-mode call after AC/DC switch condition |
| `0x1588c` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay second return-to-mode call after AC/DC switch condition |
