"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.css.aah (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Из их прогона берутся ФАКТЫ дела: признанное право
(`aah_eligible`, `taux_incapacite`, RSDAE), en_couple, af_nbenf, режим ресурсов
(их `en_activite`: salaire_imposable месяца или rpns прошлого года) и базы
ресурсов (`aah_base_ressources_conjugalisee` / `_deconjugalisee`) — механика
ресурсов у нас граница B-AAH-RESSOURCES-CALCUL, базы входят фактом дела.
Их суммы (`aah`, `aah_base`) — только цели.

НОРМАТИВНОЕ ЧИСЛО. Месячный размер AAH (L. 821-3-1: «fixé par décret», ревалоризация
1 апреля коэффициентом L. 161-25) пакет строит сам — `07-montant-chaine.law`: числа
декретов 2019-1047 … 2026-229, коэффициенты инструкций DSS и ст. 9 закона 2022-1158
закреплены в sources/montant/ (tools/pin_montant.py). Дело размер НЕ подаёт: наш
montant_aah_applicable берётся по дате права (legal_time дела — 15-е число месяца
дела). Окно 01.07.2022 — 31.03.2023 не имеет числа декрета, сумма там — прочтение
D-82 (округление произведения до сантима HALF_UP, практика касс), оно выбирается в
context каждого дела. Деления «douzième» / «tiers» D. 821-2 al. 3 (неточное частное) — прочтение
DouziemeTiersArrondiCentime (D-82, D-83: до сантима HALF_UP, практика касс), тоже выбирается в context. Их параметр `prestations_etat_de_sante.invalidite.aah.montant` в
дело не подставляется — это только их ожидание.

ОХВАТ. COVERAGE_START не объявляется: правила пакета открыты с 2021-01-01
(02-droit … 04-deconjugalisation: `effective [@2021-01-01, …)`), каталог
sources/editions начинается CSS_ED2021_01; «закреплённые окна» реестра до 2021
(CSS_D821_5_PRE2023 с 2007, CSS_L821_2_PRE2024 с 2008, CSS_D821_2_PRE2023 с
2019-10, CSS_L821_3_PRE2021 с 2019-12) — лишь начала прежних редакций, которые
действовали ещё в 2021: L. 821-1 закреплена только с 2020-07-01. Размер AAH закреплён
с 2019-11, но правила пакета открыты с 2021-01-01. 55 дел 2004–2019 — (в) по дате.

