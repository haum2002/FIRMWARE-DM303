# VIBE CODING MASTER PLAYBOOK

> Panduan operasi lengkap untuk membina aplikasi, laman web, sistem terbenam, automasi, API, alat dalaman, dan produk perisian dengan bantuan AI secara tersusun, boleh diuji, selamat, dan sesuai dikembangkan.

---

## 0. Tujuan Dokumen

Dokumen ini berfungsi sebagai:

1. Panduan utama pembangunan berasaskan Vibe Coding.
2. Arahan kerja untuk AI coding assistant.
3. Standard projek supaya kod tidak dibina secara rawak.
4. Sistem kawalan kualiti, keselamatan, ujian, dokumentasi, dan deployment.
5. Templat yang boleh terus disalin ke dalam projek sebenar.
6. Rujukan untuk pengguna baru yang belum mahir menulis kod.
7. Asas untuk projek kecil sehingga sistem produksi.

Dokumen ini boleh disimpan sebagai:

```text
VIBE_CODING.md
```

Fail tambahan yang disyorkan:

```text
README.md
PROJECT_SPEC.md
ARCHITECTURE.md
TASKS.md
DECISIONS.md
CHANGELOG.md
SECURITY.md
TEST_PLAN.md
DEPLOYMENT.md
.env.example
.gitignore
```

---

# 1. Definisi Vibe Coding

Vibe Coding ialah proses pembangunan perisian dengan memberi arahan bahasa biasa kepada AI, kemudian AI membantu:

- Merancang sistem.
- Membina kod.
- Menerangkan kod.
- Mengesan ralat.
- Menambah fungsi.
- Menulis ujian.
- Menyusun dokumentasi.
- Melakukan refactor.
- Menyediakan deployment.
- Menilai risiko teknikal.

Vibe Coding yang betul bukan sekadar meminta:

```text
Bina aplikasi ini.
```

Sebaliknya, Vibe Coding profesional menggunakan:

```text
Keperluan jelas
+ konteks projek
+ batasan teknikal
+ kriteria penerimaan
+ proses semakan
+ ujian
+ dokumentasi
+ kawalan perubahan
```

Formula asas:

```text
Idea
→ Spesifikasi
→ Seni bina
→ Pecahan tugas
→ Implementasi
→ Ujian
→ Semakan
→ Deployment
→ Pemantauan
→ Penambahbaikan
```

---

# 2. Prinsip Utama

## 2.1 Jangan Terus Menulis Kod Tanpa Spesifikasi

Sebelum kod dibina, pastikan perkara berikut jelas:

- Apa masalah yang hendak diselesaikan.
- Siapa pengguna.
- Platform sasaran.
- Bahasa pengaturcaraan.
- Framework.
- Database.
- Kaedah login.
- Cara data disimpan.
- Cara sistem berkomunikasi.
- Keperluan keselamatan.
- Keperluan prestasi.
- Kriteria siap.

## 2.2 Pecahkan Projek Besar Menjadi Modul Kecil

Jangan minta AI membina keseluruhan sistem dalam satu arahan.

Gunakan struktur:

```text
Fasa 1: Asas projek
Fasa 2: Database
Fasa 3: Authentication
Fasa 4: Fungsi utama
Fasa 5: Antara muka
Fasa 6: Ujian
Fasa 7: Deployment
```

## 2.3 Setiap Perubahan Mesti Boleh Diuji

Setiap fungsi perlu mempunyai:

- Input.
- Output.
- Keadaan normal.
- Keadaan ralat.
- Had penggunaan.
- Ujian automatik atau langkah ujian manual.

## 2.4 Jangan Benarkan AI Mengubah Fail Tanpa Kawalan

AI mesti:

- Menyenaraikan fail yang akan diubah.
- Menerangkan sebab perubahan.
- Mengelakkan perubahan tidak berkaitan.
- Menjaga fungsi sedia ada.
- Menunjukkan kesan sampingan.
- Menyediakan rollback jika perubahan besar.

## 2.5 Kod Mesti Boleh Dibaca Manusia

Kod yang baik mesti:

- Nama pemboleh ubah jelas.
- Fungsi kecil dan fokus.
- Tiada pengulangan tidak perlu.
- Tiada nilai rahsia di dalam kod.
- Ada pengendalian ralat.
- Ada log yang berguna.
- Ada komen untuk bahagian kompleks.
- Ada dokumentasi penggunaan.

---

# 3. Peranan AI dalam Projek

AI boleh bertindak sebagai:

```text
Product Manager
System Architect
UI/UX Designer
Frontend Developer
Backend Developer
Database Engineer
DevOps Engineer
Security Reviewer
QA Engineer
Technical Writer
Code Reviewer
Debugger
Release Manager
```

Namun AI tidak boleh dianggap sentiasa betul.

Setiap output AI perlu melalui:

```text
Semak
→ Jalankan
→ Uji
→ Periksa log
→ Bandingkan hasil
→ Betulkan
```

---

# 4. Maklumat Projek yang Wajib Diberikan

Gunakan blok ini sebelum memulakan projek.

```md
## Project Identity

Project Name:
Project Type:
Target Users:
Primary Goal:
Problem Being Solved:

## Platform

Target Platform:
- Web
- Android
- iOS
- Windows
- macOS
- Linux
- Embedded
- ESP32
- STM32
- Raspberry Pi
- Other

## Technology

Frontend:
Backend:
Database:
Authentication:
Hosting:
Communication Protocol:
Testing Framework:
Build System:
Package Manager:

## Constraints

Budget:
Hardware Limits:
Memory Limits:
CPU Limits:
Storage Limits:
Internet Requirement:
Offline Requirement:
Security Requirement:
Performance Requirement:
Deadline:

## Definition of Done

- [ ] Main function works
- [ ] Error handling completed
- [ ] Tests pass
- [ ] Documentation completed
- [ ] No secrets committed
- [ ] Deployment verified
- [ ] Rollback plan available
```

