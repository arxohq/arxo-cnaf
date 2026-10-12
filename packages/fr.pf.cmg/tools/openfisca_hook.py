"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.pf.cmg (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Факты дела берутся из их прогона (возраст детей, состав, ресурсы
по R. 532-3, флаги способа ухода, активность); нормативные числа — только закреплённые
байты (BMAF — fr.css.revalorisation; плафоны ресурсов CMG — инструкции DSS в
`revalorisation/sources/dss-*.txt`; номиналы D. 531-18-1/D. 531-20, ставки полос и порог
16 часов — параметры самого пакета `bareme/*.lawparam.json`).

Цель `paje_cmg` (D-85) и СТАДИЯ СВЕРКИ. Их `paje_cmg` (`paje.py`, `formula_2017_04_01`) —
не сумма к выплате, а «CMG maximal / intermédiaire / minimal» инструкций DSS: BMAF × доля
возраста (1 до трёх лет; 1 − `taux_reduit` = 1/2 от трёх до шести) × ставка полосы, выбранная
по `prestations_familiales_base_ressources` и по флагу способа ухода. Расходов на присмотр
(зарплата, часы, взносы) в их формуле нет, поэтому 85 % чистой зарплаты, часть взносов и
итог «a + b» (`montant_cmg_du`) сравнивать не с чем. Сверяется одна стадия — МАКСИМУМ полосы:

* `empl_dir` (их «Emploi direct», ставки 114,04 / 71,91 / 43,14 %) — прямой наём
  assistante maternelle, D. 531-18 2°: наш `maximum_ancien_b`;
* `ass_mat` (их ставки 172,57 / 143,81 / 115,05 % — в DSS это «association ou entreprise
  employant une assistante maternelle», D. 531-23): наш `maximum_structure` в режиме
  `STRUCTURE`; соответствие — по ставкам DSS, не по названию флага;
* `gar_dom` (их 208,53 / 179,76 / 151,00 %): у нас эти ставки — режим `EAJE`, право на
  который требует вместимости и тарифа 10 €/ч, которых в их деле нет, — не переносится.

Что в деле не хватает нам и поставлено как условие стадии, а не как измеренный факт:
`heures_remunerees = 16` (ancien D. 531-23 V, порог права STRUCTURE; их модель порога не
знает) — минимум, при котором право на максимум открыто.

Плафоны ресурсов. Пакет получает опубликованные базу и надбавку за ребёнка для обеих
границ из инструкции DSS на 1 января года права (ресурсы N−2). Для одинокого родителя
DSS печатает собственные округлённые базу и надбавку; их четыре значения предъявляются
отдельно от семейных, без множителя к номиналу. Hook проверяет строки таблицы против
«база + N × надбавка» и подаёт опубликованные составляющие как факты дела.

Формульные дела реестра (`tests/formulas/paje/paje_cmg.yaml` #0 — период 2017-04, #1 — 2018-04,
разбор 08.10.2026) остаются вне окна и не переносятся, класс (в) с датами:
1. Правила пакета действуют с 2021-01-01; старые редакции D. 531-17/-19/-22 (ed2012), D. 531-21
   (ed2015), D. 531-18 (ed2018) лишь закреплены, правил на 2017–2018 нет. BMAF закреплена в
   revalorisation только с 1 апреля 2022 (dss-2022-82.txt:169): их 407,84 € (2017-04) и 411,92 €
   (2018-04) у нас не закреплены; плафоны CMG на 2017–2018 тоже (ранняя инструкция — dss-2020-226
   на 01.01.2021). `COVERAGE_START = "2021-01"` — начало окна правил, драйвер пишет строку (в).
2. Период входа у них не определён: `salaire_imposable: 20000` и `age` заданы без периода и ложатся в
   месяц по умолчанию, а база ресурсов PF читает год N-2 (их `prestations_familiales_base_ressources`
   = 0 в обоих делах, снято их движком 08.10.2026); фактов ресурсов для переноса нет.
