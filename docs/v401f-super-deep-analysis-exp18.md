# DM303 V4.0.1f Super Deep Analysis and Clean Fix

Date: 2026-07-14

Current flash profile: `stability-exp18-resource`

## Field Result That Changed The Direction

The user confirmed that `V4.0.1e` fixed the screen/resource symptom: the text
smear/loading display issue disappeared after `system/DM30XDB1.dat` was
restored. That proves the missing resource diagnosis was correct.

The same test also proved that `V4.0.1e` was too clean to improve meter
behavior: AC/DC ammeter latency, noise, zeroing, overload/spike recovery, and
measurement stability still behaved like the vendor V4.0 baseline.

Conclusion: keep the resource fix, but reintroduce only the bounded runtime
recovery patches that target measurement blank/freeze. Do not reintroduce UI
language-slot overrides, boot-logo delay, or aggressive exp15 gate bypasses.

## Deeper Static Findings

- V3.16 and V4.0 use the same observed relay/range selector timing:
  `2/3/10` ticks.
- V3.16 and V4.0 mode-switch helper routines are functionally the same at the
  inspected helper level, so replacing the helper with a wrapper is no longer a
  trusted fix.
- Large timeout constants such as `0x7530` are present in both V3.16 and V4.0
  in similar event/timer contexts, so they are not a clean V4-only root cause.
- The strongest shared symptom remains this: when readings blank, the battery
  icon can disappear with the numeric reading. That points to a blocked
  stream/status/UI refresh path, not only a wrong scaling equation.

## What Exp18 Changes

Firmware marker:

- `MT100MM V4.0.1f`
- `BT100MM V4.0.1f`

Resource state:

- Keeps `system/DM30XDB1.dat`.
- Keeps official `TEXT_SP.DAT` and `icon-SP.dat`.
- Keeps official language-name table.
- Keeps boot-logo loader timing official.

Runtime recovery:

- Fault/default self-loop vectors route to the SYSRESETREQ recovery stub.
- Three runtime fail-stop loops return/fall through instead of hanging.
- Stream/status retry branches fail fast or route to the existing error/clear
  path after lower helper failure.
- Low byte-IO helper is routed through a bounded wrapper that returns `0xff`
  if ready never appears within the `0x0fa0` budget.
- Command `0x40` and `0x48` retry counts are clamped to `0x60`.
- Stream error cleanup clears stale bits `0` and `1` from `0x2000022c`.
- Mode/range entry clears the same stale bits before relay/range switching.
- Stream busy early-return gate is bypassed so a fresh transaction can start.
- Two AC-to-DC long-switch gates are capped from `0x3e80` to `0x0640`.

## Byte Proof

The final binary is:

```text
dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin
```

SHA-256:

```text
a9cc0fc643fa79378b04ab4c00fd7303551c63e2d75329b623f529f8856e90fe
```

The following validation gates pass:

```powershell
python tools/dm303_validate_final_package.py --profile stability-exp18-resource
python tools/dm303_preflash_check.py --root dm303_firmware\DM303-V4.0.1-beta --profile stability-exp18-resource
python tools/dm303_resource_loader_audit.py --image dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin --root dm303_firmware\DM303-V4.0.1-beta --report docs\v401f-resource-loader-audit.md
python tools/dm303_stream_state_audit.py --image dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin --report docs\v401f-stability-stream-state-audit.md
```

## What Is Not Claimed

Exp18 is not a confirmed ADC, EMI, True RMS, or calibration rewrite. No safe
ADC/RMS/math contract has been found. The patch is a bounded recovery and
latency test over the now-correct resource package.

If `V4.0.1f` still shows the same AC-to-DC 30 second delay with the UI resource
problem gone, the next useful path is hardware/protocol tracing of the
measurement engine or a controlled comparison against the V3.16 acquisition
path. More string, logo, or resource edits will not solve the measurement
problem.

## Test Gate

Flash only after `preflash_check=ok`. The version screen must show `V4.0.1f`.

Test in this order:

1. Boot/loading and text rendering remain clean.
2. Ammeter green input: DC -> AC -> DC for repeated cycles; record AC-to-DC
   recovery time.
3. Watch whether the battery icon disappears with the reading.
4. Voltmeter AC/DC zero with shorted probes.
5. Ohmmeter open/short entry behavior.
6. Oscilloscope shorted input at the same `0.1 V/div`, `12.5 us` setting.

