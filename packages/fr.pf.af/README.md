# `fr.pf.af` — family allowances (allocations familiales)

Executable formalization of the AF core: three resource bands with the
tapering top-up (D. 521-1–D. 521-4, L. 521-1), the age supplement in two
editions with the 2026-03-01 change (L. 521-3, R. 521-1, R. 521-4), the
lump sum for the 20-year-old (L. 521-1 para. 2, D. 521-2), designation
and sharing with the one-year lock (L. 521-2, R. 521-2–R. 521-4), the
pre/post-2021 ASE redirection, the DOM extension from the first child
(L. 755-11, L. 755-12, D. 755-5) with the D. 521-2–D. 521-4
applicability extension (D. 755-5-1), and the fund payment duty.

Scope: exactly 15 CSS articles (L521-1, L521-2, L521-3, R521-1, R521-2,
R521-3, R521-4, D521-1, D521-2, D521-3, D521-4, L755-11, L755-12,
D755-5, D755-5-1). Upstream premises (child in care, opener status,
debtor body) are read from `fr.pf.core`, never re-concluded here.

Status of the D. 755-5-1 transfer: AUTHOR_READY_FOR_REVIEW (nochecks
author run, 2026-10-07/08). Source outputs for the new article
(fragments, edition texts, accounting) regenerate on the next
`tools/build_sources.py --write` (GENERATED_OUTPUT_PENDING); no measure
taken, no PASS claimed.

## Measure

`law audit .` (formalization measure, static profile): 66 rules,
dangling premises 5 (all enum variants in bodies, none unsupplied),
one-way premises 1 of 66. Form catalog: 16 detectors, 11 findings, all
`strict-reader-of-foreign-defeasible-head` — the eleven rules that read
the upstream `enfant_ouvre_droit` head, whose producers are defeasible
in `fr.pf.core`. That is the documented package split (REQ-PFAF-02),
not a defect: opener status is established upstream including defeat
resolution, and read here strictly.

## Their case to our answer

Foreign benchmarks are expectations, never sources. Euro totals use
the stated BMAF 400.00; band rates come from the pinned D. 521-1
(32/41/16, 16/20.5/8, 8/10.25/4). Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (Catala 1–11, 14,
ouverture-droit; OpenFisca 2015-09 … 2026-03-fallback-14; classes
(a)/(b)/(c) per case).

Reading guide:

- Catala 2/4/9 and the 2026-03 pairs match exactly under the stated
  assumptions (a).
- Sharing situations the benchmark leaves silent are shaped
  explicitly: R. 521-2 2. disagreement in Test 4 (parent share 96.00),
  joint request in Test 10 and OF-2015-09 (b).
- Four genuine divergences (c): Test 1 (shared-custody supplement paid
  full in the benchmark, halved per R. 521-4 para. 2 here); Test 5
  (their 0.00 vs our no-conclusion); Test 14 (20-year-old opener
  asserted against upstream L. 512-3); OF-2015-09 5/6 coefficient
  (their float vs our NONEXACT_NARROWING refusal, B-PFAF-ARRONDI).
- Tests 7/8 are blocked by a foreign-package defect (below), not by
  this formalization.

## Плафоны D. 521-3 (D-81, 08.10.2026)

Плафон строится (DECISION-0452): `plafond1/2_applicable = база + надбавка × n`
(`03-montant-bande.law`). D. 521-3 III ревалоризует 1 января «les montants des
plafonds et de leur majoration respective» — база и надбавка индексируются и
округляются порознь, DSS печатает их отдельно; один коэффициент к номиналу их
не воспроизводит (2018: 56 286 + 2 × 5 628 = 67 542 против
(55 950 + 2 × 5 595) × 1,006 = 67 542,84). Поэтому:

| Период права | База I / база II / надбавка | Откуда |
|---|---|---|
| 2015-07-01 — 2016-01-01 | 55 950 / 78 300 / 5 595 | сам D. 521-3 I/II (bareme, правила `Plafond1/2Nominal`) |
| с 2016-01-01 | входы `plafond_base_tranche1_publie`, `plafond_base_tranche2_publie`, `majoration_plafond_enfant_publiee` | инструкция DSS на 1 января года права — фрагменты PLAFOND_AF пакета fr.css.revalorisation (2016 = 2017 по DSS_SD2B_2016_396_REVAL) |

