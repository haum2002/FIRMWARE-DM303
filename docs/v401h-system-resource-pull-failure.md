# V4.0.1h System Resource Pull Failure

Date: 2026-07-15

Status: confirmed packaging/root-cause risk.

User observation: failed flash builds often did not pull the `system` files accurately.

## Audit Result

Official reference:

```text
backup/DM303 V4.0-read only/system
files=65
```

Compared folders:

| Folder | Missing official files | Different official files | Extra files | Finding |
|---|---:|---:|---:|---|
| `dm303_firmware/DM303-V4.0.1-beta/system` | 0 | 37 | 2 | contaminated final system |
| `firmware-candidates/v4.0.1-beta/system` | 28 | 37 | 3 | overlay folder, not complete SD system |
| `dm303_firmware/DM303-V4.0.2-beta/system` | 0 | 34 | 1 | modified/non-official UI resource set |
| `firmware-candidates/v4.0.2-beta/system` | 0 | 34 | 1 | modified/non-official UI resource set |
| `firmware-candidates/v4.0.1h-repair-a/sd-root/system` | 0 | 0 | 1 | official system plus `DM30XDB1.dat` |
| `firmware-candidates/v4.0.1h-repair-b/sd-root/system` | 0 | 0 | 1 | official system plus `DM30XDB1.dat` |

The extra file in repair-a/repair-b is expected:

```text
system/DM30XDB1.dat
sha256=846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79
```

## Important Correction

`firmware-candidates/v4.0.1-beta/system` is an overlay/staging folder. It is
not a complete SD-card `system` folder. Treating it as complete can omit fonts,
language files, icon packs, and other resource data required by the firmware.

The safe repair-line package must be built from:

```text
backup/DM303 V4.0-read only/system
```

Then add:

```text
backup/SD-file_DM303_update_US240104-read only/system/DM30xDB1.dat
```

as:

```text
system/DM30XDB1.dat
```

## New Guard

Use this builder for repair candidates:

```powershell
python tools\dm303_build_repair_sdroot.py --candidate-dir firmware-candidates\v4.0.1h-repair-b --profile v401h-repair-b
```

Then verify:

```powershell
python tools\dm303_repair_candidate_check.py --root firmware-candidates\v4.0.1h-repair-b\sd-root --profile v401h-repair-b
```

The checker must print:

```text
repair_candidate_check=ok
official_v4_system_resources=match
```

## Policy From Now On

- Do not flash from any candidate folder's partial `system` overlay.
- Do not trust the old final folder as a clean source.
- Do not mix UI/theme/Malay/logo resources into measurement repair candidates.
- Only `sd-root/` built by `dm303_build_repair_sdroot.py` is a complete repair package.
