# DM303 V4.0.1b state hook probe

Read-only search for state hooks related to measurement blank/freeze.
This report documents the state hook evidence used by the exp13
mode/range stale-state clear patch.

## v4.0

- Path: `backup\DM303 V4.0-read only\DM303V4.004.bin`
- Size: `203260` bytes
- SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`

### Exact state literal offsets

| State | Meaning | Count | Offsets |
|---:|---|---:|---|
| `0x20000130` | busy/retry countdown word near stream/status command recovery | 2 | `0x07e50`, `0x09868` |
| `0x2000022c` | shared stream/status flag byte; bit 1 early-return, bit 0 clear-on-error | 2 | `0x0986c`, `0x09b64` |
| `0x2000022d` | stream/status result byte written from r6 | 2 | `0x09870`, `0x09b68` |

### PC-literal state loads

| Load Address | Register | Literal Address | State |
|---:|---|---:|---|
| `0x08017cd0` | `r0` | `0x08017e50` | `0x20000130` |
| `0x08017cd6` | `r0` | `0x08017e50` | `0x20000130` |
| `0x08017cdc` | `r1` | `0x08017e50` | `0x20000130` |
| `0x08019558` | `r1` | `0x08019868` | `0x20000130` |
| `0x0801956a` | `r0` | `0x08019868` | `0x20000130` |
| `0x080196dc` | `r1` | `0x08019868` | `0x20000130` |
| `0x08019700` | `r0` | `0x08019868` | `0x20000130` |
| `0x0801970c` | `r1` | `0x08019868` | `0x20000130` |
| `0x08019746` | `r0` | `0x08019868` | `0x20000130` |
| `0x0801975a` | `r0` | `0x08019868` | `0x20000130` |
| `0x080197ae` | `r0` | `0x08019868` | `0x20000130` |
| `0x080197c0` | `r0` | `0x08019868` | `0x20000130` |
| `0x080196b6` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080196c0` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080197e2` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080197ea` | `r1` | `0x0801986c` | `0x2000022c` |
| `0x080197ee` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080197f6` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x08019810` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080198ac` | `r0` | `0x08019b64` | `0x2000022c` |
| `0x080198ba` | `r0` | `0x08019b64` | `0x2000022c` |
| `0x08019948` | `r0` | `0x08019b64` | `0x2000022c` |
| `0x080197d4` | `r0` | `0x08019870` | `0x2000022d` |
| `0x0801981e` | `r0` | `0x08019870` | `0x2000022d` |
| `0x080198e4` | `r0` | `0x08019b68` | `0x2000022d` |
| `0x08019a18` | `r0` | `0x08019b68` | `0x2000022d` |
| `0x08019a76` | `r0` | `0x08019b68` | `0x2000022d` |
| `0x08019acc` | `r0` | `0x08019b68` | `0x2000022d` |

### Tracked state accesses after literal load

| State | Literal Load | Access Address | Access | Instruction | Note |
|---:|---:|---:|---|---|---|
| `0x20000130` | `0x08017cd0` | `0x08017cd2` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08017cd0` | `0x08017cd4` | test | `cbz r0, #0x8017ce0` | state-derived conditional test |
| `0x20000130` | `0x08017cd6` | `0x08017cd8` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08017cdc` | `0x08017cde` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x08019558` | `0x0801955a` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x08019558` | `0x08019566` | test | `cmp r4, #0xff` | state-derived conditional test |
| `0x20000130` | `0x08019558` | `0x0801956e` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x08019558` | `0x08019572` | test | `cmp r4, #0xfe` | state-derived conditional test |
| `0x20000130` | `0x0801956a` | `0x0801956c` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x0801956a` | `0x0801956e` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x080196dc` | `0x080196de` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x080196dc` | `0x080196f0` | test | `cmp r4, #0` | state-derived conditional test |
| `0x20000130` | `0x08019700` | `0x08019702` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08019700` | `0x08019704` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x0801970c` | `0x0801970e` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x08019746` | `0x08019748` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08019746` | `0x0801974a` | test | `cbz r0, #0x801975a` | state-derived conditional test |
| `0x20000130` | `0x0801975a` | `0x0801975c` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x0801975a` | `0x0801975e` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x080197ae` | `0x080197b0` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x080197ae` | `0x080197b2` | test | `cbz r0, #0x80197c0` | state-derived conditional test |
| `0x20000130` | `0x080197c0` | `0x080197c2` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x080197c0` | `0x080197c4` | test | `cbz r0, #0x80197d2` | state-derived conditional test |
| `0x2000022c` | `0x080196b6` | `0x080196b8` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080196b6` | `0x080196ba` | bit-op | `and r0, r0, #2` | bit manipulation after state load |
| `0x2000022c` | `0x080196c0` | `0x080196c2` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197e2` | `0x080197e4` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197e2` | `0x080197e6` | bit-op | `bic r0, r0, #1` | bit manipulation after state load |
| `0x2000022c` | `0x080197ea` | `0x080197ec` | write | `strb r0, [r1]` | memory store through state pointer |
| `0x2000022c` | `0x080197ee` | `0x080197f0` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197f6` | `0x080197f8` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197f6` | `0x08019808` | test | `cbnz r4, #0x8019810` | state-derived conditional test |
| `0x2000022c` | `0x08019810` | `0x08019812` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x08019810` | `0x08019814` | bit-op | `and r0, r0, #1` | bit manipulation after state load |
| `0x2000022c` | `0x080198ac` | `0x080198ae` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080198ac` | `0x080198b0` | bit-op | `and r0, r0, #1` | bit manipulation after state load |
| `0x2000022c` | `0x080198ba` | `0x080198bc` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080198ba` | `0x080198be` | bit-op | `and r0, r0, #4` | bit manipulation after state load |
| `0x2000022c` | `0x08019948` | `0x0801994a` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x08019948` | `0x0801994c` | bit-op | `and r0, r0, #1` | bit manipulation after state load |
| `0x2000022d` | `0x080197d4` | `0x080197d6` | write | `strb r6, [r0]` | memory store through state pointer |
| `0x2000022d` | `0x080197d4` | `0x080197e0` | test | `cbz r6, #0x80197ee` | state-derived conditional test |
| `0x2000022d` | `0x0801981e` | `0x08019820` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x0801981e` | `0x08019822` | bit-op | `and r0, r0, #8` | bit manipulation after state load |
| `0x2000022d` | `0x080198e4` | `0x080198e6` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x080198e4` | `0x080198e8` | bit-op | `and r0, r0, #6` | bit manipulation after state load |
| `0x2000022d` | `0x08019a18` | `0x08019a1a` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x08019a18` | `0x08019a1c` | bit-op | `and r0, r0, #4` | bit manipulation after state load |
| `0x2000022d` | `0x08019a76` | `0x08019a78` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x08019a76` | `0x08019a7a` | bit-op | `and r0, r0, #2` | bit manipulation after state load |
| `0x2000022d` | `0x08019acc` | `0x08019ace` | read | `ldrb r0, [r0]` | memory load through state pointer |

