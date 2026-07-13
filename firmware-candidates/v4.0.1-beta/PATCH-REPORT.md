# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `force-enhanced-exp4` - force-enhanced stability profile with V3.16 mode wrapper, stronger relay settling, and boot-logo stabilization delay.

## Safety scope

- Source firmware is not modified in place.
- Output binary size is unchanged.
- Bootloader/updater code and SD update procedure are not patched.
- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.
- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.
- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks for stronger AC/DC switching recovery.
- Mode-switch helper `0x0801f0ac` is wrapped to call `selector(1, flag)` directly, matching the smoother V3.16 non-sub-mode-4 path while leaving call sites unchanged.
- Boot-logo resource load is routed through a guarded wrapper that adds a short stabilization delay after `LOGO-1.bmp` is loaded.
- Patched self-loop vector entries: `56`.
- Bahasa Melayu resource is added to the candidate folder as `system/TEXT_MS.DAT`.
- The existing Spanish `TEXT_SP.DAT` slot is replaced with the same Malay resource for device-side language selection.
- The existing Spanish language-name string is renamed to `Melayu` in place, with byte length preserved.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `f09f9f43a156b62e90c708c858986ae57f6baa2102a307f5830999b0557249da`
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
| `0x25bf8` | 7 | `45 73 70 61 c3 b1 61` | `4d 65 6c 61 79 75 20` | rename existing Spanish language menu slot to Melayu without changing table size |
| `0x09ca0` | 2 | `fe e7` | `ff e7` | convert runtime fail-stop loop after integrity check into fall-through return |
| `0x0c6c8` | 2 | `fe e7` | `ff e7` | convert UI/render fail-stop loop into fall-through return |
| `0x2c4ea` | 2 | `fe e7` | `70 47` | return from semihosting/debug fail-stop instead of looping forever |
| `0x0f10a` | 2 | `02 20` | `08 20` | force-stable: increase relay selector pre-switch settle wait from 2 to 8 ticks |
| `0x0f146` | 2 | `03 20` | `0c 20` | force-stable: increase relay selector bit-settle wait from 3 to 12 ticks |
| `0x0f192` | 2 | `0a 20` | `64 20` | force-stable: increase final post-relay settle wait from 10 to 100 ticks |
| `0x0f0ac` | 16 | `10 b5 04 46 01 2c 08 d1 02 21 5e 48 1a f0 6d f9` | `00 b5 01 46 01 20 00 f0 1e f8 00 bd 00 bf 00 bf` | v316-switch-exp3: replace V4 helper-only tail with selector(1, flag) wrapper for smoother DC/AC mode recovery |
| `0x045b2` | 4 | `01 f0 9c fc` | `29 f0 05 f8` | force-enhanced-exp4: route LOGO-1 resource load through boot stabilization delay wrapper |
| `0x2d5c0` | 14 | `00 00 00 00 00 00 00 00 00 00 00 00 00 00` | `10 b5 d8 f7 94 fc c8 20 da f7 7b fa 10 bd` | force-enhanced-exp4: call original LOGO-1 loader, wait 200 ticks, then return to boot loader |
