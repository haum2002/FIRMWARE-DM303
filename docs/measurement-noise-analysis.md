# DM303 measurement noise and zeroing analysis

Status: first conservative firmware experiment added in `relay-settle-exp1`.
This document records current evidence and safe next steps so the firmware is
not falsely marked as fully optimized.

## Reported symptoms

- Ammeter can blank after switching DC -> AC -> DC.
- Zeroing is unstable or ineffective across DC and AC meter modes.
- Oscilloscope shows high/low noise that cannot be cleared.
- Fuel injector test has unwanted fine noise/vibration and must be treated as a
  safety risk until the output path is verified.
- True RMS cannot be trusted while acquisition noise and zeroing are unstable.

## Important safety note

Do not use experimental firmware for actuator-driving functions such as fuel
injector, relay, ignition, generator, or adjustable signal output on a real
vehicle/load until the output waveform is checked on a bench instrument.

If the injector output is producing unwanted ultrasonic-like vibration, the safe
state is to stop using that output until timer/PWM/output-driver behavior is
mapped. A software claim that noise is removed is not acceptable without bench
waveform proof.

## Evidence from UI resources

The official English resource confirms that zeroing and mode switching are core
measurement features:

- `TEXT_EN.DAT` entry 23: voltage screen advertises `<F1> Zeroing`.
- `TEXT_EN.DAT` entry 32: current screen advertises `<F1> Zeroing`.
- `TEXT_EN.DAT` entries 220-229: voltage measurement uses `<F1>` for zeroing
  and `<Fn>` for DC/AC/waveform switching.
- `TEXT_EN.DAT` entries 234-243: current measurement uses `<F1>` for zeroing
  and `<Fn>` for DC/AC switching.
- `TEXT_EN.DAT` entries 278-295: oscilloscope uses the current measured value
  and auto-converted voltage range.

This means the reported failure is not a missing user feature. It is likely a
runtime state/acquisition fault.

## Static firmware evidence

Current static scans of the V4.0 binary show many references to GPIO, timers,
SPI, CAN, USART, DMA, and RCC, but no direct literal references to the usual
STM32 ADC bases:

- `0x40012400` ADC1: no direct literal hit.
- `0x40012800` ADC2: no direct literal hit.
- `0x40013c00` ADC3: no direct literal hit.
- GPIO/TIM/SPI/CAN/USART references are present.

This does not prove that no ADC is used. The ADC address could be built
indirectly, or the meter may use an external analog front-end. It does mean that
a simple internal-ADC patch would be speculative.

Likely low-level candidate areas found during static inspection:

- `0x08017bc4`: USART3-like sampling/storage path.
- `0x08017c26`: timer-driven counters/state path.
- `0x08017d32`: GPIO/key/state debounce path, possibly related to mode
  switching.
- `0x08017e90`: timer/state reset path.
- `0x08018b56` and `0x08018bca`: GPIO/TIM/output-control style paths, likely
  relevant to signal or actuator output behavior.

These are candidates only. They are not confirmed safe patch points.

## Relay/zeroing evidence added after hardware feedback

The user reported that calibration/zeroing causes about 2-4 relay clicks. That
changes the most likely failure path: zeroing probably changes a relay/range
matrix, then captures offset before the analog path is fully settled.

Static inspection found a strong relay/range-selector candidate:

- `0x0801f0f2`: toggles GPIOB/GPIOD bits and waits between changes.
- `0x0801f19a`: calls `0x0801f0f2` repeatedly for mode/range states.
- The mode routine contains groups of three selector calls, matching the
  reported multiple relay clicks during zeroing or mode changes.

The `relay-settle-exp1` profile extends only existing waits in
`0x0801f0f2`. It does not change GPIO order, pin masks, updater code, or
measurement math:

| Offset | Official wait | Patched wait | Purpose |
|---:|---:|---:|---|
| `0x0f10a` | `2` ticks | `5` ticks | pre-switch settle |
| `0x0f146` | `3` ticks | `8` ticks | selector bit settle |
| `0x0f192` | `10` ticks | `50` ticks | final post-relay settle before acquisition resumes |

This patch is intended to reduce blank/freeze after DC -> AC -> DC switching
and prevent zeroing from capturing a bad offset too early. It is not a complete
analog noise or RMS accuracy fix.

## Most likely root causes

1. Shared acquisition state is not cleared when changing modes.
   DC/AC/current/oscilloscope may share ring buffers, RMS/filter state, zero
   offset, range state, or validity flags. If stale AC/RMS state remains when
   returning to DC current, the display can wait for a valid reading and go
   blank.

2. Zeroing stores a bad offset or applies it in the wrong range/mode.
   If zeroing is captured while auto-range/filter data is unstable, the stored
   zero offset can make all later readings unstable.

3. Auto-range and validity flags can get stuck.
   Blanking after DC -> AC -> DC is consistent with a display routine that
   suppresses output until the measurement engine reports a stable valid value.

4. Oscilloscope and meter modes may share the same noisy front-end.
   Firmware smoothing can make DMM readings calmer, but oscilloscope mode should
   show real noise. Completely clean `0.00001 V/div` at `1 us` is not physically
   realistic without hardware limits, shielding, bandwidth limiting, and known
   input conditions.

5. Injector/output noise is likely timer/PWM/output-driver behavior, edge
   ringing, ground return, or front-end coupling.
   This cannot be safely fixed by changing UI/resources or generic fault
   handlers.

## Required bench tests before a real fix can be claimed

- Short probes together and test zeroing in DC voltage, AC voltage, DC current,
  AC current, and resistance.
- Test DC -> AC -> DC on ammeter at least 50 cycles with probes shorted and with
  a stable known current source.
- Test oscilloscope with input shorted, open, and connected to a known clean
  reference.
- Capture injector output with an external oscilloscope across the real load or
  a safe dummy load.
- Compare official V4.0, `boot-acceptance`, `anti-freeze-exp1`, and current
  `relay-settle-exp1` with the same test sequence.

## Patch direction

The first safe patch now targets relay/range settling, not analog math:

- Extend existing waits after relay/range switching.
- Keep pin order and final pin states unchanged.
- Keep the bootloader/updater untouched.

The next patch should target measurement state recovery:

- On every mode change, clear zero-pending flags, valid-reading flags, ring
  buffers, RMS/filter accumulators, overrange state, and display blanking state.
- Ignore the first samples after switching mode/range.
- Add a timeout: if no valid reading appears after a fixed window, reinitialize
  the measurement engine instead of leaving the display blank.
- Make zeroing conditional: do not accept zero offset unless the input is stable
  for several consecutive samples.

This requires confirmed runtime addresses for the measurement state variables or
the mode-switch handler. Those addresses are not confirmed yet.
