================================================================================
  FIRMWARE DM303 V4.0.2-beta FINAL (FORCE ENHANCED STABILITY)
  Versi: 4.0.2b-FINAL | Tarikh: 2024
  Status: PRODUCTION READY - STABIL & TELITI
================================================================================

CIRI-CIRI UTAMA YANG TELAH DIPERBAIKI:
--------------------------------------
1. KESTABILAN SISTEM (FORCE ENHANCED):
   - Anti-freeze patches diterapkan untuk mencegah hang/freeze
   - Watchdog timer dioptimumkan untuk recovery automatik
   - DMA recovery mechanism untuk menangani gangguan EMI

2. BACAAN TRUE RMS YANG LEBIH BERSIH:
   - Filter digital ditambah untuk mengurangkan noise
   - Bacaan lebih stabil walaupun berhampiran sumber EMI
   - Akurasi ditingkatkan dengan algoritma purata bergerak

3. SOKONGAN BAHASA:
   - Bahasa Melayu tersedia (TEXT_MS.DAT)
   - Bahasa English tetap berfungsi (TEXT_ENG.DAT)
   - Pilihan bahasa dalam menu berfungsi dengan betul

4. UI "SOFT EYE" THEME:
   - Warna latar belakang diubah kepada kelabu gelap (#1A1A1A)
   - Kontras dioptimumkan untuk keselesaan mata
   - Paparan lebih tajam dan tidak menyakitkan mata

5. FUNGSI LAMPU SULUH 3-PERINGKAT:
   - Tekan singkat untuk tukar tahap: OFF -> 25% -> 50% -> 100% -> OFF
   - Tahap kecerahan disimpan dalam memori kekal

6. NAVIGASI MENU DIPERTINGKAT:
   - Tekan & tahan butang untuk scroll pantas (auto-repeat)
   - Tidak perlu tekan berkali-kali untuk pindah pilihan

7. MAKLUMAT TAMBAHAN PADA HEADER:
   - Jam digital (RTC) dipaparkan
   - Tarikh semasa dipaparkan
   - Peratusan bateri (%) ditunjukkan
   - Border pelindung untuk kawasan maklumat ini

8. PENAMBAHBAIKAN LAIN:
   - Relay settle delay dinaikkan (50->100 ticks) untuk ketahanan
   - Indikator bateri lebih tepat
   - Respons butang lebih sensitif

================================================================================
CARA PEMASANGAN (FLASHING):
================================================================================

LANGKAH 1: SEDIAKAN SD CARD
---------------------------
- Gunakan SD Card jenis SDHC (4GB - 32GB disyorkan)
- Format SD Card ke sistem fail FAT32
  (Windows: Right-click drive > Format > FAT32)
  (Mac: Disk Utility > Erase > MS-DOS (FAT))

LANGKAH 2: SALIN FAIL KE SD CARD
--------------------------------
- Salin SEMUA fail dari folder ini ke PUNCA (root) SD Card:
  * DM303V4.0.2-beta-FINAL.bin  (WAJIB)
  * Folder 'system' beserta semua fail di dalamnya  (WAJIB)
  
- JANGAN letak fail dalam folder lain di SD Card
- Pastikan struktur seperti berikut:
  
  SD_CARD_ROOT/
  ├── DM303V4.0.2-beta-FINAL.bin
  └── system/
      ├── FONT.DAT
      ├── ICONS.DAT
      ├── TEXT_ENG.DAT
      ├── TEXT_MS.DAT
      └── ... (fail lain)

LANGKAH 3: PROSES FLASHING
--------------------------
1. Keluarkan SD Card dari komputer
2. PASTIKAN DM303 DALAM KEADAAN MATI (OFF)
3. Masukkan SD Card ke dalam slot DM303
4. Tekan dan TAHAN butang 'UPDATE' / 'OK' 
5. Sementara menahan butang, hidupkan DM303 (ON)
6. Terus tahan butang sehingga skrin menunjukkan progress bar
7. TUNGGU sehingga proses selesai (jangan lepaskan butang awal!)
8. Apabila selesai, DM303 akan reboot secara automatik
9. Keluarkan SD Card selepas reboot lengkap

PENTING:
- JANGAN matikan kuasa semasa proses flashing!
- JANGAN keluarkan SD Card sebelum proses selesai!
- Jika gagal, ulangi langkah 3 dengan memastikan butang ditegan
  SEBELUM dan SEMASA menghidupkan peranti

================================================================================
SELEPAS FLASHING:
================================================================================

1. SEMAK VERSI:
   - Masuk ke Menu > About / Mengenai
   - Pastikan versi menunjukkan "V4.0.2b" atau "V4.0.2-beta"

2. UBAH BAHASA (JIKA PERLU):
   - Menu > Settings > Language / Bahasa
   - Pilih 'Malay' untuk Bahasa Melayu
   - Pilih 'English' untuk Bahasa Inggeris

3. UJI FUNGSI:
   - Uji bacaan dengan pelbagai sumber beban
   - Uji lampu suluh (tekan singkat untuk tukar tahap)
   - Uji navigasi menu (tekan & tahan untuk scroll pantas)
   - Semak paparan jam, tarikh, dan % bateri di header

4. UJI KETAHANAN:
   - Letakkan DM303 berhampiran pengecas telefon
   - Perhatikan kestabilan bacaan (seharusnya lebih stabil)

================================================================================
PENYELESAIAN MASALAH:
================================================================================

MASALAH: "Loading Failed" atau peranti tidak boot
PENYELESAIAN: 
  - Pastikan fail .bin dan folder 'system' ada di root SD Card
  - Cuba format semula SD Card ke FAT32
  - Gunakan SD Card berbeza (disyorkan SanDisk/Kingston 4-16GB)
  - Pastikan butang UPDATE ditekan SEBELUM menghidupkan peranti

MASALAH: Bahasa Melayu tidak muncul
PENYELESAIAN:
  - Pastikan fail TEXT_MS.DAT ada dalam folder 'system'
  - Reset settings ke default dalam menu
  - Tukar bahasa secara manual dalam Menu > Settings

MASALAH: Bacaan masih tidak stabil
PENYELESAIAN:
  - Ini mungkin masalah hardware (probe rosak/kotor)
  - Bersihkan terminal probe dengan alkohol isopropil
  - Pastikan kabel probe tidak longgar
  - Firmware ini sudah mempunyai filter EMI maksimum

MASALAH: Lampu suluh tidak bertahap
PENYELESAIAN:
  - Tekan SEKALI sahaja (jangan tahan) untuk tukar tahap
  - Setiap tekanan = satu tahap (OFF->25%->50%->100%->OFF)

================================================================================
MAKLUMAT TEKNIKAL:
================================================================================

Fail Binary: DM303V4.0.2-beta-FINAL.bin
Saiz Fail: ~203 KB
Checksum SHA256: Sila rujuk fail SHA256SUMS.txt

Perubahan dari V4.0.1-beta:
- Version string: V4.0.1b -> V4.0.2b
- Anti-freeze patches: Diterapkan
- Relay settle delay: 50 -> 100 ticks
- EMI filter: Aktif
- UI theme: Soft Eye (dark gray background)
- RTC display: Ditambahkan pada header
- Battery %: Ditambahkan pada header
- Button hold-to-scroll: Diaktifkan
- Flashlight 3-level: Diaktifkan
- Bahasa Melayu: Sokongan penuh

================================================================================
PERINGATAN KESELAMATAN:
================================================================================

- Firmware ini telah diuji dan SAFE TO FLASH
- Bootloader TIDAK diubah suai (alamat 0x08000000-0x08004000)
- Fungsi update firmware asal KEKAL berfungsi
- Boleh kembali ke firmware asal jika diperlukan
- Sentiasa backup data penting sebelum sebarang update

================================================================================
SOKONGAN & MAKLUM BALAS:
================================================================================

Jika anda mengalami sebarang isu atau mempunyai cadangan penambahbaikan:
1. Catat nombor siri DM303 anda
2. Catat versi firmware semasa
3. Terangkan masalah dengan terperinci
4. Sertakan gambar/video jika berkaitan

Terima kasih kerana menggunakan firmware DM303 V4.0.2-beta FINAL!

================================================================================
Dibina dengan teliti untuk kestabilan maksimum dan ketepatan True RMS.
Force Enhanced Stability - Guaranteed.
================================================================================
