#!/usr/bin/env python3
"""PAJE bareme → A3 parameters of package `fr.pf.paje` (shared core
`corpus/tools/sources/bareme_builder.py`).

Thirteen rates from the pinned fragments, none taken from a third-party
implementation. The time axis is `legal_time` (month for which the benefit
is due). Wave-1 rates hold in every wording of the coverage window
[2021-01-01, ∞): one row per rate from the coverage start; no breaks.
Wave-3 base rates split by child cohort: the 2018 wording governs
pre-2018 children only until 01.04.2021 (NOTA of D. 531-3), hence the two
Ancien rows carry the window [2021-01-01, 2021-04-01).

    build_pf_paje_bareme.py            — rewrite the parameters
    build_pf_paje_bareme.py --check    — compare without writing anything
    build_pf_paje_bareme.py --check-anchors — each row number stands
        in its anchor fragment text (core + canary)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "sources"))

from bareme_builder import ParamSpec, canary, render_dataset  # noqa: E402

PACKAGE = Path(__file__).resolve().parents[1]
OUT = PACKAGE / "bareme"
NS = "urn:fr:corpus:clir:pf-paje"
DEC = {"name": "urn:law:std#Decimal"}
START = "2021-01-01"

# The shared builder only offers the `label_ru` slot and always renders the
# `"language": "ru"` tag with its own Russian row template, so the English
# descriptions travel through that slot and are retagged below (see
# _to_english). Values, windows and anchors — the semantics — are unaffected.
SPECS: list[ParamSpec] = [
    ParamSpec(
        name="TauxPrimeNaissance", value_type=DEC,
        windows=[(START, None)], values=["2.2975"],
        anchors=[["CSS_D531_2_ED2015_01", "CSS_D531_2_ED2021_04"]],
        label_fr="taux de la prime à la naissance: 229,75 % de la BMAF (D. 531-2, I)",
        label_ru="birth grant rate: 229.75% of the BMAF (D. 531-2, I)",
    ),
    ParamSpec(
        name="TauxPrimeAdoption", value_type=DEC,
        windows=[(START, None)], values=["4.595"],
        anchors=[["CSS_D531_2_ED2015_01", "CSS_D531_2_ED2021_04"]],
        label_fr="taux de la prime à l'adoption: 459,5 % de la BMAF (D. 531-2, I)",
        label_ru="adoption grant rate: 459.5% of the BMAF (D. 531-2, I)",
    ),
    ParamSpec(
        name="TauxPlafondPrime", value_type=DEC,
        windows=[(START, None)], values=["1.1947"],
        anchors=[["CSS_D531_3_1_ED2018_04"]],
        label_fr="plafond prime naissance/adoption: 119,47 % du plafond allocation de base taux plein (D. 531-3-1)",
        label_ru="birth/adoption grant ceiling: 119.47% of the full-rate base allowance ceiling (D. 531-3-1)",
    ),
    # Wave 3: base allowance rates. The 2018 wording (41.65% / 20.825%)
    # governs children born or adopted from 01.04.2018 at once and every
    # other child from 01.04.2021 (NOTA of D. 531-3); the 2015 wording
    # (45.95% / half) still governs pre-2018 children until 01.04.2021.
    ParamSpec(
        name="TauxBasePlein", value_type=DEC,
        windows=[(START, None)], values=["0.4165"],
        anchors=[["CSS_D531_3_ED2018_04"]],
        label_fr="taux de l'allocation de base à taux plein: 41,65 % de la BMAF (D. 531-3)",
        label_ru="full-rate base allowance: 41.65% of the BMAF (D. 531-3)",
    ),
    ParamSpec(
        name="TauxBasePartiel", value_type=DEC,
        windows=[(START, None)], values=["0.20825"],
        anchors=[["CSS_D531_3_ED2018_04"]],
        label_fr="taux de l'allocation de base à taux partiel: 20,825 % de la BMAF (D. 531-3)",
        label_ru="part-rate base allowance: 20.825% of the BMAF (D. 531-3)",
    ),
    ParamSpec(
        name="TauxBasePleinAncien", value_type=DEC,
        windows=[(START, "2021-04-01")], values=["0.4595"],
        anchors=[["CSS_D531_3_ED2015_01"]],
        label_fr="taux plein antérieur: 45,95 % de la BMAF, enfants nés ou adoptés avant le 01.04.2018 jusqu'au 01.04.2021 (D. 531-3, NOTA)",
        label_ru="former full rate: 45.95% of the BMAF for pre-01.04.2018 children until 01.04.2021 (D. 531-3, NOTA)",
    ),
    ParamSpec(
        name="TauxBasePartielAncien", value_type=DEC,
        windows=[(START, "2021-04-01")], values=["0.22975"],
        anchors=[["CSS_D531_3_ED2015_01"]],
        derived=[("TauxBasePartielAncien", START)],
        label_fr="taux partiel antérieur: moitié du plein, enfants nés ou adoptés avant le 01.04.2018 jusqu'au 01.04.2021 (D. 531-3, NOTA)",
        label_ru="former part rate: half of the full rate for pre-01.04.2018 children until 01.04.2021 (D. 531-3, NOTA)",
    ),
    # Wave 3: PreParE rates (D. 531-4, single wording in force).
    ParamSpec(
        name="TauxPreparePlein", value_type=DEC,
        windows=[(START, None)], values=["0.9662"],
        anchors=[["CSS_D531_4_ED2015_01"]],
        label_fr="taux PreParE à taux plein: 96,62 % de la BMAF (D. 531-4, I)",
        label_ru="full-rate PreParE: 96.62% of the BMAF (D. 531-4, I)",
    ),
    ParamSpec(
        name="TauxPrepareMajore", value_type=DEC,
        windows=[(START, None)], values=["1.5793"],
        anchors=[["CSS_D531_4_ED2015_01"]],
        label_fr="taux PreParE majoré: 157,93 % de la BMAF (D. 531-4, I, 2°)",
        label_ru="increased PreParE: 157.93% of the BMAF (D. 531-4, I, 2)",
    ),
    ParamSpec(
        name="TauxPreparePartiel50", value_type=DEC,
        windows=[(START, None)], values=["0.6246"],
        anchors=[["CSS_D531_4_ED2015_01"]],
        label_fr="taux PreParE partiel jusqu'à 50 %: 62,46 % de la BMAF (D. 531-4, II, 1°)",
        label_ru="part-time PreParE up to 50%: 62.46% of the BMAF (D. 531-4, II, 1)",
    ),
    ParamSpec(
        name="TauxPreparePartiel80", value_type=DEC,
        windows=[(START, None)], values=["0.3603"],
        anchors=[["CSS_D531_4_ED2015_01"]],
        label_fr="taux PreParE partiel 50–80 %: 36,03 % de la BMAF (D. 531-4, II, 2°)",
        label_ru="part-time PreParE 50-80%: 36.03% of the BMAF (D. 531-4, II, 2)",
    ),
    # Wave 3: D. 531-9 SMIC ceilings for part-time PreParE (monthly SMIC is
    # a case fact — the SMIC series is fr.travail.smic, boundary B-PAJE2-SMIC).
    ParamSpec(
        name="TauxSmicPlafond50", value_type=DEC,
        windows=[(START, None)], values=["1.0625"],
        anchors=[["CSS_D531_9_ED2020_05"]],
        label_fr="plafond SMIC bande 50 %: 106,25 % du SMIC × 169 (D. 531-9, I)",
        label_ru="SMIC ceiling for the 50% band: 106.25% of SMIC x 169 (D. 531-9, I)",
    ),
    ParamSpec(
        name="TauxSmicPlafond80", value_type=DEC,
        windows=[(START, None)], values=["1.7"],
        anchors=[["CSS_D531_9_ED2020_05"]],
        label_fr="plafond SMIC bande 80 %: 170 % du SMIC × 169 (D. 531-9, II)",
        label_ru="SMIC ceiling for the 80% band: 170% of SMIC x 169 (D. 531-9, II)",
    ),
]

# Exact Russian row template of bareme_builder.render_dataset; if the shared
# template changes, --check fails loudly instead of drifting silently.
_RU_ROW_TAIL = "значение для престаций, причитающихся с"
_EN_ROW_TAIL = "value applicable from"


def _to_english(payload: str) -> str:
    return (payload.replace('"language": "ru"', '"language": "en"')
                   .replace(_RU_ROW_TAIL, _EN_ROW_TAIL))


WRITTEN = dict((name, _to_english(payload))
               for name, payload in (render_dataset(spec, NS) for spec in SPECS))


def check_anchors() -> int:
    from bareme_builder import check_values_in_anchors, parse_fragments_law
    texts = parse_fragments_law(PACKAGE / "01-sources.law")
    missing, derived = check_values_in_anchors(SPECS, texts)
    for name, raw, start, where in missing:
        print(f"{name}@{start}: {raw} stands in no anchor text ({where})")
    print(f"anchor check: {sum(len(s.windows) for s in SPECS)} rows, "
          f"{len(missing)} missing, {len(derived)} formula-derived")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    if "--check-anchors" in argv:
        return check_anchors()
    if "--canary" in argv:
        return canary()
    OUT.mkdir(exist_ok=True)
    check = "--check" in argv
    problems = []
    for name, payload in WRITTEN.items():
        path = OUT / name
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != payload:
                problems.append(name)
        else:
            path.write_text(payload, encoding="utf-8")
    if check:
        for name in problems:
            print(f"{name}: differs from the spec")
        return 1 if problems else 0
    existing = {p.name for p in OUT.glob("*.lawparam.json")}
    written = set(WRITTEN)
    for stale in sorted(existing - written):
        (OUT / stale).unlink()
        print(f"removed stale parameter {stale}")
    print(f"parameters written: {len(WRITTEN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
