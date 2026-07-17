# DM303 V4.0.1h UI/Language Failure Fix

Field result for `V4.0.1g`:

- text smear/calit still appeared above some text;
- `Melayu` appeared in the language menu;
- selecting `Melayu` still showed the original language in many or all areas;
- meter/noise/latency symptoms did not improve.

## Confirmed Resource Mistake

The previous active Malay SP replacement was built from `TEXT_EN.DAT`.

```text
TEXT_EN.DAT count: 815 entries
TEXT_SP.DAT count: 773 entries
V4.0.1g TEXT_SP.DAT count: 815 entries
```

That means the `V4.0.1g` SP slot replacement did not match the official SP
resource layout. On the device, that can explain fallback to original text,
wrong text lookup, or render artefacts.

## V4.0.1h Change

`V4.0.1h` uses:

```text
profile: stability-exp20-ms-safe
firmware marker: V4.0.1h
firmware hash: b9f54dbc46b25a8f9da7af85bc12c8eb591d7806372f10487b1aa717150ac45f
TEXT_SP.DAT hash: ba8dbd603e0cda6f4d16310a70b6b6048e887121b7e5a9265ffb8c3be0d32dbf
```

The new `TEXT_SP.DAT` is rebuilt from the official SP layout:

```text
entries: 773
verify_rebuild: byte-identical
replaced Malay entries: 130
```

Entries that do not fit in the official SP entry length remain unchanged
instead of corrupting the layout.

## Still Unresolved

This does not solve:

- oscilloscope noise;
- voltmeter AC zero offset;
- ammeter AC -> DC latency on mA/A;
- suspected hardware/current-path leakage;
- power/reference rail disturbance;
- True RMS/math/ADC filtering.

Those issues require hardware/protocol evidence after the resource layer is no
longer broken.
