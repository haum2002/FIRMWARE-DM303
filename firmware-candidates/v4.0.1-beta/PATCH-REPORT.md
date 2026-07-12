# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

## Safety scope

- Source firmware is not modified in place.
- Output binary size is unchanged.
- Bootloader/updater code and SD update procedure are not patched.
- Flashable default profile keeps fault/default handlers unchanged.
- Flashable default profile keeps runtime fail-stop loops unchanged.
- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`.
- True add-only language menu activation is not patched yet because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `211cf722a13cab09ba0244eb1b9e919bcc40b6b2dcaf0e4f1756675a353edaa4`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 62 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 62 00` | preserve model ID and mark candidate version as V4.0.1 beta |
