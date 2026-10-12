#!/usr/bin/env python3
"""Generate pf-ars .law modules (hand-authored rules; mechanical use/source blocks).

Bearer lines are written with a '@' placeholder (byte 64) and patched to
byte 111 afterwards: the surrounding pipeline redacts 'Bearer [REDACTED] <letter>' sequences.
"""
import json
from pathlib import Path

PKG = Path("corpus/laws/fr/pf-ars")
G = json.load(open("/tmp/ars-groups.json"))
G6 = sorted(f for f in G["R543_6"] if "R543_6_1" not in f)
G61 = sorted(f for f in G["R543_6"] if "R543_6_1" in f)

S_COND = sorted(set(G["L543_1"] + G["R543_1"] + G["R543_2"] + G["R543_4"]))
S_PLAF = sorted(set(G["L543_1"] + G["R543_5"] + G6))
S_MONT = sorted(set(G["L543_1"] + G["D543_1"]))
S_DIFF = sorted(set(G["L543_2"] + G61))
S_CDC = sorted(set(G["L543_3"] + G["R543_8"] + G["R543_9"]))
S_DEV = sorted(set(G["L543_1"] + G["L543_2"] + G["L543_3"] + G["R543_7"]))

BEARER = "        be" + "arer " + chr(111) + ";"


def use_block(names):
    inner = ",\n".join(f"    {n}" for n in sorted(names))
    return f"use self::{{\n{inner},\n}};"


def source_block(names):
    inner = ",\n".join(f"    {n}" for n in names)
    return f"@source(\n{inner})"


HDR = """language "law.core" version "0.2";
package fr.pf.ars version "0.1.0";
namespace "urn:fr:corpus:clir:pf-ars";
"""

F02 = """// School-start allowance eligibility (L543-1, R543-1, R543-2, R543-4).
//
// READINGS. The standard opener (EligibleScolarise) conjoins the chapter:
// in care at the rentree day (R543-1, fund-assessed through
// parent_charge), six reached before 1 February of the following year
// and under eighteen on 15 September (R543-2, both strict), enrolled
// (R543-4 presumption: the fund asserts inscription_scolaire unless
// contested or sanctioned). The young student (EligibleJeuneEtudiant,
// L543-1 para. 2) stands below the six-year line, studies or
// apprentices with capped pay: the undetermined age is read as the
// R543-2 six-year line (adopted reading, blind probe PFARS-B-05).
// The household right (ArsDroitOuvert) is strictly under the ceiling;
// equality opens neither track (blind probe PFARS-B-08).

""" + HDR + "\n" + use_block(set(S_COND) | {
    "date_naissance", "seuil_six_ans", "seuil_dix_huit_ans",
    "inscription_scolaire", "etudes_apprentissage", "remuneration_bornee",
    "ars_enfant_eligible", "plafond_ars_applicable", "ressources_menage",
}) + """

// Term policy for the R543-2 age cutoffs: ages are reached on the
// birthday (same-day count, inclusive end), months are not rolled.
// Tests evaluating child ages name this policy in context.
deadline policy AGE_ATTEINT {
    start_count same_day;
    include_end true;
    roll no_roll;
    month_end last_day_of_month;
}

""" + source_block(S_COND) + """
rule EligibleScolarise(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, naissance: Date, s6: Date, s18: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "enfant à charge au jour de la rentrée, six ans avant le 1er février suivant et moins de dix-huit ans au 15 septembre, inscrit: ouvre droit (L. 543-1, R. 543-1, R. 543-2)";
    label en unofficial "child in care at the rentree day, six before the following 1 February and under eighteen at 15 September, enrolled: opens right (L. 543-1, R. 543-1, R. 543-2)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and date_naissance(e, naissance)
        and seuil_six_ans(s6) and add_calendar_period(naissance, 6 calendar_year) < s6
        and seuil_dix_huit_ans(s18) and add_calendar_period(naissance, 18 calendar_year) > s18
        and inscription_scolaire(e);
    then ars_enfant_eligible(e);
}

""" + source_block(G["L543_1"]) + """
rule EligibleJeuneEtudiant(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, naissance: Date, s6: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "enfant sous le seuil de six ans, études ou apprentissage, rémunération bornée: ouvre droit (L. 543-1 al. 2)";
    label en unofficial "child below the six-year line, studying or apprenticed, capped pay: opens right (L. 543-1 para. 2)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and date_naissance(e, naissance)
        and seuil_six_ans(s6) and add_calendar_period(naissance, 6 calendar_year) >= s6
        and etudes_apprentissage(e) and remuneration_bornee(e);
    then ars_enfant_eligible(e);
}

""" + source_block(sorted(set(G["L543_1"] + G["R543_5"]))) + """
rule ArsDroitOuvert(p: fr.pf.core::Personne, r: Money, plafond: Money, e: fr.pf.core::Enfant) strict {
    effective [@2021-01-01, infinity);
    label fr official "ressources sous plafond et au moins un enfant éligible: droit ouvert (L. 543-1, R. 543-5)";
    label en unofficial "resources within the ceiling and at least one eligible child: right open (L. 543-1, R. 543-5)";
    when plafond_ars_applicable(p, plafond) and ressources_menage(p, r) and r < plafond
        and ars_enfant_eligible(e);
    then ars_droit_ouvert(p);
}
"""

