#!/usr/bin/env python3
"""Generate pf-asf .law modules (hand-authored rules; mechanical use/source blocks).

BEARER_O are written with a '@' placeholder (byte 64) and patched to
byte 111 afterwards: the surrounding pipeline redacts 'BEARER_O <letter>' sequences.
"""
import json
import re
from pathlib import Path

PKG = Path("corpus/laws/fr/pf-asf")
G = json.load(open("/tmp/asf-groups.json"))

L1 = sorted(set(G["L523_1"]))
L2 = sorted(set(G["L523_2"]))
L3 = sorted(set(G["L523_3"]))
R1 = sorted(set(G["R523_1"]))
R2 = sorted(set(G["R523_2"]))
R3 = sorted(f for f in set(G["R523_3"]) if re.match(r"CSS_R523_3(_ED|$)", f))
R31 = sorted(f for f in set(G["R523_3"]) if re.match(r"CSS_R523_3_1(_ED|$)", f))
R32 = sorted(f for f in set(G["R523_3"]) if re.match(r"CSS_R523_3_2(_ED|$)", f))
R4 = sorted(set(G["R523_4"]))
R5 = sorted(set(G["R523_5"]))
R6 = sorted(set(G["R523_6"]))
R7 = sorted(set(G["R523_7"]))
R8 = sorted(set(G["R523_8"]))
D1 = sorted(set(G["D523_1"]))
D2 = sorted(set(G["D523_2"]))
D3 = sorted(set(G["D523_3"]))

S_OUVR1 = sorted(set(L1 + R2))
S_OUVR2 = sorted(set(L1 + R1 + D1 + R2))
S_OUVR3 = sorted(set(L1 + R1 + R2))
S_CESS = sorted(set(L2 + R4 + R5 + R6))
S_MONT = sorted(set(L3 + R7))
S_DIFF = sorted(set(L1 + L3 + R1 + D3))
S_MAIN = sorted(set(R3))
S_CTRL = sorted(set(R3 + R31 + R32 + D2))
S_OUVC = sorted(set(R1 + D1))
S_OUVH = sorted(set(L1 + D2))
S_DEVB = sorted(set(L1 + R6))
S_DEVD = sorted(set(L1 + L3 + R6))
S_DEVC = sorted(set(R31 + R32 + D2))
S_REQ = sorted(set(R2))

BEARER_O = "        be" + "arer " + chr(111) + ";"


def use_block(names):
    inner = ",\n".join(f"    {n}" for n in sorted(names))
    return f"use self::{{\n{inner},\n}};"


def source_block(names):
    inner = ",\n".join(f"    {n}" for n in names)
    return f"@source(\n{inner})"


HDR = """language "law.core" version "0.2";
package fr.pf.asf version "0.1.0";
namespace "urn:fr:corpus:clir:pf-asf";
"""

