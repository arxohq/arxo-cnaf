# Foreign benchmarks report — `fr.casf.rsa`

Benchmarks (OpenFisca-France `rsa*.yaml`, LexImpact 2024 `rsa_*.yml`)
are expectations, never semantic sources. Euro totals below use the MF
scale values derived from the single amounts both programs share
(2023: 607.75; 2024: 635.71 — the 1 April revaluation, whose
L. 161-25 factor is unpinned, DSS_PENDING) through the pinned rates;
only structure (composition scale, majoré, flat-rate, cap,
thresholds, positions) is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open (MF euros, base components, upstream eligibility findings);
(c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.
Selection principle: post-2021 cases only (the four 2024 LexImpact
cases); the older formula cases enter solely as eligibility/input
mapping (majoré, foyer exclusion) since their periods predate the
pinned editions.

## LexImpact 2024 (period 2024, absolute_error_margin 1)

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 1 | rsa_06 femme enceinte isolée, free housing, no resources: 707.49 (Jan–Mar) → 740.04 (Apr–Dec) | majoré isolée 128.412 % (R.262-1 al. 2): 780.42 − forfait 12 % 72.93 = 707.49; after 1 April: 816.33 − 76.29 = 740.04 | (a) scale + forfait; (b) stated MF |
| 2 | rsa_04 jeune 22yo, work-hours condition met, free housing: 534.82 → 559.42 | single scale minus 12 % forfait: 607.75 − 72.93 = 534.82; 635.71 − 76.29 = 559.42 | (a) scale + forfait; (b) stated MF; jeune work-condition is an upstream input |
| 3 | rsa_01 seuil inactif, parent + 1 child, APL 344.42 → 357.91 (Oct): 665.43 → 696.05, flat from Oct | 150 % scale minus base minus capped aid: 911.62 − 100.33 − 145.86 (16 %) = 665.43; Apr: 953.57 − 104.95 − 152.57 = 696.05; the October APL rise is absorbed by the R.262-10 cap | (a) scale + cap; (b) stated MF and base |
| 4 | rsa_02 seuil chomeur, same household + ARE 265: 400.43 → 431.05 | base carries the unemployment income (265.00): 911.62 − 365.33 − 145.86 = 400.43; Apr: 953.57 − 369.95 − 152.57 = 431.05 | (a) ARE in base (Chomage lane); (b) stated MF and base |

## OpenFisca formulas (periods 2015–2016, eligibility mapping)

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 5 | rsa_majore: no majoré without recent isolation (child 5) → false | `isole_majore` absent → normal scale | (b) eligibility finding arrives as input |
| 6 | rsa_majore: recent isolation → true; child under 3 → true; pregnant, no children → true | `isole_majore` present → 128.412 % + 42.804 % per child | (b) eligibility finding arrives as input |
| 7 | rsa_majore: 17yo pregnant, dependent on parents → false | upstream age/charge finding (RSA-jeune/minor regime, outside L.262-9 scope); `isole_majore` absent | boundary (upstream) |
| 8 | rsa_exclusion_foyer ×10: child excluded from the count above 40 % (normal) / 70 % (majoré) of own resources, incl. two "pente" approximation cases | household size arrives as case input; the pinned R.262-1 carries no resource-based child exclusion (pure rate scale) | boundary (input contract; their pente cases document their own approximation error) |
| 9 | rsa_base_ressources ×2 (2016): no double count of 2EE/2DC boxes; plus-values counted | single `CompteCapital` rule counts each declared euro once; fiscal-box annualization is upstream (R.262-6 valuation) | (b) upstream shaping |

Notes.

- 1–4: the April step (+4.6 %) is visible in every series
  (707.49→740.04, 534.82→559.42, 665.43→696.05, 400.43→431.05);
  the package takes the 1 April factor as an input
  (B-RSA-MF-INPUT-CONTRACT, DSS_PENDING), so the revaluation itself
  is (b), while the scale/forfait/cap arithmetic around it is (a).
- 3: the October APL rise (344.42→357.91) with a flat RSA is the
  R.262-10 cap working as written: aid above the flat-rate counts
  only up to the flat-rate.
- Seuils: the "seuil" cases pay far above the non-payment threshold
  (L.262-2 al. 2, from 6 €); threshold behaviour is covered by the
  package's own `allocation-normale/seuil` scenarios, not by this
  selection.
- Pre-2021 formula files (rsa_2017, celibataire, couple, nationalite,
  jeune-eligibility, revenus locatifs, TNS eligibility) are not
  selected: eligibility upstream (nationality, age, residence) is
  outside the package, and their periods predate every pinned
  edition.
