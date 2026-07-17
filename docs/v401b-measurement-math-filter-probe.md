# DM303 measurement math/filter probe

Read-only scan for float-heavy measurement, scaling, display, and
possible filter/math functions. This report does not certify a safe
patch point by itself; it narrows the candidates for the next manual
disassembly pass.

## v3.16

- Path: `backup\DM303 V3.16-read only\DM303V316.bin`
- Size: `223276` bytes
- SHA256: `0c8da8396bfdb96a9daf186dd9e458ab4e9b6840046eea178fecdf0f2107770e`
- VFP groups found: `475`

| Function | VFP insns | Float ops | Top mnemonics | Helper calls | Constants |
|---:|---:|---:|---|---|---|
| `0x0802580c` | `109` | `27` | vldr:39, vstr:16, vmov:15, vmul.f32:13, vmov.f32:11, vcvt.u32.f32:8 | 0x0802581a relay/range selector, 0x08025822 relay/range selector, 0x0802582a relay/range selector, 0x08025834 relay/range selector, 0x0802583c relay/range selector, 0x08025844 relay/range selector | 0x080258a6->f32 2100, 0x080258ae->f32 100, 0x080258da->f32 2100, 0x080258e2->f32 100, 0x08025906->f32 2100, 0x08025932->f32 16100, 0x08025962->f32 3000, 0x0802596a->f32 1000 |
| `0x0802d7ce` | `99` | `27` | vldr:22, vmov:21, vmov.f32:16, vmul.f32:13, vcvt.u32.f32:8, vstr:8 | 0x0802da60 relay/range selector, 0x0802da74 mode/range routine, 0x0802dad4 relay/range selector | 0x0802d862->f32 2100, 0x0802d86a->f32 100, 0x0802d8e0->f32 2100, 0x0802d8e8->f32 100, 0x0802d908->f32 2100, 0x0802d930->f32 16100, 0x0802d95e->f32 3000, 0x0802d966->f32 1000 |
| `0x080297d4` | `98` | `27` | vmov:23, vldr:22, vmov.f32:16, vmul.f32:13, vcvt.u32.f32:8, vdiv.f32:6 | 0x08029a2a relay/range selector, 0x08029a3e mode/range routine | 0x08029830->f32 2100, 0x08029838->f32 100, 0x08029860->f32 2100, 0x08029868->f32 100, 0x080298cc->f32 2100, 0x080298f4->f32 16100, 0x08029922->f32 3000, 0x0802992a->f32 1000 |
| `0x08032b72` | `95` | `27` | vmov:29, vldr:22, vmov.f32:16, vmul.f32:13, vcvt.u32.f32:8, vdiv.f32:6 | 0x08032db0 relay/range selector, 0x08032dc4 mode/range routine, 0x08032fca mode/range routine, 0x08032fe2 mode/range routine, 0x08033022 mode/range routine, 0x08033046 mode/range routine | 0x08032bb0->f32 2100, 0x08032bb8->f32 100, 0x08032be0->f32 2100, 0x08032be8->f32 100, 0x08032c58->f32 2100, 0x08032c80->f32 16100, 0x08032cae->f32 3000, 0x08032cb6->f32 1000 |
| `0x0802ce54` | `58` | `10` | vmov:21, vldr:12, vmov.f32:5, vmul.f32:5, vcvt.u32.f32:4, vstr:4 | 0x0802cf8e relay/range selector, 0x0802cfa2 mode/range routine, 0x0802d076 relay/range selector, 0x0802d25c mode/range routine, 0x0802d264 relay/range selector, 0x0802d286 mode/range routine | 0x0802ce8c->f32 3000, 0x0802ce94->f32 1000, 0x0802cec2->f64 2090.9091, 0x0802ced2->f64 90.909091, 0x0802cf0e->f64 2019.6078, 0x0802cf1e->f64 19.607843, 0x0802cf5a->f64 16019.608, 0x0802cf6a->f64 19.607843 |
| `0x0801e606` | `102` | `2` | vmov:73, vldr:22, vdup.8:3, vpush:1, vcvt.f32.s32:1, vmul.f32:1 | - | 0x0801e626->f64 2.47, 0x0801e636->f64 4095, 0x0801e65a->f64 0.16666667, 0x0801e67e->f64 0.1, 0x0801e6a2->f64 0.55555556, 0x0801e6c6->f64 2.47, 0x0801e6d6->f64 4095, 0x0801e6fa->f64 21.8 |

