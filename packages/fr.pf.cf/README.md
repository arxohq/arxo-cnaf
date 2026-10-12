# `fr.pf.cf` — complement familial (CF)

Executable formalization of the complement familial: award conditions
with the two age bands (L. 522-1, R. 522-1; strict under-20, then
[20,21) with pay within the ceiling), the two-earner test (R. 522-2
para. 3), the stacked resource ceilings (L. 522-2, R. 522-2, R. 522-4;
+25 % for each of the first two children, +30 % for each child from
the third, tiered by rank per D-36),
the monthly amounts (D. 522-1, D. 522-2, L. 522-3; base and increased
tracks mutually exclusive per D-39(a)) with the 2018-04-01
majore rate row, the standalone differential top-up (R. 522-3), and
the fund payment duties.

Scope: exactly 17 CSS articles — metropolitan CF (L522-1, L522-2, L522-3,
R522-1, R522-2, R522-3, R522-4, D522-1, D522-2) plus the DOM CF transfer
(L755-16, L755-16-1, R755-1, R755-2, R755-3, R755-4, D755-6, D755-6-1).
Upstream premises (child in care, opener status, debtor body) are read
from `fr.pf.core`, never re-concluded here; the L. 522-1 award frame is a
local fund-established stand-in (`cadre_cf_remplie`, MIGRATION-REQ-PFCF-02)
because core keeps `cf_condition_remplie` package-private, and
`date_naissance` is local for the same reason (MIGRATION-REQ-PFCF-01).
The DOM award (06-dom.law) works from one counted child with strict ages
(over three, one under five), reuses the metropolitan R. 522-2/R. 522-4
machinery by liaison for three or more children, and computes DOM amounts
on the stated L. 755-3 base (base track) and BMAF (increased track).
That R. 755-1 track is department-only; the Title V broad track states the
six-collectivity statutory scope and the available base/increased amounts
for qualifying households (no award, ceiling, differential or duty outside
departments).

## Measure

`law audit .` (formalization measure, static profile): 16 rules,
dangling premises 0, one-way premises 0 of 16. Form catalog: 16
detectors, 2 findings, both `strict-reader-of-foreign-defeasible-head`
— the two qualifying-child rules that read the upstream
`enfant_ouvre_droit` head, whose producers are defeasible in
`fr.pf.core`. That is the documented package split (REQ-PFCF-02), not
a defect: opener status is established upstream including defeat
resolution, and read here strictly.

## Their case to our answer

Foreign benchmarks are expectations, never sources. Euro totals use
stated illustrative inputs (BMAF 320.00 base-track / 100.00
majore-track; decree nominal `plafond_base_cf` 20000 EUR); track rates
come from the pinned D. 522-1/D. 522-2 (41.65 %; majore 58.33 % until
2018-04-01, 62.48 % after). Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (OpenFisca
cf.yaml, cf_2018 Cas 1–6 + Non-Passant 1–9, cf_2018_04 Cas 1–2;
classes (a)/(b)/(c) per case).

Reading guide:

- Track selection matches on all paying cases under the stated
  assumptions (b): base where their totals are 169.03/170.71, majore
  where theirs are 236.71/256.09 — including Cas 4–6, which confirm
  the adopted L. 522-3 reading (no biactif needed for the track).
- The 2018-01/2018-04 edition pair proves the majore row switch
  (58.33 → 62.48).
- Nine genuine divergences (c), all shape: their printed 0.00 vs our
  no-conclusion (NEITHER) where no track opens.
- Biactif situations: the PASS of the reference year comes from the
  package `fr.css.pass` (pinned arrêtés 2015–2026, one per year, no gap;
  D-84) or from the case (`pass_annuel`); the N-2
  resource base is taken fund-stated (b).

## Boundaries

- B-PFCF-BMAF: euro totals rest on the stated BMAF (illustrative in
  the hand-written scenarios; the OpenFisca transfer takes it from the
  pinned DSS fragments).
- B-PFCF-PLAFOND-NOMINAL: closed by D-83 (08.10.2026): the ceilings are
  built from the published DSS amounts (base and increments, each track),
  see «Плафоны CF и PASS (D-83)» below. The amounts still arrive as case
  inputs with provenance (pinned slices in `sources/dss-plafonds/`).
- B-PFCF-PASS: closed for the reference years 2015–2026 (one arrêté per
  year, pinned by `fr.css.pass` without a gap: 26 Nov 2014 … 22 Dec 2025;
  D-84, B-PASS-2017 of that package lifted 08.10.2026). B-PFCF-PASS-2017 is
  lifted with it. A reference year outside the series (before 2015, after
  2026) is not pinned and never invented: a case with `revenu_pro_min_couple`
  for such a year MUST bring `pass_annuel`, otherwise `CoupleBiactifEstClos`
  (a closed-world negation over `foyer_du_cas`) concludes «not two-earner»
  although the threshold was never established. D-84 took the PASS series out
  of pf-cf into its own package (`corpus/laws/fr/pass`, `fr.css.pass`),
  pf-cf imports it.
