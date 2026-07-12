# DM303 V4.0.1 beta staging

This folder contains staged artifacts generated from the official V4.0 backup
reference. The clean flash package is rebuilt into `DM303-V4.0.1-beta/` with
`tools/dm303_merge_final_package.py`.

## Contents

- `DM303V4.0.1-beta.bin` - patched firmware candidate.
- Final flash package also uses `DM303V4.0.1-beta.bin` as the root firmware
  filename so the updater must display the beta identity.
- `system/TEXT_MS.DAT` - added Bahasa Melayu text resource candidate.
- `system/icon-*.bmp` - dark nav-menu icon resources.
- `PATCH-REPORT.md` - byte-level patch report.
- `SHA256SUMS.txt` - hashes for generated candidate files.
- `DARK-MENU-ASSETS.md` - resource-level dark menu asset report.
- `FINAL-PACKAGE-REPORT.md` - validation report for the merged final folder.
- `FINAL-PACKAGE-SHA256.txt` - hashes for the merged final folder.

## Direct firmware changes

- The firmware size remains unchanged at `203260` bytes.
- The flashable profile is now `relay-settle-exp1`.
- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ
  recovery stub.
- Three known runtime fail-stop loops are changed to return/fall through instead
  of hanging forever.
- Relay/range selector waits in function `0x0801f0f2` are extended from
  `2/3/10` ticks to `5/8/50` ticks while preserving GPIO order and final pin
  states.
- Version strings at offsets `0x02ca0` and `0x02cb0` preserve the original
  model IDs and are marked `MT100MM V4.0.1b` / `BT100MM V4.0.1b`.

## Navmenu UI status

The menu icon BMP resources are staged with a cleaner dark background,
preserved yellow/white glyph pixels, and a card border on each icon asset.
The dark conversion now recolors only the connected menu-card background so
the original icon and label sharpness is not rescaled or softened. The 92x92
16-bit BMP layout is preserved, and the assets are copied into the current
final package as the visible proof step.

Header-level items requested for the navmenu, including a top divider/border,
clock/date display, 12/24 hour option, and battery percent/bar option, are not
patched in this flashable package yet. Those items require confirmed runtime
rendering hooks and storage/state mapping, not only BMP resource changes.

## Bahasa Melayu status

Bahasa Melayu has been added as a resource file in this candidate folder.
The hardcoded language-name table in the firmware has no confirmed spare slot,
so true add-only menu activation is not patched yet. Replacing an existing
language slot would be easier, but that is not the requested add-only behavior.

## Safety status

The updater/SD upgrade procedure was not patched. Treat `DM303-V4.0.1-beta/`
as the final merged package; its root firmware filename is intentionally
`DM303V4.0.1-beta.bin`. The current final package includes the
`relay-settle-exp1` runtime patch profile and dark navmenu BMP resources. Still
confirm recovery, rollback, checksum, and device-side behavior before relying on
it on hardware that cannot be risked.
