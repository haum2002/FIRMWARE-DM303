# DM303 V4.0.1 beta final package report

Final folder: `dm303_firmware/DM303-V4.0.1-beta/`

## Source rules

- `backup/` is read-only reference input.
- `firmware-candidates/v4.0.1-beta/` is staging output.
- `dm303_firmware/DM303-V4.0.1-beta/` is rebuilt as the clean flash package.

## Final package checks

- File count: `69`
- Firmware: `DM303V4.0.1-beta.bin`
- Firmware SHA-256: `c97a03d6b21a74ade4fff057d5966fd180a3682a0b08d04a58093ffbfbb006be`
- Malay UI resource SHA-256: `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd`
- SP language slot replacement SHA-256: `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd`
- Staged system overlays copied: `36`
- Soft Eye navmenu overlays use a connected-background mask, softer charcoal/ivory/amber colors, and a card border inside each 92x92 icon asset.
- Firmware code uses the `force-stable-exp2` profile.
- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.
- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.
- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks without changing GPIO order or final pin states.
- This is a stability-first timing profile; switching and zeroing may feel slower by design.
- Header clock/date, 12/24 hour setting, and battery percent/bar display are not included because no safe runtime header hook has been confirmed.
- Root firmware filename is intentionally `DM303V4.0.1-beta.bin` so the updater must display the beta identity.
- The `DM303V4.0.1-beta.bin` content hash matches the staged V4.0.1 beta candidate.
- Original root name `DM303V4.004.bin` is not present in the final package.
- Invalid nested `system/system/` tree is not present.

## Files