## v4.0

- Path: `backup\DM303 V4.0-read only\DM303V4.004.bin`
- Size: `203260` bytes
- SHA256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- VFP groups found: `457`

| Function | VFP insns | Float ops | Top mnemonics | Helper calls | Constants |
|---:|---:|---:|---|---|---|
| `0x0802600c` | `115` | `27` | vldr:39, vstr:16, vmov:15, vmul.f32:13, vmov.f32:11, vcvt.u32.f32:8 | 0x08026012 relay/range selector, 0x0802601a relay/range selector, 0x08026022 relay/range selector, 0x0802602a relay/range selector, 0x080262ce mode/range routine, 0x080262d6 relay/range selector | 0x0802607e->f32 2100, 0x08026086->f32 100, 0x080260b2->f32 2100, 0x080260ba->f32 100, 0x080260de->f32 2100, 0x0802610a->f32 16100, 0x0802613a->f32 3000, 0x08026142->f32 1000 |
| `0x08029f94` | `98` | `27` | vmov:23, vldr:22, vmov.f32:16, vmul.f32:13, vcvt.u32.f32:8, vdiv.f32:6 | 0x0802a1ea relay/range selector, 0x0802a1f8 mode/range routine | 0x08029ff0->f32 2100, 0x08029ff8->f32 100, 0x0802a020->f32 2100, 0x0802a028->f32 100, 0x0802a08c->f32 2100, 0x0802a0b4->f32 16100, 0x0802a0e2->f32 3000, 0x0802a0ea->f32 1000 |
| `0x08032dba` | `45` | `17` | vmov.f32:11, vldr:10, vmul.f32:8, vdiv.f32:5, vcvt.u32.f32:4, vmov:3 | 0x08032e90 relay/range selector, 0x08032e9e mode/range routine, 0x080330d0 mode/range routine, 0x0803310e mode/range routine, 0x0803312a mode/range routine, 0x08033166 mode/range routine | 0x08032df0->f32 2100, 0x08032df8->f32 100, 0x08032e20->f32 2100, 0x08032e28->f32 100, 0x08032e48->f32 2100, 0x08032e70->f32 16100 |
| `0x0802d194` | `44` | `17` | vmov.f32:11, vldr:10, vmul.f32:8, vdiv.f32:5, vcvt.u32.f32:4, vstr:4 | 0x0802d2f0 relay/range selector, 0x0802d2fe mode/range routine, 0x0802d37a relay/range selector | 0x0802d250->f32 2100, 0x0802d258->f32 100, 0x0802d280->f32 2100, 0x0802d288->f32 100, 0x0802d2a8->f32 2100, 0x0802d2d0->f32 16100 |
| `0x080324fc` | `44` | `17` | vmov.f32:11, vldr:10, vmul.f32:8, vdiv.f32:5, vcvt.u32.f32:4, vstr:4 | 0x080325fa relay/range selector, 0x08032608 mode/range routine, 0x08032840 mode/range routine, 0x08032848 relay/range selector, 0x08032868 mode/range routine, 0x08032870 relay/range selector | 0x0803255a->f32 2100, 0x08032562->f32 100, 0x0803258a->f32 2100, 0x08032592->f32 100, 0x080325b2->f32 2100, 0x080325da->f32 16100 |
| `0x0801f48e` | `106` | `2` | vmov:73, vldr:21, vld1.16:3, vcgt.f16:2, vcge.f16:2, vpush:1 | - | 0x0801f4ae->f64 2.47, 0x0801f4be->f64 4095, 0x0801f4e2->f64 0.16666667, 0x0801f506->f64 0.1, 0x0801f52a->f64 0.55555556, 0x0801f54e->f64 2.47, 0x0801f55e->f64 4095, 0x0801f582->f64 21.8 |

## repair-i

- Path: `firmware-candidates\v4.0.1h-repair-i\DM303V4.0.1-beta.bin`
- Size: `203260` bytes
- SHA256: `11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953`
- VFP groups found: `457`