---

# 5. Struktur Fail Projek yang Disyorkan

## 5.1 Projek Web Moden

```text
project-root/
├── apps/
│   ├── web/
│   └── api/
├── packages/
│   ├── ui/
│   ├── config/
│   ├── types/
│   └── shared/
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DATABASE.md
│   ├── SECURITY.md
│   └── DEPLOYMENT.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/
├── .env.example
├── .gitignore
├── README.md
├── PROJECT_SPEC.md
├── TASKS.md
├── CHANGELOG.md
└── package.json
```

## 5.2 Projek Python

```text
project-root/
├── src/
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── services/
│       ├── models/
│       ├── repositories/
│       └── utils/
├── tests/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

## 5.3 Projek ESP32 / STM32

```text
project-root/
├── firmware/
│   ├── src/
│   ├── include/
│   ├── drivers/
│   ├── middleware/
│   ├── application/
│   ├── config/
│   └── tests/
├── hardware/
│   ├── schematic/
│   ├── pcb/
│   ├── bom/
│   └── datasheets/
├── tools/
├── docs/
│   ├── PINOUT.md
│   ├── PROTOCOL.md
│   ├── SAFETY.md
│   └── FLASHING.md
├── platformio.ini
├── README.md
└── CHANGELOG.md
```

---

# 6. Fail Arahan AI Projek

Cipta fail:

```text
AI_INSTRUCTIONS.md
```

Isi yang disyorkan:

```md
# AI Project Instructions

## General Rules

1. Read all project documentation before modifying code.
2. Do not invent requirements.
3. Do not remove existing functionality unless explicitly requested.
4. Keep changes limited to the requested scope.
5. Explain assumptions.
6. Ask for missing critical data only when implementation cannot proceed safely.
7. Prefer simple and maintainable solutions.
8. Do not hard-code secrets.
9. Add error handling.
10. Add or update tests.
11. Update documentation when behavior changes.
12. Preserve backward compatibility unless explicitly approved.
13. Show affected files before making major changes.
14. Avoid unnecessary dependencies.
15. Do not rewrite the whole project for a small fix.

## Code Quality

- Use clear naming.
- Keep functions small.
- Avoid duplicated logic.
- Validate all external input.
- Use typed interfaces where supported.
- Log important failures.
- Fail safely.
- Use configuration files or environment variables.
- Add comments only where logic is not obvious.

## Output Format

For every task, return:

1. Summary
2. Assumptions
3. Files changed
4. Implementation
5. Tests added
6. How to run
7. Risks
8. Rollback instructions
```

---

# 7. Master Prompt untuk Memulakan Projek

Salin dan ubah bahagian dalam kurungan.

```text
Anda bertindak sebagai pasukan pembangunan perisian lengkap yang terdiri daripada
system architect, senior developer, QA engineer, security reviewer, DevOps engineer,
dan technical writer.

Saya mahu membina:

[NAMA DAN TUJUAN PROJEK]

Pengguna sasaran:

[JENIS PENGGUNA]

Platform:

[WEB / ANDROID / IOS / WINDOWS / ESP32 / STM32 / LAIN-LAIN]

Teknologi pilihan:

[NYATAKAN ATAU MINTA AI CADANGKAN]

Fungsi utama:

1. [FUNGSI 1]
2. [FUNGSI 2]
3. [FUNGSI 3]

Keperluan penting:

- Sistem mesti modular.
- Kod mesti mudah dibaca.
- Semua input mesti divalidasi.
- Semua ralat mesti dikendalikan.
- Rahsia tidak boleh dimasukkan dalam kod.
- Sediakan ujian.
- Sediakan dokumentasi.
- Elakkan dependency tidak perlu.
- Jangan bina fungsi yang tidak diminta.
- Jangan ubah struktur tanpa sebab jelas.

Sebelum menulis kod:

1. Terangkan pemahaman projek.
2. Senaraikan andaian.
3. Cadangkan seni bina.
4. Cadangkan struktur folder.
5. Pecahkan projek kepada fasa.
6. Senaraikan risiko teknikal.
7. Tetapkan kriteria penerimaan.
8. Selepas itu barulah bina Fasa 1 sahaja.

Untuk setiap perubahan, berikan:

- Fail terlibat.
- Kod lengkap.
- Arahan pemasangan.
- Arahan menjalankan.
- Cara menguji.
- Hasil yang dijangka.
- Cara rollback.
```

---

# 8. Prompt untuk Menyambung Projek Sedia Ada

```text
Baca dan fahami keseluruhan projek sebelum membuat perubahan.

Tugas:

[NYATAKAN PERUBAHAN]

Peraturan:

1. Jangan ubah fungsi yang tidak berkaitan.
2. Jangan membuang kod sedia ada tanpa sebab.
3. Kekalkan compatibility.
4. Senaraikan fail yang akan diubah.
5. Terangkan punca sebenar masalah.
6. Sediakan patch minimum.
7. Tambah atau kemas kini ujian.
8. Kemas kini dokumentasi jika tingkah laku berubah.
9. Nyatakan risiko regresi.
10. Berikan arahan rollback.

Sebelum memberikan kod, tampilkan:

- Pemahaman tugas.
- Punca masalah.
- Pelan perubahan.
- Fail terlibat.
- Kriteria kejayaan.
```

---

# 9. Prompt Debugging Profesional

```text
Bertindak sebagai senior debugging engineer.

Masalah:

[TERANGKAN MASALAH]

Jangkaan:

[HASIL YANG SEPATUTNYA]

Hasil sebenar:

