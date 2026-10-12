# AJPA source-deontic map (FINISH-W3)

Per-article map over pinned bytes only (`01-sources.law` fragments, editions
`CSS_ED2019_12`…`CSS_ED2025_12`). For each article: bearer, modality,
condition, executable form, window. Outside the pinned bytes — boundary,
not conjecture. French quotations are verbatim from the fragments.

## Corrigendum 2026-10-08 (finding A-1, canonical а)

The first version of this map said “no powers” and assigned the whole
L. 168-13 withholding option to decree/external boundaries. That was a
source-reading error: the pinned text grants the paying body two
express statutory discretions — «l'organisme payeur peut procéder à la
récupération de l'indu par retenues» and «la récupération peut être
opérée … par retenue» (`sources/css/L168-13.txt`). Both are now
modelled as powers (P1 `RecouvrerParRetenues`, P2
`RecouvrerParRetenueL5532`) with their exact statutory conditions and
effects; only the execution detail (decree deadline figure, L. 553-2
deduction rules, L. 133-4-1 procedure) stays a boundary. The rows
below and the “no powers” sentence are corrected accordingly; nothing
else in the map changed.

## Corrigendum 2026-10-08 (finding A-2, canonical а)

The A-1 corrigendum recorded the P2 single-payment non-option
(«et si l'assuré n'opte pas pour le remboursement en un seul
versement») as subsumed by the instalment non-option fact. That was an
unmodelled interpretation, not a source-supported entailment: the
pinned text states the two option conditions separately — the
deadline-bound «en un ou plusieurs versements» reserve of the first
block and the independent «en un seul versement» condition of the P2
sentence — and no source passage proves either entails the other. P2
now takes both as separately recorded established facts
(`indu_sans_option_remboursement`,
`indu_sans_option_versement_unique`), each bound in `when` and
`valid_when`; two distinguishing tests pin the independence in both
directions. P1 and all other A-1 repairs stand unchanged.

## Corrigendum 2026-10-08 (finding A-3, canonical а)

The A-1/A-2 P1 rule validated the debt branch and the reserves but
carried no target-benefit class, while the pinned text authorizes
withholding only «sur les échéances à venir dues au titre des
prestations familiales mentionnées à l'article L. 511-1, de la prime
d'activité mentionnée à l'article L. 841-1 du présent code, du revenu
de solidarité active mentionné à l'article L. 262-1 du code de
l'action sociale et des familles ou des aides personnelles au logement
mentionnées à l'article L. 821-1 du code de la construction et de
l'habitation». P1 now takes the target as a closed enum
(`CibleRetenuePrestations`: PRESTATIONS_FAMILIALES, PRIME_ACTIVITE,
RSA, AIDES_LOGEMENT) carried by the recorded-target premise
(`retenue_cible_prestations`), the exercise
(`retenue_prestations_exercee`) and the effect
(`ajpa_retenue_prestations`), all joined on one variable bound in
`when` and `valid_when`. No fifth target is assertable; the
eligible/missing/mismatched-target tests pin the distinction in the
executable model, not in prose alone. All P1/P2 premises, exceptions,
windows, actors, effects and target classes were re-read against the
pinned wording for this wave: P2's L. 553-2 target stays an external
cross-reference boundary (that article is outside the nine-article
scope), everything else on both powers was already represented and
stands unchanged.

## Corrigendum 2026-10-08 (finding A-4/B-1, canonical а/б)

The D2/D3 duty bodies carried a literal square-bracket
placeholder instead of binding the headed fund actor; both now
declare the lowercase `bearer` binding to `o` (the rule-head
variable joined by `organisme_debiteur_pf(o, p)`). D1 already
declared the same binding and is unchanged. The two prose rows
below (L. 168-8 right condition, L. 168-13 D2) used the same
literal placeholder and now use lowercase typed prose. P1/P2
rules and all scenarios are untouched. Note: tool readouts
render a lowercase bearer-plus-actor pair as an uppercase
notice, so the binding is verified by byte matching
(case-sensitive `bearer` matches, uppercase-`B` and
square-bracket forms absent), not by eyeballing readouts.

## Positions

