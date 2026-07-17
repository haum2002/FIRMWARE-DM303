# DM303 V4.0.1 beta beginner flash notes

Build semasa ialah pembetulan resource Melayu/SP selepas `V4.0.1g` gagal.
Jangan anggap build ini sudah menyelesaikan akurasi/noise/latency.

## Pakej semasa

- Profil build: `stability-exp20-ms-safe`
- Marker versi pada device: `V4.0.1h`
- Folder flash: `dm303_firmware/DM303-V4.0.1-beta/`
- Fail firmware: `DM303V4.0.1-beta.bin`
- SHA-256 firmware:

```text
b9f54dbc46b25a8f9da7af85bc12c8eb591d7806372f10487b1aa717150ac45f  DM303V4.0.1-beta.bin
```

## Cara salin ke SD card

Salin isi folder `dm303_firmware/DM303-V4.0.1-beta/` terus ke root SD card,
bukan ke dalam folder tambahan.

Root SD card sepatutnya kelihatan begini:

```text
DM303V4.0.1-beta.bin
QBtest.txt
readme.txt
system/
```

## Apa yang patut kelihatan selepas flash

- Versi firmware menunjukkan `V4.0.1h`.
- Jika calit atas tulisan masih berlaku, puncanya bukan lagi mismatch
  `TEXT_SP.DAT` 815-entry.
- Slot `Melayu` patut memaparkan sebahagian teks Melayu. Tidak semua ayat akan
  Melayu kerana hanya entry yang muat dalam layout SP vendor diganti.
- `system/DM30XDB1.dat` mesti ada.

## Kenapa V4.0.1h dibuat

`V4.0.1g` menggunakan `TEXT_SP.DAT` Melayu yang dibina daripada `TEXT_EN.DAT`
815-entry. Vendor `TEXT_SP.DAT` hanya 773-entry. `V4.0.1h` membina semula
resource Melayu daripada `TEXT_SP.DAT` rasmi supaya struktur slot SP sepadan.

## Validasi sebelum flash

```powershell
python tools/dm303_validate_final_package.py --profile stability-exp20-ms-safe
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stability-exp20-ms-safe
```

Selepas salin ke SD card, tukar `E:\` kepada drive letter SD card sebenar:

```powershell
python tools/dm303_preflash_check.py --root E:\ --profile stability-exp20-ms-safe --allow-sd-extras
```

## Ujian fizikal utama

1. Semak dahulu sama ada calit tulisan hilang atau berkurang.
2. Pilih `Melayu`; catat bahagian mana Melayu dan mana masih bahasa asal.
3. Ammeter, probe hijau, DC -> AC -> DC. Catat masa AC ke DC.
4. Catat sama ada nombor bacaan dan ikon bateri hilang bersama.
5. Voltmeter AC input kosong/short selamat. Catat min/max.
6. Oscilloscope pada `0.1 V/div` dan `12.5 us`. Catat noise positif/negatif.

## Nota keselamatan

- Pastikan bateri/peranti stabil semasa update.
- Jangan cabut SD card atau matikan device semasa proses update.
- Simpan salinan firmware asal.
- Jangan uji injector/ignition/generator pada beban sebenar sehingga waveform
  disemak dengan alat luaran.
