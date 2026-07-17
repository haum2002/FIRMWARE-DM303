# DM303 V4.0.1b no-flash acceptance gate - 2026-07-15

Status: mandatory gate before any new user flash attempt.

## Purpose

This gate prevents repeating the previous failure pattern: changing many things
at once, calling the result successful, then discovering on the device that
measurement behavior did not improve.

No future DM303 V4.0.1b package may be called ready, stable, enhanced, fixed, or
accepted unless every applicable item below is satisfied.

## Language rule

Allowed wording before user testing:

- analysis-only;
- candidate;
- untested on device;
- structurally valid;
- expected offsets patched;
- hold pending acceptance.

Forbidden wording before user testing:

- fixed;
- solved;
- stable;
- accurate;
- low-latency;
- EMI-proof;
- True RMS improved;
- safe to flash;
- final;
- successful.

## Build isolation gate

The next candidate must:

- be built from `backup/DM303 V4.0-read only/DM303V4.004.bin`;
- be generated into an isolated folder first;
- not overwrite `dm303_firmware/DM303-V4.0.1-beta`;
- preserve the source firmware size;
- preserve the updater/SD procedure area unless a separate audit proves it is
  untouched at byte level;
- include a SHA-256 report for every file intended for the SD card.

## Measurement baseline gate

The first new performance baseline must:

- use official vendor UI/resources unchanged;
- exclude dark theme, icon tuning, logo edits, Malay text activation, clock UI,
  battery-percent UI, and flashlight UI changes;
- exclude boot-logo delay wrappers;
- exclude `stream-recovery-exp15` aggressive gates and stale bit0 bypasses;
- include only the selected `stream-recovery-exp14` recovery core, if rebuilt;
- provide a byte-diff table listing every changed offset, before bytes, after
  bytes, and reason.

## Resource gate

Resource/UI changes must be a separate branch after measurement behavior is
isolated.

Before any resource package is accepted:

- compare every modified BMP/DAT against vendor dimensions and file format;
- verify no lossy compression or palette conversion was introduced;
- verify `TEXT_SP.DAT` entry count and rebuild format match the official SP
  layout if the SP slot is reused;
- document which strings remain untranslated because they do not fit safely;
- do not mix resource changes with measurement-code changes.

## Evidence gate

A candidate can be offered for user consideration only after a report includes:

- source image hash;
- output image hash;
- exact profile name;
- exact visible marker;
- included patch list;
- rejected patch list;
- updater/boot safety statement;
- resource hash list;
- validation command output summary;
- known risks still unresolved.

## Device-side acceptance gate

Only the user can confirm these items on the real DM303:

- boot completes normally;
- update/loading animation is not broken;
- no smear/calit appears above text;
- voltmeter DC zero is no worse than official baseline;
- voltmeter AC zero is no worse than official baseline;
- ammeter green DC -> AC and AC -> DC switch without long blank/freeze;
- battery icon does not disappear with the reading;
- ohmmeter/continuity do not self-trigger abnormally;
- oscilloscope noise is no worse than official baseline;
- no spike/overload event causes a persistent hang.

Until the user confirms those items, the firmware remains a candidate, not a
success.

## Current decision

The `V4.0.1h` package is now failed/quarantined after user field feedback. The
next safe direction is not another feature-heavy build.

The only current repair path is:

```text
firmware-candidates/v4.0.1h-repair-a/
```

This repair keeps the visible `V4.0.1h` marker, removes failed Malay/dark/UI
resource changes, restores official vendor resources, and remains HOLD until
explicitly accepted. It is not a claim that measurement stability, accuracy, or
latency is solved.
