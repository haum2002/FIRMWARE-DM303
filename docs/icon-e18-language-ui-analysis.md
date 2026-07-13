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
- `system/icon-SP.dat` is replaced with Malay graphical labels.
- Main navmenu icon BMP files are restored byte-for-byte from the official
  V4.0 backup to remove the bad dark-theme experiment.
- Malay graphical labels use short uppercase text to match the vendor icon
  style, for example `VOLTAN`, `ARUS`, `DATA CAN`, and `DATA K/LIN`.

## Final package hashes

```text
f09f9f43a156b62e90c708c858986ae57f6baa2102a307f5830999b0557249da  DM303V4.0.1-beta.bin
7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd  system/TEXT_MS.DAT
7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd  system/TEXT_SP.DAT
cd47c7e59f38488d6ffd10617a5d90ab5c79791535a3f75d70fbaaae42c7c4b3  system/icon-SP.dat
ddf12753b3238ac02a064a1596a6030e27a328fc5d710d538d0ea5989fee8ced  system/LOGO-1.bmp
```
