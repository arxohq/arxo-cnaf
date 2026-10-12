#!/usr/bin/env python3
"""Generate pf-asf .lawtest suites (mechanical asserts; hand-checked amounts).

Stated BMAF everywhere is 400.00 EUR. 2021-window rows: simple 0.2813
(112.52), double 0.375 (150.00); from 2022-11-01: 0.422 (168.80) and
0.5625 (225.00). Differentials: 112.52 - pension, exact, no rounding.
"""
from pathlib import Path

PKG = Path("corpus/laws/fr/pf-asf")
TESTS = PKG / "tests"
FOREIGN = TESTS / "foreign" / "openfisca"

HDR22 = """language "law.core" version "0.2";
package fr.pf.asf version "0.1.0";
namespace "urn:fr:corpus:clir:pf-asf";
"""

CTX = """        context { deadline_policy %s; decision_time @%sT12:00:00Z; knowledge_time @%sT12:00:00Z; legal_time @%s; timezone "Europe/Paris"; }"""

P_MENS = "PAIEMENT_MENSUEL"
P_TRIM = "CONTROLE_TRIMESTRIEL"


def case_asserts(prefix, base, child, items):
    """items: list of (rel, kind, payload) where kind selects entity wiring."""
    out = []
    for i, (rel, kind, payload) in enumerate(items, 1):
        tag = f"{prefix}-{i:02d}"
        if kind == "pc":
            a = f'entity_ref("{base}"), entity_ref("{child}")'
        elif kind == "ch":
            a = f'entity_ref("{child}")'
            if payload:
                a += f", {payload}"
        elif kind == "hh":
            a = f'entity_ref("{base}")'
            if payload:
                a += f", {payload}"
        elif kind == "org":
            a = f'entity_ref("urn:fr:pf-asf:org:caisse"), entity_ref("{base}")'
        elif kind == "date":
            a = payload
        else:
            raise ValueError(kind)
        out.append(f'        assert "{tag}": {rel}({a}) {{ origin case_input; }}')
    return "\n".join(out)


def test(name, query, comment, ctx, givens, evals):
    return f"""// {comment}
{HDR22}
test "{query}" {{
    given {{
{ctx}
{givens}
    }}
{evals}
}}
"""


def ctx_for(policy, day):
    return CTX % (policy, day, day, day)


def ev_truth(pred, urn, amount=None, status="TRUE_ONLY"):
    arg = f'entity_ref("{urn}")' + (f", {amount}" if amount else "")
    return f"""    evaluate truth({pred}({arg}));
    expect result_kind == PROPOSITION;
    expect truth_status == {status};
    expect evaluation_status == COMPUTED;"""


def ev_truth2(pred, base, child, status="TRUE_ONLY"):
    return (f'    evaluate truth({pred}(entity_ref("{base}"), entity_ref("{child}")));\n'
            "    expect result_kind == PROPOSITION;\n"
            f"    expect truth_status == {status};\n"
            "    expect evaluation_status == COMPUTED;")


def ev_truth_d(pred, child, date, status="TRUE_ONLY"):
    return (f'    evaluate truth({pred}(entity_ref("{child}"), {date}));\n'
            "    expect result_kind == PROPOSITION;\n"
            f"    expect truth_status == {status};\n"
            "    expect evaluation_status == COMPUTED;")


def ev_positions(active):
    lines = ["    evaluate positions();",
             "    expect evaluation_status == COMPUTED;"]
    for pos in active:
        lines.append(f"    expect position({pos}, ACTIVE);")
    return "\n".join(lines)


def chain(base, child, motif=None, demande=True, manq=None, ouv=None,
          pension=None, bmaf="400.00 EUR", org=False):
    items = [("fr.pf.core::parent_charge", "pc", None),
             ("fr.pf.core::enfant_ouvre_droit", "ch", None)]
    if motif:
        items.append(("motif_asf", "ch", motif))
    if demande:
        items.append(("demande_asf", "ch", None))
    if manq:
        items.append(("manquement_debiteur", "ch", manq))
    if ouv:
        items.append(("mois_ouverture_asf", "date", ouv))
    if pension:
        items.append(("pension_recue", "ch", pension))
    if bmaf:
        items.append(("bmaf_retenu", "hh", bmaf))
    if org:
        items.append(("fr.pf.core::organisme_debiteur_pf", "org", None))
    return case_asserts("x", base, child, items)


