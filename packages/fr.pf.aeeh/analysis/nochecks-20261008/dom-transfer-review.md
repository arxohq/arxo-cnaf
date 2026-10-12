# Static review — AEEH DOM transfer (D-73)

Reviewer: independent Luna  
Date: 2026-10-08  
Author receipt: `.scratch/fr-cnaf-finish/nochecks-20261008/dom-aeeh-owner-20261007T225353003803Z.run.json` — EXITED, code 0  
Static disposition: **READY_FOR_RUN** for the declared AEEH scope  
Runtime: **NOT_RUN**

## Review scope and seal integrity

I reviewed the eight new rules in `11-dom-aeeh.law`, the associated public declarations and module imports, the current AEEH package contracts and amount producer, the added `tools/build_sources.py` scope inputs and `source-manifest.json` scope metadata, the four new test files and their family declaration, the pinned L. 755-20/D. 755-11 registry records and XML source bytes, and the recorded independent 26-case DOM reader comparison. The prior 71-rule review remains the accepted baseline in `reader-corrigendum.md` and `re-review-03.md`; this transfer adds eight rules for a current total of **79**. I did not rerun the previous 71-rule review.

Sealed originals remain untouched. AEEH `analysis/finish-blind-read.json` SHA-256 remains `1162684ebc4c5a6013fd83221c11af51b977037877891c7b3da3de617c225e00`. DOM blind answers remain SHA-256 `70cf2604543dfaad2b17a4c3758a27007c9eec220f7b0de201ad3ca0bd321340`, and DOM case input remains `de2e817560c8bb098fc6b62181fb02cb7a7aa5f4e0f99d4d349efe8f238118ad`, matching `.scratch/fr-cnaf-finish/nochecks-20261008/blind-dom/seal.json`. No blind input or answer was edited.

## Source and edition concordance

The exact DOM manifest routes the two bytes differently, and both paths were checked rather than assuming `dump/` for every row:

- **L. 755-20:** D71 record is `LEGIARTI000031324175`, effective 2015-10-16, `xml_from=LEGI_20260723-224400`, `xml_rel=article/LEGI/ARTI/00/00/31/32/41/LEGIARTI000031324175.xml` (`.scratch/fr-cnaf-finish/dom.sources.json:2375-2395`). The file under `.scratch/legi/mirror/LEGITEXT000006073189/increments/LEGI_20260723-224400/...` is 5,804 bytes with SHA-256 `08b7529507496b7b6f67894517eca8dd6e78b3a9b7a39e9301af3914c67ff289`, matching the manifest (`finish-dom-aeeh-owner.md:30-37`). Its operative text says the AEEH is awarded in the collectivities mentioned in L. 751-1, under conditions fixed by decree. The article has no in-window predecessor since it entered force in 2015.
- **D. 755-11:** D71 record is `LEGIARTI000006739184`, effective 2006-01-01, `xml_from=dump`, `xml_rel=article/LEGI/ARTI/00/00/06/73/91/LEGIARTI000006739184.xml` (`.scratch/fr-cnaf-finish/dom.sources.json:94-107`). The file under `.scratch/legi/mirror/LEGITEXT000006073189/dump/...` is 3,887 bytes with SHA-256 `272bf75cfc63dfb3b43461f8dbfa20fbeec080eb75d956b8521b952403b58599`, matching the manifest (`finish-dom-aeeh-owner.md:38-43`). Its operative sentence makes the allowance, supplements, and possible majoration identical to the metropolitan amounts. It is stable throughout the declared window. The pinned D. 755-11 is the only operative article in section 7 (the AEEH section) identified in the registry slice; its scope is amount identity, not a separate award-condition test.

The statutory anchors in the module match those texts. Six L. 755-20 rules cover the six Title V collectivities present over the declared program window. Two D. 755-11 rules express the result as a built DOM amount equal to the package’s computed metropolitan total and a separate check of a presented amount against that built amount. The checked amount producer sums base, supplement, and MPI (`02-droit-montant.law:484-490`), which corresponds to the three components named by D. 755-11. The source texts state no numerical amount, threshold, rounding rule, actor, duty, prohibition, or discretionary power; none is invented in the transfer.

## Rule and premise inventory

All eight new declarations/rules were checked against source meaning and the existing package contract:

- `AttributionDomGuadeloupe`, `AttributionDomGuyane`, `AttributionDomMartinique`, `AttributionDomReunion`, `AttributionDomSaintBarthelemy`, and `AttributionDomSaintMartin` require the existing institutional `aeeh_droit_calcule(e)` plus the empirical residence fact with the matching territory and conclude `aeeh_attribuee_dom(e)` (`11-dom-aeeh.law:61-133`). Their exact source anchors are L. 755-20 current plus the carry-forward fragments for the 2022 and 2026 package editions. An entitled metropolitan or other-territory child has no matching attribution rule; absent residence or right premises remain unknown, not false.
- `MontantDomConstruit` requires the institutional DOM attribution and `aeeh_montant_total(e,total)`, then builds the same value as `montant_aeeh_dom(e,total)` (`11-dom-aeeh.law:135-150`).
- `MontantDomVerifie` requires that built value and a separately presented empirical amount, and concludes verification only when the two values are equal (`11-dom-aeeh.law:152-163`). A mismatch has no verification conclusion; the presented figure is not used to build the entitlement amount.

The attribution tests supply `decision_cdaph_favorable` with adjudicated provenance and `residence_enfant` with case-input provenance. The former is the existing producer input to `aeeh_droit_calcule` (`02-droit-montant.law:117-123`); these are not generic flat attributes that bypass the existing adjudicated right. `package.law:1015-1040` types residence and presented amount as empirical case facts, and DOM status and computed amounts as institutional outputs. The transfer adds no external import/publication request: every added non-source name is declared in this package, and all `use self` references in `11-dom-aeeh.law:43-59` correspond to the generated source names or local public symbols. The six status rules reuse the extant AEEH right producer; no new right or payment duty is duplicated.

The decree clause in L. 755-20 is accounted for by the explicit boundary `B-PFAEEH-DOM-DECRET-CONDITIONS` (`package.law:171-176`): D. 755-11 is the pinned operative AEEH amount provision; no separate decree-set DOM award criterion is identified in the pinned corpus. The existing metropolitan award mechanics remain the source of entitlement conditions. The boundary is explicit, and the transferred rules do not manufacture a second DOM-specific threshold or condition.

## Territory referral and Mayotte date boundary

L. 755-20 does not enumerate the territories itself; it refers to L. 751-1. L. 751-1 is deliberately not added to the AEEH package’s 21-article scope, so the transfer records this as `B-PFAEEH-DOM-L751-1` (`package.law:165-170`). The six `Territoire` values reflect the title header in force over the package’s declared coverage through the 2026-10-06 cutoff. The exact L. 755-20 XML context routed by D71 shows the old Title V heading through 2028-01-01 and a Title V heading that includes Mayotte from 2028-01-01 (`.../increments/LEGI_20260723-224400/.../LEGIARTI000031324175.xml:35-41`). This transfer therefore does **not** attribute AEEH in Mayotte before that date. The Mayotte 2028 cohort lies beyond this package review’s pinned program window; the current six-territory enum does not establish post-2027 Mayotte coverage. Extending evaluation through 2028 requires an updated L. 751-1 source/scope and a dated Mayotte input/rule pair. This is an explicit source/coverage boundary, not a retroactive reading or a category-6-style negative inference.

The source generator has `L755-20` and `D755-11` in `SCOPE` (`tools/build_sources.py:78-82`), the scope metadata lists 21 articles (`sources/source-manifest.json`), and the manifest carries both records. Existing edition-building logic generates carry-forward fragments for each applicable version/edition (`tools/build_sources.py:226-266`). The model names the expected current-package fragments: L. 755-20 base, `_ED2022_01`, `_ED2026_04`; D. 755-11 `_ED2021_01`, `_ED2022_01`, `_ED2026_04` (`11-dom-aeeh.law:63-66, 75-78, 87-90, 99-102, 111-114, 123-126, 140-143, 154-157`). Generated source outputs are explicitly **GENERATED_OUTPUT_PENDING** in the author journal (`finish-dom-aeeh-owner.md:48-59`): `sources/css/L755-20.txt`, `sources/css/D755-11.txt`, edition bytes, `01-sources.law` fragments, `sources/articles.json`, and `sources/fragment-map.json` have not been materialized or checked in this review. Thus this confirms the input IDs, exact D71 XML routing, textual anchors, and expected edition mapping; it does not claim generated fragment hashes or successful source pinning.

