#!/usr/bin/env python3
"""Та ли версия статьи закреплена в редакции: окно версии против даты редакции.

ЗАЧЕМ. Охват (`SCOPE` инструмента закрепления) называет версии статей
`legi_id`-ами, набранными руками. Ошибка «взята версия не того года» проходит
`check`, `--check` закрепления и ворота закрепления: байты совпадают сами с
собой, хэши сходятся, фрагмент существует. Видно её только на исполнении — и не
отказом, а `MISSING_PARAMETER_VALUE` в месяце права, до которого никто не дошёл.
Замер 14.09.2026: ст. 18 (плафоны мензуальности) стояла версией 2020 года во
ВСЕХ трёх своих редакциях, включая октябрьскую 2025-го; окна её 48 параметров
кончались 1 августа 2022 года, и каждое дело сектора приобретения после июля
2022 года было `NON_EXECUTABLE`.

ЧТО ПРОВЕРЯЕТСЯ. Для каждой редакции берётся её `in_force` из `01-sources.law`;
среди ВСЕХ закреплённых версий этой статьи ищется применимая на дату редакции —
последняя, чья дата применимости `applies_from` не позже этой даты. В редакции
обязана стоять именно она.

Сравнение идёт по `applies_from`, а НЕ по окну действия версии: барем живёт по
дате применимости из NOTA, и она бывает РАНЬШЕ вступления версии в силу.
Так у ст. 18: версия в силе с 1 августа 2022 года применяется к престациям
с 1 июля 2022 года; так у D. 842-16: в силе с 1 сентября 2023 года,
применяется с 5 апреля 2023 года. Проверка по окну краснела бы на обеих.

Условие НЕОБХОДИМОЕ, а не достаточное: существование более поздней
НЕЗАКРЕПЛЁННОЙ версии этим не ловится (для этого нужен индекс всего дампа), но
именно устаревший пин даёт разрыв окон, и он ловится без дампа.

  audit_versions.py                    — отчёт по ЗАКРЕПЛЁННЫМ версиям
  audit_versions.py --dtd <legi_article.dtd> — плюс сверка самого РАЗБОРА:
                                         структура файлов и состояния статьи
  audit_versions.py --index <файл>     — плюс второй вопрос: нет ли версии
                                         ПОЗЖЕ, не закреплённой вовсе
Индекс строит `build_version_index.py` из дампов DILA; в пакете он не лежит
(1,1 ГБ входных данных, не источник права). Без `--index` сверка отвечает
только на первый вопрос и об этом говорит в отчёте.

СВЕРКА С DTD ЛЕГИФРАНСА (`--dtd`). На чтении XML стоит всё закрепление, а
предположения о нём до 14.09.2026 держались на опыте. Официальная DTD
(`https://echanges.dila.gouv.fr/OPENDATA/DTD_LEGIFRANCE/DTD_LEGIFRANCE_20181017.7z`,
sha256 054fc04638b756337837600bf0b86a27b96f54933aa1df2cb799b5be9734626a; внутри
`LEGIFRANCE_20181018_dtd/legi/legi_article.dtd`, sha256
c9b93b1f99c14226fbd25226d5b7a9d94cd58005355d95788c8ed6d923d09a56) говорит прямо:
`META_ARTICLE (NUM, ETAT, DATE_DEBUT, DATE_FIN, TYPE)` — это ЭЛЕМЕНТЫ, а не
атрибуты, а акт статьи называет `CONTEXTE/TEXTE@cid` (#REQUIRED). Оба
предположения пакета совпали с DTD; список состояний статьи читается ИЗ НЕЁ.

Сама DTD при этом УСТАРЕЛА: она датирована 17.10.2018 и объявляет десять
состояний, а в данных встречается одиннадцатое — `DEPLACE` (ст. L. 721-2
кодекса; в охват пакета не входит). Поэтому «состояние не объявлено DTD» —
находка, а не отказ: сверка её печатает и краснеет, чтобы решение принимал
человек.

ПОЛНОТА ИНДЕКСА — вопрос не глобального дампа, а ИНКРЕМЕНТОВ: снимок закрывает
день своего снятия, всё позднее живёт в ежедневных архивах. Их обходит
`fetch_increments.py`, и он читает каталог DILA ЗАНОВО при каждом запуске:
сохранённый список устаревает с обоих концов — не хватает и инкремента вечера
того дня, когда снят глобальный дамп, и всего, что вышло после снятия списка
(замер 14.09.2026: 427 в сохранённом списке против 430 в каталоге).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
ROOT = PACKAGE.parents[3]
ACCOUNTING = PACKAGE / "sources/fr-apl/articles.json"
SOURCES = PACKAGE / "01-sources.law"
sys.path.insert(0, str(ROOT / "corpus/tools/sources/sync"))
from sync_fr_apl_fragments import EDITION_OF  # noqa: E402

OPEN_END = "2999-01-01"

#: Состояния статьи, для которых сверка ЗНАЕТ, что делать с применимостью.
#: Остальные из закрытого списка DTD (ANNULE, DISJOINT, PERIME, TRANSFERE) у
#: статей охвата не встречались ни разу; появись такое — сверка обязана встать,
#: а не догадываться: «аннулирована» и «перенесена» — разные судьбы нормы.
HANDLED_STATES = {"VIGUEUR", "MODIFIE", "MODIFIE_MORT_NE", "ABROGE",
                  "VIGUEUR_DIFF", "ABROGE_DIFF"}


def dtd_states(path: Path) -> set[str]:
    """Закрытый список состояний статьи — ИЗ САМОЙ DTD Легифранса.

    Значения объявлены не перечислением атрибута, а КОММЕНТАРИЕМ к
    `<!ELEMENT ETAT (#PCDATA)>` («Les valeurs possibles sont : …»), поэтому
    список читается оттуда, а не переписывается сюда руками: переписанный он
    устарел бы молча, как устарела сама DTD (см. ниже).
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"Les valeurs possibles sont\s*:\s*([^@<]+)", text)
    if match is None:
        raise SystemExit(f"{path}: в DTD не найден список значений ETAT")
    return {value.strip() for value in match.group(1).split(",") if value.strip()}