### Stream/helper branch references

| Target | Name | Count | First Callers |
|---:|---|---:|---|
| `0x0801946c` | byte write helper / low-level command stream | 27 | `0x08019546 bl`, `0x08019560 bl`, `0x0801957e bl`, `0x08019590 bl`, `0x08019596 bl`, `0x080195aa bl`, `0x080195b8 bl`, `0x080195c6 bl`, `0x080195cc bl`, `0x080195d2 bl`, `0x080195ea bl`, `0x08019650 bl`, ... +15 |
| `0x08019608` | command helper | 21 | `0x0801961e bl`, `0x080196f8 bl`, `0x08019716 bl`, `0x08019752 bl`, `0x08019766 bl`, `0x0801979a bl`, `0x080197b8 bl`, `0x080197cc bl`, `0x08019832 bl`, `0x0801984a bl`, `0x08019886 bl`, `0x080198d0 bl`, ... +9 |
| `0x08019898` | stream payload helper | 16 | `0x08010340 bl`, `0x08010372 bl`, `0x0801045a bl`, `0x08011412 bl`, `0x08011580 bl`, `0x080115e2 bl`, `0x080116ee bl`, `0x080118f8 bl`, `0x080122b8 bl`, `0x08012476 bl`, `0x0801248e bl`, `0x08012504 bl`, ... +4 |
| `0x08019550` | bounded read/block helper used by measurement stream | 8 | `0x0801983c bl`, `0x08019858 bl`, `0x0801999a bl`, `0x08019a38 bl`, `0x08019a70 bl`, `0x08019ae6 bl`, `0x08019b00 bl`, `0x08019b44 bl` |
| `0x080197fc` | stream payload helper | 7 | `0x0801038c bl`, `0x08010d8c bl`, `0x08011056 bl`, `0x080113bc bl`, `0x08011440 bl`, `0x08011640 bl`, `0x0801191e bl` |
| `0x08019936` | stream/scaling-heavy payload helper | 4 | `0x08010468 bl`, `0x08012078 bl`, `0x080121ba bl`, `0x0801261e bl` |
| `0x0801959e` | read/status helper variant | 3 | `0x080198da bl`, `0x08019906 bl`, `0x08019920 bl` |
| `0x080196b2` | main stream/status transaction helper | 2 | `0x08010e84 bl`, `0x08012054 bl` |

