# V4.0.1i Repair-C Measurement Analysis

Date: 2026-07-15

Status: FAILED/HOLD.

Field result from user:

- noise became higher;
- ammeter AC to DC remained slow;
- text smear/calit above letters remained visible.

Repair-C must not be continued as the active measurement path.

## Why This Patch Exists

The user identified that failed versions often had incomplete or wrong `system`
resources. That packaging issue is now fixed for repair-line packages. With
resources isolated, the next measurement-side target is physical switching
behavior:

- relay clicks are heard during zeroing/calibration;
- readings can blank after DC/AC/DC switching;
- ammeter green path has the strongest latency/freeze report;
- noise/offset can appear immediately after mode/range changes.

## What Repair-C Changes

Repair-C keeps Repair-B's latency/state recovery:

- bounded low byte-IO helper returns `0xff` on hardware-ready timeout;
- stream/status retry loops fail through existing recovery instead of spinning;
- stale bits `0` and `1` in `0x2000022c` are cleared on recovery paths;
- stale busy early-return in stream transaction is bypassed;
- four current-switch timing guards are capped.

Repair-C adds moderate relay/mux settle timing in selector function
`0x0801f0f2`:

| Offset | Function address | Official / Repair-B | Repair-C |
|---:|---:|---|---|
| `0x0f10a` | `0x0801f10a` | `movs r0,#2` | `movs r0,#5` |
| `0x0f146` | `0x0801f146` | `movs r0,#3` | `movs r0,#8` |
| `0x0f192` | `0x0801f192` | `movs r0,#10` | `movs r0,#50` |

These are existing vendor wait calls, not new invented code paths. Pin order
and final GPIO states are not changed.

## Why It May Help Noise

If the front-end, relay, mux, digital fuse, PTC, shunt path, or protection
network is still settling, sampling immediately after a mode/range switch can
look like noise or failed zeroing. Increasing the existing settle waits gives
the analog path more time to stop moving before the next measurement/status
transaction is trusted.

This is a firmware-side mitigation for switching transient noise. It is not a
guarantee of a physically noise-free input.

## What It Does Not Claim

Repair-C does not patch:

- ADC register configuration;
- True RMS math;
- calibration tables;
- oscilloscope sampling engine;
- injector/generator PWM purity;
- hardware leakage or damaged protection components.

Those need confirmed code hooks or bench measurements before any binary patch
is safe.

## Build And Check

```powershell
python tools\dm303_v401_beta_patch.py --profile v401h-repair-c --out-dir firmware-candidates\v4.0.1h-repair-c
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-c --profile v401h-repair-c
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-c\sd-root --profile v401h-repair-c
```

Expected check:

```text
repair_candidate_check=ok
official_v4_system_resources=match
```

## Success Criteria

The candidate should be judged only against these points:

- AC to DC ammeter transition no longer blanks for tens of seconds;
- battery icon and numeric reading do not disappear together during normal
  recovery;
- zeroing immediately after relay clicks is more stable;
- UI smear does not return because official resources are used.

Do not judge it as a complete noise/accuracy/True RMS fix unless those are
measured and proven separately.
