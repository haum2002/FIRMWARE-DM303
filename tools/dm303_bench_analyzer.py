#!/usr/bin/env python3
"""Analyze DM303 bench measurements for stability, accuracy, and latency.

The input is a CSV collected from physical tests. This tool does not patch
firmware; it turns observations into numbers that can justify a later safe
calibration/filter patch.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


DEFAULT_INPUT = Path("docs/v401b-bench-measurements.csv")
DEFAULT_REPORT = Path("docs/v401b-bench-analysis-report.md")
DEFAULT_JSON_REPORT = Path("docs/v401b-bench-analysis-report.json")


@dataclass(frozen=True)
class Threshold:
    max_abs_error: float | None = None
    max_latency_ms: float | None = 2000.0
    max_noise_pp: float | None = None
    max_blank_events: int | None = 0


THRESHOLDS: dict[tuple[str, str, str], Threshold] = {
    # User-observed reference offsets: about 0.020 V DC and 0.010 V AC.
    # These are review limits, not calibration constants.
    ("voltmeter", "DC", "V"): Threshold(max_abs_error=0.020, max_latency_ms=1500.0),
    ("voltmeter", "AC", "V"): Threshold(max_abs_error=0.010, max_latency_ms=1500.0),
    ("ammeter_green", "DC", "A"): Threshold(max_latency_ms=1500.0),
    ("ammeter_green", "AC", "A"): Threshold(max_latency_ms=1500.0),
    ("ohmmeter", "open", "ohm"): Threshold(max_latency_ms=1500.0, max_blank_events=0),
    # V3.16 baseline around +0.08 / -0.05 V means about 0.13 V p-p.
    ("oscilloscope", "0.1Vdiv_12.5us", "V"): Threshold(max_noise_pp=0.130, max_latency_ms=1500.0),
    ("cranking", "open", "V"): Threshold(max_latency_ms=1500.0),
    ("cranking", "short_to_negative", "V"): Threshold(max_abs_error=0.050, max_latency_ms=1500.0),
    ("cranking", "known_limited_source", "V"): Threshold(max_abs_error=0.100, max_latency_ms=1500.0),
}


@dataclass(frozen=True)
class Measurement:
    mode: str
    range_name: str
    unit: str
    reference: float | None
    observed: float | None
    latency_ms: float | None
    noise_high: float | None
    noise_low: float | None
    noise_pp: float | None
    blank_events: int | None
    samples: int | None
    notes: str

    @property
    def group(self) -> tuple[str, str, str]:
        return self.mode, self.range_name, self.unit

    @property
    def error(self) -> float | None:
        if self.reference is None or self.observed is None:
            return None
        return self.observed - self.reference


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return float(value)


def parse_int(value: str | None) -> int | None:
    parsed = parse_float(value)
    if parsed is None:
        return None
    return int(parsed)


def derive_noise_pp(noise_pp: float | None, noise_high: float | None, noise_low: float | None) -> float | None:
    if noise_pp is not None:
        return noise_pp
    if noise_high is None or noise_low is None:
        return None
    return noise_high - noise_low


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def load_measurements(path: Path) -> list[Measurement]:
    rows: list[Measurement] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"mode", "range", "unit"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Missing required CSV columns: {sorted(missing)}")
        for raw in reader:
            if not any((value or "").strip() for value in raw.values()):
                continue
            rows.append(
                Measurement(
                    mode=(raw.get("mode") or "").strip(),
                    range_name=(raw.get("range") or "").strip(),
                    unit=(raw.get("unit") or "").strip(),
                    reference=parse_float(raw.get("reference")),
                    observed=parse_float(raw.get("observed")),
                    latency_ms=parse_float(raw.get("latency_ms")),
                    noise_high=parse_float(raw.get("noise_high")),
                    noise_low=parse_float(raw.get("noise_low")),
                    noise_pp=derive_noise_pp(
                        parse_float(raw.get("noise_pp")),
                        parse_float(raw.get("noise_high")),
                        parse_float(raw.get("noise_low")),
                    ),
                    blank_events=parse_int(raw.get("blank_events")),
                    samples=parse_int(raw.get("samples")),
                    notes=(raw.get("notes") or "").strip(),
                )
            )
    return rows


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def rmse(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def linear_fit(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    if len(points) < 2:
        return None
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    x_mean = mean(xs)
    y_mean = mean(ys)
    denom = sum((x - x_mean) ** 2 for x in xs)
    if denom == 0:
        return None
    gain = sum((x - x_mean) * (y - y_mean) for x, y in points) / denom
    offset = y_mean - gain * x_mean
    return gain, offset


def fmt(value: float | None, digits: int = 6) -> str:
    if value is None:
        return "n/a"
    return f"{value:.{digits}g}"


def threshold_for(group: tuple[str, str, str]) -> Threshold:
    return THRESHOLDS.get(group, Threshold())


def status_from_issues(issues: list[str], has_data: bool) -> str:
    if not has_data:
        return "NO DATA"
    if any(issue.startswith("FAIL") for issue in issues):
        return "FAIL"
    if issues:
        return "REVIEW"
    return "PASS"


def group_quality(items: list[Measurement]) -> tuple[str, list[str]]:
    if not items:
        return "NO DATA", ["No rows"]
    group = items[0].group
    threshold = threshold_for(group)
    issues: list[str] = []
    has_data = False

    errors = [abs(item.error) for item in items if item.error is not None]
    if errors:
        has_data = True
        if threshold.max_abs_error is not None and max(errors) > threshold.max_abs_error:
            issues.append(
                f"REVIEW accuracy max_abs_error {fmt(max(errors))} > {fmt(threshold.max_abs_error)} {group[2]}"
            )

    latencies = [item.latency_ms for item in items if item.latency_ms is not None]
    if latencies:
        has_data = True
        if threshold.max_latency_ms is not None and max(latencies) > threshold.max_latency_ms:
            issues.append(
                f"FAIL latency max {fmt(max(latencies), 4)} ms > {fmt(threshold.max_latency_ms, 4)} ms"
            )

    noises = [item.noise_pp for item in items if item.noise_pp is not None]
    if noises:
        has_data = True
        if threshold.max_noise_pp is not None and max(noises) > threshold.max_noise_pp:
            issues.append(
                f"REVIEW noise p-p {fmt(max(noises))} > V3.16-style target {fmt(threshold.max_noise_pp)} {group[2]}"
            )

    blanks = [item.blank_events for item in items if item.blank_events is not None]
    if blanks:
        has_data = True
        blank_total = sum(blanks)
        if threshold.max_blank_events is not None and blank_total > threshold.max_blank_events:
            issues.append(f"FAIL blank_events {blank_total} > {threshold.max_blank_events}")

    observed_values = [item.observed for item in items if item.observed is not None]
    if group == ("cranking", "open", "V") and observed_values:
        has_data = True
        max_open = max(abs(value) for value in observed_values)
        if max_open > 0.5:
            issues.append(
                f"REVIEW cranking open-input observed {fmt(max_open)} V; verify with short-to-negative and known source"
            )

    return status_from_issues(issues, has_data), issues


def cranking_diagnosis(rows: list[Measurement]) -> list[str]:
    by_range = {(row.mode, row.range_name): row for row in rows if row.mode == "cranking" and row.observed is not None}
    open_row = by_range.get(("cranking", "open"))
    short_row = by_range.get(("cranking", "short_to_negative"))
    known_rows = [
        row
        for row in rows
        if row.mode == "cranking"
        and row.range_name == "known_limited_source"
        and row.reference is not None
        and row.observed is not None
    ]
    lines: list[str] = []

    if open_row and open_row.observed is not None:
        if short_row and short_row.observed is not None:
            if open_row.observed > 0.5 and abs(short_row.observed) <= 0.05:
                lines.append(
                    "Cranking open input floats, but short-to-negative collapses near zero: likely ghost/bias voltage, not internal battery voltage."
                )
            elif abs(short_row.observed) > 0.5:
                lines.append(
                    "Cranking short-to-negative remains high: suspect hardware leakage, protection path, relay/mux leakage, PCB contamination, or ground/reference fault."
                )
            elif open_row.observed > 0.5:
                lines.append(
                    "Cranking open input is high; repeat with short-to-negative and known limited source before applying any firmware correction."
                )
        elif open_row.observed > 0.5:
            lines.append(
                "Cranking open input is high without a matching short/source test: treat as floating/leakage evidence, not as a valid battery reading."
            )

    if known_rows:
        errors = [abs(row.error) for row in known_rows if row.error is not None]
        if errors and max(errors) > 0.10:
            lines.append(
                "Cranking known-source error exceeds 0.10 V: possible scaling/front-end error; do not mask it with a fixed open-input offset."
            )

    if not lines:
        lines.append("Cranking diagnosis needs open, short-to-negative, and known limited-source data.")
    return lines


def rows_to_json(rows: list[Measurement], by_group: dict[tuple[str, str, str], list[Measurement]]) -> dict[str, object]:
    groups: list[dict[str, object]] = []
    for group, items in sorted(by_group.items()):
        status, issues = group_quality(items)
        errors = [item.error for item in items if item.error is not None]
        latencies = [item.latency_ms for item in items if item.latency_ms is not None]
        noises = [item.noise_pp for item in items if item.noise_pp is not None]
        blanks = [item.blank_events for item in items if item.blank_events is not None]
        groups.append(
            {
                "mode": group[0],
                "range": group[1],
                "unit": group[2],
                "status": status,
                "issues": issues,
                "points": len(items),
                "mean_error": mean(errors) if errors else None,
                "max_abs_error": max((abs(value) for value in errors), default=None),
                "mean_latency_ms": mean(latencies) if latencies else None,
                "max_latency_ms": max(latencies) if latencies else None,
                "max_noise_pp": max(noises) if noises else None,
                "blank_events": sum(blanks) if blanks else None,
            }
        )
    overall_status = "PASS"
    if any(group["status"] == "FAIL" for group in groups):
        overall_status = "FAIL"
    elif any(group["status"] in {"REVIEW", "NO DATA"} for group in groups):
        overall_status = "REVIEW"
    return {
        "rows": len(rows),
        "overall_status": overall_status,
        "groups": groups,
        "cranking_diagnosis": cranking_diagnosis(rows),
    }


def build_report(path: Path, rows: list[Measurement]) -> str:
    by_group: dict[tuple[str, str, str], list[Measurement]] = defaultdict(list)
    for row in rows:
        by_group[row.group].append(row)

    lines = [
        "# DM303 V4.0.1b bench analysis report",
        "",
        f"Input CSV: `{path.as_posix()}`",
        f"Rows: `{len(rows)}`",
        "",
        "## Accuracy By Group",
        "",
        "| Status | Mode | Range | Unit | Points | Mean Error | Max Abs Error | RMSE | Fit observed = gain*ref + offset | Suggested correction |",
        "|---|---|---|---|---:|---:|---:|---:|---|---|",
    ]

    any_accuracy = False
    for group, items in sorted(by_group.items()):
        status, _issues = group_quality(items)
        errors = [item.error for item in items if item.error is not None]
        errors_f = [value for value in errors if value is not None]
        points = [
            (item.reference, item.observed)
            for item in items
            if item.reference is not None and item.observed is not None
        ]
        if not errors_f:
            continue
        any_accuracy = True
        fit = linear_fit([(float(x), float(y)) for x, y in points])
        if fit is None:
            fit_text = "n/a"
            correction = f"offset {fmt(-mean(errors_f))} {group[2]}"
        else:
            gain, offset = fit
            fit_text = f"gain `{fmt(gain, 8)}`, offset `{fmt(offset, 8)}`"
            correction = f"corrected=(observed - {fmt(offset, 8)}) / {fmt(gain, 8)}"
        lines.append(
            f"| {status} | {group[0]} | {group[1]} | {group[2]} | {len(errors_f)} | "
            f"{fmt(mean(errors_f))} | {fmt(max(abs(value) for value in errors_f))} | "
            f"{fmt(rmse(errors_f))} | {fit_text} | {correction} |"
        )
    if not any_accuracy:
        lines.append("| NO DATA | n/a | n/a | n/a | 0 | n/a | n/a | n/a | n/a | n/a |")

    lines.extend(
        [
            "",
            "## Stability And Latency",
            "",
            "| Status | Mode | Range | Unit | Rows | Mean Latency ms | Max Latency ms | Noise High | Noise Low | Max Noise p-p | Blank Events |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    any_stability = False
    for group, items in sorted(by_group.items()):
        status, _issues = group_quality(items)
        latencies = [item.latency_ms for item in items if item.latency_ms is not None]
        highs = [item.noise_high for item in items if item.noise_high is not None]
        lows = [item.noise_low for item in items if item.noise_low is not None]
        noises = [item.noise_pp for item in items if item.noise_pp is not None]
        blanks = [item.blank_events for item in items if item.blank_events is not None]
        if not latencies and not highs and not lows and not noises and not blanks:
            continue
        any_stability = True
        lines.append(
            f"| {status} | {group[0]} | {group[1]} | {group[2]} | {len(items)} | "
            f"{fmt(mean(latencies), 4) if latencies else 'n/a'} | "
            f"{fmt(max(latencies), 4) if latencies else 'n/a'} | "
            f"{fmt(max(highs), 6) if highs else 'n/a'} | "
            f"{fmt(min(lows), 6) if lows else 'n/a'} | "
            f"{fmt(max(noises), 6) if noises else 'n/a'} | "
            f"{sum(blanks) if blanks else 0} |"
        )
    if not any_stability:
        lines.append("| NO DATA | n/a | n/a | n/a | 0 | n/a | n/a | n/a | n/a | n/a | 0 |")

    quality_json = rows_to_json(rows, by_group)
    lines.extend(
        [
            "",
            "## Quality Gate",
            "",
            f"Overall status: `{quality_json['overall_status']}`",
            "",
            "| Status | Mode | Range | Unit | Issues |",
            "|---|---|---|---|---|",
        ]
    )
    for group in quality_json["groups"]:
        issues = group["issues"] or ["none"]
        lines.append(
            f"| {group['status']} | {group['mode']} | {group['range']} | {group['unit']} | "
            f"{'; '.join(str(issue) for issue in issues)} |"
        )

    lines.extend(
        [
            "",
            "## Cranking / Power-Rail Diagnosis",
            "",
            *[f"- {item}" for item in cranking_diagnosis(rows)],
        ]
    )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A stable offset across multiple reference values suggests calibration/front-end offset.",
            "- A gain far from `1.0` suggests divider/shunt/reference scaling error.",
            "- High blank events with low numeric error suggests recovery/latency, not calibration.",
            "- High noise with probes shorted suggests front-end, ground, shielding, reference, or firmware filtering.",
            "- Do not patch firmware math from one point only; use at least two reference values per mode/range.",
            "- A `REVIEW` accuracy status means the data is strong enough to investigate gain/offset, not that a binary math patch is already safe.",
            "- A `FAIL` latency or blank-event status means recovery/state handling should be prioritized over calibration.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json-report", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--fail-on-alert", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Missing bench CSV: {args.input}")
    rows = load_measurements(args.input)
    report = build_report(args.input, rows)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    write_text_lf(args.report, report)
    by_group: dict[tuple[str, str, str], list[Measurement]] = defaultdict(list)
    for row in rows:
        by_group[row.group].append(row)
    quality = rows_to_json(rows, by_group)
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(quality, indent=2) + "\n", encoding="utf-8")
    print("bench_analysis=ok")
    print(f"input={args.input}")
    print(f"rows={len(rows)}")
    print(f"overall_status={quality['overall_status']}")
    print(f"report={args.report}")
    if args.json_report:
        print(f"json_report={args.json_report}")
    if args.fail_on_alert and quality["overall_status"] != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