### Mode/range helper branch references

| Target | Name | Count | First Callers |
|---:|---|---:|---|
| `0x0801f19a` | mode/range routine candidate | 104 | `0x0801f358 bl`, `0x0802029c bl`, `0x08021998 bl`, `0x08021a1e bl`, `0x08021a46 bl`, `0x08021ad2 bl`, `0x08021b18 bl`, `0x08021c4a bl`, `0x08022904 bl`, `0x0802292e bl`, `0x0802295e bl`, `0x0802298c bl`, ... +92 |
| `0x0801f0f2` | relay/range selector candidate | 91 | `0x0801f1b4 bl`, `0x0801f1bc bl`, `0x0801f1c4 bl`, `0x0801f1d2 bl`, `0x0801f1da bl`, `0x0801f1e2 bl`, `0x0801f24c bl`, `0x0801f254 bl`, `0x0801f25c bl`, `0x0801f26a bl`, `0x0801f272 bl`, `0x0801f27a bl`, ... +79 |
| `0x0801f0ac` | mode-switch helper | 2 | `0x0801f304 bl`, `0x0801f310 bl` |

## v4.0.1b-exp13

- Path: `dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin`
- Size: `203260` bytes
- SHA-256: `fbe05118e33743fb56679d5edd1eb2019c1d82e39f499c1459fe89401ce8130b`

### Exact state literal offsets

| State | Meaning | Count | Offsets |
|---:|---|---:|---|
| `0x20000130` | busy/retry countdown word near stream/status command recovery | 2 | `0x07e50`, `0x09868` |
| `0x2000022c` | shared stream/status flag byte; bit 1 early-return, bit 0 clear-on-error | 3 | `0x0986c`, `0x09b64`, `0x2d61c` |
| `0x2000022d` | stream/status result byte written from r6 | 2 | `0x09870`, `0x09b68` |

### PC-literal state loads

