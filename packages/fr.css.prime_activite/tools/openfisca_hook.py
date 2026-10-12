"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.css.prime_activite (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Сумма prime d'activité в пакете (03-montant.law) строится из месячных входов
трёх трёхмесячных периодов R. 843-1 (M-3…M-1 до 28.02.2025, M-4…M-2 после). Что берётся откуда:

- МОНТАН ФОРФЕТ personne seule PPA НЕ подаётся: пакет строит его по МЕСЯЦУ из закреплённых декретов
  2020-491 … 2026-222, коэффициентов DSS и ст. 9 закона 2022-1158 (`11-forfait-chaine.law`,
  `tools/pin_forfait.py`; DECISION-0452). Окно 01.07.2022 — 31.03.2023 — сумма ст. 9, прочтение D-82
  (округление произведения до сантима HALF_UP), оно выбирается в context каждого дела; среднее за квартал R. 843-1 (PrimeMoyenneArrondieCentime) и линейная
  bonification D. 843-2 (BonificationLineaireArrondieCentime) — прочтения D-82/D-83 (до сантима HALF_UP,
  практика касс), тоже выбираются в context; так же выбирается RessourcesFractionsArrondiesCentime
  (D-82/D-84: двенадцатые и трети непосаженных/годовых доходов R. 845-1/2, до сантима HALF_UP) - дела hook
  подают месячные доходы готовыми (`revenus_pro_*`), поэтому на эти дела прочтение не влияет, но выбрано в context
  наравне с остальными, чтобы дело с фактами R. 845-1/2 считалось по практике касс;
- SMIC horaire месяца — факт `smic_horaire_retenu` из закреплённого ряда `fr.travail.smic`
  (`corpus/laws/fr/smic/tools/gen_serie_tests.py: acts()` читает закреплённые тексты актов; число в
  hook не набирается). Правило пакета не может спросить fr.travail.smic на месяц, отличный от
  даты права дела, поэтому месячный SMIC входит фактом (граница B-PPA-SMIC-MOIS);
- ПЛАНКА ВЫПЛАТЫ — 15 € из закреплённой D. 846-2 (`sources/css/D846-2.txt`), факт `minimum_paiement_retenu`;
- СОСТАВ ФОЙЕ месяца (`forme_foyer_retenue`) — из их nb_parents, rsa_nb_enfants, rsa_majore_eligibilite;
  формы вне перечня пакета (изолированный с тремя детьми и более, пара с четырьмя и более детьми,
  одинокий родитель без isolement) — «не переносится» с причиной;
- ДОХОДЫ: `revenus_pro_demandeur` / `revenus_pro_conjoint` — их `ppa_revenu_activite_individu` месяца;
  `ressources_hors_logement_retenues` — их `ppa_base_ressources` (активность + прочие ресурсы, включая
  семейные пособия по их расчёту: механика ресурсов — граница B-PPA-RESSOURCES-CALCUL);
- ЖИЛЬЁ (R. 844-3, R. 844-4 I): `aide_logement > 0` → AIDE и сумма aide_logement; жильё владельца без
  aide и бесплатное → NATURE; иначе SANS. Forfait logement пакет строит сам (`12-forfait-logement.law`),
  адаптер норму не складывает;
- ПРАВО (ppa_eligibilite) — условие права L. 842-2, не сумма: цель не переносится (skip_target).