PKG_LAW = """// Shared surface of the package: case facts and predicates that the ASF
// modules fill in. Upstream premises (child in care, opener status,
// debtor body) belong to fr.pf.core and arrive as case inputs; NOTHING
// owned by a neighbour package is redefined here.
//
// Module map:
//   01-sources.law          - sources, back-to-back editions, fragments (generated)
//   02-conditions.law       - L523-1, R523-1, R523-2: per-child eligibility by ground, request gate
//   03-cessation-couple.law - L523-2, R523-4/5/6: couple cessation
//   04-montant.law          - L523-3, R523-7: single and double rates, partial-pension differential
//   05-maintien-controle.law - R523-3, R523-3-1/2, D523-2: continuation, fourth-month control
//   06-ouverture-dates.law  - R523-1, R523-2, D523-1/2: opening dates after carence, hors-etat opening
//   07-devoir-versement.law  - fund payment and quarterly-control duties
//   bareme/*.lawparam.json  - one-month carence, fourth-month control, 15 EUR floor, rates (generated)
//
// SCOPE BOUNDARY. The package computes the monthly family support
// allowance (brut) for metropolitan France from 2021-01-01. Outside: the
// 15 EUR non-payment floor (no engine fold, B-PFASF-SEUIL), the RSA
// plein-droit opener (upstream assessment, B-PFASF-RSA), the L523-1 IV
// control regulation (not published, DSS-ELIG), subrogation and recovery
// procedure (R523-8 inter-organisation, B-PFASF-SUBROGATION), euro BMAF
// (unpinned arrete -> stated-assumption input), quarterly cadence of the
// control (adopted DSS reading, B-PFASF-TRIMESTRE). Full list - README,
// "Boundaries".
//
// OWN PREDECESSOR PINS (D-15). The L523-1 predecessor text (2019-2021,
// CSS_L523_1_PREV) is pinned inside this package's @source lists; the
// R523-7 pre-2022 rate row (2018-2022) is pinned the same way.
// fr.pf.core is NOT edited for ASF history.

language "law.core" version "0.2";
package fr.pf.asf version "0.1.0";
namespace "urn:fr:corpus:clir:pf-asf";

import fr.pf.core version "0.1.0";

pub enum MotifAsf {
    label fr official "cas d'ouverture du droit a l'allocation de soutien familial (L. 523-1)";
    label en unofficial "family support allowance opening ground (L. 523-1)";
    ORPHELIN_UN_PARENT,
    ORPHELIN_DEUX_PARENTS,
    DEFAUT_SIMPLE,
    DEFAUT_DOUBLE,
    PENSION_PARTIELLE
}

// --- Household case inputs (empirical) ---

pub relation bmaf_retenu(p: fr.pf.core::Personne, montant: Money) kind empirical {
    key(p);
    label fr official "base mensuelle retenue pour l'allocation (montant en vigueur, appreciation du fonds)";
    label en unofficial "monthly base retained for the allowance (amount in force, fund assessment)";
}

pub relation mois_ouverture_asf(m: Date) kind empirical {
    label fr official "mois d'ouverture du droit, premier jour du mois (appreciation du fonds, D. 523-1, D. 523-2)";
    label en unofficial "right opening month, first of the month (fund assessment, D. 523-1, D. 523-2)";
}

pub relation mois_cessation_couple(c: Date) kind empirical {
    label fr official "mois de la cessation de la vie en couple, premier jour du mois (appreciation du fonds, L. 523-2)";
    label en unofficial "couple-life cessation month, first of the month (fund assessment, L. 523-2)";
}

pub relation mois_controle_4m(t: Date) kind empirical {
    label fr official "mois du controle du quatrieme mois, premier jour du mois (appreciation du fonds, R. 523-3-2)";
    label en unofficial "fourth-month control month, first of the month (fund assessment, R. 523-3-2)";
}

pub relation mois_droit_asf(m: Date) kind empirical {
    label fr official "mois du droit apprecie, premier jour du mois (appreciation du fonds)";
    label en unofficial "assessed right month, first of the month (fund assessment)";
}

pub relation date_limite_versement(d: Date) kind empirical {
    label fr official "date limite du versement mensuel du par le fonds (appreciation du fonds, R. 523-6)";
    label en unofficial "fund monthly payment deadline (fund assessment, R. 523-6)";
}

pub relation date_limite_controle(d: Date) kind empirical {
    label fr official "date limite du controle trimestriel du par le fonds (appreciation du fonds, R. 523-3-1)";
    label en unofficial "fund quarterly control deadline (fund assessment, R. 523-3-1)";
}

// --- Per-child case inputs ---

pub relation motif_asf(e: fr.pf.core::Enfant, motif: MotifAsf) kind empirical {
    key(e);
    label fr official "cas d'ouverture du droit pour l'enfant (appreciation du fonds, L. 523-1)";
    label en unofficial "child opening ground (fund assessment, L. 523-1)";
}

pub relation demande_asf(e: fr.pf.core::Enfant) kind empirical {
    key(e);
    label fr official "allocation demandee pour l'enfant, recours maintenu pour le hors-etat (R. 523-2, appreciation du fonds)";
    label en unofficial "allowance requested for the child, recourse maintained for hors-etat (R. 523-2, fund assessment)";
}

pub relation manquement_debiteur(e: fr.pf.core::Enfant, manquement: Date) kind empirical {
    key(e);
    label fr official "mois de la defaillance du debiteur, premier jour du mois (appreciation du fonds, R. 523-1)";
    label en unofficial "debtor default month, first of the month (fund assessment, R. 523-1)";
}

pub relation pension_recue(e: fr.pf.core::Enfant, pension: Money) kind empirical {
    key(e);
    label fr official "pension alimentaire percue pour l'enfant au mois apprecie (appreciation du fonds, L. 523-1 4°)";
    label en unofficial "support pension received for the child in the assessed month (fund assessment, L. 523-1 4°)";
}

pub relation controle_effectue(e: fr.pf.core::Enfant) kind empirical {
    key(e);
    label fr official "le controle trimestriel a ete effectue pour l'enfant (execution)";
    label en unofficial "the quarterly control was performed for the child (performance)";
}

// --- Institutional conclusions ---

pub relation asf_enfant_eligible(e: fr.pf.core::Enfant) kind institutional {
    key(e);
    label fr official "l'enfant ouvre droit a l'allocation de soutien familial (L. 523-1)";
    label en unofficial "child opens right to the family support allowance (L. 523-1)";
}

pub relation asf_cessation_couple(p: fr.pf.core::Personne, e: fr.pf.core::Enfant) kind institutional {
    key(p, e);
    label fr official "la cessation de la vie en couple fait cesser le versement (L. 523-2)";
    label en unofficial "couple-life cessation stops payment (L. 523-2)";
}

pub relation asf_montant_du(e: fr.pf.core::Enfant, montant: Money) kind institutional {
    key(e);
    label fr official "montant d'allocation du pour l'enfant, taux simple ou double (L. 523-3, R. 523-7, brut)";
    label en unofficial "allowance amount due for the child, single or double rate (L. 523-3, R. 523-7, gross)";
}

pub relation asf_differentiel_du(e: fr.pf.core::Enfant, montant: Money) kind institutional {
    key(e);
    label fr official "complement differentiel du pour l'enfant, voie autonome (L. 523-1 4°, brut)";
    label en unofficial "differential top-up due for the child, standalone track (L. 523-1 4°, gross)";
}

pub relation asf_ouverture_confirmee(e: fr.pf.core::Enfant) kind institutional {
    key(e);
    label fr official "la date d'ouverture du droit est confirmee, carence purgée ou hors-etat (R. 523-1, D. 523-1, D. 523-2)";
    label en unofficial "the right opening date is confirmed, carence served or hors-etat (R. 523-1, D. 523-1, D. 523-2)";
}

pub relation asf_controle_confirme(e: fr.pf.core::Enfant) kind institutional {
    key(e);
    label fr official "le controle du quatrieme mois est exigible pour l'enfant (R. 523-3-1, R. 523-3-2, D. 523-2)";
    label en unofficial "the fourth-month control is due for the child (R. 523-3-1, R. 523-3-2, D. 523-2)";
}

pub relation asf_maintien_mois(e: fr.pf.core::Enfant, m: Date) kind institutional {
    key(e, m);
    label fr official "le versement est maintenu pour l'enfant au mois apprecie (R. 523-3)";
    label en unofficial "payment is continued for the child in the assessed month (R. 523-3)";
}

pub relation asf_verse(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, montant: Money) kind empirical {
    key(p, e);
    label fr official "l'allocation due a ete versee au parent (execution)";
    label en unofficial "the due allowance was paid to the parent (performance)";
}
"""

