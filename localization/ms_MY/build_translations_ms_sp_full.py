#!/usr/bin/env python3
"""Build localization/ms_MY/translations_ms_sp_full.csv.

Reads analysis/sp_entries_source.csv (773 entries exported from the official
TEXT_SP.DAT) and emits a Malay translation for every entry. Hard guarantees,
checked for every row before the output file is written:

  * translation is pure ASCII (device font has no accented glyphs)
  * UTF-8 byte length of translation == record_length - 2 exactly
    (shorter text is padded with TRAILING spaces; longer is a hard error)
  * only known device placeholder tokens appear inside <...>
  * entries kept verbatim (blanks / pure symbols / units) still match length

Long help paragraphs are written as continuous Malay text per section and
word-wrapped into that section's fixed-size records, so reading the entries
in order yields correct continuous prose (rule 6 of the task brief).

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
# Entries copied verbatim from the source (blank spacer lines, pure
# symbols/units, and words that are identical in Malay).
# ---------------------------------------------------------------------------
COPY_INDICES = {18, 19, 40, 85, 86, 166, 90, 96, 97, 109, 116, 117, 145, 150}

# ---------------------------------------------------------------------------
# Fixed (single-record) translations. Strings here are NOT pre-padded; the
# builder pads with trailing spaces to the record size. Aligned layouts are
# built with explicit space runs so column positions match the originals.
# ---------------------------------------------------------------------------
FIXED = {
    1: "Memuat ...",
    2: "Tekan butang untuk teruskan",
    3: "Hidupkan",
    4: " Matikan",
    5: "Manual pengguna",
    6: "Maklumat versi",
    7: "Hardware: ",
    8: "Software: ",
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
    22: "   Min:" + " " * 7 + "V" + " " * 5 + "Maks:" + " " * 6 + "V" + " " * 3,
    23: " <HOLD> Tahan  <F1>Sifar semula",
    24: " <Fn> Mod fungsi",
    25: "Rint. PD",
    26: "Tahan",
    27: "Arus AC",
    28: "Arus DC",
    29: "20A(kuning)",
    30: " mA(hijau)   ",
    31: "   Min:" + " " * 7 + "A" + " " * 5 + "Maks:" + " " * 6 + "A" + " " * 3,
    32: " <HOLD>Tahan   <F1>Sifar semula",
    33: " <Fn>Mod fungsi   <F2> 20A/mA",
    34: "Rintangan",
    35: " Diod:",
    36: "Diod/Rintangan rendah",
    37: "Rintangan:",
    38: " <HOLD>Tahan  <F1>Sifar semula",
    39: "Trig.",
    41: "U:" + " " * 6 + "V Min:" + " " * 6 + "V Maks:" + " " * 5 + "V",
    42: "Ukur frekuensi",
    43: "<Fn> Kesan isyarat masukan (f<6k)",
    44: "rpm",
    45: "<Fn>Kesan isyarat masukan",
    46: "Rintangan sentuh:",
    47: "Output gelombang sinus/petak",
    48: "Frekuensi:" + " " * 14 + "Hz",
    49: "Kitar kerja:" + " " * 12 + "% ",
    50: "<F1><F2>Tetap kitar kerja",
    51: "Sensor:" + " " * 3 + "Min:" + " " * 6 + "V Maks:" + " " * 5 + "V",
    52: "rpm 2 lejang",
    53: "rpm 4 lejang",
    54: "Distributor",
    55: "Data K/Lin:",
    56: "<F1>Padam <L><R>laras baud",
    57: "Data CANBUS:",
    58: "<F1>Padam <L><R>laras baud",
    59: " <Fn> Mod fungsi",
    60: "Tetapan kalendar/masa",
    61: "Tetapan sistem",
    62: "Tetapan asas",
    63: "Tetapan masa",
    64: "Bahasa ",
    65: "Bunyi butang",
    66: "Cerah",
    67: "Tentukur voltan probe",
    68: "Sambung probe ke bateri!",
    69: " <UP> <Down> Laras nilai sebenar",
    70: " <ESC> Keluar" + " " * 9 + "<OK> Simpan ",
    71: "Masa tidur",
    72: " min ",
    73: "Tekan <OK> untuk teruskan",
    74: "Voltan bekalan:" + " " * 17 + "V",
    75: "<UP>Pintas B+  <DOWN>Pintas B-",
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
# Continuous Malay text for multi-record sections. Each tuple is
# (first_index, last_index, text); the builder word-wraps the text into the
# record lengths of that index range, reflowing across chunk boundaries.
# ---------------------------------------------------------------------------
S_BOOT = (
    "Hidupkan peranti, skrin mula dipaparkan; tekan sebarang butang untuk "
    "masuk ke menu utama. Penjuru kanan atas skrin memaparkan bateri dan "
    "status pengecasan. Tekan butang arah untuk menggerakkan kursor, tekan "
    "<OK> untuk masuk ke item fungsi, tekan <ESC> untuk keluar dari fungsi "
    "semasa. Tekan butang lampu untuk hidup atau padam lampu latar, tekan "
    "<HOLD> untuk mengunci nilai paparan semasa ujian, tekan <F1><F2> untuk "
    "beroperasi mengikut fungsi, dan tekan <Fn> untuk menukar mod fungsi "
    "dalam item fungsi."
)
S_VOLT = (
    "Masuk ke item fungsi ukur voltan; nilai ukur semasa probe dipaparkan. "
    "Tekan <HOLD> untuk mengunci nilai ukur, tekan <F1> untuk sifar semula "
    "dan pembetulan. Semasa guna, pintaskan dahulu probe merah dan hitam, "
    "tahan, kemudian tekan <F1> sekali lagi. Tekan <Fn> untuk menukar mod "
    "fungsi: paparan voltan DC / voltan AC / bentuk gelombang. Julat ukur "
    "voltan sehingga 1000V, voltan DC maksimum 1000V, voltan AC maksimum "
    "700V, dan julat bertukar secara automatik."
)
S_CURR = (
    "Masuk ke item fungsi ukur arus; bacaan semasa probe dipaparkan. Tekan "
    "<HOLD> untuk mengunci nilai ukur, tekan <F1> untuk sifar semula dan "
    "pembetulan. Semasa guna, pintaskan dahulu probe merah dan hitam, tahan, "
    "kemudian tekan <F1> sekali lagi. Tekan <Fn> untuk menukar mod fungsi: "
    "arus DC / arus AC. Tekan <F2> untuk menukar soket ukuran: mA (hijau) "
    "bermaksud probe merah dimasukkan dari soket mA untuk mengukur, dan 20A "
    "(kuning) bermaksud probe merah dimasukkan dari soket 20A untuk mengukur. "
    "Julat ukur arus ialah 0-200mA."
)
S_RES = (
    "Masuk ke item fungsi ukur rintangan; bacaan semasa probe dipaparkan. "
    "Tekan <HOLD> untuk mengunci nilai ukur, tekan <F1> untuk sifar semula "
    "dan pembetulan. Semasa guna, pintaskan dahulu probe merah dan hitam, "
    "tahan, kemudian tekan <F1> sekali lagi. Tekan <Fn> untuk menukar mod "
    "fungsi: paparan rintangan / paparan voltan diod. Fungsi ini mengukur "
    "nilai rintangan dan susut voltan hadapan diod serentak tanpa penukaran. "
    "Julat ukur rintangan sehingga nilai maksimum 5Mohm, dan julat bertukar "
    "secara automatik. Susut voltan hadapan diod sehingga 2.4V. Apabila "
    "rintangan yang diukur kurang daripada 20 ohm, bunyi amaran akan berbunyi "
    "untuk menandakan keadaan rintangan rendah, memudahkan menentukan sama "
    "ada talian berada dalam litar pintas semasa pemeriksaan litar."
)
S_SCOPE = (
    "Masuk ke item fungsi osiloskop; bentuk gelombang nilai ukur semasa probe "
    "dipaparkan. Tekan <HOLD> untuk mengunci keadaan semasa. Dalam keadaan "
    "ukur berkunci: tekan <UP> untuk menggerakkan bentuk gelombang ke atas, "
    "tekan <DOWN> ke bawah, tekan <LEFT> ke kiri, tekan <RIGHT> ke kanan. "
    "Dalam keadaan ukur normal: <UP> nilai pembahagi paparan voltan "
    "berkurang, <DOWN> nilai pembahagi paparan voltan bertambah, <LEFT> masa "
    "imbasan bertambah, <RIGHT> masa imbasan berkurang. <F1> anjakan positif "
    "aras trigger, <F2> anjakan negatif aras trigger. Julat ukur bentuk "
    "gelombang voltan sehingga 1000V, dan julat bertukar secara automatik."
)
S_CIRCUIT = (
    "Masuk ke item fungsi litar automotif; nilai ukur semasa probe "
    "dipaparkan. Tekan <HOLD> untuk mengunci nilai ukur, tekan <F1> untuk "
    "sifar semula dan pembetulan. Semasa guna, sambungkan dahulu probe merah "
    "kabel khas ke terminal negatif bateri, tahan, kemudian tekan <F1> "
    "sekali lagi. Tekan <Fn> untuk menukar mod fungsi: ukur voltan / paparan "
    "bentuk gelombang. <UP> ialah fungsi pacu output voltan: selepas "
    "ditekan, ia setara dengan probe merah disambung ke terminal positif "
    "bekalan kuasa, digunakan untuk memacu peranti kuasa rendah pada "
    "kenderaan yang bekerja dengan voltan bekalan, seperti lampu, relay dan "
    "sebagainya. <DOWN> ialah fungsi pintas ke terminal negatif bekalan "
    "kuasa: selepas ditekan, ia setara dengan probe merah disambung ke "
    "terminal negatif bekalan kuasa, digunakan untuk memacu peranti kuasa "
    "rendah yang kerap dibekalkan dalam litar, seperti injap solenoid, relay "
    "dan sebagainya. Pada antara muka paparan, apabila voltan kesan hampir "
    "dengan voltan bekalan kuasa (melebihi nilai voltan sebenar bateri tolak "
    "0.7), ia ditunjukkan dalam warna merah. Apabila voltan kesan kurang "
    "daripada 0.7V, pulse kesan bocor dihantar secara automatik; apabila "
    "rintangan talian kurang daripada 10K, ia ditunjukkan dalam warna hijau."
)
S_CRANK = (
    "Fungsi ini sesuai untuk ujian voltan mula kereta dan motosikal, untuk "
    "mengesan sama ada keadaan bateri kenderaan memenuhi keperluan mula. "
    "Masuk ke item fungsi ini, matikan enjin kenderaan mengikut maklumat "
    "yang ditunjukkan, sambung kabel kesan utama dan klip bateri, tekan "
    "butang <OK> untuk masuk keadaan pemantauan, hidupkan enjin kenderaan "
    "mengikut arahan, dan keputusan ujian dipaparkan mengikut nilai diukur. "
    "Apabila voltan minimum semasa proses mula kenderaan melebihi 9.6V, ia "
    "ialah keadaan normal; di bawah nilai ini, tentukan punca kerosakan: "
    "kemungkinan bateri uzur, arus mula terlalu besar, atau cas bateri tidak "
    "mencukupi. Jika bateri sudah uzur, bateri mesti diganti segera."
)
S_INJ = (
    "Fungsi ini sesuai untuk pacu isyarat penyuntik dan ujian isyarat. "
    "Sambung kabel kesan utama, gunakan klip bateri untuk sambung ke bekalan "
    "kuasa bateri 12V, kemudian sambung ke penyuntik; ia boleh memacu "
    "penyuntik 12V terus bekerja. Ia boleh memberi isyarat kerja analog "
    "penyuntik antara 500 hingga 6000 rpm, dan lebar pulse suntikan ialah "
    "3mS. Gunakan probe untuk menyemak prestasi penyuntik. Masuk ke item "
    "fungsi; maklumat arahan dipaparkan, tekan butang <OK> untuk masuk "
    "antara muka pacu isyarat, tekan butang arah untuk melaras kelajuan "
    "isyarat analog, tekan butang <OK> untuk hidup atau padam isyarat pacu "
    "analog, dan tekan butang <Fn> untuk masuk kesan isyarat. Output isyarat "
    "pacu tidak dipadam semasa masuk kesan isyarat."
)
S_RELAY = (
    "Fungsi ini sesuai untuk ujian relay automotif: sambung kabel kesan "
    "utama, gunakan klip bateri untuk sambung ke bekalan kuasa bateri 12V, "
    "kemudian sambung kabel khas relay; ia boleh memacu relay 12V terus "
    "beroperasi. Gunakan kabel khas relay untuk sambung ke pin gegelung "
    "relay, dan gunakan probe merah dan hitam untuk mengesan rintangan "
    "sentuh relay. Rintangan kecil bermaksud sentuhan tersambung, rintangan "
    "besar bermaksud sentuhan terbuka. Masuk ke item fungsi; maklumat arahan "
    "dipaparkan, tekan butang <OK> untuk masuk antara muka kesan, tekan "
    "butang <OK> untuk hidup atau padam isyarat pacu relay, dan gunakan "
    "probe untuk mengukur rintangan sentuh."
)
S_ANALOG = (
    "Fungsi ini boleh mensimulasi output gelombang petak dan gelombang "
    "sinus, sesuai untuk kesan talian kenderaan atau ujian input isyarat "
    "analog ECU. Sambung kabel kesan utama, gunakan klip bateri untuk "
    "sambung ke bekalan kuasa bateri 12V; ia boleh mengeluarkan isyarat "
    "gelombang petak 12V. Tanpa bekalan kuasa luar, ia boleh mengeluarkan "
    "isyarat gelombang petak 4.5V. Isyarat gelombang petak dikeluarkan dari "
    "terminal [K/Lin], isyarat gelombang sinus dikeluarkan dari talian "
    "isyarat, dan talian isyarat 5V mengeluarkan gelombang sinus 0-4.5V. "
    "Masuk ke item fungsi; maklumat arahan dipaparkan, tekan butang <OK> "
    "untuk masuk antara muka kawalan, tekan butang <OK> untuk hidup atau "
    "padam output isyarat, tekan butang arah untuk melaras frekuensi isyarat "
    "analog, tekan <F1><F2> untuk melaras kitar kerja gelombang petak, dan "
    "tekan butang <Fn> untuk masuk kesan isyarat. Output isyarat analog "
    "tidak dipadam semasa masuk kesan isyarat."
)
S_IGN = (
    "Fungsi ini sesuai untuk ujian isyarat voltan tinggi nyalaan enjin "
    "petrol kereta dan motosikal, dan mengesan isyarat voltan tinggi nyalaan "
    "kenderaan. Sambung sensor isyarat nyalaan, masuk ke antara muka ujian, "
    "dan letakkan kepala sensor (kawasan kesan isyarat) berhampiran wayar "
    "voltan tinggi isyarat nyalaan kenderaan untuk memaparkan bentuk "
    "gelombang isyarat nyalaan. Jika kenderaan dinyalakan terus dan tiada "
    "wayar voltan tinggi luar, kepala sensor boleh diletakkan berhampiran "
    "gegelung voltan tinggi nyalaan, yang juga boleh memaparkan bentuk "
    "gelombang isyarat nyalaan; pada masa ini kekuatan isyarat agak kecil, "
    "perhatikan dengan teliti. Tekan butang <F1> untuk menukar mod enjin: "
    "boleh tukar ke mod 4 lejang / 2 lejang / distributor. Enjin kereta "
    "biasa ialah 4 lejang, sesetengah enjin motosikal ialah 2 lejang, dan "
    "enjin lama menggunakan distributor untuk mengagihkan isyarat voltan "
    "tinggi. Dalam mod 4 lejang / 2 lejang, kelajuan enjin boleh dipaparkan. "
    "Tekan <HOLD> untuk mengunci keadaan semasa. Dalam keadaan ukur normal: "
    "<UP> nilai pembahagi paparan voltan berkurang, <DOWN> nilai pembahagi "
    "paparan voltan bertambah, <LEFT> masa imbasan bertambah, <RIGHT> masa "
    "imbasan berkurang."
)
S_KLIN = (
    "Fungsi ini boleh mengesan data komunikasi talian K kenderaan, sesuai "
    "untuk mengesan sama ada talian komunikasi kenderaan mempunyai "
    "penghantaran isyarat. Sambung kabel kesan utama, sambung wayar ground "
    "isyarat ke pin ground kenderaan (seperti lubang No.5 OBD-II), atau "
    "sambung ke badan kenderaan apabila sukar dicapai, dan sambung talian "
    "isyarat talian K ke pin isyarat talian K kenderaan (seperti lubang No.7 "
    "OBD-II). Masuk ke item fungsi untuk memaparkan data yang sedang "
    "diterima sebagai nilai heks. Tekan <F1> untuk memadam data dipaparkan, "
    "tekan butang arah <LEFT> dan <RIGHT> untuk melaras kadar baud "
    "komunikasi; kadar baud isyarat mesti sepadan dengan kadar baud yang "
    "ditetapkan untuk menerima data yang betul. Fungsi ini boleh digunakan "
    "bersama dekoder profesional untuk menyemak kerosakan talian komunikasi."
)
S_CAN = (
    "Fungsi ini boleh mengesan komunikasi data CAN bus kenderaan, sesuai "
    "untuk mengesan sama ada talian komunikasi kenderaan mempunyai "
    "penghantaran isyarat. Sambung kabel kesan utama, sambung wayar ground "
    "isyarat ke pin ground kenderaan (seperti lubang No.5 OBD-II), sambung "
    "ke badan kenderaan apabila sukar dicapai, sambung talian isyarat CAN+ "
    "ke pin isyarat CAN+ kenderaan (seperti lubang No.6 OBD-II), dan sambung "
    "talian isyarat CAN- ke pin isyarat CAN- kenderaan (seperti lubang No.14 "
    "OBD-II). Masuk ke item fungsi untuk memaparkan data yang sedang "
    "diterima sebagai nilai heks. Tekan <F1> untuk memadam data dipaparkan, "
    "tekan butang arah <LEFT> dan <RIGHT> untuk melaras kadar baud "
    "komunikasi; data hanya dapat diterima apabila kadar baud isyarat "
    "sepadan dengan kadar baud yang ditetapkan. Fungsi ini boleh digunakan "
    "bersama dekoder profesional untuk menyemak kerosakan talian komunikasi."
)
S_FREQ = (
    "Masuk ke item fungsi ukur frekuensi; nilai ukur semasa probe "
    "dipaparkan. Tekan <HOLD> untuk mengunci keadaan semasa, tekan <Fn> "
    "untuk tukar ke mod osiloskop. Julat ukur frekuensi sehingga 1MHz, dan "
    "voltan isyarat dikawal secara adaptif."
)

SECTIONS = [
    (91, 95,
     "Matikan enjin dahulu, pilih kabel C01 + kabel C02 untuk sambung ke "
     "terminal positif dan negatif bateri kenderaan."),
    (98, 101,
     "Pacu penyuntik: pilih kabel C01 untuk sambung ke penyuntik, kemudian "
     "sambung bateri kenderaan."),
    (102, 108,
     "Kesan isyarat suntikan bahan api: sambung probe hitam ke badan "
     "kenderaan, probe merah ke pin penyuntik, kemudian tekan butang <Fn> "
     "untuk masuk ujian."),
    (110, 115,
     "Pacu gegelung relay: pilih kabel C01 untuk sambung ke relay, kemudian "
     "sambung bateri kenderaan dan tekan <OK> untuk memacu tindakan relay."),
    (118, 127,
     "Output isyarat analog: gelombang petak keluar dari kabel C01-K, voltan "
     "isyarat output biasa sekitar 4.5V, frekuensi output maksimum 10KHz. "
     "Apabila bawah 5KHz, probe boleh digunakan untuk mengesan bentuk "
     "gelombang isyarat; tekan butang <Fn> untuk mengesan isyarat."),
    (128, 132,
     "Pilih kabel khas C04 untuk mengesan litar automotif dan sambung "
     "terminal positif dan negatif bateri kenderaan dengan betul."),
    (133, 139,
     "Pada antara muka paparan voltan, tekan butang <UP> untuk output "
     "terminal positif bateri, dan tekan butang <DOWN> untuk output terminal "
     "negatif bateri."),
    (140, 144,
     "Merah bermaksud voltan probe hampir voltan bateri; biru bermaksud "
     "voltan probe terlalu rendah dan ada kebocoran."),
    (146, 149,
     "Cabut bekalan kuasa dan sambung semula terminal positif dan negatif "
     "dengan betul."),
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
# plus printable ASCII would be mojibake and must be kept verbatim (rule 9).
SPANISH_CHARS = set("áéíóúüñÁÉÍÓÚÜÑ¡¿")


def wrap_text(text, widths, first_idx):
    """Greedy word-wrap `text` into records of the given byte widths."""
    words = text.split()
    lines = []
    for pos, width in enumerate(widths):
        line = ""
        while words:
            cand = words[0] if not line else line + " " + words[0]
            if len(cand.encode("utf-8")) <= width:
                line = cand
                words.pop(0)
            else:
                break
        if not line and words:
            raise ValueError(
                f"word longer than record at index {first_idx + pos}: "
                f"{words[0]!r} > {width} bytes"
            )
        lines.append(line)
    if words:
        raise ValueError(
            f"section at index {first_idx}: text overflows, "
            f"{len(' '.join(words))} bytes left over: {' '.join(words)!r}"
        )
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
        rec_len = int(row[2])
        text = row[3]
        entries[idx] = (rec_len - 2, text)  # target byte length, source text

    assert sorted(entries) == list(range(1, 774)), "source indices not 1..773"

    # Mojibake scan (rule 9).
    weird = []
    for idx, (_, text) in entries.items():
        for ch in text:
            if ch not in SPANISH_CHARS and not (32 <= ord(ch) < 127):
                weird.append((idx, repr(ch)))
                break
    if weird:
        print("WARNING: non-Spanish non-ASCII bytes in source (kept verbatim):")
        for idx, ch in weird:
            print(f"  index {idx}: {ch}")

    # Coverage check: every index resolved exactly once.
    covered = set(COPY_INDICES) | set(FIXED)
    for first, last, _ in SECTIONS:
        covered.update(range(first, last + 1))
    missing = set(entries) - covered
    dupes = len(COPY_INDICES) + len(FIXED) + sum(
        last - first + 1 for first, last, _ in SECTIONS
    ) - len(covered)
    if missing or dupes:
        print(f"FATAL: coverage error, missing={sorted(missing)} dupes={dupes}")
        return 1

    # Resolve translations.
    translations = {}
    stats = {"copied": 0, "fixed": 0, "wrapped": 0}
    for idx in sorted(COPY_INDICES):
        translations[idx] = entries[idx][1]
        stats["copied"] += 1
    for idx, text in FIXED.items():
        translations[idx] = text
        stats["fixed"] += 1
    for first, last, text in SECTIONS:
        widths = [entries[i][0] for i in range(first, last + 1)]
        lines = wrap_text(text, widths, first)
        for i, line in enumerate(lines):
            translations[first + i] = line
            stats["wrapped"] += 1

    # Validate every row.
    failures = []
    token_warnings = []
    for idx in sorted(entries):
        target, _source = entries[idx]
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

    print(f"source rows parsed : {len(data)}")
    print(f"entries copied     : {stats['copied']} (blanks/symbols/units, unchanged)")
    print(f"entries fixed      : {stats['fixed']} (single-record translations)")
    print(f"entries wrapped    : {stats['wrapped']} (help paragraphs, reflowed)")
    print(f"genuinely Malay    : {stats['fixed'] + stats['wrapped']} of {len(entries)}")

    if token_warnings:
        print("TOKEN WARNINGS:")
        for idx, tok in token_warnings:
            print(f"  index {idx}: unknown token {tok}")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for idx, msg in failures:
            print(f"  index {idx}: {msg}")
        print("\nOutput NOT written. Shorten the flagged translations.")
        return 1

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["index", "source", "translation"])
        for idx in sorted(entries):
            writer.writerow([idx, entries[idx][1], translations[idx]])

    print(f"\nwrote {OUT} ({len(entries)} data rows)")

    # Section fill report (informational).
    print("\nsection fill (bytes used / capacity):")
    for first, last, _ in SECTIONS:
        cap = sum(entries[i][0] for i in range(first, last + 1))
        used = sum(
            len(translations[i].rstrip().encode("utf-8"))
            for i in range(first, last + 1)
        )
        print(f"  {first:>3}-{last:<3}: {used:>4}/{cap:<4} ({100 * used / cap:.0f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
