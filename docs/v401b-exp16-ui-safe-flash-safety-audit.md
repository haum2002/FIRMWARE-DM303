# DM303 V4.0.1b exp16 UI-safe flash safety audit

Official: `backup/DM303 V4.0-read only/DM303V4.004.bin`
Current: `dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin`

## Result

- Overall: `PASS`
- Official SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Current SHA-256: `29a8bd71cba65538ba25d8e76aa5122234f9a28ad957287ba82fbf4fdf6c60af`
- Size unchanged: `PASS`
- Reset vector unchanged: `PASS`
- All changed bytes inside allowed exp16 UI-safe intervals: `PASS`
- Critical exp16 UI-safe byte guards present: `PASS`
- Startup/resource-loader strings unchanged: `PASS`

## Critical Bytes

| Offset | Name | Expected | Actual | OK |
|---:|---|---|---|---|
| `0x02ca0` | visible main version marker | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `PASS` |
| `0x02cb0` | visible secondary version marker | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 64 00` | `PASS` |
| `0x06a06` | low byte-IO entry branch | `00 f0 23 b8` | `00 f0 23 b8` | `PASS` |
| `0x06a50` | bounded wrapper prefix | `70 b5 05 46 40 f6 a0 76` | `70 b5 05 46 40 f6 a0 76` | `PASS` |
| `0x07554` | SYSRESETREQ stub prefix | `02 48 02 49 01 60 bf f3 4f 8f` | `02 48 02 49 01 60 bf f3 4f 8f` | `PASS` |
| `0x09570` | stream-read retry removed | `00 bf` | `00 bf` | `PASS` |
| `0x0967c` | command 0x40 retry clamp | `60` | `60` | `PASS` |
| `0x09682` | command 0x48 retry clamp | `60` | `60` | `PASS` |
| `0x096be` | exp14 stream busy gate | `02 e0` | `02 e0` | `PASS` |
| `0x09706` | command 0x40 busy failure route | `4c` | `4c` | `PASS` |
| `0x09758` | command/status retry removed | `00 bf` | `00 bf` | `PASS` |
| `0x097be` | mode/status retry removed | `00 bf` | `00 bf` | `PASS` |
| `0x097e6` | stream error cleanup clears bits 0 and 1 | `20 f0 03 00` | `20 f0 03 00` | `PASS` |
| `0x0f19a` | mode/range entry branch to wrapper | `1e f0 34 ba` | `1e f0 34 ba` | `PASS` |
| `0x1585e` | exp14 current-switch latency cap A | `b0 f5 c8 6f` | `b0 f5 c8 6f` | `PASS` |
| `0x15888` | exp14 current-switch latency cap B | `b0 f5 c8 6f` | `b0 f5 c8 6f` | `PASS` |
| `0x2c4ea` | debug/semihosting fail-stop returns | `70 47` | `70 47` | `PASS` |
| `0x2d606` | mode/range stale state clear wrapper | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `PASS` |

## Changed Ranges

| Offset | Size | Classification | OK |
|---:|---:|---|---|
| `0x0000c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00010` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00014` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00018` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0002c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00030` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00038` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00040` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00048` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0004c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00050` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00054` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0005c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00060` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00064` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00068` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00074` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00078` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0007c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00080` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00084` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0008c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000a0` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000a8` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000ac` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000bc` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000c0` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000c4` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000c8` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000cc` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000d0` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000d8` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000e0` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000e4` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000ec` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000f0` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000f4` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000f8` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x000fc` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00100` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00104` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00108` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0010c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00110` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00114` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00118` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0011c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00120` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00124` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00128` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0012c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00130` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00134` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x00138` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x0013c` | `1` | self-loop vector redirected to shared recovery stub | `PASS` |
| `0x02cac` | `3` | version identity strings | `PASS` |
| `0x02cbc` | `3` | version identity strings | `PASS` |
| `0x06a06` | `4` | low byte-IO entry branch to bounded wrapper | `PASS` |
| `0x06a50` | `1` | bounded low byte-IO wrapper code | `PASS` |
| `0x06a52` | `9` | bounded low byte-IO wrapper code | `PASS` |
| `0x06a5c` | `3` | bounded low byte-IO wrapper code | `PASS` |
| `0x06a60` | `1` | bounded low byte-IO wrapper code | `PASS` |
| `0x06a62` | `29` | bounded low byte-IO wrapper code | `PASS` |
| `0x06a80` | `32` | bounded low byte-IO wrapper code | `PASS` |
| `0x07554` | `10` | fault/default SYSRESETREQ recovery stub | `PASS` |
| `0x07560` | `8` | fault/default SYSRESETREQ recovery stub | `PASS` |
| `0x09570` | `2` | stream-read retry branch removed | `PASS` |
| `0x0967c` | `1` | command 0x40 retry clamp | `PASS` |
| `0x09682` | `1` | command 0x48 retry clamp | `PASS` |
| `0x096be` | `2` | exp14 stream busy early-return gate bypass | `PASS` |
| `0x09706` | `1` | command 0x40 busy failure error route | `PASS` |
| `0x09758` | `2` | command/status retry branch removed | `PASS` |
| `0x097be` | `2` | mode/status retry branch removed | `PASS` |
| `0x097e8` | `1` | stream error cleanup clears status bits 0 and 1 | `PASS` |
| `0x09ca0` | `1` | runtime fail-stop loop fall-through | `PASS` |
| `0x0c6c8` | `1` | UI/render fail-stop loop fall-through | `PASS` |
| `0x0f19a` | `4` | mode/range entry routed through stale state clear wrapper | `PASS` |
| `0x15860` | `2` | exp14 first current-switch latency cap | `PASS` |
| `0x1588a` | `2` | exp14 second current-switch latency cap | `PASS` |
| `0x2c4ea` | `2` | debug/semihosting fail-stop returns | `PASS` |
| `0x2d606` | `18` | mode/range stale state clear wrapper code cave | `PASS` |
| `0x2d619` | `1` | mode/range stale state clear wrapper code cave | `PASS` |
| `0x2d61b` | `3` | mode/range stale state clear wrapper code cave | `PASS` |
| `0x2d61f` | `5` | mode/range stale state clear wrapper code cave | `PASS` |

## Stable Strings

| Offset | Expected | Official | Current | OK |
|---:|---|---|---|---|
| `0x0423b` | ` Loading GBK ...` | ` Loading GBK ...` | ` Loading GBK ...` | `PASS` |
| `0x0424c` | `\system\HZK-ALL.GBK` | `\system\HZK-ALL.GBK` | `\system\HZK-ALL.GBK` | `PASS` |
| `0x04260` | `Loading DM30XDB1 ...` | `Loading DM30XDB1 ...` | `Loading DM30XDB1 ...` | `PASS` |
| `0x04278` | `\system\DM30XDB1.dat` | `\system\DM30XDB1.dat` | `\system\DM30XDB1.dat` | `PASS` |
| `0x04788` | `Loading Start-LOGO-1 ...` | `Loading Start-LOGO-1 ...` | `Loading Start-LOGO-1 ...` | `PASS` |
| `0x047a4` | `\system\LOGO-1.bmp` | `\system\LOGO-1.bmp` | `\system\LOGO-1.bmp` | `PASS` |
| `0x057f0` | `VIEW VERSION` | `VIEW VERSION` | `VIEW VERSION` | `PASS` |

## Scope

- This audit proves byte placement and startup/resource-loader integrity.
- It does not prove analog accuracy, zero-noise measurement, or hardware-side calibration.
- Device testing is still required for ammeter AC->DC latency, overload recovery, and UI visual quality.
