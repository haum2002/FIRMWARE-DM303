# DM303 V4.0.1b bench analysis report

Input CSV: `docs/v401b-bench-measurements.csv`
Rows: `9`

## Accuracy By Group

| Status | Mode | Range | Unit | Points | Mean Error | Max Abs Error | RMSE | Fit observed = gain*ref + offset | Suggested correction |
|---|---|---|---|---:|---:|---:|---:|---|---|
| NO DATA | n/a | n/a | n/a | 0 | n/a | n/a | n/a | n/a | n/a |

## Stability And Latency

| Status | Mode | Range | Unit | Rows | Mean Latency ms | Max Latency ms | Noise High | Noise Low | Max Noise p-p | Blank Events |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| NO DATA | n/a | n/a | n/a | 0 | n/a | n/a | n/a | n/a | n/a | 0 |

## Quality Gate

Overall status: `REVIEW`

| Status | Mode | Range | Unit | Issues |
|---|---|---|---|---|
| NO DATA | ammeter_green | AC | A | none |
| NO DATA | ammeter_green | DC | A | none |
| NO DATA | cranking | known_limited_source | V | none |
| NO DATA | cranking | open | V | none |
| NO DATA | cranking | short_to_negative | V | none |
| NO DATA | ohmmeter | open | ohm | none |
| NO DATA | oscilloscope | 0.1Vdiv_12.5us | V | none |
| NO DATA | voltmeter | AC | V | none |
| NO DATA | voltmeter | DC | V | none |

## Cranking / Power-Rail Diagnosis

- Cranking diagnosis needs open, short-to-negative, and known limited-source data.

## Interpretation

- A stable offset across multiple reference values suggests calibration/front-end offset.
- A gain far from `1.0` suggests divider/shunt/reference scaling error.
- High blank events with low numeric error suggests recovery/latency, not calibration.
- High noise with probes shorted suggests front-end, ground, shielding, reference, or firmware filtering.
- Do not patch firmware math from one point only; use at least two reference values per mode/range.
- A `REVIEW` accuracy status means the data is strong enough to investigate gain/offset, not that a binary math patch is already safe.
- A `FAIL` latency or blank-event status means recovery/state handling should be prioritized over calibration.
