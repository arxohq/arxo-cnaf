# `fr.css.ajpa` — daily carer allowance (allocation journalière du proche aidant)

Executable formalization of the AJPA core: the right opened by carer
leave plus stable residence in France (L. 168-8), the monthly maximum
(2025+), the 66-day career cap (2021–2025, bareme) and the renewable
duration ceiling (2025+) (L. 168-9), monthly totals at the retained daily
rate with the single-carer majoration to 2023-07 and split/part-time
modulation (L. 168-9), the ten non-cumulation items in two generations
with the part-time sick exception plus the employed-by-the-aided-person
exclusion (L. 168-10), the fund payment duty (L. 168-8, L. 168-11, D1),
the undue-payment recovery duty (L. 168-13, D2), the two statutory
recovery-by-withholding powers (L. 168-13, P1 on the four listed
benefit targets / P2) and the recourse information duty (L. 168-14,
D3).

Scope: exactly 9 articles (L168-8..16). Pre-2021 texts (the 2019 L168-8
extended channel, the 2019 L168-11 service text) and the stillborn L168-9
version are unpinned boundaries (B-PFAJPA-AVANT2021). Decree mechanics
(daily SMIC euro figure, monthly max days, duration ceiling, recovery
instalments) arrive as case inputs with provenance (B-PFAJPA-D168).

## Measure

`law audit .` (formalization measure, static profile): 15 rules, dangling
premises 0, one-way premises 2 of 15. Form catalog: 16 detectors,
1 finding: `evaluative-fact-without-producer` → `indu_ajpa` — disposition
accepted: the undue-payment character is established by the paying body's
finding (L. 168-13 «paiement indu ... constaté»); all tests assert it with
origin `adjudicated` (§73 channel, DECISION-0194). Measure not taken on 7
publications without presented text (pre-coverage editions).

## Their case to our answer

No OpenFisca AJPA model or parameters exist upstream: the DSS/CNAF texts
and blind reading are the basis, never regressions. Full table:

[`tests/foreign/REPORT.md`](tests/foreign/REPORT.md) (text-direct
readings with pinned fragments; classes (a)/ГРАНИЦА per reading).
