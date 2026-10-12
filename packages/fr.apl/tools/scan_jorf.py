#!/usr/bin/env python3
"""Открытые данные DILA: акты ДРУГИХ собраний, трогающие источники пакета.

Инструмент писался для Journal officiel и остаётся при этом имени, но собрание
задаётся ключами: `--base` и `--prefix`. Так одним и тем же вопросом
проверяются JORF (акты, изменяющие наши источники) и, например, KALI
(коллективные договоры). Ответ для разных собраний имеет разный ВЕС: акт JORF
может изменить арретэ или кодекс, договор KALI — нет, он может лишь сослаться.
Отрицательный ответ по такому собранию — измеренный факт, а не допущение.

ЗАЧЕМ. LEGI — консолидация: она показывает, как текст выглядит ПОСЛЕ правки.
Если правка опубликована в Journal officiel, но ещё не консолидирована, LEGI о
ней молчит, и сверка версий по LEGI молчит вместе с ней. Ответ на «не отстаёт
ли наша картина от официальной публикации» даёт только JORF.

ЧТО ИЩЕТСЯ. В архивах JORF — записи текстов и их статей; акт, изменяющий наш
источник, называет его идентификатором в своих связях (`cidtexte="JORFTEXT…"`).
Поэтому скан идёт по СОДЕРЖИМОМУ: файл сохраняется, если в нём встречается
идентификатор арретэ, кодекса или ордонанса пакета.

  scan_jorf.py --into <кэш> [--limit N]   — обойти инкременты JORF
  scan_jorf.py --into <кэш> --report      — что нашлось: акты, даты, NOR
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import json
import re
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

BASE = "https://echanges.dila.gouv.fr/OPENDATA/JORF/"
#: Имя архива инкремента: префикс задаётся собранием (JORF_, KALI_, …).
#: Источники пакета: арретэ о расчёте аид, кодекс, ордонанс о CRDS.
SOURCES = (b"JORFTEXT000039160329", b"LEGITEXT000006074096", b"JORFTEXT000000190291")
#: Акты, ИЗМЕНИВШИЕ источник, ищутся наравне с ним. Решение Конституционного
#: совета цитирует не кодекс, а ЗАКОН, чья статья кодекс изменила: censure или
#: réserve d'interprétation по такому закону бьёт прямо в нашу норму, а по
#: идентификатору кодекса такое решение не найдётся.
AMENDING = {
    "loi-finances-2026": b"JORFTEXT000053508155",   # LOI 2026-103, ст. 179 → L. 822-2
}
def archive_pattern(prefix: str) -> re.Pattern:
    return re.compile(rf"({re.escape(prefix)}\d{{8}}-\d{{6}}\.tar\.gz)")


ARCHIVE = archive_pattern("JORF_")


def listing(base: str, prefix: str) -> list[str]:
    with urllib.request.urlopen(base, timeout=120) as response:
        page = response.read().decode("utf-8", "replace")
    return sorted(set(archive_pattern(prefix).findall(page)))


def take(name: str, into: Path, base: str = BASE,
         sources: tuple[bytes, ...] = SOURCES) -> int:
    kept = 0
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as handle:
        path = Path(handle.name)
    try:
        for attempt in (1, 2, 3):
            try:
                urllib.request.urlretrieve(base + name, path)
                break
            except Exception:            # noqa: BLE001 — сеть, повтор
                if attempt == 3:
                    raise
                time.sleep(3)
        with tarfile.open(path, "r|gz") as archive:
            for member in archive:
                if not member.isfile() or not member.name.endswith(".xml"):
                    continue
                data = archive.extractfile(member).read()
                if not any(source in data for source in sources):
                    continue
                target = into / name.split(".")[0] / member.name.replace("/", "_")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
                kept += 1
    finally:
        path.unlink(missing_ok=True)
    return kept


#: Наш арретэ: его собственные записи из отчёта исключаются — это он сам,
#: а не акт, его изменяющий.
OWN = "JORFTEXT000039160329"
PACKAGE = Path(__file__).resolve().parents[1]


def scope_patterns() -> dict[str, re.Pattern]:
    """Номера статей охвата кодекса в той форме, в какой их пишет журнал.

    Ссылка на кодекс сама по себе почти ничего не значит: кодекс строительства
    цитируют сотни актов. Значение имеет упоминание КОНКРЕТНОЙ статьи охвата —
    «article D. 823-16», «articles L. 822-2 et L. 822-3».
    """
    book = json.loads((PACKAGE / "sources/fr-apl/articles.json").read_text(encoding="utf-8"))
    numbers: set[str] = set()
    for edition in book["editions"]:
        if edition["document"].startswith("cch"):
            numbers |= set(edition["scope"])
    out = {}
    for number in sorted(numbers):
        letter, rest = number[0], number[1:]
        out[number] = re.compile(rf"{letter}\.?\s*{re.escape(rest)}(?![0-9-])")
    return out


def known_amendments() -> dict[str, str]:
    """Акты, изменявшие источники, ПО ЗАКРЕПЛЁННЫМ версиям: NOR → дата подписания.

    В каждой версии статьи LEGI перечисляет связи, и изменившие её акты
    названы `typelien="MODIFIE"` с их NOR и датой. Это картина КОНСОЛИДАЦИИ,
    и отчёт JORF сверяется именно с ней: акт, опубликованный в журнале, но не
    попавший сюда, — либо ещё не консолидирован, либо не трогает наш охват.
    """
    out: dict[str, str] = {}
    for path in (PACKAGE / "sources/fr-apl/legi").rglob("*.xml"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for lien in re.findall(r"<LIEN [^>]*typelien=\"MODIFIE\"[^>]*>", text):
            nor = re.search(r"nortexte=\"([^\"]*)\"", lien)
            day = re.search(r"datesignatexte=\"([^\"]*)\"", lien)
            if nor and nor.group(1):
                out[nor.group(1)] = day.group(1) if day else ""
    return out


def report(into: Path) -> int:
    """Отчёт: какие акты журнала трогают источники пакета и что из них учтено."""
    acts: dict[str, dict] = {}
    patterns = scope_patterns()
    own_records = 0
    for path in sorted(into.rglob("*.xml")):
        raw = path.read_bytes()
        text = raw.decode("utf-8", "replace")
        ident = re.search(r"<ID>(JORFTEXT\d+)</ID>", text)
        if ident is None:
            own_records += OWN.encode() in raw
            continue          # запись СТАТЬИ, а не текста: акт узнаётся по своей записи
        if ident.group(1) == OWN:
            own_records += 1
            continue
        nor = re.search(r"<NOR>([^<]*)</NOR>", text)
        signed = re.search(r"<DATE_TEXTE>([^<]*)</DATE_TEXTE>", text)
        published = re.search(r"<DATE_PUBLI>([^<]*)</DATE_PUBLI>", text)
        title = re.search(r"<TITREFULL>(.*?)</TITREFULL>", text, re.S)
        nature = re.search(r"<NATURE>([^<]*)</NATURE>", text)
        acts[ident.group(1)] = {
            "id": ident.group(1), "nor": nor.group(1) if nor else "",
            "signed": signed.group(1) if signed else "",
            "published": published.group(1) if published else "",
            "nature": nature.group(1) if nature else "",
            "title": " ".join(re.sub(r"<[^>]+>", " ", title.group(1)).split()) if title else "",
            "touches_arrete": OWN.encode() in raw,
            "articles": sorted(number for number, pattern in patterns.items()
                               if pattern.search(text)),
        }
    known = known_amendments()
    print(f"актов журнала, называющих источники пакета: {len(acts)}; "
          f"записей самого арретэ: {own_records}")
    print(f"актов-изменителей, известных консолидации (по закреплённым версиям): {len(known)}")
    on_arrete = sorted((act for act in acts.values() if act["touches_arrete"]),
                       key=lambda act: act["signed"] or "")
    print(f"\n=== называют НАШ АРРЕТЭ: {len(on_arrete)}")
    for act in on_arrete:
        mark = "учтён консолидацией" if act["nor"] in known else "НЕ значится изменителем"
        print(f"  {act['signed'] or '(без даты)'} опубл. {act['published'] or '-'} "
              f"{act['nor'] or '-':14s} [{mark}]")
        print(f"      {act['title'][:150]}")
    named = sorted((act for act in acts.values()
                    if not act["touches_arrete"] and act["articles"]),
                   key=lambda act: act["signed"] or "")
    print(f"\n=== называют СТАТЬЮ ОХВАТА кодекса: {len(named)}")
    for act in named:
        mark = "учтён консолидацией" if act["nor"] in known else "НЕ значится изменителем"
        print(f"  {act['signed'] or '(без даты)'} опубл. {act['published'] or '-'} "
              f"{act['nor'] or '-':14s} [{mark}] ст. {', '.join(act['articles'])}")
        print(f"      {act['title'][:150]}")
    other = [act for act in acts.values() if not act["touches_arrete"] and not act["articles"]]
    print(f"\n=== просто цитируют кодекс или ордонанс, не называя наших статей: {len(other)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--into", type=Path, required=True)
    parser.add_argument("--base", default=BASE, help="каталог собрания DILA")
    parser.add_argument("--prefix", default="JORF_", help="префикс имён инкрементов")
    parser.add_argument("--archive", help="обойти ОДИН названный архив (например, глобальный дамп)")
    parser.add_argument("--with-amending", action="store_true",
                        help="искать и акты, изменившие источники (см. AMENDING)")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--limit", type=int, default=0,
                        help="обойти только N самых свежих архивов")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    args.into.mkdir(parents=True, exist_ok=True)
    if args.report:
        return report(args.into)
    marker = args.into / "scanned.json"
    scanned = json.loads(marker.read_text(encoding="utf-8")) if marker.exists() else {}
    sources = SOURCES + (tuple(AMENDING.values()) if args.with_amending else ())
    if args.archive:
        names, todo = [args.archive], ([args.archive] if args.archive not in scanned else [])
    else:
        names = listing(args.base, args.prefix)
        todo = [name for name in names if name not in scanned]
        if args.limit:
            todo = todo[-args.limit:]
    print(f"в каталоге {args.base} архивов {len(names)}, к обходу {len(todo)}", flush=True)
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, (name, kept) in enumerate(
                zip(todo, pool.map(lambda one: take(one, args.into, args.base, sources), todo)),
                start=1):
            scanned[name] = kept
            if kept:
                print(f"  [{index}/{len(todo)}] {name}: файлов с нашими источниками {kept}",
                      flush=True)
            if index % 25 == 0:
                marker.write_text(json.dumps(scanned), encoding="utf-8")
    marker.write_text(json.dumps(scanned), encoding="utf-8")
    print(f"обойдено {len(scanned)}, найдено файлов {sum(scanned.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
