# `fr.pf.ajpp` — daily parental-presence allowance (allocation journalière de présence parentale)

Executable formalization of the AJPP core: the right opened by the
detailed certificate plus the medical-control agreement plus parental
leave (L. 544-2), the foreseeable-duration re-exam window (6 / 12 then 14
months, bareme), the 310-day ceiling with the exceptional once-renewal
(2021+) and relapse reopening plus the pending-agreement advance (2023+)
(L. 544-3), the monthly cap and daily-rate totals with the 2023-H1 single
majoration, the expense complement and the special-worker channels
(L. 544-4/6/7/8), the nine non-cumulation items in two generations with
the part-time sick exception (L. 544-9), and the fund information duty
(L. 544-10). The FINISH ajpp-death wave adds the decree layer: the
3-year limit, re-exam window and renewal, reopening delay and payment
branches (in-period delay vs beyond-maximum expiry gate), new pathology
(D. 544-1/2/3/5), the pinned 22-day cap, SMIC
formula and 2021 BMAF rates, computed complement threshold, job-seeker
flat 22 (D. 544-4/6/7/8), file completeness, competent service, silence
rules and the monthly and expense duties (R. 544-1/2/3, D. 544-8/9/10).
The D73 owner transfer adds the L. 751-1 collectivity attribution
(L. 755-33). F05-01 qualifies every monthly daily amount on the month
conformity (daily 22 or flat 22) plus the envelope: the initial or
once-renewal 310-day count with the three-year duration, or the
beyond-maximum reopening route — never a blanket lifetime cap.

Scope: exactly 22 articles (L544-2/3/4/6/7/8/9/10, D544-1..10,
R544-1/2/3, L755-33). The base right (L. 544-1) is SANS_OWNER with a future
abrogation: boundary quote, never cited. The retained BMAF figure, the
net hourly SMIC and the CRDS rate arrive as case inputs with provenance
(B-PFAJPP-BMAF-FIGURE, B-PFAJPP-SHN-NET, B-PFAJPP-CRDS-TAUX).

## Measure

Pre-FINISH: `law audit .` (formalization measure, static profile):
21 rules, dangling premises 0, one-way premises 1 of 21. Form catalog:
16 detectors, 0 findings. Measure not taken on 11 publications without
presented text (pre-coverage editions).

FINISH measure: GENERATED_OUTPUT_PENDING — the source regeneration
(new SCOPE/OLD/editions) and the audit rerun sit in the deferred queue
(no engine execution in this authoring round).

## Their case to our answer

Foreign benchmarks are expectations, never sources. OpenFisca AJPP
parameters (frozen 2006-06-05: 22 monthly days, 3-year duration, 0.1063
couple / 0.1263 single fractions) were parameters without a model
upstream; the FINISH wave pins the same figures as decree text (D. 544-4,
D. 544-1, D. 544-6 2020) with params and rules — the documentary
measurement stays as history. Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (OpenFisca AJPP
measurement; classes (a)/(b)/(c) per case).
