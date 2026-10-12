# fr.css.revalorisation

Benefit revaluation

> Independent demonstration model. It is not an implementation by or
> for an authority and does not establish legal accuracy or completeness.
> For a real case, rely on the official texts and competent bodies.

## Package snapshot

| Item | Value |
|---|---|
| Version | `0.1.0` |
| Namespace | `urn:fr:corpus:clir:revalorisation` |
| Semantics | `law.core/0.2.11` |
| Dependencies | None declared |

## Run an example

Install the CLI as described in the [repository README](../../README.md).
From the repository root:

```sh
cd packages/fr.css.revalorisation
law test . --file tests/bmaf-chaine-2016.lawtest --json
```

Success checks the declared expectations of the model; it does not certify
that the model covers the whole benefit or every possible case.

## Scope and inputs

The executable scope is defined by the rules and declared scenarios in this
snapshot. Each rule has its own dates, prerequisites and source anchors.
Use the supplied facts and any explicitly selected readings of the scenario;
do not infer wider coverage from the subject named above.

| Inspect | What it contains |
|---|---|
| [law.toml](law.toml) | Package identity, dependencies and declared scenario groups |
| [law.lock](law.lock) | Exact dependency, semantics and resource pins |
| [tests/](tests/) | Declared scenarios and their fixtures |
| [sources/](sources/) | Captured source material; individual reproduction terms apply |
| [i18n/](i18n/) | Labels and translations |
| [01-sources.law](01-sources.law) | Model declarations and source references |

## Reproduction and rights

See the [repository instructions](../../README.md) for rebuilding
a source package and restoring any withheld sources. The [repository licence](../../LICENSE)
covers the model code; captured publisher texts keep their own terms in
[NOTICE](../../NOTICE) and [package-info.json](package-info.json).
