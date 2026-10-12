# AEEH reader corrigendum and static run gate

Reviewer: independent Luna  
Date: 2026-10-08  
Receipt: `.scratch/fr-cnaf-finish/nochecks-20261008/aeeh-repair-20261007T223518947073Z.run.json` (EXITED, exit code 0)  
Gate: **READY_FOR_RUN**  
Runtime: **NOT_RUN**

## Purpose and immutable record

This corrigendum records the source-backed class (б) corrections for two answers in the sealed source-only set. It does not rewrite or replace `analysis/finish-blind-read.json`; that original remains immutable, with its SHA-256 `1162684ebc4c5a6013fd83221c11af51b977037877891c7b3da3de617c225e00` unchanged from phase 2. The original answer discrepancies remain visible as history, with corrected reader conclusions recorded here.

The canonical classes used here are **(а) model**, **(б) reader**, and **(в) input/edition/source**.

## Recorded reader corrections

### Case 09 — category 6 is undetermined on the supplied facts

**Class (б), recorded correction.** The sealed value `categorie6_criteres_remplis: false` and explanation “Sans contraintes permanentes” overstate the supplied evidence: the case gives no permanent-constraint record, which is not affirmative proof that permanent family supervision and care constraints are absent. Pinned R. 541-2 makes those constraints a category-6 condition (`sources/css/R541-2.txt:15`). Under the package’s open-world input contract, a missing premise does not establish its negation (`package.law:135-156`).

Corrected source conclusion: **category 6 is undetermined (NEITHER on the supplied record); category 4(a) is satisfied** because the case affirmatively states total cessation of a parent's professional activity, matching R. 541-2 (`sources/css/R541-2.txt:11-15`). The original answer bytes remain untouched.

### Case 23 — no 2021 death extension under the applicable pinned editions

**Class (б), recorded correction.** The sealed answer’s `SOURCE_PENDING` status is incorrect. For the stated 2021 death, the applicable R. 541-4 version (2019 wording) has no section V or death-continuation clause (`sources/css/R541-4-2019.txt:1-13`); contemporaneous R. 541-1 likewise has no death extension (`sources/editions/CSS_ED2021_01.txt:35-40`). This is an applicable historical text with no such extension, not an unpinned-source gap. The later R. 541-4 V applies from 2022-01-31 in the package (`10-deces-prolongation.law:45-50`) and is not backdated.

Corrected source conclusion: **the applicable pinned 2021 provisions establish no three-month death-continuation entitlement, so no continuation amount is established on that basis**. This does not claim that no other benefit or legal provision could apply outside the reviewed pinned sources. The original answer bytes remain untouched.

## Static run gate

The 71-rule source/model inventory and the F-01 through F-03 repair reassessment are recorded in `re-review-03.md` and `re-review-03.json`. The current R. 541-4 rules and paired controls are source-concordant: special duration requires both stated affirmative triggers and the derogation record, ordinary due-end cases require adjudicated ordinary regime plus affirmative evidence that one trigger is absent, and the missing-regime control remains silent. The 50–80% edition/cohort boundary at 2026-04-01 is retained. R. 541-3 completeness requires all listed branches and the useful-pieces fact bound to the same filing, with adjudicated dossier provenance.

No class (а) discrepancy remains in the current rules after static review. The two class (б) discrepancies are now explicitly recorded above as reader corrections; immutable answer originals remain available for comparison. No unresolved class (в) issue blocks the static gate: the source does not name a usefulness evaluator, and the evaluator identity remains an explicit source boundary; the dossier fact is adjudicated case provenance, not an invented MDPH delegation. The filing-date join and multi-filing identity limitation are stated input boundaries (`package.law:138-143, 190-197, 544-548`; `07-procedure-demande.law:80-87`). Other documented external/unpinned thresholds, urgency deadline, and PCH mechanics remain boundaries, not inferred rules.

Therefore the independent **static** gate is **READY_FOR_RUN**. This means the package may proceed to the separately authorized run queue; it is not a claim that a run occurred or passed. **Runtime: NOT_RUN**. No engine, test, audit, gate, generator, source hash check, or package verification was run for this corrigendum. Parser validity, fresh snapshot coverage, scenario execution, audit completeness, source-hash gate, lawref execution, and Rust semantics remain pending.

Files added by this corrigendum:

- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/reader-corrigendum.md`
- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/reader-corrigendum.json`
- appended `2026-10-08 reader corrigendum / static gate` journal entry in `docs/foundations/fr-cnaf/lines/finish-aeeh-review-nochecks.md`

No normative source, test, generated artifact, registry, sealed answer, or blind input was modified.
