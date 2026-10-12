#!/usr/bin/env python3
"""Модуль 07-montant-chaine.law: месячный размер AAH — цепочка L. 161-25 из закреплённых байтов.

DECISION-0452: сначала строит, потом проверяет. Источник чисел один — закреплённые тексты
`sources/montant/` (`tools/pin_montant.py`): число в правило выписывает этот генератор, а не рука.

  * ДЕКРЕТ называет сумму («est porté à 919,86 euros»): правило окна несёт её как норму
    (`MontantAahDecret<год>` → `montant_aah_applicable`) и тем же числом объявляет
    `aah_montant_publie`;
  * ПОСТРОЕНИЕ: предыдущая закреплённая сумма × коэффициент L. 161-25 на 1 апреля (абзац
    инструкции DSS) с округлением до сантима. Тексты округления не называют — это ЧТЕНИЕ D-82
    (`AahRevalorisationArrondiCentime`, практика касс): без него построенное
    (`aah_montant_construit`) не выводится, а окно 01.07.2022 — 31.03.2023, у которого нет
    декрета, остаётся без суммы (как окно ст. 9 закона 2022-1158 в пакете rsa);
  * ОКНО 01.07.2022: сумма декрета 2022-700 × 1,04 (ст. 9 закона 2022-1158);
  * 1 апреля 2023 — первая ревалоризация после 01.07.2022: ст. 9 берёт частное коэффициента
    L. 161-25 (1,056 по инструкции DSS/2B/2023/41) на 1,04: `div_round(сумма июля 2022 × 1,056,
    1,04, 2, "HALF_UP")`;
  * ПРОВЕРКА: построенное сверяется с опубликованным (`aah_montant_conforme_publie`) и с числом,
    предъявленным делом (`aah_saisi_conforme_construit`). Генератор сам считает цепочку и
    отказывает, если построенное расходится с числом декрета.

Число, предъявленное делом (`montant_mensuel_retenu`), прежде всего: оно вытесняет сумму
декрета (марка `aah_montant_saisi`), как `mf_base` в пакете rsa.

Коэффициент DSS/SD2B/2020/33 — ставка дерогации LFSS 2020 (+0,3 %), остальные — коэффициент
L. 161-25 из текста инструкции. Инструкция называет его при BMAF; распространение на AAH — чтение
L. 821-3-1 («le coefficient mentionné à l'article L. 161-25»), его подтверждает совпадение
построенного с каждым числом декрета до сантима.

  python3 corpus/laws/fr/aah/tools/build_montant_chaine.py --write   # затем: law fix imports corpus/laws/fr/aah
  python3 corpus/laws/fr/aah/tools/build_montant_chaine.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus/laws/fr/aah"
OUT = PKG / "07-montant-chaine.law"
COVERAGE_START = "2021-01-01"
LOI = "loi-2022-1158-art9"
LOI_FRAGMENT = "LOI_2022_1158_ART9"


def amount(text: str) -> Decimal:
    found = re.search(r"((?:\d[\d   ]*)(?:,\d+)?) euros", text)
    return Decimal(re.sub(r"[   ]", "", found.group(1)).replace(",", "."))


def coefficient(text: str) -> Decimal:
    plain = re.sub(r"\s+", " ", text)
    found = re.search(r"fixé à (1,\d+)", plain)
    if found:
        return Decimal(found.group(1).replace(",", "."))
    rate = re.search(r"revalorisation de (\d+,\d+) ?%", plain)
    return Decimal(1) + Decimal(rate.group(1).replace(",", ".")) / 100


def loi_coefficient(text: str) -> Decimal:
    return Decimal(re.search(r"coefficient égal à (1,\d+)", text).group(1).replace(",", "."))


def cents(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), ROUND_HALF_UP)


def money(value: Decimal) -> str:
    return f"{cents(value)} EUR"


def num(value: Decimal) -> str:
    return format(value.normalize(), "f")


def fr(value: Decimal) -> str:
    return num(value).replace(".", ",")


def euros_fr(value: Decimal) -> str:
    return f"{cents(value)}".replace(".", ",")


def build() -> tuple[str, list[tuple[str, Decimal, Decimal]], Decimal]:
    manifest = json.loads((PKG / "sources/montant/manifest.json").read_text(encoding="utf-8"))
    rows = {row["name"]: row for row in manifest["texts"]}
    texts = {name: (PKG / row["text"]).read_text(encoding="utf-8") for name, row in rows.items()}
    decrees = sorted((row for row in rows.values() if row["kind"] == "decree" and row["name"].endswith("art1")),
                     key=lambda row: row["applies_from"])
    coeff = {int(re.match(r"dss-(\d{4})-", name).group(1)): (name, coefficient(texts[name]))
             for name, row in rows.items() if row["kind"] == "guidance"}
    loi_rate = loi_coefficient(texts[LOI])
    loi_start = "2022-07-01"
    assert "1er juillet 2022" in texts[LOI]

    def frag(name: str) -> str:
        row = rows[name]
        if row["kind"] == "decree":
            return "DEC" + row["numero"].replace("-", "_") + f"_ART{row['article']}"
        if row["kind"] == "statute":
            return LOI_FRAGMENT
        return row["origin_fragment"].split("::")[1]

    fmap = json.loads((PKG / "sources/fragment-map.json").read_text(encoding="utf-8"))
    l821 = fmap["CSS_L821_3_1"]
    edition_start = lambda name: "-".join(re.search(r"ED(\d{4})_(\d{2})_(\d{2})$", name).groups())
    debuts = sorted(edition_start(name) for name in l821)

    def css(window_start: str, window_end: str | None) -> list[str]:
        """Редакции ст. L. 821-3-1, пересекающие окно."""
        picked = []
        for name in l821:
            begin = edition_start(name)
            later = [d for d in debuts if d > begin]
            end = later[0] if later else None
            if begin < (window_end or "9999") and (end is None or end > window_start):
                picked.append(name)
        return picked

    def sources(*names: str) -> str:
        return "@source(\n    " + ",\n    ".join(names) + ")"

    def rule(name, start, end, source_names, label_fr, label_en, params, when, then) -> str:
        return "\n".join([
            sources(*source_names),
            f"rule {name}({params}) strict {{",
            f"    effective [@{start}, {('@' + end) if end else 'infinity'});",
            f'    label fr official "{label_fr}";',
            f'    label en unofficial "{label_en}";',
            f"    when {when};",
            f"    then {then};",
            "}",
            "",
        ])

    published = {row["applies_from"]: amount(texts[row["name"]]) for row in decrees}
    starts = [row["applies_from"] for row in decrees]
    law_index = max(i for i, row in enumerate(decrees) if row["applies_from"] < loi_start)
    root = decrees[0]
    css_all = css(COVERAGE_START, None)

    header = [
        "// Месячный размер AAH: цепочка L. 161-25 из закреплённых байтов (L. 821-3-1, DECISION-0452).",
        "// Модуль порождён tools/build_montant_chaine.py из sources/montant/ — руками не править.",
        "//",
        "// Декрет называет сумму: правило окна несёт её как норму и объявляет её опубликованной.",
        "// Построение — предыдущая сумма × коэффициент L. 161-25 на 1 апреля, округление до сантима",
        "// HALF_UP: тексты округления не называют, это ЧТЕНИЕ (§152, прочтение D-82, практика касс),",
        "// поэтому построенное выводится только под AahRevalorisationArrondiCentime. Окно 01.07.2022 —",
        "// 31.03.2023 не имеет декрета: сумма декрета 2022-700 × 1,04 (ст. 9 закона 2022-1158) и есть",
        "// норма окна, под тем же чтением. 1 апреля 2023 ст. 9 берёт коэффициент L. 161-25 (1,056)",
        "// на 1,04. Построенное сверяется с опубликованным и с числом, предъявленным делом.",
        "// Число дела (montant_mensuel_retenu) вытесняет сумму декрета.",
        "",
        'language "law.core" version "0.2";',
        'package fr.css.aah version "0.1.0";',
        'namespace "urn:fr:corpus:clir:aah";',
        "",
        "use self::{",
        "};",
        "",
        "pub relation aah_montant_saisi() kind institutional {",
        '    label fr official "un montant mensuel est fourni pour l\'espèce (montant_mensuel_retenu) et prévaut sur celui des décrets";',
        '    label en unofficial "a monthly amount is supplied for the case (montant_mensuel_retenu) and prevails over the decree amounts";',
        "}",
        "",
        "pub relation montant_aah_applicable(montant: Money) kind institutional {",
        '    label fr official "montant mensuel de l\'allocation applicable à la date des droits : montant fourni pour l\'espèce, sinon montant du décret de revalorisation épinglé (L. 821-3-1)";',
        '    label en unofficial "monthly allowance amount applicable at the date of the rights: case-supplied amount, otherwise the pinned revaluation decree amount (L. 821-3-1)";',
        "}",
        "",
        "pub relation aah_montant_publie(montant: Money) kind institutional {",
        '    label fr official "montant mensuel publié par le décret de revalorisation en vigueur (article 1er)";',
        '    label en unofficial "monthly amount published by the revaluation decree in force (article 1)";',
        "}",
        "",
        "pub relation aah_montant_construit(montant: Money) kind institutional {",
        '    label fr official "montant mensuel construit : montant précédent multiplié par le coefficient L. 161-25, arrondi au centime (lecture)";',
        '    label en unofficial "monthly amount built: previous amount times the L. 161-25 coefficient, rounded to the centime (reading)";',
        "}",
        "",
        "pub relation aah_montant_conforme_publie() kind institutional {",
        '    label fr official "le montant construit est égal au montant publié du décret";',
        '    label en unofficial "the built amount equals the decree\'s published amount";',
        "}",
        "",
        "pub relation aah_saisi_conforme_construit() kind institutional {",
        '    label fr official "le montant fourni pour l\'espèce est égal au montant construit";',
        '    label en unofficial "the case-supplied amount equals the built amount";',
        "}",
        "",
    ]
    blocks = [
        rule("MontantSaisiMarque", COVERAGE_START, None, css_all,
             "un montant fourni pour l'espèce écarte celui des décrets (marque)",
             "a case-supplied amount displaces the decree amounts (marker)",
             "m: Money", "montant_mensuel_retenu(m)", "aah_montant_saisi()"),
        rule("MontantSaisi", COVERAGE_START, None, css_all,
             "montant mensuel fourni pour l'espèce, retenu tel quel (L. 821-3-1)",
             "monthly amount supplied for the case, used as is (L. 821-3-1)",
             "m: Money", "montant_mensuel_retenu(m)", "montant_aah_applicable(m)"),
    ]
    reading = []
    log = []
    previous = published[root["applies_from"]]
    previous_sources = [frag(root["name"]), frag(root["name"].replace("art1", "art3"))]
    built_loi = None
    for i, row in enumerate(decrees):
        if i == 0:
            continue       # корень цепи: 900 € с 2019-11 (декрет 2019-1047); окна правила у него нет
        start, end = row["applies_from"], (starts[i + 1] if i + 1 < len(starts) else None)
        if i == law_index:      # декрет 2022-700 действует до окна закона: с 01.07.2022 сумма — по ст. 9
            end = loi_start
        year, number = int(start[:4]), row["numero"]
        pub = published[start]
        coeff_name, c = coeff[year]
        decree_sources = [frag(row["name"])] + [frag(extra) for extra in (row["name"].replace("art1", "art2"),) if extra in rows]
        win_start = max(start, COVERAGE_START)
        blocks.append(rule(
            f"MontantAahDecret{year}", win_start, end, decree_sources + css(win_start, end),
            f"montant mensuel de l'allocation porté à {euros_fr(pub)} euros par le décret {number}, à compter des allocations dues au titre du mois d'avril {year}",
            f"monthly allowance amount raised to {cents(pub)} euros by decree {number}, from the allocations due for April {year}",
            "", "not_known(aah_montant_saisi())", f"montant_aah_applicable({money(pub)})"))
        blocks.append(rule(
            f"MontantAahPublie{year}", win_start, end, decree_sources,
            f"montant publié par le décret {number} : {euros_fr(pub)} euros",
            f"amount published by decree {number}: {cents(pub)} euros",
            "", "true", f"aah_montant_publie({money(pub)})"))
        if year == 2023:
            built_expr = f'div_round({built_loi} * {num(c)}, {num(loi_rate)}, 2, "HALF_UP")'
            value = cents(cents(published[starts[law_index]] * loi_rate) * c / loi_rate)
            extra_sources = [frag(LOI)]
        else:
            built_expr = f'round({money(previous)} * {num(c)}, 2, "HALF_UP")'
            value = cents(previous * c)
            extra_sources = []
        assert value == pub, f"{year}: построено {value}, опубликовано {pub} (генератор не продолжает при расхождении)"
        log.append((year, previous, c, value))
        reading.append(f"MontantAahConstruit{year}")
        blocks.append(rule(
            f"MontantAahConstruit{year}", win_start, end,
            previous_sources + [frag(coeff_name)] + extra_sources + css(win_start, end),
            f"montant construit au 1er avril {year} : montant précédent multiplié par le coefficient L. 161-25 ({fr(c)}), arrondi au centime (lecture)",
            f"amount built on 1 April {year}: previous amount times the L. 161-25 coefficient ({num(c)}), rounded to the centime (reading)",
            "", "true", f"aah_montant_construit({built_expr})"))
        previous, previous_sources = pub, decree_sources
        if i == law_index:      # окно закона — сразу за декретом 2022-04, до декрета 2023-04
            july_end = starts[i + 1]
            built_loi = f'round({money(pub)} * {num(loi_rate)}, 2, "HALF_UP")'
            reading.append("MontantAahLoi2022")
            blocks.append(rule(
                "MontantAahLoi2022", loi_start, july_end,
                decree_sources + [frag(LOI)] + css(loi_start, july_end),
                f"montant mensuel du 1er juillet 2022 : montant du décret {number} multiplié par le coefficient {fr(loi_rate)} de l'article 9 de la loi 2022-1158, arrondi au centime (lecture)",
                f"monthly amount from 1 July 2022: decree {number} amount times the {num(loi_rate)} coefficient of article 9 of Act 2022-1158, rounded to the centime (reading)",
                "", "not_known(aah_montant_saisi())", f"montant_aah_applicable({built_loi})"))
            log.append(("2022-07", pub, loi_rate, cents(pub * loi_rate)))
    blocks.append(rule(
        "MontantAahConformePublie", COVERAGE_START, None, css_all,
        "le montant construit par la chaîne L. 161-25 est égal au montant publié du décret",
        "the amount built by the L. 161-25 chain equals the decree's published amount",
        "p: Money, c: Money", "aah_montant_publie(p) and aah_montant_construit(c) and p == c", "aah_montant_conforme_publie()"))
    blocks.append(rule(
        "MontantAahSaisiConformeConstruit", COVERAGE_START, None, css_all,
        "le montant fourni pour l'espèce est égal au montant construit par la chaîne L. 161-25",
        "the case-supplied amount equals the amount built by the L. 161-25 chain",
        "s: Money, c: Money", "montant_mensuel_retenu(s) and aah_montant_construit(c) and s == c", "aah_saisi_conforme_construit()"))
    interpretation = [
        sources(LOI_FRAGMENT, *[frag(n) for n in sorted(coeff_row for coeff_row in rows if rows[coeff_row]["kind"] == "guidance")]),
        "pub interpretation AahRevalorisationArrondiCentime of LOI_2022_1158_ART9 {",
        "    status disputed;",
        '    label fr official "lecture : le produit du montant précédent de l\'allocation par le coefficient de revalorisation (L. 161-25, ou 1,04 de l\'article 9 de la loi 2022-1158) est arrondi au centime, demi vers le haut — pratique des caisses (CNAF) ; ni le décret ni L. 821-3-1 ni L. 161-25 ni l\'article 9 ne fixent d\'arrondi";',
        '    label en unofficial "reading: the product of the previous allowance amount and the revaluation coefficient (L. 161-25, or the 1.04 of article 9 of Act 2022-1158) is rounded to the centime, half up - fund (CNAF) practice; neither the decree nor L. 821-3-1 nor L. 161-25 nor article 9 states a rounding";',
        *[f"    include {name};" for name in reading],
        "}",
        "",
    ]
    series = [(row["applies_from"], published[row["applies_from"]]) for row in decrees[1:]]
    return "\n".join(header + blocks + interpretation), series, cents(published[starts[law_index]] * loi_rate)


TEST_HEAD = ('language "law.core" version "0.2";\npackage fr.css.aah version "0.1.0";\n'
             'namespace "urn:fr:corpus:clir:aah";\n')
READING = "AahRevalorisationArrondiCentime"
#: середина окна — дата дела; ожидания читаются из закреплённых текстов, не набираются руками.
MID = {"2020": "2021-02-15", "2021": "2021-06-15", "2022": "2022-05-15", "2023": "2023-06-15",
       "2024": "2024-06-15", "2025": "2025-06-15", "2026": "2026-05-15"}
CASE = 'entity_ref("urn:fr:css-aah:case:{}")'


def context(day: str, reading: bool = False) -> str:
    return (f"        context {{ decision_time @{day}T12:00:00Z; knowledge_time @{day}T12:00:00Z; legal_time @{day}; "
            f'timezone "Europe/Paris";{(" interpretation " + READING + ";") if reading else ""} }}\n')


def one(name: str, title: str, day: str, asserts: list[str], queries: list[tuple[str, str]], reading=False,
        status: str = "COMPUTED") -> str:
    body = "".join(f"        assert \"{name}-{i:02d}\": {a} {{ origin case_input; }}\n" for i, a in enumerate(asserts, 1))
    evals = ""
    for query, truth in queries:
        evals += (f"    evaluate {query};\n    expect result_kind == PROPOSITION;\n"
                  f"    expect truth_status == {truth};\n    expect evaluation_status == {status};\n")
    return (f"// {title}\n" f'test "urn:query:fr-css-aah-{name}" {{\n    given {{\n{context(day, reading)}{body}    }}\n'
            f"{evals}}}\n\n")


def scenarios(series, july: Decimal) -> dict[str, str]:
    """Сценарии цепочки: окна декретов, окно закона, чтение, число дела."""
    files = {}
    dummy = lambda tag: [f"en_couple({CASE.format(tag)})"]       # given без утверждений не принимается
    text = ("// Окна декретов о размере AAH: сумма окна — число статьи 1 декрета (sources/montant/),\n"
            "// дата дела — середина окна. Ожидания читаются из закреплённых текстов (build_montant_chaine.py).\n" + TEST_HEAD + "\n")
    prev = None
    for start, pub in series:
        year = start[:4]
        queries = [(f"truth(montant_aah_applicable({money(pub)}))", "TRUE_ONLY")]
        if prev is not None:        # окна не пересекаются: сумма предыдущего окна не выводится
            queries.append((f"truth(montant_aah_applicable({money(prev)}))", "NEITHER"))
        text += one(f"decret-{year}", f"{year}: montant_aah_applicable = {cents(pub)} EUR, décret du mois d'avril {year}", MID[year],
                    dummy(f"decret-{year}"), queries)
        prev = pub
    files["tests/aah-montant-decrets.lawtest"] = text.rstrip("\n") + "\n"

    text = ("// Окно 01.07.2022 — 31.03.2023 (ст. 9 закона 2022-1158): сумма декрета 2022-700 × 1,04 с округлением\n"
            "// до сантима HALF_UP — ЧТЕНИЕ D-82 (" + READING + "); границы окна и середина.\n" + TEST_HEAD + "\n")
    for tag, day in (("2022-07-01", "2022-07-01"), ("2022-12-15", "2022-12-15"), ("2023-03-31", "2023-03-31")):
        text += one(f"loi-{tag}", f"{tag}: montant_aah_applicable = {july} EUR (lecture); сумма декрета 2022-700 здесь не применяется", day,
                    dummy(f"loi-{tag}"),
                    [(f"truth(montant_aah_applicable({money(july)}))", "TRUE_ONLY"),
                     (f"truth(montant_aah_applicable({money(dict(series)['2022-04-01'])}))", "NEITHER")], reading=True)
    text += one("loi-2022-06-30", "2022-06-30: накануне окна закона — ещё сумма декрета 2022-700", "2022-06-30", dummy("loi-2022-06-30"),
                [(f"truth(montant_aah_applicable({money(dict(series)['2022-04-01'])}))", "TRUE_ONLY")], reading=True)
    text += one("loi-2023-04-01", "2023-04-01: окно закона закрыто — сумма декрета 2023-328", "2023-04-01", dummy("loi-2023-04-01"),
                [(f"truth(montant_aah_applicable({money(dict(series)['2023-04-01'])}))", "TRUE_ONLY")], reading=True)
    files["tests/aah-montant-loi-2022.lawtest"] = text.rstrip("\n") + "\n"

    text = ("// Построение и сверка (DECISION-0452) под чтением " + READING + ": предыдущая сумма × коэффициент L. 161-25,\n"
            "// округление до сантима; построенное равно опубликованному в каждом окне.\n" + TEST_HEAD + "\n")
    for start, pub in series:
        year = start[:4]
        text += one(f"chaine-{year}", f"{year}: aah_montant_construit = {cents(pub)} EUR и conforme au décret", MID[year],
                    dummy(f"chaine-{year}"),
                    [(f"truth(aah_montant_construit({money(pub)}))", "TRUE_ONLY"), ("truth(aah_montant_conforme_publie())", "TRUE_ONLY")],
                    reading=True)
    files["tests/aah-montant-chaine-lecture.lawtest"] = text.rstrip("\n") + "\n"

    pub23 = dict(series)["2023-04-01"]
    text = ("// Без чтения: окно закона без суммы (число декрета отсутствует, округление текстами не задано), построенное\n"
            "// не выводится, число декрета окна остаётся нормой.\n" + TEST_HEAD + "\n")
    text += one("sans-lecture-loi", "2022-09-15 без чтения: суммы нет", "2022-09-15", dummy("sans-lecture-loi"),
                [(f"truth(montant_aah_applicable({money(july)}))", "NEITHER")])
    text += one("sans-lecture-2023", "2023-06-15 без чтения: число декрета есть, построенного нет", "2023-06-15",
                dummy("sans-lecture-2023"),
                [(f"truth(montant_aah_applicable({money(pub23)}))", "TRUE_ONLY"), (f"truth(aah_montant_construit({money(pub23)}))", "NEITHER"),
                 ("truth(aah_montant_conforme_publie())", "NEITHER")])
    files["tests/aah-montant-sans-lecture.lawtest"] = text.rstrip("\n") + "\n"

    pub24 = dict(series)["2024-04-01"]
    text = ("// Число дела вытесняет сумму декрета (марка aah_montant_saisi); сверка предъявленного числа с построенным.\n"
            + TEST_HEAD + "\n")
    text += one("saisi-prevaut", "2024-06-15: предъявлено 1000.00 — оно и применяется, число декрета вытеснено", "2024-06-15",
                ["montant_mensuel_retenu(1000.00 EUR)"],
                [("truth(montant_aah_applicable(1000.00 EUR))", "TRUE_ONLY"), (f"truth(montant_aah_applicable({money(pub24)}))", "NEITHER")])
    text += one("saisi-ecart", "2024-06-15 под чтением: 1000.00 не равно построенному", "2024-06-15", ["montant_mensuel_retenu(1000.00 EUR)"],
                [("truth(aah_saisi_conforme_construit())", "NEITHER")], reading=True)
    text += one("saisi-conforme", "2024-06-15 под чтением: предъявленное число равно построенному", "2024-06-15",
                [f"montant_mensuel_retenu({money(pub24)})"],
                [("truth(aah_saisi_conforme_construit())", "TRUE_ONLY")], reading=True)
    files["tests/aah-montant-saisi-prevaut.lawtest"] = text.rstrip("\n") + "\n"

    text = ("// От декрета до суммы дела (L. 821-3-1 + D. 821-2 в редакции с 01.10.2023): одинокий заявитель, 80 % и выше,\n"
            "// без ресурсов, годовой режим; число дела не подаётся — сумма берётся из закреплённого декрета окна.\n" + TEST_HEAD + "\n")
    for year, day in (("2023", "2023-12-15"), ("2024", "2024-06-15"), ("2025", "2025-06-15"), ("2026", "2026-05-15")):
        pub = dict(series)[f"{year}-04-01"]
        c = CASE.format(f"bout-{year}")
        facts = [f"decision_cdaph_80({c})", f"age_droit_depasse({c})", f"residence_permanente({c})", f"sejour_regulier({c})",
                 f"sans_revenu_activite({c})", f"personne_seule({c})", f"ressources_annuelles_retenues({c}, 0.00 EUR)",
                 "enfants_charge(0)"]
        text += one(f"bout-{year}", f"{day}: aah_montant_nouveau = {cents(pub)} EUR (décret du mois d'avril {year})", day, facts,
                    [(f"truth(aah_montant_nouveau({c}, {money(pub)}))", "TRUE_ONLY")])
    files["tests/aah-montant-decret-bout-en-bout.lawtest"] = text.rstrip("\n") + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text, series, july = build()
    tests = scenarios(series, july)
    if args.write:
        if OUT.exists():        # блок `use self::{…}` ведёт `law fix imports`: не затираем его
            keep = re.search(r"use self::\{.*?\};", OUT.read_text(encoding="utf-8"), re.S).group(0)
            text = re.sub(r"use self::\{.*?\};", lambda _m: keep, text, count=1, flags=re.S)
        OUT.write_text(text, encoding="utf-8")
        for rel, body in tests.items():
            (PKG / rel).write_text(body, encoding="utf-8")
        print(f"WROTE {OUT.relative_to(ROOT)} + {len(tests)} scenario files")
        return 0
    # Блок `use self::{…}` ведёт `law fix imports corpus/laws/fr/aah` (DECISION-0386): при сверке он не сравнивается.
    strip = lambda t: re.sub(r"use self::\{.*?\};", "use self::{};", t, count=1, flags=re.S)
    bad = []
    if not OUT.exists() or strip(OUT.read_text(encoding="utf-8")) != strip(text):
        bad.append(str(OUT.relative_to(ROOT)))
    for rel, body in tests.items():
        if not (PKG / rel).exists() or (PKG / rel).read_text(encoding="utf-8") != body:
            bad.append(rel)
    if bad:
        print("drift " + ", ".join(bad))
        return 1
    print("CHAIN OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
