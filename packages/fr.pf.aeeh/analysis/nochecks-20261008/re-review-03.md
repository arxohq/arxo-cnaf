# AEEH repair re-review 03 — static

Reviewer: independent Luna  
Date: 2026-10-08  
Repair receipt: `.scratch/fr-cnaf-finish/nochecks-20261008/aeeh-repair-20261007T223518947073Z.run.json`, `EXITED`, exit code 0  
Result: **CHANGES_REQUESTED**  
Runtime: **NOT_RUN**

## Scope and disposition

I read the author’s third repair only after the native receipt reported exit code 0 and the line journal reported `AUTHOR_READY_FOR_REVIEW`. I statically re-read the changed R. 541-4 rules/tests, R. 541-3 completeness input contract/tests, package boundaries, pinned source text, and the two still-open sealed-answer discrepancies. The three rule-level repair points are now source-concordant on static review: R. 541-4 ordinary controls carry affirmative evidence that at least one derogation trigger is absent; the 50–80% source cohort remains split at 2026-04-01; and completeness requires a filing-bound adjudicated dossier fact. I found no new rule-level discrepancy in these changes.

The immutable source-only answer file still has two reader findings, so this review does not issue `READY_FOR_RUN`. The owner-controlled answer process must resolve them before this line can be called discrepancy-free. The old seal is intact: `analysis/finish-blind-read.json` SHA-256 `1162684ebc4c5a6013fd83221c11af51b977037877891c7b3da3de617c225e00`, matching the phase-2 record. Neither sealed answers nor blind inputs were modified.

## Canonical findings

- **(а) model** — a rule or scenario admits a source-inconsistent result.
- **(б) reader** — a sealed source-only answer misreads or overstates what pinned text establishes.
- **(в) input/edition/source** — a required case input, edition boundary, or source channel remains unresolved.

### R3-01 — sealed case 09 infers a negative from an absent record

**Class (б), reader; material, owner-process action required.** The sealed case 09 answer says category-6 criteria are false because there is “No permanent-constraint record” (`analysis/finish-blind-read.json`, answer `pfaeeh-finish-09`). Pinned R. 541-2 requires permanent family supervision and care constraints for category 6 (`sources/css/R541-2.txt:15`); absence of a recorded fact does not establish the condition’s negation under the package’s open-world input contract (`package.law:135-156`). The category 4(a) conclusion based on total work cessation remains supported.

**Exact owner request:** keep the sealed bytes untouched until authorized answer revision. In that revision, retain category 4(a) as supported and leave category 6 undetermined unless the case supplies affirmative evidence that the permanent constraints are absent.

### R3-02 — sealed case 23 treats an applicable historical text as missing

**Class (б), reader; material, owner-process action required.** For the 2021 death, the applicable pinned R. 541-4 (2019) contains no section V (`sources/css/R541-4-2019.txt:1-13`), and the contemporaneous R. 541-1 edition contains no death-continuation provision (`sources/editions/CSS_ED2021_01.txt:35-40`). Calling this `SOURCE_PENDING` confuses a later rule’s non-applicability with missing source coverage (`analysis/finish-blind-read.json`, answer `pfaeeh-finish-23`). The model’s extension begins 2022-01-31 (`10-deces-prolongation.law:45-50`), consistent with the temporal boundary.

**Exact owner request:** preserve sealed bytes pending the owner-controlled answer process. Revise the 2021 answer to say the applicable pinned editions provide no R. 541-4 V death extension; do not backdate the later clause.

No (а) or (в) finding remains from the current F-01/F-02/F-03 repairs. The completeness evaluator’s identity remains explicitly unspecified by the source and is recorded as a boundary, not attributed to the MDPH (`package.law:138-143, 190-197`). The relation is keyed by child and filing date (`package.law:544-548`); multi-filing identity beyond the filing-date join remains an explicit input boundary, and the reviewed rule binds its result to the same `depot` (`07-procedure-demande.law:80-87`).

## Re-review of repair points and paired scenarios

- **F-01 / R. 541-4 derogation:** pinned current text says “Par dérogation” and requires an improvement prospect expressly mentioned in the certificate *and* a team proposal (`sources/css/R541-4.txt:5-6`). `BornesDuree80` and current 50–80% special bounds require both affirmative triggers plus the adjudicated derogation regime (`08-durees-revision.law:82-115`). Each ordinary due-end rule requires an adjudicated ordinary regime and one affirmative no-trigger record (`08-durees-revision.law:141-237`). The 80% scenarios now provide two separate ordinary controls: team proposal + `certificat_sans_perspective`, and prospect + `equipe_sans_proposition`, each with an AAH trigger; each expects only due-end, while the special child expects only bounds and the full-trigger/no-regime child is NEITHER (`tests/r541-derogation-80.lawtest:1-13, 27-43, 45-75`). The 2026 50–80% scenario mirrors those branches with filing cohort and conditions-end trigger, and retains the missing-regime and pre-cutoff controls (`tests/r541-derogation-5080.lawtest:1-13, 18-90`). These are feasible, source-aligned tests: absence is asserted affirmatively, never inferred from an omitted positive fact. Static review does not claim the scenarios execute.
- **F-02 / edition cohort:** the current 50–80% special rule is effective from 2026-04-01, anchored only to the current R. 541-4, and requires a filing date on/after the cutoff; the pre-cutoff rule retains the unconditional section-II 2–5 year period and no prospect condition (`08-durees-revision.law:99-136`). The pinned 2026 NOTA limits the new wording to initial and renewal filings from 1 April 2026 (`sources/css/R541-4.txt:13`). The old/new cohort scenarios preserve that boundary (`tests/r541-derogation-5080.lawtest:11-13` and cohort cases). No F-02 discrepancy found.
- **F-03 / R. 541-3 completeness:** source requires all useful supporting documents, the medical certificate, and the two declaration branches (`sources/css/R541-3.txt:3-8`). `DemandeComplete` now requires the filed request, certificate, both declarations, and `pieces_utiles_completes(e,depot)` (`07-procedure-demande.law:74-87`). The package states that this is an adjudicated dossier record, binds it to the filing date, and records that the source does not name the evaluator (`package.law:138-143, 190-197, 544-548`). The paired test has a complete positive dossier record, a missing declaration, and a complete set of named statutory pieces without a dossier usefulness record; the last two remain NEITHER (`tests/r541-demande-complete.lawtest:1-31`). This addresses the earlier open-world overclaim without inventing MDPH authority. The record’s decision-maker remains case provenance/source boundary.