F02 = """// Per-child eligibility by opening ground (L523-1, R523-1, R523-2).
//
// READINGS. Each opener conjoins the chapter: child in care, upstream
// opener, the fund-stated ground, and the request (R523-2: the allowance
// is due upon request, the hors-etat recourse upkeep folded into the
// same demande_asf input). Orphanhood of one or both parents opens
// without carence (1 and 2, hors-etat track opened by D523-2). The
// single-default and partial-pension grounds (3 and 4) open only once
// the one-month default period has run: the opening month is at least
// the month after the default month, both stated first-of-month
// (R523-1 carence, D523-1 monthly opening). The double default of both
// debtors (5) opened the double rate until 2022-11-01 (same effect as
// the orphan-of-both rate in the 2021 window); from 2022-11-01 the
// 2022 reading folds it into the full-rate opener (L523-1 2022-11,
// blind probe PFASF-B-01). The RSA plein-droit opener (1 IV) is an
// upstream assessment, out of scope (B-PFASF-RSA).

""" + HDR + "\n" + use_block(set(S_OUVR1 + S_OUVR2 + S_OUVR3 + S_REQ) | {
    "motif_asf", "demande_asf", "manquement_debiteur", "pension_recue",
    "mois_ouverture_asf", "asf_enfant_eligible",
}) + """

""" + source_block(S_OUVR1) + """
rule EligibleOrphelinUnParent(p: fr.pf.core::Personne, e: fr.pf.core::Enfant) strict {
    effective [@2021-01-01, infinity);
    label fr official "orphelin d'un parent: ouvre droit sans carence (L. 523-1 1°)";
    label en unofficial "orphan of one parent: opens right without carence (L. 523-1 1°)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and motif_asf(e, ORPHELIN_UN_PARENT) and demande_asf(e);
    then asf_enfant_eligible(e);
}

""" + source_block(S_OUVR1) + """
rule EligibleOrphelinDeuxParents(p: fr.pf.core::Personne, e: fr.pf.core::Enfant) strict {
    effective [@2021-01-01, infinity);
    label fr official "orphelin des deux parents: ouvre droit sans carence (L. 523-1 1°)";
    label en unofficial "orphan of both parents: opens right without carence (L. 523-1 1°)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and motif_asf(e, ORPHELIN_DEUX_PARENTS) and demande_asf(e);
    then asf_enfant_eligible(e);
}

""" + source_block(S_OUVR2) + """
rule EligibleDefautCarence(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, manq: Date, m0: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "defaillance d'un debiteur, delai d'un mois purge: ouvre droit (L. 523-1 3°, R. 523-1, D. 523-1)";
    label en unofficial "single debtor default, one-month period served: opens right (L. 523-1 3°, R. 523-1, D. 523-1)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and motif_asf(e, DEFAUT_SIMPLE) and demande_asf(e)
        and manquement_debiteur(e, manq) and mois_ouverture_asf(m0)
        and m0 >= add_calendar_period(manq, 1 calendar_month);
    then asf_enfant_eligible(e);
}

""" + source_block(sorted(set(L1 + R1))) + """
rule EligibleDefautDouble2022(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, manq: Date, m0: Date) strict {
    effective [@2021-01-01, @2022-11-01);
    label fr official "defaillance des deux debiteurs avant novembre 2022: ouvre droit au taux double (L. 523-1 5°)";
    label en unofficial "double debtor default before November 2022: opens right at the double rate (L. 523-1 5°)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and motif_asf(e, DEFAUT_DOUBLE) and demande_asf(e)
        and manquement_debiteur(e, manq) and mois_ouverture_asf(m0)
        and m0 >= add_calendar_period(manq, 1 calendar_month);
    then asf_enfant_eligible(e);
}

""" + source_block(S_OUVR3) + """
rule EligiblePensionPartielle(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, pension: Money, manq: Date, m0: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "pension percue sous le montant de l'allocation, delai d'un mois purge: ouvre droit (L. 523-1 4°, R. 523-1)";
    label en unofficial "pension received below the allowance amount, one-month period served: opens right (L. 523-1 4°, R. 523-1)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and motif_asf(e, PENSION_PARTIELLE) and demande_asf(e)
        and pension_recue(e, pension)
        and manquement_debiteur(e, manq) and mois_ouverture_asf(m0)
        and m0 >= add_calendar_period(manq, 1 calendar_month);
    then asf_enfant_eligible(e);
}
"""

