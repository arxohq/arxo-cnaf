# Foreign benchmarks report — `fr.pf.aeeh`

Benchmarks (OpenFisca-France `aeeh.yaml`) are expectations, never semantic
sources. Euro totals below use the stated BMAF of each case; complement
fractions come from the pinned D. 541-1. Only structure (base, complement
category, MPI channel, entitlement, positions) is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open; (c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

## OpenFisca

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 1 | 2012-01, couple, one 9-year-old disabled child, handicap level 4; BMAF 395.04, expectation 395.04 x (0.32 + 0.92) = 489.8496 | base 126.4128 + complement cat. 3 (0.92) 363.4368 = total 489.8496; entitlement via the package head on the established CDAPH fact | (a) |
| 2 | 2012-01, couple, one 9-year-old disabled child, no handicap level; BMAF 395.04, expectation 395.04 x 0.32 = 126.4128 | base 126.4128, sans_complement + sans_mpi; total 126.4128 | (a) |
| 3 | 2024-01, single carer, one disabled child, no handicap level; BMAF 445.93, expectation 445.93 x 0.32 = 142.6976 | base 142.6976, sans_complement + sans_mpi; total 142.6976 | (a) |

Notes.

- 1: mapping OF niveau 4 (non-isolated) = complement category 3 without
  MPI (OF aeeh.py: niveau 4 → complement.categorie_3 + majoration
  categorie_4 x isole; isole = 0 for a couple). Hand arithmetic first
  mis-computed the products (363.3168/488.8496); machine-checked values
  363.4368/489.8496 now asserted.
- 2/3: no handicap level = sans_complement + sans_mpi; the single-carer
  majoration (D. 541-2) does not attach without a category.
- No Catala AEEH program exists upstream: OpenFisca only.
- DSS_PENDING: the 80% incapacity threshold, category criteria and MTP
  euro figure arrive as adjudicated/case inputs (B-PFAEEH-SEUIL,
  B-PFAEEH-CATEGORIE, B-PFAEEH-MTP).
- BLIND_PENDING: 24 blind second-reading cases in
  `analysis/blind-read-cases.json` (inputs only, no answers).
