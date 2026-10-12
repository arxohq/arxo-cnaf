# `fr.pf.core` — French family benefits, common socle

Common socle of French family benefits (prestations familiales): child in
care, allocataire, monthly calculation bases (BMAF), N-2 resources,
limitation and recovery, the duty to pay and sanctions, plus the principles,
powers and time limits of the benefit series whose computation lives in the
benefit packages. Wave 1 of the plan
`docs/plans/rules-as-code/RULES-AS-CODE-FR-CNAF.ru.md` (§7); sample —
`corpus/laws/fr/apl/`.

Owner rule: formalization in English only. Labels are `fr official` (quotation
from the pinned bytes) plus `en unofficial`; comments, boundaries, reports and
blind cases are in English. No Russian anywhere in this package.

## What is pinned and as of when

Bytes — LEGI open data (DILA), CSS snapshot 2026-10-06 (registry
`.scratch/reg-css.json`). Pinned: **71 articles** L511-1–L584-1 except series
L521-* (package `fr.pf.af`) and L531-* (package `fr.pf.paje`), plus R512-1,
R512-2, R532-3, L551-1, L552-1, L553-1, L553-2; **16 editions**
(CSS_ED2021_01 … CSS_ED2026_06); **20 declared prev-text gaps**
(`prev-text-unpinned`: pre-coverage versions not in the dump, recorded in
`sources/articles.json`, not silently bridged).

FINISH payment-core (2026-10-08, no-run authoring, verification
deferred — `docs/foundations/fr-cnaf/lines/finish-payment-core.md`):
generator input extends the scope to **100 articles** (+27:
L552-2/4/6, L554-2/3, R514-1, R552-1..4, R553-1/2/3(+1..7),
D552-6/7, D553-1..5; +2 D73 DOM L755-4 (3 rules in 08,
metropole/DOM split PC-R03-09) and D755-2 (1 rule in
fr.prestations.versement 06, DOM applicability)) with
four new PREV pins (L532-2, L552-4,
D553-1, R552-3) under frozen edition states (PW-01). Generated
output pending: `01-sources.law`, `sources/css/*`,
`sources/editions/*`, `sources/articles.json` regenerate on the
deferred run; existing fragments/editions/publications stay
byte-identical by construction. R03-01..09 (2026-10-08) add the
D552-6 authority mapping (3 rules in 10), the L553-4 benefit-specific
rights (8 rules in 07), and the L553-5/R553-3-5 regulatory linkage
(07+11); R553-3-2 stays SOURCE_ONLY (pure renvoi). R04-01..05
(2026-10-08) fix the DOM bearer spelling (08), add the D552-6
delegate branch (10), the R553-3-1 fallback/household/date/evidence
conditions (11), and the benefit-specific L755-4 prime exclusion
(08); D553-4 ordering lives in fr.prestations.versement 06.

Layout: one pinned file per article (`sources/css/<ARTICLE>.txt`, 71 files)
plus one publication per edition (`sources/editions/<ED>.txt`, 16 files,
concatenating all in-force fragments). Every in-force fragment is repeated per
later edition (`<FRAG>_<ED>`, 973 `pub fragment` total) so `@source` anchors
fire at any `legal_time` past debut — the E-0095 silence pattern (rules
unheard past their debut edition) is closed by construction. Generator:
`tools/build_sources.py` (`--check`: `articles: 71, editions: 16, declared
prev-text gaps: 20`, `SOURCES OK`). The 30 `MIRROR: ... xml sha256 mismatch`
lines are informational (mirror XML drift vs registry, prior-line
provenance); the gate exits 0.

Bareme: `tools/build_bareme.py` (`--check`: `BAREME OK: 95 rows,
boundary removed, all formulas verified`). 95 rows transcribed from the
pinned DSS/2B/2026/46 (amounts at 2026-04-01) and DSS/2B/2025/177
(ceilings for 2026): every %BMAF product and every ceiling table is
arithmetically self-checked by the builder (boundary B-PFCORE-BAREME
REMOVED 2026-10-06). The package itself derives threshold conditions
and shares, not amounts; the BMAF chain is executable in
fr.css.revalorisation.

## Module map

- `01-sources.law` — sources, editions, fragments (generated; do not hand-edit)
- `02-enfant-charge.law` — R. 512-2, L. 512-3, R. 512-1: child in care
  (55 % SMIC × 169 h ceiling via `fr.travail.smic`)
- `03-allocataire.law` — L. 513-1, L. 512-1, L. 512-4/5/6: allocataire
- `04-bmaf.law` — L. 551-1: BMAF classification (amounts — B-PFCORE-BAREME)
- `05-ressources-n2.law` — R. 532-3: N-2 year, resource facts, concubinage
- `06-prescription.law` — L. 553-1: 2/5-year limitation, interruption
- `07-recouvrement.law` — L. 553-2/2-1/3/4/5: indu, 10 %, unseizability
- `08-devoir-paiement.law` — fund duty L. 511-1 + L. 583-1, L. 552-2/6,
  sanctions L. 554-2/3 (restored FINISH payment-core)
