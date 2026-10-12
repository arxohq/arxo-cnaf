"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.pf.cf (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Из их прогона берутся ФАКТЫ дела (состав, возраст детей,
ресурсы по R. 532-3, число детей, открывающих право), а не их суммы. Нормативные
суммы — только закреплённые байты:

* плафоны CF и montant majoré (D-83, образец D-81): база и надбавки — опубликованные
  порознь суммы инструкции DSS на 1 января года права, срезы `sources/dss-plafonds/`
  (`tools/pin_plafonds_dss.py`; 2016 = 2017 по абзацу «reconduits à l'identique»):
  `plafond_base_cf`, `majoration_enfant_cf`, `majoration_troisieme_cf`,
  `majoration_biactivite` и `plafond_base_majore`, `majoration_enfant_majore`,
  `majoration_troisieme_majore`, `majoration_biactivite_majore`;
* `bmaf_retenu` — BMAF на месяц права (разбор hook-а fr.pf.af, фрагменты revalorisation);
* PASS — не факт hook-а: пакет строит его сам из закреплённого arrêté года отсчёта
  (пакет `fr.css.pass`, D-84; мост — правило `PassReferenceArrete` в `07-pass.law`), hook
  называет только год отсчёта ресурсов (N−2, `annee_reference_ressources`).

Граница переноса — двойная активность (R. 522-2 al. 3, `pf-cf/sources/css/R522-2.txt:4`):
порог — 13,6 % PASS на 1 января года отсчёта N−2. Пакет `fr.css.pass` закрепляет arrêtés
на 2015–2026 годы без пропусков (B-PASS-2017 снята, 08.10.2026), годы читаются из его учёта
(`pass_years`), поэтому пара, где у обоих родителей есть доход N−2, переносится для любого года
права, у которого N−2 лежит в 2015–2026; для N−2 вне ряда замкнутость `CoupleBiactifEstClos` дала бы ложное «не биактивна»,
и дело «не переносится». Их код решает биактивность иначе: 12 × BMAF года N−2
(`base_ressource.py`, `biactivite`); расхождение на деле — класс (б).

Цель `cf` — их итог по двум дорожкам (D. 522-1 база / D. 522-2 повышенная); у пакета
дорожки — разные отношения (`cf_montant_du`, `cf_majore_du`, D-39(a)), поэтому шаблон цели
берёт любую из них (`or`), а не только базу, как в сессии 2.
"""
from __future__ import annotations

import importlib.util
import json
import re
from decimal import Decimal
from pathlib import Path

PACKAGE = {"package": "fr.pf.cf", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:pf-cf",
           "prefix": "fr-pf-cf", "timezone": "Europe/Paris", "world": ["fr.pf.cf", "fr.pf.core", "fr.css.pass"],
           "resolve": ["fr.pf.cf", "fr.pf.core", "fr.css.pass"], "context": "deadline_policy AGE_ATTEINT;"}

#: Правила метрополии действуют с 2018-01-01 (effective в 02–04); реестр объявлял 2021-01.
COVERAGE_START = "2018-01"

#: Их `cf` — итог одной из двух дорожек (cf_montant = базовая или повышенная, D-39(a) у нас:
#: взаимоисключающие). Шаблон сравнивает их число с тем, что дорожки дают вместе: ни одной
#: выплаты нет — «у обоих нет выплаты».
TARGETS = {
    "cf": {"predicate": "cf_montant_du", "kind": "Money",
           "pattern": "(cf_montant_du({subject}, v) or cf_majore_du({subject}, v))"},
}

QUALIFIED: dict = {}

_spec = importlib.util.spec_from_file_location(
    "pf_af_openfisca_hook", Path(__file__).resolve().parents[2] / "pf-af/tools/openfisca_hook.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)


SOURCES = Path(__file__).resolve().parents[1] / "sources"
PASS_SOURCES = Path(__file__).resolve().parents[2] / "pass/sources"


def plafonds_cf() -> dict[int, dict[str, tuple[int, int, int, int, str]]]:
    """Год → дорожка («cf», «majore») → (база, 25 %, 30 %, двойная активность, происхождение).

    Числа читаются из закреплённых срезов инструкций DSS (`sources/dss-plafonds/manifest.json`),
    разобранных `tools/pin_plafonds_dss.py`; 2016 — как 2017 (абзац reconduction).
    """
    manifest = json.loads((SOURCES / "dss-plafonds/manifest.json").read_text(encoding="utf-8"))
    table: dict[int, dict[str, tuple[int, int, int, int, str]]] = {}
    for row in manifest["texts"]:
        if row["kind"] in ("cf", "majore"):
            table.setdefault(row["year"], {})[row["kind"]] = (
                row["base"], row["majoration_enfant"], row["majoration_troisieme"],
                row["majoration_biactivite"], row["name"])
    for row in manifest["texts"]:
        if row["kind"] == "reconduction":
            for kind, values in table[row["same_as_year"]].items():
                table.setdefault(row["year"], {})[kind] = values[:4] + (f"{values[4]} через {row['name']}",)
    return table


def pass_years() -> set[int]:
    """Годы, на которые закреплён arrêté о PASS (учёт пакета fr.css.pass, D-84)."""
    manifest = json.loads((PASS_SOURCES / "pass/manifest.json").read_text(encoding="utf-8"))
    return {row["year"] for row in manifest["texts"]}


def members(ctx, key: str) -> list[str]:
    return list((ctx.item["input"].get("famille") or {}).get(key) or [])


def facts(ctx) -> list[str]:
    if ctx.value("residence_dom"):
        raise ctx.Skip("ménage en DOM: перенос заведён для метрополии")
    parents, children = members(ctx, "parents"), members(ctx, "enfants")
    if not children:
        raise ctx.Skip("их дело без детей: проверка их промежуточной величины, не CF")
    people = ctx.item["input"]["individus"]
    names = list(people)
    n_2 = str(int(ctx.period[:4]) - 2)
    income_facts: list[str] = []
    if len(parents) == 2:
        # R. 522-2 al. 3: профессиональный доход каждого члена пары за год N−2 (R. 532-3).
        incomes = []
        for parent in parents:
            index = names.index(parent)
            income = (ctx.value("revenu_assimile_salaire_apres_abattements", period=n_2, index=index)
                      + ctx.value("rpns_imposables", period=n_2, index=index))
            incomes.append(income)
        if min(incomes) > 0:
            if int(n_2) not in pass_years():
                raise ctx.Skip(f"двойная активность (R. 522-2 al. 3): порог 13,6 % PASS {n_2}, arrêté на {n_2} не закреплён "
                               "в fr.css.pass (год вне ряда); их код — 12 × BMAF N−2")
            income_facts = [f"revenu_pro_min_couple({{main}}, {AF.money(min(incomes))} EUR)",
                            f"annee_reference_ressources({{main}}, {n_2})"]
    for child in children:
        person = people.get(child) or {}
        if "date_naissance" not in person and "age" not in person:
            raise ctx.Skip("ни даты рождения, ни возраста ребёнка")
    births = ctx.values("date_naissance")
    try:
        bmaf, _ = AF.bmaf(ctx.period)
    except LookupError as why:
        raise ctx.Skip(str(why))
    year = int(ctx.period[:4])
    table = plafonds_cf()
    if year not in table:
        raise ctx.Skip(f"плафоны CF на {year} не закреплены в sources/dss-plafonds")
    base, enfant, troisieme, double, _ = table[year]["cf"]
    base_m, enfant_m, troisieme_m, double_m, _ = table[year]["majore"]
    ressources = ctx.value("cf_base_ressources")
    # Счёт детей CF устанавливает фонд (B-PFCF-COMPTAGE): их сумма cf_enfant_eligible по детям.
    eligible = ctx.values("cf_enfant_eligible")
    nb = sum(1 for c in children if eligible[names.index(c)])
    out = [f"nb_enfants_cf({{main}}, {nb})",
           f"ressources_menage({{main}}, {AF.money(ressources)} EUR)",
           f"plafond_base_cf({{main}}, {base} EUR)",
           f"majoration_enfant_cf({{main}}, {enfant} EUR)",
           f"majoration_troisieme_cf({{main}}, {troisieme} EUR)",
           f"majoration_biactivite({{main}}, {double} EUR)",
           f"plafond_base_majore({{main}}, {base_m} EUR)",
           f"majoration_enfant_majore({{main}}, {enfant_m} EUR)",
           f"majoration_troisieme_majore({{main}}, {troisieme_m} EUR)",
           f"majoration_biactivite_majore({{main}}, {double_m} EUR)",
           f"bmaf_retenu({{main}}, {bmaf} EUR)",
           "foyer_du_cas({main})",
           "cadre_cf_remplie({main})",
           f"mois_droit(@{ctx.period}-01)"]
    out += income_facts
    if len(parents) == 1:
        out.append("parent_isole({main})")
    for child in children:
        index = names.index(child)
        birth = AF.birth(ctx, people.get(child) or {}, index, births)
        age_now = ctx.value("age", index=index)
        if age_now == 20:
            # R. 522-1: в 20 лет — условие вознаграждения (remuneration_sous_plafond); их факт не снят.
            raise ctx.Skip("ребёнок 20 лет: условие вознаграждения R. 522-1 не перенесено")
        out += [f"fr.pf.core::parent_charge({{main}}, {{m:{child}}})",
                f"date_naissance({{m:{child}}}, @{birth})",
                f"enfant_du_cas({{m:{child}}})"]
        if age_now < 20:
            # L. 512-3: ребёнок до 20 лет открывает право (статус fr.pf.core, факт дела).
            out.append(f"fr.pf.core::enfant_ouvre_droit({{m:{child}}})")
    return out
