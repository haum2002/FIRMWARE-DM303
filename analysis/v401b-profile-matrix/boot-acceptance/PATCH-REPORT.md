# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `boot-acceptance` - minimal beta identity and resource build.

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
- Long meter/current transition guards are kept unchanged.
- Immediate mode/range switch gates are kept unchanged.
- Stream transfer helper bit0 error gates are kept unchanged.
- Version strings are marked `V4.0.1b`.
- Boot-logo resource load timing is kept unchanged.
- Patched self-loop vector entries: `0`.
- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`.
- The existing Spanish `TEXT_SP.DAT` slot is replaced with the same Malay resource for device-side language selection.
- The existing Spanish language-name string is renamed to `Melayu` in place, with byte length preserved.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `ea910e141c9ddb19b550e4769fa87228fb5601492ae412487c39dc6efbc304d5`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 62 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 62 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x25bf8` | 7 | `45 73 70 61 c3 b1 61` | `4d 65 6c 61 79 75 20` | rename existing Spanish language menu slot to Melayu without changing table size |
