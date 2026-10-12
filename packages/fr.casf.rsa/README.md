# `fr.casf.rsa` — RSA right, duties, sanctions, recovery

Executable formalization of the RSA core: composition scale and
majoré (R.262-1, L.262-9, R.262-2), monthly entitlement (L.262-2–6,
L.262-20, R.262-39), duties and the 15-hour contract (L.262-27–31,
L.262-34, C. trav. L.5411-6, decree 2025-478 art. 12),
suspension/suppression/radiation (L.262-37–39, R.262-68–69), and
recovery with prescription (L.262-45–47, R.262-88–94).

FINISH wave (group `rsa`, 25 residual CASF articles, authored
without checks): young-worker hours (D.262-25-1–25-4), claim filing
and instruction (D.262-26–30), department-body conventions
(D.262-61–64), insertion duties and orientation (D.262-65, 65-2,
65-2-1, 73), control and the D.553 recovery bridge (D.262-77,
94-2), statistics (D.262-95–100; D.262-99 is a source boundary).

Scope: L.262-2–6, L.262-9, L.262-20, L.262-27–31, L.262-34,
L.262-37–39, L.262-45–47; R.262-1, R.262-2, R.262-5, R.262-39,
R.262-68–68-7, R.262-69–69-8, R.262-88–90, R.262-92, R.262-92-1,
R.262-93, R.262-94, R.262-94-1; D.262-25-1–25-4, D.262-26–30,
D.262-61–65, D.262-65-2, D.262-65-2-1, D.262-73, D.262-77,
D.262-94-2, D.262-95–100; C. trav. L.5411-6; decree 2025-478
art. 12 (art. 13 not pinned); article 1 of the six MF revaluation decrees
2020-490, 2021-530, 2022-699, 2023-340, 2024-396 and 2025-293; article 9 of law
2022-1158 (coefficient 1.04 from 1 July 2022). The quarterly
amount DUE arrives from `fr.minima.ressources` (same lane) and is consumed AS
the due (D-26, D-44 — no second subtraction). The single-person MF base is
BUILT from the pinned decree and, for 2022-07..2023-03, from the pinned article 9
(see "Flat-rate amount built, not supplied" and "Readings"); a case-supplied base
stays the override outside the pinned series (DSS_PENDING). L.542-/R.542- and the L.542-/R.542- DOM lane are wave 7.

Module map: `package.law` (surface) + `01-sources.law` (provenance)
+ `02-montant` (right, MF, allowance) + `03-devoirs` (contract) +
`04-suspension` + `05-recouvrement` + `06-jeunes-activite` +
`07-demandes-instruction` + `08-conventions` +
`09-devoirs-insertion` + `10-controle-recours` + `11-statistiques`;
bareme parameters in `bareme/*.lawparam.json` (generated).

## Measure

Wave-4 measure (`audit.py --fast fr-rsa`, static profile, 06.10.2026):
6 `.law` files, 30 scenarios, 73 rules, all strict;
established ×209, not_known ×36. Form catalog: 9 of 57 declaration
kinds used. Dangling premises 0. One-way premises 1 of 73
(`RadiationSansVersement`: the elapsed payment-free period is a
lawful case input, exercised by `radiation-sans-versement`). Dead
symbols 0 (86 symbols). LawQL lints 5, all `accepted` in
`corpus/ratchets/ql-baseline.json`: two lawful empirical inputs
(prescription years, presidential remission) and three deliberate
`then not` rules the engine needs for FALSE_ONLY
(`HeuresInsuffisantes`, `SuspensionSansProcedure`,
`NonTenuExempte`). Reachability (§6) not run (`--fast`).

FINISH measure: NOT_RUN (nochecks authoring, 08.10.2026; the figures below predate the MF-decree round). File
inventory, not a measurement: 12 `.law` modules, 100 `.lawtest`
scenarios in 10 `[[tests]]` families (all files on disk
registered), 5 new bareme specs authored (pending generation).
The static-review repair round added 4 rules (artist-author
alternative in both D.262-25-2 windows, prefect recipient in both
D.262-95 windows), bound the turnover MF inputs to the turnover
year, and removed the invented D.262-100 claim gate. The
re-review-02 repair round added no rules (126 total): it made the
pre-2023 artist route cumulative, gated both charge-reimbursement
duties on established charges, scoped D.262-98 to the L.262-55
sample, aligned both cascade right months to the filing month, and
bound all 27 duty/prohibition addressees to source-backed actors.
The full-evidence-04 repair round added no rules (126 total): it
replaced the `not_known` presidential-inaction test with an
established six-week absence fact (D.262-65-2), bound both
free-instruction prohibitions to the filing recipient (D.262-28),
and added 3 paired unknown/different-recipient controls.
Fresh numbers require the deferred run queue (sources + bareme
generation, `law fix imports`, check, lower, suites, pinning,
audit) after the locks free; the reviewer rebuilds the snapshot
before any test.