| Load Address | Register | Literal Address | State |
|---:|---|---:|---|
| `0x08017cd0` | `r0` | `0x08017e50` | `0x20000130` |
| `0x08017cd6` | `r0` | `0x08017e50` | `0x20000130` |
| `0x08017cdc` | `r1` | `0x08017e50` | `0x20000130` |
| `0x08019558` | `r1` | `0x08019868` | `0x20000130` |
| `0x0801956a` | `r0` | `0x08019868` | `0x20000130` |
| `0x080196dc` | `r1` | `0x08019868` | `0x20000130` |
| `0x08019700` | `r0` | `0x08019868` | `0x20000130` |
| `0x0801970c` | `r1` | `0x08019868` | `0x20000130` |
| `0x08019746` | `r0` | `0x08019868` | `0x20000130` |
| `0x0801975a` | `r0` | `0x08019868` | `0x20000130` |
| `0x080197ae` | `r0` | `0x08019868` | `0x20000130` |
| `0x080197c0` | `r0` | `0x08019868` | `0x20000130` |
| `0x080196b6` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080196c0` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080197e2` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080197ea` | `r1` | `0x0801986c` | `0x2000022c` |
| `0x080197ee` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080197f6` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x08019810` | `r0` | `0x0801986c` | `0x2000022c` |
| `0x080198ac` | `r0` | `0x08019b64` | `0x2000022c` |
| `0x080198ba` | `r0` | `0x08019b64` | `0x2000022c` |
| `0x08019948` | `r0` | `0x08019b64` | `0x2000022c` |
| `0x0803d60a` | `r1` | `0x0803d61c` | `0x2000022c` |
| `0x080197d4` | `r0` | `0x08019870` | `0x2000022d` |
| `0x0801981e` | `r0` | `0x08019870` | `0x2000022d` |
| `0x080198e4` | `r0` | `0x08019b68` | `0x2000022d` |
| `0x08019a18` | `r0` | `0x08019b68` | `0x2000022d` |
| `0x08019a76` | `r0` | `0x08019b68` | `0x2000022d` |
| `0x08019acc` | `r0` | `0x08019b68` | `0x2000022d` |

### Tracked state accesses after literal load

| State | Literal Load | Access Address | Access | Instruction | Note |
|---:|---:|---:|---|---|---|
| `0x20000130` | `0x08017cd0` | `0x08017cd2` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08017cd0` | `0x08017cd4` | test | `cbz r0, #0x8017ce0` | state-derived conditional test |
| `0x20000130` | `0x08017cd6` | `0x08017cd8` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08017cdc` | `0x08017cde` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x08019558` | `0x0801955a` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x08019558` | `0x08019566` | test | `cmp r4, #0xff` | state-derived conditional test |
| `0x20000130` | `0x08019558` | `0x0801956e` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x08019558` | `0x08019572` | test | `cmp r4, #0xfe` | state-derived conditional test |
| `0x20000130` | `0x0801956a` | `0x0801956c` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x0801956a` | `0x0801956e` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x080196dc` | `0x080196de` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x080196dc` | `0x080196f0` | test | `cmp r4, #0` | state-derived conditional test |
| `0x20000130` | `0x08019700` | `0x08019702` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08019700` | `0x08019704` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x0801970c` | `0x0801970e` | write | `str r0, [r1]` | memory store through state pointer |
| `0x20000130` | `0x08019746` | `0x08019748` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x08019746` | `0x0801974a` | test | `cbz r0, #0x801975a` | state-derived conditional test |
| `0x20000130` | `0x0801975a` | `0x0801975c` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x0801975a` | `0x0801975e` | test | `cmp r0, #0` | state-derived conditional test |
| `0x20000130` | `0x080197ae` | `0x080197b0` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x080197ae` | `0x080197b2` | test | `cbz r0, #0x80197c0` | state-derived conditional test |
| `0x20000130` | `0x080197c0` | `0x080197c2` | read | `ldr r0, [r0]` | memory load through state pointer |
| `0x20000130` | `0x080197c0` | `0x080197c4` | test | `cbz r0, #0x80197d2` | state-derived conditional test |
| `0x2000022c` | `0x080196b6` | `0x080196b8` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080196b6` | `0x080196ba` | bit-op | `and r0, r0, #2` | bit manipulation after state load |
| `0x2000022c` | `0x080196c0` | `0x080196c2` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197e2` | `0x080197e4` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197e2` | `0x080197e6` | bit-op | `bic r0, r0, #3` | bit manipulation after state load |
| `0x2000022c` | `0x080197ea` | `0x080197ec` | write | `strb r0, [r1]` | memory store through state pointer |
| `0x2000022c` | `0x080197ee` | `0x080197f0` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197f6` | `0x080197f8` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080197f6` | `0x08019808` | test | `cbnz r4, #0x8019810` | state-derived conditional test |
| `0x2000022c` | `0x08019810` | `0x08019812` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x08019810` | `0x08019814` | bit-op | `and r0, r0, #1` | bit manipulation after state load |
| `0x2000022c` | `0x080198ac` | `0x080198ae` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080198ac` | `0x080198b0` | bit-op | `and r0, r0, #1` | bit manipulation after state load |
| `0x2000022c` | `0x080198ba` | `0x080198bc` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x080198ba` | `0x080198be` | bit-op | `and r0, r0, #4` | bit manipulation after state load |
| `0x2000022c` | `0x08019948` | `0x0801994a` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022c` | `0x08019948` | `0x0801994c` | bit-op | `and r0, r0, #1` | bit manipulation after state load |
| `0x2000022c` | `0x0803d60a` | `0x0803d60c` | read | `ldrb r2, [r1]` | memory load through state pointer |
| `0x2000022c` | `0x0803d60a` | `0x0803d60e` | bit-op | `bic r2, r2, #3` | bit manipulation after state load |
| `0x2000022c` | `0x0803d60a` | `0x0803d612` | write | `strb r2, [r1]` | memory store through state pointer |
| `0x2000022d` | `0x080197d4` | `0x080197d6` | write | `strb r6, [r0]` | memory store through state pointer |
| `0x2000022d` | `0x080197d4` | `0x080197e0` | test | `cbz r6, #0x80197ee` | state-derived conditional test |
| `0x2000022d` | `0x0801981e` | `0x08019820` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x0801981e` | `0x08019822` | bit-op | `and r0, r0, #8` | bit manipulation after state load |
| `0x2000022d` | `0x080198e4` | `0x080198e6` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x080198e4` | `0x080198e8` | bit-op | `and r0, r0, #6` | bit manipulation after state load |
| `0x2000022d` | `0x08019a18` | `0x08019a1a` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x08019a18` | `0x08019a1c` | bit-op | `and r0, r0, #4` | bit manipulation after state load |
| `0x2000022d` | `0x08019a76` | `0x08019a78` | read | `ldrb r0, [r0]` | memory load through state pointer |
| `0x2000022d` | `0x08019a76` | `0x08019a7a` | bit-op | `and r0, r0, #2` | bit manipulation after state load |
| `0x2000022d` | `0x08019acc` | `0x08019ace` | read | `ldrb r0, [r0]` | memory load through state pointer |

