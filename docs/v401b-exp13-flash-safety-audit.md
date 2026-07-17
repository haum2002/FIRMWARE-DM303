# DM303 V4.0.1b exp13 flash safety audit

Read-only comparison of the final flashable image against the official
V4.0 reference. This report proves whether every changed byte belongs
to the known exp13 patch set and whether startup/resource-loader strings
remain stable.

## Overall

- Result: `PASS`
- Official image: `backup\DM303 V4.0-read only\DM303V4.004.bin`
- Current image: `dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin`
- Official SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Current SHA-256: `fbe05118e33743fb56679d5edd1eb2019c1d82e39f499c1459fe89401ce8130b`
- Differing bytes: `226`
- Differing ranges: `86`

## Safety gates

| Gate | Result | Evidence |
|---|---|---|
| Official hash matches V4.0 reference | `PASS` | `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158` |
| Current hash matches exp13 final | `PASS` | `fbe05118e33743fb56679d5edd1eb2019c1d82e39f499c1459fe89401ce8130b` |
| Firmware size unchanged | `PASS` | official `203260`, current `203260` |
| Initial SP unchanged | `PASS` | `0x200126e0` |
| Reset vector unchanged | `PASS` | `0x0801754d` |
| Every changed byte is allowlisted | `PASS` | `226` changed bytes classified |
| Vector changes are only self-loop recovery redirects | `PASS` | `55` vector entries changed |
| Critical exp13 patch bytes present | `PASS` | `14` byte guards checked |
| Resource-loader strings unchanged | `PASS` | `7` strings checked |

## Diff classification counts

| Classification | Bytes |
|---|---:|
| UI/render fail-stop loop fall-through | 1 |
| boot-logo delay wrapper code cave | 14 |
| boot-logo load call routed through delay wrapper | 3 |
| bounded low byte-IO wrapper code | 75 |
| command 0x40 busy failure error route | 1 |
| command 0x40 retry clamp | 1 |
| command 0x48 retry clamp | 1 |
| command/status retry branch removed | 2 |
| debug/semihosting fail-stop returns | 2 |
| fault/default SYSRESETREQ recovery stub | 18 |
| language menu name renamed to Melayu | 6 |
| low byte-IO entry branch to bounded wrapper | 4 |
| mode/range entry routed through stale state clear wrapper | 4 |
| mode/range stale state clear wrapper code cave | 27 |
| mode/status retry branch removed | 2 |
| runtime fail-stop loop fall-through | 1 |
| self-loop vector redirected to shared recovery stub | 55 |
| stream error cleanup clears status bits 0 and 1 | 1 |
| stream-read retry branch removed | 2 |
| version identity strings | 6 |

## Changed vector entries

Reset vector is intentionally not listed because it is unchanged.
Changed entries below point to the shared fault/default recovery stub
only when the official target was a `fe e7` self-loop.

