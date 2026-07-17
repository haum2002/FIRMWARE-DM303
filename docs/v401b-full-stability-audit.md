# DM303 V4.0.1b full stability audit

Read-only audit generated from local firmware files. This report proves
what the current V4.0.1b image actually changes and what is still only
a hypothesis. It does not claim physical accuracy/noise is fixed without
bench data from the real device.

## Image identity

| Image | Path | Size | SHA-256 |
|---|---|---:|---|
| v3.16 | `backup\DM303 V3.16-read only\DM303V316.bin` | 223276 | `0c8da8396bfdb96a9daf186dd9e458ab4e9b6840046eea178fecdf0f2107770e` |
| v4.0 | `backup\DM303 V4.0-read only\DM303V4.004.bin` | 203260 | `64faaffb5fb65bdd0057d4fce1d9a2ac93e9229f118fba0a84d758c0ff926158` |
| v4.0.1b-exp13 | `dm303_firmware\DM303-V4.0.1-beta\DM303V4.0.1-beta.bin` | 203260 | `fbe05118e33743fb56679d5edd1eb2019c1d82e39f499c1459fe89401ce8130b` |

## Verified binary changes from official V4.0

- Differing byte count: `226`.
- This proves the final V4.0.1b image is not just renamed.

| Offset | Size | V4.0 bytes | V4.0.1b bytes |
|---:|---:|---|---|
| `0x0000c` | 1 | `57` | `55` |
| `0x00010` | 1 | `59` | `55` |
| `0x00014` | 1 | `5b` | `55` |
| `0x00018` | 1 | `5d` | `55` |
| `0x0002c` | 1 | `5f` | `55` |
| `0x00030` | 1 | `61` | `55` |
| `0x00038` | 1 | `63` | `55` |
| `0x00040` | 1 | `67` | `55` |
| `0x00048` | 1 | `67` | `55` |
| `0x0004c` | 1 | `67` | `55` |
| `0x00050` | 1 | `67` | `55` |
| `0x00054` | 1 | `67` | `55` |
| `0x0005c` | 1 | `67` | `55` |
| `0x00060` | 1 | `67` | `55` |
| `0x00064` | 1 | `67` | `55` |
| `0x00068` | 1 | `67` | `55` |
| `0x00074` | 1 | `67` | `55` |
| `0x00078` | 1 | `67` | `55` |
| `0x0007c` | 1 | `67` | `55` |
| `0x00080` | 1 | `67` | `55` |
| `0x00084` | 1 | `67` | `55` |
| `0x0008c` | 1 | `67` | `55` |
| `0x000a0` | 1 | `67` | `55` |
| `0x000a8` | 1 | `67` | `55` |
| `0x000ac` | 1 | `67` | `55` |
| `0x000bc` | 1 | `67` | `55` |
| `0x000c0` | 1 | `67` | `55` |
| `0x000c4` | 1 | `67` | `55` |
| `0x000c8` | 1 | `67` | `55` |
| `0x000cc` | 1 | `67` | `55` |
| `0x000d0` | 1 | `67` | `55` |
| `0x000d8` | 1 | `67` | `55` |
| `0x000e0` | 1 | `67` | `55` |
| `0x000e4` | 1 | `67` | `55` |
| `0x000ec` | 1 | `67` | `55` |
| `0x000f0` | 1 | `67` | `55` |
| ... | ... | additional changed ranges omitted | additional changed ranges omitted |

## exp13 patch byte proof

