# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

## Safety scope

- Source firmware is not modified in place.
- Output binary size is unchanged.
- Bootloader/updater code and SD update procedure are not patched.
- Fault/default self-loop handlers are redirected to a hardware reset request.
- Runtime fail-stop loops are converted to return/fall-through paths.
- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`.
- True add-only language menu activation is not patched yet because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `9206f9e0c574a8f4ad4c8ba1be7fb51206799641b89e74ce202a93c372382112`
- Source size: `203260` bytes
- Output size: `203260` bytes

## Byte patches

| Offset | Size | Before | After | Reason |
|---:|---:|---|---|---|
| `0x0000c` | 4 | `57 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00010` | 4 | `59 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00014` | 4 | `5b 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00018` | 4 | `5d 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0002c` | 4 | `5f 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00030` | 4 | `61 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00038` | 4 | `63 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00040` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00048` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0004c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00050` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00054` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0005c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00060` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00064` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00068` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00074` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00078` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0007c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00080` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00084` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0008c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000a0` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000a8` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000ac` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000bc` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000c0` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000c4` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000c8` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000cc` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000d0` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000d8` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000e0` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000e4` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000ec` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000f0` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000f4` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000f8` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x000fc` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00100` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00104` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00108` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0010c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00110` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00114` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00118` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0011c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00120` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00124` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00128` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0012c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00130` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00134` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x00138` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x0013c` | 4 | `67 75 01 08` | `55 75 01 08` | redirect self-loop exception/IRQ vector to shared reset-recovery stub |
| `0x07554` | 20 | `fe e7 fe e7 fe e7 fe e7 fe e7 fe e7 fe e7 fe e7 fe e7 fe e7` | `02 48 02 49 01 60 bf f3 4f 8f fe e7 0c ed 00 e0 04 00 fa 05` | replace permanent fault/default loops with SCB_AIRCR SYSRESETREQ stub |
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 62 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 62 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x09ca0` | 2 | `fe e7` | `ff e7` | convert runtime fail-stop loop after integrity check into fall-through return |
| `0x0c6c8` | 2 | `fe e7` | `ff e7` | convert UI/render fail-stop loop into fall-through return |
| `0x2c4ea` | 2 | `fe e7` | `70 47` | return from semihosting/debug fail-stop instead of looping forever |