Год плафона — год месяца права: таблицы DSS действуют «du 1er janvier N au
31 décembre N» и сравниваются с доходом года N−2. Прежний вход
`facteur_revalorisation` снят, второго пути нет (решение D-81 в
`docs/foundations/fr-cnaf/DECISIONS.md`). Сценарии с прежним коэффициентом F
получили «сумма D. 521-3 × F» тремя входами — тождественно прежнему, ожидания
не менялись (комментарий в начале каждого сценария); `catala-test-04` —
опубликованные суммы 2020. Новые сценарии на опубликованных суммах:
`plafond-nominal-2015`, `plafond-publie-2016-reconduit`,
`plafond-publie-2018-bande-2`, `plafond-publie-2021-bande-2`,
`plafond-publie-2026-bande-3`. Сценарий 2021 показывает: ресурсы дела Catala
Test 8 (69 945 €) при опубликованных суммах 2021 (I = 69 933 €) попадают в
полосу 2, а не 1, как при прежнем «калиброванном» коэффициенте 1,05
(`catala-test-08` сохраняет его как сверку логики); с дополнением при BMAF
414,40 € итог 197,91 € против их 197,90 € — разница в стадии округления
(по строкам DSS 66,30 + 33,15 даёт ровно их число; граница B-PFAF-ARRONDI,
та же, что в деле OpenFisca 2018-01 Cas 6).

Сверка с OpenFisca-France 176.1.2 (`analysis/openfisca-176/REPORT.md`, hook
`tools/openfisca_hook.py`): BMAF и плафоны — из закреплённых фрагментов
fr.css.revalorisation; итог на D-81 — РАВНО 29, одно (б) (их код округляет полную
ставку до модуляции полосы 3) и две (а)-границы B-PFAF-ARRONDI (стадия
округления по строкам DSS; доля R. 521-3 5/6). Стадию округления сняло
прочтение D-83 (раздел ниже).

## Округление по строкам DSS (D-83, 08.10.2026)