def dtd_report(book: dict, index: dict, dtd: Path, legi: Path) -> list[str]:
    """Сверка предположений о разборе с DTD: структура файлов и состояния.

    На чтении XML стоит ВСЁ закрепление, и предположения были проверены
    только опытом. DTD говорит прямо: `META_ARTICLE (NUM, ETAT, DATE_DEBUT,
    DATE_FIN, TYPE)` — это ЭЛЕМЕНТЫ, а не атрибуты; акт статьи называет
    `CONTEXTE/TEXTE@cid` (#REQUIRED), и именно по нему определяется акт.
    """
    declared = dtd_states(dtd)
    problems: list[str] = []
    # 1. структура каждого ЗАКРЕПЛЁННОГО файла версии
    required = ("<NUM>", "<ETAT>", "<DATE_DEBUT>", "<DATE_FIN>", "<TYPE>")
    meta = re.compile(r"<META_ARTICLE>(.*?)</META_ARTICLE>", re.S)
    context = re.compile(r"<CONTEXTE>\s*<TEXTE[^>]*?cid=\"[A-Z0-9]+\"")
    seen_states: set[str] = set()
    files = sorted(legi.rglob("*.xml")) if legi.is_dir() else []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        block = meta.search(text)
        if block is None:
            problems.append(f"{path.name}: нет META_ARTICLE — DTD требует её в META_SPEC")
            continue
        order = [tag for tag in required if tag in block.group(1)]
        if order != list(required):
            problems.append(f"{path.name}: META_ARTICLE не несёт всех элементов "
                            f"DTD (NUM, ETAT, DATE_DEBUT, DATE_FIN, TYPE)")
        if context.search(text) is None:
            problems.append(f"{path.name}: нет CONTEXTE/TEXTE@cid — по нему определяется акт")
        state = re.search(r"<ETAT>([^<]*)</ETAT>", block.group(1))
        if state:
            seen_states.add(state.group(1))
    for state in sorted(seen_states - declared):
        problems.append(f"состояние {state} есть в закреплённых файлах, но НЕ объявлено DTD")
    for state in sorted(seen_states - HANDLED_STATES):
        problems.append(f"состояние {state} закреплённого файла сверка не умеет толковать")
    # 2. состояния ВСЕХ версий статей охвата
    for edition in book["editions"]:
        act = ACT_OF(edition["document"])
        for number in edition["scope"]:
            for row in index.get(act, {}).get(number, []):
                state = row.get("etat", "")
                if state not in declared:
                    problems.append(f"{act} ст. {number}: состояние {state!r} версии "
                                    f"{row['id']} НЕ объявлено DTD Легифранса")
                elif state not in HANDLED_STATES:
                    problems.append(f"{act} ст. {number}: состояние {state} версии "
                                    f"{row['id']} объявлено DTD, но сверка не знает, "
                                    f"как его толковать")
    print(f"DTD: состояний объявлено {len(declared)}, в закреплённых файлах "
          f"встречено {len(seen_states)} ({', '.join(sorted(seen_states))}), "
          f"файлов проверено {len(files)}")
    return problems

