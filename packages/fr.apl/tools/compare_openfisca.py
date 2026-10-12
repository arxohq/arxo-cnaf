#!/usr/bin/env python3
"""Сверка с OpenFisca-France: их КОД против нашего текста, дело за делом.

ЗАЧЕМ ОТДЕЛЬНЫЙ ИНСТРУМЕНТ. Числа в их файле дел (`aides_logement_reforme_
janvier_2021.yaml`) не равны тому, что выдаёт их собственный код: тесты держит
допуск `relative_error_margin: 0.01`. Сравнение с опубликованными числами
поэтому измеряет не их модель, а состояние их файла — и первый круг сверки
(13.09.2026) на этом получил два «необъяснённых» дела. Здесь считается их код.

ЧТО СЧИТАЕТСЯ. Три колонки: значение из их файла, значение их кода и наш итог
по тексту (тот же, что закреплён сценариями `tests/openfisca-*.lawtest`).
Плюс АТРИБУЦИЯ: реплика их чтения (пять отличий ниже) обязана воспроизводить
их код до цента — иначе остаётся неназванная причина, и отчёт об этом говорит.

ПЯТЬ ОТЛИЧИЙ ИХ МОДЕЛИ ОТ D. 823-16/17 (измерены, см. README пакета):
  1. шаг CRDS: `× (1 − 0,5 %)` вместо «вычесть взносы, округлить остаток к
     нижнему евро, вернуть взносы» (D. 823-16, абз. 10);
  2. порядок: вычет 98 % RLS ДО вилки взносов, тогда как в тексте — после;
  3. наём округляется до целого евро (`round_` в `aide_logement_loyer_reel`; numpy —
     половина к чётному: 214,50 → 214, найдено сверкой Ф8 16.09.2026);
  4. промежуточные P0 и Pp округляются до сантима (их денежный тип);
  5. все округления numpy `round_` — половина к чётному (наём, RL, TL): 0,001125 → 0,00112
     (найдено сверкой Ф8 16.09.2026 на синтетической выборке).

КАК ЗАПУСТИТЬ (их код в свой venv, репозиторий не трогается):

    python3 -m venv /tmp/of-venv
    /tmp/of-venv/bin/pip install \\
        "git+https://github.com/openfisca/openfisca-france@b2ab994331f6f35706bbe789ca015b422202530a"
    /tmp/of-venv/bin/python corpus/laws/fr/apl/tools/compare_openfisca.py <путь к их yaml>

Коммит закреплён: `b2ab9943` (OpenFisca-France 176.0.9). Их дела берутся из их
же репозитория по тому же коммиту — файл в наш корпус не копируется, это их
артефакт.
"""
from __future__ import annotations

import json
import re
import sys
import warnings
from decimal import (ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal as D,
                     getcontext)
from fractions import Fraction
from pathlib import Path

getcontext().prec = 50
PACKAGE = Path(__file__).resolve().parents[1]
#: Окно дел «AL Reforme 2019»: январь 2021 года.
LEGAL_TIME = "2021-01-15"
#: Дела их файла, которые пакет исполняет: секторный наём с известными
#: ресурсами. Вне сверки Cas 1 (ресурсы не названы в ожидании), Cas 9
#: (logement-foyer) и Cas 12 (студенческий форфейт) — три отдельных объёма.
CASES = [
    # (номер, наём, зона, пара, иждивенцы, ресурсы, RLS)
    (2, "608", 3, False, 0, "6900", "0"),
    (3, "306", 3, False, 0, "9600", "0"),
    (4, "579.50", 3, True, 2, "21600", "0"),
    (5, "214.38", 3, False, 0, "5000", "0"),
    (6, "267.66", 3, False, 0, "12500", "0"),
    (7, "527.37", 3, True, 1, "11500", "51.59"),
    (8, "545.93", 2, True, 4, "11400", "80.13"),
    (10, "300", 2, False, 0, "6200", "0"),
    (11, "500", 2, False, 0, "7700", "40.51"),
]