- B-PFCF-COMPTAGE: the fund establishes `nb_enfants_cf`; the input
  contract requires consistency with the per-child
  `cf_enfant_qualifie` facts (AF pattern).
- B-PFCF-ARRONDI: no cent-rounding rule in scope for the differential
  (the division refuses silently-inexact inputs instead of rounding);
  the ceilings no longer round anything (D-83: each published amount is
  already a whole euro).
- B-PFCF-CRDS: brut before CRDS; the 0.5 % levy is outside scope
  (their `X / (1 - 0.005)` outputs are not reproduced).
- B-PFCF-N2: N-2 resource assessment (R. 532-1/R. 532-3..8) is
  upstream; resources arrive fund-stated.
- B-PFCF-DOM: lifted for CF by the 06-dom.law transfer (all 8 DOM CF
  articles modeled); remaining DOM boundaries below.
- B-PFCF-DOM-TERRITOIRE (D-76): Mayotte (wave 7) and AUTRE conclude
  nothing anywhere; Saint-Barthélemy/Saint-Martin conclude nothing on the
  R. 755-1 department track (award, differential, duties). The six enum
  values spell the Title V header in force over the window; the L. 751-1
  list itself is unowned (pending the L751-1 owner decision) and the
  department class arrives as the provenance-bearing departement_l751_1
  case fact — a department value without it (unknown class) opens no
  department conclusion either.
- B-PFCF-DOM-TITRE-V: the broad track qualifies a Title V collectivity
  household through the retained fund-established frame
  (cadre_cf_titre_v_remplie) where non-department regulatory detail is
  genuinely not pinned; it builds available base/increased amounts from the
  generic D. 755-6/6-1 rates without asserting R. 755-1 ages, R. 755-2/4
  ceilings, the R. 755-3 differential, base/majore exclusivity or any duty.
  Available is not due.
- B-PFCF-DOM-LIAISON: the L. 755-3 monthly base arrives stated
  (`base_dom_retenue`); the liaison to `fr.pf.dom::base_calcul_dom` and to
  the DOM general opener (L. 755-9/10/2-1) lands after that package
  registers. The DOM frame (`cadre_cf_dom_remplie`) and the young-child
  presence (`presence_jeune_dom`) are fund-established meanwhile.
- B-PFCF-DOM-ARRONDI (retained policy, SOURCE_PENDING): DOM base/increased
  tracks round HALF_UP to the centime as adopted interpretation — no pinned
  text names rounding or tie-breaking (D. 755-6 «… 41,65 % …», D. 755-6-1
  «… 62,48 % …» give rates only; §194 fragments carry no rounding rule).
  Metropolitan precedent is not legal proof; no universal source-prescribed
  tie policy is claimed. Tests use exact non-tie amounts only, preserving
  non-tieability. The DOM differential is exact.
- B-PFCF-DOM-IPC: L. 755-16 al. 3 / L. 755-16-1 CPI indexation is a
  despite (nominals arrive stated; the revalorisation chain is upstream).
- Adopted DOM readings (recorded in `lines/finish-dom-cf-owner.md`): R755-1
  pins the vague L755-16 age limbs (the L531-1 al. 1 renvoi adds no further
  executable content) and stays department-only; base/increased exclusivity
  mirrors D-39(a) on the department track only; the DOM differential keeps
  the R755-1 frame premises while staying standalone from the open base
  right; the Title V frame qualifies non-department collectivity households
  for available amounts without inventing R755-1 content there.
- B-PFCF-MOIS-DROIT: calendar month mechanics assumed; the
  `AGE_ATTEINT` deadline policy arrives as case input.
