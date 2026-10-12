#!/usr/bin/env python3
"""CMG bareme → A3 parameters of package `fr.pf.cmg` (shared core
`corpus/tools/sources/bareme_builder.py`).

Forty-two scale numbers from the pinned fragments, none taken from a
third-party implementation. The time axis is `legal_time` (month for
which the aid is due). Old-scale figures hold across the whole coverage
window in a single row from 2021-01-01 (the reform reprises the same
nominals for the L.531-6 ceilings); reform-formula figures run from
2025-09-01. The x1.4/x1.1/x1.3 majoration factors and the ages, hour
thresholds and differential hour floors are `derived` rows: the anchor
text prints the percent or the number in words, the factor or digits are
computed from it — reported, not failed, by the anchor check.
The formula's reference hourly cost has no value in the pinned bytes
(B-CMG-COUT-REFERENCE, DSS_PENDING) and enters as a case fact instead.

    build_pf_cmg_bareme.py            — rewrite the parameters
    build_pf_cmg_bareme.py --check    — compare without writing anything
    build_pf_cmg_bareme.py --check-anchors — each row number stands
        in its anchor fragment text (core + canary)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "sources"))

from bareme_builder import ParamSpec, canary, render_dataset  # noqa: E402

PACKAGE = Path(__file__).resolve().parents[1]
OUT = PACKAGE / "bareme"
NS = "urn:fr:corpus:clir:pf-cmg"
DEC = {"name": "urn:law:std#Decimal"}
MNY = {"name": "urn:law:std#Money"}
START = "2021-01-01"
REFORM = "2025-09-01"

OLD_CEIL = ["CSS_D531_18_1_ED2018_04", "CSS_D531_18_1_ED2022_01", "CSS_D531_20_ED2025_09"]
OLD_BMAF = ["CSS_D531_18_ED2018_04"]
STRUCT = ["CSS_D531_23_ED2020_01", "CSS_D531_23_ED2021_09", "CSS_D531_21_ED2025_09"]
FORMULA = ["CSS_D531_18_ED2025_09"]
D17 = ["CSS_D531_17_ED2012_06", "CSS_D531_17_ED2022_01", "CSS_D531_17_ED2025_09"]

# The shared builder only offers the `label_ru` slot and always renders the
# `"language": "ru"` tag with its own Russian row template, so the English
# descriptions travel through that slot and are retagged below (see
# _to_english). Values, windows and anchors — the semantics — are unaffected.
SPECS: list[ParamSpec] = [
    ParamSpec(
        name="PlafondAncien1", value_type=MNY, currency="EUR",
        windows=[(START, None)], values=["17633"], anchors=[OLD_CEIL],
        label_fr="plafond de ressources a: 17 633 euros, majoré de 2 917 par enfant (D. 531-18-1 puis D. 531-20)",
        label_ru="resource a-ceiling: EUR 17,633, plus 2,917 per child (D. 531-18-1 then D. 531-20)",
    ),
    ParamSpec(
        name="MajorationPlafondAncien1", value_type=MNY, currency="EUR",
        windows=[(START, None)], values=["2917"], anchors=[OLD_CEIL],
        label_fr="majoration du plafond a par enfant à charge: 2 917 euros",
        label_ru="a-ceiling increase per dependent child: EUR 2,917",
    ),
    ParamSpec(
        name="PlafondAncien2", value_type=MNY, currency="EUR",
        windows=[(START, None)], values=["39184"], anchors=[OLD_CEIL],
        label_fr="plafond de ressources c: 39 184 euros, majoré de 6 482 par enfant",
        label_ru="resource c-ceiling: EUR 39,184, plus 6,482 per child",
    ),
    ParamSpec(
        name="MajorationPlafondAncien2", value_type=MNY, currency="EUR",
        windows=[(START, None)], values=["6482"], anchors=[OLD_CEIL],
        label_fr="majoration du plafond c par enfant à charge: 6 482 euros",
        label_ru="c-ceiling increase per dependent child: EUR 6,482",
    ),
    ParamSpec(
        name="TauxBMAFAncienBande1", value_type=DEC,
        windows=[(START, None)], values=["1.1404"], anchors=[OLD_BMAF],
        label_fr="ancien taux BMAF bande 1: 114,04 % (D. 531-18, 2°)",
        label_ru="old band-1 BMAF rate: 114.04% (D. 531-18, 2°)",
    ),
    ParamSpec(
        name="TauxBMAFAncienBande2", value_type=DEC,
        windows=[(START, None)], values=["0.7191"], anchors=[OLD_BMAF],
        label_fr="ancien taux BMAF bande 2: 71,91 %",
        label_ru="old band-2 BMAF rate: 71.91%",
    ),
    ParamSpec(
        name="TauxBMAFAncienBande3", value_type=DEC,
        windows=[(START, None)], values=["0.4314"], anchors=[OLD_BMAF],
        label_fr="ancien taux BMAF bande 3: 43,14 %",
        label_ru="old band-3 BMAF rate: 43.14%",
    ),
    ParamSpec(
        name="TauxStructureAssmatBande1", value_type=DEC,
        windows=[(START, None)], values=["1.7257"], anchors=[STRUCT],
        label_fr="taux structure assistante maternelle bande 1: 172,57 % (D. 531-23 puis D. 531-21)",
        label_ru="structure childminder band-1 rate: 172.57% (D. 531-23 then D. 531-21)",
    ),
    ParamSpec(
        name="TauxStructureAssmatBande2", value_type=DEC,
        windows=[(START, None)], values=["1.4381"], anchors=[STRUCT],
        label_fr="taux structure assistante maternelle bande 2: 143,81 %",
        label_ru="structure childminder band-2 rate: 143.81%",
    ),
    ParamSpec(
        name="TauxStructureAssmatBande3", value_type=DEC,
        windows=[(START, None)], values=["1.1505"], anchors=[STRUCT],
        label_fr="taux structure assistante maternelle bande 3: 115,05 %",
        label_ru="structure childminder band-3 rate: 115.05%",
    ),
    ParamSpec(
        name="TauxStructureDomBande1", value_type=DEC,
        windows=[(START, None)], values=["2.0853"], anchors=[STRUCT],
        label_fr="taux domicile/EAJE bande 1: 208,53 %",
        label_ru="home/EAJE band-1 rate: 208.53%",
    ),
    ParamSpec(
        name="TauxStructureDomBande2", value_type=DEC,
        windows=[(START, None)], values=["1.7976"], anchors=[STRUCT],
        label_fr="taux domicile/EAJE bande 2: 179,76 %",
        label_ru="home/EAJE band-2 rate: 179.76%",
    ),
    ParamSpec(
        name="TauxStructureDomBande3", value_type=DEC,
        windows=[(START, None)], values=["1.51"], anchors=[STRUCT],
        label_fr="taux domicile/EAJE bande 3: 151,00 %",
        label_ru="home/EAJE band-3 rate: 151.00%",
    ),
    ParamSpec(
        name="TauxPriseEnCharge85", value_type=DEC,
        windows=[(START, None)], values=["0.85"],
        anchors=[["CSS_D531_18_ED2018_04", "CSS_D531_21_ED2025_09"]],
        label_fr="prise en charge partielle: 85 % du salaire net ou de la dépense",
        label_ru="partial coverage: 85% of net pay or expense",
    ),
    ParamSpec(
        name="TauxPriseEnCharge50", value_type=DEC,
        windows=[(START, None)], values=["0.5"], anchors=[D17],
        label_fr="prise en charge domicile: 50 % des cotisations (D. 531-17, II)",
        label_ru="home-employment coverage: 50% of contributions (D. 531-17, II)",
    ),
    ParamSpec(
        name="MajorationPlafond40", value_type=DEC,
        windows=[(START, None)], values=["1.4"],
        anchors=[["CSS_D531_18_ED2018_04", "CSS_D531_23_ED2021_09", "CSS_D531_21_ED2025_09"]],
        derived=[("MajorationPlafond40", START)],
        label_fr="plafonds et maxima majorés de 40 % (personne seule): facteur 1,4",
        label_ru="ceilings and maxima plus 40% (single person): factor 1.4",
    ),
    ParamSpec(
        name="PlafondHoraireAssmat", value_type=MNY, currency="EUR",
        windows=[(REFORM, None)], values=["8"], anchors=[FORMULA],
        label_fr="plafond horaire du coût assistante maternelle: 8 euros (D. 531-18, 1°)",
        label_ru="childminder hourly cost cap: EUR 8 (D. 531-18, 1°)",
    ),
    ParamSpec(
        name="PlafondHoraireDomicile", value_type=MNY, currency="EUR",
        windows=[(REFORM, None)], values=["15"], anchors=[FORMULA],
        label_fr="plafond horaire du coût domicile: 15 euros",
        label_ru="home-employment hourly cost cap: EUR 15",
    ),
    ParamSpec(
        name="PlafondRevenuMensuel", value_type=MNY, currency="EUR",
        windows=[(REFORM, None)], values=["8500"], anchors=[FORMULA],
        label_fr="plafond de ressources mensuelles: 8 500 euros (D. 531-18, 2°)",
        label_ru="monthly resource ceiling: EUR 8,500 (D. 531-18, 2°)",
    ),
    ParamSpec(
        name="TauxEffortAM1Enfant", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0619"], anchors=[FORMULA],
        label_fr="taux d'effort assistante maternelle, un enfant: 0,0619 %",
        label_ru="childminder effort rate, one child: 0.0619%",
    ),
    ParamSpec(
        name="TauxEffortAM2Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0516"], anchors=[FORMULA],
        label_fr="taux d'effort assistante maternelle, deux enfants: 0,0516 %",
        label_ru="childminder effort rate, two children: 0.0516%",
    ),
    ParamSpec(
        name="TauxEffortAM3Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0413"], anchors=[FORMULA],
        label_fr="taux d'effort assistante maternelle, trois enfants: 0,0413 %",
        label_ru="childminder effort rate, three children: 0.0413%",
    ),
    ParamSpec(
        name="TauxEffortAM4a7Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0310"], anchors=[FORMULA],
        label_fr="taux d'effort assistante maternelle, quatre à sept enfants: 0,0310 %",
        label_ru="childminder effort rate, four to seven children: 0.0310%",
    ),
    ParamSpec(
        name="TauxEffortAM8Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0206"], anchors=[FORMULA],
        label_fr="taux d'effort assistante maternelle, huit enfants et plus: 0,0206 %",
        label_ru="childminder effort rate, eight children or more: 0.0206%",
    ),
    ParamSpec(
        name="TauxEffortDom1Enfant", value_type=DEC,
        windows=[(REFORM, None)], values=["0.1238"], anchors=[FORMULA],
        label_fr="taux d'effort domicile, un enfant: 0,1238 %",
        label_ru="home-employment effort rate, one child: 0.1238%",
    ),
    ParamSpec(
        name="TauxEffortDom2Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.1032"], anchors=[FORMULA],
        label_fr="taux d'effort domicile, deux enfants: 0,1032 %",
        label_ru="home-employment effort rate, two children: 0.1032%",
    ),
    ParamSpec(
        name="TauxEffortDom3Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0826"], anchors=[FORMULA],
        label_fr="taux d'effort domicile, trois enfants: 0,0826 %",
        label_ru="home-employment effort rate, three children: 0.0826%",
    ),
    ParamSpec(
        name="TauxEffortDom4a7Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0620"], anchors=[FORMULA],
        label_fr="taux d'effort domicile, quatre à sept enfants: 0,0620 %",
        label_ru="home-employment effort rate, four to seven children: 0.0620%",
    ),
    ParamSpec(
        name="TauxEffortDom8Enfants", value_type=DEC,
        windows=[(REFORM, None)], values=["0.0412"], anchors=[FORMULA],
        label_fr="taux d'effort domicile, huit enfants et plus: 0,0412 %",
        label_ru="home-employment effort rate, eight children or more: 0.0412%",
    ),
    ParamSpec(
        name="MajorationSpecifiques10", value_type=DEC,
        windows=[(REFORM, None)], values=["1.1"],
        anchors=[["CSS_D531_22_ED2025_09"]],
        derived=[("MajorationSpecifiques10", REFORM)],
        label_fr="maximum majoré de 10 % (horaires spécifiques): facteur 1,1",
        label_ru="maximum plus 10% (specific hours): factor 1.1",
    ),
    ParamSpec(
        name="MajorationTrente30", value_type=DEC,
        windows=[(REFORM, None)], values=["1.3"],
        anchors=[["CSS_D531_22_ED2025_09"]],
        derived=[("MajorationTrente30", REFORM)],
        label_fr="maximum majoré de 30 % (AAH, personne seule, L. 541-1): facteur 1,3",
        label_ru="maximum plus 30% (AAH, single, L. 541-1): factor 1.3",
    ),
    ParamSpec(
        name="PlafondDifferentiel90", value_type=DEC,
        windows=[(REFORM, None)], values=["0.9"],
        anchors=[["JORF_DECR2025_515_ART3"]],
        label_fr="différentiel sous 90 % de la rémunération nette (décret 2025-515 art. 3, II)",
        label_ru="differential under 90% of net pay (Decree 2025-515 Art. 3, II)",
    ),
    ParamSpec(
        name="TarifHoraireMaxEAJE", value_type=MNY, currency="EUR",
        windows=[(START, None)], values=["10"],
        anchors=[["CSS_D531_23_ED2021_09", "CSS_D531_21_ED2025_09"]],
        label_fr="tarification EAJE: 10 euros par heure d'accueil au plus",
        label_ru="EAJE tariff: at most EUR 10 per care hour",
    ),
    ParamSpec(
        name="AgeLimite6", value_type={"name": "urn:law:std#Integer"},
        windows=[(START, None)], values=["6"],
        anchors=[["CSS_D531_20_ED2020_01", "CSS_D531_18_1_ED2025_09"]],
        derived=[("AgeLimite6", START)],
        label_fr="âge limite: six ans, ancien D. 531-20 puis décret (mot imprimé en lettres)",
        label_ru="age limit: six years, old D. 531-20 then decree (word printed in letters)",
    ),
    ParamSpec(
        name="AgeLimiteIsole12", value_type={"name": "urn:law:std#Integer"},
        windows=[(REFORM, None)], values=["12"],
        anchors=[["CSS_D531_18_1_ED2025_09"]],
        derived=[("AgeLimiteIsole12", REFORM)],
        label_fr="âge limite parents isolés: douze ans (mot imprimé en lettres)",
        label_ru="isolated-parent age limit: twelve years (word printed in letters)",
    ),
    ParamSpec(
        name="AgeSeuil3", value_type={"name": "urn:law:std#Integer"},
        windows=[(START, None)], values=["3"],
        anchors=[["CSS_D531_21_ED2025_09"]],
        derived=[("AgeSeuil3", START)],
        label_fr="seuil trois ans des moitiés et du différentiel (mot imprimé en lettres)",
        label_ru="three-year threshold of halves and differential (word printed in letters)",
    ),
    ParamSpec(
        name="SeuilHeuresStructure16", value_type=DEC,
        windows=[(START, None)], values=["16"],
        anchors=[["CSS_D531_23_ED2021_09"]],
        derived=[("SeuilHeuresStructure16", START)],
        label_fr="minimum seize heures L. 531-6 ancien droit (mot imprimé en lettres)",
        label_ru="old-law L. 531-6 sixteen-hour minimum (word printed in letters)",
    ),
    ParamSpec(
        name="SeuilSpecifiques25", value_type=DEC,
        windows=[(REFORM, None)], values=["25"],
        anchors=[["CSS_D531_22_ED2025_09"]],
        derived=[("SeuilSpecifiques25", REFORM)],
        label_fr="seuil vingt-cinq heures spécifiques (chiffres dans le texte: 25)",
        label_ru="twenty-five specific-hours threshold (digits in text: 25)",
    ),
    ParamSpec(
        name="SeuilDiffAssmat100", value_type=DEC,
        windows=[(REFORM, None)], values=["100"],
        anchors=[["JORF_DECR2025_515_ART3"]],
        derived=[("SeuilDiffAssmat100", REFORM)],
        label_fr="différentiel: cent heures assistante maternelle (mot imprimé en lettres)",
        label_ru="differential: one hundred childminder hours (word printed in letters)",
    ),
    ParamSpec(
        name="SeuilDiffDomicile50", value_type=DEC,
        windows=[(REFORM, None)], values=["50"],
        anchors=[["JORF_DECR2025_515_ART3"]],
        derived=[("SeuilDiffDomicile50", REFORM)],
        label_fr="différentiel: cinquante heures domicile (mot imprimé en lettres)",
        label_ru="differential: fifty home hours (word printed in letters)",
    ),
    ParamSpec(
        name="SeuilDiffNombreuxJeunes150", value_type=DEC,
        windows=[(REFORM, None)], values=["150"],
        anchors=[["JORF_DECR2025_515_ART3"]],
        derived=[("SeuilDiffNombreuxJeunes150", REFORM)],
        label_fr="différentiel: cent cinquante heures fratrie jeune (mots imprimés en lettres)",
        label_ru="differential: one hundred fifty young-sibling hours (words printed in letters)",
    ),
    ParamSpec(
        name="SeuilDiffNombreuxGrand100", value_type=DEC,
        windows=[(REFORM, None)], values=["100"],
        anchors=[["JORF_DECR2025_515_ART3"]],
        derived=[("SeuilDiffNombreuxGrand100", REFORM)],
        label_fr="différentiel: cent heures fratrie avec aîné (mot imprimé en lettres)",
        label_ru="differential: one hundred hours with an older sibling (word printed in letters)",
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
