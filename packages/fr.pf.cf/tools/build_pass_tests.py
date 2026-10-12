#!/usr/bin/env python3
"""Сценарии порога двойной активности R. 522-2 al. 3 по годам отсчёта 2017–2025 (D-85).

Ряд PASS закреплён пакетом fr.css.pass непрерывно за 2015–2026 годы (D-84, граница B-PASS-2017
снята): PASS года отсчёта N−2 пакет pf-cf берёт у него (мост `PassReferenceArrete`,
07-pass.law). Для каждого года Y ряда сценарий проверяет порог 13,6 % × PASS(Y):

* доход, достигающий порога («au moins égal», наименьшая сумма в сантимах не ниже порога), —
  `couple_biactif` установлена;
* доход на сантим меньше — не установлена (NEITHER).

PASS (valeur mensuelle × 12) читается из ТЕКСТА закреплённого arrêté (`pass/sources/pass/*.txt`,
учёт `manifest.json`), а не вводится руками: сценарий падает, если число в правилах ряда
разойдётся с байтами. Годы 2015, 2016 и 2026 покрыты написанными вручную `pass-2015-seuil-egal`,
`pass-2016-biactif`, `pass-2016-sous-seuil`, `pass-2026-seuil-egal`. Дата дела — июнь года права
(год отсчёта + 2, ресурсы N−2 по R. 532-1).

  python3 corpus/laws/fr/pf-cf/tools/build_pass_tests.py --write
  python3 corpus/laws/fr/pf-cf/tools/build_pass_tests.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import ROUND_CEILING, Decimal
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
PASS_PKG = PKG.parent / "pass"
YEARS = range(2017, 2026)
RATE = Decimal("0.136")          # R. 522-2 al. 3: TauxBiactifRevenu (bareme/TauxBiactifRevenu.lawparam.json)
CENT = Decimal("0.01")

HEADER = ('language "law.core" version "0.2";\npackage fr.pf.cf version "0.1.0";\n'
          'namespace "urn:fr:corpus:clir:pf-cf";\n')
TRUE = ("    expect result_kind == PROPOSITION;\n    expect truth_status == TRUE_ONLY;\n"
        "    expect evaluation_status == COMPUTED;\n")
NEITHER = ("    expect result_kind == PROPOSITION;\n    expect truth_status == NEITHER;\n"
           "    expect evaluation_status == COMPUTED;\n")


def series() -> dict[int, dict]:
    manifest = json.loads((PASS_PKG / "sources/pass/manifest.json").read_text(encoding="utf-8"))
    out = {}
    for row in manifest["texts"]:
        text = (PASS_PKG / row["text"]).read_text(encoding="utf-8")
        monthly = int(re.sub(r"[\s  ]", "", re.search(r"valeur mensuelle : (\d[\d\s  ]*) euros", text).group(1)))
        out[row["year"]] = {"monthly": monthly, "annual": monthly * 12, "nor": row["nor"],
                            "date": row["date_texte"], "name": row["name"]}
    return out


def money(value: Decimal) -> str:
    return f"{value.quantize(CENT)} EUR"


def render(year: int, row: dict, rate: Decimal) -> str:
    annual = Decimal(row["annual"])
    threshold = annual * rate
    reached = threshold.quantize(CENT, rounding=ROUND_CEILING)      # наименьшая сумма в сантимах не ниже порога
    below = reached - CENT
    assert below < threshold <= reached
    pre = f"p{year % 100:02d}"
    day = f"{year + 2}-06-15"
    context = (f'context {{ decision_time @{day}T12:00:00Z; knowledge_time @{day}T12:00:00Z; legal_time @{day}; '
               'timezone "Europe/Paris"; }')
    exact = " (порог попадает на сантим)" if threshold == reached else ""
    head = (f"// D-85: PASS года отсчёта {year} строится из закреплённого arrêté du {row['date']} ({row['nor']}; "
            f"fr.css.pass: sources/pass/{row['name']}.txt):\n"
            f"// valeur mensuelle {row['monthly']} € x 12 = {row['annual']} €. Порог R. 522-2 al. 3: 13,6 % x {row['annual']} = "
            f"{threshold.normalize():f}{exact}.\n"
            f"// Доход {reached} достигает порога -> couple_biactif; на сантим меньше ({below}) — нет (NEITHER). "
            f"Дата дела — июнь {year + 2} (ресурсы N-2 по R. 532-1).\n"
            "// Порождено tools/build_pass_tests.py из закреплённых байтов fr.css.pass — руками не править.\n")
    blocks = []
    for tag, mark, amount, expect in (("seuil", "a", reached, TRUE), ("sous-seuil", "b", below, NEITHER)):
        entity = f'entity_ref("urn:fr:pf-cf:case:pass-{year}-{tag}")'
        blocks.append(
            f'test "urn:query:fr-pf-cf-pass-{year}-{tag}" {{\n'
            f"    given {{\n        {context}\n"
            f'        assert "{pre}{mark}-01": revenu_pro_min_couple({entity}, {money(amount)}) {{ origin case_input; }}\n'
            f'        assert "{pre}{mark}-02": annee_reference_ressources({entity}, {year}) {{ origin case_input; }}\n'
            "    }\n"
            f"    evaluate truth(pass_reference({entity}, {row['annual']} EUR));\n{TRUE}"
            f"    evaluate truth(couple_biactif({entity}));\n{expect}"
            "}\n")
    return head + HEADER + "\n" + "\n".join(blocks)


def rate_from_package() -> Decimal:
    data = json.loads((PKG / "bareme/TauxBiactifRevenu.lawparam.json").read_text(encoding="utf-8"))
    (entry,) = data["values"]
    value = entry["value"]["value"]
    if "/" in str(value):
        numerator, denominator = str(value).split("/")
        return Decimal(numerator) / Decimal(denominator)
    return Decimal(str(value))


def targets() -> dict[Path, str]:
    rows, rate = series(), rate_from_package()
    assert rate == RATE, rate
    return {PKG / "tests" / f"pass-{year}-seuil.lawtest": render(year, rows[year], rate) for year in YEARS}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    files = targets()
    if args.check:
        bad = [p.name for p, text in files.items() if not p.exists() or p.read_text(encoding="utf-8") != text]
        if bad:
            print("расходятся с закреплёнными байтами fr.css.pass:\n" + "\n".join(bad))
            return 1
        print(f"pf-cf: {len(files)} сценариев порога PASS — чисто")
        return 0
    for path, text in files.items():
        path.write_text(text, encoding="utf-8")
    print(f"pf-cf: записано {len(files)} сценариев порога PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
