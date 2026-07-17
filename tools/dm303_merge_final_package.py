#!/usr/bin/env python3
"""Merge staged DM303 V4.0.1 beta artifacts into the final flash folder.

Workflow:
1. Treat backup/ as read-only reference input.
2. Treat firmware-candidates/v4.0.1-beta/ as staging output.
3. Rebuild dm303_firmware/DM303-V4.0.1-beta/ as the clean final flash package.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import struct
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
BACKUP_V4 = WORKSPACE / "backup" / "DM303 V4.0-read only"
BACKUP_V313 = WORKSPACE / "backup" / "SD-file_DM303_update_US240104-read only"
CANDIDATE = WORKSPACE / "firmware-candidates" / "v4.0.1-beta"
FINAL = WORKSPACE / "dm303_firmware" / "DM303-V4.0.1-beta"

CANDIDATE_BIN = CANDIDATE / "DM303V4.0.1-beta.bin"
CANDIDATE_MS = CANDIDATE / "system" / "TEXT_MS.DAT"
CANDIDATE_SP = CANDIDATE / "system" / "TEXT_SP.DAT"
CANDIDATE_ICON_SP = CANDIDATE / "system" / "icon-SP.dat"
CANDIDATE_LOGO = CANDIDATE / "system" / "LOGO-1.bmp"
FINAL_BIN = FINAL / "DM303V4.0.1-beta.bin"
FINAL_MS = FINAL / "system" / "TEXT_MS.DAT"
FINAL_SP = FINAL / "system" / "TEXT_SP.DAT"
FINAL_ICON_SP = FINAL / "system" / "icon-SP.dat"
FINAL_LOGO = FINAL / "system" / "LOGO-1.bmp"
DM30XDB1_SOURCE = BACKUP_V313 / "system" / "DM30xDB1.dat"
FINAL_DM30XDB1 = FINAL / "system" / "DM30XDB1.dat"
FINAL_REPORT = CANDIDATE / "FINAL-PACKAGE-REPORT.md"
FINAL_SUMS = CANDIDATE / "FINAL-PACKAGE-SHA256.txt"
WORKSPACE_SUMS = WORKSPACE / "CHECKSUMS-SHA256.txt"

DEFAULT_PROFILE = "stability-exp20-ms-safe"
EXPECTED_CANDIDATE_SHA256_BY_PROFILE = {
    "anti-freeze-exp1": "de953819e5d9804cbb66eb7bb2bd17ac24d2d80282816951db1dd9048e77e6ab",
    "boot-acceptance": "ea910e141c9ddb19b550e4769fa87228fb5601492ae412487c39dc6efbc304d5",
    "relay-settle-exp1": "2ff2575d2e5d8311f8e6da26c2acee90231badf6eb77b2b21ce60c03abd6ae65",
    "force-stable-exp2": "74d1c7d812798277859f2c6c45b5263d72ca420c5c8093d3578a58f9a6f67854",
    "v316-switch-exp3": "ce6dfd8ef9a624bac2f9bb20be1d231cfd1f1379673e2a66d604ffd773ef9981",
    "force-enhanced-exp4": "f09f9f43a156b62e90c708c858986ae57f6baa2102a307f5830999b0557249da",
    "clean-stability-exp5": "c27c1e33bb7180252cd165a17c228a604912c0ee5700dbdeb1198f7186c2dbdf",
    "stream-recovery-exp6": "2edb2912d2ef5b4202e23b94701af8b609d0baccc30b82ed3a62c50581c62818",
    "stream-recovery-exp7": "736f26211cd56efaf68f76f180d20f6e71a8bc1dffbc36047d00d73d6475f935",
    "stream-recovery-exp8": "05ec94f87b758f7401bbdc84afd271c66a53797cfc39eef9cfb375011f712bbb",
    "stream-recovery-exp9": "b7a3985a7e739f5f71044a8a8c66243f41b606f761389e155a885da56f480f98",
    "stream-recovery-exp10": "2281a311e9731854b9b55df39ea523551a0761b83a6a967518656129abf55872",
    "stream-recovery-exp11": "d244ffd168dded8656a83e2cf62f663a2228d32803b4a7ee08a4b857b5b44526",
    "stream-recovery-exp12": "0a2090bf5c42cd89509f65881d8b54862d243c6b9d224478ab95bb3ef8e06a16",
    "stream-recovery-exp13": "fbe05118e33743fb56679d5edd1eb2019c1d82e39f499c1459fe89401ce8130b",
    "stream-recovery-exp14": "57204ff3219fe2bbb06df116ce6ffd87593605c66b1e0fd40b803f61d08dcab9",
    "stream-recovery-exp15": "3a2db571a4c783d0df2a454ec13d8d38a3a22a0e6ad7cc9993a0afa1edd7f3a0",
    "stream-recovery-exp16-ui-safe": "29a8bd71cba65538ba25d8e76aa5122234f9a28ad957287ba82fbf4fdf6c60af",
    "clean-resource-exp17": "d3760c42731a5fd6c0db508b51df85b1725046f028d767315916c4ee58904b77",
    "stability-exp18-resource": "a9cc0fc643fa79378b04ab4c00fd7303551c63e2d75329b623f529f8856e90fe",
    "stability-exp19-ui-ms": "24c3bd15282b3e43e42c0e45a7743261469283e61d345bf46a8483eb9350342d",
    "stability-exp20-ms-safe": "b9f54dbc46b25a8f9da7af85bc12c8eb591d7806372f10487b1aa717150ac45f",
}
EXPECTED_MS_SHA256 = "d4a93b1ae0ef215fad8277e768beaa6169bd8b34b2f0f208823791fcec4150ae"
EXPECTED_SP_SHA256 = EXPECTED_MS_SHA256
EXPECTED_SAFE_SP_SHA256 = "ba8dbd603e0cda6f4d16310a70b6b6048e887121b7e5a9265ffb8c3be0d32dbf"
EXPECTED_ICON_SP_SHA256 = "4b3e3c593d3e935905d6dc7bb6494973042cd7ff4a6a76245f308de828941ba8"
EXPECTED_OFFICIAL_SP_SHA256 = "4b6b2fd9c6dee916390144815e7becc02549b7d6f1260b0551c8d939c3acf83e"
EXPECTED_OFFICIAL_ICON_SP_SHA256 = "96f2b294c7fad14a527eb96f1a8f09f7e0f33e2f02f7f43af305c9fa2df57394"
EXPECTED_LOGO_SHA256 = "a847c346837164d25e882f0f10bb47815b43e9f381b130e2870447b20d6845a3"
EXPECTED_DM30XDB1_SHA256 = "846fea603bbd4233ff930cb97fbf4d5be3ad21c9abe3b8cc38fdba9781e1fd79"
EXPECTED_DM30XDB1_SIZE = 1179648
EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE = {
    "default": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("00 bf"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp10": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp11": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp12": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp13": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp14": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp15": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stream-recovery-exp16-ui-safe": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stability-exp18-resource": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stability-exp19-ui-ms": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
    "stability-exp20-ms-safe": {
        0x09570: bytes.fromhex("00 bf"),
        0x09706: bytes.fromhex("4c d1"),
        0x09758: bytes.fromhex("00 bf"),
        0x097BE: bytes.fromhex("00 bf"),
    },
}
EXPECTED_STREAM_RECOVERY_BYTES = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["default"]
EXPECTED_STREAM_RECOVERY_BYTES.update({})
EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["stream-recovery-exp6"] = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["default"]
EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["stream-recovery-exp7"] = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["default"]
EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["stream-recovery-exp8"] = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["default"]
EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["stream-recovery-exp9"] = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["default"]
EXPECTED_LOW_IO_TIMEOUT_BYTES_BY_PROFILE = {
    "stream-recovery-exp7": {
        0x06A1C: bytes.fromhex("41 f2 88 30"),
        0x06A3E: bytes.fromhex("41 f2 88 30"),
    },
    "stream-recovery-exp8": {
        0x06A1C: bytes.fromhex("40 f6 a0 70"),
        0x06A3E: bytes.fromhex("40 f6 a0 70"),
    },
    "stream-recovery-exp9": {
        0x06A1C: bytes.fromhex("40 f6 a0 70"),
        0x06A3E: bytes.fromhex("40 f6 a0 70"),
    },
    "stream-recovery-exp10": {
        0x06A1C: bytes.fromhex("40 f6 a0 70"),
        0x06A3E: bytes.fromhex("40 f6 a0 70"),
    },
}
EXPECTED_COMMAND_RETRY_BYTES_BY_PROFILE = {
    "stream-recovery-exp9": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp10": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp11": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp12": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp13": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp14": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp15": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stream-recovery-exp16-ui-safe": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stability-exp18-resource": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stability-exp19-ui-ms": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
    "stability-exp20-ms-safe": {
        0x0967C: bytes.fromhex("60 27"),
        0x09682: bytes.fromhex("60 27"),
    },
}
EXPECTED_LOW_IO_WRAPPER_BYTES_BY_PROFILE = {
    "stream-recovery-exp11": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stream-recovery-exp12": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stream-recovery-exp13": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stream-recovery-exp14": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stream-recovery-exp15": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stream-recovery-exp16-ui-safe": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stability-exp18-resource": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stability-exp19-ui-ms": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
    "stability-exp20-ms-safe": {
        0x06A06: bytes.fromhex("00 f0 23 b8"),
        0x06A50: bytes.fromhex(
            "70 b5 05 46 40 f6 a0 76 00 24 02 21 0f 48 24 f0 48 f8 "
            "20 b9 01 34 a4 b2 b4 42 f6 d3 13 e0 29 46 0a 48 23 f0 "
            "eb ff 00 24 01 21 08 48 24 f0 39 f8 20 b9 01 34 a4 b2 "
            "b4 42 f6 d3 04 e0 03 48 23 f0 df ff c0 b2 00 e0 ff 20 "
            "70 bd 00 bf 00 30 01 40"
        ),
    },
}
EXPECTED_STREAM_STATE_CLEAR_BYTES_BY_PROFILE = {
    "stream-recovery-exp12": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stream-recovery-exp13": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stream-recovery-exp14": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stream-recovery-exp15": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stream-recovery-exp16-ui-safe": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stability-exp18-resource": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stability-exp19-ui-ms": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
    "stability-exp20-ms-safe": {
        0x097E6: bytes.fromhex("20 f0 03 00"),
    },
}
EXPECTED_MODE_STATE_CLEAR_BYTES_BY_PROFILE = {
    "stream-recovery-exp13": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
    "stream-recovery-exp14": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
    "stream-recovery-exp15": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
    "stream-recovery-exp16-ui-safe": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
    "stability-exp18-resource": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
    "stability-exp19-ui-ms": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
    "stability-exp20-ms-safe": {
        0x0F19A: bytes.fromhex("1e f0 34 ba"),
        0x2D606: bytes.fromhex(
            "10 b5 04 46 04 49 0a 78 22 f0 03 02 0a 70 02 4b "
            "18 47 00 bf 00 bf 2c 02 00 20 9f f1 01 08"
        ),
    },
}
EXPECTED_STREAM_BUSY_GATE_BYTES_BY_PROFILE = {
    "stream-recovery-exp14": {
        0x096BE: bytes.fromhex("02 e0"),
    },
    "stream-recovery-exp15": {
        0x096BE: bytes.fromhex("02 e0"),
    },
    "stream-recovery-exp16-ui-safe": {
        0x096BE: bytes.fromhex("02 e0"),
    },
    "stability-exp18-resource": {
        0x096BE: bytes.fromhex("02 e0"),
    },
    "stability-exp19-ui-ms": {
        0x096BE: bytes.fromhex("02 e0"),
    },
    "stability-exp20-ms-safe": {
        0x096BE: bytes.fromhex("02 e0"),
    },
}
EXPECTED_CURRENT_SWITCH_LATENCY_BYTES_BY_PROFILE = {
    "stream-recovery-exp14": {
        0x1585E: bytes.fromhex("b0 f5 c8 6f"),
        0x15888: bytes.fromhex("b0 f5 c8 6f"),
    },
    "stream-recovery-exp15": {
        0x1585E: bytes.fromhex("b0 f5 c8 6f"),
        0x15888: bytes.fromhex("b0 f5 c8 6f"),
    },
    "stream-recovery-exp16-ui-safe": {
        0x1585E: bytes.fromhex("b0 f5 c8 6f"),
        0x15888: bytes.fromhex("b0 f5 c8 6f"),
    },
    "stability-exp18-resource": {
        0x1585E: bytes.fromhex("b0 f5 c8 6f"),
        0x15888: bytes.fromhex("b0 f5 c8 6f"),
    },
    "stability-exp19-ui-ms": {
        0x1585E: bytes.fromhex("b0 f5 c8 6f"),
        0x15888: bytes.fromhex("b0 f5 c8 6f"),
    },
    "stability-exp20-ms-safe": {
        0x1585E: bytes.fromhex("b0 f5 c8 6f"),
        0x15888: bytes.fromhex("b0 f5 c8 6f"),
    },
}
EXPECTED_INSTANT_SWITCH_BYTES_BY_PROFILE = {
    "stream-recovery-exp15": {
        0x15812: bytes.fromhex("00 bf"),
        0x15838: bytes.fromhex("00 bf"),
        0x15862: bytes.fromhex("00 bf"),
        0x1588C: bytes.fromhex("00 bf"),
    },
}
EXPECTED_STALE_ERROR_GATE_BYTES_BY_PROFILE = {
    "stream-recovery-exp15": {
        0x09818: bytes.fromhex("01 e0"),
        0x098B4: bytes.fromhex("01 e0"),
        0x09950: bytes.fromhex("03 e0"),
    },
}
EXPECTED_VERSION_BYTES_BY_PROFILE = {
    "stream-recovery-exp15": {
        0x02CA0: b"MT100MM V4.0.1c\x00",
        0x02CB0: b"BT100MM V4.0.1c\x00",
    },
    "stream-recovery-exp16-ui-safe": {
        0x02CA0: b"MT100MM V4.0.1d\x00",
        0x02CB0: b"BT100MM V4.0.1d\x00",
    },
    "clean-resource-exp17": {
        0x02CA0: b"MT100MM V4.0.1e\x00",
        0x02CB0: b"BT100MM V4.0.1e\x00",
    },
    "stability-exp18-resource": {
        0x02CA0: b"MT100MM V4.0.1f\x00",
        0x02CB0: b"BT100MM V4.0.1f\x00",
    },
    "stability-exp19-ui-ms": {
        0x02CA0: b"MT100MM V4.0.1g\x00",
        0x02CB0: b"BT100MM V4.0.1g\x00",
    },
    "stability-exp20-ms-safe": {
        0x02CA0: b"MT100MM V4.0.1h\x00",
        0x02CB0: b"BT100MM V4.0.1h\x00",
    },
}
INCLUDE_DARK_MENU_ICONS = True
INCLUDE_MS_RESOURCE = True
REPLACE_SP_WITH_MS_RESOURCE = False
INCLUDE_MS_ICON_PACK = False
INCLUDE_BETA_LOGO = True
INCLUDE_DM30XDB1 = True
MS_SP_RESOURCE_PROFILES = {"stability-exp19-ui-ms", "stability-exp20-ms-safe"}


def replace_sp_with_ms_resource(profile: str | None) -> bool:
    return bool(REPLACE_SP_WITH_MS_RESOURCE or profile in MS_SP_RESOURCE_PROFILES)


def include_ms_icon_pack(profile: str | None) -> bool:
    return bool(INCLUDE_MS_ICON_PACK or profile in MS_SP_RESOURCE_PROFILES)


def expected_sp_sha256(profile: str | None) -> str:
    return EXPECTED_SAFE_SP_SHA256 if profile == "stability-exp20-ms-safe" else EXPECTED_SP_SHA256


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def validate_bmp_layout(path: Path, width: int, height: int, size: int) -> None:
    data = path.read_bytes()
    if len(data) != size:
        raise SystemExit(f"Unexpected BMP size for {path}: {len(data)}")
    if data[:2] != b"BM":
        raise SystemExit(f"Not a BMP file: {path}")
    file_size = struct.unpack_from("<I", data, 2)[0]
    pixel_offset = struct.unpack_from("<I", data, 10)[0]
    dib_size = struct.unpack_from("<I", data, 14)[0]
    actual_width = struct.unpack_from("<i", data, 18)[0]
    actual_height = struct.unpack_from("<i", data, 22)[0]
    planes = struct.unpack_from("<H", data, 26)[0]
    bpp = struct.unpack_from("<H", data, 28)[0]
    compression = struct.unpack_from("<I", data, 30)[0]
    masks = struct.unpack_from("<III", data, 54)
    if (
        file_size != len(data)
        or pixel_offset != 70
        or dib_size != 56
        or actual_width != width
        or actual_height != height
        or planes != 1
        or bpp != 16
        or compression != 3
        or masks != (0xF800, 0x07E0, 0x001F)
    ):
        raise SystemExit(f"Unexpected RGB565 BMP layout for {path}")


def validate_menu_icon_set(root: Path) -> None:
    system = root / "system"
    expected = {f"icon-E{index}.bmp" for index in range(1, 19)}
    expected.update({f"icon-C{index}.bmp" for index in range(1, 17)})
    actual = {path.name for path in system.glob("icon-E*.bmp")}
    actual.update({path.name for path in system.glob("icon-C*.bmp")})
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing or extra:
        raise SystemExit(f"Unexpected dark menu icon set in {system}: missing={missing} extra={extra}")
    for name in sorted(expected):
        validate_bmp_layout(system / name, 92, -92, 17000)


def validate_icon_pack(path: Path, expected_hash: str) -> None:
    data = path.read_bytes()
    if len(data) != 78336 or len(data) % 17 != 0 or len(data) // 17 != 4608:
        raise SystemExit(f"Unexpected icon-SP.dat layout: {path}")
    digest = sha256_file(path)
    if digest != expected_hash:
        raise SystemExit(f"Unexpected icon-SP.dat hash for {path}: {digest}")


def validate_logo(path: Path) -> None:
    validate_bmp_layout(path, 320, -240, 153672)
    digest = sha256_file(path)
    if EXPECTED_LOGO_SHA256 and digest != EXPECTED_LOGO_SHA256:
        raise SystemExit(f"Unexpected LOGO-1.bmp hash for {path}: {digest}")


def validate_official_sp_resources(root: Path) -> None:
    text_sp = root / "system" / "TEXT_SP.DAT"
    icon_sp = root / "system" / "icon-SP.dat"
    text_hash = sha256_file(text_sp)
    icon_hash = sha256_file(icon_sp)
    if text_hash != EXPECTED_OFFICIAL_SP_SHA256:
        raise SystemExit(f"Official TEXT_SP.DAT was not preserved: {text_hash}")
    validate_icon_pack(icon_sp, EXPECTED_OFFICIAL_ICON_SP_SHA256)


def validate_dm30xdb1(path: Path) -> None:
    if path.stat().st_size != EXPECTED_DM30XDB1_SIZE:
        raise SystemExit(f"Unexpected DM30XDB1.dat size for {path}: {path.stat().st_size}")
    data = path.read_bytes()
    if data[:2] != b"BM":
        raise SystemExit(f"DM30XDB1.dat does not start with a BMP frame: {path}")
    digest = sha256_file(path)
    if digest != EXPECTED_DM30XDB1_SHA256:
        raise SystemExit(f"Unexpected DM30XDB1.dat hash for {path}: {digest}")


def validate_stream_recovery_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE.get(
        profile, EXPECTED_STREAM_RECOVERY_BYTES_BY_PROFILE["default"]
    )
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing stream-recovery patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_low_io_timeout_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_LOW_IO_TIMEOUT_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing low-IO timeout patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_command_retry_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_COMMAND_RETRY_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing command-retry patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_low_io_wrapper_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_LOW_IO_WRAPPER_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing low-IO wrapper patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_stream_state_clear_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STREAM_STATE_CLEAR_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing stream-state clear patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_mode_state_clear_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_MODE_STATE_CLEAR_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing mode-state clear patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_stream_busy_gate_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STREAM_BUSY_GATE_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing stream-busy gate patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_current_switch_latency_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_CURRENT_SWITCH_LATENCY_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing current-switch latency patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_instant_switch_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_INSTANT_SWITCH_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing instant-switch patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_stale_error_gate_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_STALE_ERROR_GATE_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing stale-error gate patch at 0x{offset:05x}: "
                f"expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )


def validate_version_bytes(path: Path, profile: str) -> None:
    data = path.read_bytes()
    expected_bytes = EXPECTED_VERSION_BYTES_BY_PROFILE[profile]
    for offset, expected in expected_bytes.items():
        actual = data[offset : offset + len(expected)]
        if actual != expected:
            raise SystemExit(
                f"Missing version marker at 0x{offset:05x}: "
                f"expected {expected!r}, got {actual!r}"
            )


def profile_for_expected_hash(expected_candidate_sha256: str) -> str | None:
    for profile, digest in EXPECTED_CANDIDATE_SHA256_BY_PROFILE.items():
        if digest == expected_candidate_sha256:
            return profile
    return None


def validate_profile_patch_bytes(path: Path, profile: str | None) -> None:
    if profile in {"stream-recovery-exp6", "stream-recovery-exp7", "stream-recovery-exp8", "stream-recovery-exp9", "stream-recovery-exp10", "stream-recovery-exp11", "stream-recovery-exp12", "stream-recovery-exp13", "stream-recovery-exp14", "stream-recovery-exp15", "stream-recovery-exp16-ui-safe", "stability-exp18-resource", "stability-exp19-ui-ms", "stability-exp20-ms-safe"}:
        validate_stream_recovery_bytes(path, profile)
    if profile in EXPECTED_LOW_IO_TIMEOUT_BYTES_BY_PROFILE:
        validate_low_io_timeout_bytes(path, profile)
    if profile in EXPECTED_COMMAND_RETRY_BYTES_BY_PROFILE:
        validate_command_retry_bytes(path, profile)
    if profile in EXPECTED_LOW_IO_WRAPPER_BYTES_BY_PROFILE:
        validate_low_io_wrapper_bytes(path, profile)
    if profile in EXPECTED_STREAM_STATE_CLEAR_BYTES_BY_PROFILE:
        validate_stream_state_clear_bytes(path, profile)
    if profile in EXPECTED_MODE_STATE_CLEAR_BYTES_BY_PROFILE:
        validate_mode_state_clear_bytes(path, profile)
    if profile in EXPECTED_STREAM_BUSY_GATE_BYTES_BY_PROFILE:
        validate_stream_busy_gate_bytes(path, profile)
    if profile in EXPECTED_CURRENT_SWITCH_LATENCY_BYTES_BY_PROFILE:
        validate_current_switch_latency_bytes(path, profile)
    if profile in EXPECTED_INSTANT_SWITCH_BYTES_BY_PROFILE:
        validate_instant_switch_bytes(path, profile)
    if profile in EXPECTED_STALE_ERROR_GATE_BYTES_BY_PROFILE:
        validate_stale_error_gate_bytes(path, profile)
    if profile in EXPECTED_VERSION_BYTES_BY_PROFILE:
        validate_version_bytes(path, profile)


def ensure_inside_workspace(path: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(WORKSPACE)
    return resolved


def copy_tree_contents(source: Path, destination: Path) -> None:
    for item in source.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def staged_system_overlays(profile: str | None = None) -> list[Path]:
    system = CANDIDATE / "system"
    overlays: list[Path] = []
    if INCLUDE_MS_RESOURCE:
        overlays.append(CANDIDATE_MS)
    if replace_sp_with_ms_resource(profile):
        overlays.append(CANDIDATE_SP)
    if include_ms_icon_pack(profile):
        overlays.append(CANDIDATE_ICON_SP)
    if INCLUDE_BETA_LOGO:
        overlays.append(CANDIDATE_LOGO)
    if INCLUDE_DARK_MENU_ICONS:
        overlays.extend(sorted(system.glob("icon-E*.bmp")))
        overlays.extend(sorted(system.glob("icon-C*.bmp")))
    return sorted({path for path in overlays if path.exists()})


def profile_report_lines(profile: str) -> list[str]:
    if profile == "anti-freeze-exp1":
        return [
            "- Firmware code uses the `anti-freeze-exp1` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
        ]
    if profile == "relay-settle-exp1":
        return [
            "- Firmware code uses the `relay-settle-exp1` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits in function `0x0801f0f2` are extended without changing GPIO order or final pin states.",
        ]
    if profile == "force-stable-exp2":
        return [
            "- Firmware code uses the `force-stable-exp2` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks without changing GPIO order or final pin states.",
            "- This is a stability-first timing profile; switching and zeroing may feel slower by design.",
        ]
    if profile == "v316-switch-exp3":
        return [
            "- Firmware code uses the `v316-switch-exp3` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks.",
            "- Mode-switch helper `0x0801f0ac` is wrapped to call `selector(1, flag)` directly, matching the smoother V3.16 non-sub-mode-4 path while leaving call sites unchanged.",
        ]
    if profile == "force-enhanced-exp4":
        return [
            "- Firmware code uses the `force-enhanced-exp4` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits in function `0x0801f0f2` are extended to `8/12/100` ticks for stronger settling after relay/range changes.",
            "- Mode-switch helper `0x0801f0ac` is wrapped to call `selector(1, flag)` directly, matching the smoother V3.16 non-sub-mode-4 path while leaving call sites unchanged.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is a stability-first test profile; switching and boot may feel slower by design.",
        ]
    if profile == "clean-stability-exp5":
        return [
            "- Firmware code uses the `clean-stability-exp5` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` is restored to the original V4.0 behavior; the old wrapper is not used because the V3.16/V4.0 helper comparison did not justify it.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the clean comparison build for the DC/AC blanking and noise tests.",
        ]
    if profile == "stream-recovery-exp6":
        return [
            "- Firmware code uses the `stream-recovery-exp6` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- Four high-level measurement stream/status retry branches are changed to fail fast after the lower helper has already timed out, so UI/status refresh can resume instead of waiting indefinitely.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current stability/latency test build for the DC/AC blanking and battery-icon disappearance symptom.",
        ]
    if profile == "stream-recovery-exp7":
        return [
            "- Firmware code uses the `stream-recovery-exp7` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- Four high-level measurement stream/status retry branches are changed to fail fast after the lower helper has already timed out, so UI/status refresh can resume instead of waiting indefinitely.",
            "- Lower byte-IO hardware-ready timeout in function `0x08016a06` is reduced from `0x2710` to `0x1388` at both wait points, preserving the same failure path but reducing worst-case stall latency after spike/overload.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current stronger stability/latency test build for blank/freeze after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp8":
        return [
            "- Firmware code uses the `stream-recovery-exp8` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- Four high-level measurement stream/status retry branches are changed to fail fast after the lower helper has already timed out, so UI/status refresh can resume instead of waiting indefinitely.",
            "- Lower byte-IO hardware-ready timeout in function `0x08016a06` is reduced from `0x2710` to `0x0fa0` at both wait points, preserving the same failure path while reducing recovery latency further than exp7.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current fine-tuned stability/latency test build for blank/freeze after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp9":
        return [
            "- Firmware code uses the `stream-recovery-exp9` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- Four high-level measurement stream/status retry branches are changed to fail fast after the lower helper has already timed out, so UI/status refresh can resume instead of waiting indefinitely.",
            "- Lower byte-IO hardware-ready timeout in function `0x08016a06` is reduced from `0x2710` to `0x0fa0` at both wait points, preserving the same failure path.",
            "- Command helper `0x08019608` reduces command `0x40` retry count from `0x95` to `0x60` and command `0x48` retry count from `0x87` to `0x60`, preserving the same status polling/failure path.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current balanced stability/latency test build for blank/freeze after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp10":
        return [
            "- Firmware code uses the `stream-recovery-exp10` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- High-level stream/status recovery keeps the exp9 fail-fast behavior, except command `0x40` failure with the busy flag still set now routes to the existing error/clear sequence instead of normal fall-through.",
            "- Lower byte-IO hardware-ready timeout in function `0x08016a06` is reduced from `0x2710` to `0x0fa0` at both wait points, preserving the same failure path.",
            "- Command helper `0x08019608` reduces command `0x40` retry count from `0x95` to `0x60` and command `0x48` retry count from `0x87` to `0x60`, preserving the same status polling/failure path.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current structured recovery build for blank/freeze after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp11":
        return [
            "- Firmware code uses the `stream-recovery-exp11` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- High-level stream/status recovery keeps the exp10 error-route behavior: command `0x40` failure with the busy flag still set routes to the existing error/clear sequence instead of normal fall-through.",
            "- Low byte-IO helper `0x08016a06` is routed to a bounded wrapper at `0x08016a50` that keeps a `0x0fa0` wait budget and returns `0xff` if either ready flag never appears.",
            "- The wrapper preserves the same SPI1 status/write/read HAL calls and exposes timeout to the existing upper stream recovery instead of continuing with a stale read.",
            "- Command helper `0x08019608` reduces command `0x40` retry count from `0x95` to `0x60` and command `0x48` retry count from `0x87` to `0x60`, preserving the same status polling/failure path.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current stronger recovery build for blank/freeze after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp12":
        return [
            "- Firmware code uses the `stream-recovery-exp12` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- High-level stream/status recovery keeps the exp11 bounded low-IO wrapper and command retry clamp.",
            "- Existing stream error cleanup at `0x080197e6` now clears flag bits `0` and `1` from `0x2000022c`, so a timeout/spike cannot leave the stale busy/status bit set after the error path.",
            "- Other observed protection/status bits are not cleared by this patch.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current focused recovery build for blank/freeze with battery-icon disappearance after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp13":
        return [
            "- Firmware code uses the `stream-recovery-exp13` profile.",
            "- Fault/default self-loop vectors are redirected to a shared SCB SYSRESETREQ recovery stub.",
            "- Three known runtime fail-stop loops are changed to return/fall through instead of hanging forever.",
            "- Relay/range selector waits are kept at the official/V3.16 `2/3/10` ticks to avoid adding latency as a false fix.",
            "- Mode-switch helper `0x0801f0ac` stays at the original V4.0 behavior.",
            "- High-level stream/status recovery keeps the bounded low-IO wrapper, command retry clamp, and stream error-state clear.",
            "- Mode/range function `0x0801f19a` enters through a guarded wrapper at `0x0803d606` that preserves the original prologue, clears stale flag bits `0` and `1` from `0x2000022c`, then continues the original relay/range switching code.",
            "- Relay GPIO order, updater/bootloader path, and firmware image size are not changed by this profile.",
            "- The `LOGO-1.bmp` boot resource load is routed through a guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current aggressive recovery build for blank/freeze with battery-icon disappearance after spike, overload, or DC/AC switching.",
        ]
    if profile == "stream-recovery-exp14":
        return [
            "- Firmware code uses the `stream-recovery-exp14` profile.",
            "- It keeps exp13: bounded low-IO wrapper, command retry clamp, stream error-state clear, and mode/range stale-state clear.",
            "- Stream function `0x080196b2` now branches to the normal transaction body instead of returning early when stale busy bit `1` remains set in `0x2000022c`.",
            "- Two long current/meter switch guards at `0x0802585e` and `0x08025888` are capped from `0x3e80` to `0x0640` to target the measured 30-second AC->DC ammeter blank.",
            "- Relay GPIO order, updater/bootloader path, vector reset entry, and firmware image size are not changed by this profile.",
            "- The `LOGO-1.bmp` boot resource load remains routed through the guarded wrapper that calls the original loader, waits 200 ticks, and returns.",
            "- This is the current focused recovery build for the reported ammeter AC->DC latency, stale blank/freeze, and battery-icon disappearance symptom.",
        ]
    if profile == "stream-recovery-exp15":
        return [
            "- Firmware code uses the `stream-recovery-exp15` profile.",
            "- It keeps exp14: bounded low-IO wrapper, command retry clamp, stream error-state clear, mode/range stale-state clear, stream busy gate bypass, and capped long current-switch guards.",
            "- The internal version strings are changed to `V4.0.1c` as a visible flash marker while the SD-card filename remains `DM303V4.0.1-beta.bin`.",
            "- Four elapsed-time skip branches before mode/range calls at `0x08025812`, `0x08025838`, `0x08025862`, and `0x0802588c` are replaced with NOPs so a detected AC/DC transition can call mode/range immediately.",
            "- Three stream transfer helpers at `0x08019818`, `0x080198b4`, and `0x08019950` bypass stale bit0 early error returns and continue into the normal helper body.",
            "- Relay GPIO order, updater/bootloader path, reset vector, resource-loader strings, and firmware image size are not changed by this profile.",
            "- This is a diagnostic-plus-fix build for the reported no-improvement result after exp14; dummy-load testing is required before real overload/current work.",
        ]
    if profile == "stream-recovery-exp16-ui-safe":
        return [
            "- Firmware code uses the `stream-recovery-exp16-ui-safe` profile.",
            "- It keeps exp14 recovery bytes but removes exp15's aggressive immediate-switch and stale bit0 bypass gates because the device showed `V4.0.1c` with no performance improvement and possible regression.",
            "- The internal version strings are changed to `V4.0.1d` as a visible UI-safe flash marker while the SD-card filename remains `DM303V4.0.1-beta.bin`.",
            "- Boot-logo delay is disabled in this profile to isolate the missing loading/progress animation report.",
            "- `TEXT_SP.DAT` and `icon-SP.dat` are preserved from the official V4.0 backup to isolate the text-smear report from the previous Malay SP-slot override.",
            "- Main navmenu BMP icons still use the direct RGB565 dark-blue theme, retuned brighter than exp15 without compression, resizing, or BMP header changes.",
            "- This build is for UI recovery and root-cause isolation; it does not claim analog/noise/latency improvement until device-side tests show it.",
        ]
    if profile == "clean-resource-exp17":
        return [
            "- Firmware code uses the `clean-resource-exp17` profile.",
            "- It removes the ineffective stream/mode latency patches from exp14-exp16 and returns the measurement/control flow to official V4.0 behavior.",
            "- It keeps only fault/default SYSRESETREQ recovery and three runtime fail-stop loop returns, so hard crashes are less likely to stay frozen forever.",
            "- The internal version strings are changed to `V4.0.1e` as a visible clean resource-restore flash marker while the SD-card filename remains `DM303V4.0.1-beta.bin`.",
            "- `TEXT_SP.DAT`, `icon-SP.dat`, the language-name table, and the boot-logo loader call are preserved from official V4.0.",
            "- `system/DM30XDB1.dat` is restored as an external resource because the firmware references it during boot and all V4.0/V3.x binaries carry the same loader string.",
            "- This build is a clean baseline plus missing-resource fix. It is the correct next test after exp15/exp16 proved byte patches entered the device but did not improve physical measurement behavior.",
        ]
    if profile == "stability-exp18-resource":
        return [
            "- Firmware code uses the `stability-exp18-resource` profile.",
            "- It keeps the exp17 `DM30XDB1.dat` resource restoration, so the UI/load resource fault remains fixed.",
            "- It restores the bounded recovery set from exp14/exp16: high-level stream fail-fast/error route, bounded low byte-IO fail return, command retry clamp, stream stale-state cleanup, mode/range stale-state entry clear, stream busy-gate bypass, and the two AC-to-DC long-switch caps.",
            "- The internal version strings are changed to `V4.0.1f` as a visible resource-complete stability flash marker while the SD-card filename remains `DM303V4.0.1-beta.bin`.",
            "- `TEXT_SP.DAT`, `icon-SP.dat`, the language-name table, and the boot-logo loader call are preserved from official V4.0 to avoid reintroducing text smear or loading animation damage.",
            "- This build is the next real stability/latency test after exp17 proved the resource fix but also proved vendor-clean code cannot improve the measurement symptom.",
        ]
    if profile == "stability-exp19-ui-ms":
        return [
            "- Firmware code uses the `stability-exp19-ui-ms` profile.",
            "- It keeps the exp18 bounded recovery set and the restored `system/DM30XDB1.dat` resource.",
            "- The internal version strings are changed to `V4.0.1g` as a visible UI-restored stability flash marker while the SD-card filename remains `DM303V4.0.1-beta.bin`.",
            "- The Spanish language-name slot is renamed to `Melayu` in-place, preserving the table length.",
            "- `TEXT_SP.DAT` and `icon-SP.dat` are replaced with the Malay/dark resource pack, with the official 17-frame icon-pack length preserved.",
            "- This build fixes the exp18 UI regression without claiming that the unresolved analog/noise/latency symptom is solved.",
        ]
    if profile == "stability-exp20-ms-safe":
        return [
            "- Firmware code uses the `stability-exp20-ms-safe` profile.",
            "- It keeps the exp18 bounded recovery set and the restored `system/DM30XDB1.dat` resource.",
            "- The internal version strings are changed to `V4.0.1h` as a visible safe-Malay-SP flash marker while the SD-card filename remains `DM303V4.0.1-beta.bin`.",
            "- The Spanish language-name slot is renamed to `Melayu` in-place, preserving the table length.",
            "- `TEXT_SP.DAT` is rebuilt from the official SP 773-entry layout and only fitting Malay entries are replaced, avoiding the broken 815-entry English-layout resource used in exp19.",
            "- `icon-SP.dat` keeps the Malay/dark 17-frame pack.",
            "- This build tests whether the previous calit/fallback language behavior was caused by the malformed SP text resource. It does not claim analog/noise/latency is solved.",
        ]
    return [
        "- Firmware code uses the `boot-acceptance` rollback/diagnostic profile.",
        "- Fault/default handlers are kept unchanged.",
        "- Runtime fail-stop loops are kept unchanged.",
    ]


def validate_inputs(expected_candidate_sha256: str, profile: str | None = None) -> None:
    required = [BACKUP_V4, CANDIDATE, CANDIDATE_BIN]
    if INCLUDE_MS_RESOURCE:
        required.append(CANDIDATE_MS)
    if replace_sp_with_ms_resource(profile):
        required.append(CANDIDATE_SP)
    if include_ms_icon_pack(profile):
        required.append(CANDIDATE_ICON_SP)
    if INCLUDE_BETA_LOGO:
        required.append(CANDIDATE_LOGO)
    if INCLUDE_DM30XDB1:
        required.append(DM30XDB1_SOURCE)
    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required input: {path}")

    candidate_hash = sha256_file(CANDIDATE_BIN)
    if candidate_hash != expected_candidate_sha256:
        raise SystemExit(f"Unexpected candidate firmware hash: {candidate_hash}")
    validate_profile_patch_bytes(CANDIDATE_BIN, profile or profile_for_expected_hash(expected_candidate_sha256))

    if INCLUDE_MS_RESOURCE:
        ms_hash = sha256_file(CANDIDATE_MS)
        if ms_hash != EXPECTED_MS_SHA256:
            raise SystemExit(f"Unexpected Malay text resource hash: {ms_hash}")
    if replace_sp_with_ms_resource(profile):
        sp_hash = sha256_file(CANDIDATE_SP)
        if sp_hash != expected_sp_sha256(profile):
            raise SystemExit(f"Unexpected SP-slot Malay text resource hash: {sp_hash}")
    if include_ms_icon_pack(profile):
        validate_icon_pack(CANDIDATE_ICON_SP, EXPECTED_ICON_SP_SHA256)
    if INCLUDE_BETA_LOGO:
        validate_logo(CANDIDATE_LOGO)
    if INCLUDE_DM30XDB1:
        validate_dm30xdb1(DM30XDB1_SOURCE)
    if INCLUDE_DARK_MENU_ICONS:
        validate_menu_icon_set(CANDIDATE)


def rebuild_final(profile: str | None = None) -> None:
    final_resolved = ensure_inside_workspace(FINAL)
    backup_resolved = ensure_inside_workspace(BACKUP_V4)
    candidate_resolved = ensure_inside_workspace(CANDIDATE)

    if backup_resolved == final_resolved or candidate_resolved == final_resolved:
        raise SystemExit("Refusing to merge: final path overlaps input path")

    if final_resolved.exists():
        shutil.rmtree(final_resolved)
    final_resolved.mkdir(parents=True)

    copy_tree_contents(backup_resolved, final_resolved)

    original_bin = final_resolved / "DM303V4.004.bin"
    if original_bin.exists():
        original_bin.unlink()

    shutil.copy2(CANDIDATE_BIN, FINAL_BIN)
    for source in staged_system_overlays(profile):
        rel = source.relative_to(CANDIDATE)
        destination = FINAL / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    if INCLUDE_DM30XDB1:
        FINAL_DM30XDB1.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DM30XDB1_SOURCE, FINAL_DM30XDB1)


def inventory(root: Path) -> list[tuple[str, int, str]]:
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            rows.append((rel, path.stat().st_size, sha256_file(path)))
    return rows


def validate_final(expected_candidate_sha256: str, profile: str | None = None) -> list[tuple[str, int, str]]:
    rows = inventory(FINAL)
    rels = {rel for rel, _, _ in rows}
    if "DM303V4.004.bin" in rels:
        raise SystemExit("Final folder still contains original DM303V4.004.bin")
    if "system/system/ASCII64.dat" in rels:
        raise SystemExit("Final folder contains invalid nested system/system tree")
    if "DM303V4.0.1-beta.bin" not in rels:
        raise SystemExit("Final folder is missing DM303V4.0.1-beta.bin")
    if INCLUDE_MS_RESOURCE and "system/TEXT_MS.DAT" not in rels:
        raise SystemExit("Final folder is missing system/TEXT_MS.DAT")
    if replace_sp_with_ms_resource(profile) and "system/TEXT_SP.DAT" not in rels:
        raise SystemExit("Final folder is missing replacement system/TEXT_SP.DAT")
    if include_ms_icon_pack(profile) and "system/icon-SP.dat" not in rels:
        raise SystemExit("Final folder is missing replacement system/icon-SP.dat")
    if INCLUDE_BETA_LOGO and "system/LOGO-1.bmp" not in rels:
        raise SystemExit("Final folder is missing beta system/LOGO-1.bmp")
    if INCLUDE_DM30XDB1 and "system/DM30XDB1.dat" not in rels:
        raise SystemExit("Final folder is missing system/DM30XDB1.dat")

    final_bin_hash = sha256_file(FINAL_BIN)
    if final_bin_hash != expected_candidate_sha256:
        raise SystemExit(f"Final firmware hash mismatch: {final_bin_hash}")
    validate_profile_patch_bytes(FINAL_BIN, profile or profile_for_expected_hash(expected_candidate_sha256))
    if INCLUDE_MS_RESOURCE:
        final_ms_hash = sha256_file(FINAL_MS)
        if final_ms_hash != EXPECTED_MS_SHA256:
            raise SystemExit(f"Final TEXT_MS hash mismatch: {final_ms_hash}")
    if replace_sp_with_ms_resource(profile):
        final_sp_hash = sha256_file(FINAL_SP)
        if final_sp_hash != expected_sp_sha256(profile):
            raise SystemExit(f"Final TEXT_SP hash mismatch: {final_sp_hash}")
    if include_ms_icon_pack(profile):
        validate_icon_pack(FINAL_ICON_SP, EXPECTED_ICON_SP_SHA256)
    if not replace_sp_with_ms_resource(profile) or not include_ms_icon_pack(profile):
        validate_official_sp_resources(FINAL)
    if INCLUDE_BETA_LOGO:
        validate_logo(FINAL_LOGO)
    if INCLUDE_DM30XDB1:
        validate_dm30xdb1(FINAL_DM30XDB1)
    if INCLUDE_DARK_MENU_ICONS:
        validate_menu_icon_set(FINAL)

    return rows


def write_reports(rows: list[tuple[str, int, str]], profile: str) -> None:
    write_text_lf(FINAL_SUMS, "".join(f"{digest}  {rel}\n" for rel, _, digest in rows))
    prefix = FINAL.relative_to(WORKSPACE).as_posix()
    write_text_lf(
        WORKSPACE_SUMS,
        "".join(f"{digest}  {prefix}/{rel}\n" for rel, _, digest in rows),
    )

    lines = [
        "# DM303 V4.0.1 beta final package report",
        "",
        "Final folder: `dm303_firmware/DM303-V4.0.1-beta/`",
        "",
        "## Source rules",
        "",
        "- `backup/` is read-only reference input.",
        "- `firmware-candidates/v4.0.1-beta/` is staging output.",
        "- `dm303_firmware/DM303-V4.0.1-beta/` is rebuilt as the clean flash package.",
        "",
        "## Final package checks",
        "",
        f"- File count: `{len(rows)}`",
        f"- Firmware: `DM303V4.0.1-beta.bin`",
        f"- Firmware SHA-256: `{sha256_file(FINAL_BIN)}`",
        f"- Malay UI resource SHA-256: `{sha256_file(FINAL_MS) if INCLUDE_MS_RESOURCE else f'not included in this {profile} package'}`",
        f"- SP language slot replacement SHA-256: `{sha256_file(FINAL_SP) if replace_sp_with_ms_resource(profile) else 'not replaced'}`",
        f"- Malay SP icon-pack SHA-256: `{sha256_file(FINAL_ICON_SP) if include_ms_icon_pack(profile) else 'not included'}`",
        f"- Beta logo overlay SHA-256: `{sha256_file(FINAL_LOGO) if INCLUDE_BETA_LOGO else 'not included'}`",
        f"- DM30XDB1 resource SHA-256: `{sha256_file(FINAL_DM30XDB1) if INCLUDE_DM30XDB1 else 'not included'}`",
        f"- Staged system overlays copied: `{len(staged_system_overlays(profile))}`",
        "- Main navmenu BMP icons use the safe dark RGB565 theme generated from official vendor V4.0 assets.",
        (
            "- `system/icon-SP.dat` replaces the Spanish graphical label pack with Malay labels, applies the same safe dark RGB565 theme, and preserves the official 17-frame file size."
            if include_ms_icon_pack(profile)
            else "- `system/icon-SP.dat` is preserved from the official V4.0 backup for this UI-safe build."
        ),
        (
            "- `system/TEXT_SP.DAT` is replaced with Malay text for the reused SP language slot."
            if replace_sp_with_ms_resource(profile)
            else "- `system/TEXT_SP.DAT` is preserved from the official V4.0 backup for this UI-safe build."
        ),
        "- `system/LOGO-1.bmp` is converted into the official 16-bit resource layout from the selected beta artwork.",
        (
            "- `system/DM30XDB1.dat` is restored from the official V3.13 SD resource package because every inspected firmware references `\\system\\DM30XDB1.dat`, while the V4.0 support folder omitted it."
            if INCLUDE_DM30XDB1
            else "- `system/DM30XDB1.dat` is not included."
        ),
        *profile_report_lines(profile),
        "- Header clock/date, 12/24 hour setting, and battery percent/bar display are not included because no safe runtime header hook has been confirmed.",
        "- Root firmware filename is intentionally `DM303V4.0.1-beta.bin` so the updater must display the beta identity.",
        "- The `DM303V4.0.1-beta.bin` content hash matches the staged V4.0.1 beta candidate.",
        "- Original root name `DM303V4.004.bin` is not present in the final package.",
        "- Invalid nested `system/system/` tree is not present.",
        "- RGB565 layout checks passed for `LOGO-1.bmp` and all 34 dark menu BMP icons.",
        "- Stream-recovery byte guards are present in the final firmware image.",
        "",
        "## Files",
        "",
        "| Path | Size | SHA-256 |",
        "|---|---:|---|",
    ]
    for rel, size, digest in rows:
        lines.append(f"| `{rel}` | {size} | `{digest}` |")
    write_text_lf(FINAL_REPORT, "\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        choices=sorted(EXPECTED_CANDIDATE_SHA256_BY_PROFILE),
        default=DEFAULT_PROFILE,
        help="expected candidate profile to merge",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_candidate_sha256 = EXPECTED_CANDIDATE_SHA256_BY_PROFILE[args.profile]
    validate_inputs(expected_candidate_sha256, args.profile)
    rebuild_final(args.profile)
    rows = validate_final(expected_candidate_sha256, args.profile)
    write_reports(rows, args.profile)

    print(f"backup_reference={BACKUP_V4}")
    print(f"candidate={CANDIDATE}")
    print(f"final={FINAL}")
    print(f"profile={args.profile}")
    print(f"final_files={len(rows)}")
    print(f"final_firmware_sha256={sha256_file(FINAL_BIN)}")
    if INCLUDE_MS_RESOURCE:
        print(f"final_text_ms_sha256={sha256_file(FINAL_MS)}")
    else:
        print("final_text_ms_sha256=not-included")
    if replace_sp_with_ms_resource(args.profile):
        print(f"final_text_sp_sha256={sha256_file(FINAL_SP)}")
    if include_ms_icon_pack(args.profile):
        print(f"final_icon_sp_sha256={sha256_file(FINAL_ICON_SP)}")
    print(f"report={FINAL_REPORT}")
    print(f"workspace_checksums={WORKSPACE_SUMS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