| Index | Name | Before | After | Official target self-loop | OK |
|---:|---|---:|---:|---|---|
| 3 | hardfault | `0x08017557` | `0x08017555` | `True` | `True` |
| 4 | memmanage | `0x08017559` | `0x08017555` | `True` | `True` |
| 5 | busfault | `0x0801755b` | `0x08017555` | `True` | `True` |
| 6 | usagefault | `0x0801755d` | `0x08017555` | `True` | `True` |
| 11 | svcall | `0x0801755f` | `0x08017555` | `True` | `True` |
| 12 | debugmon | `0x08017561` | `0x08017555` | `True` | `True` |
| 14 | pendsv | `0x08017563` | `0x08017555` | `True` | `True` |
| 16 | irq0 | `0x08017567` | `0x08017555` | `True` | `True` |
| 18 | irq2 | `0x08017567` | `0x08017555` | `True` | `True` |
| 19 | irq3 | `0x08017567` | `0x08017555` | `True` | `True` |
| 20 | irq4 | `0x08017567` | `0x08017555` | `True` | `True` |
| 21 | irq5 | `0x08017567` | `0x08017555` | `True` | `True` |
| 23 | irq7 | `0x08017567` | `0x08017555` | `True` | `True` |
| 24 | irq8 | `0x08017567` | `0x08017555` | `True` | `True` |
| 25 | irq9 | `0x08017567` | `0x08017555` | `True` | `True` |
| 26 | irq10 | `0x08017567` | `0x08017555` | `True` | `True` |
| 29 | irq13 | `0x08017567` | `0x08017555` | `True` | `True` |
| 30 | irq14 | `0x08017567` | `0x08017555` | `True` | `True` |
| 31 | irq15 | `0x08017567` | `0x08017555` | `True` | `True` |
| 32 | irq16 | `0x08017567` | `0x08017555` | `True` | `True` |
| 33 | irq17 | `0x08017567` | `0x08017555` | `True` | `True` |
| 35 | irq19 | `0x08017567` | `0x08017555` | `True` | `True` |
| 40 | irq24 | `0x08017567` | `0x08017555` | `True` | `True` |
| 42 | irq26 | `0x08017567` | `0x08017555` | `True` | `True` |
| 43 | irq27 | `0x08017567` | `0x08017555` | `True` | `True` |
| 47 | irq31 | `0x08017567` | `0x08017555` | `True` | `True` |
| 48 | irq32 | `0x08017567` | `0x08017555` | `True` | `True` |
| 49 | irq33 | `0x08017567` | `0x08017555` | `True` | `True` |
| 50 | irq34 | `0x08017567` | `0x08017555` | `True` | `True` |
| 51 | irq35 | `0x08017567` | `0x08017555` | `True` | `True` |
| 52 | irq36 | `0x08017567` | `0x08017555` | `True` | `True` |
| 54 | irq38 | `0x08017567` | `0x08017555` | `True` | `True` |
| 56 | irq40 | `0x08017567` | `0x08017555` | `True` | `True` |
| 57 | irq41 | `0x08017567` | `0x08017555` | `True` | `True` |
| 59 | irq43 | `0x08017567` | `0x08017555` | `True` | `True` |
| 60 | irq44 | `0x08017567` | `0x08017555` | `True` | `True` |
| 61 | irq45 | `0x08017567` | `0x08017555` | `True` | `True` |
| 62 | irq46 | `0x08017567` | `0x08017555` | `True` | `True` |
| 63 | irq47 | `0x08017567` | `0x08017555` | `True` | `True` |
| 64 | irq48 | `0x08017567` | `0x08017555` | `True` | `True` |
| 65 | irq49 | `0x08017567` | `0x08017555` | `True` | `True` |
| 66 | irq50 | `0x08017567` | `0x08017555` | `True` | `True` |
| 67 | irq51 | `0x08017567` | `0x08017555` | `True` | `True` |
| 68 | irq52 | `0x08017567` | `0x08017555` | `True` | `True` |
| 69 | irq53 | `0x08017567` | `0x08017555` | `True` | `True` |
| 70 | irq54 | `0x08017567` | `0x08017555` | `True` | `True` |
| 71 | irq55 | `0x08017567` | `0x08017555` | `True` | `True` |
| 72 | irq56 | `0x08017567` | `0x08017555` | `True` | `True` |
| 73 | irq57 | `0x08017567` | `0x08017555` | `True` | `True` |
| 74 | irq58 | `0x08017567` | `0x08017555` | `True` | `True` |
| 75 | irq59 | `0x08017567` | `0x08017555` | `True` | `True` |
| 76 | irq60 | `0x08017567` | `0x08017555` | `True` | `True` |
| 77 | irq61 | `0x08017567` | `0x08017555` | `True` | `True` |
| 78 | irq62 | `0x08017567` | `0x08017555` | `True` | `True` |
| 79 | irq63 | `0x08017567` | `0x08017555` | `True` | `True` |

## Critical byte guards

