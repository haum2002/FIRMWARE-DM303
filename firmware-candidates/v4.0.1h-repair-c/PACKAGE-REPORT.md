# DM303 V4.0.1i Repair-C Measurement Candidate

Date: 2026-07-15

Status: **HOLD / candidate only**

This package continues from `v401h-repair-b` after the system-resource pull
problem was identified and fixed. It keeps the complete official V4.0 `system`
folder and adds only `DM30XDB1.dat`.

## Goal

Repair-C targets measurement instability that can happen after physical
relay/mux/range switching:

- DC/AC/DC switching latency in the green ammeter path;
- blank/freeze after spike, overload, or stale acquisition state;
- zeroing instability caused by reading too soon after relay/mux movement;
- visible noise/transient immediately after switching.

It does **not** claim that physical analog noise, input leakage, True RMS math,
or oscilloscope waveform noise is fully solved.

## Firmware

- File: `DM303V4.0.1-beta.bin`
- Visible marker: `V4.0.1i`
- SHA256: `70b98735978f711c2203c0b907927aded22eb91ca03fdc601ebdfb33f56b117d`
- Source: `backup/DM303 V4.0-read only/DM303V4.004.bin`
- Source SHA256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Size: `203260` bytes, unchanged

## Measurement Patch Evidence

Repair-C keeps the Repair-B current-switch latency caps:

| Offset | Repair-B | Repair-C | Meaning |
|---:|---|---|---|
| `0x1585e` | `b0 f5 c8 6f` | `b0 f5 c8 6f` | first `0x3e80` wait remains capped to `0x0640` |
| `0x15888` | `b0 f5 c8 6f` | `b0 f5 c8 6f` | second `0x3e80` wait remains capped to `0x0640` |
| `0x15934` | `40 f2 dc 51` | `40 f2 dc 51` | state-2 `0x3a98` wait remains lowered to `0x05dc` |
| `0x1595c` | `40 f2 dc 51` | `40 f2 dc 51` | second state-2 `0x3a98` wait remains lowered to `0x05dc` |

Repair-C adds moderate relay/mux settle timing at the proven selector waits:

| Offset | Official / Repair-B | Repair-C | Meaning |
|---:|---|---|---|
| `0x0f10a` | `02 20` | `05 20` | pre-switch settle `2` to `5` ticks |
| `0x0f146` | `03 20` | `08 20` | bit-settle `3` to `8` ticks |
| `0x0f192` | `0a 20` | `32 20` | final post-relay settle `10` to `50` ticks |

This is intended to let the physical analog/protection path settle after relay
clicks before the next reading/zeroing operation, while Repair-B still prevents
the long ammeter AC-to-DC gate from remaining at the original large values.

## SD-Root Build

Use only:

```text
firmware-candidates/v4.0.1h-repair-c/sd-root/
```

Build command:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-c --profile v401h-repair-c
```

Validation command:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-c\sd-root --profile v401h-repair-c
```

Validation result:

```text
repair_candidate_check=ok
official_v4_system_resources=match
firmware_sha256=70b98735978f711c2203c0b907927aded22eb91ca03fdc601ebdfb33f56b117d
dm30xdb1_sha256=846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79
```

## Resource Policy

- Full `system` folder is copied from `backup/DM303 V4.0-read only/system`.
- `system/DM30XDB1.dat` is added from the official SD resource package.
- No Malay UI, dark theme, logo edit, icon edit, or boot-logo delay is included.

## Honest Limitation

Firmware can reduce stale-state waits, timeout lockups, and relay-settle
transients. It cannot guarantee a truly noise-free hardware connection if the
source is physical input leakage, PCB contamination, relay contact behavior,
protection-device recovery, grounding, shielding, or analog front-end damage.

The success criteria for this candidate are narrower:

- no long blank/freeze after ammeter AC to DC switching;
- no shared reading/battery-icon disappearance during normal recovery;
- better zeroing stability immediately after relay clicks;
- no return of UI smear/glitch because official resources are used.
