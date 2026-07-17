# DM303 manual function map for V4.0.1b work

Source studied: `C:\Users\Administrator\Downloads\Documents\AUTOOL-DM303-Manual.pdf`.

## Meter modes

- Voltmeter supports DC voltage, AC voltage, and oscilloscope switching through
  the function key path. Zeroing is expected through the meter UI.
- Ammeter supports DC/AC switching. The green `mA/uA` input is for lower current
  ranges and uses the self-resetting protection path; the high-current input is
  separate.
- Ohmmeter/continuity/diode/frequency share the measurement engine and must not
  be treated as isolated UI-only modes when blank/freeze appears.

## Signal and output modes

- Oscilloscope bandwidth is limited, so firmware can reduce stale-state hangs
  and display noise handling but cannot guarantee mathematically perfect
  `0.000 V` physical noise at every gain/timebase.
- Signal/wave generator outputs square/sine style waveforms over the supported
  range. A dirty waveform can be caused by timing state, output loading, power
  rail noise, or hardware output filtering, not only display math.
- Injector, relay, ignition, CAN/K/LIN, and generator tests must be validated
  with dummy load or external scope before use on real vehicle circuits.

## Manual clues used by exp14

- The manual confirms that current mode has a real DC/AC switching path, so the
  reported ammeter AC -> DC 30-second blank is treated as a measurement-stream
  recovery problem, not only a visual label issue.
- The green current jack path has protection/fuse behavior, matching the field
  observation that blank/freeze is worst there after overload/spike-like events.
- The frequency/high-impedance warning supports the hardware hypothesis: open
  or floating inputs can show induced/ghost voltage, so firmware must avoid a
  fixed fake subtraction such as removing `2.88 V` from cranking globally.
- The output-test modes reinforce the need for bounded recovery and fresh
  transactions. A stale busy/status byte can affect more than one visible mode.

## Current firmware response

`stream-recovery-exp14` targets the shared stream/status path:

- release stale stream bits on error cleanup and mode/range entry,
- bypass the stale busy early-return gate so a fresh transaction can start,
- cap two long transition guards that match the observed 30-second blank window,
- keep bootloader/updater and relay GPIO order unchanged.

This document is a function map, not a claim that all manual features are fully
reimplemented or recalibrated.
