#!/usr/bin/env python3
"""Сценарии прочтения RessourcesFractionsArrondiesCentime (D-82/D-84): двенадцатые и трети доходов R. 845-1/2.

Пишет два файла в tests/:
  ressources-division-lecture.lawtest       - каждое из 18 делений (4 двенадцатых, 14 третей) ПОД прочтением;
  ressources-division-sans-lecture.lawtest  - те же факты БЕЗ прочтения (неточное частное - RUNTIME_ERROR по
                                              INEXACT_DIVISION, SPEC 50/18; точное - прежний результат).

Ожидания - независимая реплика на дробях (fractions.Fraction, HALF_UP до сантима), без обращения к движку и
к тексту правил: «douzième» и «tiers» берутся из закреплённых sources/css/R845-1.txt и R845-2.txt. Исходные
суммы, ставки абатмана и плафоны - входы дела (в сценарии они задаются фактами), не нормы. Запуск:

    python3 corpus/laws/fr/prime-activite/tools/build_ressources_division.py [--check]

--check не пишет, а сравнивает с файлами на диске (расхождение - код 1).
"""
from __future__ import annotations

import sys
from fractions import Fraction
from math import floor
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
TESTS = PKG / "tests"

NEW = {"revue": "2026-06-01", "legal": "2026-06-15"}
OLD = {"revue": "2025-02-01", "legal": "2025-02-15"}


def half_up(x: Fraction) -> Fraction:
    """До сантима, полцента вверх (положительные суммы)."""
    return Fraction(floor(x * 100 + Fraction(1, 2)), 100)


def terminates(x: Fraction) -> bool:
    d = x.denominator
    for p in (2, 5):
        while d % p == 0:
            d //= p
    return d == 1


def dec(x: Fraction) -> str:
    """Дробь с конечной десятичной записью как число (минимум два знака)."""
    assert terminates(x), x
    places = 2
    while (x * 10**places).denominator != 1:
        places += 1
    n = int(x * 10**places)
    sign = "-" if n < 0 else ""
    s = str(abs(n)).rjust(places + 1, "0")
    return f"{sign}{s[:-places]}.{s[-places:]}"


def eur(x: Fraction) -> str:
    return dec(x) + " EUR"


def money(text: str) -> Fraction:
    return Fraction(text.replace(".", "")) / 100


# --- таблица дел --------------------------------------------------------------------------------
# kind: "n2"/"n1" - двенадцатая; "third" - треть, умноженная на (1 - t).
# facts: (отношение, аргументы после (d, revue)); None в revue-позиции - 0-арное по d.
def case(cid, rule, cat, era, kind, amount, facts, rate=None, note=""):
    return dict(id=cid, rule=rule, cat=cat, era=era, kind=kind, amount=money(amount), rate=rate, facts=facts, note=note)


A_RATE, B_RATE = Fraction(10, 100), Fraction(34, 100)

