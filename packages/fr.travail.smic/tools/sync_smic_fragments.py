#!/usr/bin/env python3
"""Фрагменты `01-sources.law` пакета `fr/smic` из закреплённых байтов.

Читает `sources/fr-smic/articles.json` (учёт `fetch_smic_texts.py`) и
пересобирает блок между маркерами: `publication <РЕД>_TEXT` (хэш целого
документа, §194) + `fragment` на каждую статью охвата. Руками не править;
правка охвата — правка манифеста с пересборкой.

  sync_smic_fragments.py          — пересобрать блок
  sync_smic_fragments.py --check  — блок устарел = ошибка
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = ROOT / "corpus/laws/fr/smic"
ACCOUNTING = PACKAGE / "sources/fr-smic/articles.json"
TARGET = PACKAGE / "01-sources.law"
BEGIN = "// BEGIN GENERATED FR-SMIC FRAGMENTS"
END = "// END GENERATED FR-SMIC FRAGMENTS"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

_MANIFEST = _load_manifest(PACKAGE)
DOCUMENTS = _MANIFEST["documents"]          # ключ документа -> [файл, unit, заголовок]
EDITION_OF = _MANIFEST["edition_of"]        # файл документа -> редакция пакета
DUMPS = {d["archive"]: d for d in _MANIFEST.get("dumps", [])}


def edition_of_dockey(dockey: str) -> str:
    """Редакция пакета по ключу документа манифеста."""
    return EDITION_OF[DOCUMENTS[dockey][0]]


def dump_of_dockey(dockey: str) -> dict:
    row = next(r for r in _MANIFEST["scope"] if r["edition"] == dockey)
    return DUMPS.get(row["dump"], {})


def block(book: dict) -> str:
    lines = [BEGIN, ""]
    entries = {e["edition"]: e for e in book["editions"]}
    dockeys = list(entries)
    for dockey in dockeys:
        entry = entries[dockey]
        edition = edition_of_dockey(dockey)
        doc = DOCUMENTS[dockey][0]
        dump = dump_of_dockey(dockey)
        lines += [f"publication {edition}_TEXT of {edition} {{",
                  "    media_type \"text/plain; charset=utf-8\";",
                  f"    uri \"{dump.get('url', 'https://echanges.dila.gouv.fr/OPENDATA/JORF/')}\";",
                  f"    retrieved_at @{dump.get('retrieved_at', '2026-10-05')}T00:00:00Z;",
                  f"    content_hash \"{entry['documentHash']}\";",
                  f"    local_path \"sources/fr-smic/{doc}\";",
                  "}", ""]
    for dockey in dockeys:
        entry = entries[dockey]
        edition = edition_of_dockey(dockey)
        text = (PACKAGE / "sources/fr-smic" / DOCUMENTS[dockey][0]).read_text(encoding="utf-8")
        for num in entry["scope"]:
            row = next(r for r in _MANIFEST["scope"]
                       if r["edition"] == dockey and r["num"] == num)
            section = f"Article {num}\n"
            start = text.find(section)
            if start < 0:
                raise SystemExit(f"нет секции {section.strip()} в {DOCUMENTS[dockey][0]}")
            stop = text.find("\nArticle ", start + 1)
            body = text[start:stop if stop > 0 else len(text)].rstrip("\n") + "\n"
            digest = "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
            lines += [f"@id(\"urn:fr:corpus:clir:smic#{row['fragment']}\")",
                      f"pub fragment {row['fragment']} in {edition} {{",
                      "    kind article;",
                      f"    locator \"article/{num}\";",
                      f"    text fr official \"\"\"{body}\"\"\";",
                      f"    content_hash \"{digest}\";",
                      "}", ""]
    lines.append(END)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    book = json.loads(ACCOUNTING.read_text(encoding="utf-8"))
    current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
    count = sum(len(e["scope"]) for e in book["editions"])
    if BEGIN not in current:
        if check:
            print(f"{TARGET}: нет генерируемого блока")
            return 1
        rebuilt = block(book) + "\n"
    else:
        head, rest = current.split(BEGIN, 1)
        _old, tail = rest.split(END, 1)
        rebuilt = head + block(book) + tail
    if check:
        if rebuilt != current:
            print(f"{TARGET}: блок фрагментов устарел")
            return 1
        print(f"smic: блок в сроке ({count} фрагментов)")
        return 0
    TARGET.write_text(rebuilt, encoding="utf-8")
    print(f"{TARGET.relative_to(ROOT)}: {count} фрагментов")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
