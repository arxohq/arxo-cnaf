#!/usr/bin/env python3
"""Pin the AJPP bareme (law.params/0.1 datasets from pinned fragments).

Only values whose French text form stands in a pinned fragment are emitted
("figure must stand in the anchor text"). Percent text forms keep French
formatting (comma decimals, " %"); row values are Decimal fractions
(APL/pf-af convention: 10,63 % -> "0.1063"). The FINISH ajpp-death wave
pins the D544/R544 decree figures; the retained BMAF euro figure, the net
hourly SMIC and the CRDS rate stay case inputs with provenance
(B-PFAJPP-BMAF-FIGURE, B-PFAJPP-SHN-NET, B-PFAJPP-CRDS-TAUX). OpenFisca AJPP
parameters (frozen 2006-06-05) are measurement only, in REPORT.

Usage:
  python3 corpus/laws/fr/pf-ajpp/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-ajpp/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-ajpp"

NS = "urn:fr:corpus:clir:pf-ajpp"

INTEGER = {"name": "urn:law:std#Integer"}
DECIMAL = {"name": "urn:law:std#Decimal"}

# (name, kind, rows, fr_desc, en_desc); rows = list of
# (start, end, value, text_form, anchor_frag, anchor_txt).
SPECS = [
    # L544-3: 310 daily allowances maximum (all pinned versions).
    ("Plafond310Jours", INTEGER,
     [("2021-01-01", None, 310, "trois cent dix", "CSS_L544_3_PRE2021",
       "sources/css/L544-3-2019-03-11.txt")],
     "nombre maximum d'allocations journalières (L. 544-3)",
     "maximum daily allowances (L. 544-3)"),
    # L544-2: re-exam floor, six months (2019 and 2026 versions).
    ("DelaiReexamenMinMois", INTEGER,
     [("2021-01-01", None, 6, "six mois", "CSS_L544_2_PRE2026",
       "sources/css/L544-2-2019-03-11.txt")],
     "réexamen à une échéance de six mois au moins (L. 544-2)",
     "re-examination no earlier than six months (L. 544-2)"),
    # L544-2: re-exam ceiling, "un an" (2019) then "quatorze mois" (2026).
    ("DelaiReexamenMaxMois", INTEGER,
     [("2021-01-01", "2026-06-14", 12, "un an", "CSS_L544_2_PRE2026",
       "sources/css/L544-2-2019-03-11.txt"),
      ("2026-06-14", None, 14, "quatorze mois", "CSS_L544_2",
       "sources/css/L544-2.txt")],
     "réexamen au plus tard : un an puis quatorze mois (L. 544-2)",
     "re-examination deadline: one year then fourteen months (L. 544-2)"),
    # D544-1: 3-year payment limit per child and pathology.
    ("DureeMaxAjppAnnees", INTEGER,
     [("2021-01-01", None, 3, "trois ans", "CSS_D544_1",
       "sources/css/D544-1.txt")],
     "durée maximale de versement en années, par enfant et pathologie (D. 544-1)",
     "maximum payment duration in years, per child and pathology (D. 544-1)"),
    # D544-2: re-exam request from the last month before the point.
    ("MoisPrecedantReexamen", INTEGER,
     [("2021-01-01", None, 1, "dernier mois", "CSS_D544_2",
       "sources/css/D544-2.txt")],
     "demande de réexamen à compter du dernier mois précédant l'échéance (D. 544-2)",
     "re-examination request from the last month before the point (D. 544-2)"),
    # D544-4: 22 daily allowances maximum per calendar month.
    ("PlafondMensuel22Jours", INTEGER,
     [("2021-01-01", None, 22, "supérieur à 22", "CSS_D544_4",
       "sources/css/D544-4.txt")],
     "allocations journalières maximales par mois civil (D. 544-4)",
     "maximum daily allowances per calendar month (D. 544-4)"),
    # D544-6 2020: BMAF daily rates, couple / single / half-day.
    ("TauxJournalierCouple2021", DECIMAL,
     [("2021-01-01", "2022-01-01", "0.1063", "10,63 %", "CSS_D544_6_PRE2022",
       "sources/css/D544-6-2020-09-30.txt")],
     "taux journalier 2021 couple : 10,63 % de la BMAF (D. 544-6 2020)",
     "2021 couple daily rate: 10.63% of BMAF (D. 544-6 2020)"),
    ("TauxJournalierIsole2021", DECIMAL,
     [("2021-01-01", "2022-01-01", "0.1263", "12,63 %", "CSS_D544_6_PRE2022",
       "sources/css/D544-6-2020-09-30.txt")],
     "taux journalier 2021 personne seule : 12,63 % de la BMAF (D. 544-6 2020)",
     "2021 single-person daily rate: 12.63% of BMAF (D. 544-6 2020)"),
    ("TauxDemiJourneeCouple2021", DECIMAL,
     [("2021-01-01", "2022-01-01", "0.05315", "5,315 %", "CSS_D544_6_PRE2022",
       "sources/css/D544-6-2020-09-30.txt")],
     "taux de demi-journée 2021 couple : 5,315 % de la BMAF (D. 544-6 2020)",
     "2021 couple half-day rate: 5.315% of BMAF (D. 544-6 2020)"),
    ("TauxDemiJourneeIsole2021", DECIMAL,
     [("2021-01-01", "2022-01-01", "0.06315", "6,315 %", "CSS_D544_6_PRE2022",
       "sources/css/D544-6-2020-09-30.txt")],
     "taux de demi-journée 2021 personne seule : 6,315 % de la BMAF (D. 544-6 2020)",
     "2021 single-person half-day rate: 6.315% of BMAF (D. 544-6 2020)"),
    # D544-7: 27.19 % complement threshold and amount.
    ("TauxSeuilComplementFrais", DECIMAL,
     [("2021-01-01", None, "0.2719", "27,19 %", "CSS_D544_7",
       "sources/css/D544-7.txt")],
     "seuil et montant du complément pour frais : 27,19 % de la BMAF (D. 544-7)",
     "expense-supplement threshold and amount: 27.19% of BMAF (D. 544-7)"),
    # D544-8: 22 flat monthly days for job-seekers and trainees.
    ("JoursForfaitairesDemandeur", INTEGER,
     [("2021-01-01", None, 22, "est égal à 22", "CSS_D544_8",
       "sources/css/D544-8.txt")],
     "jours forfaitaires mensuels du demandeur d'emploi (D. 544-8)",
     "monthly flat days of the job-seeker (D. 544-8)"),
    # R544-3: silence delays, second and third month.
    ("DelaiSilenceControleMois", INTEGER,
     [("2021-01-01", None, 2, "deuxième mois", "CSS_R544_3",
       "sources/css/R544-3.txt")],
     "silence du contrôle médical jusqu'au deuxième mois : avis favorable (R. 544-3)",
     "medical-control silence through the second month: favourable opinion (R. 544-3)"),
    ("DelaiSilenceOrganismeMois", INTEGER,
     [("2021-01-01", None, 3, "troisième mois", "CSS_R544_3",
       "sources/css/R544-3.txt")],
     "silence de l'organisme jusqu'au troisième mois : décision favorable (R. 544-3)",
     "body silence through the third month: favourable decision (R. 544-3)"),
]


def scalar_value(kind, v):
    return {"kind": "value", "type": kind, "value": v}


def dataset(name, kind, rows, fr_desc, en_desc, coverage_start):
    vals = []
    for (start, end, v, text_form, anchor_frag, anchor_txt) in rows:
        anchor = f"{NS}#" + anchor_frag
        rid = f"{NS}:param:{name}#{start}"
        vals.append({
            "id": rid,
            "valid": {"start": start, "endExclusive": end},
            "value": scalar_value(kind, v),
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
    for (name, kind, rows, fr_desc, en_desc) in SPECS:
        for (start, end, v, text_form, anchor_frag, anchor_txt) in rows:
            blob = (PKG / anchor_txt).read_text(encoding="utf-8")
            assert text_form in blob, (
                f"{name}: text form {text_form!r} absent from {anchor_txt}")
        outputs[f"bareme/{name}.lawparam.json"] = dataset(
            name, kind, rows, fr_desc, en_desc, "2021-01-01")
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
