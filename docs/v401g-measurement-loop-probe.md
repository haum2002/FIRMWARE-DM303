# DM303 measurement loop probe

Read-only static probe for wait/retry loops related to blank/freeze,
latency, and measurement stream recovery. This report does not prove
analog accuracy; it identifies firmware paths that are safe or unsafe
to consider for further patching.

## v3.16

- Path: `backup\DM303 V3.16-read only\DM303V316.bin`
- Size: `223276` bytes
- SHA-256: `0c8da8396bfdb96a9daf186dd9e458ab4e9b6840046eea178fecdf0f2107770e`

### Backward branches in watched ranges

| Address | Instruction | Target | Distance | Context |
|---:|---|---:|---:|---|
| `0x080169de` | `blt #0x80169ca` | `0x080169ca` | `20` | low byte-IO / hardware-ready waits |
| `0x08016a00` | `blt #0x80169ec` | `0x080169ec` | `20` | low byte-IO / hardware-ready waits |
| `0x08016a7a` | `beq #0x8016a70` | `0x08016a70` | `10` | low byte-IO / hardware-ready waits |
| `0x08016a90` | `beq #0x8016a86` | `0x08016a86` | `10` | low byte-IO / hardware-ready waits |
| `0x08018e84` | `bne #0x8018e72` | `0x08018e72` | `18` | measurement stream/status transaction helpers |
| `0x08018ea0` | `bne #0x8018e90` | `0x08018e90` | `16` | measurement stream/status transaction helpers |
| `0x08018eb0` | `b #0x8018e8c` | `0x08018e8c` | `36` | measurement stream/status transaction helpers |
| `0x08018ed6` | `blo #0x8018eca` | `0x08018eca` | `12` | measurement stream/status transaction helpers |
| `0x08018efa` | `blo #0x8018ef2` | `0x08018ef2` | `8` | measurement stream/status transaction helpers |
| `0x08018f0a` | `blo #0x8018eec` | `0x08018eec` | `30` | measurement stream/status transaction helpers |
| `0x08018f1a` | `b #0x8018f14` | `0x08018f14` | `6` | measurement stream/status transaction helpers |
| `0x08018f60` | `b #0x8018f3e` | `0x08018f3e` | `34` | measurement stream/status transaction helpers |
| `0x08018fc0` | `bne #0x8018fac` | `0x08018fac` | `20` | measurement stream/status transaction helpers |
| `0x08018fc4` | `b #0x8018f3e` | `0x08018f3e` | `134` | measurement stream/status transaction helpers |
| `0x08019006` | `bne #0x8018ffa` | `0x08018ffa` | `12` | measurement stream/status transaction helpers |
| `0x0801901a` | `bne #0x8018ff6` | `0x08018ff6` | `36` | measurement stream/status transaction helpers |
| `0x08019046` | `blt #0x8019036` | `0x08019036` | `16` | measurement stream/status transaction helpers |
| `0x0801906c` | `bne #0x801905a` | `0x0801905a` | `18` | measurement stream/status transaction helpers |
| `0x08019094` | `blt #0x8019084` | `0x08019084` | `16` | measurement stream/status transaction helpers |
| `0x080190d2` | `bne #0x80190c2` | `0x080190c2` | `16` | measurement stream/status transaction helpers |
| `0x08019106` | `b #0x8018fd8` | `0x08018fd8` | `302` | measurement stream/status transaction helpers |
| `0x08019130` | `b #0x8019120` | `0x08019120` | `16` | measurement stream/status transaction helpers |
| `0x08019192` | `bne #0x8019166` | `0x08019166` | `44` | measurement stream/status transaction helpers |
| `0x080191a6` | `b #0x8019120` | `0x08019120` | `134` | measurement stream/status transaction helpers |
| `0x080191aa` | `b #0x8019120` | `0x08019120` | `138` | measurement stream/status transaction helpers |
| `0x080191cc` | `b #0x80191bc` | `0x080191bc` | `16` | measurement stream/status transaction helpers |
| `0x080191da` | `b #0x80191bc` | `0x080191bc` | `30` | measurement stream/status transaction helpers |
| `0x0801922c` | `bne #0x8019216` | `0x08019216` | `22` | measurement stream/status transaction helpers |
| `0x08019244` | `b #0x80191bc` | `0x080191bc` | `136` | measurement stream/status transaction helpers |
| `0x08019248` | `b #0x80191bc` | `0x080191bc` | `140` | measurement stream/status transaction helpers |
| `0x08019280` | `b.w #0x7f0f7ec` | `0x07f0f7ec` | `1088148` | measurement stream/status transaction helpers |
| `0x08019284` | `bmi #0x8019216` | `0x08019216` | `110` | measurement stream/status transaction helpers |
| `0x08019364` | `bne #0x8019358` | `0x08019358` | `12` | measurement stream/status transaction helpers |
| `0x0801943e` | `bne #0x801942e` | `0x0801942e` | `16` | measurement stream/status transaction helpers |

