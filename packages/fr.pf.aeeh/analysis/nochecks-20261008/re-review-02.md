# AEEH repair re-review 02 — static

Reviewer: independent Luna  
Date: 2026-10-08  
Repair receipt: `.scratch/fr-cnaf-finish/nochecks-20261008/aeeh-repair-20261007T222053678255Z.run.json`, `EXITED`, exit code 0  
Result: **CHANGES_REQUESTED**  
Runtime: **NOT_RUN**

## Review scope and result

The final Muse repair was read only after its native receipt recorded exit code 0. The changes address the three earlier findings in the rules: an explicit R. 541-4 award-regime input, a 2026-only 50–80% prospect rule, and a dossier-level useful-pieces premise. The corresponding new/updated scenarios cover the source windows and missing-input behavior. `use self` was hand-edited in the author's own package modules 07 and 08; the declared symbols are present in `package.law`. No deferred `law fix imports` substitute was needed for this static review.

The source-only 24-answer file remains unchanged. SHA-256 is still `1162684ebc4c5a6013fd83221c11af51b977037877891c7b3da3de617c225e00`, matching the stored phase-2 seal. I did not edit or regenerate any blind answers.

The repair is not ready for a run because one new ordinary-regime test asserts facts that activate the statutory derogation while also asserting an ordinary attribution. The new useful-pieces relation also lacks the per-request provenance and scope needed to establish its open-ended relevance judgment. The two earlier source-only answer discrepancies remain for the owner's sealed-answer process.

## Canonical finding classes

- **(а) model** — the formal rules or a scenario admit a source-inconsistent result.
- **(б) reader** — a sealed source-only answer misreads or overstates what the pinned text establishes.
- **(в) input/edition/source** — a case lacks a required input, edition boundary is unresolved, or the pinned source does not specify the claimed channel.

## Findings

### R2-01 — ordinary-regime scenarios contradict the R. 541-4 derogation trigger

**Class (а), model/scenario.** The new `r541-derogation-80` ordinary child asserts `perspective_amelioration`, `proposition_equipe_pluridisciplinaire`, and `attribution_ordinaire_r5414` together (`tests/r541-derogation-80.lawtest:23-28`). The new `r541-derogation-5080` ordinary child asserts the same combination (`tests/r541-derogation-5080.lawtest:24-30`). The pinned text says when the improvement prospect is expressly stated and the multidisciplinary team proposes it, the commission fixes the period by derogation (`sources/css/R541-4-2022.txt:6`; current 2026 wording `sources/css/R541-4.txt:5`). The test's ordinary regime fact therefore conflicts with its positive statutory trigger facts. The current rules then derive the ordinary due-end and withhold the special period for this impossible combination (`08-durees-revision.law:83-91`, `141-160`, `166-184`).

**Author repair request:** make the ordinary branch source-consistent. Supply an explicit positive case fact showing that at least one statutory trigger is absent in the records, such as the medical certificate not expressly recording a prospect or the team record containing no proposal. Do not turn missing prospect/proposal facts into negatives. Key the ordinary regime assertion to the recorded CDAPH decision or give it adjudicated provenance, rather than treating the legal classification as an unsupported generic case input (`package.law:658-665`; current tests use `origin case_input` at the ordinary assertions). Add separate ordinary cases for each affirmative basis. Preserve the existing missing-regime child as pending.

### R2-02 — useful-pieces completeness is not scoped to a request or its decision record

**Class (в), input/source channel.** The new `pieces_utiles_completes(e)` premise is declared as an empirical fact with only the child as argument and a generic “fait du dossier” label (`package.law:527-530`). `DemandeComplete` consumes it alongside the child-level certificate and declaration facts (`07-procedure-demande.law:74-81`); the new positive scenario supplies it as `origin case_input` (`tests/r541-demande-complete.lawtest:14-17`). R. 541-3 requires all supporting documents useful to assess the claimant's rights (`sources/css/R541-3.txt:3-8`). “Useful” requires a case-specific determination, and the rule speaks about a particular *request*. The present relation neither identifies the dossier/request when a child has more than one filing nor records who established that the additional material is complete. The source names the MDPH as recipient of the request but does not expressly assign it the determination of usefulness, so this review cannot invent that authority.

**Author repair request:** make the premise request/dossier-specific (for example, bind it to the filing date or a stable dossier identifier) and document the provenance of the completeness determination. Treat it as an established, adjudicated dossier fact if that is the input contract; do not claim that R. 541-3 expressly delegates this judgment to the MDPH. If the source leaves the decision-maker unspecified, record that as a boundary. Update the positive scenario with that dossier-level provenance and retain the missing-premise case as NEITHER.

### R2-03 — sealed case 09 overstates a negative from a missing record

**Class (б), reader.** The sealed answer for case 09 says category-6 criteria are false based on “No permanent-constraint record.” R. 541-2 requires permanent family supervision and care constraints for category 6 (`sources/css/R541-2.txt:15`); no record is not evidence the constraints do not exist. This also conflicts with the package's open-world input contract (`package.law:135-156`). The category 4(a) result from total work cessation remains supported.

**Owner-process request:** preserve the sealed bytes pending authorized answer revision; a revised answer should leave category 6 undetermined unless the case gives affirmative evidence that the constraints are absent.

### R2-04 — sealed case 23 calls an inapplicable historical rule a source gap

**Class (б), reader.** For a death in 2021, the pinned then-applicable R. 541-4 text has no section V (`sources/css/R541-4-2019.txt:1-13`) and the contemporaneous R. 541-1 text has no death continuation (`sources/editions/CSS_ED2021_01.txt:35-40`). The sealed `SOURCE_PENDING` answer confuses the later rule's inapplicability with an unpinned source. The package's later extension correctly begins on 2022-01-31 (`10-deces-prolongation.law:45-50`).