def param(name: str, at: str = LEGAL_TIME) -> D:
    """Значение параметра барема на дату — из закреплённого A3 пакета."""
    data = json.loads((PACKAGE / "bareme" / f"{name}.lawparam.json").read_text(encoding="utf-8"))
    best = None
    for row in data["values"]:
        start = row["valid"]["start"]
        if start <= at and (best is None or start > best[0]):
            best = (start, D(row["value"]["value"]))
    if best is None:
        raise SystemExit(f"{name}: на {at} значения нет — вне покрытия барема")
    return best[1]


def cents(value: D) -> D:
    return value.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def chain(loyer: D, zone: int, couple: bool, pac: int, ressources: D, rls: D,
          reading: str, stop: str | None = None, aah: bool = False) -> D | None:
    """Цепочка D. 823-16/17. `reading`: 'text' — дословно; 'openfisca' — их четыре отличия.
    `aah` — получатель AAH/AEEH: дегрессивность не применяется (D. 823-16; у их кода —
    признак `handicap` любого члена семьи, отличие 6 сверки Ф8).
    `stop="minoration"` (Ф8, `verify/ci/tools/compare_openfisca_bank.py`): вернуть величину
    сразу после минорации — до RLS и взносов; у их чтения это `aide_logement_montant_brut`
    (сантимы, не ниже нуля)."""
    zn = {1: "Zone1", 2: "Zone2", 3: "Zone3"}[zone]
    if reading == "openfisca":                      # отличие 3: наём до евро (numpy round_: половина к чётному)
        loyer = loyer.quantize(D("1"), rounding=ROUND_HALF_EVEN)
    plafond = (param(f"PlafondLoyer{zn}Couple") if couple else param(f"PlafondLoyer{zn}Isole")) \
        if pac == 0 else (param(f"PlafondLoyer{zn}UnePac")
                          + param(f"PlafondLoyer{zn}ParPacSup") * (pac - 1))
    loyer_eligible = min(loyer, plafond)
    charges = param("ForfaitChargesBase") + param("ForfaitChargesParPacSup") * pac
    minimale = max((loyer_eligible + charges) * param("TauxParticipationMinimale"),
                   param("PlancherParticipationMinimale"))
    taux_famille = (param("TauxFamilleCouple") if couple else param("TauxFamilleIsole")) \
        if pac == 0 else param(f"TauxFamille{min(pac, 6)}Pac")
    reference = (param("LoyerReferenceCouple") if couple else param("LoyerReferenceIsole")) \
        if pac == 0 else (param("LoyerReference1Pac")
                          + param("LoyerReferenceMajoration") * (pac - 1))
    # numpy `round_` — половина к чётному (отличие 5, сверка Ф8): у текста «arrondi» — половина вверх.
    half = ROUND_HALF_EVEN if reading == "openfisca" else ROUND_HALF_UP
    rapport = (loyer_eligible / reference).quantize(D("0.0001"), rounding=half)
    bas, haut = param("SeuilBasRL"), param("SeuilHautRL")
    taux_bas, taux_haut = param("TauxRLTrancheBasse"), param("TauxRLTrancheHaute")
    if rapport < bas:
        taux_loyer = D(0)
    elif rapport < haut:
        taux_loyer = taux_bas * (rapport - bas)
    else:
        taux_loyer = taux_bas * (haut - bas) + taux_haut * (rapport - haut)
    taux_loyer = taux_loyer.quantize(D("0.00001"), rounding=half)
    retenues = (ressources / 100).quantize(D("1"), rounding=ROUND_CEILING) * 100
    abattement = (param("AbattementR0Couple") if couple else param("AbattementR0Isole")) \
        if pac == 0 else param(f"AbattementR0{min(pac, 6)}Pac")
    participation = max(minimale,
                        minimale + (retenues - abattement) * (taux_famille + taux_loyer))
    if reading == "openfisca":                      # отличие 4: сантимная гранулярность
        participation = cents(participation)
    aide = loyer_eligible + charges - participation
    premier, second = param(f"CoefDegressivite{zn}"), param(f"CoefSuppression{zn}")
    if loyer > plafond * premier and not aah:
        if loyer >= plafond * second:
            aide = D(0)
        else:
            part = Fraction(plafond * second - loyer) / Fraction(plafond * second
                                                                 - plafond * premier)
            product = Fraction(aide) * part
            tail = product.denominator
            for factor in (2, 5):
                while tail % factor == 0:
                    tail //= factor
            if tail != 1 and reading == "text":
                # Норма велит уменьшать пропорционально и НЕ называет политики
                # округления: §50 отказывает (INEXACT_DIVISION), и пакет тоже.
                return None
            aide = D(product.numerator) / D(product.denominator)
    aide -= param("MinorationForfaitaire")
    if stop == "minoration":
        return aide if reading == "text" else max(cents(aide), D(0))
    if reading == "text":
        contributions = aide * param("TauxCRDS")
        aide = (aide - contributions).quantize(D("1"), rounding=ROUND_FLOOR) + contributions
        return cents(aide - rls * param("PartRLSDeduite"))
    aide = cents(aide) - rls * param("PartRLSDeduite")   # отличия 1 и 2
    return cents(aide * (1 - param("TauxCRDS")))