[HASIL YANG BERLAKU]

Log ralat:

[TAMPAL LOG]

Kod berkaitan:

[TAMPAL KOD ATAU FAIL]

Persekitaran:

- OS:
- Runtime:
- Framework:
- Versi dependency:
- Hardware:
- Cara menjalankan:

Lakukan proses berikut:

1. Bezakan simptom dan punca.
2. Senaraikan 3 hingga 5 kemungkinan punca.
3. Susun mengikut kebarangkalian.
4. Nyatakan cara mengesahkan setiap punca.
5. Cadangkan pembetulan minimum.
6. Jangan ubah bahagian tidak berkaitan.
7. Sediakan kod pembetulan lengkap.
8. Tambah ujian regresi.
9. Berikan langkah pengesahan.
10. Nyatakan perkara yang masih belum pasti.
```

---

# 10. Prompt Refactor

```text
Refactor kod berikut tanpa mengubah output atau tingkah laku luaran.

Matlamat:

- Kurangkan pengulangan.
- Tingkatkan kebolehbacaan.
- Pecahkan fungsi terlalu panjang.
- Tambah type safety.
- Tingkatkan error handling.
- Kekalkan API sedia ada.
- Elakkan dependency baru.
- Pastikan semua ujian lama masih lulus.

Sebelum refactor:

1. Terangkan masalah struktur kod.
2. Kenal pasti code smell.
3. Nyatakan risiko perubahan.
4. Cadangkan pelan refactor bertahap.

Selepas refactor:

1. Paparkan perbezaan utama.
2. Senaraikan fail berubah.
3. Sediakan ujian.
4. Nyatakan cara rollback.
```

---

# 11. Prompt Code Review

```text
Lakukan code review menyeluruh terhadap kod berikut.

Semak:

- Ketepatan logik.
- Bug tersembunyi.
- Race condition.
- Memory leak.
- Null handling.
- Input validation.
- Authentication.
- Authorization.
- Injection.
- XSS.
- CSRF.
- Path traversal.
- Data exposure.
- Secret leakage.
- Error handling.
- Logging.
- Prestasi.
- Kebolehskalaan.
- Maintainability.
- Test coverage.
- Dependency risk.

Klasifikasikan setiap penemuan sebagai:

- Critical
- High
- Medium
- Low
- Improvement

Untuk setiap penemuan berikan:

1. Lokasi.
2. Masalah.
3. Kesan.
4. Cara mencetuskan.
5. Cara membaiki.
6. Kod pembetulan.
7. Ujian yang perlu ditambah.
```

---

# 12. Prompt Menjana Ujian

```text
Bina ujian lengkap untuk modul berikut.

Wajib meliputi:

- Happy path.
- Input kosong.
- Input salah.
- Nilai minimum.
- Nilai maksimum.
- Nilai luar julat.
- Timeout.
- Dependency gagal.
- Database gagal.
- Network gagal.
- Unauthorized access.
- Duplicate request.
- Concurrent request.
- Recovery selepas gagal.

Jenis ujian:

- Unit test.
- Integration test.
- End-to-end test jika berkaitan.
- Regression test.

Pastikan:

- Ujian deterministik.
- Tidak bergantung pada masa sebenar tanpa mocking.
- Tidak bergantung pada servis luaran tanpa mocking.
- Nama ujian jelas.
- Setiap ujian menerangkan tingkah laku.
```

---

# 13. Prompt UI/UX

```text
Bina UI berdasarkan keperluan berikut:

Jenis aplikasi:
[WEB / MOBILE / DESKTOP / EMBEDDED DISPLAY]

Pengguna:
[JENIS PENGGUNA]

Matlamat skrin:
[TUJUAN]

Elemen wajib:
[SENARAI]

Keperluan:

- Responsive.
- Accessible.
- Keyboard navigation.
- Loading state.
- Empty state.
- Error state.
- Success state.
- Disabled state.
- Confirmation untuk tindakan berisiko.
- Borang mempunyai validasi.
- Mesej ralat jelas.
- Tidak menggunakan animasi berlebihan.
- Prestasi baik pada peranti rendah.
- Komponen boleh digunakan semula.

Sediakan:

1. Struktur komponen.
2. State model.
3. Data flow.
4. Kod lengkap.
5. Mock data.
6. Ujian komponen.
7. Ujian accessibility.
```

---

# 14. Prompt Backend/API

```text
Bina API produksi untuk fungsi berikut:

[FUNGSI]

Keperluan:

- REST atau GraphQL berdasarkan kesesuaian.
- Input validation.
- Authentication.
- Authorization.
- Rate limiting.
- Idempotency untuk operasi kritikal.
- Structured logging.
- Error response standard.
- Database transaction.
- Pagination.
- Filtering.
- Sorting.
- Audit trail.
- Health endpoint.
- Metrics.
- API versioning.
- OpenAPI documentation.
- Unit test.
- Integration test.

Format ralat standard:

{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {},
    "requestId": "unique-id"
  }
}
```

---

# 15. Prompt Database

```text
Reka bentuk database untuk sistem berikut:

[SISTEM]

Keperluan:

1. Senaraikan entiti.
2. Terangkan hubungan.
3. Tentukan primary key.
4. Tentukan foreign key.
5. Tentukan index.
6. Tentukan unique constraint.
7. Tentukan nullable field.
8. Tentukan audit fields.
9. Sediakan migration.
10. Sediakan rollback migration.
11. Elakkan data duplication.
12. Jelaskan trade-off normalization.
13. Pertimbangkan query paling kerap.
14. Pertimbangkan pertumbuhan data.
15. Sediakan sample data.
16. Sediakan backup dan restore strategy.
```

---

# 16. Prompt Keselamatan

```text
Lakukan security hardening untuk projek ini.

