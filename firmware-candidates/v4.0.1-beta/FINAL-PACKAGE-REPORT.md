# DM303 V4.0.1 beta final package report

Final folder: `DM303-V4.0.1-beta/`

## Source rules

- `backup/` is read-only reference input.
- `firmware-candidates/v4.0.1-beta/` is staging output.
- `DM303-V4.0.1-beta/` is rebuilt as the clean flash package.

## Final package checks

- File count: `68`
- Firmware: `DM303V4.0.1-beta.bin`
- Firmware SHA-256: `9206f9e0c574a8f4ad4c8ba1be7fb51206799641b89e74ce202a93c372382112`
- Malay UI resource SHA-256: `not included in this anti-freeze-exp1 package`
- Staged system overlays copied: `34`
- Dark navmenu overlays use a connected-background mask, preserve original glyph and label pixels, and add a card border inside each 92x92 icon asset.
- Firmware code uses the `anti-freeze-exp1` profile.
- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.
- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.
- Header clock/date, 12/24 hour setting, and battery percent/bar display are not included because no safe runtime header hook has been confirmed.
- Root firmware filename is intentionally `DM303V4.0.1-beta.bin` so the updater must display the beta identity.
- The `DM303V4.0.1-beta.bin` content hash matches the staged V4.0.1 beta candidate.
- Original root name `DM303V4.004.bin` is not present in the final package.
- Invalid nested `system/system/` tree is not present.

## Files