ЦЕЛИ. `aah` и `aah_base` (уровень Individu) → наш aah_montant_du на каждого
родителя дела (per_member по famille.parents); дело без famille (плоский вход
одного индивида) — цель на {main}. Базы ресурсов (`aah_base_ressources_*`) нашей
цели не имеют: их вычисление — граница B-AAH-RESSOURCES-CALCUL.
"""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

PACKAGE = {"package": "fr.css.aah", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:aah",
           "prefix": "fr-css-aah", "timezone": "Europe/Paris",
           "world": ["fr.css.aah"], "resolve": ["fr.css.aah"],
           "context": "interpretation AahRevalorisationArrondiCentime; interpretation DouziemeTiersArrondiCentime;"}

QUALIFIED: dict[str, dict] = {}

def _tolerate_periodless_rows() -> None:
    """Обход двух дефектов драйвера (сам драйвер не правится). Первый: строка реестра
    complement_aah.yaml#5 несёт source_period.start_date = null, а extract()
    берёт `row["source_period"].get("start_date", "")[:7]` до проверки охвата и
    падает TypeError на всём пакете. Пустая дата сохраняет смысл драйвера
    («вне охвата»); исполняется только при загрузке hook из драйвера."""
    import sys
    driver = sys.modules.get("__main__")
    original = getattr(driver, "coverage_rows", None)
    if original is None or getattr(original, "_periodless_ok", False):
        return

    def rows(package):
        out = original(package)
        for row in out:
            period = dict(row.get("source_period") or {})
            if period.get("start_date") is None:
                period["start_date"] = ""
            # Второй дефект: record["period"] = raw «month:2022-05» (aah.yaml #24…#30),
            # а emit строит из него legal_time @month:2022-05-15 — тест не разбирается.
            if isinstance(period.get("raw"), str) and period["raw"].startswith("month:"):
                period["raw"] = period["raw"][len("month:"):]
            row["source_period"] = period
        return out
    rows._periodless_ok = True
    driver.coverage_rows = rows


_tolerate_periodless_rows()

#: Плоский ли вход текущего дела (ставит facts(); драйвер берёт цель после фактов).
_STATE = {"flat": False}


class _Targets(dict):
    """Цель на члена семьи (per_member) или на единственного индивида плоского дела."""

    def get(self, key, default=None):
        spec = super().get(key, default)
        if spec is None or not _STATE["flat"]:
            return spec
        return {k: v for k, v in spec.items() if k != "per_member"}


TARGETS = _Targets({
    variable: {"predicate": "aah_montant_du", "kind": "Money", "subject": "{main}",
               "per_member": {"of": variable, "members": "parents",
                              "predicate": "aah_montant_du", "kind": "Money"}}
    for variable in ("aah", "aah_base")
})

def members(ctx, key: str) -> list[str]:
    return list((ctx.item["input"].get("famille") or {}).get(key) or [])


def _cents(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP)


def facts(ctx) -> list[str]:
    outputs = set(ctx.item.get("output") or {})
    if not outputs & {"aah", "aah_base"}:
        raise ctx.Skip("цели — только базы ресурсов AAH: механика R. 532-3 / R. 821-4 / D. 821-6…10 "
                       "вне модели (B-AAH-RESSOURCES-CALCUL), нашей цели нет")
    individus = ctx.item["input"].get("individus")
    _STATE["flat"] = individus is None
    if individus is None:
        people = {"{main}": 0}
    else:
        names = list(individus)
        parents = members(ctx, "parents")
        if not parents:
            raise ctx.Skip("нет famille.parents: заявитель дела не назван")
        people = {f"{{m:{p}}}": names.index(p) for p in parents}
    month = ctx.period
    reform = month >= "2023-10"
    year_before = str(int(month[:4]) - 1)
    eligible = ctx.values("aah_eligible")
    taux = ctx.values("taux_incapacite")
    rsdae = ctx.values("aah_restriction_substantielle_durable_acces_emploi")
    conj = ctx.values("aah_base_ressources_conjugalisee")
    deconj = ctx.values("aah_base_ressources_deconjugalisee") if reform else None
    maintien = ctx.values("aah_conjugalise_eligible")
    salaire = ctx.values("salaire_imposable")
    rpns = ctx.values("rpns_imposables", year_before)
    non_cumulable = ctx.values("aah_base_non_cumulable")
    base, final = ctx.values("aah_base"), ctx.values("aah")
    couple = bool(ctx.value("en_couple"))
    given_eligible = individus is not None and any(
        "aah_eligible" in (individus.get(name) or {}) for name in individus)
    out = [f"enfants_charge({int(ctx.value('af_nbenf'))})"]
    for subject, i in people.items():
        if non_cumulable[i]:
            raise ctx.Skip("pension/ASI в aah_base_non_cumulable: координация L. 821-1 al. 9-11 вне модели (B-AAH-VIEILLESSE)")
        if abs(base[i] - final[i]) > 0.005:
            raise ctx.Skip("их сокращение за госпитализацию/заключение: L. 821-6 вне модели (B-AAH-HEBERGEMENT)")
        if eligible[i]:
            # Их aah_eligible — признанное право: у нас установленные факты решения
            # commission (L. 821-4) и условия L. 821-1 al. 1 (возраст, резиденция, пребывание).
            if given_eligible or taux[i] >= 0.8:
                out.append(f"decision_cdaph_80({subject})")
            else:
                out.append(f"decision_cdaph_50_79({subject})")
                if rsdae[i]:
                    out.append(f"rsdae_reconnue({subject})")
            out += [f"age_droit_depasse({subject})", f"residence_permanente({subject})",
                    f"sejour_regulier({subject})"]
        out.append(f"sans_esat({subject})")
        out.append(f"{'en_couple' if couple else 'personne_seule'}({subject})")
        # Их ресурсы — месячные (база/12); наш трек: годовой ×12 (R. 821-4) или
        # квартальный ×3 (R. 821-4-1) по их же признаку en_activite.
        own = _cents(deconj[i]) if reform else _cents(conj[i])
        spouse = _cents(conj[i]) - own if reform else Decimal("0.00")
        active = salaire[i] > 0 or rpns[i] > 0
        factor = 3 if active else 12
        out.append(f"{'percoit_revenu_activite' if active else 'sans_revenu_activite'}({subject})")
        regime = "ressources_trimestrielles_retenues" if active else "ressources_annuelles_retenues"
        out.append(f"{regime}({subject}, {own * factor} EUR)")
        if couple:
            # До реформы их база уже содержит долю супруга (assiette_conjoint):
            # сумма r1 + r2 правила MontantAncien* та же при r2 = 0.
            out.append(f"ressources_conjoint_retenues({subject}, {spouse * factor} EUR)")
        if reform and maintien[i]:
            out.append(f"beneficiaire_au_1er_octobre_2023({subject})")
    return out