Прочтение §152 `ArrondiLignesDss` (`08-lecture-arrondi-lignes.law`, вне групп
выбора, образец — `fr.apl::ArrondiCentimeHalfUp`): суммы AF округляются до
сантима HALF_UP по строкам таблицы DSS, итог — сумма округлённых строк.
Основание: статьи декретов (D. 521-1, D. 521-2, R. 521-4, D. 755-5) об
округлении молчат; ежегодная инструкция DSS — административный текст, не
декрет — округляет публикуемые суммы до ближайшего сантима («Ces montants sont
arrondis au centième d'euro le plus proche», DSS/2B/2026/46) и печатает
округлённые строки. Как округлять ровно полсантима (HALF_UP — наш выбор) и
округлять ли итог или строки, инструкция не говорит, поэтому это прочтение
(`status disputed`), а не норма пакета. Без выбора поведение прежнее: точные произведения, один
round итога, неточный douzième — отказ INEXACT_DIVISION.

| Место | Строка под прочтением | Базовое правило (молчит при выборе) |
|---|---|---|
| база по полосе | строка «N enfants»: round((t2 + t3 × (N − 2)) × BMAF) — доля семьи, не сумма рангов (DSS 2017: «4 enfants 114 % 464,94», 130,51 + 2 × 167,21 = 464,93) | `MontantMensuel` |
| надбавка за возраст | строка I.2 round(t × BMAF); половинная (R. 521-4) — строка половинной ставки round(t × BMAF / 2) | `MontantMensuel`, `MajorationMontantPlein/Moitié` |
| forfait | строка I.3 round(t × BMAF) | `ForfaitMontant` |
| ДОМ, один ребёнок | строки I.4 (5,88 %, 3,69 %, 5,67 %) | `DomMontantUnique`, `DomMajoOnze/Seize` |
| complément dégressif D. 521-1 II, D. 521-2 II | douzième над округлёнными строками, до сантима (D-82) | `ComplementPlafond1/2`, `ForfaitComplementP1/P2` |

Не затронуто: доля родителя R. 521-3 (5/6) — D-82 её не покрывает, D-83 объём
не расширяет (дело OpenFisca of176-af-54 остаётся (а)). Сценарии с выбранным
прочтением — `tests/lignes-dss-*` (ожидания — строки закреплённых таблиц
`fr.css.revalorisation/sources/dss-*.txt`); прежние сценарии без прочтения не
менялись. Hook OpenFisca выбирает прочтение в context: сверка формул — РАВНО 31,
(б) 1, (а) 1 (доля 5/6); сквозные pf-af — РАВНО 12, (б) 6, (а) 0.

## Boundaries

- B-PFAF-BMAF-EURO / B-PFAF-BMAF-DOM: euro totals rest on stated
  BMAF/retained-base assumptions (2020-05 example BMAF reconstructs to
  ~414.42: Catala 3 = 5.88% x 414.42; Catala 4 = 0.24 x 414.42).
- B-PFAF-PLAFOND-REVALO: closed by D-81 (08.10.2026) — see «Плафоны
  D. 521-3» below; the factor input is gone.
- B-PFAF-COMPTAGE: two fund-established counts — `nb_enfants_charge`
  (openers: base, right, ceilings) and `nb_enfants_charge_forfait`
  (forfait minimum, includes the reaching 20-year-old).
- B-PFAF-ARRONDI: no cent-rounding rule in the decree articles (the yearly
  DSS instruction rounds published amounts to the nearest cent; tie rule
  and row-vs-total unstated); inexact Decimal
  narrowings refuse instead of rounding silently. Lifted for the scale
  amounts and the douzième by the reading `ArrondiLignesDss` (D-83, above)
  when the case selects it; the 5/6 sharing coefficient (R. 521-3) stays
  a refusal.
- B-PFAF-SEUIL-MOYENNE: the L. 521-3 para. 2 three-or-more test counts
  opening children (benchmark rule text, full-custody parity); the
  R. 521-4 para. 1 reference to the R. 521-3 average convention is
  recorded as strain (Q-PFAF-3).
- B-PFAF-MAYOTTE: Mayotte and AUTRE conclude nothing.
- B-PFAF-D755-5-1: D. 521-2–D. 521-4 apply in the L. 751-1 departments as
  recorded statuses; the 03/05 computations already run without a
  territory gate, so no amounts change. Territory inherits the package
  reading of L. 755-11/12 (four DOM; Mayotte/AUTRE excluded);
  Saint-Barthélemy and Saint-Martin have no Territoire member
  (pre-existing enum boundary).
- B-PFAF-MOIS-DROIT: calendar month mechanics assumed; deadline
  policies arrive as case inputs.
- B-PFAF-ASE-MIXTE / B-PFAF-ASE-BENEFICIAIRE: mixed ASE per-child
  shares indeterminate from marginal rates; service-bound parts carry
  no inter-parent duty.
- B-PFAF-JUMEAUX: twins (equal birthdates) are never "older", both
  stay eligible under the under-three rule.
- B-PFAF-DECRET-L5212: L. 521-2 para. 5 (a)–(d) renvoi ends the charge
  upstream.
- Foreign blocker REQ-PFAF-03: `fr.pf.core` compiles its
  `asf_ouvre_droit` defeater without a defeasible mate in their
  CSS_ED2021_01, so every evaluation at legal_time in [2021-01-01,
  2021-05-01) in the suite world refuses
  (NON_EXECUTABLE_STRATUM_BARRIER). Request string in the status
  record; our Tests 7/8 are proven correct in the two-package world.
- Pre-existing oracle gaps (lawref, untouched by this lane): DOM
  amounts and power/position evaluations diverge from lawc
  (dom-*, Catala 3/14, OF-2020-04-dom, partage-ase-juge);
  engine results stand.