MF-decree round (08.10.2026, session 5): 6 decree sources/editions/fragments
(`DEC<year>_<no>_ART1`), bareme `MontantForfaitaireDecret` (15 bareme in all),
7 rules (133 in all: `MfBaseDecret`, `MfBaseSaisieMarque`, `MfBaseSaisie`,
`MfCompositionMinima`, `MfMoisReference1..3`), 18 scenarios in the family
`fr.casf.rsa#mf-decrets` (118 `.lawtest` in all). Measured: `lawc check` OK;
`check_lawtest_suites --package` 118/118 on the oracle and on Rust (before:
100/100); `check_source_pinning --only` 18 publications, 0 violations;
`check_i18n_overlays` no dangling key (28 `kk` keys added, none removed).

Window round (08.10.2026, session 6, owner decision of the same day): the window
2022-07..2023-03 is bridged by article 9 of law 2022-1158 (source `LOI_2022_1158`,
fragment `LOI_2022_1158_ART9`, bareme `MontantForfaitaireBaseLoi2022` and
`CoefficientLoi2022`, rule `MfBaseLoi2022`, 17 bareme in all), the rounding of
the quarterly average is the reading `fr.minima.ressources::MoyenneArrondieCentime`
(see "Readings"). 9 scenarios added (127 `.lawtest` in all): family
`fr.casf.rsa#mf-loi-2022` (7) and `fr.casf.rsa#lecture-moyenne` (2).

## Flat-rate amount built, not supplied (DECISION-0452)

The household montant forfaitaire is no longer a case input in the pinned
years. Chain, from the pinned bytes:

1. `sources/decrets-mf/` (`tools/pin_mf_decrets.py`) holds article 1 of the six
   revaluation decrees; `01-sources.law` carries them as sources
   `DECRET_<year>_<no>`, editions `DEC<year>_<no>` and fragments
   `DEC<year>_<no>_ART1` (`tools/build_sources.py`).
2. `bareme/MontantForfaitaireDecret.lawparam.json` (`tools/build_bareme.py`)
   reads each figure out of the pinned text ("est de / est fixé à NNN,NN euros")
   and anchors it to the decree fragment: 564.78 from 2021-01 (decree 2020-490,
   allocations of April 2020), 565.34 from 2021-04, 575.52 from 2022-04 to
   2022-07, then 607.75 / 635.71 / 646.52 from the 1 April of 2023 / 2024 / 2025
   for a year each. The window 2022-07..2023-03 is not a value of this parameter:
   see "Readings" (article 9 of law 2022-1158, 575.52 x 1.04, rule `MfBaseLoi2022`).
3. `MfBaseDecret` reads the parameter at the legal time of the case into
   `mf_base_retenue`; a supplied `mf_base` wins (`MfBaseSaisieMarque`,
   `MfBaseSaisie`), which keeps every earlier case valid.
4. R. 262-1 composes the household amount from that base (`mf_menage`: +50 %
   for the second person, +30 % for each further dependant, 40 % from the third
   child or under-25 dependant; lone-parent increase `mf_majore`).
5. The package then WRITES the result into the neighbour: `MfMoisReference1..3`
   put `mf_applicable_mois` (increase included) into
   `fr.minima.ressources::mf_mois` for each month of the reference quarter, and
   `MfCompositionMinima` puts the size-class amounts into
   `fr.minima.ressources::mf_composition` (a foreign rule head, E-0126; nothing
   becomes `pub` that was not, both relations are the neighbour's own).
   A couple, a family or a lone parent therefore needs no flat-rate fact:
   `tests/mf-decret-couple-trimestre.lawtest` takes a pair from the decree to
   the allowance (633.9946 EUR) with no amount supplied.

## Readings (§152): rounding is practice, not text

Two rounding choices are not in any pinned text; each is a named, disputed
interpretation outside any group, so the default answer does not change (the
reading is silent unselected) and the choice is made in the `context` of the
scenario or the case, as `PpPlancherFinal` in `fr.apl`:

- `fr.minima.ressources::MoyenneArrondieCentime` (owner decision 08.10.2026, basis:
  the practice of the funds, CNAF): the quarterly average of R. 262-7 (resources
  and amount due) is rounded to the centime, HALF_UP, in place of the exact
  division that refuses a non-terminating quotient. It lives with the owner of the
  division (`fr.minima.ressources`, `02-trimestre.law`, `pub interpretation`).
  Case OpenFisca rsa #19 (334 / 3): resources 111.33, amount due 689.66 (the
  unrounded 689.6646 is not what the funds pay). Scenarios `moyenne-arrondie-couple`
  and `moyenne-inexacte-sans-lecture`. Where the quotient is exact with two
  decimals or fewer, both answers coincide; the reading also rounds an exact
  quotient that has more than two decimals (e.g. the MF-derived 3 or 4 decimals),
  which the funds do too.
