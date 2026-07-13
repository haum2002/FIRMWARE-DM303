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
- Navmenu patut kembali menggunakan ikon vendor rasmi yang tajam, bukan ikon
  tema gelap eksperimen.
- Dalam pilihan bahasa, slot yang dahulu bernama Sepanyol kini patut muncul
  sebagai `Melayu`. Pilih `Melayu` untuk menguji UI Melayu.
- Logo boot `LOGO-1.bmp` patut memaparkan artwork beta yang dibekalkan.
- Build ini menggunakan profil `force-enhanced-exp4`.
- Timing relay/range selector dipanjangkan kepada `8/12/100` ticks untuk ujian
  stability-first selepas relay/range berubah. Patch utama lain ialah wrapper
  mode-switch `0x0801f0ac` dan delay boot-logo 200 ticks.

## Apa yang belum aktif

- Resource Bahasa Melayu `system/TEXT_MS.DAT` sudah disertakan.
- Pilihan bahasa `Melayu` menggunakan `system/TEXT_SP.DAT` untuk teks dan
  `system/icon-SP.dat` untuk label grafik menu.
- `icon-E18.bmp` dikenal pasti sebagai `ADJ. VOLT SIG`, tetapi tidak
  diaktifkan paksa kerana pack bahasa bukan-Cina rasmi hanya mempunyai 17
  frame dan jadual dispatch fungsi belum disahkan.
- Patch ini belum menjamin akurasi bacaan penuh; ia mengurangkan risiko hang
  kekal dan menambah masa settling relay/range sebelum bacaan disambung semula.
- Jam/tarikh header, pilihan 12/24 jam, dan pilihan paparan bateri belum
  dipatch. Jika paparan itu belum muncul, itu normal untuk build ini.
- Filter ADC/EMI sebenar belum dipatch kerana alamat enjin pengukuran belum
  disahkan selamat.
- Math/True RMS belum dipatch dalam build ini. Rutin scaling/math sudah dikesan
  secara statik, tetapi belum cukup disahkan untuk diubah tanpa risiko merosak
  bacaan.

## Jangan guna V4.0.2 beta sedia ada

Semua pakej V4.0.2 beta sedia ada dalam workspace ini dianggap gagal/corrupt
dan tidak patut diflash:

- `firmware-candidates/v4.0.2-beta/`
- `dm303_firmware/DM303-V4.0.2-beta/`
- `dm303_firmware/DM303-V4.0.2-beta-FINAL/`

Sebab utama:

- Ada patch pada offset tekaan yang menimpa code/string loader.
- Salah satu binary V4.0.2 bersaiz `203261` bytes, satu byte lebih besar
  daripada saiz firmware rasmi/V4.0.1b `203260` bytes.
- Pakej `V4.0.2-beta-FINAL` mengubah banyak vector IRQ/fault ke reset vector
  dan mempunyai identiti versi tidak konsisten.

Rujukan audit: `docs/v402-qwen-audit.md`.

## Cara semak pakej

Sahkan hash firmware:

```text
f09f9f43a156b62e90c708c858986ae57f6baa2102a307f5830999b0557249da  DM303V4.0.1-beta.bin
```

Skrip validasi utama:

```powershell
python tools/dm303_v4_static_analysis.py --no-walk
python tools/dm303_compare_sets.py --current dm303_firmware\DM303-V4.0.1-beta
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
python tools/dm303_v401_beta_patch.py --profile force-enhanced-exp4
python tools/dm303_make_dark_menu_assets.py
powershell -ExecutionPolicy Bypass -File tools/dm303_make_ms_icon_pack.ps1
powershell -ExecutionPolicy Bypass -File tools/dm303_make_beta_logo.ps1 -SourceArtwork "C:\Users\Administrator\Downloads\image_(1).bmp"
python tools/dm303_merge_final_package.py --profile force-enhanced-exp4
```

## Ujian A/B selepas dapatan V3.16

Ujian fizikal V3.16 menunjukkan tukar DC -> AC -> DC boleh lancar walaupun
timing relay/range selector sama seperti V4.0 rasmi, iaitu `2/3/10` ticks.
Build semasa `force-enhanced-exp4` sengaja menggunakan timing lebih panjang
`8/12/100` untuk menguji sama ada digital fuse/relay/range settling membantu
kes blank/freeze yang masih berlaku.

Untuk bandingan paling bersih:

```powershell
python tools/dm303_v401_beta_patch.py --profile v316-switch-exp3
python tools/dm303_merge_final_package.py --profile v316-switch-exp3
python tools/dm303_v316_v401_compare.py
```

Flash pakej `dm303_firmware/DM303-V4.0.1-beta/` dan uji:

- Ammeter DC -> AC -> DC sekurang-kurangnya 50 kali.
- Voltmeter DC -> AC -> DC sekurang-kurangnya 50 kali.
- Oscilloscope pada `0.1 V/div` dan `12.5 us`.
- Catat noise puncak positif/negatif, masa blank, dan sama ada perlu restart.

Jika perlu bandingkan dengan mitigasi delay panjang lama:

```powershell
python tools/dm303_v401_beta_patch.py --profile force-stable-exp2
python tools/dm303_merge_final_package.py --profile force-stable-exp2
```

Jika `force-enhanced-exp4` masih blank/freeze, jangan tambah delay lagi secara
membuta tuli. Langkah seterusnya mesti cari hook state/filter bacaan untuk
noise, zeroing, offset, dan valid-reading timeout.

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
