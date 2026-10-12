#!/usr/bin/env python3
"""Модуль 11-forfait-chaine.law: montant forfaitaire PPA (personne seule) — цепочка L. 161-25 из закреплённых байтов.

DECISION-0452: сначала строит, потом проверяет. Источник чисел один — закреплённые тексты
`sources/montant/` (`tools/pin_forfait.py`): число в правило выписывает этот генератор, а не рука.

Сумма ПО МЕСЯЦУ, а не по дате дела: R. 843-1 берёт три месяца квартала, и в одном запросе
месяцы могут лежать по обе стороны от 1 апреля. Поэтому окна задаются условиями на дату месяца
(`mois >= @… and mois < @…`), а не `effective` (`effective` — дата права дела); месяц привязывает
`forme_foyer_retenue` (она есть у любого месяца расчёта).

  * ДЕКРЕТ называет сумму («est fixé à 595,25 euros à compter du 1er avril 2023»): правило окна несёт
    её как норму (`ForfaitBaseDecret<год>` → `forfait_base_du_mois`) и тем же числом объявляет
    `forfait_base_publie`;
  * ПОСТРОЕНИЕ: предыдущая закреплённая сумма × коэффициент L. 161-25 на 1 апреля (абзац инструкции
    DSS) с округлением до сантима. Тексты округления не называют — это ЧТЕНИЕ D-82
    (`ForfaitRevalorisationArrondiCentime`, практика касс): без него построенное
    (`forfait_base_construit`) не выводится, а окно 01.07.2022 — 31.03.2023 без числа декрета
    остаётся без суммы;
  * ОКНО 01.07.2022: сумма декрета 2022-701 × 1,04 (ст. 9 закона 2022-1158);
  * 1 апреля 2023 — первая ревалоризация после 01.07.2022: ст. 9 берёт частное коэффициента L. 161-25
    (1,056 по DSS/2B/2023/41) на 1,04: `div_round(сумма июля 2022 × 1,056, 1,04, 2, "HALF_UP")`;
  * ПРОВЕРКА: построенное сверяется с опубликованным и с числом, предъявленным делом
    (`forfait_base_retenu`). Генератор сам считает цепочку и отказывает при расхождении с декретом.

Число дела (`forfait_base_retenu`) прежде всего: оно вытесняет сумму декрета (марка
`forfait_base_saisi`), как `mf_base` в пакете rsa. Корень цепи — число декрета 2020-491
(553,16 € с апреля 2020; число 551,51 декрета 2018-836 на 2019 год ревалоризации не имело, поэтому
шаг 2020 не строится).

Коэффициент DSS/SD2B/2020/33 — ставка дерогации LFSS 2020 (+0,3 %), остальные — коэффициент
L. 161-25 из текста инструкции; публикация DSS называет его при BMAF, распространение на PPA —
чтение L. 842-3 («le coefficient mentionné à l'article L. 161-25»), его подтверждает совпадение
построенного с каждым числом декрета до сантима.

  python3 corpus/laws/fr/prime-activite/tools/build_forfait_chaine.py --write   # затем: law fix imports corpus/laws/fr/prime-activite
  python3 corpus/laws/fr/prime-activite/tools/build_forfait_chaine.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus/laws/fr/prime-activite"
OUT = PKG / "11-forfait-chaine.law"
COVERAGE_START = "2021-01-01"
LOI = "loi-2022-1158-art9"
LOI_FRAGMENT = "LOI_2022_1158_ART9"
READING = "ForfaitRevalorisationArrondiCentime"


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


def load():
    manifest = json.loads((PKG / "sources/montant/manifest.json").read_text(encoding="utf-8"))
    rows = {row["name"]: row for row in manifest["texts"]}
    texts = {name: (PKG / row["text"]).read_text(encoding="utf-8") for name, row in rows.items()}
    decrees = sorted((row for row in rows.values() if row["kind"] == "decree"
                      and re.search(r"art[12]$", row["name"]) and amount_in(texts[row["name"]])),
                     key=lambda row: row["applies_from"])
    return rows, texts, decrees


def amount_in(text: str) -> bool:
    return bool(re.search(r"fixé à|égal à", text))


def build():
    rows, texts, decrees = load()
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
    l842 = fmap["CSS_L842_3"]

    def sources(*names: str) -> str:
        return "@source(\n    " + ",\n    ".join(names) + ")"

    def related(row) -> list[str]:
        """Статья о числе и (где отдельная) статья о дате применения того же декрета."""
        same = [r for r in rows.values() if r["kind"] == "decree" and r["numero"] == row["numero"]]
        return [frag(r["name"]) for r in sorted(same, key=lambda r: r["article"])]

    def rule(name, source_names, label_fr, label_en, params, when, then) -> str:
        return "\n".join([
            sources(*source_names),
            f"rule {name}({params}) strict {{",
            f"    effective [@{COVERAGE_START}, infinity);",
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

    header = [
        "// Montant forfaitaire PPA (personne seule) par mois: цепочка L. 161-25 из закреплённых байтов",
        "// (L. 842-3, DECISION-0452). Модуль порождён tools/build_forfait_chaine.py из sources/montant/ —",
        "// руками не править.",
        "//",
        "// Сумма задаётся МЕСЯЦЕМ расчёта (R. 843-1: три месяца квартала), поэтому окна — условия на дату",
        "// месяца, а не `effective`. Декрет называет сумму: правило окна несёт её как норму и объявляет её",
        "// опубликованной. Построение — предыдущая сумма × коэффициент L. 161-25 на 1 апреля, округление",
        "// до сантима HALF_UP: тексты округления не называют, это ЧТЕНИЕ (§152, прочтение D-82, практика",
        "// касс), поэтому построенное выводится только под ForfaitRevalorisationArrondiCentime. Окно",
        "// 01.07.2022 — 31.03.2023 не имеет декрета: сумма декрета 2022-701 × 1,04 (ст. 9 закона 2022-1158)",
        "// и есть норма окна, под тем же чтением. 1 апреля 2023 ст. 9 берёт коэффициент L. 161-25 (1,056)",
        "// на 1,04. Построенное сверяется с опубликованным и с числом, предъявленным делом. Число дела",
        "// (forfait_base_retenu) вытесняет сумму декрета.",
        "",
        'language "law.core" version "0.2";',
        'package fr.css.prime_activite version "0.1.0";',
        'namespace "urn:fr:corpus:clir:ppa";',
        "",
        "use self::{",
        "};",
        "",
        "pub relation forfait_base_saisi(mois: Date) kind institutional {",
        "    key(mois);",
        '    label fr official "une base mensuelle personne seule est fournie pour le mois (forfait_base_retenu) et prévaut sur celle des décrets";',
        '    label en unofficial "a single-person monthly base is supplied for the month (forfait_base_retenu) and prevails over the decree amounts";',
        "}",
        "",
        "pub relation forfait_base_du_mois(mois: Date, base: Money) kind institutional {",
        "    key(mois);",
        '    label fr official "montant forfaitaire personne seule applicable au mois : base fournie pour l\'espèce, sinon montant du décret de revalorisation épinglé (L. 842-3)";',
        '    label en unofficial "single-person flat-rate amount applicable to the month: case-supplied base, otherwise the pinned revaluation decree amount (L. 842-3)";',
        "}",
        "",
        "pub relation forfait_base_publie(mois: Date, base: Money) kind institutional {",
        "    key(mois);",
        '    label fr official "montant forfaitaire personne seule publié par le décret de revalorisation en vigueur au mois";',
        '    label en unofficial "single-person flat-rate amount published by the revaluation decree in force in the month";',
        "}",
        "",
        "pub relation forfait_base_construit(mois: Date, base: Money) kind institutional {",
        "    key(mois);",
        '    label fr official "montant forfaitaire construit : montant précédent multiplié par le coefficient L. 161-25, arrondi au centime (lecture)";',
        '    label en unofficial "flat-rate amount built: previous amount times the L. 161-25 coefficient, rounded to the centime (reading)";',
        "}",
        "",
        "pub relation forfait_base_conforme_publie(mois: Date) kind institutional {",
        "    key(mois);",
        '    label fr official "le montant forfaitaire construit est égal au montant publié du décret pour le mois";',
        '    label en unofficial "the built flat-rate amount equals the decree\'s published amount for the month";',
        "}",
        "",
        "pub relation forfait_saisi_conforme_construit(mois: Date) kind institutional {",
        "    key(mois);",
        '    label fr official "la base fournie pour le mois est égale au montant forfaitaire construit";',
        '    label en unofficial "the base supplied for the month equals the built flat-rate amount";',
        "}",
        "",
    ]
    binder = "forme_foyer_retenue(d, mois, f)"
    params = "d: Demandeur, mois: Date, f: FormeFoyer"

    def window(start: str, end: str | None) -> str:
        return f"mois >= @{start}" + (f" and mois < @{end}" if end else "")

    blocks = [
        rule("ForfaitBaseSaisiMarque", l842,
             "une base fournie pour le mois écarte celle des décrets (marque)",
             "a base supplied for the month displaces the decree amounts (marker)",
             "mois: Date, b: Money", "forfait_base_retenu(mois, b)", "forfait_base_saisi(mois)"),
        rule("ForfaitBaseSaisie", l842,
             "base mensuelle personne seule fournie pour le mois, retenue telle quelle (L. 842-3)",
             "single-person monthly base supplied for the month, used as is (L. 842-3)",
             "mois: Date, b: Money", "forfait_base_retenu(mois, b)", "forfait_base_du_mois(mois, b)"),
    ]
    reading = []
    previous = published[decrees[0]["applies_from"]]
    previous_sources = related(decrees[0])
    built_loi = None
    for i, row in enumerate(decrees):
        start, end = row["applies_from"], (starts[i + 1] if i + 1 < len(starts) else None)
        if i == law_index:      # декрет 2022-701 действует до окна закона: с 01.07.2022 сумма — по ст. 9
            end = loi_start
        year, number = int(start[:4]), row["numero"]
        pub = published[start]
        decree_sources = related(row)
        blocks.append(rule(
            f"ForfaitBaseDecret{year}", decree_sources + l842,
            f"montant forfaitaire personne seule porté à {euros_fr(pub)} euros par le décret {number}, applicable au mois d'avril {year}",
            f"single-person flat-rate amount set at {cents(pub)} euros by decree {number}, applicable from April {year}",
            params, f"{binder} and {window(start, end)} and not_known(forfait_base_saisi(mois))",
            f"forfait_base_du_mois(mois, {money(pub)})"))
        blocks.append(rule(
            f"ForfaitBasePublie{year}", decree_sources,
            f"montant publié par le décret {number} : {euros_fr(pub)} euros",
            f"amount published by decree {number}: {cents(pub)} euros",
            params, f"{binder} and {window(start, end)}", f"forfait_base_publie(mois, {money(pub)})"))
        if i > 0:
            c_name, c = coeff[year]
            if year == 2023:
                built_expr = f'div_round({built_loi} * {num(c)}, {num(loi_rate)}, 2, "HALF_UP")'
                value = cents(cents(published[starts[law_index]] * loi_rate) * c / loi_rate)
                extra = [frag(LOI)]
            else:
                built_expr = f'round({money(previous)} * {num(c)}, 2, "HALF_UP")'
                value = cents(previous * c)
                extra = []
            assert value == pub, f"{year}: построено {value}, опубликовано {pub} (генератор не продолжает при расхождении)"
            reading.append(f"ForfaitBaseConstruit{year}")
            blocks.append(rule(
                f"ForfaitBaseConstruit{year}", previous_sources + [frag(c_name)] + extra + l842,
                f"montant forfaitaire construit au 1er avril {year} : montant précédent multiplié par le coefficient L. 161-25 ({fr(c)}), arrondi au centime (lecture)",
                f"flat-rate amount built on 1 April {year}: previous amount times the L. 161-25 coefficient ({num(c)}), rounded to the centime (reading)",
                params, f"{binder} and {window(start, end)}", f"forfait_base_construit(mois, {built_expr})"))
        previous, previous_sources = pub, decree_sources
        if i == law_index:      # окно закона — сразу за декретом 2022-04, до декрета 2023-04
            july_end = starts[i + 1]
            built_loi = f'round({money(pub)} * {num(loi_rate)}, 2, "HALF_UP")'
            reading.append("ForfaitBaseLoi2022")
            blocks.append(rule(
                "ForfaitBaseLoi2022", decree_sources + [frag(LOI)] + l842,
                f"montant forfaitaire du 1er juillet 2022 : montant du décret {number} multiplié par le coefficient {fr(loi_rate)} de l'article 9 de la loi 2022-1158, arrondi au centime (lecture)",
                f"flat-rate amount from 1 July 2022: decree {number} amount times the {num(loi_rate)} coefficient of article 9 of Act 2022-1158, rounded to the centime (reading)",
                params, f"{binder} and {window(loi_start, july_end)} and not_known(forfait_base_saisi(mois))",
                f"forfait_base_du_mois(mois, {built_loi})"))
    blocks.append(rule(
        "ForfaitBaseConformePublie", l842,
        "le montant forfaitaire construit par la chaîne L. 161-25 est égal au montant publié du décret",
        "the flat-rate amount built by the L. 161-25 chain equals the decree's published amount",
        "mois: Date, p: Money, c: Money", "forfait_base_publie(mois, p) and forfait_base_construit(mois, c) and p == c",
        "forfait_base_conforme_publie(mois)"))
    blocks.append(rule(
        "ForfaitSaisiConformeConstruit", l842,
        "la base fournie pour le mois est égale au montant forfaitaire construit par la chaîne L. 161-25",
        "the base supplied for the month equals the flat-rate amount built by the L. 161-25 chain",
        "mois: Date, s: Money, c: Money", "forfait_base_retenu(mois, s) and forfait_base_construit(mois, c) and s == c",
        "forfait_saisi_conforme_construit(mois)"))
    interpretation = [
        sources(LOI_FRAGMENT, *[frag(n) for n in sorted(r for r in rows if rows[r]["kind"] == "guidance")]),
        f"pub interpretation {READING} of LOI_2022_1158_ART9 {{",
        "    status disputed;",
        '    label fr official "lecture : le produit du montant forfaitaire précédent par le coefficient de revalorisation (L. 161-25, ou 1,04 de l\'article 9 de la loi 2022-1158) est arrondi au centime, demi vers le haut — pratique des caisses (CNAF) ; ni le décret ni L. 842-3 ni L. 161-25 ni l\'article 9 ne fixent d\'arrondi";',
        '    label en unofficial "reading: the product of the previous flat-rate amount and the revaluation coefficient (L. 161-25, or the 1.04 of article 9 of Act 2022-1158) is rounded to the centime, half up - fund (CNAF) practice; neither the decree nor L. 842-3 nor L. 161-25 nor article 9 states a rounding";',
        *[f"    include {name};" for name in reading],
        "}",
        "",
    ]
    series = [(row["applies_from"], published[row["applies_from"]]) for row in decrees]
    july = cents(published[starts[law_index]] * loi_rate)
    return "\n".join(header + blocks + interpretation), series, july, loi_rate


TEST_HEAD = ('language "law.core" version "0.2";\npackage fr.css.prime_activite version "0.1.0";\n'
             'namespace "urn:fr:corpus:clir:ppa";\n')
CASE = 'entity_ref("urn:fr:ppa:case:{}")'


def context(day: str, reading: bool = False) -> str:
    return (f"        context {{ deadline_policy PPA_MOIS; decision_time @{day}T12:00:00Z; knowledge_time @{day}T12:00:00Z; "
            f'legal_time @{day}; timezone "Europe/Paris";{(" interpretation " + READING + ";") if reading else ""} }}\n')


def one(name: str, title: str, day: str, asserts: list[str], queries: list[tuple[str, str]], reading=False) -> str:
    body = "".join(f"        assert \"{name}-{i:02d}\": {a} {{ origin case_input; }}\n" for i, a in enumerate(asserts, 1))
    evals = ""
    for query, truth in queries:
        evals += (f"    evaluate {query};\n    expect result_kind == PROPOSITION;\n"
                  f"    expect truth_status == {truth};\n    expect evaluation_status == COMPUTED;\n")
    return f"// {title}\n" f'test "urn:query:fr-ppa-{name}" {{\n    given {{\n{context(day, reading)}{body}    }}\n{evals}}}\n\n'


def scenarios(series, july: Decimal, loi_rate: Decimal) -> dict[str, str]:
    """Сценарии цепочки: окна декретов, окно закона, чтение, число дела; ожидания — из закреплённых текстов."""
    files = {}
    pubs = dict(series)
    binder = lambda tag, mois: f"forme_foyer_retenue({CASE.format(tag)}, @{mois}, SEUL)"
    review = "2027-02-15"       # дата права дела не влияет на сумму месяца: берём позднюю, чтобы это было видно
    text = ("// Сумма по МЕСЯЦУ расчёта (а не по дате дела): окна декретов о montant forfaitaire PPA, число — статья декрета\n"
            "// (sources/montant/). Дата права дела — 2027-02-15, месяцы — середины окон; ожидания читаются из закреплённых\n"
            "// текстов (build_forfait_chaine.py).\n" + TEST_HEAD + "\n")
    prev = None
    mid = {"2020": "2020-10-01", "2021": "2021-10-01", "2022": "2022-05-01", "2023": "2023-10-01", "2024": "2024-10-01",
           "2025": "2025-10-01", "2026": "2026-10-01"}
    for start, pub in series:
        year = start[:4]
        queries = [(f"truth(forfait_base_du_mois(@{mid[year]}, {money(pub)}))", "TRUE_ONLY")]
        if prev is not None:
            queries.append((f"truth(forfait_base_du_mois(@{mid[year]}, {money(prev)}))", "NEITHER"))
        text += one(f"forfait-decret-{year}", f"{mid[year]}: forfait_base_du_mois = {cents(pub)} EUR (décret du mois d'avril {year})",
                    review, [binder(f"forfait-decret-{year}", mid[year])], queries)
        prev = pub
    files["tests/forfait-decrets.lawtest"] = text.rstrip("\n") + "\n"

    text = ("// Границы окон по МЕСЯЦУ: первый и последний месяц каждого окна; окно ст. 9 закона 2022-1158 (чтение D-82).\n"
            + TEST_HEAD + "\n")
    edges = [("2021-03-01", pubs["2020-04-01"], False), ("2021-04-01", pubs["2021-04-01"], False),
             ("2022-03-01", pubs["2021-04-01"], False), ("2022-04-01", pubs["2022-04-01"], False),
             ("2022-06-01", pubs["2022-04-01"], False), ("2022-07-01", july, True),
             ("2023-03-01", july, True), ("2023-04-01", pubs["2023-04-01"], False),
             ("2025-03-01", pubs["2024-04-01"], False), ("2025-04-01", pubs["2025-04-01"], False),
             ("2026-03-01", pubs["2025-04-01"], False), ("2026-04-01", pubs["2026-04-01"], False)]
    for mois, value, reading in edges:
        text += one(f"forfait-bord-{mois}", f"{mois}: forfait_base_du_mois = {cents(value)} EUR" + (" (lecture)" if reading else ""),
                    review, [binder(f"forfait-bord-{mois}", mois)],
                    [(f"truth(forfait_base_du_mois(@{mois}, {money(value)}))", "TRUE_ONLY")], reading=reading)
    files["tests/forfait-bords-mois.lawtest"] = text.rstrip("\n") + "\n"

    text = ("// Построение и сверка (DECISION-0452) под чтением " + READING + ": предыдущая сумма × коэффициент L. 161-25,\n"
            "// округление до сантима; построенное равно опубликованному в каждом окне, начиная с 2021.\n" + TEST_HEAD + "\n")
    for start, pub in series[1:]:
        year = start[:4]
        text += one(f"forfait-chaine-{year}", f"{mid[year]}: forfait_base_construit = {cents(pub)} EUR et conforme au décret",
                    review, [binder(f"forfait-chaine-{year}", mid[year])],
                    [(f"truth(forfait_base_construit(@{mid[year]}, {money(pub)}))", "TRUE_ONLY"),
                     (f"truth(forfait_base_conforme_publie(@{mid[year]}))", "TRUE_ONLY")], reading=True)
    files["tests/forfait-chaine-lecture.lawtest"] = text.rstrip("\n") + "\n"

    pub23 = pubs["2023-04-01"]
    text = ("// Без чтения: окно закона без суммы (число декрета отсутствует, округление текстами не задано), построенное\n"
            "// не выводится, число декрета окна остаётся нормой.\n" + TEST_HEAD + "\n")
    text += one("forfait-sans-lecture-loi", "2022-09-01 без чтения: суммы нет", review,
                [binder("forfait-sans-lecture-loi", "2022-09-01")],
                [(f"truth(forfait_base_du_mois(@2022-09-01, {money(july)}))", "NEITHER")])
    text += one("forfait-sans-lecture-2023", "2023-10-01 без чтения: число декрета есть, построенного нет", review,
                [binder("forfait-sans-lecture-2023", "2023-10-01")],
                [(f"truth(forfait_base_du_mois(@2023-10-01, {money(pub23)}))", "TRUE_ONLY"),
                 (f"truth(forfait_base_construit(@2023-10-01, {money(pub23)}))", "NEITHER"),
                 ("truth(forfait_base_conforme_publie(@2023-10-01))", "NEITHER")])
    files["tests/forfait-sans-lecture.lawtest"] = text.rstrip("\n") + "\n"

    pub24 = pubs["2024-04-01"]
    text = "// База дела вытесняет сумму декрета (марка forfait_base_saisi); сверка предъявленного числа с построенным.\n" + TEST_HEAD + "\n"
    text += one("forfait-saisi-prevaut", "2024-10-01: предъявлено 600.00 — оно и применяется, число декрета вытеснено", review,
                [binder("forfait-saisi-prevaut", "2024-10-01"), "forfait_base_retenu(@2024-10-01, 600.00 EUR)"],
                [("truth(forfait_base_du_mois(@2024-10-01, 600.00 EUR))", "TRUE_ONLY"),
                 (f"truth(forfait_base_du_mois(@2024-10-01, {money(pub24)}))", "NEITHER")])
    text += one("forfait-saisi-ecart", "2024-10-01 под чтением: 600.00 не равно построенному", review,
                [binder("forfait-saisi-ecart", "2024-10-01"), "forfait_base_retenu(@2024-10-01, 600.00 EUR)"],
                [("truth(forfait_saisi_conforme_construit(@2024-10-01))", "NEITHER")], reading=True)
    text += one("forfait-saisi-conforme", "2024-10-01 под чтением: предъявленное число равно построенному", review,
                [binder("forfait-saisi-conforme", "2024-10-01"), f"forfait_base_retenu(@2024-10-01, {money(pub24)})"],
                [("truth(forfait_saisi_conforme_construit(@2024-10-01))", "TRUE_ONLY")], reading=True)
    files["tests/forfait-saisi-prevaut.lawtest"] = text.rstrip("\n") + "\n"
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text, series, july, loi_rate = build()
    tests = scenarios(series, july, loi_rate)
    if args.write:
        if OUT.exists():        # блок `use self::{…}` ведёт `law fix imports`: не затираем его
            keep = re.search(r"use self::\{.*?\};", OUT.read_text(encoding="utf-8"), re.S).group(0)
            text = re.sub(r"use self::\{.*?\};", lambda _m: keep, text, count=1, flags=re.S)
        OUT.write_text(text, encoding="utf-8")
        for rel, body in tests.items():
            (PKG / rel).write_text(body, encoding="utf-8")
        print(f"WROTE {OUT.relative_to(ROOT)} + {len(tests)} scenario files")
        return 0
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
