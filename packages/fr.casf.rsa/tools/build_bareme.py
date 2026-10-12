#!/usr/bin/env python3
"""Bareme builder for package fr.casf.rsa (CNAF wave 4, W4-RSA).

Parameter spec (name, unit, anchor, rule for extracting the figure from
pinned text), windows from versions.

Every figure below is read from the pinned fragment text; the builder
refuses to emit a row whose text form is absent from the anchor file
("figure must stand in the anchor text"). Percent text forms keep French
formatting (comma decimals, R. 262-1 uses a space: "128, 412 %"); row
values are Decimal fractions (APL convention: 16,5 % -> "0.165").

Windows: the composition and lone-parent percentages are identical in
every wording in force since 2021-01-01, so rows run from the coverage
start 2021-01-01. The sanction scale (30 % / 50 % cap) is the decree
2025-478 wording in force from 2025-06-01. Finish-wave factors (43x/24x
turnover, double hours, 500 EUR duties threshold, one-point rate
top-up) are identical in every in-window wording, so their rows also
run from 2021-01-01.

MontantForfaitaireDecret (the L. 262-2 single-person monthly base) is a
multi-row dataset built from the six pinned revaluation decrees
(sources/decrets-mf/, tools/pin_mf_decrets.py): each row's figure is READ from
the pinned article text ("est de / est fixé à NNN,NN euros"), anchored to the
decree fragment DEC<year>_<no>_ART1 of 01-sources.law. A row runs from the
decree's stated month (clamped to the coverage start) for one year; the
row of decree 2022-699 is cut at 2022-07-01 (the +4 % of law 2022-1158 art. 9
from 1 July 2022) and the window 2022-07..2023-03 is NOT a value of this
parameter: it is bridged by the rule MfBaseLoi2022 (a reading) from two
further datasets built here, MontantForfaitaireBaseLoi2022 (the 2022-699
figure, read from its pinned text) and CoefficientLoi2022 (1.04, read from the
pinned text of art. 9), both valid exactly in the window. The series stops at
2026-04-01 (the next 1 April decree is not pinned): outside it the parameter
has no value (MissingParameterValue) and the base stays the case input
mf_base (B-RSA-MF-EURO).

Deliberately NOT in the bareme (case inputs with provenance instead):
  - monthly MF amount for a single person OUTSIDE the pinned series (the gap,
    2026-04-01 on; the 1 April L. 161-25 factor is DSS_PENDING) -> input
    mf_base (boundary B-RSA-MF-EURO);
  - quarterly average resources -> upstream premise
    fr.minima.ressources::moyenne_trimestre (same lane, dependency);
  - received housing-aid figure -> input (APL-FORFAIT-PENDING);
  - annual working hours of C. trav. L. 3121-41 al. 3 (D. 262-25-1 base,
    unpinned) -> input heures_annuelles_reference (B-RSA-CTRAV-HORAIRES);
  - overnight money-market rate (D. 262-64 base, unpinned) -> input
    taux_marche_monetaire (B-RSA-TAUX-MARCHE);
  - monthly social-security ceiling of CSS L. 241-3 (D. 262-77,
    unpinned) -> input plafond_secu_retenu (B-RSA-PLAFOND-SECU).

Usage:
  python3 corpus/laws/fr/rsa/tools/build_bareme.py --check
  python3 corpus/laws/fr/rsa/tools/build_bareme.py --write
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "rsa"

NS = "urn:fr:corpus:clir:rsa"

DECIMAL = {"name": "urn:law:std#Decimal"}
MONEY = {"name": "urn:law:std#Money"}

# (name, kind, value, extra, text_form, anchor_txt, valid_start,
#  fr_desc, en_desc); extra holds {"currency": "EUR"} for Money.
SPECS = [
    # R262-1: two-person household, +50 % of the single-person MF.
    ("TauxCompositionDeux", DECIMAL, "0.50", None, "50 %",
     "sources/casf/R262-1.txt", "2021-01-01",
     "majoration à deux personnes du montant forfaitaire",
     "two-person increase of the flat-rate amount"),
    # R262-1: each additional dependant, +30 %.
    ("TauxCompositionSupp", DECIMAL, "0.30", None, "30 %",
     "sources/casf/R262-1.txt", "2021-01-01",
     "majoration par personne supplémentaire à charge",
     "increase per additional dependant"),
    # R262-1: from the third child or under-25 dependant, +40 %.
    ("TauxCompositionEnfant3Plus", DECIMAL, "0.40", None, "40 %",
     "sources/casf/R262-1.txt", "2021-01-01",
     "majoration à 40 % à partir du troisième enfant ou jeune à charge",
     "increase to 40 % from the third dependent child or young person"),
    # R262-1 al.2: lone parent, 128.412 % of the single-person MF.
    ("TauxMajoreIsole", DECIMAL, "1.28412", None, "128, 412 %",
     "sources/casf/R262-1.txt", "2021-01-01",
     "montant majoré personne isolée",
     "increased amount for a lone parent"),
    # R262-1 al.2: supplement per dependent child, 42.804 %.
    ("TauxMajoreEnfant", DECIMAL, "0.42804", None, "42, 804 %",
     "sources/casf/R262-1.txt", "2021-01-01",
     "supplément par enfant à charge du montant majoré",
     "supplement per dependent child of the increased amount"),
    # R262-39: allocation below 6 euros is not paid.
    ("SeuilNonVersement", MONEY, "6", {"currency": "EUR"}, "6 €",
     "sources/casf/R262-39.txt", "2021-01-01",
     "seuil de non-versement de l'allocation",
     "non-payment threshold of the allowance"),
    # R262-92: overpayment below 77 euros is not recovered.
    ("SeuilNonRecouvrement", MONEY, "77", {"currency": "EUR"}, "77 €",
     "sources/casf/R262-92.txt", "2021-01-01",
     "seuil de non-récupération de l'indu",
     "non-recovery threshold of overpayments"),
    # R262-68: first sanction, suspension of at least 30 %.
    ("TauxSanctionMini", DECIMAL, "0.30", None, "30 %",
     "sources/casf/R262-68.txt", "2025-06-01",
     "part minimale suspendue ou supprimée en premier manquement",
     "minimum share suspended or removed for a first breach"),
    # R262-68-6: multi-person or increased-amount household, cap 50 %.
    ("PlafondSanctionMenage", DECIMAL, "0.50", None, "50 %",
     "sources/casf/R262-68-6.txt", "2025-06-01",
     "plafond de la part suspendue ou supprimée, foyer pluripersonnel",
     "cap on the suspended or removed share, multi-person household"),
    # D262-25-1: young workers, twice the annual hours of C. trav. L3121-41.
    ("CoefficientDoubleHeures", DECIMAL, "2", None, "double du nombre",
     "sources/casf/D262-25-1.txt", "2021-01-01",
     "coefficient doublant les heures annuelles de référence",
     "coefficient doubling the annual reference hours"),
    # D262-25-2: self-employed turnover, 43x the single-person monthly MF.
    ("FacteurCATNS", DECIMAL, "43", None, "quarante-trois fois",
     "sources/casf/D262-25-2.txt", "2021-01-01",
     "facteur du chiffre d'affaires des non-salariés non agricoles",
     "turnover factor for non-agricultural self-employed workers"),
    # D262-25-3: agricultural turnover, 24x the single-person monthly MF.
    ("FacteurCAAgricole", DECIMAL, "24", None, "vingt-quatre fois",
     "sources/casf/D262-25-3.txt", "2021-01-01",
     "facteur du chiffre d'affaires du régime agricole",
     "turnover factor for the agricultural scheme"),
    # D262-65: insertion duties below 500 EUR of monthly professional income.
    ("SeuilRevenusDevoirs", MONEY, "500", {"currency": "EUR"}, "500 €",
     "sources/casf/D262-65.txt", "2021-01-01",
     "seuil de revenus professionnels des devoirs d'insertion",
     "professional-income threshold of the insertion duties"),
    # D262-64 2°: no-convention fallback rate, market rate plus one point.
    ("MajorationTauxMarche", DECIMAL, "0.01", None, "plus un point",
     "sources/casf/D262-64.txt", "2021-01-01",
     "majoration d'un point du taux du marché monétaire",
     "one-point top-up of the money-market rate"),
]


def build_row(name, kind, value, extra, text_form, anchor_txt, start,
              fr_desc, en_desc):
    blob = (PKG / anchor_txt).read_text(encoding="utf-8")
    assert text_form in blob, (
        f"{name}: text form {text_form!r} absent from {anchor_txt}")
    frag = "CASF_" + anchor_txt.split("/")[-1].removesuffix(".txt").replace("-", "_")
    anchor = f"{NS}#{frag}"
    row_id = f"{NS}:param:{name}"
    if extra:
        val = {"kind": "value", "type": kind, "value": value, **extra}
    else:
        val = {"kind": "value", "type": kind, "value": value}
    return {
        "labels": [
            {"language": "fr", "status": "unofficial", "text": fr_desc},
            {"language": "en", "status": "unofficial", "text": en_desc},
        ],
        "schemaVersion": "law.params/0.1",
        "kind": "parameter-dataset",
        "id": row_id,
        "parameter": f"{NS}#{name}",
        "valueType": kind,
        "timeAxis": "legal_time",
        "granularity": "date",
        "coverage": {"start": start, "endExclusive": None},
        "values": [
            {
                "id": f"{row_id}#{start}",
                "valid": {"start": start, "endExclusive": None},
                "value": val,
                "anchors": [anchor],
                "labels": [
                    {"language": "fr", "status": "unofficial",
                     "text": f"{fr_desc} : valeur applicable à compter du {start}"},
                    {"language": "en", "status": "unofficial",
                     "text": f"{en_desc}: value applicable from {start}"},
                ],
            }
        ],
    }


MF_DIR = PKG / "sources" / "decrets-mf"
MF_AMOUNT = re.compile(r"(?:est de|est fixé à) ([\d ]+,\d\d) euros")
COVERAGE_START = "2021-01-01"


def plus_year(month_first: str) -> str:
    return f"{int(month_first[:4]) + 1:04d}{month_first[4:]}"


def build_mf_dataset():
    """MontantForfaitaireDecret: one row per pinned decree, figure read from the text."""
    manifest = json.loads((MF_DIR / "manifest.json").read_text(encoding="utf-8"))
    name = "MontantForfaitaireDecret"
    fr_desc = ("montant forfaitaire mensuel du RSA d'une personne seule "
               "(L. 262-2), fixé par décret de revalorisation")
    en_desc = ("single-person monthly RSA flat-rate amount (L. 262-2) set by "
               "a revaluation decree")
    row_id = f"{NS}:param:{name}"
    rows = []
    for row in manifest["decrets"]:
        year, num = row["decret"].removeprefix("decret-").split("-")
        text = (PKG / row["text"]).read_text(encoding="utf-8")
        found = MF_AMOUNT.findall(text)
        assert len(found) == 1, (row["decret"], found)
        figure = found[0]
        assert f"{figure} euros" in text
        amount = figure.replace(" ", "").replace(",", ".")
        start = max(COVERAGE_START, row["start_month"] + "-01")
        end = plus_year(row["start_month"] + "-01")
        for bridge in manifest["bridges"]:
            bridge_from = bridge["from"] + "-01"
            if start < bridge_from < end:
                end = bridge_from
        rows.append({
            "id": f"{row_id}#{start}",
            "valid": {"start": start, "endExclusive": end},
            "value": {"kind": "value", "type": MONEY, "value": amount,
                      "currency": "EUR"},
            "anchors": [f"{NS}#DEC{year}_{num}_ART1"],
            "labels": [
                {"language": "fr", "status": "unofficial",
                 "text": (f"{fr_desc} : {figure} euros, décret n° {year}-{num}, "
                          f"du {start} au {end} (exclu)")},
                {"language": "en", "status": "unofficial",
                 "text": (f"{en_desc}: {amount} EUR, decree no. {year}-{num}, "
                          f"from {start} to {end} (exclusive)")},
            ],
        })
    rows.sort(key=lambda r: r["valid"]["start"])
    for a, b in zip(rows, rows[1:]):
        assert a["valid"]["endExclusive"] <= b["valid"]["start"], (a["id"], b["id"])
    return name, {
        "labels": [
            {"language": "fr", "status": "unofficial", "text": fr_desc},
            {"language": "en", "status": "unofficial", "text": en_desc},
        ],
        "schemaVersion": "law.params/0.1",
        "kind": "parameter-dataset",
        "id": row_id,
        "parameter": f"{NS}#{name}",
        "valueType": MONEY,
        "timeAxis": "legal_time",
        "granularity": "date",
        "coverage": {"start": rows[0]["valid"]["start"],
                     "endExclusive": rows[-1]["valid"]["endExclusive"]},
        "values": rows,
    }


LOI_COEFF = re.compile(r"coefficient égal à (\d+,\d+)")


def bridge_window(manifest) -> tuple[str, str]:
    """[from, to] of the single bridge: first day of its first month .. first day after its last."""
    assert len(manifest["bridges"]) == 1, manifest["bridges"]
    bridge = manifest["bridges"][0]
    last_year, last_month = map(int, bridge["to"].split("-"))
    end_year, end_month = (last_year + 1, 1) if last_month == 12 else (last_year, last_month + 1)
    return bridge["from"] + "-01", f"{end_year:04d}-{end_month:02d}-01"


def one_value_dataset(name, kind, value, anchor, start, end, fr_desc, en_desc, fr_value, en_value):
    row_id = f"{NS}:param:{name}"
    val = {"kind": "value", "type": kind, "value": value}
    if kind is MONEY:
        val["currency"] = "EUR"
    return name, {
        "labels": [
            {"language": "fr", "status": "unofficial", "text": fr_desc},
            {"language": "en", "status": "unofficial", "text": en_desc},
        ],
        "schemaVersion": "law.params/0.1",
        "kind": "parameter-dataset",
        "id": row_id,
        "parameter": f"{NS}#{name}",
        "valueType": kind,
        "timeAxis": "legal_time",
        "granularity": "date",
        "coverage": {"start": start, "endExclusive": end},
        "values": [{
            "id": f"{row_id}#{start}",
            "valid": {"start": start, "endExclusive": end},
            "value": val,
            "anchors": [anchor],
            "labels": [
                {"language": "fr", "status": "unofficial",
                 "text": f"{fr_desc} : {fr_value}, du {start} au {end} (exclu)"},
                {"language": "en", "status": "unofficial",
                 "text": f"{en_desc}: {en_value}, from {start} to {end} (exclusive)"},
            ],
        }],
    }


def build_bridge_datasets():
    """Two datasets of the window 2022-07..2023-03, figures read from the pinned texts.

    MontantForfaitaireBaseLoi2022: the figure of decree 2022-699 (the base article 9
    revalorises), CoefficientLoi2022: the coefficient of article 9. The product and
    its rounding are NOT here: they are the rule MfBaseLoi2022 (02-montant.law).
    """
    manifest = json.loads((MF_DIR / "manifest.json").read_text(encoding="utf-8"))
    start, end = bridge_window(manifest)
    bridge = manifest["bridges"][0]
    assert start == bridge["start_date"], (start, bridge)
    decret = next(r for r in manifest["decrets"] if r["decret"] == bridge["base_decret"])
    year, num = decret["decret"].removeprefix("decret-").split("-")
    dtext = (PKG / decret["text"]).read_text(encoding="utf-8")
    figures = MF_AMOUNT.findall(dtext)
    assert len(figures) == 1, figures
    amount = figures[0].replace(" ", "").replace(",", ".")
    law = next(r for r in manifest["lois"] if r["loi"] == bridge["law"])
    ltext = (PKG / law["text"]).read_text(encoding="utf-8")
    coeffs = LOI_COEFF.findall(ltext)
    assert len(coeffs) == 1, coeffs
    assert "le 1er juillet 2022" in ltext and "l'article L. 161-25" in ltext
    coefficient = coeffs[0].replace(",", ".")
    return [
        one_value_dataset(
            "MontantForfaitaireBaseLoi2022", MONEY, amount,
            f"{NS}#DEC{year}_{num}_ART1", start, end,
            ("montant forfaitaire mensuel du RSA d'une personne seule du décret "
             f"n° {year}-{num}, base de la revalorisation du 1er juillet 2022 (loi n° 2022-1158, art. 9)"),
            ("single-person monthly RSA flat-rate amount of decree "
             f"no. {year}-{num}, the base of the 1 July 2022 revaluation (Act no. 2022-1158, art. 9)"),
            f"{figures[0]} euros", f"{amount} EUR"),
        one_value_dataset(
            "CoefficientLoi2022", DECIMAL, coefficient,
            f"{NS}#LOI_{law['number'].replace('-', '_')}_ART9", start, end,
            "coefficient de revalorisation du 1er juillet 2022 (loi n° 2022-1158, art. 9, I)",
            "revaluation coefficient of 1 July 2022 (Act no. 2022-1158, art. 9, I)",
            f"coefficient {coeffs[0]}", f"coefficient {coefficient}"),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    assert args.check or args.write, "give --check or --write"
    outputs = {}
    for spec in SPECS:
        name = spec[0]
        outputs[f"bareme/{name}.lawparam.json"] = (
            json.dumps(build_row(*spec), ensure_ascii=False, indent=2)
            + "\n").encode("utf-8")
    mf_name, mf_dataset = build_mf_dataset()
    outputs[f"bareme/{mf_name}.lawparam.json"] = (
        json.dumps(mf_dataset, ensure_ascii=False, indent=2)
        + "\n").encode("utf-8")
    for bridge_name, bridge_dataset in build_bridge_datasets():
        outputs[f"bareme/{bridge_name}.lawparam.json"] = (
            json.dumps(bridge_dataset, ensure_ascii=False, indent=2)
            + "\n").encode("utf-8")
    if args.write:
        for rel, blob in outputs.items():
            p = PKG / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            old = p.read_bytes() if p.exists() else None
            if old != blob:
                p.write_bytes(blob)
                print(f"write {rel}")
        print(f"params={len(outputs)}")
        return
    bad = [rel for rel, blob in outputs.items()
           if not (PKG / rel).exists()
           or (PKG / rel).read_bytes() != blob]
    if bad:
        print("STALE: " + " ".join(bad))
        sys.exit(1)
    print(f"current: params={len(outputs)}")


if __name__ == "__main__":
    main()
