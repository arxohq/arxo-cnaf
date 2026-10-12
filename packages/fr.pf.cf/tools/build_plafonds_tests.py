#!/usr/bin/env python3
"""Сценарии «плафон равен напечатанной строке таблицы DSS» (D-83), по одному на год 2018–2026.

Входы — опубликованные база и надбавки года (`sources/dss-plafonds/manifest.json`, срезы
инструкций DSS), ожидания — НАПЕЧАТАННЫЕ строки таблиц тех же инструкций (3 и 4 ребёнка,
плафон и плафон «biactivité ou isolement»; плафон CF и montant majoré). Плафон строит
пакет (03-plafond.law), а не сценарий: совпадение с напечатанной строкой — проверка
построения. Годы 2015–2017 вне окна правил пакета (`effective` с 2018-01-01) и сценариями не
покрываются; их таблицы сверяет `pin_plafonds_dss.py` арифметически.

  python3 corpus/laws/fr/pf-cf/tools/build_plafonds_tests.py --write
  python3 corpus/laws/fr/pf-cf/tools/build_plafonds_tests.py --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
YEARS = range(2018, 2027)


def entity(year: int, tag: str) -> str:
    return f'entity_ref("urn:fr:pf-cf:case:plafond-dss-{year}-{tag}")'


def render(year: int, cf: dict, majore: dict, src: str) -> str:
    pre = f"pd{year % 100:02d}"
    lines = []
    n = [0]

    def add(rel: str, ent: str, value: str) -> None:
        n[0] += 1
        lines.append(f'        assert "{pre}-{n[0]:02d}": {rel}({ent}, {value}) {{ origin case_input; }}')

    cases = [("a", 3, False), ("b", 4, True)]
    for tag, count, isolated in cases:
        ent = entity(year, tag)
        add("plafond_base_cf", ent, f"{cf['base']} EUR")
        add("majoration_enfant_cf", ent, f"{cf['majoration_enfant']} EUR")
        add("majoration_troisieme_cf", ent, f"{cf['majoration_troisieme']} EUR")
        add("majoration_biactivite", ent, f"{cf['majoration_biactivite']} EUR")
        add("plafond_base_majore", ent, f"{majore['base']} EUR")
        add("majoration_enfant_majore", ent, f"{majore['majoration_enfant']} EUR")
        add("majoration_troisieme_majore", ent, f"{majore['majoration_troisieme']} EUR")
        add("majoration_biactivite_majore", ent, f"{majore['majoration_biactivite']} EUR")
        add("nb_enfants_cf", ent, str(count))
        n[0] += 1
        lines.append(f'        assert "{pre}-{n[0]:02d}": foyer_du_cas({ent}) {{ origin case_input; }}')
        if isolated:
            n[0] += 1
            lines.append(f'        assert "{pre}-{n[0]:02d}": parent_isole({ent}) {{ origin case_input; }}')
    a, b = entity(year, "a"), entity(year, "b")
    plain_cf = cf["rows"]["3"][0]
    iso_cf = cf["rows"]["4"][1]
    plain_m = majore["rows"]["3"][0]
    iso_m = majore["rows"]["4"][1]
    evals = [(f"plafond_cf_applicable({a}, {plain_cf} EUR)"), (f"plafond_majore_applicable({a}, {plain_m} EUR)"),
             (f"plafond_cf_applicable({b}, {iso_cf} EUR)"), (f"plafond_majore_applicable({b}, {iso_m} EUR)")]
    body = "\n".join(
        f"    evaluate truth({e});\n    expect result_kind == PROPOSITION;\n    expect truth_status == TRUE_ONLY;\n"
        f"    expect evaluation_status == COMPUTED;" for e in evals)
    head = (
        f"// D-83: плафоны {year} года из ОПУБЛИКОВАННЫХ сумм инструкции {src} (срезы sources/dss-plafonds/): плафон CF и montant majoré.\n"
        f"// Ожидания — напечатанные строки таблиц той же инструкции: 3 ребёнка без надбавки "
        f"(CF {plain_cf}, montant majoré {plain_m}) и 4 ребёнка для parent isolé "
        f"(CF {iso_cf}, montant majoré {iso_m}); плафон строит пакет, не сценарий.\n"
        "// Файл порождается tools/build_plafonds_tests.py — руками не править.\n"
        'language "law.core" version "0.2";\n'
        'package fr.pf.cf version "0.1.0";\n'
        'namespace "urn:fr:corpus:clir:pf-cf";\n\n'
        f'test "urn:query:fr-pf-cf-plafond-dss-{year}" {{\n'
        "    given {\n"
        f'        context {{ decision_time @{year}-06-15T12:00:00Z; knowledge_time @{year}-06-15T12:00:00Z; '
        f'legal_time @{year}-06-15; timezone "Europe/Paris"; }}')
    return head + "\n" + "\n".join(lines) + "\n    }\n" + body + "\n}\n"


def build() -> dict[str, str]:
    manifest = json.loads((PKG / "sources/dss-plafonds/manifest.json").read_text(encoding="utf-8"))
    by_year: dict[int, dict] = {}
    for row in manifest["texts"]:
        if row["kind"] in ("cf", "majore"):
            by_year.setdefault(row["year"], {})[row["kind"]] = row
    out = {}
    for year in YEARS:
        rows = by_year[year]
        out[f"tests/plafond-dss-{year}.lawtest"] = render(year, rows["cf"], rows["majore"], rows["cf"]["instruction"].upper().replace("-", "/", 1).replace("-", "/"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    assert args.write or args.check
    files = build()
    if args.write:
        for rel, text in files.items():
            (PKG / rel).write_text(text, encoding="utf-8")
        print(f"записано {len(files)} сценариев")
    bad = [rel for rel, text in files.items() if not (PKG / rel).exists() or (PKG / rel).read_text(encoding="utf-8") != text]
    if bad:
        print("расхождения:", ", ".join(bad))
        return 1
    print(f"OK: {len(files)} сценариев порождены из учёта")
    return 0


if __name__ == "__main__":
    sys.exit(main())