| Article | Map entry | Form | Window |
|---|---|---|---|
| L. 168-8 | Fund pays («Une allocation journalière du proche aidant est versée») to carers with leave + stable residence | duty `VerserAjpaDue` (`DevoirVerserAjpa`), bearer `organisme_debiteur_pf` (fr.pf.core), beneficiary carer, performance `ajpa_verse` | [@2021-01-01, ∞) |
| L. 168-8 | Right condition: carer leave (L. 3142-16 travail) + lawful stay / stable residence (L. 512-1, L. 512-2 paras. 1-2); no bearer (classification rule, not a duty) | classification `ajpa_droit_ouvert` (`DroitAjpaOuvert`, literal head) | [@2021-01-01, ∞) |
| L. 168-9 | Monthly total = retained daily rate × month days; single-carer majoration to 2023-07; split/part-time modulation; no bearer | values `ajpa_montant_mois` (`MontantMensuelNormal/Module/Majore`, literal heads) + retained-rate case inputs | normal/module [@2021-01-01, ∞); majoré [@2021-01-01, @2023-07-21) |
| L. 168-9 | Career count within sixty-six («…pour l'ensemble de sa carrière est égal à soixante-six») in the 2019/2022/2023-07 wordings; no bearer | classification `ajpa_dans_limite_carriere` (`PlafondCarriere66`, literal head) + bareme `NombreMaxCarriere66` | [@2021-01-01, @2025-01-01) |
| L. 168-9 | 2025: month days within retained maximum; running count within retained duration ceiling; renewal for another aided person; no bearer | classifications `mensuel_dans_limite`, `ajpa_dans_duree_max`, `renouvellement_accorde` (literal heads) + decree case inputs | [@2025-01-01, ∞) |
| L. 168-10 | Allowance not due when the carer is employed by the aided person (CASF L. 232-7 / L. 245-12 para. 2) | refusal `ajpa_cumul_refuse` (`ExclusionSalarieAidant`, literal head) | [@2021-01-01, ∞) |
| L. 168-10 | Ten concurrent benefits refuse cumulation (2019 list; 2025 list within the NOTA birth scope; nine items common to both wordings) | refusal `ajpa_cumul_refuse` (`NonCumul2019/2025/2025Commun`, literal heads) | 2019 [@2021-01-01, @2025-12-31); 2025 [@2025-12-31, ∞) |
| L. 168-10 | «Toutefois» part-time sick exception: cumulation in the course of the right | permission record `activite_partielle_cumulee` (`CumulPartielMaladie`; no negation, input contract separates worlds) | [@2021-01-01, ∞) |
| L. 168-11 | Allowance «est servie et contrôlée par les organismes débiteurs des prestations familiales pour le compte de la» CNSA | feeds the D1 bearer (`organisme_debiteur_pf`); no standalone rule | [@2021-01-01, ∞) |
| L. 168-12 | Payment/recovery actions prescribe within the L. 553-1 delays (external) | not modelled | B-PFAJPA-PRESCRIPTION |
| L. 168-13 | «Tout paiement indu … est récupéré sur les allocations à venir ou par remboursement intégral» | duty `RecouvrerInduAjpa` (`DevoirRecouvrerIndu`), bearer `o` (paying body), performance `ajpa_indu_recupere` | [@2021-01-01, ∞) |
| L. 168-13 | «A défaut, et sous réserve que l'assuré ne conteste pas le caractère indu et n'opte pas pour le remboursement en un ou plusieurs versements …, l'organisme payeur peut procéder à la récupération de l'indu par retenues sur les échéances à venir» dues au titre des prestations familiales (L. 511-1), de la prime d'activité (L. 841-1), du RSA (L. 262-1 CASF) ou des aides au logement (L. 821-1 CCH) | power `RecouvrerParRetenues` (`PouvoirRecouvrerParRetenues`), holder the paying body, over the debtor; validity: recorded undue + «A défaut» branch + the two recorded reserves + the recorded target class (`retenue_cible_prestations`, closed enum `CibleRetenuePrestations` — corrigendum A-3); exercise the body's withholding act on that target; effect `ajpa_retenue_prestations` on that target | [@2021-01-01, ∞) |
| L. 168-13 | «Lorsque l'indu notifié ne peut être récupéré sur les prestations mentionnées au premier alinéa …, la récupération peut être opérée, sous les réserves indiquées au même premier alinéa, et si l'assuré n'opte pas pour le remboursement en un seul versement, par retenue sur les prestations mentionnées à l'avant-dernier alinéa de l'article L. 553-2» | power `RecouvrerParRetenueL5532` (`PouvoirRecouvrerParRetenueL5532`), holder the paying body, over the debtor; validity: recorded undue + recorded non-recoverability + block-1 reserves + the separately recorded single-payment non-option (`indu_sans_option_versement_unique`; the two option facts are independent premises, corrigendum A-2); exercise the body's withholding act; effect `ajpa_retenue_l5532` | [@2021-01-01, ∞) |
| L. 168-13 | Execution detail only: decree deadline figure (≤ 12 months), L. 553-2 al. 3 / avant-dernier-alinéa deduction rules and benefit conditions, L. 133-4-1 recovery procedure | not modelled: precise boundary on the detail, not on the powers | B-PFAJPA-D168 |
| L. 168-14 | «Le bénéficiaire … est informé, par tout moyen, des modalités de réclamation et de recours» | duty `InformerRecoursAjpa` (`DevoirInformerRecours`), performance `ajpa_recours_informe` | [@2021-01-01, ∞) |
| L. 168-14 | Prior recourse before litigation (L. 142-4 / L. 142-1 procedure) | referenced, not modelled | procedure reference |
| L. 168-15 | Control/fraud provisions apply (external articles) | not modelled | B-PFAJPA-FRAUDE |
| L. 168-16 | Application decree delegation | not modelled | B-PFAJPA-D168 |

No recipient duties («doit», «est tenu»), no sanctions, no
liberties, no immunities in the nine pinned articles. The three duties
(D1 payment, D2 recovery, D3 recourse information) each carry a
`positions` scenario pair in family `fr.css.ajpa#devoirs`; the two
L. 168-13 powers (P1, P2) each carry a `positions` scenario and
truth scenarios for the effected / waiting / invalid-exercise paths,
P1 additionally for the missing- and mismatched-target paths.

## Evaluative elements (three channels, DECISION-0194)

- Fact established by a finding → empirical + `adjudicated`:
  `residence_stable_france` (L. 512-1 / L. 512-2 conditions),
  `indu_ajpa` («paiement indu … constaté», L. 168-13) and the five
  power-branch facts (`indu_non_recupere_allocations`,
  `indu_non_conteste`, `indu_sans_option_remboursement`,
  `indu_sans_option_versement_unique`,
  `indu_notifie_non_recuperable` — the body's recorded file state,
  L. 168-13). All tests assert them with origin `adjudicated`.
- Case-recorded inputs → empirical + `case_input`: carer leave
  (L. 3142-16 grant is external, B-PFAJPA-L3142), day counters, retained
  decree figures, non-cumulation motifs, NOTA birth scope, employment
  by the aided person, the P1 recorded target
  (`retenue_cible_prestations`, one target per debt per world), and
  the two withholding exercises
  (`retenue_prestations_exercee`, `retenue_l5532_exercee`).
- No §47.3 authority-judgment relations and no §152 disputed
  interpretations in this package.

## Builds before checks (DECISION-0452)

Every computed result is built from case inputs by one formula: the
career status from the recorded counter against 66, monthly totals
from the retained rate times month days, ceiling statuses from
recorded counts against retained maxima, duties from the open right
plus the computed total, withholding effects from the recorded branch
facts plus the recorded target plus the body's exercise. No
check-only computation, no presented value is only verified.

## Career and source boundaries (remaining)

- A-4 (D2/D3 duty bearers) and B-1 (prose actor records) —
  CLOSED by the 2026-10-08 corrigendum 4: both duty bodies bind
  the headed fund actor in lowercase duty syntax; D1 already
  did; map and journal prose use lowercase typed names.
- A-3 (P1 withholding target) — CLOSED by the 2026-10-08
  corrigendum 3: the four statutory target groups are a closed enum
  joining the recorded-target premise, the exercise and the effect;
  eligible/missing/mismatched-target tests pin the executable
  distinction. A fifth, unlisted target class is unassertable by
  construction.
- A-1 (withholding powers) — CLOSED by the 2026-10-08 corrigendum:
  P1/P2 modelled with statutory conditions and effects; only the
  execution detail (decree deadline figure, L. 553-2 rules,
  L. 133-4-1 procedure) stays B-PFAJPA-D168.
- A-2 (P2 single-payment condition) — CLOSED by the 2026-10-08
  corrigendum 2: the «en un seul versement» non-option is its own
  recorded premise alongside the instalment reserve; no entailment
  asserted either way. The A-1 «premier alinéa» block reading and
  the P2 paying-body holder stand (journal request 5, narrowed).
- B-AJPA-CARRIERE-2021-2023 — CLOSED by FINISH-W3: the cap now runs
  [@2021-01-01, @2025-01-01), one fragment per wording
  (`CSS_L168_9_PRE2022_ED2021_01`, `CSS_L168_9_PRE2023`,
  `CSS_L168_9_PRE2025`) and one bareme row per wording.
- Pre-2021: the cap sentence is pinned in `CSS_ED2019_12` /
  `CSS_ED2020_12`, but the right cannot open there (the 2019 L. 168-8
  extended channel and the 2019 L. 168-11 service text are unpinned):
  B-PFAJPA-AVANT2021 stays; test `ajpa-carriere-66-2020-silence`
  pins the silence.
- Post-2025: the 2025 wording removes the career sentence; the decree
  duration ceiling replaces it. Test `ajpa-carriere-66-2025-absent`
  pins the closed window.
- Stillborn L. 168-9 LEGIARTI000045061968 (MODIFIE_MORT_NE, debut
  2024-01-01 after fin 2023-07-21, never in force): unpinned by
  construction, no rule reads it.
- D168/R168 decree figures (daily SMIC euro amount, monthly max days,
  duration ceiling, renewal terms, recovery instalments): case inputs
  with provenance (B-PFAJPA-D168, DSS_PENDING); inventory PENDING_WAVE.
- L. 3142-16/19/20 carer-leave mechanics: external case facts
  (B-PFAJPA-L3142); the L. 3142-19 renewal bound is not checked.
- No cent-rounding rule in scope: exact Decimal products
  (B-PFAJPA-ARRONDI). No OpenFisca AJPA model upstream (B-PFAJPA-OF).
