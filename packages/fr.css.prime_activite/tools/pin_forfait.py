#!/usr/bin/env python3
"""Закрепить тексты, из которых строится montant forfaitaire PPA (L. 842-3, DECISION-0452).

Montant forfaitaire personne seule задаёт декрет, затем L. 842-3 ревалоризует его на 1 апреля
коэффициентом L. 161-25. Для цепочки нужны три вида байтов, все — из официальных источников:

  1. Декреты о montant forfaitaire (ст. 1 — число и месяц права): 2020-491, 2021-528, 2022-701,
     2023-343, 2024-403, 2025-294 — из глобального дампа LEGI DILA
     `Freemium_legi_global_20250713-140000` (TNC_en_vigueur/JORF); декрет 2026-222 (ст. 2 — число,
     ст. 3 — дата применения) — из суточного инкремента LEGI 31.03.2026 (`.scratch/legi/mirror`),
     которого в дампе нет (дамп кончается 13.07.2025).
  2. Коэффициент L. 161-25 на 1 апреля 2020–2026 — абзацы инструкций DSS, уже закреплённые
     пакетом `fr.css.revalorisation` (читаются, не правятся): байты абзаца копируются дословно и
     сверяются с фрагментом того пакета (`content_hash`) и с его извлечённым текстом инструкции.
  3. Ст. 9 закона 2022-1158 (+4 % с 01.07.2022) — те же байты, что закрепил
     `fr.css.revalorisation` (сверка по `text_sha256` его учёта).

Пишет `sources/montant/<имя>.txt` и `sources/montant/manifest.json`. Генератор
`tools/build_sources.py` вносит эти тексты в 01-sources.law, генератор
`tools/build_forfait_chaine.py` — выписывает из них числа правил модуля 11-forfait-chaine.law.

  python3 corpus/laws/fr/prime-activite/tools/pin_forfait.py --write   # читает дамп (~10 мин)
  python3 corpus/laws/fr/prime-activite/tools/pin_forfait.py --check   # сверяет тексты с учётом
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
PKG = ROOT / "corpus/laws/fr/prime-activite"
OUT = PKG / "sources/montant"
DUMP = ROOT / ".scratch/legi/Freemium_legi_global_20250713-140000.tar.gz"
DUMP_URL = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/Freemium_legi_global_20250713-140000.tar.gz"
MIRROR_2026 = ROOT / ".scratch/legi/mirror/JORFTEXT000053733855/increments/LEGI_20260331-215650/article/LEGI/ARTI/00/00/53/73/96"
REVALO = ROOT / "corpus/laws/fr/revalorisation"

#: (имя файла, JORFTEXT, идентификатор статьи, номер статьи, источник байтов, начало применения,
#:  подстрока текста, подтверждающая начало)
#: Начало применения — месяц права, с которого действует сумма («primes calculées pour déterminer le
#: montant dû au titre du mois d'avril 2021», «à compter du 1er avril 2023»).
DECREE_ARTICLES = [
    ("decret-2020-491-art1", "JORFTEXT000041835204", "LEGIARTI000041838367", "1", "dump", "2020-04-01", "mois d'avril 2020"),
    ("decret-2021-528-art1", "JORFTEXT000043459542", "LEGIARTI000043462055", "1", "dump", "2021-04-01", "mois d'avril 2021"),
    ("decret-2022-701-art1", "JORFTEXT000045668709", "LEGIARTI000045673887", "1", "dump", "2022-04-01", "mois d'avril 2022"),
    ("decret-2023-343-art1", "JORFTEXT000047521594", "LEGIARTI000047521806", "1", "dump", "2023-04-01", "1er avril 2023"),
    ("decret-2024-403-art1", "JORFTEXT000049490757", "LEGIARTI000049492015", "1", "dump", "2024-04-01", "1er avril 2024"),
    ("decret-2025-294-art1", "JORFTEXT000051393100", "LEGIARTI000051395318", "1", "dump", "2025-04-01", "1er avril 2025"),
    ("decret-2026-222-art2", "JORFTEXT000053733855", "LEGIARTI000053739626", "2", "mirror2026", "2026-04-01", None),
    ("decret-2026-222-art3", "JORFTEXT000053733855", "LEGIARTI000053739628", "3", "mirror2026", "2026-04-01", "1er avril 2026"),
]

#: фрагменты fr.css.revalorisation с коэффициентом L. 161-25 → (файл инструкции, имя файла)
COEFFICIENTS = [
    ("DSS_SD2B_2020_33_COEFF", "dss-2020-33.txt", "dss-2020-33-coeff"),
    ("DSS_2B_2021_65_COEFF", "dss-2021-65.txt", "dss-2021-65-coeff"),
    ("DSS_2B_2022_82_COEFF", "dss-2022-82.txt", "dss-2022-82-coeff"),
    ("DSS_2B_2023_41_COEFF", "dss-2023-41.txt", "dss-2023-41-coeff"),
    ("DSS_2B_2024_43_COEFF", "dss-2024-43.txt", "dss-2024-43-coeff"),
    ("DSS_2B_2025_38_COEFF", "dss-2025-38.txt", "dss-2025-38-coeff"),
    ("DSS_2026_46_COEFF", "dss-2026-46.txt", "dss-2026-46-coeff"),
]
LOI_NAME = "loi-2022-1158-art9"


def alineas(xml: str) -> list[str]:
    """Алинеи BLOC_TEXTUEL (как `build_sources.xml_alineas`), без NOTA."""
    block = re.search(r"<BLOC_TEXTUEL>.*?</BLOC_TEXTUEL>", xml, re.S).group(0)
    block = re.sub(r"</p\s*>", "\n\n", block)
    block = re.sub(r"(<br\s*/>\s*){2,}", "\n\n", block)
    block = re.sub(r"<br\s*/>", " ", block)
    block = re.sub(r"<[^>]+>", "", block)
    parts = [re.sub(r"\s+", " ", html.unescape(t)).strip() for t in block.split("\n\n")]
    return [t for t in parts if t]


def context(xml: str, jorftext: str) -> dict:
    """Заголовок, NOR и даты декрета — из контекста самой статьи."""
    texte = re.search(r"<TEXTE\b([^>]*)>", xml).group(1)
    attr = lambda name: re.search(rf'{name}="([^"]*)"', texte).group(1)
    title = re.search(r'<TITRE_TXT[^>]*id_txt="%s"[^>]*>([^<]*)<' % jorftext, xml).group(1)
    return {"titre": html.unescape(title).strip(), "nor": attr("nor"), "numero": attr("num"),
            "date_signature": attr("date_signature"), "date_publi": attr("date_publi")}


def tag(xml: str, name: str) -> str:
    found = re.search(rf"<{name}>([^<]*)", xml)
    return found.group(1).strip() if found else ""


def fragment_texts() -> dict[str, dict]:
    """Фрагменты fr.css.revalorisation: имя → текст, content_hash, подписи и публикация источника."""
    law = (REVALO / "01-sources.law").read_text(encoding="utf-8")
    sources = {}
    for match in re.finditer(r'\nsource (\w+) \{(.*?)\n\}', law, re.S):
        body = match.group(2)
        fr = re.search(r'label fr official "([^"]*)"', body)
        en = re.search(r'label en unofficial "([^"]*)"', body)
        sources[match.group(1)] = (fr.group(1) if fr else "", en.group(1) if en else "")
    editions = {m.group(1): m.group(2) for m in re.finditer(r'\nedition (\w+) of (\w+) \{', law)}
    publications = {}
    for match in re.finditer(r'\npublication (\w+) of (\w+) \{(.*?)\n\}', law, re.S):
        body = match.group(3)
        if 'media_type "text/plain' in body:
            publications[match.group(2)] = (re.search(r'uri "([^"]*)"', body).group(1),
                                            re.search(r'retrieved_at (@[0-9TZ:-]+);', body).group(1))
    found = {}
    for match in re.finditer(r'pub fragment (\w+) in (\w+) \{.*?locator "([^"]*)";\s*text fr official """(.*?)""";\s*content_hash "sha256:([0-9a-f]+)";',
                             law, re.S):
        name, edition = match.group(1), match.group(2)
        source = editions[edition]
        found[name] = {"text": match.group(4), "hash": match.group(5), "source": source, "locator": match.group(3),
                       "label_fr": sources[source][0], "label_en": sources[source][1],
                       "uri": publications.get(edition, (None, None))[0],
                       "retrieved_at": publications.get(edition, (None, None))[1]}
    return found


def read_dump() -> dict[str, tuple[str, bytes]]:
    wanted = {row[2]: row[0] for row in DECREE_ARTICLES if row[4] == "dump"}
    found = {}
    with tarfile.open(DUMP, "r|gz") as tar:
        for member in tar:
            if not member.isfile():
                continue
            stem = Path(member.name).stem
            if stem in wanted and "/JORF/TEXT/" in member.name and "/article/" in member.name:
                found[stem] = (member.name, tar.extractfile(member).read())
                if len(found) == len(wanted):
                    break
    missing = set(wanted) - set(found)
    assert not missing, f"в дампе нет: {sorted(missing)}"
    return found


def write() -> int:
    revalo = fragment_texts()
    dump = read_dump()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, jorf, arti, num, kind, applies_from, phrase in DECREE_ARTICLES:
        if kind == "dump":
            path, raw = dump[arti]
            xml = raw.decode("utf-8")
            origin = {"origin_kind": "dump", "dump_path": path}
            version_debut = tag(xml, "DATE_DEBUT")
        else:
            file = MIRROR_2026 / f"{arti}.xml"
            raw = file.read_bytes()
            xml = raw.decode("utf-8")
            origin = {"origin_kind": "LEGI_20260331-215650", "mirror_path": str(file.relative_to(ROOT))}
            version_debut = tag(xml, "DATE_DEBUT")
            assert version_debut == applies_from, (name, version_debut)
        assert tag(xml, "NUM") == num, (name, tag(xml, "NUM"))
        text = f"Article {num}\n" + "\n".join(alineas(xml)) + "\n"
        assert phrase is None or phrase in text, (name, phrase)
        (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
        ctx = context(xml, jorf)
        rows.append({"name": name, "kind": "decree", "jorftext": jorf, "article_id": arti, "article": num,
                     **ctx, "etat": tag(xml, "ETAT") or "VIGUEUR", "version_debut": version_debut, "applies_from": applies_from,
                     **origin, "xml_sha256": hashlib.sha256(raw).hexdigest(),
                     "text": f"sources/montant/{name}.txt",
                     "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    for frag, source_txt, name in COEFFICIENTS:
        info = revalo[frag]
        text, fragment_hash = info["text"], info["hash"]
        source = (REVALO / "sources" / source_txt).read_text(encoding="utf-8")
        assert text in source, f"{frag}: абзац не найден в {source_txt}"
        assert hashlib.sha256(text.encode("utf-8")).hexdigest() == fragment_hash, frag
        (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
        rows.append({"name": name, "kind": "guidance", "origin_fragment": f"fr.css.revalorisation::{frag}",
                     "origin_text": f"corpus/laws/fr/revalorisation/sources/{source_txt}",
                     "origin_text_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                     "source": info["source"], "locator": info["locator"], "label_fr": info["label_fr"],
                     "label_en": info["label_en"], "uri": info["uri"], "retrieved_at": info["retrieved_at"],
                     "text": f"sources/montant/{name}.txt",
                     "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    record = json.loads((REVALO / f"sources/{LOI_NAME}.json").read_text(encoding="utf-8"))
    raw = (REVALO / f"sources/{LOI_NAME}.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["text_sha256"], "текст revalorisation расходится с его учётом"
    (OUT / f"{LOI_NAME}.txt").write_bytes(raw)
    rows.append({**record, "name": LOI_NAME, "kind": "statute", "start_date": "2022-07-01",
                 "origin": "fr.css.revalorisation/sources/loi-2022-1158-art9.txt",
                 "text": f"sources/montant/{LOI_NAME}.txt"})
    manifest = {"dump": DUMP_URL, "retrieved_at": "2026-10-08",
                "scope": "Métropole et DOM (hors Mayotte); montant forfaitaire de la prime d'activité pour une personne seule (L. 842-3)",
                "texts": rows}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"закреплено {len(rows)} → {OUT.relative_to(ROOT)}")
    return 0


def check() -> int:
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    bad = []
    for row in manifest["texts"]:
        data = (PKG / row["text"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != row["text_sha256"]:
            bad.append(row["name"])
    revalo = fragment_texts()
    for row in manifest["texts"]:
        if row["kind"] == "guidance":
            frag = row["origin_fragment"].split("::")[1]
            if (PKG / row["text"]).read_text(encoding="utf-8") != revalo[frag]["text"]:
                bad.append(row["name"] + " (расходится с фрагментом revalorisation)")
    print("OK" if not bad else f"расхождение: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sys.exit(write() if args.write else check())
