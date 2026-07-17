# DM303 V3.13 / V3.16 / V4.0 switching-path comparison

Date: 2026-07-17
Analyst pass: three-way read-only binary comparison targeting the V4.0 field
symptoms: ~30 s blank on ammeter AC<->DC, reading noise, freeze/blank,
zero/calibration trouble. V3.13 had never been analyzed before this pass.

Nothing under `backup/` was modified. All outputs are under `docs/` and
`analysis/`.

## 0. Image identity

| Image | Path | Size | SHA-256 (prefix) | Reset |
|---|---|---:|---|---:|
| V3.13 | `backup/SD-file_DM303_update_US240104-read only/DM303-V3.13.bin` | 221,704 | `c62dbd24…` | `0x08016e21` |
| V3.16 | `backup/DM303 V3.16-read only/DM303V316.bin` | 223,276 | `0c8da839…` | `0x08016e21` |
| V4.0 | `backup/DM303 V4.0-read only/DM303V4.004.bin` | 203,260 | `64faaffb…` | `0x0801754d` |

V3.13 and V3.16 share the reset vector, the version-string block layout
(`0x02ca3`…`0x02cf4`), and byte-identical call structure in the ammeter
screen. V3.13 identifies as `BT100MM V3.13`.

Method note: constants were located two independent ways — an
alignment-proof raw byte scan of every `movw`/`movs` encoding
(`analysis/v313-v316-v40-constant-map.py`) and a full capstone linear sweep
resolving `cmp.w`/`mov.w`/literal-pool loads. Function counterparts were
matched by call-graph shape (selector / mode-routine / draw-text call
orders) and by identical immediate sequences, then read in full from the
disassembly dumps listed in §7.

---

## (a) Constant / cluster map per firmware

### The 15000 (`0x3a98`) guard question — answered: V3.x HAS them

`movw rd, #0x3a98` occurrences (all registers, raw byte scan):

| Firmware | `r0` sites | `r1` sites | `r8` sites | Total |
|---|---|---|---|---:|
| V3.13 | `0x14056`, `0x1407e` | `0x14e7c`, `0x14ea4` | `0x1d526` (ammeter fn) | 5 |
| V3.16 | `0x1430e`, `0x14336` | `0x15134`, `0x1515c` | `0x1d7de` (ammeter fn) | 5 |
| V4.0 | `0x14b0e`, `0x14b36`, `0x1d1a4`, `0x1d1c0`, `0x1eaa0`, `0x22528`, `0x239a6` | `0x15934`, `0x1595c` | — | 9 |

The two `r0` pairs and the two `r1` sites sit in the **same** clusters in all
three firmwares:

| Cluster (role) | V3.13 | V3.16 | V4.0 |
|---|---|---|---|
| mode/range helper cluster, `movw r0,#0x3a98` ×2 | `0x08024056`/`0x0802407e` | `0x0802430e`/`0x08024336` | `0x08024b0e`/`0x08024b36` |
| state-machine cluster, `movw r1,#0x3a98` ×2 | `0x08024e7c`/`0x08024ea4` | `0x08025134`/`0x0802515c` | `0x08025934`/`0x0802595c` |
| state-machine `cmp.w r0,#0x3e80` (16000) ×2 | `0x08024da6`/`0x08024dd0` | `0x0802505e`/`0x08025088` | `0x0802585e`/`0x08025888` |
| state-machine `movw #0x5dc` (1500) ×2 | `0x08024e02`/`0x08024e2a` | `0x080250ba`/`0x080250e2` | `0x080258ba`/`0x080258e2` |

The full state-machine threshold sequence is **identical** in all three:
`0x118, 0x12c, 0x640 ×2, 0x3e80 ×2, 0x5dc ×2, 0x3a98 ×2`, in the same
order, each followed by `bl <mode_routine>` (V3.13 `0x0801dfe2`, V3.16
`0x0801e29a`, V4.0 `0x0801f19a`). The sibling clusters
(`0x96/0x514/0x44c/0x6e/0x15e/0x118/0x12c` threshold families at
V3.13 `0x080229xx`/`0x08023exx`, V3.16 `0x080240xx`/`0x080242xx`, V4.0
`0x080218xx`/`0x080228xx`) also match constant-for-constant.

**Consequence for the repair line:** every guard the repair-a…i profiles
capped (15000→1500 at the six state-2/helper sites, 16000→1600 cmp gates)
exists byte-for-byte in V3.13 — the firmware that switches *smoothly*.
Those guards were never the regression. This is consistent with the
on-device result: all those caps changed nothing.

### What the `0x3a98`/`0x2ee0` values in the screen functions actually are

