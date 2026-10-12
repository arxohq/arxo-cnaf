#!/usr/bin/env python3
"""Bareme builder for package fr.pf.core (CNAF wave 1).

Common builder per plan 5.2.5: parameter spec (name, unit,
anchor, rule for extracting the figure from pinned text), windows from versions.

State 2026-10-06 (phase W0-06): DSS instructions DSS/2B/2026/46 (euro
amounts at 2026-04-01) and DSS/2B/2025/177 (resource ceilings for 2026)
are pinned in fr.css.revalorisation as official PDF bytes plus extracted
layout text (sources/dss-2026-46.pdf/.txt, sources/dss-2025-177.pdf/.txt).
This builder transcribes the published figures into rows and
SELF-CHECKS every row that carries a formula:

- kind "pct_bmaf": euros == round_half_up(pct * BMAF_2026, 2);
- kind "plafond": euros == base + r1 * min(n, 2) + r3 * max(n - 2, 0)
  (+ biact_extra for the biactivite/isolement column);
- kind "scaled": euros == round_half_up(base_value * factor, 0);
- kind "fixed": no formula (BMAF history, AEEH 6th complement linked to
  pensions, recovery scale, transcription anchored to the PDF section).

A transcription error fails --check loudly. Anchors point at the pinned
PDF section (file + section reference), never at memory.

In-text constants (55%, 169 h, 10%, 310 jours, 4,500 euros, 150 euros,
2/5 ans, 1 mois, 5 jours ouvrables) stay rule literals, not bareme.

Usage:
  python3 corpus/laws/fr/pf-core/tools/build_bareme.py --check
  python3 corpus/laws/fr/pf-core/tools/build_bareme.py --write
"""

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus" / "laws" / "fr" / "pf-core"

BMAF_2026 = Decimal("478.16")
D46 = "fr.css.revalorisation/sources/dss-2026-46.pdf"
D177 = "fr.css.revalorisation/sources/dss-2025-177.pdf"

# (id, pct of BMAF, published euros, anchor)
PCT_ROWS = [
    ("af.2enf.max", "32", "153.01", D46 + ":annexe-I.1"),
    ("af.2enf.int", "16", "76.51", D46 + ":annexe-I.1"),
    ("af.2enf.min", "8", "38.25", D46 + ":annexe-I.1"),
    ("af.3enf.max", "73", "349.06", D46 + ":annexe-I.1"),
    ("af.3enf.int", "36.5", "174.53", D46 + ":annexe-I.1"),
    ("af.3enf.min", "18.25", "87.26", D46 + ":annexe-I.1"),
    ("af.4enf.max", "114", "545.10", D46 + ":annexe-I.1"),
    ("af.4enf.int", "57", "272.55", D46 + ":annexe-I.1"),
    ("af.4enf.min", "28.5", "136.28", D46 + ":annexe-I.1"),
    ("af.5enf.max", "155", "741.15", D46 + ":annexe-I.1"),
    ("af.5enf.int", "77.5", "370.57", D46 + ":annexe-I.1"),
    ("af.5enf.min", "38.75", "185.29", D46 + ":annexe-I.1"),
    ("af.supp.max", "41", "196.05", D46 + ":annexe-I.1"),
    ("af.supp.int", "20.5", "98.02", D46 + ":annexe-I.1"),
    ("af.supp.min", "10.25", "49.01", D46 + ":annexe-I.1"),
    ("majo.max", "16", "76.51", D46 + ":annexe-I.2"),
    ("majo.int", "8", "38.25", D46 + ":annexe-I.2"),
    ("majo.min", "4", "19.13", D46 + ":annexe-I.2"),
    ("forfait.max", "20.234", "96.75", D46 + ":annexe-I.3"),
    ("forfait.int", "10.117", "48.38", D46 + ":annexe-I.3"),
    ("forfait.min", "5.059", "24.19", D46 + ":annexe-I.3"),
    ("af.dom.1enf", "5.88", "28.12", D46 + ":annexe-I.4"),
    ("af.dom.majo11", "3.69", "17.64", D46 + ":annexe-I.4"),
    ("af.dom.majo16", "5.67", "27.11", D46 + ":annexe-I.4"),
    ("paje.naissance", "229.75", "1098.57", D46 + ":annexe-II.1"),
    ("paje.adoption", "459.50", "2197.15", D46 + ":annexe-II.1"),
    ("paje.base.plein", "41.65", "199.15", D46 + ":annexe-II.1"),
    ("paje.base.partiel", "20.825", "99.58", D46 + ":annexe-II.1"),
    ("cf.montant", "41.65", "199.15", D46 + ":annexe-III.1"),
    ("cf.majore", "62.48", "298.75", D46 + ":annexe-III.1"),
    ("asf.plein", "56.25", "268.97", D46 + ":annexe-III.2"),
    ("asf.partiel", "42.20", "201.78", D46 + ":annexe-III.2"),
    ("ars.6-10", "89.72", "429.01", D46 + ":annexe-III.3"),
    ("ars.11-14", "94.67", "452.67", D46 + ":annexe-III.3"),
    ("ars.15-18", "97.95", "468.36", D46 + ":annexe-III.3"),
    ("aeeh.base", "32.00", "153.01", D46 + ":annexe-III.4"),
    ("aeeh.c1", "24.00", "114.76", D46 + ":annexe-III.4"),
    ("aeeh.c2", "65.00", "310.80", D46 + ":annexe-III.4"),
    ("aeeh.c3", "92.00", "439.91", D46 + ":annexe-III.4"),
    ("aeeh.c4", "142.57", "681.71", D46 + ":annexe-III.4"),
    ("aeeh.c5", "182.21", "871.26", D46 + ":annexe-III.4"),
    ("prepare.plein", "96.62", "462.00", D46 + ":annexe-II.2"),
    ("prepare.partiel-moins50", "62.46", "298.66", D46 + ":annexe-II.2"),
    ("prepare.partiel-50-80", "36.03", "172.28", D46 + ":annexe-II.2"),
    ("prepare.majoree", "157.93", "755.16", D46 + ":annexe-II.3"),
    ("cmg.assmat.maximal", "172.57", "825.16", D46 + ":annexe-II.4.1"),
    ("cmg.assmat.intermediaire", "143.81", "687.64", D46 + ":annexe-II.4.1"),
    ("cmg.assmat.minimal", "115.05", "550.12", D46 + ":annexe-II.4.1"),
    ("cmg.garde.maximal", "208.53", "997.11", D46 + ":annexe-II.4.2"),
    ("cmg.garde.intermediaire", "179.76", "859.54", D46 + ":annexe-II.4.2"),
    ("cmg.garde.minimal", "151.00", "722.02", D46 + ":annexe-II.4.2"),
]

