# Foreign benchmarks report — `fr.pf.cf`

Benchmarks (OpenFisca-France `cf.yaml`, `cf_2018.yaml`,
`cf_2018_04.yaml`, pinned at the registry cutoff 2026-10-06) are
expectations, never semantic sources. Euro totals below use stated
illustrative inputs (BMAF 320.00 for base-track ports, 100.00 for
majore-track ports; decree nominal `plafond_base_cf` 20000 EUR);
track rates come from the pinned D. 522-1/D. 522-2 versions (base
41.65 %; majore 58.33 % until 2018-04-01, 62.48 % after). The foreign
program computes with its own BMAF/arrete tables (unpinned here);
only structure (tracks, rates, eligibility, boundaries) is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark
leaves open (fund counts, N-2 resource totals, stated BMAF/nominals,
biactif situation);
(c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

Their `cf` outputs read `X / (1 - 0.005)`: X is their brut
(0.4165 x their BMAF 405.83 = 169.03 for 2018-01; 0.6248 x 409.88 =
256.09 for the April majore), and the division is their CRDS
handling, outside our brut scope (B-PFCF-CRDS).

## OpenFisca

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 0 | 2018-01, foncier 20000 (2016) -> base 20000 | base taken as stated ressources_menage; base 133.28 (resources 20000 above the half ceiling 18000, under 36000; L. 522-3 exclusivity D-29(a), tiered ceiling D-36) | (b) household borrowed |
| 1 | 2018-01, [12, 10, 7], N-2 35000, total 169.03 | droit open, base track, brut 133.28 | (b) BMAF/nominal |
| 2 | 2018-01, [12, 10, 7, 5], N-2 35000, total 169.03 | droit open, base track under the 4-child 42000 ceiling, 133.28 | (b) BMAF/nominal |
| 3 | 2018-01, [12, 10, 7, 5, 3], N-2 35000, total 169.03 | the 3-year-old counts (birthday reached); base track under 48000, 133.28 | (b) BMAF/nominal |
| 4 | 2018-01, [12, 10, 7], N-2 15000, total 236.71 | MAJORE track (15000 within 18000; L. 522-3 needs no biactif), 58.33 | (b) BMAF/nominal |
| 5 | 2018-01, 4 children, N-2 15000, total 236.71 | MAJORE track under the 26000 majore ceiling, 58.33 | (b) BMAF/nominal |
| 6 | 2018-01, [14, 10, 7, 5, 3], N-2 15000, total 236.71 | MAJORE track under 31500, 58.33 | (b) BMAF/nominal |
| NP1 | 2018-01, [12], N-2 35000, total 0 | count below three: no conclusion (NEITHER), not a printed zero | (c) shape |
| NP2 | 2018-01, [12], N-2 15000, total 0 | same as NP1 | (c) shape |
| NP3 | 2018-01, [12, 10], N-2 35000, total 0 | count below three: no conclusion | (c) shape |
| NP4 | 2018-01, [12, 10], N-2 65000, total 0 | count fails before any ceiling: no conclusion | (c) shape |
| NP5 | 2018-01, [12, 10, 7], N-2 55000, total 0 | over the ceiling and past twelve monthly amounts: no right, no differential | (c) shape |
| NP6 | 2018-01, [21, 12, 10], N-2 35000, total 0 | the 21-year-old is out (no pay established); count two: no conclusion | (c) shape |
| NP7 | 2018-01, [21, 12, 10], N-2 15000, total 0 | same household as NP6 at lower resources: no conclusion | (c) shape |
| NP8 | 2018-01, [12, 10, 1], N-2 35000, total 0 | the 1-year-old is below the 3-year floor; count two: no conclusion | (c) shape |
| NP9 | 2018-01, [12, 10, 1], N-2 15000, total 0 | same household as NP8 at lower resources: no conclusion | (c) shape |
| 04-1 | 2018-04, [12, 10, 7], N-2 35000, total 170.71 | base rate unchanged: brut 133.28 | (b) BMAF/nominal |
| 04-2 | 2018-04, [12, 10, 7], N-2 15000, total 256.09 | 2018-04-01 majore row 0.6248: brut 62.48; the edition pair proves the row switch | (b) BMAF/nominal |

Notes.

- Biactif shaping (b): OF households carry two salaries, but the
  per-member 13.6 % PASS test needs N-2 PASS tables (unpinned), so no
  port asserts `revenu_pro_min_couple`/`pass_annuel`; the plain-ceiling
  chain applies. Cas 1 still opens (35000 <= 36000 either way).
- Cas 4-6 confirm the adopted L. 522-3 reading: OF pays the majore
  rate at 15000 without any biactif/isolated situation, exactly the
  lower-ceiling track the package builds.
- NP5 is the far-overrun mirror of the differential-ouvert unit test:
  55000 - 36000 = 14000 > 12 x 133.28 = 1599.36, so R. 522-3 stays
  shut on both implementations.
- Zero-vs-absence (c): the package concludes no amount rather than
  printing 0.00; economics agree, shapes differ.
