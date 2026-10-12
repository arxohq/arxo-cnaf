#!/usr/bin/env python3
"""SMIC, ряд 2026 года → байты пакета `fr/smic` (фаза 0, по образцу APL).

Закрепляются открытые данные JORF DILA (суточные архивы; полные тексты —
`JORFTEXT*.xml`, статьи — `JORFARTI*.xml`): декрет № 2025-1228 от 17.12.2025
(эффект 01.01.2026) и арретэ от 22.05.2026 (эффект 01.06.2026). Охват —
ДАННЫЕ (`sources/source-manifest.json`), не перечни в коде.

  fetch_smic_texts.py          — пересобрать *.txt/articles.json из XML
  fetch_smic_texts.py --check  — то же без записи: расхождение = ошибка
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = ROOT / "corpus/laws/fr/smic"
SOURCE_DIR = PACKAGE / "sources/fr-smic"
LEGI_DIR = SOURCE_DIR / "legi"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

_MANIFEST = _load_manifest(PACKAGE)
DOCUMENTS = _MANIFEST["documents"]
SCOPE = _MANIFEST["scope"]
ACCOUNTING = SOURCE_DIR / "articles.json"


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def render(path: Path) -> tuple[str, str, str]:
    """Текст статьи из BLOC_TEXTUEL: абзацы `<p>` — строкой, таблицы — строкой
    на `<tr>` с ячейками через « | ». Возвращает (num, date_debut, text)."""
    root = ET.parse(path).getroot()

    def text(tag: str) -> str:
        el = root.find(f".//{tag}")
        return (el.text or "").strip() if el is not None and el.text else ""

    def blocks(parent) -> list:
        """Абзацы и таблицы уровня блока: LEGI кладёт `<p>` прямо в
        BLOC_TEXTUEL, JORF заворачивает их в CONTENU."""
        out = []
        for child in parent:
            tag = child.tag.split("}")[-1]
            if tag in ("p", "table"):
                out.append(child)
            elif tag == "CONTENU":
                out.extend(blocks(child))
        return out

    body = root.find(".//BLOC_TEXTUEL")
    lines: list[str] = []
    if body is not None:
        for elem in blocks(body):
            tag = elem.tag.split("}")[-1]
            if tag == "p":
                line = " ".join("".join(elem.itertext()).split())
                if line:
                    lines.append(line)
            elif tag == "table":
                for row in elem.iter("tr"):
                    cells = [" ".join("".join(c.itertext()).split()) for c in row.iter("td")]
                    cells = [c for c in cells if c]
                    if cells:
                        lines.append(" | ".join(cells))
    return text("NUM"), text("DATE_DEBUT"), unicodedata.normalize("NFC", "\n".join(lines) + "\n")


def article(entry: dict) -> dict:
    path = LEGI_DIR / entry["dir"] / f"{entry['id']}.xml"
    num, debut, text = render(path)
    want = entry["num"].replace(".", "")
    if num.replace(".", "").replace(" ", "") != want.replace(" ", ""):
        raise SystemExit(f"{path}: номер {num!r} != охват {entry['num']!r}")
    return {"fragment": entry["fragment"], "num": num, "edition": entry["edition"],
            "dump": entry["dump"], "legi_id": entry["id"],
            "sha256": sha256(text.encode("utf-8")), "in_force_from": debut,
            "applies_from": debut, "text": text}


def build() -> tuple[dict[str, str], dict]:
    articles = [article(entry) for entry in SCOPE]
    documents = {}
    for edition, (name, _unit, _heading) in DOCUMENTS.items():
        parts = [a for a in articles if a["edition"] == edition]
        head = f"{name} — {len(parts)} статей охвата\n\n"
        body = "".join(f"Article {a['num']}\n{a['text']}\n" for a in parts)
        documents[edition] = head + body
    versions: list[dict] = []
    for edition, text in documents.items():
        by_num: dict[str, dict] = {}
        for a in [x for x in articles if x["edition"] == edition]:
            by_num[a["num"]] = {"legi_id": a["legi_id"], "fragment": a["fragment"],
                                "sha256": a["sha256"], "dump": a["dump"],
                                "in_force_from": a["in_force_from"],
                                "applies_from": a["applies_from"]}
        # Форма `editions` — список, как у остальных пакетов с несколькими
        # редакциями (ворота закрепления §33.1 читают именно её): `unit` —
        # конвенция «Article N» на своей строке, `declared` — статей вне охвата нет.
        versions.append({"edition": edition, "document": DOCUMENTS[edition][0], "unit": "fr_article",
                         "documentHash": sha256(text.encode("utf-8")),
                         "scope": [a["num"] for a in articles if a["edition"] == edition],
                         "versions": by_num, "declared": {}})
    return documents, {"editions": versions,
                       "$comment": "Учёт закрепления ряда SMIC 2021–2026: версии статей из глобального дампа LEGI (2020–2024) и суточных архивов JORF (2026), DILA."}


def main(argv: list[str]) -> int:
    check = "--check" in argv
    documents, accounting = build()
    problems: list[str] = []
    for edition, (name, _unit, _heading) in DOCUMENTS.items():
        target = SOURCE_DIR / name
        if check:
            if not target.exists() or target.read_text(encoding="utf-8") != documents[edition]:
                problems.append(str(target))
        else:
            target.write_text(documents[edition], encoding="utf-8")
    want = json.dumps(accounting, ensure_ascii=False, indent=2) + "\n"
    if check:
        if not ACCOUNTING.exists() or ACCOUNTING.read_text(encoding="utf-8") != want:
            problems.append(str(ACCOUNTING))
        if problems:
            print("расходятся с закреплёнными XML:\n" + "\n".join(problems))
            return 1
        print(f"smic: {len(SCOPE)} версий, {len(documents)} документа — чисто")
        return 0
    ACCOUNTING.write_text(want, encoding="utf-8")
    print(f"smic: {len(SCOPE)} версий статей")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
