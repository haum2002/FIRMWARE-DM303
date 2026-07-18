# README-UNSAFE — DM303-V4.0.2-beta-FINAL (QUARANTINED)

**DO NOT FLASH THIS PACKAGE.**

Status: QUARANTINED / FAILED line. Despite the folder name and its
`FIRMWARE-READY.txt`, this package is **not** safe to flash: the whole V4.0.2
line was produced by an uncontrolled Qwen-assisted experiment and failed the
independent audit; see `docs/v402-qwen-audit.md` for the full analysis.

- The firmware binary in this folder is not derived from the controlled
  patcher (`tools/dm303_v401_beta_patch.py`) and has no auditable
  PATCH-REPORT.
- The "FINAL"/"READY" naming is unverified vendor-style marketing from the
  failed experiment, not a project acceptance gate.
- Never use this package, its firmware, or its resource layer as a base for
  new work.
- For current package status, see the repository root `README.md`.

This label was added on 2026-07-18 as part of project housekeeping.