#: Названные исключения: (редакция, статья) → причина. Пин ПОЗЖЕ применимого —
#: над-претензия якоря, и допускается она только с причиной. С 14.09.2026 список
#: ПУСТ: прежнее исключение (D. 842-16 в редакции кодекса, собранной по 5 апреля
#: 2023 года, при применимости версии с 1 сентября) сняла не оговорка, а
#: перестройка — редакция кодекса стала ПОЛНЫМ состоянием охвата на дату, и у
#: 1 сентября 2023 года появилось своё состояние.
EXCEPTIONS: dict[tuple[str, str], str] = {}


def edition_starts() -> dict[str, str]:
    """Начало действия каждой редакции — из `in_force [@дата, …)`."""
    text = SOURCES.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for match in re.finditer(r"edition (\w+) of \w+ \{(.*?)\n\}", text, re.S):
        window = re.search(r"in_force \[@(\d{4}-\d\d-\d\d),", match.group(2))
        if window is not None:
            out[match.group(1)] = window.group(1)
    return out


def skipped_inside(book: dict, index: dict, starts: dict[str, str]) -> list[str]:
    """Версии внутри покрытого промежутка, не попавшие НИ В ОДНО состояние.

    Третий вопрос сверки, и он ловит то, чего не видят первые два. Первый
    сравнивает закреплённое с ЗАКРЕПЛЁННЫМ и потому слеп к версии, которой в
    учёте нет вовсе; второй смотрит только на ПОСЛЕДНЮЮ версию статьи. Версия
    в СЕРЕДИНЕ промежутка выпадает из обоих — а именно она рвёт барем.

    Замер 14.09.2026: так нашлись версии ст. 15 и 47 от 1 августа 2022 года
    (арретэ от 29 июля 2022 года, применимые к престациям с 1 июля). Без ст. 15
    в бареме зияла дыра с августа по декабрь 2022 года: окно январской версии
    кончалось 1 августа, а следующая закреплённая применялась лишь с 1 января
    2023 года, и дело тех месяцев было NON_EXECUTABLE.

    Промежуток акта считается от начала его ПЕРВОГО состояния: версии, кончившиеся
    раньше, к покрытию не относятся.
    """
    pinned: dict[tuple[str, str], set[str]] = {}
    for edition in book["editions"]:
        act = ACT_OF(edition["document"])
        for number, version in edition["versions"].items():
            pinned.setdefault((act, number), set()).add(version["legi_id"])
    out: list[str] = []
    for (act, number), ids in sorted(pinned.items()):
        start = starts.get(act)
        if start is None:
            continue
        run = applicable_run(index.get(act, {}).get(number, []))
        for position, row in enumerate(run):
            # Промежуток применимости версии: от её даты до даты следующей.
            until = run[position + 1]["applies_from"] if position + 1 < len(run) else None
            if until is not None and until <= start:
                continue        # применялась целиком до начала покрытия акта
            if row["id"] in ids:
                continue
            out.append(f"{act} ст. {number}: версия {row['id']} применяется "
                       f"с {row['applies_from']}"
                       + (f" по {until}" if until else " и далее")
                       + " — внутри покрытия, но НЕ закреплена")
    return out


