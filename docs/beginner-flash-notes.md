# DM303 V4.0.1 beta beginner flash notes

Nota ini untuk orang yang baru pertama kali melihat pakej DM303.

## Fail yang perlu masuk SD card

Salin isi folder `DM303-V4.0.1-beta/` terus ke root SD card, bukan ke dalam
folder tambahan.

Root SD card sepatutnya kelihatan begini:

```text
DM303V4.0.1-beta.bin
QBtest.txt
readme.txt
system/
```

Jangan letak fail seperti ini:

```text
SD:/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
```

Susunan itu boleh menyebabkan DM303 masuk loading putih, gagal update, atau
boot semula ke firmware asal.

## Apa yang patut kelihatan selepas flash

- Versi firmware menunjukkan `V4.0.1b`.
- Nama fail update yang dipilih ialah `DM303V4.0.1-beta.bin`.
- Navmenu patut menggunakan ikon berlatar gelap.

## Apa yang belum aktif

- Bahasa Melayu UI belum aktif dalam menu bahasa.
- Patch anti-freeze kod belum dimasukkan ke final semasa.
- Jam/tarikh header, pilihan 12/24 jam, dan pilihan paparan bateri belum
  dipatch.

## Cara semak pakej

Sahkan hash firmware:

```text
211cf722a13cab09ba0244eb1b9e919bcc40b6b2dcaf0e4f1756675a353edaa4  DM303V4.0.1-beta.bin
```

Skrip validasi utama:

```powershell
python tools/dm303_v4_static_analysis.py --no-walk
python tools/dm303_compare_sets.py
```

## Peraturan keselamatan

- Pastikan bateri/peranti stabil semasa update.
- Jangan cabut SD card atau matikan device semasa proses update berjalan.
- Simpan salinan firmware asal.
- Uji satu perubahan pada satu masa; jika gagal, lebih mudah tahu puncanya.
