# `fr.prestations.versement` — payment stage for all CNAF benefits

Transversal payment stage (wave 5): what is actually paid after CRDS,
rounding, non-payment floors and cross-benefit recovery. The package
owns no benefit computation; it IMPORTS brut heads from the benefit
packages and applies the payment-stage texts:

- CRDS 0.5 % (Ord. 96-50 art. 14/19, via `fr.apl` pins) on the PF
  brut tracks: AF, CF (base/majore/differentiel), ARS
  (base/differentiel), ASF (base/differentiel), PAJE
  (prime/base/PreParE), CMG (direct/structure/differentiel), AJPP
  (monthly/complement). AEEH is the art. 14 II 8° exception (no rule);
  housing CRDS stays in `fr.apl.versement`.
- Non-payment floors per benefit text: 15 EUR household totals for ASF
  (D. 523-3) and ARS (D. 543-2). RSA (6 EUR), housing and rounding
  mechanics are neighbour-owned; every other benefit is SILENCE.
- Cross-benefit recovery (L. 553-2 + pinned analogues L. 262-46 /
  L. 845-3 and the L. 553-2 al. 3 scope sentence): debt composition
  per echeance (AF, RSA, AAH, housing, PA), fund-stated scale rate,
  fraud uplift to 50 %, doubling on repeat within 5 years (PF),
  10 % fraud indemnity (PF, RSA and PA all imported, never derived),
  per-debt limitation (D-V5), no defeaters.
- Fund duties to pay the net tracks (CMG split ancien/réforme) and
  the 2 floor totals: 18 duties.

Norms owned elsewhere are NOT redefined (D-V1): L. 553-1/2/2-1/3/4/5
live in `fr.pf.core` (modules 06/07); housing payment lives in
`fr.apl.versement`. This package reads their heads.

Scope: payment-stage articles only (Ord. 96-50 art. 14/19 by
reference, D. 523-3, D. 543-2, L. 553-1/2, L. 262-45/46, L. 821-5,
duty sentences of the benefit articles). Own LEGI pins: none — every
`@source` cites a qualified neighbour fragment.

## Measure

96 rules (02: 32 strict; 03: 8 strict; 04: 12 strict + 26 defeasible; 05: 18 strict duties; +4 PA-carry input
relations and dette_totale4 in 04 since the cascade follow-up, no new rules). 84 scenarios in 5 families
(`#crds` 18, `#seuils` 6, `#devoir-versement` 19 positions,
`#recouvrement` 32, `#dossier` 9).

FINISH payment-core (2026-10-08, no-run authoring, verification
deferred — `docs/foundations/fr-cnaf/lines/finish-payment-core.md`):
module 06 adds 30 rules (D. 553-1..5, R. 553-1, fragments qualified
from `fr.pf.core`) and 24 authored-but-unrun scenarios in the new
`#bareme-retenues` family (registered in `law.toml`). Static-return
repair 2026-10-08 (PC-A01/A02, D. 553-4 al. 2 rewrite, still unrun):
R/N weighting removed for the organ-stated input, housing-unknown
notice added, 5 scenarios added (29 total). Re-review-02 repair
2026-10-08 (PC-R02-01, still unrun): quarterly-info-absent and
declaration-not-received gates on all estimated bases, inform duty
extended to quarterly-unknown cases, 6 scenarios added (35 total).
Re-review-03 repair 2026-10-08 (D755-2 applicability, still unrun):
2 scenarios added (37 total). Re-review-04 repair 2026-10-08
(PC-R04-03 D553-4 ordering, still unrun): dated-amount ledger with
oldest-first and same-date smallest-first ordering plus single-levy
allocation, 6 scenarios added (43 total).
Expectations are author assertions, not observations.

- `law engine check`: green (all 4 modules).
- lawc direct run (`lower` + `engine test`, no CLIR snapshot yet):
  70/70 PASS for all 4 modules (incl. 6 dossier checkpoints), including
  a 4-decimal exactness probe (10.0495 EUR — no invented rounding),
  all duty positions, and the silence-shaped suspensif test
  (COMPUTED + NEITHER, observed). Journal request 1 closed by
  be74ee4ba6 (all 7 `fr.pf.core` pubs landed).
