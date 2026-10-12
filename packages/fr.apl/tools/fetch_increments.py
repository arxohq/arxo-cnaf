#!/usr/bin/env python3
"""Инкрементальные дампы DILA LEGI: обойти ВСЕ и оставить файлы охвата.

ЗАЧЕМ ОТДЕЛЬНЫЙ ИНСТРУМЕНТ. Глобальный дамп — снимок на дату (наш от 13 июля
2025 года, 14:00). Всё, что случилось позже, живёт в ЕЖЕДНЕВНЫХ инкрементах, и
сверка версий без них отвечает о прошлом: так версия L. 822-2 от 1 июля 2026
года (закон о финансах 2026 года) в глобальном дампе отсутствует вовсе.

ПОЧЕМУ СПИСОК ЧИТАЕТСЯ ЗАНОВО, А НЕ ХРАНИТСЯ. Снимок каталога устаревает С ОБОИХ
КОНЦОВ. Замер 14.09.2026: сохранённый 13.09 список из 427 архивов не содержал ни
инкремента ВЕЧЕРА того дня, когда снят глобальный дамп (`LEGI_20250713-205013`:
дамп снят в 14:00, инкремент — в 20:50, и между ними помещаются изменения), ни
инкрементов, опубликованных после снятия списка. Поэтому каталог читается при
каждом запуске, а `scanned.json` держит уже обойдённые архивы.

Из каждого архива сохраняются только файлы версий трёх источников пакета — по
пути, без чтения содержимого: каталог текста несёт его идентификатор.

ГЛОБАЛЬНЫЕ ДАМПЫ ТОЖЕ СВЕРЯЮТСЯ. В каталоге LEGI их ровно один, и он
ЗАМЕНЯЕМЫЙ: DILA публикует новый снимок и подчищает старые инкременты. Поэтому
`--check` отвечает и на три вопроса о дампе: тот ли файл ещё опубликован, того
ли он размера и не появился ли снимок НОВЕЕ закреплённого. Появившийся новый
дамп — не беда сам по себе, но он означает, что цепочка «наш снимок + все
инкременты» перестала быть единственной возможной, а старые инкременты могут
исчезнуть из каталога; молча этого знать нельзя.

  fetch_increments.py --into <каталог>           — обойти недостающие
  fetch_increments.py --into <каталог> --check   — сколько их и что с дампом
  fetch_increments.py --into <каталог> --check --local <дамп> — плюс sha256
                                                   локальной копии дампа
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
import hashlib
import json
import re
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

BASE = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
#: Те же три источника, что закрепляет пакет — ДАННЫЕ (волна 0, W0-04):
#: `sources/source-manifest.json` (`texts`): арретэ, ордонанс о CRDS, кодекс.
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "corpus/tools/sources"))
from fr_manifest import load_package as _load_manifest  # noqa: E402

TEXTS = tuple(_load_manifest(Path(__file__).resolve().parents[1])["texts"])
ARCHIVE = re.compile(r"(LEGI_\d{8}-\d{6}\.tar\.gz)")
GLOBAL = re.compile(r"(\w*legi_global_(\d{8})-\d{6}\.tar\.gz)", re.IGNORECASE)
ACCOUNTING = Path(__file__).resolve().parents[1] / "sources/fr-apl/articles.json"


def listing() -> tuple[list[str], list[tuple[str, str]]]:
    """Инкременты и глобальные дампы каталога — одним чтением."""
    with urllib.request.urlopen(BASE, timeout=120) as response:
        page = response.read().decode("utf-8", "replace")
    dumps = sorted({(name, day) for name, day in GLOBAL.findall(page)})
    return sorted(set(ARCHIVE.findall(page))), dumps


def dump_report(dumps: list[tuple[str, str]], local: Path | None) -> list[str]:
    """Сверка ЗАКРЕПЛЁННОГО дампа с каталогом: тот ли, того ли размера, не новее ли."""
    book = json.loads(ACCOUNTING.read_text(encoding="utf-8"))
    pinned = book["dump"]
    name = pinned["url"].rsplit("/", 1)[-1]
    problems: list[str] = []
    published = {item[0] for item in dumps}
    print(f"глобальных дампов в каталоге: {len(dumps)}; закреплён {name}")
    if name not in published:
        problems.append(f"закреплённый дамп {name} в каталоге ОТСУТСТВУЕТ "
                        f"(опубликованы: {', '.join(sorted(published)) or 'ни одного'})")
    else:
        request = urllib.request.Request(BASE + name, method="HEAD")
        with urllib.request.urlopen(request, timeout=120) as response:
            size = int(response.headers.get("Content-Length", "0"))
        if size != pinned["bytes"]:
            problems.append(f"{name}: в каталоге {size} байт, закреплено {pinned['bytes']} — "
                            f"файл ПОДМЕНЁН под тем же именем")
        else:
            print(f"   размер совпал с закреплённым: {size} байт")
    day = name.rsplit("_", 1)[-1][:8]
    newer = [item for item in dumps if item[1] > day]
    for item in newer:
        problems.append(f"опубликован дамп НОВЕЕ закреплённого: {item[0]} "
                        f"(закреплён снимок {day})")
    if local is not None:
        if not local.exists():
            problems.append(f"локальной копии дампа нет: {local}")
        else:
            digest = hashlib.sha256()
            with local.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1 << 22), b""):
                    digest.update(chunk)
            if digest.hexdigest() != pinned["sha256"]:
                problems.append(f"локальная копия {local} расходится с закреплённым sha256")
            else:
                print(f"   sha256 локальной копии совпал: {pinned['sha256'][:16]}…")
    return problems


def take(name: str, into: Path) -> int:
    """Скачать архив, оставить файлы охвата, вернуть их число."""
    kept = 0
    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as handle:
        path = Path(handle.name)
    try:
        for attempt in (1, 2, 3):
            try:
                urllib.request.urlretrieve(BASE + name, path)
                break
            except Exception:          # noqa: BLE001 — сеть, повтор
                if attempt == 3:
                    raise
                time.sleep(3)
        with tarfile.open(path, "r|gz") as archive:
            for member in archive:
                if not member.isfile() or not member.name.endswith(".xml"):
                    continue
                if not any(text in member.name for text in TEXTS):
                    continue
                target = into / name.split(".")[0] / member.name.replace("/", "_")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(member).read())
                kept += 1
    finally:
        path.unlink(missing_ok=True)
    return kept


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--into", type=Path, required=True,
                        help="каталог кэша (в нём же лежит scanned.json)")
    parser.add_argument("--check", action="store_true",
                        help="не скачивать: сказать, сколько архивов не обойдено")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--local", type=Path,
                        help="локальная копия глобального дампа: сверить sha256")
    args = parser.parse_args()
    args.into.mkdir(parents=True, exist_ok=True)
    marker = args.into / "scanned.json"
    scanned = json.loads(marker.read_text(encoding="utf-8")) if marker.exists() else {}
    names, dumps = listing()
    todo = [name for name in names if name not in scanned]
    print(f"в каталоге DILA {len(names)} инкрементов, не обойдено {len(todo)}")
    if args.check:
        for name in todo:
            print("   ", name)
        problems = dump_report(dumps, args.local)
        for problem in problems:
            print("РАСХОЖДЕНИЕ:", problem)
        return 1 if todo or problems else 0
    with futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for index, (name, kept) in enumerate(
                zip(todo, pool.map(lambda one: take(one, args.into), todo)), start=1):
            scanned[name] = kept
            if kept:
                print(f"  [{index}/{len(todo)}] {name}: файлов охвата {kept}", flush=True)
            if index % 20 == 0:
                marker.write_text(json.dumps(scanned), encoding="utf-8")
    marker.write_text(json.dumps(scanned), encoding="utf-8")
    print(f"обойдено архивов {len(scanned)}, файлов охвата всего {sum(scanned.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
