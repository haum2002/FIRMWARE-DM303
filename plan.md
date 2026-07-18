# PLAN — Kerja Modifikasi Firmware DM303 (V4.0 → v4.0.1-beta)

Dikemas kini: 2026-07-18. Dokumen ini merumuskan pemahaman penuh projek selepas
bacaan menyeluruh (semua kod `tools/`, semua `.md`/`.txt` arahan & bukti),
serta pelan stage-gate untuk kerja modifikasi seterusnya.

---

## 1. Keadaan Terkini (disahkan semula, bukan dianda)

| Item | Nilai | Status |
|---|---|---|
| Baseline rasmi | `backup/DM303 V4.0-read only/DM303V4.004.bin`, SHA-256 `64faaffb…6158`, 203 260 bait, load base `0x08010000` | READ-ONLY, tidak disentuh |
| Calon terkawal semasa | profil `v401h-repair-i`, marker `V4.0.1o`, SHA-256 `11d8f9ba…3953` | DISAHKAN — `dm303_firmware/DM303-V4.0.1-beta/` identik bait-demi-bait dengan `firmware-candidates/v4.0.1h-repair-i/sd-root/` |
| Pakej akhir | 69 fail keseluruhan: firmware + `QBtest.txt` + `readme.txt` + `system/` 66 fail (65 rasmi V4.0 + `DM30XDB1.dat` `846fea60…1fd79`) | Konsisten dengan `CHECKSUMS-SHA256.txt` root |
| Overlay UI/Melayu | `v401h-repair-i-ui-ms`, marker `V4.0.1p`, SHA `a26edd27…8878` | HOLD — tidak diuji sebelum `V4.0.1o` terbukti |
| Calon suis AC/DC | `v401h-repair-j`, marker `V4.0.1q`, SHA `ecd7b5dc…4642` — rasmi + tetingkap suis 600/360→240 sahaja | HOLD — calon measurement paling disokong bukti vendor (perbandingan tiga hala 2026-07-17) |
| Pakej gabungan | `v401h-repair-j-ui-ms`, marker `V4.0.1r`, SHA `e75f8cbd…af8c` — bait measurement repair-j + overlay Melayu/dark V4.0.1p | HOLD — dibina & digatekan 2026-07-18; audit bebas `final-audit-2026-07-18.py` PASS untuk keempat-empat pakej |
| Garis gagal/dikuarantin | `V4.0.1h`/`stability-exp20-ms-safe` (`b9f54dbc…`), `v401h-repair-c` (`70b98735…`), keseluruhan garis V4.0.2 (Qwen: `2fe3d555…`, `4bcd5d3e…` 203261 bait, `47eee60e…`) | DILARANG flash / jangan jadikan asas |

Kandungan patch repair-i berbanding rasmi V4.0 (13 julat diff sahaja, disahkan
`measurement_candidate_gate=ok`):

- Marker versi `0x02ca0`/`0x02cb0` → `MT100MM V4.0.1o` / `BT100MM V4.0.1o`.
- Cap guard state-2 `0x3a98`→`0x05dc`: `0x14b0e`, `0x14b36`, `0x15934`, `0x1595c`,
  `0x1d1a4`, `0x1d1c0` (dua yang terakhir di dalam fungsi skrin ammeter `0x0802d194`).
- Cap gate transition `0x3e80`→`0x0640`: `0x1585e`, `0x15888`; NOP skip-branch
  `0x15812`, `0x15838`, `0x15862`, `0x1588c`.
- Tetingkap akuisisi ammeter `0x1d1da`: `movs r0,#0xf0` (240 sampel) →
  `movs r0,#0x40` (64 sampel) — sasaran blank AC→DC ~30 s pada ~8 sampel/s.
- SEMUA komponen lain rasmi: fault vector, stream/read helper, byte-IO, retry,
  busy gate, relay settle `2/3/10`, UI render, boot-logo, resource system V4.0.

## 2. Peraturan Wajib (dipatuhi untuk sebarang kerja seterusnya)