In the V4.0 ammeter function the prologue stores
`[sp,#0x7c]=0x3a98, [sp,#0x78]=0x2ee0, [sp,#0x30]=0x3a98, [sp,#0x2c]=0x2ee0`.
The only later use of `[sp,#0x30]`/`[sp,#0x2c]` is a min/max tracker
(`0x0802dd66`–`0x0802dd80`: replace slot when the current reading is
smaller/larger). `[sp,#0x7c]` is overwritten with a runtime value right
after the mode-routine call. V3.x keeps the same pair in registers
(`r8=0x3a98, sb=0x2ee0`) and reloads them at the same point. **They are
min/max display seeds (15000 = "big initial min", 12000 = "initial max"),
not delays.** The five V4.0-only `0x3a98` sites (`0x1eaa0`, `0x22528`,
`0x239a6` plus the ammeter pair) are the same seed pattern in the prologues
of the other redesigned screen functions.

### The constants that actually differ

| Constant | V3.13 | V3.16 | V4.0 |
|---|---|---|---|
| `movs r0,#0xf0` (240) in ammeter fn | absent | absent | `0x1d1da` (init of window slot `[sp,#0x10]`) |
| `mov.w r0,#0x258` (600) total sites | 10 (all buffer/waveform dimensions) | 10 | 10 — but site `0x1df0c` is the **ammeter AC↔DC switch window** |
| `mov.w r0,#0x168` (360) | 0 | 0 | 2 — `0x1df40` (ammeter switch window, other direction), `0x1eac0` (sibling screen) |
| selector settle waits 2 / 3 / 10 (and `0x6e`=110 branch) | `0x0801def4` | `0x0801e1ac` | `0x0801f0f2` — identical sequence |
| `0x200000e6` sample-count refs | many (producer + all consumers) | many | **zero** |
| `0x20001560` 600-sample ring refs | many | many | **zero** |
| `0x2000022c` stream-state byte pools | 1 | 1 | 2 |

---

## (b) Function-match table