### Large constants in watched ranges

| Address | Instruction | Immediate | Context |
|---:|---|---:|---|
| `0x0801697c` | `mov.w r0, #0x104` | `0x104` | low byte-IO / hardware-ready waits |
| `0x080169d8` | `movw r0, #0x2710` | `0x2710` | low byte-IO / hardware-ready waits |
| `0x080169fa` | `movw r0, #0x2710` | `0x2710` | low byte-IO / hardware-ready waits |
| `0x08016a24` | `mov.w r0, #0x104` | `0x104` | low byte-IO / hardware-ready waits |
| `0x08018da4` | `mov.w r0, #0x104` | `0x104` | measurement stream/status transaction helpers |
| `0x08018e02` | `mov.w r0, #0x104` | `0x104` | measurement stream/status transaction helpers |
| `0x08018e48` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018e4e` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08018e58` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018e72` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018e90` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018ea2` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018ea8` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018ed8` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018ede` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018ee4` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018ef4` | `movw r0, #0xfff0` | `0xfff0` | measurement stream/status transaction helpers |
| `0x08018efc` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018f42` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08018f4c` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08018f5e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018f62` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018f90` | `movs r7, #0x95` | `0x95` | measurement stream/status transaction helpers |
| `0x08018f96` | `movs r7, #0x87` | `0x87` | measurement stream/status transaction helpers |
| `0x08018fa2` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018fac` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08018fe2` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08018fec` | `mov.w r0, #0x1f4` | `0x1f4` | measurement stream/status transaction helpers |
| `0x08018ffa` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801901e` | `movs r0, #0xc8` | `0xc8` | measurement stream/status transaction helpers |
| `0x08019024` | `mov.w r1, #0x1aa` | `0x1aa` | measurement stream/status transaction helpers |
| `0x08019036` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019060` | `mov.w r1, #0x40000000` | `0x40000000` | measurement stream/status transaction helpers |
| `0x08019064` | `movs r0, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x08019084` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080190ac` | `movs r0, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x080190b8` | `movs r5, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x080190da` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019166` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x080191ea` | `movs r1, #0xfe` | `0xfe` | measurement stream/status transaction helpers |
| `0x08019204` | `movs r0, #0xd7` | `0xd7` | measurement stream/status transaction helpers |
| `0x08019216` | `movs r1, #0xfc` | `0xfc` | measurement stream/status transaction helpers |
| `0x08019230` | `movs r1, #0xfd` | `0xfd` | measurement stream/status transaction helpers |
| `0x08019288` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019320` | `mov.w r0, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019338` | `movs r0, #0xcd` | `0xcd` | measurement stream/status transaction helpers |
| `0x08019342` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019358` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801942e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801e220` | `mov.w r1, #0x800` | `0x800` | relay/range and mode-switch helper |
| `0x0801e22c` | `mov.w r1, #0x800` | `0x800` | relay/range and mode-switch helper |
| `0x0801e276` | `mov.w r1, #0x400` | `0x400` | relay/range and mode-switch helper |
| `0x0801e28e` | `mov.w r1, #0x400` | `0x400` | relay/range and mode-switch helper |
| `0x0801e45e` | `mov.w r1, #0x400` | `0x400` | relay/range and mode-switch helper |
| `0x0801e476` | `mov.w r1, #0x400` | `0x400` | relay/range and mode-switch helper |
| `0x0801e498` | `mov.w r1, #0x100` | `0x100` | relay/range and mode-switch helper |
| `0x0801e4a2` | `movw sb, #0x4ab` | `0x4ab` | relay/range and mode-switch helper |
| `0x0801e4a6` | `movw sl, #0x1771` | `0x1771` | relay/range and mode-switch helper |

### Calls into watched helper targets