- `audit.py --fast`: inventory 5 of 57 declaration kinds; sections
  1/2/2b/4/4b/5/6 not checked (no CLIR snapshot — journal request 3);
  section 7's fail cause (foreign stray `law.lock`+`deps/` in
  `fr.pf.cmg`, journal request 4) is gone from the tree — section
  un-re-run; `law audit --clir` on 02/03/05: 16 detectors, 0 findings.
- Blind cases: `analysis/blind-read-cases.json` (26, no answers),
  protocol test 3/3. Answers: session G (BLIND_PENDING). Finish
  linkage: `analysis/finish-blind-read-cases.json` (24, no answers);
  answers pending Luna review. Cascade follow-up:
  `analysis/finish-cascade-blind-read-cases.json` (24, no answers);
  answers pending.

## Their case to our answer

Foreign benchmarks are expectations, never sources. No foreign number
enters any rule. Survey (`drafts/foreign-expectations.md`, kept as the
working note): 508 OpenFisca tests parsed at pin 16b2e696, 389 touch
the payment stage — 305 mes-aides (gross only, 2014–2015 law) and 84
leximpact/2024 (the only gross+CRDS+net triples: PPA 19, ARS 7, AF 6,
ASF 3, CF 2, PAJE 1).

Reading guide:

- CRDS is per-benefit upstream (`crds_af`, `crds_asf`, …) and
  RSA/AAH have no CRDS variables (exempt) — same split as module 02.
- Floors and rounding are embedded in their totals, never asserted
  standalone; leximpact's ±1 EUR margin can only anchor structure
  (CRDS applies / net = brut − CRDS), never cents.
- Recovery/retenues/10 %/fraud +50 % do not exist upstream: module
  04 has no foreign through-case coverage at all.
- Leximpact year-period cases do not fit the converter (`extract`
  rejects non-month periods); the convertible mes-aides cases are
  gross-only 2014–2015 law. Hand-written `.lawtest` in the pf-cf
  Stelle style is the documented path; the dossier household below
  is bespoke anyway.

## Boundaries

- B-PV-DSS-SCALE (DSS_PENDING): the non-PF levies (RSA, AAH,
  housing, PA, AJPA) arrive as the fund-stated Money amount
  (`retenue_mensuelle_*_declaree`, `retenue_trimestrielle_pa_declaree`);
  no rate input and no installment x rate product exist (PC-R07-39,
  contract (b) of module 04). The fraud uplift is the FIXED 50 % of
  D. 553-5 I (x1.50, x2.00 on repeat), never a stated fraction
  (PC-R07-38). D-42 (2026-10-08): the scenarios still carried the
  removed `taux_retenue_*_retenu` / `taux_majoration_*` inputs; they
  now state the Money levy (rate x echeance of the same case) and the
  lawful-carry gates.
- B-VERS-D5531-REVALO: post-2022 tranche/deeming values are
  unpinned (IPC hors tabac revalorisation, rounding unstated):
  tranche and 1 096 EUR rules stop at 2023-01-01. D-42
  (2026-10-08): from 2023-01-01 the PF levy arrives fund-stated
  (`prelevement_mensuel_declare` -> `prelevement_mensuel`, rule
  `PrelevementMensuelDeclare`), the same contract as the non-PF
  levies; before, no PF levy existed for 2024+ and every AF/CF/ASF/
  ARS recovery of module 04 (effective 2024-01-01) was unreachable.
- B-PV-APL-LECTURE (D-42): the recovery scenarios on housing and
  the AF positions scenario return INTERPRETATION_REQUIRED, not
  COMPUTED, because the world holds fr.apl's unselected reading
  group SensMinimumPp (and fr.css.aah's SensRenouvellement for the
  positions query). Selecting `fr.apl::PpPlancherFinal` from this
  package needs `pub interpretation PpPlancherFinal` in fr.apl
  (LDC-E1105); owner change pending.