- `MfJuillet2022ArrondiCentime` (this package): article 9 of law 2022-1158 revalues
  on 1 July 2022 the amounts revalued under L. 161-25 by the coefficient 1.04;
  L. 262-3 al. 1 makes the montant forfaitaire one of them (pinned text), so the
  window 2022-07-01 .. 2023-03-31 is built as the decree 2022-699 amount (575.52)
  x 1.04 = 598.5408, rounded to the centime HALF_UP = 598.54 (rule `MfBaseLoi2022`;
  factors are the bareme `MontantForfaitaireBaseLoi2022` and `CoefficientLoi2022`,
  read from the pinned texts). Neither art. 9 nor L. 161-25 nor L. 262-3 states a
  rounding: practice of the funds. The window ends where decree 2023-340 sets
  607.75 outright. Scenarios `mf-loi-2022-*`; a supplied `mf_base` still prevails.
  The art. 9 bytes are shared with `fr.css.revalorisation`
  (`sources/loi-2022-1158-art9.txt`, same sha256) and re-pinned here
  (`tools/pin_mf_decrets.py --loi`) instead of importing that package, so that the
  RSA world does not grow by a package for one 1.7 KB fragment.

## R. 262-1 composition and L. 262-9 period

For rank five and above, the case supplies each counted person's household rank,
child/dependent status and, for a dependent who is not a child, date of birth.
`Rang40` assigns 40% to the third or later dependent child or person under 25;
`Rang30AvantTroisieme` and `Rang30Autre25` assign 30% where applicable.
`Rangs5Plus40/30` count the classified persons only when every member of the
reported household size has a rank fact. The OpenFisca hook supplies parent and
child membership facts and leaves rate classification to these rules. Cases with
other dependants require their established personal facts.

For the increased amount, `majore_demande_mois` is the established filing month;
`MajoreDebutDemande` builds the first month of service from it. The generating
event and delay beyond six months remain separate facts under R. 262-2. A foreign
case without a dated declaration/claim cannot establish the start of the
12-month service period. In particular LexImpact's pregnancy true across
2022–2024 does not establish such a date.

## Their case to our answer

Foreign benchmarks are expectations, never semantic sources. Euro
totals use the MF scale derived from the shared single amounts
(2023: 607.75; 2024: 635.71) through the pinned rates; only
structure is asserted. Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (LexImpact
2024 `rsa_*.yml` + OpenFisca `rsa_majore.yaml`,
`rsa_exclusion_foyer.yaml`, `rsa_base_ressources.yaml`).

Reading guide:

- All four 2024 amount series reconcile exactly: majoré 128.412 %
  (780.42 → 707.49 after the 12 % flat-rate; 816.33 → 740.04),
  single scale minus forfait (534.82; 559.42), 150 % scale minus
  base minus capped aid (665.43; 696.05), same with ARE 265 in the
  base (400.43; 431.05).
- The April step (+4.6 %) and the October APL rise absorbed by the
  R.262-10 cap are visible in their series; the 1 April factor
  itself is an input (b).
- Eligibility findings (`isole_majore`, jeune work condition,
  household size) arrive as case inputs (b); the foyer child-count
  exclusion is a boundary (input contract — the pinned R.262-1 is a
  pure rate scale).
- Blind independent reading (session G): [`analysis/blind-read-cases.json`](analysis/blind-read-cases.json) (24 probe cases) with answers in [`analysis/blind-read.json`](analysis/blind-read.json). The author's own 20-case reading is preserved in commit `618ed5c9e8`.

## Boundaries

- DSS_PENDING / B-RSA-MF-EURO: the MF euro base is built from the pinned decrees for
  the right months 2021-01 … 2022-06 and 2023-04 … 2026-03, and from the pinned
  article 9 of law 2022-1158 for 2022-07 … 2023-03 (reading
  `MfJuillet2022ArrondiCentime`, see "Readings"; without the reading the window has
  no built base and the stale 575.52 is not carried forward, tests
  `mf-decret-trou-2022`, `mf-loi-2022-*`); from 2026-04-01 no base is built and a
  case-supplied `mf_base` (with the 1 April L.161-25 factor pre-applied) stays the
  input (test `mf-decret-apres-serie`). The series end 2026-04-01 is the next
  annual 1 April and is NOT extended (checked 08.10.2026): L. 262-3 al. 1 says the
  amount is revalued each 1 April by the L. 161-25 coefficient, but the decree of
  1 April 2026 is not among the pinned bytes, and the pinned instruction
  DSS/2B/2026/46 of `fr.css.revalorisation` (coefficient of 1 April 2026) deals with
  family benefits and does not name the RSA; a coefficient is not an amount, and the
  rounding of the decree is unknown. The parameter is read at the legal time
  of the case, not at `mois_droit`: a retrospective question uses the legal
  time of the month it asks about.
