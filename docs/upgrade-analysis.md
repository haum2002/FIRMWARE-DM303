# Analisis naik taraf dalaman DM303 V4.0.1 beta

Status: pakej akhir `v4.0.1 beta` telah dijana di
`dm303_firmware/DM303-V4.0.1-beta/`.
Validasi yang dibuat ialah validasi statik dan rebuild resource; ujian pada
device sebenar, recovery, dan rollback masih perlu dibuat sebelum penggunaan
berisiko rendah boleh disahkan.

## Skop terkunci

Kerja ini hanya menggunakan firmware rasmi yang dibekalkan di workspace ini:

- `backup/DM303 V4.0-read only/` sebagai rujukan read-only.
- `firmware-candidates/v4.0.1-beta/` sebagai staging hasil modifikasi.
- `dm303_firmware/DM303-V4.0.1-beta/` sebagai folder akhir yang digabungkan.

Pakej firmware luar, muat turun awam, dan fail update yang beredar di luar
tidak digunakan untuk perbandingan, patch, atau gabungan. Fail lama daripada
luar tidak disalin masuk ke pakej akhir.

## Identiti baseline

- Source firmware: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Size: `203260` bytes (`0x319fc`)
- SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Working load-base assumption: `0x08010000`

Load base ini disokong oleh vector table:

- Initial stack pointer: `0x200126e0`
- Reset vector: `0x0801754d`, mapping ke file offset `0x0754c`
- Sasaran reset boleh didisassemble sebagai kod startup Thumb yang sah
- Reset stub asal memuatkan target `0x08017339` dan kemudian melompat ke
  `0x08010199`

## Masalah freeze yang disasarkan

Firmware asal mempunyai beberapa exception/fault/default handler yang branch
kepada diri sendiri tanpa tamat. Ini termasuk HardFault, MemManage, BusFault,
UsageFault, dan banyak default vector. Jika spike isyarat, overload, akses
memori tidak sah, peripheral state rosak, atau interrupt tidak dijangka masuk
ke handler ini, device boleh kelihatan hang kerana handler tidak pernah return.

Selepas pengguna mengesahkan fallback sebelumnya berpunca daripada susunan fail
SD card, patch anti-freeze dimasukkan semula. Dapatan fizikal V3.16 kemudian
menunjukkan DC -> AC -> DC boleh lancar walaupun selector timing sama seperti
V4.0 rasmi, iaitu `2/3/10` ticks. Build semasa kini menggunakan profil
`force-enhanced-exp4`: laluan exception/default tetap diarahkan kepada
permintaan reset sistem, tiga fail-stop runtime keluar/return daripada loop
kekal, relay/range settling dipanjangkan kepada `8/12/100`, helper mode-switch
`0x0801f0ac` dibalut untuk memanggil `selector(1, flag)` seperti laluan V3.16
non-sub-mode-4, dan load resource `LOGO-1.bmp` melalui wrapper delay 200 ticks.

Ini belum menyelesaikan semua punca bacaan tidak stabil seperti DMA/state
acquisition, filtering, kalibrasi ADC, atau display-update blocking. Ia ialah
patch reliability/recovery untuk mengurangkan keadaan hang kekal apabila fault
atau fail-stop path tercetus. Math/True RMS dan ADC/filter engine belum dipatch
kerana hook runtime yang selamat belum disahkan.

## Perubahan firmware candidate

Firmware candidate berada di:

```text
firmware-candidates/v4.0.1-beta/DM303V4.0.1-beta.bin
```

Perubahan yang dibuat:

- Saiz binari kekal `203260` bytes.
- Vector exception/default self-loop dialihkan kepada stub recovery yang menulis
  `SCB_AIRCR SYSRESETREQ`.
- Fail-stop runtime pada offset `0x09ca0`, `0x0c6c8`, dan `0x2c4ea`
  ditukar supaya fall-through/return dan tidak loop selama-lamanya.
- Delay dalam calon relay/range selector `0x0801f0f2` dipanjangkan:
  offset `0x0f10a` daripada `2` ke `8`, offset `0x0f146` daripada `3` ke
  `12`, dan offset `0x0f192` daripada `10` ke `100`.
- String versi di offset `0x02ca0` dan `0x02cb0` mengekalkan identiti model
  asal dan ditukar kepada `MT100MM V4.0.1b` / `BT100MM V4.0.1b`.
- Bootloader/updater dan prosedur SD upgrade tidak dipatch.

Hash candidate:

```text
b2c86842c8149f6b66648285e4cbec61f7699fd4ac2ec424725a784cd484a992  DM303V4.0.1-beta.bin
```

Dalam folder flash akhir, fail root juga kekal bernama
`DM303V4.0.1-beta.bin`. Ini disengajakan supaya menu updater perlu memaparkan
identiti beta; nama rasmi lama `DM303V4.004.bin` tidak digunakan sebagai
penutup atau alias.

## Bahasa Melayu UI

Format `TEXT_*.DAT` telah diparse dan boleh dibina semula byte-identical.
Setiap entri mempunyai record panjang 2-byte dan jadual offset di awal fail.

Resource Bahasa Melayu:

- Source binaan: `backup/DM303 V4.0-read only/system/TEXT_EN.DAT`
- Candidate: `localization/ms_MY/TEXT_MS.DAT`
- Staging: `firmware-candidates/v4.0.1-beta/system/TEXT_MS.DAT`
- Final: `dm303_firmware/DM303-V4.0.1-beta/system/TEXT_MS.DAT`.
- SP slot replacement: `dm303_firmware/DM303-V4.0.1-beta/system/TEXT_SP.DAT`
  contains the same Malay resource so the existing SP language option can be
  used for device-side testing.

Validasi semasa:

- 815 entri boleh diparse.
- 781 entri diterjemah atau diwrap semula.
- `TEXT_MS.DAT` boleh rebuild byte-identical.
- Tiada aksara bukan ASCII untuk mengurangkan risiko font/rendering.
- SHA-256: `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd`

Bahasa Melayu ditambah sebagai resource staging dan dioverlay ke folder akhir
sebagai fail tambahan `system/TEXT_MS.DAT`. Slot bahasa SP sedia ada turut
diganti dengan resource yang sama melalui `system/TEXT_SP.DAT`. Aktivasi menu
Bahasa Melayu secara add-only belum dipatch kerana jadual nama bahasa hardcoded
sekitar `0x08035be4` belum mempunyai spare slot yang disahkan.

## UI navmenu

Tema tuned dark navmenu dibuat pada lapisan resource:

- Source asset: `backup/DM303 V4.0-read only/system/icon-*.bmp`
- Staging: `firmware-candidates/v4.0.1-beta/system/icon-*.bmp`
- Final: `dm303_firmware/DM303-V4.0.1-beta/system/icon-*.bmp`
- 34 ikon BMP menu final ditukar kepada palet charcoal-blue rata berdasarkan
  arah tema gelap sebelumnya.
- Penjana menukar background biru vendor kepada satu tona charcoal-blue,
  menormalkan foreground putih/kuning, dan mengelak gradient shadow.
- Ikon dan label asal tidak diskala semula atau diblur, jadi bentuk asal
  dikekalkan.
- Border satu warna ditambah di dalam setiap aset `92x92`.
- Header BMP, dimensi `92x92`, row layout, dan saiz fail dikekalkan.
- Laporan: `firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS.md`

Logo beta juga dibuat pada lapisan resource:

- Source artwork: `assets/logo/dm303-v401-beta-logo-source.bmp`
- Template firmware: `backup/DM303 V4.0-read only/system/LOGO-1.bmp`
- Staging: `firmware-candidates/v4.0.1-beta/system/LOGO-1.bmp`
- Final: `dm303_firmware/DM303-V4.0.1-beta/system/LOGO-1.bmp`
- Artwork `image_(1).bmp` daripada pengguna ditukar ke layout firmware
  `LOGO-1.bmp`.
- Header BMP, dimensi `320x240`, row layout, bit depth, dan saiz fail
  dikekalkan.

Fungsi UI runtime seperti jam/tarikh di header, pilihan 12/24 jam, pilihan
bateri peratus/bar, dan border header antara navmenu/bateri belum dipatch
kerana titik fungsi render/header dan storage setting belum disahkan selamat.
Carian statik menunjukkan string format masa seperti `Year-Mon-Day Hour:Min:Sec`,
tetapi belum menjumpai literal RTC `0x40002800` atau laluan render header yang
boleh dipatch tanpa risiko fallback/brick. Ini masih tugas runtime berikutnya,
bukan resource-only patch.

## Pakej akhir

Skrip gabungan:

```powershell
python tools/dm303_merge_final_package.py
```

Peraturan gabungan:

- `backup/` dibaca sahaja dan tidak diubah.
- `firmware-candidates/v4.0.1-beta/` menjadi input staging.
- `dm303_firmware/DM303-V4.0.1-beta/` dibina semula bersih daripada rujukan
  V4.0 rasmi.
