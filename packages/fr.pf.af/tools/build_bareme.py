#!/usr/bin/env python3
"""Bareme builder for package fr.pf.af (CNAF wave 1, lane fr-cnaf-pf-af).

Common builder per plan 5.2.5: parameter spec (name, unit, anchor, rule for
extracting the figure from pinned text), windows from versions.

Every rate and figure below is read from the pinned fragment text; the
builder refuses to emit a row whose text form is absent from the anchor
fragment ("figure must stand in the anchor text"). Percent text forms keep
French formatting (comma decimals, "p. 100"); row values are Decimal
fractions (APL convention: 8,5 % -> "0.085"). Integer params are numbers.

Windows come from the pinned version debuts (sources/articles.json); one row
covers every edition inside its window (APL convention).

Deliberately NOT in the bareme (case inputs with provenance instead):
  - BMAF monthly amount in euros (L. 551-1 base; arretes unpinned, D-Q4) ->
    input bmaf_montant (boundary B-PFAF-BMAF-EURO);
  - DOM base L. 755-3 monthly amount (arrete unpinned) -> input
    base_dom_montant (boundary B-PFAF-BMAF-DOM);
  - yearly applicable plafond values (D-81, 08.10.2026): the D521-3 I/II
    amounts ARE pinned and emitted here; they serve the ceiling rules only
    before the first revaluation (2015-07-01 .. 2016-01-01). From 2016-01-01
    the base ceilings and the per-child increment are the amounts published
    by the DSS instruction for 1 January of the year of right (each rounded
    on its own, D521-3 III "leur majoration respective") and arrive as case
    inputs plafond_base_tranche1/2_publie, majoration_plafond_enfant_publiee
    (provenance: PLAFOND_AF fragments of fr.css.revalorisation).

Usage:
  python3 corpus/laws/fr/pf-af/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-af/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-af"

NS = "urn:fr:corpus:clir:pf-af"

MONEY = {"name": "urn:law:std#Money"}
DECIMAL = {"name": "urn:law:std#Decimal"}
INTEGER = {"name": "urn:law:std#Integer"}

# (name, kind, value, text_form, anchor_txt, valid_start, fr_desc, en_desc)
SPECS = [
    # D521-1, I 1°: band 1 rates (fight against the registry cut 2026-10-06).
    ("TauxAfRang2Bande1", DECIMAL, "0.32", "32 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "taux pour le deuxième enfant, bande 1",
     "rate for the second child, band 1"),
    ("TauxAfRang3PlusBande1", DECIMAL, "0.41", "41 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "taux pour le troisième enfant et les suivants, bande 1",
     "rate for the third and subsequent children, band 1"),
    ("TauxMajorationBande1", DECIMAL, "0.16", "16 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "majoration pour âge, bande 1", "age supplement, band 1"),
    # D521-1, I 2°: band 2 rates.
    ("TauxAfRang2Bande2", DECIMAL, "0.16", "16 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "taux pour le deuxième enfant, bande 2",
     "rate for the second child, band 2"),
    ("TauxAfRang3PlusBande2", DECIMAL, "0.205", "20,5 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "taux pour le troisième enfant et les suivants, bande 2",
     "rate for the third and subsequent children, band 2"),
    ("TauxMajorationBande2", DECIMAL, "0.08", "8 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "majoration pour âge, bande 2", "age supplement, band 2"),
    # D521-1, I 3°: band 3 rates.
    ("TauxAfRang2Bande3", DECIMAL, "0.08", "8 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "taux pour le deuxième enfant, bande 3",
     "rate for the second child, band 3"),
    ("TauxAfRang3PlusBande3", DECIMAL, "0.1025", "10,25 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "taux pour le troisième enfant et les suivants, bande 3",
     "rate for the third and subsequent children, band 3"),
    ("TauxMajorationBande3", DECIMAL, "0.04", "4 %",
     "sources/css/D521-1.txt", "2015-07-01",
     "majoration pour âge, bande 3", "age supplement, band 3"),
    # D521-2, I: forfait rates per band.
    ("TauxForfaitBande1", DECIMAL, "0.20234", "20,234 %",
     "sources/css/D521-2.txt", "2015-07-01",
     "allocation forfaitaire, bande 1", "lump-sum allowance, band 1"),
    ("TauxForfaitBande2", DECIMAL, "0.10117", "10,117 %",
     "sources/css/D521-2.txt", "2015-07-01",
     "allocation forfaitaire, bande 2", "lump-sum allowance, band 2"),
    ("TauxForfaitBande3", DECIMAL, "0.05059", "5,059 %",
     "sources/css/D521-2.txt", "2015-07-01",
     "allocation forfaitaire, bande 3", "lump-sum allowance, band 3"),
    # D521-3, I/II: plafond bases and per-child increment as set by the
    # decree (2015-07-01). The ceiling rules read them until the first
    # revaluation on 2016-01-01; later years take the published amounts as
    # case inputs (D-81).
    ("PlafondBaseI", MONEY, "55950", "55 950 euros",
     "sources/css/D521-3.txt", "2015-07-01",
     "plafond de ressources, première tranche (montant fixé par D. 521-3, avant la première revalorisation)",
     "resource ceiling, first band (amount set by D. 521-3, before the first revaluation)"),
    ("PlafondBaseII", MONEY, "78300", "78 300 euros",
     "sources/css/D521-3.txt", "2015-07-01",
     "plafond de ressources, deuxième tranche (montant fixé par D. 521-3, avant la première revalorisation)",
     "resource ceiling, second band (amount set by D. 521-3, before the first revaluation)"),
    ("MajorationPlafondParEnfant", MONEY, "5595", "5 595 euros",
     "sources/css/D521-3.txt", "2015-07-01",
     "majoration du plafond par enfant à charge (montant fixé par D. 521-3, avant la première revalorisation)",
     "ceiling increment per dependent child (amount set by D. 521-3, before the first revaluation)"),
    # D755-5, II: single-child DOM rates (base L. 755-3).
    ("TauxDomEnfantUnique", DECIMAL, "0.0588", "5,88 p. 100",
     "sources/css/D755-5.txt", "1998-12-30",
     "taux enfant unique dans les DOM", "single-child rate in the DOM"),
    ("TauxDomMajorationOnzeAns", DECIMAL, "0.0369", "3,69 p. 100",
     "sources/css/D755-5.txt", "1998-12-30",
     "majoration enfant unique à partir de onze ans",
     "single-child supplement from age eleven"),
    ("TauxDomMajorationSeizeAns", DECIMAL, "0.0567", "5,67 p. 100",
     "sources/css/D755-5.txt", "1998-12-30",
     "majoration enfant unique à partir de seize ans",
     "single-child supplement from age sixteen"),
    # Integer thresholds (numbers, not strings).
    ("SeuilEnfantsMajorationTous", INTEGER, 3, "est fixé à trois",
     "sources/css/R521-1.txt", "2008-04-30",
     "enfants pour la majoration de chaque enfant",
     "children for the every-child supplement"),
    ("SeuilEnfantsForfaitMinimum", INTEGER, 3, "est fixé à trois",
     "sources/css/D521-2.txt", "2015-07-01",
     "enfants pour l'allocation forfaitaire",
     "children for the lump-sum allowance"),
    ("AgeDomMajorationOnze", INTEGER, 11, "à partir de onze ans",
     "sources/css/D755-5.txt", "1998-12-30",
     "âge de la première majoration enfant unique",
     "age of the first single-child supplement"),
    ("AgeDomMajorationSeize", INTEGER, 16, "à partir de seize ans",
     "sources/css/D755-5.txt", "1998-12-30",
     "âge de la seconde majoration enfant unique",
     "age of the second single-child supplement"),
]

# The age threshold moves 14 -> 18 on 2026-03-01 (decree 2026-138): two rows.
AGE_ROWS = [
    ("2008-04-30", "2026-03-01", 14, "14 ans",
     "sources/css/R521-1-2008.txt"),
    ("2026-03-01", None, 18, "18 ans",
     "sources/css/R521-1.txt"),
]


def money_value(v):
    return {"kind": "value", "type": MONEY, "value": v, "currency": "EUR"}


def scalar_value(kind, v):
    if kind == INTEGER:
        return {"kind": "value", "type": INTEGER, "value": v}
    return {"kind": "value", "type": kind, "value": v}


def dataset(name, kind, rows, fr_desc, en_desc, coverage_start):
    vals = []
    for (start, end, v, text_form, anchor_txt) in rows:
        anchor = f"{NS}#" + anchor_txt.replace(
            "sources/css/", "CSS_").replace(".txt", "").replace("-", "_")
        if anchor_txt.endswith("-2008.txt"):
            anchor = f"{NS}#CSS_R521_1_PRE2026"
        if anchor_txt.endswith("-2015.txt"):
            anchor = f"{NS}#CSS_D521_3_PRE2022"
        rid = f"{NS}:param:{name}#{start}"
        val = money_value(v) if kind == MONEY else scalar_value(kind, v)
        vals.append({
            "id": rid,
            "valid": {"start": start, "endExclusive": end},
            "value": val,
            "anchors": [anchor],
            "labels": [
                {"language": "fr", "status": "unofficial",
                 "text": f"{fr_desc}: valeur applicable à compter du {start}"},
                {"language": "en", "status": "unofficial",
                 "text": f"{en_desc}: value applicable from {start}"},
            ],
        })
    return {
        "labels": [
            {"language": "fr", "status": "unofficial", "text": fr_desc},
            {"language": "en", "status": "unofficial", "text": en_desc},
        ],
        "schemaVersion": "law.params/0.1",
        "kind": "parameter-dataset",
        "id": f"{NS}:param:{name}",
        "parameter": f"{NS}#{name}",
        "valueType": kind,
        "timeAxis": "legal_time",
        "granularity": "date",
        "coverage": {"start": coverage_start, "endExclusive": None},
        "values": vals,
    }


def build():
    outputs = {}
    for (name, kind, v, text_form, anchor_txt, start,
            fr_desc, en_desc) in SPECS:
        blob = (PKG / anchor_txt).read_text(encoding="utf-8")
        assert text_form in blob, (
            f"{name}: text form {text_form!r} absent from {anchor_txt}")
        outputs[f"bareme/{name}.lawparam.json"] = dataset(
            name, kind, [(start, None, v, text_form, anchor_txt)],
            fr_desc, en_desc, start)
    # Age threshold: two rows, one per edition.
    rows = []
    for (start, end, v, text_form, anchor_txt) in AGE_ROWS:
        blob = (PKG / anchor_txt).read_text(encoding="utf-8")
        assert text_form in blob, (
            f"AgeMajoration: text form {text_form!r} absent from {anchor_txt}")
        rows.append((start, end, v, text_form, anchor_txt))
    outputs["bareme/AgeMajoration.lawparam.json"] = dataset(
        "AgeMajoration", INTEGER, rows,
        "âge d'ouverture de la majoration (L. 521-3)",
        "age opening the supplement (L. 521-3)",
        "2008-04-30")
    return outputs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    assert args.check or args.write, "give --check or --write"
    outputs = build()
    if args.write:
        for rel, doc in outputs.items():
            p = PKG / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
        nrows = sum(len(d["values"]) for d in outputs.values())
        print(f"WROTE {len(outputs)} datasets, {nrows} rows")
        return 0
    errors = []
    for rel, doc in outputs.items():
        p = PKG / rel
        want = json.dumps(doc, ensure_ascii=False, indent=2) + "\n"
        if not p.exists():
            errors.append(f"missing {rel}")
        elif p.read_text(encoding="utf-8") != want:
            errors.append(f"drift {rel}")
    nrows = sum(len(d["values"]) for d in outputs.values())
    print(f"datasets: {len(outputs)}, rows: {nrows}, "
          f"anchor-text verified: {len(outputs)}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print("  " + e)
        return 1
    print("BAREME OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
