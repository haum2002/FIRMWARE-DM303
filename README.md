# FIRMWARE-DM303

Arkib komuniti untuk kerja naik taraf AUTool DM303 daripada firmware rasmi V4.0
kepada pakej `v4.0.1 beta`.

## Pakej Akhir Semasa

Profile: `v401h-repair-i`

Visible marker pada device: `V4.0.1o`

Firmware:

```text
dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
```

SHA-256:

```text
11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953
```

## Status Ringkas

- `V4.0.1h` / `stability-exp20-ms-safe` dikuarantin selepas field feedback:
  noise meningkat, ammeter AC -> DC masih lambat, dan teks masih bercalit.
- Folder akhir kini dibina semula daripada `v401h-repair-i`: system resource
  rasmi V4.0 dipulihkan, `DM30XDB1.dat` ditambah, dan lapisan Melayu/dark/logo
  eksperimen dikeluarkan sementara.
- `repair-i` hanya menambah patch measurement terhad pada laluan ammeter:
  window pengumpulan sampel fungsi `AC / 20A / mA` dikurangkan daripada 240
  kepada 64 sampel untuk menguji punca latency panjang.

## Validasi

```powershell
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_measurement_candidate_gate.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
```

Untuk SD card:

```powershell
python tools/dm303_preflash_check.py --root E:\ --profile v401h-repair-i --allow-sd-extras
```

Salin kandungan `dm303_firmware/DM303-V4.0.1-beta/` terus ke root SD card.

## Overlay UI/Melayu

Calon UI/Melayu/tema gelap yang tidak dipromosi:

```text
firmware-candidates/v4.0.1h-repair-i-ui-ms/sd-root/
```

Profile: `v401h-repair-i-ui-ms`, marker `V4.0.1p`.

Overlay ini hanya patut diuji selepas `V4.0.1o` membuktikan calit hilang
dengan resource vendor rasmi.

## Pakej Gabungan (Melayu + Tema Gelap) — HOLD

```text
dm303_firmware/DM303-V4.0.1p-ms-beta/
```

Profile: `v401h-repair-i-ui-ms`, marker pada device `V4.0.1p`.

SHA-256 firmware:

```text
a26edd279ae15a68c3f819b1e2dac10d91043a45f6faac64aa0bdfa504f38878
```

Kandungan: firmware `repair-i` penuh (patch measurement yang sama, bait demi
bait) + menu bahasa `Melayu` (slot Spanish digunakan semula) + 137 entri teks
Melayu + tema gelap (latar `#0A233B`, teks `#EFF7FA`, ambar `#FFCC48`).
Semua resource sistem lain kekal rasmi V4.0.

Firmware ini berbeza dengan `V4.0.1o` hanya pada 8 bait: marker versi
(`0x02cae`, `0x02cbe`) dan nama menu bahasa (`0x25bf8`-`0x25bfe`).

Nota slot bahasa: firmware rasmi mempunyai 14 slot bahasa tetap tanpa slot
kosong, jadi Bahasa Melayu tidak boleh ditambah tanpa menggantikan satu slot
sedia ada. Slot Spanish dipilih; bahasa Spanish boleh dipulihkan dengan flash
semula pakej rasmi V4.0 atau pakej `V4.0.1o`.

Validasi:

```powershell
python tools/dm303_ui_overlay_candidate_check.py --root dm303_firmware\DM303-V4.0.1p-ms-beta
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1p-ms-beta --profile v401h-repair-i-ui-ms
```

Status: **HOLD** — belum diuji pada device. Susunan ujian yang disyorkan:
`V4.0.1o` dahulu (baseline measurement bersih); jika calit/noise hilang,
baru uji `V4.0.1p` untuk UI Melayu/tema gelap.

## Batasan

Build ini belum membuktikan ADC, True RMS, EMI filter, calibration math, atau
noise analog sudah diperbaiki. Jika `V4.0.1o` masih menunjukkan latency/blank
yang sama, laluan seterusnya ialah audit sampling/math yang lebih dalam dan
ujian rail/reference/relay/input current berdasarkan bukti hardware.
