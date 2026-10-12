"""Перенос формульных дел OpenFisca-France 176.1.2 в fr.pf.paje (corpus/tools/foreign/openfisca_formulas.py).

Исполняется в их venv. Охват — 18 дел `tests/formulas/paje/paje_adoption.yaml`
(период 2025-07); прочие дела реестра (paje.yaml, paje_2018*.yaml,
paje_clca_colca.yaml, paje_prepare.yaml: 2013–2018) — класс (в) по дате, их
пишет драйвер.

Из их ВХОДА берутся только факты дела: состав (родители, дети), флаг
biactivite, база ресурсов `prestations_familiales_base_ressources` (R. 532-1),
флаг `adoption` и дата `date_adoption` (прибытие ребёнка в семью), дата
рождения. Их суммы, их BMAF и их плафоны в факты не идут.

Нормативные числа — только наши закреплённые:
  * BMAF — строка «Base mensuelle … à compter du 1er avril YYYY : X €»
    инструкций DSS в corpus/laws/fr/revalorisation/sources/ (как в образце pf-af);
  * плафон премии — таблица 3.1 «Plafonds de ressources applicables pour
    l'attribution de la prime à la naissance ou à l'adoption …» тех же
    инструкций DSS (документ «opposable», R. 531-1 al. 3: плафоны
    ревалоризуются 1 января ежегодно), строка по числу детей «à charge ou à
    naître», столбец «biactivité ou isolement» по L. 531-2 al. 3;
  * возрастной предел — R. 512-2 (fr.pf.core/sources/css/R512-2.txt:2,
    «jusqu'à l'âge de vingt ans»), предел L. 512-3 2° для L. 531-2 al. 1.

Даты по тексту, а не по их модели:
  * дата рассмотрения ситуации — R. 531-1 al. 5 «la situation de la famille est
    appréciée le premier jour du mois de l'arrivée de l'enfant au foyer» →
    первое число месяца прибытия; BMAF и плафон берутся на эту дату
    («montant en vigueur à la date d'examen», R. 531-1 al. 5 in fine).

Цель: их `paje_adoption` (семья, поток месяца) ↔ наш
`montant_primes_adoption_menage(m, total)` — сумма премий, присуждённых
домохозяйству за каждого усыновлённого ребёнка (L. 531-2 al. 1 «pour chaque
enfant adopté»). Их величина — выплата МЕСЯЦА, наша — присуждённая премия;
отображение верно только когда месяц цели лежит в окне выплаты по тексту:
D. 531-2 II «versée au plus tard le deuxième mois qui suit l'arrivée des
enfants au foyer» (sources/fr-pf-paje/D531-2-ed2021.txt:7) — от месяца
прибытия до второго месяца после него. Вне окна (их «TROP_TARD») дело не
переносится: месячного потока выплаты премии в пакете нет (граница
B-PAJE-DEADLINE-CALC), а их 0 за июль тексту не противоречит.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

PACKAGE = {"package": "fr.pf.paje", "version": "0.1.0", "namespace": "urn:fr:corpus:clir:pf-paje",
           "prefix": "fr-pf-paje", "timezone": "Europe/Paris", "world": ["fr.pf.paje"], "resolve": ["fr.pf.paje"],
           "context": ""}

TARGETS = {
    "paje_adoption": {"predicate": "montant_primes_adoption_menage", "kind": "Money", "zero": "absent"},
}

FR = Path(__file__).resolve().parents[2]
DSS = FR / "revalorisation/sources"
R512_2 = FR / "pf-core/sources/css/R512-2.txt"

_BMAF = re.compile(r"Base mensuelle de calcul des allocations familiales à compter du 1er avril (\d{4}) : ([\d ]+,\d\d) €")
_SECTION = re.compile(r"3\.1 Plafonds de ressources applicables pour l.attribution de la prime à la naissance ou\s+"
                      r"à l.adoption et de l.allocation de base à taux partiel pour la période du 1er janvier (\d{4})"
                      r"(.*?)Par enfant supplémentaire\s+\+?\s?(\d{1,3}(?: \d{3})?)\s{2,}\+?\s?(\d{1,3}(?: \d{3})?)\s*\n", re.S)
_ROW = re.compile(r"^\s*(\d) enfants?\s+(\d{1,3}(?: \d{3})?)\s{2,}(\d{1,3}(?: \d{3})?)\s*$", re.M)

QUALIFIED: dict = {}


def _euros(text: str) -> int:
    return int(text.replace(" ", ""))


def bmaf(month: str) -> str:
    """BMAF в силе в месяце `month`: последняя ревалоризация 1 апреля не позже него."""
    table = {}
    for path in sorted(DSS.glob("dss-*.txt")):
        for year, amount in _BMAF.findall(path.read_text(encoding="utf-8")):
            table[f"{year}-04"] = amount.replace(" ", "").replace(",", ".")
    keys = [k for k in sorted(table) if k <= month]
    if not keys:
        raise LookupError(f"BMAF на {month} не закреплена в revalorisation/sources")
    return table[keys[-1]]


def plafond_prime(year: int, children: int, majore: bool) -> int:
    """Плафон премии из таблицы 3.1 инструкции DSS на 1 января `year`."""
    for path in sorted(DSS.glob("dss-*.txt")):
        for match in _SECTION.finditer(path.read_text(encoding="utf-8")):
            if int(match.group(1)) != year:
                continue
            rows = {int(n): (_euros(a), _euros(b)) for n, a, b in _ROW.findall(match.group(2))}
            extra = (_euros(match.group(3)), _euros(match.group(4)))
            if sorted(rows) != [1, 2, 3, 4]:
                raise LookupError(f"{path.name}: таблица 3.1 разобрана не полностью: {rows}")
            column = 1 if majore else 0
            if children <= 4:
                return rows[children][column]
            return rows[4][column] + (children - 4) * extra[column]
    raise LookupError(f"таблица 3.1 DSS на 1 января {year} не закреплена в revalorisation/sources")


def _age_limit() -> int:
    text = R512_2.read_text(encoding="utf-8")
    if "jusqu'à l'âge de vingt ans" not in text:
        raise LookupError("R. 512-2: формулировка «jusqu'à l'âge de vingt ans» не найдена")
    return 20


def _month(day: dt.date) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def _add_months(month: str, n: int) -> str:
    y, m = map(int, month.split("-"))
    m += n
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


def _flatten_output(item: dict) -> None:
    """Их YAML adoption пишет выход по сущностям: `output: familles: famille: paje_adoption: {месяц: x}`.

    Драйвер читает `output` плоско (`переменная: значение`) и иначе счёл бы
    «familles» выходом без цели. Поднимаем переменные единственной семьи на
    верхний уровень — только формат записи их ожидания, значения не трогаются.
    Вызывается из facts() до того, как драйвер читает output (тот же объект дела).
    """
    output = item.get("output") or {}
    nested = output.get("familles")
    if isinstance(nested, dict) and len(nested) == 1:
        lifted = dict(next(iter(nested.values())))
        rest = {k: v for k, v in output.items() if k != "familles"}
        item["output"] = {**rest, **lifted}


def members(ctx, key: str) -> list[str]:
    return list(ctx.item["input"]["familles"]["famille"].get(key) or [])


def facts(ctx) -> list[str]:
    raw = ctx.item["input"]
    family = raw["familles"]["famille"]
    people = raw["individus"]
    parents, children = members(ctx, "parents"), members(ctx, "enfants")
    period = ctx.period
    if len(raw["familles"]) != 1:
        raise ctx.Skip("в деле больше одной семьи")
    _flatten_output(ctx.item)
    nbenf = ctx.value("af_nbenf")
    if nbenf != len(children):
        raise ctx.Skip(f"их af_nbenf={nbenf} ≠ число детей семьи {len(children)}: состав «à charge» не однозначен")
    resources = family["prestations_familiales_base_ressources"][period]
    biactivite = bool((family.get("biactivite") or {}).get(period, False))
    isolement = len(parents) == 1
    adopted = []
    for child in children:
        person = people[child]
        if (person.get("adoption") or {}).get(period) is True:
            arrival = (person.get("date_adoption") or {}).get("ETERNITY")
            if arrival is None:
                raise ctx.Skip(f"{child}: adoption=true без date_adoption")
            adopted.append((child, arrival if isinstance(arrival, dt.date) else dt.date.fromisoformat(str(arrival)),
                            person["date_naissance"]["ETERNITY"]))
    if not adopted:
        raise ctx.Skip("в деле нет усыновлённого ребёнка")
    arrivals = {_month(a) for _, a, _ in adopted}
    if len(arrivals) != 1:
        raise ctx.Skip("дети прибыли в разные месяцы: BMAF и плафон по дате рассмотрения у нас ключованы по ménage")
    arrival_month = arrivals.pop()
    last_month = _add_months(arrival_month, 2)
    if not (arrival_month <= period <= last_month):
        raise ctx.Skip(f"их paje_adoption — поток месяца {period}; прибытие {arrival_month}, окно выплаты по "
                       f"D. 531-2 II («au plus tard le deuxième mois qui suit l'arrivée») — {arrival_month}…{last_month}; "
                       "месячной выплаты премии в пакете нет (B-PAJE-DEADLINE-CALC), их 0 тексту не противоречит")
    examen = f"{arrival_month}-01"
    try:
        base = bmaf(arrival_month)
        ceiling = plafond_prime(int(arrival_month[:4]), len(children), isolement or biactivite)
        limit = _age_limit()
    except LookupError as why:
        raise ctx.Skip(str(why))
    out = [f"ressources_annuelles({{main}}, {resources} EUR)",
           f"plafond_prime_revalorise({{main}}, {ceiling} EUR)",
           f"bmaf_applicable({{main}}, {base} EUR)"]
    for child, arrival, birth in adopted:
        birth = birth if isinstance(birth, dt.date) else dt.date.fromisoformat(str(birth))
        twentieth = birth.replace(year=birth.year + limit)
        out += [f"adoption_arrivee({{main}}, {{m:{child}}})",
                f"date_examen_situation({{main}}, {{m:{child}}}, @{examen})"]
        if arrival < twentieth:
            out.append(f"condition_age_adoption({{m:{child}}})")
    return out
