# DM303 V4.0.1m Repair-G Candidate

Date: 2026-07-15

Status: **HOLD / candidate only**

Repair-G continues from Repair-F after a scan found another mode/range helper
cluster that still used `0x3a98` state-2 timing guards and still called
`0x0801f19a`. This may explain why patching only the `0x158xx` cluster did not
change the ammeter AC to DC delay.

## Firmware

- File: `DM303V4.0.1-beta.bin`
- Visible marker: `V4.0.1m`
- SHA256: `a84dda5e7f3d675d0985bde4c431a0d86c21d063d7c2dfd56a68726690566c7d`
- Source: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Source SHA256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Size: `203260` bytes, unchanged

## Safety Boundary

The following remain byte-identical to official V4.0:

- fault/default vectors and fault handler block;
- runtime fail-stop loops;
- UI/render guard at `0x0c6c8`;
- lower byte-IO helper and wrapper area;
- stream retry loops and stream busy gate;
- stream state cleanup;
- mode/range entry wrapper area;
- relay settle timing;
- boot-logo loader and boot-logo delay cave;
- all official `system` resources.

No Malay UI, dark theme, logo edit, icon edit, boot-logo delay, stream recovery,
ADC math, True RMS math, or low-level IO timeout patch is included.

## Measurement-Latency Changes

Repair-G changes only version strings and these mode/range timing guards:

| Offset | Change |
|---:|---|
| `0x14b0e` | earlier mode/range state-2 guard `0x3a98` to `0x05dc` |
| `0x14b36` | earlier mode/range state-2 guard `0x3a98` to `0x05dc` |
| `0x15812` | elapsed-time skip branch to NOP |
| `0x15838` | elapsed-time skip branch to NOP |
| `0x1585e` | long compare `0x3e80` to `0x0640` |
| `0x15862` | elapsed-time skip branch to NOP |
| `0x15888` | long compare `0x3e80` to `0x0640` |
| `0x1588c` | elapsed-time skip branch to NOP |
| `0x15934` | current/meter state-2 guard `0x3a98` to `0x05dc` |
| `0x1595c` | current/meter state-2 guard `0x3a98` to `0x05dc` |

## SD-Root

Use only:

```text
firmware-candidates/v4.0.1h-repair-g/sd-root/
```

Build command:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-g --profile v401h-repair-g
```

Validation commands:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-g\sd-root --profile v401h-repair-g
python tools\dm303_measurement_candidate_gate.py --root firmware-candidates\v4.0.1h-repair-g\sd-root --profile v401h-repair-g
```

Validation result:

```text
repair_candidate_check=ok
measurement_candidate_gate=ok
official_v4_system_resources=match
ui_render_stream_io_relay_boot_windows=official
diff_ranges=0x02cac-0x02cae, 0x02cbc-0x02cbe, 0x14b0e-0x14b11, 0x14b36-0x14b39, 0x15812-0x15813, 0x15838-0x15839, 0x15860-0x15863, 0x1588a-0x1588d, 0x15934-0x15937, 0x1595c-0x1595f
```

## Honest Limitation

Repair-G is meant to isolate the ammeter AC to DC latency path without making
the noise/UI situation worse. It still cannot prove analog noise removal,
AC zero accuracy, True RMS correction, or hardware leakage repair before
device-side testing.