| Caller | Target | Context |
|---:|---:|---|
| `0x08018d86` | `0x080169c2` | measurement stream/status transaction helpers |
| `0x08018e5a` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018e74` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018e92` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018ea4` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018eaa` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018ebe` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018ecc` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018eda` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018ee0` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018ee6` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018efe` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f32` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08018f64` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f6a` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f70` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f78` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f80` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f86` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018f9a` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018fa4` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018fae` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08018ffc` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x0801900c` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x0801902a` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019038` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x08019066` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x0801907a` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019086` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x080190ae` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x080190cc` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x080190e0` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019146` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019150` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x0801915e` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x0801916c` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x0801919a` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x080191e4` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x080191ee` | `0x08018eb2` | measurement stream/status transaction helpers |
| `0x08019206` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x0801920e` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x0801921a` | `0x08018eb2` | measurement stream/status transaction helpers |
| `0x08019234` | `0x08018eb2` | measurement stream/status transaction helpers |
| `0x080192a4` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x080192ae` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x0801933a` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019344` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x0801934c` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x0801935a` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x0801937a` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019384` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x080193f0` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x080193fa` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x0801940a` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019414` | `0x08018e64` | measurement stream/status transaction helpers |
| `0x08019424` | `0x08018f1c` | measurement stream/status transaction helpers |
| `0x08019430` | `0x08018d80` | measurement stream/status transaction helpers |
| `0x0801e2b4` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e2bc` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e2c4` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e2d2` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e2da` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e2e2` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e34c` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e354` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e35c` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e36a` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e372` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e37a` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e386` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e38e` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e396` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3a6` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3ae` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3b6` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3c4` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3cc` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3d4` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3e2` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3ea` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e3f2` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e40e` | `0x0801e254` | relay/range and mode-switch helper |
| `0x0801e41a` | `0x0801e254` | relay/range and mode-switch helper |
| `0x0801e428` | `0x0801e1ac` | relay/range and mode-switch helper |
| `0x0801e436` | `0x0801e1ac` | relay/range and mode-switch helper |

## v4.0

- Path: `backup\DM303 V4.0-read only\DM303V4.004.bin`
- Size: `203260` bytes
- SHA-256: `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158`

### Backward branches in watched ranges

