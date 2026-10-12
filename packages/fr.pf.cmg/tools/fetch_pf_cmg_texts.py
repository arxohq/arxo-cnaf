#!/usr/bin/env python3
"""CMG (free choice of childcare supplement) -> bytes of package `fr/pf-cmg`.

Pins CSS article versions from the LEGI mirror (see
`sources/source-manifest.json`; registry `.scratch/reg-css.json`, snapshot
2026-10-06) and the two reform decrees 2025-514 (R.531-6 June wording,
R.513-1 December wording is pf-core's: NOT pinned here) and 2025-515
(transitional differential, application dates, entry into force) from
their JORF mirrors. Version XML vendored in `sources/fr-pf-cmg/legi/`
and `sources/fr-pf-cmg/jorf/` (mirror `.scratch/legi/` is a cache,
not package bytes).

Covered numbers and their window wordings (back-to-back from the
coverage start 2021-01-01; earlier wordings only where the window
needs them):
  L531-5: ED2020 [2020-01-01,2025-09-01), ED2025_09 [2025-09-01,2025-12-31),
          ED2025_12 [2025-12-31,inf) — the 2026-01-01 V-bis wording
          (LEGIARTI000051288212) is MODIFIE_MORT_NE, never in force.
  L531-6: ED2020, ED2024_09 (tiers payant), ED2025_01 (EAJE tariff scope),
          ED2025_02 (tiers payant removed), ED2025_09 (reform).
  D531-17: ED2012 [2012-06-01,2022-01-01), ED2022, ED2025_09.
  D531-18: ED2018, ED2025_09 (formula with tables).
  D531-18-1: ED2018 [2018-04-01,2022-01-01), ED2022 [2022-01-01,2025-09-01),
          ED2025_09 (age <6, 12 for isolated parents).
  D531-18-2: ED2025_12 (shared residence, from 2025-12-01).
  D531-18-3: ED2025_09 (same-month cumulation of L.531-5 aids).
  D531-19: ED2012 [2012-06-01,2026-07-01), ED2026_07.
  D531-20: ED2020, ED2025_09 (L.531-6 ceilings, same nominals).
  D531-21: ED2015, ED2025_09 (L.531-6 scale + EAJE).
  D531-22: ED2012, ED2025_09 (specific-hours and AAH/disability/single
          majorations of the L.531-6 maxima).
  D531-23: ED2020 [2020-01-01,2021-09-01), ED2021 [2021-09-01,2025-09-01),
          ED2025_09 (cumulation L.531-5 x L.531-6).
  R531-5: single wording (activity assessment month).
  R531-6: ED2016 [2016-01-01,2024-07-01), ED2024, ED2025_06 (RSA insertion).
  JORF 2025-514: arts 2 (Dec-2025 deferred entry), 3 (execution).
  JORF 2025-515: arts 3 (transitional differential), 4 (reform dates),
          5 (entry into force), 6 (execution).

  fetch_pf_cmg_texts.py          — rebuild *.txt/articles.json from XML
  fetch_pf_cmg_texts.py --check  — same without writing: mismatch = error

Depth addressing (FINISH-W4, D-43 pilot): each map edition entry carries
`unit` mapped from the manifest doc class (`legi_article` ->
`fr_code_lettered_article`, `jorf_article` -> `fr_article`); the map top
level carries `scope` (current CSS article numbers), `unit`
(`fr_code_lettered_article`) and `document` (generated composite
`CMG-current.txt`: the 16 current CSS version texts at the cutoff, same
`Article <num>` rendering, CSS only — JORF decree articles keep their own
unit and stay out of the CSS scope, AAH precedent). The composite is
output only (GENERATED_OUTPUT_PENDING); edition documents, hashes and
fragment IDs are unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = ROOT / "corpus/laws/fr/pf-cmg"
SOURCE_DIR = PACKAGE / "sources/fr-pf-cmg"
LEGI_DIR = SOURCE_DIR / "legi"
JORF_DIR = SOURCE_DIR / "jorf"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

_MANIFEST = _load_manifest(PACKAGE)
DOCUMENTS = _MANIFEST["documents"]
SCOPE = _MANIFEST["scope"]
ACCOUNTING = SOURCE_DIR / "articles.json"
DEPTH = _MANIFEST["depth_layout"]
UNIT_BY_CLASS = {"legi_article": DEPTH["css_unit"],
                 "jorf_article": DEPTH["jorf_unit"]}


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def render(path: Path) -> tuple[str, str, str, str]:
    """Article version text from BLOC_TEXTUEL: `<p>` paragraphs as lines,
    `<table>` rows as `cell | cell` lines (the D. 531-18 effort-rate
    tables carry the normative numbers; a `<p>`-only rendering would
    silently drop them). Returns (num, date_debut, date_fin, text)."""
    root = ET.parse(path).getroot()

    def text(tag: str) -> str:
        el = root.find(f".//{tag}")
        return (el.text or "").strip() if el is not None and el.text else ""

    body = root.find(".//BLOC_TEXTUEL")
    lines: list[str] = []

    def walk(parent) -> None:
        for child in parent:
            tag = child.tag.split("}")[-1]
            if tag == "p":
                line = " ".join("".join(child.itertext()).split())
                if line:
                    lines.append(line)
            elif tag == "table":
                for row in child.findall(".//tr"):
                    cells = [" ".join("".join(c.itertext()).split())
                             for c in list(row)]
                    if any(cells):
                        lines.append(" | ".join(cells))
            elif tag in ("CONTENU",):
                walk(child)

    if body is not None:
        walk(body)
    return (text("NUM"), text("DATE_DEBUT"), text("DATE_FIN"),
            unicodedata.normalize("NFC", "\n".join(lines) + "\n"))


def nota_of(path: Path) -> str:
    root = ET.parse(path).getroot()
    parts = [" ".join("".join(p.itertext()).split())
             for p in root.findall(".//NOTA//p")]
    return " | ".join(p for p in parts if p)


def article(entry: dict) -> dict:
    sub = "jorf" if entry.get("corpus") == "jorf" else "legi"
    path = SOURCE_DIR / sub / f"{entry['id']}.xml"
    num, debut, fin, text = render(path)
    want = entry["num"].replace(".", "")
    if num.replace(".", "").replace(" ", "") != want.replace(" ", ""):
        raise SystemExit(f"{path}: number {num!r} != scope {entry['num']!r}")
    return {"fragment": entry["fragment"], "num": num, "edition": entry["edition"],
            "dump": entry["dump"], "legi_id": entry["id"],
            "sha256": sha256(text.encode("utf-8")), "in_force_from": debut,
            "in_force_to": fin if fin != "2999-01-01" else None,
            "applies_from": debut, "nota": nota_of(path), "text": text}


def build() -> tuple[dict[str, str], dict[str, str], dict]:
    articles = [article(entry) for entry in SCOPE]
    documents = {}
    for edition, (name, _unit_class, _heading) in DOCUMENTS.items():
        parts = [a for a in articles if a["edition"] == edition]
        # Pinned-byte header format: changing this line changes the
        # documentHash of every *.txt, so it stays as is by design.
        head = f"{name} — {len(parts)} версий охвата\n\n"
        body = "".join(f"Article {a['num']}\n{a['text']}\n" for a in parts)
        documents[edition] = head + body
    # Generated composite of the current CSS slice (depth top-level
    # document): same `Article <num>` rendering, declaration order, CSS
    # only. Created only by this generator; never hand-written.
    current_parts = []
    for edition in DEPTH["current_editions"]:
        if edition not in DOCUMENTS:
            raise SystemExit(f"depth_layout current_editions: unknown edition {edition!r}")
        current_parts += [a for a in articles if a["edition"] == edition]
    current_nums = [a["num"] for a in current_parts]
    if current_nums != DEPTH["current_scope"]:
        raise SystemExit("depth_layout current_scope != current_editions members: "
                         f"{current_nums!r}")
    current_name = DEPTH["current_document"]
    current_text = (f"{current_name} — {len(current_parts)} current slice versions "
                    f"at {DEPTH['cutoff']}\n\n"
                    + "".join(f"Article {a['num']}\n{a['text']}\n"
                              for a in current_parts))
    current = {current_name: current_text}
    versions: dict[str, dict] = {}
    for edition, text in documents.items():
        by_num: dict[str, dict] = {}
        for a in [x for x in articles if x["edition"] == edition]:
            by_num[a["legi_id"]] = {"num": a["num"], "fragment": a["fragment"],
                                   "sha256": a["sha256"], "dump": a["dump"],
                                   "in_force_from": a["in_force_from"],
                                   "in_force_to": a["in_force_to"],
                                   "applies_from": a["applies_from"],
                                   "nota": a["nota"]}
        unit_class = DOCUMENTS[edition][1]
        if unit_class not in UNIT_BY_CLASS:
            raise SystemExit(f"depth_layout: no depth unit mapped for doc class "
                             f"{unit_class!r} ({edition})")
        versions[edition] = {"document": DOCUMENTS[edition][0],
                             "documentHash": sha256(text.encode("utf-8")),
                             "unit": UNIT_BY_CLASS[unit_class],
                             "scope": [a["num"] for a in articles if a["edition"] == edition],
                             "versions": by_num}
    return documents, current, {"cutoff": DEPTH["cutoff"],
                       "coverage_start": DEPTH["coverage_start"],
                       "scope": DEPTH["current_scope"],
                       "unit": DEPTH["css_unit"],
                       "document": current_name,
                       "editions": [{"edition": ed, **versions[ed]}
                                    for ed in documents],
                       "$comment": "CMG pinning account: CSS article versions and reform decrees 2025-514/515 from the LEGI/JORF mirrors (snapshot 2026-10-06). NOTA is article bytes; applicability is read from them. editions is a LIST of {edition, document, ...}: the source-pinning gate iterates entries and calls .get (str keys would crash it). Depth top level (FINISH-W4 D-43): scope/unit/document address the generated current CSS composite; per-edition unit maps the manifest doc class; JORF editions keep fr_article and stay out of the CSS scope."}


def main(argv: list[str]) -> int:
    check = "--check" in argv
    documents, current, accounting = build()
    problems: list[str] = []
    for edition, (name, _unit_class, _heading) in DOCUMENTS.items():
        target = SOURCE_DIR / name
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != documents[edition]:
                problems.append(str(target))
        else:
            target.write_text(documents[edition], encoding="utf-8")
    for name, text in current.items():
        target = SOURCE_DIR / name
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != text:
                problems.append(str(target))
        else:
            target.write_text(text, encoding="utf-8")
    want = json.dumps(accounting, ensure_ascii=False, indent=2) + "\n"
    if check:
        if not ACCOUNTING.exists() or ACCOUNTING.read_text(encoding="utf-8") != want:
            problems.append(str(ACCOUNTING))
        if problems:
            print("differ from the pinned XML:\n" + "\n".join(problems))
            return 1
        print(f"pf-cmg: {len(SCOPE)} versions, {len(documents)} documents "
              f"+ current slice — clean")
        return 0
    ACCOUNTING.write_text(want, encoding="utf-8")
    print(f"pf-cmg: {len(SCOPE)} article versions + current slice")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
