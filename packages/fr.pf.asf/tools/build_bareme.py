#!/usr/bin/env python3
"""Bareme builder for package fr.pf.asf (CNAF wave 3, lane fr-cnaf-pf-small).

Common builder per plan 5.2.5: parameter spec (name, unit, rows with anchor),
windows from pinned versions. Every rate and figure is read from the pinned
fragment text; the builder refuses to emit a row whose text form is absent
from the anchor file ("figure must stand in the anchor text"). Percent text
forms keep French formatting (comma decimals); row values are Decimal
fractions (APL convention: 56,25 % -> "0.5625"). Integer params are numbers.

Deliberately NOT in the bareme (case inputs with provenance instead):
  - BMAF monthly amount in euros (L. 551-1 base; arrete unpinned, D-Q4) ->
    input bmaf_retenu (boundary B-PFASF-BMAF-EURO);
  - maintenance-contribution threshold scale (R. 582-1, outside scope):
    seuil_contribution input (boundary B-PFASF-SEUIL-CONTRIBUTION);
  - RSA flat amount and AAH full rate (D523-2 insolvency channel, wave 4):
    inputs (boundary B-PFASF-MINIMA-MONTANTS).

Usage:
  python3 corpus/laws/fr/pf-asf/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-asf/tools/build_bareme.py --write
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-asf"

NS = "urn:fr:corpus:clir:pf-asf"

MONEY = {"name": "urn:law:std#Money"}
DECIMAL = {"name": "urn:law:std#Decimal"}
INTEGER = {"name": "urn:law:std#Integer"}

# (name, kind, rows, fr_desc, en_desc)
# row = (valid_start, valid_end, value, text_form, anchor_frag, anchor_txt)
SPECS = [
    # R523-7 1°: double-orphan (or assimilated) rate, yearly rows.
    ("TauxAsfDoubleOrphelin", DECIMAL,
     [("2014-04-01", "2015-04-01", "0.315", "31,50 %",
       "CSS_R523_7_PRE2015", "sources/css/R523-7-2014.txt"),
      ("2015-04-01", "2016-04-03", "0.33", "33 %",
       "CSS_R523_7_PRE2016", "sources/css/R523-7-2015.txt"),
      ("2016-04-03", "2017-04-15", "0.345", "34,5 %",
       "CSS_R523_7_PRE2017", "sources/css/R523-7-2016.txt"),
      ("2017-04-15", "2018-04-01", "0.36", "36 %",
       "CSS_R523_7_PRE2018", "sources/css/R523-7-2017.txt"),
      ("2018-04-01", "2022-11-01", "0.375", "37,5 %",
       "CSS_R523_7_PRE2022", "sources/css/R523-7-2018.txt"),
      ("2022-11-01", None, "0.5625", "56,25 %",
       "CSS_R523_7", "sources/css/R523-7.txt")],
     "taux ASF orphelin des deux parents (R. 523-7)",
     "ASF rate for children orphaned of both parents (R. 523-7)"),
    # R523-7 2°: single-parent rate, yearly rows.
    ("TauxAsfSimple", DECIMAL,
     [("2014-04-01", "2015-04-01", "0.2363", "23,63 %",
       "CSS_R523_7_PRE2015", "sources/css/R523-7-2014.txt"),
      ("2015-04-01", "2016-04-03", "0.2476", "24,76 %",
       "CSS_R523_7_PRE2016", "sources/css/R523-7-2015.txt"),
      ("2016-04-03", "2017-04-15", "0.2589", "25,89 %",
       "CSS_R523_7_PRE2017", "sources/css/R523-7-2016.txt"),
      ("2017-04-15", "2018-04-01", "0.2702", "27,02 %",
       "CSS_R523_7_PRE2018", "sources/css/R523-7-2017.txt"),
      ("2018-04-01", "2022-11-01", "0.2813", "28,13 %",
       "CSS_R523_7_PRE2022", "sources/css/R523-7-2018.txt"),
      ("2022-11-01", None, "0.422", "42,2 %",
       "CSS_R523_7", "sources/css/R523-7.txt")],
     "taux ASF orphelin d'un parent (R. 523-7)",
     "ASF rate for children orphaned of one parent (R. 523-7)"),
    # D523-3: no payment under 15 euros.
    ("SeuilNonVersementAsf", MONEY,
     [("2018-07-01", None, "15", "15 euros",
       "CSS_D523_3", "sources/css/D523-3.txt")],
     "seuil de non-versement de l'ASF (D. 523-3)",
     "ASF non-payment threshold (D. 523-3)"),
    # R523-1: one-month default persistence.
    ("DelaiCarenceUnMois", INTEGER,
     [("2017-04-15", None, 1, "un mois",
       "CSS_R523_1", "sources/css/R523-1.txt")],
     "délai d'un mois de la défaillance (R. 523-1)",
     "one-month default period (R. 523-1)"),
    # R523-3 al. 1: continuation beyond the fourth monthly payment.
    ("DelaiQuatriemeMensualite", INTEGER,
     [("2017-04-15", None, 4, "quatrième mensualité",
       "CSS_R523_3", "sources/css/R523-3.txt")],
     "quatrième mensualité du maintien (R. 523-3)",
     "fourth monthly payment of continuation (R. 523-3)"),
    # D523-2 III: fund control within four months, then yearly.
    ("DelaiControleQuatreMois", INTEGER,
     [("2018-07-27", None, 4, "quatre mois",
       "CSS_D523_2", "sources/css/D523-2.txt")],
     "délai de contrôle de quatre mois (D. 523-2)",
     "four-month control period (D. 523-2)"),
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
