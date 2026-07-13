# DM303 measurement noise and zeroing analysis

Status: stability-first test build added in `force-enhanced-exp4`.
This document records current evidence and safe next steps so the firmware is
not falsely marked as fully optimized.

## Physical comparison evidence from V3.16 testing

The user later tested BT100MM V3.16 and MT100MM V3.0 firmware on the same
device path and compared it with official V4.0 and current V4.0.1b. These
bench/device observations are now treated as the strongest evidence because
they come from physical behavior, not only static binary inspection.

| Area | V3.16 behavior | V4.0 / V4.0.1b behavior | Meaning for V4.0.1b work |
|---|---|---|---|
| DC -> AC -> DC switching in voltmeter and ammeter | Smooth and fast; no blanking seen in the reported test | Blanking/freezing can occur, especially after DC -> AC -> DC in ammeter | Root cause is likely mode/acquisition state handling, not only relay delay |
| Reading offset | About `0.010 V` AC and `0.020 V` DC error | Similar reported offset | This looks like calibration/front-end offset shared across versions, not a V4-only regression |
| Oscilloscope noise at `0.1 V/div`, `12.5 us` | About `+0.08 V` and `-0.05 V` | About `+0.15 V` and `-0.09 V` | V3.16 likely has calmer acquisition/filter/display behavior in scope path |
| Internal battery reading | Less stable | Not the current best reference | Do not port V3.16 battery behavior blindly |
| Ohmmeter and continuity | Continuity can beep by itself without touch | V4 line still has stability issues, but V3.16 is not clean here | V3.16 is useful as a switching/noise clue, not as a full golden firmware |

Immediate conclusion: V3.16 is a useful reference for smoother DC/AC switching
and lower oscilloscope display noise, but it is not safe to copy wholesale
because resistance, continuity, and battery behavior are weaker.

## Reported symptoms

- Ammeter can blank after switching DC -> AC -> DC.
- The blank state is not limited to the numeric reading: the battery icon can
  disappear at the same time and only returns when the numeric value returns.
- Ohmmeter can enter the same blank state when opening ohmmeter mode.
- Blank/freeze can happen on any meter mode after spike, overload, or abnormal
  signal handling.
- The worst repeated case reported so far is ammeter mode through the green
  `A/mA/uA` input.
- Zeroing is unstable or ineffective across DC and AC meter modes.
- Oscilloscope shows high/low noise that cannot be cleared.
- Latest observed oscilloscope noise on the current V4.0.1b line is about
  `+0.07 V` and `-0.03 V`; this is better than the earlier V4.0/V4.0.1b
  `+0.15 V` / `-0.09 V` observation, but it does not prove the meter
  acquisition freeze is fixed.
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

Current `force-enhanced-exp4` does not patch ADC averaging, RMS math, True RMS
math, or EMI filter code. That is intentional: no confirmed measurement-engine
hook has been found yet. The package improves recovery from fault paths, changes
a confirmed mode-switch helper difference between V3.16 and V4.0, restores the
stronger `8/12/100` relay/range settling test profile, and adds a guarded
boot-logo resource delay while keeping unverified ADC/filter/math code
untouched.

Latest read-only probe after the battery-icon observation confirms the same
constraint: the V4.0.1b binary still follows the V4.0 peripheral/acquisition
layout, apart from the known guarded patches. The symptom where the battery
icon disappears together with the numeric value therefore cannot be explained as
a cosmetic text/icon resource issue. It points back to a runtime path that stops
servicing the normal display/status refresh while waiting for measurement data,
range/protection recovery, or a valid-state flag.

Static disassembly has identified math/scaling-heavy routines, but no safe patch
contract yet. Those routines are not modified in `force-enhanced-exp4`; changing
them without a confirmed input/output contract could make True RMS and DC/AC
calibration worse while still leaving the freeze intact.

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

The earlier `relay-settle-exp1` profile extended only existing waits in
`0x0801f0f2`. After user feedback that instability remained,
`force-stable-exp2` used a more conservative timing set. The later physical
V3.16 comparison showed that V3.16 and official V4.0 both use `2/3/10` waits,
so the current `v316-switch-exp3` build no longer uses the long-delay profile
as the main fix.

| Offset | Official wait | Patched wait | Purpose |
|---:|---:|---:|---|
| `0x0f10a` | `2` ticks | `8` ticks | pre-switch settle |
| `0x0f146` | `3` ticks | `12` ticks | selector bit settle |
| `0x0f192` | `10` ticks | `100` ticks | final post-relay settle before acquisition resumes |

The old long-delay profile was intended to reduce blank/freeze after
DC -> AC -> DC switching and prevent zeroing from capturing a bad offset too
early. It is expected to increase switching/zeroing latency. It is retained as
a diagnostic profile, not as the current default and not as a complete analog
noise or RMS accuracy fix.

## V3.16 timing comparison update

Static comparison after the physical V3.16 report found the closest known
relay/range selector and mode-switch routines:

