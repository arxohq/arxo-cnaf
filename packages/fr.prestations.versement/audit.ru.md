# Audit — fr.prestations.versement (fast pass, 06.10.2026)

Method: `audit-formalization`, `audit.py fr-prestations-versement --fast`
+ `law audit --clir` + direct lawc runs. Numbers only from tools.
Criterion: no unexpressed source content, no silent pipeline losses —
not the share of used productions.

## Verdict: 5 of 57 — and should not be more

`inventory.py`: 5 of 57 top-level declaration kinds used
(`const_decl` 1, `relation_decl` 88, `function_decl` 8 (tool run;
now 7 — CH2 removed `indemnite_dix_pourcent`), `rule_decl` 86,
`test_decl` 61 as `.lawtest` input). Re-count after the 06.10
audit-fix wave (grep, 18:15): relations 91, rules 90 (02: 32, 03: 8,
04: 9 strict + 23 defeasible, 05: 18 duties), tests 65. Re-audit
CH2 (grep): rules 88 (04: 9 strict + 21 defeasible, dead witnesses
removed), tests 69 (+2 floor-total nets, +2 CMG réforme duties).
The 52 zeroes get verdicts below;
verdict 4 («Работа») appears nowhere.

## Measures

| Section | Tool | State | Result |
|---|---|---|---|
| 1 depth §33.1 | boundaries.py | not_checked | no CLIR — snapshot pending (journal request 3) |
| 2 unit volume | uncovered.py | not_checked | no own LEGI units; package cites neighbour fragments only |
| 2b source elements | inventory_pair.py | not_checked | no CLIR to compare against |
| 3 inventory | inventory.py | completed | 5 of 57; verdicts below |
| 4 premises | law audit | not_checked | no CLIR snapshot |
| 4b one-way | law audit | not_checked | no CLIR snapshot |
| 5 dead symbols | dead_symbols.py | not_checked | no CLIR snapshot |
| 6 executability | check_rule_executability | not_checked | needs gate runs (no snapshot) |
| 7 form | law audit --clir | failed→stale | fail cause (foreign stray `fr.pf.cmg/law.lock`+`deps/`, journal request 4) gone from tree; section un-re-run; last green partial: 16 detectors, 0 findings on 02/03/05 |
| 8 registries | — | completed | LOWERED_ACTS row missing — journal request 3 filed |

Direct (non-gate) evidence: `law engine check` green on all 4 modules;
lawc `lower` + `engine test`: 70/70 PASS (all 4 modules + 6 dossier
checkpoints); journal request 1 closed by be74ee4ba6 (all 7 pubs).

## Axis 1 — text → expressed

Own source bytes: none — the package owns no LEGI pins by design
(D-V1): every `@source` cites a qualified neighbour fragment
(`fr.apl::ORD9650_*`, `fr.pf.*::CSS_*`, `fr.casf.rsa::CASF_L262_46*`,
`fr.pf.core::CSS_L553_*`). Byte coverage of neighbour pins is the
neighbours' measure, not this package's. No `despite` needed: no own
articles exist to leave unexpressed. Silences are findings with
reasons, not gaps: AEEH (art. 14 II 8° exception), AJPA (outside
L. 511-1), PF rounding (no sentence), housing limitation (old
L. 351-11 abrogated), PA (package exists, not wired).

## Axis 3 — recorded → alive

- Orphan/one-way premises, dead symbols: measure not taken (no CLIR).
  Mitigation: 70 scenarios name every product relation (each CRDS
  track, both floors, all 4 recovery families, all 18 duties);
  `law fix imports` reports canonical blocks.
- «Проверка без построения» (DECISION-0452): clean. Every computed
  value is BUILT from case inputs: CRDS nets (brut × 0.5 %),
  floor statuses (total vs 15 EUR), debts/rates/deductions/nets in
  04, duty positions in 05. First scenario of each capability gives
  only inputs. Fund-stated inputs (scale rates, carried debts,
  household totals) are justified as foreign artefacts / stated
  assumptions in the 03/04 contracts and README boundaries (same
  pattern as B-PFCF-COMPTAGE).

## Verdicts on the 52 unused kinds (formulas 1–4)

1. **Source/pinning** (`source/edition/publication/fragment/alignment/
   revision/entrenchment/reference_decl`) — **1**: the package owns no
   source bytes; pinning declarations would pin nothing.
2. **Types** (`entity/record/enum/map/variant_type/alias_type/unit/
   facts/facts_use_decl`) — **1**: no new entities (neighbour
   Personne/Enfant/Menage/Beneficiaire/Organisme reused); no closed
   lists in the payment-stage texts (numeric/conditional content
   only); no units beyond Money/Decimal/Date.
3. **Normative extras** (`role/event/action/external/evidence/
   evidence_policy/support/assertion/closure_decl`) — **1**: no
   roles, events, actions or external snapshots in the texts;
   household totals arrive fund-stated by design (03 contract),
   no closed-collection reasoning required.
4. **`constraint_decl`** — **1**: no coherence invariant in the
   texts; total-vs-heads consistency is a stated assumption (AF/CF
   pattern), enforcement would need §93.1 support the texts do not
   give. **`definition_decl`** — **1**: no defined terms beyond
   relations.
5. **`presumption/fiction/classification_decl`** — **1**: fraud must
   be established, never presumed (04 establishment inputs); no
   legal fictions; tracks are relations, not classifications.
6. **`priority/priority_policy_decl`** — **1**: applicable rules are
   disjoint by head/condition (base/fraud/reiteration by
   establishment inputs); bars are `not_known` guards and per-debt
   rules (D-V5), not priorities — no defeater kind is used in 04.
7. **`interpretation/interpretation_group_decl`** — **1**: no §152
   disputed reading adopted; L. 553-2 al. 3 applies as written
   (S3 report); the S4 structural reading is documented in
   WITNESS.md, not a canon choice.
8. **`procedure/decision/case/snapshot/context_decl`** — **1**: fund
   internal process not formalized; cases/snapshots/contexts live
   in `examples/famille-dans-le-temps/`, not the canon.
9. **`deadline_policy/temporal_resolution_policy/stage_decl`** —
   **1**: limites are case inputs (ARS/ASF mirror), no computed
   deadlines; no temporal ambiguity; one stage by design.
10. **`term/expansion/expand/query/counterfactual_decl`** — **1**:
    7 functions suffice (1 in 02 + 6 in 04; CH2 removed the dead
    10 % helper), no term macros; queries live as
    `examples/` JSON (question catalog: measure missing, phase-5
    row open); no counterfactuals in the texts.
11. **`property/factors/precedent_decl`** — **1**: amounts are
    arithmetic, not factor balancing; no precedents cited.

No verdict 4. The package needs its five constructions; the rest
was considered and refused with reasons above.
