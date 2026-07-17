# DM303 V4.0.1j Repair-D Candidate

Date: 2026-07-15

Status: **HOLD / candidate only**

Repair-D was created after Repair-C failed in field observation:

- noise became higher;
- ammeter AC -> DC remained slow;
- text smear/calit above letters remained visible.

The user-provided photo showed short horizontal artifacts above text strokes.
That pattern is now treated as likely render-state/fall-through corruption, not
only a BMP/icon palette problem.

## Firmware

- File: `DM303V4.0.1-beta.bin`
- Visible marker: `V4.0.1j`
- SHA256: `0d0899258a5167e34e56485aeb7a72d74211dd9c40ec2faa5e9412fe8107b41c`
- Source: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Source SHA256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Size: `203260` bytes, unchanged

## What Was Rolled Back

Repair-D removes the Repair-C relay/mux settle increase because field noise got
worse:

| Offset | Repair-C | Repair-D |
|---:|---|---|
| `0x0f10a` | `05 20` | `02 20` |
| `0x0f146` | `08 20` | `03 20` |
| `0x0f192` | `32 20` | `0a 20` |

Repair-D also keeps the UI/render fail-stop loop official:

| Offset | Repair-C | Repair-D | Reason |
|---:|---|---|---|
| `0x0c6c8` | `ff e7` | `fe e7` | avoid render fall-through that can draw with invalid state |

Disassembly around `0x0801c6c8` shows an intentional loop after a render-state
check. Repair-C and older builds let that path fall through; Repair-D restores
the official loop behavior at that UI/render point.

## What Still Targets Latency

Repair-D keeps Repair-B's latency/state recovery:

- bounded low byte-IO helper;
- stream/status fail-fast recovery;
- stale bits `0` and `1` clear from `0x2000022c`;
- stream stale-busy early-return bypass;
- current-switch guards capped from `0x3e80`/`0x3a98` to shorter bounded values.

Repair-D additionally tests only the immediate mode/range call gates:

| Offset | Official / Repair-C | Repair-D | Purpose |
|---:|---|---|---|
| `0x15812` | `05 d9` | `00 bf` | do not delay first mode/range call once switch condition is detected |
| `0x15838` | `34 d9` | `00 bf` | do not delay second mode/range call once switch condition is detected |
| `0x15862` | `06 d9` | `00 bf` | do not delay first return-to-mode call |
| `0x1588c` | `05 d9` | `00 bf` | do not delay second return-to-mode call |

The aggressive stale bit0 stream-helper bypasses from old exp15 remain disabled.

## SD-Root Build

Use only:

```text
firmware-candidates/v4.0.1h-repair-d/sd-root/
```

Build command:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-d --profile v401h-repair-d
```

Validation command:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-d\sd-root --profile v401h-repair-d
```

Validation result:

```text
repair_candidate_check=ok
official_v4_system_resources=match
firmware_sha256=0d0899258a5167e34e56485aeb7a72d74211dd9c40ec2faa5e9412fe8107b41c
dm30xdb1_sha256=846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79
```

## Resource Policy

- Full `system` folder is copied from `backup/DM303 V4.0-read only/system`.
- `system/DM30XDB1.dat` is added from the official SD resource package.
- No Malay UI, dark theme, logo edit, icon edit, or boot-logo delay is included.

## Honest Limitation

Repair-D is a corrective candidate after Repair-C failed. It is meant to isolate
whether the calit comes from the UI/render fall-through patch and whether the
remaining latency is caused by delayed mode/range call gates. It still does not
claim a complete analog noise, accuracy, True RMS, or hardware-leakage fix.
