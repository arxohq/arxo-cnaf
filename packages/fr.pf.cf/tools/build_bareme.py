#!/usr/bin/env python3
"""Bareme builder for package fr.pf.cf (CNAF wave 3, lane fr-cnaf-pf-small).

Common builder per plan 5.2.5: parameter spec (name, unit, rows with anchor),
windows from pinned versions. Every rate and figure is read from the pinned
fragment text; the builder refuses to emit a row whose text form is absent
from the anchor file ("figure must stand in the anchor text"). Percent text
forms keep French formatting (comma decimals); row values are Decimal
fractions (APL convention: 41,65 % -> "0.4165"). Integer params are numbers.

Deliberately NOT in the bareme (case inputs with provenance instead):
  - BMAF monthly amount in euros (L. 551-1 base; arrete unpinned, D-Q4) ->
    input bmaf_retenu (boundary B-PFCF-BMAF-EURO);
  - L. 755-3 monthly base in euros (DOM; arrete unpinned) ->
    input base_dom_retenue (boundary B-PFCF-DOM-LIAISON);
  - yearly applicable plafond nominals (decree/arrete unpinned, DSS_PENDING):
    plafond_base_cf and majoration_biactivite arrive as inputs
    (boundary B-PFCF-PLAFOND-NOMINAL);
  - N-2 resource assessment (R. 532-1/R. 532-3, fr.tax.income_for_pf):
    ressources_menage input (boundary B-PFCF-RESSOURCES-N2).

Usage:
  python3 corpus/laws/fr/pf-cf/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-cf/tools/build_bareme.py --write
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-cf"

NS = "urn:fr:corpus:clir:pf-cf"

MONEY = {"name": "urn:law:std#Money"}
DECIMAL = {"name": "urn:law:std#Decimal"}
INTEGER = {"name": "urn:law:std#Integer"}

# (name, kind, rows, fr_desc, en_desc)
# row = (valid_start, valid_end, value, text_form, anchor_frag, anchor_txt)
SPECS = [
    # D522-1: base CF rate 41,65 % of the BMAF.
    ("TauxCfBase", DECIMAL,
     [("1989-08-31", None, "0.4165", "41,65 p. 100",
       "CSS_D522_1", "sources/css/D522-1.txt")],
     "taux du complément familial (D. 522-1)",
     "complement familial rate (D. 522-1)"),
    # D522-2: majore rate 58,33 % until 2018-04-01, then 62,48 %.
    ("TauxCfMajore", DECIMAL,
     [("2017-04-15", "2018-04-01", "0.5833", "58,33 %",
       "CSS_D522_2_PRE2018", "sources/css/D522-2-2017.txt"),
      ("2018-04-01", None, "0.6248", "62,48 %",
       "CSS_D522_2", "sources/css/D522-2.txt")],
     "taux du complément familial majoré (D. 522-2)",
     "increased complement familial rate (D. 522-2)"),
    # R522-2 al. 2: the 25 % / 30 % increments per child are NOT parameters
    # here (D-83): the amounts are the published ones (inputs of
    # 03-plafond.law, sources/dss-plafonds/), each rounded on its own.
    # R522-2 al. 3: each working member earns at least 13,6 % of the
    # annual social-security ceiling.
    ("TauxBiactifRevenu", DECIMAL,
     [("2011-11-01", None, "0.136", "13,6 %",
       "CSS_R522_2_PRE2022", "sources/css/R522-2-2011.txt")],
     "seuil de revenu professionnel par membre du couple (R. 522-2)",
     "work-income threshold per couple member (R. 522-2)"),
    # R522-1: at least three children aged three and over.
    ("SeuilEnfantsCf", INTEGER,
     [("2000-01-29", None, 3, "trois enfants",
       "CSS_R522_1", "sources/css/R522-1.txt")],
     "enfants pour le complément familial (R. 522-1)",
     "children for the complement familial (R. 522-1)"),
    ("AgeCfMinimum", INTEGER,
     [("2000-01-29", None, 3, "trois ans",
       "CSS_R522_1", "sources/css/R522-1.txt")],
     "âge minimum des enfants (R. 522-1)",
     "minimum child age (R. 522-1)"),
    # R522-1 al. 2: open until age 21 within the remuneration ceiling.
    ("AgeCfLimite", INTEGER,
     [("2000-01-29", None, 21, "vingt et un ans",
       "CSS_R522_1", "sources/css/R522-1.txt")],
     "âge limite du complément familial (R. 522-1)",
     "complement familial age limit (R. 522-1)"),
    # R522-3 al. 1: differential within twelve monthly amounts.
    ("SeuilDifferentielCf", INTEGER,
     [("2014-01-01", None, 12, "douze fois",
       "CSS_R522_3", "sources/css/R522-3.txt")],
     "seuil du complément différentiel en mensualités (R. 522-3)",
     "differential threshold in monthly amounts (R. 522-3)"),
    # D755-6: DOM base CF rate 41,65 % of the L755-3 monthly base.
    ("TauxCfDomBase", DECIMAL,
     [("2020-04-01", None, "0.4165", "41,65 %",
       "CSS_D755_6", "sources/css/D755-6.txt")],
     "taux du complément familial DOM (D. 755-6)",
     "DOM complement familial rate (D. 755-6)"),
    # D755-6-1: DOM majore rate 62,48 % of the L551-1 BMAF.
    ("TauxCfDomMajore", DECIMAL,
     [("2020-04-01", None, "0.6248", "62,48 %",
       "CSS_D755_6_1", "sources/css/D755-6-1.txt")],
     "taux du complément familial DOM majoré (D. 755-6-1)",
     "increased DOM complement familial rate (D. 755-6-1)"),
    # R755-1: every counted DOM child is over three.
    ("AgeCfDomMinimum", INTEGER,
     [("1996-01-01", None, 3, "trois ans",
       "CSS_R755_1", "sources/css/R755-1.txt")],
     "âge minimum des enfants DOM (R. 755-1)",
     "minimum DOM child age (R. 755-1)"),
    # R755-1: at least one counted DOM child is under five.
    ("AgeCfDomLimite", INTEGER,
     [("1996-01-01", None, 5, "cinq ans",
       "CSS_R755_1", "sources/css/R755-1.txt")],
     "âge limite du jeune DOM (R. 755-1)",
     "young DOM child age limit (R. 755-1)"),
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
