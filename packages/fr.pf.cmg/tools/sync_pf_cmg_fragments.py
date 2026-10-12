#!/usr/bin/env python3
"""Fragments of `01-sources.law` of package `fr/pf-cmg` from the pinned bytes.

Reads `sources/fr-pf-cmg/articles.json` (accounted by
`fetch_pf_cmg_texts.py`) and rebuilds the block between the markers:
`publication <EDITION>_TEXT` (whole-document hash, §194) + `fragment` per
covered version. Do not edit by hand; a scope change is a manifest change
with a rebuild.

  sync_pf_cmg_fragments.py          — rebuild the block
  sync_pf_cmg_fragments.py --check  — stale block = error
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PACKAGE = ROOT / "corpus/laws/fr/pf-cmg"
ACCOUNTING = PACKAGE / "sources/fr-pf-cmg/articles.json"
TARGET = PACKAGE / "01-sources.law"
BEGIN = "// BEGIN GENERATED FR-PF-CMG FRAGMENTS"
END = "// END GENERATED FR-PF-CMG FRAGMENTS"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

EDITION_OF = _load_manifest(PACKAGE)["edition_of"]
NAMESPACE = "urn:fr:corpus:clir:pf-cmg"


def units() -> list[tuple[str, str, str, str, str]]:
    """(fragment id, locator, text, edition, article number)."""
    book = json.loads(ACCOUNTING.read_text(encoding="utf-8"))
    out = []
    for edition_book in book["editions"]:
        document = (PACKAGE / "sources/fr-pf-cmg" / edition_book["document"])
        body = document.read_text(encoding="utf-8").split("\n")
        for number in edition_book["scope"]:
            legi_id = next(k for k, v in edition_book["versions"].items()
                           if v["num"] == number)
            version = edition_book["versions"][legi_id]
            marker = f"Article {number}"
            try:
                start = body.index(marker)
            except ValueError as error:  # pragma: no cover — scope mismatch
                raise SystemExit(f"{edition_book['document']} has no line {marker!r}") from error
            end = start + 1
            while end < len(body) and body[end] != "":
                end += 1
            text = "\n".join([marker, *body[start + 1:end]]) + "\n"
            out.append((version["fragment"], f"article/{number}", text,
                        EDITION_OF[edition_book["document"]], number))
    return out


def block() -> str:
    book = json.loads(ACCOUNTING.read_text(encoding="utf-8"))
    lines = [BEGIN, ""]
    for entry in book["editions"]:
        edition = EDITION_OF[entry["document"]]
        lines += [f"publication {edition}_TEXT of {edition} {{",
                  "    media_type \"text/plain; charset=utf-8\";",
                  "    uri \"https://echanges.dila.gouv.fr/OPENDATA/LEGI/\";",
                  "    retrieved_at @2026-10-06T00:00:00Z;",
                  f"    content_hash \"{entry['documentHash']}\";",
                  f"    local_path \"sources/fr-pf-cmg/{entry['document']}\";",
                  "}", ""]
    for fragment, locator, text, edition, number in units():
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        lines.append(f'@id("{NAMESPACE}#{fragment}")')
        lines.append(f"pub fragment {fragment} in {edition} {{")
        lines.append("    kind article;")
        lines.append(f'    locator "{locator}";')
        lines.append(f'    text fr official """{text}""";')
        lines.append(f'    content_hash "sha256:{digest}";')
        lines.append("}")
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    check = "--check" in argv
    current = TARGET.read_text(encoding="utf-8")
    head, _, rest = current.partition(BEGIN)
    _, _, tail = rest.partition(END)
    rebuilt = head + block() + tail
    if check:
        if rebuilt != current:
            print(f"{TARGET.relative_to(ROOT)}: fragment block is stale")
            return 1
        print(f"pf-cmg: block is current ({len(units())} fragments)")
        return 0
    TARGET.write_text(rebuilt, encoding="utf-8")
    print(f"{TARGET.relative_to(ROOT)}: {len(units())} fragments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