| Firmware | Selector candidate | Mode routine candidate | Observed waits |
|---|---:|---:|---:|
| V3.16 | `0x0801e1ac` | `0x0801e29a` | `2/3/10` ticks |
| Official V4.0 | `0x0801f0f2` | `0x0801f19a` | `2/3/10` ticks |
| V4.0.1b `v316-switch-exp3` | `0x0801f0f2` | `0x0801f19a` | `2/3/10` ticks |
| V4.0.1b `force-enhanced-exp4` | `0x0801f0f2` | `0x0801f19a` | `8/12/100` ticks |

This is a key correction: the smoother V3.16 DC/AC switching is not explained
by longer relay/range waits, because V3.16 and official V4.0 use the same
observed waits. The old long-wait V4.0.1b profile remains available as a
diagnostic mitigation for bad zero capture and post-switch blanking, but it
should not be described as the proven root-cause fix. It may also add latency.

Further static comparison found one stronger V3.16/V4.0 difference:

- V3.16 mode tail checks a sub-mode value before using helper `0x0801e254`.
  Outside sub-mode `4`, it calls the selector path directly.
- V4.0 mode tail calls helper `0x0801f0ac` directly from the corresponding
  flag path.
- `v316-switch-exp3` wraps V4 helper `0x0801f0ac` so those existing call sites
  perform `selector(1, flag)` directly. The call sites and updater are left
  unchanged.

The next safe diagnostic comparison is therefore:

- Test `force-enhanced-exp4`: current build with V3.16-style helper wrapper,
  stronger `8/12/100` selector timing, and guarded boot-logo settling delay.
- Test `v316-switch-exp3`: comparison build with V3.16-style helper wrapper and
  official/V3.16 `2/3/10` selector timing.
- Test `force-stable-exp2`: old long-delay mitigation with `8/12/100`.
- Compare both on the exact same DC -> AC -> DC ammeter sequence and
  oscilloscope noise setting.

If `force-enhanced-exp4` still fails while V3.16 succeeds, the next patch must
target mode-change state, filter buffers, validity flags, or measurement engine
reset points. Adding more relay delay after that would likely only increase
latency.

## Most likely root causes

1. Main measurement/acquisition path can block the UI refresh loop.
   The battery icon disappearing with the numeric reading means the display
   header/value refresh is likely not being serviced. This is stronger evidence
   for a blocked acquisition/status wait or global valid-state stall than for a
   simple "value text was not drawn" bug.

2. Shared acquisition state is not cleared when changing modes.
   DC/AC/current/oscilloscope may share ring buffers, RMS/filter state, zero
   offset, range state, or validity flags. If stale AC/RMS state remains when
   returning to DC current, the display can wait for a valid reading and go
   blank.

3. Ammeter green input path is a high-risk trigger.
   The repeated failure in `A/mA/uA` suggests a current shunt/range/protection
   path, relay matrix state, or overload flag can hold the acquisition engine
   in a waiting state. This should be prioritized over cosmetic UI work.

4. Zeroing stores a bad offset or applies it in the wrong range/mode.
   If zeroing is captured while auto-range/filter data is unstable, the stored
   zero offset can make all later readings unstable.

5. Auto-range and validity flags can get stuck.
   Blanking after DC -> AC -> DC is consistent with a display routine that
   suppresses output until the measurement engine reports a stable valid value.

6. Oscilloscope and meter modes may share the same noisy front-end.
   Firmware smoothing can make DMM readings calmer, but oscilloscope mode should
   show real noise. Completely clean `0.00001 V/div` at `1 us` is not physically
   realistic without hardware limits, shielding, bandwidth limiting, and known
   input conditions.

7. Injector/output noise is likely timer/PWM/output-driver behavior, edge
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
- When blanking occurs, record whether the battery icon disappears, whether
  buttons still respond, and whether changing mode recovers without power-off.
- Repeat ammeter tests separately on each current input/range. The green
  `A/mA/uA` path is currently the highest-priority trigger.
- Capture injector output with an external oscilloscope across the real load or
  a safe dummy load.
- Compare official V4.0, `boot-acceptance`, `anti-freeze-exp1`,
  `v316-switch-exp3`, `force-stable-exp2`, and current `force-enhanced-exp4` with the same test
  sequence.

## Patch direction

Relay/range settling was the first conservative diagnostic patch, not a proven
root-cause fix:

- Extend existing waits after relay/range switching.
- Keep pin order and final pin states unchanged.
- Keep the bootloader/updater untouched.
- Use it only to test whether extra settling reduces bad zero capture after
  relay clicks.

The next real patch direction should target measurement state recovery:

- On every mode change, clear zero-pending flags, valid-reading flags, ring
  buffers, RMS/filter accumulators, overrange state, and display blanking state.
- Ignore the first samples after switching mode/range.
- Add a timeout: if no valid reading appears after a fixed window, reinitialize
  the measurement engine instead of leaving the display blank.
- Make zeroing conditional: do not accept zero offset unless the input is stable
  for several consecutive samples.
- On spike/overload in ammeter, especially the green `A/mA/uA` input, clear the
  protection/overrange latch and force a fresh measurement start instead of
  waiting indefinitely.
- Keep the UI/status header refresh independent from measurement validity so the
  battery icon and menu controls do not disappear when acquisition stalls.

This requires confirmed runtime addresses for the measurement state variables or
the mode-switch handler. Those addresses are not confirmed yet.
