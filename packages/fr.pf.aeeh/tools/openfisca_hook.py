"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.pf.aeeh (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Из их прогона берутся ФАКТЫ дела (состав семьи, их флаг
`handicap`, уровень `aeeh_niveau_handicap`, en_couple), а не их суммы. BMAF —
наше закреплённое число: строка «Base mensuelle de calcul des allocations
familiales à compter du 1er avril YYYY : X €» циркуляров DSS в
corpus/laws/fr/revalorisation/sources/ (как в hook пакета fr.pf.af).

Охват. Реестр даёт пакету coverage_start 2021-01-01. Редакции D. 541-1/2 закреплены
с 2006-01-01 (правила 02-droit-montant открыты с 2006), но BMAF закреплена лишь с
1 апреля 2022 (DSS/2B/2022/82): на 2012-01 суммы у нас нет, поэтому COVERAGE_START
не объявляется и два дела 2012-01 остаются (в) по дате.

Цель. Их `aeeh` — сумма по семье (Famille); переменной уровня ребёнка у них нет.
В охвате одно дело с одним ребёнком: их сумма = сумма на ребёнка, наша цель —
aeeh_montant_total ребёнка (aeeh_montant_servi с округлением открыт лишь
с 2026-04-01). Несколько детей — Skip (сверка суммы семьи не на ребёнка).
"""
from __future__ import annotations

import re
from pathlib import Path

PACKAGE = {"package": "fr.pf.aeeh", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:pf-aeeh",
           "prefix": "fr-pf-aeeh", "timezone": "Europe/Paris",
           "world": ["fr.pf.aeeh", "fr.pf.core"], "resolve": ["fr.pf.aeeh", "fr.pf.core"],
           "context": ""}

TARGETS = {
    # Субъект — ребёнок дела; members() проверяет, что он единственный.
    "aeeh": {"predicate": "aeeh_montant_total", "kind": "Money", "subject": "{m:enfant1}"},
}

QUALIFIED: dict[str, dict] = {}

DSS = Path(__file__).resolve().parents[2] / "revalorisation/sources"
_BMAF = re.compile(r"Base mensuelle de calcul des allocations familiales à compter du 1er avril (\d{4}) : ([\d ]+,\d\d) €")


def bmaf(period: str) -> str:
    """BMAF на месяц права: последняя ревалоризация 1 апреля не позже месяца."""
    table = {}
    for path in sorted(DSS.glob("dss-*.txt")):
        for year, amount in _BMAF.findall(path.read_text(encoding="utf-8")):
            table[f"{year}-04"] = amount.replace(" ", "").replace(",", ".")
    keys = [k for k in sorted(table) if k <= period]
    if not keys:
        raise LookupError(f"BMAF на {period} не закреплена в revalorisation/sources")
    # Ряд закреплён с 2022-04: месяц раньше следующей ступени берёт предыдущую,
    # только если она сама закреплена (2022-01 → нет ступени 2021-04 → отказ).
    return table[keys[-1]]


def members(ctx, key: str) -> list[str]:
    return list(ctx.item["input"]["famille"].get(key) or [])


def facts(ctx) -> list[str]:
    famille = ctx.item["input"].get("famille") or {}
    children, parents = list(famille.get("enfants") or []), list(famille.get("parents") or [])
    if children != ["enfant1"]:
        raise ctx.Skip("не один ребёнок enfant1: их `aeeh` — сумма семьи, наша цель — на ребёнка")
    names = list(ctx.item["input"]["individus"])
    index = names.index("enfant1")
    if not ctx.values("handicap")[index]:
        raise ctx.Skip("ребёнок без их флага handicap: дело не о праве")
    if ctx.values("aeeh_niveau_handicap")[index]:
        # Их формула даёт MPI на категориях 2–6 по одному isole; D. 541-3 требует
        # ещё основание complément (contrainte d'activité / tierce) — их входа нет.
        raise ctx.Skip("категория complément задана: основание D. 541-3 (contrainte activité) у них не входит в дело")
    # Возрастная граница — их `age_maximum_enfant` (L. 541-1 «âge ... fixé»);
    # у нас право — на решении commission, возраст в голову не входит.
    if not (ctx.values("age")[index] < 20):
        raise ctx.Skip("ребёнок старше их возрастной границы: у нас граница — решение commission")
    try:
        base = bmaf(ctx.period)
    except LookupError as why:
        raise ctx.Skip(str(why))
    out = []
    for parent in parents:
        out.append(f"fr.pf.core::parent_charge({{m:{parent}}}, {{m:enfant1}})")
    # Их `handicap: true` без уровня — признанное право на базу: у нас — установленный
    # факт решения commission (L. 541-2, канал DECISION-0194 №2).
    out += ["decision_cdaph_favorable({m:enfant1})",
            f"bmaf_retenue({{m:enfant1}}, {base} EUR)",
            "sans_complement({m:enfant1})",
            "sans_mpi({m:enfant1})"]
    if not ctx.value("en_couple") and parents:
        out.append(f"personne_isolee({{m:{parents[0]}}})")
    return out