def fix_tags(text, prefix):
    import re
    n = [0]

    def sub(m):
        n[0] += 1
        return f'assert "{prefix}-{n[0]:02d}":'
    return re.sub(r'assert "x-\d+":', sub, text, count=99)


FILES = {}


def add(path, content):
    FILES[path] = content


D = "2021-06-15"
# --- conditions ---
base = "urn:fr:pf-asf:case:orphelin-un-parent"
ch = base + "-e1"
add("tests/asf-orphelin-un-parent.lawtest", test(
    "orphelin-un-parent", "urn:query:fr-pf-asf-orphelin-un-parent",
    "Orphan of one parent, requested: eligible, no carence (L. 523-1 1°).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_UN_PARENT"), "oou"),
    ev_truth("asf_enfant_eligible", ch)))

base = "urn:fr:pf-asf:case:orphelin-deux-parents"
ch = base + "-e1"
add("tests/asf-orphelin-deux-parents.lawtest", test(
    "orphelin-deux-parents", "urn:query:fr-pf-asf-orphelin-deux-parents",
    "Orphan of both parents, requested: eligible, no carence (L. 523-1 1°).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_DEUX_PARENTS"), "ood"),
    ev_truth("asf_enfant_eligible", ch)))

base = "urn:fr:pf-asf:case:defaut-carence"
ch = base + "-e1"
add("tests/asf-defaut-carence.lawtest", test(
    "defaut-carence", "urn:query:fr-pf-asf-defaut-carence",
    "Single default March 2021, opening April 2021, requested: carence served, eligible (R. 523-1, D. 523-1).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01"), "odc"),
    ev_truth("asf_enfant_eligible", ch)))

base = "urn:fr:pf-asf:case:defaut-carence-non-atteinte"
ch = base + "-e1"
add("tests/asf-defaut-carence-non-atteinte.lawtest", test(
    "defaut-carence-non-atteinte", "urn:query:fr-pf-asf-defaut-carence-non-atteinte",
    "Single default March 2021, opening March 2021: carence not served, nothing opens (NEITHER probe).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-03-01"), "odn"),
    ev_truth("asf_enfant_eligible", ch, status="NEITHER")))

D22 = "2022-05-15"
base = "urn:fr:pf-asf:case:defaut-double-2022"
ch = base + "-e1"
add("tests/asf-defaut-double-2022.lawtest", test(
    "defaut-double-2022", "urn:query:fr-pf-asf-defaut-double-2022",
    "Double default March 2022, opening April 2022, requested: eligible under the pre-2022 5° (L. 523-1 5°).",
    ctx_for(P_MENS, D22),
    fix_tags(chain(base, ch, motif="DEFAUT_DOUBLE", manq="@2022-03-01",
                   ouv="@2022-04-01"), "odd"),
    ev_truth("asf_enfant_eligible", ch)))

base = "urn:fr:pf-asf:case:pension-partielle"
ch = base + "-e1"
add("tests/asf-pension-partielle.lawtest", test(
    "pension-partielle", "urn:query:fr-pf-asf-pension-partielle",
    "Pension 60 received, default March 2021, opening April 2021, requested: eligible (L. 523-1 4°).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="PENSION_PARTIELLE", manq="@2021-03-01",
                   ouv="@2021-04-01", pension="60.00 EUR"), "opp"),
    ev_truth("asf_enfant_eligible", ch)))

