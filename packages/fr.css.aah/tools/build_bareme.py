#!/usr/bin/env python3
"""Bareme builder for package fr.css.aah (CNAF wave 4, lane fr-cnaf-aah).

Every rate below is read from the pinned fragment text; the builder refuses
to emit a row whose text form is absent from the anchor fragment ("figure
must stand in the anchor text"). Percent text forms keep French formatting;
row values are Decimal fractions (APL convention: 81 % -> "0.81").

Windows come from the pinned version debuts (sources/articles.json): the
2023-10-01 reform splits the couple majorations (81 % and 30 % live only in
the PRE2023 wordings). Both couple figures get a FROZEN continuation row
[start = reform, end = none): decree 2022-1694 art. 2 freezes the 30.09.2023
modalities for the transitional comparison, so the engine must still resolve
the figure after the source wording is replaced; the frozen row anchors the
old wording (the figure's source) plus the freezing decree article.

Deliberately NOT in the bareme (retained case inputs with provenance):
  - monthly AAH euro amount (L. 821-3-1, set by decree) and the L. 161-25
    revalorisation coefficient: pinned and BUILT by the amount chain
    (07-montant-chaine.law, tools/build_montant_chaine.py); a case may still
    supply montant_mensuel_retenu, which prevails (B-AAH-MONTANT-EURO);
  - SMIC brut mensuel for 151.67 h (D. 821-5 cap; smic series 2021-2025
    awaits the farm) -> input smic_brut_mensuel_retenu (B-AAH-SMIC);
  - 80 %/50 % incapacity thresholds (D. 821-1): commission-established facts.

Usage:
  python3 corpus/laws/fr/aah/tools/build_bareme.py --check
  python3 corpus/laws/fr/aah/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "aah"

NS = "urn:fr:corpus:clir:aah"

DECIMAL = {"name": "urn:law:std#Decimal"}

# (name, value, text_form, anchor_file, anchor_frag, start, end,
#  fr_desc, en_desc, frozen_extra_frag): anchor_frag names a declared
# fragment holding the figure; frozen_extra_frag (only with end) names the
# decree article freezing the figure past the wording's end.
SPECS = [
    # Old D821-2 para. 2: couple plafond majoration, before 2023-10-01.
    ("MajorationPlafondCoupleAncien", "0.81", "majoré de 81 %",
     "sources/css/D821-2-2019.txt", "CSS_D821_2_PRE2023_ED2023_09_01",
     "2021-01-01", "2023-10-01",
     "majoration du plafond pour couple avant le 01.10.2023 (D. 821-2 ancien)",
     "couple ceiling increase before 01.10.2023 (former D. 821-2)",
     "JORF_D1694_ART2"),
    # D821-2 para. 2: half-plafond per dependent child (both wordings).
    ("MajorationPlafondEnfant", "0.5", "la moitié",
     "sources/css/D821-2.txt", "CSS_D821_2_ED2023_10_01",
     "2021-01-01", None,
     "majoration du plafond par enfant à charge (D. 821-2)",
     "ceiling increase per dependent child (D. 821-2)",
     None),
    # D821-5: ESAT joint cap is 100 % of the gross SMIC (both wordings).
    ("PlafondCumulEsat", "1.0", "100 %",
     "sources/css/D821-5.txt", "CSS_D821_5_ED2023_10_01",
     "2021-01-01", None,
     "plafond du cumul AAH et rémunération garantie (D. 821-5)",
     "joint AAH and guaranteed-pay cap (D. 821-5)",
     None),
    # D821-5: +15 % for a dependent child or ascendant (both wordings).
    ("MajorationEsatEnfantAscendant", "0.15", "majoré de 15 %",
     "sources/css/D821-5.txt", "CSS_D821_5_ED2023_10_01",
     "2021-01-01", None,
     "majoration ESAT pour enfant ou ascendant à charge (D. 821-5)",
     "ESAT increase for a dependent child or ascendant (D. 821-5)",
     None),
    # Old D821-5 para. 2: +30 % for a couple, before 2023-10-01.
    ("MajorationEsatCoupleAncien", "0.3", "majoré de 30 %",
     "sources/css/D821-5-2007.txt", "CSS_D821_5_PRE2023_ED2023_09_01",
     "2021-01-01", "2023-10-01",
     "majoration ESAT pour couple avant le 01.10.2023 (D. 821-5 ancien)",
     "ESAT couple increase before 01.10.2023 (former D. 821-5)",
     "JORF_D1694_ART2"),
]


def scalar_value(v):
    return {"kind": "value", "type": DECIMAL, "value": v}


FROZEN_FR = "figure gelée au 30.09.2023 (décret 2022-1694 art. 2)"
FROZEN_EN = "figure frozen at 30.09.2023 (decree 2022-1694 art. 2)"


def dataset(name, rows, fr_desc, en_desc, coverage_start):
    vals = []
    for (start, end, v, text_form, anchor_frag, extra) in rows:
        anchors = [f"{NS}#{anchor_frag}"]
        suffix_fr = f": valeur applicable à compter du {start}"
        suffix_en = f": value applicable from {start}"
        if extra is not None:
            anchors.append(f"{NS}#{extra}")
            suffix_fr = f" — {FROZEN_FR}" + suffix_fr
            suffix_en = f" — {FROZEN_EN}" + suffix_en
        rid = f"{NS}:param:{name}#{start}"
        vals.append({
            "id": rid,
            "valid": {"start": start, "endExclusive": end},
            "value": scalar_value(v),
            "anchors": anchors,
            "labels": [
                {"language": "fr", "status": "unofficial",
                 "text": f"{fr_desc}" + suffix_fr},
                {"language": "en", "status": "unofficial",
                 "text": f"{en_desc}" + suffix_en},
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
        "valueType": DECIMAL,
        "timeAxis": "legal_time",
        "granularity": "date",
        "coverage": {"start": coverage_start, "endExclusive": None},
        "values": vals,
    }


def build():
    outputs = {}
    for (name, v, text_form, anchor_file, anchor_frag, start, end,
            fr_desc, en_desc, frozen_extra) in SPECS:
        blob = (PKG / anchor_file).read_text(encoding="utf-8")
        assert text_form in blob, (
            f"{name}: text form {text_form!r} absent from {anchor_file}")
        rows = [(start, end, v, text_form, anchor_frag, None)]
        if end is not None and frozen_extra is not None:
            rows.append((end, None, v, text_form, anchor_frag,
                         frozen_extra))
        outputs[f"bareme/{name}.lawparam.json"] = dataset(
            name, rows, fr_desc, en_desc, "2021-01-01")
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
