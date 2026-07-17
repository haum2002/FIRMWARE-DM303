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
V4.0 rasmi, iaitu `2/3/10` ticks. Semakan disassembly seterusnya membetulkan
andaian lama: helper V3.16 dan V4.0 mempunyai bentuk kawalan yang sama pada
laluan relevan, jadi wrapper helper eksperimen tidak dijadikan default lagi.

Build semasa kini menggunakan profil `stream-recovery-exp15`: laluan
exception/default tetap diarahkan kepada permintaan reset sistem, tiga
fail-stop runtime keluar/return daripada loop kekal, relay/range timing
dikekalkan pada `2/3/10`, helper mode-switch `0x0801f0ac` dikekalkan seperti
V4.0 rasmi, empat retry loop stream/status bacaan dibuat fail-fast selepas
helper bawah sudah timeout, helper byte-IO bawah dihala kepada wrapper bounded
`0x0fa0` yang pulang `0xff` jika ready flag tidak muncul, dua retry command
tinggi dikurangkan daripada `0x95`/`0x87` kepada `0x60`, kegagalan busy command
`0x40` dihala ke laluan error/clear sedia ada, stream error cleanup
membersihkan bit `0` dan `1` daripada `0x2000022c`, entry mode/range
`0x0801f19a` melalui wrapper stale-state clear sebelum relay/range switching,
stream/status `0x080196b2` memaksa transaction segar apabila stale busy gate
masih set, dua long current/meter switch gate `0x0802585e` dan `0x08025888`
diccap daripada `0x3e80` kepada `0x0640`, dan load resource `LOGO-1.bmp`
melalui wrapper delay 200 ticks. Exp15 ditambah selepas exp14 diuji tanpa
penambahbaikan nyata; ia menandakan versi dalaman sebagai `V4.0.1c`, membuang
empat elapsed-time skip branch sebelum panggilan mode/range, dan bypass tiga
stale bit0 early-error gate dalam stream helper.

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
- Delay dalam calon relay/range selector `0x0801f0f2` tidak dipanjangkan dalam
  profil semasa; ia kekal pada nilai rasmi/V3.16 `2/3/10` ticks.
- Helper mode-switch `0x0801f0ac` tidak dibalut dalam profil semasa; ia kekal
  seperti V4.0 rasmi.
- Retry loop stream/status pada offset `0x09570`, `0x09758`, dan `0x097be`
  tidak lagi mengulang tanpa had apabila helper bawah sudah timeout tetapi
  busy/valid flag masih tersangkut. Laluan ini kini keluar daripada retry supaya
  UI/status refresh boleh berjalan semula.
- Cabang busy command `0x40` pada offset `0x09706` kini dihala ke blok
  error/clear sedia ada di `0x080197a2`, bukan fall-through normal.
- Helper byte-IO bawah `0x08016a06` kini bercabang daripada offset `0x06a06`
  kepada wrapper bounded di `0x08016a50`. Wrapper ini mengekalkan panggilan
  SPI1 status/write/read, menunggu ready flag sehingga bajet `0x0fa0`, dan
  pulang `0xff` jika timeout supaya upper stream recovery dapat bertindak.
- Stream error cleanup pada `0x080197e6` kini membersihkan bit `0` dan `1`
  daripada `0x2000022c`.
- Entry mode/range pada `0x0801f19a` kini bercabang ke wrapper `0x0803d606`
  yang menjalankan prologue asal, membersihkan bit stale `0` dan `1`, kemudian
  kembali ke fungsi asal sebelum relay/range switching diteruskan.
- Stream/status pada `0x080196be` kini bercabang terus ke body transaction
  normal supaya stale busy bit tidak menyebabkan early-return kosong.
- Dua compare long switch gate pada `0x0802585e` dan `0x08025888` dicap
  daripada `0x3e80` kepada `0x0640` untuk mengurangkan blank AC -> DC ammeter
  sekitar 30 saat.
- Empat elapsed-time skip branch sebelum panggilan mode/range pada
  `0x08025812`, `0x08025838`, `0x08025862`, dan `0x0802588c` diganti dengan
  NOP supaya transition AC/DC yang sudah dikesan boleh memanggil mode/range
  segera.
- Tiga stream helper pada `0x08019818`, `0x080198b4`, dan `0x08019950`
  bypass stale bit0 early-error gate dan meneruskan helper body normal.
- String versi di offset `0x02ca0` dan `0x02cb0` mengekalkan identiti model
  asal dan ditukar kepada `MT100MM V4.0.1c` / `BT100MM V4.0.1c`.
- Bootloader/updater dan prosedur SD upgrade tidak dipatch.

