# FIRMWARE-DM303

Arkib komuniti untuk snapshot firmware AUTool DM303 V4.0.

Vendor telah menyatakan bahawa peranti ini tidak lagi menerima sokongan
kemas kini firmware rasmi. Repo ini menyimpan salinan asal supaya analisis,
backup, dan kerja naik taraf komuniti boleh dibuat secara telus tanpa
menimpa baseline firmware.

## Kandungan

- `DM303-V4.0/DM303V4.004.bin` - firmware utama.
- `DM303-V4.0/system/` - aset sistem seperti font, ikon, logo, dan fail teks bahasa.
- `CHECKSUMS-SHA256.txt` - hash SHA-256 untuk semua fail dalam snapshot ini.

Folder `DM303-V4.0/` ditandakan sebagai binari dalam `.gitattributes` supaya
Git tidak menukar byte asal firmware semasa checkout atau commit.

SHA-256 firmware utama:

```text
64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158  DM303-V4.0/DM303V4.004.bin
```

## Nota keselamatan

- Jangan flash firmware yang telah diubah tanpa checksum, changelog, dan ujian
  pada unit yang sanggup menanggung risiko.
- Simpan salinan firmware asal daripada peranti sendiri jika boleh.
- Buat kerja eksperimen pada branch berasingan supaya snapshot asal kekal bersih.
- Catat versi hardware, kaedah flash, dan pilihan recovery sebelum mencuba naik taraf.

## Kerja naik taraf

Analisis upgrade dalaman bermula di [docs/upgrade-analysis.md](docs/upgrade-analysis.md).
Skrip awal yang digunakan adalah read-only dan tidak menghasilkan firmware
flashable: [tools/dm303_v4_static_analysis.py](tools/dm303_v4_static_analysis.py).

Calon resource Bahasa Melayu UI berada di `localization/ms_MY/`. Ia belum
diintegrasi ke firmware dan tidak boleh dianggap sebagai update flashable.
