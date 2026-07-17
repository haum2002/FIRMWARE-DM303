# DM303 V4.0.1b baseline reassessment - 2026-07-15

Status: analysis-only. No new flash package is promoted by this document.

Correction after user feedback: the newest package has not been tested by the
user and must not be described as accepted, successful, or ready. The analysis
below only identifies a safer baseline direction from earlier known reports.

## Inputs checked

Firmware references:

| Image | Path | Size | SHA-256 |
|---|---:|---:|---|
| V3.16 backup | `backup/DM303 V3.16-read only/DM303V316.bin` | 223276 | `0c8da8396bfdb96a9daf186dd9e458ab4e9b6840046eea178fecdf0f2107770e` |
| V4.0 backup | `backup/DM303 V4.0-read only/DM303V4.004.bin` | 203260 | `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158` |
| V3.13 backup | `backup/SD-file_DM303_update_US240104-read only/DM303-V3.13.bin` | 221704 | `c62dbd24bc0627cba733151fb278d27ffdf7be9ea5c97a0c0ea4c16835387002` |
| Current final folder image | `dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin` | 203260 | `b9f54dbc46b25a8f9da7af85bc12c8eb591d7806372f10487b1aa717150ac45f` |

Other evidence:

- Hardware photos zip: `C:\Users\Administrator\Downloads\WhatsApp Unknown 2026-07-15 at 12.07.37 AM.zip`.
- Extracted hardware photos: `hardware_photos/whatsapp-2026-07-15/`.
- Manual PDF: `C:\Users\Administrator\Downloads\Documents\AUTOOL-DM303-Manual.pdf`.
- Manual text extract: `docs/dm303-manual-extract-2026-07-15.txt`.
- Profile matrix: `analysis/v401b-profile-matrix/profile-summary.csv`.

## Main conclusion

The modified build that best matches the user's description of the earlier,
closer-to-stable `V4.0.1b` is:

```text
profile: stream-recovery-exp14
visible marker: V4.0.1b
sha256: 57204ff3219fe2bbb06df116ce6ffd87593605c66b1e0fd40b803f61d08dcab9
```

Reason:

- It is the last profile still marked `V4.0.1b` before `stream-recovery-exp15`
  introduced visible `V4.0.1c`.
- It contains the first focused attempt at the reported ammeter AC-to-DC delay:
  forced fresh stream transaction after stale busy and capped long current/meter
  switch gates.
- Later profiles added UI, language, resource, and aggressive mode-gate changes
  that made diagnosis harder and did not prove performance improvement.

This is not a claim that `stream-recovery-exp14` fixed the device. The field
analysis still marks it `FAIL`: ammeter green AC-to-DC latency was about 30000
ms with blank events, ohmmeter blanking still occurred, and AC zero/noise were
not corrected. The correct meaning is narrower: exp14 is the least-bad binary
baseline for rebuilding the next controlled candidate.

## What to keep from exp14

Keep these concepts for the next controlled candidate, but rebuild them from the
official V4.0 image instead of layering over the current mixed final folder:

- fault/default self-loop recovery to system reset, because permanent loops can
  turn a small runtime fault into a hard hang;
- high-level stream/status retry fail-fast routing, so acquisition failures can
  return to caller instead of looping on stale data;
- bounded low byte-IO helper that returns `0xff` on ready-timeout;
- command `0x40` and `0x48` retry clamp from `0x95`/`0x87` to `0x60`;
- stream error cleanup clearing stale bits `0` and `1` at `0x2000022c`;
- mode/range entry wrapper clearing those same stale bits before relay/range
  switching;
- stale busy bit `1` early-return bypass at `0x080196be`;
- two long current/meter transition guard caps at `0x0802585e` and
  `0x08025888`.

These are still only recovery and latency hypotheses. They do not directly
recalibrate ADC, True RMS, analog reference, relay contact quality, current
shunt, or external flash calibration data.

## What not to carry forward

Do not carry these into the next measurement-performance baseline:

- `stream-recovery-exp15` immediate mode/range gates at `0x08025812`,
  `0x08025838`, `0x08025862`, and `0x0802588c`;