Hash candidate:

```text
3a2db571a4c783d0df2a454ec13d8d38a3a22a0e6ad7cc9993a0afa1edd7f3a0  DM303V4.0.1-beta.bin
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
- SHA-256: `d4a93b1ae0ef215fad8277e768beaa6169bd8b34b2f0f208823791fcec4150ae`

Bahasa Melayu ditambah sebagai resource staging dan dioverlay ke folder akhir
sebagai fail tambahan `system/TEXT_MS.DAT`. Slot bahasa SP sedia ada turut
diganti dengan resource yang sama melalui `system/TEXT_SP.DAT`. Aktivasi menu
Bahasa Melayu secara add-only belum dipatch kerana jadual nama bahasa hardcoded
sekitar `0x08035be4` belum mempunyai spare slot yang disahkan.

## UI navmenu

Navmenu kini menggunakan tema gelap selamat pada lapisan resource:

- Source asset: `backup/DM303 V4.0-read only/system/icon-*.bmp`
- Staging: `firmware-candidates/v4.0.1-beta/system/icon-*.bmp`
- Final: `dm303_firmware/DM303-V4.0.1-beta/system/icon-*.bmp`
- 34 ikon BMP menu final dijana daripada backup V4.0 rasmi dengan penulisan
  piksel RGB565 terus, tanpa encoder imej, resize, compression, atau rewrite
  header.
- Header BMP, mask RGB565, dimensi `92x92`, row layout, bit depth, compression
  mode `BI_BITFIELDS`, dan saiz fail `17000` byte dikekalkan.
- Palet final menggunakan gradasi deep navy vendor-preserving, text
  `#E2EEF4`, dan amber `#EEC642`/`#F8DA60`.
- `system/icon-SP.dat` Melayu turut ditint dengan palet yang sama dan kekal 17
  frame, `78336` byte.
- Laporan: `firmware-candidates/v4.0.1-beta/DARK-MENU-ASSETS.md`

Logo beta juga dibuat pada lapisan resource:

- Source artwork: `C:\Users\Administrator\Downloads\image_(1).bmp`
- Template firmware: `backup/DM303 V4.0-read only/system/LOGO-1.bmp`
- Staging: `firmware-candidates/v4.0.1-beta/system/LOGO-1.bmp`
- Final: `dm303_firmware/DM303-V4.0.1-beta/system/LOGO-1.bmp`
- Artwork `image_(1).bmp` daripada pengguna dibaca terus daripada payload BMP
  dan ditukar ke layout firmware `LOGO-1.bmp` tanpa image encoder, resampling,
  compression, dithering, atau scaling.
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
python tools/dm303_validate_final_package.py
```

Peraturan gabungan:

- `backup/` dibaca sahaja dan tidak diubah.
- `firmware-candidates/v4.0.1-beta/` menjadi input staging.
- `dm303_firmware/DM303-V4.0.1-beta/` dibina semula bersih daripada rujukan
  V4.0 rasmi.
- Nama root firmware akhir ialah `DM303V4.0.1-beta.bin`.
- `DM303V4.004.bin` asal dibuang daripada folder akhir.
- Kandungan `DM303V4.0.1-beta.bin` akhir mempunyai hash
  `3a2db571a4c783d0df2a454ec13d8d38a3a22a0e6ad7cc9993a0afa1edd7f3a0`.
- Resource `system/` akhir diambil daripada rujukan V4.0 rasmi; `TEXT_MS.DAT`,
  `TEXT_SP.DAT`, `icon-SP.dat`, 34 ikon BMP gelap, dan `LOGO-1.bmp` beta
  daripada staging dioverlay.
- `system/TEXT_MS.DAT` dioverlay sebagai resource tambahan Bahasa Melayu.
- `system/TEXT_SP.DAT` diganti dengan resource Melayu untuk menggantikan
  pilihan SP pada device.
- `system/icon-SP.dat` diganti dengan label Melayu bertema gelap; SHA-256:
  `3ff19be55a946a99613c46e5501b586fa8202d43a02a1af0f2d5f22f179c8e8d`.
- Nested tree tidak sah seperti `system/system/` ditolak.
- Validator akhir `tools/dm303_validate_final_package.py` menyemak hash
  firmware/resource, byte patch `stream-recovery-exp15`, layout RGB565
  `LOGO-1.bmp`, layout semua 34 ikon BMP gelap, saiz `icon-SP.dat`, dan
  ketiadaan nested `system/system/`.
- Pre-flash checker `tools/dm303_preflash_check.py` boleh digunakan pada folder
  akhir atau root SD card sebenar untuk mengesan kesilapan salin fail ke dalam
  folder tambahan sebelum device mencuba update.

## Pembetulan selepas ujian device menolak upgrade

Ujian pada device menunjukkan pakej akhir sebelumnya tidak masuk proses update:
fungsi upgrade tertutup dan device boot seperti biasa. Semakan lanjut
menunjukkan patch lama membuang prefix model dalam slot versi: string asal
`MT100MM V4.0` dan `BT100MM V4.0` telah diganti kepada `V4.0.1 beta`. Jika
updater menyemak identiti model sebelum flash, perubahan itu boleh menyebabkan
fail dianggap bukan firmware yang sesuai.

Patch seterusnya masih mengekalkan prefix model dan hanya menaikkan versi
kepada bentuk yang muat dalam slot 16-byte. Build semasa menggunakan marker
diagnostik `MT100MM V4.0.1c` dan `BT100MM V4.0.1c`. Build minimal dan build resource beta sudah diterima oleh
device. Selepas pengguna mengesahkan masalah fallback lama berpunca daripada
fail firmware diletakkan dalam folder SD card, profil `anti-freeze-exp1`
dimasukkan semula dan pernah dikembangkan kepada `force-stable-exp2` untuk
eksperimen settling relay/range. Dapatan V3.16 kemudian menunjukkan delay
panjang bukan punca tunggal, tetapi pemerhatian terbaru masih menunjukkan
blank/freeze selepas spike/overload. Build semasa dinaikkan kepada
`stream-recovery-exp15`: helper V4.0 asal, timing rasmi `2/3/10`, fault
recovery, fail-fast pada retry loop stream/status bacaan, timeout byte-IO bawah
wrapper bounded `0x0fa0` dengan pulangan `0xff` pada timeout, clamp retry
command `0x40`/`0x48` kepada `0x60`, command `0x40` busy-failure route ke
error/clear, stream/status stale-bit clear, mode/range stale-state clear,
stream transaction forced past stale-busy early-return, current-switch long
gate cap, immediate mode/range switch gates, stale bit0 helper bypass,
Bahasa Melayu, dan boot-logo delay 200 ticks. Bahasa Melayu
resource sudah disertakan, dan slot Sepanyol lama dinamakan semula `Melayu`;
menu Bahasa Melayu add-only masih belum diaktifkan.

Laporan akhir:

- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-REPORT.md`
- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-SHA256.txt`
- `CHECKSUMS-SHA256.txt`

## Dapatan cranking dan kemungkinan hardware

Pemerhatian terbaru menunjukkan mode cranking boleh memaparkan voltan masa
nyata sekitar `2.88 V` ketika bateri internal nominal `3.7 V` dan indikator
bateri masih sekitar `3/4` bar. Ini belum membuktikan firmware salah membaca
bateri internal. Mode cranking direka untuk input bateri kenderaan; jika
kabel/klip tidak disambung, channel input boleh terapung dan mendapat ghost
voltage daripada bias/leakage/rail internal.

Resource Melayu cranking kini ditambah nota bahawa bacaan tanpa sambungan boleh
terapung dan tidak boleh dianggap sebagai voltan bateri sebenar. Firmware tidak
menolak `2.88 V` secara fixed-offset kerana tindakan itu akan merosakkan ujian
cranking sebenar pada bateri kenderaan yang lemah. Laluan diagnosis penuh
berada di `docs/power-rail-cranking-analysis.md`.

## Dapatan set fail

- Perbandingan dengan `backup/DM303 V4.0-read only` mengesahkan set final
  dibina daripada rujukan V4.0 rasmi, dengan perbezaan terkawal pada firmware
  utama, `TEXT_MS.DAT`, `TEXT_SP.DAT`, `icon-SP.dat`, 34 ikon BMP navmenu
  bertema gelap, dan `LOGO-1.bmp`.
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

Jana label ikon Melayu, kemudian tint tema gelap:

```powershell
powershell -ExecutionPolicy Bypass -File tools/dm303_make_ms_icon_pack.ps1
python tools/dm303_make_dark_menu_assets.py
```

Jana logo beta:

```powershell
python tools/dm303_make_beta_logo.py --source "C:\Users\Administrator\Downloads\image_(1).bmp"
```

Gabungkan ke folder akhir:

```powershell
python tools/dm303_merge_final_package.py
python tools/dm303_validate_final_package.py
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta
```

Sahkan firmware akhir:

```powershell
python tools/dm303_v4_static_analysis.py --no-walk
```

Sahkan resource Bahasa Melayu:

```powershell
python tools/dm303_text_resource.py --input firmware-candidates/v4.0.1-beta/system/TEXT_MS.DAT --verify-rebuild
```