Daripada `note.txt`, `docs/v401b-no-flash-acceptance-gate-2026-07-15.md`, dan
`VIBE_CODING.md`:

1. Bina HANYA daripada `backup/DM303 V4.0-read only/DM303V4.004.bin`; folder
   `backup/` tidak diubah langsung (rujukan/perbandingan sahaja).
2. Resource UI kekal rasmi sehingga tingkah laku pengukuran diasingkan — tiada
   Melayu/dark theme/logo/boot-delay/gate agresif exp15 dalam baseline pengukuran.
3. Bina calon baharu di bawah `firmware-candidates/` (atau `analysis/`) dahulu —
   JANGAN terus dalam `dm303_firmware/DM303-V4.0.1-beta/`.
4. sd-root HANYA melalui `tools/dm303_build_repair_sdroot.py`; mesti lulus
   `tools/dm303_repair_candidate_check.py` dengan `official_v4_system_resources=match`.
5. Gate wajib sebelum tawar flash: `repair_candidate_check=ok`,
   `measurement_candidate_gate=ok`, `preflash_check=ok` (hantar `--profile`
   eksplisit — default beberapa tool masih `stability-exp20-ms-safe` yang gagal).
6. Sediakan SHA-256, jadual byte-diff, offset diterima/ditolak, dan output
   validasi SEBELUM meminta pengguna mempertimbang flash; status HOLD melainkan
   pengguna terima risiko secara eksplisit.
7. Disiplin bahasa: DILARANG sebut "fixed/stable/successful/safe to flash"
   sebelum ujian device oleh pengguna. Hanya: analysis-only / candidate /
   untested / structurally valid / hold pending acceptance.
8. Perubahan minimum; senaraikan fail terjejas, sebab, risiko, rollback
   (VIBE_CODING §19–§22, §45–§50, §52).

## 3. Rantaian Kerja Standard (profil repair baharu)

1. Takrif profil baharu dalam `PROFILES` di `tools/dm303_v401_beta_patch.py`.
2. Jana calon → `firmware-candidates/v4.0.1h-repair-<x>/`.
3. Daftar hash + peta offset jangkaan dalam `dm303_repair_candidate_check.EXPECTED`
   (dan `EXPECTED_DIFF_RANGES` dalam `dm303_measurement_candidate_gate.py` jika
   profil pengukuran).
4. Bina sd-root: `tools/dm303_build_repair_sdroot.py --candidate-dir … --profile …`.
5. Gate: `dm303_repair_candidate_check.py`, `dm303_measurement_candidate_gate.py`,
   `dm303_preflash_check.py` — ketiga-tiga mesti `=ok`.
6. Dokumen: `PATCH-REPORT.md`, `PACKAGE-REPORT.md`, `SHA256SUMS.txt`,
   `SD-ROOT-SHA256SUMS.txt`; kemas kini `note.txt` + `README.md` root + `plan.md`.
7. Tawarkan kepada pengguna sebagai HOLD + bukti lengkap. Pengguna sahaja yang
   mengesahkan gate device-side.

## 4. Bukti Teknikal Utama (ringkasan)

- Dua masalah berasingan: (a) calit teks — punca resource (`DM30XDB1.dat` hilang;
  layout TEXT_SP 815-lwn-773 salah) — diselesaikan pada tahap resource;
  (b) latency AC→DC ammeter ~30 s / noise / blank — MASIH terbuka.
- Asimetri disahkan data lapangan: DC→AC < 1 s, AC→DC ~30 s.
- Fungsi ammeter `0x0802d194` dipetakan melalui teks UI (entri 27 "AC",
  29 "20A(Kuning)", 30 "mA(Hijau)"); memanggil selector relay `0x0801f0f2`
  dan mode/range `0x0801f19a`.
- Siri patch stream/state exp11–exp16 dibuktikan TIDAK berkesan di device —
  tidak dibawa ke repair-i.
