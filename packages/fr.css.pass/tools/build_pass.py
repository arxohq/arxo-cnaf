#!/usr/bin/env python3
"""Порождает `01-sources.law` (провенанс §194) и `02-serie.law` (ряд PASS) из закреплённых байтов.

Числа правил выписывает генератор из `sources/pass/` (учёт `manifest.json`, тексты arrêtés;
`tools/pin_pass.py`): arrêté называет «valeur mensuelle» плафона на календарный год.
Правило ряда несёт ЭТО число (`pass_mensuel_arrete`); годовое значение СТРОИТ отдельное
правило как 12 × valeur mensuelle (DECISION-0452: сначала строит), множитель виден в коде,
а не в готовых 38 040 / 48 060. Генератор сверяет год в тексте arrêté, заголовок и сумму.

  python3 corpus/laws/fr/pass/tools/build_pass.py --write
  python3 corpus/laws/fr/pass/tools/build_pass.py --check
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
SOURCES = PKG / "01-sources.law"
SERIE = PKG / "02-serie.law"
HEADER = ('language "law.core" version "0.2";\n'
          'package fr.css.pass version "0.1.0";\n'
          'namespace "urn:fr:corpus:clir:pass";\n')
MONTHS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre",
             "octobre", "novembre", "décembre"]
MONTHS_RU = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября",
             "октября", "ноября", "декабря"]


def rows() -> list[dict]:
    manifest = json.loads((PKG / "sources/pass/manifest.json").read_text(encoding="utf-8"))
    out = []
    for row in manifest["texts"]:
        text = (PKG / row["text"]).read_text(encoding="utf-8")
        year = row["year"]
        assert f"pour {year}" in row["titre"], row["titre"]
        monthly = re.search(r"valeur mensuelle : (\d[\d\s  ]*) euros", text)
        assert monthly, row["name"]
        amount = int(re.sub(r"[\s  ]", "", monthly.group(1)))
        stem = row["arrete"].replace("-", "_")[len("arrete_"):]
        y, m, d = row["date_texte"].split("-")
        row = dict(row, monthly=amount, text_body=text, stem=stem,
                   date_fr=f"{int(d)}{'er' if d == '01' else ''} {MONTHS_FR[int(m) - 1]} {y}",
                   date_ru=f"{int(d)} {MONTHS_RU[int(m) - 1]} {y} года")
        out.append(row)
    return sorted(out, key=lambda r: r["year"])


def gap_years(series: list[dict]) -> list[int]:
    """Годы внутри охвата ряда (от первого до последнего), на которые arrêté не закреплён."""
    have = {r["year"] for r in series}
    return [y for y in range(series[0]["year"], series[-1]["year"] + 1) if y not in have]


def gap_note(series: list[dict]) -> str:
    gaps = gap_years(series)
    first, last = series[0]["year"], series[-1]["year"]
    if not gaps:
        return (f"Ряд непрерывен: {first}–{last}, по одному arrêté на год, без пропусков и внеочередных\n"
                "изменений (README, «Источники»); число из памяти не берётся.")
    return (f"Годы {', '.join(map(str, gaps))} внутри ряда байтами не закреплены (README, «Границы»);\n"
            "год без arrêté не даёт значения, число из памяти не берётся.")


def names(r: dict) -> dict:
    base = f"ARRETE_{r['stem']}_PASS"
    return {"source": base, "edition": f"{base}_ART{r['article']}_ED", "fragment": f"{base}_ART{r['article']}"}


def render_sources(series: list[dict]) -> str:
    lines = [
        "// Провенанс §194: arrêtés «portant fixation du plafond de la sécurité sociale» (PASS, CSS L. 241-3,",
        "// D. 242-17) — по одному на календарный год. Порождено tools/build_pass.py из sources/pass/",
        "// (tools/pin_pass.py; охват — sources/source-manifest.json). Руками не править.",
        "//",
    ] + [f"// {r['year']}: arrêté du {r['date_texte']} ({r['nor']}), {r['parution']}; архив {r['archive']}." for r in series] + [
        "//",
    ] + ["// " + line for line in gap_note(series).splitlines()] + [
        "",
        HEADER,
    ]
    for r in series:
        n = names(r)
        lines += [
            f"source {n['source']} {{",
            "    kind order;",
            "    jurisdiction FR;",
            f'    number "{r["nor"]}";',
            f'    label fr official "{r["titre"]}";',
            f'    label ru unofficial "Приказ от {r["date_ru"]} об определении потолка социального страхования (PASS) на {r["year"]} год";',
            "}",
            "",
            f"edition {n['edition']} of {n['source']} {{",
            "    language fr;",
            "    officiality official;",
            "    materialization_status PINNED_UNOFFICIAL_COPY;",
            f"    in_force [@{r['year']}-01-01, infinity);",
            f'    label fr official "{r["titre"]}, article {r["article"]} (miroir DILA, {r["article_id"]}, {r["parution"]})";',
            f'    label ru unofficial "Приказ от {r["date_texte"]}, статья {r["article"]} (зеркало DILA, {r["article_id"]}, версия закреплённого охвата с 1 января {r["year"]} года)";',
            "}",
            "",
            f"publication {n['edition']}_TEXT of {n['edition']} {{",
            '    media_type "text/plain; charset=utf-8";',
            f'    uri "{r["archive_url"]}";',
            "    retrieved_at @2026-10-08T00:00:00Z;",
            f'    content_hash "sha256:{r["text_sha256"]}";',
            f'    local_path "{r["text"]}";',
            "}",
            "",
            f'@id("urn:fr:corpus:clir:pass#{n["fragment"]}")',
            f"pub fragment {n['fragment']} in {n['edition']} {{",
            "    kind article;",
            f'    locator "article/{r["article"]}";',
            f'    text fr official """{r["text_body"]}""";',
            f'    content_hash "sha256:{r["text_sha256"]}";',
            "}",
            "",
        ]
    return "\n".join(lines).rstrip("\n") + "\n"


def render_serie(series: list[dict]) -> str:
    fragments = [names(r)["fragment"] for r in series]
    used = sorted(set(fragments + ["pass_mensuel_arrete", "pass_annuel_arrete"]))
    lines = [
        "// Ряд PASS (plafond de la sécurité sociale) по календарным годам — из закреплённых arrêtés.",
        "// Порождено tools/build_pass.py из sources/pass/ (tools/pin_pass.py) — руками не править.",
        "//",
        "// Arrêté на год называет valeur mensuelle и valeur journalière (D. 242-17); правило ряда несёт",
        "// valeur mensuelle ЛИТЕРАЛОМ (сама норма arrêté). Годовое значение СТРОИТ правило PassAnnuelArrete:",
        "// 12 × valeur mensuelle (D. 242-17: valeur journalière = valeur mensuelle × 12 / число рабочих дней;",
        "// множитель стоит в правиле, а не в готовой сумме) — DECISION-0452, сначала строит.",
        "//",
        "// КЛЮЧ — календарный год (annee), а не legal_time: потребитель спрашивает PASS «en vigueur au 1er",
        "// janvier» года отсчёта, который не совпадает с датой дела (fr.pf.cf, R. 522-2 al. 3: год N−2). Поэтому",
        "// окно правила [1 января года, ∞): факт «PASS года Y равен X» установлен с первого дня Y и не гаснет.",
        "// Год без закреплённого arrêté (вне ряда или в пропуске) не даёт значения — не устанавливается.",
        "",
        HEADER,
        "use self::{",
    ] + [f"    {n}," for n in used] + ["};", ""]
    for r in series:
        n = names(r)
        y, m = r["year"], r["monthly"]
        lines += [
            f"@source({n['fragment']})",
            f"rule PassMensuelArrete{y}() strict {{",
            f"    effective [@{y}-01-01, infinity);",
            f'    label fr official "plafond de la sécurité sociale {y} : valeur mensuelle {m} euros selon l\'arrêté du {r["date_texte"]} ({r["nor"]}), article {r["article"]}";',
            f'    label ru unofficial "PASS {y}: месячное значение {m} € по приказу от {r["date_texte"]} ({r["nor"]}), ст. {r["article"]}";',
            f"    then pass_mensuel_arrete({y}, {m} EUR);",
            "}",
            "",
        ]
    anchors = ", ".join(fragments)
    lines += [
        f"@source({anchors})",
        "rule PassAnnuelArrete(annee: Integer, mensuel: Money) strict {",
        f"    effective [@{series[0]['year']}-01-01, infinity);",
        '    label fr official "le plafond annuel de la sécurité sociale est douze fois la valeur mensuelle de l\'arrêté (D. 242-17 ; R. 522-2 al. 3 pour fr.pf.cf)";',
        '    label ru unofficial "годовой PASS строится как 12 × месячное значение arrêté (D. 242-17; для fr.pf.cf — R. 522-2 al. 3)";',
        "    when pass_mensuel_arrete(annee, mensuel);",
        "    then pass_annuel_arrete(annee, mensuel * 12.0);",
        "}",
    ]
    return "\n".join(lines).rstrip("\n") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    assert args.write or args.check
    series = rows()
    targets = {SOURCES: render_sources(series), SERIE: render_serie(series)}
    bad = []
    for path, text in targets.items():
        if args.write:
            path.write_text(text, encoding="utf-8")
            print(f"записано {path.name}")
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            bad.append(path.name)
    if bad:
        print("расхождение:", ", ".join(bad))
        return 1
    print("OK: 01-sources.law и 02-serie.law порождены из sources/pass/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