| Address | Instruction | Target | Distance | Context |
|---:|---|---:|---:|---|
| `0x08016a22` | `blt #0x8016a0e` | `0x08016a0e` | `20` | low byte-IO / hardware-ready waits |
| `0x08016a44` | `blt #0x8016a30` | `0x08016a30` | `20` | low byte-IO / hardware-ready waits |
| `0x08016abe` | `beq #0x8016ab4` | `0x08016ab4` | `10` | low byte-IO / hardware-ready waits |
| `0x08016ad4` | `beq #0x8016aca` | `0x08016aca` | `10` | low byte-IO / hardware-ready waits |
| `0x08019570` | `bne #0x801955e` | `0x0801955e` | `18` | measurement stream/status transaction helpers |
| `0x0801958c` | `bne #0x801957c` | `0x0801957c` | `16` | measurement stream/status transaction helpers |
| `0x0801959c` | `b #0x8019578` | `0x08019578` | `36` | measurement stream/status transaction helpers |
| `0x080195c2` | `blo #0x80195b6` | `0x080195b6` | `12` | measurement stream/status transaction helpers |
| `0x080195e6` | `blo #0x80195de` | `0x080195de` | `8` | measurement stream/status transaction helpers |
| `0x080195f6` | `blo #0x80195d8` | `0x080195d8` | `30` | measurement stream/status transaction helpers |
| `0x08019606` | `b #0x8019600` | `0x08019600` | `6` | measurement stream/status transaction helpers |
| `0x0801964c` | `b #0x801962a` | `0x0801962a` | `34` | measurement stream/status transaction helpers |
| `0x080196ac` | `bne #0x8019698` | `0x08019698` | `20` | measurement stream/status transaction helpers |
| `0x080196b0` | `b #0x801962a` | `0x0801962a` | `134` | measurement stream/status transaction helpers |
| `0x080196f2` | `bne #0x80196e6` | `0x080196e6` | `12` | measurement stream/status transaction helpers |
| `0x08019706` | `bne #0x80196e2` | `0x080196e2` | `36` | measurement stream/status transaction helpers |
| `0x08019732` | `blt #0x8019722` | `0x08019722` | `16` | measurement stream/status transaction helpers |
| `0x08019758` | `bne #0x8019746` | `0x08019746` | `18` | measurement stream/status transaction helpers |
| `0x08019780` | `blt #0x8019770` | `0x08019770` | `16` | measurement stream/status transaction helpers |
| `0x080197be` | `bne #0x80197ae` | `0x080197ae` | `16` | measurement stream/status transaction helpers |
| `0x080197f2` | `b #0x80196c4` | `0x080196c4` | `302` | measurement stream/status transaction helpers |
| `0x0801981c` | `b #0x801980c` | `0x0801980c` | `16` | measurement stream/status transaction helpers |
| `0x0801987e` | `bne #0x8019852` | `0x08019852` | `44` | measurement stream/status transaction helpers |
| `0x08019892` | `b #0x801980c` | `0x0801980c` | `134` | measurement stream/status transaction helpers |
| `0x08019896` | `b #0x801980c` | `0x0801980c` | `138` | measurement stream/status transaction helpers |
| `0x080198b8` | `b #0x80198a8` | `0x080198a8` | `16` | measurement stream/status transaction helpers |
| `0x080198c6` | `b #0x80198a8` | `0x080198a8` | `30` | measurement stream/status transaction helpers |
| `0x08019918` | `bne #0x8019902` | `0x08019902` | `22` | measurement stream/status transaction helpers |
| `0x08019930` | `b #0x80198a8` | `0x080198a8` | `136` | measurement stream/status transaction helpers |
| `0x08019934` | `b #0x80198a8` | `0x080198a8` | `140` | measurement stream/status transaction helpers |
| `0x0801996c` | `b.w #0x7f0fed8` | `0x07f0fed8` | `1088148` | measurement stream/status transaction helpers |
| `0x08019970` | `bmi #0x8019902` | `0x08019902` | `110` | measurement stream/status transaction helpers |
| `0x08019a50` | `bne #0x8019a44` | `0x08019a44` | `12` | measurement stream/status transaction helpers |
| `0x08019b2a` | `bne #0x8019b1a` | `0x08019b1a` | `16` | measurement stream/status transaction helpers |

### Large constants in watched ranges

| Address | Instruction | Immediate | Context |
|---:|---|---:|---|
| `0x080169c0` | `mov.w r0, #0x104` | `0x104` | low byte-IO / hardware-ready waits |
| `0x08016a1c` | `movw r0, #0x2710` | `0x2710` | low byte-IO / hardware-ready waits |
| `0x08016a3e` | `movw r0, #0x2710` | `0x2710` | low byte-IO / hardware-ready waits |
| `0x08016a68` | `mov.w r0, #0x104` | `0x104` | low byte-IO / hardware-ready waits |
| `0x08016aea` | `mov.w r0, #0x10000` | `0x10000` | low byte-IO / hardware-ready waits |
| `0x08019490` | `mov.w r0, #0x104` | `0x104` | measurement stream/status transaction helpers |
| `0x080194ee` | `mov.w r0, #0x104` | `0x104` | measurement stream/status transaction helpers |
| `0x08019534` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801953a` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019544` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801955e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801957c` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801958e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019594` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195c4` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195ca` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195d0` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195e0` | `movw r0, #0xfff0` | `0xfff0` | measurement stream/status transaction helpers |
| `0x080195e8` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801962e` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019638` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x0801964a` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801964e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801967c` | `movs r7, #0x95` | `0x95` | measurement stream/status transaction helpers |
| `0x08019682` | `movs r7, #0x87` | `0x87` | measurement stream/status transaction helpers |
| `0x0801968e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019698` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080196ce` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x080196d8` | `mov.w r0, #0x1f4` | `0x1f4` | measurement stream/status transaction helpers |
| `0x080196e6` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801970a` | `movs r0, #0xc8` | `0xc8` | measurement stream/status transaction helpers |
| `0x08019710` | `mov.w r1, #0x1aa` | `0x1aa` | measurement stream/status transaction helpers |
| `0x08019722` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801974c` | `mov.w r1, #0x40000000` | `0x40000000` | measurement stream/status transaction helpers |
| `0x08019750` | `movs r0, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x08019770` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019798` | `movs r0, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x080197a4` | `movs r5, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x080197c6` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019852` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x080198d6` | `movs r1, #0xfe` | `0xfe` | measurement stream/status transaction helpers |
| `0x080198f0` | `movs r0, #0xd7` | `0xd7` | measurement stream/status transaction helpers |
| `0x08019902` | `movs r1, #0xfc` | `0xfc` | measurement stream/status transaction helpers |
| `0x0801991c` | `movs r1, #0xfd` | `0xfd` | measurement stream/status transaction helpers |
| `0x08019974` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019a0c` | `mov.w r0, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019a24` | `movs r0, #0xcd` | `0xcd` | measurement stream/status transaction helpers |
| `0x08019a2e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019a44` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019b1a` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019b32` | `movs r0, #0xcd` | `0xcd` | measurement stream/status transaction helpers |
| `0x08019b3a` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |

### Calls into watched helper targets

| Caller | Target | Context |
|---:|---:|---|
| `0x08019472` | `0x08016a06` | measurement stream/status transaction helpers |
| `0x08019546` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019560` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801957e` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019590` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019596` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195aa` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195b8` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195c6` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195cc` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195d2` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195ea` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801961e` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019650` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019656` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801965c` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019664` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801966c` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019672` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019686` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019690` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801969a` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080196e8` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080196f8` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019716` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019724` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019752` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019766` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019772` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801979a` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080197b8` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080197cc` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019832` | `0x08019608` | measurement stream/status transaction helpers |
| `0x0801983c` | `0x08019550` | measurement stream/status transaction helpers |
| `0x0801984a` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019858` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019886` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080198d0` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080198da` | `0x0801959e` | measurement stream/status transaction helpers |
| `0x080198f2` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080198fa` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019906` | `0x0801959e` | measurement stream/status transaction helpers |
| `0x08019920` | `0x0801959e` | measurement stream/status transaction helpers |
| `0x08019990` | `0x08019608` | measurement stream/status transaction helpers |
| `0x0801999a` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019a26` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019a30` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019a38` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019a46` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019a66` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019a70` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019adc` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019ae6` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019af6` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019b00` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019b10` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019b1c` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019b34` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019b3c` | `0x0801946c` | measurement stream/status transaction helpers |

## v4.0.1b

- Path: `dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin`
- Size: `203260` bytes
- SHA-256: `24c3bd15282b3e43e42c0e45a7743261469283e61d345bf46a8483eb9350342d`

### Backward branches in watched ranges

| Address | Instruction | Target | Distance | Context |
|---:|---|---:|---:|---|
| `0x08016a22` | `blt #0x8016a0e` | `0x08016a0e` | `20` | low byte-IO / hardware-ready waits |
| `0x08016a44` | `blt #0x8016a30` | `0x08016a30` | `20` | low byte-IO / hardware-ready waits |
| `0x08016a6a` | `blo #0x8016a5a` | `0x08016a5a` | `16` | low byte-IO / hardware-ready waits |
| `0x08016a88` | `blo #0x8016a78` | `0x08016a78` | `16` | low byte-IO / hardware-ready waits |
| `0x08016abe` | `beq #0x8016ab4` | `0x08016ab4` | `10` | low byte-IO / hardware-ready waits |
| `0x08016ad4` | `beq #0x8016aca` | `0x08016aca` | `10` | low byte-IO / hardware-ready waits |
| `0x0801958c` | `bne #0x801957c` | `0x0801957c` | `16` | measurement stream/status transaction helpers |
| `0x0801959c` | `b #0x8019578` | `0x08019578` | `36` | measurement stream/status transaction helpers |
| `0x080195c2` | `blo #0x80195b6` | `0x080195b6` | `12` | measurement stream/status transaction helpers |
| `0x080195e6` | `blo #0x80195de` | `0x080195de` | `8` | measurement stream/status transaction helpers |
| `0x080195f6` | `blo #0x80195d8` | `0x080195d8` | `30` | measurement stream/status transaction helpers |
| `0x08019606` | `b #0x8019600` | `0x08019600` | `6` | measurement stream/status transaction helpers |
| `0x0801964c` | `b #0x801962a` | `0x0801962a` | `34` | measurement stream/status transaction helpers |
| `0x080196ac` | `bne #0x8019698` | `0x08019698` | `20` | measurement stream/status transaction helpers |
| `0x080196b0` | `b #0x801962a` | `0x0801962a` | `134` | measurement stream/status transaction helpers |
| `0x080196f2` | `bne #0x80196e6` | `0x080196e6` | `12` | measurement stream/status transaction helpers |
| `0x08019732` | `blt #0x8019722` | `0x08019722` | `16` | measurement stream/status transaction helpers |
| `0x08019780` | `blt #0x8019770` | `0x08019770` | `16` | measurement stream/status transaction helpers |
| `0x080197f2` | `b #0x80196c4` | `0x080196c4` | `302` | measurement stream/status transaction helpers |
| `0x0801981c` | `b #0x801980c` | `0x0801980c` | `16` | measurement stream/status transaction helpers |
| `0x0801987e` | `bne #0x8019852` | `0x08019852` | `44` | measurement stream/status transaction helpers |
| `0x08019892` | `b #0x801980c` | `0x0801980c` | `134` | measurement stream/status transaction helpers |
| `0x08019896` | `b #0x801980c` | `0x0801980c` | `138` | measurement stream/status transaction helpers |
| `0x080198b8` | `b #0x80198a8` | `0x080198a8` | `16` | measurement stream/status transaction helpers |
| `0x080198c6` | `b #0x80198a8` | `0x080198a8` | `30` | measurement stream/status transaction helpers |
| `0x08019918` | `bne #0x8019902` | `0x08019902` | `22` | measurement stream/status transaction helpers |
| `0x08019930` | `b #0x80198a8` | `0x080198a8` | `136` | measurement stream/status transaction helpers |
| `0x08019934` | `b #0x80198a8` | `0x080198a8` | `140` | measurement stream/status transaction helpers |
| `0x0801996c` | `b.w #0x7f0fed8` | `0x07f0fed8` | `1088148` | measurement stream/status transaction helpers |
| `0x08019970` | `bmi #0x8019902` | `0x08019902` | `110` | measurement stream/status transaction helpers |
| `0x08019a50` | `bne #0x8019a44` | `0x08019a44` | `12` | measurement stream/status transaction helpers |
| `0x08019b2a` | `bne #0x8019b1a` | `0x08019b1a` | `16` | measurement stream/status transaction helpers |