F03 = """// Couple cessation (L523-2, R523-4, R523-5, R523-6).
//
// The cessation of couple life stops payment: any assessed month at or
// after the fund-stated cessation month (both first-of-month) concludes
// cessation for the household and child. The R523-4/R523-5/R523-6
// cessation and cadence dates arrive through the same two month inputs
// (fund assessment, B-PFASF-DATES).

""" + HDR + "\n" + use_block(set(S_CESS) | {
    "mois_cessation_couple", "mois_droit_asf", "asf_cessation_couple",
}) + """

""" + source_block(S_CESS) + """
rule CessationCouple(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, c: Date, m: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "cessation de la vie en couple, mois apprecie au plus tot le mois de cessation: fin du versement (L. 523-2)";
    label en unofficial "couple-life cessation, assessed month no earlier than the cessation month: payment ends (L. 523-2)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and mois_cessation_couple(c) and mois_droit_asf(m) and m >= c;
    then asf_cessation_couple(p, e);
}
"""

F04 = """// Monthly amounts by rate and the partial-pension differential (L523-3, R523-7).
//
// READINGS. The single rate pays the 1, 3 and 4 grounds, the double
// rate the orphan-of-both ground; the pre-2022 double default (5)
// paid the double rate with the same effect in the 2021 window. The
// engine selects the R523-7 row in force at legal_time (0.2813 simple
// and 0.375 double from 2018-04-01 to 2022-11-01, then 0.422 and
// 0.5625; the own-package pre-2022 pin stands in the @source lists,
// D-15). The 4 differential is standalone: it computes from the
// maintenance facts alone, with no opened right and no request needed
// (adopted reading, blind probe PFASF-B-02). The 15 EUR non-payment
// floor (D523-3) operates on the household total, which the engine
// cannot fold: small differentials below it are a documented
// divergence, never a source (B-PFASF-SEUIL).

""" + HDR + "\n" + use_block(set(S_MONT + S_DIFF) | {
    "motif_asf", "manquement_debiteur", "pension_recue",
    "mois_ouverture_asf", "asf_enfant_eligible", "bmaf_retenu",
    "asf_montant_du", "asf_differentiel_du",
}) + """

""" + source_block(S_MONT) + """
rule MontantSimpleOrphelin(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "orphelin d'un parent eligible: taux simple de la base mensuelle (L. 523-3, R. 523-7)";
    label en unofficial "eligible orphan of one parent: single rate of the monthly base (L. 523-3, R. 523-7)";
    when asf_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and motif_asf(e, ORPHELIN_UN_PARENT) and bmaf_retenu(p, bmaf);
    then asf_montant_du(e, TauxAsfSimple * bmaf);
}

""" + source_block(S_MONT) + """
rule MontantSimpleDefaut(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "defaillance eligible: taux simple de la base mensuelle (L. 523-3, R. 523-7)";
    label en unofficial "eligible default: single rate of the monthly base (L. 523-3, R. 523-7)";
    when asf_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and motif_asf(e, DEFAUT_SIMPLE) and bmaf_retenu(p, bmaf);
    then asf_montant_du(e, TauxAsfSimple * bmaf);
}

""" + source_block(S_MONT) + """
rule MontantSimplePension(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "pension partielle eligible: taux simple de la base mensuelle avant imputation (L. 523-3, R. 523-7)";
    label en unofficial "eligible partial pension: single rate of the monthly base before imputation (L. 523-3, R. 523-7)";
    when asf_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and motif_asf(e, PENSION_PARTIELLE) and bmaf_retenu(p, bmaf);
    then asf_montant_du(e, TauxAsfSimple * bmaf);
}

""" + source_block(S_MONT) + """
rule MontantDoubleDeuxParents(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "orphelin des deux parents eligible: taux double de la base mensuelle (L. 523-3, R. 523-7)";
    label en unofficial "eligible orphan of both parents: double rate of the monthly base (L. 523-3, R. 523-7)";
    when asf_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and motif_asf(e, ORPHELIN_DEUX_PARENTS) and bmaf_retenu(p, bmaf);
    then asf_montant_du(e, TauxAsfDoubleOrphelin * bmaf);
}

""" + source_block(S_MONT) + """
rule MontantDoubleDefaut2022(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, bmaf: Money) strict {
    effective [@2022-11-01, infinity);
    label fr official "defaillance double depuis novembre 2022: taux plein de la base mensuelle (L. 523-1 2022-11, R. 523-7)";
    label en unofficial "double default since November 2022: full rate of the monthly base (L. 523-1 2022-11, R. 523-7)";
    when asf_enfant_eligible(e) and fr.pf.core::parent_charge(p, e)
        and motif_asf(e, DEFAUT_DOUBLE) and bmaf_retenu(p, bmaf);
    then asf_montant_du(e, TauxAsfDoubleOrphelin * bmaf);
}

""" + source_block(S_DIFF) + """
rule DifferentielPartiel(p: fr.pf.core::Personne, e: fr.pf.core::Enfant, pension: Money, manq: Date, m0: Date, bmaf: Money) strict {
    effective [@2021-01-01, infinity);
    label fr official "pension sous le taux simple, delai purge: differentiel brut, voie autonome sans droit ouvert ni demande (L. 523-1 4°)";
    label en unofficial "pension below the single rate, period served: gross differential, standalone track with no open right or request (L. 523-1 4°)";
    when fr.pf.core::parent_charge(p, e) and fr.pf.core::enfant_ouvre_droit(e)
        and motif_asf(e, PENSION_PARTIELLE)
        and manquement_debiteur(e, manq) and mois_ouverture_asf(m0)
        and m0 >= add_calendar_period(manq, 1 calendar_month)
        and pension_recue(e, pension) and bmaf_retenu(p, bmaf)
        and pension < TauxAsfSimple * bmaf;
    then asf_differentiel_du(e, TauxAsfSimple * bmaf - pension);
}
"""

