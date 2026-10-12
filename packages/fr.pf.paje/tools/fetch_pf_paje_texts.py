#!/usr/bin/env python3
"""PAJE part 1 (birth and adoption grant) → bytes of package `fr/pf-paje`.

Pins 7 CSS article versions from the LEGI mirror (see
`sources/source-manifest.json`; registry `.scratch/reg-css.json`, snapshot
2026-10-06): L531-2 (1 wording in the window), D531-2 (2), R531-1 (2),
D531-3-1 (1), D531-1 (1, context). Version XML vendored in
`sources/fr-pf-paje/legi/` (mirror `.scratch/legi/` is a cache, not package
bytes).

  fetch_pf_paje_texts.py          — rebuild *.txt/articles.json from XML
  fetch_pf_paje_texts.py --check  — same without writing: mismatch = error
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
PACKAGE = ROOT / "corpus/laws/fr/pf-paje"
SOURCE_DIR = PACKAGE / "sources/fr-pf-paje"
LEGI_DIR = SOURCE_DIR / "legi"

sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

_MANIFEST = _load_manifest(PACKAGE)
DOCUMENTS = _MANIFEST["documents"]
SCOPE = _MANIFEST["scope"]
ACCOUNTING = SOURCE_DIR / "articles.json"


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _contenu_lines(parent) -> list[str]:
    """Text lines of BLOC_TEXTUEL/NOTA in document order.

    Wave-3 fix: LEGI writes some articles without `<p>` — the sentence sits
    directly in CONTENU, split by `<br/>` (D. 531-1, R. 531-3, old L. 531-4-1).
    The wave-1 walk read only `<p>` and pinned those fragments EMPTY. Now the
    CONTENU head text and every `<br/>` tail count as lines too; `<p>` lines
    are unchanged, so the six non-empty wave-1 documents rebuild byte-identical.
    """
    lines: list[str] = []

    def emit(raw: str | None) -> None:
        line = " ".join((raw or "").split())
        if line:
            lines.append(line)

    def walk(el) -> None:
        emit(el.text)
        for child in el:
            tag = child.tag.split("}")[-1]
            if tag == "p":
                emit("".join(child.itertext()))
                emit(child.tail)
            elif tag == "br":
                emit(child.tail)
            elif tag == "CONTENU":
                walk(child)
            else:  # pragma: no cover — unknown inline element
                emit("".join(child.itertext()))
                emit(child.tail)

    body = parent.find(".//BLOC_TEXTUEL")
    if body is not None:
        for contenu in body.findall("CONTENU"):
            walk(contenu)
        if not body.findall("CONTENU"):
            walk(body)
    out = [l for i, l in enumerate(lines) if i == 0 or lines[i - 1] != l]
    return out


def render(path: Path) -> tuple[str, str, str, str]:
    """Article version text from BLOC_TEXTUEL: paragraphs as lines.
    Returns (num, date_debut, date_fin, text)."""
    root = ET.parse(path).getroot()

    def text(tag: str) -> str:
        el = root.find(f".//{tag}")
        return (el.text or "").strip() if el is not None and el.text else ""

    lines = _contenu_lines(root)
    return (text("NUM"), text("DATE_DEBUT"), text("DATE_FIN"),
            unicodedata.normalize("NFC", "\n".join(lines) + "\n") if lines else "")


def nota_of(path: Path) -> str:
    root = ET.parse(path).getroot()
    nota = root.find(".//NOTA")
    if nota is None:
        return ""
    parts = [" ".join("".join(p.itertext()).split())
             for p in nota.findall(".//p")]
    for contenu in nota.findall("CONTENU"):
        head = " ".join((contenu.text or "").split())
        if head:
            parts.append(head)
        for child in contenu:
            if child.tag.split("}")[-1] == "br" and (child.tail or "").strip():
                parts.append(" ".join(child.tail.split()))
    return " | ".join(p for p in parts if p)


def article(entry: dict) -> dict:
    path = SOURCE_DIR / entry["dir"] / f"{entry['id']}.xml"
    num, debut, fin, text = render(path)
    want = entry["num"].replace(".", "")
    if num.replace(".", "").replace(" ", "") != want.replace(" ", ""):
        raise SystemExit(f"{path}: number {num!r} != scope {entry['num']!r}")
    return {"fragment": entry["fragment"], "num": num, "edition": entry["edition"],
            "dump": entry["dump"], "legi_id": entry["id"],
            "sha256": sha256(text.encode("utf-8")), "in_force_from": debut,
            "in_force_to": fin if fin != "2999-01-01" else None,
            "applies_from": debut, "nota": nota_of(path), "text": text}


def build() -> tuple[dict[str, str], dict]:
    articles = [article(entry) for entry in SCOPE]
    documents = {}
    for edition, (name, _unit, _heading) in DOCUMENTS.items():
        parts = [a for a in articles if a["edition"] == edition]
        # Pinned-byte header format: changing this line changes the
        # documentHash of every *.txt, so it stays as is by design.
        head = f"{name} — {len(parts)} версий охвата\n\n"
        body = "".join(f"Article {a['num']}\n{a['text']}\n" for a in parts)
        documents[edition] = head + body
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
        versions[edition] = {"document": DOCUMENTS[edition][0],
                             "documentHash": sha256(text.encode("utf-8")),
                             "scope": [a["num"] for a in articles if a["edition"] == edition],
                             "versions": by_num}
    return documents, {"editions": [{"edition": ed, **versions[ed]}
                                     for ed in documents],
                       "$comment": "PAJE part 1 pinning account: CSS article versions from the LEGI mirror (snapshot 2026-10-06). NOTA is article bytes; applicability is read from them. editions is a LIST of {edition, document, ...}: the source-pinning gate iterates entries and calls .get (str keys would crash it)."}


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
            print("differ from the pinned XML:\n" + "\n".join(problems))
            return 1
        print(f"pf-paje: {len(SCOPE)} versions, {len(documents)} documents — clean")
        return 0
    ACCOUNTING.write_text(want, encoding="utf-8")
    print(f"pf-paje: {len(SCOPE)} article versions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
