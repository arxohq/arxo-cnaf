# Foreign expectations — OpenFisca ASF (`tests/formulas/asf`)

OpenFisca numbers are expectations, never sources. All ports run on
stated illustrative BMAF 400.00 EUR in the 2021 window (D-01/D-15):
the 2015/2018/2020 benchmark periods are shaped to 2021 because the
producers are effective `[@2021-01-01, infinity)`. Rates come from the
pinned R. 523-7 rows (simple 0.2813 → 112.52; double 0.375 →
150.00; from 2022-11-01: 0.422 → 168.80, 0.5625 → 225.00).

| Benchmark | Their output | Our answer (stated BMAF 400) | Class |
|---|---|---|---|
| Seuil de non-versement (2020-01), pension 112 | 0 | differential 0.52 | (c) genuine: their 0 is the 15 EUR floor (D. 523-3), which the engine cannot fold (B-PFASF-SEUIL) |
| 2015 lone parent, 9yo | 96 | eligible, 112.52 | (b) shaped period + ground (orphan-of-one, unstated upstream) + their 2015 rate/BMAF |
| Limite d'âge 20 ans (2015-01) | 0 | no ground opens (NEITHER) | (b) upstream shaping: their `asf_elig_enfant` false; ASF per se carries no age bar |
| 2018-04 Cas 1, lone parent | 115.87 | eligible, 112.52 | (b) shaped period + ground (single default with carence, unstated upstream) + their April-2018 BMAF |
| 2018-04 Cas 2, two children | 231.74 | 112.52 per child | (b) same shaping; per-child independence confirmed (2 × 115.87 = theirs) |
| 2018-04 Cas 3, pension 50 | 65.87 | differential 62.52 | (b) same shaping; confirms the 4° mechanics (ASF − pension: 115.87 − 50 = theirs) |

Reading guide:

- The 2018-04 trio confirms the rate mapping (simple rate for the
  lone-parent track) and the differential mechanics
  (allowance − pension), both reproduced exactly up to their BMAF.
- The seuil case confirms the live boundary: a 3.87-scale
  differential vanishes under their floor while ours computes brut.
- The age-bar case confirms the architecture: the 20-year cutoff
  arrives upstream (`enfant_ouvre_droit`), never from the ASF
  articles in scope.
- No Catala counterpart exists for ASF in the pinned inputs.
