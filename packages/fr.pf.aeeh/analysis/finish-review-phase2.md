# Independent phase 2 review — AEEH finish wave

Reviewer: Luna (independent review of Muse repair)
Date: 2026-10-07
Package: `fr.pf.aeeh`
Private snapshot: `.scratch/fr-cnaf-finish/aeeh-private-20261007T070446919784Z/clir/fr-pf-aeeh.lawir.json`
Snapshot state: `.scratch/fr-cnaf-finish/aeeh-private-20261007T070446919784Z/state.json`
Sealed source-only answers: `finish-blind-read.json`, SHA-256
`1162684ebc4c5a6013fd83221c11af51b977037877891c7b3da3de617c225e00` (24 answers).

## Review result

**Not accepted.** The source report is clean within its stated Python-only scope, but the package lawref run reports ten failures and the audit identifies one source-only article plus five measures that remain `not_checked`. A material source/model conflict also remains in R. 541-4 I: the text's express derogation is not represented in the due-end rules or tested with the conflicting facts.

No sealed file was changed, and no blind answer was fitted to the package. The source-only answer file is treated as immutable evidence. This review does not claim Rust semantic validation: `NOT_RUN_RUST (SEMANTIC_RELEASE_UNAVAILABLE)`.

## Check receipts and scope

The private snapshot was built by the root helper after the D46 record and the check-2 claim. The helper completed with exit 0; its receipt records only `fr.pf.aeeh` as freshly compiled and `fr.pf.core` / `fr.travail.smic` as pinned inputs. No shared CLIR or lock file was written by that build.

The package lawref command was run under `nice -n 10`, with `LAW_WORK_PROFILE_STATE` pointing to the private state and `--python-only --workers 1`. The captured run used system Python 3.10.11, below the repository's configured Python 3.12 minimum, so treat it as a diagnostic result rather than a conforming acceptance run. It returned **1** after 24.721 seconds: 11 suites, 44 tests, 10 failures. The exact captured stdout/stderr and return code are retained in `.scratch/fr-cnaf-finish/aeeh-phase2-review-checks-20261007.json`. The run was not repeated with another interpreter.

The static audit and Python source report used `.venv-work-profile/bin/python` 3.13.5, `nice -n 10`, and the same private snapshot. Their captured stdout/stderr and actual return codes are in `.scratch/fr-cnaf-finish/aeeh-phase2-review-checks-validpy-20261007.json`.

| Measure | Return code | Result |
|---|---:|---|
| `check_lawtest_suites.py --package corpus/laws/fr/pf-aeeh --python-only --workers 1` | 1 | Diagnostic only (Python 3.10.11); ten failures listed below. |
| `audit.py fr-pf-aeeh --fast --skip-dead-symbols --law /nonexistent` | 1 | Five sections measured, five `not_checked`; not a clean/full audit. |
| `python_source_report.py corpus/laws/fr/pf-aeeh <private fr-pf-aeeh.lawir.json>` | 0 | `PARTIAL_PYTHON_SOURCE_REPORT`; zero reported problems, not a full pinning-gate PASS. |

The Python source report found 7/7 publication hashes matching and all 101 fragment texts both hash-matching and present in their pinned publication bytes. It found 19 articles in scope, no missing article and no unresolved anchors. This supports source-byte integrity for this report only; Rust source-pinning checks were not run.

The audit measured 11 of 57 grammar declaration kinds, 88 rules (86 strict, one defeasible, one defeater), 14 duties and five liberties. Its five absent measures are: within-article coverage; element-to-implementation comparison (CLIR fragments contain no model-language text); dead-symbol slice (`--skip-dead-symbols`); reachability (`--fast`); and LawQL form (`--law /nonexistent`). The source-only `L541-3` unit is the single `SOURCE_ONLY` article. Its text only makes L. 521-2 applicable to AEEH; the package declares designation/sharing to neighbor `fr.pf.af` under `B-PFAEEH-PARTAGE`. That is a plausible ownership boundary, not an unrecorded omission, subject to the neighbor's own acceptance. The six category enum names in orphan-reference output and the `DateFinProlongationDeces` / `PontR5122` one-way premises match the package's stated enum, terminal-result and cross-package bridge contracts. The doctor section also reports that `build_sources.py --check` is not registered in the common gate; no gate file was changed in this review.

## Lawref failures

These are the ten failures reported against the private snapshot. They prevent acceptance; because the run used Python 3.10.11, the statuses below are diagnostic until a conforming post-repair Python 3.12+ run.