CASES = [
    # --- R. 845-1 (revenus agricoles) -------------------------------------------------------------
    case("rd-a1", "AgriBaseN2", "agri", NEW, "twelfth", "10000.00",
         [("n_2_agri_connu", []), ("benefices_agri_n_2", ["$"]), ("annee_agri_complete", [])]),
    case("rd-a2", "AgriBaseN1", "agri", NEW, "twelfth", "18000.10",
         [("n_1_agri_connu", []), ("benefices_agri_n_1", ["$"]), ("annee_agri_n_1_complete", [])]),
    case("rd-a3", "AgriFallbackAncienNonImposes", "agri", OLD, "third", "9000.01",
         [("regime_general", None), ("mois_revue", []), ("benefices_agri_non_imposes", []),
          ("recettes_agri_trimestre_precedent", ["$"]), ("abattement_64bis", ["%"])], rate=A_RATE),
    case("rd-a4", "AgriFallbackAncienIncomplet", "agri", OLD, "third", "4500.02",
         [("regime_general", None), ("mois_revue", []), ("annee_agri_incomplete", []),
          ("recettes_agri_trimestre_precedent", ["$"]), ("abattement_64bis", ["%"])], rate=A_RATE),
    case("rd-a5", "AgriFallbackNouveauNonImposes", "agri", NEW, "third", "3000.01",
         [("regime_general", None), ("mois_revue", []), ("benefices_agri_non_imposes", []),
          ("recettes_agri_m_4_m_2", ["$"]), ("abattement_64bis", ["%"])], rate=A_RATE),
    case("rd-a6", "AgriFallbackNouveauIncomplet", "agri", NEW, "third", "2100.05",
         [("regime_general", None), ("mois_revue", []), ("annee_agri_incomplete", []),
          ("recettes_agri_m_4_m_2", ["$"]), ("abattement_64bis", ["%"])], rate=A_RATE),
    case("rd-a7", "AgriOptionAncienne", "agri", OLD, "third", "1234.58",
         [("regime_general", None), ("mois_revue", []), ("demande_option_agri", []),
          ("recettes_agri_12_mois", ["40000.00 EUR"]), ("plafond_69_I", ["82800.00 EUR"]),
          ("recettes_agri_trimestre", ["9000.00 EUR"]), ("recettes_agri_trimestre_precedent", ["$"]),
          ("abattement_64bis", ["%"])], rate=A_RATE),
    case("rd-a8", "AgriOptionNouvelle", "agri", NEW, "third", "2500.07",
         [("regime_general", None), ("mois_revue", []), ("demande_option_agri", []),
          ("recettes_agri_12_mois", ["40000.00 EUR"]), ("plafond_69_I", ["82800.00 EUR"]),
          ("recettes_agri_trimestre", ["9000.00 EUR"]), ("recettes_agri_m_4_m_2", ["$"]),
          ("abattement_64bis", ["%"])], rate=A_RATE),
    # --- R. 845-2 (BIC/BNC) ------------------------------------------------------------------------
    case("rd-b1", "BicBaseN2", "bic", NEW, "twelfth", "12000.50",
         [("n_2_bic_connu", []), ("benefices_bic_n_2", ["$"]), ("annee_bic_complete", [])]),
    case("rd-b2", "BicBaseN1", "bic", NEW, "twelfth", "6000.07",
         [("n_1_bic_connu", []), ("benefices_bic_n_1", ["$"]), ("annee_bic_n_1_complete", [])]),
    case("rd-b3", "BicFallbackAncienNonImposes", "bic", OLD, "third", "7000.04",
         [("regime_general", None), ("mois_revue", []), ("benefices_bic_non_imposes", []),
          ("ca_bic_trimestre_precedent", ["$"]), ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b4", "BicFallbackAncienIncomplet", "bic", OLD, "third", "5200.12",
         [("regime_general", None), ("mois_revue", []), ("annee_bic_incomplete", []),
          ("ca_bic_trimestre_precedent", ["$"]), ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b5", "BicFallbackAncienSpecial", "bic", OLD, "third", "3100.21",
         [("regime_general", None), ("mois_revue", []), ("indep_special_bic", []),
          ("ca_bic_trimestre_precedent", ["$"]), ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b6", "BicFallbackNouveauNonImposes", "bic", NEW, "third", "8000.02",
         [("regime_general", None), ("mois_revue", []), ("benefices_bic_non_imposes", []),
          ("ca_bic_m_4_m_2", ["$"]), ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b7", "BicFallbackNouveauIncomplet", "bic", NEW, "third", "6400.13",
         [("regime_general", None), ("mois_revue", []), ("annee_bic_incomplete", []),
          ("ca_bic_m_4_m_2", ["$"]), ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b8", "BicFallbackNouveauSpecial", "bic", NEW, "third", "4300.22",
         [("regime_general", None), ("mois_revue", []), ("indep_special_bic", []),
          ("ca_bic_m_4_m_2", ["$"]), ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b9", "BicOptionAncienne", "bic", OLD, "third", "2900.32",
         [("regime_general", None), ("mois_revue", []), ("demande_option_bic", []),
          ("ca_bic_12_mois", ["40000.00 EUR"]), ("plafond_50_0_102ter", ["77700.00 EUR"]),
          ("ca_bic_trimestre", ["9000.00 EUR"]), ("ca_bic_trimestre_precedent", ["$"]),
          ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    case("rd-b10", "BicOptionNouvelle", "bic", NEW, "third", "3700.19",
         [("regime_general", None), ("mois_revue", []), ("demande_option_bic", []),
          ("ca_bic_12_mois", ["40000.00 EUR"]), ("plafond_50_0_102ter", ["77700.00 EUR"]),
          ("ca_bic_trimestre", ["9000.00 EUR"]), ("ca_bic_m_4_m_2", ["$"]),
          ("abattement_50_0_102ter", ["%"])], rate=B_RATE),
    # --- края D-82: частное конечное, но длиннее двух знаков; ничья на полцента ----------------------------
    case("rd-a1x", "AgriBaseN2", "agri", NEW, "twelfth", "24000.03",
         [("n_2_agri_connu", []), ("benefices_agri_n_2", ["$"]), ("annee_agri_complete", [])],
         note="частное точное, четыре знака"),
    case("rd-a1t", "AgriBaseN2", "agri", NEW, "twelfth", "24010.14",
         [("n_2_agri_connu", []), ("benefices_agri_n_2", ["$"]), ("annee_agri_complete", [])],
         note="ровно полцента, HALF_UP вверх, а HALF_EVEN дал бы вниз"),
    case("rd-b1x", "BicBaseN1", "bic", NEW, "twelfth", "18000.09",
         [("n_1_bic_connu", []), ("benefices_bic_n_1", ["$"]), ("annee_bic_n_1_complete", [])],
         note="частное точное, четыре знака"),
    case("rd-b1t", "BicBaseN2", "bic", NEW, "twelfth", "12000.06",
         [("n_2_bic_connu", []), ("benefices_bic_n_2", ["$"]), ("annee_bic_complete", [])],
         note="ровно полцента, HALF_UP вверх, а HALF_EVEN дал бы вниз"),
]


def replica(c):
    """(точное значение без округления | None, значение после прочтения) по дробям."""
    if c["kind"] == "twelfth":
        quotient = c["amount"] / 12
        return quotient, half_up(quotient)
    quotient = c["amount"] / 3
    one_minus_t = 1 - c["rate"]
    return quotient * one_minus_t, half_up(quotient) * one_minus_t


def head(c):
    return "revenu_agri" if c["cat"] == "agri" else "revenu_bic"


def ref(cid):
    return f'entity_ref("urn:fr:ppa:case:{cid}")'


def context(era):
    return (f"context {{ deadline_policy PPA_MOIS; decision_time @{era['legal']}T12:00:00Z; "
            f"knowledge_time @{era['legal']}T12:00:00Z; legal_time @{era['legal']}; timezone \"Europe/Paris\"; "
            "%s}")


def facts_block(c):
    era = c["era"]
    lines = []
    for n, (name, args) in enumerate(c["facts"], 1):
        label = f'{c["id"]}-{n:02d}'
        if args is None:
            call = f"{name}({ref(c['id'])})"
        else:
            vals = []
            for a in args:
                if a == "$":
                    vals.append(eur(c["amount"]))
                elif a == "%":
                    vals.append(dec(c["rate"]))
                else:
                    vals.append(a)
            call = f"{name}({', '.join([ref(c['id']), '@' + era['revue']] + vals)})"
        lines.append(f'        assert "{label}": {call} {{ origin case_input; }}')
    return "\n".join(lines)


def test_text(c, reading: bool) -> str:
    exact_value, rounded = replica(c)
    era = c["era"]
    ctx = context(era) % ("interpretation RessourcesFractionsArrondiesCentime; " if reading else "")
    if reading:
        value, status, truth = rounded, "COMPUTED", "TRUE_ONLY"
    elif terminates(c["amount"] / (12 if c["kind"] == "twelfth" else 3)):  # решает частное, не произведение с (1 - t)
        value, status, truth = exact_value, "COMPUTED", "TRUE_ONLY"
    else:
        value, status, truth = rounded, "RUNTIME_ERROR", "NEITHER"
    suffix = "" if reading else "-sans"
    name = f"urn:query:fr-ppa-ressources-division-{c['id']}{suffix}"
    return (f'test "{name}" {{\n    given {{\n        {ctx}\n{facts_block(c)}\n    }}\n'
            f'    evaluate truth({head(c)}({ref(c["id"])}, @{era["revue"]}, {eur(value)}));\n'
            f'    expect result_kind == PROPOSITION;\n    expect truth_status == {truth};\n'
            f'    expect evaluation_status == {status};\n}}\n')


def summary(c) -> str:
    exact_value, rounded = replica(c)
    if c["kind"] == "twelfth":
        calc = f"{dec(c['amount'])} / 12 = " + (dec(exact_value) if terminates(exact_value) else
                                                  f"{float(exact_value):.6f}...") + f" -> {dec(rounded)}"
    else:
        third = c["amount"] / 3
        calc = (f"{dec(c['amount'])} / 3 = {float(third):.6f}... -> {dec(half_up(third))}; x (1 - {dec(c['rate'])}) = "
                f"{dec(rounded)}")
    extra = f" ({c['note']})" if c["note"] else ""
    return f"//   {c['id']:7s} {c['rule']}: {calc}{extra};"


HEADER_COMMON = """language "law.core" version "0.2";
package fr.css.prime_activite version "0.1.0";
namespace "urn:fr:corpus:clir:ppa";
"""


def build() -> dict[str, str]:
    for c in CASES:
        exact_value, _ = replica(c)
        if c["kind"] == "third":
            assert (c["amount"] * 100) % 3 != 0, c["id"]
    reading_head = (
        "// D-82/D-84 (решение владельца, 08.10.2026): двенадцатые и трети доходов R. 845-1/2 под прочтением\n"
        "// RessourcesFractionsArrondiesCentime - частное округляется до сантима HALF_UP (практика CNAF, не текст), всегда, в т. ч.\n"
        "// точное частное длиннее двух знаков; произведение с (1 - t) остаётся точным. Ожидания - независимая реплика на дробях\n"
        "// (fractions.Fraction, HALF_UP), tools/build_ressources_division.py; «douzième» и «tiers» - из закреплённых\n"
        "// sources/css/R845-1.txt и R845-2.txt, суммы и ставки абатмана - входы дела. Новая редакция - обзор 2026-06-01\n"
        "// (M-4..M-2), прежняя - 2025-02-01 (трети квартала, предшествующего обзору), оба на общем режиме.\n"
        + "\n".join(summary(c) for c in CASES) + "\n")
    sans_head = (
        "// D-82/D-84 БЕЗ прочтения: те же факты, что в ressources-division-lecture.lawtest, прочтение не выбрано - поведение прежнее.\n"
        "// Неточное частное (бесконечная дробь) - RUNTIME_ERROR по INEXACT_DIVISION (SPEC 50/18: округление - только явной политикой);\n"
        "// конечное частное (rd-a1x, rd-b1x - четыре знака; rd-a1t, rd-b1t - три знака, ровно полцента) - точное значение без округления. Реплика - Fraction.\n")
    reading = reading_head + HEADER_COMMON + "\n" + "\n".join(test_text(c, True) for c in CASES)
    sans = sans_head + HEADER_COMMON + "\n" + "\n".join(test_text(c, False) for c in CASES)
    return {"ressources-division-lecture.lawtest": reading, "ressources-division-sans-lecture.lawtest": sans}


def main() -> int:
    out = build()
    if "--check" in sys.argv:
        bad = [n for n, t in out.items() if not (TESTS / n).exists() or (TESTS / n).read_text(encoding="utf-8") != t]
        for n in bad:
            print("расходится:", n)
        return 1 if bad else 0
    for n, t in out.items():
        (TESTS / n).write_text(t, encoding="utf-8")
        print("записан", TESTS / n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