- Nama root firmware akhir ialah `DM303V4.0.1-beta.bin`.
- `DM303V4.004.bin` asal dibuang daripada folder akhir.
- Kandungan `DM303V4.0.1-beta.bin` akhir mempunyai hash
  `b2c86842c8149f6b66648285e4cbec61f7699fd4ac2ec424725a784cd484a992`.
- Resource `system/` akhir diambil daripada rujukan V4.0 rasmi; 34 ikon
  navmenu tuned dark dan `LOGO-1.bmp` beta daripada staging dioverlay.
- `system/TEXT_MS.DAT` dioverlay sebagai resource tambahan Bahasa Melayu.
- `system/TEXT_SP.DAT` diganti dengan resource Melayu untuk menggantikan
  pilihan SP pada device.
- Nested tree tidak sah seperti `system/system/` ditolak.

## Pembetulan selepas ujian device menolak upgrade

Ujian pada device menunjukkan pakej akhir sebelumnya tidak masuk proses update:
fungsi upgrade tertutup dan device boot seperti biasa. Semakan lanjut
menunjukkan patch lama membuang prefix model dalam slot versi: string asal
`MT100MM V4.0` dan `BT100MM V4.0` telah diganti kepada `V4.0.1 beta`. Jika
updater menyemak identiti model sebelum flash, perubahan itu boleh menyebabkan
fail dianggap bukan firmware yang sesuai.

Patch seterusnya masih mengekalkan prefix model dan hanya menaikkan versi
kepada bentuk yang muat dalam slot 16-byte: `MT100MM V4.0.1b` dan
`BT100MM V4.0.1b`. Build minimal dan build navmenu gelap sudah diterima oleh
device. Selepas pengguna mengesahkan masalah fallback lama berpunca daripada
fail firmware diletakkan dalam folder SD card, profil `anti-freeze-exp1`
dimasukkan semula dan pernah dikembangkan kepada `force-stable-exp2` untuk
eksperimen settling relay/range. Dapatan V3.16 kemudian menunjukkan delay
panjang bukan punca tunggal, tetapi pemerhatian terbaru masih menunjukkan
blank/freeze selepas spike/overload. Build semasa dinaikkan kepada
`force-enhanced-exp4` untuk ujian stability-first: wrapper mode-switch V3.16,
settling `8/12/100`, dan boot-logo delay 200 ticks. Bahasa Melayu resource
sudah disertakan, tetapi menu Bahasa Melayu add-only masih belum diaktifkan.

Laporan akhir:

- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-REPORT.md`
- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-SHA256.txt`
- `CHECKSUMS-SHA256.txt`

## Dapatan set fail

- Perbandingan dengan `backup/DM303 V4.0-read only` mengesahkan set final
  dibina daripada rujukan V4.0 rasmi, dengan firmware utama dan 34 ikon menu
  gelap yang berbeza.
- Perbandingan dengan `backup/DM303 V3.16-read only` menunjukkan aset bersama
  kebanyakannya sama, tetapi firmware utama berbeza.
- `backup/SD-file_DM303_update_US240104-read only` ialah set update lain yang
  lebih kecil. Ia mengandungi `\system\DM30xDB1.dat`, tetapi set V4.0 rasmi dan
  set V3.16 rasmi tidak mengandungi fail itu.
- Binari merujuk `\system\DM30XDB1.dat`, tetapi fail itu tidak wujud dalam set
  V4.0 rasmi. Fail daripada set versi lain tidak disalin masuk kerana format,
  alamat flash, dan compatibility belum dibuktikan.

## Arahan validasi

Pasang dependency analisis jika perlu:

```powershell
python -m pip install -r tools/requirements-analysis.txt
```

Jana resource Bahasa Melayu:

```powershell
python tools/dm303_make_ms_pack.py
```

Jana firmware candidate:

```powershell
python tools/dm303_v401_beta_patch.py
```

Jana tema gelap ikon navmenu:

```powershell
python tools/dm303_make_dark_menu_assets.py
```

Gabungkan ke folder akhir:

```powershell
python tools/dm303_merge_final_package.py
```

Sahkan firmware akhir:

```powershell
python tools/dm303_v4_static_analysis.py --no-walk
```

Sahkan resource Bahasa Melayu:

```powershell
python tools/dm303_text_resource.py --input firmware-candidates/v4.0.1-beta/system/TEXT_MS.DAT --verify-rebuild
```
