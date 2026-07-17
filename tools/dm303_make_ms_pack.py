#!/usr/bin/env python3
"""Build a Malay (ms-MY) UI text resource for DM303.

The generated resource is reviewed in localization/ms_MY and then copied into
the staging/final packages by the firmware build workflow.
"""

from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

from dm303_text_resource import parse_text_dat, rebuild, sha256


DEFAULT_SOURCE = Path("backup/DM303 V4.0-read only/system/TEXT_EN.DAT")
DEFAULT_OUTPUT_DIR = Path("localization/ms_MY")


STATIC_TRANSLATIONS: dict[int, str] = {
    1: "Memuat......",
    2: "Tekan mana-mana butang",
    3: "ON ",
    4: "OFF",
    5: "Manual",
    6: "MAKLUMAT VERSI",
    7: "Hardware: ",
    8: "Software: ",
    9: "ID Alat:",
    10: "Tekan mana-mana butang",
    11: "Semak paparan",
    12: "Uji Butang",
    13: "Nota:papar butang ditekan.",
    14: "Tekan <ESC> dua kali untuk ",
    15: "keluar ujian.                ",
    16: "ESC keluar ",
    17: "Butang:",
    20: "Voltan(AC)",
    21: "Voltan(DC)",
    22: "   Min:       V     Maks:      V  ",
    23: " <HOLD> Tahan       <F1> Sifar    ",
    24: " <Fn> Mod Fungsi                  ",
    25: "Rint. PD ",
    26: "TAHAN",
    29: "20A(Kuning)",
    30: "mA(Hijau) ",
    31: "   Min:       A     Maks:      A  ",
    32: " <HOLD> Tahan        <F1> Sifar   ",
    33: " <Fn> Mod Fungsi   <F2> 20A/mA    ",
    34: "Rintangan ",
    35: " Diod:              ",
    36: "Diod/Rint. Rendah",
    37: " Rint.:          ",
    38: " <HOLD> Tahan       <F1> Sifar    ",
    39: "Trig.",
    40: "div",
    41: "U:      V Min:      V Maks:     V",
    42: "Ukur Frekuensi",
    43: "<Fn> kesan isyarat(f<6000)",
    45: "<Fn> ke kesan isyarat",
    46: "Rint. Sentuh:    ",
    47: "Output sinus/petak",
    48: "Frekuensi:        Hz",
    49: "Duty Cycle:       % ",
    50: "<F1><F2> Tetap Duty Cycle",
    51: "Sensor:   Min:      V Maks:     V",
    52: "rpm 2Lejang",
    53: "rpm 4Lejang",
    54: "Distributor ",
    55: "Data K/Lin: ",
    56: "<F1>Padam <Fn><LEFT><RIGHT> BPS",
    57: "Data CANBUS: ",
    58: "<F1>Padam <Fn><LEFT><RIGHT> BPS",
    59: " <Fn> Mod Fungsi     ",
    60: "Tetapan Kalendar/Masa",
    61: "Tetapan Sistem",
    62: "Tetapan Asas",
    63: "Tetapan Masa",
    64: "Bahasa ",
    65: "Bunyi",
    66: "Cerah ",
    67: "Tentukur voltan dg probe.",
    68: "Sambung probe ke bateri.",
    69: " <UP> <Down> Laras nilai sebenar",
    70: " <ESC> Keluar          <OK> SIMPAN",
    71: "Masa tidur",
    72: " min ",
    73: " Tekan <OK> untuk terus ",
    74: "Voltan Bekal:       V",
    75: " <UP>Pintas B+ <DOWN>Pintas B-",
    76: "Sambungan salah!!",
    77: "Tentukur Voltan Bateri",
    78: "Sambung bateri kenderaan!",
    79: "Tentukur arus(mA) ",
    80: "Sambung ke isyarat arus(mA)!",
    81: "Tentukur Voltan Litar Kenderaan",
    82: "Sambung ke isyarat voltan!",
    83: "Tentukur arus(A) ",
    84: "Sambung ke isyarat arus(A)!",
    87: "Huraian Fungsi",
    88: "Bocor Kunci Jauh(3V)",
    89: "Voltan:      ",
    90: "Output Isyarat Voltan",
    91: "(Terminal: C01-S1)",
    92: "(Terminal: C01-S2)",
    93: "gelombang petak:     ",
    94: "Laras Voltan:        ",
    95: "<F1><F2> Tetap Frekuensi",
    159: "PILIHAN BAHASA",
    160: "Hidupkan enjin dan",
    161: "biar 15 saat           ",
    162: "Ujian Mula",
    163: "hidupkan enjin",
    164: "Voltan min > 9.6V",
    165: "Voltan min > 19.2V",
    166: "Ujian Penyuntik",
    167: "Ujian Relay Auto",
    168: "RPM Enjin Simulasi",
    169: " Tekan <OK> output ",
    170: " Tekan <OK> henti  ",
    171: "Status Output",
    172: "Voltan masa nyata:",
    173: "Voltan Minimum:",
    174: "       Normal      ",
    175: "Voltan rendah.",
    176: "Ujian Litar Kenderaan",
    177: "1.Skrin Mula ",
    178: "2.Ukur Voltan",
    179: "3.Ukur Arus",
    180: "4.Ukur Rintangan",
    181: "5.Osiloskop",
    182: "6.Kesan litar auto",
    183: "7.Ujian cranking bateri",
    184: "8.Uji injektor",
    185: "9.Uji relay",
    186: "10.Uji isyarat analog",
    187: "11.Ujian nadi nyalaan",
    188: "12.Kesan Data K/Lin",
    189: "13.Kesan Data CAN",
    190: "14.Ukur Frekuensi",
    191: "1.Skrin Mula ",
    192: "2.Ukur Voltan",
    193: "3.Ukur Arus",
    194: "4.Ukur Rintangan",
    195: "5.Osiloskop",
    196: "6.Ujian nadi nyalaan",
    197: "7.Ukur Frekuensi",
    198: "1.Skrin Mula ",
    199: "2.Ukur Voltan",
    200: "3.Ukur Arus",
    201: "4.Ukur Rintangan",
    202: "5.Osiloskop",
    203: "6.Ujian isyarat voltan",
    204: "7.Uji isyarat analog",
    205: "1.Skrin Mula",
    536: "1.Skrin Mula",
    675: "1.Skrin Mula",
}


