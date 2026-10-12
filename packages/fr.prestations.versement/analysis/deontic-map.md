# Deontic map — fr.prestations.versement (phase 1)

Norms owned elsewhere are NOT remapped here (D-V1): L. 553-1/2/2-1/3/4/5
live in fr.pf.core (modules 06/07, see their headers); housing payment
(CRDS, euro-floor rounding, guide decisions) lives in fr.apl.versement.
This map covers only what this package adds: CRDS on PF, per-benefit
rounding and non-payment floors, cross-benefit recovery, limitation
applied to payment, and the fund duty to pay the net amount.

## 02-crds — Ord. 96-50 art. 14 (via fr.apl pins)

- Art. 14 "il est institué ... une contribution" + précompte on
  replacement-family benefits: institutional computation
  (crds_precomptee = 0.5% of brut, withheld by the paying body).
  Deontic surface: duty of the body to withhold (duty, bearer =
  empirical organisme_debiteur); no liberty (rate and base are fixed).
- Territorial carve-outs (CGCT LO 6414-1 for Saint-Pierre-et-Miquelon):
  status rule (crds = 0), no position.
- Rounding of the CRDS amount itself: ONLY where the pinned text names
  it (housing guide p.23: lower centime — already in fr.apl.versement).
  For PF: S1 reports; silence = boundary, no invented rounding.

## 03-arrondi-seuils — rounding and floors per benefit text

- Each benefit: institutional statuses (montant_net / decision_versement /
  decision_non_versement). No new must/must-not: the floor is a
  threshold on the fund's existing payment duty (defeater when below).
- Known leads (S2 confirms against pinned bytes): 15 EUR PF floor
  (B-PFASF-SEUIL lead), CCH D.823-16 housing non-payment (already read
  by fr.apl.versement via aide_non_versee), RSA allocation_non_versee,
  AAH/PA/CMG/AJPP texts or SILENCE.

## 04-recouvrement — L. 553-2 + analogues, applied across benefits

- "Tout indu est récupéré par retenues sur les prestations à venir":
  organ duty to recover (duty, maintained indu_recupere_retenues) —
  the norm is pf-core's; this package applies it when the indu sits on
  benefit X and the future benefits are Y (cross-benefit wiring).
- Single-repayment option: allocataire liberty — already pf-core's.
- 10% fraud indemnity: institutional amount — pf-core computes it for
  PF indus; this package reads the head (and the analogues' heads when
  RSA/AAH/PA publish them) into the net.
- Retention uplift on fraud (L. 553-2 al. 3, "jusqu'à +50%", doubling
  on repeat within 5 years): executable condition (fraude_reiteree —
  pf-core's); the uplift RATE is text (not DSS), the BASE scale rate is
  DSS bytes → empirical input + boundary DSS_PENDING.
- L. 553-1 applied: action_prescrite (pf-core) drops the PF indu
  (and its indemnity) per-debt via DetteAfPrescrit (D-V5) — a
  guard, not a defeater; no new position. No late-payment rules
  exist in this package.

## 05-devoir-versement — fund duty to pay the net

- Duty of the debtor body to pay the computed net amount (duty,
  bearer = empirical organisme_debiteur), mirroring the sibling
  07-devoir-versement modules. Defeaters: decision_non_versement
  (floor), action_prescrite (limitation).

## Evaluative channels (DECISION-0194)

- Fraud / fausse declaration / manoeuvre frauduleuse: established by
  decision → Boolean case inputs (same as pf-core: indu_frauduleux,
  manoeuvre_frauduleuse, fausse_declaration). No new judgment channel.
- Retention scale rate: DSS instruction bytes missing → stated-assumption
  empirical input (DSS_PENDING), never invented.