## Whole-rule inventory

I reconciled the current whole 71-rule finish-wave inventory to the current module declarations, pinned R. 541-1 through R. 541-10 text, and the previously reviewed unchanged modules. All 71 rules were checked; current changed rules in 07 and 08 were re-read in this pass. Inventory checked:

- `05-seuils-taux.law` — **5**: `Seuil80Atteint`, `Seuil50Atteint`, `Tranche5080`, `PriseEnChargeReconnue`, `ModaliteVersementAnnuel`.
- `06-categories.law` — **20**: `CritereCategorie1Depenses`; `CritereCategorie2Reduction`, `CritereCategorie2Tierce`, `CritereCategorie2Depenses`; `CritereCategorie3aReduction`, `CritereCategorie3aTierce`, `CritereCategorie3bReductionDepenses`, `CritereCategorie3bTierceDepenses`, `CritereCategorie3cDepenses`; `CritereCategorie4aCessation`, `CritereCategorie4aTiercePlein`, `CritereCategorie4bReductionDepenses`, `CritereCategorie4bTierceDepenses`, `CritereCategorie4cReductionDepenses`, `CritereCategorie4cTierceDepenses`, `CritereCategorie4dDepenses`; `CritereCategorie5CessationDepenses`, `CritereCategorie5TierceDepenses`; `CritereCategorie6CessationContraintes`, `CritereCategorie6TierceContraintes`.
- `07-procedure-demande.law` — **8**: `DemandeComplete`, `DevoirJoindrePieces`, `DevoirTransmettreDossier`, `DevoirDeposerDemandePCH`, `ExclusionChargesComplement`, `DevoirReviserDecisionPCH`, `DevoirReexaminerComplementPCH`, `InterdictionOpterAvantEcheance`.
- `08-durees-revision.law` — **22**: `BornesDuree80`, `BornesDuree5080`, `BornesDuree5080AncienneCohorte`, `FinExclusiveAAH80SansPerspective`, `FinExclusiveAAH80SansProposition`, `FinExclusiveConditions80SansPerspective`, `FinExclusiveConditions80SansProposition`, `FinExclusiveAAH5080SansPerspective`, `FinExclusiveAAH5080SansProposition`, `FinExclusiveConditions5080SansPerspective`, `FinExclusiveConditions5080SansProposition`, `DroitMaintenuChangement`, `LiberteRevisionBeneficiaire`, `LiberteRevisionOrganisme`, `DevoirReexaminerAggravation`, `LiberteControlerEffectivite`, `DevoirSaisirCommission`, `DevoirVerserAvance`, `DevoirStatuerUrgence`, `DateLimiteReexamen`, `DevoirReexaminerMesures`, `ReexamenEnRetard`.
- `09-dates-effet.law` — **13**: `DateRejetImplicite`, `RejetImplicite`, `DateDebutDroit`, `DateFinSuppressionSansAAH`, `DateFinSuppressionAvecAAH`, `PontR5122`, `DateFinComplementPCH`, `DevoirSuspendreComplement`, `DevoirRetablirComplement`, `DateAssimilationHospitalisation`, `AssimilationHospitalisation`, `DefeaterContraintesHospitalisation`, `LiberteMaintienVersement`.
- `10-deces-prolongation.law` — **3**: `DateFinProlongationDeces`, `MontantProlongationMoisDeces`, `MontantProlongationMoisPrecedent`.

**Total: 71 checked.** Existing stated boundaries remain: unpinned guide/order thresholds and deadlines, external PCH mechanics, and the usefulness evaluator/source channel. There are no new rule findings in this inventory. The two sealed reader findings above remain open. Runtime remains **NOT_RUN**: no engine, test, audit, generator, gate, or verification script was invoked; this document is not a parser, source-hash-gate, audit-completeness, lawref, or Rust-semantic result.

## Files added

- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/re-review-03.md`
- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/re-review-03.json`
- appended `2026-10-08 re-review 03` section in `docs/foundations/fr-cnaf/lines/finish-aeeh-review-nochecks.md`

No normative file, source, test, generated artifact, snapshot, registry, blind input, or sealed answer was edited by this reviewer.
