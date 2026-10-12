# Static review — AEEH finish repair

Reviewer: independent Luna static pass  
Date: 2026-10-08  
Package: `corpus/laws/fr/pf-aeeh`  
Runtime: `NOT_RUN` (no engine, generator, audit, or test command was invoked)

## Result

**CHANGES_REQUESTED.** The sealed source-only answer file is intact, but the current package still has a source/model conflict around the express R. 541-4 derogation. The review also found an overbroad completeness conclusion and two source-only answer classifications that should be corrected in a later blind-answer revision. No normative file was edited in this review.

The prior sealed answer file `analysis/finish-blind-read.json` has SHA-256 `1162684ebc4c5a6013fd83221c11af51b977037877891c7b3da3de617c225e00`, matching the hash recorded in `analysis/finish-review-phase2.md`. It was read as static evidence and left byte-for-byte unchanged. Source citations and statutory language below were checked against the pinned local bytes; this is not a source-hash gate result.

## Findings and exact repair requests

### F-01 — R. 541-4 I derogation can coexist with ordinary due-end

**Severity: blocking.** `08-durees-revision.law:76-99` derives special 3–5 / 2–5 year bounds when the improvement prospect and team proposal are present. `08-durees-revision.law:130-169` independently derives the ordinary due-end for 80% cases and, for the 2026 filing cohort, 50–80% cases. The pinned 2022 text says the special provision applies “Par dérogation aux dispositions des deuxième et troisième alinéas” (`sources/css/R541-4-2022.txt:2-7`); the current text has the same derogation (`sources/css/R541-4.txt:2-7`). For a single applicable initial/renewal award with a qualifying prospect/team proposal and AAH opening or cessation of conditions, the model can therefore conclude both the special period and the ordinary due-end.

The existing tests do not exercise this same-child conflict: `tests/r541-bornes-duree.lawtest:13-34` pairs an 80% special duration with an AAH opening only for the 60% child; `tests/r541-cohorte-2026.lawtest:19-44` tests 50–80% cohort selection without the prospect/team predicates. This matches the phase-2 review finding and remains unresolved.

**Author repair request:** model the 2026 derogation against the ordinary due-end using an explicit, source-supported attribution regime/input. Keep filing date as the selector required by the Decree 2026-227 NOTA (`sources/css/R541-4.txt:14`), and keep historical editions separate. Do not use absence of a prospect/team fact as proof that the derogation is inapplicable. Add paired scenarios for 80% and 50–80% where the same award has the derogation facts and the ordinary end trigger, plus the corresponding ordinary-regime cases with affirmative evidence that the derogation does not apply. Preserve old-edition behavior: the 2022/2019 50–80% rule is the unconditional 2–5 year rule in section II (`sources/css/R541-4-2022.txt:7`), while the 2019 special wording concerns the 80% provision (`sources/css/R541-4-2019.txt:2-7`).

### F-02 — 50–80% prospect rule cites editions that do not contain it

**Severity: material source-fidelity defect.** `08-durees-revision.law:88-99` anchors `BornesDuree5080` to `CSS_R541_4_PRE2022`, `CSS_R541_4_PRE2026`, and the current `CSS_R541_4`. The 2019 and 2022 pinned texts provide an unconditional 2–5 year period for 50–80% in section II (`sources/css/R541-4-2019.txt:7`; `sources/css/R541-4-2022.txt:7`). The improvement-prospect derogation in those editions is not a 50–80% rule. The separate `BornesDuree5080AncienneCohorte` at lines 115-121 correctly captures the prior-cohort 2–5 year period, while the new wording and its filing cutoff are in the current text.

**Author repair request:** separate the historical unconditional 50–80% duration from the current special prospect rule. Anchor the latter only to the edition(s) containing that 50–80% derogation and gate it on the 2026-04-01 filing cohort. Keep `BornesDuree5080AncienneCohorte` tied to an actual filing date before the cutoff. Add a direct source-window pair proving an older filing gets the unconditional range without needing prospect/team facts and a qualifying current filing gets the special rule.

### F-03 — request completeness is concluded without the open-ended useful-documents condition