### Stream/helper branch references

| Target | Name | Count | First Callers |
|---:|---|---:|---|
| `0x0801946c` | byte write helper / low-level command stream | 27 | `0x08019546 bl`, `0x08019560 bl`, `0x0801957e bl`, `0x08019590 bl`, `0x08019596 bl`, `0x080195aa bl`, `0x080195b8 bl`, `0x080195c6 bl`, `0x080195cc bl`, `0x080195d2 bl`, `0x080195ea bl`, `0x08019650 bl`, ... +15 |
| `0x08019608` | command helper | 21 | `0x0801961e bl`, `0x080196f8 bl`, `0x08019716 bl`, `0x08019752 bl`, `0x08019766 bl`, `0x0801979a bl`, `0x080197b8 bl`, `0x080197cc bl`, `0x08019832 bl`, `0x0801984a bl`, `0x08019886 bl`, `0x080198d0 bl`, ... +9 |
| `0x08019898` | stream payload helper | 16 | `0x08010340 bl`, `0x08010372 bl`, `0x0801045a bl`, `0x08011412 bl`, `0x08011580 bl`, `0x080115e2 bl`, `0x080116ee bl`, `0x080118f8 bl`, `0x080122b8 bl`, `0x08012476 bl`, `0x0801248e bl`, `0x08012504 bl`, ... +4 |
| `0x08019550` | bounded read/block helper used by measurement stream | 8 | `0x0801983c bl`, `0x08019858 bl`, `0x0801999a bl`, `0x08019a38 bl`, `0x08019a70 bl`, `0x08019ae6 bl`, `0x08019b00 bl`, `0x08019b44 bl` |
| `0x080197fc` | stream payload helper | 7 | `0x0801038c bl`, `0x08010d8c bl`, `0x08011056 bl`, `0x080113bc bl`, `0x08011440 bl`, `0x08011640 bl`, `0x0801191e bl` |
| `0x08019936` | stream/scaling-heavy payload helper | 4 | `0x08010468 bl`, `0x08012078 bl`, `0x080121ba bl`, `0x0801261e bl` |
| `0x0801959e` | read/status helper variant | 3 | `0x080198da bl`, `0x08019906 bl`, `0x08019920 bl` |
| `0x080196b2` | main stream/status transaction helper | 2 | `0x08010e84 bl`, `0x08012054 bl` |

### Mode/range helper branch references

| Target | Name | Count | First Callers |
|---:|---|---:|---|
| `0x0801f19a` | mode/range routine candidate | 104 | `0x0801f358 bl`, `0x0802029c bl`, `0x08021998 bl`, `0x08021a1e bl`, `0x08021a46 bl`, `0x08021ad2 bl`, `0x08021b18 bl`, `0x08021c4a bl`, `0x08022904 bl`, `0x0802292e bl`, `0x0802295e bl`, `0x0802298c bl`, ... +92 |
| `0x0801f0f2` | relay/range selector candidate | 91 | `0x0801f1b4 bl`, `0x0801f1bc bl`, `0x0801f1c4 bl`, `0x0801f1d2 bl`, `0x0801f1da bl`, `0x0801f1e2 bl`, `0x0801f24c bl`, `0x0801f254 bl`, `0x0801f25c bl`, `0x0801f26a bl`, `0x0801f272 bl`, `0x0801f27a bl`, ... +79 |
| `0x0801f0ac` | mode-switch helper | 2 | `0x0801f304 bl`, `0x0801f310 bl` |
| `0x0803d606` | exp13 mode/range stale state clear wrapper | 1 | `0x0801f19a b.w` |

## Decision

- The visible V4.0/V4.0.1b state literals remain concentrated in the
  stream/status helper region, especially `0x2000022c`, `0x2000022d`,
  and `0x20000130`.
- Exp13 uses the confirmed mode/range entry at `0x0801f19a` as the
  state-reset hook. The patch preserves the original prologue, clears
  only bits `0` and `1` from `0x2000022c`, then continues original
  relay/range code.
- This evidence supports the exp13 recovery hook, not an immediate
  ADC/RMS/math rewrite. A math/filter patch still needs a confirmed
  measurement-buffer or RMS accumulator contract.
