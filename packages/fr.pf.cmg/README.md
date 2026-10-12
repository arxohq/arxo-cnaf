# `fr.pf.cmg` — complément de libre choix du mode de garde (CMG)

Executable formalization of the CMG: eligibility with the age windows
(under 6, isolated parent to 12, shared residence from 2025-12-01 —
L. 531-5–L. 531-6, R. 531-5–R. 531-6), the contribution share
(D. 531-17), the 2025 formula with the hourly cap, the reference cost,
the effort rate and the resource test (D. 531-18–D. 531-18-3, decrees
2025-514/2025-515), the pre-2025-09-01 banded scale (D. 531-19–D. 531-21),
structure/EAJE care with tiers-payant (D. 531-22), cumulation with AF
sharing, shared residence, and the home-care differential (D. 531-23),
and the paying duty with recovery of undue majorations.

Scope: CSS L. 531-5–L. 531-6, L. 531-8-1, L. 531-9;
D. 531-17–D. 531-23 with D. 531-18-1–D. 531-18-3; R. 531-5–R. 531-6;
decrees 2025-514 and 2025-515
(41 documents, 44 fragments after the pending generation; L. 531-8-1
and L. 531-9 added by FINISH paje-cmg, GENERATED_OUTPUT_PENDING). The
2025-09-01 reform is versioned as
windows: pre-reform `[@2021-01-01,@2025-09-01)`, reform
`[@2025-09-01,infinity)`. Upstream premises (opener status, debtor
body, employment facts) are read from `fr.pf.core`, never re-concluded
here. Money inputs not present in the pinned bytes (ceilings, factors,
reference cost) arrive as stated case facts.

## Measure

`law audit .` (formalization measure, static profile): 151 rules
(17 + 8 + 31 + 15 + 43 + 27 + 10 across 02–08). FINISH paje-cmg adds
6 rules in 09 (non-cumul markers, levy minoration) — authored, not
measured (GENERATED_OUTPUT_PENDING, no audit run). Form catalog:
16 detectors, 1 finding `evaluative-fact-without-producer` on
`recouvrement_majoration_action` — an empirically exercised action
(never produced, like the uz-family-code registration actions), which
is the correct shape for a performed recovery, not a defect.

## Their case to our answer

Foreign benchmarks are expectations, never sources. There is no
foreign case to compare: OpenFisca has no CMG reform variant and
there is no Catala CMG model. Foreign support is DSS/CNAF document
reading plus the blind protocol below.

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (no foreign
cases; status BLIND_PENDING).

OpenFisca-France 176.1.2 has one CMG output, `paje_cmg`, and its formula
(`paje.py`, `formula_2017_04_01`) is the band maximum of the DSS table
("CMG maximal / intermédiaire / minimal": BMAF × age share × band rate),
without any expense input. D-85 (09.10.2026) therefore compares one stage
only, the maximum: `maximum_ancien_b` for direct employment of a childminder
(their `empl_dir`) and `maximum_structure` in `STRUCTURE` mode for the 172.57 /
143.81 / 115.05 % figures (their `ass_mat`); `gar_dom` (208.53 / 179.76 /
151.00 %, our `EAJE` rows) and the sum due (`montant_cmg_du`) are not
compared. The hook `tools/openfisca_hook.py` takes the case facts from their
run; BMAF comes from the pinned `fr.css.revalorisation` fragments and the
resource ceilings from the pinned DSS instructions
(`revalorisation/sources/dss-*.txt`, separately published bases and per-child
supplements for the entitlement year, including the isolated-parent table). Report: the cross
report of `fr.prestations.versement`
(`analysis/openfisca-176-cross/`, LexImpact `paje_cmg_01…`, 12 months of 2024);
the register's two formula cases (2017-04, 2018-04) stay before the package
window (class (в)).

Second reading: 22 inputs-only blind cases in
[`analysis/blind-read-cases.json`](analysis/blind-read-cases.json)
across formule / ancien-bareme / structure / cumul-alternance /
devoir-versement families, guarded by
`analysis/test_blind_read_cases.py` (3/3 pass). Reading by a second
model is pending (BLIND_PENDING). FINISH paje-cmg adds 20 neutral
inputs-only cases in
[`analysis/blind-read-cases-finish.json`](analysis/blind-read-cases-finish.json)
(pfcmg-finish-01..20: non-cumul, levy minoration, shared residence,
activity assessment, age gates); no answers recorded.

The old 3–6 age scale follows L. 531-5 IV and D. 531-20. A third birthday
between January and August keeps the full rate through 31 August; the half rate
starts in September. Outside that extension the half rate applies after the
third birthday, and the old scale ends before six. The case supplies the
child's birth date and entitlement month at the three-year boundary; completed
age alone does not decide the rate. L. 552-1 (pf-core/sources/css/L552-1.txt:2)
and R. 552-3 I–II 1° (pf-core/sources/css/R552-3.txt:2-4) govern
monthly changes and CMG cessation; this package's age input is a
first-of-month case snapshot, while the exact payment transition for a
mid-month birthday belongs to the separate versement stage. OpenFisca's `paje_cmg` ignores the
January–August full-rate extension, so synthetic comparisons at that boundary
are qualified separately.

## Boundaries

- DSS_PENDING: 50% home-cap arretes, SMIC-growth
  factors, BMAF series, RSA forfait euros, the reference hourly
  cost (case fact `cout_reference_retenu`, B-CMG-COUT-REFERENCE) —
  sums are case facts until DSS/BO bytes pin them.
- B-CMG-V-BIS-MORT-NE: the stillborn V-bis suspension, no rule.
- B-CMG-MAJO-ANCIENNE: pre-2025 D. 531-19/20 unmeasured
  1°/2°/4° majorations — only the +40% single-parent rise is built.
- B-CMG-MASSE-ANCIENNE / B-CMG-STRUCTURE-FAMILLE: old-law mixed
  pooling and home per-family pooling unbuilt.
- B-CMG-FRATRIE: differential sibling most-favourable rule unbuilt.
- B-CMG-EXTINCTION-JOUR: extinction cohort A at month precision;
  day precision unbuilt.
- B-CMG-DEMI-DOUBLE / B-CMG-MAJO-COEX / B-CMG-CUMUL-DOMICILE-MIXTE:
  old-law half co-occurrence, majoration co-occurrence, and mixed-mode
  D. 531-23 2° household scope unbuilt.
- B-CMG-L531-9-PREPARE: cross-benefit payment exclusion (CMG vs
  full-rate PreParE / daily allowance) needs the versement stage
  (fr.prestations.versement, wave 5); markers conclude, amounts compute.
- B-CMG-L531-8-MONTANT: L. 531-8 unpinned, L. 133-5-10/12 mechanics
  external; the minoré levy builds from two established amounts.
- B-CMG-L531-9-COHORTE-2014 (RETURN 2026-10-08: modelled; FULL RETURN
  03: boundary pair): the 2014-wording NOTA cohort (born/adopted from
  01.10.2014) is the explicit gate cohorte_l5319_2014 on both
  PreParE-bar rules; the affirmative pre-cutoff input concludes
  NEITHER, the at-cutoff child (born 01.10.2014) concludes TRUE, and
  the unevaluated cohort stays a distinct NEITHER control. The VI
  exception is the affirmative fact prepare_plein_hors_vi (missing
  evidence proves nothing).
- `law engine check` carries 38 `LDC-E1372` `@id` warnings — the
  accepted corpus-wide form (DECISION-0352 §4), not defects.
