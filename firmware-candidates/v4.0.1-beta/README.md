# DM303 V4.0.1 beta staging

This folder contains staged artifacts generated from the official V4.0 backup
reference. The clean flash package is rebuilt into `DM303-V4.0.1-beta/` with
`tools/dm303_merge_final_package.py`.

## Contents

- `DM303V4.0.1-beta.bin` - patched firmware candidate.
- `system/TEXT_MS.DAT` - added Bahasa Melayu text resource candidate.
- `system/icon-*.bmp` - dark nav-menu icon resources.
- `PATCH-REPORT.md` - byte-level patch report.
- `SHA256SUMS.txt` - hashes for generated candidate files.
- `DARK-MENU-ASSETS.md` - resource-level dark menu asset report.
- `FINAL-PACKAGE-REPORT.md` - validation report for the merged final folder.
- `FINAL-PACKAGE-SHA256.txt` - hashes for the merged final folder.

## Direct firmware changes

- The firmware size remains unchanged at `203260` bytes.
- Self-loop exception/default vectors now point to a shared recovery stub.
- The recovery stub writes `0x05FA0004` to `SCB_AIRCR` (`0xE000ED0C`) to request hardware reset.
- Runtime fail-stop loops at `0x09ca0`, `0x0c6c8`, and `0x2c4ea` no longer loop forever.
- Version strings at offsets `0x02ca0` and `0x02cb0` are marked `V4.0.1 beta`.

## Navmenu UI status

The menu icon BMP resources are rebuilt with a dark background, yellow icons,
and preserved 92x92 16-bit BMP layout. Header-level clock/date/battery options
are not patched yet because the runtime render path and setting storage still
need safer mapping.

## Bahasa Melayu status

Bahasa Melayu has been added as a resource file in this candidate folder.
The hardcoded language-name table in the firmware has no confirmed spare slot,
so true add-only menu activation is not patched yet. Replacing an existing
language slot would be easier, but that is not the requested add-only behavior.

## Safety status

The updater/SD upgrade procedure was not patched. Treat `DM303-V4.0.1-beta/`
as the final merged package, but still confirm recovery, rollback, checksum,
and device-side behavior before relying on it on hardware that cannot be risked.
