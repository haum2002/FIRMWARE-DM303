# V4.0.1 Repair-I Ammeter Latency Analysis

Date: 2026-07-15

## Field Symptom

- Ammeter AC -> DC on the green mA/uA path can take around 30 seconds before
  numeric readings return.
- Earlier package line also produced higher noise and text smear/calit.
- The failed `V4.0.1h` package still carried modified UI/resources and
  stream/IO recovery bytes, so it was not a clean measurement baseline.

## Function Mapping

Static analysis maps function `0x0802d194` to the ammeter screen:

```text
0x0802d1fa -> draw text entry 27: AC
0x0802d220 -> draw text entry 29: 20A(Yellow)
0x0802d232 -> draw text entry 30: mA(Green)
0x0802d2f0 -> calls relay/range selector 0x0801f0f2
0x0802d2fe -> calls mode/range routine 0x0801f19a
0x0802d37a -> calls relay/range selector 0x0801f0f2
```

The same function contains:

```text
0x0802d1a4: movw r0, #0x3a98
0x0802d1c0: movw r0, #0x3a98
0x0802d1da: movs r0, #0xf0
```

The two `0x3a98` guards were lowered in Repair-H. Repair-I adds the `0x1d1da`
change because `0xf0` is stored as the sample acquisition count used by the
post-switch numeric update loop.

## Repair-I Byte Changes

```text
0x1d1a4: 43 f6 98 20 -> 40 f2 dc 50
0x1d1c0: 43 f6 98 20 -> 40 f2 dc 50
0x1d1da: f0 20       -> 40 20
```

The last change means:

```text
movs r0, #0xf0  ; 240 samples
movs r0, #0x40  ; 64 samples
```

If the effective sampling cadence collapses near 8 samples per second, a
240-sample acquisition window can match the reported roughly 30 second blank.
Reducing the window should make the result visible faster, but it can also make
current readings less averaged. This is why the change is isolated and must be
tested before any broader filter or True RMS patch.

## Clean Baseline Rules

Repair-I intentionally keeps these official:

- stream/read helper;
- lower byte-IO helper;
- command retry counters;
- stream busy gate;
- relay settle timing;
- UI render loop;
- boot-logo timing;
- all official V4.0 system resources.

This prevents the latest test from mixing measurement behavior with the failed
Malay/dark/logo/resource layer.

## Validation Result

```text
repair_candidate_check=ok
measurement_candidate_gate=ok
preflash_check=ok
official_v4_system_resources=match
ui_render_stream_io_relay_boot_windows=official
```

## Next Decision After Device Test

- Latency improved, noise acceptable: keep `0x40` and continue with AC zero and
  oscilloscope noise analysis.
- Latency improved, noise worse: retune sample window upward to `0x80` or
  `0xc0`.
- No latency change: revert `0x1d1da` and trace deeper into the acquisition or
  status helper path.
