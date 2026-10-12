"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.pf.af (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Из их прогона берутся ФАКТЫ дела (даты рождения, состав,
garde_alternee, ресурсы по R. 532-3), а не их суммы. Нормативные суммы — только
закреплённые байты пакета fr.css.revalorisation (фрагменты `01-sources.law`):

* BMAF на месяц права — последняя ревалоризация не позже месяца: строка
  «Base mensuelle de calcul des allocations familiales à compter du 1er avril
  YYYY : X €» фрагментов *_BMAF; 01.04.2018 — цитата инструкции 2019 («porté de
  411,92 € à 413,16 € au 1er avril 2019», DSS_SD2B_2019_65_COEFF); ступень
  01.07.2022 — 439,17 €, построенная правилом пакета (422,28 × 1,04 по ст. 9 закона
  2022-1158, сценарий `tests/bmaf-chaine-2022-07`), не напечатанная ни одной
  инструкцией.
* Плафоны D. 521-3 (D-81) — «plafond de base X € majoré de Y € par enfant à
  charge» фрагмента PLAFOND_AF инструкции на 1 января года права (таблица «du
  1er janvier N au 31 décembre N»; ресурсы года N−2 — их факт); 2016 = 2017 по
  фрагменту DSS_SD2B_2016_396_REVAL («reconduits à l'identique»). Для 2015
  (07–12) входов нет: правила Plafond1/2Nominal пакета берут суммы самого D. 521-3.

Прочтение D-83 `ArrondiLignesDss` (08-lecture-arrondi-lignes.law) выбрано в context:
суммы AF — округлённые до сантима строки таблицы DSS (база по полосе — строка
«N enfants», надбавка, forfait), итог — их сумма; douzième complément dégressif —
до сантима HALF_UP (D-82). Без выбора пакет округлял один итог, а douzième
отказывал (граница B-PFAF-ARRONDI).
"""
from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

PACKAGE = {"package": "fr.pf.af", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:pf-af",
           "prefix": "fr-pf-af", "timezone": "Europe/Paris", "world": ["fr.pf.af", "fr.pf.core"], "resolve": ["fr.pf.af", "fr.pf.core"],
           "context": "deadline_policy AGE_ATTEINT; interpretation ArrondiLignesDss;"}

#: Правила пакета действуют с 2015-07-01 (effective у D. 521-1 и др., редакции CSS с 2015-10);
#: реестр объявлял 2021-01.
COVERAGE_START = "2015-07"

TARGETS = {
    "af": {"predicate": "af_montant_du", "kind": "Money"},
    "af_base": {"predicate": "montant_mensuel_af", "kind": "Money"},
    "af_majoration": {"predicate": "montant_majoration", "kind": "Money",
                      "per_member": {"of": "af_majoration_enfant", "members": "enfants",
                                     "predicate": "montant_majoration", "kind": "Money"}},
}

QUALIFIED = {
    "of176-af-2018-01-16/af": {
        "class": "(б) их дефект против текста",
        "why": ("D. 521-1 I 3° (pf-af/sources/css/D521-1.txt:12-13): полоса 3 — 8 % за второго и 10,25 % за "
                "каждого следующего ребёнка от BMAF; DSS/SD2B/2017/97 (revalorisation/sources/dss-2017-97.txt:148) "
                "публикует для 4 детей «28,5 % … 116,23». Наше 0,285 × 407,84 = 116,2344 → 116,23 (= DSS); их код "
                "116,235. Реплика их чтения (af.py, af_base): round2(BMAF × 114 %) × 0,25 = 464,94 × 0,25 = 116,235 — "
                "округляют полную ставку полосы 1 до модуляции, а не сумму полосы 3. Под прочтением D-83 "
                "ArrondiLignesDss наше 116,23 — сама строка таблицы DSS, класс не меняется"),
    },
    "of176-af-54/af": {
        "class": "(а) граница B-PFAF-ARRONDI (стадия доли R. 521-3)",
        "why": ("их af в деле с garde alternée — доля родителя R. 521-3: их файл «296.53 * 0.8333», их код "
                "296,53 × 5/6 = 247,108; наш af_montant_du — итог ménage, строка «3 enfants» 0,73 × 406,21 = 296,5333 → "
                "296,53, ровно множитель их файла. Доля 5/6 не терминируется — движок отказывает без политики "
                "округления (B-PFAF-ARRONDI, ручной перенос tests/foreign/openfisca/of-2015-09); прочтение D-83 "
                "ArrondiLignesDss долю R. 521-3 не покрывает (D-82: «не покрыто», D-83 объём не расширяет)"),
    },
}

REVALO = Path(__file__).resolve().parents[2] / "revalorisation"
_NUM = r"\d{1,3}(?: \d{3})*"


def _norm(text: str) -> str:
    """Раскладка pdftotext: переводы строк, табуляции, разрыв «d e» (dss-2021-247, PROVENANCE)."""
    text = re.sub(r"[\s  ]+", " ", text)
    return text.replace("plafond de base d e ", "plafond de base de ")


def _int(num: str) -> int:
    return int(num.replace(" ", ""))


def _money(num: str) -> str:
    return str(Decimal(num.replace(" ", "").replace(",", ".")))


def fragments() -> dict[str, str]:
    """Тексты фрагментов fr.css.revalorisation (закреплённые байты с content_hash)."""
    source = (REVALO / "01-sources.law").read_text(encoding="utf-8")
    return {name: _norm(text) for name, text in
            re.findall(r'pub fragment (\w+) in \w+ \{.*?text fr official """(.*?)""";', source, re.S)}


def bmaf_table() -> dict[str, tuple[str, str]]:
    """Месяц начала → (BMAF, происхождение)."""
    frags = fragments()
    table: dict[str, tuple[str, str]] = {}
    for name, text in frags.items():
        for year, amount in re.findall(rf"à compter du 1er avril (\d{{4}}) : ({_NUM},\d+) €", text):
            table[f"{year}-04"] = (_money(amount), name)
    for name, text in frags.items():
        # Цитата прежней базы в инструкции следующего года: «porté de A € à B € au 1er avril N».
        for before, after, year in re.findall(rf"porté de ({_NUM},\d+) € à ({_NUM},\d+) € au 1er avril (\d{{4}})", text):
            assert table[f"{year}-04"][0] == _money(after), (name, year)
            table.setdefault(f"{int(year) - 1}-04", (_money(before), f"{name} (цитата)"))
        # «sera maintenu à A € à compter du 1er avril N»: база до N-04 та же (DSS_SD2B_2015_92_COEFF).
        for amount, year in re.findall(rf"maintenu à ({_NUM},\d+) € à compter du 1er avril (\d{{4}})", text):
            assert table[f"{year}-04"][0] == _money(amount), (name, year)
            table.setdefault(f"{int(year) - 1}-04", (_money(amount), f"{name} (maintenu)"))
    # Ступень 01.07.2022: построена правилом пакета, проверена его сценарием.
    scenario = (REVALO / "tests/bmaf-chaine-2022-07.lawtest").read_text(encoding="utf-8")
    previous = re.search(r"bmaf_precedente\([^,]+, ([\d.]+) EUR\)", scenario).group(1)
    coefficient = re.search(r"coefficient_annee\([^,]+, ([\d.]+)\)", scenario).group(1)
    built = re.search(r"bmaf_revalorisee\([^,]+, ([\d.]+) EUR\)", scenario).group(1)
    assert "legal_time @2022-07-01" in scenario and table["2022-04"][0] == previous
    assert f"coefficient égal à {coefficient.replace('.', ',')}" in frags["LOI_2022_1158_ART9"]
    table["2022-07"] = (built, "LOI_2022_1158_ART9 × DSS_2B_2022_82_BMAF, сценарий revalorisation bmaf-chaine-2022-07")
    return table


def bmaf(period: str) -> tuple[str, str]:
    """BMAF на месяц права: последняя ревалоризация не позже месяца."""
    table = bmaf_table()
    keys = [k for k in sorted(table) if k <= period]
    if not keys:
        raise LookupError(f"BMAF на {period} не закреплена в fr.css.revalorisation")
    return table[keys[-1]]


def plafonds_af() -> dict[int, tuple[int, int, int, str]]:
    """Год → (база I, база II, надбавка за ребёнка, происхождение) по фрагментам PLAFOND_AF."""
    frags = fragments()
    table: dict[int, tuple[int, int, int, str]] = {}
    for name, text in frags.items():
        if not name.endswith("_PLAFOND_AF"):
            continue
        year = int(re.search(r"du 1er janvier (\d{4}) au 31 décembre \1", text).group(1))
        pairs = re.findall(rf"plafond de base de ({_NUM})(?: (?:€|euros))?,? majoré de ({_NUM}) (?:€|euros) par enfant", text)
        bases = sorted({_int(b) for b, _ in pairs})
        increments = {_int(m) for _, m in pairs}
        assert len(bases) == 2 and len(increments) == 1, (name, pairs)
        increment = increments.pop()
        # Сверка разбора со строкой таблицы «2 enfants ≤ X» (не вычисление, а контроль чтения).
        row = re.search(rf"2 enfants ≤ ({_NUM})", text)
        assert row and _int(row.group(1)) == bases[0] + 2 * increment, name
        table[year] = (bases[0], bases[1], increment, name)
    for name, text in frags.items():
        for same, later in re.findall(r"période du 1er janvier (\d{4}) au 31 décembre \1, sont reconduits à l.identique "
                                      r"pour la période du 1er janvier (\d{4})", text):
            b1, b2, inc, origin = table[int(later)]
            table.setdefault(int(same), (b1, b2, inc, f"{origin} через {name}"))
    return table


def money(value) -> str:
    amount = Decimal(repr(value)) if isinstance(value, float) else Decimal(str(value))
    return format(amount.quantize(Decimal("0.01")) if amount == amount.quantize(Decimal("0.01")) else amount, "f")


def members(ctx, key: str) -> list[str]:
    return list((ctx.item["input"].get("famille") or {}).get(key) or [])


def birth(ctx, person: dict, index: int, births) -> str:
    """Дата рождения ребёнка: их факт; если дан только возраст — середина совместимого окна.

    Возраст A на 1-е число месяца права M означает рождение в (M − A − 1 год, M − A].
    Пороги, которые читают правила (14 и 20 лет R. 521-1 / L. 512-3, старшинство
    L. 521-3), — целые годы на 1-е число месяца и порядок по возрасту, поэтому
    выбор даты внутри окна исхода не меняет. Исключение — граница 01.03.2012
    декрета 2026-138 (не целый возраст): там дата обязательна (см. facts).
    """
    if "date_naissance" in person:
        return str(births[index])[:10]
    age = person["age"]
    age = int(next(iter(age.values()))) if isinstance(age, dict) else int(age)
    year, month = int(ctx.period[:4]) - age - 1, int(ctx.period[5:7]) + 6
    if month > 12:
        year, month = year + 1, month - 12
    return f"{year:04d}-{month:02d}-01"


def facts(ctx) -> list[str]:
    if ctx.value("residence_dom"):
        raise ctx.Skip("ménage en DOM: перенос заведён для метрополии")
    children = members(ctx, "enfants")
    people = ctx.item["input"]["individus"]
    undated = [c for c in children if "date_naissance" not in (people.get(c) or {})]
    if undated and ctx.period >= "2026-03":
        # Их дело проверяет их приближение даты по возрасту («fallback age seul»);
        # декрет 2026-138 решает по дате рождения относительно 01.03.2012 — у нас
        # это факт, не приближение.
        raise ctx.Skip("дата рождения ребёнка не задана: их приближение по возрасту — свойство их модели")
    if any("age" not in (people.get(c) or {}) for c in undated):
        raise ctx.Skip("ни даты рождения, ни возраста ребёнка")
    names = list(ctx.item["input"]["individus"])
    births = ctx.values("date_naissance")
    alternee = ctx.values("garde_alternee")
    try:
        base, _ = bmaf(ctx.period)
    except LookupError as why:
        raise ctx.Skip(str(why))
    ressources = ctx.value("prestations_familiales_base_ressources")
    out = [f"territoire({{main}}, METROPOLE)",
           f"nb_enfants_charge({{main}}, {ctx.value('af_nbenf')})",
           f"ressources_menage({{main}}, {money(ressources)} EUR)",
           f"bmaf_retenu({{main}}, {base} EUR)",
           "foyer_du_cas({main})",
           f"mois_droit(@{ctx.period}-01)"]
    # Счета, которые движок не сворачивает (B-PFAF-COMPTAGE): число majorations по
    # детям и итог forfait устанавливает фонд. Здесь фонд — их прогон: счёт детей с
    # ненулевой их majoration (полная/половинная по garde_alternee), как af_nbenf.
    # Право ребёнка на majoration сверка `af` поэтому не проверяет — это делают дела
    # af_majoration_age_2026 (цель af_majoration по ребёнку).
    if ctx.value("af_allocation_forfaitaire"):
        raise ctx.Skip("allocation forfaitaire: итог по детям — свёртка (B-PFAF-COMPTAGE), сумма не переносится")
    majorations = ctx.values("af_majoration_enfant")
    pleines = sum(1 for c in children if majorations[names.index(c)] and not alternee[names.index(c)])
    demi = sum(1 for c in children if majorations[names.index(c)] and alternee[names.index(c)])
    out += [f"nb_majorations_pleines({{main}}, {pleines})",
            f"nb_majorations_demi({{main}}, {demi})",
            "forfait_total_menage({main}, 0 EUR)",
            "nb_enfants_ase_service({main}, 0)"]
    year = int(ctx.period[:4])
    if year >= 2016:
        # D. 521-3 III: плафоны года права — суммы, опубликованные на 1 января этого года.
        table = plafonds_af()
        if year not in table:
            raise ctx.Skip(f"плафоны D. 521-3 на {year} не закреплены в fr.css.revalorisation")
        b1, b2, inc, _ = table[year]
        out += [f"plafond_base_tranche1_publie({{main}}, {b1} EUR)",
                f"plafond_base_tranche2_publie({{main}}, {b2} EUR)",
                f"majoration_plafond_enfant_publiee({{main}}, {inc} EUR)"]
    for child in children:
        index = names.index(child)
        born = birth(ctx, people.get(child) or {}, index, births)
        mode = "RESIDENCE_ALTERNEE_PARTAGE" if alternee[index] else "CHARGE_EFFECTIVE_PERMANENTE"
        out += [f"fr.pf.core::parent_charge({{main}}, {{m:{child}}})",
                f"fr.pf.core::enfant_ouvre_droit({{m:{child}}})",
                f"date_naissance({{m:{child}}}, @{born})",
                f"enfant_du_cas({{m:{child}}})",
                f"garde({{m:{child}}}, {mode})"]
    return out
