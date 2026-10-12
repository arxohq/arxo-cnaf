#!/usr/bin/env python3
"""Bareme builder for package fr.pf.ars (CNAF wave 3, lane fr-cnaf-pf-small).

Common builder per plan 5.2.5: parameter spec (name, unit, rows with anchor),
windows from pinned versions. Every rate and figure is read from the pinned
fragment text; the builder refuses to emit a row whose text form is absent
from the anchor file ("figure must stand in the anchor text"). Percent text
forms keep French formatting (comma decimals); row values are Decimal
fractions (APL convention: 89,72 % -> "0.8972"). Integer params are numbers.

Deliberately NOT in the bareme (case inputs with provenance instead):
  - BMAF monthly amount in euros (L. 551-1 base; arrete unpinned, D-Q4) ->
    input bmaf_retenu (boundary B-PFARS-BMAF-EURO);
  - yearly applicable plafond nominals (decree/arrete unpinned, DSS_PENDING):
    plafond_base_ars arrives as input (boundary B-PFARS-PLAFOND-NOMINAL);
  - N-2 resource assessment (R. 532-3/R. 532-8 via R. 543-6,
    fr.tax.income_for_pf): ressources_menage input (boundary
    B-PFARS-RESSOURCES-N2).

Usage:
  python3 corpus/laws/fr/pf-ars/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-ars/tools/build_bareme.py --write
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-ars"

NS = "urn:fr:corpus:clir:pf-ars"

MONEY = {"name": "urn:law:std#Money"}
DECIMAL = {"name": "urn:law:std#Decimal"}
INTEGER = {"name": "urn:law:std#Integer"}

# (name, kind, rows, fr_desc, en_desc)
# row = (valid_start, valid_end, value, text_form, anchor_frag, anchor_txt)
SPECS = [
    # D543-1: ARS rate by age band (as of 31 December of the rentree year).
    ("TauxArsMoins11", DECIMAL,
     [("2012-06-30", None, "0.8972", "89,72 %",
       "CSS_D543_1", "sources/css/D543-1.txt")],
     "taux ARS avant onze ans (D. 543-1)",
     "ARS rate under eleven (D. 543-1)"),
    ("TauxArs11a14", DECIMAL,
     [("2012-06-30", None, "0.9467", "94,67 %",
       "CSS_D543_1", "sources/css/D543-1.txt")],
     "taux ARS onze à quatorze ans (D. 543-1)",
     "ARS rate eleven to fourteen (D. 543-1)"),
    ("TauxArs15Plus", DECIMAL,
     [("2012-06-30", None, "0.9795", "97,95 %",
       "CSS_D543_1", "sources/css/D543-1.txt")],
     "taux ARS quinze ans et plus (D. 543-1)",
     "ARS rate fifteen and over (D. 543-1)"),
    # R543-5 al. 2: ceiling +30 % per dependent child from the first.
    ("MajorationPlafondArs", DECIMAL,
     [("2008-08-03", None, "0.30", "30 %",
       "CSS_R543_5", "sources/css/R543-5.txt")],
     "majoration du plafond par enfant des le premier (R. 543-5)",
     "ceiling increment per child from the first (R. 543-5)"),
    # D543-2: no payment under 15 euros.
    ("SeuilNonVersementArs", MONEY,
     [("2002-08-08", None, "15", "15 euros",
       "CSS_D543_2", "sources/css/D543-2.txt")],
     "seuil de non-versement de l'ARS (D. 543-2)",
     "ARS non-payment threshold (D. 543-2)"),
    # R543-2: sixth birthday before 1 February after the rentree year.
    ("AgeArsSix", INTEGER,
     [("2008-08-03", None, 6, "sixième anniversaire",
       "CSS_R543_2", "sources/css/R543-2.txt")],
     "âge d'ouverture de l'ARS, six ans (R. 543-2)",
     "ARS opening age, six (R. 543-2)"),
    # R543-2 al. 2: under eighteen on 15 September.
    ("AgeArsDixHuit", INTEGER,
     [("2008-08-03", None, 18, "dix-huit ans",
       "CSS_R543_2", "sources/css/R543-2.txt")],
     "âge limite de l'ARS, dix-huit ans (R. 543-2)",
     "ARS age limit, eighteen (R. 543-2)"),
    # R543-2 al. 3: increase at eleven, then at fifteen, in the calendar year.
    ("AgeArsOnze", INTEGER,
     [("2008-08-03", None, 11, "onze ans",
       "CSS_R543_2", "sources/css/R543-2.txt")],
     "âge de la première majoration ARS (R. 543-2)",
     "first ARS increase age (R. 543-2)"),
    ("AgeArsQuinze", INTEGER,
     [("2008-08-03", None, 15, "quinze ans",
       "CSS_R543_2", "sources/css/R543-2.txt")],
     "âge de la seconde majoration ARS (R. 543-2)",
     "second ARS increase age (R. 543-2)"),
]


def money_value(v):
    return {"kind": "value", "type": MONEY, "value": v, "currency": "EUR"}


def scalar_value(kind, v):
    if kind == INTEGER:
        return {"kind": "value", "type": INTEGER, "value": v}
    return {"kind": "value", "type": kind, "value": v}


def dataset(name, kind, rows, fr_desc, en_desc):
    vals = []
    for (start, end, v, text_form, anchor_frag, anchor_txt) in rows:
        blob = (PKG / anchor_txt).read_text(encoding="utf-8")
        assert text_form in blob, (
            f"{name}: text form {text_form!r} absent from {anchor_txt}")
        anchor = f"{NS}#{anchor_frag}"
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
        "coverage": {"start": rows[0][0], "endExclusive": None},
        "values": vals,
    }


def build():
    outputs = {}
    for (name, kind, rows, fr_desc, en_desc) in SPECS:
        outputs[f"bareme/{name}.lawparam.json"] = dataset(
            name, kind, rows, fr_desc, en_desc)
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
    import sys
    sys.exit(main())