| Path | Size | SHA-256 |
|---|---:|---|
| `DM303V4.0.1-beta.bin` | 203260 | `c97a03d6b21a74ade4fff057d5966fd180a3682a0b08d04a58093ffbfbb006be` |
| `QBtest.txt` | 206 | `f5dbf843a66f86919a7a0c9084069dcf48145270c7f87273894cbfe1bf74a287` |
| `readme.txt` | 115 | `9cd641f93c673b447cc3855f21b9299a510950beed17e37fb073c9db60424fdc` |
| `system/ASCII64.dat` | 24320 | `e82995fad4c4227d97aef5db2befa7dda23397d71d8277f8ab2842a9ec5c6018` |
| `system/ASCII96.dat` | 54720 | `da9a6165fb441529a4f913c54960784c19cf6118e2cb0e1ae9671c572b14cd10` |
| `system/HZK-ALL.GBK` | 4194304 | `0286dea064da9b480654586dee2706bbf4ac9abc489bbf57f5652e830cee3301` |
| `system/ICcorner.dat` | 1792 | `f74ae380602419a9a3e0fcbfc6d13dc5d4586657409ead7243b8458946badd8a` |
| `system/icon-C.dat` | 82944 | `a268409bd0962c723b9be5ec7c451076217fb9c1ca63fd52b6df2a5344b20ecb` |
| `system/icon-C1.bmp` | 17000 | `f77b3a8fce8ea0c1c14e68a065714023382e405b2373899dc43badde3546bf83` |
| `system/icon-C10.bmp` | 17000 | `390a7deef0a8162d35334b9ea0aa3ec52caf61ac6921c376f362fe84e25e11f5` |
| `system/icon-C11.bmp` | 17000 | `b56f84ba84994bc033e8fe47f882743e21736815a22ab239e00e54fc497b5ef8` |
| `system/icon-C12.bmp` | 17000 | `4ca6ce45e7f047765797252e09f9e5aeead764ae8c574c23f07d46665ac98c69` |
| `system/icon-C13.bmp` | 17000 | `465e728fd7b6bc587bf8e5a9fdfd34ef899f99bcab4018a6cdfa3cb5b2256c03` |
| `system/icon-C14.bmp` | 17000 | `4488701a888df55f94b2a6a9e4e569380bc7f103f515de7ad692446e77ec8a6f` |
| `system/icon-C15.bmp` | 17000 | `ffcc1c757a19a5558a06c1aa2f1762614d67bb053700e02c5726e4af016b6683` |
| `system/icon-C16.bmp` | 17000 | `0b899d2032f764fe1ad67e71d0c8dbc8e112d060b44c0c96203d7d62bf018f98` |
| `system/icon-C2.bmp` | 17000 | `a54df9411a2a7832fa59129e3d67bb56ef2e4d9ed3d0c3854e59da7d131fc541` |
| `system/icon-C3.bmp` | 17000 | `7100db4478af9780226d17d40fe36de8b808da6948d45e54b15bd6b4b9f7f8a9` |
| `system/icon-C4.bmp` | 17000 | `0b6a424c71664fe80a5c5eff1cd1de41076d1ed4e37c4037588648a8b0728d2c` |
| `system/icon-C5.bmp` | 17000 | `939ec8c92ef140d4d3ddf2bb8403f5d39f2f9d5491fcbbae05da3d574274be9e` |
| `system/icon-C6.bmp` | 17000 | `f618fbc53caeded2557b184dc9cd76dd4563e864b796e729d76794c395145337` |
| `system/icon-C7.bmp` | 17000 | `c445bb765c5396aeec592e078ae51c355cedd1914126d5ad35b80874563fbc1f` |
| `system/icon-C8.bmp` | 17000 | `b91abcb9659f39b470f6cdc5052c4b84f23c3acfc2dd37fe56ce277fa6960060` |
| `system/icon-C9.bmp` | 17000 | `eb38b3698578e7b2fd41eb2914f71d65fb3275a9e1d3e509ffdbba62fb8db777` |
| `system/icon-Dt.dat` | 78336 | `b98018d080aa6b731ca10ce974b53a6d44f831bad04377558f9cef10a8c5553d` |
| `system/icon-E1.bmp` | 17000 | `41b6db491c54c048a6a326981dfdd9f508148959bb10e1af22b19e1f4d09e88c` |
| `system/icon-E10.bmp` | 17000 | `7e5f5ccf19e29529890d6d44ccc72b938523a45a9aef4dd27dcda42524914c88` |
| `system/icon-E11.bmp` | 17000 | `bf53b4bf70d059922de3f8c56698c9bbd901377d5408eefe33cbcc9b045fc2ba` |
| `system/icon-E12.bmp` | 17000 | `fdd6029f3920488fe3e4961403693a68e6de4229ddf43149cd1a55eb95a603f6` |
| `system/icon-E13.bmp` | 17000 | `32910bc669f62ae4fec3aed622cb0ec65f03a245082c2e3d991cca98ad4391b8` |
| `system/icon-E14.bmp` | 17000 | `9650d691026f31d8f715f964c5a1eab9268c4775edab57da648449ff2cdc0b25` |
| `system/icon-E15.bmp` | 17000 | `536e80faaa436e633a557869b917ecbdd7b1caae44d7d35415d1030b54eb00c9` |
| `system/icon-E16.bmp` | 17000 | `32f965f0c3280939c6685693cf1cba6cdb4f41f77dc23831ff15e54346c78c74` |
| `system/icon-E17.bmp` | 17000 | `b2efe529cf44512666e20ff43f744f2dd465b9740bbf9538c4e23489d4fe3569` |
| `system/icon-E18.bmp` | 17000 | `cf3ea6b6c6a36574be0de23793e2a5498a7e1e58f46ff53de5220900ccb5e242` |
| `system/icon-E2.bmp` | 17000 | `f7821c90fac0f960f1aa464c43e94a8962da23c81d4f73b280198e7b862785d9` |
| `system/icon-E3.bmp` | 17000 | `94b1055358d21cb379a74b36cc598ba3b79fe27ab858546bc87dd84ee338dbdf` |
| `system/icon-E4.bmp` | 17000 | `f91f3face55e8e0eb031e92fe0270edaa2dfc6a3c919dc0e95a185a6ff755b65` |
| `system/icon-E5.bmp` | 17000 | `a4c2475e9c3880cd6008b0b0e68c950cb1d64a2c543cc7fa86e9666779632092` |
| `system/icon-E6.bmp` | 17000 | `56b193fe7a2746c69a0c7c8e541b3114576077d27c1040b85559db500621109c` |
| `system/icon-E7.bmp` | 17000 | `3e3198ff27935eec4ef7cee65b1b3e5284f0ffecb32d106b67654f9c27619509` |
| `system/icon-E8.bmp` | 17000 | `238e95fbef4b89919ce1fc5ca67f2764c2338ca0ac005a7968ec668f8d42a320` |
| `system/icon-E9.bmp` | 17000 | `12c8ce91e7452c0bedce52f0ad2cb2a74e70dbd7c9a638dd7aadb4e0cf5606ec` |
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
| `system/TEXT_MS.DAT` | 33280 | `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd` |
| `system/TEXT_NL.DAT` | 29587 | `788a260484f88b8c69ae7259f16367eb162e6e1cef16e72080db5d73c6908f3f` |
| `system/TEXT_PL.DAT` | 31074 | `6103531c0a9e1fdf5e1450950df6798e73f3b040080f81138666835d09dcad18` |
| `system/TEXT_PO.DAT` | 30739 | `dfdba40eb3dd58c981bca9ec6ccaf782058355d7861047bf44bf8ef2b6fb8af7` |
| `system/TEXT_Pt.DAT` | 26853 | `c6e61ff1ea497e90afe37ce7fb403ca9a27aa39b30a01bd1889c649b65a27c69` |
| `system/TEXT_RU.DAT` | 47079 | `dd7b001acc5994e240dcb0234e298a85d9ce35ac4c6f7c8aafe4e72355e4e699` |
| `system/TEXT_SP.DAT` | 33280 | `7f30177d74a396baf31514297723d31b9c4a6961531b2cd84b0758e8eb70d3fd` |
