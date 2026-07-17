# DM303 V4.0.1b bench analysis report

Input CSV: `docs/v401b-field-observations.csv`
Rows: `15`

## Accuracy By Group

| Status | Mode | Range | Unit | Points | Mean Error | Max Abs Error | RMSE | Fit observed = gain*ref + offset | Suggested correction |
|---|---|---|---|---:|---:|---:|---:|---|---|
| PASS | voltmeter | AC_zero | V | 1 | 0.003 | 0.003 | 0.003 | n/a | offset -0.003 V |
| PASS | voltmeter | DC_zero | V | 1 | 0 | 0 | 0 | n/a | offset -0 V |

## Stability And Latency

| Status | Mode | Range | Unit | Rows | Mean Latency ms | Max Latency ms | Noise High | Noise Low | Max Noise p-p | Blank Events |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| FAIL | ammeter_green | AC | A | 1 | n/a | n/a | n/a | n/a | n/a | 1 |
| FAIL | ammeter_green | AC_to_DC | A | 1 | 3e+04 | 3e+04 | n/a | n/a | n/a | 1 |
| FAIL | ammeter_green | DC | A | 1 | n/a | n/a | n/a | n/a | n/a | 1 |
| PASS | ammeter_green | DC_to_AC | A | 1 | 1000 | 1000 | n/a | n/a | n/a | 0 |
| FAIL | firmware_exp14 | field_result | status | 1 | n/a | n/a | n/a | n/a | n/a | 1 |
| PASS | ignition | 0.1V_12.5us | V | 1 | n/a | n/a | 0.12 | 0.01 | 0.11 | 0 |
| FAIL | ohmmeter | open | ohm | 1 | n/a | n/a | n/a | n/a | n/a | 1 |
| PASS | oscilloscope | 0.1Vdiv_12.5us | V | 2 | n/a | n/a | 0.08 | -0.03 | 0.1 | 0 |
| PASS | signal_generator | wave_output | V | 1 | n/a | n/a | n/a | n/a | n/a | 0 |
| PASS | voltmeter | AC | V | 1 | n/a | n/a | n/a | n/a | n/a | 0 |
| PASS | voltmeter | AC_zero | V | 1 | n/a | n/a | 0.003 | 0.001 | 0.002 | 0 |
| PASS | voltmeter | DC | V | 1 | n/a | n/a | n/a | n/a | n/a | 0 |
| PASS | voltmeter | DC_zero | V | 1 | n/a | n/a | n/a | n/a | n/a | 0 |

## Quality Gate

Overall status: `FAIL`

| Status | Mode | Range | Unit | Issues |
|---|---|---|---|---|
| FAIL | ammeter_green | AC | A | FAIL blank_events 1 > 0 |
| FAIL | ammeter_green | AC_to_DC | A | FAIL latency max 3e+04 ms > 2000 ms; FAIL blank_events 1 > 0 |
| FAIL | ammeter_green | DC | A | FAIL blank_events 1 > 0 |
| PASS | ammeter_green | DC_to_AC | A | none |
| REVIEW | cranking | open | V | REVIEW cranking open-input observed 2.88 V; verify with short-to-negative and known source |
| FAIL | firmware_exp14 | field_result | status | FAIL blank_events 1 > 0 |
| PASS | ignition | 0.1V_12.5us | V | none |
| FAIL | ohmmeter | open | ohm | FAIL blank_events 1 > 0 |
| PASS | oscilloscope | 0.1Vdiv_12.5us | V | none |
| PASS | signal_generator | wave_output | V | none |
| PASS | voltmeter | AC | V | none |
| PASS | voltmeter | AC_zero | V | none |
| PASS | voltmeter | DC | V | none |
| PASS | voltmeter | DC_zero | V | none |

## Cranking / Power-Rail Diagnosis

- Cranking open input is high without a matching short/source test: treat as floating/leakage evidence, not as a valid battery reading.

## Interpretation

- A stable offset across multiple reference values suggests calibration/front-end offset.
- A gain far from `1.0` suggests divider/shunt/reference scaling error.
- High blank events with low numeric error suggests recovery/latency, not calibration.
- High noise with probes shorted suggests front-end, ground, shielding, reference, or firmware filtering.
- Do not patch firmware math from one point only; use at least two reference values per mode/range.
- A `REVIEW` accuracy status means the data is strong enough to investigate gain/offset, not that a binary math patch is already safe.
- A `FAIL` latency or blank-event status means recovery/state handling should be prioritized over calibration.