| Function | VFP insns | Float ops | Top mnemonics | Helper calls | Constants |
|---:|---:|---:|---|---|---|
| `0x0802600c` | `115` | `27` | vldr:39, vstr:16, vmov:15, vmul.f32:13, vmov.f32:11, vcvt.u32.f32:8 | 0x08026012 relay/range selector, 0x0802601a relay/range selector, 0x08026022 relay/range selector, 0x0802602a relay/range selector, 0x080262ce mode/range routine, 0x080262d6 relay/range selector | 0x0802607e->f32 2100, 0x08026086->f32 100, 0x080260b2->f32 2100, 0x080260ba->f32 100, 0x080260de->f32 2100, 0x0802610a->f32 16100, 0x0802613a->f32 3000, 0x08026142->f32 1000 |
| `0x08029f94` | `98` | `27` | vmov:23, vldr:22, vmov.f32:16, vmul.f32:13, vcvt.u32.f32:8, vdiv.f32:6 | 0x0802a1ea relay/range selector, 0x0802a1f8 mode/range routine | 0x08029ff0->f32 2100, 0x08029ff8->f32 100, 0x0802a020->f32 2100, 0x0802a028->f32 100, 0x0802a08c->f32 2100, 0x0802a0b4->f32 16100, 0x0802a0e2->f32 3000, 0x0802a0ea->f32 1000 |
| `0x08032dba` | `45` | `17` | vmov.f32:11, vldr:10, vmul.f32:8, vdiv.f32:5, vcvt.u32.f32:4, vmov:3 | 0x08032e90 relay/range selector, 0x08032e9e mode/range routine, 0x080330d0 mode/range routine, 0x0803310e mode/range routine, 0x0803312a mode/range routine, 0x08033166 mode/range routine | 0x08032df0->f32 2100, 0x08032df8->f32 100, 0x08032e20->f32 2100, 0x08032e28->f32 100, 0x08032e48->f32 2100, 0x08032e70->f32 16100 |
| `0x0802d194` | `44` | `17` | vmov.f32:11, vldr:10, vmul.f32:8, vdiv.f32:5, vcvt.u32.f32:4, vstr:4 | 0x0802d2f0 relay/range selector, 0x0802d2fe mode/range routine, 0x0802d37a relay/range selector | 0x0802d250->f32 2100, 0x0802d258->f32 100, 0x0802d280->f32 2100, 0x0802d288->f32 100, 0x0802d2a8->f32 2100, 0x0802d2d0->f32 16100 |
| `0x080324fc` | `44` | `17` | vmov.f32:11, vldr:10, vmul.f32:8, vdiv.f32:5, vcvt.u32.f32:4, vstr:4 | 0x080325fa relay/range selector, 0x08032608 mode/range routine, 0x08032840 mode/range routine, 0x08032848 relay/range selector, 0x08032868 mode/range routine, 0x08032870 relay/range selector | 0x0803255a->f32 2100, 0x08032562->f32 100, 0x0803258a->f32 2100, 0x08032592->f32 100, 0x080325b2->f32 2100, 0x080325da->f32 16100 |
| `0x0801f48e` | `106` | `2` | vmov:73, vldr:21, vld1.16:3, vcgt.f16:2, vcge.f16:2, vpush:1 | - | 0x0801f4ae->f64 2.47, 0x0801f4be->f64 4095, 0x0801f4e2->f64 0.16666667, 0x0801f506->f64 0.1, 0x0801f52a->f64 0.55555556, 0x0801f54e->f64 2.47, 0x0801f55e->f64 4095, 0x0801f582->f64 21.8 |

## Current Interpretation

- The V4.0 and Repair-I math candidates are byte-identical except for
  the latency guard offsets and the ammeter acquisition-window byte
  already checked by `dm303_measurement_candidate_gate.py`.
- Several V4.0 functions contain coherent float scaling constants such as
  `2100`, `100`, `4095`, `0.1`, `1.5`, and `21.8`; these are likely
  display/scaling/calibration paths, not confirmed ADC sampling hooks yet.
- No safe zero-deadband, RMS, or oscilloscope filter patch is selected by
  this probe alone. A patch must first prove which function maps to
  voltage AC, current AC, scope, or cranking.