- `09a-prestations.law` — series L. 522/523/532/533/541/543/544/545, L. 542-9,
  L. 552-*: entitlement principles, powers, time limits
- `09b-creances.law` — L. 581-584: maintenance claims, intermediation,
  advances, data transmission
- `10-service-dates.law` — R. 514-1, R. 552-1..4, L. 552-4/7, D. 552-7,
  R. 553-2: service, due/cessation dates (FINISH payment-core, unrun)
- `11-train-de-vie.law` — R. 553-3(+1..7): lifestyle scale, procedure
  (FINISH payment-core, unrun)
- `12-cumul-5322.law` — L. 532-2 I–V, 2026 + 2018 cohorts, D72
  (II prev + 2026 delta since re-review-02; FINISH payment-core, unrun)

Explicit package (SPEC §23.2, DECISION-0386): cross-file symbols travel in
`use self::{...}` blocks. `law fix imports` refuses in this tree
(`LPK-E0201: no law.toml` for both `fr/pf-core` and `fr.pf.core` forms —
open question Q6); the blocks are maintained by hand from the E1116 map.

## Measure (§33.1) and checks

`law engine check`: `check OK: corpus/laws/fr/pf-core` (one LDC-E1372
warning on the explicit `@id("urn:fr:source:css")`, same class as the APL
warnings — DECISION-0352 §4).

`law test`: `total: 70 checked, 70 passed, 0 failed, 0 not run` — 42 hand
scenarios in 8 families (enfant-charge 6, allocataire 6, bmaf-socle 2,
ressources-n2 3, prescription 4, recouvrement 6, devoir-paiement 6,
prestations-renvois 9) plus 25 generated catalog witnesses
(`tests/catalog/`, 28 verdicts, registered in `law.toml`).

`check_lawtest_suites.py --only "fr.pf.core#<family>"`: OK for all 8
families, `--python-only` first then the byte differential — both engines
agree on every scenario.

`check_source_pinning.py --only fr-pf-core`: see the status record for the
verbatim result (per-article §33.1 statuses).

Blind guard: `pytest analysis/test_blind_read_cases.py` — 3 passed.

`law catalog build`: 54 cards, 9 internal, 4 boundaries, 28 scenarios
(`analysis/questions.json` with `"language": "en"`, `QUESTIONS.md`,
`check_package_questions --only` agrees with CLIR/scenarios/package-info).
Stored card stubs are English 1:1 translations of the builder templates
("Is it established that …", "Which normative positions arose …"); the
shared stub prefixes do not recognize the current stub shape (0 of 54
counted), so no shared ratchet number moves. A catalog rebuild restores
Russian stubs — re-translate after any rebuild until `build_catalog.py`
is language-aware.

Depth (§33.1): `check_formalization_depth --only fr-pf-core` gives
`EXECUTABLE 52, SOURCE_ONLY 19, UNEXPLAINED 0` — registered
(`--register fr-pf-core`). Declaration:
`sources/pf-core/articles.json` (editions form, `fr_code_lettered_article`,
primary text CSS_ED2026_06 first); the 19 SOURCE_ONLY reasons live in each
entry's `declared` (one `pending_addressee: fr.pf.af` for L541-3).

Label ratchet: dictionary 151/6 (the 6 are the `function` bodies — the
grammar has no label slot for functions, E0201/E1108 verified 2026-10-06),
norms 99/0, unanchored 0 — row written by hand with `$comment`
(`--register` would drop the comment).

## Boundaries

Full list — `package.law` (`B-PFCORE-*`); engine-behavior entries:

- B-PFCORE-BAREME — REMOVED 2026-10-06: DSS/2B/2026/46 + DSS/2B/2025/177
  pinned in fr.css.revalorisation, 95 rows in `bareme.json` (self-checked).
- B-PFCORE-SMIC-PRE2026 — SMIC via `fr.travail.smic` from 01.01.2026.
- B-PFCORE-CGI — net categorical income details live in the sibling
  `fr.tax.income_for_pf` package; amounts arrive here as provenanced facts.
- B-PFCORE-DATES-MOIS — NARROWED 2026-10-08: R. 552-2/3 execute via
  stated month anchors + `SERVICE_MOIS` (module 10); backward steps stay
  caller-stated; titres de séjour still out; D. 553-1 scale lives in
  `fr.prestations.versement` (module 06).
- B-PFCORE-MOIS-PRECEDENT — no backward month step (FORWARD-only
  policies): CMG preceding month and ASF 3-month floor are stated anchors.
- B-PFCORE-MOIS-FIN-LECTURE — R. 552-3 IV month-end roll reading (SPEC
  §86), flagged for reviewer confirmation.
