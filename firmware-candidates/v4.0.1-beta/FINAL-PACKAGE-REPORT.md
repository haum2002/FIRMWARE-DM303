# DM303 V4.0.1 beta final package report

Final folder: `DM303-V4.0.1-beta/`

## Source rules

- `backup/` is read-only reference input.
- `firmware-candidates/v4.0.1-beta/` is staging output.
- `DM303-V4.0.1-beta/` is rebuilt as the clean flash package.

## Final package checks

- File count: `68`
- Firmware: `DM303V4.0.1-beta.bin`
- Firmware SHA-256: `211cf722a13cab09ba0244eb1b9e919bcc40b6b2dcaf0e4f1756675a353edaa4`
- Malay UI resource SHA-256: `not included in this visible-resource package`
- Staged system overlays copied: `34`
- Final package includes only dark navmenu BMP overlays as the visible proof step.
- Firmware code still stays on the minimal boot-acceptance profile.
- Root firmware filename is intentionally `DM303V4.0.1-beta.bin` so the updater must display the beta identity.
- The `DM303V4.0.1-beta.bin` content hash matches the staged V4.0.1 beta candidate.
- Original root name `DM303V4.004.bin` is not present in the final package.
- Invalid nested `system/system/` tree is not present.

## Files

| Path | Size | SHA-256 |
|---|---:|---|
| `DM303V4.0.1-beta.bin` | 203260 | `211cf722a13cab09ba0244eb1b9e919bcc40b6b2dcaf0e4f1756675a353edaa4` |
| `QBtest.txt` | 206 | `f5dbf843a66f86919a7a0c9084069dcf48145270c7f87273894cbfe1bf74a287` |
| `readme.txt` | 115 | `9cd641f93c673b447cc3855f21b9299a510950beed17e37fb073c9db60424fdc` |
| `system/ASCII64.dat` | 24320 | `e82995fad4c4227d97aef5db2befa7dda23397d71d8277f8ab2842a9ec5c6018` |
| `system/ASCII96.dat` | 54720 | `da9a6165fb441529a4f913c54960784c19cf6118e2cb0e1ae9671c572b14cd10` |
| `system/HZK-ALL.GBK` | 4194304 | `0286dea064da9b480654586dee2706bbf4ac9abc489bbf57f5652e830cee3301` |
| `system/ICcorner.dat` | 1792 | `f74ae380602419a9a3e0fcbfc6d13dc5d4586657409ead7243b8458946badd8a` |
| `system/icon-C.dat` | 82944 | `a268409bd0962c723b9be5ec7c451076217fb9c1ca63fd52b6df2a5344b20ecb` |
| `system/icon-C1.bmp` | 17000 | `6575784a2a4a11d8eda8694fa2ffbc2998ee7f51c1cb6e63782cc11d3c4bfcbe` |
| `system/icon-C10.bmp` | 17000 | `d0efc74efab71c884695ae2f0077d379deaad5e4f477fcd5cb57c9842a2bbdc9` |
| `system/icon-C11.bmp` | 17000 | `c7c81f1219a9c508a155b534fb59d3bc8077674a45d894d39bc914fcf4b65371` |
| `system/icon-C12.bmp` | 17000 | `f55635be732dc7b933cdf91997c279d92fb3793a666c620906641c4d84cd9e9f` |
| `system/icon-C13.bmp` | 17000 | `7bf2188a0ceef6bb268d74088701f2b1e2b78c5a993151d4090d4573646c62ec` |
| `system/icon-C14.bmp` | 17000 | `b26ec5417937f2cb0806cd8a0febc0fa51a20da05726b1ccf067ffb1ea285ba3` |
| `system/icon-C15.bmp` | 17000 | `2f7b5d12b143c249453b2cda29749e4a8d18cc34b089491c29e3a7178500c2d9` |
| `system/icon-C16.bmp` | 17000 | `f2b006e934244826bf5e5ce67a471f10bbfbc3afd17496497cae62faf33c8253` |
| `system/icon-C2.bmp` | 17000 | `6129e49551ab92c02f7c40e0ca5f139afc5db6b65a3bbdac12f1d1e44c4390a5` |
| `system/icon-C3.bmp` | 17000 | `5eca252af7237fe8a9d03f9b9f4e9a3cf480dd4b7288fba650b9c2071658e7f0` |
| `system/icon-C4.bmp` | 17000 | `fac648a98fd1905409473d13aaa53302aaffb02937a3f56288f25df9b4a40601` |
| `system/icon-C5.bmp` | 17000 | `ba0f46999419dcd4b568ee97b81908e8b3acecd6be70087dc9087a1a2b3bd9f7` |
| `system/icon-C6.bmp` | 17000 | `348ea535627eee5ad854966c20d62c68aad6dae16e7d1e0f0e0556623b74e73b` |
| `system/icon-C7.bmp` | 17000 | `5761f811c5ee52fac18698299e27df287e86569096ec882dfd11198e63e1f5fe` |
| `system/icon-C8.bmp` | 17000 | `adbfe6cc07c844d5108ce2f50ef606e472f8ba13058f01ceb6a6e28bc5d7bb91` |
| `system/icon-C9.bmp` | 17000 | `0a9caedca03c99739c83c7b2443b623061e399a915023446f2a4c4dd657305f0` |
| `system/icon-Dt.dat` | 78336 | `b98018d080aa6b731ca10ce974b53a6d44f831bad04377558f9cef10a8c5553d` |
| `system/icon-E1.bmp` | 17000 | `f9625b987efc8da4f5484386b933a519ed23ee2782ab8307cfcdb576ee4d18c4` |
| `system/icon-E10.bmp` | 17000 | `b8d3a5128e0e840a831742a1ec9cf4165ea5cc7370a6c8709b75b64ff15c1db0` |
| `system/icon-E11.bmp` | 17000 | `103963dfa4fa1607e58f3240561fbfe173f6c30e94062dbf7ecffc1d9d624076` |
| `system/icon-E12.bmp` | 17000 | `8fa73063e293d4e3fe2e8099e50c9ab894586f9f0c2bbf5c732a88b1b5fade5b` |
| `system/icon-E13.bmp` | 17000 | `978f222daee29bd1419b3bb51da46f999c92c74bcbedd9fddca7e6669a56ed42` |
| `system/icon-E14.bmp` | 17000 | `0fd1482be1a22c5ae0015bf78f75a5671e52d03beefa558e4b4195b31b9ee83e` |
| `system/icon-E15.bmp` | 17000 | `7a6dbfea9bf07e93e9b9852695503e955f7cff3feaa36f718071e56a14b1ce62` |
| `system/icon-E16.bmp` | 17000 | `5a7926c93bcdb185b79c3f091ebcb56883bc52d16740ced68118e0256e15bd8f` |
| `system/icon-E17.bmp` | 17000 | `e17d73fc1be3a18b8c134b32d58dfe4aa20d8afe0a393e13c1eefc66adbb21b4` |
| `system/icon-E18.bmp` | 17000 | `852ec8ef475d73d3068b5ff09ef6b3999e5738d80a5782d7c90386deea32572e` |
| `system/icon-E2.bmp` | 17000 | `bc694542234add1c53501eae0659285a7a157397ad4b6276636538d4accbfc27` |
| `system/icon-E3.bmp` | 17000 | `effc61bebcf683de477b6efd2da4c644f6550aa3b4032082561d71e31085d8f8` |
| `system/icon-E4.bmp` | 17000 | `1eb62e6e32877183ede8eca07977ab2602236d15e388c2395ff997ccf09792f9` |
| `system/icon-E5.bmp` | 17000 | `62a1961ed47d345b3920f6d3f0f34b9b970869d0ff0afc60d1bf5a86d9f7896e` |
| `system/icon-E6.bmp` | 17000 | `daf8d9c6ed87b4a14cf157a676ce2dc64ccab34f22e936c10b049e308b7b9eef` |
| `system/icon-E7.bmp` | 17000 | `54fa6592b08a6b856c1fe8351472c46d6254899705055cd8307be5db75b9eff1` |
| `system/icon-E8.bmp` | 17000 | `2d74f2c12cb9149622ced81388fd9cdf0e35526199bc9804702d8a4ddc8acaf3` |
| `system/icon-E9.bmp` | 17000 | `2e05124755e1bc1fb5ea33a6fff4b988dfcca406e2bee95e622c47fc4e904e3d` |
| `system/icon-Fr.dat` | 78336 | `c6a70079bb3f65107eab99f81b8b1cf5c8ac372cb33a1df54004a2fe2284f537` |
| `system/icon-IT.dat` | 78336 | `e41ddda8922cba8aa2976f40f4846310760b536c90ed612d3093f0cfa50fd36c` |
| `system/icon-jp.dat` | 78336 | `160a9262d5525860b339bf1ed6954b7735b94c303e17e6ff837659fa53ff94df` |
| `system/icon-Kr.dat` | 78336 | `4630b5e0f94faaf0a1608f31ff1e79b0baa8263ef2a30d9d66a84ed8bab39e2a` |
| `system/icon-NL.dat` | 78336 | `9d01c3100bb44fbfab2c4aece2c07d22335a38bc634a32f7e314830cb8dc9d5f` |
| `system/icon-PL.dat` | 78336 | `f34893bd1c318906c4e245ee0a4741ef1b6aa817f6fb8920323de4a1f43dc635` |
| `system/icon-Pt.dat` | 78336 | `bd6f7602e9f1613a68972cb2a80d64ee103ab48208065ca9e6ca55ae1b11aa57` |
| `system/icon-RS.dat` | 78336 | `3e305e1317a06966a5e44e330ce5e1d32c88767be422e829b06e0ae9c9263140` |
| `system/icon-SP.dat` | 78336 | `96f2b294c7fad14a527eb96f1a8f09f7e0f33e2f02f7f43af305c9fa2df57394` |
| `system/LOGO-1-BDS.bmp` | 153672 | `51324780fab5eeca5fd4b2ff5671a460a1707bb8dcdcf932285dff163b70ab46` |
| `system/LOGO-1.bmp` | 153672 | `f5e84dfd0a14f63ad8c570629c59c36a0a8a8844ce4cfc48c9c89d1031b41ba3` |
| `system/TEXT_CFT.DAT` | 17840 | `24e415a0dd767bb33601ac4a681f9a4f8bc105525c4d3e43e63fc5b0c8de8bba` |
| `system/TEXT_CN.DAT` | 22341 | `e97b859ad975c6501b6410de0e8cf0e938e536898901a25bb3599779f4fe74a5` |
| `system/TEXT_EN.DAT` | 33649 | `8b5d61ed079c69042cc1cfcc972ae22add20ae3aa708452c05bf5e51ad812e93` |
| `system/TEXT_FR.DAT` | 32219 | `a22157ba97734d9cf08ae0dbc2b1a6a5b85c9f4767885ade47858d87d33e86c0` |
| `system/TEXT_GE.DAT` | 30280 | `0c3b7e77ccd70951a42d91cdad8cbed12e9b20b1c6f82d81c81476b1dcd608a4` |
| `system/TEXT_IT.DAT` | 31604 | `f123c49bf87b9b03944829ea1dca8e7a14cc59bbb5b1f6b1d3bf69d32174a71b` |
| `system/TEXT_JP.DAT` | 22655 | `dc3550ec28df1797938226cb07e6920d3343103e411a77e62e310c92d40ab034` |
| `system/TEXT_Kr.DAT` | 22541 | `a28a073e4c8e95165065c6b3325079b073df7bf9852110ed8f8fa229ec0b99e9` |
| `system/TEXT_NL.DAT` | 29587 | `788a260484f88b8c69ae7259f16367eb162e6e1cef16e72080db5d73c6908f3f` |
| `system/TEXT_PL.DAT` | 31074 | `6103531c0a9e1fdf5e1450950df6798e73f3b040080f81138666835d09dcad18` |
| `system/TEXT_PO.DAT` | 30739 | `dfdba40eb3dd58c981bca9ec6ccaf782058355d7861047bf44bf8ef2b6fb8af7` |
| `system/TEXT_Pt.DAT` | 26853 | `c6e61ff1ea497e90afe37ce7fb403ca9a27aa39b30a01bd1889c649b65a27c69` |
| `system/TEXT_RU.DAT` | 47079 | `dd7b001acc5994e240dcb0234e298a85d9ce35ac4c6f7c8aafe4e72355e4e699` |
| `system/TEXT_SP.DAT` | 32888 | `4b6b2fd9c6dee916390144815e7becc02549b7d6f1260b0551c8d939c3acf83e` |