**Severity: material open-world overclaim.** `07-procedure-demande.law:74-80` concludes `demande_complete(e)` from the medical certificate and two declaration branches alone. R. 541-3's pinned text additionally requires “toutes les pièces justificatives utiles à l'appréciation des droits de l'intéressé” (`sources/css/R541-3.txt:3-8`); the sealed case 10 itself acknowledges its answer is limited to listed pieces and that other useful pieces may depend on the file (`analysis/finish-blind-read.json`, `pfaeeh-finish-10`). A missing record of further useful pieces cannot establish that none are needed.

**Author repair request:** either rename/narrow the derived head so it means only that the statutory certificate and declaration branches are present, or add an explicit dossier-level fact establishing that all useful supporting documents for this applicant are present before deriving `demande_complete`. Do not infer that no additional document is useful from its absence. Preserve the existing incomplete-document pair.

### F-04 — sealed case 09 turns an absent record into a negative category-6 fact

**Preliminary class A: source-only answer defect.** Case 09 says “No permanent-constraint record” and the sealed answer concludes `categorie6_criteres_remplis: false`. R. 541-2 requires permanent supervision and care constraints for category 6 (`sources/css/R541-2.txt:15`); absence of a record does not establish their nonexistence. The package's open-world contract is explicit at `package.law:135-156`, and the model's positive gates are at `06-categories.law:308-325`. The category 4(a) positive result from total cessation is source-supported; only the category-6 negative answer is unsupported.

**Answer repair request (owner-controlled sealed-answer process):** preserve this sealed file until authorized; in any later answer version mark category 6 pending/undetermined unless the case supplies an affirmative contrary fact. Do not add a negative fact to the model or use the sealed answer as an expectation.

### F-05 — sealed case 23 labels an inapplicable rule as a source gap

**Preliminary class A: source-only answer defect.** For the 2021-06-15 death, the applicable pinned R. 541-4 version has no section V and the applicable R. 541-1 version has no death extension. The answer's `SOURCE_PENDING` classification is therefore not supported: the pinned historical texts establish that this package's later continuation rule does not apply to that date. Compare the complete pinned version `sources/css/R541-4-2019.txt:1-13` with R. 541-1 in `sources/editions/CSS_ED2021_01.txt:35-40`, and the later death clauses in `sources/css/R541-4.txt:13` and current R. 541-1. The existing `10-deces-prolongation.law:45-50` correctly starts the extension on 2022-01-31.

**Answer repair request (owner-controlled sealed-answer process):** preserve the file until authorized; classify the 2021 probe as no extension under the applicable pinned versions, with amount comparison inapplicable. Never backdate the 2022 clause.

## Blind-answer comparison: preliminary classes

Classes used here: **A** = source-only sealed answer issue; **B** = model/source or input-contract defect; **C** = indeterminate because the case omits a source-required input. These are static preliminary classes, not runtime comparison results.

| Cases | Preliminary classification |
|---|---|
| 01–08 | No static discrepancy found in the sealed values against the pinned thresholds and category gates. Case 05 remains `SOURCE_PENDING` because the expense threshold is delegated to an unpinned order. |
| 09 | **A / F-04:** absence of a constraint record cannot support a false category-6 result. |
| 10 | **B / F-03:** answer caveat is correct; model's `demande_complete` head is broader than the stated facts support. |
| 11 | No discrepancy found: the required declaration branch is expressly missing. |
| 12–14 | Case 12's MDPH transmission is source-supported; the PCH filing duty is pending without a third-element request. Cases 13–14 correctly remain pending without the subtype/eligibility facts R. 541-10 names. Model input distinctions remain contingent on typed scenario facts. |
| 15–16 | **B / F-01:** the same-period derogation interaction needs to be settled and tested. Case 16's historical 50–80% range is source-supported by section II. |
| 17 | **C:** the answer correctly leaves the 2026 50–80% due-end pending because the initial/renewal filing date is absent; `legal_time` is not a substitute. |
| 18–22 | No static discrepancy found against the pinned two-year re-examination, strict-over-four-month rejection, month-boundary dates, and third-following-month hospitalization rules. |
| 23 | **A / F-05:** later death-continuation law is not a source gap for the 2021 death. |
| 24 | No discrepancy found: R. 541-4 V supports the 2024 end date; the R. 541-1 amount comparison is limited to L. 541-1 fourth-paragraph periods, which the facts do not establish. |

## Rule inventory and review coverage

Static source/model pass completed for the 67 finish-wave rules in modules 05–10; scenario families and cited article windows were read, but no evaluation was run. Module totals and inventory:

- `05-seuils-taux.law` (5): `Seuil80Atteint`, `Seuil50Atteint`, `Tranche5080`, `PriseEnChargeReconnue`, `ModaliteVersementAnnuel` — checked against R. 541-1.
- `06-categories.law` (20): `CritereCategorie1Depenses`; `CritereCategorie2Reduction`, `CritereCategorie2Tierce`, `CritereCategorie2Depenses`; `CritereCategorie3aReduction`, `CritereCategorie3aTierce`, `CritereCategorie3bReductionDepenses`, `CritereCategorie3bTierceDepenses`, `CritereCategorie3cDepenses`; `CritereCategorie4aCessation`, `CritereCategorie4aTiercePlein`, `CritereCategorie4bReductionDepenses`, `CritereCategorie4bTierceDepenses`, `CritereCategorie4cReductionDepenses`, `CritereCategorie4cTierceDepenses`, `CritereCategorie4dDepenses`; `CritereCategorie5CessationDepenses`, `CritereCategorie5TierceDepenses`; `CritereCategorie6CessationContraintes`, `CritereCategorie6TierceContraintes` — checked against R. 541-2. Delegated expense values, evaluation guide, and legal full-time reference remain explicit boundaries.
- `07-procedure-demande.law` (8): `DemandeComplete`, `DevoirJoindrePieces`, `DevoirTransmettreDossier`, `DevoirDeposerDemandePCH`, `ExclusionChargesComplement`, `DevoirReviserDecisionPCH`, `DevoirReexaminerComplementPCH`, `InterdictionOpterAvantEcheance` — checked against R. 541-3, R. 541-9, R. 541-10; F-03 remains open.
- `08-durees-revision.law` (18): `BornesDuree80`, `BornesDuree5080`, `BornesDuree5080AncienneCohorte`, `FinExclusiveAAH80`, `FinExclusiveConditions80`, `FinExclusiveAAH5080`, `FinExclusiveConditions5080`, `DroitMaintenuChangement`, `LiberteRevisionBeneficiaire`, `LiberteRevisionOrganisme`, `DevoirReexaminerAggravation`, `LiberteControlerEffectivite`, `DevoirSaisirCommission`, `DevoirVerserAvance`, `DevoirStatuerUrgence`, `DateLimiteReexamen`, `DevoirReexaminerMesures`, `ReexamenEnRetard` — checked against R. 541-4 and R. 541-5. F-01/F-02 remain open. The urgent-decision number is delegated and not modelled.
- `09-dates-effet.law` (13): `DateRejetImplicite`, `RejetImplicite`, `DateDebutDroit`, `DateFinSuppressionSansAAH`, `DateFinSuppressionAvecAAH`, `PontR5122`, `DateFinComplementPCH`, `DevoirSuspendreComplement`, `DevoirRetablirComplement`, `DateAssimilationHospitalisation`, `AssimilationHospitalisation`, `DefeaterContraintesHospitalisation`, `LiberteMaintienVersement` — checked against R. 541-6, R. 541-7, R. 541-8.
- `10-deces-prolongation.law` (3): `DateFinProlongationDeces`, `MontantProlongationMoisDeces`, `MontantProlongationMoisPrecedent` — checked against R. 541-1 al. 5 and R. 541-4 V; historical window starts 2022-01-31.

Cross-read `02-droit-montant.law`, `03-pouvoir-suspension.law`, `04-devoir-versement.law`, `package.law`, README, source anchors and relevant `.lawtest` files for integration, deontic roles, use-self blocks and stated boundaries. Historical windows were compared to the pinned 2019, 2022, 2026 editions and the 2026 NOTA. Scenario behavior, parser validity, generated-source reproducibility, package audit depth, and execution semantics remain **pending runtime**.

## Exact deferred author/reviewer queue

1. Resolve F-01 and F-02 in the AEEH package, with filing-cohort-aware rules and paired same-period conflict scenarios. Any negative branch must use affirmative, source-grounded case evidence; do not treat missing facts as false.
2. Narrow or complete the input contract for `demande_complete` (F-03) and pair a complete statutory document set with a case that has an additional useful supporting document.
3. Keep F-04 and F-05 as sealed-answer review requests; no reviewer edits to sealed answer bytes.
4. After author changes and under the separate owner's authorized workflow, rebuild a fresh package snapshot and run only the appropriate package checks. Until that happens, source/model review is static only and runtime remains `NOT_RUN`.