def applicable_run(rows: list[dict]) -> list[dict]:
    """Версии в порядке ПРИМЕНИМОСТИ, без тех, что не применяются никогда.

    Сверка считает по дате применимости («prestations dues à compter du …»), а
    не по окну действия: барем живёт по первой, и она бывает и раньше, и позже
    второй. Версия, у которой преемница применяется не позже её самой, не
    применяется НИКОГДА — это либо перебивший её акт (арретэ от 16 августа
    2022 года против арретэ от 29 июля с той же датой применимости), либо
    состояние `MODIFIE_MORT_NE` (версия, не вступившая в силу вовсе).
    """
    # ПУСТОЕ ОКНО ДЕЙСТВИЯ ПОБЕЖДАЕТ ЛЮБУЮ NOTA. У ст. 46 арретэ есть версия
    # с окном [2022-08-01 .. 2022-07-01) — конец раньше начала: акт от 29 июля
    # 2022 года был вытеснен актом от 16 августа ДО того, как начал
    # действовать. Её NOTA по-прежнему объявляет применимость с 1 июля, и по
    # одной применимости она выглядела бы «последней применимой» — а значения
    # у них РАЗНЫЕ (36,40/9,36 против 37,67/9,69). Такая версия не применяется
    # никогда, и сверка её не спрашивает (измерено 14.09.2026).
    ordered = sorted((row for row in rows
                      if row.get("etat") != "MODIFIE_MORT_NE"
                      and row.get("fin", "9999-01-01") > row["debut"]),
                     key=lambda row: (row["applies_from"], row["debut"]))
    out: list[dict] = []
    for index, row in enumerate(ordered):
        following = ordered[index + 1] if index + 1 < len(ordered) else None
        if following is not None and following["applies_from"] <= row["applies_from"]:
            continue
        out.append(row)
    return out


def later_unpinned(book: dict, index: dict) -> list[str]:
    """Статьи охвата, у которых ПОСЛЕДНЯЯ версия источника не закреплена.

    Именно этот вопрос нашёл L. 442-2-1: её версия от 31 декабря 2023 года
    лежала в том же глобальном дампе, а закреплена была версия 2019 года —
    и обе редакции кодекса открыты, так что дело 2025 года читало снятый текст.
    """
    pinned = {version["legi_id"]
              for edition in book["editions"]
              for version in edition["versions"].values()}
    out: set[str] = set()
    for edition_book in book["editions"]:
        act = ACT_OF(edition_book["document"])
        for number in edition_book["scope"]:
            run = applicable_run(index.get(act, {}).get(number, []))
            if not run or run[-1]["id"] in pinned:
                continue
            last = run[-1]
            out.add(f"{act} ст. {number}: последняя ПО ПРИМЕНИМОСТИ версия "
                    f"{last['id']} (применяется с {last['applies_from']}, "
                    f"в силе с {last['debut']}, {last['source']}) НЕ закреплена")
    return sorted(out)