- B-VERS-D5531-TRANCHE-691: the decree writes bands up to 690 and
  above 691; (690, 691] is literally uncovered — no rule fires
  (paired scenarios `bareme-trou-691` / `bareme-tranche4-lisiere`).
- B-VERS-D5531-PARTS-CALCUL (engine risk): parts rules mix
  Decimal and Integer; no corpus precedent found. Reviewer lawref
  verdict decides; fallback is a stated-parts input contract.
- B-VERS-D5531-DIVISION-ARRONDI: RETIRED 2026-10-08 (PC-A01) —
  no weighting division is computed anymore (see PONDERE-FORMULE).
- B-VERS-D5531-PONDERE-FORMULE: the pinned D. 553-1 II exposes R,
  the weighting sentence and N with no operator or expression — no
  weighting formula is computed; weighted income arrives organ-stated,
  deemed 1 096 EUR, or last-known only. Tranche bands apply to that
  typed retained input (paired scenarios `bareme-chaine-isole`,
  `bareme-chaine-menage`, boundary `bareme-pondere-sans-formule`).
- B-VERS-D5531-LISIERE-FRACTION: fractional-euro edges (345, 346)
  and (516, 517] fall through every band — literal, no result
  (`bareme-lisiere-fraction-345/-516`).
- B-VERS-D5534-ORDRE: multi-indu oldest-first/smallest-first
  ordering needs a ledger — single-deduction status only
  (B-PV-NO-LEDGER consistent).
- B-PV-PF-TRACKS: module 04 wires the AF echeance for the PF regime;
  CF/ARS/ASF/PAJE/CMG/AJPP echeances are the same-regime mechanical
  extension, deferred: Enfant-keyed tracks need a parent bridge,
  PAJE multi-key shapes need a join, CF tracks need a selector.
- B-PV-PA: REMOVED (FINISH-W2, follow-up 6 closed). PA is wired:
  04 Y = PA section (RSA pattern, 8 rules on
  `prime_due_trimestre` / `indu_recupere` / `indemnite_fraude` /
  `indu_frauduleux` / `option_remboursement_unique`), 05
  owned-stage (neighbour `DevoirServirPrime` stands, no new duty),
  dossier stage 4 (`Famille2026_06`). Remainder is scoped below.
- B-PV-PA-CARRY: PA-source carries onto AF/RSA/AAH/housing are
  WIRED (FINISH-W2 cascade follow-up, L. 845-3 al. 3 destination
  list). Per-destination remainder, each with its own blocker:
  PF→PA carry (L. 553-2 "titre IV" inference, MIRROR); AAH/
  housing→PA carries (L. 821-5-1/L. 823-9, mirror-only); PA→AJPA
  (L. 168-8: no AJPA echeance in this layer — input block);
  L. 845-3 al. 4 tiers-payant and al. 6 L. 133-4-1/livre III
  destinations (decree modalities unpinned / outside surveyed
  benefits — source/input blocks).
- B-PV-PA-TRIMESTRE: the PA echeance is the quarterly served
  amount (`prime_due_trimestre`); monthly apportionment of the
  served quarter is unmodelled (no neighbour head).
- B-PV-PA-CRDS: no CRDS rule for PA. PA sits at book VIII
  title IV, outside the Ord. 96-50 art. 14 II 8° L. 511-1 list
  quoted in 02; coverage under other limbs is unestablished in
  pinned bytes (AJPA precedent in 02).
- B-PV-PA-ARRONDI: no payment-stage rounding rule for PA in
  pinned bytes; the 04 nets compute exactly.
- B-PV-AAH-LOGEMENT-INDEMNITE (renamed, PA left since FINISH-W2):
  the 10 % indemnity and own-recovery permissions of AAH/housing
  (L. 821-5-1, L. 823-9) are mirror-only, reserved pending pinning.
  The scale math for their retenues is pinned-grounded via
  L. 553-2 al. 3. PA: L. 845-3 is pinned in the neighbour and its
  10 % indemnity is consumed (04 Y = PA section).
