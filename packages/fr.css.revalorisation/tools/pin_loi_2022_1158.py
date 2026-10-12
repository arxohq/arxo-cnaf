#!/usr/bin/env python3
"""Закрепить статью 9 закона n° 2022-1158 (коэффициент 1,04 с 1 июля 2022).

Источник — глобальный дамп LEGI DILA (тот же, что у L. 161-25 и у пакета
`fr.rsa`: Freemium_legi_global_20250713-140000). Статья 9 лежит в дампе как
LEGIARTI000046188473 (версия VIGUEUR, начало 2022-08-18) закона
LEGITEXT000046188434 / JORFTEXT000046186723 (NOR ECOX2217989L). Пишется
`sources/loi-2022-1158-art9.txt` (текст статьи, формат как у `L161-25.txt`:
первая строка «Article 9», дальше абзацы) и запись `loi_2022_1158_art9` в
`sources/loi-2022-1158-art9.json` (идентификаторы, путь в дампе, sha256 XML и
текста).

  python3 tools/pin_loi_2022_1158.py --write            # читает дамп (~10-30 мин)
  python3 tools/pin_loi_2022_1158.py --write --xml F    # F — уже извлечённый XML статьи
  python3 tools/pin_loi_2022_1158.py --check            # сверяет текст с учётом

Закрепление — вход фрагмента `LOI_2022_1158_ART9` в `01-sources.law` и
сценария `tests/bmaf-chaine-2022-07.lawtest`.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import tarfile
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
ROOT = PKG.parents[3]
OUT_TXT = PKG / "sources/loi-2022-1158-art9.txt"
OUT_JSON = PKG / "sources/loi-2022-1158-art9.json"
DUMP = ROOT / ".scratch/legi/Freemium_legi_global_20250713-140000.tar.gz"
DUMP_URL = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/Freemium_legi_global_20250713-140000.tar.gz"
ARTI = "LEGIARTI000046188473"
JORFTEXT = "JORFTEXT000046186723"
MEMBER = (
    "legi/global/code_et_TNC_en_vigueur/TNC_en_vigueur/JORF/TEXT/00/00/46/18/67/"
    f"{JORFTEXT}/article/LEGI/ARTI/00/00/46/18/84/{ARTI}.xml"
)
VERSION_MEMBER = (
    "legi/global/code_et_TNC_en_vigueur/TNC_en_vigueur/JORF/TEXT/00/00/46/18/67/"
    f"{JORFTEXT}/texte/version/LEGITEXT000046188434.xml"
)


def contenu(xml: str) -> str:
    body = re.search(r"<CONTENU>(.*?)</CONTENU>", xml, re.S).group(1)
    body = re.sub(r"<br\s*/?>|</p>", "\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", "", body))
    return "\n".join(line.strip() for line in body.splitlines() if line.strip()) + "\n"


def tag(xml: str, name: str) -> str:
    return re.search(rf"<{name}>([^<]*)", xml).group(1).strip()


def read_dump() -> tuple[bytes, bytes]:
    found: dict[str, bytes] = {}
    with tarfile.open(DUMP, "r|gz") as tar:
        for member in tar:
            if member.isfile() and member.name in (MEMBER, VERSION_MEMBER):
                found[member.name] = tar.extractfile(member).read()
                if len(found) == 2:
                    break
    return found[MEMBER], found[VERSION_MEMBER]


def write(xml_path: str | None, version_path: str | None) -> int:
    if xml_path:
        raw = Path(xml_path).read_bytes()
        head = Path(version_path).read_bytes() if version_path else b""
    else:
        raw, head = read_dump()
    xml = raw.decode("utf-8")
    assert tag(xml, "ID") == ARTI and tag(xml, "NUM") == "9", "not article 9"
    text = "Article 9\n" + contenu(xml)
    OUT_TXT.write_text(text, encoding="utf-8")
    hx = head.decode("utf-8") if head else ""
    record = {
        "dump": DUMP_URL,
        "retrieved_at": "2026-10-08",
        "dump_path": MEMBER,
        "legiarti": ARTI,
        "jorftext": JORFTEXT,
        "legitext": "LEGITEXT000046188434",
        "article": "9",
        "etat": tag(xml, "ETAT"),
        "version_debut": tag(xml, "DATE_DEBUT"),
        "xml_sha256": hashlib.sha256(raw).hexdigest(),
        "text": "sources/loi-2022-1158-art9.txt",
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    if hx:
        record.update(
            titre=html.unescape(tag(hx, "TITREFULL")),
            nor=tag(hx, "NOR"),
            date_texte=tag(hx, "DATE_TEXTE"),
            date_publi=tag(hx, "DATE_PUBLI"),
            texte_dump_path=VERSION_MEMBER,
            texte_xml_sha256=hashlib.sha256(head).hexdigest(),
        )
    OUT_JSON.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"закреплено → {OUT_TXT.relative_to(ROOT)}")
    return 0


def check() -> int:
    record = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    got = hashlib.sha256(OUT_TXT.read_bytes()).hexdigest()
    ok = got == record["text_sha256"]
    print("OK" if ok else f"расхождение: {got} != {record['text_sha256']}")
    return 0 if ok else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--xml", help="уже извлечённый XML статьи (вместо чтения дампа)")
    parser.add_argument("--version-xml", help="уже извлечённый XML texte/version закона")
    args = parser.parse_args()
    sys.exit(write(args.xml, args.version_xml) if args.write else check())
