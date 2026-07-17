# DM303 Hardware Photo Analysis - 2026-07-15

Source photos:

```text
hardware_photos/whatsapp-2026-07-15/
```

The photos were extracted from:

```text
C:\Users\Administrator\Downloads\WhatsApp Unknown 2026-07-15 at 12.07.37 AM.zip
```

## Visible Board Architecture

- Main MCU: Nation-branded N32G45x/N32G455-class MCU marking is visible but
  partly obscured by lighting and chip texture.
- Main clocking: an `8.000` MHz crystal is near the MCU, with a separate
  `32.768` kHz crystal nearby.
- External memory: a `25VQ64CSIG` SPI flash is visible near the SD/USB area.
- Analog/protection area: multiple HF 4.5 V relays, MOSFETs, diode clamps,
  MOV/TVS-style protection, fuses marked `F1/F2/F3/F4`, large yellow safety
  capacitors, and high-value resistor networks are visible.
- Analog support ICs visible in photos include `LM393G`, `SGM8054XS14`,
  `SGM8552`-marked parts, and other small ICs around the relay/input section.
- Power/backup area: a CR1220 cell marked `BAT1` is separate from the `LIBAT`
  lithium battery connector.
- Input path: the current/ammeter path is physically separate from the voltage
  and signal paths and passes through protection, relay, fuse/current-control,
  and low-ohm/high-current components.

## What This Means For The Failed V4.0.1f Test

The `V4.0.1f` field result is important:

- UI/resource smear was fixed by restoring `system/DM30XDB1.dat`.
- Meter stability, AC-to-DC ammeter latency, and noise did not improve.
- The device lost Malay/dark resources because exp18 intentionally preserved
  official `TEXT_SP.DAT` and `icon-SP.dat` to isolate the UI fault.

That result means the remaining measurement fault is probably not in the same
resource/UI layer. The stronger candidates are:

- analog front-end leakage or protection loading;
- relay contact state or range-selection settling that is not represented by
  the simple `2/3/10` delay constants already inspected;
- current-path digital fuse/current-control state not clearing cleanly after
  AC/DC mode changes;
- power/reference rail disturbance during current-mode switching;
- a measurement/status protocol path between the analog section and the main
  MCU that the current patch does not yet hook;
- calibration/reference data stored outside the main firmware binary, possibly
  in external flash or factory data.

## Specific Symptom Mapping

### Ammeter green input, AC -> DC delay

The green current input is the most suspicious path because it uses the
highest-risk protection/current circuitry. A 30-second blank after AC -> DC can
be caused by a hardware state that remains busy until a timeout, fuse/protection
state clears, relay state settles, or a measurement packet becomes valid again.

The previous firmware patches changed high-level retry/timeout paths, but the
field result shows those hooks are either not the active path or not sufficient.

### Reading and battery icon disappear together

This still points to shared acquisition/status refresh. The battery icon may be
updated from the same service/status transaction as the live reading. If that
transaction stalls, both the number and the battery icon can disappear even if
the LCD renderer itself is healthy.

### Cranking mode around 2.88 V while internal battery is 3.7 V

Do not assume this is a direct battery read. It may be a divided internal node,
selected test input, protection leakage, or stale measurement value. However,
seeing this with no valid external signal is a strong clue to check leakage,
reference rails, and battery/power isolation.

### Zeroing relay clicks

The audible 2-4 relay clicks during zero/calibration show that zeroing is a real
hardware auto-zero/range sequence, not just a software subtraction. A firmware
math-only patch cannot fix dirty contacts, leakage, rail droop, or a protection
state that does not clear.

## Required Physical Checks Before More Blind Firmware Patches

Record these on the same firmware version before and after any change:

```text
Firmware marker:
Internal Li-ion voltage:
CR1220 voltage:
3.3 V rail idle:
3.3 V rail during ammeter DC -> AC -> DC:
Analog reference rail if accessible:
Ammeter AC -> DC blank time:
Does battery icon disappear with reading: yes/no
Voltmeter DC zero min/max:
Voltmeter AC zero min/max:
Oscilloscope 0.1 V/div 12.5 us noise +peak/-peak:
```

Physical checks:

- Inspect and clean flux/moisture/dust around the green ammeter input,
  relay area, MOV/TVS parts, fuse parts, and high-value resistors.
- Check relay solder joints and connector spring contacts.
- Check whether CR1220 is weak or leaking.
- Check whether the Li-ion connector or battery rail drops during relay clicks.
- Check whether any large resistor/fuse/PTC/current-control part heats after
  ammeter mode switching.
- Test with no external load, then with a known dummy load only.

## Current Firmware Direction

`V4.0.1g` restores the UI resources that exp18 removed:

- visible marker: `V4.0.1g`;
- profile: `stability-exp19-ui-ms`;
- keeps exp18 bounded recovery patches;
- keeps restored `system/DM30XDB1.dat`;
- restores Malay `TEXT_SP.DAT`;
- restores Malay/dark `icon-SP.dat`.

This build is not proof that analog accuracy/noise is solved. It is a corrected
test package so the UI/language regression no longer distracts from the
hardware/protocol investigation.