base = "urn:fr:pf-asf:case:demande-absente"
ch = base + "-e1"
add("tests/asf-demande-absente.lawtest", test(
    "demande-absente", "urn:query:fr-pf-asf-demande-absente",
    "Single default with carence served but no request: nothing opens (R. 523-2, NEITHER probe).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", demande=False,
                   manq="@2021-03-01", ouv="@2021-04-01"), "oda"),
    ev_truth("asf_enfant_eligible", ch, status="NEITHER")))

# --- cessation-couple ---
base = "urn:fr:pf-asf:case:cessation-active"
ch = base + "-e1"
add("tests/asf-cessation-active.lawtest", test(
    "cessation-active", "urn:query:fr-pf-asf-cessation-active",
    "Cessation June 2021, assessed June 2021: payment ends (L. 523-2).",
    ctx_for(P_MENS, D),
    fix_tags(case_asserts("x", base, ch, [
        ("fr.pf.core::parent_charge", "pc", None),
        ("fr.pf.core::enfant_ouvre_droit", "ch", None),
        ("mois_cessation_couple", "date", "@2021-06-01"),
        ("mois_droit_asf", "date", "@2021-06-01"),
    ]), "oca"),
    ev_truth2("asf_cessation_couple", base, ch)))

base = "urn:fr:pf-asf:case:cessation-avant"
ch = base + "-e1"
add("tests/asf-cessation-avant.lawtest", test(
    "cessation-avant", "urn:query:fr-pf-asf-cessation-avant",
    "Cessation June 2021, assessed May 2021: no cessation yet (NEITHER probe).",
    ctx_for(P_MENS, D),
    fix_tags(case_asserts("x", base, ch, [
        ("fr.pf.core::parent_charge", "pc", None),
        ("fr.pf.core::enfant_ouvre_droit", "ch", None),
        ("mois_cessation_couple", "date", "@2021-06-01"),
        ("mois_droit_asf", "date", "@2021-05-01"),
    ]), "ocb"),
    ev_truth2("asf_cessation_couple", base, ch, status="NEITHER")))

# --- montant: 0.2813 x 400 = 112.52; 0.375 x 400 = 150.00 ---
base = "urn:fr:pf-asf:case:montant-simple"
ch = base + "-e1"
add("tests/asf-montant-simple.lawtest", test(
    "montant-simple", "urn:query:fr-pf-asf-montant-simple",
    "Eligible orphan of one parent, stated BMAF 400: 0.2813 x 400 = 112.52 (R. 523-7).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_UN_PARENT", ouv="@2021-04-01"), "oms"),
    ev_truth("asf_montant_du", ch, "112.52 EUR")))

D23 = "2023-06-15"
base = "urn:fr:pf-asf:case:montant-double"
ch = base + "-e1"
add("tests/asf-montant-double.lawtest", test(
    "montant-double", "urn:query:fr-pf-asf-montant-double",
    "Eligible orphan of both parents at 2023, stated BMAF 400: 0.5625 x 400 = 225.00 (R. 523-7 2022 row).",
    ctx_for(P_MENS, D23),
    fix_tags(chain(base, ch, motif="ORPHELIN_DEUX_PARENTS", ouv="@2023-04-01"), "omd"),
    ev_truth("asf_montant_du", ch, "225.00 EUR")))

base = "urn:fr:pf-asf:case:montant-double-pre-2022"
ch = base + "-e1"
add("tests/asf-montant-double-pre-2022.lawtest", test(
    "montant-double-pre-2022", "urn:query:fr-pf-asf-montant-double-pre-2022",
    "Eligible orphan of both parents at 2021, stated BMAF 400: 0.375 x 400 = 150.00 (R. 523-7 2018 row).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_DEUX_PARENTS", ouv="@2021-04-01"), "omp"),
    ev_truth("asf_montant_du", ch, "150.00 EUR")))