def their_code(path: Path) -> dict[int, tuple[D, D, D]]:
    """(итог их кода, их loyer_retenu, число из их файла) по номеру дела."""
    warnings.filterwarnings("ignore")
    try:
        import yaml
        from openfisca_core.simulations import SimulationBuilder
        from openfisca_france import FranceTaxBenefitSystem
    except ImportError as error:  # pragma: no cover — инструмент вне репозитория
        raise SystemExit(
            f"нужен их код в venv: {error}. Команды — в шапке этого файла") from error
    system = FranceTaxBenefitSystem()
    out = {}
    for case in yaml.safe_load(path.read_text(encoding="utf-8")):
        number = int(re.search(r"Cas (\d+)", case["name"]).group(1))
        period = str(case["period"])
        builder = SimulationBuilder()
        builder.set_default_period(period)
        simulation = builder.build_from_dict(system, case["input"])
        out[number] = (
            D(f"{float(simulation.calculate('aide_logement', period)[0]):.2f}"),
            D(f"{float(simulation.calculate('aide_logement_loyer_retenu', period)[0]):.2f}"),
            D(repr(case["output"].get("aide_logement"))),
        )
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    code = their_code(Path(argv[0]))
    print(f"{'дело':7} {'их файл':>9} {'их код':>9} {'наш текст':>11} "
          f"{'наш − их код':>13} {'%':>8}  реплика их чтения")
    unattributed = []
    for number, loyer, zone, couple, pac, ressources, rls in CASES:
        theirs, loyer_retenu, published = code[number]
        text = chain(D(loyer), zone, couple, pac, D(ressources), D(rls), "text")
        replica = chain(D(loyer), zone, couple, pac, D(ressources), D(rls), "openfisca")
        matches = replica == theirs
        if not matches:
            unattributed.append(number)
        if text is None:
            print(f"Cas {number:<3} {published:>9} {theirs:>9} {'ОТКАЗ':>11} "
                  f"{'—':>13} {'—':>8}  {replica} {'сходится' if matches else 'РАСХОДИТСЯ'}")
            continue
        delta = text - theirs
        percent = delta / theirs * 100
        print(f"Cas {number:<3} {published:>9} {theirs:>9} {text:>11} {delta:>13} "
              f"{percent:>+7.2f}%  {replica} {'сходится' if matches else 'РАСХОДИТСЯ'}")
    stale = [n for n in code if code[n][0] != code[n][2]]
    print(f"\nчисел их файла, не равных их же коду: {len(stale)} из {len(code)} "
          f"(держит допуск relative_error_margin 0,01)")
    print(f"дел без названной причины расхождения: {len(unattributed)}"
          + (f" — {unattributed}" if unattributed else " (атрибуция полная)"))
    return 1 if unattributed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
