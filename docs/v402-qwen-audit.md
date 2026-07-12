# DM303 V4.0.2b Qwen audit

Status: do not flash the current Qwen-generated V4.0.2b candidate.

This audit was made after the firmware was moved under `dm303_firmware/` and
after `firmware-candidates/v4.0.2-beta/DM303V4.0.2-beta.bin` appeared in the
branch.

## Repository issue

`dm303_firmware` is currently recorded by Git as a gitlink/submodule pointer:

```text
160000 commit 20e60f9fd253894b9db9998cd94856d6c97b2262 dm303_firmware
```

There is no `.gitmodules` file. GitHub therefore cannot show the folder
contents as normal files. The fix is to remove the gitlink from the index and
add `dm303_firmware/` as a normal folder.

## Hashes

| File | SHA-256 |
|---|---|
| Official V4.0 reference `backup/DM303 V4.0-read only/DM303V4.004.bin` | `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158` |
| V4.0.1 beta candidate | `a8fe14bb34e3a58eaf88a6eb33ed58517416885cc6edcc948a4f7ac5713e19b0` |
| Qwen V4.0.2b candidate | `2fe3d55595eb7e3c9cc76055e8fe6185ef2ec9135ac8804b9feff94f2bf5ec8d` |

The V4.0.2b binary is the same size as V4.0.1b and changes only 58 bytes across
26 byte ranges.

## Critical findings

Most V4.0.2b feature claims are not supported by the byte-level evidence.

| Offset | Claim | Audit result |
|---:|---|---|
| `0x04f00` | Insert PWM duty table | Overwrites ASCII loader text beginning `DAT\0Loading`; this is not an unused code cave. |
| `0x05210` | Activate Bahasa Melayu language slot | Overwrites executable UI code, including `movs r1,#0x87` and `movw r3,#0x13f`; this is not a language table. |
| `0x05220` | Add Malay as selectable language | Changes an argument from `movs r0,#0x14` to `movs r0,#2` in code, not a proven menu count. |
| `0x08c45` | Long-press detection | Uses an odd offset and corrupts the existing `pop {r4, pc}` / next function prologue boundary. |
| `0x09100` | RTC read call | Changes the first halfword of a normal data-pack routine. It does not encode a valid `BL` target. |
| `0x0c150` | Median filter | Partially overwrites a 32-bit `ubfx` instruction and decodes as a `bl` to an out-of-image address. |
| `0x0d100` | DMA recovery | Partially overwrites a real GPIO/helper `BL`, producing invalid instruction flow. |
| `0x0d150` | DMA overflow check | Replaces `movs r0,#1` with bytes that decode as an unrelated 32-bit instruction. |
| `0x07700` | Watchdog feed | Replaces a function prologue `push {r4, lr}` with an unrelated 32-bit instruction. |
| `0x0e100`-`0x0e130` | Dark theme color tuning | Overwrites decimal/string rendering code, not a confirmed RGB palette table. |

The only changes that look structurally conservative are:

- Version text from `V4.0.1b` to `V4.0.2b`.
- Relay settle delay at `0x0f192` from 50 to 100 ticks.

The relay delay alone is not enough to claim noise, accuracy, latency, true RMS,
spike, overload, Bahasa Melayu, clock/date, battery percent, or brightness
control improvements.

## Backlight finding

The real light key path found in V4.0.1b is:

- Key code `0x1e` calls `0x080185bc`.
- `0x080185bc` toggles byte state `0x20000156`.
- It sets/resets `GPIOD` bit `0x08`.

That is a digital on/off GPIO path. The current binary evidence does not show a
safe PWM brightness path for 3 brightness levels. A 3-level brightness feature
needs a confirmed timer/PWM route or a carefully hooked software PWM routine;
Qwen's `TIM4 CH2` assumption is not proven here.

## Safe next action

Do not use `firmware-candidates/v4.0.2-beta/DM303V4.0.2-beta.bin` on the device.

Continue from the known flashable V4.0.1b baseline and only add a new V4.0.2
candidate after each patch point is confirmed by disassembly and guarded by
exact byte checks.
