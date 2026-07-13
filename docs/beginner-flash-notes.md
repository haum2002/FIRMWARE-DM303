# DM303 V4.0.1 beta beginner flash notes

Nota ini untuk orang yang baru pertama kali melihat pakej DM303.

## Fail yang perlu masuk SD card

Salin isi folder `dm303_firmware/DM303-V4.0.1-beta/` terus ke root SD card,
bukan ke dalam folder tambahan.

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
- Navmenu patut menggunakan ikon `Soft Eye` yang lebih lembut, dengan border
  pada kad ikon. Ikon dan tulisan tidak diskala semula.
- Build ini menggunakan profil `force-stable-exp2`.
- Semasa zeroing atau tukar DC/AC, relay mungkin terasa sedikit lebih lambat
  kerana masa settling sengaja dipanjangkan kepada profil `8/12/100` ticks.

## Apa yang belum aktif

- Resource Bahasa Melayu `system/TEXT_MS.DAT` sudah disertakan.
- Pilihan bahasa SP kini menggunakan `system/TEXT_SP.DAT` yang berisi Bahasa
  Melayu. Pilih SP jika mahu menguji UI Melayu pada device.
- Patch ini belum menjamin akurasi bacaan penuh; ia mengurangkan risiko hang
  kekal dan menambah masa settling relay/range sebelum bacaan disambung semula.
- Jam/tarikh header, pilihan 12/24 jam, dan pilihan paparan bateri belum
  dipatch. Jika paparan itu belum muncul, itu normal untuk build ini.
- Filter ADC/EMI sebenar belum dipatch kerana alamat enjin pengukuran belum
  disahkan selamat.

## Cara semak pakej

Sahkan hash firmware:

```text
c97a03d6b21a74ade4fff057d5966fd180a3682a0b08d04a58093ffbfbb006be  DM303V4.0.1-beta.bin
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

Untuk kembali kepada build semasa selepas diagnosis:

```powershell
python tools/dm303_v401_beta_patch.py --profile force-stable-exp2
python tools/dm303_merge_final_package.py --profile force-stable-exp2
```

## Ujian selepas flash untuk isu bacaan

- Short probe merah dan hitam, masuk voltmeter DC, tekan zeroing, tunggu bacaan
  stabil.
- Tukar DC -> AC -> DC sebanyak 20 kali pada voltmeter dan ammeter. Catat jika
  paparan blank lebih daripada 2 saat.
- Untuk ammeter, ulang ujian dengan input selamat atau dummy load, bukan pada
  litar kenderaan penting.
- Jangan guna injector/ignition/generator pada beban sebenar sehingga waveform
  disemak dengan oscilloscope luaran.

## Peraturan keselamatan

- Pastikan bateri/peranti stabil semasa update.
- Jangan cabut SD card atau matikan device semasa proses update berjalan.
- Simpan salinan firmware asal.
- Uji satu perubahan pada satu masa; jika gagal, lebih mudah tahu puncanya.