- `stream-recovery-exp15` stale bit0 bypasses at `0x08019818`,
  `0x080198b4`, and `0x08019950`;
- boot-logo delay wrapper from exp14, because later reports linked boot/loading
  animation and UI-resource behavior to this area;
- false Malay activation by replacing `TEXT_SP.DAT` with a resource that does
  not match the official SP table layout;
- any dark theme or icon/logo modification while performance is being isolated;
- fixed math offsets from one zero reading only, for example subtracting a
  global `0.003 V` AC offset or hiding a cranking `2.88 V` ghost value.

The next performance candidate must use official UI resources first. Malay UI
and dark theme should be added later as a resource-only branch after the meter
path is proven unchanged.

## Manual evidence

The manual supports the hardware/protection hypothesis:

- Voltage input impedance is `2~3Mohm` below 160 V and `10Mohm` above 160 V;
  floating or induced readings are expected in some open-input situations.
- Current `mA/uA` uses the green jack, is limited to below 200 mA, and has a
  `0.5A` self-recovery fuse path.
- Current above 200 mA uses the yellow `A` jack and a separate higher-current
  path.
- Voltage zeroing and current zeroing both require shorted probes plus `[F1]`.
- `[Fn]` is the documented switch for AC/DC current conversion.
- The manual warns that high input impedance can display induced interference
  when no effective signal is connected.

This matters because the worst symptom is on the green ammeter path. That path
is explicitly a protected low-current path, not just a software display range.

## Hardware-photo evidence

The extracted photos show:

- a Nation N32G45x/N32G455-class main MCU;
- an 8 MHz main crystal and 32.768 kHz low-speed crystal;
- a `25VQ64CSIG` external SPI flash near the SD/USB area;
- multiple relays, protection parts, fuses/PTC-style parts, MOV/TVS-style
  clamps, high-value resistors, and analog support ICs;
- CR1220 backup cell separate from the `LIBAT` Li-ion connector;
- the current input path is physically separate and protection-heavy.

Implication: calibration tables, factory constants, or status data may live
outside the main `.bin`. Also, if the analog/protection path is leaking,
contaminated, warm, or latched, a firmware display/math patch cannot produce
true physical zero noise.

## Working diagnosis

The strongest current diagnosis is:

1. The UI/resource layer did cause visible screen smear in later builds, but
   restoring vendor resources removed that symptom without improving measurement.
2. The measurement blank/freeze is probably in shared acquisition/status
   service, because the reading and battery icon disappear together.
3. The green ammeter AC-to-DC delay points to current-path protection, digital
   fuse/PTC state, relay/mux settling, or an acquisition status transaction that
   remains busy until a long timeout.
4. V3.16 switching smoothly does not prove V3.16 math is better; it proves the
   V4.0/V4.0.1 path has a state/recovery regression that must be isolated.
5. Perfect `0.0000 V` on all open/floating/noisy modes is not a safe firmware
   target unless external reference data proves the physical input is actually
   quiet. The safe target is: no blank/freeze, bounded recovery, correct zeroing
   after shorted probes, and calibrated gain/offset from multiple references.

## Next controlled build proposal

Create a new analysis candidate named `v401b-safe-baseline-a` only after this
report is accepted:

- source image: official `backup/DM303 V4.0-read only/DM303V4.004.bin`;
- visible marker: keep `V4.0.1b`, not `V4.0.1c` or later;
- include exp14 recovery core listed above;
- exclude boot-logo delay, exp15 aggressive gates, dark UI, logo edits, icon
  edits, and language slot replacement;
- copy official vendor UI resources unchanged;
- produce it under `analysis/` or `firmware-candidates/` first, not directly
  into `dm303_firmware/DM303-V4.0.1-beta`;
- require a written diff/hash report before any flash attempt.

Only after the user confirms this baseline is visually clean and no worse than
the old `V4.0.1b`, split the work into two branches:

1. measurement branch: isolate AC-to-DC latency, stream recovery, zeroing, and
   calibration behavior;
2. resource branch: Malay text, dark theme, logo, and icon tuning, with no
   firmware-code change.

This separation is necessary because previous builds mixed code, resources,
language, logo, and UI changes, making a failed flash hard to diagnose.