### Large constants in watched ranges

| Address | Instruction | Immediate | Context |
|---:|---|---:|---|
| `0x080169c0` | `mov.w r0, #0x104` | `0x104` | low byte-IO / hardware-ready waits |
| `0x08016a1c` | `movw r0, #0x2710` | `0x2710` | low byte-IO / hardware-ready waits |
| `0x08016a3e` | `movw r0, #0x2710` | `0x2710` | low byte-IO / hardware-ready waits |
| `0x08016a54` | `movw r6, #0xfa0` | `0xfa0` | low byte-IO / hardware-ready waits |
| `0x08016a96` | `movs r0, #0xff` | `0xff` | low byte-IO / hardware-ready waits |
| `0x08016aea` | `mov.w r0, #0x10000` | `0x10000` | low byte-IO / hardware-ready waits |
| `0x08019490` | `mov.w r0, #0x104` | `0x104` | measurement stream/status transaction helpers |
| `0x080194ee` | `mov.w r0, #0x104` | `0x104` | measurement stream/status transaction helpers |
| `0x08019534` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801953a` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019544` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801955e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801957c` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801958e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019594` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195c4` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195ca` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195d0` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080195e0` | `movw r0, #0xfff0` | `0xfff0` | measurement stream/status transaction helpers |
| `0x080195e8` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801962e` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019638` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x0801964a` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801964e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801968e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019698` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x080196ce` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x080196d8` | `mov.w r0, #0x1f4` | `0x1f4` | measurement stream/status transaction helpers |
| `0x080196e6` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801970a` | `movs r0, #0xc8` | `0xc8` | measurement stream/status transaction helpers |
| `0x08019710` | `mov.w r1, #0x1aa` | `0x1aa` | measurement stream/status transaction helpers |
| `0x08019722` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x0801974c` | `mov.w r1, #0x40000000` | `0x40000000` | measurement stream/status transaction helpers |
| `0x08019750` | `movs r0, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x08019770` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019798` | `movs r0, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x080197a4` | `movs r5, #0xe9` | `0xe9` | measurement stream/status transaction helpers |
| `0x080197c6` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019852` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x080198d6` | `movs r1, #0xfe` | `0xfe` | measurement stream/status transaction helpers |
| `0x080198f0` | `movs r0, #0xd7` | `0xd7` | measurement stream/status transaction helpers |
| `0x08019902` | `movs r1, #0xfc` | `0xfc` | measurement stream/status transaction helpers |
| `0x0801991c` | `movs r1, #0xfd` | `0xfd` | measurement stream/status transaction helpers |
| `0x08019974` | `mov.w r1, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019a0c` | `mov.w r0, #0x200` | `0x200` | measurement stream/status transaction helpers |
| `0x08019a24` | `movs r0, #0xcd` | `0xcd` | measurement stream/status transaction helpers |
| `0x08019a2e` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019a44` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019b1a` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |
| `0x08019b32` | `movs r0, #0xcd` | `0xcd` | measurement stream/status transaction helpers |
| `0x08019b3a` | `movs r0, #0xff` | `0xff` | measurement stream/status transaction helpers |

