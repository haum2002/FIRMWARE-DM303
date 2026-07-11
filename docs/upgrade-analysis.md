# DM303 Firmware Upgrade Analysis

Status: initial candidate branch `analysis/firmware-upgrade-start`.

## Sources

- Local baseline: `DM303-V4.0/DM303V4.004.bin`
- Official AUTOOL update listing: `https://www.autooltech.com/update-info/`
- Official attachment found through AUTOOL WordPress API:
  `https://www.autooltech.com/wp-content/uploads/2025/03/SD-file_DM303_update_US2401042.rar`

The official listing describes `AUTOOL DM303 Software Update-2024`, release
date 2024, version marker `US240104`, and the note "Optimized ignition pulse
test function".

## Vendor Update Notes

`QBtest.txt` is encoded as GBK/CP936. Translation:

1. Power off first. Copy the files to an SD card and insert the SD card into
   the machine.
2. Power on. Select the listed file and press `<OK>` to enter update state.
3. Keep the machine powered on. It automatically replaces all files until the
   main interface is displayed.
4. Power off, remove the SD card, and the update operation is complete.

`readme.txt` states:

- SD type: HC-I or SDC
- SD format: FAT32
- `DM30xDB1.dat`: image data starting from flash address `0x400000`

## Firmware Shape

`DM303V4.004.bin` appears to be a raw ARM Cortex-M image:

- Size: `203260` bytes (`0x319fc`)
- SHA-256:
  `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Initial stack pointer: `0x200126e0`
- Reset handler: `0x0801754d`
- Inferred flash base: `0x08000000`
- Reset offset from base: `0x1754c`

The firmware contains embedded system paths such as:

- `\system\HZK-ALL.GBK`
- `\system\DM30XDB1.dat`
- `\system\icon-e1.bmp`
- `\system\TEXT_EN.DAT`

## First Finding

Before this branch, the local package was missing the data file that the
firmware explicitly tries to load:

```text
\system\DM30XDB1.dat
```

The official `US240104` RAR contains:

```text
system/DM30xDB1.dat
```

Metadata for that file:

- Size: `1179648` bytes (`0x120000`)
- SHA-256:
  `846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79`
- Content shape: repeated BMP-like records, not executable code

This branch adds that file to `DM303-V4.0/system/DM30xDB1.dat`.

## What Not To Do Yet

Do not replace `DM303V4.004.bin` with the official `DM303-V3.13.bin` unless a
deliberate rollback test is planned. The official RAR contains an older-looking
firmware filename and version strings:

- Official binary: `DM303-V3.13.bin`
- Local binary: `DM303V4.004.bin`

The safer first candidate is to keep the V4 executable and add the missing data
file that both the firmware strings and vendor readme reference.

## Candidate Test Plan

1. Use an empty FAT32 SD card.
2. Copy the contents of `DM303-V4.0/` to the SD card root.
3. Verify SD card file hashes against `CHECKSUMS-SHA256.txt`.
4. Confirm the device battery/power is stable.
5. Confirm recovery options before testing on a valuable unit.
6. Power off, insert SD card, power on, select the update file, and press
   `<OK>` as described by the vendor notes.
7. Record device version screen, boot behavior, and whether the earlier
   instability remains.

No executable firmware patch has been made in this branch.