D22B = "2022-12-15"
base = "urn:fr:pf-asf:case:montant-simple-2022-11"
ch = base + "-e1"
add("tests/asf-montant-simple-2022-11.lawtest", test(
    "montant-simple-2022-11", "urn:query:fr-pf-asf-montant-simple-2022-11",
    "Eligible orphan of one parent at Dec 2022, stated BMAF 400: 0.422 x 400 = 168.80 (R. 523-7 2022 row).",
    ctx_for(P_MENS, D22B),
    fix_tags(chain(base, ch, motif="ORPHELIN_UN_PARENT", ouv="@2022-04-01"), "om2"),
    ev_truth("asf_montant_du", ch, "168.80 EUR")))

# --- differentiel: standalone, no request, no opened right ---
base = "urn:fr:pf-asf:case:differentiel-sans-demande"
ch = base + "-e1"
add("tests/asf-differentiel-sans-demande.lawtest", test(
    "differentiel-sans-demande", "urn:query:fr-pf-asf-differentiel-sans-demande",
    "Pension 60, carence served, NO request: differential 112.52 - 60 = 52.52 fires standalone (L. 523-1 4°); no right opens.",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="PENSION_PARTIELLE", demande=False,
                   manq="@2021-03-01", ouv="@2021-04-01",
                   pension="60.00 EUR"), "ods"),
    ev_truth("asf_differentiel_du", ch, "52.52 EUR") + "\n" + ev_truth("asf_enfant_eligible", ch, status="NEITHER")))

base = "urn:fr:pf-asf:case:differentiel-pension-elevee"
ch = base + "-e1"
add("tests/asf-differentiel-pension-elevee.lawtest", test(
    "differentiel-pension-elevee", "urn:query:fr-pf-asf-differentiel-pension-elevee",
    "Pension 120 above the 112.52 single rate: no differential (0 EUR probe, NEITHER).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="PENSION_PARTIELLE", demande=False,
                   manq="@2021-03-01", ouv="@2021-04-01",
                   pension="120.00 EUR"), "odp"),
    ev_truth("asf_differentiel_du", ch, "0 EUR", status="NEITHER")))

# --- maintien-controle ---
base = "urn:fr:pf-asf:case:maintien-apres-carence"
ch = base + "-e1"
add("tests/asf-maintien-apres-carence.lawtest", test(
    "maintien-apres-carence", "urn:query:fr-pf-asf-maintien-apres-carence",
    "Default chain confirmed, opening April 2021, assessed May 2021: payment continued (R. 523-3).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01") + "\n" + case_asserts("x", base, ch, [
                       ("mois_droit_asf", "date", "@2021-05-01"),
                   ]), "oma"),
    ev_truth_d("asf_maintien_mois", ch, "@2021-05-01")))

base = "urn:fr:pf-asf:case:maintien-mois-ouverture"
ch = base + "-e1"
add("tests/asf-maintien-mois-ouverture.lawtest", test(
    "maintien-mois-ouverture", "urn:query:fr-pf-asf-maintien-mois-ouverture",
    "Opening month itself is not continuation: assessed April 2021 for an April opening gives NEITHER.",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01") + "\n" + case_asserts("x", base, ch, [
                       ("mois_droit_asf", "date", "@2021-04-01"),
                   ]), "omo"),
    ev_truth_d("asf_maintien_mois", ch, "@2021-04-01", status="NEITHER")))

base = "urn:fr:pf-asf:case:controle-quatrieme-mois"
ch = base + "-e1"
add("tests/asf-controle-quatrieme-mois.lawtest", test(
    "controle-quatrieme-mois", "urn:query:fr-pf-asf-controle-quatrieme-mois",
    "Opening April 2021 confirmed, control July 2021: fourth-month control due (R. 523-3-2).",
    ctx_for(P_TRIM, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01") + "\n" + case_asserts("x", base, ch, [
                       ("mois_controle_4m", "date", "@2021-07-01"),
                   ]), "ocq"),
    ev_truth("asf_controle_confirme", ch)))