## Scenario review

The four new suites are meaningful source-derived cases, all statically read but never run:

- `tests/dom-attribution-collectivites.lawtest:1-61` covers all six positive territories and the METROPOLE/AUTRE silence controls using adjudicated right premises and case-input residence.
- `tests/dom-montant-construit.lawtest:1-26` uses inputs only (BMAF 400.00 explicitly declared as an external case value; no supplement; no MPI), expects the existing metro amount calculation 128.00, and checks the DOM value is built from that result.
- `tests/dom-montant-verifie.lawtest:1-32` tests both equality (128.00) and mismatch (100.00) against the same computed inputs; a presented amount cannot change the built result.
- `tests/dom-edition-2021.lawtest:1-26` provides the base-edition pair at 2021-06-15. The other amount/attribution tests use 2024-03-15 and exercise the 2022 carry-forward edition. The current 2026 carry-forward fragment is statically anchored in the rule and expected from the source generator, but no new 2026-context DOM test exists; generation and execution remain pending, so this review makes no run/fragment-participation claim.

## Independent 26-case DOM reader comparison

The sealed DOM reading has four already-recorded class (б) reader corrections in `docs/foundations/fr-cnaf/analysis/nochecks-20261008/review-dom/static-review.md:250-275`. I confirmed their source rationale; they are reader-answer discrepancies, not defects in the eight AEEH DOM-transfer rules. Original DOM bytes remain sealed:

- **DOM-01:** age 3 does not satisfy “tous âgés de plus de trois ans”; age 4 does. The age condition across the two children is therefore not met (`DOM-01` in `blind-read-cases.json`; R. 755-1 in `.scratch/fr-cnaf-finish/dom.sources.json:3956-4059`).
- **DOM-02:** ages 4 and 5 meet the strict-more-than-three condition, and the four-year-old meets “au moins l’un d’entre eux ait moins de cinq ans”; the sealed answer’s “aucun enfant n’a moins de cinq ans” is wrong (case facts and R. 755-1 citations as above).
- **DOM-06:** the slice’s R. 755-2/3/4 version arrays identify the predecessor editions and their validity windows, so edition identity on 2017-03-31 is established by metadata. The predecessor text itself is absent; substantive predecessor content remains unknown. The sealed answer conflates those two questions (`dom.sources.json:4415-4545, 4545-4668`).
- **DOM-17:** the D. 755-8 NOTA expressly states application to benefits due from September 1995; the answer should report that date. The August 1995 applicable edition/content remains a separate unresolved question (`blind-read.json` DOM-17; D. 755-8 slice `dom.sources.json:1210-1224`).

Those reader corrections are already recorded append-only in the independent DOM review, and are not written into either sealed answer file here. The AEEH 24-answer review’s two source-reader corrections also remain separately recorded in `reader-corrigendum.md`; this transfer changes neither its rules nor its sealed comparison.

## Static gate and limitations

For the currently declared AEEH package scope (2021-01-01 through the pinned registry cutoff 2026-10-06), the eight new rules match the pinned L. 755-20 and D. 755-11 text, the full source premises have typed producers or explicit source/input boundaries, package imports resolve by author declarations, and the four scenarios exercise positive, exclusion, build, check, and base-edition paths. The 2028 Mayotte extension and the four pre-existing DOM reader discrepancies are explicitly recorded without retroactive law or answer-file changes. The prior 71-rule static result remains unchanged. Combined static disposition: **READY_FOR_RUN**.

Runtime status is **NOT_RUN**. No engine, test, audit, source generator, pinning command, snapshot, or gate was invoked. Fresh source generation, fragment-map/edition materialization, package scenarios, static audit, source hash gate, lawref, and Rust semantics are still pending in the author’s deferred queue and require the authorized lock/window. The static disposition is not a claim of those outputs or checks passing.

This review adds only:

- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/dom-transfer-review.md`
- `corpus/laws/fr/pf-aeeh/analysis/nochecks-20261008/dom-transfer-review.json`
- appended `2026-10-08 DOM transfer review` entry to `docs/foundations/fr-cnaf/lines/finish-aeeh-review-nochecks.md`

No normative file, test, source generator, generated source block, registry, blind input, or sealed answer was edited by this reviewer.