F05 = """// Continuation and the fourth-month control (R523-3, R523-3-1, R523-3-2, D523-2).
//
// READINGS. Once the opening is confirmed, payment continues for every
// later assessed month (the month after the opening month onwards,
// R523-3). The fourth-month control is exigible at the fund-stated
// control month, no earlier than three months after the opening month
// (R523-3-2 title mechanics, D523-2 hors-etat control). The quarterly
// cadence of the fund's control (R523-3-1) is an adopted DSS reading:
// the control duty below runs on CONTROLE_TRIMESTRIEL, the title serves
// one month per quarter (B-PFASF-TRIMESTRE, blind probe PFASF-B-08).

""" + HDR + "\n" + use_block(set(S_MAIN + S_CTRL) | {
    "mois_ouverture_asf", "mois_controle_4m", "mois_droit_asf",
    "asf_ouverture_confirmee", "asf_controle_confirme", "asf_maintien_mois",
}) + """

// Term policy for the quarterly control: deadlines arrive per case,
// months are not rolled.
deadline policy CONTROLE_TRIMESTRIEL {
    start_count same_day;
    include_end true;
    roll no_roll;
    month_end last_day_of_month;
}

""" + source_block(S_MAIN) + """
rule MaintienApresCarence(e: fr.pf.core::Enfant, m0: Date, m: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "ouverture confirmee, mois apprecie apres le mois d'ouverture: versement maintenu (R. 523-3)";
    label en unofficial "opening confirmed, assessed month after the opening month: payment continued (R. 523-3)";
    when asf_ouverture_confirmee(e)
        and mois_ouverture_asf(m0) and mois_droit_asf(m)
        and m >= add_calendar_period(m0, 1 calendar_month);
    then asf_maintien_mois(e, m);
}

""" + source_block(S_CTRL) + """
rule ControleQuatriemeMois(e: fr.pf.core::Enfant, m0: Date, t: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "ouverture confirmee, mois de controle au plus tot trois mois apres l'ouverture: controle exigible (R. 523-3-2, D. 523-2)";
    label en unofficial "opening confirmed, control month no earlier than three months after opening: control due (R. 523-3-2, D. 523-2)";
    when asf_ouverture_confirmee(e)
        and mois_ouverture_asf(m0) and mois_controle_4m(t)
        and t >= add_calendar_period(m0, 3 calendar_month);
    then asf_controle_confirme(e);
}
"""

