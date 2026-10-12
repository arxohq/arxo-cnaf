#!/usr/bin/env python3
"""Барем APL секторного найма → параметры A3 пакета `fr.apl`.

КАЖДОЕ ЧИСЛО перенесено из закреплённого фрагмента, названного в `anchors`
своей строки значений; ни одно не взято из чужой реализации. Ось времени —
`legal_time`: у каждой статьи арретэ своё окно действия («applicables aux
prestations dues à compter du …»), и строка значения повторяет окно ИМЕННО
своей версии статьи. Поэтому у плафонов перелом 1 октября 2021 года, а у
форфейта R0 — 1 января 2022 года: так в самом акте.

Почему параметры, а не таблицы решений. A3 `mode: rules` требует факта
внутреннего отношения `<id таблицы>/input`, которое с поверхностей `.law` и
`.lawtest` не адресуемо, а `mode: function` не даёт вызвать себя из правила
(LDC-E2105) — измерено пакетами `fiqh.zakat`, `us/kidney-allocation`,
`org/iso/7064-check-characters` и повторно этим пакетом. Параметр же читается
голым именем и из правила, и из `function`, и его значение выбирается по
`context.legalTime` — то есть по месяцу, за который пособие причитается.

    build_bareme.py            — переписать параметры
    build_bareme.py --check    — сверить, ничего не записывая
    build_bareme.py --check-anchors — число каждой строки стоит в тексте
        якорного фрагмента (ядро: corpus/tools/sources/bareme_builder.py)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools" / "sources"))

PACKAGE = Path(__file__).resolve().parents[1]
OUT = PACKAGE / "bareme"
NS = "urn:fr:corpus:clir:apl"
MONEY = {"name": "urn:law:std#Money"}
DEC = {"name": "urn:law:std#Decimal"}
INT = {"name": "urn:law:std#Integer"}

#: Окна строк значений СЧИТАЮТСЯ из закреплённых байтов, а не пишутся руками.
#:
#: Начало — дата применимости версии к престациям: её называет NOTA самой
#: статьи («applicables aux prestations dues à compter du …»), и у редакции
#: 2025 года она НЕ совпадает с датой версии в LEGI (10 сентября против
#: 1 октября). Конец — дата применимости СЛЕДУЮЩЕЙ закреплённой версии, если
#: она непосредственно сменяет эту (её `in_force_from` равен нашему
#: `in_force_to`); иначе конец окна версии, а у последней версии окна нет
#: вовсе. Правило означает: между закреплёнными редакциями у акта были другие,
#: и там параметр не подставляется — оценка отвечает MISSING_PARAMETER_VALUE,
#: а не «последним известным» числом.
BOOK = json.loads((PACKAGE / "sources/fr-apl/articles.json").read_text(encoding="utf-8"))
OPEN_END = "2999-01-01"


#: К какому АКТУ относится документ редакции. Нужно потому, что учёт ключуется
#: НОМЕРОМ статьи, а номер «19» есть и у арретэ (форфейт расходов главы IV), и у
#: ордонанса 96-50 (ставка CRDS). Пока преемница искалась среди всех версий с тем
#: же номером, версия ордонанса получала в преемницы статью арретэ, и окно ставки
#: CRDS обрывалось на 1 октября 2020 года — 82 сценария разом (измерено
#: 14.09.2026). Преемница версии осмысленна только внутри своего акта.
def _act(document: str) -> str:
    if document.startswith("decret"):
        return "decret"
    if document.startswith("cch"):
        return "cch"
    if document.startswith("arrete"):
        return "arrete"
    return "ordonnance"


def _versions(number: str) -> list[dict]:
    rows = []
    for edition in BOOK["editions"]:
        version = edition["versions"].get(number)
        if version is not None:
            rows.append({"document": edition["document"], **version})
    return sorted(rows, key=lambda r: r["in_force_from"])


def _emitted(number: str, documents: tuple[str, ...]) -> list[dict]:
    """Версии статьи, дающие строки значений, в порядке применимости.

    Общее тело `windows()` и `anchors()`: окна и якоря обязаны идти одним
    списком, иначе `dataset` ловит расхождение чисел, а провенанс строки
    указывает на чужую редакцию.
    """
    rows = _versions(number)
    acts = {_act(document) for document in documents}
    if len(acts) != 1:
        raise SystemExit(f"окна статьи {number}: документы разных актов {sorted(acts)}")
    act = acts.pop()
    rows = [row for row in rows if _act(row["document"]) == act]
    distinct: list[dict] = []
    for row in rows:
        if all(other["legi_id"] != row["legi_id"] for other in distinct):
            distinct.append(row)
    distinct.sort(key=lambda r: (r["applies_from"], r["in_force_from"]))
    wanted = {row["legi_id"] for row in rows if row["document"] in documents}
    return [row for row in distinct if row["legi_id"] in wanted], distinct


#: Дерогация 2026 года: декрет № 2025-1401 от 28.12.2025 отменил ежегодную
#: переоценку R0 (и форфейта ресурсов студентов) на 2026 год. Он ничего не
#: устанавливает и потому не даёт строки значений — но именно им держится
#: применимость ПОСЛЕДНЕЙ строки R0 в месяцах права 2026 года. Поэтому его
#: ст. 1 добавляется якорем к последней строке каждого семейства R0: без неё
#: провенанс говорил бы «значение января 2025 года», не объясняя, почему оно
#: ещё действует.
DEROGATION_2026 = "DEC20251401_ART1"


def with_derogation(rows: list[list[str]]) -> list[list[str]]:
    """Добавить якорь дерогации 2026 года к ПОСЛЕДНЕЙ строке значений."""
    if rows:
        rows[-1] = rows[-1] + [DEROGATION_2026]
    return rows


def anchors(number: str, documents: tuple[str, ...]) -> list[list[str]]:
    """Якоря строк значений: ВСЕ состояния охвата, где действует эта версия.

    Редакция акта с 14.09.2026 — полное состояние охвата на дату, поэтому одна
    и та же версия статьи закреплена в нескольких состояниях подряд. Строка
    значений называет их все: провенанс не выбирает произвольную копию.
    """
    emitted, _ = _emitted(number, documents)
    by_version: dict[str, list[str]] = {}
    for row in _versions(number):
        by_version.setdefault(row["legi_id"], []).append(row["fragment"])
    return [by_version[row["legi_id"]] for row in emitted]


def windows(number: str, documents: tuple[str, ...]) -> list[tuple[str, str | None]]:
    """Окна строк значений для статьи `number` в названных документах.

    ПОЧЕМУ ВЕРСИИ СНАЧАЛА СХЛОПЫВАЮТСЯ ПО `legi_id`. Одна и та же версия статьи
    входит в НЕСКОЛЬКО состояний охвата (редакция акта — полное состояние на
    дату), и без схлопывания «следующей версией» оказывался её же дубликат:
    конец окна брался из окна версии, и строки значений ПЕРЕКРЫВАЛИСЬ.
    Измерено 14.09.2026; проверка на перекрытие стоит в `dataset`.
    """
    # ОСЬ ОКОН — ДАТА ПРИМЕНИМОСТИ. Начало строки — `applies_from` версии,
    # конец — `applies_from` её преемницы. Окно действия (`in_force_*`) входит
    # в расчёт ровно в одном качестве: им распознаётся НЕЗАКРЕПЛЁННАЯ версия
    # между двумя закреплёнными. Если преемница вступила в силу позже, чем
    # кончилось окно этой версии, между ними есть чужая версия, и строка
    # ОБЯЗАНА кончиться раньше — иначе значение молча растянулось бы на месяцы
    # права, которым принадлежит другое число (так было у R0 метрополии с
    # августа по декабрь 2022 года; измерено 14.09.2026).
    emitted, distinct = _emitted(number, documents)
    out = []
    for row in emitted:
        index = distinct.index(row)
        following = distinct[index + 1] if index + 1 < len(distinct) else None
        if following is not None and following["in_force_from"] <= row["in_force_to"]:
            # Версия не может действовать после начала своей преемницы. Условие
            # ослаблено с равенства до «не позже» намеренно: у ГЛОБАЛЬНОГО дампа
            # DATE_FIN версии бывает УСТАРЕВШИМ — её закрыл более поздний
            # инкремент, и в глобальном снимке стоит 2999-01-01.
            end = following["applies_from"]
        elif row["in_force_to"] == OPEN_END:
            end = None
        else:
            # Между закреплёнными версиями есть незакреплённые: разрыв намеренный,
            # и параметр в нём не подставляется.
            end = row["in_force_to"]
        out.append((row["applies_from"], end))
    return out


#: Состояния охвата арретэ, по которым строится барем: все, начиная с
#: 1 октября 2020 года — даты, с которой пакет объявляет покрытие барема.
#: Состояния 02.10.2019 и 01.01.2020 закреплены (нормы этих месяцев права
#: живы и названы якорями), но их ЧИСЛА в барем не перенесены: параметр там
#: не подставляется и отвечает MISSING_PARAMETER_VALUE — объявленная граница
#: покрытия, а не молчание.
ED_DOCS = ("arrete-2020-10.txt", "arrete-2021-01.txt", "arrete-2021-10.txt",
           "arrete-2022-01.txt", "arrete-2022-07.txt", "arrete-2023-01.txt",
           "arrete-2023-10.txt", "arrete-2024-01.txt", "arrete-2024-10.txt",
           "arrete-2025-01.txt", "arrete-2025-10.txt",
           "arrete-2026-10.txt")
#: Фрагменты, удостоверяющие значение: по редакции в том же порядке, что окна.
A_ART7 = ["ARR_ART07_ED2020", "ARR_ART07_ED2021", "ARR_ART07_ED2023", "ARR_ART07_ED2024", "ARR_ART07_ED2025_01", "ARR_ART07_ED2025"]
A_ART8 = ["ARR_ART08_ED2020", "ARR_ART08_ED2021", "ARR_ART08_ED2023", "ARR_ART08_ED2024", "ARR_ART08_ED2025_01", "ARR_ART08_ED2025"]
A_ART9 = ["ARR_ART09_ED2020", "ARR_ART09_ED2021", "ARR_ART09_ED2023", "ARR_ART09_ED2024", "ARR_ART09_ED2025_01", "ARR_ART09_ED2025"]
A_ART13 = ["ARR_ART13_ED2020", "ARR_ART13_ED2021", "ARR_ART13_ED2023", "ARR_ART13_ED2024", "ARR_ART13_ED2025_01", "ARR_ART13_ED2025"]
A_ART14 = ["ARR_ART14_ED2020", "ARR_ART14_ED2021", "ARR_ART14_ED2023", "ARR_ART14_ED2024", "ARR_ART14_ED2025_01", "ARR_ART14_ED2025"]
A_ART15 = ["ARR_ART15_ED2020", "ARR_ART15_ED2022", "ARR_ART15_ED2023", "ARR_ART15_ED2024",
           ["ARR_ART15_ED2025_01", "ARR_ART15_ED2025"]]
A_ART16 = ["ARR_ART16_ED2020", "ARR_ART16_ED2021", "ARR_ART16_ED2023", "ARR_ART16_ED2024", "ARR_ART16_ED2025_01", "ARR_ART16_ED2025"]
#: Статьи 10–12 не менялись: одно окно, но фрагмент есть в каждой редакции,
#: и строка значения удостоверяется обоими.
A_ART10 = ["ARR_ART10_ED2020", "ARR_ART10_ED2021", "ARR_ART10_ED2023", "ARR_ART10_ED2025", "ARR_ART10_ED2024", "ARR_ART10_ED2025_01"]
A_ART11 = ["ARR_ART11_ED2020", "ARR_ART11_ED2021", "ARR_ART11_ED2023", "ARR_ART11_ED2025", "ARR_ART11_ED2024", "ARR_ART11_ED2025_01"]
A_ART12 = ["ARR_ART12_ED2020", "ARR_ART12_ED2021", "ARR_ART12_ED2023", "ARR_ART12_ED2025", "ARR_ART12_ED2024", "ARR_ART12_ED2025_01"]

#: Главы V и VII арретэ (APL-foyer и AL-foyer) закреплены в ДВУХ редакциях —
#: тех, что нужны делам Catala. Редакция 2025 года у этих глав не закреплена,
#: и это видно в `coverage` каждого параметра: после 1 июля 2022 года значение
#: не подставляется, оценка отвечает MISSING_PARAMETER_VALUE.
ED_FOYER_DOCS = ED_DOCS
#: Главы VI и V вместе с редакцией, действующей на делах заморских территорий.
ED_AL_DOCS = ED_DOCS
A_ART27 = ["ARR_ART27_ED2020", "ARR_ART27_ED2021", "ARR_ART27_ED2023", "ARR_ART27_ED2024", "ARR_ART27_ED2025_01", "ARR_ART27_ED2025"]
A_ART40 = ["ARR_ART40_ED2020", "ARR_ART40_ED2021", "ARR_ART40_ED2023", "ARR_ART40_ED2024", "ARR_ART40_ED2025_01", "ARR_ART40_ED2025"]
A_ART43 = ["ARR_ART43_ED2020", "ARR_ART43_ED2021", "ARR_ART43_ED2023", "ARR_ART43_ED2024", "ARR_ART43_ED2025_01", "ARR_ART43_ED2025"]
#: Ст. 28–32, 41, 42 и 44 не менялись с 2019-10-02: одно окно, удостоверяемое
#: фрагментами обеих редакций.
A_ART28 = ["ARR_ART28_ED2020", "ARR_ART28_ED2021", "ARR_ART28_ED2023", "ARR_ART28_ED2024", "ARR_ART28_ED2025_01", "ARR_ART28_ED2025"]
A_ART29 = ["ARR_ART29_ED2020", "ARR_ART29_ED2021", "ARR_ART29_ED2023", "ARR_ART29_ED2024", "ARR_ART29_ED2025_01", "ARR_ART29_ED2025"]
A_ART30 = ["ARR_ART30_ED2020", "ARR_ART30_ED2021", "ARR_ART30_ED2023", "ARR_ART30_ED2024", "ARR_ART30_ED2025_01", "ARR_ART30_ED2025"]
A_ART31 = ["ARR_ART31_ED2020", "ARR_ART31_ED2021", "ARR_ART31_ED2023", "ARR_ART31_ED2024", "ARR_ART31_ED2025_01", "ARR_ART31_ED2025"]
A_ART32 = ["ARR_ART32_ED2020", "ARR_ART32_ED2021", "ARR_ART32_ED2023", "ARR_ART32_ED2024", "ARR_ART32_ED2025_01", "ARR_ART32_ED2025"]
A_ART41 = ["ARR_ART41_ED2020", "ARR_ART41_ED2021", "ARR_ART41_ED2023", "ARR_ART41_ED2024", "ARR_ART41_ED2025_01", "ARR_ART41_ED2025"]
A_ART42 = ["ARR_ART42_ED2020", "ARR_ART42_ED2021", "ARR_ART42_ED2023", "ARR_ART42_ED2024", "ARR_ART42_ED2025_01", "ARR_ART42_ED2025"]
A_ART44 = ["ARR_ART44_ED2020", "ARR_ART44_ED2021", "ARR_ART44_ED2023", "ARR_ART44_ED2024", "ARR_ART44_ED2025_01", "ARR_ART44_ED2025"]

#: Глава IV арретэ (APL-accession). Ст. 19 и 24 меняются по редакциям, ст. 17,
#: 18, 20–23, 25 и 26 — нет.
A_ART17 = ["ARR_ART17_ED2020", "ARR_ART17_ED2021"]
#: Ст. 18 — ТРИ состояния, а не одно. Версия от 01.08.2022 (применяется к
#: престациям с 1 июля 2022 года) ИСПРАВИЛА ДВЕ ОПЕЧАТКИ официального
#: текста: в подслучаях 12° и 13°, зона III, «par personne supplémentaire»
#: стояло 459,47 и 347,99 вместо 59,47 и 47,99. Версия от 30.12.2022
#: (с 1 января 2023 года) переложила статью из десятка таблиц по датам
#: подписания договора в одну сводную; ЧИСЛА подслучаев 17° и 18°, которые
#: и переносит барем, во всех трёх состояниях одни и те же.
A_ART18_2020 = ["ARR_ART18_ED2020", "ARR_ART18_ED2021"]
A_ART18_2022_07 = ["ARR_ART18_ED2022_07"]
A_ART18_2023 = ["ARR_ART18_ED2023", "ARR_ART18_ED2025"]
#: Документы, в которых закреплены эти три состояния.
ED_ART18_DOCS = ED_DOCS
A_ART19 = ["ARR_ART19_ED2020", "ARR_ART19_ED2021", "ARR_ART19_ED2023", "ARR_ART19_ED2024",
           "ARR_ART19_ED2025_01", "ARR_ART19_ED2025"]
A_ART20 = ["ARR_ART20_ED2020", "ARR_ART20_ED2021"]
A_ART21 = ["ARR_ART21_ED2020", "ARR_ART21_ED2021"]
A_ART22 = ["ARR_ART22_ED2020", "ARR_ART22_ED2021"]
A_ART23 = ["ARR_ART23_ED2020", "ARR_ART23_ED2021"]
A_ART24 = ["ARR_ART24_ED2020", "ARR_ART24_ED2021", "ARR_ART24_ED2023", "ARR_ART24_ED2024",
           "ARR_ART24_ED2025_01", "ARR_ART24_ED2025"]
A_ART25 = ["ARR_ART25_ED2020", "ARR_ART25_ED2021"]
A_ART26 = ["ARR_ART26_ED2020", "ARR_ART26_ED2021"]

#: Глава VI арретэ (аллокации сектора accession). Ст. 34 и 37 меняются по
#: редакциям, ст. 33, 35, 36, 38 и 39 — нет.
A_ART33 = ["ARR_ART33_ED2020", "ARR_ART33_ED2021", "ARR_ART33_ED2023", "ARR_ART33_ED2024", "ARR_ART33_ED2025_01", "ARR_ART33_ED2025"]
A_ART34 = ["ARR_ART34_ED2020", "ARR_ART34_ED2021", "ARR_ART34_ED2023", "ARR_ART34_ED2024", "ARR_ART34_ED2025_01", "ARR_ART34_ED2025"]
A_ART35 = ["ARR_ART35_ED2020", "ARR_ART35_ED2021", "ARR_ART35_ED2023", "ARR_ART35_ED2024", "ARR_ART35_ED2025_01", "ARR_ART35_ED2025"]
A_ART36 = ["ARR_ART36_ED2020", "ARR_ART36_ED2021", "ARR_ART36_ED2023", "ARR_ART36_ED2024", "ARR_ART36_ED2025_01", "ARR_ART36_ED2025"]
A_ART37 = ["ARR_ART37_ED2020", "ARR_ART37_ED2021", "ARR_ART37_ED2023", "ARR_ART37_ED2024", "ARR_ART37_ED2025_01", "ARR_ART37_ED2025"]
A_ART38 = ["ARR_ART38_ED2020", "ARR_ART38_ED2021", "ARR_ART38_ED2023", "ARR_ART38_ED2024", "ARR_ART38_ED2025_01", "ARR_ART38_ED2025"]
A_ART39 = ["ARR_ART39_ED2020", "ARR_ART39_ED2021", "ARR_ART39_ED2023", "ARR_ART39_ED2024", "ARR_ART39_ED2025_01", "ARR_ART39_ED2025"]
#: Две редакции кодекса: значения таблиц долей и потолков K в них ТОЖДЕСТВЕННЫ,
#: но без второй строки параметр кончался бы 5 апреля 2023 года.
#: Состояния охвата кодекса, в которых менялись статьи барема. Редакция кодекса
#: с 14.09.2026 — ПОЛНОЕ состояние охвата на дату (восемь состояний, окна
#: встык), поэтому одна и та же версия статьи закреплена в нескольких из них:
#: `windows()` схлопывает их по `legi_id`, а якоря строки называют ВСЕ
#: состояния, где эта версия действует.
ORD_DOCS = ("ordonnance-96-50-2019-09.txt", "ordonnance-96-50.txt")
CCH_DOCS = ("cch.txt", "cch-2019-12.txt", "cch-2020-01.txt", "cch-2021-01.txt",
            "cch-2023-04.txt", "cch-2023-09.txt", "cch-2023-12.txt",
            "cch-2026-07.txt")
#: Состояния до и с 5 апреля 2023 года — для якорей двух строк значений.
CCH_AVANT_2023 = ["CCH_{a}", "CCH_{a}_ED2019_12", "CCH_{a}_ED2020_01", "CCH_{a}_ED2021_01"]
CCH_DEPUIS_2023 = ["CCH_{a}_ED2023_04", "CCH_{a}_ED2023_09", "CCH_{a}_ED2023_12",
                   "CCH_{a}_ED2026_07"]
CCH_TOUS = CCH_AVANT_2023 + CCH_DEPUIS_2023


def cch_anchors(article: str, part: list[str]) -> list[str]:
    """Якоря строки значений: состояния охвата, где действует её версия."""
    return [name.format(a=article) for name in part]

#: Главы V и VII (фойе) третьей редакцией НЕ покрыты: дел на 2023 год у них нет,
#: строки значений не заводились. Фрагменты редакции закреплены, но параметр на
#: такой месяц права не подставится — видно в `coverage` каждого параметра.
#: Глава IX — режим заморских территорий: закреплена одной редакцией (2023).
#: Изъятия переоцениваются каждый год: три закреплённые редакции.
# Пять состояний ст. 46 в хронологическом порядке применимости: январь 2023,
# октябрь 2023, январь 2024, октябрь 2024, январь 2025.
ED_OM_DOCS = ED_DOCS
A_ART46 = ["ARR_ART46_ED2020_10", "ARR_ART46_ED2021_10", "ARR_ART46_ED2022_01",
           "ARR_ART46_ED2022_07", "ARR_ART46_ED2023", "ARR_ART46_ED2023_10",
           "ARR_ART46_ED2024", "ARR_ART46_ED2024_10", "ARR_ART46_ED2025_01",
           "ARR_ART46_ED2025"]
#: Ст. 47 до 2022 года регулировала МАЙОТТУ рекуррентной формулой сходимости —
#: объявленная граница, в барем она не перенесена. Сен-Пьер-и-Микелон появился
#: в статье с 1 января 2022 года, а закреплены три его состояния: значения
#: 2022 года пакет не переносил.
ED_OM_LIMITE_DOCS = ("arrete-2020-10.txt", "arrete-2021-10.txt",
                     "arrete-2022-01.txt", "arrete-2022-07.txt")
ED_OM47_DOCS = ("arrete-2023-01.txt", "arrete-2024-01.txt", "arrete-2025-01.txt")
A_ART47 = ["ARR_ART47_ED2023", "ARR_ART47_ED2024", "ARR_ART47_ED2025_01"]
A_ART31_2023 = ["ARR_ART31_ED2023"]

WRITTEN: dict[Path, str] = {}
#: Specs behind WRITTEN, for the anchor check (--check-anchors): the same
#: code path builds both, so the check sees exactly the rows being written.
SPECS: list = []


#: Русские названия столбцов и составов — для метки §218 второго языка.
RU = {
    "Isole": "одинокое лицо", "Couple": "пара без иждивенцев",
    "UnePac": "лицо или пара с одним иждивенцем",
    "ParPacSup": "надбавка за каждого следующего иждивенца",
    "Zone1": "зона I", "Zone2": "зона II", "Zone3": "зона III",
    "1Pac": "один иждивенец", "2Pac": "два иждивенца", "3Pac": "три иждивенца",
    "4Pac": "четыре иждивенца", "5Pac": "пять иждивенцев",
    "6Pac": "шесть иждивенцев", "Majoration": "надбавка",
    "DeuxPac": "лицо или пара с двумя иждивенцами",
    "TroisPac": "лицо или пара с тремя иждивенцами",
    "QuatrePac": "лицо или пара с четырьмя иждивенцами",
    "EtudiantChambre": "студент, живущий в комнате",
    "EtudiantChambreRehabilitee": "студент в комнате после реабилитации",
    "PersonnesAgees": "пожилые лица, получатели ASPA и лица с инвалидностью",
    "AutresPersonnes": "прочие лица",
    "Seule": "одинокое лицо", "Deux": "пара",
    "General": "общий случай",
    "JeunesTravailleurs": "фойе молодых работников и социальные резиденции",
    "Ap2017": "заём подписан после 30 сентября 2017 года",
    "Ap2019": "заём подписан после 30 сентября 2019 года",
    "Neuf": "жильё новое, построенное или приобретённое приобретателем",
    "AcquisAmeliore": "жильё расширенное, переоборудованное из нежилого либо приобретённое и при необходимости улучшенное",
    "Cert2017": "сертификат датирован с 1 октября 2017 года",
    "Cert2019": "сертификат датирован с 1 октября 2019 года",
    "Couples": "пара без иждивенцев",
    "C1": "один иждивенец", "C2": "два иждивенца", "C3": "три иждивенца",
    "C4": "четыре иждивенца", "C5": "пять иждивенцев",
    "ParPersSupp": "надбавка за каждого следующего иждивенца",
    "Cert2015": "сертификат датирован с 1 октября 2015 года",
    "OutreMer": "Гваделупа, Гвиана, Мартиника, Реюньон, Майотта, Сен-Бартелеми и Сен-Мартен",
    "SaintPierre": "Сен-Пьер-и-Микелон",
    "7Pac": "семь иждивенцев",
}
FR = {
    "Isole": "personne seule", "Couple": "couple sans personne à charge",
    "UnePac": "personne seule ou couple ayant une personne à charge",
    "ParPacSup": "par personne à charge supplémentaire",
    "Zone1": "zone I", "Zone2": "zone II", "Zone3": "zone III",
    "1Pac": "une personne à charge", "2Pac": "deux personnes à charge",
    "3Pac": "trois personnes à charge", "4Pac": "quatre personnes à charge",
    "5Pac": "cinq personnes à charge", "6Pac": "six personnes à charge",
    "Majoration": "majoration",
    "DeuxPac": "personne seule ou couple ayant deux personnes à charge",
    "TroisPac": "personne seule ou couple ayant trois personnes à charge",
    "QuatrePac": "personne seule ou couple ayant quatre personnes à charge",
    "EtudiantChambre": "étudiant logé en chambre",
    "EtudiantChambreRehabilitee": "étudiant logé dans une chambre réhabilitée",
    "PersonnesAgees": "personnes âgées, titulaires de l'ASPA et personnes handicapées",
    "AutresPersonnes": "autres personnes",
    "Seule": "personne seule", "Deux": "couple",
    "General": "cas général",
    "JeunesTravailleurs": "logements-foyers de jeunes travailleurs et résidences sociales",
    "Ap2017": "contrat de prêt signé postérieurement au 30 septembre 2017",
    "Ap2019": "contrat de prêt signé postérieurement au 30 septembre 2019",
    "Neuf": "logements neufs construits ou acquis par l'accédant à la propriété",
    "AcquisAmeliore": "logements agrandis ou aménagés à partir de locaux non destinés à l'habitation ou logements existants acquis et, le cas échéant, améliorés",
    "Cert2017": "certificats datés à partir du 1er octobre 2017",
    "Cert2019": "certificats datés à partir du 1er octobre 2019",
    "Couples": "couples", "C1": "C+1", "C2": "C+2", "C3": "C+3",
    "C4": "C+4", "C5": "C+5", "ParPersSupp": "par personne supplémentaire",
    "Cert2015": "certificats datés à partir du 1er octobre 2015",
    "OutreMer": "Guadeloupe, Guyane, Martinique, La Réunion, Mayotte, Saint-Barthélemy et Saint-Martin",
    "SaintPierre": "Saint-Pierre-et-Miquelon",
    "7Pac": "sept personnes à charge",
}


def dataset(name: str, value_type: dict, windows: list[tuple[str, str | None]],
            values: list[str], anchors: list[str], currency: str | None,
            label_fr: str = "", label_ru: str = "") -> None:
    # Emission moved to the generic core (first consumer: this package).
    # Payloads must stay byte-identical: see bareme_builder.render_dataset.
    from bareme_builder import ParamSpec, render_dataset
    spec = ParamSpec(name=name, value_type=value_type, windows=windows,
                     values=values, anchors=anchors, currency=currency,
                     label_fr=label_fr, label_ru=label_ru)
    # Saint-Pierre ramp: values computed by the decree formula ALspm =
    # ALt x (1 - (2026-n)/8), printed nowhere in the anchor text.
    if name == "CoefficientMonteeEnChargeSaintPierre":
        spec.derived = [(name, start) for start, _ in windows]
    filename, payload = render_dataset(spec, NS)
    WRITTEN[OUT / filename] = payload
    SPECS.append(spec)


def money(name: str, windows, values, anchors, fr: str = "", ru: str = "") -> None:
    dataset(name, MONEY, windows, values, anchors, "EUR", fr, ru)


def decimal(name: str, windows, values, anchors, fr: str = "", ru: str = "") -> None:
    dataset(name, DEC, windows, values, anchors, None, fr, ru)


def integer(name: str, windows, values, anchors, fr: str = "", ru: str = "") -> None:
    dataset(name, INT, windows, values, anchors, None, fr, ru)


# --- ст. 7: плафоны найма (ED2020, ED2021) ---------------------------------
PLAFONDS = {
    "Zone1": {"Isole": ("296.82", "298.07", "308.50", "319.30", "329.71", "333.14", "336.97"), "Couple": ("357.99", "359.49", "372.07", "385.09", "397.64", "401.78", "406.40"),
              "UnePac": ("404.60", "406.30", "420.52", "435.24", "449.43", "454.10", "459.32"), "ParPacSup": ("58.70", "58.95", "61.01", "63.15", "65.21", "65.89", "66.65")},
    "Zone2": {"Isole": ("258.69", "259.78", "268.87", "278.28", "287.35", "290.34", "293.68"), "Couple": ("316.64", "317.97", "329.10", "340.62", "351.72", "355.38", "359.47"),
              "UnePac": ("356.30", "357.80", "370.32", "383.28", "395.77", "399.89", "404.49"), "ParPacSup": ("51.86", "52.08", "53.90", "55.79", "57.61", "58.21", "58.88")},
    "Zone3": {"Isole": ("242.46", "243.48", "252.00", "260.82", "269.32", "272.12", "275.25"), "Couple": ("293.92", "295.15", "305.48", "316.17", "326.48", "329.88", "333.67"),
              "UnePac": ("329.56", "330.94", "342.52", "354.51", "366.07", "369.88", "374.13"), "ParPacSup": ("47.23", "47.43", "49.09", "50.81", "52.47", "53.01", "53.62")},
}
# --- ст. 16 1°: те же плафоны для колокаторов (75 % плафонов ст. 7) --------
PLAFONDS_COLOC = {
    "Zone1": {"Isole": ("222.62", "223.55", "231.38", "239.48", "247.28", "249.86", "252.73"), "Couple": ("268.49", "269.62", "279.05", "288.82", "298.23", "301.34", "304.80"),
              "UnePac": ("303.45", "304.73", "315.39", "326.43", "337.07", "340.58", "344.49"), "ParPacSup": ("44.03", "44.21", "45.76", "47.36", "48.91", "49.42", "49.99")},
    "Zone2": {"Isole": ("194.02", "194.84", "201.65", "208.71", "215.51", "217.76", "220.26"), "Couple": ("237.48", "238.48", "246.83", "255.47", "263.79", "266.54", "269.60"),
              "UnePac": ("267.23", "268.35", "277.74", "287.46", "296.83", "299.92", "303.37"), "ParPacSup": ("38.90", "39.06", "40.43", "41.84", "43.21", "43.66", "44.16")},
    "Zone3": {"Isole": ("181.85", "182.61", "189.00", "195.62", "201.99", "204.09", "206.44"), "Couple": ("220.44", "221.36", "229.11", "237.13", "244.86", "247.41", "250.25"),
              "UnePac": ("247.17", "248.21", "256.89", "265.88", "274.55", "277.41", "280.60"), "ParPacSup": ("35.42", "35.57", "36.82", "38.11", "39.35", "39.76", "40.22")},
}
# --- ст. 8: плафоны комнаты: общий случай и размещение за плату ------------
CHAMBRE = {"Zone1": ("267.14", "268.26", "277.65", "287.37", "296.74", "299.83", "303.27"), "Zone2": ("232.82", "233.80", "241.98", "250.45", "258.62", "261.31", "264.31"),
           "Zone3": ("218.21", "219.13", "226.80", "234.74", "242.39", "244.91", "247.73")}
CHAMBRE_ONEREUX = {"Zone1": ("222.62", "223.55", "231.38", "239.48", "247.28", "249.86", "252.73"),
                   "Zone2": ("194.02", "194.84", "201.65", "208.71", "215.51", "217.76", "220.26"),
                   "Zone3": ("181.85", "182.61", "189.00", "195.62", "201.99", "204.09", "206.44")}
# --- ст. 14 1°: TF ---------------------------------------------------------
TAUX_FAMILLE = {
    "Isole": ("0.0283",) * 7, "Couple": ("0.0315",) * 7,
    "1Pac": ("0.0270",) * 7, "2Pac": ("0.0238",) * 7,
    "3Pac": ("0.0201",) * 7, "4Pac": ("0.0185",) * 7,
    "5Pac": ("0.0179",) * 7, "6Pac": ("0.0173",) * 7,
    "Majoration": ("-0.0006",) * 7,
}
# --- ст. 14 2°: LR и ступени RL -------------------------------------------
LOYER_REFERENCE = {"Isole": ("258.69", "259.78", "268.87", "278.28", "287.35", "290.34", "293.68"),
                   "Couple": ("316.64", "317.97", "329.10", "340.62", "351.72", "355.38", "359.47"),
                   "1Pac": ("356.30", "357.80", "370.32", "383.28", "395.77", "399.89", "404.49"),
                   "Majoration": ("51.86", "52.08", "53.90", "55.79", "57.61", "58.21", "58.88")}
TRANCHES_RL = {"SeuilBasRL": ("0.45",) * 7, "SeuilHautRL": ("0.75",) * 7,
               "TauxRLTrancheBasse": ("0.0045",) * 7,
               "TauxRLTrancheHaute": ("0.0068",) * 7}
# --- ст. 15: R0 (окна версий ст. 15, а не ст. 7) --------------------------
#: R0 метрополии. ТРЕТЬЯ строка — версия ст. 15 от 01.08.2022 (арретэ от
#: 29 июля 2022 года, применяется к престациям с 1 ИЮЛЯ 2022 года). Без неё в
#: бареме зияла дыра с августа по декабрь 2022 года: окно январской версии
#: кончалось 1 августа, а следующая закреплённая версия применялась лишь с
#: 1 января 2023 года, и дело тех месяцев отвечало MISSING_PARAMETER_VALUE.
ABATTEMENT_R0 = {
    "Isole": ("4588", "4683", "4870", "4949", "5186", "5235"), "Couple": ("6572", "6709", "6977", "7090", "7430", "7501"),
    "1Pac": ("7839", "8002", "8322", "8456", "8862", "8947"), "2Pac": ("8015", "8182", "8509", "8646", "9061", "9148"),
    "3Pac": ("8322", "8495", "8834", "8977", "9408", "9498"), "4Pac": ("8631", "8811", "9163", "9311", "9758", "9851"),
    "5Pac": ("8938", "9124", "9488", "9642", "10105", "10202"), "6Pac": ("9246", "9439", "9816", "9975", "10454", "10554"),
    "Majoration": ("305", "311", "323", "328", "343", "346"),
}


# ==========================================================================
# СЕКТОР LOGEMENT-FOYER. Две формулы, обе из закреплённого текста:
#   APL-foyer  (D. 832-24): Af = K × (E − E0)
#   AL-foyer   (D. 842-15): Af = K × (L + C − L0)
# Значения ниже перенесены из глав V и VII арретэ и из таблиц САМОЙ D. 832-25
# (доли N стоят в кодексе, а не в арретэ — поэтому их якорь кодексный).
# ==========================================================================

# --- ст. 27: плафоны эквивалентности найма и расходов E (APL-foyer) --------
PLAFONDS_E = {
    "Zone1": {"Isole": ("444.43", "446.30", "461.92", "478.09", "493.68", "498.81", "504.55"),
              "Couple": ("521.02", "523.21", "541.52", "560.47", "578.74", "584.76", "591.48"),
              "UnePac": ("555.55", "557.88", "577.41", "597.62", "617.10", "623.52", "630.69"),
              "DeuxPac": ("594.54", "597.04", "617.94", "639.57", "660.42", "667.29", "674.96"),
              "TroisPac": ("633.69", "636.35", "658.62", "681.67", "703.89", "711.21", "719.39"),
              "QuatrePac": ("683.50", "686.37", "710.39", "735.25", "759.22", "767.12", "775.94"),
              "ParPacSup": ("70.89", "71.19", "73.68", "76.26", "78.75", "79.57", "80.49")},
    "Zone2": {"Isole": ("406.43", "408.14", "422.42", "437.20", "451.45", "456.15", "461.40"),
              "Couple": ("474.33", "476.32", "492.99", "510.24", "526.87", "532.35", "538.47"),
              "UnePac": ("505.75", "507.87", "525.65", "544.05", "561.79", "567.63", "574.16"),
              "DeuxPac": ("541.38", "543.65", "562.68", "582.37", "601.36", "607.61", "614.60"),
              "TroisPac": ("576.87", "579.29", "599.57", "620.55", "640.78", "647.44", "654.89"),
              "QuatrePac": ("614.69", "617.27", "638.87", "661.23", "682.79", "689.89", "697.82"),
              "ParPacSup": ("64.07", "64.34", "66.59", "68.92", "71.17", "71.91", "72.74")},
    "Zone3": {"Isole": ("385.78", "387.40", "400.96", "414.99", "428.52", "432.98", "437.96"),
              "Couple": ("448.69", "450.57", "466.34", "482.66", "498.39", "503.57", "509.36"),
              "UnePac": ("476.02", "478.02", "494.75", "512.07", "528.76", "534.26", "540.40"),
              "DeuxPac": ("507.44", "509.57", "527.40", "545.86", "563.66", "569.52", "576.07"),
              "TroisPac": ("538.84", "541.10", "560.04", "579.64", "598.54", "604.76", "611.71"),
              "QuatrePac": ("574.16", "576.57", "596.75", "617.64", "637.78", "644.41", "651.82"),
              "ParPacSup": ("59.46", "59.71", "61.80", "63.96", "66.05", "66.74", "67.51")},
}
# --- D. 832-25 e du 1° и d du 2°: доли N ----------------------------------
# Две таблицы, потому что у фойе молодых работников (конвенционированных после
# 30.09.1990) и социальных резиденций (после 31.12.1994) свои доли: 1,2 и 1,5
# против 1,4 и 1,8. Начиная с одного иждивенца таблицы совпадают — и это
# совпадение ТЕКСТА, не экономия: обе выписаны целиком.
PARTS_FOYER = {
    "General": {"Isole": "1.4", "Couple": "1.8", "UnePac": "2.5", "DeuxPac": "3.0",
                "TroisPac": "3.7", "QuatrePac": "4.3", "ParPacSup": "0.5"},
    "JeunesTravailleurs": {"Isole": "1.2", "Couple": "1.5", "UnePac": "2.5",
                           "DeuxPac": "3.0", "TroisPac": "3.7", "QuatrePac": "4.3",
                           "ParPacSup": "0.5"},
}
# --- ст. 31 I: ставки и границы транш E0 ----------------------------------
TAUX_E0 = ("0.0400", "0.1040", "0.2160", "0.2640", "0.3200", "0.4800")
BORNES_E0 = ("1948.10", "2678.71", "3896.18", "5357.44", "6331.29")
# --- ст. 43: эквивалентность найма L по категориям (AL-foyer) -------------
EQUIVALENCE_L = {
    "EtudiantChambre": {"Seule": ("83.79", "84.14", "87.08", "90.13", "93.07", "94.04", "95.12"),
                        "Deux": ("130.45", "131.00", "135.59", "140.34", "144.92", "146.43", "148.11")},
    "EtudiantChambreRehabilitee": {"Seule": ("169.41", "170.12", "176.07", "182.23", "188.17", "190.13", "192.32"),
                                   "Deux": ("263.29", "264.40", "273.65", "283.23", "292.46", "295.50", "298.90")},
    "PersonnesAgees": {"Seule": ("205.54", "206.40", "213.62", "221.10", "228.31", "230.68", "233.33"),
                       "Deux": ("319.39", "320.73", "331.96", "343.58", "354.78", "358.47", "362.59")},
    "AutresPersonnes": {"Seule": ("169.41", "170.12", "176.07", "182.23", "188.17", "190.13", "192.32"),
                        "Deux": ("263.29", "264.40", "273.65", "283.23", "292.46", "295.50", "298.90")},
}


def build_foyer() -> None:
    """Барем двух глав сектора logement-foyer."""
    for zone, columns in PLAFONDS_E.items():
        for column, values in columns.items():
            money(f"PlafondEquivalence{zone}{column}",
                  windows("27", ED_FOYER_DOCS), list(values), anchors("27", ED_FOYER_DOCS),
                  f"plafond d'équivalence de loyer et de charges, {FR[zone]}, {FR[column]}",
                  f"плафон эквивалентности найма и расходов, {RU[zone]}, {RU[column]}")
    money("MinorationForfaitaireFoyerAPL", windows("28", ("arrete-2020-10.txt",)),
          ["5"], anchors("28", ("arrete-2020-10.txt",)),
          "minoration forfaitaire retranchée de l'aide en secteur logement-foyer (APL)",
          "форфейтная минорация пособия в секторе logement-foyer (APL)")
    money("SeuilVersementFoyerAPL", windows("29", ("arrete-2020-10.txt",)),
          ["10"], anchors("29", ("arrete-2020-10.txt",)),
          "seuil de versement de l'APL en secteur logement-foyer, avant CRDS",
          "порог выплаты APL в секторе logement-foyer, до CRDS")
    money("CoefficientRFoyer", windows("30", ("arrete-2020-10.txt",)),
          ["1217.26"], anchors("30", ("arrete-2020-10.txt",)),
          "coefficient « r » de la formule du coefficient de prise en charge K",
          "коэффициент « r » формулы коэффициента принятия на себя K")
    money("CoefMultiplicateurFoyerGeneral", windows("30", ("arrete-2020-10.txt",)),
          ["13393.40"], anchors("30", ("arrete-2020-10.txt",)),
          "coefficient multiplicateur « cm », cas général (d du 1°)",
          "множитель « cm », общий случай (d пункта 1°)")
    money("CoefMultiplicateurFoyerJeunesTravailleurs",
          windows("30", ("arrete-2020-10.txt",)), ["21420.91"], anchors("30", ("arrete-2020-10.txt",)),
          "coefficient multiplicateur « cm », logements-foyers de jeunes "
          "travailleurs et résidences sociales (c du 2°)",
          "множитель « cm », фойе молодых работников и социальные резиденции (c пункта 2°)")
    for index, taux in enumerate(TAUX_E0, start=1):
        decimal(f"TauxE0Tranche{index}",
                windows("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
                [taux, taux], anchors("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
                f"pourcentage de la tranche {index} du calcul de E0",
                f"ставка {index}-й транши расчёта E0")
    for index, borne in enumerate(BORNES_E0, start=1):
        money(f"BorneE0Tranche{index}",
              windows("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
              [borne, borne], anchors("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
              f"borne supérieure de la tranche {index} du calcul de E0 "
              "(à multiplier par le nombre de parts N)",
              f"верхняя граница {index}-й транши расчёта E0 (умножается на число долей N)")
    money("ForfaitE0General",
          windows("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
          ["45.57", "45.57"], anchors("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
          "montant forfaitaire ajouté au calcul de E0, cas général",
          "форфейт, добавляемый к расчёту E0, общий случай")
    money("ForfaitE0JeunesTravailleurs",
          windows("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
          ["76.32", "76.32"], anchors("31", ("arrete-2020-10.txt", "arrete-2023-01.txt")),
          "montant forfaitaire ajouté au calcul de E0, logements-foyers de jeunes "
          "travailleurs et résidences sociales",
          "форфейт, добавляемый к расчёту E0, фойе молодых работников и социальные резиденции")
    money("DepenseNetteMinimaleFoyerAPL", windows("32", ("arrete-2020-10.txt",)),
          ["26.68"], anchors("32", ("arrete-2020-10.txt",)),
          "montant minimum de dépense nette de logement, cas général",
          "минимальный чистый расход на жильё, общий случай")
    money("DepenseNetteMinimaleFoyerJeunesTravailleurs",
          windows("32", ("arrete-2020-10.txt",)), ["15"], anchors("32", ("arrete-2020-10.txt",)),
          "montant minimum de dépense nette de logement, logements-foyers de "
          "jeunes travailleurs et résidences sociales",
          "минимальный чистый расход на жильё, фойе молодых работников и социальные резиденции")
    # Доли N и потолки K стоят в САМОЙ D. 832-25 — якорь кодексный.
    for variante, columns in PARTS_FOYER.items():
        for column, value in columns.items():
            decimal(f"PartsFoyer{variante}{column}",
                    windows("D832-25", CCH_DOCS), [value, value],
                    anchors("D832-25", CCH_DOCS),
                    f"nombre de parts N, {FR[variante]}, {FR[column]}",
                    f"число долей N, {RU[variante]}, {RU[column]}")
    decimal("PlafondCoefficientPriseEnChargeGeneral",
            windows("D832-25", CCH_DOCS), ["0.95", "0.95"],
            anchors("D832-25", CCH_DOCS),
            "valeur maximale du coefficient de prise en charge K, cas général",
            "предельное значение коэффициента K, общий случай")
    decimal("PlafondCoefficientPriseEnChargeJeunesTravailleurs",
            windows("D832-25", CCH_DOCS), ["0.90", "0.90"],
            anchors("D832-25", CCH_DOCS),
            "valeur maximale du coefficient de prise en charge K, logements-foyers "
            "de jeunes travailleurs et résidences sociales",
            "предельное значение коэффициента K, фойе молодых работников и социальные резиденции")
    # --- глава VII: AL-foyer ---------------------------------------------
    money("ForfaitChargesFoyerBase", windows("40", ED_FOYER_DOCS),
          ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("40", ED_FOYER_DOCS),
          "montant forfaitaire de charges en logement-foyer, bénéficiaire isolé "
          "ou couple sans personne à charge",
          "форфейт расходов в logement-foyer: одинокое лицо либо пара без иждивенцев")
    money("ForfaitChargesFoyerParPacSup", windows("40", ED_FOYER_DOCS),
          ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("40", ED_FOYER_DOCS),
          "montant forfaitaire de charges en logement-foyer, par personne "
          "supplémentaire à charge",
          "форфейт расходов в logement-foyer: за каждого дополнительного иждивенца")
    money("MinorationForfaitaireFoyerAL", windows("41", ("arrete-2020-10.txt",)),
          ["5"], anchors("41", ("arrete-2020-10.txt",)),
          "minoration forfaitaire retranchée de l'allocation en logement-foyer",
          "форфейтная минорация аллокации в logement-foyer")
    money("SeuilVersementFoyerAL", windows("42", ("arrete-2020-10.txt",)),
          ["10"], anchors("42", ("arrete-2020-10.txt",)),
          "seuil de versement de l'allocation en logement-foyer, avant CRDS",
          "порог выплаты аллокации в logement-foyer, до CRDS")
    for categorie, colonnes in EQUIVALENCE_L.items():
        for column, values in colonnes.items():
            money(f"EquivalenceLoyer{categorie}{column}",
                  windows("43", ED_FOYER_DOCS), list(values), anchors("43", ED_FOYER_DOCS),
                  f"équivalence de loyer L, {FR[categorie]}, {FR[column]}",
                  f"эквивалентность найма L, {RU[categorie]}, {RU[column]}")
    money("DepenseNetteMinimaleFoyerAL", windows("44", ("arrete-2020-10.txt",)),
          ["15"], anchors("44", ("arrete-2020-10.txt",)),
          "montant minimum de dépense nette de logement en logement-foyer (AL)",
          "минимальный чистый расход на жильё в logement-foyer (AL)")


# ==========================================================================
# СЕКТОР ACCESSION (приобретение жилья), APL. D. 832-10: Af = K × (L + C − L0).
#
# ГРАНИЦА ОХВАТА ВНУТРИ СТАТЬИ 18. Плафон мензуальности выбирается ДАТОЙ
# ПОДПИСАНИЯ ЗАЙМА — это факт дела, а не месяц права, поэтому ось `legal_time`
# здесь не работает и подслучай приходит перечислением. Статья 18 несёт
# ВОСЕМНАДЦАТЬ подслучаев (винтажей займа) с 30 июня 1992 года; перенесены два
# последних — 17° (заём после 30.09.2017) и 18° (после 30.09.2019), те, что
# нужны делам Catala. Остальные шестнадцать в закреплённом тексте ЕСТЬ, но в
# барем не перенесены: на таком деле параметр не подставится и оценка ответит
# MISSING_PARAMETER_VALUE, а не значением чужого винтажа. Подслучаи 1°–3°
# вдобавок выражены во ФРАНКАХ, и правила пересчёта в евро эта статья не даёт.
#
# НАБЛЮДЕНИЕ О САМОМ ТЕКСТЕ. В подслучае 13° строка «Par personne
# supplémentaire à charge» несёт по зоне III 459,47 (a) и 347,99 (b) там, где у
# всех соседних винтажей эта надбавка около 50–60 €, а у зон I и II того же
# 13° — 73,99 и 65,15 (a). Это похоже на опечатку ОФИЦИАЛЬНОГО текста, а не на
# норму; 13° в барем не перенесён, и утверждать о нём пакет ничего не может.
# --- ст. 18, подслучаи 17° и 18°: плафоны мензуальности -------------------
PLAFONDS_MENSUALITE = {
    "Ap2017": {
        "Neuf": {"Zone1": ("371.40", "448.07", "524.72", "76.64"),
                 "Zone2": ("331.45", "398.93", "466.43", "67.48"),
                 "Zone3": ("309.43", "371.03", "432.64", "61.61")},
        "AcquisAmeliore": {"Zone1": ("298.97", "360.79", "422.60", "61.82"),
                           "Zone2": ("266.50", "320.97", "375.43", "54.47"),
                           "Zone3": ("248.89", "298.58", "348.29", "49.71")},
    },
    "Ap2019": {
        "Neuf": {"Zone1": ("372.52", "449.41", "526.29", "76.87"),
                 "Zone2": ("332.44", "400.13", "467.83", "67.68"),
                 "Zone3": ("310.36", "372.15", "433.94", "61.79")},
        "AcquisAmeliore": {"Zone1": ("299.86", "361.87", "423.86", "62.01"),
                           "Zone2": ("267.30", "321.93", "376.56", "54.63"),
                           "Zone3": ("249.64", "299.48", "349.34", "49.86")},
    },
}
#: Столбцы таблиц ст. 18 в порядке строк документа.
COLONNES_MENSUALITE = ("Isole", "Couple", "UnePac", "ParPacSup")
# --- D. 832-11 4°: доли N сектора приобретения ---------------------------
PARTS_ACCESSION = {"Isole": "1.4", "Couple": "1.8", "UnePac": "2.5",
                   "DeuxPac": "3.0", "TroisPac": "3.7", "QuatrePac": "4.3",
                   "ParPacSup": "0.5"}


def build_accession() -> None:
    """Барем главы IV: сектор приобретения жилья, APL."""
    for sous_cas, finalites in PLAFONDS_MENSUALITE.items():
        for finalite, zones in finalites.items():
            for zone, values in zones.items():
                for column, value in zip(COLONNES_MENSUALITE, values, strict=True):
                    money(f"PlafondMensualite{sous_cas}{finalite}{zone}{column}",
                          windows("18", ED_ART18_DOCS), [value] * 3,
                          anchors("18", ED_ART18_DOCS),
                          f"plafond de mensualité, {FR[sous_cas]}, {FR[finalite]}, "
                          f"{FR[zone]}, {FR[column]}",
                          f"плафон мензуальности, {RU[sous_cas]}, {RU[finalite]}, "
                          f"{RU[zone]}, {RU[column]}")
    money("ForfaitChargesAccessionBase", windows("19", ED_FOYER_DOCS),
          ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("19", ED_FOYER_DOCS),
          "montant forfaitaire des charges en secteur accession, bénéficiaire "
          "isolé ou couple sans personne à charge",
          "форфейт расходов в секторе приобретения: одинокое лицо либо пара без иждивенцев")
    money("ForfaitChargesAccessionParPacSup", windows("19", ED_FOYER_DOCS),
          ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("19", ED_FOYER_DOCS),
          "montant forfaitaire des charges en secteur accession, par personne "
          "supplémentaire à charge",
          "форфейт расходов в секторе приобретения: за каждого дополнительного иждивенца")
    money("MinorationForfaitaireAccession", windows("20", ("arrete-2020-10.txt",)),
          ["5"], anchors("20", ("arrete-2020-10.txt",)),
          "minoration forfaitaire retranchée de l'aide en secteur accession",
          "форфейтная минорация пособия в секторе приобретения")
    money("SeuilVersementAccession", windows("21", ("arrete-2020-10.txt",)),
          ["10"], anchors("21", ("arrete-2020-10.txt",)),
          "seuil de versement de l'APL en secteur accession, avant CRDS",
          "порог выплаты APL в секторе приобретения, до CRDS")
    money("CoefMultiplicateurAccession", windows("22", ("arrete-2020-10.txt",)),
          ["22111.33"], anchors("22", ("arrete-2020-10.txt",)),
          "coefficient multiplicateur « cm » du 3° de l'article D. 832-11",
          "множитель « cm » пункта 3° ст. D. 832-11")
    decimal("TauxL0TrancheBasse", windows("23", ("arrete-2020-10.txt",)),
            ["0.2080"], anchors("23", ("arrete-2020-10.txt",)),
            "pourcentage de la tranche inférieure du calcul de L0",
            "ставка нижней транши расчёта L0")
    decimal("TauxL0TrancheHaute", windows("23", ("arrete-2020-10.txt",)),
            ["0.4160"], anchors("23", ("arrete-2020-10.txt",)),
            "pourcentage de la tranche supérieure du calcul de L0",
            "ставка верхней транши расчёта L0")
    money("BorneL0", windows("23", ("arrete-2020-10.txt",)), ["5600.85"], anchors("23", ("arrete-2020-10.txt",)),
          "borne des tranches de ressources du calcul de L0 (à multiplier par N)",
          "граница транш ресурсов расчёта L0 (умножается на N)")
    # Ст. 24 МЕНЯЕТСЯ по редакциям (в ней же форфейты расходов), поэтому доля
    # 75 % обязана иметь строку в КАЖДОЙ редакции: одна строка окном первой
    # редакции оставила бы параметр без значения на втором месяце права.
    decimal("PartCoproprietairePlafond", windows("24", ED_FOYER_DOCS),
            ["0.75"] * 7, anchors("24", ED_FOYER_DOCS),
            "part des plafonds de mensualités applicable aux copropriétaires",
            "доля плафонов мензуальности, применяемая к сособственникам")
    money("ForfaitChargesCoproIsole", windows("24", ED_FOYER_DOCS),
          ["26.99", "27.10", "28.05", "29.03", "29.98", "30.29", "30.64"], anchors("24", ED_FOYER_DOCS),
          "montant forfaitaire des charges des copropriétaires, bénéficiaire isolé",
          "форфейт расходов сособственника: одинокое лицо")
    money("ForfaitChargesCoproCouple", windows("24", ED_FOYER_DOCS),
          ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("24", ED_FOYER_DOCS),
          "montant forfaitaire des charges des copropriétaires, couple sans personne à charge",
          "форфейт расходов сособственника: пара без иждивенцев")
    money("ForfaitChargesCoproMajoration", windows("24", ED_FOYER_DOCS),
          ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("24", ED_FOYER_DOCS),
          "montant forfaitaire des charges des copropriétaires, majoration par personne à charge",
          "форфейт расходов сособственника: надбавка за иждивенца")
    decimal("CoefDepenseNetteAmelioreParOccupant",
            windows("25", ("arrete-2020-10.txt",)), ["0.0172"], anchors("25", ("arrete-2020-10.txt",)),
            "coefficient de la dépense nette minimale, logements améliorés par "
            "leur propriétaire occupant",
            "коэффициент минимального чистого расхода: жильё, улучшенное собственником-жильцом")
    decimal("CoefDepenseNetteAvantOctobre1998",
            windows("25", ("arrete-2020-10.txt",)), ["0.0226"], anchors("25", ("arrete-2020-10.txt",)),
            "coefficient de la dépense nette minimale, prêts souscrits avant le 1er octobre 1998",
            "коэффициент минимального чистого расхода: займы до 1 октября 1998 года")
    decimal("CoefDepenseNetteDepuisOctobre1998",
            windows("25", ("arrete-2020-10.txt",)), ["0.0234"], anchors("25", ("arrete-2020-10.txt",)),
            "coefficient de la dépense nette minimale, prêts souscrits à compter "
            "du 1er octobre 1998",
            "коэффициент минимального чистого расхода: займы с 1 октября 1998 года")
    decimal("CoefPlancherRessources", windows("26", ("arrete-2020-10.txt",)),
            ["16.25"], anchors("26", ("arrete-2020-10.txt",)),
            "coefficient déterminant le plancher de ressources de l'article D. 832-18",
            "коэффициент пола ресурсов ст. D. 832-18")
    for column, value in PARTS_ACCESSION.items():
        decimal(f"PartsAccession{column}", windows("D832-11", CCH_DOCS),
                [value, value], anchors("D832-11", CCH_DOCS),
                f"nombre de parts N du secteur accession, {FR[column]}",
                f"число долей N сектора приобретения, {RU[column]}")


# ==========================================================================
# АЛЛОКАЦИИ СЕКТОРА ACCESSION. D. 842-6: Af = K × (L + C − L0), где K считается
# по 2° D. 832-25, а L0 — по ВТОРОМУ абзацу D. 832-26. Обе отсылки те же, что у
# аллокаций сектора фойе, и это второй независимый свидетель той же пары норм.
#
# ГРАНИЦА ОХВАТА ВНУТРИ СТАТЬИ 33. Плафон выбирается ДАТОЙ «сертификата с
# датой» (`certificat daté`) — фактом дела, не месяцем права. Статья несёт
# двадцать один винтаж с 1 июля 1992 года; перенесены два последних (с
# 01.10.2017 и с 01.10.2019). Остальные в тексте есть, но в барем не перенесены:
# оценка ответит MISSING_PARAMETER_VALUE, а не значением чужого винтажа.
# Винтажи до 1 января 2002 года вдобавок выражены во ФРАНКАХ.
#
# ВТОРОЕ НАБЛЮДЕНИЕ О САМОМ ТЕКСТЕ (первое — в винтаже 13° ст. 18). В винтаже
# «сертификаты с 01/07/02» зоны III колонка C+1 несёт 2987,27 там, где соседние
# зоны того же винтажа дают 342,04 и 307,32, а соседние винтажи той же зоны —
# 283,86 и 290,72. Похоже на опечатку официального текста; винтаж в барем не
# перенесён, и пакет о нём ничего не утверждает.
# --- ст. 33: плафоны мензуальности аллокаций -----------------------------
# Столбцов ВОСЕМЬ, а не четыре, как у ст. 18: до пяти иждивенцев таблица
# перечисляет составы поимённо и лишь затем даёт надбавку.
PLAFONDS_MENSUALITE_AL = {
    "Cert2015": {
        "Zone1": ("311.48", "375.38", "403.62", "414.90", "426.57", "438.01", "447.29", "38.95"),
        "Zone2": ("273.26", "335.00", "362.64", "375.20", "388.14", "400.88", "429.26", "37.32"),
        "Zone3": ("256.34", "310.92", "338.98", "352.99", "367.21", "381.20", "409.61", "35.51"),
    },
    "Cert2017": {
        "Zone1": ("313.82", "378.20", "406.65", "418.01", "429.77", "441.30", "450.64", "39.24"),
        "Zone2": ("275.31", "337.51", "365.36", "378.01", "391.05", "403.89", "432.48", "37.60"),
        "Zone3": ("258.26", "313.25", "341.52", "355.64", "369.96", "384.06", "412.68", "35.78"),
    },
    "Cert2019": {
        "Zone1": ("314.76", "379.33", "407.87", "419.27", "431.06", "442.62", "452.00", "39.36"),
        "Zone2": ("276.14", "338.53", "366.46", "379.15", "392.22", "405.10", "433.78", "37.71"),
        "Zone3": ("259.04", "314.19", "342.55", "356.70", "371.07", "385.21", "413.92", "35.88"),
    },
}
COLONNES_MENSUALITE_AL = ("Isole", "Couples", "C1", "C2", "C3", "C4", "C5", "ParPersSupp")


def build_accession_allocations() -> None:
    """Барем главы VI: аллокации сектора приобретения жилья."""
    for vintage, zones in PLAFONDS_MENSUALITE_AL.items():
        for zone, values in zones.items():
            for column, value in zip(COLONNES_MENSUALITE_AL, values, strict=True):
                # Значения винтажей между редакциями не менялись, но строка
                # обязана быть в КАЖДОЙ закреплённой редакции статьи: иначе на
                # месяце права вне первой редакции параметра нет (измерено
                # 14.09.2026 на доле 75 % сособственников).
                money(f"PlafondMensualiteAL{vintage}{zone}{column}",
                      # У ст. 33 две версии на все закреплённые редакции: одна
                      # до 1 июля 2022 года, вторая после. Первая удостоверяется
                      # фрагментами двух редакций, вторая — трёх.
                      windows("33", ED_FOYER_DOCS),
                      [value, value], anchors("33", ED_FOYER_DOCS),
                      f"plafond de mensualité des allocations, {FR[vintage]}, "
                      f"{FR[zone]}, {FR[column]}",
                      f"плафон мензуальности аллокаций, {RU[vintage]}, "
                      f"{RU[zone]}, {RU[column]}")
    money("ForfaitChargesALAccessionBase", windows("34", ED_AL_DOCS),
          ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("34", ED_AL_DOCS),
          "montant forfaitaire des charges des allocations en secteur accession, "
          "bénéficiaire isolé ou couple sans personne à charge",
          "форфейт расходов аллокаций сектора приобретения: одинокое лицо либо пара без иждивенцев")
    money("ForfaitChargesALAccessionParPacSup", windows("34", ED_AL_DOCS),
          ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("34", ED_AL_DOCS),
          "montant forfaitaire des charges des allocations en secteur accession, "
          "par personne supplémentaire à charge",
          "форфейт расходов аллокаций сектора приобретения: за каждого дополнительного иждивенца")
    money("MinorationForfaitaireALAccession", windows("35", ("arrete-2020-10.txt",)),
          ["5"], anchors("35", ("arrete-2020-10.txt",)),
          "minoration forfaitaire retranchée de l'allocation en secteur accession",
          "форфейтная минорация аллокации сектора приобретения")
    money("SeuilVersementALAccession", windows("36", ("arrete-2020-10.txt",)),
          ["10"], anchors("36", ("arrete-2020-10.txt",)),
          "seuil de versement de l'allocation en secteur accession, avant CRDS",
          "порог выплаты аллокации сектора приобретения, до CRDS")
    # То же у ст. 37: см. замечание к ст. 24.
    decimal("PartCoproprietairePlafondAL", windows("37", ED_AL_DOCS),
            ["0.75"] * 7, anchors("37", ED_AL_DOCS),
            "part des plafonds de mensualités applicable aux copropriétaires (allocations)",
            "доля плафонов мензуальности для сособственников (аллокации)")
    money("ForfaitChargesCoproALIsole", windows("37", ED_AL_DOCS),
          ["26.99", "27.10", "28.05", "29.03", "29.98", "30.29", "30.64"], anchors("37", ED_AL_DOCS),
          "montant forfaitaire des charges des copropriétaires (allocations), bénéficiaire isolé",
          "форфейт расходов сособственника (аллокации): одинокое лицо")
    money("ForfaitChargesCoproALCouple", windows("37", ED_AL_DOCS),
          ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("37", ED_AL_DOCS),
          "montant forfaitaire des charges des copropriétaires (allocations), couple sans personne à charge",
          "форфейт расходов сособственника (аллокации): пара без иждивенцев")
    money("ForfaitChargesCoproALMajoration", windows("37", ED_AL_DOCS),
          ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("37", ED_AL_DOCS),
          "montant forfaitaire des charges des copropriétaires (allocations), majoration par personne à charge",
          "форфейт расходов сособственника (аллокации): надбавка за иждивенца")
    money("DepenseNetteMinimaleALAccession", windows("38", ("arrete-2020-10.txt",)),
          ["15"], anchors("38", ("arrete-2020-10.txt",)),
          "montant minimum de dépense nette de logement, allocations en secteur accession",
          "минимальный чистый расход на жильё: аллокации сектора приобретения")
    decimal("CoefDepenseNetteALAccession", windows("38", ("arrete-2020-10.txt",)),
            ["0.0234"], anchors("38", ("arrete-2020-10.txt",)),
            "coefficient de la dépense nette minimale du troisième alinéa de l'article D. 842-11",
            "коэффициент минимального чистого расхода третьего абзаца ст. D. 842-11")
    decimal("CoefPlancherRessourcesAL", windows("39", ("arrete-2020-10.txt",)),
            ["16.25"], anchors("39", ("arrete-2020-10.txt",)),
            "coefficient du plancher de ressources du 1° de l'article D. 842-12",
            "коэффициент пола ресурсов 1° ст. D. 842-12")
    money("ForfaitPlancherRessourcesAL", windows("39", ("arrete-2020-10.txt",)),
          ["3900"], anchors("39", ("arrete-2020-10.txt",)),
          "montant forfaitaire du plancher de ressources du 2° de l'article D. 842-12",
          "форфейтная сумма пола ресурсов 2° ст. D. 842-12")


# ==========================================================================
# ЗАМОРСКИЕ ТЕРРИТОРИИ (глава IX арретэ). Своих формул у режима НЕТ: статья 46
# ЗАМЕНЯЕТ отдельные значения глав III, VI и VII для Гваделупы, Гвианы,
# Мартиники, Реюньона, Майотты, Сен-Бартелеми и Сен-Мартена, а статья 47 делает
# то же для Сен-Пьера-и-Микелона. Поэтому территория — ВТОРАЯ ОСЬ барема рядом с
# месяцем права: параметр выбирается и датой, и территорией, а территория есть
# факт дела. Ось `legal_time` её выразить не может.
#
# ЧТО ИМЕННО ЗАМЕНЯЕТСЯ (ст. 46, редакция, применимая с 1 января 2023 года):
#   1° форфейт R0 ТОЛЬКО для домохозяйства с одним иждивенцем — 8 181 €;
#   2° a) форфейты расходов статей 9, 34 и 40 — 37,67 и 9,69;
#      b) суммы колокаторов и сособственников статей 16 и 37 — 19,38 / 37,67 / 9,69;
#   3° таблица ставок TF статьи 14 — своя, и в ней ЕСТЬ строка семи иждивенцев,
#      которой у метрополии нет вовсе (у неё таблица кончается шестью);
#   4° с 1 января 2022 года форфейт R0 Майотты равен заморскому.
# Плафоны найма и мензуальности ст. 46 НЕ заменяет — и дело Catala Гваделупы это
# подтверждает: его плафон 375,20 € есть строка ст. 33 метрополии.
# --- ст. 46 2°: форфейты расходов заморских территорий -------------------
# Значения по редакциям: 1 января 2023, 2024 и 2025 годов.
# Пять состояний: янв-2023, окт-2023, янв-2024, окт-2024, янв-2025. ФОРФЕЙТЫ
# меняются в ОКТЯБРЕ (и потому январское состояние повторяет октябрьское), а
# форфейт R0 — в ЯНВАРЕ. Обе группы стоят в одной статье 46, и именно поэтому у
# неё пять версий, а не три.
# Девять состояний ст. 46: окт-2020, окт-2021, янв-2022, июл-2022, янв-2023,
# окт-2023, янв-2024, окт-2024, янв-2025.
FORFAITS_OUTRE_MER = {
    "Base": ("36.25", "36.40", "36.40", "37.67",
             "37.67", "38.99", "38.99", "40.26", "40.26", "40.68", "41.15"),
    "ParPacSup": ("9.32", "9.36", "9.36", "9.69",
                  "9.69", "10.03", "10.03", "10.36", "10.36", "10.47", "10.59"),
}
FORFAITS_PARTAGE_OUTRE_MER = {
    "Isole": ("18.64", "18.72", "18.72", "19.38",
              "19.38", "20.06", "20.06", "20.71", "20.71", "20.93", "21.17"),
    "Couple": ("36.25", "36.40", "36.40", "37.67",
               "37.67", "38.99", "38.99", "40.26", "40.26", "40.68", "41.15"),
    "Majoration": ("9.32", "9.36", "9.36", "9.69",
                   "9.69", "10.03", "10.03", "10.36", "10.36", "10.47", "10.59"),
}
# --- ст. 46 3°: ставки TF заморских территорий ---------------------------
# Таблица TF заморских территорий НЕ переоценивалась: во всех трёх редакциях
# ст. 46 3° стоят те же десять значений. Строки всё равно заводятся по редакции
# на каждую — иначе вне окна первой параметр не подставится.
TAUX_FAMILLE_OUTRE_MER = {
    "Isole": ("0.0281",) * 11, "Couple": ("0.0299",) * 11, "1Pac": ("0.0238",) * 11,
    "2Pac": ("0.0217",) * 11, "3Pac": ("0.0194",) * 11, "4Pac": ("0.0180",) * 11,
    "5Pac": ("0.0169",) * 11, "6Pac": ("0.0162",) * 11,
    # Строка СЕМИ иждивенцев появилась лишь с 30 декабря 2022 года. До неё
    # таблица кончалась строкой «6 enfants ou 6 personnes et plus», и надбавки
    # сверх шести не было вовсе. Чтобы одна функция считала оба режима, ранние
    # состояния несут «ставку при семи» равной ставке шести, а надбавку — нулём:
    # это ПЕРЕСКАЗ строки «шесть и более», а не значение из текста, и потому
    # сказано здесь прямо. Проверяется сценарием на восьми иждивенцах.
    "7Pac": ("0.0162", "0.0162", "0.0162", "0.0162",
             "0.0167", "0.0167", "0.0167", "0.0167", "0.0167", "0.0167", "0.0167"),
    "Majoration": ("0.0000", "0.0000", "0.0000", "0.0000",
                   "-0.0006", "-0.0006", "-0.0006", "-0.0006", "-0.0006",
                   "-0.0006", "-0.0006"),
}
# --- ст. 47: форфейт R0 Сен-Пьера-и-Микелона (таблица целиком) -----------
ABATTEMENT_R0_SAINT_PIERRE = {
    "Isole": ("5272", "5335", "5507"), "Couple": ("7552", "7643", "7889"),
    "1Pac": ("9008", "9116", "9410"), "2Pac": ("9211", "9322", "9623"),
    "3Pac": ("9563", "9678", "9990"), "4Pac": ("9919", "10039", "10363"),
    "5Pac": ("10271", "10395", "10730"), "6Pac": ("10626", "10754", "11101"),
    "Majoration": ("350", "354", "365"),
}
# --- ст. 31 b) редакции, применимой с 1 июля 2022 года -------------------
#
# РЕДАКЦИЯ, КОТОРАЯ ЗАКРЫЛА ОТКРЫТЫЙ ВОПРОС. До неё статья 31 давала ОДИН набор
# ставок «mentionnés à l'article D. 832-26», и второй абзац приходилось считать
# тем же набором. Версия, применимая с 1 июля 2022 года, расщепила их явно:
# «a) Au premier alinéa … b) Au deuxième alinéa», и у второго абзаца СВОИ пять
# транш с другими ставками и другими границами. Именно они воспроизводят все три
# дела Catala, считавшиеся расхождением: 307,97 €, 267,90 € и 296,96 €.
#
# Строки заведены ТОЛЬКО этой редакцией: до 1 июля 2022 года закреплённый текст
# их не называет, и на более раннем месяце права параметр не подставится —
# оценка ответит MISSING_PARAMETER_VALUE, а не значением редакции, вступившей
# позже даты дела.
BORNES_L0_SECOND = ("1423.03", "2047.61", "2629.85", "4095.05")
TAUX_L0_SECOND = ("0.0000", "0.0240", "0.2080", "0.2320", "0.3280")


def build_outre_mer() -> None:
    """Глава IX: значения, заменяемые для заморских территорий."""
    money("ForfaitChargesBaseOutreMer", windows("46", ED_OM_DOCS),
          list(FORFAITS_OUTRE_MER["Base"]), anchors("46", ED_OM_DOCS),
          "montant forfaitaire des charges, outre-mer, bénéficiaire isolé ou "
          "couple sans personne à charge",
          "форфейт расходов, заморские территории: одинокое лицо либо пара без иждивенцев")
    money("ForfaitChargesParPacSupOutreMer", windows("46", ED_OM_DOCS),
          list(FORFAITS_OUTRE_MER["ParPacSup"]), anchors("46", ED_OM_DOCS),
          "montant forfaitaire des charges, outre-mer, par personne supplémentaire à charge",
          "форфейт расходов, заморские территории: за каждого дополнительного иждивенца")
    for column, value in FORFAITS_PARTAGE_OUTRE_MER.items():
        money(f"ForfaitChargesPartage{column}OutreMer",
              windows("46", ED_OM_DOCS), list(value), anchors("46", ED_OM_DOCS),
              f"montant forfaitaire des charges des colocataires et copropriétaires, "
              f"outre-mer, {FR[column]}",
              f"форфейт расходов колокаторов и сособственников, заморские территории, {RU[column]}")
    for column, value in TAUX_FAMILLE_OUTRE_MER.items():
        decimal(f"TauxFamille{column}OutreMer", windows("46", ED_OM_DOCS),
                list(value), anchors("46", ED_OM_DOCS),
                f"taux TF, outre-mer, {FR[column]}",
                f"ставка TF, заморские территории, {RU[column]}")
    money("AbattementR0UnePacOutreMer", windows("46", ED_OM_DOCS),
          # R0 переоценивается в январе: октябрьское состояние несёт прежнее число.
          ["7584", "7584", "7742", "8051",
           "8181", "8181", "8574", "8574", "8656", "8656", "8656"],
          with_derogation(anchors("46", ED_OM_DOCS)),
          "forfait R0, outre-mer, personne seule ou couple ayant une personne à charge",
          "форфейт R0, заморские территории: лицо или пара с одним иждивенцем")
    for column, value in ABATTEMENT_R0_SAINT_PIERRE.items():
        money(f"AbattementR0{column}SaintPierre", windows("47", ED_OM47_DOCS),
              list(value), anchors("47", ED_OM47_DOCS),
              f"forfait R0, Saint-Pierre-et-Miquelon, {FR[column]}",
              f"форфейт R0, Сен-Пьер-и-Микелон, {RU[column]}")
    # Предел шести иждивенцев жил до версии от 30.12.2022: четыре состояния
    # охвата, в которых ст. 46 1° ещё называет его.
    integer("LimitePacOutreMer",
            windows("46", ED_OM_LIMITE_DOCS), ["6", "6", "6", "6"],
            anchors("46", ED_OM_LIMITE_DOCS),
            "nombre maximal de personnes à charge prises en compte pour la "
            "majoration outre-mer (article 46, 1°)",
            "предел числа иждивенцев, принимаемых в расчёт надбавки на заморских "
            "территориях (ст. 46 1°)")
    for index, borne in enumerate(BORNES_L0_SECOND, start=1):
        money(f"BorneL0SecondAlinea{index}", windows("31", ("arrete-2023-01.txt",)),
              [borne], anchors("31", ("arrete-2023-01.txt",)),
              f"borne supérieure de la tranche {index} du deuxième alinéa de "
              "l'article D. 832-26 (à multiplier par le nombre de parts N)",
              f"верхняя граница {index}-й транши второго абзаца ст. D. 832-26 "
              "(умножается на число долей N)")
    for index, taux in enumerate(TAUX_L0_SECOND, start=1):
        decimal(f"TauxL0SecondAlinea{index}", windows("31", ("arrete-2023-01.txt",)),
                [taux], anchors("31", ("arrete-2023-01.txt",)),
                f"pourcentage de la tranche {index} du deuxième alinéa de l'article D. 832-26",
                f"ставка {index}-й транши второго абзаца ст. D. 832-26")


def build() -> None:
    for zone, columns in PLAFONDS.items():
        for column, values in columns.items():
            money(f"PlafondLoyer{zone}{column}", windows("7", ED_DOCS), list(values), anchors("7", ED_DOCS),
                  f"plafond de loyer, {FR[zone]}, {FR[column]}",
                  f"плафон найма, {RU[zone]}, {RU[column]}")
    for zone, columns in PLAFONDS_COLOC.items():
        for column, values in columns.items():
            money(f"PlafondColoc{zone}{column}", windows("16", ED_DOCS), list(values), anchors("16", ED_DOCS),
                  f"plafond de loyer en colocation, {FR[zone]}, {FR[column]}",
                  f"плафон найма при колокации, {RU[zone]}, {RU[column]}")
    for zone, values in CHAMBRE.items():
        money(f"PlafondChambre{zone}", windows("8", ED_DOCS), list(values), anchors("8", ED_DOCS),
              f"plafond de loyer d'une chambre, {FR[zone]}",
              f"плафон найма комнаты, {RU[zone]}")
    for zone, values in CHAMBRE_ONEREUX.items():
        money(f"PlafondChambreOnereux{zone}", windows("8", ED_DOCS), list(values), anchors("8", ED_DOCS),
              "plafond de loyer d'une chambre d'une personne âgée ou handicapée "
              f"hébergée à titre onéreux, {FR[zone]}",
              f"плафон найма комнаты размещённого за плату, {RU[zone]}")
    money("ForfaitChargesBase", windows("9", ED_DOCS), ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("9", ED_DOCS),
          "montant forfaitaire de charges, bénéficiaire isolé ou couple sans personne à charge", "форфейт расходов: одинокое лицо либо пара без иждивенцев")
    money("ForfaitChargesParPacSup", windows("9", ED_DOCS), ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("9", ED_DOCS),
          "montant forfaitaire de charges, par personne supplémentaire à charge", "форфейт расходов: за каждого дополнительного иждивенца")
    money("ForfaitChargesColocIsole", windows("16", ED_DOCS), ["26.99", "27.10", "28.05", "29.03", "29.98", "30.29", "30.64"], anchors("16", ED_DOCS),
          "montant forfaitaire de charges en colocation, bénéficiaire isolé", "форфейт расходов при колокации: одинокое лицо")
    money("ForfaitChargesColocCouple", windows("16", ED_DOCS), ["53.99", "54.22", "56.12", "58.08", "59.97", "60.59", "61.29"], anchors("16", ED_DOCS),
          "montant forfaitaire de charges en colocation, couple sans personne à charge", "форфейт расходов при колокации: пара без иждивенцев")
    money("ForfaitChargesColocParPac", windows("16", ED_DOCS), ["12.24", "12.29", "12.72", "13.17", "13.60", "13.74", "13.90"], anchors("16", ED_DOCS),
          "montant forfaitaire de charges en colocation, majoration par personne à charge", "форфейт расходов при колокации: надбавка за иждивенца")
    decimal("TauxParticipationMinimale", windows("13", ED_DOCS), ["0.085", "0.085", "0.085", "0.085", "0.085", "0.085", "0.085"], anchors("13", ED_DOCS),
            "part du loyer éligible et du forfait de charges dans P0", "доля суммы (L + C) в минимальном участии P0")
    money("PlancherParticipationMinimale", windows("13", ED_DOCS), ["35.24", "35.39", "36.63", "37.91", "39.15", "39.56", "40.01"], anchors("13", ED_DOCS),
          "montant minimum de la participation minimale P0", "нижняя граница минимального участия P0")
    for column, values in TAUX_FAMILLE.items():
        decimal(f"TauxFamille{column}", windows("14", ED_DOCS), list(values), anchors("14", ED_DOCS),
                f"taux TF, {FR[column]}", f"ставка TF, {RU[column]}")
    for column, values in LOYER_REFERENCE.items():
        money(f"LoyerReference{column}", windows("14", ED_DOCS), list(values), anchors("14", ED_DOCS),
              f"loyer de référence LR, {FR[column]}",
              f"эталонный наём LR, {RU[column]}")
    tranche_labels = {
        "SeuilBasRL": ("borne inférieure du rapport RL", "нижняя граница отношения RL"),
        "SeuilHautRL": ("borne supérieure du rapport RL", "верхняя граница отношения RL"),
        "TauxRLTrancheBasse": ("taux de la tranche de RL entre 45 % et 75 %",
                               "ставка ступени RL от 45 % до 75 %"),
        "TauxRLTrancheHaute": ("taux de la tranche de RL supérieure à 75 %",
                               "ставка ступени RL выше 75 %"),
    }
    for name, values in TRANCHES_RL.items():
        decimal(name, windows("14", ED_DOCS), list(values), anchors("14", ED_DOCS),
                *tranche_labels[name])
    for column, values in ABATTEMENT_R0.items():
        money(f"AbattementR0{column}", windows("15", ED_DOCS), list(values),
              with_derogation(anchors("15", ED_DOCS)),
              f"forfait R0, {FR[column]}", f"форфейт R0, {RU[column]}")
    for zone, premier, second in (("Zone1", "3.4", "4"), ("Zone2", "2.5", "3.1"),
                                  ("Zone3", "2.5", "3.1")):
        decimal(f"CoefDegressivite{zone}", windows("10", ("arrete-2020-10.txt",)), [premier], anchors("10", ("arrete-2020-10.txt",)),
                f"coefficient du plafond de dégressivité, {FR[zone]}",
                f"коэффициент плафона дегрессивности, {RU[zone]}")
        decimal(f"CoefSuppression{zone}", windows("10", ("arrete-2020-10.txt",)), [second], anchors("10", ("arrete-2020-10.txt",)),
                f"coefficient du plafond de suppression, {FR[zone]}",
                f"коэффициент плафона прекращения, {RU[zone]}")
    money("MinorationForfaitaire", windows("11", ("arrete-2020-10.txt",)), ["5"], anchors("11", ("arrete-2020-10.txt",)),
          "minoration forfaitaire retranchée de l'aide", "форфейтная минорация, вычитаемая из пособия")
    money("SeuilVersementAPL", windows("12", ("arrete-2020-10.txt",)), ["0"], anchors("12", ("arrete-2020-10.txt",)),
          "seuil de versement de l'aide personnalisée au logement", "порог выплаты APL")
    money("SeuilVersementAllocationLogement", windows("12", ("arrete-2020-10.txt",)), ["10"], anchors("12", ("arrete-2020-10.txt",)),
          "seuil de versement des allocations de logement", "порог выплаты жилищных аллокаций")
    # Ставка взносов ст. 14–17 — 0,5 % в ОБЕИХ закреплённых версиях ст. 19:
    # версия от 13.05.2010 и версия от 01.01.2020 расходятся только ставками
    # ст. 18 (2,2 % и 3 %), которых пакет не касается. Поэтому строки две, а
    # число одно — и месяц права до 2020 года не остаётся без ставки.
    # ст. 7 декрета 2021-1750: ALspm = ALt × (1 − (2026 − n)/8), n — год месяца
    # права; строки — значения формулы текста для четырёх лет монтажа
    decimal("CoefficientMonteeEnChargeSaintPierre",
            [("2022-01-01", "2023-01-01"), ("2023-01-01", "2024-01-01"),
             ("2024-01-01", "2025-01-01"), ("2025-01-01", "2026-01-01")],
            ["0.5", "0.625", "0.75", "0.875"],
            [["DEC20211750_ART7"]] * 4,
            "coefficient de montée en charge à Saint-Pierre-et-Miquelon: 1 − (2026 − n)/8",
            "коэффициент монтажа Сен-Пьер-и-Микелона: 1 − (2026 − n)/8")
    decimal("TauxCRDS", windows("19", ORD_DOCS), ["0.005", "0.005"],
            anchors("19", ORD_DOCS),
            "taux de la contribution pour le remboursement de la dette sociale", "ставка CRDS")
    decimal("PartRLSDeduite", windows("D823-16", ("cch.txt",)), ["0.98"], anchors("D823-16", ("cch.txt",)),
            "part de la réduction de loyer de solidarité déduite de l'aide", "доля RLS, вычитаемая из пособия")
    build_foyer()
    build_accession()
    build_accession_allocations()
    build_outre_mer()


def check_anchors() -> int:
    # Every row value must stand in the text of at least one anchor
    # fragment; formula-derived rows are listed, not failed.
    from bareme_builder import check_values_in_anchors, parse_fragments_law
    texts = parse_fragments_law(PACKAGE / "01-sources.law")
    missing, derived = check_values_in_anchors(SPECS, texts)
    for name, raw, start, where in missing:
        print(f"{name}@{start}: {raw} stands in no anchor text ({where})")
    print(f"anchor check: {sum(len(s.windows) for s in SPECS)} rows, "
          f"{len(missing)} missing, {len(derived)} formula-derived")
    return 1 if missing else 0


def main(argv: list[str]) -> int:
    build()
    if "--check-anchors" in argv:
        return check_anchors()
    OUT.mkdir(exist_ok=True)
    check = "--check" in argv
    problems = []
    for path, payload in WRITTEN.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != payload:
                problems.append(path.name)
        else:
            path.write_text(payload, encoding="utf-8")
    if check:
        for name in problems:
            print(f"{name}: расходится с транскрипцией барема")
        return 1 if problems else 0
    existing = {p.name for p in OUT.glob("*.lawparam.json")}
    written = {p.name for p in WRITTEN}
    for stale in sorted(existing - written):
        (OUT / stale).unlink()
        print(f"снят устаревший параметр {stale}")
    print(f"записано параметров: {len(WRITTEN)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