Semak dan baiki:

- Authentication.
- Authorization.
- Session management.
- Password storage.
- Token storage.
- Secret management.
- Input validation.
- Output encoding.
- SQL injection.
- Command injection.
- XSS.
- CSRF.
- SSRF.
- File upload.
- Path traversal.
- Rate limiting.
- Brute force.
- Logging sensitif.
- Dependency vulnerability.
- CORS.
- CSP.
- Secure headers.
- Encryption in transit.
- Encryption at rest.
- Backup security.
- Audit logging.
- Least privilege.
- Default credentials.
- Debug mode.
- Error leakage.

Sediakan:

1. Senarai risiko.
2. Severity.
3. Bukti atau lokasi.
4. Pembetulan.
5. Kod.
6. Konfigurasi.
7. Ujian keselamatan.
8. Checklist deployment.
```

---

# 17. Prompt Projek Mikropengawal

```text
Bertindak sebagai embedded systems architect dan firmware engineer.

MCU:
[ESP32 / STM32 / ARDUINO / RASPBERRY PI PICO / LAIN-LAIN]

Fungsi:
[FUNGSI]

Periferal:
- GPIO:
- ADC:
- PWM:
- I2C:
- SPI:
- UART:
- CAN:
- Wi-Fi:
- Bluetooth:

Had:
- RAM:
- Flash:
- CPU:
- Voltage:
- Current:
- Timing:
- Temperature:
- Real-time requirement:

Keperluan firmware:

- Non-blocking.
- Watchdog.
- Brownout handling.
- Safe boot.
- Failsafe state.
- Input filtering.
- Debouncing.
- Timeout.
- Sensor fault detection.
- Communication CRC.
- Persistent config validation.
- Firmware versioning.
- OTA jika sesuai.
- Rollback firmware.
- Logging.
- Test mode.
- Hardware abstraction layer.
- State machine.
- No dynamic allocation jika tidak perlu.

Sebelum kod:

1. Cadangkan seni bina firmware.
2. Bentuk state machine.
3. Bentuk task/thread.
4. Bentuk timing budget.
5. Bentuk fault model.
6. Bentuk pin mapping.
7. Bentuk protokol.
8. Bentuk test plan.
```

---

# 18. Aliran Kerja Vibe Coding Profesional

## Fasa 1: Discovery

Hasil wajib:

```text
PROJECT_SPEC.md
```

Kandungan:

- Masalah.
- Pengguna.
- Fungsi.
- Had.
- Keutamaan.
- Kriteria siap.

## Fasa 2: Architecture

Hasil wajib:

```text
ARCHITECTURE.md
```

Kandungan:

- Komponen.
- Data flow.
- API.
- Database.
- Security boundary.
- Failure mode.
- Deployment model.

## Fasa 3: Task Breakdown

Hasil wajib:

```text
TASKS.md
```

Contoh:

```md
# Tasks

## Phase 1: Foundation

- [ ] Initialize repository
- [ ] Add formatter
- [ ] Add linter
- [ ] Add test framework
- [ ] Add environment configuration
- [ ] Add CI

## Phase 2: Core

- [ ] Add domain model
- [ ] Add database
- [ ] Add service layer
- [ ] Add API

## Phase 3: Interface

- [ ] Add UI
- [ ] Add form validation
- [ ] Add loading states
- [ ] Add error states

## Phase 4: Release

- [ ] Security review
- [ ] Performance test
- [ ] Deployment
- [ ] Backup verification
```

## Fasa 4: Implementasi

Gunakan satu tugas kecil pada satu masa.

Contoh tugas baik:

```text
Tambah endpoint POST /users dengan validasi email,
hash password, duplicate checking, unit test, dan
integration test. Jangan ubah endpoint lain.
```

Contoh tugas buruk:

```text
Siapkan semua backend.
```

## Fasa 5: Verification

Periksa:

- Build lulus.
- Test lulus.
- Linter lulus.
- Type check lulus.
- Security scan lulus.
- Fungsi manual lulus.
- Dokumentasi dikemas kini.

## Fasa 6: Release

Periksa:

- Environment variable lengkap.
- Database migration berjaya.
- Backup tersedia.
- Rollback diuji.
- Health check berfungsi.
- Monitoring aktif.
- Log boleh dibaca.

---

# 19. Definition of Done

Sesuatu tugas hanya dianggap selesai apabila:

```md
- [ ] Requirement dipenuhi
- [ ] Kod boleh dibina
- [ ] Kod boleh dijalankan
- [ ] Ujian lulus
- [ ] Error handling tersedia
- [ ] Logging tersedia
- [ ] Tiada secret dalam kod
- [ ] Dokumentasi dikemas kini
- [ ] Tiada perubahan tidak berkaitan
- [ ] Compatibility disemak
- [ ] Security disemak
- [ ] Rollback diketahui
```

---

# 20. Standard Respons AI

Setiap jawapan teknikal AI perlu mengikuti format:

```md
## Ringkasan

## Andaian

## Punca atau Rasional

## Fail Terlibat

## Perubahan

## Kod

## Cara Memasang

## Cara Menjalankan

## Cara Menguji

## Hasil Dijangka

## Risiko

## Rollback

