# DM303 V4.0.1 beta candidate

This folder contains a direct firmware candidate generated from the official
V4.0 snapshot in this repository.

## Contents

- `DM303V4.0.1-beta.bin` - patched firmware candidate.
- `system/TEXT_MS.DAT` - added Bahasa Melayu text resource candidate.
- `PATCH-REPORT.md` - byte-level patch report.
- `SHA256SUMS.txt` - hashes for generated candidate files.

## Direct firmware changes

- The firmware size remains unchanged at `203260` bytes.
- Self-loop exception/default vectors now point to a shared recovery stub.
- The recovery stub writes `0x05FA0004` to `SCB_AIRCR` (`0xE000ED0C`) to request hardware reset.
- Version strings at offsets `0x02ca0` and `0x02cb0` are marked `V4.0.1 beta`.

## Bahasa Melayu status

Bahasa Melayu has been added as a resource file in this candidate folder.
The hardcoded language-name table in the firmware has no confirmed spare slot,
so true add-only menu activation is not patched yet. Replacing an existing
language slot would be easier, but that is not the requested add-only behavior.

## Safety status

This is a candidate for bench validation. The updater/SD upgrade procedure was
not patched. Do not treat this as fully validated production firmware until
recovery, rollback, and device-side behavior are confirmed.
