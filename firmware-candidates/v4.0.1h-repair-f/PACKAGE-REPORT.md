# DM303 V4.0.1l Repair-F Candidate

Date: 2026-07-15

Status: **HOLD / candidate only**

Repair-F is a rollback and isolation build after the field result that reported:

- noise became higher;
- ammeter AC to DC remained slow;
- text smear/calit above letters remained visible.

The previous repair line still carried stream/IO recovery patches and other
runtime changes. Repair-F removes those changes and keeps only the current
AC/DC switch timing cluster patches.

## Firmware

- File: `DM303V4.0.1-beta.bin`
- Visible marker: `V4.0.1l`
- SHA256: `a324b9dfc0647601a7775685f15d17185da01d8443b1b2cd67aa7ea7709d4de3`
- Source: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Source SHA256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Size: `203260` bytes, unchanged

## What Repair-F Deliberately Removes

The following areas are kept byte-identical to official V4.0:

- fault/default vectors and fault handler block;
- runtime fail-stop loops;
- UI/render guard at `0x0c6c8`;
- lower byte-IO helper and wrapper area;
- stream retry loops and stream busy gate;
- stream state byte cleanup;
- mode/range state wrapper;
- relay settle timing;
- boot-logo loader and boot-logo delay cave;
- full `system` resource folder.

This is intended to remove patch causes that could plausibly increase noise or
create text smear while still testing the AC/DC ammeter latency hypothesis.

## What Still Targets AC/DC Ammeter Latency

Only the same switch timing cluster is changed:

| Offset | Change |
|---:|---|
| `0x15812` | elapsed-time skip branch to NOP |
| `0x15838` | elapsed-time skip branch to NOP |
| `0x1585e` | long compare `0x3e80` to `0x0640` |
| `0x15862` | elapsed-time skip branch to NOP |
| `0x15888` | long compare `0x3e80` to `0x0640` |
| `0x1588c` | elapsed-time skip branch to NOP |
| `0x15934` | state-2 guard `0x3a98` to `0x05dc` |
| `0x1595c` | state-2 guard `0x3a98` to `0x05dc` |

## Validation

Use only this SD-root folder:

```text
firmware-candidates/v4.0.1h-repair-f/sd-root/
```

Build command:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-f --profile v401h-repair-f
```

Standard validation:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-f\sd-root --profile v401h-repair-f
```

Strict measurement gate:

```powershell
python tools\dm303_measurement_candidate_gate.py --root firmware-candidates\v4.0.1h-repair-f\sd-root --profile v401h-repair-f
```

Validation result:

```text
repair_candidate_check=ok
measurement_candidate_gate=ok
official_v4_system_resources=match
ui_render_stream_io_relay_boot_windows=official
diff_ranges=0x02cac-0x02cae, 0x02cbc-0x02cbe, 0x15812-0x15813, 0x15838-0x15839, 0x15860-0x15863, 0x1588a-0x1588d, 0x15934-0x15937, 0x1595c-0x1595f
```

## Honest Limitation

Repair-F cannot prove on-device analog noise removal before field testing. It
is intentionally designed to avoid making the noise and UI smear worse while
isolating the AC/DC ammeter latency patch.
