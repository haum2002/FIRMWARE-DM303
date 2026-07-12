# Analisis naik taraf dalaman DM303 V4.0.1 beta

Status: pakej akhir `v4.0.1 beta` telah dijana di `DM303-V4.0.1-beta/`.
Validasi yang dibuat ialah validasi statik dan rebuild resource; ujian pada
device sebenar, recovery, dan rollback masih perlu dibuat sebelum penggunaan
berisiko rendah boleh disahkan.

## Skop terkunci

Kerja ini hanya menggunakan firmware rasmi yang dibekalkan di workspace ini:

- `backup/DM303 V4.0-read only/` sebagai rujukan read-only.
- `firmware-candidates/v4.0.1-beta/` sebagai staging hasil modifikasi.
- `DM303-V4.0.1-beta/` sebagai folder akhir yang digabungkan.

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

Patch anti-freeze eksperimen pernah menukar laluan exception/default kepada
permintaan reset dan menukar beberapa fail-stop runtime kepada return. Ujian
hardware selepas itu menunjukkan white-screen/loading fallback ke firmware asal.
Oleh itu folder akhir semasa diturunkan kepada boot-acceptance build: hanya
identiti beta dipatch dahulu, manakala patch anti-freeze kod disimpan sebagai
calon eksperimen sehingga punca fallback dipetakan dengan lebih tepat.

Ini belum menyelesaikan semua punca bacaan tidak stabil seperti DMA/state
acquisition, filtering, atau display-update blocking. Langkah semasa ialah
memastikan device menerima identiti beta yang paling minimal sebelum patch
fungsi dimasukkan semula secara satu-per-satu.

## Perubahan firmware candidate

Firmware candidate berada di:

```text
firmware-candidates/v4.0.1-beta/DM303V4.0.1-beta.bin
```

Perubahan yang dibuat:

- Saiz binari kekal `203260` bytes.
- Vector exception/default dikekalkan seperti firmware asal dalam
  boot-acceptance build.
- Fail-stop runtime pada offset `0x09ca0`, `0x0c6c8`, dan `0x2c4ea`
  dikekalkan seperti firmware asal dalam boot-acceptance build.
- String versi di offset `0x02ca0` dan `0x02cb0` mengekalkan identiti model
  asal dan ditukar kepada `MT100MM V4.0.1b` / `BT100MM V4.0.1b`.
- Bootloader/updater dan prosedur SD upgrade tidak dipatch.

Hash candidate:

```text
211cf722a13cab09ba0244eb1b9e919bcc40b6b2dcaf0e4f1756675a353edaa4  DM303V4.0.1-beta.bin
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
- Final: belum dimasukkan ke boot-acceptance build.

Validasi semasa:

- 815 entri boleh diparse.
- 781 entri diterjemah atau diwrap semula.
- `TEXT_MS.DAT` boleh rebuild byte-identical.
- Tiada aksara bukan ASCII untuk mengurangkan risiko font/rendering.
- SHA-256: `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd`

Bahasa Melayu ditambah sebagai resource staging baru. Aktivasi menu Bahasa
Melayu secara add-only belum dipatch kerana jadual nama bahasa hardcoded sekitar
`0x08035be4` belum mempunyai spare slot yang disahkan. Resource ini sengaja
belum dioverlay ke folder akhir semasa supaya ujian hardware seterusnya hanya
menguji penerimaan identiti beta minimal.

## UI navmenu

Tema gelap navmenu dibuat pada lapisan resource:

- Source asset: `backup/DM303 V4.0-read only/system/icon-*.bmp`
- Staging: `firmware-candidates/v4.0.1-beta/system/icon-*.bmp`
- Final: belum dimasukkan ke boot-acceptance build.
- 34 ikon BMP menu staging ditukar latar daripada biru kepada gelap.
- Header BMP, dimensi `92x92`, row layout, dan saiz fail dikekalkan.
- Laporan: `firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS.md`

Fungsi UI runtime seperti jam/tarikh di header, pilihan 12/24 jam, pilihan
bateri peratus/bar, dan border header antara navmenu/bateri belum dipatch
kerana titik fungsi render/header dan storage setting belum disahkan selamat.

## Pakej akhir

Skrip gabungan:

```powershell
python tools/dm303_merge_final_package.py
```

Peraturan gabungan:

- `backup/` dibaca sahaja dan tidak diubah.
- `firmware-candidates/v4.0.1-beta/` menjadi input staging.
- `DM303-V4.0.1-beta/` dibina semula bersih daripada rujukan V4.0 rasmi.
- Nama root firmware akhir ialah `DM303V4.0.1-beta.bin`.
- `DM303V4.004.bin` asal dibuang daripada folder akhir.
- Kandungan `DM303V4.0.1-beta.bin` akhir mempunyai hash
  `211cf722a13cab09ba0244eb1b9e919bcc40b6b2dcaf0e4f1756675a353edaa4`.
- Resource `system/` akhir diambil terus daripada rujukan V4.0 rasmi.
- `system/TEXT_MS.DAT` dan ikon navmenu gelap belum dioverlay dalam
  boot-acceptance build.
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
`BT100MM V4.0.1b`. Selepas laporan terbaru bahawa build penuh memaparkan layar
putih/loading dan fallback ke firmware asal, folder akhir kini sengaja dibina
sebagai boot-acceptance build tanpa patch anti-freeze kod dan tanpa overlay
resource. Jika build minimal ini diterima, punca fallback hampir pasti berada
pada patch kod anti-freeze atau overlay resource. Jika masih ditolak, punca
berada pada penerimaan nama/versi beta atau validator updater.

Laporan akhir:

- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-REPORT.md`
- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-SHA256.txt`
- `CHECKSUMS-SHA256.txt`

## Dapatan set fail

- Perbandingan dengan `backup/DM303 V4.0-read only` mengesahkan set final
  dibina daripada rujukan V4.0 rasmi, dengan hanya nama/kandungan firmware
  utama yang berbeza.
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