# --- ouverture-dates ---
base = "urn:fr:pf-asf:case:ouverture-apres-carence"
ch = base + "-e1"
add("tests/asf-ouverture-apres-carence.lawtest", test(
    "ouverture-apres-carence", "urn:query:fr-pf-asf-ouverture-apres-carence",
    "Eligible default, opening April 2021 after the March default: opening confirmed (R. 523-1, D. 523-1).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01"), "ooa"),
    ev_truth("asf_ouverture_confirmee", ch)))

base = "urn:fr:pf-asf:case:ouverture-hors-etat"
ch = base + "-e1"
add("tests/asf-ouverture-hors-etat.lawtest", test(
    "ouverture-hors-etat", "urn:query:fr-pf-asf-ouverture-hors-etat",
    "Eligible orphan, stated opening April 2021, no default: opening confirmed without carence (D. 523-2).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_UN_PARENT",
                   ouv="@2021-04-01"), "ooh"),
    ev_truth("asf_ouverture_confirmee", ch)))

# --- devoir-versement ---
base = "urn:fr:pf-asf:case:devoir-versement-actif"
ch = base + "-e1"
add("tests/asf-devoir-versement-actif.lawtest", test(
    "devoir-versement-actif", "urn:query:fr-pf-asf-devoir-versement-actif",
    "112.52 due for the eligible orphan, payable no later than 2021-06-30: PayerAsfDu ACTIVE.",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_UN_PARENT", ouv="@2021-04-01",
                   org=True) + "\n" + case_asserts("x", base, ch, [
                       ("date_limite_versement", "date", "@2021-06-30"),
                   ]), "ova"),
    ev_positions(["PayerAsfDu"])))

base = "urn:fr:pf-asf:case:devoir-versement-differentiel"
ch = base + "-e1"
add("tests/asf-devoir-versement-differentiel.lawtest", test(
    "devoir-versement-differentiel", "urn:query:fr-pf-asf-devoir-versement-differentiel",
    "52.52 differential due without request, payable no later than 2021-06-30: PayerAsfDifferentielDu ACTIVE.",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="PENSION_PARTIELLE", demande=False,
                   manq="@2021-03-01", ouv="@2021-04-01",
                   pension="60.00 EUR", org=True) + "\n" + case_asserts("x", base, ch, [
                       ("date_limite_versement", "date", "@2021-06-30"),
                   ]), "ovd"),
    ev_positions(["PayerAsfDifferentielDu"])))

base = "urn:fr:pf-asf:case:devoir-controle-trimestriel"
ch = base + "-e1"
add("tests/asf-devoir-controle-trimestriel.lawtest", test(
    "devoir-controle-trimestriel", "urn:query:fr-pf-asf-devoir-controle-trimestriel",
    "Fourth-month control due, control deadline 2021-07-31: ControlerTrimestre ACTIVE.",
    ctx_for(P_TRIM, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01", org=True) + "\n" + case_asserts("x", base, ch, [
                       ("mois_controle_4m", "date", "@2021-07-01"),
                       ("date_limite_controle", "date", "@2021-07-31"),
                   ]), "ovc"),
    ev_positions(["ControlerTrimestre"])))

# --- foreign OpenFisca ports (tests/foreign/openfisca/) ---
# Periods are shaped to the 2021 window (D-01/D-15): OpenFisca runs at
# 2015/2018/2020 cannot execute against 2021-effective producers.
# OpenFisca numbers embed their BMAF; ours run on stated BMAF 400.
FB = "urn:fr:pf-asf:foreign:"

base = FB + "of-seuil-non-versement"
ch = base + "-e1"
add("tests/foreign/openfisca/of-seuil-non-versement.lawtest", test(
    "of-seuil-non-versement", "urn:query:fr-pf-asf-of-seuil-non-versement",
    "OpenFisca Seuil de non-versement (2020-01), period shaped to 2021: pension 112 against the 112.52 single rate gives a 0.52 differential. Their 0 is the 15 EUR floor (D. 523-3), which the engine cannot fold: class (c) divergence, B-PFASF-SEUIL.",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="PENSION_PARTIELLE", demande=False,
                   manq="@2021-03-01", ouv="@2021-04-01",
                   pension="112.00 EUR"), "ofn"),
    ev_truth("asf_differentiel_du", ch, "0.52 EUR")))