| Suite / scenario | Observed failure | Review classification |
|---|---|---|
| `procedure-demande / r541-devoirs-demande` | Expected `COMPUTED`, got `NON_EXECUTABLE` | Scenario for sealed case 10. R. 541-3 supports the document duty and MDPH transmission after favourable decision; the model evaluation is non-executable, so not source disagreement. |
| `procedure-demande / r541-option-avant-echeance` | Expected `OpterComplementAvantEcheance ACTIVE`, position absent | Typed scenario asserts the qualifying lump-sum PCH subtype; R. 541-10 al. 3 supports the prohibition before expiry. The implementation does not emit it. Sealed case 14 omits subtype, so its own `INPUT_PENDING` remains appropriate. |
| `durees-revision / r541-bornes-duree` | Expected bounds `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 15 and the bound portion of case 16. The test context omits a `deadline_policy`; the package declares `AEEH_DUREES`. This is a scenario-context defect, not evidence against the source reading. |
| `durees-revision / r541-cohorte-2026` | Expected bounds `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 17 cohort controls. The test context omits its policy binding; add the declared policy in the scenario context. |
| `durees-revision / r541-revision-reexamen` | Expected `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 18 deadline result. The test context omits its policy binding; R. 541-5 says the opening must be re-examined within at most two years. |
| `dates-effet / r541-rejet-implicite` | Expected `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 20. The test context omits its policy binding; “more than four months” supports the sealed May 11 conclusion. |
| `dates-effet / r541-dates-debut-fin` | Expected `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 21. The test context omits its policy binding; the next-month start and notification-month cessation are source-supported. |
| `dates-effet / r541-hospitalisation` | Expected `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 22. The test context omits its policy binding; R. 541-8 supports the third-following-month assimilation date. |
| `deces-prolongation / r541-deces-date-fin` | Expected `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 24. The test context omits its policy binding; R. 541-4 V supports the end date. |
| `deces-prolongation / r541-deces-2026` | Expected date result `TRUE_ONLY` / `COMPUTED`; got `NEITHER` / `MISSING_POLICY` | Relevant to case 24's date and amount split. The test context omits its policy binding; the amount's separate input scope is discussed below. |

All eight `MISSING_POLICY` cases define `deadline policy` declarations in their package modules but do not name a policy in the `.lawtest` context. The language's context contract supports an explicit `deadline_policy` reference (SPEC §§89, 129), and the evaluator correctly reports missing policy. The author should add the appropriate package policy to each affected scenario context; this does not require a core change.

The two remaining failures were inspected at source and rule level. `DevoirJoindrePieces` is anchored to R. 541-3 and its asserted case facts meet the three body premises; R. 541-3 al. 2 supports the document duty. `InterdictionOpterAvantEcheance` is anchored to R. 541-10 and requires the exact listed PCH subtypes, a lump-sum award, an early date, and an attempted option; those facts are asserted by its direct test. R. 541-10 al. 3 supports that prohibition. The captured summary does not include a whynot/diagnostic trace for either failure, so the exact runtime cause remains undiagnosed; both are package-level emission/evaluation failures, not a contrary source reading. The author should resolve them in the package and preserve the input contract.

## Sealed answers checked against pinned text and model contract

The 24 source-only answers were checked against the pinned R. 541-1 through R. 541-10 text, applicable edition notes, package contracts, and matching package scenarios. Most answers are aligned with the source and declared boundaries. The following classifications must stay visible:

| Case | Independent source classification | Package/model review |
|---|---|---|
| 01–04 | Correct threshold distinctions at 80%, 50%, and the half-open 50–80% band. | Rules and scenarios cover the boundary values. |
| 05 | `SOURCE_PENDING` is correct: R. 541-2 delegates the expense threshold to an unpinned joint order. | Correctly retained as a boundary/input, not fabricated. |
| 06–08 | Correct: 20% reduction and eight paid hours meet category 2 alternatives; case 08 supplies both category-6 cumulative conditions. | The repair's category gates represent these alternatives. |
| 09 | The sealed answer says category 6 is false and category 4(a) true. The latter is supported by total cessation. The former overstates what follows from “No permanent-constraint record”: absence of a record does not prove the statutory condition false under the package's open-world input contract. | The repaired scenario's `NEITHER` for category 6 and `TRUE_ONLY` for category 4(a) is the supported result for an absent constraint fact. This is a reader/model classification difference, not grounds to force a negative fact. |
| 10–11 | Correct: the two required declaration branches plus medical certificate establish completeness in case 10; a missing branch leaves case 11 incomplete. | Case 10 is blocked by the `NON_EXECUTABLE` failure above; case 11 was not among the reported failures. |
| 12–14 | Correct conditional treatment. Case 12 supports MDPH transmission after a favourable decision, but does not establish a third-element PCH filing duty. Cases 13–14 omit the PCH subtype/evolution inputs needed to activate R. 541-10. | The added subtype contract is consistent with the text. Case 14's direct test with the qualifying typed subtype fails to emit the prohibition. |
| 15–17 | The 2024 80% award has 3–5-year bounds; the 2024 60% award has the pre-2026 2–5-year period and no 2026 due-end; the 2026 60% due-end requires the 1 April 2026 filing cohort. | Case 15 and cohort tests have `MISSING_POLICY` failures. There is no blind case combining a special-prospect trigger with an AAH/conditions due-end; see the material conflict below. |
| 18–19 | Correct within pinned text: re-examination was due within two years; ineffective activity/care triggers referral, an advance for the ascertained situation, and urgent review, while the delegated deadline and amount remain unpinned/unknown. | The case 18 test is mechanically blocked. No lawref failure was reported for the case 19 duties. |
| 20–22 | Correct: rejection is only after more than four months; the start/suppression dates and third-following-month hospitalization date follow the pinned text. | All three date families fail with `MISSING_POLICY`, so their execution remains unverified. |
| 23 | The sealed answer labels the 2021 death extension `SOURCE_PENDING`. The applicable pinned pre-2022 R. 541-4 contains no V death-extension clause, and the applicable R. 541-1 text contains no death sentence. This is not a missing-source case: the package's effective date from 2022 is supported; the 2021 statutory continuation is absent in the complete pinned versions. The answer should be classified as no R. 541-4 V extension for that date, not a source gap. | The pre-2022 scenario is an appropriate edition guard. Do not apply 2022 law retroactively. |
| 24 | R. 541-4 V supports continuation through 30 June 2024. R. 541-1 al. 5's amount comparison applies to the annual single payment for L. 541-1 al. 4 periods, because “ce versement” refers back to that payment. The facts give amounts but do not establish those qualifying periods; this is an input gap, not a missing source. | The new `periodes_conges_internat` gate matches the pinned wording. Keep the amount inconclusive absent that fact; do not label it `SOURCE_PENDING`. The date calculation is blocked by `MISSING_POLICY`. |

## Material model/source conflict: R. 541-4 I derogation

The pinned 2022 and 2026 R. 541-4 texts both introduce the special prospect rule with **“Par dérogation aux dispositions des deuxième et troisième alinéas”**. In the 2026 text, those preceding provisions are the ordinary AAH-successor and cessation-of-conditions due-ends for the 50%+ band. The derogation then requires an award period of three to five years at 80%+, or two to five years at 50–80%, when an improvement prospect is expressly recorded and the multidisciplinary team proposes it. This is affirmative source wording that the special period derogates from the ordinary due-end paragraphs.

The current model has `BornesDuree80` / `BornesDuree5080` for that trigger while leaving `FinExclusiveAAH80` / `FinExclusiveConditions80` and the 2026-cohort 50–80% due-end rules independently enabled. Thus, on a case with the same applicable period, prospect, team proposal, and AAH opening (or cessation of conditions), it can conclude both the special duration and the ordinary due-end. The package does not contain a genuine conflict scenario joining those facts. The already sealed cases do not resolve this: case 15 has no AAH/conditions-end fact, case 16 is a pre-2026 50–80% cohort, and case 17 has no prospect/team proposal.

Classify this as a material model/source conflict requiring an author decision grounded in these pinned words and a conflict-pair scenario. Do not treat the blind answers as the legal authority, and do not accept coexistence merely because the current separate tests pass. The same derogation wording exists in the 2022 version for its then-applicable 80% provision; review that edition's interaction too.

## Acceptance status

Not accepted. Required before reconsideration: author resolution of the R. 541-4 derogation conflict with a genuine same-period test; repair of the two failed procedure cases and the date-policy failures; then a fresh package-only lawref run under Python >=3.12 and `--workers 1`. Keep Rust semantic status `NOT_RUN_RUST`. The audit remains partial (`5 not_checked`), and the source report remains `PARTIAL_PYTHON_SOURCE_REPORT`; neither is a full-gate PASS.
