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

Patch `v4.0.1 beta` menukar laluan tersebut daripada self-loop kekal kepada
permintaan hardware reset melalui `SCB_AIRCR`. Ini mengurangkan risiko freeze
kekal pada exception/default IRQ, tetapi ia belum membetulkan semua kemungkinan
punca bacaan tidak stabil seperti DMA/state acquisition, filtering, atau
display-update blocking.

## Perubahan firmware candidate

Firmware candidate berada di:

```text
firmware-candidates/v4.0.1-beta/DM303V4.0.1-beta.bin
```

Perubahan yang dibuat:

- Saiz binari kekal `203260` bytes.
- 56 vector exception/default yang sebelum ini menuju ke self-loop `FE E7`
  kini menuju ke satu stub recovery di `0x08017554`.
- Stub recovery menulis `0x05FA0004` ke `SCB_AIRCR` (`0xE000ED0C`) untuk
  meminta hardware reset.
- Tiada vector target yang masih menunjuk ke self-loop handler selepas patch.
- String versi di offset `0x02ca0` dan `0x02cb0` ditukar kepada
  `V4.0.1 beta`.
- Bootloader/updater dan prosedur SD upgrade tidak dipatch.

Hash candidate:

```text
8ba7a3bc14ad30485d12b6fa4c7acb5c18dbb3dd29d2eda34fa32d83f6a2daf8  DM303V4.0.1-beta.bin
```

## Bahasa Melayu UI

Format `TEXT_*.DAT` telah diparse dan boleh dibina semula byte-identical.
Setiap entri mempunyai record panjang 2-byte dan jadual offset di awal fail.

Resource Bahasa Melayu:

- Source binaan: `backup/DM303 V4.0-read only/system/TEXT_EN.DAT`
- Candidate: `localization/ms_MY/TEXT_MS.DAT`
- Staging: `firmware-candidates/v4.0.1-beta/system/TEXT_MS.DAT`
- Final: `DM303-V4.0.1-beta/system/TEXT_MS.DAT`

Validasi semasa:

- 815 entri boleh diparse.
- 781 entri diterjemah atau diwrap semula.
- `TEXT_MS.DAT` boleh rebuild byte-identical.
- Tiada aksara bukan ASCII untuk mengurangkan risiko font/rendering.
- SHA-256: `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd`

Bahasa Melayu ditambah sebagai resource baru. Aktivasi menu Bahasa Melayu
secara add-only belum dipatch kerana jadual nama bahasa hardcoded sekitar
`0x08035be4` belum mempunyai spare slot yang disahkan. Mengganti slot bahasa
sedia ada lebih mudah, tetapi itu bukan arahan yang diminta.

## Pakej akhir

Skrip gabungan:

```powershell
python tools/dm303_merge_final_package.py
```

Peraturan gabungan:

- `backup/` dibaca sahaja dan tidak diubah.
- `firmware-candidates/v4.0.1-beta/` menjadi input staging.
- `DM303-V4.0.1-beta/` dibina semula bersih daripada rujukan V4.0 rasmi.
- `DM303V4.004.bin` asal dibuang daripada folder akhir.
- `DM303V4.0.1-beta.bin` dimasukkan sebagai firmware utama.
- `system/TEXT_MS.DAT` dimasukkan sebagai resource Bahasa Melayu tambahan.
- Nested tree tidak sah seperti `system/system/` ditolak.

Laporan akhir:

- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-REPORT.md`
- `firmware-candidates/v4.0.1-beta/FINAL-PACKAGE-SHA256.txt`
- `CHECKSUMS-SHA256.txt`

## Dapatan set fail

- Perbandingan dengan `backup/DM303 V4.0-read only` mengesahkan set final
  dibina daripada rujukan V4.0 rasmi, dengan binari utama diganti oleh
  candidate dan `TEXT_MS.DAT` ditambah.
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
python tools/dm303_text_resource.py --input DM303-V4.0.1-beta/system/TEXT_MS.DAT --verify-rebuild
```
