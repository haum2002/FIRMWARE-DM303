# DM303 firmware package folder

This folder is the public firmware package location for the branch.

Current status:

- `DM303-V4.0.1-beta/` contains the current V4.0.1b flash package generated
  with the `force-stable-exp2` profile.
- The package keeps the root firmware filename `DM303V4.0.1-beta.bin` and now
  includes `system/TEXT_MS.DAT` as an added Malay text resource.
- The Qwen-generated V4.0.2b candidate is under
  `firmware-candidates/v4.0.2-beta/`, but it is marked unsafe after audit and
  must not be flashed.
- See `../docs/v402-qwen-audit.md` for the reason V4.0.2b is quarantined.

When publishing to GitHub, this folder must be committed as normal files, not as
a gitlink/submodule pointer.
