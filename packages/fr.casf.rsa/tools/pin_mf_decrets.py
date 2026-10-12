#!/usr/bin/env python3
"""Закрепить статьи 1 декретов о ревалоризации montant forfaitaire RSA (метрополия).

Источник — тот же глобальный дамп LEGI DILA, что у кодифицированных статей пакета
(`build_sources.py`: Freemium_legi_global_20250713-140000). Из дампа берётся XML
статьи 1 каждого декрета (текст вне Майотты, ст. 2 исключает Майотту), пишется
`sources/decrets-mf/<декрет>.txt` (текст статьи как в CONTENU) и учёт
`sources/decrets-mf/manifest.json` (идентификаторы LEGI/JORF, путь в дампе,
sha256 XML и текста, дата начала версии).

Закреплено для пакета: `tools/build_sources.py` вносит эти тексты в
01-sources.law (источники DECRET_2020_490 … DECRET_2025_293, публикации,
фрагменты DEC<год>_<номер>_ART1), а `tools/build_bareme.py` берёт из них суммы
параметра MontantForfaitaireDecret («figure must stand in the anchor text»).
Заголовок, дата и NOR декрета — из версии текста JORFTEXT дампа (`texte/version`),
чтобы подписи источников не писались по памяти.

Мост 01.07.2022: ревалоризация +4 % (коэффициент 1,04) — законом 2022-1158
(ст. 9), не декретом, поэтому окно 2022-07…2023-03 в ряду декретов пусто. Статья 9
закреплена здесь же (`sources/decrets-mf/loi-2022-1158-art9.txt`, запись
`lois` манифеста): байты те же, что закрепил пакет `fr.css.revalorisation`
(`tools/pin_loi_2022_1158.py`, тот же дамп LEGI), — их хэш сверяется при
`--loi` и при `--check`; в окне сумма строится правилом пакета как сумма
декрета 2022-699 × 1,04 с округлением (прочтение, текст не задаёт округление),
поэтому окно записано в `bridges`, а не в пробелы.

  python3 corpus/laws/fr/rsa/tools/pin_mf_decrets.py --write   # читает дамп (~5 мин)
  python3 corpus/laws/fr/rsa/tools/pin_mf_decrets.py --loi     # статья 9: из закрепления revalorisation, без дампа
  python3 corpus/laws/fr/rsa/tools/pin_mf_decrets.py --check   # сверяет тексты с учётом
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
PKG = ROOT / "corpus/laws/fr/rsa"
OUT = PKG / "sources/decrets-mf"
DUMP = ROOT / ".scratch/legi/Freemium_legi_global_20250713-140000.tar.gz"
DUMP_URL = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/Freemium_legi_global_20250713-140000.tar.gz"

#: декрет → (JORFTEXT, LEGIARTI статьи 1, месяц начала действия суммы)
DECRETS = {
    "decret-2020-490": ("JORFTEXT000041835196", "LEGIARTI000041838360", "2020-04"),
    "decret-2021-530": ("JORFTEXT000043459557", "LEGIARTI000043462070", "2021-04"),
    "decret-2022-699": ("JORFTEXT000045668694", "LEGIARTI000045673958", "2022-04"),
    "decret-2023-340": ("JORFTEXT000047521562", "LEGIARTI000047521835", "2023-04"),
    "decret-2024-396": ("JORFTEXT000049486510", "LEGIARTI000049488586", "2024-04"),
    "decret-2025-293": ("JORFTEXT000051393086", "LEGIARTI000051395304", "2025-04"),
}
#: Окно, которое декреты не покрывают: сумма с 01.07.2022 по 31.03.2023 строится из
#: суммы декрета-основания по статье 9 закона (правило MfBaseLoi2022 под прочтением).
BRIDGES = [{"from": "2022-07", "to": "2023-03", "law": "loi-2022-1158-art9",
            "base_decret": "decret-2022-699", "start_date": "2022-07-01",
            "why": "loi n° 2022-1158 du 16 août 2022, art. 9 : coefficient 1,04 au 1er juillet 2022 sur la somme du décret 2022-699"}]

#: Закон: каталог в пакете `fr.css.revalorisation`, откуда берутся уже закреплённые байты.
LOI_SRC = ROOT / "corpus/laws/fr/revalorisation/sources"
LOI_NAME = "loi-2022-1158-art9"


def contenu(xml: str) -> str:
    body = re.search(r"<CONTENU>(.*?)</CONTENU>", xml, re.S).group(1)
    body = re.sub(r"<br\s*/?>|</p>", "\n", body)
    body = html.unescape(re.sub(r"<[^>]+>", "", body))
    return "\n".join(line.strip() for line in body.splitlines() if line.strip()) + "\n"


def write() -> int:
    wanted = {arti: name for name, (_, arti, _) in DECRETS.items()}
    texts = {jorf: name for name, (jorf, _, _) in DECRETS.items()}
    found, found_texts = {}, {}
    with tarfile.open(DUMP, "r|gz") as tar:
        for member in tar:
            stem = Path(member.name).stem
            if not member.isfile():
                continue
            if stem in wanted:
                found[stem] = (member.name, tar.extractfile(member).read())
            elif "/texte/version/" in member.name:
                owner = re.search(r"/(JORFTEXT\d{12})/texte/version/", member.name)
                if owner and owner.group(1) in texts:
                    found_texts[owner.group(1)] = (member.name, tar.extractfile(member).read())
            if len(found) == len(wanted) and len(found_texts) == len(texts):
                break
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, (jorf, arti, start) in DECRETS.items():
        path, raw = found[arti]
        xml = raw.decode("utf-8")
        text = contenu(xml)
        (OUT / f"{name}.txt").write_text(text, encoding="utf-8")
        head = found_texts[jorf][1].decode("utf-8")
        tag = lambda t: re.search(rf"<{t}>([^<]*)", head).group(1).strip()
        rows.append({"decret": name, "jorftext": jorf, "legiarti": arti, "article": "1",
                     "start_month": start,
                     "titre": html.unescape(tag("TITREFULL")), "nor": tag("NOR"),
                     "date_texte": tag("DATE_TEXTE"), "date_publi": tag("DATE_PUBLI"),
                     "texte_dump_path": found_texts[jorf][0],
                     "texte_xml_sha256": hashlib.sha256(found_texts[jorf][1]).hexdigest(),
                     "version_debut": re.search(r"<DATE_DEBUT>([^<]*)", xml).group(1),
                     "etat": re.search(r"<ETAT>([^<]*)", xml).group(1),
                     "dump_path": path, "xml_sha256": hashlib.sha256(raw).hexdigest(),
                     "text": f"sources/decrets-mf/{name}.txt",
                     "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()})
    previous = json.loads((OUT / "manifest.json").read_text(encoding="utf-8")) if (OUT / "manifest.json").exists() else {}
    manifest = {"dump": DUMP_URL, "retrieved_at": "2026-10-08", "scope": "Métropole et DOM hors Mayotte (art. 2)",
                "decrets": rows, "bridges": BRIDGES, "lois": previous.get("lois", [])}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"закреплено {len(rows)} → {OUT.relative_to(ROOT)}")
    return 0


def pin_loi() -> int:
    """Статья 9 закона 2022-1158: байты и учёт — из закрепления пакета `fr.css.revalorisation`."""
    record = json.loads((LOI_SRC / f"{LOI_NAME}.json").read_text(encoding="utf-8"))
    raw = (LOI_SRC / f"{LOI_NAME}.txt").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["text_sha256"], "текст revalorisation расходится с его учётом"
    (OUT / f"{LOI_NAME}.txt").write_bytes(raw)
    row = {"loi": LOI_NAME, "number": "2022-1158", "article": "9",
           "start_date": "2022-07-01", "origin": "fr.css.revalorisation/sources/loi-2022-1158-art9.txt", **record}
    row["text"] = f"sources/decrets-mf/{LOI_NAME}.txt"
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    manifest["bridges"] = BRIDGES
    manifest.pop("gaps", None)
    manifest["lois"] = [row]
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"закреплено {LOI_NAME} → {(OUT / (LOI_NAME + '.txt')).relative_to(ROOT)}")
    return 0


def check() -> int:
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    bad = [row["decret"] for row in manifest["decrets"]
           if hashlib.sha256((PKG / row["text"]).read_bytes()).hexdigest() != row["text_sha256"]]
    bad += [row["loi"] for row in manifest.get("lois", [])
            if hashlib.sha256((PKG / row["text"]).read_bytes()).hexdigest() != row["text_sha256"]]
    print("OK" if not bad else f"расхождение: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--loi", action="store_true", help="статья 9 закона 2022-1158 из закрепления revalorisation (без дампа)")
    args = parser.parse_args()
    sys.exit(write() if args.write else pin_loi() if args.loi else check())