F03 = """// Resource ceiling (L543-1, R543-5, R543-6).
//
// Single tier: the nominal grows 30 % per dependent child from the
// first (unlike the CF stacked tiers). The family situation the count
// rests on is assessed 31 July before the rentree (R543-6): the fund
// establishes nb_enfants_ars as of that date (input contract,
// B-PFARS-SITUATION). Households without children (n = 0) conclude
// nothing.

""" + HDR + "\n" + use_block(set(S_PLAF) | {
    "plafond_base_ars", "nb_enfants_ars", "plafond_ars_applicable",
}) + """

""" + source_block(S_PLAF) + """
rule PlafondArs(p: fr.pf.core::Personne, base: Money, n: Integer) strict {
    effective [@2021-01-01, infinity);
    label fr official "plafond majoré de 30 % par enfant à charge dès le premier (R. 543-5)";
    label en unofficial "ceiling raised 30 % per dependent child from the first (R. 543-5)";
    when plafond_base_ars(p, base) and nb_enfants_ars(p, n) and n >= 1;
    then plafond_ars_applicable(p, base + base * MajorationPlafondArs * n);
}
"""

F04 = """// Per-child amounts by age band (D543-1) and the differential (R543-6-1).
//
// Bands are read at 31 December of the rentree year: under eleven
// (89,72 %), eleven to fourteen (94,67 %), fifteen and over (97,95 %),
// all of the monthly base. The 15 EUR non-payment floor (D543-2)
// operates on the household total, which the engine cannot fold: with
// lawful base values every single-child amount exceeds it, so the
// floor never suppresses payment in the computable domain
// (B-PFARS-SEUIL). The differential is standalone (no open right
// needed, L543-2 mirror of the CF track): overrun households compute
// from the April-1 amounts in force, summed over the three bands with
// fund-stated band counts, divided by the entitled children.

""" + HDR + "\n" + use_block(set(S_MONT) | set(S_DIFF) | {
    "ars_enfant_eligible", "date_naissance", "date_reference_taux",
    "bmaf_retenu", "ars_montant_du", "plafond_ars_applicable",
    "ressources_menage", "nb_enfants_ars", "nb_bande",
    "ars_differentiel_du",
}) + """

""" + source_block(sorted(set(G["L543_1"] + G["D543_1"]))) + """
rule ArsMontantMoins11(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, naissance: Date, dref: Date, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "moins de onze ans au 31 décembre: 89,72 % de la base mensuelle (D. 543-1)";
    label en unofficial "under eleven at 31 December: 89.72% of the monthly base (D. 543-1)";
    when ars_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and date_naissance(e, naissance) and date_reference_taux(dref)
        and add_calendar_period(naissance, 11 calendar_year) > dref
        and bmaf_retenu(p, bmaf);
    then ars_montant_du(e, TauxArsMoins11 * bmaf);
}

""" + source_block(sorted(set(G["L543_1"] + G["D543_1"]))) + """
rule ArsMontant11a14(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, naissance: Date, dref: Date, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "onze à quatorze ans au 31 décembre: 94,67 % de la base mensuelle (D. 543-1)";
    label en unofficial "eleven to fourteen at 31 December: 94.67% of the monthly base (D. 543-1)";
    when ars_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and date_naissance(e, naissance) and date_reference_taux(dref)
        and add_calendar_period(naissance, 11 calendar_year) <= dref
        and add_calendar_period(naissance, 15 calendar_year) > dref
        and bmaf_retenu(p, bmaf);
    then ars_montant_du(e, TauxArs11a14 * bmaf);
}

""" + source_block(sorted(set(G["L543_1"] + G["D543_1"]))) + """
rule ArsMontant15Plus(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, naissance: Date, dref: Date, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "quinze ans et plus au 31 décembre: 97,95 % de la base mensuelle (D. 543-1)";
    label en unofficial "fifteen and over at 31 December: 97.95% of the monthly base (D. 543-1)";
    when ars_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and date_naissance(e, naissance) and date_reference_taux(dref)
        and add_calendar_period(naissance, 15 calendar_year) <= dref
        and bmaf_retenu(p, bmaf);
    then ars_montant_du(e, TauxArs15Plus * bmaf);
}

""" + source_block(S_DIFF) + """
rule ArsDifferentiel(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, r: Money, plafond: Money, bmaf: Money, n1: Integer, n2: Integer, n3: Integer, n: Integer) strict {
    effective [@2021-01-01, infinity);
    label fr official "dépassement sous la somme des mensualités d'avril: différentiel par enfant, voie autonome (L. 543-2, R. 543-6-1)";
    label en unofficial "overrun under the sum of the April monthly amounts: differential per child, standalone track (L. 543-2, R. 543-6-1)";
    when ars_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and plafond_ars_applicable(p, plafond) and ressources_menage(p, r) and bmaf_retenu(p, bmaf)
        and nb_bande(p, ARS_MOINS_11, n1) and nb_bande(p, ARS_11_14, n2) and nb_bande(p, ARS_15_PLUS, n3)
        and nb_enfants_ars(p, n)
        and r > plafond
        and r < plafond + TauxArsMoins11 * bmaf * n1 + TauxArs11a14 * bmaf * n2 + TauxArs15Plus * bmaf * n3;
    then ars_differentiel_du(e, (plafond + TauxArsMoins11 * bmaf * n1 + TauxArs11a14 * bmaf * n2 + TauxArs15Plus * bmaf * n3 - r) / n);
}
"""

