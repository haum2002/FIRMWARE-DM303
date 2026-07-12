# Analisis naik taraf dalaman DM303 V4.0

Status: analisis sahaja. Tiada imej `v4.0.1 beta` yang boleh diflash telah dihasilkan.

## Skop terkunci

Kerja ini hanya menggunakan snapshot firmware yang dibekalkan dalam repo ini:

- `DM303-V4.0/DM303V4.004.bin`
- `DM303-V4.0/system/`
- fail teks vendor di dalam `DM303-V4.0/`
- set rasmi tambahan yang pengguna letakkan di `backup/`

Pakej firmware luar, muat turun awam, dan fail update yang beredar di luar tidak termasuk dalam skop. Fail seperti itu tidak boleh digunakan untuk perbandingan, patch, atau gabungan. Calon luar yang pernah tersilap diuji telah ditarik balik dan branch/PR berkaitan tidak lagi menjadi laluan upgrade aktif.

## Identiti baseline

- Main firmware: `DM303-V4.0/DM303V4.004.bin`
- Size: `203260` bytes (`0x319fc`)
- SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Working load-base assumption: `0x08010000`

Load base ini disokong oleh vector table:

- Initial stack pointer: `0x200126e0`
- Reset vector: `0x0801754d`, mapping to file offset `0x0754c`
- Sasaran reset boleh didisassemble sebagai kod startup Thumb yang sah di offset tersebut
- Reset stub memuatkan target `0x08017339` dan kemudian melompat ke `0x08010199`. Redirect fault terus ke reset stub tidak boleh dianggap sama seperti hardware reset kerana CPU tidak semestinya mengulang set stack/peripheral seperti reset sebenar.

## Hipotesis freeze semasa

Firmware ini mempunyai beberapa exception/fault/default handler yang branch kepada diri sendiri tanpa tamat. Ini termasuk HardFault, MemManage, BusFault, UsageFault, dan beberapa default vector. Jika spike isyarat, laluan overload, keadaan peripheral yang rosak, akses memori tidak sah, atau interrupt tidak dijangka masuk ke handler ini, device boleh kelihatan hang kerana handler tidak pernah return dan tiada laluan recovery yang jelas daripada analisis statik.

Ini sepadan dengan corak simptom yang dilaporkan, tetapi belum membuktikan semua freeze datang daripada CPU fault. Saturation pada laluan bacaan, DMA state loss, display-update blocking, atau parsing protocol masih boleh terlibat.

## Dapatan statik setakat ini

- Tiada literal terus kepada alamat base IWDG `0x40003000` ditemui.
- Tiada literal terus kepada alamat base WWDG `0x40002c00` ditemui.
- `SCB_AIRCR` muncul sebagai literal, tetapi nilai terus `SYSRESETREQ` belum ditemui dalam scan semasa.
- Perkataan 32-bit dalam julat peripheral memberi petunjuk kepada laluan timer, GPIO, CAN, RCC, FLASH, SCB, dan DMA-related, tetapi ini bukti statik dan belum menjadi bukti data-flow penuh.
- Binari mengandungi string ASCII berkaitan device/version termasuk `MT100MM V4.0` dan `BT100MM V4.0`.
- Perbandingan dengan `backup/DM303 V4.0-read only` menunjukkan 68/68 fail adalah byte-for-byte sama dengan folder kerja `DM303-V4.0`.
- Perbandingan dengan `backup/DM303 V3.16-read only` menunjukkan 67 aset bersama adalah byte-for-byte sama; perbezaannya ialah binari firmware utama (`DM303V4.004.bin` berbanding `DM303V316.bin`).
- `backup/SD-file_DM303_update_US240104-read only` ialah set update lain yang lebih kecil. Ia mengandungi `\system\DM30xDB1.dat`, tetapi set V4.0 rasmi dan set V3.16 rasmi tidak mengandungi fail itu.
- Binari merujuk 64 path `\system\...`; hanya `\system\DM30XDB1.dat` hilang daripada folder `DM303-V4.0/system/`.
- Binari dan readme yang dibekalkan merujuk `DM30XDB1.dat`, tetapi `DM303-V4.0/system/DM30XDB1.dat` tidak wujud dalam set V4.0 kerja atau backup V4.0 rasmi. Fail daripada set versi lain tidak boleh disalin masuk ke V4.0 tanpa bukti format, alamat flash, dan compatibility.
- Ada julat kosong berisi `0x00`, tetapi ia tidak boleh dianggap sebagai code cave selamat sehingga pemilikannya dibuktikan. Ia mungkin data table, aset paparan, buffer, atau alignment region.

## Arah naik taraf v4.0.1 beta

1. Kekalkan firmware v4.0 asal byte-identical dan boleh disahkan semula.
2. Bina analisis statik yang boleh dijalankan semula oleh orang lain sebelum patching.
3. Petakan behavior reset/fault/update dan kenal pasti sama ada updater menguatkuasakan checksum, length, atau signing.
4. Selepas itu sahaja, cipta patch generator dan elakkan edit binari secara manual.
5. Calon patch pertama perlu minimal dan berorientasikan recovery, contohnya mengganti fault loop kekal dengan laluan recovery terkawal, hanya jika format update membenarkannya dengan selamat.
6. Perubahan algoritma bacaan perlu tunggu sehingga fungsi acquisition dan RAM buffer dikenal pasti dengan lebih tepat.
7. Teks versi hanya patut berubah kepada `v4.0.1 beta` selepas patch disahkan dan boleh diulang bina.

## Arahan

Pasang dependency analisis:

```powershell
python -m pip install -r tools/requirements-analysis.txt
```

Jalankan analisis dalaman:

```powershell
python tools/dm303_v4_static_analysis.py
```

Bandingkan folder kerja dengan set rasmi tambahan di `backup/`:

```powershell
python tools/dm303_compare_sets.py
```

Skrip ini read-only. Ia tidak menghasilkan firmware yang telah dipatch.
