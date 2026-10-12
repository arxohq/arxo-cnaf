# Foreign through-case expectations — payment stage (S4 draft)

Status: EXPECTATIONS ONLY. No number from the foreign suites enters any
rule. No foreign amount is copied into this file: only case ids, household
shapes, periods and asserted variable names.

Source: `openfisca/openfisca-france` at the registry pin `16b2e696`
(tag 176.1.2), read from the vendored checkout under
`.scratch/openfisca-france/` (pin verified against
`docs/foundations/fr-cnaf/registry/foreign-cases.json`, which lists these
suites file-by-file without input/output detail, so the YAML files
themselves were parsed: 508 files / 508 tests).

## 1. Counts

| Pool | Tests | Touching payment stage |
|---|---|---|
| `tests/mes-aides.gouv.fr/` | 424 | 305 |
| `tests/leximpact/2024/` | 84 | 84 |
| Total | 508 | 389 |

Payment-stage variables asserted, by test count (a test counts once per
variable; gross/CRDS/net triples exist only in leximpact):

| Variable family | Tests | Suites |
|---|---|---|
| `rsa` (post floor, CRDS-exempt) | 109 | MA + LX |
| `aide_logement` (+ `apl`/`als`/`alf`, post floor/CRDS/rounding) | 80 + 13 + 5 + 3 | MA + LX |
| `af` / `af_base` (+ `crds_af`, `af_nettes_crds`) | 50 / 6 | MA + LX |
| `aspa` | 37 | MA |
| `cf` (+ `crds_cf`, `cf_net_crds`) | 35 | MA + LX |
| `ass` | 28 | MA + LX |
| `asf` (+ `crds_asf`, `asf_nette_crds`) | 19 | MA + LX |
| `ppa` + `crds_ppa` + `ppa_nette_crds` (always as triple) | 19 | LX only |
| `aefa` | 9 | LX only |
| `ars` + `crds_ars` + `ars_nette_crds` (always as triple) | 7 | LX only |
| `reduction_loyer_solidarite` | 4 | LX only |
| `paje` + `crds_paje` + `paje_nette_crds` (+ `paje_cmg`) | 1 | LX only |
| `aah` | 2 | LX only |
| `asi` | 3 | MA |
| `crds_hors_prestations` (wages/pensions side, context only) | 75 | LX only |

