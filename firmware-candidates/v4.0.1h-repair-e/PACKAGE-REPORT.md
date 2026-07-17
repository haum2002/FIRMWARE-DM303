# DM303 V4.0.1k Repair-E Candidate

Date: 2026-07-15

Status: **HOLD / candidate only**

Repair-E continues after the user's Repair-C field result and the Repair-D
runtime-loop audit. It is the cleanest current UI/resource-safe measurement
candidate.

## Why Repair-E Exists

Repair-D kept the UI/render loop official at `0x0c6c8`, but still allowed two
other broad runtime fail-stop fall-through patches:

- `0x09ca0`: `fe e7` to `ff e7`
- `0x2c4ea`: `fe e7` to `70 47`

Disassembly shows `0x09ca0` is also a guard after a validation check. Repair-E
therefore removes all broad runtime fail-stop fall-through patches. It keeps
the more specific measurement recovery and current-switch latency patches.

## Firmware

- File: `DM303V4.0.1-beta.bin`
- Visible marker: `V4.0.1k`
- SHA256: `75dffe2bbe1ed3193c3073f39d018c888f4a684440e17647645bd18d7ef40216`
- Source: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Source SHA256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Size: `203260` bytes, unchanged

## What Is Kept Official

| Offset | Official | Repair-E | Reason |
|---:|---|---|---|
| `0x09ca0` | `fe e7` | `fe e7` | keep validation/runtime guard official |
| `0x0c6c8` | `fe e7` | `fe e7` | keep UI/render guard official to avoid calit/fall-through drawing artifacts |
| `0x2c4ea` | `fe e7` | `fe e7` | keep semihost/debug fail-stop official |
| `0x0f10a` | `02 20` | `02 20` | keep relay pre-switch settle official |
| `0x0f146` | `03 20` | `03 20` | keep relay bit-settle official |
| `0x0f192` | `0a 20` | `0a 20` | keep final relay settle official |

## What Still Targets Measurement Latency

Repair-E keeps:

- bounded low byte-IO helper;
- high-level stream/status fail-fast recovery;
- command `0x40` busy failure routing into the existing error/clear path;
- stale bits `0` and `1` clear from `0x2000022c`;
- mode/range entry stale-state clear wrapper;
- stream stale-busy early-return bypass;
- current-switch long guard caps:
  - `0x1585e`
  - `0x15888`
  - `0x15934`
  - `0x1595c`
- immediate mode/range call gates:
  - `0x15812`
  - `0x15838`
  - `0x15862`
  - `0x1588c`

The old aggressive stale bit0 stream-helper bypasses remain disabled.

## SD-Root Build

Use only:

```text
firmware-candidates/v4.0.1h-repair-e/sd-root/
```

Build command:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-e --profile v401h-repair-e
```

Validation command:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-e\sd-root --profile v401h-repair-e
```

Validation result:

```text
repair_candidate_check=ok
official_v4_system_resources=match
firmware_sha256=75dffe2bbe1ed3193c3073f39d018c888f4a684440e17647645bd18d7ef40216
dm30xdb1_sha256=846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79
```

## Resource Policy

- Full `system` folder is copied from `backup/DM303 V4.0-read only/system`.
- `system/DM30XDB1.dat` is added from the official SD resource package.
- No Malay UI, dark theme, logo edit, icon edit, or boot-logo delay is included.

## Honest Limitation

Repair-E is designed to reduce UI/render corruption risk while preserving the
best current latency hypotheses. It still does not prove analog noise removal,
accuracy calibration, True RMS correction, or hardware-leakage repair.