| Offset | Address | Purpose | Expected | Actual | Match |
|---:|---:|---|---|---|---|
| `0x06a06` | `0x08016a06` | low byte-IO entry redirected to exp11/exp13 bounded wrapper | `00 f0 23 b8` | `00 f0 23 b8` | True |
| `0x06a50` | `0x08016a50` | bounded wrapper prefix, waits up to 0x0fa0 and returns 0xff on timeout | `70 b5 05 46 40 f6 a0 76` | `70 b5 05 46 40 f6 a0 76` | True |
| `0x09570` | `0x08019570` | stream-read retry branch removed | `00 bf` | `00 bf` | True |
| `0x0967c` | `0x0801967c` | command 0x40 retry budget clamped to 0x60 | `60 27` | `60 27` | True |
| `0x09682` | `0x08019682` | command 0x48 retry budget clamped to 0x60 | `60 27` | `60 27` | True |
| `0x09694` | `0x08019694` | small fallback retry budget kept at 0x0a | `0a 27` | `0a 27` | True |
| `0x09706` | `0x08019706` | command 0x40 busy failure routed to existing error/clear block | `4c d1` | `4c d1` | True |
| `0x09758` | `0x08019758` | command/status retry branch removed | `00 bf` | `00 bf` | True |
| `0x097be` | `0x080197be` | mode/status retry branch removed | `00 bf` | `00 bf` | True |
| `0x097e6` | `0x080197e6` | stream error cleanup clears flag bits 0 and 1 | `20 f0 03 00` | `20 f0 03 00` | True |
| `0x0f19a` | `0x0801f19a` | mode/range entry branch to stale state clear wrapper | `1e f0 34 ba` | `1e f0 34 ba` | True |
| `0x2d606` | `0x0803d606` | mode/range stale state clear wrapper | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | `10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b 18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08` | True |

## Direct peripheral literal evidence

Exact 32-bit base-address hits are a conservative test. No direct ADC
literal means an ADC/filter/RMS patch cannot yet be justified by a
simple register-base address.

| Image | ADC1 | ADC2 | ADC3 | DMA1 | DMA2 | SPI1 | GPIOB | GPIOD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| v3.16 | 0 | 0 | 0 | 1 | 0 | 3 | 17 | 15 |
| v4.0 | 0 | 0 | 0 | 1 | 0 | 3 | 19 | 14 |
| v4.0.1b-exp13 | 0 | 0 | 0 | 1 | 0 | 4 | 19 | 14 |

## Peripheral code-path concentration

Top functions with PC-literal peripheral loads. These are candidates for
hardware interaction, not confirmed ADC math hooks.

### v3.16

| Function | Hit Count | Peripherals |
|---:|---:|---|
| `0x080188fa` | 13 | `{'CAN1': 13}` |
| `0x08018a7e` | 13 | `{'CAN1': 13}` |
| `0x0801886a` | 12 | `{'CAN1': 12}` |
| `0x080189d8` | 12 | `{'CAN1': 12}` |
| `0x0803d860` | 6 | `{'EXTI': 6}` |
| `0x08017dca` | 5 | `{'PERIPH 0x40020800': 5}` |
| `0x08017ad4` | 4 | `{'PERIPH 0x40020c00': 4}` |
| `0x08015a92` | 3 | `{'USART1': 3}` |
| `0x080171b6` | 3 | `{'TIM1': 1, 'GPIOC': 1, 'GPIOB': 1}` |
| `0x08017448` | 3 | `{'USART3': 3}` |
| `0x080184d8` | 3 | `{'GPIOB': 1, 'TIM4': 2}` |
| `0x0803e51a` | 3 | `{'AFIO': 3}` |
| `0x080171f2` | 2 | `{'GPIOC': 1, 'GPIOB': 1}` |
| `0x0801721e` | 2 | `{'GPIOC': 1, 'GPIOB': 1}` |
| `0x080174aa` | 2 | `{'TIM3': 2}` |
| `0x08017640` | 2 | `{'TIM4': 2}` |
| `0x08017882` | 2 | `{'PERIPH 0x40020800': 2}` |
| `0x080178d4` | 2 | `{'PERIPH 0x40020800': 2}` |

### v4.0

