# DM303 V4.0.1b next patch decision

Status: exp14 generated for stream/status, mode/range stale-state recovery, and
the reported ammeter AC -> DC latency. Do not generate an ADC/RMS/math firmware
patch in this pass.

## Why

- Current field observations still fail on blank/freeze:
  - `ammeter_green` AC: blank event present.
  - `ammeter_green` DC: blank event present.
  - `ohmmeter` open: blank event present.
- The latest oscilloscope observation `+0.07 V / -0.03 V` is better than the
  earlier V4.0/V4.0.1b observation and passes the V3.16-style `0.13 V`
  peak-to-peak target, but it does not prove the meter blank/freeze path is
  fixed.
- Cranking open `2.88 V` is treated as floating/leakage evidence until the
  same input is tested shorted to the correct negative clamp and against a
  known current-limited source.
- Static audit still finds no direct ADC1/ADC2/ADC3 base literal hit, so an
  internal ADC averaging or True RMS math patch would be speculative.
- The known safe firmware changes are already present in `stream-recovery-exp14`
  and verified by byte guards:
  - stream/status retry fail-fast patches,
  - command `0x40` busy failure routed to the existing error/clear block,
  - low byte-IO redirected through a bounded `0x0fa0` wrapper,
  - command retry clamp from `0x95`/`0x87` to `0x60`,
  - stream error cleanup clears flag bits `0` and `1` from `0x2000022c`,
  - mode/range entry clears the same stale bits before relay/range switching,
  - stream/status stale-busy early return is bypassed so a fresh transaction
    can start,
  - two long current/meter switch gates are capped from `0x3e80` to `0x0640`,
  - fault/default recovery stub,
  - guarded boot-logo delay,
  - Malay text/resources and safe RGB565 resource edits.

## What would justify a later patch

Generate another firmware patch only after at least one additional safe hook is confirmed:

- A valid-reading timeout hook that refreshes UI/header even when the
  acquisition path is invalid.
- A measurement buffer or RMS accumulator reset hook with known input/output
  registers and safe caller behavior.
- A cranking connected-input threshold hook that rejects open/floating input
  without subtracting a fixed `2.88 V` offset.

## Required next data

- Ammeter green DC -> AC -> DC for at least 50 cycles, with `blank_events`,
  recovery time, and whether the battery icon disappears.
- Cranking open, short-to-negative, and known limited-source readings.
- Voltmeter/ammeter DC and AC readings from at least two known reference values
  per mode so gain/offset can be separated.
- Oscilloscope noise with input shorted and open using the same scale/timebase.
- Injector/output waveform on dummy load only.

Until that data or a confirmed hook is available, further binary math patches
would increase brick/accuracy risk without proving they address the active
blank/freeze failure.