#: Документ → акт. Список ЯВНЫЙ, и это не педантизм: пока неизвестный документ
#: молча попадал в «ordonnance», добавленный другой сессией `cgct-lo6414-1.txt`
#: (кодекс территориальных коллективностей, ст. LO 6414-1) сдвинул начало
#: покрытия ордонанса на 2007 год — и третий вопрос выдал СЕМЬ мнимых находок о
#: незакреплённых версиях ст. 14 и 19 ордонанса 2004–2019 годов (измерено
#: 14.09.2026). Неизвестный префикс теперь называется прямо, а не подшивается
#: к чужому акту.
ACT_PREFIXES = (("cch", "cch"), ("arrete", "arrete"), ("ordonnance", "ordonnance"),
                ("decret-2025-1401", "decret_2025_1401"),
                ("decret-2021-1750", "decret_2021_1750"), ("cgct", "cgct"))


def ACT_OF(document: str) -> str:
    for prefix, act in ACT_PREFIXES:
        if document.startswith(prefix):
            return act
    raise SystemExit(f"сверка не знает акта документа {document!r}: "
                     f"добавьте его в ACT_PREFIXES — молча подшивать к чужому "
                     f"акту нельзя, это сдвигает начало покрытия")


def butting(starts: dict[str, str]) -> list[str]:
    """Окна состояний одного акта обязаны идти ВСТЫК: без разрывов и нахлёстов.

    Окно редакции в этом пакете — промежуток ПРИМЕНИМОСТИ, а не действия
    версий: состояние октября 2025 года открывается 1 октября, хотя его версии
    вступили в силу 10 сентября. Сверка считает по той же оси.

    Решение владельца 14.09.2026: редакция — полное состояние охвата на дату.
    Разрыв между состояниями означает месяц права, в котором не действует ни
    одна редакция акта, и все нормы с якорями только в нём мертвы (E-0095);
    нахлёст означает две действующие редакции одного акта сразу. Ни то, ни
    другое не видно ни `check`, ни воротам закрепления — только здесь.
    """
    text = SOURCES.read_text(encoding="utf-8")
    windows: dict[str, list[tuple[str, str, str]]] = {}
    for match in re.finditer(r"edition (\w+) of (\w+) \{(.*?)\n\}", text, re.S):
        span = re.search(r"in_force \[@(\d{4}-\d\d-\d\d), (@\d{4}-\d\d-\d\d|infinity)\)",
                         match.group(3))
        if span is None:
            continue
        windows.setdefault(match.group(2), []).append(
            (span.group(1), span.group(2).lstrip("@"), match.group(1)))
    problems = []
    for act, rows in windows.items():
        rows.sort()
        for (start, end, name), (next_start, _, next_name) in zip(rows, rows[1:]):
            if end == "infinity":
                problems.append(f"{act}: {name} объявлена бессрочной, но за ней идёт {next_name}")
            elif end != next_start:
                kind = "разрыв" if end < next_start else "нахлёст"
                problems.append(f"{act}: {kind} между {name} (по {end}) и {next_name} (с {next_start})")
        if rows and rows[-1][1] != "infinity":
            problems.append(f"{act}: последнее состояние {rows[-1][2]} закрыто {rows[-1][1]} — "
                            f"у действующего акта последнее окно открыто")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dtd", type=Path,
                        help="legi_article.dtd Легифранса: сверить разбор и состояния")
    parser.add_argument("--index", type=Path,
                        help="перечень версий из дампов (build_version_index.py)")
    args = parser.parse_args()
    book = json.loads(ACCOUNTING.read_text(encoding="utf-8"))
    starts = edition_starts()
    #: Полный перечень версий: с ним первый вопрос сравнивает закреплённое не с
    #: закреплённым, а со ВСЕМИ известными версиями — иначе он слеп к той,
    #: которой в учёте нет вовсе (так пропускались версии ст. 15 и 47 от
    #: 1 августа 2022 года; измерено 14.09.2026).
    full = json.loads(args.index.read_text(encoding="utf-8")) if args.index else {}
    # Все закреплённые версии статьи, по акту: номер статьи «19» есть и у арретэ,
    # и у ордонанса о CRDS, и смешивать их нельзя (тот же класс ошибки, что в
    # `windows()` сборщика барема).
    known: dict[tuple[str, str], list[dict]] = {}
    for edition_book in book["editions"]:
        act = edition_book["document"].split("-")[0].split(".")[0]
        for number, version in edition_book["versions"].items():
            rows = known.setdefault((act, number), [])
            if all(row["legi_id"] != version["legi_id"] for row in rows):
                rows.append(version)
    for rows in known.values():
        # При равной дате применимости побеждает позже вступившая в силу версия:
        # арретэ от 16 августа 2022 года издано позже арретэ от 29 июля, а
        # применимость у них объявлена одна (см. README, ст. 46).
        rows.sort(key=lambda row: (row["applies_from"], row["in_force_from"]))
    problems: list[str] = []
    declared: list[str] = []
    checked = 0
    for edition_book in book["editions"]:
        edition = EDITION_OF[edition_book["document"]]
        act = edition_book["document"].split("-")[0].split(".")[0]
        start = starts.get(edition)
        if start is None:
            problems.append(f"{edition}: в 01-sources.law нет редакции с in_force")
            continue
        for number, version in edition_book["versions"].items():
            checked += 1
            catalogue = applicable_run(full.get(act, {}).get(number, [])) or known[(act, number)]
            applicable = [row for row in catalogue if row["applies_from"] <= start]
            if not applicable:
                continue
            want = applicable[-1]
            if want.get("legi_id", want.get("id")) == version["legi_id"]:
                continue
            reason = EXCEPTIONS.get((edition, number))
            if reason is not None:
                declared.append(f"{edition}: ст. {number} — {reason}")
                continue
            problems.append(
                f"{edition} (с {start}): ст. {number} закреплена версией "
                f"{version['legi_id']} (применяется с {version['applies_from']}), "
                f"а применима {want.get('legi_id', want.get('id'))} "
                f"(с {want['applies_from']})")
    problems += butting(starts)
    if args.dtd is not None:
        problems += dtd_report(book, json.loads(args.index.read_text(encoding="utf-8"))
                               if args.index else {}, args.dtd,
                               ACCOUNTING.parent / "legi")
    unpinned: list[str] = []
    skipped: list[str] = []
    if args.index is not None:
        index = json.loads(args.index.read_text(encoding="utf-8"))
        stamp = index.pop("$meta", None)
        if stamp is not None:
            count = stamp.get("increments_with_sources", stamp.get("increments_read", 0))
            print(f"перечень версий: инкрементов С ФАЙЛАМИ источников {count}, "
                  f"файлов версий {stamp['files_read']}; сколько архивов ОБОЙДЕНО "
                  f"и не осталось ли необойденных — отвечает fetch_increments.py --check")
        unpinned = later_unpinned(book, index)
        # Начало покрытия акта — левая граница его первого состояния.
        act_starts: dict[str, str] = {}
        for edition_book in book["editions"]:
            act = ACT_OF(edition_book["document"])
            start = starts.get(EDITION_OF[edition_book["document"]])
            if start is not None:
                act_starts[act] = min(act_starts.get(act, "9999-99-99"), start)
        skipped = skipped_inside(book, index, act_starts)
        problems += unpinned + skipped
    for problem in problems:
        print(problem)
    for item in declared:
        print(f"названное исключение — {item}")
    print(f"audit_versions: редакций {len(book['editions'])}, "
          f"закреплённых версий {checked}, расхождений {len(problems)}, "
          f"названных исключений {len(declared)}"
          + (f", незакреплённых поздних версий {len(unpinned)}, "
             f"пропущенных версий внутри покрытия {len(skipped)}" if args.index is not None
             else "; БЕЗ --index второй вопрос (нет ли версии позже) НЕ задан"))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
