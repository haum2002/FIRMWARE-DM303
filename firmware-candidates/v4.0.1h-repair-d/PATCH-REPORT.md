# DM303 V4.0.1 beta patch report

Status: candidate firmware only. Bench validation is still required before flashing.

Profile: `v401h-repair-d` - repair after repair-c failed: remove relay-settle increase, keep official UI resources, exclude risky UI/render fail-stop fall-through, and test immediate current-switch mode calls.

## Safety scope

- Source firmware is not modified in place.
- Output binary size is unchanged.
- Bootloader/updater code and SD update procedure are not patched.
- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.
- Runtime anti-freeze is limited to non-UI fail-stop loops. The UI/render loop at `0x0801c6c8` is kept official to avoid fall-through drawing artifacts.
- Relay/range selector timing is kept unchanged.
- Mode-switch helper behavior is kept unchanged.
- High-level measurement stream/status retry loops use fail-fast recovery, and command `0x40` busy failure routes into the existing error/clear sequence instead of normal fall-through.
- Low byte-IO helper `0x08016a06` is routed to a bounded wrapper that keeps a `0x0fa0` ready-wait budget and returns `0xff` if either ready flag never appears. This exposes timeout to the existing stream recovery instead of continuing with a stale read.
- Command helper `0x08019608` keeps the same status polling path but reduces command `0x40` and `0x48` retry counts to `0x60` for lower worst-case status latency.
- Existing stream error cleanup now clears bits `0` and `1` from flag `0x2000022c`, releasing stale busy/status after timeout, spike, overload, or failed mode transition while leaving the other observed protection/status bits untouched.
- Mode/range function `0x0801f19a` now enters through a guarded wrapper that preserves its original prologue, clears stale bits `0` and `1` from flag `0x2000022c`, then continues the original relay/range switching code. This targets blank/freeze after DC/AC/DC switching without changing relay GPIO order.
- Stream function `0x080196b2` no longer returns early only because stale busy bit `1` in `0x2000022c` is set. It branches to the normal transaction body so AC->DC recovery can request a fresh sample instead of waiting for the stale gate to expire.
- Four meter/current transition guards in the same timing cluster are capped: two `0x3e80` compares are changed to `0x0640`, and two remaining state-2 `0x3a98` guards are changed to the vendor-adjacent `0x05dc` settle budget.
- Four elapsed-time skip branches immediately before mode/range calls are replaced with NOPs. Direction/state checks remain, but the mode/range call is no longer delayed once the switch condition is detected.
- Stream transfer helper bit0 error gates are kept unchanged.
- Version strings are marked `V4.0.1j` as a visible repair-d UI-safe latency flash marker.
- Boot-logo resource load timing is kept unchanged.
- Patched self-loop vector entries: `56`.
- Malay text/resource staging is disabled for this repair profile so official UI resources can be preserved.
- The existing language resources are not staged or replaced by this patcher profile.
- The Spanish language-name string is kept unchanged for this repair profile.
- True add-only language menu activation is not patched because the hardcoded language table has no confirmed spare slot.

## Hashes

- Source SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`
- Output SHA-256: `0d0899258a5167e34e56485aeb7a72d74211dd9c40ec2faa5e9412fe8107b41c`
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
| `0x02ca0` | 16 | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `4d 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6a 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x02cb0` | 16 | `42 54 31 30 30 4d 4d 20 56 34 2e 30 20 00 00 00` | `42 54 31 30 30 4d 4d 20 56 34 2e 30 2e 31 6a 00` | preserve model ID and mark candidate version as V4.0.1 beta |
| `0x09ca0` | 2 | `fe e7` | `ff e7` | convert runtime fail-stop loop after integrity check into fall-through return |
| `0x2c4ea` | 2 | `fe e7` | `70 47` | return from semihosting/debug fail-stop instead of looping forever |
| `0x09570` | 2 | `f5 d1` | `00 bf` | stream-recovery error-route: stop repeated 0xff stream-read retry after lower helper timeout; return failure to caller so UI/status refresh can resume |
| `0x09706` | 2 | `ec d1` | `4c d1` | stream-recovery error-route: route command-0x40 failure with busy flag set to existing error/clear path instead of treating it as normal fall-through |
| `0x09758` | 2 | `f5 d1` | `00 bf` | stream-recovery error-route: stop repeated command-0xe9 retry when the lower command helper cannot clear the acquisition/status path |
| `0x097be` | 2 | `f6 d1` | `00 bf` | stream-recovery error-route: stop repeated mode/status retry when the lower command helper cannot clear the acquisition/status path |
| `0x06a06` | 4 | `70 b5 05 46` | `00 f0 23 b8` | stream-recovery-exp11: branch low byte-IO helper to bounded failure-return wrapper |
| `0x06a50` | 80 | `00 b5 85 b0 23 48 23 f0 fd fe 01 21 88 03 23 f0 ac f8 00 20 ad f8 00 00 4f f4 82 70 ad f8 02 00 00 20 ad f8 04 00 02 20 ad f8 06 00 01 20 ad f8 08 00 40 02 ad f8 0a 00 08 20 ad f8 0c 00 00 20 ad f8 0e 00 07 20 ad f8 10 00 69 46 11 48 23 f0` | `70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 70 bd 00 bf 00 30 01 40` | stream-recovery-exp11: bounded low byte-IO wrapper returns 0xff on ready-timeout and preserves SPI1 read/write calls |
| `0x0967c` | 2 | `95 27` | `60 27` | stream-recovery balanced clamp: reduce command-0x40 bounded status retry count from 0x95 to 0x60 |
| `0x09682` | 2 | `87 27` | `60 27` | stream-recovery balanced clamp: reduce command-0x48 bounded status retry count from 0x87 to 0x60 |
| `0x097e6` | 4 | `20 f0 01 00` | `20 f0 03 00` | stream-recovery state-clear: on existing stream error cleanup, clear flag bits 0 and 1 from 0x2000022c instead of only bit 0 so stale busy/status cannot persist after timeout/spike |
| `0x0f19a` | 4 | `10 b5 04 46` | `1e f0 34 ba` | stream-recovery-exp13: route mode/range entry through stale stream-state clear wrapper before relay switching |
| `0x2d606` | 30 | `00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | stream-recovery-exp13: preserve original mode/range prologue, clear bits 0 and 1 of 0x2000022c, then continue original function |
| `0x096be` | 2 | `10 b1` | `02 e0` | stream-recovery-exp14: force fresh stream transaction instead of returning early on stale busy bit 1 at 0x2000022c |
| `0x1585e` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-b: cap first long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15888` | 4 | `b0 f5 7a 5f` | `b0 f5 c8 6f` | v401h-repair-b: cap second long current/meter switch compare from 0x3e80 to 0x0640 |
| `0x15934` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-b: lower remaining state-2 current/meter switch guard from 0x3a98 to vendor-adjacent 0x05dc |
| `0x1595c` | 4 | `43 f6 98 21` | `40 f2 dc 51` | v401h-repair-b: lower second remaining state-2 current/meter switch guard from 0x3a98 to vendor-adjacent 0x05dc |
| `0x15812` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay first immediate mode/range call after switch condition |
| `0x15838` | 2 | `34 d9` | `00 bf` | stream-recovery-exp15: do not delay second immediate mode/range call after switch condition |
| `0x15862` | 2 | `06 d9` | `00 bf` | stream-recovery-exp15: do not delay first return-to-mode call after AC/DC switch condition |
| `0x1588c` | 2 | `05 d9` | `00 bf` | stream-recovery-exp15: do not delay second return-to-mode call after AC/DC switch condition |
