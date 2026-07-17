# DM303 V4.0.1h repair-a package report

Status: HOLD. This package is not accepted for flash and is not a success claim.

## Reason for this repair

The user reported that `V4.0.1h` still produced full failure. Therefore the
`stability-exp20-ms-safe` line is treated as failed/quarantined.

This repair does not continue feature work. It removes the failed V4.0.1h
resource/language layer and rebuilds a cleaner V4.0.1h-marker candidate for
analysis.

## Build identity

```text
profile: v401h-repair-a
source: backup/DM303 V4.0-read only/DM303V4.004.bin
source sha256: 64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158
firmware output: firmware-candidates/v4.0.1h-repair-a/DM303V4.0.1-beta.bin
firmware sha256: 66315b32c079842251143450bb853c5f60a29bb27c93b73f03389a9813b1cd36
visible marker: V4.0.1h
size: 203260 bytes
```

## What this repair changes from failed V4.0.1h

Binary difference from failed `V4.0.1h`:

| Offset | Size | Failed V4.0.1h | Repair-a | Meaning |
|---:|---:|---|---|---|
| `0x25bf8` | 3 | `4d 65 6c` | `45 73 70` | restore first part of official `España` language-name bytes |
| `0x25bfc` | 3 | `79 75 20` | `c3 b1 61` | restore final part of official `España` language-name bytes |

The repair removes the V4.0.1h Malay language-name patch from the firmware
image. Measurement/recovery code bytes remain the same as the V4.0.1h recovery
core.

## What this repair removes from the SD package

The isolated `sd-root/` package uses official vendor resources:

| Resource | Repair-a SHA-256 | Decision |
|---|---|---|
| `system/TEXT_SP.DAT` | `4b6b2fd9c6dee916390144815e7becc02549b7d6f1260b0551c8d939c3acf83e` | official SP restored |
| `system/icon-SP.dat` | `96f2b294c7fad14a527eb96f1a8f09f7e0f33e2f02f7f43af305c9fa2df57394` | official SP icon pack restored |
| `system/LOGO-1.bmp` | `f5e84dfd0a14f63ad8c570629c59c36a0a8a8844ce4cfc48c9c89d1031b41ba3` | official V4.0 logo restored |
| `system/DM30XDB1.dat` | `846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79` | restored from official SD resource set |

Removed from this repair baseline:

- Malay `TEXT_SP.DAT` slot replacement;
- Malay/dark `icon-SP.dat`;
- beta logo overlay;
- dark menu BMP changes;
- boot-logo delay wrapper;
- `stream-recovery-exp15` aggressive gates.

## What remains included

The binary still includes the selected exp14/exp16 recovery core:

- fault/default self-loop recovery to system reset;
- runtime fail-stop loop fall-through/return patches;
- stream retry fail-fast/error routing;
- bounded low byte-IO wrapper;
- command retry clamp;
- stale stream bits `0` and `1` clear on error;
- mode/range entry stale-state clear;
- stale busy bit `1` fresh transaction path;
- long current/meter switch gate cap from `0x3e80` to `0x0640`;
- visible `V4.0.1h` marker.

## Validation performed

Structural checks performed:

```text
root_exists=True
firmware_exists=True
original_bin_absent=True
nested_folder_absent=True
nested_system_absent=True
bmp_layout_check=ok
checked_bmp_count=35
```

Package checksums are written to:

```text
firmware-candidates/v4.0.1h-repair-a/SD-ROOT-SHA256SUMS.txt
```

Patch report is written to:

```text
firmware-candidates/v4.0.1h-repair-a/PATCH-REPORT.md
```

## What is not claimed

This package does not prove:

- ammeter AC-to-DC latency is fixed;
- oscilloscope noise is reduced;
- AC zero is corrected;
- accuracy or True RMS math is improved;
- spike/overload hang is solved;
- Malay UI or dark theme is available.

The purpose of `repair-a` is narrower: clean the failed V4.0.1h line so the next
diagnosis can separate UI/resource failure from measurement-code failure.

