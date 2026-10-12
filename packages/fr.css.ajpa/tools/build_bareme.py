#!/usr/bin/env python3
"""Pin the AJPA bareme (law.params/0.1 datasets from pinned L168 fragments).

Only values whose French text form stands in a pinned fragment are emitted
("figure must stand in the anchor text"). D168/R168 decree figures (daily
SMIC euro amount, monthly max days, duration ceiling, flat-day counts) are
NOT pinned (inventory PENDING_WAVE): they arrive as case inputs with
provenance. No OpenFisca AJPA model or parameters exist upstream: DSS/CNAF
texts and blind reading are the basis (REPORT).

Usage:
  python3 corpus/laws/fr/ajpa/tools/build_bareme.py --check
  python3 corpus/laws/fr/ajpa/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "ajpa"

NS = "urn:fr:corpus:clir:css-ajpa"

INTEGER = {"name": "urn:law:std#Integer"}

# (name, kind, rows, fr_desc, en_desc); rows = list of
# (start, end, value, text_form, anchor_frag, anchor_txt).
SPECS = [
    # L168-9 2021-2025: career maximum, "soixante-six" daily allowances.
    # FINISH-W3 closes B-AJPA-CARRIERE-2021-2023: the figure stands verbatim
    # in the pinned 2019, 2022 and 2023-07 wordings, one row per wording.
    # Descriptions stay byte-identical so the 2023-07-21 row keeps its id
    # and labels; the two new rows need kk overlay keys (reviewer call).
    ("NombreMaxCarriere66", INTEGER,
     [("2021-01-01", "2022-01-01", 66, "soixante-six",
       "CSS_L168_9_PRE2022_ED2021_01", "sources/css/L168-9-2019-12-28.txt"),
      ("2022-01-01", "2023-07-21", 66, "soixante-six",
       "CSS_L168_9_PRE2023", "sources/css/L168-9-2022-01-01.txt"),
      ("2023-07-21", "2025-01-01", 66, "soixante-six",
       "CSS_L168_9_PRE2025", "sources/css/L168-9-2023-07-21.txt")],
     "nombre maximal d'allocations journalières pour l'ensemble de la carrière (L. 168-9 2023)",
     "maximum daily allowances over the whole career (L. 168-9 2023)"),
    # L168-13: recovery by instalments within twelve months at most.
    ("DelaiRecouvrementMaxMois", INTEGER,
     [("2021-01-01", None, 12, "douze mois", "CSS_L168_13",
       "sources/css/L168-13.txt")],
     "remboursement en plusieurs versements dans un délai de douze mois au plus (L. 168-13)",
     "repayment in instalments within twelve months at most (L. 168-13)"),
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