# (id, base, r1 (per child 1-2), r3 (per child from 3rd, default r1),
#  n (children), biact_extra or None, published euros, published
#  biact euros or None, anchor)
PLAFOND_ROWS = [
    ("plafond.af.t1", "66652", "6664", "6664", 2, None, "79980", None,
     D177 + ":section-1"),
    ("plafond.af.t1", "66652", "6664", "6664", 3, None, "86644", None,
     D177 + ":section-1"),
    ("plafond.af.t1", "66652", "6664", "6664", 4, None, "93308", None,
     D177 + ":section-1"),
    ("plafond.af.t1", "66652", "6664", "6664", 5, None, "99972", None,
     D177 + ":section-1"),
    ("plafond.af.t2", "93276", "6664", "6664", 2, None, "106604", None,
     D177 + ":section-1"),
    ("plafond.af.t2", "93276", "6664", "6664", 3, None, "113268", None,
     D177 + ":section-1"),
    ("plafond.cf", "24853", "6213", "7456", 1, "9989", "31066", "41055",
     D177 + ":section-2.1"),
    ("plafond.cf", "24853", "6213", "7456", 2, "9989", "37279", "47268",
     D177 + ":section-2.1"),
    ("plafond.cf", "24853", "6213", "7456", 3, "9989", "44735", "54724",
     D177 + ":section-2.1"),
    ("plafond.cf", "24853", "6213", "7456", 4, "9989", "52191", "62180",
     D177 + ":section-2.1"),
    ("plafond.cf.majore", "12429", "3107", "3729", 1, "4995", "15536",
     "20531", D177 + ":section-2.2"),
    ("plafond.cf.majore", "12429", "3107", "3729", 2, "4995", "18643",
     "23638", D177 + ":section-2.2"),
    ("plafond.cf.majore", "12429", "3107", "3729", 3, "4995", "22372",
     "27367", D177 + ":section-2.2"),
    ("plafond.cf.majore", "12429", "3107", "3729", 4, "4995", "26101",
     "31096", D177 + ":section-2.2"),
    ("plafond.paje", "29694", "7424", "8908", 1, "11936", "37118", "49054",
     D177 + ":section-3.1"),
    ("plafond.paje", "29694", "7424", "8908", 2, "11936", "44542", "56478",
     D177 + ":section-3.1"),
    ("plafond.paje", "29694", "7424", "8908", 3, "11936", "53450", "65386",
     D177 + ":section-3.1"),
    ("plafond.paje", "29694", "7424", "8908", 4, "11936", "62358", "74294",
     D177 + ":section-3.1"),
    ("plafond.cmg.t1", "20880", "3453", "3453", 1, None, "24333", None,
     D177 + ":section-3.3.1"),
    ("plafond.cmg.t1", "20880", "3453", "3453", 2, None, "27786", None,
     D177 + ":section-3.3.1"),
    ("plafond.cmg.t2", "46399", "7676", "7676", 1, None, "54075", None,
     D177 + ":section-3.3.1"),
    ("plafond.cmg.t2", "46399", "7676", "7676", 2, None, "61751", None,
     D177 + ":section-3.3.1"),
    ("plafond.cmg.iso.t1", "29232", "4834", "4834", 1, None, "34066", None,
     D177 + ":section-3.3.2"),
    ("plafond.cmg.iso.t1", "29232", "4834", "4834", 2, None, "38900", None,
     D177 + ":section-3.3.2"),
    ("plafond.cmg.iso.t2", "64959", "10746", "10746", 1, None, "75705",
     None, D177 + ":section-3.3.2"),
    ("plafond.cmg.iso.t2", "64959", "10746", "10746", 2, None, "86451",
     None, D177 + ":section-3.3.2"),
    ("plafond.ars", "22274", "6682", "6682", 1, None, "28956", None,
     D177 + ":section-4"),
    ("plafond.ars", "22274", "6682", "6682", 2, None, "35638", None,
     D177 + ":section-4"),
    ("plafond.ars", "22274", "6682", "6682", 3, None, "42320", None,
     D177 + ":section-4"),
    ("plafond.ars", "22274", "6682", "6682", 4, None, "49002", None,
     D177 + ":section-4"),
    ("plafond.deces", "93276", "6664", "6664", 1, None, "99940", None,
     D177 + ":section-5"),
    ("plafond.deces", "93276", "6664", "6664", 2, None, "106604", None,
     D177 + ":section-5"),
    ("plafond.mayotte", "32394", "3240", "3240", 1, None, "35634", None,
     D177 + ":section-Mayotte-1.1"),
    ("plafond.mayotte", "32394", "3240", "3240", 2, None, "38874", None,
     D177 + ":section-Mayotte-1.1"),
]

