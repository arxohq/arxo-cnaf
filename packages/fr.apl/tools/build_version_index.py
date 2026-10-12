#!/usr/bin/env python3
"""Индекс ВСЕХ версий статей трёх источников пакета — вход сверки закрепления.

Сверка `audit_versions.py` без индекса отвечает на вопрос «та ли версия стоит
среди ЗАКРЕПЛЁННЫХ» и не может ответить на второй, столь же важный: «нет ли
версии ПОЗЖЕ, которую не закрепили вовсе». Второй вопрос требует полного
перечня версий, то есть самих дампов DILA.

Индекс не кладётся в пакет: это не источник права, а вспомогательный перечень
на 1,1 ГБ входных данных. Он строится в рабочий каталог и передаётся сверке
ключом `--index`.

  build_version_index.py --dump <legi_global.tar.gz> [--increments <каталог>]
                         --out <version-index.json>

Инкременты (каталог с распакованными `LEGIARTI*.xml` любой глубины) ВЫТЕСНЯЮТ
сведения глобального дампа: в снимке у версии, закрытой позже, `DATE_FIN`
остаётся `2999-01-01`, и без инкремента она выглядит действующей.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "corpus/tools/sources/fetch"))
#: Дату применимости («prestations dues à compter du …») разбирает ТОТ ЖЕ код,
#: что и инструмент закрепления: две формулы этой даты означали бы, что сверка
#: и барем расходятся молча.
from fetch_fr_apl_texts import applies_from  # noqa: E402

#: Идентификаторы текстов — ДАННЫЕ (волна 0, W0-04):
#: `sources/source-manifest.json` (`texts`): арретэ, ордонанс о CRDS, кодекс.
sys.path.insert(0, str(ROOT / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

TEXTS = _load_manifest(Path(__file__).resolve().parents[1])["texts"]
OPEN_END = "2999-01-01"


#: Акт статьи — cid её КОНТЕКСТА, а не первое вхождение идентификатора текста.
#: Замер 14.09.2026: D. 823-16 ссылается на арретэ (`<LIEN cidtexte=…>`), и по
#: «первому вхождению» десять статей кодекса легли в индекс как статьи арретэ —
#: у акта стало 64 статьи вместо 52, а второй вопрос сверки по этим статьям
#: ТИХО не задавался.
CONTEXT_CID = re.compile(r"<CONTEXTE>\s*<TEXTE[^>]*?cid=\"([A-Z0-9]+)\"")


def row_of(data: str, legi_id: str, source: str) -> tuple[str, str, dict] | None:
    context = CONTEXT_CID.search(data)
    act = TEXTS.get(context.group(1)) if context else None
    number = re.search(r"<NUM>([^<]*)</NUM>", data)
    begin = re.search(r"<DATE_DEBUT>([^<]*)</DATE_DEBUT>", data)
    if act is None or number is None or begin is None:
        return None
    end = re.search(r"<DATE_FIN>([^<]*)</DATE_FIN>", data)
    state = re.search(r"<ETAT>([^<]*)</ETAT>", data)
    nota = re.search(r"<NOTA>(.*?)</NOTA>", data, re.S)
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", nota.group(1))).split()) if nota else ""
    return act, number.group(1), {
        "id": legi_id, "debut": begin.group(1),
        "fin": end.group(1) if end else OPEN_END,
        # Дата применимости — та, по которой живёт барем; у арретэ она бывает
        # РАНЬШЕ или ПОЗЖЕ начала окна версии, и сверка обязана считать по ней.
        "applies_from": applies_from(text, begin.group(1)),
        "etat": state.group(1) if state else "", "source": source}


def add(index: dict, act: str, number: str, row: dict) -> None:
    rows = index.setdefault(act, {}).setdefault(number, [])
    known = next((r for r in rows if r["id"] == row["id"]), None)
    if known is None:
        rows.append(row)
    else:
        known.update(row)   # инкремент знает позже


def check_scope(index: dict) -> list[str]:
    """Каждая статья закреплённого охвата обязана быть в индексе СВОЕГО акта.

    Без этой проверки пробел индекса не виден: сверка просто не задаёт по такой
    статье второй вопрос и остаётся зелёной.
    """
    accounting = Path(__file__).resolve().parents[1] / "sources/fr-apl/articles.json"
    if not accounting.exists():
        return []
    book = json.loads(accounting.read_text(encoding="utf-8"))
    missing = []
    for edition in book["editions"]:
        document = edition["document"]
        act = ("cch" if document.startswith("cch")
               else "arrete" if document.startswith("arrete") else "ordonnance")
        for number in edition["scope"]:
            if number not in index.get(act, {}):
                missing.append(f"{act} ст. {number} — нет ни одной версии")
    return sorted(set(missing))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump", type=Path, help="глобальный дамп LEGI (tar.gz)")
    parser.add_argument("--increments", type=Path,
                        help="каталог с распакованными XML инкрементов")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    index: dict[str, dict[str, list[dict]]] = {}
    if args.dump is not None:
        with tarfile.open(args.dump, "r|gz") as archive:
            for member in archive:
                if not member.isfile() or not member.name.endswith(".xml"):
                    continue
                if not any(text in member.name for text in TEXTS):
                    continue
                data = archive.extractfile(member).read().decode("utf-8", "replace")
                parsed = row_of(data, member.name.split("/")[-1][:-4], "глобальный")
                if parsed is not None:
                    add(index, *parsed[:2], parsed[2])
    if args.increments is not None:
        for path in sorted(args.increments.glob("**/*.xml")):
            data = path.read_text(encoding="utf-8", errors="replace")
            parsed = row_of(data, path.name[:-4].split("_")[-1], path.parent.name)
            if parsed is not None:
                add(index, *parsed[:2], parsed[2])
    #: Провенанс самого перечня: чем он собран. Без этой строки «сверка по всем
    #: инкрементам» — обещание, а не свойство файла: по индексу не видно, сколько
    #: архивов в него вошло. Полноту доказывает `fetch_increments.py --check`
    #: (читает каталог DILA заново и краснеет, если хоть один не обойдён), а
    #: здесь записывается то, что фактически прочитано.
    meta = {
        "dump": str(args.dump) if args.dump else None,
        "increments_dir": str(args.increments) if args.increments else None,
        # ЧИСЛО ЧЕСТНОЕ, НО УЗКОЕ: считаются архивы, В КОТОРЫХ НАШЛИСЬ файлы
        # наших источников (у остальных каталога нет). Обойдено архивов больше:
        # 14.09.2026 — 430 обойдено, 255 с файлами. Полноту обхода доказывает
        # `fetch_increments.py --check`, а не это число.
        "increments_with_sources": (
            len([path for path in args.increments.iterdir() if path.is_dir()])
            if args.increments and args.increments.is_dir() else 0),
        "files_read": sum(len(rows) for articles in index.values()
                          for rows in articles.values()),
    }
    for articles in index.values():
        for rows in articles.values():
            # Порядок — ПО ПРИМЕНИМОСТИ: при равной дате побеждает версия,
            # вступившая в силу позже (арретэ от 16 августа 2022 года издано
            # позже арретэ от 29 июля, а применимость у них объявлена одна).
            rows.sort(key=lambda row: (row["applies_from"], row["debut"]))
    missing = check_scope(index)
    if missing:
        for line in missing:
            print("ПРОБЕЛ ИНДЕКСА:", line)
    args.out.write_text(json.dumps({"$meta": meta, **index}, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print("индекс записан:", args.out)
    print(f"  инкрементов с файлами источников: {meta['increments_with_sources']}")
    for act, articles in sorted(index.items()):
        print(f"  {act}: статей {len(articles)}, версий "
              f"{sum(len(r) for r in articles.values())}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