| Role | V3.13 | V3.16 | V4.0 | Match evidence |
|---|---|---|---|---|
| relay/range selector | `0x0801def4` | `0x0801e1ac` | `0x0801f0f2` | identical body plan: GPIO RMW via `0x0803dc5e/0x0803dc56` family, delay calls `movs #2 / #3 / #0x6e / #0xa` in the same order |
| selector helper (called once from ammeter fn) | `0x0801e184` | `0x0801e43c` | `0x08017ed8`* | same call-site position (*V4.0's is a different, TIM2/AFE-rate setup routine — see §c) |
| mode/range routine | `0x0801dfe2` | `0x0801e29a` | `0x0801f19a` | only shared `bl` target of every guard-cluster site; same prologue (`ldrb; cmp #0; bne; ldrh; cmp #4`) |
| ammeter screen fn | `0x0802d512` | `0x0802d7ca` | `0x0802d190` | identical prologue constants (100, 0x3a98/0x2ee0 pair, 1), identical draw-text triple (entries 27=AC, 29=20A, 30=mA), identical call sequence draw×3 → delay → selector(0) → helper(0) → mode=3 → mode_routine() |
| sample acquisition | ADC-EOC ISR family `0x08017882`… fills ring `0x20001560` under counter `0x200000e6` (wrap `0x752f`) | same | **none — replaced by per-screen polled reader `0x080171de`** | V4.0 has zero refs to ring/counter; `0x080171de` has 16 callers |
| AC scale factor | ×1.105 (sum/600, ×65×17/1000) | ×1.105 | ×0x456/0x3e8 (=1.110) | same calibration math, different acquisition |

V4.0 `0x080171de` callers (screens redesigned onto the polled path):
`0x0802abdc, 0x0802b176, 0x0802b18c, 0x0802d460 (ammeter), 0x0802e31e,
0x0802e6d4, 0x0802e6f0, 0x0802e70c, 0x0802e7ca, 0x0802ec58, 0x0802f2cc,
0x0802f73a, 0x0803276a, 0x08033ac4, 0x08033e54, 0x08034310`.

---

## (c) Structural switching-path differences (the actual regression)

### V3.13/V3.16 ammeter AC↔DC path (smooth)

1. Entry: draw AC/20A/mA labels; `selector(0)`; `helper(0)`; mode=3;
   `mode_routine()`.
2. Wait for **first paint**: spin until `*(0x200000e6) >= 0xc8` (200
   background samples already in the ring) — `0x0802d7f8` (V3.13) /
   `0x0802dab0` (V3.16).
3. Loop: consume the shared 600-sample ring (`0x20001560`) — min/max scan
   over `0x258` samples, scaled sum; AC averages 600 samples, DC path
   divides by 60. The ADC-EOC ISR keeps filling the ring at hardware pace
   while the UI runs. The screen never touches the AFE and never polls a
   conversion-ready pin; the AC↔DC switch is just a relay/mode change plus
   ring refill.

### V4.0 ammeter AC↔DC path (~30 s blank)

1. Same entry sequence, then the function itself **synchronously collects
   samples**: loop `bl 0x080171de` (poll DRDY = GPIOC pin 8; if set, no
   sample; else bit-bang one 24-bit word out, clock = GPIOB pin 2, sign-fix
   `eor/sub 0x800000`), store into a private 240-word buffer, until
   `count >= [sp,#0x10]`.
2. The window slot `[sp,#0x10]` has exactly three writes (verified across
   the whole function `0x0802d190`–`0x0802df8a`):
   - `0x0802d1da`: `movs r0,#0xf0` → **240** (entry / normal update)
   - `0x0802df0c`: `mov.w r0,#0x258` → **600**, written by the AC↔DC
     switch-state handler (state `0x2d`, direction A: AFE command `0x37`
     via `0x08016d34`, then `0x08016d5a(0,0)`, `0x08016fa4`)
   - `0x0802df40`: `mov.w r0,#0x168` → **360**, same handler, direction B
     (AFE command `0x16`, `0x08016d5a(1,1)`, `0x08016fa4`)
3. While collecting, every >10-tick stall without a sample re-issues the
   AFE command sequence (`bl 0x080170dc`; `0x08016d34(0x37|0x16)`;
   `0x08016d5a`; `0x08016d12(1,8)`; `0x08016fa4`) — `0x0802d48c`–
   `0x0802d4b4`. These are bit-banged register writes to the analog
   front-end (RMW command bytes via `0x08016caa`/`0x08016c2e`, strobe
   pattern in `0x08016fa4`). V3.x performs **no** AFE access during
   acquisition.
4. Only after the window fills does the screen compute (mean = sum/window,
   min/max, AC ×1.110) and redraw. During the whole collection the display
   shows the state-7 "switching" animation — the reported blank.

**Why repair-i (240→64 at `0x1d1da`) could not work on-device:** the
patched initializer only sets the *normal-update* window. Every AC↔DC
switch immediately overwrites the same slot with 600 or 360 at
`0x0802df0c`/`0x0802df40` — offsets no repair profile ever touched. 600
polled conversions at the field-observed ~30 s blank implies an effective
~20 conversions/s in this path; 240 would be ~12 s, and the unpatched
600-window reproduces the field number exactly.

**Noise/zero, same root:** V4.0's averaging window is 240 samples vs
V3.x's 600 (≈1.58× higher reading noise from averaging alone), and the
10-tick watchdog re-configures the AFE mid-acquisition — a noise/zero
disturbance V3.x does not have. Freeze/blank: the screen blocks on DRDY
with only the re-kick as recovery, so a stalled conversion path presents
as a freeze.

The selector (2/3/10 waits), mode routine, guard clusters, stream-state
byte `0x2000022c`, and AC calibration factor are unchanged across all
three firmwares — the vendor regression is the **acquisition redesign**:
shared background ADC ring → per-screen synchronous polled reader with
inflated post-switch windows.

---

## (d) DM30XDB1.dat verdict

- Firmware references (ASCII only; no UTF-16LE variant anywhere):
  V3.13 `0x0423c`, V3.16 `0x0423c`, V4.0 `0x04278` — all three plus the
  `Loading DM30XDB1 ...` message. All three firmwares load it.
- File (`backup/SD-file_DM303_update_US240104-read only/system/DM30xDB1.dat`,
  1,179,648 bytes) parsed record by record:
  - 34 × 92×92 RGB565 BMPs, 17,000 B each (56-byte BITMAPV3 header,
    BI_BITFIELDS masks `0xf800/0x07e0/0x001f`, top-down)
  - 7 × 8×8 RGB565 BMPs, 200 B each
  - 1 × 320×240 RGB565 full-screen image, 153,672 B (same size as
    `LOGO-1.bmp`)
  - remainder: 245,144 B of `0xFF` padding plus zero/`0x0250`-filled gaps
    between records
- No tables, headers, or numeric structures of any kind — it is a pure
  image/sprite pack provisioned to the external SPI flash at boot.

**Verdict: UI-only.** Its absence from the official V4.0 SD package can
produce missing/garbage icons (including the bitmap shown by the ammeter
"switching" animation via `0x0801bd88`) but cannot affect measurement,
calibration, or timing. It is already present in both final flash
packages; no action needed. (Oddity noted: V4.0 firmware still references
the path although the official V4.0 card omits the file — the loader
evidently tolerates that; V3.13/V3.16 cards ship it.)

---

## (e) Best-supported next patch candidate

**Candidate `v401h-repair-j` (HOLD): cap the two AC↔DC switch windows in
the V4.0 ammeter function to the vendor's own normal-update window (240).**

| File offset | Address | Current bytes | Patched bytes | Meaning |
|---:|---:|---|---|---|
| `0x1df0c` | `0x0802df0c` | `4f f4 16 70` (`mov.w r0,#0x258` = 600) | `f0 20 00 bf` (`movs r0,#0xf0` = 240; `nop`) | switch window, direction A |
| `0x1df40` | `0x0802df40` | `4f f4 b4 70` (`mov.w r0,#0x168` = 360) | `f0 20 00 bf` (`movs r0,#0xf0` = 240; `nop`) | switch window, direction B |

Why this is the best-supported candidate:

1. **Vendor evidence:** V4.0 itself uses 240 (`0xf0`) for this exact stack
   slot in this exact function for normal updates (`0x0802d1da`). The
   switch states inflate it 2.5×/1.5×. The patch makes a switch cost the
   same as one normal update — no invented constants.
2. **Explains the device results:** repair-i changed only the initializer
   and the ~30 s persisted; the operative constants after any switch are
   600/360 at these two untouched offsets.
3. **Field correlation:** 600 samples ≈ 30 s matches the reported blank;
   240 predicts ~12 s (measured against the same cadence).
4. **Self-consistent:** the slot is also the averaging divisor
   (`0x0802d50e`/`0x0802d5d0`: mean = sum/window), so mean math stays
   correct after the patch. Both sites are flag-safe (followed by
   `str r0,[sp,#0x10]` and immediates; no live flags dependency).
5. **Minimal and isolated:** 8 bytes, ammeter function only, AFE command
   sequence untouched (unlike the failed repair-c settle changes).
   Sibling screens with the same pattern (`0x0802ea80`-family window 360
   at `0x1eac0`, plus screens at `0x080324f8`/`0x08033986`) are
   deliberately excluded — one change at a time.

What this patch does **not** claim to fix: the structural difference
(V4.0's synchronous polled acquisition vs V3.x's background ring) cannot
be reverted by byte patch. If ~12 s residual latency is unacceptable, the
next investigative step is the 10-tick AFE re-kick
(`0x0802d48c`–`0x0802d4b4`) — whether conversions free-run or require the
kick cannot be settled statically; NOP-ing it is *not* proposed without
device evidence.

If repair-j fails on-device, the discriminating measurements are:

- Time AC→DC and DC→AC separately. Window asymmetry 600:360 predicts a
  5:3 ratio; a symmetric residual delay points at the AFE re-kick or the
  mode routine instead.
- Time a plain range toggle (20A↔mA) and a non-switch display update:
  if a normal update also takes ~12 s, the cadence itself is the story
  and the re-kick becomes the primary suspect.
- Observe whether the state-7 "switching" animation is visible during the
  blank — confirms the device is inside the collection loop, not the
  state machine.

---

## 7. Evidence artifacts produced in this pass

Scripts (repo root, portable Python):
- `analysis/v313-v316-v40-constant-map.py` → `analysis/constant-map-output.txt`
- `analysis/v313-v316-v40-function-match.py`

Disassembly dumps:
- `docs/disasm-v313-ammeter-fn.txt`, `docs/disasm-v316-ammeter-fn.txt`,
  `docs/disasm-v40-ammeter-fn.txt`
- `docs/disasm-v313-ammeter-loop.txt`, `docs/disasm-v316-ammeter-loop.txt`,
  `docs/disasm-v40-ammeter-loop.txt`
- `docs/disasm-v40-ammeter-fn-tail.txt`, `docs/disasm-v40-ammeter-tail2.txt`
- `docs/disasm-v313-mode-routine.txt`, `docs/disasm-v313-selector.txt`
  (`docs/disasm-v316-mode-routine.txt`, `docs/disasm-v40-mode-routine.txt`
  were also regenerated by the matcher)
- helpers: `docs/disasm-v40-helper-171de.txt` (DRDY reader),
  `docs/disasm-v40-helper-16d34.txt`, `docs/disasm-v40-helper-16fa4.txt`,
  `docs/disasm-v40-helper-17ed8.txt`, `docs/disasm-v40-helper-16caa.txt`,
  `docs/disasm-v316-helper-17768.txt`, `docs/disasm-v316-helper-1b95c.txt`
  (V3.16 waveform consumer), `docs/disasm-v40-mode-routine.txt`,
  `docs/disasm-v316-mode-routine.txt`

Status: analysis only, no package built, no flash recommended. Any
repair-j build stays HOLD per `note.txt` rules until the user accepts the
risk and the strict gates pass.