- B-PFCORE-DELEGUE-MAX — L. 552-6/L. 755-4 highest-payer selection is
  caller-side (`organisme_montant_le_plus_eleve`); single-benefit
  serving organ is stated; prime forfaitaire excluded (L. 755-4 al. 2).
- B-PFCORE-TDV-VEHICULE-ITEMISE — R. 553-3-1 5 per-vehicle test is
  caller-side; the rule re-tests the stated qualifying sum.
- B-PFCORE-L5527-FENETRE — L. 552-7 applicability window question
  (finding F-01, journaled; existing 09a rule preserved).
- B-PFCORE-L5322-II-PREV — RESOLVED 2026-10-08: predecessor II
  authored (2018 list); two 2026-only items have dedicated 2026-gated
  rules. B-PFCORE-L5322-II-MAP — the caller maps the new items to the
  dedicated relations only, never to shared `percoit_indemnite_concurrente`.
- B-PFCORE-ANNEE2-REQUETE — pf-core-10: no genuine package-side fix
  (query-side D-11 lowering); boundary recorded without type tricks.
- B-PFCORE-DOM-LIVRE7 — Book VII DOM specials out of scope; D73
  2026-10-08: D. 755-2 stays SOURCE_ONLY (pure renvoi); L. 755-4
  al. 1/3 share the L. 552-6 heads, al. 2 gates both cost rules —
  `@source` extension awaits fragment generation (journaled).
- B-PFCORE-DUES-KEY-PERSONNE — due/cessation date heads key on the
  person only: single-benefit cases (recorded 2026-10-08).
- B-PFCORE-N2-INTEGER-FN — engine gap: Integer literals in function bodies
  are not evaluated (silent absence, check green); the N-2 chain reads
  NEITHER, the downstream link reads TRUE. Ratchet for constant folding.
- B-PFCORE-NEGATION-ABSENCE — negatives read NEITHER (negation as absence);
  no FALSE_ONLY verdict exists corpus-wide for defeated conclusions.
- B-PFCORE-JUGEMENT-CHARGE — the care channel is judicial
  (`external judgment`; REQUIRES_JUDGMENT without the Organisme assessment).
- B-PFCORE-POLICY-CONTEXT — calendar steps need `deadline_policy NAME` in
  the evaluation context (§86/E-0029); units are singular
  (`calendar_year`, `calendar_month`).

## Scenarios and deontics

41 hand scenarios plus 1 downstream-link proof (`tests/`, registered in
`law.toml`). Truth idiom (`evaluate truth(...)`) for statuses, positions
idiom (`evaluate positions()`) for duties/liberties/prohibitions, judgment
idiom (`origin adjudicated` + `REQUIRES_JUDGMENT` + `judgment_request`) for
the care channel. Calendar scenarios bind the package policy in the test
context (`deadline_policy ENFANT_VINGT_ANS | PRESCRIPTION_ANNEES |
RECOUVREMENT_DELAI`) — the APL `R822_13_MOIS_SUIVANT` idiom.

FINISH payment-core adds 61 authored-but-unrun scenarios (no engine
run in this session; expectations are author assertions, not
observations): `#devoir-paiement` +2, `#prestations-renvois` +6,
new `#service-dates` 38, new `#train-de-vie` 15, all registered in
`law.toml`. Static-return repair 2026-10-08 (still unrun) adds 30
more (`#devoir-paiement` +4, `#prestations-renvois` +11,
`#service-dates` +9, `#train-de-vie` +6; 91 FINISH scenarios
total). Re-review-02 repair 2026-10-08 (still unrun) adds 25 more
(`#devoir-paiement` +5, `#prestations-renvois` +6,
`#train-de-vie` +14; 116 FINISH scenarios total). Re-review-03
repair 2026-10-08 (still unrun) adds 37 more (`#recouvrement` +19,
`#service-dates` +10, `#train-de-vie` +3, `#devoir-paiement` +5;
153 total; 35 migrated). Re-review-04 repair 2026-10-08 (still
unrun) adds 14 more (`#devoir-paiement` +2, `#service-dates` +2,
`#train-de-vie` +10; 167 total; 4 migrated + 2 comment-only).
New calendar scenarios bind `SERVICE_MOIS` / `TRAIN_VIE_DELAI` (D-47).

Deontic map — `analysis/duty-bearer-inventory.json` (17
duties/liberties/prohibitions, 8 defeaters, all anchored).

Cross-check: no Catala/OpenFisca socle cases exist, so expectations travel
through converters only; independent verification is blind reading —
`analysis/blind-read-cases.json` (24 cases, facts plus date, no answers).
Status: BLIND_PENDING (no second model in this environment).

## Open questions

Q6 `law fix imports` correct invocation (LPK-E0201 both forms); Q7
coordinator approval of the `fr-smic` LOWERED_ACTS row added as a dependency
enabler; Q8 mirror `xml sha256 mismatch` ×30 confirmation (informational —
check exits 0). D-11/NEITHER/decimal-truth theme untouched by directive.
