# DM303 power rail and cranking ghost-voltage analysis

Status: new hardware-facing diagnostic path added after the observed cranking
reading of about `2.88 V`.

## Observation

- User observed cranking mode showing real-time voltage around `2.88 V`.
- The internal battery is described as a nominal `3.7 V` cell.
- The device battery icon currently shows about `3/4` bars.

## Current interpretation

The `2.88 V` value in cranking mode must not be treated as proven internal
battery voltage yet. Cranking mode is designed for a vehicle battery test, and
the original manual text says to connect the main detection lead and battery
clamp before monitoring. If the cranking input is open, a high-impedance analog
front-end can float and display a ghost voltage caused by internal bias,
divider leakage, protection components, relay/mux leakage, PCB contamination,
or coupling from the device supply rail.

The `3/4` battery indicator supports this caution. A healthy single Li-ion cell
can sit around `3.7 V` nominal and still show partial bars. If the internal
battery were truly collapsing to `2.88 V` under normal load, the device would
usually be close to cutoff, unstable, or unable to boot reliably.

## Separating firmware fault from hardware fault

Run these tests with no vehicle attached first:

| Test | Expected result | Meaning if abnormal |
|---|---|---|
| Measure internal cell at battery terminals with an external DMM | Around `3.4-4.2 V` depending charge | If near `2.8-3.0 V` under load, internal battery or power path is weak |
| Cranking input open | May float; any value here is not proof | A stable repeatable `2.88 V` suggests bias/leakage/coupling |
| Cranking input shorted to the correct ground/negative clamp | Should drop close to `0 V` | If it remains high, suspect leakage, damaged protection, stuck mux/relay, or ADC/reference fault |
| Cranking input connected to a known current-limited DC source | Should track source through the expected divider scale | Offset or nonlinear error suggests calibration/divider/reference problem |
| Repeat after full charge and after battery drops one bar | Cranking open ghost may change if coupled to supply rail | Strong correlation with internal battery level suggests rail leakage into measurement front-end |

Use only the cranking/vehicle-voltage input path for these tests. Do not inject
voltage into current, injector, relay, ignition, or signal-output terminals.

## Firmware mitigation that is safe to consider

- Treat cranking readings below a sane connected-battery threshold as
  "connect battery" instead of a valid vehicle result.
- Keep the display/status refresh alive even if the cranking measurement path
  reports invalid data.
- Add hysteresis or a short stability window before accepting cranking voltage.
- Do not silently subtract a fixed `2.88 V` offset. That would hide a hardware
  leak and make real low-voltage tests wrong.

The current `stream-recovery-exp13` firmware addresses retry-loop
freeze/latency, routes low byte-IO through a bounded `0x0fa0` wrapper that
returns `0xff` when ready flags never appear, clamps two high-level command
retries to `0x60`, routes command `0x40` busy failure to the existing
error/clear path, and clears stale stream/status bits on both the error cleanup
path and the mode/range entry. It does not yet patch a cranking voltage
threshold or ADC/math calibration hook because the safe runtime hook is not
confirmed.

## Resource/manual update already applied

The Malay cranking manual text now warns that if the cable/clip is not
connected, the reading can float because the input is open and must not be
treated as real battery voltage.

## Hardware repair indicators

Treat the problem as likely hardware if any of these are true:

- Cranking input shorted to the correct negative clamp still displays a stable
  nonzero voltage.
- The same ghost voltage changes with humidity, pressure on the PCB, or after
  cleaning connectors.
- Internal battery voltage measured externally sags heavily during mode
  switching, relay clicks, or screen brightness changes.
- Ohmmeter/continuity beeps by itself even with clean open probes.
- Ammeter blank/freeze is worst on the green `A/mA/uA` path and correlates with
  relay clicks or digital fuse/protection activity.

If those signs are present, firmware can reduce UI hang and reject impossible
readings, but the actual accuracy/noise fix must include hardware inspection of
the analog input, relay/mux path, protection network, shunt/current path,
grounding, internal battery, and regulator ripple.
