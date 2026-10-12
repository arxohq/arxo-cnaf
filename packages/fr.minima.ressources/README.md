# `fr.minima.ressources` — quarterly resources, matrix and housing flat-rate

Executable formalization of the RSA resource side: the reference
quarter and monthly base (R.262-7, pre- and post-2025-03-01), the
per-category resource matrix (R.262-6, R.262-11–R.262-25), and the
housing flat-rate with the aid cap (R.262-9, R.262-10).

Scope: exactly 20 CASF articles (R262-4, R262-4-1, R262-4-2, R262-6,
R262-7, R262-9, R262-10, R262-10-1, R262-11, R262-12, R262-13,
R262-14, R262-18, R262-19, R262-20, R262-21, R262-22, R262-23,
R262-24, R262-25). The MF-by-size figures (`mf_composition`) and the
monthly household MF (`mf_mois`) are relations of this package that
`fr.casf.rsa` WRITES from its R.262-1 scale and the pinned revaluation
decrees (B-RSA-MF-INPUT-CONTRACT, closed from the rsa side); in a world
without `fr.casf.rsa`, or for a month outside its pinned series, they are
case inputs. The received housing aid arrives as a
case input with provenance (APL-FORFAIT-PENDING). DOM articles
(L.542-/R.542-) are wave 7.

## Measure

`audit.py --fast fr-minima-ressources` (formalization measure, static
profile): 5 `.law` files, 23 scenarios, 92 rules, all strict;
established ×163, not_known ×19. Form catalog: 10 of 57 declaration
kinds used (computation-only: no deontic, temporal or procedural
forms). Dangling premises 27, all enum constructors supplied by case
inputs (DECISION-0047 pattern). One-way premises 1 of 92
(`TnsTrimestriel`: the president-set TNS annual figure is a lawful
case input under B-MINRES-TNS-REFERENCE, exercised by
`tns-trimestre`). Dead symbols 0 open (4 superseded declarations
removed 06.10.2026; `territoire`/`Territoire` filed in
`corpus/slices/dead-symbols.json` as the wave-7 DOM reserve). LawQL
lints 0. Reachability (§6) not run (`--fast`).

## Their case to our answer

Foreign benchmarks are expectations, never sources. The 2025-03-01
reform (M-4…M-2 window, DSN prefill) has no foreign program; the
reform date-pair scenarios stand in for benchmarks. Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (OpenFisca
`rsa_base_ressources.yaml` + LexImpact 2024 base rows).

Reading guide:

- Unemployment income joins the base (row 2: ARE 265.00 retained).
- Capital income counts once via the upstream R.262-6 valuation
  (row 3).
- Shape difference (row 4, class c): their base excludes housing and
  adds the flat-rate separately; ours includes the capped aid and the
  in-kind flat-rate directly in the monthly base (R.262-7, II 3°).
- Blind independent reading: [`analysis/blind-read-cases.json`](analysis/blind-read-cases.json) (20 cases).

## Boundaries

- B-MINRES-MOYENNE-INEXACTE (closed by a reading, owner decision 08.10.2026): R. 262-7
  (I and II) speaks of "la moyenne mensuelle" and states no rounding. The default
  rules divide exactly (`(v1 + v2 + v3) / 3.0`): a non-terminating quotient (167 + 167
  + 0 over three months) makes the document refuse (INEXACT_DIVISION, §50/§18; status
  RUNTIME_ERROR, scenario `moyenne-inexacte-sans-lecture`). The rounding is practice of
  the funds (CNAF), not text, so it is the `pub interpretation MoyenneArrondieCentime`
  (§152, status disputed, outside any group): selected in the `context` of the case
  (`interpretation MoyenneArrondieCentime;`, from another package
  `interpretation fr.minima.ressources::MoyenneArrondieCentime;`) it replaces the
  division by `div_round(sum, 3.0, 2, "HALF_UP")` in the six averaging rules (DSN
  professional, other DSN, declared in both regimes, amount due in both regimes) and
  silences the exact rules through the marker `lecture_moyenne_arrondie` (one value per
  head under either choice). Unselected it executes nothing and no earlier answer
  changes. The reading also rounds an exact quotient that has more than two decimals
  (amounts derived from the MF scale). Scenarios: family `#lecture-moyenne` (7).
- B-MINRES-DUAL-FEED: the quarter runs on fund-block totals
  (`dsn_pro_mois`/`dsn_autre_mois`/`declare_total_mois`); the matrix
  demonstrates per-category counting with a consistency contract.
- B-MINRES-PRO-PRE2024: pre-2024 professional-income wording.
- B-MINRES-TNS-REFERENCE: reference years and IPC for the TNS
  annual figure are unpinned; the president-set figure is an input.
- B-MINRES-BMAF-EURO: euro scales (BMAF, MF) arrive stated, never
  reconstituted.
- B-RSA-EXPERIMENTATION-2024 (base found, regime not modelled): the experiment of
  the prefilled quarterly declarations, décret n° 2024-693 du 5 juillet 2024
  (articles 1–10) and arrêté du 7 juillet 2024 (1 October 2024 – 1 March 2025),
  is pinned in `sources/experimentation-2024/` (`tools/pin_experimentation.py`,
  LEGI dump of 2025-07-13). Scope: allocataires of the CAF of the Alpes-Maritimes,
  Aube, Hérault, Pyrénées-Atlantiques and Vendée who declare by téléservice
  (art. 1). By derogation to R. 262-7 (art. 3) the reference months are the
  4th, 3rd and 2nd before the claim or review with the three resource blocks
  that decree 2025-185 generalised from 2025-03-01 (the mechanics
  `02-trimestre.law` already runs after that date); art. 2 deems the spouse
  present over the same months (R. 262-4), art. 4 sets the self-employed
  receipts and turnover (R. 262-18, R. 262-19), art. 8 keeps the lower of two
  averages at the first renewal. Not modelled: the regime would be a second
  computation of the quarter on the window [2024-10-01, 2025-03-01) for a class
  of claimants (about twenty dated rules of `02-trimestre.law`, the old
  versions of R. 262-11/12/13/18/19 and the art. 8 minimum), so before
  2025-03-01 the package computes every case with the three previous months
  (R. 262-7 as then pinned). OpenFisca RSA case #18 (`departement_experimentation_rsa`)
  is therefore not transferred.
- B-MINRES-PA-TRIMESTRE: prime d'activité stays quarterly out of
  this package.
- APL-FORFAIT-PENDING: no formal dep on `fr.apl` (W2-APL
  IN_PROGRESS); the R.262-9 flat-rate is self-contained CASF text
  and the received aid is an input with provenance.
- Garden benefits are never counted (R.262-9, last paragraph).
- DOM (L.542-/R.542-) is SANS_OWNER, wave 7; metro and DOM share
  the same texts here.
