# Foreign benchmarks report — `fr.css.prime_activite`

Benchmarks are expectations, never semantic sources. Euro bases below are
the retained case inputs of each scenario (B-PPA-MONTANT-EURO); resource
bases are fed as retained monthly facts (B-PPA-RESSOURCES-CALCUL); SMIC
rates are retained monthly facts. Only the computation structure (scales,
fraction, bonification bands, trimestre window, floor) is asserted.

Classes: (a) exact structure match under the stated assumptions;
(b) structure match with documented input shaping the benchmark leaves
open; (c) genuine divergence between the benchmark outcome and the adopted
text reading, recorded with a BOUNDARY marker and evidence.

## IT-2026-080 (CNAF instruction, thresholds from the plan/registry)

| # | Their figure | Our answer | Class |
|---|--------------|------------|-------|
| 1 | bonification zero at 709.18 | 59 x 12.02 = 709.18: BoniNulle2026 fires at the edge (`rev <= smic * 59.0`); monthly prime 355.26423 | (a) |
| 2 | plateau from 1442.40 (old scale) | 120 x 12.02 = 1442.40: pre-2026 cap edge (BoniMaxPre2026, 29.101 %); post-2026 the scale runs linear to 138x | (a) |
| 3 | bonification capped at 1658.76 | 138 x 12.02 = 1658.76: BoniMax2026 fires at the edge (`rev >= smic * 138.0`), cap 0.377 x base; monthly prime 215.28786 | (a) |

The three circulaire thresholds factorise exactly over the 2026 hourly
SMIC (12.02) into the D. 843-2 statutory multiples (59/120/138). The text
is pinned since 2026-10-06 (source CNAF_IT_2026_080, fragments BORNES /
MONTANTS / SORTIE); the seuils scenario is document-anchored. The
quarter-mapping table («trimestre ressources → trimestre droit») stays
unmodelled — R842-2 timing is PENDING_WAVE.

[`seuils-it-2026-080.lawtest`](seuils-it-2026-080.lawtest) pins cases 1
and 3 as the `fr.css.prime_activite#foreign` family (monthly primes at
the band edges, new wording).

## OpenFisca

No OpenFisca import: benchmark runs are out of the laptop scope, and no
OF prime_activite case file was pinned. Structure coverage of the
L. 842-3 formula (forfait + fraction + bonifications − resources,
trimestre average, payment floor) is carried by the authored `montant`
family instead. Revisit when an OF yaml is pinned as input.