### Calls into watched helper targets

| Caller | Target | Context |
|---:|---:|---|
| `0x08019472` | `0x08016a06` | measurement stream/status transaction helpers |
| `0x08019546` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019560` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801957e` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019590` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019596` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195aa` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195b8` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195c6` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195cc` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195d2` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080195ea` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801961e` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019650` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019656` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801965c` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019664` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801966c` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019672` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019686` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019690` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801969a` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080196e8` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x080196f8` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019716` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019724` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019752` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019766` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019772` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x0801979a` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080197b8` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080197cc` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019832` | `0x08019608` | measurement stream/status transaction helpers |
| `0x0801983c` | `0x08019550` | measurement stream/status transaction helpers |
| `0x0801984a` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019858` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019886` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080198d0` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080198da` | `0x0801959e` | measurement stream/status transaction helpers |
| `0x080198f2` | `0x08019608` | measurement stream/status transaction helpers |
| `0x080198fa` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019906` | `0x0801959e` | measurement stream/status transaction helpers |
| `0x08019920` | `0x0801959e` | measurement stream/status transaction helpers |
| `0x08019990` | `0x08019608` | measurement stream/status transaction helpers |
| `0x0801999a` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019a26` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019a30` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019a38` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019a46` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019a66` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019a70` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019adc` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019ae6` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019af6` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019b00` | `0x08019550` | measurement stream/status transaction helpers |
| `0x08019b10` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019b1c` | `0x0801946c` | measurement stream/status transaction helpers |
| `0x08019b34` | `0x08019608` | measurement stream/status transaction helpers |
| `0x08019b3c` | `0x0801946c` | measurement stream/status transaction helpers |

### exp13 patch byte check

| Offset | Expected | Actual | Match |
|---:|---|---|---|
| `0x09570` | `00 bf` | `00 bf` | `True` |
| `0x09706` | `4c d1` | `4c d1` | `True` |
| `0x09758` | `00 bf` | `00 bf` | `True` |
| `0x097be` | `00 bf` | `00 bf` | `True` |
| `0x06a06` | `00 f0 23 b8` | `00 f0 23 b8` | `True` |
| `0x06a50` | `70 b5 05 46 40 f6 a0 76` | `70 b5 05 46 40 f6 a0 76` | `True` |
| `0x0967c` | `60 27` | `60 27` | `True` |
| `0x09682` | `60 27` | `60 27` | `True` |
| `0x097e6` | `20 f0 03 00` | `20 f0 03 00` | `True` |
| `0x0f19a` | `1e f0 34 ba` | `1e f0 34 ba` | `True` |
| `0x2d606` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `True` |

## Interpretation

- The V3.16 and V4.0 stream transaction block still contains the same
  large `0xfff0` inner delay and `0x200` retry limits. Because V3.16
  can switch DC/AC more smoothly in the user's physical test, that
  block is not the best first root-cause target for V4.0.1b.
- The exp13 changes target the paths that can keep UI/status refresh
  waiting after lower byte-IO timeout, while preserving official
  relay/range timing and the original mode-switch helper. Command
  `0x40` busy failure is routed to the existing error/clear path,
  and low byte-IO now returns `0xff` if a ready flag never appears
  within the bounded wrapper budget instead of continuing with a
  stale read. Exp13 keeps the stream error cleanup from exp12 and
  additionally routes the mode/range entry through a wrapper that
  clears stale stream flag bits `0` and `1` before relay/range logic
  continues.
- Further accuracy/EMI/True RMS work still needs a confirmed
  measurement-engine state hook before writing a safe patch.
