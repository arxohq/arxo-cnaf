"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.pf.asf (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Нормативная сумма пакета — BMAF на месяц права
(`bmaf_retenu`, R. 523-7 — проценты от неё): закреплённые фрагменты пакета
fr.css.revalorisation, общий разбор hook-а fr.pf.af (`pf-af/tools/openfisca_hook.py`).

Охват: производящие правила пакета действуют с 2021-01-01 (D-01, README), а их
шесть дел — 2015-01, 2018-04 и 2020-01; COVERAGE_START не объявлен, реестр
относит дела к классу (в) «дата». Закреплённые редакции CSS до 2021 года в
пакете есть (`01-sources.law`, CSS_ED2014_04 …), но правила их не исполняют —
продление охвата назад — работа над пакетом, а не над переносом.

Вторая граница — основание ASF (R. 523-1: сиротство, неуплата алиментов,
частичная уплата): у пакета это факт `motif_asf` ребёнка, у них основания нет
(их `asf_elig_enfant` — вычисленный признак). Дело без основания не переносится.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

PACKAGE = {"package": "fr.pf.asf", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:pf-asf",
           "prefix": "fr-pf-asf", "timezone": "Europe/Paris", "world": ["fr.pf.asf", "fr.pf.core"],
           "resolve": ["fr.pf.asf", "fr.pf.core"], "context": "deadline_policy PAIEMENT_MENSUEL;"}

#: Их итог `asf` — сумма по детям; у пакета `asf_montant_du(e, …)` на ребёнка: цель ставится
#: на ребёнка их переменной уровня члена, если она будет снята (сейчас дела вне охвата).
TARGETS = {
    "asf": {"predicate": "asf_montant_du", "kind": "Money"},
}

QUALIFIED: dict = {}

_spec = importlib.util.spec_from_file_location(
    "pf_af_openfisca_hook", Path(__file__).resolve().parents[2] / "pf-af/tools/openfisca_hook.py")
AF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AF)


def members(ctx, key: str) -> list[str]:
    return list((ctx.item["input"].get("famille") or {}).get(key) or [])


def facts(ctx) -> list[str]:
    if ctx.value("residence_dom"):
        raise ctx.Skip("ménage en DOM: перенос заведён для метрополии")
    try:
        AF.bmaf(ctx.period)
    except LookupError as why:
        raise ctx.Skip(str(why))
    # Основание R. 523-1 (`motif_asf`) их дело не задаёт: без него правила открытия молчат.
    raise ctx.Skip("основание ASF (R. 523-1: сиротство / неуплата / частичная уплата) в их деле не задано")