# (id, value, unit, anchor) - no formula, transcription anchored to source.
FIXED_ROWS = [
    ("bmaf.2025-04-01", "474.37", "EUR/month",
     D46 + ":page-2 (base depuis le 1er avril 2025)"),
    ("bmaf.2026-04-01", "478.16", "EUR/month",
     D46 + ":page-2 + annexe-table-BMAF"),
    ("coeff.2026", "1.008", "ratio",
     D46 + ":page-2 (taux de revalorisation de la BMAF de 0,8 %)"),
    ("aeeh.c6", "1298.44", "EUR/month",
     D46 + ":page-2 (sixieme complement, L. 341-4/L. 341-6 pensions)"),
    ("recouvrement.tranche.306-458", "25", "percent",
     D177 + ":section-6a"),
    ("recouvrement.tranche.459-684", "35", "percent",
     D177 + ":section-6a"),
    ("recouvrement.tranche.685-914", "45", "percent",
     D177 + ":section-6a"),
    ("recouvrement.tranche.sup-915", "60", "percent",
     D177 + ":section-6a"),
    ("recouvrement.retenue-moins-306", "57", "EUR",
     D177 + ":section-6b"),
    ("recouvrement.revenu-presume", "1369", "EUR/month",
     D177 + ":section-6c"),
]


def q2(x: Decimal) -> Decimal:
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def build():
    rows = []
    for rid, pct, euros, anchor in PCT_ROWS:
        calc = q2(Decimal(pct) / Decimal(100) * BMAF_2026)
        assert calc == Decimal(euros), f"{rid}: {pct}% x BMAF = {calc}, want {euros}"
        rows.append({"id": rid, "kind": "pct_bmaf", "pct": pct,
                     "euros": euros, "anchor": anchor})
    for (rid, base, r1, r3, n, biact, euros, euros_b, anchor) in PLAFOND_ROWS:
        b, a, c = Decimal(base), Decimal(r1), Decimal(r3)
        calc = b + a * min(n, 2) + c * max(n - 2, 0)
        assert calc == Decimal(euros), f"{rid} n={n}: {calc}, want {euros}"
        row = {"id": rid, "kind": "plafond", "base": base, "per_child_1_2": r1,
               "per_child_from_3": r3, "children": n, "euros": euros,
               "anchor": anchor}
        if biact is not None:
            calc_b = calc + Decimal(biact)
            assert calc_b == Decimal(euros_b), f"{rid} n={n} biact: {calc_b}"
            row["biact_extra"] = biact
            row["euros_biact"] = euros_b
        rows.append(row)
    for rid, value, unit, anchor in FIXED_ROWS:
        rows.append({"id": rid, "kind": "fixed", "value": value,
                     "unit": unit, "anchor": anchor})
    return {
        "boundary": None,
        "sources": [
            "DSS/2B/2026/46 (amounts at 2026-04-01, BMAF 478.16)",
            "DSS/2B/2025/177 (ceilings for 2026)",
        ],
        "bmaf_2026": "478.16",
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    assert args.check or args.write, "give --check or --write"
    result = build()
    out = PKG / "bareme.json"
    if args.write:
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"WROTE {out} ({len(result['rows'])} rows, boundary removed)")
    else:
        if not out.exists():
            print(f"MISSING {out} (run --write once)")
            return 1
        disk = json.loads(out.read_text(encoding="utf-8"))
        if disk != result:
            print("DRIFT bareme.json")
            return 1
    print(f"BAREME OK: {len(result['rows'])} rows, boundary removed, "
          f"all formulas verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