| Offset | Address | Purpose | Expected | Actual | OK |
|---:|---:|---|---|---|---|
| `0x06a06` | `0x08016a06` | low byte-IO entry branch | `00 f0 23 b8` | `00 f0 23 b8` | `True` |
| `0x06a50` | `0x08016a50` | bounded wrapper prefix | `70 b5 05 46 40 f6 a0 76` | `70 b5 05 46 40 f6 a0 76` | `True` |
| `0x07554` | `0x08017554` | SYSRESETREQ stub prefix | `02 48 02 49 01 60 bf f3 4f 8f` | `02 48 02 49 01 60 bf f3 4f 8f` | `True` |
| `0x09570` | `0x08019570` | stream-read retry removed | `00 bf` | `00 bf` | `True` |
| `0x0967c` | `0x0801967c` | command 0x40 retry clamp | `60` | `60` | `True` |
| `0x09682` | `0x08019682` | command 0x48 retry clamp | `60` | `60` | `True` |
| `0x09706` | `0x08019706` | command 0x40 busy failure route | `4c` | `4c` | `True` |
| `0x09758` | `0x08019758` | command/status retry removed | `00 bf` | `00 bf` | `True` |
| `0x097be` | `0x080197be` | mode/status retry removed | `00 bf` | `00 bf` | `True` |
| `0x097e6` | `0x080197e6` | stream error cleanup clears bits 0 and 1 | `20 f0 03 00` | `20 f0 03 00` | `True` |
| `0x0f19a` | `0x0801f19a` | mode/range entry branch to wrapper | `1e f0 34 ba` | `1e f0 34 ba` | `True` |
| `0x2c4ea` | `0x0803c4ea` | debug/semihosting fail-stop returns | `70 47` | `70 47` | `True` |
| `0x2d5c0` | `0x0803d5c0` | boot-logo delay wrapper prefix | `10 b5` | `10 b5` | `True` |
| `0x2d606` | `0x0803d606` | mode/range stale state clear wrapper | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `True` |

## Stable resource-loader strings

| Offset | Expected | Official | Current | OK |
|---:|---|---|---|---|
| `0x0423b` | ` Loading GBK ...` | ` Loading GBK ...` | ` Loading GBK ...` | `True` |
| `0x0424c` | `\system\HZK-ALL.GBK` | `\system\HZK-ALL.GBK` | `\system\HZK-ALL.GBK` | `True` |
| `0x04260` | `Loading DM30XDB1 ...` | `Loading DM30XDB1 ...` | `Loading DM30XDB1 ...` | `True` |
| `0x04278` | `\system\DM30XDB1.dat` | `\system\DM30XDB1.dat` | `\system\DM30XDB1.dat` | `True` |
| `0x04788` | `Loading Start-LOGO-1 ...` | `Loading Start-LOGO-1 ...` | `Loading Start-LOGO-1 ...` | `True` |
| `0x047a4` | `\system\LOGO-1.bmp` | `\system\LOGO-1.bmp` | `\system\LOGO-1.bmp` | `True` |
| `0x057f0` | `VIEW VERSION` | `VIEW VERSION` | `VIEW VERSION` | `True` |

## Changed byte ranges

