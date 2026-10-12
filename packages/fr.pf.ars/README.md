# `fr.pf.ars` — school-start allowance (allocation de rentrée scolaire)

Executable formalization of the ARS: per-child eligibility with the
R. 543-2 age lines (six reached before 1 February of the following
year, under eighteen on 15 September, both strict; the L. 543-1
para. 2 young student with capped pay), the single-tier resource
ceiling (R. 543-5: +30 % per dependent child from the first),
age-band amounts (D. 543-1: 89.72 / 94.67 / 97.95 % of the monthly
base at 31 December), the standalone differential (L. 543-2,
R. 543-6-1: April amounts summed over bands, per entitled child), CDC
vs family payment routing for placed children (L. 543-3, R. 543-8),
and the fund payment duties with the 31-October deadline (R. 543-7).

Scope: exactly 18 CSS articles (L543-1, L543-2, L543-3, R543-1–R543-9,
D543-1, D543-2; DOM extension L755-22, R755-14, R755-14-1). Upstream
premises (child in care, opener status,
debtor body) are read from `fr.pf.core`, never re-concluded here;
`date_naissance` is a local stand-in (MIGRATION-REQ-PFARS-01).

DOM extension (FINISH transfer, `07-dom.law`, nochecks authoring): L. 755-22
grants the ARS in the six L. 751-1 collectivities on collectivity
residence; R. 755-14 makes R. 543-1..7 applicable in L. 751-1
departments only, on department residence with provenance, as a
separate branch that does not gate the award (D76 territory split);
R. 755-14-1 excludes ARS actually paid (versées) in a department from
the CAF health/social action fund resources. Four thin link statuses
over three heads (`ars_attribuee_dom`, `ars_r543_applicable_dom`,
`ars_exclue_ressources_fonds`) read the untouched metro computation; no
metro rule is duplicated or gated on territory. Adopted readings: the
allocataire parent's residence anchors the case, collectivity and
department facts stated independently (Q-PFARS-DOM-1);
"collectivités" vs "départements" are two source classes
(Q-PFARS-DOM-2 superseded by the D76 return); R. 755-14-1 excludes
only actually paid (versées) amounts, each per paid track and child on
matching `ars_verse` evidence plus department residence; the fund
aggregate itself is not calculated here (B-PFARS-DOM-FONDS, package
coverage boundary, no engine limitation claimed). Source outputs for
the three articles are GENERATED_OUTPUT_PENDING (`build_sources.py
--write` in the deferred queue). Measure counts below predate the
transfer; re-measure at the deferred run.

No foreign benchmarks exist for the ARS (no OpenFisca ARS tests; the
Catala prestations_familiales scope has no ARS): the suite is
self-built on pinned texts, DSS-stated inputs and blind reading
(B-PFARS-FOREIGN-NONE).

## Measure

`law audit .` (formalization measure, static profile): 12 rules,
dangling premises 3 (all enum band variants in bodies, none
unsupplied), one-way premises 0 of 12. Form catalog: 16 detectors, 2
findings, both `strict-reader-of-foreign-defeasible-head` — the two
eligibility rules that read the upstream `enfant_ouvre_droit` head,
whose producers are defeasible in `fr.pf.core`. That is the documented
package split (REQ-PFCF-02), not a defect.

## Their case to our answer

No foreign case to port. Structure is asserted by the unit suite (21
tests: eligibility bands with boundary-day probes, single-tier
ceilings, the three rate bands, the differential with the equality
shut-off, CDC routing both ways, duties on all tracks) and by 22
blind second-reading cases
(`analysis/blind-read-cases.json`, BLIND_PENDING).

## Boundaries

- B-PFARS-FOREIGN-NONE: zero foreign benchmarks found; reliance on
  DSS-stated inputs and blind reading.
- B-PFARS-BMAF / B-PFARS-PLAFOND-NOMINAL: euro totals rest on stated
  assumptions (illustrative monthly bases; decree nominals arrive as
  case inputs, unpinned arretes/decree).
- B-PFARS-SEUIL: the 15 EUR non-payment floor (D. 543-2) operates on
  the household total, which the engine cannot fold; with lawful base
  values every single-child amount exceeds 15 EUR, so the floor never
  suppresses payment in the computable domain.
- B-PFARS-SITUATION: the family situation (counts, placement) is
  assessed 31 July before the rentree (R. 543-6, R. 543-8); counts
  arrive fund-stated as of that date. The May–July deceased-child rule
  (L. 552-7) and the R. 532-3..8 renvoi are upstream.
- B-PFARS-CDC-PROC: CDC account mechanics, interest (L. 518-23 monetary
  code), yearly reporting and indu restitution (R. 543-9) are
  inter-organisation procedure, out of scope; only the routing
  conclusion (CDC pecule vs family member) is built.
- B-PFARS-DOM-FONDS: the CAF health/social action fund resource
  computation (R. 755-14-1) is action-sociale mechanics, out of scope
  (program GOAL §1.1); only the per-child exclusion status is built,
  and only on matching `ars_verse` payment evidence for the due
  amount being excluded plus department residence.
- B-PFARS-DOM-L751-1: the L. 751-1 enumeration (which collectivities /
  departments) is not pinned here; residence arrives as two
  independent fund-stated inputs, `residence_dom` (collectivity,
  L. 755-22) and `residence_departement_dom` (department, R. 755-14
  + R. 755-14-1), neither implying the other. Liaison to the
  `fr.pf.dom` territory vocabulary requested once that package is
  accepted.
- B-PFARS-DOM-HORS-DEPT: in a collectivity-only world (no department
  residence) the L. 755-22 award holds where its premises hold, the
  R. 755-14 status and the R. 755-14-1 exclusion stay silent, and
  which R543 provisions govern there is caller case input (upstream
  assessment) — this package concludes nothing for it.
- B-PFARS-INSCRIPTION: enrolment is fund-asserted per the R. 543-4
  presumption (contested and post-sanction justification cases arrive
  as absent input).
- B-PFARS-MOIS-DROIT: rentree calendar mechanics assumed; cutoff dates
  arrive fund-stated and the `AGE_ATTEINT` deadline policy as case
  input.
- Q-PFARS-1 (open, blind): the L. 543-1 para. 2 "undetermined age" is
  read as the R. 543-2 six-year line (blind probe PFARS-B-05,
  BLIND_PENDING).
- Q-PFARS-DOM-1 (open): L. 755-22 / R. 755-14 / R. 755-14-1 name no
  resident; adopted: the allocataire parent's residence anchors the
  DOM case, collectivity and department facts stated independently.
  The child's-residence and either-party readings await the
  independent second reading.
- Q-PFARS-DOM-2 (superseded by the D76 return): "collectivités"
  (L. 755-22) and "départements" (R. 755-14, R. 755-14-1) are two
  source classes with two independent residence facts; the one-scope
  reading is withdrawn.
- DSS_PENDING: euro BMAF, decree nominals and the reference-year
  assessment await the DSS pricelist; BLIND_PENDING: Q-PFARS-1 and the
  standalone-differential reading await the second model.
