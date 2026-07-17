# DM303 V4.0.1b exp17 clean resource flash safety audit

Official: `backup/DM303 V4.0-read only/DM303V4.004.bin`
Current: `dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin`

## Result

- Overall: `PASS`
- Official SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Current SHA-256: `d3760c42731a5fd6c0db508b51df85b1725046f028d767315916c4ee58904b77`
- Size unchanged: `PASS`
- Reset vector unchanged: `PASS`
- All changed bytes inside allowed exp17 clean-resource intervals: `PASS`
- Critical exp17 clean-resource byte guards present: `PASS`
- Startup/resource-loader strings unchanged: `PASS`

## Critical Bytes

| Offset | Name | Expected | Actual | OK |
|---:|---|---|---|---|
| `0x02ca0` | visible main version marker | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 65 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 65 00` | `PASS` |
| `0x02cb0` | visible secondary version marker | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 65 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 65 00` | `PASS` |
| `0x07554` | SYSRESETREQ stub prefix | `02 48 02 49 01 60 bf f3 4f 8f` | `02 48 02 49 01 60 bf f3 4f 8f` | `PASS` |
| `0x09ca0` | runtime fail-stop loop fall-through | `ff e7` | `ff e7` | `PASS` |
| `0x0c6c8` | UI/render fail-stop loop fall-through | `ff e7` | `ff e7` | `PASS` |
| `0x2c4ea` | debug/semihosting fail-stop returns | `70 47` | `70 47` | `PASS` |

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
| `0x07554` | `10` | fault/default SYSRESETREQ recovery stub | `PASS` |
| `0x07560` | `8` | fault/default SYSRESETREQ recovery stub | `PASS` |
| `0x09ca0` | `1` | runtime fail-stop loop fall-through | `PASS` |
| `0x0c6c8` | `1` | UI/render fail-stop loop fall-through | `PASS` |
| `0x2c4ea` | `2` | debug/semihosting fail-stop returns | `PASS` |

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
