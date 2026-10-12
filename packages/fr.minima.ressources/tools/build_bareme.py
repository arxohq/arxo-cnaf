#!/usr/bin/env python3
"""Bareme builder for package fr.minima.ressources (CNAF wave 4, W4-RSA).

Common builder per plan 5.2.5: parameter spec (name, unit, anchor, rule for
extracting the figure from pinned text), windows from versions.

Every rate below is read from the pinned fragment text; the builder
refuses to emit a row whose text form is absent from the anchor file
("figure must stand in the anchor text"). Percent text forms keep French
formatting (comma decimals); row values are Decimal fractions
(APL convention: 16,5 % -> "0.165").

Windows: the forfait percentages are identical in the 2016 and 2023
wordings of R. 262-9, so rows run from the coverage start 2021-01-01.

Deliberately NOT in the bareme (case inputs with provenance instead):
  - monthly MF amount (L. 262-2 euro base, decree, unpinned) -> input
    mf_mois (boundary B-RSA-MF-EURO; consistency with the fr.casf.rsa
    computation is a per-case contract until the wave-5 cascade wires it:
    B-RSA-MF-INPUT-CONTRACT);
  - DSN monthly amounts and declared resources (plan §1.1: DSN
    extraction out of scope) -> inputs montant_dsn_mois /
    ressource_declaree_mois;
  - BMAF monthly amount for the R. 262-10-1 forfaits (arretes unpinned,
    D-Q4) -> input bmaf_retenue (boundary B-MINRES-BMAF-EURO).

Usage:
  python3 corpus/laws/fr/minima-ressources/tools/build_bareme.py --check
  python3 corpus/laws/fr/minima-ressources/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "minima-ressources"

NS = "urn:fr:corpus:clir:minima-ressources"

DECIMAL = {"name": "urn:law:std#Decimal"}

# (name, kind, value, text_form, anchor_txt, valid_start, fr_desc, en_desc)
SPECS = [
    # R262-9 1°: housing flat-rate, one-person household.
    ("TauxForfaitLogement1", DECIMAL, "0.12", "12 %",
     "sources/casf/R262-9.txt", "2021-01-01",
     "forfait logement, foyer d'une personne",
     "housing flat-rate, one-person household"),
    # R262-9 2°: two-person household.
    ("TauxForfaitLogement2", DECIMAL, "0.16", "16 %",
     "sources/casf/R262-9.txt", "2021-01-01",
     "forfait logement, foyer de deux personnes",
     "housing flat-rate, two-person household"),
    # R262-9 3°: three or more persons.
    ("TauxForfaitLogement3Plus", DECIMAL, "0.165", "16,5 %",
     "sources/casf/R262-9.txt", "2021-01-01",
     "forfait logement, foyer de trois personnes ou plus",
     "housing flat-rate, household of three or more"),
    # R262-10-1, I: increased complément familial counted as a flat-rate.
    ("TauxCfMajoreForfait", DECIMAL, "0.4165", "41,65 %",
     "sources/casf/R262-10-1.txt", "2021-01-01",
     "complément familial majoré retenu forfaitairement",
     "increased complément familial counted as a flat-rate"),
    # R262-10-1, II 1°: ASF per child of L. 523-3 1°.
    ("TauxAsfForfaitRang1", DECIMAL, "0.30", "30 %",
     "sources/casf/R262-10-1.txt", "2021-01-01",
     "ASF retenue forfaitairement, enfant du 1° de L. 523-3",
     "ASF counted as a flat-rate, child of L. 523-3 1°"),
    # R262-10-1, II 2°: ASF per child of L. 523-3 2°.
    ("TauxAsfForfaitRang2", DECIMAL, "0.225", "22,5 %",
     "sources/casf/R262-10-1.txt", "2021-01-01",
     "ASF retenue forfaitairement, enfant du 2° de L. 523-3",
     "ASF counted as a flat-rate, child of L. 523-3 2°"),
    # R262-22: non-salaried professional income retained quarterly.
    ("TauxTnsTrimestriel", DECIMAL, "0.25", "25 %",
     "sources/casf/R262-22.txt", "2021-01-01",
     "revenus non salariés retenus à 25 % de l'annuel",
     "non-salaried income retained at 25 % of the annual figure"),
]


def build_row(name, kind, value, text_form, anchor_txt, start,
              fr_desc, en_desc):
    blob = (PKG / anchor_txt).read_text(encoding="utf-8")
    assert text_form in blob, (
        f"{name}: text form {text_form!r} absent from {anchor_txt}")
    frag = "CASF_" + anchor_txt.split("/")[-1].removesuffix(".txt").replace("-", "_")
    base = frag.removesuffix("_PRE2025").removesuffix("_PRE2024")
    anchor = f"{NS}#{base}"
    row_id = f"{NS}:param:{name}"
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
                "value": {"kind": "value", "type": kind, "value": value},
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
    if args.write:
        for rel, blob in outputs.items():
            p = PKG / rel
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