## Perkara Belum Pasti
```

---

# 21. Kawalan Halusinasi AI

AI kadangkala mencipta:

- Nama fungsi yang tidak wujud.
- Package yang salah.
- API palsu.
- Parameter salah.
- Versi dependency tidak serasi.
- Pin hardware salah.
- Register MCU salah.
- Command terminal salah.
- Struktur fail tidak sepadan.

Arahan anti-halusinasi:

```text
Jangan mereka-reka API, fungsi, package, pin, register, parameter,
atau command. Jika tidak pasti, nyatakan tidak pasti dan gunakan
dokumentasi rasmi sebagai sumber rujukan. Bezakan fakta, andaian,
dan cadangan. Jangan mendakwa kod telah diuji jika ia belum dijalankan.
```

Checklist:

```md
- [ ] Nama package disahkan
- [ ] Versi package disahkan
- [ ] API disahkan
- [ ] Import disahkan
- [ ] Command disahkan
- [ ] Pin disahkan
- [ ] Datasheet disahkan
- [ ] Build dijalankan
- [ ] Test dijalankan
```

---

# 22. Git Workflow

## 22.1 Branch

```text
main
develop
feature/nama-fungsi
fix/nama-bug
refactor/nama-modul
docs/nama-dokumen
```

## 22.2 Commit

Format:

```text
type(scope): description
```

Contoh:

```text
feat(auth): add login endpoint
fix(api): handle duplicate request
refactor(core): simplify configuration loader
test(user): add registration regression test
docs(readme): add local setup guide
```

Jenis commit:

```text
feat
fix
refactor
test
docs
build
ci
chore
perf
security
```

## 22.3 Sebelum Commit

```md
- [ ] Build lulus
- [ ] Test lulus
- [ ] Linter lulus
- [ ] Tiada secret
- [ ] Diff diperiksa
- [ ] Dokumentasi dikemas kini
```

---

# 23. Pengurusan Perubahan

Gunakan fail:

```text
DECISIONS.md
```

Format:

```md
# ADR-001: Use PostgreSQL

## Status

Accepted

## Context

Sistem memerlukan transaksi, relational data, dan query kompleks.

## Decision

Gunakan PostgreSQL.

## Alternatives

- SQLite
- MySQL
- MongoDB

## Consequences

Kelebihan:
- Strong transaction support
- Mature ecosystem

Kekurangan:
- Memerlukan server
- Deployment lebih kompleks
```

---

# 24. Environment Variable

Jangan letakkan rahsia dalam kod.

Contoh `.env.example`:

```env
APP_ENV=development
APP_PORT=3000
DATABASE_URL=
JWT_SECRET=
API_KEY=
LOG_LEVEL=info
```

Peraturan:

```md
- [ ] `.env` berada dalam `.gitignore`
- [ ] `.env.example` tidak mengandungi nilai sebenar
- [ ] Secret produksi disimpan dalam secret manager
- [ ] Secret boleh diputar
- [ ] Secret tidak dicetak dalam log
```

---

# 25. Logging

Log yang baik mengandungi:

```text
timestamp
level
service
event
requestId
userId jika sesuai
duration
result
errorCode
```

Jangan log:

```text
password
token penuh
API key
session cookie
kad pembayaran
data peribadi tidak perlu
```

Contoh:

```json
{
  "timestamp": "2026-07-12T10:00:00Z",
  "level": "error",
  "service": "user-api",
  "event": "user.create.failed",
  "requestId": "req_123",
  "errorCode": "EMAIL_ALREADY_EXISTS"
}
```

---

# 26. Error Handling

Gunakan kategori ralat:

```text
VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
RATE_LIMITED
DEPENDENCY_ERROR
TIMEOUT
INTERNAL_ERROR
```

Prinsip:

- Jangan dedahkan stack trace kepada pengguna.
- Simpan stack trace dalam log dalaman.
- Gunakan error code tetap.
- Beri mesej yang boleh difahami.
- Sertakan request ID.
- Jangan senyapkan ralat.

---

# 27. Ujian Minimum

## Unit Test

Menguji satu fungsi atau modul.

## Integration Test

Menguji hubungan:

```text
API + database
service + repository
firmware + driver abstraction
```

## End-to-End Test

Menguji aliran sebenar pengguna.

## Regression Test

Mencegah bug lama kembali.

## Smoke Test

Mengesahkan sistem boleh hidup selepas deployment.

---

# 28. CI/CD

Pipeline minimum:

```text
Checkout
→ Install dependencies
→ Format check
→ Lint
→ Type check
→ Unit test
→ Integration test
→ Security scan
→ Build
→ Package
→ Deploy staging
→ Smoke test
→ Manual approval
→ Deploy production
```

---

# 29. Deployment Checklist

```md
## Before Deployment

- [ ] Semua test lulus
- [ ] Backup dibuat
- [ ] Migration disemak
- [ ] Environment variable lengkap
- [ ] Secret sah
- [ ] Build produksi berjaya
- [ ] Rollback tersedia
- [ ] Monitoring tersedia
- [ ] Health check tersedia

## After Deployment

