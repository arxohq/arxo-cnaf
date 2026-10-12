#!/usr/bin/env python3
"""Сценарии ряда PASS из закреплённых байтов (без ручных чисел).

Для каждого закреплённого года ожидаемые valeur mensuelle и годовое значение берутся из ТЕКСТА
arrêté (`sources/pass/*.txt`, учёт `sources/pass/manifest.json`): годовое = 12 × mensuelle.
Правила пакета этим файлом не проверяются «сами собой»: расхождение числа в правиле и в байтах
роняет сценарий. Плюс отрицательные сценарии: сумма, не равная построенной, и год без arrêté.

  gen_serie_tests.py          — записать tests/pass-*.lawtest
  gen_serie_tests.py --check  — файлы не совпадают с байтами = ошибка
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
TESTS = PKG / "tests"
HEADER = ('language "law.core" version "0.2";\npackage fr.css.pass version "0.1.0";\n'
          'namespace "urn:fr:corpus:clir:pass";\n\n')
CONTEXT = ('context {{ decision_time @{d}T12:00:00Z; knowledge_time @{d}T12:00:00Z; legal_time @{d}; '
           'timezone "Europe/Paris"; }}')
TRUE = ("    expect result_kind == PROPOSITION;\n    expect truth_status == TRUE_ONLY;\n"
        "    expect evaluation_status == COMPUTED;\n")
NEITHER = ("    expect result_kind == PROPOSITION;\n    expect truth_status == NEITHER;\n"
           "    expect evaluation_status == COMPUTED;\n")



def series() -> list[dict]:
    manifest = json.loads((PKG / "sources/pass/manifest.json").read_text(encoding="utf-8"))
    out = []
    for row in manifest["texts"]:
        text = (PKG / row["text"]).read_text(encoding="utf-8")
        found = re.search(r"valeur mensuelle : (\d[\d\s  ]*) euros", text)
        monthly = int(re.sub(r"[\s  ]", "", found.group(1)))
        out.append({"year": row["year"], "monthly": monthly, "annual": monthly * 12, "arrete": row["arrete"],
                    "nor": row["nor"], "date": row["date_texte"], "name": row["name"]})
    return sorted(out, key=lambda r: r["year"])


def serie_test(r: dict) -> str:
    y = r["year"]
    day = f"{max(y, 2018)}-06-15"
    return (f"// PASS {y}: valeur mensuelle {r['monthly']} € (arrêté du {r['date']}, {r['nor']}; sources/pass/{r['name']}.txt);\n"
            f"// годовое значение строится 12 × {r['monthly']} = {r['annual']} €. Дата дела ни при чём: ключ — год.\n"
            + HEADER +
            f'test "urn:query:fr-pass-serie-{y}" {{\n'
            f"    given {{\n        {CONTEXT.format(d=day)}\n    }}\n"
            f"    evaluate truth(pass_mensuel_arrete({y}, {r['monthly']} EUR));\n{TRUE}"
            f"    evaluate truth(pass_annuel_arrete({y}, {r['annual']} EUR));\n{TRUE}"
            "}\n")


def ecart_test(series_: list[dict]) -> str:
    blocks = []
    for r in series_:
        y = r["year"]
        blocks.append(
            f"// {y}: построение — не подстановка. Годовое значение {r['annual'] + 1} (на евро больше 12 × {r['monthly']}) и\n"
            f"// месячное {r['monthly'] + 1} (на евро больше текста arrêté) не устанавливаются.\n"
            f'test "urn:query:fr-pass-ecart-{y}" {{\n'
            f"    given {{\n        {CONTEXT.format(d='2018-06-15')}\n    }}\n"
            f"    evaluate truth(pass_annuel_arrete({y}, {r['annual'] + 1} EUR));\n{NEITHER}"
            f"    evaluate truth(pass_mensuel_arrete({y}, {r['monthly'] + 1} EUR));\n{NEITHER}"
            "}\n")
    return ("// Построение годового PASS не принимает суммы, расходящиеся с текстом arrêté ровно на евро.\n"
            + HEADER + "\n".join(blocks))


def unpinned_probes(series_: list[dict]) -> list[int]:
    """Годы без закреплённого arrêté: год до ряда, год после ряда и пропуски внутри него."""
    pinned = {r["year"] for r in series_}
    first, last = min(pinned), max(pinned)
    return [first - 1] + [y for y in range(first, last + 1) if y not in pinned] + [last + 1]


def gap_test(series_: list[dict]) -> str:
    blocks = []
    for y in unpinned_probes(series_):
        blocks.append(
            f"// {y}: arrêté не закреплён (год вне закреплённого ряда или пропуск в нём): ни месячное, ни годовое\n"
            f"// значение не устанавливается; предъявленное число (здесь 1 € и 12 €, не претензия на величину) не подтверждено.\n"
            f'test "urn:query:fr-pass-annee-non-epinglee-{y}" {{\n'
            f"    given {{\n        {CONTEXT.format(d='2018-06-15')}\n    }}\n"
            f"    evaluate truth(pass_mensuel_arrete({y}, 1 EUR));\n{NEITHER}"
            f"    evaluate truth(pass_annuel_arrete({y}, 12 EUR));\n{NEITHER}"
            "}\n")
    return ("// Год без закреплённого arrêté (до ряда, после него или пропуск внутри) не получает значения.\n"
            + HEADER + "\n".join(blocks))


def targets() -> dict[Path, str]:
    s = series()
    files = {TESTS / f"pass-serie-{r['year']}.lawtest": serie_test(r) for r in s}
    files[TESTS / "pass-ecart-construit.lawtest"] = ecart_test(s)
    files[TESTS / "pass-annee-non-epinglee.lawtest"] = gap_test(s)
    return files


def main(argv: list[str]) -> int:
    check = "--check" in argv
    files = targets()
    bad = []
    for path, text in files.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                bad.append(path.name)
        else:
            path.write_text(text, encoding="utf-8")
    if check:
        if bad:
            print("расходятся с закреплёнными байтами:\n" + "\n".join(bad))
            return 1
        print(f"pass: {len(files)} файлов сценариев — чисто")
        return 0
    print(f"pass: записано {len(files)} файлов сценариев")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