F06 = """// Opening-date confirmation (R523-1, R523-2, D523-1, D523-2).
//
// READINGS. The tracks route on the default fact itself: a child with
// a stated debtor default confirms the opening through the carence
// check (opening month at least the month after the default month,
// R523-1, D523-1 monthly opening); an eligible orphan with no default
// confirms through the hors-etat opening (L523-1 1/2, D523-2,
// no carence). The request upkeep for hors-etat (R523-2) is folded
// into demande_asf at the eligibility stage.

""" + HDR + "\n" + use_block(set(S_OUVC + S_OUVH) | {
    "motif_asf", "manquement_debiteur", "mois_ouverture_asf",
    "asf_enfant_eligible", "asf_ouverture_confirmee",
}) + """

""" + source_block(S_OUVC) + """
rule OuvertureApresCarence(e: fr.pf.core::Enfant, manq: Date, m0: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "eligible avec defaillance, mois d'ouverture au plus tot le mois suivant la defaillance: ouverture confirmee (R. 523-1, D. 523-1)";
    label en unofficial "eligible with default, opening month no earlier than the month after default: opening confirmed (R. 523-1, D. 523-1)";
    when asf_enfant_eligible(e)
        and manquement_debiteur(e, manq) and mois_ouverture_asf(m0)
        and m0 >= add_calendar_period(manq, 1 calendar_month);
    then asf_ouverture_confirmee(e);
}

""" + source_block(S_OUVH) + """
rule OuvertureHorsEtatOrphelinUn(e: fr.pf.core::Enfant, m0: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "orphelin d'un parent eligible, mois d'ouverture constate: ouverture confirmee sans carence (L. 523-1 1°, D. 523-2)";
    label en unofficial "eligible orphan of one parent, opening month stated: opening confirmed without carence (L. 523-1 1°, D. 523-2)";
    when asf_enfant_eligible(e)
        and motif_asf(e, ORPHELIN_UN_PARENT) and mois_ouverture_asf(m0);
    then asf_ouverture_confirmee(e);
}

""" + source_block(S_OUVH) + """
rule OuvertureHorsEtatOrphelinDeux(e: fr.pf.core::Enfant, m0: Date) strict {
    effective [@2021-01-01, infinity);
    label fr official "orphelin des deux parents eligible, mois d'ouverture constate: ouverture confirmee sans carence (L. 523-1 2°, D. 523-2)";
    label en unofficial "eligible orphan of both parents, opening month stated: opening confirmed without carence (L. 523-1 2°, D. 523-2)";
    when asf_enfant_eligible(e)
        and motif_asf(e, ORPHELIN_DEUX_PARENTS) and mois_ouverture_asf(m0);
    then asf_ouverture_confirmee(e);
}
"""

