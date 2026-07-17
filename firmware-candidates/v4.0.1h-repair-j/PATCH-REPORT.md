# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `v401h-repair-j` - single-change AC/DC switch-window candidate: official V4.0 plus the two AC/DC switch-state acquisition windows (600/360) lowered to the vendor's own 240; evidence in docs/v313-v316-v40-switching-comparison-2026-07-17.md.

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
- Version strings are marked `V4.0.1q` as a visible repair-j AC/DC switch-window flash marker.
- Boot-logo resource load timing is kept unchanged.
- Patched self-loop vector entries: `0`.
- Malay text/resource staging is disabled for this repair profile so official UI resources can be preserved.
- The existing language resources are not staged or replaced by this patcher profile.
- The Spanish language-name string is kept unchanged for this repair profile.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `ecd7b5dc85158467ce9e2ffc8b71fd1523c934383c7d1e6677b7bd0f79e34642`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 71 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 71 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x1df0c` | 4 | `4f f4 16 70` | `40 f2 f0 00` | v401h-repair-j: lower AC->DC switch-state acquisition window from 600 samples (0x258) to vendor's 240 (0xf0) |
| `0x1df40` | 4 | `4f f4 b4 70` | `40 f2 f0 00` | v401h-repair-j: lower DC->AC switch-state acquisition window from 360 samples (0x168) to vendor's 240 (0xf0) |
