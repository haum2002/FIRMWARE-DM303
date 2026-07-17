# AGENTS.md — DM303 Firmware Workspace

Guidance for AI coding agents working in this repository. Read this fully before
touching anything. Also read `note.txt` (the project's current working memory)
and `README.md` (current package status, in Bahasa Melayu) before making
changes.

## 1. Project Overview

This is a **community firmware reverse-engineering and patching archive** for
the **AUTOOL DM303 digital multimeter** (firmware identifies itself as
`MT100MM` / `BT100MM`). It is not a from-source firmware project: there is no C
toolchain and no recompiled firmware. Work consists of **byte-level binary
patching** of the official vendor firmware image, plus generation of UI
resource files (text/icon/logo packs) that live on the device's SD card.

Goals of the work archived here:

- Fix stability/UX problems in the official V4.0 firmware: ammeter AC→DC
  switching latency (~30 s blank), reading noise, freeze/blank symptoms, and
  text rendering artifacts ("calit" — smear above glyphs).
- Add a Bahasa Melayu (ms_MY) UI by repurposing the Spanish language slot.
- Produce flashable SD-card update packages (`v4.0.1-beta`, `v4.0.2-beta`
  lines) with auditable, minimal, revertible changes.

Hardware/firmware facts established by analysis (see `docs/`):

- MCU: Nations N32G455-class ARM Cortex-M (Thumb-2), 8 MHz + 32.768 kHz
  crystals, external `25VQ64` SPI flash, relay-switched analog front end.
- Firmware load base: `0x08010000`; RAM window `0x20000000–0x20040000`.
- Official V4.0 image: `backup/DM303 V4.0-read only/DM303V4.004.bin`,
  203,260 bytes (`0x319fc`),
  SHA-256 `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`.
- Version strings live at file offsets `0x02CA0` / `0x02CB0`
  (e.g. `MT100MM V4.0.1o\0`, `BT100MM V4.0.1o\0`).
- SD-card update layout: firmware `.bin` + `QBtest.txt` + `readme.txt` +
  `system/` (fonts, icons, per-language `TEXT_*.DAT`, logo BMPs) at the card
  root. The device updates from this layout.

## 2. Current Status (read before any work)

- Current final package: `dm303_firmware/DM303-V4.0.1-beta/`, profile
  `v401h-repair-i`, visible device marker `V4.0.1o`, firmware SHA-256
  `11d8f9ba7ba956e0da5f9fc5c6634e851a6aafeaa11bc4fc0a94dcf2a2e63953`.
- It is official V4.0 + targeted ammeter latency patches only (AC/DC
  current-switch guard caps + acquisition window 240→64 samples). All UI,
  stream/IO, relay-settle, and boot windows are official bytes.
- `V4.0.1h` (`stability-exp20-ms-safe`) is **quarantined/failed** — never use
  it or its resource layer as a base.
- `v401h-repair-i-ui-ms` (marker `V4.0.1p`) is a separate, unpromoted
  Malay/dark-UI overlay at `firmware-candidates/v4.0.1h-repair-i-ui-ms/`.
- **Nothing here is proven on-device.** Never claim stability, accuracy,
  latency, EMI, True RMS, or UI fixes unless that exact build passed
  device-side tests. Packages stay on HOLD until the user explicitly accepts
  the flash risk.

## 3. Repository Layout

| Path | Role |
| --- | --- |
| `backup/` | Read-only official firmware references: `DM303 V3.16-read only/`, `DM303 V4.0-read only/`, `SD-file_DM303_update_US240104-read only/`. **Only permitted patch source. Git-ignored; treat as immutable.** |
| `tools/` | All automation: 34 Python scripts + 2 PowerShell helpers. See §4–§5. |
| `firmware-candidates/` | Staging output of patchers, one folder per profile (`v4.0.1-beta`, `v4.0.1h-repair-a`…`-i`, `v4.0.1h-repair-i-ui-ms`, `v4.0.2-beta`). Each carries `PATCH-REPORT.md`, `SHA256SUMS.txt`, and usually a built `sd-root/`. |
| `dm303_firmware/` | Final flash packages (`DM303-V4.0.1-beta/`, `DM303-V4.0.2-beta/`, `DM303-V4.0.2-beta-FINAL/`) + status README. Contents are copied to the SD card root. |
| `localization/ms_MY/` | Malay text/icon resources generated from official `TEXT_EN.DAT`/`TEXT_SP.DAT` by `tools/dm303_make_ms_pack.py`, plus reviewable `translations_ms.csv`. |
| `docs/` | ~70 analysis documents: disassembly dumps (`disasm-*.txt`), per-experiment audits and byte proofs, comparison reports, field-observation logs, manual extracts, flash notes. |
| `analysis/` | UI icon frame extractions and contact sheets (BMP/PNG evidence). |
| `assets/` | Font (`AbrilFatface-Regular.ttf`) and beta logo sources used by resource generators. |
| `hardware_photos/` | PCB teardown photos used for the hardware analysis doc. |
| `dm303_deep_analysis/` | Scratch directory (currently empty). |
| `note.txt` | Authoritative working memory: field feedback, failed-build history, hard rules. Keep it updated when status changes. |
| `CHECKSUMS-SHA256.txt` | SHA-256 manifest of every file in the current final package. Regenerate when the final package changes. |
| `README.md` | Current package status and validation commands (Bahasa Melayu). |
| `VIBE_CODING.md` | Generic AI-assisted development playbook (Bahasa Melayu); process guidance, not project architecture. |

## 4. Technology Stack

- **Python 3** (run from the repository root). Most tools are **stdlib-only**
  (`argparse`, `hashlib`, `pathlib`, `struct`, `shutil`).
- Disassembly/analysis tools additionally need:
  `python -m pip install -r tools/requirements-analysis.txt`
  (`capstone==5.0.9`, `keystone-engine==0.9.2`). Install into a virtual
  environment, not the system Python.
- **PowerShell** helpers: `tools/dm303_make_beta_logo.ps1`,
  `tools/dm303_make_ms_icon_pack.ps1`.
- No `pyproject.toml`/`package.json`/build system, no CI, no unit-test
  framework. Validation is done by the purpose-built checker scripts below.
- Git: firmware binaries/`*.DAT`/`*.bmp` are marked `binary` in
  `.gitattributes`; text files use LF. `backup/` is git-ignored (local
  read-only reference). Commit messages use conventional prefixes
  (`feat(firmware):`, `chore(firmware):`).

## 5. Build, Validate, and Flash Workflow

Run all commands from the repository root. The workflow is a pipeline:
**patch → stage in `firmware-candidates/` → build sd-root → validate → merge
to `dm303_firmware/` → preflash check → copy to SD card.**

### 5.1 Patch (create a candidate binary)

```powershell
python tools/dm303_v401_beta_patch.py --profile <profile>
python tools/dm303_v402_beta_patch.py --profile <profile>   # v4.0.2 line
```

- Never modifies `backup/` in place; emits a new binary +
  `PATCH-REPORT.md` + `SHA256SUMS.txt` under `firmware-candidates/<...>/`.
- Profiles are named, registered experiments (`boot-acceptance`,
  `anti-freeze-exp1`, `stream-recovery-exp14`, `stability-exp20-ms-safe`,
  `v401h-repair-a`…`-i`, …). Every profile has an expected SHA-256 and an
  expected-bytes map registered in the checker tools — a new profile must be
  registered there too or validation cannot run.

### 5.2 Build an SD-root (repair line — the only permitted way)

```powershell
python tools/dm303_build_repair_sdroot.py --candidate-dir firmware-candidates/v4.0.1h-repair-i --profile v401h-repair-i
```

- Copies the **full official** `backup/DM303 V4.0-read only/system/` tree and
  adds `DM30XDB1.dat` from the US240104 SD update. Candidate `system/` folders
  are overlays only and must never be used as the base system tree (several
  failed builds came from exactly that mistake).
- UI/Malay overlay packages use `tools/dm303_build_ui_overlay_sdroot.py`.
- Legacy final-package assembly uses `tools/dm303_merge_final_package.py`.

### 5.3 Validate (all read-only gates)

```powershell
python tools/dm303_repair_candidate_check.py  --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_measurement_candidate_gate.py --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
python tools/dm303_preflash_check.py          --root dm303_firmware\DM303-V4.0.1-beta --profile v401h-repair-i
```

- `dm303_repair_candidate_check.py` — profile SHA-256 + expected patched
  bytes + `official_v4_system_resources=match`.
- `dm303_measurement_candidate_gate.py` — strict byte-diff gate: proves the
  candidate differs from official V4.0 **only** in the approved ranges for the
  profile (UI/render/stream/IO/relay/boot areas must be official).
- `dm303_preflash_check.py` — final package or actual SD-card layout check;
  rejects the dangerous "folder copied inside the SD card" layout. Against a
  real card: `python tools/dm303_preflash_check.py --root E:\ --profile v401h-repair-i --allow-sd-extras`.
- UI overlays: `tools/dm303_ui_overlay_candidate_check.py`; legacy packages:
  `tools/dm303_validate_final_package.py`.

### 5.4 Analysis/probing tools (all read-only)

`dm303_v4_static_analysis.py` (capstone disassembly, vector map),
`dm303_measurement_probe.py`, `dm303_measurement_loop_probe.py`,
`dm303_measurement_math_probe.py`, `dm303_latency_guard_probe.py`,
`dm303_state_hook_probe.py`, `dm303_stream_state_audit.py`,
`dm303_ui_function_mapper.py`, `dm303_resource_loader_audit.py`,
`dm303_full_stability_audit.py`, `dm303_bench_analyzer.py` (parses bench
CSV logs), `dm303_compare_sets.py`, `dm303_v316_v401_compare.py`, and the
`dm303_expNN_*_safety_audit.py` per-experiment auditors. Resource generators:
`dm303_make_ms_pack.py`, `dm303_make_safe_ms_sp_resource.py`,
`dm303_text_resource.py`, `dm303_make_dark_menu_assets.py`,
`dm303_make_beta_logo.py`, `dm303_make_ms_icon_pack.ps1`.

### 5.5 Flash (manual, by the user)

Copy the **contents** of `dm303_firmware/DM303-V4.0.1-beta/` (not the folder
itself) to the SD-card root: `DM303V4.0.1-beta.bin`, `QBtest.txt`,
`readme.txt`, `system/`. See `docs/beginner-flash-notes.md`.

## 6. Hard Rules and Conventions

These come from `note.txt` and are binding:

1. Build only from official `backup/DM303 V4.0-read only/DM303V4.004.bin`.
2. Keep UI resources official until measurement behavior is isolated — no
   dark theme, logo changes, Malay slot changes, boot-logo delay, or exp15
   aggressive gates in a measurement baseline.
3. Stage new builds under `firmware-candidates/` (or `analysis/`) first —
   never write directly into `dm303_firmware/DM303-V4.0.1-beta/`.
4. Before asking the user to flash anything, provide: exact SHA-256, byte
   diff, expected offsets, rejected offsets, and validation output.
5. Mark every new package **HOLD** unless the user explicitly accepts risk.
6. Change one thing at a time. Past failures came from mixing measurement
   patches with UI/resource/logo/boot changes in one build — failures became
   un-isolatable.
7. Repair-line sd-roots must be built only with
   `tools/dm303_build_repair_sdroot.py` and must pass
   `dm303_repair_candidate_check.py` with `official_v4_system_resources=match`.
8. Every patch must be byte-auditable: patchers emit reports; checkers pin
   exact expected bytes at exact offsets. Do not hand-edit binaries outside
   this tooling.
9. When package status changes, update `README.md`, `note.txt`,
   `dm303_firmware/README.md`, and `CHECKSUMS-SHA256.txt` together.

## 7. Testing Strategy

There is no unit-test suite. Verification is layered:

- **Static gates** (always run, cheap): the checker scripts in §5.3 — SHA-256
  identity, expected/rejected byte offsets, system-resource match against
  official V4.0, SD layout shape.
- **Byte proofs / audits** (per experiment): documented in
  `docs/v401b-expNN-*-byte-proof.md` and `docs/v401b-expNN-flash-safety-audit.md`.
- **Bench/field evidence**: `docs/v401b-bench-measurements.csv`,
  `docs/v401b-field-observations.csv` and their analysis reports; the
  acceptance discipline is in `docs/v401b-no-flash-acceptance-gate-2026-07-15.md`.
- **Device-side tests** are the final arbiter and are performed by the user
  only, on a HOLD-then-accept basis.

## 8. Safety and Security Considerations

- **This is mains-capable test equipment.** Patches to measurement paths,
  fault handlers, or fail-stop loops can hide real hardware faults from the
  user. Treat vendor fault vectors and fail-stop loops as safety features;
  the repair line deliberately keeps them official (that was the lesson of
  the failed repair-c/d/e experiments).
- **Brick risk:** `backup/` is the only recovery source — never modify,
  rename, or "clean up" anything under it. Patchers and checkers are
  read-only against it by design; keep them that way.
- Tools that write (patchers, sd-root builders, merge) must refuse unsafe
  output locations (see `ensure_safe_output` in
  `tools/dm303_build_repair_sdroot.py`) — preserve those guards.
- No secrets, credentials, or network services are involved; nothing in this
  repo should phone home.
- Do not run `git` mutations (commit/push/reset) without the user's explicit
  request.

## 9. Language and Documentation Conventions

- Tool docstrings, code comments, audit/byte-proof docs, `note.txt`, and git
  commits are in **English** — write new technical content in English.
- User-facing status docs (`README.md`, `VIBE_CODING.md`,
  `docs/beginner-flash-notes.md`, `docs/upgrade-analysis.md`) are in
  **Bahasa Melayu** — keep that language when editing those files.
- Docs state status honestly and date-stamped; follow the existing
  "Status:" header convention and never overstate what a build has proven.
