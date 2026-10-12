# `fr.pf.aeeh` — disabled-child education allowance (allocation d'éducation de l'enfant handicapé)

Executable formalization of the AEEH core: the base allowance at 32% of
the retained BMAF (L. 541-1), six complement categories as retained
fractions of the BMAF (D. 541-1), the single-parent majoration (D. 541-2),
the disability-related work-cost increase MPI (L. 541-4, D. 541-3/4, zeros
carried), the CDAPH decision as established channel fact, the
non-follow-up suspension liberty (L. 541-2) and the fund payment duty.

Scope: exactly 21 articles (L541-1/2/3/4/5, D541-1/2/3/4,
R541-1..10, L755-20, D755-11: DOM transfer, D-73). Upstream principle-level filters (`AeehDecisionCdaph`,
`aeeh_ouvre_droit`) are package-internal (§24) and cannot be read here:
the computation head runs on the package-local established fact
(B-PFAEEH-TETE).

Finish wave (R. 541-1..10, multisession, author pass — checks NOT run by
the author, acceptance NOT claimed): 80 %/50 % thresholds and the 50-80 %
tranche as pinned Decimal parameters; the six-category criteria as an
executable verification skeleton (the commission classification itself
stays the established fact); demande completeness (certificate + both
declaration branches + adjudicated dossier useful-pieces record bound to
the filing date, evaluator unspecified) with carer/MDPH duties; duration
bounds and exclusive due-ends under an explicit award regime (the
«Par dérogation» special period displaces the ordinary 1°/2° for the same
award; the ordinary head requires an affirmative no-trigger record; the
2026 50-80 % heads require the initial/renewal filing cohort from
2026-04-01, decree 2026-227 NOTA, older filings keeping
the unconditional 2-5 year period), revision liberties, the
control/saisine/advance chain, reexamination deadlines; the four-month
silence fiction (exclusive +4-month threshold); award, suppression,
PCH-option and hospitalization dates; PCH interplay duties (third-element
intention, expense subtype, L. 245-1 III 1° status, handicap/factor
evolution) and the pre-expiry option prohibition (L. 245-3 2°/4°/5°
elements); the post-2022-01-31 death extension (general end date +
higher-of-two-months amount for L. 541-1 para. 4 periods). Seven editions run
back to back from 2005-02-12 (the in-coverage debuts 2022-01-31 and
2026-04-01 open CSS_ED2022_01/CSS_ED2026_04); three in-window superseded
R versions are pinned (R541-1-PRE2022, R541-4-PRE2022/PRE2026). Adopted
reading (not disputed): «premier/dernier jour du troisième mois civil
suivant» counts the following months exclusive of the event month;
«dernier jour du mois précédent» is the equivalent exclusive bound
«premier jour du mois». Boundaries: B-PFAEEH-GUIDE-BAREME,
B-PFAEEH-SEUILS-ARRETE, B-PFAEEH-GUIDE-EVALUATION, B-PFAEEH-TEMPS-PLEIN,
B-PFAEEH-MODELE-ARRETE, B-PFAEEH-PIECES-APPRECIATION,
B-PFAEEH-DELAI-URGENCE, B-PFAEEH-PCH-MECANIQUE
(see package.law). Calendar scenarios bind the declared deadline policy
in context (`AEEH_DUREES` / `AEEH_MOIS_CIVIL` / `AEEH_PROLONGATION`).
New suites: 29 `tests/r541-*.lawtest` in six families (`#seuils-taux`,
`#categories`, `#procedure-demande`, `#durees-revision`,
`#dates-effet`, `#deces-prolongation`) plus `aeeh-base-2026-05` in
`#droit-montant`; 24 neutral blind cases in
`analysis/finish-blind-read-cases.json` (no answers; prior blind
artifacts untouched).

DOM transfer (D-73, author pass — checks NOT run by the author,
acceptance NOT claimed): L. 755-20 attribution in the six L. 751-1
collectivities as six strict rules (one per collectivity, no `or`
across value relations) concluding `aeeh_attribuee_dom` for an entitled
resident child; D. 755-11 DOM/metropolitan amount identity as build
(`montant_aeeh_dom` from the computed total) + check
(`montant_aeeh_dom_verifie`, presented vs built). Institutional norms
only: no new duty, prohibition, power or liberty (payment stays D1).
Both pinned versions cover the whole window (L755-20 since 2015-10-16,
D755-11 since 2006-01-01), no predecessors, no new editions, no bareme
rows (no figures in either sentence). Boundaries:
B-PFAEEH-DOM-L751-1 (list unpinned here; values from the pinned Title V
header), B-PFAEEH-DOM-DECRET-CONDITIONS (D. 755-11 is the pinned
operative decree provision for amounts). New suites: 4
`tests/dom-*.lawtest` in family `#dom-aeeh`. Generated outputs pending
reviewer run: `01-sources.law` fragments (predicted +9: 3 L755-20, 6
D755-11), `sources/css/L755-20.txt`, `sources/css/D755-11.txt`, edition
texts, `sources/articles.json`, `sources/fragment-map.json`
(GENERATED_OUTPUT_PENDING — never hand-edited).

## Measure

`law audit .` (formalization measure, static profile, wave-3 core):
20 rules, dangling premises 6 (all enum variants in bodies, none
unsupplied), one-way premises 0 of 20. Form catalog: 16 detectors,
0 findings. Measure not taken on 5 publications without presented text
(pre-coverage editions). Finish-wave measure NOT taken (author has no
execution; the Luna reviewer runs the package checks and the static
audit): rule/head counts below are author counts from the authored
modules, not tool output — 05: 5 rules, 06: 20, 07: 8, 08: 22, 09: 13,
10: 3 (71 rules), 11: 8 (79 total with the DOM transfer).

## Their case to our answer

Foreign benchmarks are expectations, never sources. Euro totals use the
stated BMAF of each case; complement fractions come from the pinned
D. 541-1. Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (OpenFisca AEEH 1–3;
classes (a)/(b)/(c) per case).

Reading guide:

- All three OpenFisca cases match exactly under the stated assumptions
  (a): the mapping is OF handicap level → complement category + MPI
  channel, entitlement via the package head on the established CDAPH
  fact. Machine-checked products (e.g. 395.04 x 0.92 = 363.4368).
