# DM303 V4.0.1 beta staging

This folder contains staged artifacts generated from the official V4.0 backup
reference. The clean flash package is rebuilt into
`dm303_firmware/DM303-V4.0.1-beta/` with
`tools/dm303_merge_final_package.py`.

## Contents

- `DM303V4.0.1-beta.bin` - patched firmware candidate.
- Final flash package also uses `DM303V4.0.1-beta.bin` as the root firmware
  filename so the updater must display the beta identity.
- `system/TEXT_MS.DAT` - added Bahasa Melayu text resource candidate.
- `system/TEXT_SP.DAT` - Spanish slot replacement containing the Malay text
  resource for device-side selection through the renamed `Melayu` option.
- `system/icon-SP.dat` - Malay graphical label pack for the reused SP slot.
- `system/icon-*.bmp` - official vendor nav-menu icon BMP resources restored
  from the V4.0 backup.
- `system/LOGO-1.bmp` - beta boot logo overlay converted from the selected
  320x240 artwork into the official 16-bit resource layout.
- `PATCH-REPORT.md` - byte-level patch report.
- `SHA256SUMS.txt` - hashes for generated candidate files.
- `DARK-MENU-ASSETS.md` - resource-level tuned dark menu asset report.
- `system/BETA-LOGO-REPORT.md` - resource-level beta logo report.
- `FINAL-PACKAGE-REPORT.md` - validation report for the merged final folder.
- `FINAL-PACKAGE-SHA256.txt` - hashes for the merged final folder.

## Direct firmware changes

- The firmware size remains unchanged at `203260` bytes.
- The flashable profile is now `force-enhanced-exp4`.
- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ
  recovery stub.
- Three known runtime fail-stop loops are changed to return/fall through instead
  of hanging forever.
- Relay/range selector waits in function `0x0801f0f2` are extended to
  `8/12/100` ticks for a stability-first test after relay/range changes.
- Mode-switch helper `0x0801f0ac` is wrapped to call `selector(1, flag)`
  directly. This targets the V4 helper-only tail that differs from the smoother
  V3.16 non-sub-mode-4 path.
- The `LOGO-1.bmp` resource load is routed through a guarded wrapper that calls
  the original loader, waits 200 ticks, and returns.
- The language-name string at offset `0x25bf8` is changed from `España` to
  `Melayu ` with byte length preserved.
- Version strings at offsets `0x02ca0` and `0x02cb0` preserve the original
  model IDs and are marked `MT100MM V4.0.1b` / `BT100MM V4.0.1b`.

## Navmenu UI status

The menu icon BMP resources are restored from the official V4.0 backup. The
dark-theme experiment was removed because it looked rough on the DM303 LCD.
The final package preserves the vendor palette, anti-aliased glyph pixels,
dimensions, headers, and file sizes for `icon-E*.bmp` and `icon-C*.bmp`.

`system/LOGO-1.bmp` is staged from the supplied beta artwork
`C:\Users\Administrator\Downloads\image_(1).bmp`. The output keeps the
official 320x240 16-bit BMP firmware layout and file size.

Header-level items requested for the navmenu, including a top divider/border,
clock/date display, 12/24 hour option, and battery percent/bar option, are not
patched in this flashable package yet. Those items require confirmed runtime
rendering hooks and storage/state mapping, not only BMP resource changes.

## Bahasa Melayu status

Bahasa Melayu has been added as a resource file in this candidate folder and
is copied into the final package as `system/TEXT_MS.DAT`. The existing Spanish
slot `system/TEXT_SP.DAT` is also replaced with the same Malay resource, and
`system/icon-SP.dat` is replaced with Malay graphical labels. The visible
language-name table is patched in place so the device should show `Melayu`,
not `España`. A true add-only Malay slot is not patched because no spare
runtime slot has been confirmed.

`icon-E18.bmp` is the `ADJ. VOLT SIG` resource. The firmware references it, and
the Chinese label pack contains an 18th frame for it, but the official
non-Chinese packs contain only 17 frames. This build does not force-activate
that menu item because the menu dispatch table has not been confirmed safe.

## Safety status

The updater/SD upgrade procedure was not patched. Treat
`dm303_firmware/DM303-V4.0.1-beta/` as the final merged package; its root
firmware filename is intentionally `DM303V4.0.1-beta.bin`. The current final
package includes the `force-enhanced-exp4` runtime patch profile, Malay text
resource, renamed Malay language option, Malay `icon-SP.dat`, restored vendor
navmenu BMP resources, beta logo overlay, and boot-logo settling delay. Still
confirm recovery, rollback, checksum, and device-side behavior before relying
on it on hardware that cannot be risked.