def set_entry(replacements: dict[int, str], lengths: dict[int, int], index: int, text: str) -> None:
    encoded = text.encode("utf-8")
    limit = lengths[index]
    if len(encoded) > limit:
        raise ValueError(f"entry {index} too long: {len(encoded)} > {limit}: {text!r}")
    replacements[index] = text


def fill_wrapped(
    replacements: dict[int, str],
    lengths: dict[int, int],
    start: int,
    end: int,
    width: int,
    text: str,
) -> None:
    lines = textwrap.wrap(
        text,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    capacity = end - start + 1
    if len(lines) > capacity:
        raise ValueError(f"text for {start}-{end} needs {len(lines)} lines, capacity {capacity}")
    lines.extend([""] * (capacity - len(lines)))
    for index, line in zip(range(start, end + 1), lines):
        set_entry(replacements, lengths, index, line.ljust(lengths[index]))


def build_translations(lengths: dict[int, int]) -> dict[int, str]:
    replacements: dict[int, str] = {}

    for index, text in STATIC_TRANSLATIONS.items():
        set_entry(replacements, lengths, index, text)

    fill_wrapped(
        replacements,
        lengths,
        97,
        100,
        32,
        "Matikan enjin dahulu, pilih kabel C01 dan C02, kemudian sambungkan kedua-dua terminal bateri kenderaan.",
    )
    fill_wrapped(
        replacements,
        lengths,
        104,
        112,
        32,
        "Pacu penyuntik bahan api: pilih kabel C01 untuk sambung ke penyuntik, kemudian sambungkan bateri kenderaan. Untuk kesan isyarat suntikan, probe hitam ke ground kenderaan dan probe merah ke pin penyuntik, lalu tekan <Fn>.",
    )
    fill_wrapped(
        replacements,
        lengths,
        114,
        118,
        32,
        "Pacu gegelung relay: pilih kabel C01 ke relay, sambungkan bateri, kemudian tekan <OK> untuk mengaktifkan relay.",
    )
    fill_wrapped(
        replacements,
        lengths,
        122,
        130,
        32,
        "Output isyarat analog: gelombang petak keluar dari talian C01-K. Voltan isyarat biasa kira-kira 4.5V dan frekuensi maksimum 10KHz. Di bawah 5KHz, probe boleh digunakan untuk menyemak bentuk gelombang; tekan <Fn> untuk semak isyarat.",
    )
    fill_wrapped(
        replacements,
        lengths,
        131,
        142,
        32,
        "Pilih kabel khas C04 untuk pemeriksaan litar automotif dan sambungkan terminal bateri dengan betul. Rujuk paparan voltan. Tekan UP untuk output positif melalui probe, dan DOWN untuk output negatif. Merah bermaksud voltan probe hampir dengan voltan bateri; biru bermaksud voltan terlalu rendah atau ada kebocoran.",
    )
    fill_wrapped(
        replacements,
        lengths,
        146,
        148,
        32,
        "Putus kuasa dan sambung semula terminal + dan - dengan betul.",
    )
    fill_wrapped(
        replacements,
        lengths,
        152,
        155,
        32,
        "Output voltan dari C01-S1. Julat 0-4.5V. Gunakan probe untuk semak gelombang. Tekan <Fn> semak isyarat.",
    )

    title = {
        219: "2.Ukur Voltan",
        234: "3.Ukur Arus",
        253: "4.Ukur Rintangan",
        278: "5.Osiloskop",
        297: "6.Kesan litar auto",
        332: "7.Ujian cranking bateri",
        356: "8.Ujian injektor",
        381: "9.Ujian relay",
        404: "10.Ujian isyarat analog",
        431: "11.Ujian nadi nyalaan",
        469: "12.Kesan Data K/Lin",
        497: "13.Kesan Data CAN",
        527: "14.Ukur Frekuensi",
        550: "2.Ukur Voltan",
        565: "3.Ukur Arus",
        584: "4.Ukur Rintangan",
        609: "5.Osiloskop",
        628: "6.Ujian nadi nyalaan",
        666: "7.Ukur Frekuensi",
        689: "2.Ukur Voltan",
        704: "3.Ukur Arus",
        723: "4.Ukur Rintangan",
        748: "5.Osiloskop",
        767: "7.Ujian isyarat analog",
        794: "6.Ujian isyarat voltan",
    }
    for index, text in title.items():
        set_entry(replacements, lengths, index, text.ljust(lengths[index]))

    common_boot = (
        "Hidupkan peranti dan tunggu skrin mula. Tekan mana-mana butang untuk "
        "masuk ke menu utama. Status bateri dan pengecasan dipaparkan di penjuru "
        "kanan atas. Gunakan butang arah untuk gerak kursor, <OK> untuk masuk "
        "fungsi, dan <ESC> untuk keluar. Butang lampu hidup/matikan lampu, "
        "<HOLD> mengunci nilai bacaan, <F1><F2> ikut arahan paparan, dan <Fn> "
        "menukar mod fungsi."
    )
    voltage = (
        "Masuk fungsi ukur voltan untuk melihat bacaan semasa. Tekan <HOLD> "
        "untuk mengunci bacaan dan <F1> untuk sifar. Semasa guna, pintaskan "
        "probe merah dan hitam, tahan, kemudian tekan <F1>. Tekan <Fn> untuk "
        "tukar mod DC/AC/bentuk gelombang. Julat voltan hingga 1000V; DC maks "
        "1000V, AC maks 700V, dan julat bertukar automatik."
    )
    current = (
        "Masuk fungsi ukur arus untuk melihat bacaan semasa. Tekan <HOLD> untuk "
        "mengunci bacaan dan <F1> untuk sifar. Pintaskan probe merah dan hitam, "
        "tahan, kemudian tekan <F1>. Tekan <Fn> untuk tukar DC/AC. Tekan <F2> "
        "untuk tukar jack ukur. mA hijau bermaksud probe merah pada jack mA; "
        "20A kuning bermaksud probe merah pada jack 20A. Julat arus 0-200mA."
    )
    resistance = (
        "Masuk fungsi ukur rintangan untuk melihat bacaan semasa. Tekan <HOLD> "
        "untuk mengunci bacaan dan <F1> untuk sifar. Pintaskan probe merah dan "
        "hitam, tahan, kemudian tekan <F1>. Tekan <Fn> untuk tukar paparan "
        "rintangan atau voltan diod. Fungsi ini mengukur rintangan dan jatuhan "
        "voltan hadapan diod tanpa penukaran manual. Rintangan maks 5MOhm dan "
        "julat bertukar automatik. Jatuhan hadapan diod maks 2.4V. Jika "
        "rintangan di bawah 20 Ohm, bunyi amaran menandakan keadaan rintangan "
        "rendah, berguna untuk memeriksa litar pintas."
    )
    oscilloscope = (
        "Masuk fungsi osiloskop untuk melihat bentuk gelombang nilai yang "
        "diukur. Tekan <HOLD> untuk kunci keadaan semasa. <UP>/<DOWN>/<LEFT>/"
        "<RIGHT> menggerakkan bentuk gelombang. Dalam keadaan normal, <UP> "
        "mengecilkan nilai pembahagi voltan, <DOWN> membesarkan nilai itu, "
        "<LEFT> menambah masa imbasan, dan <RIGHT> mengurangkan masa imbasan. "
        "<F1> mengalih aras trigger positif, <F2> negatif. Julat bentuk "
        "gelombang hingga 1000V dan julat bertukar automatik."
    )
    circuit = (
        "Masuk fungsi kesan litar automotif. Bacaan semasa dipaparkan; <HOLD> "
        "mengunci bacaan dan <F1> untuk sifar. Sambungkan probe merah ke "
        "terminal negatif bateri, tahan, kemudian tekan <F1>. Tekan <Fn> untuk "
        "tukar voltan/bentuk gelombang. <UP> memacu output voltan positif untuk "
        "beban kecil seperti lampu atau relay. <DOWN> memintas ke terminal "
        "negatif untuk memacu beban kecil seperti solenoid atau relay. Jika "
        "voltan hampir voltan bekalan, paparan memberi amaran merah. Jika "
        "voltan di bawah 0.7V, pulse kesan kebocoran dihantar. Jika rintangan "
        "talian bawah 10K, paparan memberi amaran hijau."
    )
    cranking = (
        "Fungsi ini untuk ujian cranking kereta dan motosikal, bagi menilai sama "
        "ada keadaan bateri memenuhi keperluan mula enjin. Ikut arahan, matikan "
        "enjin, sambungkan kabel utama dan klip bateri, tekan <OK> untuk masuk "
        "mod pemantauan, hidupkan enjin, kemudian baca keputusan. Voltan minimum "
        "melebihi 9.6V semasa mula adalah normal. Jika lebih rendah, semak punca "
        "seperti bateri uzur, arus starter terlalu tinggi, atau bateri tidak "
        "cukup cas. Ganti bateri jika sudah uzur. Jika kabel/klip tidak "
        "disambung, bacaan boleh terapung akibat input terbuka dan tidak boleh "
        "dianggap sebagai voltan bateri sebenar."
    )
    injector = (
        "Fungsi ini untuk pacu dan uji isyarat penyuntik bahan api. Sambungkan "
        "kabel utama, gunakan klip bateri ke bekalan 12V, kemudian sambungkan "
        "penyuntik untuk memacu penyuntik 12V terus. Ia memberi isyarat kerja "
        "simulasi 500 hingga 6000 rpm dengan lebar pulse 3mS. Gunakan probe "
        "untuk semak prestasi penyuntik. Tekan <OK> untuk masuk antara muka "
        "pacu, butang arah melaras kelajuan simulasi, <OK> hidup/matikan isyarat "
        "pacu, dan <Fn> masuk kesan isyarat. Output pacu tidak dimatikan ketika "
        "masuk kesan isyarat."
    )
    relay = (
        "Fungsi ini untuk ujian relay automotif. Sambungkan kabel utama dan klip "
        "bateri ke bekalan 12V, kemudian sambungkan kabel khas relay untuk "
        "memacu relay 12V. Gunakan kabel khas ke pin gegelung relay, dan probe "
        "merah/hitam untuk mengukur rintangan sentuh. Rintangan kecil bermaksud "
        "sentuhan tersambung; rintangan besar bermaksud terputus. Tekan <OK> "
        "untuk masuk antara muka, <OK> hidup/matikan pacu relay, dan probe "
        "mengukur rintangan sentuh."
    )
    analog = (
        "Fungsi ini mensimulasi output gelombang petak dan sinus. Ia sesuai "
        "untuk ujian talian kenderaan atau input isyarat analog ECU. Sambungkan "
        "kabel utama dan klip bateri ke bekalan 12V untuk output gelombang petak "
        "12V. Tanpa bekalan luar, ia boleh output gelombang petak 4.5V. Gelombang "
        "petak keluar dari terminal [K line], gelombang sinus dari talian isyarat, "
        "dan talian 5V mengeluarkan sinus 0-4.5V. Tekan <OK> untuk hidup/matikan "
        "output, butang arah melaras frekuensi, <F1><F2> melaras duty cycle, dan "
        "<Fn> masuk kesan isyarat. Output analog tidak dimatikan ketika masuk "
        "kesan isyarat."
    )
    ignition = (
        "Fungsi ini untuk ujian isyarat voltan tinggi nyalaan enjin petrol pada "
        "kereta dan motosikal. Sambungkan sensor isyarat nyalaan, masuk antara "
        "muka ujian, dan dekatkan kepala sensor ke wayar voltan tinggi nyalaan. "
        "Bentuk gelombang nyalaan akan dipaparkan. Jika kenderaan tiada wayar "
        "voltan tinggi luaran, dekatkan sensor ke gegelung nyalaan; isyarat "
        "mungkin lebih kecil. Tekan <F1> untuk tukar mod enjin 4-lejang, 2-lejang "
        "atau distributor. <HOLD> mengunci keadaan semasa. Dalam bacaan normal, "
        "<UP> mengecilkan pembahagi voltan, <DOWN> membesarkan, <LEFT> menambah "
        "masa imbasan, dan <RIGHT> mengurangkannya."
    )
    klin = (
        "Fungsi ini mengesan data komunikasi K/Lin kenderaan dan sesuai untuk "
        "menyemak sama ada ada penghantaran isyarat pada talian komunikasi. "
        "Sambungkan kabel utama, talian ground isyarat ke pin ground kenderaan "
        "(contoh lubang 5 OBD-II) atau ground badan, dan talian K ke pin berkaitan "
        "(contoh lubang 7 OBD-II). Data diterima dipaparkan sebagai nilai heks. "
        "Tekan <F1> untuk padam paparan dan laras baud rate dengan <LEFT>/<RIGHT>. "
        "Data betul hanya diterima apabila baud rate isyarat sama dengan tetapan."
    )
    can = (
        "Fungsi ini mengesan data komunikasi CAN bus kenderaan. Sambungkan kabel "
        "utama, ground isyarat ke pin ground kenderaan (contoh lubang 5 OBD-II) "
        "atau ground badan, CAN+ ke pin CAN+ (contoh lubang 6 OBD-II), dan CAN- "
        "ke pin CAN- (contoh lubang 14 OBD-II). Data diterima dipaparkan sebagai "
        "nilai heks. Tekan <F1> untuk padam paparan dan laras baud rate dengan "
        "<LEFT>/<RIGHT>. Data betul hanya diterima apabila baud rate sama dengan "
        "tetapan. Fungsi ini boleh membantu semak kerosakan talian komunikasi "
        "bersama decoder profesional."
    )
    frequency = (
        "Masuk fungsi ukur frekuensi untuk melihat nilai semasa. Tekan <HOLD> "
        "untuk mengunci keadaan semasa, dan <Fn> untuk tukar ke mod osiloskop. "
        "Julat frekuensi hingga 1MHz dan voltan isyarat dikawal secara adaptif."
    )
    adj_voltage = (
        "Fungsi ini mensimulasi voltan sensor dan gelombang petak, sesuai untuk "
        "simulasi isyarat sensor kenderaan seperti sensor suhu dan throttle "
        "position. Voltan output simulasi 0V-4.5V dan gelombang petak 4.5V boleh "
        "dikeluarkan. Gelombang petak keluar dari terminal [C01-K], manakala "
        "voltan boleh laras dari terminal [C01-S1]. Gunakan butang arah untuk "
        "melaras voltan simulasi, <F1><F2> untuk frekuensi gelombang petak, dan "
        "<Fn> untuk masuk kesan isyarat. Output simulasi tidak dimatikan ketika "
        "masuk kesan isyarat."
    )

    fill_wrapped(replacements, lengths, 206, 218, 34, common_boot)
    fill_wrapped(replacements, lengths, 220, 233, 34, voltage)
    fill_wrapped(replacements, lengths, 235, 252, 34, current)
    fill_wrapped(replacements, lengths, 254, 277, 34, resistance)
    fill_wrapped(replacements, lengths, 279, 296, 34, oscilloscope)
    fill_wrapped(replacements, lengths, 298, 331, 34, circuit)
    fill_wrapped(replacements, lengths, 333, 355, 34, cranking)
    fill_wrapped(replacements, lengths, 357, 380, 34, injector)
    fill_wrapped(replacements, lengths, 382, 403, 34, relay)
    fill_wrapped(replacements, lengths, 405, 430, 34, analog)
    fill_wrapped(replacements, lengths, 432, 468, 34, ignition)
    fill_wrapped(replacements, lengths, 470, 496, 34, klin)
    fill_wrapped(replacements, lengths, 498, 526, 34, can)
    fill_wrapped(replacements, lengths, 528, 535, 34, frequency)

    fill_wrapped(replacements, lengths, 537, 549, 34, common_boot)
    fill_wrapped(replacements, lengths, 551, 564, 34, voltage)
    fill_wrapped(replacements, lengths, 566, 583, 34, current)
    fill_wrapped(replacements, lengths, 585, 608, 34, resistance)
    fill_wrapped(replacements, lengths, 610, 627, 34, oscilloscope)
    fill_wrapped(replacements, lengths, 629, 665, 34, ignition)
    fill_wrapped(replacements, lengths, 667, 674, 34, frequency)

    fill_wrapped(replacements, lengths, 676, 688, 34, common_boot)
    fill_wrapped(replacements, lengths, 690, 703, 34, voltage)
    fill_wrapped(replacements, lengths, 705, 722, 34, current)
    fill_wrapped(replacements, lengths, 724, 747, 34, resistance)
    fill_wrapped(replacements, lengths, 749, 766, 34, oscilloscope)
    fill_wrapped(replacements, lengths, 768, 793, 34, analog)
    fill_wrapped(replacements, lengths, 795, 815, 34, adj_voltage)

    return replacements


def write_csv(path: Path, entries, replacements: dict[int, str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "source_length", "source", "translation"])
        for entry in entries:
            writer.writerow([
                entry.index,
                len(entry.raw_text),
                entry.text.rstrip(" "),
                replacements.get(entry.index, entry.text).rstrip(" "),
            ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    data, _, entries = parse_text_dat(args.source)
    lengths = {entry.index: len(entry.raw_text) for entry in entries}
    replacements = build_translations(lengths)

    changed = sum(1 for entry in entries if replacements.get(entry.index, entry.text) != entry.text)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    text_ms = output_dir / "TEXT_MS.DAT"
    slot_candidate = output_dir / "TEXT_PO.ms-slot-candidate.DAT"
    sp_replacement = output_dir / "TEXT_SP.ms-slot-replacement.DAT"
    csv_path = output_dir / "translations_ms.csv"

    rebuilt = rebuild(data, entries, replacements)
    text_ms.write_bytes(rebuilt)
    slot_candidate.write_bytes(rebuilt)
    sp_replacement.write_bytes(rebuilt)
    write_csv(csv_path, entries, replacements)

    print(f"source={args.source}")
    print(f"source_size={len(data)} source_sha256={sha256(data)}")
    print(f"entries={len(entries)} translated_or_rewrapped={changed}")
    print(f"text_ms={text_ms} size={len(rebuilt)} sha256={sha256(rebuilt)}")
    print(f"slot_candidate={slot_candidate}")
    print(f"sp_replacement={sp_replacement}")
    print(f"translations_csv={csv_path}")
    print("safety_note=text resource only; firmware binary and upgrade system untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
