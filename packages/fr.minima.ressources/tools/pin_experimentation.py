#!/usr/bin/env python3
"""Закрепить основание эксперимента «départements expérimentateurs» (с 10.2024).

OpenFisca-France (`departement_experimentation_rsa`, `formula_2024_10`) считает ресурсы
RSA за месяцы M-4…M-2 в отдельных департаментах с октября 2024 года. Основание — не
кодифицированный текст CASF, а два акта вне кодексов (глобальный дамп LEGI DILA, тот же,
что у пакетов fr.casf.rsa и fr.minima.ressources: Freemium_legi_global_20250713-140000):

  * décret n° 2024-693 du 5 juillet 2024 «portant expérimentation des déclarations
    préremplies de ressources pour l'attribution du revenu de solidarité active et de la
    prime d'activité» (JORFTEXT000049888897), статьи 1–10;
  * arrêté du 7 juillet 2024 «fixant les dates de début et de fin de l'expérimentation …»
    (JORFTEXT000049894945), статья 1: с 1er octobre 2024 по 1er mars 2025.

Пишет `sources/experimentation-2024/<акт>.txt` (статьи как в CONTENU, под заголовками
«Article N») и учёт `sources/experimentation-2024/manifest.json` (идентификаторы
LEGI/JORF, путь в дампе, sha256 XML статей и текста, дата начала версии). Граница модели —
README пакета, раздел «B-RSA-EXPERIMENTATION-2024». Правил в 02-trimestre.law эксперимент
не получил: текст ст. 3 однозначен, но реализация — второй режим расчёта квартала на окне
[2024-10-01, 2025-03-01) для одних департаментов, и это правка ~22 правил, а не вставка.

  python3 corpus/laws/fr/minima-ressources/tools/pin_experimentation.py --write   # читает дамп (~10 мин)
  python3 corpus/laws/fr/minima-ressources/tools/pin_experimentation.py --check   # сверяет тексты с учётом
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

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "corpus/laws/fr/minima-ressources"
OUT = PKG / "sources/experimentation-2024"
DUMP = ROOT / ".scratch/legi/Freemium_legi_global_20250713-140000.tar.gz"
DUMP_URL = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/Freemium_legi_global_20250713-140000.tar.gz"

#: акт → (JORFTEXT, номера статей)
ACTS = {
    "decret-2024-693": ("JORFTEXT000049888897", [str(n) for n in range(1, 11)]),
    "arrete-2024-07-07": ("JORFTEXT000049894945", ["1"]),
}


def tag(xml: str, name: str) -> str:
    found = re.search(rf"<{name}>([^<]*)", xml)
    return found.group(1).strip() if found else ""


def contenu(xml: str) -> str:
    body = re.search(r"<CONTENU>(.*?)</CONTENU>", xml, re.S).group(1)
    body = re.sub(r"<br\s*/?>|</p>", "\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", "", body))
    return "\n".join(line.strip() for line in body.splitlines() if line.strip())


def write() -> int:
    owners = {jorf: act for act, (jorf, _) in ACTS.items()}
    articles: dict[str, list] = {act: [] for act in ACTS}
    heads: dict[str, tuple[str, bytes]] = {}
    with tarfile.open(DUMP, "r|gz") as tar:
        for member in tar:
            if not member.isfile() or "/JORF/TEXT/" not in member.name:
                continue
            owner = re.search(r"/(JORFTEXT\d{12})/(article|texte/version)/", member.name)
            if not owner or owner.group(1) not in owners:
                continue
            raw = tar.extractfile(member).read()
            act = owners[owner.group(1)]
            if owner.group(2) == "article":
                articles[act].append((member.name, raw))
            else:
                heads[act] = (member.name, raw)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for act, (jorf, wanted) in ACTS.items():
        head_path, head_raw = heads[act]
        head = head_raw.decode("utf-8")
        picked = {}
        for path, raw in articles[act]:
            xml = raw.decode("utf-8")
            if tag(xml, "NUM") in wanted and tag(xml, "ETAT") == "VIGUEUR":
                picked[tag(xml, "NUM")] = (path, raw, xml)
        missing = [n for n in wanted if n not in picked]
        assert not missing, (act, missing)
        text = "".join(f"Article {n}\n{contenu(picked[n][2])}\n" for n in wanted)
        (OUT / f"{act}.txt").write_text(text, encoding="utf-8")
        rows.append({
            "acte": act, "jorftext": jorf, "titre": html.unescape(tag(head, "TITREFULL")),
            "nor": tag(head, "NOR"), "date_texte": tag(head, "DATE_TEXTE"),
            "date_publi": tag(head, "DATE_PUBLI"),
            "texte_dump_path": head_path, "texte_xml_sha256": hashlib.sha256(head_raw).hexdigest(),
            "articles": [{"num": n, "legiarti": tag(picked[n][2], "ID"), "etat": "VIGUEUR",
                          "version_debut": tag(picked[n][2], "DATE_DEBUT"),
                          "dump_path": picked[n][0],
                          "xml_sha256": hashlib.sha256(picked[n][1]).hexdigest()} for n in wanted],
            "text": f"sources/experimentation-2024/{act}.txt",
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        })
    manifest = {
        "dump": DUMP_URL, "retrieved_at": "2026-10-08",
        "scope": "Expérimentation 2024-2025 des déclarations trimestrielles préremplies de ressources "
                 "(RSA et prime d'activité): départements des Alpes-Maritimes, de l'Aube, de l'Hérault, "
                 "des Pyrénées-Atlantiques et de la Vendée (art. 1er du décret)",
        "model": "NOT_MODELLED", "acts": rows,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"закреплено {len(rows)} акта → {OUT.relative_to(ROOT)}")
    return 0


def check() -> int:
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    bad = [row["acte"] for row in manifest["acts"]
           if hashlib.sha256((PKG / row["text"]).read_bytes()).hexdigest() != row["text_sha256"]]
    print("OK" if not bad else f"расхождение: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sys.exit(write() if args.write else check())