- [ ] Health endpoint lulus
- [ ] Login berfungsi
- [ ] Fungsi utama berfungsi
- [ ] Database boleh dibaca dan ditulis
- [ ] Log normal
- [ ] Tiada error spike
- [ ] Backup boleh dipulihkan
```

---

# 30. Security Baseline

```md
- [ ] Password di-hash menggunakan algoritma sesuai
- [ ] Token mempunyai expiry
- [ ] Authorization diperiksa pada server
- [ ] Input divalidasi
- [ ] Output di-encode
- [ ] Rate limiting aktif
- [ ] CORS dikawal
- [ ] Secure headers aktif
- [ ] HTTPS wajib
- [ ] Debug mode dimatikan
- [ ] Default credential dibuang
- [ ] Dependency scan aktif
- [ ] Audit log tersedia
- [ ] Backup dienkripsi
- [ ] Least privilege digunakan
```

---

# 31. Prestasi

Jangan optimakan tanpa data.

Proses:

```text
Ukur
→ Kenal pasti bottleneck
→ Ubah
→ Ukur semula
```

Metrik:

```text
latency
throughput
CPU
RAM
storage
network
database query time
cache hit rate
error rate
startup time
frame rate
power consumption
```

---

# 32. Vibe Coding untuk Pengguna Baru

Urutan paling mudah:

```text
1. Nyatakan idea.
2. Minta AI tulis spesifikasi.
3. Semak spesifikasi.
4. Minta AI cadangkan teknologi.
5. Minta AI bina struktur folder.
6. Bina satu fungsi kecil.
7. Jalankan.
8. Tampal ralat.
9. Betulkan.
10. Tambah ujian.
11. Commit.
12. Sambung fungsi seterusnya.
```

Jangan lakukan:

```text
- Salin kod tanpa faham lokasi fail.
- Jalankan command rawak.
- Padam folder projek semasa debugging.
- Dedahkan API key.
- Ubah banyak perkara serentak.
- Install terlalu banyak package.
- Terus deploy tanpa test.
```

---

# 33. Arahan Apabila AI Memberikan Kod

Minta AI sentiasa menyatakan:

```text
1. Nama fail.
2. Lokasi fail.
3. Sama ada fail baru atau fail sedia ada.
4. Bahagian yang perlu diganti.
5. Kod penuh.
6. Command pemasangan.
7. Command menjalankan.
8. Hasil dijangka.
9. Cara mengesahkan.
```

Prompt:

```text
Saya pengguna baru. Jangan berikan potongan kod tanpa lokasi.
Untuk setiap kod, nyatakan nama fail penuh, lokasi folder,
sama ada perlu mencipta atau mengganti fail, dan command tepat
untuk menjalankannya.
```

---

# 34. Prompt Auto-Repair Build Error

```text
Projek gagal dibina.

Command:
[COMMAND]

Output penuh:
[OUTPUT]

Tugas:

1. Cari ralat pertama yang sebenar.
2. Abaikan ralat susulan yang berpunca daripadanya.
3. Terangkan punca.
4. Nyatakan fail terlibat.
5. Berikan pembetulan minimum.
6. Jangan menaik taraf semua dependency kecuali perlu.
7. Jangan memadam lockfile tanpa sebab.
8. Berikan command untuk mengesahkan pembetulan.
9. Jika ada beberapa pilihan, pilih yang paling rendah risiko.
```

---

# 35. Prompt Dependency Audit

```text
Audit semua dependency projek.

Untuk setiap dependency:

- Tujuan.
- Sama ada masih digunakan.
- Risiko keselamatan.
- Risiko maintenance.
- Saiz atau kesan prestasi.
- Versi semasa.
- Compatibility.
- Cadangan kekal, naik taraf, ganti, atau buang.

Jangan naik taraf major version secara automatik.
Sediakan pelan migration untuk perubahan breaking.
```

---

# 36. Prompt Dokumentasi Automatik

```text
Bina dokumentasi lengkap berdasarkan kod projek.

Dokumentasi wajib:

- Tujuan projek.
- Seni bina.
- Struktur folder.
- Keperluan sistem.
- Cara memasang.
- Cara konfigurasi.
- Cara menjalankan.
- Cara menguji.
- API.
- Database.
- Error codes.
- Security.
- Deployment.
- Troubleshooting.
- Known limitations.
- Contribution guide.
```

---

# 37. Prompt Release

```text
Sediakan release untuk versi [VERSI].

Lakukan:

1. Semak perubahan sejak release terakhir.
2. Klasifikasikan breaking change.
3. Kemas kini version.
4. Kemas kini CHANGELOG.
5. Jalankan test.
6. Jalankan build.
7. Semak migration.
8. Semak environment variable.
9. Sediakan release notes.
10. Sediakan rollback plan.
11. Jangan release jika test gagal.
```

---

# 38. CHANGELOG Standard

```md
# Changelog

## [Unreleased]

### Added

### Changed

### Fixed

### Security

### Removed

## [1.0.0] - 2026-07-12

### Added

- Initial release.
```

---

# 39. Template TASKS.md

```md
# Project Tasks

## Current Goal

[MATLAMAT SEMASA]

## In Progress

- [ ] Task

## Next

- [ ] Task
- [ ] Task

## Blocked

- [ ] Task
  - Blocker:
  - Required information:

## Completed

- [x] Task

## Technical Debt

- [ ] Debt item

## Bugs

- [ ] Bug
  - Severity:
  - Reproduction:
  - Expected:
  - Actual:
```

---

# 40. Template PROJECT_SPEC.md

```md
# Project Specification

## 1. Overview

## 2. Problem

## 3. Goals

## 4. Non-Goals

## 5. Users

## 6. Functional Requirements

## 7. Non-Functional Requirements

## 8. User Flow

## 9. Data Model

## 10. API Requirements

## 11. Security Requirements

## 12. Performance Requirements

## 13. Offline Requirements

## 14. Hardware Requirements

## 15. Constraints

## 16. Acceptance Criteria

## 17. Risks

## 18. Milestones
```

---

# 41. Template ARCHITECTURE.md

```md
# System Architecture

## 1. Context

## 2. Components

## 3. Data Flow

## 4. Interfaces

## 5. Database

## 6. Authentication

## 7. Authorization

## 8. Error Handling

## 9. Logging

## 10. Monitoring

## 11. Security Boundaries

## 12. Failure Modes

## 13. Scalability

## 14. Deployment

## 15. Backup and Recovery

## 16. Design Decisions
```

---

# 42. Template SECURITY.md

```md
# Security Policy

## Supported Versions

## Threat Model

## Authentication

## Authorization

## Secret Management

## Data Protection

## Network Security

## Input Validation

## Logging Rules

## Dependency Management

## Vulnerability Reporting

## Incident Response

## Backup Security

## Production Checklist
```

---

# 43. Template TEST_PLAN.md

```md
# Test Plan

## Scope

## Out of Scope