- B-PV-LOGEMENT-PRESCRIPTION: housing limitation is SILENCE in the
  current CCH (old L. 351-11 abrogated 2019-09-01): no defeater
  exists or can exist for housing deductions.
- B-PV-PRE2024: module 04 starts 2024-01-01 (L. 553-2 pinned from
  CSS_ED2024_01; 10 % sentences from loi 2022-1616 art. 100). The
  identical pre-2024 paragraphs are reserved, not encoded.
- B-PV-NO-LEDGER: one recoverable debt per debtor per case; no
  month-to-month exhaustion, no cross-identity join (each family is
  keyed on its own neighbour person type; carried debts arrive as
  fund-stated inputs on the payee's key).
- B-PV-AJPP-DEVOIR: no net-payment duty for AJPP — no general
  payment sentence is pinned (L. 544-1 unpinned in `fr.pf.ajpp`).
- B-PV-ASF-DUTY-ASSUMED (F-CH6-01/02): no pinned fragment states a
  general monthly ASF payment duty (L. 523-1 is opening language;
  R. 523-6 is quarterly L. 581-2 differential, ex-cited). The three
  ASF duties rest on L. 523-1 + assumed monthly frequency per
  neighbour convention; referred to pf-asf (journal request 7).
- B-PV-ARRONDI: no cent- or euro-rounding rule is pinned for any PF
  benefit at payment stage; CRDS and nets compute exactly.
- B-PV-RSA-77 / B-PV-RSA-PRESCRIPTION: consumed, not awaited —
  the 77 EUR floor, notification, limitation and suspensive-appeal
  bar arrive pre-encoded in imported `indu_recouvrable` (fr.casf.rsa
  05 live); the 10 % indemnity arrives via `indemnite_fraude`.
- B-PV-PRESCRIPTION-SPLIT (D-V5/Q5): limitation is per-debt. PF
  prescription drops the PF indu+indemnity on AF echeances
  (DetteAfPrescrit, carry survives); PF-carried debts on
  RSA/AAH/housing keys and AAH own-limitation are unencoded
  (other keys unreachable — IDENTITY).
- B-PV-DROIT-PAIEMENT (Q7): 05 duties are ENTITLEMENT (droit), 04 nets
  are PAYABLE (paiement = entitlement minus lawful deductions). No
  rule links the stages; linking needs the debt as a duty premise
  (18 more duties), refused as over-modelling.
- B-PV-SUBSIDIARITE (D9): "à défaut" (carry only after own-benefit
  recovery failed) is caller-side: the fund states a carry only
  then. No rule second-guesses chargeability.
- B-PV-UPSTREAM-EXCLUSIVITE: alternative tracks of one benefit (CF
  base/majore/differentiel, ARS base/differentiel, ASF
  base/differentiel, CMG direct/structure) are assumed mutually
  exclusive upstream. Where upstream montant rules co-fire, CRDS is
  withheld per stated head (garbage-in); no in-module guard masks a
  foreign double-payment. Complementary by design, outside this
  contract: PAJE prime/base/PreParE and the CMG transitional
  differential (tops up new-law amount, separate bearer). Owners or
  composed tests must settle it (journal request 5).

## Dossier

`examples/famille-dans-le-temps/` — one household 2024–2026 across
all ready benefits (NOT_LOWERED; registration: orchestrator). No
author's task-guide route was followed (no `fr` package publishes
one): the order of questions is the agent's, only the answers are
the canon's. The June-2026 case is a given-PA recovery checkpoint
(stated 280.00 → 210.00); the joined housing → forfait → RSA →
PA derivation (derived due 167.55 → net 134.04) runs as
`tests/dossier-pa-cascade-2026-06.lawtest` + positions twin —
no normative end-to-end calculation is claimed from the stated
280.00.
