# FIRMWARE-DM303

Arkib komuniti untuk kerja naik taraf AUTool DM303 daripada firmware rasmi
V4.0 yang dibekalkan oleh pengguna kepada pakej `v4.0.1 beta`.

Vendor telah menyatakan bahawa peranti ini tidak lagi menerima sokongan kemas
kini firmware rasmi. Repo ini menyimpan hasil analisis, skrip bina semula, dan
pakej akhir supaya perubahan boleh disemak tanpa menimpa rujukan asal.

## Aliran kerja folder

- `backup/` - rujukan rasmi tempatan sahaja. Folder ini tidak dijejak dalam git,
  tidak diubah, dan digunakan sebagai input read-only oleh skrip.
- `firmware-candidates/v4.0.1-beta/` - staging untuk hasil modifikasi, laporan
  patch, resource Bahasa Melayu, dan checksum candidate.
- `dm303_firmware/DM303-V4.0.1-beta/` - folder akhir yang telah digabungkan
  semula sebagai pakej upgrade/flash.
- `CHECKSUMS-SHA256.txt` - checksum SHA-256 untuk semua fail dalam folder akhir.

## Pakej akhir

Firmware akhir:

```text
c97a03d6b21a74ade4fff057d5966fd180a3682a0b08d04a58093ffbfbb006be  dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
```

Nama fail root `DM303V4.0.1-beta.bin` digunakan supaya updater dan pengguna
dapat melihat identiti beta secara terus. String model dalaman masih mengekalkan
prefix asal `MT100MM`/`BT100MM` dengan versi ringkas `V4.0.1b`.

Pakej akhir semasa ialah **force-stable-exp2 build**. Firmware mengekalkan
identiti `V4.0.1b`, memasukkan 34 ikon navmenu `Soft Eye`, menambah resource
Bahasa Melayu, mengganti slot bahasa SP dengan Melayu, mengalih fault/default
self-loop handler kepada permintaan reset sistem, menukar tiga runtime
fail-stop loop supaya tidak mengunci peranti selama-lamanya, dan memanjangkan
masa settling relay/range selector kepada profil lebih konservatif `8/12/100`
ticks sebelum bacaan disambung semula.

Resource Bahasa Melayu staging:

```text
7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd  dm303_firmware/DM303-V4.0.1-beta/system/TEXT_MS.DAT
7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd  dm303_firmware/DM303-V4.0.1-beta/system/TEXT_SP.DAT
```

Folder `dm303_firmware/DM303-V4.0.1-beta/` ditandakan sebagai binari dalam
`.gitattributes` supaya Git tidak menukar byte firmware, font, ikon, logo, atau
resource semasa checkout dan commit.

## Nota keselamatan

- Jangan flash tanpa menyemak checksum, laporan patch, dan kaedah recovery.
- Bootloader/updater dan prosedur SD upgrade tidak dipatch.
- Perubahan firmware dibuat melalui skrip, bukan edit binari manual.
- Patch anti-freeze kod sudah dimasukkan ke folder akhir semasa, tetapi ini
  masih perlu diuji pada device kerana ia mengubah laluan fault/runtime.
- Patch force-stable hanya memanjangkan delay sedia ada dalam fungsi
  `0x0801f0f2`; ia belum membuktikan akurasi analog, true RMS, atau noise
  oscilloscope sudah selesai tanpa ujian bench.
- Bahasa Melayu sudah disertakan sebagai `system/TEXT_MS.DAT`; pilihan SP
  menggunakan resource Melayu melalui `system/TEXT_SP.DAT`. Menu bahasa
  add-only belum dipatch kerana slot runtime yang selamat belum disahkan.
- Tiada patch ADC/EMI matematik dimasukkan kerana alamat enjin pengukuran
  belum disahkan. Menulis filter ke alamat tekaan akan berisiko merosakkan
  firmware.
- Simpan salinan firmware asal daripada peranti sendiri jika boleh.
- Catat versi hardware, kaedah flash, dan pilihan rollback sebelum mencuba.

## Arahan ringkas

Jana semula resource Bahasa Melayu:

```powershell
python tools/dm303_make_ms_pack.py
```

Jana semula firmware candidate:

```powershell
python tools/dm303_v401_beta_patch.py
```

Jana semula profil force-stable semasa secara eksplisit:

```powershell
python tools/dm303_v401_beta_patch.py --profile force-stable-exp2
python tools/dm303_merge_final_package.py --profile force-stable-exp2
```

Jana semula profil minimal untuk rollback/diagnostik:

```powershell
python tools/dm303_v401_beta_patch.py --profile boot-acceptance
python tools/dm303_merge_final_package.py --profile boot-acceptance
```

Jana tema gelap ikon navmenu:

```powershell
python tools/dm303_make_dark_menu_assets.py
```

Gabungkan staging ke folder akhir:

```powershell
python tools/dm303_merge_final_package.py
```

Sahkan binari dan resource:

```powershell
python tools/dm303_v4_static_analysis.py --no-walk
python tools/dm303_text_resource.py --input firmware-candidates/v4.0.1-beta/system/TEXT_MS.DAT --verify-rebuild
```

Analisis penuh berada di [docs/upgrade-analysis.md](docs/upgrade-analysis.md).

Analisis isu noise/zeroing/acquisition berada di
[docs/measurement-noise-analysis.md](docs/measurement-noise-analysis.md).

Nota flash untuk pemula berada di [docs/beginner-flash-notes.md](docs/beginner-flash-notes.md).
