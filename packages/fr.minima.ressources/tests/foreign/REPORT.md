# Foreign benchmarks report — `fr.minima.ressources`

Benchmarks (OpenFisca-France `rsa_base_ressources.yaml`, LexImpact
2024 `rsa_*.yml` base rows) are expectations, never semantic sources.
The quarterly DSN-prefill machinery (R.262-7 post-2025-03) has no
foreign program: it is covered by the package's own scenarios. Euro
rows below use the stated base components; only structure (averages,
perception-month allocation, capped aid, category counting) is
asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open (base components, fiscal annualization);
(c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

| # | Their case | Our answer | Class |
|---|------------|------------|-------|
| 1 | rsa_01 base 100.33 (Jan–Mar) → 104.95 (Apr–Dec): inactif parent, no own resources | declared averages plus perception-month benefits (R.262-7, II 3°); component shaping (ARS slices and al.) is upstream | (b) component shaping |
| 2 | rsa_02 base 365.33 → 369.95 = row 1 + 265.00 ARE each month | unemployment income joins the base (Chomage lane, R.262-12/13) | (a) ARE in base |
| 3 | rsa_base_ressources ×2 (2016): 2EE/2DC counted once (2000/month); plus-values counted (12000) | single `CompteCapital` rule counts each declared capital euro once (R.262-6 upstream valuation) | (b) fiscal annualization upstream |
| 4 | their `rsa_base_ressources` excludes housing; the flat-rate is added separately in their `rsa_revenu` | our `base_ressources_mois` includes the capped aid / in-kind flat-rate directly (R.262-7, II 3° + R.262-9/R.262-10) | (c) shape, same euros |

Notes.

- 1–2: the April base step (+4.62) is a resource change, not a rule
  change; the package takes monthly components as inputs, so the
  step is (b) while the averaging/allocation around it is (a).
- 4: the shape difference is deliberate and text-driven: R.262-7,
  II 3° counts housing aid "à hauteur" of the flat-rate inside the
  base itself. The LexImpact rows 1–2 reconcile exactly through our
  base only together with the separately added flat-rate
  (e.g. 911.62 − 100.33 − 145.86 = 665.43), which is the
  pre-2025-03 regime both programs share for 2024.
- No foreign program models the 2025-03-01 reform (M-4…M-2 window,
  DSN prefill blocks, fund totals): the reform date-pair scenarios
  (`trimestre-2025-02-ancien`, `trimestre-2025-03-nouveau`) stand in
  for benchmarks here.
