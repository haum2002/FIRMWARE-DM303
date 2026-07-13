# DM303 V4.0.1 beta logo report

Status: resource-level LOGO-1.bmp overlay for `v4.0.1 beta`.

## Safety scope

- Source artwork archive is `assets/logo/dm303-v401-beta-logo-source.bmp`.
- Firmware BMP template is `backup/DM303 V4.0-read only/system/LOGO-1.bmp`.
- If source artwork exists, it is converted directly into the official 16-bit LOGO-1.bmp layout.
- If source artwork is absent, the clean vendor logo pixels are kept from the original template and the website text is replaced with `BETA VERSION`.
- BMP header, dimensions, bit depth, compression mode, row layout, and file size are preserved.
- Firmware code, bootloader, and updater are not touched by this tool.

## Output

- File: `system/LOGO-1.bmp`
- Source artwork SHA-256: `f430fc1738e3c7a0b1118cb4181256c5a35b900c8f891b076a14a1a49e583e23`
- Changed pixels vs template: `12101`
- Output SHA-256: `ddf12753b3238ac02a064a1596a6030e27a328fc5d710d538d0ea5989fee8ced`
