# Foreign benchmarks report — `fr.pf.ajpp`

Benchmarks (OpenFisca-France AJPP parameters) are expectations, never
semantic sources. Only structure (ceilings, amounts under retained rates)
is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open; (c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

## OpenFisca

OpenFisca AJPP has no model and no test cases upstream — only frozen
parameters (`parameters/prestations_sociales/education_presence_parentale/ajpp`,
2006-06-05): 22 monthly days, 3-year maximum duration, couple fraction
0.1063 and single fraction 0.1263 of the daily SMIC base. Documentary
measurement in [`openfisca/NOTE.md`](openfisca/NOTE.md).

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| OF-22 | frozen 22 monthly days | 22 allowance days within the retained maximum 22 | (b) rate assumption: the 22 is an assumed decree input (B-PFAJPP-D544), not a pinned computation |

Notes.

- The frozen fractions (0.1063/0.1263) and the 3-year duration were not
  recomputed here while no SMIC figure and no duration arithmetic were
  pinned; the FINISH ajpp-death wave pins them as decree text
  (D. 544-6 2020 rates, D. 544-1) with params and rules — the
  measurement above stays as history.
- DSS_PENDING (partly closed): monthly max days, multi-year duration,
  daily-rate formula and 2021 BMAF rates, expense-complement
  rate/threshold, job-seeker flat days are now pinned decree text
  (D. 544-x, R. 544-x, FINISH ajpp-death). Still pending: the retained
  BMAF euro figure, the net hourly SMIC, the CRDS rate, the R. 522-2
  annual ceiling and R. 532-1 assessed resources (case inputs with
  provenance).
- BLIND_PENDING: 24 blind second-reading cases in
  `analysis/blind-read-cases.json` (inputs only, no answers); the FINISH
  decree surface is read blind by independent Luna.
