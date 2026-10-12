#!/usr/bin/env python3
"""Сценарии ряда SMIC 2021–2025 из закреплённых байтов (без ручных чисел).

Для каждого месяца 2021-01…2025-12 (legal_time — первое число месяца) ожидаемые
значения берутся из ТЕКСТА закреплённых актов `sources/fr-smic/*.txt`:
действует последний акт, чей «à compter du …» не позже месяца; суммы —
«porté à / fixé à … l'heure» (1°, 2°) и «minimum garanti … fixé à …».
Плюс граничные сценарии «последний день перед сменой» (8 переходов).
Правила пакета этим файлом не проверяются «сами собой»: расхождение числа
в правиле и в байтах роняет сценарий.

  gen_serie_tests.py          — записать tests/smic-serie-*.lawtest
  gen_serie_tests.py --check  — файлы не совпадают с байтами = ошибка
"""
from __future__ import annotations

import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = ROOT / "corpus/laws/fr/smic"
SRC = PACKAGE / "sources/fr-smic"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

MONTHS = {"janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6, "juillet": 7,
          "août": 8, "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12}
HEADER = ('language "law.core" version "0.2";\npackage fr.travail.smic version "0.1.0";\n'
          'namespace "urn:fr:corpus:clir:smic";\n\n')


def money(text: str) -> str:
    return text.replace(",", ".")


def acts() -> list[dict]:
    """Акты из документов манифеста: дата вступления и суммы из текста статей."""
    found = []
    for key, (name, _unit, _heading) in _load_manifest(PACKAGE)["documents"].items():
        text = (SRC / name).read_text(encoding="utf-8")
        start = re.search(r"A compter du 1er (\w+) (\d{4}), pour les catégories", text)
        if not start:
            start = re.search(r"à compter du 1er (\w+) (\d{4}), pour les catégories", text)
        metro = re.search(r"son montant est porté à ([\d,]+) (?:€|euros) l'heure", text)
        mayotte = re.search(r"A Mayotte, son montant est fixé à ([\d,]+) (?:€|euros) l'heure", text)
        mg = re.search(r"minimum garanti prévu à l'article L\. 3231-12 du code du travail est fixé à ([\d,]+) (?:€|euros)", text)
        if not (start and metro and mayotte and mg):
            raise SystemExit(f"{name}: не найдены дата или суммы")
        found.append({"doc": name, "start": date(int(start.group(2)), MONTHS[start.group(1)], 1),
                      "metro": money(metro.group(1)), "mayotte": money(mayotte.group(1)),
                      "mg": money(mg.group(1))})
    return sorted(found, key=lambda a: a["start"])


def active(all_acts: list[dict], day: date) -> dict:
    return [a for a in all_acts if a["start"] <= day][-1]


def block(slug: str, day: date, act: dict, note: str) -> str:
    m, y = f"urn:fr:smic:case:{slug}:metropole", f"urn:fr:smic:case:{slug}:mayotte"
    return f'''// {note}: {act["doc"]} (с {act["start"].isoformat()}).
test "urn:query:fr-smic-{slug}" {{
    given {{
        context {{ decision_time @{day}T12:00:00Z; knowledge_time @{day}T12:00:00Z; legal_time @{day}; timezone "Europe/Paris"; }}
        assert "{slug}-01": territoire_smic(entity_ref("{m}"), METROPOLE_ET_DOM) {{ origin case_input; }}
        assert "{slug}-02": territoire_smic(entity_ref("{y}"), MAYOTTE) {{ origin case_input; }}
    }}
    evaluate truth(smic_horaire(entity_ref("{m}"), {act["metro"]} EUR));
    expect result_kind == PROPOSITION;
    expect truth_status == TRUE_ONLY;
    expect evaluation_status == COMPUTED;
    evaluate truth(smic_horaire(entity_ref("{y}"), {act["mayotte"]} EUR));
    expect result_kind == PROPOSITION;
    expect truth_status == TRUE_ONLY;
    expect evaluation_status == COMPUTED;
    evaluate truth(minimum_garanti(entity_ref("{m}"), {act["mg"]} EUR));
    expect result_kind == PROPOSITION;
    expect truth_status == TRUE_ONLY;
    expect evaluation_status == COMPUTED;
}}
'''


def build() -> dict[str, str]:
    all_acts = acts()
    series = ["// Ряд SMIC 2021–2025, первое число каждого месяца: метрополия+, Майотта,\n"
              "// minimum garanti. Ожидания читаются из закреплённых текстов актов\n"
              "// (tools/gen_serie_tests.py), не набраны руками.\n", HEADER]
    for year in range(2021, 2026):
        for month in range(1, 13):
            day = date(year, month, 1)
            series.append(block(f"serie-{year}-{month:02d}", day, active(all_acts, day), f"{year}-{month:02d}-01"))
    edges = ["// Границы ряда 2021–2025: последний день ПЕРЕД сменой ставки — ещё прежняя\n"
             "// ставка (окна полуоткрытые [с, до)). Ожидания — из закреплённых текстов.\n", HEADER]
    for act in all_acts:
        if date(2021, 1, 1) < act["start"] <= date(2026, 1, 1):
            eve = act["start"] - timedelta(days=1)
            edges.append(block(f"veille-{act['start'].isoformat()}", eve, active(all_acts, eve), f"{eve} (накануне {act['start']})"))
    return {"tests/smic-serie-mensuelle-2021-2025.lawtest": "\n".join(series),
            "tests/smic-serie-veilles-2021-2025.lawtest": "\n".join(edges)}


def main(argv: list[str]) -> int:
    files = build()
    if "--check" in argv:
        bad = [name for name, text in files.items()
               if not (PACKAGE / name).exists() or (PACKAGE / name).read_text(encoding="utf-8") != text]
        print("расходятся с байтами: " + ", ".join(bad) if bad else f"smic: {len(files)} файла серии — чисто")
        return 1 if bad else 0
    for name, text in files.items():
        (PACKAGE / name).write_text(text, encoding="utf-8")
        print(f"{name}: {text.count(chr(10) + 'test ') + text.startswith('test ')} сценариев")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
