# Foreign benchmarks report — `fr.css.ajpa`

No OpenFisca AJPA model or parameters exist upstream, and no Catala AJPA
program exists: the DSS/CNAF statutory texts (pinned in `01-sources.law`)
and blind reading are the basis, never regressions. Each reading below
names its pinned fragment.

Classes: (a) text-direct reading under the stated assumptions;
(b) structure match with documented input shaping the text leaves open;
(c) genuine divergence between a foreign outcome and the adopted text
reading, recorded with a BOUNDARY marker and evidence;
ГРАНИЦА: out-of-scope mechanics, recorded with the boundary marker.

## Readings

| # | Reading | Pinned basis | Class |
|---|---------|--------------|-------|
| R1 | leave + stable residence open the right | CSS_L168_8 (all editions from 2021-01) | (a) |
| R2 | monthly total = retained daily rate x month days | CSS_L168_9 (every generation) | (a) |
| R3 | single-carer majoration ends 2023-07-21 | CSS_L168_9_PRE2022 / PRE2023 vs PRE2025 | (a) |
| R4 | 66-day career ceiling 2023-07-21 → 2025-01-01 | CSS_L168_9_PRE2025 («soixante-six») | (a) |
| R5 | monthly maximum from 2025-01-01, retained decree figure | CSS_L168_9 (2025) | (a), (b) decree figure |
| R6 | duration ceiling + renewal for another aided person, 2025+ | CSS_L168_9 (2025) | (a), (b) L. 3142-19 bound unchecked |
| R7 | 2019 ten-item non-cumulation list | CSS_L168_10_PRE2026 | (a) |
| R8 | 2025 list with birth-leave wording + NOTA birth scope | CSS_L168_10 (2025) | (a) |
| R9 | part-time sick exception both generations | CSS_L168_10_PRE2026 + CSS_L168_10 («Toutefois») | (a) |
| R10 | payment / recovery / recourse-information duties | CSS_L168_8 + CSS_L168_11 / CSS_L168_13 / CSS_L168_14 | (a), (b) option mechanics |
| G1 | 2019 extended channel (L. 544-8 persons, public agents) | unpinned (pre-coverage) | ГРАНИЦА B-PFAJPA-AVANT2021 |
| G2 | stillborn L168-9 2024 version (MODIFIE_MORT_NE) | unpinned (never in force) | ГРАНИЦА B-PFAJPA-AVANT2021 |
| G3 | decree euro figures, monthly max, duration, instalments | unpinned (D. 168-x/R. 168-x) | ГРАНИЦА B-PFAJPA-D168 |
| G4 | carer-leave grant, split/part-time conversion, L. 3142-19 bound | external (travail) | ГРАНИЦА B-PFAJPA-L3142 |
| G5 | prescription via L. 553-1; control/fraud applicability | external references | ГРАНИЦА B-PFAJPA-PRESCRIPTION / B-PFAJPA-FRAUDE |

Notes.

- DSS_PENDING: daily SMIC euro figure, monthly max days, duration
  ceiling and renewal terms, recovery instalment mechanics — case inputs
  with provenance until the DSS/CNAF bareme lane assigns them.
- BLIND_PENDING: 24 blind second-reading cases in
  `analysis/blind-read-cases.json` (inputs only, no answers).
