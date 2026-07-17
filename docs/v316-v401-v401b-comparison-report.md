# DM303 V3.16 / V4.0 / V4.0.1b comparison

Read-only comparison; no firmware image is modified.

## Image identity

| Image | Path | Size | SHA-256 | Reset vector | Reset offset |
|---|---|---:|---|---:|---:|
| v3.16 | `backup/DM303 V3.16-read only/DM303V316.bin` | 223276 | `0c8da8396bfdb96a9daf186dd9e458ab4e9b6840046eea178fecdf0f2107770e` | `0x08016e21` | `0x06e20` |
| v4.0 | `backup/DM303 V4.0-read only/DM303V4.004.bin` | 203260 | `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158` | `0x0801754d` | `0x0754c` |
| v4.0.1b | `dm303_firmware/DM303-V4.0.1-beta/DM303V4.0.1-beta.bin` | 203260 | `57204ff3219fe2bbb06df116ce6ffd87593605c66b1e0fd40b803f61d08dcab9` | `0x0801754d` | `0x0754c` |

## Version-like strings

### v3.16
- `0x02ca3`: ` MT100MM V3.0 `
- `0x02cb4`: `MT100MM V2.0 `
- `0x02cc4`: `MT100MM V1.0 `
- `0x02cd4`: `BT100MM V3.16 `
- `0x02ce4`: `BT100MM V2.16 `
- `0x02cf4`: `BT100MM V1.26 `
- `0x04224`: `Loading DM30XDB1 ...`
- `0x0423c`: `\system\DM30XDB1.dat`
### v4.0
- `0x02ca0`: `MT100MM V4.0 `
- `0x02cb0`: `BT100MM V4.0 `
- `0x04260`: `Loading DM30XDB1 ...`
- `0x04278`: `\system\DM30XDB1.dat`
### v4.0.1b
- `0x02ca0`: `MT100MM V4.0.1b`
- `0x02cb0`: `BT100MM V4.0.1b`
- `0x04260`: `Loading DM30XDB1 ...`
- `0x04278`: `\system\DM30XDB1.dat`

## Known relay/range selector timing evidence

| Image | Selector addr | Helper addr | Mode routine addr | Helper status | Pre-switch | Bit-settle | Post-switch |
|---|---:|---:|---:|---|---:|---:|---:|
| v3.16 | `0x0801e1ac` | `0x0801e254` | `0x0801e29a` | v3-original | 2 | 3 | 10 |
| v4.0 | `0x0801f0f2` | `0x0801f0ac` | `0x0801f19a` | v4-original | 2 | 3 | 10 |
| v4.0.1b | `0x0801f0f2` | `0x0801f0ac` | `0x0801f19a` | v4-original | 2 | 3 | 10 |

## Interpretation guardrails

- V3.16 and official V4.0 use the same observed selector waits: `2/3/10` ticks.
- If V3.16 switches DC/AC smoothly, the improvement is probably not from longer relay waits.
- Current V4.0.1b should be `stream-recovery-exp14` with original helper behavior, official/V3.16 `2/3/10` timing, fail-fast recovery for high-level stream/status retries, command-0x40 busy failure routed to the existing error/clear path, low byte-IO routed through a bounded `0x0fa0` failure-return wrapper, command 0x40/0x48 retry clamp `0x60`, stream error cleanup that clears stale flag bits `0` and `1`, a guarded mode/range entry wrapper that clears the same stale bits before relay/range switching, stale-busy stream early-return bypass, and two current-switch long-gate caps.
- Old long-delay or wrapper profiles are diagnostic comparisons, not proven analog math or True RMS fixes.
- Do not blindly port V3.16 behavior: the user observed weaker battery, ohmmeter, and continuity stability there.