## Test Environment

## Unit Tests

## Integration Tests

## End-to-End Tests

## Security Tests

## Performance Tests

## Recovery Tests

## Hardware Tests

## Acceptance Tests

## Entry Criteria

## Exit Criteria

## Known Risks
```

---

# 44. Sistem Penilaian Output AI

Berikan markah 0 hingga 5.

| Kategori | 0 | 5 |
|---|---:|---:|
| Ketepatan | Salah | Tepat |
| Kelengkapan | Tidak lengkap | Lengkap |
| Kebolehgunaan | Tidak boleh jalan | Terus boleh guna |
| Keselamatan | Berisiko | Dikawal |
| Ujian | Tiada | Lengkap |
| Dokumentasi | Tiada | Lengkap |
| Maintainability | Sukar | Mudah |
| Scope control | Melampau | Tepat |

Output tidak diterima jika:

```text
Ketepatan < 4
Keselamatan < 4
Kebolehgunaan < 4
```

---

# 45. Red Flag dalam Jawapan AI

Berhenti dan semak jika AI:

- Mengubah banyak fail tanpa sebab.
- Menambah package tidak dikenali.
- Menghapuskan ujian.
- Menyahaktifkan keselamatan.
- Menyimpan password dalam plain text.
- Meminta mematikan firewall.
- Menggunakan `sudo` tanpa sebab.
- Meminta memadam lockfile.
- Meminta memadam database.
- Mengabaikan error.
- Menggunakan `try/catch` kosong.
- Menandakan semua type sebagai `any`.
- Mematikan SSL verification.
- Menggunakan default password.
- Mendakwa selesai tanpa menjalankan test.
- Menulis semula projek untuk bug kecil.

---

# 46. Prompt “Jangan Rosakkan Projek”

```text
Lakukan perubahan secara konservatif.

Peraturan wajib:

- Jangan padam fail.
- Jangan ubah API awam.
- Jangan ubah schema database tanpa migration.
- Jangan naik taraf major dependency.
- Jangan ubah config produksi.
- Jangan ubah authentication.
- Jangan ubah authorization.
- Jangan buang test.
- Jangan menukar framework.
- Jangan menulis semula keseluruhan modul.
- Jangan melakukan perubahan di luar skop.

Jika perubahan tersebut benar-benar diperlukan,
terangkan dahulu sebab, kesan, risiko, dan rollback.
```

---

# 47. Prompt “Kod Siap Pakai”

```text
Berikan implementasi lengkap, bukan pseudo-code.

Wajib sertakan:

- Struktur folder.
- Nama fail.
- Kod penuh.
- Dependency.
- Versi minimum.
- Konfigurasi.
- Environment variable.
- Command install.
- Command run.
- Command test.
- Sample input.
- Expected output.
- Error handling.
- Logging.
- Ujian.
- Dokumentasi.
```

---

# 48. Prompt “Semak Sebelum Ubah”

```text
Sebelum membuat perubahan:

1. Baca fail berkaitan.
2. Cari dependency kepada fungsi tersebut.
3. Cari test sedia ada.
4. Cari penggunaan API.
5. Cari konfigurasi berkaitan.
6. Cari risiko compatibility.
7. Senaraikan fail terjejas.
8. Nyatakan pelan minimum.
9. Selepas itu barulah berikan patch.
```

---

# 49. Prompt “Satu Langkah Satu Masa”

```text
Bina projek ini secara bertahap.

Untuk setiap langkah:

1. Nyatakan matlamat.
2. Ubah bilangan fail minimum.
3. Berikan kod lengkap.
4. Berikan command tepat.
5. Berikan hasil dijangka.
6. Berikan cara test.
7. Berhenti selepas langkah siap.

Jangan terus ke langkah seterusnya sehingga langkah semasa boleh dibina dan diuji.
```

---

# 50. Kaedah Penyelesaian Masalah

Gunakan urutan:

```text
Reproduce
→ Observe
→ Isolate
→ Form hypothesis
→ Test hypothesis
→ Apply minimal fix
→ Add regression test
→ Verify
→ Document
```

Jangan terus meneka dan menukar banyak perkara.

---

# 51. Untuk Projek Besar

Gunakan hierarki:

```text
Product
├── Domain
│   ├── Module
│   │   ├── Feature
│   │   │   ├── Task
│   │   │   │   ├── Test
```

Contoh:

```text
ECU Platform
├── Engine Control
│   ├── Fuel
│   │   ├── Base Fuel Map
│   │   │   ├── Interpolation
│   │   │   │   ├── Unit Test
```

---

# 52. Vibe Coding untuk Sistem Kritikal

Untuk sistem automotif, perubatan, industri, tenaga, dan kawalan mesin:

- Jangan bergantung pada AI sahaja.
- Gunakan datasheet rasmi.
- Gunakan standard industri.
- Sediakan failsafe.
- Sediakan watchdog.
- Sediakan hardware interlock.
- Uji fault injection.
- Uji brownout.
- Uji sensor open/short.
- Uji komunikasi terputus.
- Uji data rosak.
- Uji reboot.
- Uji thermal.
- Uji voltage transient.
- Gunakan nilai default selamat.
- Log setiap fault.
- Jangan mengaktifkan output berbahaya semasa boot.

---

# 53. Format Spesifikasi Fungsi

```md
# Feature: [Nama]

## Purpose

## User Story

Sebagai [pengguna],
saya mahu [fungsi],
supaya [hasil].

## Inputs

## Outputs

## Validation

## Business Rules

## Error Cases

## Security

## Performance

## Dependencies

## Acceptance Criteria

- [ ] Condition
- [ ] Condition

## Tests

## Rollback
```

---

# 54. Format Bug Report

```md
# Bug Report

## Title

## Environment

