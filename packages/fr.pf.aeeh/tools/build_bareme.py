#!/usr/bin/env python3
"""Bareme builder for package fr.pf.aeeh (CNAF wave 3, lane fr-cnaf-pf-handicap).

Common builder per plan 5.2.5: parameter spec (name, unit, anchor, rule for
extracting the figure from pinned text), windows from versions.

Every rate below is read from the pinned fragment text; the builder refuses
to emit a row whose text form is absent from the anchor fragment ("figure
must stand in the anchor text"). Percent text forms keep French formatting
(comma decimals, "p. 100" / "%"); row values are Decimal fractions
(APL convention: 32 p. 100 -> "0.32").

Windows come from the pinned version debuts (sources/articles.json); one row
covers every edition inside its window (APL convention). All three rate
articles are stable since 2006-01-01, so every D-rate row opens there (the
OpenFisca 2012-01 cases run on the same rates). R541 threshold rows open
at 2021-01-01 (R541 rules open at coverage start, D-01); the R541-1
thresholds span the 2022-01-31 reform with unchanged values, hence two
rows each (AAH-gelees pattern: same value, per-version anchors).

Deliberately NOT in the bareme (case inputs with provenance instead):
  - BMAF monthly amount in euros (L. 551-1 base; arretes unpinned, D-Q4) ->
    input bmaf_retenue (boundary B-PFAEEH-BMAF-EURO);
  - sixth-category complement: equals the MTP amount (L. 341-4, external,
    unpinned) -> input montant_mtp_retenu (boundary B-PFAEEH-MTP);
  - category expense amounts (each "montant fixe par arrete" of R. 541-2)
    -> retained seuil_depenses_retenu inputs (B-PFAEEH-SEUILS-ARRETE);
  - durations (3/5/2 years, 4 months, civil-month counts) stay literals
    in rules (pf-core precedent: prescription 2/5 years are literals).

Usage:
  python3 corpus/laws/fr/pf-aeeh/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-aeeh/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-aeeh"

NS = "urn:fr:corpus:clir:pf-aeeh"

MONEY = {"name": "urn:law:std#Money"}
DECIMAL = {"name": "urn:law:std#Decimal"}
INTEGER = {"name": "urn:law:std#Integer"}

# (name, kind, value, text_form, anchor_txt, valid_start, fr_desc, en_desc)
SPECS = [
    # D541-1: base allowance rate (32 p. 100 of the L. 551-1 monthly base).
    ("TauxAeehBase", DECIMAL, "0.32", "32 p. 100",
     "sources/css/D541-1.txt", "2006-01-01",
     "taux de l'allocation proprement dite (D. 541-1)",
     "base allowance rate (D. 541-1)"),
    # D541-2: complements, categories 1-5 (percent of the AF monthly base).
    ("TauxComplementCategorie1", DECIMAL, "0.24", "24 %",
     "sources/css/D541-2.txt", "2006-01-01",
     "taux du complément de première catégorie (D. 541-2)",
     "first-category supplement rate (D. 541-2)"),
    ("TauxComplementCategorie2", DECIMAL, "0.65", "65 %",
     "sources/css/D541-2.txt", "2006-01-01",
     "taux du complément de deuxième catégorie (D. 541-2)",
     "second-category supplement rate (D. 541-2)"),
    ("TauxComplementCategorie3", DECIMAL, "0.92", "92 %",
     "sources/css/D541-2.txt", "2006-01-01",
     "taux du complément de troisième catégorie (D. 541-2)",
     "third-category supplement rate (D. 541-2)"),
    ("TauxComplementCategorie4", DECIMAL, "1.4257", "142,57 %",
     "sources/css/D541-2.txt", "2006-01-01",
     "taux du complément de quatrième catégorie (D. 541-2)",
     "fourth-category supplement rate (D. 541-2)"),
    ("TauxComplementCategorie5", DECIMAL, "1.8221", "182,21 %",
     "sources/css/D541-2.txt", "2006-01-01",
     "taux du complément de cinquième catégorie (D. 541-2)",
     "fifth-category supplement rate (D. 541-2)"),
    # D541-4: isolated-parent supplement (MPI), by granted category 2-6.
    ("TauxMpiCategorie2", DECIMAL, "0.13", "13 %",
     "sources/css/D541-4.txt", "2006-01-01",
     "taux MPI, complément de deuxième catégorie (D. 541-4 a)",
     "MPI rate, second-category supplement (D. 541-4 a)"),
    ("TauxMpiCategorie3", DECIMAL, "0.18", "18 %",
     "sources/css/D541-4.txt", "2006-01-01",
     "taux MPI, complément de troisième catégorie (D. 541-4 b)",
     "MPI rate, third-category supplement (D. 541-4 b)"),
    ("TauxMpiCategorie4", DECIMAL, "0.57", "57 %",
     "sources/css/D541-4.txt", "2006-01-01",
     "taux MPI, complément de quatrième catégorie (D. 541-4 c)",
     "MPI rate, fourth-category supplement (D. 541-4 c)"),
    ("TauxMpiCategorie5", DECIMAL, "0.73", "73 %",
     "sources/css/D541-4.txt", "2006-01-01",
     "taux MPI, complément de cinquième catégorie (D. 541-4 d)",
     "MPI rate, fifth-category supplement (D. 541-4 d)"),
    ("TauxMpiCategorie6", DECIMAL, "1.07", "107 %",
     "sources/css/D541-4.txt", "2006-01-01",
     "taux MPI, complément de sixième catégorie (D. 541-4 e)",
     "MPI rate, sixth-category supplement (D. 541-4 e)"),
]

# (name, kind, rows, fr_desc, en_desc): R541 thresholds, percent points /
# hours per week as Decimal ("80" means 80 %). Each row is
# (start, endExclusive, value, text_form, anchor_txt, anchor_frag):
# anchor_frag names the fragment in force during the row (per-version
# anchors where the article was reformed; base fragments otherwise).
ROWSPECS = [
    ("SeuilIncapacite80", DECIMAL, [
        ("2021-01-01", "2022-01-31", "80", "80 %",
         "sources/css/R541-1-2005.txt", "CSS_R541_1_PRE2022_ED2021_01"),
        ("2022-01-31", None, "80", "80 %",
         "sources/css/R541-1.txt", "CSS_R541_1"),
    ],
     "seuil d'incapacité permanente, premier alinéa L. 541-1 (R. 541-1)",
     "permanent-incapacity threshold, L. 541-1 para. 1 (R. 541-1)"),
    ("SeuilIncapacite50", DECIMAL, [
        ("2021-01-01", "2022-01-31", "50", "50 %",
         "sources/css/R541-1-2005.txt", "CSS_R541_1_PRE2022_ED2021_01"),
        ("2022-01-31", None, "50", "50 %",
         "sources/css/R541-1.txt", "CSS_R541_1"),
    ],
     "minimum d'incapacité permanente, troisième alinéa L. 541-1 (R. 541-1)",
     "permanent-incapacity minimum, L. 541-1 para. 3 (R. 541-1)"),
    ("SeuilReduction20", DECIMAL, [
        ("2021-01-01", None, "20", "20 %",
         "sources/css/R541-2.txt", "CSS_R541_2"),
    ],
     "réduction d'activité d'au moins 20 % (R. 541-2, 2°/3°/4°)",
     "work reduction of at least 20% (R. 541-2, 2/3/4)"),
    ("SeuilReduction50", DECIMAL, [
        ("2021-01-01", None, "50", "50 %",
         "sources/css/R541-2.txt", "CSS_R541_2"),
    ],
     "réduction d'activité d'au moins 50 % (R. 541-2, 3°/4°)",
     "work reduction of at least 50% (R. 541-2, 3/4)"),
    ("SeuilTierce8h", DECIMAL, [
        ("2021-01-01", None, "8", "huit heures",
         "sources/css/R541-2.txt", "CSS_R541_2"),
    ],
     "tierce personne au moins huit heures par semaine (R. 541-2, 2°/3°/4°)",
     "third person at least eight hours a week (R. 541-2, 2/3/4)"),
    ("SeuilTierce20h", DECIMAL, [
        ("2021-01-01", None, "20", "vingt heures",
         "sources/css/R541-2.txt", "CSS_R541_2"),
    ],
     "tierce personne au moins vingt heures par semaine (R. 541-2, 3°/4°)",
     "third person at least twenty hours a week (R. 541-2, 3/4)"),
]


def scalar_value(kind, v):
    return {"kind": "value", "type": kind, "value": v}


def dataset(name, kind, rows, fr_desc, en_desc, coverage_start):
    vals = []
    for row in rows:
        if len(row) == 6:
            start, end, v, text_form, anchor_txt, anchor_frag = row
            anchor = f"{NS}#{anchor_frag}"
        else:
            start, end, v, text_form, anchor_txt = row
            anchor = f"{NS}#" + anchor_txt.replace(
                "sources/css/", "CSS_").replace(".txt", "").replace("-", "_")
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
    for (name, kind, v, text_form, anchor_txt, start,
            fr_desc, en_desc) in SPECS:
        blob = (PKG / anchor_txt).read_text(encoding="utf-8")
        assert text_form in blob, (
            f"{name}: text form {text_form!r} absent from {anchor_txt}")
        outputs[f"bareme/{name}.lawparam.json"] = dataset(
            name, kind, [(start, None, v, text_form, anchor_txt)],
            fr_desc, en_desc, start)
    for (name, kind, rows, fr_desc, en_desc) in ROWSPECS:
        for (start, _end, _v, text_form, anchor_txt, _frag) in rows:
            blob = (PKG / anchor_txt).read_text(encoding="utf-8")
            assert text_form in blob, (
                f"{name}: text form {text_form!r} absent from {anchor_txt}")
        outputs[f"bareme/{name}.lawparam.json"] = dataset(
            name, kind, rows, fr_desc, en_desc, rows[0][0])
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
