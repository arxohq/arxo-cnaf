# fr.pf.core

Shared family-benefit rules

> Independent demonstration model. It is not an implementation by or
> for an authority and does not establish legal accuracy or completeness.
> For a real case, rely on the official texts and competent bodies.

## Package snapshot

| Item | Value |
|---|---|
| Version | `0.1.0` |
| Namespace | `urn:fr:corpus:clir:pf-core` |
| Semantics | `law.core/0.2.11` |
| Dependencies | `fr.travail.smic` |

## Run an example

Install the CLI as described in the [repository README](../../README.md).
From the repository root:

```sh
cd packages/fr.pf.core
law test . --file tests/enfant-charge-20-ans-salaire-sous-plafond.lawtest --json
```

Success checks the declared expectations of the model; it does not certify
that the model covers the whole benefit or every possible case.

## Scope and inputs

The executable scope is defined by the rules and declared scenarios in this
snapshot. Each rule has its own dates, prerequisites and source anchors.
Use the supplied facts and any explicitly selected readings of the scenario;
do not infer wider coverage from the subject named above.

The package author records these limitations (retained from
[package-info.json](package-info.json)):

- Rules are filed for 712 of 973 pinned fragments: the rest are pinned by publication bytes but carry no executable norms. The absence of a card means «no norm in the model», not «the law is silent».
- 4 package conclusions are left without executable witness: their premises contain a disjunction, a text value or a term call, or the head is computed. Such conclusions are recorded in internal and will become cards together with hand-written scenarios.
- 2 package norms are confirmed only by a negative scenario («on these facts the position does not arise»): the generating pass could not build a world that activates them. The positive witness is a debt.
- Time limits are computed by §86 terms: the case must carry a counting policy (ENFANT_VINGT_ANS, PRESCRIPTION_ANNEES, RECOUVREMENT_DELAI), a §85 calendar snapshot and the calendar package itself in the program, otherwise the document answers MISSING_CALENDAR or MISSING_POLICY.

| Inspect | What it contains |
|---|---|
| [law.toml](law.toml) | Package identity, dependencies and declared scenario groups |
| [law.lock](law.lock) | Exact dependency, semantics and resource pins |
| [tests/](tests/) | Declared scenarios and their fixtures |
| [sources/](sources/) | Captured source material; individual reproduction terms apply |
| [deps/](deps/) | Pinned dependency bytes |
| [i18n/](i18n/) | Labels and translations |
| [01-sources.law](01-sources.law) | Model declarations and source references |

## Reproduction and rights

See the [repository instructions](../../README.md) for rebuilding
a source package and restoring any withheld sources. The [repository licence](../../LICENSE)
covers the model code; captured publisher texts keep their own terms in
[NOTICE](../../NOTICE) and [package-info.json](package-info.json).
