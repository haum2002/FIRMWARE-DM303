# DM303 icon-E18 and Malay UI notes

## icon-E18 finding

`system/icon-E18.bmp` is an official resource, not junk data. In the vendor
V4.0 system folder it displays:

```text
ADJ. VOLT SIG
```

The firmware binary also references `icon-en-18`, so the resource is known by
the firmware loader.

## Why it is not force-enabled

The language label packs do not all have the same frame count:

- `icon-C.dat`: 18 frames, including the adjustable-voltage-signal label.
- `icon-SP.dat`, `icon-Dt.dat`, `icon-Fr.dat`, `icon-IT.dat`, `icon-jp.dat`,
  `icon-Kr.dat`, `icon-NL.dat`, `icon-PL.dat`, `icon-Pt.dat`, and
  `icon-RS.dat`: 17 frames.

Because the official non-Chinese packs use 17 frames, this build keeps the
Malay replacement `icon-SP.dat` at 17 frames. Expanding it to 18 frames or
forcing `icon-E18.bmp` into a visible menu could be unsafe until the menu item
table and function dispatch target are confirmed.

## What changed safely

- The old Spanish language-name string `España` is changed in place to
  `Melayu ` at firmware offset `0x25bf8`; the byte length is preserved.
- `system/TEXT_SP.DAT` is replaced with Malay text.
- `system/icon-SP.dat` is replaced with Malay graphical labels and tinted with
  the safe dark RGB565 palette.
- Main navmenu icon BMP files are generated from the official V4.0 backup with
  direct RGB565 pixel writes. BMP headers, masks, dimensions, compression mode,
  and file sizes are preserved.
- The current dark-theme pass preserves vendor gradient/anti-alias levels as
  deep-blue variants instead of flattening them to one color.
- Malay graphical labels use short uppercase text to match the vendor icon
  style, for example `VOLTAN`, `ARUS`, `DATA CAN`, and `DATA K/LIN`.

## Final package hashes

```text
57204ff3219fe2bbb06df116ce6ffd87593605c66b1e0fd40b803f61d08dcab9  DM303V4.0.1-beta.bin
d4a93b1ae0ef215fad8277e768beaa6169bd8b34b2f0f208823791fcec4150ae  system/TEXT_MS.DAT
d4a93b1ae0ef215fad8277e768beaa6169bd8b34b2f0f208823791fcec4150ae  system/TEXT_SP.DAT
3ff19be55a946a99613c46e5501b586fa8202d43a02a1af0f2d5f22f179c8e8d  system/icon-SP.dat
a847c346837164d25e882f0f10bb47815b43e9f381b130e2870447b20d6845a3  system/LOGO-1.bmp
```
