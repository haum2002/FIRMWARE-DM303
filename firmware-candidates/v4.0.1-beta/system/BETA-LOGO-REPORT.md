# DM303 V4.0.1 beta logo report

Status: direct BMP-to-RGB565 LOGO-1 overlay for `v4.0.1 beta`.

## Safety scope

- Source artwork pixels are decoded directly from the BMP byte payload.
- No image library, resampling, encoder, compression, dithering, or scaling is used.
- Firmware BMP header, dimensions, bit depth, compression mode, RGB565 masks, row layout, and file size are preserved from the official V4.0 template.
- Near-black residue pixels are snapped to exact black before RGB565 packing to avoid LCD speckle without changing geometry or header format.
- Firmware code, bootloader, and updater are not touched by this tool.

## Input

- Template: `backup/DM303 V4.0-read only/system/LOGO-1.bmp`
- Template SHA-256: `f5e84dfd0a14f63ad8c570629c59c36a0a8a8844ce4cfc48c9c89d1031b41ba3`
- Source artwork: `C:/Users/Administrator/Downloads/image_(1).bmp`
- Source artwork SHA-256: `f430fc1738e3c7a0b1118cb4181256c5a35b900c8f891b076a14a1a49e583e23`
- Source layout: `320x240`, `32` bpp, compression `3`, pixel offset `122`

## Output

- File: `firmware-candidates/v4.0.1-beta/system/LOGO-1.bmp`
- Output SHA-256: `a847c346837164d25e882f0f10bb47815b43e9f381b130e2870447b20d6845a3`
- Output layout: `320x-240`, `16` bpp, compression `3`, pixel offset `70`
- Changed pixels vs template: `9935`
- Unique RGB565 colors: `1326`
- Near-black pixels sanitized: `30895`
- Output size matches template: `True`