Дело с их флагом departement_experimentation_rsa=true (окно M-2…M-4 с 10.2024, решение владельца,
граница B-RSA-EXPERIMENTATION-2024) остаётся «не переносится»: закреплённый R. 843-1 до 28.02.2025 —
M-3…M-1. Их числа — только ожидания; ни одно не попадает в факты дела.
"""
from __future__ import annotations

import importlib.util
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[4]      # .../corpus
PKG = Path(__file__).resolve().parents[1]

PACKAGE = {"package": "fr.css.prime_activite", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:ppa",
           "prefix": "fr-ppa", "timezone": "Europe/Paris", "world": ["fr.css.prime_activite"],
           "resolve": ["fr.css.prime_activite"],
           "context": ("deadline_policy PPA_MOIS; interpretation ForfaitRevalorisationArrondiCentime; "
                       "interpretation PrimeMoyenneArrondieCentime; interpretation BonificationLineaireArrondieCentime; "
                       "interpretation RessourcesFractionsArrondiesCentime;")}

# COVERAGE_START не объявляется: правила пакета действуют с 2021-01-01, первая
# редакция CSS — CSS_ED2021_01_01; реестр (2021-01) верен, дела 2015–2020 — (в).

TARGETS = {
    "ppa": {"predicate": "prime_due_trimestre", "kind": "Money"},
    "ppa_eligibilite": {"predicate": "droit_ouvert", "kind": "Boolean"},
}

QUALIFIED: dict[str, dict] = {}


def skip_target(ctx, variable) -> str | None:
    if variable == "ppa_eligibilite":
        return ("право на prime d'activité (L. 842-2, R. 842-1…5) — условие права, не сумма: этот hook подаёт "
                "факты суммы, факты права (возраст, резиденция, статус) он не снимает")
    return None


def _month_minus(period: str, k: int) -> str:
    year, month = map(int, period.split("-"))
    month -= k
    while month <= 0:
        month, year = month + 12, year - 1
    return f"{year:04d}-{month:02d}"


def _eur(value) -> str:
    """Их число как денежный факт: 4 знака (их float32 → вход дела, не норма), хвост нулей снят до сотых."""
    quantized = Decimal(str(value)).quantize(Decimal("0.0001"), ROUND_HALF_UP).normalize()
    text = format(quantized, "f")
    if "." not in text:
        return text + ".00 EUR"
    return (text + "0" if len(text.split(".")[1]) == 1 else text) + " EUR"


def _smic_series():
    """Часовой SMIC метрополии по закреплённым актам пакета fr.travail.smic (его же разбор текстов)."""
    path = CORPUS / "laws/fr/smic/tools/gen_serie_tests.py"
    spec = importlib.util.spec_from_file_location("smic_gen_serie_tests", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def smic_horaire(month: str) -> str:
    module = _smic_series()
    year, mon = map(int, month.split("-"))
    return module.active(module.acts(), date(year, mon, 1))["metro"]


def minimum_paiement() -> str:
    """Планка выплаты из закреплённой D. 846-2: «fixé à 15 euros»."""
    text = (PKG / "sources/css/D846-2.txt").read_text(encoding="utf-8")
    return re.search(r"fixé à (\d+(?:,\d+)?) euros", text).group(1).replace(",", ".")


def _forme(parents: int, enfants: int, majoree: bool, ctx) -> str:
    if parents == 2:
        forms = {0: "COUPLE", 1: "COUPLE_1E", 2: "COUPLE_2E", 3: "COUPLE_3E"}
        if enfants not in forms:
            raise ctx.Skip(f"пара с {enfants} детьми: формы пакета — до трёх детей (D. 843-1 al. 1)")
        return forms[enfants]
    if parents == 1:
        if majoree:
            forms = {0: "ISOLE", 1: "ISOLE_1E", 2: "ISOLE_2E"}
            if enfants not in forms:
                raise ctx.Skip(f"изолированный родитель с {enfants} детьми: формы пакета — до двух детей (D. 843-1 al. 2)")
            return forms[enfants]
        if enfants == 0:
            return "SEUL"
        raise ctx.Skip("одинокий родитель с детьми без их rsa_majore_eligibilite: формы SEUL с детьми в пакете нет")
    raise ctx.Skip(f"нет родителей в семье (nb_parents={parents})")


def facts(ctx) -> list[str]:
    item = ctx.item
    famille = item["input"].get("famille") or {}
    if famille.get("departement_experimentation_rsa") is True:
        raise ctx.Skip("их флаг departement_experimentation_rsa=true (окно M-2…M-4 с 10.2024): основание "
                       "эксперимента не закреплено (граница B-RSA-EXPERIMENTATION-2024), закреплённый R. 843-1 "
                       "до 28.02.2025 — M-3…M-1")
    lag = (4, 3, 2) if ctx.period >= "2025-03" else (3, 2, 1)
    refs = [_month_minus(ctx.period, k) for k in lag]
    individus = item["input"].get("individus")
    names = list(individus) if individus else []
    parents = [name for name in (famille.get("parents") or [])]
    index = {name: names.index(name) for name in parents} if individus else {}
    if individus and not parents:
        raise ctx.Skip("нет famille.parents: заявитель дела не назван")
    if not ctx.value("ppa_eligibilite_apprenants", ctx.period):
        raise ctx.Skip("их ppa_eligibilite_apprenants=false (учащийся/стажёр, L. 842-2 — условие права)")
    main = "{main}"
    out = []
    for ref in refs:
        if not ctx.value("ppa_eligibilite", ref):
            raise ctx.Skip(f"их ppa_eligibilite=false на {ref}: условие права L. 842-2, вне суммы")
        n_parents = int(ctx.value("nb_parents", ref))
        n_children = int(ctx.value("rsa_nb_enfants", ref))
        majoree = bool(ctx.value("rsa_majore_eligibilite", ref))
        out.append(f"forme_foyer_retenue({main}, @{ref}-01, {_forme(n_parents, n_children, majoree, ctx)})")
        revenue = ctx.values("ppa_revenu_activite_individu", ref)
        who = [index[name] for name in parents] if individus else [0]
        out.append(f"revenus_pro_demandeur({main}, @{ref}-01, {_eur(revenue[who[0]])})")
        if n_parents == 2:
            if len(who) < 2:
                raise ctx.Skip("nb_parents=2, но второй родитель не назван в famille.parents")
            out.append(f"revenus_pro_conjoint({main}, @{ref}-01, {_eur(revenue[who[1]])})")
        out.append(f"smic_horaire_retenu(@{ref}-01, {_eur(smic_horaire(ref))})")
        aide = float(ctx.value("aide_logement", ref))
        statut = ctx.values("statut_occupation_logement", ref)[0]
        loyer = float(ctx.value("loyer", ref)) if "loyer" in ctx.simulation.tax_benefit_system.variables else 0.0
        participation = float(ctx.value("participation_frais", ref))
        nature = ((statut in ("primo_accedant", "proprietaire")) and not loyer) or (
            statut == "loge_gratuitement" and not participation)
        if aide > 0 and nature:
            raise ctx.Skip(f"на {ref} у них и aide_logement>0, и жильё в натуре: их max(montant_al, montant_nature) "
                           "— R. 844-3 и R. 844-4 I исключают друг друга по тексту")
        if aide > 0:
            out.append(f"situation_logement_retenue({main}, @{ref}-01, AIDE)")
            out.append(f"aide_logement_retenue({main}, @{ref}-01, {_eur(aide)})")
        elif nature:
            out.append(f"situation_logement_retenue({main}, @{ref}-01, NATURE)")
        else:
            out.append(f"situation_logement_retenue({main}, @{ref}-01, SANS)")
        out.append(f"ressources_hors_logement_retenues({main}, @{ref}-01, {_eur(ctx.value('ppa_base_ressources', ref))})")
    out.append(f"mois_revue({main}, @{ctx.period}-01)")
    out.append(f"minimum_paiement_retenu(@{ctx.period}-01, {_eur(minimum_paiement())})")
    return out