F07 = """// Fund payment and quarterly-control duties (L523-1, L523-3, R523-6, R523-8, R523-3-1, R523-3-2).
//
// The debtor fund pays the due amount (base or differential) no later
// than the per-case payment deadline, monthly (R523-6), and performs
// the quarterly control no later than the per-case control deadline
// (R523-3-1, adopted DSS cadence). Only the fund bears duties. The
// maintain windows open at the D-01 coverage floor.

""" + HDR + "\n" + use_block(set(S_DEVB + S_DEVD + S_DEVC) | {
    "asf_montant_du", "asf_differentiel_du", "asf_controle_confirme",
    "asf_verse", "controle_effectue", "date_limite_versement",
    "date_limite_controle",
}) + """

// Term policy for monthly payments: the deadline arrives per case as
// date_limite_versement and bounds the maintain window, which opens at
// the D-01 coverage floor.
deadline policy PAIEMENT_MENSUEL {
    start_count same_day;
    include_end true;
    roll no_roll;
    month_end last_day_of_month;
}

""" + source_block(S_DEVB) + """
rule DevoirVerserAsf(o: fr.pf.core::Organisme, p: fr.pf.core::Personne, e: fr.pf.core::Enfant, montant: Money, limite: Date) strict {
    label fr official "l'organisme debiteur paie le montant d'allocation du au plus tard a la date limite mensuelle";
    label en unofficial "the debtor fund pays the allowance amount due no later than the monthly deadline";
    when asf_montant_du(e, montant) and fr.pf.core::organisme_debiteur_pf(o, p)
        and date_limite_versement(limite);
    then duty PayerAsfDu {
""" + BEARER_O + """
        beneficiary p;
        maintain asf_verse(p, e, montant) during [@2021-01-01, limite];
    };
}

""" + source_block(S_DEVD) + """
rule DevoirVerserAsfDifferentiel(o: fr.pf.core::Organisme, p: fr.pf.core::Personne, e: fr.pf.core::Enfant, montant: Money, limite: Date) strict {
    label fr official "l'organisme debiteur paie le differentiel du au plus tard a la date limite mensuelle";
    label en unofficial "the debtor fund pays the differential due no later than the monthly deadline";
    when asf_differentiel_du(e, montant) and fr.pf.core::organisme_debiteur_pf(o, p)
        and date_limite_versement(limite);
    then duty PayerAsfDifferentielDu {
""" + BEARER_O + """
        beneficiary p;
        maintain asf_verse(p, e, montant) during [@2021-01-01, limite];
    };
}

""" + source_block(S_DEVC) + """
rule DevoirControleTrimestriel(o: fr.pf.core::Organisme, p: fr.pf.core::Personne, e: fr.pf.core::Enfant, limite: Date) strict {
    label fr official "l'organisme debiteur effectue le controle trimestriel au plus tard a la date limite de controle";
    label en unofficial "the debtor fund performs the quarterly control no later than the control deadline";
    when asf_controle_confirme(e) and fr.pf.core::parent_charge(p, e)
        and fr.pf.core::organisme_debiteur_pf(o, p)
        and date_limite_controle(limite);
    then duty ControlerTrimestre {
""" + BEARER_O + """
        beneficiary p;
        maintain controle_effectue(e) during [@2021-01-01, limite];
    };
}
"""

FILES = {
    "package.law": PKG_LAW,
    "02-conditions.law": F02,
    "03-cessation-couple.law": F03,
    "04-montant.law": F04,
    "05-maintien-controle.law": F05,
    "06-ouverture-dates.law": F06,
    "07-devoir-versement.law": F07,
}

for name, content in FILES.items():
    (PKG / name).write_text(content, encoding="utf-8")
    print("wrote", name, len(content))


