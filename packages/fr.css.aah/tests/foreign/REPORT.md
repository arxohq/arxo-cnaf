# Foreign benchmarks report — `fr.css.aah`

Benchmarks (OpenFisca-France `aah.yaml`, `aah_couple.yaml`) are
expectations, never semantic sources. Euro rates below are the retained
case inputs of each scenario (B-AAH-MONTANT-EURO); resource bases are fed
as retained annual/quarterly facts (B-AAH-RESSOURCES-CALCUL). Only the
computation structure (track routing, ceiling, couple majoration,
deconjugalised spouse handling, transitional comparison) is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open; (c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

## OpenFisca

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 1 | 2023-03, single, activity ceased (inactif in 2023-03); monthly base 696.41, rate 956.65, expectation 260 | annual track, single: (12 x 956.65 - 8356.92) / 12 = 260.24 (their 260 within their margin 1) | (a) |
| 2 | 2023-08, couple, claimant actif, quarterly base 990.33/month; rate 971.37, expectation 767.85 | quarterly track, transitional couple: (3 x 971.37 x 1.81 - 2970.99) / 3 = 767.8497 (exact Decimal; no cent-rounding rule in scope) | (b) |
| 3 | 2023-11, deconjugalised couple, second parent without income; rate 971.37, expectation aah = 971.37 | current track, spouse ignored: min(971.37, (12 x 971.37 - 0) / 12) = 971.37 | (a) |

Notes.

- 1: their monthly base 696.41 is R. 821-4-4 cessation mechanics — outside
  the model (B-AAH-RESSOURCES-CALCUL) — fed as retained annual
  696.41 x 12 = 8356.92.
- 2: spouse income negligible in their setup (12 euros/year) is fed as 0.00;
  their expectation is cent-rounded, ours is the exact Decimal quotient.
  The case also confirms the adopted D. 821-2 reading: the eligibility
  ceiling is the majorated plafond (al. 2 «le plafond mentionné au premier
  alinéa»), since 2970.99 > 3 x 971.37 = 2914.11 yet the right opens
  (2970.99 < 3 x 971.37 x 1.81 = 5274.54).
- 3: post-reform spouse-income disregard; the benchmark expectation equals
  the full rate.
- Eligibility mapping (not transposed as scenarios): OF `taux_incapacite`
  0.5/0.8/0.9 with the RSDAE condition maps onto the package tracks
  80%+ (decision_cdaph_80) and 50-79% with RSDAE (decision_cdaph_50_79 +
  rsdae_etablie); OF `aah_eligible` false-cases (age, residence) map onto
  the droit premises. No divergence found in the mapping.
- Not imported: the remaining ~60 OF AAH cases are pre-coverage
  (periods 2004-2018, rates/wordings outside the 2021+ scope) or mechanics
  outside the model (abattements, R. 532-3 resource base, pensions,
  R. 821-4-4 cessation) — importing them would book technical debt, so the
  import stays at the 3 structure-proving cases above.
- No Catala AAH program exists upstream: OpenFisca only.
- DSS_PENDING: monthly euro rates, resource bases, SMIC and revalorisation
  arrive as retained/case inputs (B-AAH-MONTANT-EURO,
  B-AAH-RESSOURCES-CALCUL, B-AAH-SMIC, AAH-REVALO-PENDING).
- BLIND_PENDING: blind second-reading cases in
  `analysis/blind-read-cases.json` (inputs only, no answers).