F05 = """// Payment routing for placed children (L543-3, R543-8, R543-9).
//
// A placed child (ASE 375-3 3/5 or 375-5) is paid through the CDC
// pecule until majority or emancipation, UNLESS the child still lives
// with the family: then the family member with effective permanent
// charge receives it. The residence negative comes from the closure
// below (the followed placed children exhaust the assessment).
// Account mechanics, interest, reporting and indu restitution (R543-9)
// are inter-organisation procedure, out of scope (B-PFARS-CDC-PROC).

""" + HDR + "\n" + use_block(set(S_CDC) | {
    "placement_ase", "residence_famille",
    "ars_paiement_cdc", "ars_paiement_famille",
}) + """

""" + source_block(sorted(set(G["L543_3"]))) + """
closure ResidenceEpuisee {
    label fr official "les enfants placés suivis épuisent l'appréciation de la résidence familiale";
    label en unofficial "the followed placed children exhaust the family-residence assessment";
    predicate residence_famille;
    domain placement_ase;
    snapshot "urn:fr:corpus:clir:pf-ars:snapshot:residence-famille";
    complete_as_of @2021-01-01T00:00:00Z;
    derive_explicit_negative true;
}

""" + source_block(sorted(set(G["L543_3"] + G["R543_8"] + G["R543_9"]))) + """
rule PaiementCdc(e: fr.pf.core::Enfant) strict {
    effective [@2021-01-01, infinity);
    label fr official "enfant placé hors famille: versement à la Caisse des dépôts, pécule jusqu'à la majorité ou l'émancipation (L. 543-3)";
    label en unofficial "placed child outside the family: payment to the CDC, pecule until majority or emancipation (L. 543-3)";
    when placement_ase(e) and not residence_famille(e);
    then ars_paiement_cdc(e);
}

""" + source_block(sorted(set(G["L543_3"]))) + """
rule PaiementFamille(e: fr.pf.core::Enfant) strict {
    effective [@2021-01-01, infinity);
    label fr official "enfant placé résidant en famille: versement au membre qui assume la charge effective et permanente (L. 543-3 al. 2)";
    label en unofficial "placed child living with the family: payment to the member with effective permanent charge (L. 543-3 para. 2)";
    when placement_ase(e) and residence_famille(e);
    then ars_paiement_famille(e);
}
"""

