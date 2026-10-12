# Foreign benchmarks report — `fr.pf.af`

Benchmarks (Catala allocations-familiales example, OpenFisca-France
`af.yaml`) are expectations, never semantic sources. Euro totals below
use the stated BMAF 400.00 unless noted; band rates come from the pinned
D. 521-1 versions (band 1: 32/41/16; band 2: 16/20.5/8; band 3:
8/10.25/4 — all percent of the base). The foreign programs compute with
their own BMAF/arrete tables (unpinned here); only structure
(bands, rates, eligibility, positions) is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open (fund counts, sharing situation, stated ceiling factors);
(c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

## Catala

> История (рукописный перенос, BMAF 400 «заявленная»). Числовая сверка с закреплённым коммитом
> CatalaLang/catala-examples@2694b17 — `catala/REPORT.md` (09.10.2026).

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 1 | 2020-05-01, Metro, 30 000, [2007, 2009, 2003-alterne, 2001-1100EUR], total 351.54 | 3 openers, band 1, base 292.00 + demi-supplement 32.00 = 324.00 | (c) supplement rate |
| 2 | 2020-05-01, Metro, 30 000, [2007, 2009, 2000-20yo], total 216.46 | base 128.00 (2 openers) + forfait open (forfait count 3, incl. the 20-year-old) | (a) |
| 3 | 2020-05-01, Guyane, 63 540, [2007], total 24.37 | DOM single child: 5.88% of the retained base (1 000.00 stated, B-PFAF-BMAF-DOM) = 58.80 | (b) base assumption |
| 4 | 2020-05-01, Metro, 67 250, [2007, 2003-alterne], total 99.46 | band 1 (real 2020 ceilings, stated factor 1.0323); eldest-of-two supplement 0 (L. 521-3 para. 1); household 128.00; R. 521-2 2. parent share 0.75 x 128.00 = 96.00 | (a) structure, (b) sharing situation |
| 5 | 2020-05-01, Metro, 30 000, [2007], total 0.00 | no conclusion (neither opened nor zeroed); same economics, different shape | (c) shape |
| 6 | 2020-05-01, Guadeloupe, 78 830, [2010, unborn-2020-09], band-2 mirror 64.00 | fund count 2 (B-PFAF-COMPTAGE; the unborn opens no right upstream) | (b) count shaping |
| 7 | 2021-02-01, Metro, 30 000, T1 children +9 months, total 417.84 | BLOCKED — see below; intended structure 292.00 + 64.00 + 32.00 = 388.00 | blocked |
| 8 | 2021-01-01, Metro, [2004], band 1, eligible, total 192.00 | BLOCKED — see below; intended structure unchanged | blocked |
| 9 | 2020-05-01, Guadeloupe, 75 786, 2 ASE-placed, service gets band-2 64.00 | pre-2021 L. 521-2 para. 4 twin: all placed, no judge maintenance, service receives 64.00 | (a) |
| 10 | 2020-04-20, Metro, 30 000, [2003-alterne, 2013-alterne], joint request | partage 1., coefficient (1 + 0.5)/2 = 0.75, parent share 96.00 | (b) sharing situation |
| 11 | 2021-12-31, Metro, 30 000, [2003, 2013, 2007] all full custody | eldest (18) included by the 3-or-more rule + 14-year-old non-eldest: 292.00 + 128.00 = 420.00 | (a) |
| 14 | 2022-05-01, Guadeloupe, 64 033, [2003-alterne, 2001-20yo], designated allocataire | two single-child households, 58.80 each; the 20-year-old opener asserted though upstream would deny it | (c) opener shaping |
| ouv | ouverture-droit mapping | input mapping only (L. 512-3 upstream, REQ-PFAF-02); no package conclusion from earnings | boundary |

Notes.

- 1: the 2003 shared-custody supplement. Their 351.54 pays it full;
  R. 521-4 para. 2 halves every shared-custody supplement, so ours pays
  32.00 (demi). The total is also not decomposable at any single BMAF
  (0.89 x B = 351.54 gives B = 395.00, against 414.42 below): the
  expectation looks stale. Structure asserted per the rule text.
- 2: the 20-year-old counts toward the forfait three (Catala counts
  [2007, 2009, 2000] to 3 for the forfait while the base stays on the
  2 openers). The package separates the two counts: `nb_enfants_charge`
  (openers: base, right, ceilings) and `nb_enfants_charge_forfait`
  (forfait minimum, includes the reaching child).
- 3: their 24.37 = 5.88% x 414.42, fixing the example BMAF around
  414.42 for 2020-05 (T4: 0.24 x 414.42 = 99.46 exact). Our 58.80 uses
  the stated 1 000.00 retained L. 755-3 base (B-PFAF-BMAF-DOM).
- 4: their band is band 1 under the real 2020 ceilings
  (57 759 + 5 775 x 2 = 69 309 > 67 250); the earlier band-2 conversion
  was wrong and is replaced. Their 99.46 = band-1 base x R. 521-3
  average 0.75 with NO supplement for the eldest of two — exactly the
  adopted structure. The benchmark is silent on designation, so the
  R. 521-2 2. disagreement reading carries the parent share (b).
- 5: metropolitan single child opens nothing; the package concludes
  no amount rather than printing 0.00.
- 7: their 417.84 is not decomposable at B = 414.42 under any rule-text
  structure (base x 0.8333 + supplements + forfait all miss); stale
  expectation suspected. Our intended structure follows the rules.
- 7/8 BLOCKED: any evaluation at legal_time in [2021-01-01,
  2021-05-01) in the three-package suite world refuses with
  NON_EXECUTABLE_STRATUM_BARRIER. Root cause (verified): `fr.pf.core`
  compiles its `asf_ouvre_droit` defeater `AsfCessationCouple` (bare
  CSS_L523 fragment in their CSS_ED2021_01) while none of its
  defeasible mates (AsfOrphelin/Filiation/Defaillance/Differentielle,
  effective 2021-12-25, fragments from ED2021_12 on) is in force.
  Foreign-package state; request string for the coordinator lane in
  the status record (REQ-PFAF-03). Our files are proven correct: the
  same T7 passes via the two-package projection world
  (`lawc test --program --imports`).
- 14: the designated-allocataire two-household reading is ours; the
  20-year-old opener fact contradicts upstream L. 512-3 and is
  asserted as case input only.

## OpenFisca

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 2015-09 | 3 children (2010, 2011, 2012-alterne), no income, joint request; `af_coeff_garde_alternee: 0.8333`, `af: 296.53 * 0.8333` | partage 1. steps: partage_actif, household 292.00. The (2 + 0.5)/3 = 5/6 coefficient step omitted (below) | (a) steps, (c) coefficient |
| 2018-01-cas2 | band 1, household 292.00 | band 1, household 292.00 | (a) |
| 2018-04-cas2 | eligibility + household 356.00 | eligible + 356.00 | (a) |
| 2020-04-dom | right open + DOM single 58.80 | right open + 58.80 (stated base) | (b) base assumption |
| 2026-03-maintien | post-2026-03-01, 14 kept (2012-03-01 pair) | eligible + 64.00 | (a) edition pair |
| 2026-03-passage | post-2026-03-01, new 18 regime | supplement 0 | (a) edition pair |
| 2026-03-fallback-14 | post-2026-03-01 | right open, band 1 | (a) edition pair |

Notes.

- 2015-09: their coefficient is the float 0.8333 (tolerance 0.01).
  Ours refuses: (2 + 0.5)/3 = 5/6 has no exact Decimal form
  (NONEXACT_NARROWING, SPEC section 48, no silent rounding). The
  parent-share cent amount would additionally need a rounding rule,
  which is outside the 14-article scope (B-PFAF-ARRONDI). The
  coefficient step is omitted, not approximated; exact-coefficient
  households (0.75, 0.875, ...) evaluate normally.
- The 2026-03 pairs pin the age-supplement edition change
  (pre/post 2026-138, birthdate around 2012-03-01).

## Markers

- B-PFAF-BMAF-EURO: euro totals use stated BMAF assumptions.
- B-PFAF-BMAF-DOM: DOM single amounts use a stated retained base.
- B-PFAF-PLAFOND-REVALO: ceiling factors carry unpinned arrete ratios
  (2020 factor 1.0323 stated from the DSS/SD2B/2019/261 instruction).
- B-PFAF-COMPTAGE: counts are fund-established inputs with a
  consistency contract (opener count vs forfait count separated).
- B-PFAF-ARRONDI: cent rounding for inexact household shares is out
  of scope; inexact Decimal narrowings refuse (SPEC section 48).
- B-PFAF-SEUIL-MOYENNE: the L. 521-3 para. 2 three-or-more test counts
  opening children (benchmark rule text, full-custody parity); the
  R. 521-4 para. 1 reference to the R. 521-3 average convention is
  recorded as strain (Q-PFAF-3).
- Q-PFAF-1 (eldest scope): eldest among all `parent_charge` siblings
  including non-openers (validated by Catala T7 arithmetic structure).
- Q-PFAF-2 (agreed-single-allocataire count): full count, half amount.
- Q-PFAF-3 (new): majoration threshold for shared-custody households —
  opener count (adopted) vs R. 521-3-average (text strain).
- REQ-PFAF-02: upstream `pub` needs from `fr.pf.core` (standing).
- REQ-PFAF-03 (new): `fr.pf.core` `asf_ouvre_droit` defeater/mate split
  in their CSS_ED2021_01 blocks every evaluation at legal_time in
  [2021-01-01, 2021-05-01) with NON_EXECUTABLE_STRATUM_BARRIER.
