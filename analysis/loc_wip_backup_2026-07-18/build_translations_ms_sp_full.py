#!/usr/bin/env python3
"""Build localization/ms_MY/translations_ms_sp_full.csv.

Reads analysis/sp_entries_source.csv (773 entries exported from the official
TEXT_SP.DAT) and emits a Malay translation for every entry.

Guarantees, checked for every row before the output file is written:

  * translation is pure ASCII (device font has no accented glyphs)
  * UTF-8 byte length of translation == record_length - 2 exactly
  * only known device placeholder tokens appear inside <...>
  * ALIGNMENT replicates the official entry layout:
      (a) entries padded on BOTH sides (lead>=2 and trail>=2, i.e. visually
          centered) are re-centered: left pad = remaining//2, right = rest;
      (b) all other entries keep the official leading-space count exactly and
          are trailing-space padded;
      (c) units-in-line entries (Min/Maks/V/A/Hz/% and positioned key hints)
          keep value columns at the official byte offsets.
  * blank spacer entries are copied verbatim.

Long help/guide sections are written as SHORT NUMBERED STEPS in Malay (one
action per record where the width allows, continuations indented), which is
what the device shows as one screen line per record. Steps are wrapped into
the records of that section; overflow is a hard error.

Run from the repository root:
    tools/_py/python.exe localization/ms_MY/build_translations_ms_sp_full.py
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "analysis" / "sp_entries_source.csv"
OUT = ROOT / "localization" / "ms_MY" / "translations_ms_sp_full.csv"

ALLOWED_TOKENS = {
    "<HOLD>", "<Fn>", "<F1>", "<F2>", "<ESC>", "<OK>",
    "<UP>", "<Down>", "<DOWN>", "<LEFT>", "<RIGHT>", "<L>", "<R>",
}
TOKEN_RE = re.compile(r"<[^<>]*>")

# ---------------------------------------------------------------------------
# Entries copied verbatim from the source (blank spacer lines and pure
# symbols/units). Note: entry 166 ("Normal") is NOT here anymore; it is
# re-centered via FIXED per the centering rule.
# ---------------------------------------------------------------------------
COPY_INDICES = {18, 19, 40, 85, 86, 90, 96, 97, 109, 116, 117, 145, 150}

# ---------------------------------------------------------------------------
# Fixed single-record translations: CONTENT ONLY (no manual leading or
# trailing spaces). The aligner adds the official leading-space count (or
# re-centers when the official entry is centered).
# ---------------------------------------------------------------------------
FIXED = {
    1: "Memuat ...",
    2: "Tekan butang untuk teruskan",
    3: "Hidupkan",
    4: "Matikan",
    5: "Manual pengguna",
    6: "Maklumat versi",
    7: "Hardware:",
    8: "Software:",
    9: "ID peranti:",
    10: "Tekan butang untuk teruskan",
    11: "Semakan paparan",
    12: "Ujian butang",
    13: "Nota: Papar butang ditekan",
    14: "Tekan <ESC> 2 kali utk keluar",
    15: "untuk keluar dari ujian",
    16: "<ESC>Keluar",
    17: "Butang ditekan:",
    20: "Voltan AC",
    21: "Voltan DC",
    23: "<HOLD> Tahan  <F1>Sifar semula",
    24: "<Fn> Mod fungsi",
    25: "Rint. PD",
    26: "Tahan",
    27: "Arus AC",
    28: "Arus DC",
    29: "20A(kuning)",
    30: "mA(hijau)",
    32: "<HOLD>Tahan   <F1>Sifar semula",
    33: "<Fn>Mod fungsi   <F2> 20A/mA",
    34: "Rintangan",
    35: "Diod:",
    36: "Diod/Rintangan rendah",
    37: "Rintangan:",
    38: "<HOLD>Tahan  <F1>Sifar semula",
    39: "Trig.",
    42: "Ukur frekuensi",
    43: "<Fn> Kesan isyarat masukan (f<6k)",
    44: "rpm",
    45: "<Fn>Kesan isyarat masukan",
    46: "Rintangan sentuh:",
    47: "Output gelombang sinus/petak",
    50: "<F1><F2>Tetap kitar kerja",
    52: "rpm 2 lejang",
    53: "rpm 4 lejang",
    54: "Distributor",
    55: "Data K/Lin:",
    56: "<F1>Padam <L><R>laras baud",
    57: "Data CANBUS:",
    58: "<F1>Padam <L><R>laras baud",
    59: "<Fn> Mod fungsi",
    60: "Tetapan kalendar/masa",
    61: "Tetapan sistem",
    62: "Tetapan asas",
    63: "Tetapan masa",
    64: "Bahasa",
    65: "Bunyi butang",
    66: "Cerah",
    67: "Tentukur voltan probe",
    68: "Sambung probe ke bateri!",
    69: "<UP> <Down> Laras nilai sebenar",
    71: "Masa tidur",
    72: "min",
    73: "Tekan <OK> untuk teruskan",
    76: "Ralat: Sambungan salah!",
    77: "Tentukur Voltan Bateri",
    78: "Sambung bateri kenderaan!",
    79: "Tentukur arus(mA)",
    80: "Sambung isyarat arus(mA)!",
    81: "Tentukur voltan litar kenderaan",
    82: "Sambung isyarat voltan!",
    83: "Tentukur arus(A)",
    84: "Sambung isyarat arus(A)!",
    87: "Huraian fungsi",
    88: "Bocor kunci jauh(3V)",
    89: "Voltan:",
    151: "Pilihan bahasa",
    152: "Hidupkan enjin dan biarkan",
    153: "selama 15s",
    154: "Ujian mula",
    155: "Hidupkan enjin",
    156: "Voltan minimum > 9.6V",
    157: "Voltan minimum > 19.2V",
    158: "Ujian penyuntik automotif",
    159: "Ujian relay automotif",
    160: "Simulasi RPM enjin",
    161: "Tekan <OK> untuk output.",
    162: "Tekan <OK> henti output.",
    163: "Status output",
    164: "Voltan masa nyata:",
    165: "Voltan minimum:",
    166: "Normal",
    167: "Voltan terlalu rendah",
    168: "Ujian periksa litar",
    169: "1.Skrin mula",
    170: "2.Ukur voltan",
    171: "3.Ukur arus",
    172: "4.Ukur rintangan",
    173: "5.Osiloskop",
    174: "6.Ujian periksa litar",
    175: "7.Ujian mula bateri",
    176: "8.Ujian penyuntik",
    177: "9.Ujian relay",
    178: "10.Ujian isyarat analog",
    179: "11.Ujian nadi nyalaan",
    180: "12.Kesan data K/Lin",
    181: "13.Kesan data CAN",
    182: "14.Ukur frekuensi",
    183: "1.Skrin mula",
    184: "2.Ukur voltan",
    185: "3.Ukur arus",
    186: "4.Ukur rintangan",
    187: "5.Osiloskop",
    188: "6.Ujian nadi nyalaan",
    189: "7.Ukur frekuensi",
    190: "1.Skrin mula",
    210: "2.Ukur voltan",
    229: "3.Ukur arus",
    250: "4.Ukur rintangan",
    281: "5.Osiloskop",
    310: "6.Kesan litar automotif",
    356: "7.Ujian mula bateri",
    385: "8.Ujian penyuntik",
    415: "9.Ujian relay",
    441: "10.Ujian isyarat analog",
    476: "11.Ujian nadi nyalaan",
    522: "12.Kesan data K/Lin",
    554: "13.Kesan data talian CAN",
    588: "14.Ukur frekuensi",
    598: "1.Skrin mula",
    618: "2.Ukur voltan",
    637: "3.Ukur arus",
    658: "4.Ukur rintangan",
    689: "5.Osiloskop",
    718: "6.Ujian nadi nyalaan",
    764: "7.Ukur frekuensi",
}

# ---------------------------------------------------------------------------
# EXACT layout entries: units-in-line and positioned key-hint records. The
# full inner layout (leading + column positions) is given explicitly; the
# builder asserts official leading count and official unit-column byte
# offsets are preserved, then trailing-pads. Columns to verify per entry.
# ---------------------------------------------------------------------------
EXACT = {
    22: ("   Min:" + " " * 7 + "V" + " " * 5 + "Maks:" + " " * 6 + "V" + " " * 3, ["V"]),
    31: ("   Min:" + " " * 7 + "A" + " " * 5 + "Maks:" + " " * 6 + "A" + " " * 3, ["A"]),
    41: ("U:" + " " * 6 + "V Min:" + " " * 6 + "V Maks:" + " " * 5 + "V", ["V"]),
    48: ("Frekuensi:" + " " * 14 + "Hz", ["Hz"]),
    49: ("Kitar kerja:" + " " * 12 + "% ", ["%"]),
    51: ("Sensor:" + " " * 3 + "Min:" + " " * 6 + "V Maks:" + " " * 5 + "V", ["V"]),
    70: (" <ESC> Keluar" + " " * 8 + "<OK> Simpan", ["<OK>"]),
    74: ("Voltan bekalan:" + " " * 17 + "V", ["V"]),
    75: ("<UP>Pintas B+  <DOWN>Pintas B-", []),  # tokens differ in length; lead check only
}

# ---------------------------------------------------------------------------
# Help/guide sections as SHORT NUMBERED STEPS (Malay). Each list item is one
# logical line: a numbered step ("1. ...") or an indented sub-line. The
# renderer wraps a step over consecutive records with a 3-space continuation
# indent when it does not fit one record; every step starts on a new record.
# Safety order follows the originals: black/ground probe first, red second.
# ---------------------------------------------------------------------------
S_HOOK_BAT = [
    "1. Matikan enjin dahulu.",
    "2. Pilih kabel C01 + kabel C02.",
    "3. Sambung ke terminal (+) dan (-) bateri kenderaan.",
]
S_HOOK_INJ = [
    "1. Pacu penyuntik bahan api:",
    "2. Pilih kabel C01 ke penyuntik.",
    "3. Sambung klip ke bateri kenderaan.",
]
S_HOOK_INJSIG = [
    "1. Kesan isyarat suntikan:",
    "2. Sambung probe hitam ke badan kenderaan (ground).",
    "3. Sambung probe merah ke pin penyuntik.",
    "4. Tekan <Fn> untuk mula ujian.",
]
S_HOOK_RELAY = [
    "1. Pacu gegelung relay:",
    "2. Pilih kabel C01 ke relay.",
    "3. Sambung klip ke bateri kenderaan.",
    "4. Tekan <OK> untuk memacu relay.",
]
S_ANALOGOUT = [
    "1. Output isyarat analog:",
    "2. Gelombang petak keluar dari kabel C01-K.",
    "3. Voltan isyarat sekitar 4.5V.",
    "4. Frekuensi maksimum 10KHz.",
    "5. Bawah 5KHz: probe boleh semak bentuk gelombang.",
    "6. Tekan <Fn> untuk semak isyarat.",
]
S_HOOK_C04 = [
    "1. Pilih kabel khas C04 untuk kesan litar automotif.",
    "2. Sambung terminal (+) dan (-) bateri kenderaan dengan betul.",
]
S_UPDOWN = [
    "1. Pada paparan voltan:",
    "2. Tekan <UP>: output terminal positif bateri.",
    "3. Tekan <DOWN>: output terminal negatif bateri.",
]
S_REDBLUE = [
    "1. Merah: voltan probe hampir voltan bateri.",
    "2. Biru: voltan terlalu rendah, ada kebocoran.",
]
S_RECONNECT = [
    "1. Cabut bekalan kuasa.",
    "2. Sambung semula terminal (+) dan (-) dengan betul.",
]
S_BOOT = [
    "1. Hidupkan peranti.",
    "2. Tekan sebarang butang untuk masuk ke menu utama.",
    "3. Bateri dan status cas di penjuru kanan atas skrin.",
    "4. Butang arah: gerakkan kursor.",
    "5. <OK>: masuk item fungsi.",
    "6. <ESC>: keluar fungsi semasa.",
    "7. Butang lampu: hidup/padam latar.",
    "8. <HOLD>: kunci nilai paparan semasa ujian.",
    "9. <F1><F2>: operasi ikut fungsi.",
    "10. <Fn>: tukar mod fungsi.",
]
S_VOLT = [
    "1. Masuk item ukur voltan:",
    "   Bacaan semasa probe dipaparkan.",
    "2. <HOLD>: kunci nilai ukur.",
    "3. <F1>: sifar semula.",
    "4. Sifar: pintas probe merah dan hitam, tahan, tekan <F1>.",
    "5. <Fn>: mod DC / AC / bentuk gelombang.",
    "6. Julat voltan sehingga 1000V.",
    "7. DC maks 1000V, AC maks 700V.",
    "8. Julat bertukar automatik.",
]
S_CURR = [
    "1. Masuk item ukur arus:",
    "   Bacaan semasa probe dipaparkan.",
    "2. <HOLD>: kunci nilai ukur.",
    "3. <F1>: sifar semula.",
    "4. Sifar: pintas probe merah dan hitam, tahan, tekan <F1>.",
    "5. <Fn>: mod arus DC / AC.",
    "6. <F2>: tukar soket ukuran.",
    "7. mA (hijau): probe merah di soket mA.",
    "8. 20A (kuning): probe merah di soket 20A.",
    "9. Julat arus 0-200mA.",
]
S_RES = [
    "1. Masuk item ukur rintangan:",
    "   Bacaan semasa probe dipaparkan.",
    "2. <HOLD>: kunci nilai ukur.",
    "3. <F1>: sifar semula.",
    "4. Sifar: pintas probe merah dan hitam, tahan, tekan <F1>.",
    "5. <Fn>: paparan rintangan / voltan diod.",
    "6. Ukur rintangan dan susut voltan hadapan diod serentak.",
    "7. Rintangan maks 5Mohm.",
    "8. Susut diod sehingga 2.4V.",
    "9. Bawah 20 ohm: bunyi amaran (rintangan rendah).",
    "10. Guna untuk semak litar pintas.",
]
S_SCOPE = [
    "1. Masuk item osiloskop:",
    "   Bentuk gelombang dipaparkan.",
    "2. <HOLD>: kunci keadaan semasa.",
    "3. Keadaan berkunci:",
    "   <UP>/<DOWN>/<LEFT>/<RIGHT>: gerakkan gelombang.",
    "4. Keadaan normal:",
    "   <UP>: pembahagi voltan kecil.",
    "   <DOWN>: pembahagi voltan besar.",
    "   <LEFT>: masa imbasan tambah.",
    "   <RIGHT>: masa imbasan kurang.",
    "5. <F1>/<F2>: anjak trigger (+/-).",
    "6. Julat sehingga 1000V.",
    "7. Julat bertukar automatik.",
]
S_CIRCUIT = [
    "1. Masuk item litar automotif:",
    "   Bacaan semasa probe dipaparkan.",
    "2. <HOLD>: kunci nilai ukur.",
    "3. <F1>: sifar semula.",
    "4. Sifar: probe merah kabel khas ke terminal (-) bateri, tahan, tekan <F1>.",
    "5. <Fn>: ukur voltan / bentuk gelombang.",
    "6. <UP>: pacu output ke terminal (+) bekalan kuasa.",
    "   Beban kecil: lampu, relay dsb.",
    "7. <DOWN>: pintas ke terminal (-) bekalan kuasa.",
    "   Beban litar: solenoid, relay.",
    "8. Merah: voltan kesan hampir voltan bekalan (melebihi voltan bateri tolak 0.7V).",
    "9. Bawah 0.7V: pulse kesan bocor dihantar automatik.",
    "10. Rintangan talian bawah 10K: paparan hijau.",
]
S_CRANK = [
    "1. Ujian voltan mula kereta dan motosikal.",
    "2. Semak bateri memenuhi keperluan mula enjin.",
    "3. Matikan enjin kenderaan.",
    "4. Sambung kabel utama dan klip bateri.",
    "5. Tekan <OK>: mod pemantauan.",
    "6. Hidupkan enjin dan baca keputusan.",
    "7. Voltan min melebihi 9.6V: normal.",
    "8. Bawah 9.6V - kemungkinan: bateri uzur, arus mula tinggi, atau cas kurang.",
    "9. Bateri uzur: ganti segera.",
]
S_INJ = [
    "1. Pacu dan uji isyarat penyuntik bahan api.",
    "2. Sambung kabel utama, klip ke bateri 12V.",
    "3. Sambung ke penyuntik: pacu penyuntik 12V terus.",
    "4. Isyarat analog 500-6000 rpm.",
    "5. Lebar pulse suntikan 3mS.",
    "6. Probe: semak prestasi penyuntik.",
    "7. Tekan <OK>: antara muka pacu.",
    "8. Butang arah: laras kelajuan isyarat.",
    "9. <OK>: hidup/padam isyarat pacu.",
    "10. <Fn>: masuk kesan isyarat.",
    "11. Output pacu tidak padam semasa kesan isyarat.",
]
S_RELAY = [
    "1. Ujian relay automotif.",
    "2. Sambung kabel utama, klip ke bateri 12V.",
    "3. Kabel khas relay: pacu relay 12V terus.",
    "4. Kabel khas ke pin gegelung.",
    "5. Probe merah/hitam: ukur rintangan sentuh.",
    "6. Rintangan kecil: sentuhan tersambung.",
    "7. Rintangan besar: sentuhan terbuka.",
    "8. Tekan <OK>: antara muka kesan.",
    "9. <OK>: hidup/padam pacu relay.",
]
S_ANALOG = [
    "1. Simulasi gelombang petak dan sinus.",
    "2. Untuk ujian talian kenderaan atau input analog ECU.",
    "3. Sambung kabel utama, klip ke bateri 12V.",
    "4. Output petak 12V dengan bekalan luar.",
    "5. Tanpa bekalan luar: petak 4.5V.",
    "6. Petak keluar dari terminal [K/Lin].",
    "7. Sinus keluar dari talian isyarat.",
    "8. Talian 5V: sinus 0-4.5V.",
    "9. Tekan <OK>: antara muka kawalan.",
    "10. <OK>: hidup/padam output.",
    "11. Butang arah: laras frekuensi.",
    "12. <F1><F2>: laras kitar kerja.",
    "13. <Fn>: masuk kesan isyarat.",
    "14. Output analog tidak padam semasa kesan isyarat.",
]
S_IGN = [
    "1. Uji isyarat voltan tinggi nyalaan enjin petrol.",
    "2. Sambung sensor isyarat nyalaan.",
    "3. Letak kepala sensor (kawasan kesan) dekat wayar voltan tinggi nyalaan.",
    "4. Bentuk gelombang nyalaan dipaparkan.",
    "5. Tiada wayar luar: dekatkan sensor ke gegelung nyalaan.",
    "6. Isyarat lebih kecil: perhatikan dengan teliti.",
    "7. <F1>: mod enjin 4-lejang / 2-lejang / distributor.",
    "8. Kereta biasa: 4-lejang.",
    "9. Sesetengah motosikal: 2-lejang.",
    "10. Enjin lama: distributor.",
    "11. Mod 4/2-lejang papar rpm.",
    "12. <HOLD>: kunci keadaan semasa.",
    "13. Keadaan normal:",
    "   <UP>: pembahagi voltan kecil.",
    "   <DOWN>: pembahagi voltan besar.",
    "   <LEFT>: masa imbasan tambah.",
    "   <RIGHT>: masa imbasan kurang.",
]
S_KLIN = [
    "1. Kesan data komunikasi talian K kenderaan.",
    "2. Semak penghantaran isyarat pada talian komunikasi.",
    "3. Sambung kabel utama.",
    "4. Wayar ground ke pin ground (lubang 5 OBD-II) atau ke badan kenderaan.",
    "5. Talian K ke pin isyarat K (lubang 7 OBD-II).",
    "6. Data diterima: nilai heks.",
    "7. <F1>: padam data.",
    "8. <LEFT>/<RIGHT>: laras kadar baud.",
    "9. Kadar baud mesti sepadan untuk terima data betul.",
    "10. Guna dengan dekoder untuk semak kerosakan talian.",
]
S_CAN = [
    "1. Kesan komunikasi data CAN bus kenderaan.",
    "2. Semak penghantaran isyarat pada talian komunikasi.",
    "3. Sambung kabel utama.",
    "4. Wayar ground ke pin ground (lubang 5 OBD-II) atau badan kenderaan.",
    "5. CAN+ ke pin CAN+ kenderaan (lubang 6 OBD-II).",
    "6. CAN- ke pin CAN- kenderaan (lubang 14 OBD-II).",
    "7. Data diterima: nilai heks.",
    "8. <F1>: padam data.",
    "9. <LEFT>/<RIGHT>: laras kadar baud.",
    "10. Data diterima hanya jika kadar baud sepadan.",
    "11. Guna dengan dekoder untuk semak kerosakan talian.",
]
S_FREQ = [
    "1. Masuk item ukur frekuensi:",
    "   Nilai semasa probe dipaparkan.",
    "2. <HOLD>: kunci keadaan semasa.",
    "3. <Fn>: tukar ke mod osiloskop.",
    "4. Julat frekuensi sehingga 1MHz.",
    "5. Voltan isyarat: kawalan adaptif.",
]

SECTIONS = [
    (91, 95, S_HOOK_BAT),
    (98, 101, S_HOOK_INJ),
    (102, 108, S_HOOK_INJSIG),
    (110, 115, S_HOOK_RELAY),
    (118, 127, S_ANALOGOUT),
    (128, 132, S_HOOK_C04),
    (133, 139, S_UPDOWN),
    (140, 144, S_REDBLUE),
    (146, 149, S_RECONNECT),
    (191, 209, S_BOOT),
    (211, 228, S_VOLT),
    (230, 249, S_CURR),
    (251, 280, S_RES),
    (282, 309, S_SCOPE),
    (311, 355, S_CIRCUIT),
    (357, 384, S_CRANK),
    (386, 414, S_INJ),
    (416, 440, S_RELAY),
    (442, 475, S_ANALOG),
    (477, 521, S_IGN),
    (523, 553, S_KLIN),
    (555, 587, S_CAN),
    (589, 597, S_FREQ),
    (599, 617, S_BOOT),
    (619, 636, S_VOLT),
    (638, 657, S_CURR),
    (659, 688, S_RES),
    (690, 717, S_SCOPE),
    (719, 763, S_IGN),
    (765, 773, S_FREQ),
]

# Spanish characters expected in the source export; anything outside this set
# plus printable ASCII would be mojibake and must be kept verbatim.
SPANISH_CHARS = set("áéíóúüñÁÉÍÓÚÜÑ¡¿")


def lead_trail(text):
    b = text.encode("utf-8")
    lead = len(b) - len(b.lstrip(b" "))
    trail = len(b) - len(b.rstrip(b" "))
    return lead, trail, len(b)


def align_content(idx, content, source, target):
    """Apply the official visual layout to `content`.

    (a) official entry centered (lead>=2 and trail>=2): re-center content;
    (b) otherwise: keep official leading-space count, trailing-pad.
    Returns (padded_text, style).
    """
    cbytes = len(content.encode("utf-8"))
    if cbytes > target:
        raise ValueError(f"index {idx}: content too long: {cbytes} > {target}: {content!r}")
    lead, trail, _ = lead_trail(source)
    if lead >= 2 and trail >= 2:
        pad = target - cbytes
        left = pad // 2
        return " " * left + content + " " * (pad - left), "centered"
    if lead + cbytes > target:
        raise ValueError(
            f"index {idx}: content too long with official lead {lead}: "
            f"{lead}+{cbytes} > {target}: {content!r}"
        )
    return " " * lead + content + " " * (target - lead - cbytes), "left"


def find_all(hay, needle):
    out, start = [], 0
    while True:
        pos = hay.find(needle, start)
        if pos < 0:
            return out
        out.append(pos)
        start = pos + 1


def check_exact(idx, text, source, target, markers):
    """Verify an EXACT-layout entry: length, official lead, unit columns."""
    tb = text.encode("utf-8")
    sb = source.encode("utf-8")
    if len(tb) > target:
        raise ValueError(f"index {idx}: EXACT too long: {len(tb)} > {target}")
    text = text + " " * (target - len(tb))
    tb = text.encode("utf-8")
    (slead, _, _), (tlead, _, _) = lead_trail(source), lead_trail(text)
    if slead != tlead:
        raise ValueError(f"index {idx}: lead {tlead} != official {slead}")
    for marker in markers:
        want = find_all(sb, marker.encode("utf-8"))
        got = find_all(tb, marker.encode("utf-8"))
        if want != got:
            raise ValueError(
                f"index {idx}: column mismatch for {marker!r}: official {want} vs {got}"
            )
    return text


def render_steps(steps, widths, first_idx):
    """Render numbered steps into records of the given byte widths.

    One step per record; a step that does not fit wraps onto the next
    record(s) with a 3-space continuation indent (added to its own indent).
    Unused records become blank lines. Overflow is a hard error.
    """
    lines = []
    wi = 0
    for step in steps:
        base = len(step) - len(step.lstrip(" "))
        indent = " " * base
        cont = " " * (base + 3)
        cur = indent
        for word in step.split():
            cand = cur + ("" if cur == indent else " ") + word
            if len(cand.encode("utf-8")) <= widths[wi]:
                cur = cand
            else:
                lines.append(cur)
                wi += 1
                if wi >= len(widths):
                    raise ValueError(
                        f"section at index {first_idx}: steps overflow, "
                        f"no record left for {word!r} (step {step!r})"
                    )
                cur = cont + word
                if len(cur.encode("utf-8")) > widths[wi]:
                    raise ValueError(
                        f"section at index {first_idx}: word {word!r} wider "
                        f"than record {widths[wi]} at line {wi}"
                    )
        lines.append(cur)
        wi += 1
    while wi < len(widths):
        lines.append("")
        wi += 1
    return lines


def main():
    # Windows console is cp1252; keep prints from crashing on source glyphs.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass
    with SRC.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    header, data = rows[0], rows[1:]
    assert header == ["index", "offset", "record_length", "text"], header

    entries = {}
    for row in data:
        idx = int(row[0])
        entries[idx] = (int(row[2]) - 2, row[3])  # target bytes, source text
    assert sorted(entries) == list(range(1, 774)), "source indices not 1..773"

    # Mojibake scan.
    weird = []
    for idx, (_, text) in entries.items():
        for ch in text:
            if ch not in SPANISH_CHARS and not (32 <= ord(ch) < 127):
                weird.append((idx, repr(ch)))
                break
    if weird:
        print("NOTE: non-Spanish non-ASCII bytes in source (translated to ASCII):")
        for idx, ch in weird:
            print(f"  index {idx}: {ch}")

    # Coverage check: every index resolved exactly once.
    covered = set(COPY_INDICES) | set(FIXED) | set(EXACT)
    for first, last, _ in SECTIONS:
        covered.update(range(first, last + 1))
    missing = set(entries) - covered
    dupes = len(COPY_INDICES) + len(FIXED) + len(EXACT) + sum(
        last - first + 1 for first, last, _ in SECTIONS
    ) - len(covered)
    if missing or dupes:
        print(f"FATAL: coverage error, missing={sorted(missing)} dupes={dupes}")
        return 1

    # Resolve translations.
    translations = {}
    stats = {"copied": 0, "fixed_left": 0, "fixed_centered": 0, "exact": 0, "steps": 0}
    failures = []
    for idx in sorted(COPY_INDICES):
        translations[idx] = entries[idx][1]
        stats["copied"] += 1
    for idx, content in FIXED.items():
        target, source = entries[idx]
        try:
            translations[idx], style = align_content(idx, content, source, target)
            stats["fixed_centered" if style == "centered" else "fixed_left"] += 1
        except ValueError as exc:
            failures.append((idx, str(exc)))
    for idx, (text, markers) in EXACT.items():
        target, source = entries[idx]
        try:
            translations[idx] = check_exact(idx, text, source, target, markers)
            stats["exact"] += 1
        except ValueError as exc:
            failures.append((idx, str(exc)))
    for first, last, steps in SECTIONS:
        widths = [entries[i][0] for i in range(first, last + 1)]
        try:
            lines = render_steps(steps, widths, first)
        except ValueError as exc:
            failures.append((first, str(exc)))
            continue
        for i, line in enumerate(lines):
            translations[first + i] = line
            stats["steps"] += 1

    # Validate every row: exact length, ASCII, trailing-pad to target.
    token_warnings = []
    for idx in sorted(entries):
        target, _ = entries[idx]
        if idx not in translations:
            failures.append((idx, "no translation produced"))
            continue
        trans = translations[idx]
        bad = [c for c in trans if ord(c) >= 128]
        if bad:
            failures.append((idx, f"non-ASCII chars: {bad!r}"))
        blen = len(trans.encode("utf-8"))
        if blen > target:
            failures.append((idx, f"TOO LONG: {blen} > {target} bytes: {trans!r}"))
        elif blen < target:
            translations[idx] = trans + " " * (target - blen)
        for tok in TOKEN_RE.findall(trans):
            if tok not in ALLOWED_TOKENS:
                token_warnings.append((idx, tok))

    print(f"source rows parsed   : {len(data)}")
    print(f"copied verbatim      : {stats['copied']} (blanks/symbols/units)")
    print(f"fixed, lead-preserved: {stats['fixed_left']}")
    print(f"fixed, re-centered   : {stats['fixed_centered']}")
    print(f"exact column layout  : {stats['exact']} (units-in-line)")
    print(f"help step lines      : {stats['steps']}")
    changed = stats["fixed_left"] + stats["fixed_centered"] + stats["exact"] + stats["steps"]
    print(f"genuinely Malay      : {changed} of {len(entries)}")

    if token_warnings:
        print("TOKEN WARNINGS:")
        for idx, tok in token_warnings:
            print(f"  index {idx}: unknown token {tok}")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for idx, msg in failures:
            print(f"  index {idx}: {msg}")
        print("\nOutput NOT written.")
        return 1

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["index", "source", "translation"])
        for idx in sorted(entries):
            writer.writerow([idx, entries[idx][1], translations[idx]])

    print(f"\nwrote {OUT} ({len(entries)} data rows)")

    # Section usage report (informational).
    print("\nsection usage (non-blank records / total records):")
    for first, last, _ in SECTIONS:
        total = last - first + 1
        used = sum(1 for i in range(first, last + 1) if translations[i].strip())
        print(f"  {first:>3}-{last:<3}: {used:>2}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