3. `ass_mat: 1` — только флаг; ни зарплаты, ни часов, ни взносов, их paje_cmg = 1,7257 × BMAF + 351,91
   (максимум + взносы) без входов, из которых строится наш расчёт.
Их `paje_base` из тех же дел принадлежит fr.pf.paje и тоже до 2021.

Границы переноса (каждая — Skip с причиной):
* после 2025-09 формула 2025 строится иначе (стоимость/потолок), их `paje_cmg` остаётся
  прежней — период вне стадии «максимум»;
* два и более ребёнка до шести лет: у них один максимум на семью (по самому младшему), у нас —
  на ребёнка;
* PreParE (`paje_prepare > 0`): они делят плафоны на два, у нас делится максимум (D. 531-21);
* два способа ухода сразу и garde à domicile; дело без способа ухода переносится (выплаты нет у обоих).
"""
from __future__ import annotations

import importlib.util
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

PACKAGE = {"package": "fr.pf.cmg", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:pf-cmg",
           "prefix": "fr-pf-cmg", "timezone": "Europe/Paris", "world": ["fr.pf.cmg", "fr.pf.core"],
           "resolve": ["fr.pf.cmg", "fr.pf.core"], "context": "deadline_policy CMG_MOIS_CALENDAIRE; interpretation ArrondiMaximumCmgCentime;"}

#: Начало окна правил пакета (самое раннее `effective [@2021-01-01, …)`); реестр не нашёл coverage_start.
COVERAGE_START = "2021-01"

#: Реформа 2025-09-01 (decrets 2025-514/515): формула 2025, прежних полос «максимум» уже нет.
REFORM = "2025-09"

#: Их `paje_cmg` — максимум полосы; у нас это `maximum_ancien_b` (emploi direct, D. 531-18 2°) или
#: `maximum_structure` (STRUCTURE, ancien D. 531-23). Оба отношения — пары «человек, ребёнок»,
#: поэтому субъект цели — пара: сравниваемого ребёнка hook всегда называет `{m:enfant}`
#: (их имя ребёнка не важно), а шаблон берёт любое из двух отношений (они исключают друг друга
#: по способу ухода). Квантор `exists` над ребёнком здесь не годится: оракул не понижает его в
#: `collect` с двумя отношениями.
TARGETS = {
    "paje_cmg": {"predicate": "maximum_ancien_b", "kind": "Money", "subject": "{main}, {m:enfant}",
                 "pattern": "(maximum_ancien_b({subject}, v) or maximum_structure({subject}, v))"},
}

QUALIFIED: dict = {}

_spec = importlib.util.spec_from_file_location(
    "pf_af_openfisca_hook", Path(__file__).resolve().parents[2] / "pf-af/tools/openfisca_hook.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)

PACKAGE_DIR = Path(__file__).resolve().parents[1]
REVALO_SOURCES = Path(__file__).resolve().parents[2] / "revalorisation/sources"
_NUM = r"\d{1,3}(?: \d{3})*"
_ROW = re.compile(rf"(\d) enfants? ≤ ({_NUM}) ≤ ({_NUM}) > ({_NUM})")
_NOTE = re.compile(rf"plafond de base d ?e ({_NUM}) (?:€|euros),? major. d ?e ({_NUM}) (?:€|euros)")
_SECTION = re.compile(r"Plafonds de ressources applicables au compl.ment de libre choix du mode de garde "
                      r"pour la p.riode du 1er janvier (\d{4}) au 31 d.cembre \1")


def base_age() -> int:
    """Возраст полной ставки — D. 531-1 «fixé à trois ans» (закреплён пакетом fr.pf.paje)."""
    text = (Path(__file__).resolve().parents[2] / "pf-paje/sources/fr-pf-paje/D531-1-ed2004.txt").read_text(encoding="utf-8")
    assert "est fixé à trois ans" in text
    return 3


def decimal_literal(value: Decimal) -> str:
    text = format(value, "f")
    return text if "." in text else text + ".0"


def parameter(name: str) -> Decimal:
    """Значение параметра пакета (`bareme/<имя>.lawparam.json`, единственная запись)."""
    data = json.loads((PACKAGE_DIR / "bareme" / f"{name}.lawparam.json").read_text(encoding="utf-8"))
    (entry,) = data["values"]
    return Decimal(str(entry["value"]["value"]))


def plafonds_cmg() -> dict[int, dict]:
    """Год права → {"normal"|"seule": ((база a, надбавка a), (база c, надбавка c)), "origin": файл DSS}.

    Таблицы 3.3.1 (семья) и 3.3.2 (одинокий родитель, +40 %) инструкции на 1 января года права
    печатают плафоны для N детей и в замечании NB называют базу и надбавку за ребёнка («plafond de
    base de A euros majoré de B euros par enfant à charge»). Берутся база и надбавка из NB, плафон на
    N детей = база + N × надбавка; строки таблицы «N enfants ≤ a ≤ c» служат контролем разбора
    (в части файлов pdftotext теряет строку — контроль идёт по тем, что напечатаны).
    """
    table: dict[int, dict] = {}
    for path in sorted(REVALO_SOURCES.glob("dss-*.txt")):
        text = AF._norm(path.read_text(encoding="utf-8"))
        found = _SECTION.search(text)
        if not found:
            continue
        year = int(found.group(1))
        segment = text[found.start():found.start() + 7000]
        pairs: list[tuple[int, int]] = []
        for base, step in _NOTE.findall(segment):
            pair = (int(base.replace(" ", "")), int(step.replace(" ", "")))
            if not pairs or pairs[-1] != pair:
                pairs.append(pair)
        if len(pairs) < 4:
            continue                      # таблицы без замечания NB (до 2021) не нужны: окно пакета с 2021
        entry = {"origin": path.name, "normal": (pairs[0], pairs[1]), "seule": (pairs[2], pairs[3])}
        rows = [(int(n), int(a.replace(" ", "")), int(c.replace(" ", "")))
                for n, a, c, _ in _ROW.findall(segment)]
        # Контроль разбора: строки первой таблицы (семья) обязаны совпасть с «база + N × надбавка».
        for n, a, c in rows[:4]:
            (base_a, step_a), (base_c, step_c) = entry["normal"]
            assert (base_a + n * step_a, base_c + n * step_c) == (a, c), (path.name, n)
        table[year] = entry
    return table


def published_plafonds(year: int, n: int, single: bool) -> tuple[int, int, str]:
    entry = plafonds_cmg()[year]
    (base_a, step_a), (base_c, step_c) = entry["seule" if single else "normal"]
    return base_a + n * step_a, base_c + n * step_c, entry["origin"]



def band(resources: Decimal, first, second) -> int:
    return 1 if resources <= first else 2 if resources <= second else 3


def members(ctx, key: str) -> list[str]:
    return list((ctx.item["input"].get("famille") or {}).get(key) or [])


def facts(ctx) -> list[str]:
    if ctx.period >= REFORM:
        raise ctx.Skip("с 2025-09 формула CMG другая (стоимость, потолок, taux d'effort); их paje_cmg остаётся "
                       "прежней «максимум полосы» — стадии для сверки нет")
    if ctx.value("residence_dom"):
        raise ctx.Skip("ménage en DOM: перенос заведён для метрополии")
    flags = {name: bool(ctx.value(name)) for name in ("empl_dir", "ass_mat", "gar_dom")}
    chosen = [name for name, on in flags.items() if on]
    if len(chosen) > 1:
        raise ctx.Skip(f"заданы несколько способов ухода ({', '.join(chosen)}): их paje_cmg складывает ставки, "
                       "у нас максимум на способ")
    if chosen == ["gar_dom"]:
        raise ctx.Skip("gar_dom: их ставки 208,53 / 179,76 / 151,00 % у нас — режим EAJE; право требует "
                       "вместимости и тарифа 10 €/ч, которых в их деле нет")
    parents, children = members(ctx, "parents"), members(ctx, "enfants")
    if not children:
        raise ctx.Skip("их дело без детей")
    people = ctx.item["input"]["individus"]
    names = list(people)
    ages = {child: ctx.value("age", index=names.index(child)) for child in children}
    young = [c for c in children if 0 <= ages[c] <= 5 and not ctx.value("autonomie_financiere", index=names.index(c))]
    if len(young) > 1:
        raise ctx.Skip("два и более ребёнка до шести лет: у них один максимум на семью (по самому младшему), "
                       "у нас — на ребёнка")
    prepare = ctx.value("paje_prepare")
    if prepare and prepare > 0:
        raise ctx.Skip("PreParE: они делят плафоны ресурсов на два, у нас делится максимум (D. 531-21) — "
                       "стадии разной формы")
    try:
        bmaf, _ = AF.bmaf(ctx.period)
    except LookupError as why:
        raise ctx.Skip(str(why))
    year, nb = int(ctx.period[:4]), int(ctx.value("af_nbenf"))
    if not young:
        child = min(children, key=lambda c: ages[c])      # возраст вне окна: у обоих нет CMG
    else:
        child = young[0]
    # Их float32 даёт хвост шума (58806.50390625): ресурсы берутся до сантима HALF_UP.
    resources = Decimal(str(ctx.value("prestations_familiales_base_ressources"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    out = [f"nb_enfants_charge({{main}}, {nb})",
           f"bmaf_retenu({{main}}, {bmaf} EUR)",
           f"ressources_annuelles({{main}}, {AF.money(resources)} EUR)",
           f"fr.pf.core::parent_charge({{main}}, {{m:enfant}})",
           f"age_revolu_ans({{m:enfant}}, {ages[child]})",
           f"age_base_ans({{m:enfant}}, {base_age()})"]
    # L. 531-5 IV: third birthdays in January–August keep the full rate through August.
    # Age in completed years alone cannot distinguish those months; use the birth date of the
    # compared child, which is an actual OpenFisca case fact, and the month of entitlement.
    if ages[child] == 3:
        birth = str(ctx.value("date_naissance", index=names.index(child)))[:10]
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", birth):
            raise ctx.Skip("ребёнку 3 года, но дата рождения не установлена: L. 531-5 IV требует проверки продления до 31 августа")
        out.append(f"date_naissance({{m:enfant}}, @{birth})")
        out.append(f"mois_droit(@{ctx.period}-01)")
    single = len(parents) == 1
    if single:
        out.append("personne_seule({main})")
    # Опубликованные база и надбавка каждой полосы, для семьи и для isolement отдельно.
    if year not in plafonds_cmg():
        raise ctx.Skip(f"плафоны CMG на {year} не закреплены в revalorisation/sources/dss-*.txt")
    entry = plafonds_cmg()[year]
    for suffix, bands in (("", entry["normal"]), ("_isole", entry["seule"])):
        for band_name, (base, step) in zip(("a", "c"), bands):
            out.append(f"plafond_{band_name}_base{suffix}_publie({{main}}, {base} EUR)")
            out.append(f"plafond_{band_name}_enfant{suffix}_publie({{main}}, {step} EUR)")
    # Активность: их условие `not_(inactif) | aah > 0 | parent_etudiant`.
    inactive = bool(ctx.value("inactif"))
    if not inactive:
        out.append("exerce_activite({main})")
    else:
        aah = sum(ctx.value("aah", index=names.index(p)) for p in parents)
        student = any(ctx.value("etudiant", index=names.index(p)) for p in parents)
        if aah > 0 or student:
            out.append("dispense_activite({main})")
    if "empl_dir" in chosen:
        out.append(f"mode_garde({{main}}, {{m:enfant}}, ASSISTANT_MATERNEL)")
    elif "ass_mat" in chosen:
        out.append(f"mode_garde({{main}}, {{m:enfant}}, STRUCTURE)")
        out.append(f"heures_remunerees({{main}}, {{m:enfant}}, {decimal_literal(parameter('SeuilHeuresStructure16'))})")
    return out
