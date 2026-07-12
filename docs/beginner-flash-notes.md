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
- Navmenu patut menggunakan ikon berlatar gelap yang lebih kemas, dengan border
  pada kad ikon. Ikon dan tulisan asal tidak diskala semula.
- Build ini menggunakan profil `anti-freeze-exp1`.

## Apa yang belum aktif

- Bahasa Melayu UI belum aktif dalam menu bahasa.
- Patch ini belum menjamin akurasi bacaan; ia hanya mengurangkan risiko hang
  kekal dengan reset recovery dan laluan keluar daripada loop fail-stop.
- Jam/tarikh header, pilihan 12/24 jam, dan pilihan paparan bateri belum
  dipatch. Jika paparan itu belum muncul, itu normal untuk build ini.

## Cara semak pakej

Sahkan hash firmware:

```text
9206f9e0c574a8f4ad4c8ba1be7fb51206799641b89e74ce202a93c372382112  DM303V4.0.1-beta.bin
```

Skrip validasi utama:

```powershell
python tools/dm303_v4_static_analysis.py --no-walk
python tools/dm303_compare_sets.py
```

## Rollback / diagnosis

Jika perlu jana semula profil minimal tanpa patch anti-freeze untuk bandingan,
guna:

```powershell
python tools/dm303_v401_beta_patch.py --profile boot-acceptance
python tools/dm303_merge_final_package.py --profile boot-acceptance
```

Selepas itu semak semula hash dan laporan sebelum flash. Untuk kembali kepada
build `anti-freeze-exp1`, jalankan:

```powershell
python tools/dm303_v401_beta_patch.py --profile anti-freeze-exp1
python tools/dm303_merge_final_package.py --profile anti-freeze-exp1
```

## Peraturan keselamatan

- Pastikan bateri/peranti stabil semasa update.
- Jangan cabut SD card atau matikan device semasa proses update berjalan.
- Simpan salinan firmware asal.
- Uji satu perubahan pada satu masa; jika gagal, lebih mudah tahu puncanya.