| Path | Size | SHA-256 |
|---|---:|---|
| `DM303V4.0.1-beta.bin` | 203260 | `9206f9e0c574a8f4ad4c8ba1be7fb51206799641b89e74ce202a93c372382112` |
| `QBtest.txt` | 206 | `f5dbf843a66f86919a7a0c9084069dcf48145270c7f87273894cbfe1bf74a287` |
| `readme.txt` | 115 | `9cd641f93c673b447cc3855f21b9299a510950beed17e37fb073c9db60424fdc` |
| `system/ASCII64.dat` | 24320 | `e82995fad4c4227d97aef5db2befa7dda23397d71d8277f8ab2842a9ec5c6018` |
| `system/ASCII96.dat` | 54720 | `da9a6165fb441529a4f913c54960784c19cf6118e2cb0e1ae9671c572b14cd10` |
| `system/HZK-ALL.GBK` | 4194304 | `0286dea064da9b480654586dee2706bbf4ac9abc489bbf57f5652e830cee3301` |
| `system/ICcorner.dat` | 1792 | `f74ae380602419a9a3e0fcbfc6d13dc5d4586657409ead7243b8458946badd8a` |
| `system/icon-C.dat` | 82944 | `a268409bd0962c723b9be5ec7c451076217fb9c1ca63fd52b6df2a5344b20ecb` |
| `system/icon-C1.bmp` | 17000 | `9b535027e07b41ed3226c31f8bf3c83e3415cd8b803d3bf85e22c6888fb6d0d5` |
| `system/icon-C10.bmp` | 17000 | `854d64a7b913bef7c63c03d19a19d5c31843f43deb4fca9ca0c86a08ebfc9339` |
| `system/icon-C11.bmp` | 17000 | `b8c96ad9a9b0aaca2b77d509e8958eb163dad3cf8d0935969f53af6daa2a2466` |
| `system/icon-C12.bmp` | 17000 | `e9b5017bca535fef0cce3109b78b6f866bb213ca6b6efd125160131da51e3e4f` |
| `system/icon-C13.bmp` | 17000 | `e19be3185fb8c0e1671f0b09a7e62b1dcde0bb6120f61b1ca42f3f7ef7cf46a2` |
| `system/icon-C14.bmp` | 17000 | `578d98536aa0d93ad02f709b395d38b56160112dd4fdb53201707a59699f3a44` |
| `system/icon-C15.bmp` | 17000 | `2ef26e18bfbea7485631a35f74d58ce7f1bb06b239e982689393cd096fbf1106` |
| `system/icon-C16.bmp` | 17000 | `d671f19574b7cd90d0a58156f0b77715bab38311ef69aa70e6c212cb39b5c5a3` |
| `system/icon-C2.bmp` | 17000 | `c2eb7024ad16a56cbac7b9789ba204ddae5b31a6f8fba382103cf1de1fad5d15` |
| `system/icon-C3.bmp` | 17000 | `76f33fa999848c9f616439c1af79539a70366e4f9202eac97300be58911f0aac` |
| `system/icon-C4.bmp` | 17000 | `4b08f8b80decd83cb8c2f09e4a65303371d332030c7a5333d7fe780633b52c24` |
| `system/icon-C5.bmp` | 17000 | `789735f12eaa1256fcb2d6cf3f4996ad77d03358117627ca3e1fde8291b3a45e` |
| `system/icon-C6.bmp` | 17000 | `64e8d673fdc321d7f6f7a526cf7c171cdde8e44fadde34d608cc7117389e58d2` |
| `system/icon-C7.bmp` | 17000 | `4222824a4a66ea5092e1a1a3025b3afba457db73e4662afbe3965c13573f215d` |
| `system/icon-C8.bmp` | 17000 | `fc62d359fb55d66631d5c76c30225dc564b62767ec746ed86b6beaea1329db1b` |
| `system/icon-C9.bmp` | 17000 | `cf371de15f8714833338c4faddce8226367740594a0f795f333f20019e1f1e34` |
| `system/icon-Dt.dat` | 78336 | `b98018d080aa6b731ca10ce974b53a6d44f831bad04377558f9cef10a8c5553d` |
| `system/icon-E1.bmp` | 17000 | `2e0b4d17294cf72cf88a47eeaa30d490fa8728239f2fb22a2607f893dbe2755c` |
| `system/icon-E10.bmp` | 17000 | `dcee5349f92201111f6dd3a5153dee9208aa14d88de9183af417bdfaaa66f3d8` |
| `system/icon-E11.bmp` | 17000 | `32087008976e984adaae9d4f2a5f96a9495c93d4f2fb95957fdf051bb204086b` |
| `system/icon-E12.bmp` | 17000 | `5d06d251eb8a13a59d2e9f0b84a1ed1f1d6eac53cf9bc8e24df1bd59f5b7761a` |
| `system/icon-E13.bmp` | 17000 | `90329d0db4fcfae6942221a667935df93a365063f9561c539e27f1be8a261591` |
| `system/icon-E14.bmp` | 17000 | `a8cbe8ff6446b6a178047484b368c157aeff1ef8745a3cc647441727078085e1` |
| `system/icon-E15.bmp` | 17000 | `863ab1087571374a781b43d449ad1f857ef0e14bda329d01e884dc272ac12343` |
| `system/icon-E16.bmp` | 17000 | `1bc84c735d659d21877aacecc35b7506c79b4a153fff2d7f7119aba987b70ddc` |
| `system/icon-E17.bmp` | 17000 | `ed7fe21bfd7f90e00ff5b5eaecf784fe0d91be967df2b57c7eb75f485ce35b2e` |
| `system/icon-E18.bmp` | 17000 | `335eaaddfd90cce0577740a0dee5d11f65c5547b907b1c4f8e5addd2a4ba0f97` |
| `system/icon-E2.bmp` | 17000 | `fdfb0eb5daccd16402dd3b92b46180ec3a8ddb9ec5106f72b6baef7307e4b72f` |
| `system/icon-E3.bmp` | 17000 | `4c5062df527a0ab7b3e85985f378c6dd523f57b12b454ad41da5d48e1d8a39a4` |
| `system/icon-E4.bmp` | 17000 | `92c72486438317659f543d064d27783f2b8cc96723a0c4159d83da3f981c9bd0` |
| `system/icon-E5.bmp` | 17000 | `2236e8c289a335acd0db2a8769f2303982758c81f8eb51c764ac8cbe3e9ebf2b` |
| `system/icon-E6.bmp` | 17000 | `60dc2998afdd662bf55999f7c38310a7cf31abd2837ec35c1b1a0acb5b552b74` |
| `system/icon-E7.bmp` | 17000 | `eacd24ac599d70b28709b859c10f9103078017475066b146527838e0c5983a78` |
| `system/icon-E8.bmp` | 17000 | `b48e3608673eaf2fec067d9e3f40b243fb3abebabcd0fc90a75474546de5bd48` |
| `system/icon-E9.bmp` | 17000 | `11c6556d81f5049c20b83f6dbfc5d17e91c1842bfd7d6ea68424bd20643aed1f` |
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
