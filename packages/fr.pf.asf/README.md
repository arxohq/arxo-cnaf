# `fr.pf.asf` — allocation de soutien familial (ASF)

Executable formalization of the family support allowance: per-child
eligibility by opening ground (L. 523-1, R. 523-1, R. 523-2; orphanhood
opens without carence, default and partial-pension grounds open once the
one-month default period has run, every track upon request), couple
cessation (L. 523-2, R. 523-4/5/6), the single and double rates
(L. 523-3, R. 523-7; 0.2813/0.375 in the 2021 window, 0.422/0.5625 from
2022-11-01) with the standalone partial-pension differential (L. 523-1
4°), continuation and the fourth-month control (R. 523-3, R. 523-3-1/2,
D. 523-2), opening-date confirmation (R. 523-1, D. 523-1/2), and the fund
payment and quarterly-control duties.

Scope: exactly 19 CSS articles (L523-1, L523-2, L523-3, R523-1, R523-2,
R523-3, R523-3-1, R523-3-2, R523-4, R523-5, R523-6, R523-7, R523-8,
D523-1, D523-2, D523-3; DOM extension L755-17, D755-7, D755-8).
Upstream premises (child in care, opener status,
debtor body) are read from `fr.pf.core`, never re-concluded here. Own
predecessor pins (D-15): the L523-1 predecessor text (2019–2021,
`CSS_L523_1_PREV`) and the R523-7 pre-2022 rate row stand in this
package's `@source` lists; `fr.pf.core` is untouched. Coverage from
2021-01-01 (D-01); producers effective `[@2021-01-01, infinity)` except
the pre-2022 double-default opener (`[@2021-01-01, @2022-11-01)`) and
its post-2022 full-rate amount (`[@2022-11-01, infinity)`).

DOM extension (FINISH transfer, `08-dom.law`, nochecks authoring): L. 755-17
grants the ASF in the six L. 751-1 collectivities on the parent in
charge, the eligible child and the collectivity residence (L. 755-17
alone); the generic D. 755-8 rate parity and the D. 755-7 department
applicability (R. 523-1..6, R. 523-8, D. 523-3 in L. 751-1 departments
only, on department residence with provenance) are independent branches
that do not gate the award (RETURN04 award/parity split, D76 territory
split). Three thin link statuses (`asf_attribuee_dom`,
`asf_metro_applicable_dom`, `asf_taux_parite_dom`) read the untouched
metro computation; no metro rule is duplicated or gated on territory.
Adopted readings: the allocataire parent's residence anchors the case,
collectivity and department facts stated independently (Q-PFASF-DOM-1);
"collectivités" vs "départements" are two source classes
(Q-PFASF-DOM-2 superseded by the D76 return). Source outputs for the
three articles are GENERATED_OUTPUT_PENDING (`build_sources.py --write`
in the deferred queue). Measure counts below predate the transfer;
re-measure at the deferred run.

## Measure

`law audit .` (formalization measure, static profile): 20 rules. Form
catalog: 16 detectors, 7 findings, all
`strict-reader-of-foreign-defeasible-head` — the five ground openers,
the standalone differential and the cessation rule, which read the
upstream `parent_charge` / `enfant_ouvre_droit` heads, whose producers
are defeasible in `fr.pf.core`. Same detector as the ARS control (2
findings on its openers): the documented package split, not a defect.

## Their case to our answer

Foreign benchmarks are expectations, never sources. Euro totals use
the stated illustrative BMAF 400.00 EUR; track rates come from the
pinned R. 523-7 rows. Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (OpenFisca
`tests/formulas/asf`: 2018-07 seuil, 2015, 2018-04 Cas 1–3; classes
(a)/(b)/(c) per case).

Reading guide:

- Track selection matches on all paying cases under the stated
  assumptions (b): single rate where their totals are 96/115.87, the
  differential shape where theirs is 65.87 (= 115.87 − 50).
- The 2018-04 trio confirms the adopted ground shaping (lone-parent
  benchmarks read as single default with carence) and the 4°
  mechanics (allowance − pension).
- One genuine divergence (c): their seuil 0 vs our 0.52 — the 15 EUR
  floor their engine folds and ours documents (B-PFASF-SEUIL).
- The age-bar benchmark is upstream shaping (b): their
  `asf_elig_enfant` false withholds the opener; ASF per se carries no
  age bar.
