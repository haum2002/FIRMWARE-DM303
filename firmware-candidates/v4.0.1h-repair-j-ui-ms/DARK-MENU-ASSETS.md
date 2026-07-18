# DM303 safe dark nav-menu asset report

Status: safe dark theme generated for `v4.0.1 beta`.

## Safety scope

- Source assets in `backup/` are read-only.
- Output menu BMP files keep the official V4.0 BMP headers, RGB565 masks, dimensions, row layout, and file sizes.
- Pixels are rewritten directly as RGB565 values; no image encoder, scaling, compression, or external palette remapping tool is used.
- Vendor dark gradients and anti-alias levels are preserved as deep-blue variants instead of being flattened.
- Icon yellow becomes softer amber, and text/anti-alias pixels become a soft high-contrast white.
- Firmware code, bootloader, and updater are not touched by this tool.

## Palette

- Background: `#0A233B`
- Text: `#EFF7FA`
- Amber: `#FFCC48`

## Label pack

- `system/icon-SP.dat` frames tinted: `17`
- `system/icon-SP.dat` SHA-256: `4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8`

## Files

| File | Size | SHA-256 | Original colors | Final colors | Background px | Text px | Amber px |
|---|---:|---|---:|---:|---:|---:|---:|
| `icon-C1.bmp` | 17000 | `10b31fc3fadb4c95abf8dc5d89db83f7c9b8642eaf1e6a404bdc5fea8ba1e6d8` | 168 | 70 | 7368 | 414 | 682 |
| `icon-C2.bmp` | 17000 | `a58ddad26b8499211797976c04fc020e2ec6937ad6bdc629df93212fc929ecd9` | 178 | 77 | 7321 | 426 | 717 |
| `icon-C3.bmp` | 17000 | `4ddc819a2b702d07685c5a16a731841e32a7ce7ad3f997f25e3fcb090dd51aab` | 131 | 67 | 7218 | 564 | 682 |
| `icon-C4.bmp` | 17000 | `07c51a0788b5a3a0ef657736560d19208eab333447420f0651614acda0776f10` | 165 | 77 | 7048 | 657 | 759 |
| `icon-C5.bmp` | 17000 | `bc5ae81bb31346f86030a54db644edd1efb4c29d7cff7501aad5c24ef7829b5f` | 138 | 72 | 7305 | 387 | 772 |
| `icon-C6.bmp` | 17000 | `9302ab5e6d60d6251e8a55a666d7d26279b31d1b30bab16455f603663094bd46` | 127 | 69 | 7551 | 338 | 575 |
| `icon-C7.bmp` | 17000 | `9166ba89a021fc5adea499a2e69712e6ab89392a7bead62800b6789da7f3bbcc` | 116 | 66 | 7292 | 442 | 730 |
| `icon-C8.bmp` | 17000 | `0e7cecf0f1929d320cbeeefb0efb95c3f3f571d6f0d0f977e49a13554e61ddda` | 127 | 67 | 7256 | 521 | 687 |
| `icon-C9.bmp` | 17000 | `ad2a3223fb005999417d71aef8e8b763d6b8e9f25de82e6185dbec6d6c5c0d71` | 128 | 72 | 7173 | 500 | 791 |
| `icon-C10.bmp` | 17000 | `671402f2fdc12da843ef907d8a6268f787037a7dc9b62e811573ae33ab91a866` | 113 | 64 | 7208 | 596 | 660 |
| `icon-C11.bmp` | 17000 | `ca3f2392fe0e4a0ff7904621df127458dad01973c702c7fae3d4a106f26fdd06` | 121 | 68 | 7276 | 479 | 709 |
| `icon-C12.bmp` | 17000 | `f0dd95e3a14820212809e6879df4a3681445a5d54357e995018bd8120cd49ae0` | 173 | 76 | 7049 | 660 | 755 |
| `icon-C13.bmp` | 17000 | `ce8df24ae472dad5887c71a1e41459acaace6c7ab32aad775d528aa39b1c759d` | 116 | 69 | 7254 | 554 | 656 |
| `icon-C14.bmp` | 17000 | `ccf4a6892878489275e8892c792c14c3744305d3e408287e5a538d0db0b2e025` | 186 | 78 | 7123 | 608 | 733 |
| `icon-C15.bmp` | 17000 | `cd459bdb4351fc16422c039fe1b819a1634d4c005b0bcc2f6453a09480dd2fd9` | 181 | 74 | 7223 | 557 | 684 |
| `icon-C16.bmp` | 17000 | `dfda71cecb75503bd2a92556fefeb14c736a05ab90938a12c344888e66b299cd` | 121 | 70 | 7540 | 229 | 695 |
| `icon-E1.bmp` | 17000 | `a7989c48dda8be53cf9d153e5a2a9a8ee6b70bd565ab485f90c4836f1e32589f` | 169 | 70 | 7333 | 449 | 682 |
| `icon-E2.bmp` | 17000 | `4f0fd51cabcbd442d3fd3fb46241e74497ccb8bb9e21e54bd53e23bdf04946f4` | 179 | 77 | 7326 | 421 | 717 |
| `icon-E3.bmp` | 17000 | `8cfa7e49c3cc8e21b43d76de33f547cd2cd2be80883db79ce27d16266646c983` | 132 | 68 | 7353 | 429 | 682 |
| `icon-E4.bmp` | 17000 | `268283b2dd0194b4acbc820bdf640b1b7ffe78a0630b3656e151f12da8c04252` | 166 | 77 | 7226 | 479 | 759 |
| `icon-E5.bmp` | 17000 | `d438119d5545990021696dc24bd65a541bcff473407cfd12ffdac8e59eb70050` | 139 | 72 | 7278 | 414 | 772 |
| `icon-E6.bmp` | 17000 | `3804c7f57fe3086e9bdb803bc94eca6c4eab8586d5c7630aba78de30e5508da6` | 127 | 67 | 7651 | 238 | 575 |
| `icon-E7.bmp` | 17000 | `1ba737f95e78b709372adffd79ce9f5d9186d60332b5d95b844004aa486591d2` | 117 | 68 | 7220 | 514 | 730 |
| `icon-E8.bmp` | 17000 | `7cf4487cee0033a60d25efa48a745fb0f77b218f5d59f467ac35c7b8871bcabb` | 128 | 68 | 7359 | 418 | 687 |
| `icon-E9.bmp` | 17000 | `42de79a605e016e64f6d278a927da6c8bdffe9a93ce2505e1732f840c63694e3` | 129 | 72 | 7353 | 320 | 791 |
| `icon-E10.bmp` | 17000 | `1c21c84da0f8375f59d7a8047156439b6dba11dcf9a7b4ef6f9ff7b37ce1a7c9` | 113 | 64 | 7357 | 447 | 660 |
| `icon-E11.bmp` | 17000 | `2e75df4026128c76040f0cf99a35703026050f5fe1e93bd3d20e1fbc544c7191` | 122 | 69 | 7382 | 373 | 709 |
| `icon-E12.bmp` | 17000 | `877cc8395f0cd5f3d66c20702f0060970aafb43393b1c91e6233cb15bebae68c` | 174 | 76 | 7205 | 504 | 755 |
| `icon-E13.bmp` | 17000 | `ee77c0e26f21c3e088a9649c2966919604b7dd07b3e51df833b6c5a647506dd1` | 117 | 69 | 7367 | 441 | 656 |
| `icon-E14.bmp` | 17000 | `0232c7912d21433aad76205a051462157a0f77a6c3b2932830d7fadd4c8e4df8` | 185 | 77 | 7330 | 401 | 733 |
| `icon-E15.bmp` | 17000 | `a9b6734839f0644361bdbf9bd75ab9d986926ec1b7ff9811e203767b4ac5dd62` | 182 | 74 | 7403 | 377 | 684 |
| `icon-E16.bmp` | 17000 | `fa0ac2b59017a5e315b1c10ffd97ce6f2e13dcc515cc5e780285376a0cb0a11f` | 123 | 70 | 7483 | 286 | 695 |
| `icon-E17.bmp` | 17000 | `fa3e5ded72d29afad0228bb416a73eacf0918f30d51a312a8e1d4327247a89fc` | 123 | 69 | 7210 | 510 | 744 |
| `icon-E18.bmp` | 17000 | `1844255c1f64766aa2235dd3599e26cdb6cd02c84a60bbd8d7ec2fe91f01976e` | 115 | 69 | 7495 | 415 | 554 |