| Offset | Size | Classification | OK | Official bytes | Current bytes |
|---:|---:|---|---|---|---|
| `0x0000c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `57` | `55` |
| `0x00010` | 1 | self-loop vector redirected to shared recovery stub | `True` | `59` | `55` |
| `0x00014` | 1 | self-loop vector redirected to shared recovery stub | `True` | `5b` | `55` |
| `0x00018` | 1 | self-loop vector redirected to shared recovery stub | `True` | `5d` | `55` |
| `0x0002c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `5f` | `55` |
| `0x00030` | 1 | self-loop vector redirected to shared recovery stub | `True` | `61` | `55` |
| `0x00038` | 1 | self-loop vector redirected to shared recovery stub | `True` | `63` | `55` |
| `0x00040` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00048` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0004c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00050` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00054` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0005c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00060` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00064` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00068` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00074` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00078` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0007c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00080` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00084` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0008c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000a0` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000a8` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000ac` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000bc` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000c0` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000c4` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000c8` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000cc` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000d0` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000d8` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000e0` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000e4` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000ec` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000f0` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000f4` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000f8` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x000fc` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00100` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00104` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00108` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0010c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00110` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00114` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00118` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0011c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00120` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00124` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00128` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0012c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00130` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00134` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x00138` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x0013c` | 1 | self-loop vector redirected to shared recovery stub | `True` | `67` | `55` |
| `0x02cac` | 3 | version identity strings | `True` | `20 00 00` | `2e 31 62` |
| `0x02cbc` | 3 | version identity strings | `True` | `20 00 00` | `2e 31 62` |
| `0x045b2` | 1 | boot-logo load call routed through delay wrapper | `True` | `01` | `29` |
| `0x045b4` | 2 | boot-logo load call routed through delay wrapper | `True` | `9c fc` | `05 f8` |
| `0x06a06` | 4 | low byte-IO entry branch to bounded wrapper | `True` | `70 b5 05 46` | `00 f0 23 b8` |
| `0x06a50` | 1 | bounded low byte-IO wrapper code | `True` | `00` | `70` |
| `0x06a52` | 9 | bounded low byte-IO wrapper code | `True` | `85 b0 23 48 23 f0 fd fe 01` | `05 46 40 f6 a0 76 00 24 02` |
| `0x06a5c` | 3 | bounded low byte-IO wrapper code | `True` | `88 03 23` | `0f 48 24` |
| `0x06a60` | 1 | bounded low byte-IO wrapper code | `True` | `ac` | `48` |
| `0x06a62` | 29 | bounded low byte-IO wrapper code | `True` | `00 20 ad f8 00 00 4f f4 82 70 ad f8 02 00 00 20 ad f8 ...` | `20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 ...` |
| `0x06a80` | 32 | bounded low byte-IO wrapper code | `True` | `08 00 40 02 ad f8 0a 00 08 20 ad f8 0c 00 00 20 ad f8 ...` | `20 b9 01 34 a4 b2 b4 42 f6 d3 04 e0 03 48 23 f0 df ff ...` |
| `0x07554` | 10 | fault/default SYSRESETREQ recovery stub | `True` | `fe e7 fe e7 fe e7 fe e7 fe e7` | `02 48 02 49 01 60 bf f3 4f 8f` |
| `0x07560` | 8 | fault/default SYSRESETREQ recovery stub | `True` | `fe e7 fe e7 fe e7 fe e7` | `0c ed 00 e0 04 00 fa 05` |
| `0x09570` | 2 | stream-read retry branch removed | `True` | `f5 d1` | `00 bf` |
| `0x0967c` | 1 | command 0x40 retry clamp | `True` | `95` | `60` |
| `0x09682` | 1 | command 0x48 retry clamp | `True` | `87` | `60` |
| `0x09706` | 1 | command 0x40 busy failure error route | `True` | `ec` | `4c` |
| `0x09758` | 2 | command/status retry branch removed | `True` | `f5 d1` | `00 bf` |
| `0x097be` | 2 | mode/status retry branch removed | `True` | `f6 d1` | `00 bf` |
| `0x097e8` | 1 | stream error cleanup clears status bits 0 and 1 | `True` | `01` | `03` |
| `0x09ca0` | 1 | runtime fail-stop loop fall-through | `True` | `fe` | `ff` |
| `0x0c6c8` | 1 | UI/render fail-stop loop fall-through | `True` | `fe` | `ff` |
| `0x0f19a` | 4 | mode/range entry routed through stale state clear wrapper | `True` | `10 b5 04 46` | `1e f0 34 ba` |
| `0x25bf8` | 3 | language menu name renamed to Melayu | `True` | `45 73 70` | `4d 65 6c` |
| `0x25bfc` | 3 | language menu name renamed to Melayu | `True` | `c3 b1 61` | `79 75 20` |
| `0x2c4ea` | 2 | debug/semihosting fail-stop returns | `True` | `fe e7` | `70 47` |
| `0x2d5c0` | 14 | boot-logo delay wrapper code cave | `True` | `00 00 00 00 00 00 00 00 00 00 00 00 00 00` | `10 b5 d8 f7 94 fc c8 20 da f7 7b fa 10 bd` |
| `0x2d606` | 18 | mode/range stale state clear wrapper code cave | `True` | `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47` |
| `0x2d619` | 1 | mode/range stale state clear wrapper code cave | `True` | `00` | `bf` |
| `0x2d61b` | 3 | mode/range stale state clear wrapper code cave | `True` | `00 00 00` | `bf 2c 02` |
| `0x2d61f` | 5 | mode/range stale state clear wrapper code cave | `True` | `00 00 00 00 00` | `20 9f f1 01 08` |

## Interpretation

- The bootloader below application load base `0x08010000` is not present
  in this firmware image, so this package cannot directly overwrite it.
- The application reset vector is unchanged. Exp13 does not redirect
  normal boot/startup.
- The SD/resource loader strings for `DM30XDB1`, `LOGO-1.bmp`, and core
  system files remain byte-identical.
- Vector-table changes are limited to official self-loop fault/default
  entries redirected to a shared reset-request recovery stub.
- This audit does not prove analog accuracy. It proves the exp13 binary
  is a tightly scoped runtime recovery build rather than an updater or
  bootloader modification.