| Function | Hit Count | Peripherals |
|---:|---:|---|
| `0x08018fec` | 13 | `{'CAN1': 13}` |
| `0x0801916c` | 13 | `{'CAN1': 13}` |
| `0x080190c6` | 12 | `{'CAN1': 12}` |
| `0x08018f26` | 6 | `{'CAN1': 6}` |
| `0x08018fa4` | 6 | `{'CAN1': 6}` |
| `0x0803897c` | 6 | `{'EXTI': 6}` |
| `0x080184c0` | 5 | `{'PERIPH 0x40020800': 5}` |
| `0x08015ad6` | 3 | `{'USART1': 3}` |
| `0x080178e2` | 3 | `{'TIM1': 1, 'GPIOC': 1, 'GPIOB': 1}` |
| `0x08017bc4` | 3 | `{'USART3': 3}` |
| `0x08018bca` | 3 | `{'GPIOB': 1, 'TIM4': 2}` |
| `0x08039636` | 3 | `{'AFIO': 3}` |
| `0x0801791e` | 2 | `{'GPIOC': 1, 'GPIOB': 1}` |
| `0x0801794a` | 2 | `{'GPIOC': 1, 'GPIOB': 1}` |
| `0x08017c26` | 2 | `{'TIM3': 2}` |
| `0x08017ff2` | 2 | `{'PERIPH 0x40020800': 2}` |
| `0x08018044` | 2 | `{'PERIPH 0x40020800': 2}` |
| `0x08018056` | 2 | `{'PERIPH 0x40020800': 2}` |

### v4.0.1b-exp13

| Function | Hit Count | Peripherals |
|---:|---:|---|
| `0x08018fec` | 13 | `{'CAN1': 13}` |
| `0x0801916c` | 13 | `{'CAN1': 13}` |
| `0x080190c6` | 12 | `{'CAN1': 12}` |
| `0x08018f26` | 6 | `{'CAN1': 6}` |
| `0x08018fa4` | 6 | `{'CAN1': 6}` |
| `0x0803897c` | 6 | `{'EXTI': 6}` |
| `0x080184c0` | 5 | `{'PERIPH 0x40020800': 5}` |
| `0x08015ad6` | 3 | `{'USART1': 3}` |
| `0x080178e2` | 3 | `{'TIM1': 1, 'GPIOC': 1, 'GPIOB': 1}` |
| `0x08017bc4` | 3 | `{'USART3': 3}` |
| `0x08018bca` | 3 | `{'GPIOB': 1, 'TIM4': 2}` |
| `0x08039636` | 3 | `{'AFIO': 3}` |
| `0x08017554` | 2 | `{'SCB': 2}` |
| `0x0801791e` | 2 | `{'GPIOC': 1, 'GPIOB': 1}` |
| `0x0801794a` | 2 | `{'GPIOC': 1, 'GPIOB': 1}` |
| `0x08017c26` | 2 | `{'TIM3': 2}` |
| `0x08017ff2` | 2 | `{'PERIPH 0x40020800': 2}` |
| `0x08018044` | 2 | `{'PERIPH 0x40020800': 2}` |

## Important literal search

| Image | Literal | Meaning | Hits | First Offsets |
|---|---:|---|---:|---|
| v3.16 | `0x2000022c` | shared stream/status byte used by V4.0 measurement helper | 1 | `0x0c304` |
| v3.16 | `0x20000130` | busy/retry word observed near command/status logic | 0 | none |
| v3.16 | `0x40012400` | ADC1 base, direct literal would support an internal ADC patch | 0 | none |
| v3.16 | `0x40012800` | ADC2 base, direct literal would support an internal ADC patch | 0 | none |
| v3.16 | `0x40013c00` | ADC3 base, direct literal would support an internal ADC patch | 0 | none |
| v3.16 | `0x40020000` | DMA1 base | 1 | `0x07ff4` |
| v3.16 | `0x40020400` | DMA2 base | 0 | none |
| v4.0 | `0x2000022c` | shared stream/status byte used by V4.0 measurement helper | 4 | `0x0986c`, `0x09870`, `0x09b64`, `0x09b68` |
| v4.0 | `0x20000130` | busy/retry word observed near command/status logic | 2 | `0x07e50`, `0x09868` |
| v4.0 | `0x40012400` | ADC1 base, direct literal would support an internal ADC patch | 0 | none |
| v4.0 | `0x40012800` | ADC2 base, direct literal would support an internal ADC patch | 0 | none |
| v4.0 | `0x40013c00` | ADC3 base, direct literal would support an internal ADC patch | 0 | none |
| v4.0 | `0x40020000` | DMA1 base | 1 | `0x0871c` |
| v4.0 | `0x40020400` | DMA2 base | 0 | none |
| v4.0.1b-exp13 | `0x2000022c` | shared stream/status byte used by V4.0 measurement helper | 5 | `0x0986c`, `0x09870`, `0x09b64`, `0x09b68`, `0x2d61c` |
| v4.0.1b-exp13 | `0x20000130` | busy/retry word observed near command/status logic | 2 | `0x07e50`, `0x09868` |
| v4.0.1b-exp13 | `0x40012400` | ADC1 base, direct literal would support an internal ADC patch | 0 | none |
| v4.0.1b-exp13 | `0x40012800` | ADC2 base, direct literal would support an internal ADC patch | 0 | none |
| v4.0.1b-exp13 | `0x40013c00` | ADC3 base, direct literal would support an internal ADC patch | 0 | none |
| v4.0.1b-exp13 | `0x40020000` | DMA1 base | 1 | `0x0871c` |
| v4.0.1b-exp13 | `0x40020400` | DMA2 base | 0 | none |