**Owner-process request:** preserve the sealed bytes pending authorized answer revision; the 2021 probe should state that no extension is provided by those applicable versions and must not backdate the 2022 clause.

## Re-reviewed F-01–F-03 corrections

- **F-01, R. 541-4 derogation:** the two new regime relations make missing regime input silent, and the scenarios include missing-regime controls. The 2022 wording's “Par dérogation” is correctly treated as displacing the ordinary 1°/2° end for the same award (`sources/css/R541-4-2022.txt:2-7`). The remaining defect is R2-01: the ordinary control case contradicts its affirmative prospect and team facts.
- **F-02, 50–80% historical/source windows:** `BornesDuree5080` now uses only `CSS_R541_4`, takes effect 2026-04-01, and requires the filing date and derogation regime (`08-durees-revision.law:94-110`). The old-cohort rule continues to require a pre-cutoff filing and has no prospect premise (`08-durees-revision.law:113-132`); the old/new pair appears in `tests/r541-derogation-5080.lawtest:37-68`. This correction is source-concordant on static review.
- **F-03, request completeness:** the new completeness relation prevents the old certificate/declaration-only overclaim and its missing-premise child remains NEITHER by declared input (`tests/r541-demande-complete.lawtest:20-35`). However, its child-only scope and `case_input` provenance do not identify the particular request or establish who made the usefulness/completeness determination; R2-02 remains open.

## Full 67-rule inventory

The whole finish-wave inventory was reconciled against the module rule declarations and pinned R. 541-1 through R. 541-10 text. The unchanged modules retain the previous static source/model review; changed rules in 07 and 08 were re-read against the cited articles. No runtime status is inferred.

- `05-seuils-taux.law` — **5 checked** against R. 541-1: `Seuil80Atteint`, `Seuil50Atteint`, `Tranche5080`, `PriseEnChargeReconnue`, `ModaliteVersementAnnuel`.
- `06-categories.law` — **20 checked** against R. 541-2: `CritereCategorie1Depenses`; `CritereCategorie2Reduction`, `CritereCategorie2Tierce`, `CritereCategorie2Depenses`; `CritereCategorie3aReduction`, `CritereCategorie3aTierce`, `CritereCategorie3bReductionDepenses`, `CritereCategorie3bTierceDepenses`, `CritereCategorie3cDepenses`; `CritereCategorie4aCessation`, `CritereCategorie4aTiercePlein`, `CritereCategorie4bReductionDepenses`, `CritereCategorie4bTierceDepenses`, `CritereCategorie4cReductionDepenses`, `CritereCategorie4cTierceDepenses`, `CritereCategorie4dDepenses`; `CritereCategorie5CessationDepenses`, `CritereCategorie5TierceDepenses`; `CritereCategorie6CessationContraintes`, `CritereCategorie6TierceContraintes`.
- `07-procedure-demande.law` — **8 checked with R2-02 open** against R. 541-3, R. 541-9, R. 541-10: `DemandeComplete`, `DevoirJoindrePieces`, `DevoirTransmettreDossier`, `DevoirDeposerDemandePCH`, `ExclusionChargesComplement`, `DevoirReviserDecisionPCH`, `DevoirReexaminerComplementPCH`, `InterdictionOpterAvantEcheance`.
- `08-durees-revision.law` — **18 checked with R2-01 open** against R. 541-4 and R. 541-5: `BornesDuree80`, `BornesDuree5080`, `BornesDuree5080AncienneCohorte`, `FinExclusiveAAH80`, `FinExclusiveConditions80`, `FinExclusiveAAH5080`, `FinExclusiveConditions5080`, `DroitMaintenuChangement`, `LiberteRevisionBeneficiaire`, `LiberteRevisionOrganisme`, `DevoirReexaminerAggravation`, `LiberteControlerEffectivite`, `DevoirSaisirCommission`, `DevoirVerserAvance`, `DevoirStatuerUrgence`, `DateLimiteReexamen`, `DevoirReexaminerMesures`, `ReexamenEnRetard`.
- `09-dates-effet.law` — **13 checked** against R. 541-6, R. 541-7, R. 541-8: `DateRejetImplicite`, `RejetImplicite`, `DateDebutDroit`, `DateFinSuppressionSansAAH`, `DateFinSuppressionAvecAAH`, `PontR5122`, `DateFinComplementPCH`, `DevoirSuspendreComplement`, `DevoirRetablirComplement`, `DateAssimilationHospitalisation`, `AssimilationHospitalisation`, `DefeaterContraintesHospitalisation`, `LiberteMaintienVersement`.
- `10-deces-prolongation.law` — **3 checked** against R. 541-1 al. 5 and R. 541-4 V: `DateFinProlongationDeces`, `MontantProlongationMoisDeces`, `MontantProlongationMoisPrecedent`.

**Total: 67 rules.** The stated boundaries remain: unpinned guide/arrete thresholds and deadlines, external PCH mechanics, and items explicitly identified in `package.law`. Static source review does not establish parser validity, fresh snapshot coverage, lawref execution, audit completeness, or Rust semantics. Deferred run queue remains in the author's `REPAIR-2` journal section; runtime status here is **NOT_RUN**.

## Read-only evidence and changed paths

The previous report `analysis/nochecks-20261008/static-review.md` and its JSON were preserved. The sealed source-only answer and blind-case input files were hash/byte-read only. This re-review adds only:

- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/re-review-02.md`
- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/re-review-02.json`
- appended `2026-10-08 re-review 02` section in `docs/foundations/fr-cnaf/lines/finish-aeeh-review-nochecks.md`

No source, test, package, registry, generated block, snapshot, or answer file was modified by this reviewer.