## Version

## Steps to Reproduce

1.
2.
3.

## Expected Result

## Actual Result

## Logs

## Screenshots

## Frequency

## Severity

## Workaround

## Suspected Area
```

---

# 55. Format Permintaan Perubahan

```md
# Change Request

## Current Behavior

## Requested Behavior

## Reason

## Affected Users

## Affected Modules

## Compatibility Requirement

## Data Migration

## Security Impact

## Performance Impact

## Acceptance Criteria

## Rollback Plan
```

---

# 56. Prompt Harian Pembangunan

```text
Baca PROJECT_SPEC.md, ARCHITECTURE.md, TASKS.md, dan CHANGELOG.md.

Pilih satu tugas paling penting yang belum selesai.

Sebelum mengubah kod:

- Terangkan tugas.
- Senaraikan fail.
- Nyatakan acceptance criteria.
- Nyatakan test yang akan ditambah.

Selepas implementasi:

- Jalankan formatter.
- Jalankan linter.
- Jalankan type check.
- Jalankan test.
- Kemas kini TASKS.md.
- Kemas kini CHANGELOG.md.
- Berikan ringkasan perubahan.
```

---

# 57. Prompt Audit Projek Penuh

```text
Audit projek ini secara menyeluruh.

Bahagian audit:

1. Architecture
2. Code quality
3. Security
4. Performance
5. Reliability
6. Error handling
7. Logging
8. Testing
9. Database
10. API
11. UI/UX
12. Accessibility
13. Dependencies
14. Deployment
15. Documentation
16. Technical debt

Untuk setiap penemuan:

- Severity
- Evidence
- Impact
- Recommended fix
- Estimated complexity
- Regression risk
- Required test

Akhir sekali, hasilkan pelan pembaikan mengikut keutamaan.
```

---

# 58. Peraturan Penggunaan Terminal

Sebelum menjalankan command:

- Fahami fungsi command.
- Pastikan lokasi folder.
- Elakkan wildcard berbahaya.
- Elakkan `rm -rf`.
- Elakkan menjalankan script tidak dikenali.
- Semak `package.json`, `pyproject.toml`, atau build file.
- Gunakan virtual environment.
- Gunakan lockfile.
- Simpan backup sebelum migration.

Prompt:

```text
Terangkan fungsi setiap command sebelum memberikannya.
Jangan beri command yang memadam data tanpa arahan jelas.
Nyatakan folder tempat command perlu dijalankan.
```

---

# 59. Standard Kualiti Minimum Kod

Kod mesti:

```md
- [ ] Boleh dibina
- [ ] Boleh dijalankan
- [ ] Diformat
- [ ] Dilint
- [ ] Typed jika disokong
- [ ] Ada validasi
- [ ] Ada error handling
- [ ] Ada logging
- [ ] Ada test
- [ ] Tiada secret
- [ ] Tiada dead code
- [ ] Tiada dependency tidak perlu
- [ ] Tiada fungsi terlalu panjang
- [ ] Tiada pengulangan besar
```

---

# 60. Master Prompt Akhir

```text
Anda ialah pasukan pembangunan penuh untuk projek ini.

Baca semua fail dokumentasi dan kod sebelum bekerja.

Objektif utama:

[OBJEKTIF]

Tugas semasa:

[TUGAS]

Keperluan wajib:

1. Jangan mereka-reka requirement.
2. Jangan ubah bahagian tidak berkaitan.
3. Gunakan perubahan minimum yang lengkap.
4. Kekalkan backward compatibility.
5. Validasi semua input.
6. Kendalikan semua ralat.
7. Jangan hard-code secret.
8. Tambah logging yang berguna.
9. Tambah atau kemas kini ujian.
10. Kemas kini dokumentasi.
11. Jangan tambah dependency tanpa justifikasi.
12. Jangan mendakwa test lulus jika belum dijalankan.
13. Bezakan fakta, andaian, dan cadangan.
14. Nyatakan risiko.
15. Nyatakan rollback.

Format jawapan:

## Pemahaman
## Andaian
## Pelan
## Fail Terlibat
## Implementasi
## Ujian
## Arahan Menjalankan
## Hasil Dijangka
## Risiko
## Rollback
## Perkara Belum Pasti

Selesaikan satu skop pada satu masa.
```

---

# 61. Ringkasan Operasi

Vibe Coding yang baik mengikuti disiplin ini:

```text
Jelas sebelum kod
Kecilkan skop
Satu perubahan satu tujuan
Uji setiap perubahan
Jangan percaya output tanpa pengesahan
Dokumentasikan keputusan
Simpan sejarah melalui Git
Jaga rahsia
Sediakan rollback
Deploy hanya selepas verifikasi
```

Kaedah paling selamat:

```text
Plan
→ Build
→ Run
→ Test
→ Review
→ Commit
→ Release
```

---

# 62. Penutup Dokumen

Dokumen ini boleh dijadikan arahan kekal projek.

Cadangan penggunaan:

1. Simpan sebagai `VIBE_CODING.md`.
2. Letakkan di root projek.
3. Arahkan AI membaca fail ini sebelum menulis kod.
4. Cipta `PROJECT_SPEC.md`.
5. Cipta `ARCHITECTURE.md`.
6. Cipta `TASKS.md`.
7. Mulakan satu fungsi kecil.
8. Jalankan dan uji.
9. Commit selepas stabil.
10. Ulang proses sehingga sistem siap.

Arahan pembukaan untuk setiap sesi:

```text
Baca VIBE_CODING.md, PROJECT_SPEC.md, ARCHITECTURE.md,
TASKS.md, dan CHANGELOG.md sebelum membuat sebarang perubahan.
Patuhi semua standard projek dan lakukan satu tugas pada satu masa.
```