- Tiada literal ADC1/2/3 dalam mana-mana image → patch ADC/RMS/True RMS adalah
  spekulatif; DILARANG tanpa hook yang disahkan (`v401b-next-patch-decision.md`).
- Hipotesis berbaki: guard/window timing ammeter (sedang diuji repair-i),
  settling relay/mux fizikal, leakage laluan hijau (fuse self-recovery 0.5 A,
  maks 200 mA), kalibrasi dalam SPI flash luar `25VQ64CSIG` (di luar `.bin`).
- MCU: Nation N32G45x/N32G455; kristal 8 MHz + 32.768 kHz; relay HF 4.5 V
  berbilang; laluan arus hijau berasingan dan terlindung.

## 5. Pilihan Langkah Seterusnya (menanti keputusan pengguna)

> Bergantung pada maklum balas medan `V4.0.1o` (repair-i) — gate device-side
> hanya boleh disahkan oleh pengguna. Tiada binaan baharu dimulakan sebelum
> arahan eksplisit.

- **A. Jika `V4.0.1o` latency baik tetapi noise meningkat** → tala semula
  tetingkap `0x1d1da` ke `0x80`/`0xc0` sebagai `v401h-repair-j` (HOLD).
- **B. Jika `V4.0.1o` tiada perubahan** → revert `0x1d1da`, jejak lebih dalam:
  protocol trace laluan stream `0x080196b2` (hanya 2 pemanggil), pengesahan
  fungsi calon float (`0x0802600c`, `0x08029f94`, `0x08032dba`, `0x080324fc`),
  buru data kalibrasi dalam SPI flash `25VQ64CSIG`.
- **C. Jika `V4.0.1o` terbukti bersih (calit hilang, latency selesai)** → barulah
  pertimbang promosi overlay `v401h-repair-i-ui-ms` (`V4.0.1p`) untuk keperluan
  UI Melayu/dark, melalui gate overlay (`ui_overlay_candidate_check=ok`).
- **D. Kerja housekeeping berisiko rendah (docs sahaja, tiada patch)**: label
  semula garis V4.0.2 sebagai UNSAFE/QUARANTINE dalam `dm303_firmware/`
  (README-UNSAFE.md dipadam dari working tree); kemas kini dokumen lapuk
  (`beginner-flash-notes.md`, `firmware-candidates/v4.0.1-beta/README.md`,
  `localization/ms_MY/README.md`); tandai `analysis/…/tmp-build/` sebagai
  KARANTINA. Perlu persetujuan pengguna kerana ia mengubah fail.
- **E. Data yang pengguna boleh kumpul untuk membuka langkah seterusnya**:
  ≥50 kitaran DC→AC→DC ammeter hijau (catat blank_events, masa recovery, ikon
  bateri), ≥2 nilai rujukan setiap mod, noise input short lwn open, voltan rail
  semasa klik relay.

## 6. Percanggahan Dokumen Dikesan (untuk pengetahuan)

1. Angka "69 fail system" dalam note.txt tidak tepat: `system/` = 66 fail
   (65 rasmi + DM30XDB1.dat); 69 = jumlah keseluruhan pakej.
2. `docs/beginner-flash-notes.md` masih merujuk `V4.0.1h` sebagai semasa — LAPU.
3. `analysis/v401b-profile-matrix/tmp-build/` mementaskan binari karantina
   exp20 (`b9f54dbc…`) — risiko salah ambil.
4. Default `--profile` pada `dm303_preflash_check.py` / `dm303_validate_final_package.py`
   / `dm303_merge_final_package.py` masih `stability-exp20-ms-safe` — sentiasa
   hantar profil eksplisit.
5. Tiga binari V4.0.2 berbeza wujud tanpa PATCH-REPORT terkawal; folder
   `DM303-V4.0.2-beta-FINAL` mendakwa "SAFE TO FLASH" tanpa bukti — kuarantin.
6. `localization/ms_MY/README.md` tidak merekodkan `TEXT_SP.safe-slot-replacement.*`
   (varian 137-entri, 31 787 B, `96bde6bc…`).