- Q-PFCF-1 (closed by D-83, 08.10.2026): the two-earner / lone-parent
  increment of the increased amount is the one the DSS prints for that
  track (`majoration_biactivite_majore`: 2018 — 4 218 against the base
  track's 8 437), not the full base-track value added to a halved ceiling.
  The blind pair PFCF-B-12 (`analysis/blind-read-cases.json`) stays as a
  record of the question, its reading is now source-prescribed.
- Adopted reading (blind-pending): the R. 522-3 differential is a
  standalone track — an overrun household has no open base right, so
  `CfDifferentiel` requires neither `cf_droit_ouvert` nor the
  resource-gated monthly amount, computing instead from the
  theoretical base amount (probes PFCF-B-16/B-20).
- DSS_PENDING: euro BMAF and the N-2 assessment await the DSS pricelist;
  BLIND_PENDING: the standalone-differential reading awaits the second
  model.

## Плафоны CF и PASS (D-83, 08.10.2026)

**Плафон строится из опубликованных сумм** (образец D-81, fr.pf.af). R. 522-2 al. 4 и R. 522-4
al. 3 поручают декрету «le montant du plafond de ressources et celui de la majoration» и
ревалоризацию 1 января; инструкции DSS печатают базу и надбавки отдельно, каждую со своим
округлением до евро (2018: база 20 989, 25 % = 5 247, 30 % = 6 297, двойная активность 8 437;
montant majoré — своя база 10 496, 2 624, 3 149 и своя надбавка 4 218). Модель «номинал ×
проценты» их не воспроизводила (5 247,25 вместо 5 247; половина базы 10 494,5 вместо 10 496;
половина надбавки 4 218,5 вместо 4 218), а повышенный плафон (`MajoreAvecBiactif`,
`MajoreAvecIsole`) добавлял к половинной базе полную надбавку плафона CF (8 437 вместо 4 218).
Теперь по каждой дорожке плафон = база + надбавка за ребёнка × число детей (25 % на первых двух,
30 % с третьего) + надбавка за двойную активность или изоляцию:

| Дорожка | Входы-факты (case_input с provenance) | Вывод |
|---|---|---|
| Плафон CF (R. 522-2) | `plafond_base_cf`, `majoration_enfant_cf`, `majoration_troisieme_cf`, `majoration_biactivite` | `plafond_cf_applicable` |
| Montant majoré (R. 522-4) | `plafond_base_majore`, `majoration_enfant_majore`, `majoration_troisieme_majore`, `majoration_biactivite_majore` | `plafond_majore_applicable` |

Те же факты строят плафоны DOM для одного и двух детей (R. 755-2, R. 755-4 отсылают к R. 522-2 и
R. 522-4), второго пути нет. Параметры-проценты `MajorationPlafondEnfant`/`MajorationPlafondTroisieme`
сняты: при опубликованных надбавках они давали бы второе значение того же плафона.
Источник сумм — `sources/dss-plafonds/` (`tools/pin_plafonds_dss.py`): дословные срезы разделов
«Plafonds … complément familial» и «… montant majoré» инструкций DSS, закреплённых пакетом
`fr.css.revalorisation` (там фрагмента montant majoré нет); 2016 = 2017 по абзацу о
reconduction. Сумма срезов сверяется с напечатанной таблицей инструкции (в `manifest.json`
`anomalies`: одна опечатка DSS/SD2B/2016/396 — «4 604» вместо 34 604 для одного ребёнка). Сценарии
`tests/plafond-dss-2018…2026.lawtest` (`tools/build_plafonds_tests.py`) сверяют построенный плафон
с напечатанной строкой таблицы (3 ребёнка и 4 ребёнка для parent isolé, обе дорожки).
Прежние сценарии мигрированы тождественно (входы 25 % = 5 000 и 30 % = 6 000 от базы 20 000;
ожидания не менялись, причина — комментарий каждого сценария).

**PASS.** Порог R. 522-2 al. 3 — 13,6 % «du plafond annuel de la sécurité sociale en vigueur au
1er janvier de la même année» (года отсчёта ресурсов). С D-84 (08.10.2026) ряд PASS ведёт
отдельный пакет `fr.css.pass` (`corpus/laws/fr/pass`, образец — `fr.travail.smic`): закреплены
arrêtés на все годы 2015–2026 подряд (2015–2016 — из дампа LEGI, 2017–2025 — из глобального
дампа JORF, 2026 — из суточного архива; граница B-PASS-2017 снята), годовое значение строится
как 12 × valeur mensuelle (`pass_annuel_arrete`). pf-cf импортирует пакет; мост — правило
`PassReferenceArrete` в `07-pass.law` (год отсчёта — факт дела `annee_reference_ressources`,
PASS года берёт `fr.css.pass::pass_annuel_arrete`). Число, предъявленное делом (`pass_annuel`),
вытесняет число arrêté. Для года отсчёта вне ряда 2015–2026 arrêté нет — дело предъявляет
`pass_annuel` (граница B-PFCF-PASS выше); собственных источников PASS в pf-cf больше нет
(`sources/pass/`, `tools/pin_pass.py`, `tools/build_pass_serie.py` удалены).

Сценарии порога — `tests/pass-<год отсчёта>-seuil.lawtest` на 2017–2025 годы (порождает
`tools/build_pass_tests.py`, `--check` сверяет с байтами `fr.css.pass`): для каждого года две
проверки — наименьшая сумма в сантимах, достигающая 13,6 % × PASS года («au moins égal»), даёт
`couple_biactif`, сумма на сантим меньше — нет; PASS и порог берутся из текста arrêté
(valeur mensuelle × 12), а не вводятся руками. Годы 2015, 2016 и 2026 покрыты написанными вручную
`pass-2015-seuil-egal`, `pass-2016-biactif`, `pass-2016-sous-seuil`, `pass-2026-seuil-egal`.
Дата дела — июнь года права (год отсчёта + 2, R. 532-1).
