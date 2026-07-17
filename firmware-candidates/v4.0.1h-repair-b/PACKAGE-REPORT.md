# DM303 V4.0.1h Repair-B Candidate

Date: 2026-07-15

Status: **HOLD / candidate only**

This package was created after field feedback that `v401h-repair-a` produced no visible functional improvement. Repair-A restored official UI/resource files and kept the previous exp14/exp16 recovery core, but it did not close two remaining long state-2 timing guards in the same ammeter/current switch cluster.

## What changed in Repair-B

Firmware file:

- `DM303V4.0.1-beta.bin`
- SHA256: `3ef4cfd80a86f984a8679c3e340eb17a3441e8d761b16046693eb18c230d5613`
- Built from official source: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Visible marker remains: `V4.0.1h`

Measurement/latency patch evidence:

| Offset | Official V4.0 | Repair-A | Repair-B | Purpose |
|---:|---|---|---|---|
| `0x1585e` | `b0 f5 7a 5f` | `b0 f5 c8 6f` | `b0 f5 c8 6f` | `0x3e80` guard capped to `0x0640` |
| `0x15888` | `b0 f5 7a 5f` | `b0 f5 c8 6f` | `b0 f5 c8 6f` | second `0x3e80` guard capped to `0x0640` |
| `0x15934` | `43 f6 98 21` | `43 f6 98 21` | `40 f2 dc 51` | remaining state-2 `0x3a98` guard lowered to `0x05dc` |
| `0x1595c` | `43 f6 98 21` | `43 f6 98 21` | `40 f2 dc 51` | second remaining state-2 `0x3a98` guard lowered to `0x05dc` |

The new `0x05dc` value is not invented from outside firmware; it already exists as a nearby vendor-used settle budget in the same timing cluster. The goal is to reduce the reported long AC-to-DC ammeter blank while keeping a bounded settle wait instead of bypassing protection logic.

## Resource policy

The SD-root package intentionally keeps the official V4.0 system resources unchanged to avoid repeating the UI calit/glitch problem:

- `official_system_match=True` for all files from `backup/DM303 V4.0-read only/system`
- `DM30XDB1.dat` is added from `backup/SD-file_DM303_update_US240104-read only/system/DM30xDB1.dat`
- No dark theme, Malay slot, logo, or icon modification is included in this repair candidate
- `LOGO-1.bmp` SHA256: `f5e84dfd0a14f63ad8c570629c59c36a0a8a8844ce4cfc48c9c89d1031b41ba3`
- `icon-SP.dat` SHA256: `96f2b294c7fad14a527eb96f1a8f09f7e0f33e2f02f7f43af305c9fa2df57394`
- `TEXT_SP.DAT` SHA256: `4b6b2fd9c6dee916390144815e7becc02549b7d6f1260b0551c8d939c3acf83e`

## SD-root structure

Use only the contents of:

`firmware-candidates/v4.0.1h-repair-b/sd-root/`

Expected root-level files:

- `DM303V4.0.1-beta.bin`
- `QBtest.txt`
- `readme.txt`
- `system/`

Validation:

- `root_exists=True`
- `firmware_exists=True`
- `original_bin_absent=True`
- `nested_candidate_absent=True`
- `dm30xdb1_exists=True`
- `repair_candidate_check=ok`
- `official_v4_system_resources=match`

Full hashes are recorded in `SD-ROOT-SHA256SUMS.txt`.

Build command used for the SD-root:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-b --profile v401h-repair-b
```

Validation command:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-b\sd-root --profile v401h-repair-b
```

## Honest limitation

This is a targeted latency repair, not a proven accuracy/noise fix. It changes real firmware code in the suspected current-switch wait cluster, but it does not yet prove oscilloscope noise reduction, AC zero accuracy, True RMS math improvement, or hardware leakage correction. Those need a separate validated patch path after this latency gate is confirmed or rejected.