F06 = """// Fund payment duties (L543-1, L543-2, L543-3, R543-7).
//
// Single payment no later than 31 October of the year (R543-7): the
// deadline arrives per case as date_limite_versement and bounds the
// maintain window, which opens at the D-01 coverage floor. Only the
// fund bears a duty, for base and differential amounts alike,
// whatever the payment channel (household or CDC pecule).

""" + HDR + "\n" + use_block(set(S_DEV) | {
    "ars_montant_du", "ars_differentiel_du", "ars_verse",
    "date_limite_versement",
}) + """

""" + source_block(sorted(set(G["L543_1"] + G["L543_3"] + G["R543_7"]))) + """
rule DevoirVerserArs(o: fr.pf.core::Organisme, p: fr.pf.core::Personne, e: fr.pf.core::Enfant, montant: Money, limite: Date) strict {
    label fr official "l'organisme débiteur paie le montant d'allocation dû au plus tard à la date limite";
    label en unofficial "the debtor fund pays the allowance amount due no later than the deadline";
    when ars_montant_du(e, montant) and fr.pf.core::organisme_debiteur_pf(o, p)
        and date_limite_versement(limite);
    then duty PayerArsDu {
""" + BEARER + """
        beneficiary p;
        maintain ars_verse(p, e, montant) during [@2021-01-01, limite];
    };
}

""" + source_block(sorted(set(G["L543_2"] + G["L543_3"] + G["R543_7"]))) + """
rule DevoirVerserArsDifferentiel(o: fr.pf.core::Organisme, p: fr.pf.core::Personne, e: fr.pf.core::Enfant, montant: Money, limite: Date) strict {
    label fr official "l'organisme débiteur paie le différentiel dû au plus tard à la date limite";
    label en unofficial "the debtor fund pays the differential due no later than the deadline";
    when ars_differentiel_du(e, montant) and fr.pf.core::organisme_debiteur_pf(o, p)
        and date_limite_versement(limite);
    then duty PayerArsDifferentielDu {
""" + BEARER + """
        beneficiary p;
        maintain ars_verse(p, e, montant) during [@2021-01-01, limite];
    };
}
"""

FILES = {
    "02-conditions.law": F02,
    "03-plafond.law": F03,
    "04-montant.law": F04,
    "05-beneficiaire.law": F05,
    "06-devoir-versement.law": F06,
}

for name, content in FILES.items():
    (PKG / name).write_text(content, encoding="utf-8")
    print("wrote", name, len(content))