- Benchmark periods are shaped to 2021 throughout (D-01/D-15): the
  2015/2018/2020 runs cannot execute against 2021-effective
  producers.

## Boundaries

- B-PFASF-BMAF: euro totals rest on the stated illustrative BMAF
  400.00 EUR (unpinned arrete → stated-assumption input).
- B-PFASF-SEUIL: the 15 EUR non-payment floor (D. 523-3) operates on
  the household total, which the engine cannot fold; small
  differentials below it are a documented divergence, never a
  source (blind probe PFASF-B-12, class (c) port
  `of-seuil-non-versement`).
- B-PFASF-RSA: the RSA plein-droit opener (L. 523-1 1° IV) is an
  upstream assessment; the package concludes nothing for it (blind
  probe PFASF-B-06).
- B-PFASF-SUBROGATION: subrogation and recovery procedure (R. 523-8)
  are inter-organisation mechanics, out of scope (blind probe
  PFASF-B-21).
- B-PFASF-D755-7-R581: D. 755-7 also declares R. 581-1..10 applicable
  in the DOM. R. 581-1 and R. 581-3..10 are authored in
  `fr.pf.maintenance` this round; their static review and
  publication/liaison remain pending. R. 581-2 content is separately
  scoped. The boundary is a provisional maintenance
  liaison/publication dependency, not an absent owner or absent
  source. The applicability status covers R. 523-1..6, R. 523-8 and
  D. 523-3 only, with the exclusion in its label; norms unchanged.
- B-PFASF-DOM-L751-1: the L. 751-1 enumeration (which collectivities /
  departments) is not pinned here; residence arrives as two
  independent fund-stated inputs, `residence_dom` (collectivity,
  L. 755-17 + D. 755-8) and `residence_departement_dom` (department,
  D. 755-7), neither implying the other. Liaison to the `fr.pf.dom`
  territory vocabulary requested once that package is accepted.
- B-PFASF-DOM-HORS-DEPT: in a collectivity-only world (no department
  residence) the L. 755-17 award holds where its premises hold, the
  D. 755-7 status stays silent, and which R523/D523 provisions govern
  there is caller case input (upstream assessment) — this package
  concludes nothing for it.
- B-PFASF-TRIMESTRE: the quarterly cadence of the fund's control
  (R. 523-3-1, title one month per quarter) is an adopted DSS
  reading; the control duty runs on `CONTROLE_TRIMESTRIEL` (blind
  probe PFASF-B-17).
- B-PFASF-DATES: R. 523-4/R. 523-5/R. 523-6 cessation and cadence
  dates arrive through the two fund-stated month inputs; calendar
  month mechanics (first-of-month) assumed, `PAIEMENT_MENSUEL` /
  `CONTROLE_TRIMESTRIEL` deadline policies arrive as case input
  (blind probe PFASF-B-19).
- Q-PFASF-1 (open, blind): the pre-2022 double default (5°) is
  folded to the double rate with the same effect as the
  orphan-of-both rate in the 2021 window, and to the full rate from
  2022-11-01; the distinct-track reading awaits the blind second
  reading (`analysis/blind-read-cases.json` PFASF-B-01/B-07,
  BLIND_PENDING).
- Q-PFASF-2 (open, blind): the 4° differential is a standalone
  track — it requires neither the opened right nor the request,
  computing from the maintenance facts alone; the
  request-gated reading awaits the blind second reading (probes
  PFASF-B-02, unit `asf-differentiel-sans-demande`).
- Q-PFASF-DOM-1 (open): L. 755-17 / D. 755-7 / D. 755-8 name no
  resident; adopted: the allocataire parent's residence anchors the
  DOM case, collectivity and department facts stated independently.
  The child's-residence and either-party readings await the
  independent second reading.
- Q-PFASF-DOM-2 (superseded by the D76 return): "collectivités"
  (L. 755-17, D. 755-8) and "départements" (D. 755-7) are two source
  classes with two independent residence facts; the one-scope reading
  is withdrawn.
- DSS_PENDING: euro BMAF, the L523-1 IV control regulation and the
  quarterly title cadence await the DSS pricelist; BLIND_PENDING:
  Q-PFASF-1 and Q-PFASF-2 await the second model.