base = FB + "of-2015"
ch = base + "-e1"
add("tests/foreign/openfisca/of-2015.lawtest", test(
    "of-2015", "urn:query:fr-pf-asf-of-2015",
    "OpenFisca 2015 lone-parent case, period shaped to 2021 and ground shaped to orphan-of-one (unstated upstream): eligible, 112.52. Their 96 embeds their 2015 rate and BMAF: class (b).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="ORPHELIN_UN_PARENT"), "ofq"),
    ev_truth("asf_enfant_eligible", ch) + "\n" + ev_truth("asf_montant_du", ch, "112.52 EUR")))

base = FB + "of-limite-20-ans"
ch = base + "-e1"
add("tests/foreign/openfisca/of-limite-20-ans.lawtest", test(
    "of-limite-20-ans", "urn:query:fr-pf-asf-of-limite-20-ans",
    "OpenFisca 20-year age bar (2015-01), shaped: the upstream opener is withheld (their asf_elig_enfant false), so no ASF ground opens here. ASF per se carries no age bar; the bar is upstream: class (b).",
    ctx_for(P_MENS, D),
    fix_tags(case_asserts("x", base, ch, [
        ("fr.pf.core::parent_charge", "pc", None),
        ("motif_asf", "ch", "ORPHELIN_UN_PARENT"),
        ("demande_asf", "ch", None),
    ]), "ofl"),
    ev_truth("asf_enfant_eligible", ch, status="NEITHER")))

base = FB + "of-2018-04-cas1"
ch = base + "-e1"
add("tests/foreign/openfisca/of-2018-04-cas1.lawtest", test(
    "of-2018-04-cas1", "urn:query:fr-pf-asf-of-2018-04-cas1",
    "OpenFisca 2018-04 lone parent, period shaped to 2021, ground shaped to single default with carence: eligible, 112.52. Their 115.87 embeds their April 2018 BMAF: class (b).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01"), "of1"),
    ev_truth("asf_enfant_eligible", ch) + "\n" + ev_truth("asf_montant_du", ch, "112.52 EUR")))

base = FB + "of-2018-04-cas2"
ch1 = base + "-e1"
ch2 = base + "-e2"
add("tests/foreign/openfisca/of-2018-04-cas2.lawtest", test(
    "of-2018-04-cas2", "urn:query:fr-pf-asf-of-2018-04-cas2",
    "OpenFisca 2018-04 two children, shaped as cas1 per child: 112.52 each, independent per-child amounts. Their 231.74 embeds their BMAF: class (b).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch1, motif="DEFAUT_SIMPLE", manq="@2021-03-01",
                   ouv="@2021-04-01") + "\n" + chain(base, ch2, motif="DEFAUT_SIMPLE",
                   manq="@2021-03-01", ouv=None, bmaf=None), "of2"),
    ev_truth("asf_montant_du", ch1, "112.52 EUR") + "\n" + ev_truth("asf_montant_du", ch2, "112.52 EUR")))

base = FB + "of-2018-04-cas3"
ch = base + "-e1"
add("tests/foreign/openfisca/of-2018-04-cas3.lawtest", test(
    "of-2018-04-cas3", "urn:query:fr-pf-asf-of-2018-04-cas3",
    "OpenFisca 2018-04 pension 50, period shaped to 2021: differential 112.52 - 50 = 62.52. Their 65.87 embeds their BMAF: class (b).",
    ctx_for(P_MENS, D),
    fix_tags(chain(base, ch, motif="PENSION_PARTIELLE", demande=False,
                   manq="@2021-03-01", ouv="@2021-04-01",
                   pension="50.00 EUR"), "of3"),
    ev_truth("asf_differentiel_du", ch, "62.52 EUR")))

for path, content in FILES.items():
    (PKG / path).write_text(content, encoding="utf-8")
    print("wrote", path)
print("total:", len(FILES))