- B-RSA-MF-INPUT-CONTRACT: closed from this side (see the section above) for
  the worlds that contain this package; `fr.minima.ressources` alone still
  takes `mf_mois` / `mf_composition` as inputs.
- B-RSA-MF-MOIS-TRIMESTRE: R. 262-7 I does not say which monthly flat-rate enters
  each of the three intermediate amounts (the intermediate-amount article is
  not pinned); the model carries the MF of the month of right (increase
  included) to all three reference months. A quarter that straddles the 1 April
  revaluation is therefore computed with the new amount throughout.
- B-RSA-EXPERIMENTATION-2024: décret n° 2024-693 du 5 juillet 2024 (expérimentation
  des déclarations préremplies, arts 1–10) and the arrêté du 7 juillet 2024
  (1 October 2024 – 1 March 2025) are pinned in
  `fr.minima.ressources/sources/experimentation-2024/`. Allocataires of the CAF
  of the Alpes-Maritimes, Aube, Hérault, Pyrénées-Atlantiques and Vendée who
  declare through the téléservice get, by derogation to R. 262-7, the
  reference months M-4…M-2 and DSN-prefilled blocks (art. 3), the spouse deemed
  present over the same months (art. 2), turnover rules for the self-employed
  (art. 4) and, at the first renewal, the lower of two averages (art. 8). NOT
  modelled: the text of art. 3 is unambiguous, but the regime is a second
  computation of the quarter on a window for a class of claimants, i.e. a change
  of the roughly twenty dated rules of `02-trimestre.law`, not an insertion. A
  case with the experiment flag is not transferred from OpenFisca (#18).
- B-RSA-MOYENNE-INEXACTE: R. 262-7 gives no rounding rule for the quarterly
  average; a non-terminating Money division (167 + 167 + 0 over three months)
  makes the document refuse (INEXACT_DIVISION, §50/§18; status RUNTIME_ERROR) unless
  the reading `fr.minima.ressources::MoyenneArrondieCentime` is selected in the
  context (owner decision 08.10.2026, see "Readings"); cases with equal or
  divisible months run under either choice.
- The young-worker turnover MF (`mf_reference_ca`) additionally carries
  the turnover year as typed provenance: the retained amount is the
  one in force at 1 January of that year
  (D.262-25-2/25-3 2°), joined to the turnover of the same year.
- B-RSA-PF-CASCADE: prime d'activité cascade into the base is a
  same-lane input.
- B-RSA-SANCTION-PRE202506 / B-RSA-AVANT-2025: sanction scales run
  from 2025-06-01; earlier law is out of scope.
- B-RSA-RECOUVREMENT-PRE202103: R.262-92-1 runs from 2021-03-25.
- B-RSA-DECRET-ARRETE: decree 2025-478 transition runs to
  2027-07-01; art. 13 not pinned.
- APL-FORFAIT-PENDING (via `fr.minima.ressources`): received
  housing aid is an input with provenance until the wave-5 cascade.
- DOM (L.542-/R.542-) is SANS_OWNER, wave 7.
- B-RSA-CTRAV-HORAIRES: annual hours of C. trav. L.3121-41 al. 3
  (D.262-25-1 base) unpinned — retained case input.
- B-RSA-TAUX-MARCHE: overnight money-market rate (D.262-64 base)
  unpinned — retained case input; the one-point top-up is a
  parameter (MajorationTauxMarche).
- B-RSA-PLAFOND-SECU: monthly social-security ceiling of CSS
  L.241-3 (D.262-77) unpinned — retained case input.
- B-RSA-D553-MODALITES: CSS D.553-1/2/4/5 recovery modalities
  (D.262-94-2) owned by the payment-core finish group — external.
- B-RSA-ARRETE-LISTES: ministerial orders fixing the statistical
  lists (D.262-99) — source boundary, no rule.
- Seams (documented, fund-established synthesis outside the
  package): 18–25 age synthesis into `age_charge_condition`
  (D.262-25-* gives the hours limb only); full bound-by-duties
  synthesis into `tenu_obligations_262_28` (D.262-65 gives the
  income limb only); L.262-41 lifestyle assessment around the
  D.262-77 exclusion.
