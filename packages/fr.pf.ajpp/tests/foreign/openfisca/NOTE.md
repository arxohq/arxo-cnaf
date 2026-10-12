# OpenFisca AJPP parameters — documentary measurement (B-PFAJPP-OF)

Source: `.scratch/openfisca-france/openfisca_france/model/prestations/
prestations_familiales/education_presence_parentale/ajpp/` (parameters
only, frozen 2006-06-05). There is no AJPP model and no AJPP test case
upstream.

Frozen figures (measurement only, never regressions):

- monthly maximum: 22 days (`duree_versement`, 2006-06-05);
- maximum duration: 3 years (`duree_max`, 2006-06-05);
- couple daily fraction: 0.1063 of the SMIC-derived base;
- single daily fraction: 0.1263 of the SMIC-derived base.

Why measurement only: the figures are parameters of a program that never
computes AJPP. The package used to model the statutory structure
(ceilings, renewal, amounts as retained-rate multiplications) with the
decree figures as case inputs (B-PFAJPP-D544). The single regression
importing this measurement is
`tests/foreign/openfisca/of-2006-06-mensuel-22.lawtest`: 22 days within
the retained maximum 22 — a structure check under the stated assumption,
class (b) in [`REPORT.md`](../REPORT.md).

FINISH ajpp-death (2026-10-07, no engine run): the same figures are now
pinned decree text — 22 monthly days (D. 544-4, PlafondMensuel22Jours),
3-year duration (D. 544-1, DureeMaxAjppAnnees), 10.63/12.63 %
(TauxJournalierCouple/Isole2021, window 2021) — with params and rules.
This note stays as the documentary history of the measurement.
