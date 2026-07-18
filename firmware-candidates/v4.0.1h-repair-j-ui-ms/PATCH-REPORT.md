# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `v401h-repair-j-ui-ms` - combined candidate: repair-j measurement bytes (AC/DC switch windows 240) plus Melayu SP-slot name and safe SP-layout Malay text staging; measurement bytes identical to v401h-repair-j.

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
- Single-change candidate: the ammeter AC<->DC switch-state handler's acquisition windows (600/360 polled samples at `0x1df0c`/`0x1df40`) are lowered to the vendor's own 240-sample normal-update window. Three-way vendor comparison showed V3.13 and V3.16 share V4.0's 0x3a98 guards and switch smoothly, so the repair-a..i guard caps are absent here; everything else in the firmware is official V4.0.
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
- Output SHA-256: `e75f8cbd8657c9a72f84ce454d5fc43298aead48c4053df00946eae3f99faf8c`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 72 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 72 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x25bf8` | 7 | `45 73 70 61 c3 b1 61` | `4d 65 6c 61 79 75 20` | rename existing Spanish language menu slot to Melayu without changing table size |
| `0x1df0c` | 4 | `4f f4 16 70` | `40 f2 f0 00` | v401h-repair-j: lower AC->DC switch-state acquisition window from 600 samples (0x258) to vendor's 240 (0xf0) |
| `0x1df40` | 4 | `4f f4 b4 70` | `40 f2 f0 00` | v401h-repair-j: lower DC->AC switch-state acquisition window from 360 samples (0x168) to vendor's 240 (0xf0) |