Full gross + CRDS + net triples per benefit: PPA 19, AF 6, ARS 7,
ASF 3, CF 2, PAJE 1. Mes-aides asserts gross amounts only (never the
CRDS/net counterparts); 2 mes-aides tests assert 4 benefits at once
(see #9–#10 below), all others assert 1–2.

Periods: mes-aides is almost all `month:2014-07` … `month:2015-09`
(plus a few 2017 and two 2024-01); leximpact is year `2024` with
`absolute_error_margin: 1` (euro tolerance, not exact cents).
Mes-aides uses `relative_error_margin: 0.02`.

Household shapes over the 389 candidates (adults+children; leximpact
from `familles.parents/enfants`, mes-aides from input ages, adult = 18+):
single 171, couple 69, 1+1: 32, 1+2: 21, 1+3: 24, 1+4: 9,
2+1: 21, 2+2: 25, 2+3: 8, plus a tail of larger/composite households
(up to 3+8). No shape metadata beyond this was extracted.

Zero-amount assertions (non-payment-shaped expectations, mostly
ineligibility rather than floor edges): rsa 32, aide_logement 26,
als 18, cf 14, ass 9, aspa 8, asf 7, af 2, apl 1, asi 1.

## 2. What the asserted variables actually cover

Verified in the vendored formulas (paths relative to
`openfisca_france/model/`):

- **CRDS is per-benefit and observable.** `crds_af`, `crds_asf`,
  `crds_cf`, `crds_paje`, `crds_ars`, `crds_ppa`, `crds_logement` are
  separate variables; `*_nette_crds = brut + crds_*`. RSA/AAH have no
  CRDS variables (exempt). This matches our 02-crds.law split.
- **Non-payment floors are embedded, not asserted standalone.**
  `rsa_montant` zeroes below `montant_minimum_verse` (`rsa.py`);
  same pattern for PPA (`ppa.py`); `aide_logement_montant_brut`
  zeroes below `seuils_minimum_versement[type_aide]`
  (`aides_logement.py`). Floors are observable only through cases
  whose brut falls under the threshold (the `rsa_01/rsa_02 "seuil"`
  cases are the closest; genuine floor-edge cases are otherwise
  absent — most zeros are plain ineligibility).
- **Rounding is embedded.** `aide_logement_montant =
  round_(montant + crds_logement, 2)`; CF/PAJE round to cents inside
  their formulas. No standalone rounding variable exists; cent-level
  rounding is observable only via final totals, and leximpact's ±1 €
  margin makes it unusable for rounding checks.
- **Recovery/retenues do not exist upstream.** No variable models
  indus, recouvrement, retenues on prestations, the 10 % indemnity,
  or fraud retention. Our 04-recouvrement.law has no foreign
  through-case coverage at all.

## 3. Candidate through-cases for the famille-dans-le-temps dossier

Ranked by coverage of OUR scope (CRDS + floors + net on PF benefits;
housing belongs to `fr.apl.versement`, RSA/PPA/AAH to wave-4 pubs).

| # | Case id (file stem) | Suite | Household | Period | Asserted payment vars | Covers (ours) | Gaps |
|---|---|---|---|---|---|---|---|
| 1 | `couple_1actif_1inactif_0.8_SMIC_3_enfants_d1` | LX | 2+3 | 2024 | AF+ARS+CF+PPA triples, AL/APL/RLS | AF, ARS, CF CRDS→net | year period; ±1 € margin; no floor edge |
| 2 | `couple_1actif_1inactif_1.5_SMIC_3_enfants_d2` | LX | 2+3 | 2024 | AF+ARS+CF+PPA triples | AF, ARS, CF CRDS→net (higher-income mirror of #1) | same as #1 |
| 3 | `rsa_01_seuil_rsa_inactif_d1` | LX | 1+1 | 2024 | ASF+ARS triples, RSA, AEFA, AL/APL/RLS | ASF, ARS CRDS→net; RSA post-floor | RSA brut pre-floor not asserted |
| 4 | `rsa_02_seuil_rsa_chomeur` | LX | 1+1 | 2024 | same shape as #3 | same, chômeur variant | same as #3 |
| 5 | `famille_monoparentale_un_enfant_0.8_smic_d2` | LX | 1+1 | 2024 | ASF+PPA triples, AL/APL/RLS | ASF CRDS→net (single-parent) | no AF/CF/ARS here |
| 6 | `01_couple_marie_salaries_secteur_prive_1_smic_chacun_2_enfants_d3` | LX | 2+2 | 2024 | AF+ARS+PPA triples | AF, ARS CRDS→net | no CF/ASF |
| 7 | `paje_cmg_01_salaries_secteur_prive_2.5_smic_1_enfant_mode_de_garde_d8` | LX | 2+1 | 2024 | PAJE triple + `paje_cmg` | PAJE CRDS→net (only PAJE case) | single data point |
| 8 | `ass_02_couple_marie_salarie_secteur_prive_1_smic_conjoint_ass_1_enfant` | LX | 2+1 | 2024 | ARS triple, ASS, AEFA, AL/ALF | ARS CRDS→net | ASS/AEFA outside our scope |
| 9 | `test_mes_aides_54f73d14…` ("Couple avec 3 enfants…") | MA | 2+3 | 2015-03 | AF, AL, CF, RSA (gross only) | multi-benefit household shape | 2015 law; no CRDS/net counterparts |
| 10 | `test_mes_aides_55915f4c…` ("Foyer 3 enfants") | MA | 1+3 | 2015-06 | AF, AL, ASF, CF (gross only) | multi-benefit household shape | 2015 law; no CRDS/net counterparts |

Further triple cases not in the top 10 (same 2024/LX caveats):
AF — `Z_couple_marie_…_1.3_smic_chacun_2_enfants_d4`,
`Z_couple_marie_…_3.2_smic_2_enfants_d5`,
`irpp_economique_06_…_effet_quotient_familial_d7`;
ARS — `ass_02_…_conjoint_sans_ass_1_enfant`;
PPA-only triples (wave-4, no PF benefit alongside) — 10 single-adult
cases (`01_salarie_prive_1.25_SMIC_d4`, `ZZZ_aah`, `ZZ_cotis_…`,
`ZZ_salarie_prive_cdd_…`, `csg_salaire_01_…0.8_SMIC_d2`,
`csg_salaire_01_…1_SMIC_d3`, `exoneration_…_tode_01/02`,
`prime_partage_valeur_01/02/03`, `irpp_economique_01/02`,
`ass_02_…_conjoint_sans_ass`,
`ass_02_…_conjoint_sans_ass_1_enfant` is ARS+PPA, counted above).

## 4. Convertibility: converter vs hand-written `.lawtest`

Wave-3 pattern (per `corpus/laws/fr/pf-cf/tests/foreign/REPORT.md`,
`of-2018-cas1.lawtest`, `corpus/tools/foreign/openfisca_tests.py`):

- The supported path is **extract + emit**: `extract` runs THEIR
  engine in their venv (`.scratch/of-venv`) to recompute
  intermediate facts and targets — the published YAML numbers are
  NOT trusted (their `reforme_janvier_2021` file mismatched their
  own code 12/12, measured 13.09.2026, quoted in the converter
  docstring) — then `emit` renders `.lawtest` via a package
  `tools/foreign-map.json` (cf. `fr.apl`, `fr.pf.core`,
  `fr.pf.paje` maps) and classifies (a)/(b)/(c) in REPORT.md.
  pf-cf's ports are hand-shaped Stelle (b)-style cases, not raw
  converter output.
- **Mes-aides candidates (#9–#10 and the 305 gross-only cases) fit
  the converter**: month periods, flat `output: {var: value}` which
  `extract` accepts. Needs a new `fr.prestations.versement`
  foreign-map whose facts are per-benefit bruts recomputed by their
  engine. Value is limited: gross-only, 2014–2015 law, 2 % relative
  margin.
- **Leximpact candidates (#1–#8) do NOT fit the converter as-is**:
  `period: 2024` (year) is rejected by `extract` ("период не месяц").
  Options: (i) hand-written `.lawtest` in the pf-cf Stelle style
  (recommended: only ~8 cases, and the dossier household is
  bespoke anyway); or (ii) extend the converter with year-period
  support. Either way the ±1 € margin means these can only anchor
  structure (CRDS applies / floor bites / net = brut − CRDS), never
  cents.
- **Recovery, rounding-to-cent, and floor-edge expectations have no
  converter path**: no upstream variables exist. They need
  hand-written `.lawtest` against our own texts (or Civiltax/Catala
  if those model recovery — out of S4 scope).

## 5. Gaps vs our scope (summary)

1. AEEH, AJPP, AJPA, CMG (hors `paje_cmg` input), AER: zero foreign cases.
2. PAJE: exactly one triple (#7).
3. Rounding: observable only inside AL totals; LX margin kills precision.
4. Floors: embedded; no pre-floor brut asserted anywhere except via
   recomputation; no clean floor-edge case except the two `rsa_*seuil*`.
5. Recovery/indus/retenues/10 %/fraud +50 %: entirely absent upstream.
6. Period mismatch: MA is 2014–2015 law (pre-PPA-scale reforms etc.);
   our dossier is 2024–2026. LX is 2024 but year-grained ±1 €.
7. Their YAML numbers ≠ their code (known): any conversion must
   recompute via `extract`, never copy file values.