## exp13 code-cave caller audit

Official V4.0 should not have normal callers into the area reused by
the exp11/exp13 low byte-IO wrapper or the exp13 mode/range wrapper.
Current V4.0.1b should show only the deliberate branches from
`0x08016a06` to `0x08016a50` and `0x0801f19a` to `0x0803d606`.

| Image | Target | Meaning | Control-flow Refs | Literal Refs |
|---|---:|---|---|---|
| v4.0 | `0x08016a50` | exp11/exp13 low byte-IO wrapper code cave, original V4 setup-helper prefix | none | none |
| v4.0 | `0x08016aae` | adjacent original V4 setup helper area | none | none |
| v4.0 | `0x0803d606` | exp13 mode/range stale state clear wrapper code cave | none | none |
| v4.0.1b-exp13 | `0x08016a50` | exp11/exp13 low byte-IO wrapper code cave, original V4 setup-helper prefix | `0x08016a06 b.w #0x8016a50` | none |
| v4.0.1b-exp13 | `0x08016aae` | adjacent original V4 setup helper area | none | none |
| v4.0.1b-exp13 | `0x0803d606` | exp13 mode/range stale state clear wrapper code cave | `0x0801f19a b.w #0x803d606` | none |

## UI/manual text clues

| Resource | Entry | Len | Text |
|---|---:|---:|---|
| official-en | 20 | 13 | `Voltage(AC)` |
| official-en | 21 | 13 | `Voltage(DC)` |
| official-en | 23 | 37 | ` <HOLD> Hold        <F1> Zeroing   ` |
| official-en | 26 | 7 | `HOLD ` |
| official-en | 27 | 4 | `AC` |
| official-en | 28 | 4 | `DC` |
| official-en | 32 | 37 | ` <HOLD> Hold         <F1> Zeroing  ` |
| official-en | 38 | 37 | ` <HOLD> Hold        <F1> Zeroing   ` |
| official-en | 42 | 23 | `Frequency Measurement` |
| official-en | 46 | 31 | `Contact Resistance:          ` |
| official-en | 48 | 23 | `Frequency:         Hz` |
| official-en | 67 | 35 | `Calibrate the voltage with probe.` |
| official-en | 69 | 35 | ` <UP> <Down> Adjust actual value ` |
| official-en | 74 | 24 | `Supply Voltage:      V` |
| official-en | 77 | 32 | `Calibration Voltage of Battery` |
| official-en | 79 | 30 | `Calibration the current(mA) ` |
| official-en | 80 | 31 | `Conect to Signal current(mA)!` |
| official-en | 81 | 37 | `Calibration Vehicle Circuit Voltage` |
| official-en | 82 | 28 | `Conect to Signal Voltage !` |
| official-en | 83 | 25 | `Calibration current(A) ` |
| official-en | 84 | 30 | `Conect to Signal current(A)!` |
| official-en | 89 | 15 | `Voltage:     ` |
| official-en | 90 | 23 | `Voltage Signal Output` |
| official-en | 94 | 23 | `Adj. Voltage\uff1a       ` |
| official-en | 95 | 28 | `<F1><F2> Frequency Setting` |
| official-en | 104 | 34 | `Drive the fuel injector: Choose ` |
| official-en | 105 | 34 | `the C01 line to connect the fuel` |
| official-en | 106 | 34 | `injector, and then connect the  ` |
| official-en | 108 | 34 | `Detect fuel injection signal: co` |
| official-en | 109 | 34 | `nnect the black probe to the veh` |
| official-en | 111 | 34 | `to the fuel injector pin, press ` |
| official-en | 124 | 34 | `normal output signal voltage is ` |
| official-en | 135 | 34 | `voltage display, press up button` |
| official-en | 139 | 34 | `probe voltage is close to the ba` |
| official-en | 140 | 34 | `ttery voltage, blue means the pr` |
| official-en | 141 | 34 | `obe voltage is too low and there` |
| official-en | 164 | 26 | `Min.voltage value > 9.6V` |
| official-en | 165 | 27 | `Min.voltage value > 19.2V` |
| official-en | 166 | 20 | `Fuel Injector Test` |
| official-en | 172 | 20 | `Real-time voltage:` |
| official-en | 173 | 18 | `Minimum Voltage:` |
| official-en | 175 | 21 | `Voltage is too low.` |
| official-en | 178 | 23 | `2.Voltage Measurement` |
| official-en | 179 | 23 | `3.Current Measurement` |
| official-en | 181 | 16 | `5.Oscilloscope` |
| official-en | 183 | 25 | `7.Battery cranking test` |
| official-en | 184 | 17 | `8.Injector test` |
| official-en | 190 | 26 | `14.Frequency Measurement` |
| official-en | 192 | 23 | `2.Voltage Measurement` |
| official-en | 193 | 23 | `3.Current Measurement` |
| official-en | 195 | 16 | `5.Oscilloscope` |
| official-en | 197 | 25 | `7.Frequency Measurement` |
| official-en | 199 | 23 | `2.Voltage Measurement` |
| official-en | 200 | 23 | `3.Current Measurement` |
| official-en | 202 | 16 | `5.Oscilloscope` |
| official-en | 203 | 28 | `6.Adj. Voltage signal Test` |
| official-en | 214 | 36 | `f the light,<HOLD> key to lock the` |
| official-en | 216 | 36 | ` ><F2>to operate according to the ` |
| official-en | 219 | 36 | `2.Voltage Measurement             ` |
| official-en | 220 | 36 | `Enter the voltage measurement func` |
| official-en | 221 | 36 | `tion,the current measurement value` |
| official-en | 222 | 36 | ` is displayed,press<HOLD>to lock t` |
| official-en | 224 | 36 | `zeroing.When using, short connecte` |
| official-en | 225 | 36 | `d the red and black probe,and hold` |
| official-en | 228 | 36 | `to switch DC voltage/AC voltage/wa` |
| official-en | 229 | 36 | `veform display. The voltage measur` |
| official-en | 231 | 36 | `x.DC voltage is 1000V, the max.AC ` |
| official-en | 232 | 36 | `voltage is 700V, and the range is ` |
| official-en | 234 | 36 | `3.Current Measurement             ` |
| official-en | 235 | 36 | `Enter the current measurement func` |
| official-en | 236 | 36 | `tion,the current measurement value` |
| official-en | 237 | 36 | ` is displayed,press<HOLD>to lock t` |
| official-en | 239 | 36 | `zeroing.When using, short connecte` |
| official-en | 240 | 36 | `d the red and black probe,and hold` |
| official-en | 243 | 36 | `to switch DC voltage/AC voltage.  ` |
| official-en | 245 | 36 | `nt jack.If it shows mA (green), it` |
| official-en | 247 | 36 | `ted from the mA jack for measureme` |
| official-en | 250 | 36 | `rted from the 20A jack for measure` |
| official-en | 251 | 36 | `ment. Current measurement range is` |
| official-en | 255 | 36 | `unction,the current measurement va` |
| current-ms | 20 | 12 | `Voltan(AC)` |
| current-ms | 21 | 12 | `Voltan(DC)` |
| current-ms | 23 | 36 | ` <HOLD> Tahan       <F1> Sifar    ` |
| current-ms | 27 | 4 | `AC` |
| current-ms | 28 | 4 | `DC` |
| current-ms | 32 | 36 | ` <HOLD> Tahan        <F1> Sifar   ` |
| current-ms | 38 | 36 | ` <HOLD> Tahan       <F1> Sifar    ` |
| current-ms | 42 | 16 | `Ukur Frekuensi` |
| current-ms | 48 | 22 | `Frekuensi:        Hz` |
| current-ms | 67 | 31 | `Tentukur voltan dengan probe.` |
| current-ms | 74 | 23 | `Voltan Bekal:       V` |
| current-ms | 77 | 24 | `Tentukur Voltan Bateri` |
| current-ms | 79 | 20 | `Tentukur arus(mA) ` |
| current-ms | 80 | 30 | `Sambung ke isyarat arus(mA)!` |
| current-ms | 81 | 33 | `Tentukur Voltan Litar Kenderaan` |
| current-ms | 82 | 28 | `Sambung ke isyarat voltan!` |
| current-ms | 83 | 19 | `Tentukur arus(A) ` |
| current-ms | 84 | 29 | `Sambung ke isyarat arus(A)!` |
| current-ms | 89 | 15 | `Voltan:      ` |
| current-ms | 90 | 23 | `Output Isyarat Voltan` |
| current-ms | 94 | 23 | `Laras Voltan:        ` |
| current-ms | 95 | 26 | `<F1><F2> Tetap Frekuensi` |
| current-ms | 104 | 34 | `Pacu penyuntik bahan api: pilih ` |
| current-ms | 114 | 34 | `Pacu gegelung relay: pilih kabel` |
| current-ms | 124 | 34 | `Voltan isyarat biasa kira-kira  ` |
| current-ms | 125 | 34 | `4.5V dan frekuensi maksimum     ` |
| current-ms | 135 | 34 | `voltan. Tekan UP untuk output   ` |
| current-ms | 138 | 34 | `bermaksud voltan probe hampir   ` |
| current-ms | 139 | 34 | `dengan voltan bateri; biru      ` |
| current-ms | 140 | 34 | `bermaksud voltan terlalu rendah ` |
| current-ms | 152 | 34 | `Output voltan dari C01-S1. Julat` |
| current-ms | 164 | 19 | `Voltan min > 9.6V` |
| current-ms | 165 | 20 | `Voltan min > 19.2V` |
| current-ms | 172 | 20 | `Voltan masa nyata:` |
| current-ms | 173 | 17 | `Voltan Minimum:` |
| current-ms | 175 | 16 | `Voltan rendah.` |
| current-ms | 178 | 15 | `2.Ukur Voltan` |
| current-ms | 179 | 13 | `3.Ukur Arus` |
| current-ms | 183 | 25 | `7.Ujian cranking bateri` |
| current-ms | 190 | 19 | `14.Ukur Frekuensi` |
| current-ms | 192 | 15 | `2.Ukur Voltan` |
| current-ms | 193 | 13 | `3.Ukur Arus` |
| current-ms | 197 | 18 | `7.Ukur Frekuensi` |
| current-ms | 199 | 15 | `2.Ukur Voltan` |
| current-ms | 200 | 13 | `3.Ukur Arus` |
| current-ms | 203 | 24 | `6.Ujian isyarat voltan` |
| current-ms | 214 | 36 | `hidup/matikan lampu, <HOLD>       ` |
| current-ms | 215 | 36 | `mengunci nilai bacaan, <F1><F2>   ` |
| current-ms | 219 | 36 | `2.Ukur Voltan                     ` |
| current-ms | 220 | 36 | `Masuk fungsi ukur voltan untuk    ` |
| current-ms | 221 | 36 | `melihat bacaan semasa. Tekan      ` |
| current-ms | 222 | 36 | `<HOLD> untuk mengunci bacaan dan  ` |
| current-ms | 223 | 36 | `<F1> untuk sifar. Semasa guna,    ` |
| current-ms | 226 | 36 | `<Fn> untuk tukar mod DC/AC/bentuk ` |
| current-ms | 227 | 36 | `gelombang. Julat voltan hingga    ` |
| current-ms | 228 | 36 | `1000V; DC maks 1000V, AC maks     ` |
| current-ms | 234 | 36 | `3.Ukur Arus                       ` |
| current-ms | 235 | 36 | `Masuk fungsi ukur arus untuk      ` |
| current-ms | 236 | 36 | `melihat bacaan semasa. Tekan      ` |
| current-ms | 237 | 36 | `<HOLD> untuk mengunci bacaan dan  ` |
| current-ms | 238 | 36 | `<F1> untuk sifar. Pintaskan probe ` |
| current-ms | 241 | 36 | `DC/AC. Tekan <F2> untuk tukar jack` |
| current-ms | 243 | 36 | `merah pada jack mA; 20A kuning    ` |
| current-ms | 244 | 36 | `bermaksud probe merah pada jack   ` |
| current-ms | 245 | 36 | `20A. Julat arus 0-200mA.          ` |
| current-ms | 255 | 36 | `melihat bacaan semasa. Tekan      ` |
| current-ms | 256 | 36 | `<HOLD> untuk mengunci bacaan dan  ` |
| current-ms | 257 | 36 | `<F1> untuk sifar. Pintaskan probe ` |
| current-ms | 260 | 36 | `paparan rintangan atau voltan     ` |
| current-ms | 262 | 36 | `rintangan dan jatuhan voltan      ` |
| current-ms | 281 | 36 | `yang diukur. Tekan <HOLD> untuk   ` |
| current-ms | 287 | 36 | `voltan, <DOWN> membesarkan nilai  ` |
| current-ms | 299 | 36 | `automotif. Bacaan semasa          ` |
| current-ms | 300 | 36 | `dipaparkan; <HOLD> mengunci bacaan` |
| current-ms | 301 | 36 | `dan <F1> untuk sifar. Sambungkan  ` |
| current-ms | 305 | 36 | `voltan/bentuk gelombang. <UP>     ` |
| current-ms | 306 | 36 | `memacu output voltan positif untuk` |
| current-ms | 309 | 36 | `negatif untuk memacu beban kecil  ` |
| current-ms | 311 | 36 | `voltan hampir voltan bekalan,     ` |
| current-ms | 313 | 36 | `voltan di bawah 0.7V, pulse kesan ` |

## Findings

- The strongest firmware-side clue is still shared stream/status blocking:
  when the number and battery icon vanish together, the UI/status refresh
  is likely waiting on measurement/status recovery rather than suffering
  only from a bitmap or text resource problem.
- The exp13 binary really modifies the stream/status, low byte-IO, stream error-state cleanup, and mode/range entry path.
  It is not a cosmetic-only build.
- Direct ADC1/ADC2/ADC3 literal hits remain absent. The analog front-end may
  be external, indirectly addressed, or hidden behind a stream protocol.
  A claimed ADC averaging/RMS patch is unsafe until the input/output
  contract of that routine is confirmed.
- DMA literals can be present as platform support, but that alone does not
  prove a measurement DMA recovery hook.
- V4.0.2-style guessed offset patches must stay rejected unless every
  target is revalidated against disassembly and a safe caller contract.

## Safe next decision

Do not add a new ADC/RMS/math patch in this pass. Exp13 has already added
the confirmed mode-change state reset hook. The next firmware change
should only be made after a valid-reading timeout hook or measurement
buffer/RMS accumulator reset hook is confirmed. Until then, use the
bench CSV and this audit to separate hardware leakage/noise from
firmware recovery latency.
