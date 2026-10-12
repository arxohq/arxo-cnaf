# arxo-cnaf

Explore French benefit rules as executable models, and trace their answers
back to published legal sources.

**[Explore the demo](https://french-benefits.law.arxo.io/)** ·
**[Run an example](#quick-start)** ·
**[Read the book](https://books.arxo.io/)**

> **First of all, a demonstration.** This repository shows what modelling legislation with Arxo can do:
> French family-benefit law written as executable canons, with the source of every answer. It is an
> independent model built from published French law for teaching and demonstration. It does not claim
> legal accuracy or completeness, it is not an implementation by or for the Cnaf or any French
> authority, and its answers are not legal advice. For a real file, rely on the official texts and the
> competent bodies.

## Choose your starting point

| I want to… | Start here |
|---|---|
| Explore saved cases and their sources in a browser | [French Benefits Lab](https://french-benefits.law.arxo.io/) — no installation |
| Run a scenario on my machine | [Quick start](#quick-start) |
| Find the model for a benefit | [Browse the models](#browse-the-models) |
| Reproduce a chapter of the book | [Book examples](https://github.com/arxohq/law-as-code-france-examples#readme) |
| Rebuild a package or check the registry | [Reproducibility guide](docs/reproducibility.md) |

[![French Benefits Lab overview: saved family-allowance cases for March and April 2026, with links to their evidence.](docs/images/french-benefits-lab.jpg)](https://french-benefits.law.arxo.io/)

*French Benefits Lab, captured on 12 October 2026. Open the demo and choose
“Explore a saved family case” to inspect its inputs, answer and French sources.
The lab presents its own recorded evidence release; its coverage and version
are separate from this repository's export.*

## Quick start

You need **Git, Node.js 20+ and npm**. This example uses the released
**`law` 0.2.2** command-line tool, which executes the models. The package
already includes its pinned dependency; no Python, source restoration or
registry installation is needed for this scenario.

```sh
npm install -g @arxo/cli@0.2.2
law --version

git clone https://github.com/arxohq/arxo-cnaf.git
cd arxo-cnaf/packages/fr.apl

law test . --file tests/finish-lecture-pp.lawtest --json
```

This runs seven scenarios about the personal contribution in housing aid
(article D. 823-17). Success means the command exits with code `0` and the
JSON report records no failed scenarios. These are checks against the
model's declared expectations, not certification of legal accuracy.
The successful report includes these fields:

```json
{"ok": true, "passed": 7, "failed": 0, "notRun": 0, "total": 7}
```

**What to explore next:** open
[`finish-lecture-pp.lawtest`](packages/fr.apl/tests/finish-lecture-pp.lawtest).
The same supplied facts give €20.17 or €53.7338 under two selected readings;
without a selection, the model reports `INTERPRETATION_REQUIRED`. These are
an isolated zero-rent probe, not a realistic benefit claim. Follow the
calculation in [`02-calcul-locatif.law`](packages/fr.apl/02-calcul-locatif.law)
and its source declarations in
[`01-sources.law`](packages/fr.apl/01-sources.law).

Need help getting started? See [Troubleshooting](docs/reproducibility.md#troubleshooting).

## How to read a model

**Published text → executable rules → dated case facts → answer and evidence.**

A **canon** is a package containing a legal model, its source references and
checks. A **scenario** supplies facts, dates and any selected interpretation,
then states the expected answer. A **pinned source** is a captured publication
identified by its provenance and a content hash, so the model's input can be
checked later.

The rules are data in `.law` files, executed by `law`. This repository carries
no separate implementation of the benefit formulas in application code.
Models have individual scope and date boundaries; read a package's source
and scenarios before applying its answers to a different case.

## Browse the models

The export contains **21 source packages and 1,985 declared scenarios**.
The names below identify the subject of each model, not a claim of complete
coverage of that benefit. The [version and scenario inventory](docs/reproducibility.md#package-inventory)
records the exported package versions and dependency counts.

### Housing

| Subject | Model |
|---|---|
| Housing aid (APL / AL) | [`fr.apl`](packages/fr.apl/) |
| Housing-aid payment stage | [`fr.apl.versement`](packages/fr.apl.versement/) |
| Income used for housing aid | [`fr.tax.income_for_apl`](packages/fr.tax.income_for_apl/) |

### Family and children

| Subject | Model |
|---|---|
| Family allowances (AF) | [`fr.pf.af`](packages/fr.pf.af/) |
| Early-childhood benefits (PAJE) | [`fr.pf.paje`](packages/fr.pf.paje/) |
| Childcare supplement (CMG) | [`fr.pf.cmg`](packages/fr.pf.cmg/) |
| Family supplement (CF) | [`fr.pf.cf`](packages/fr.pf.cf/) |
| School-start allowance (ARS) | [`fr.pf.ars`](packages/fr.pf.ars/) |
| Family support allowance (ASF) | [`fr.pf.asf`](packages/fr.pf.asf/) |

### Disability and care

| Subject | Model |
|---|---|
| Adult disability allowance (AAH) | [`fr.css.aah`](packages/fr.css.aah/) |
| Disabled-child education allowance (AEEH) | [`fr.pf.aeeh`](packages/fr.pf.aeeh/) |
| Parental presence allowance (AJPP) | [`fr.pf.ajpp`](packages/fr.pf.ajpp/) |
| Caregiver allowance (AJPA) | [`fr.css.ajpa`](packages/fr.css.ajpa/) |

### Income support

| Subject | Model |
|---|---|
| Active solidarity income (RSA) | [`fr.casf.rsa`](packages/fr.casf.rsa/) |
| Activity bonus | [`fr.css.prime_activite`](packages/fr.css.prime_activite/) |
| Resources for minimum-income benefits | [`fr.minima.ressources`](packages/fr.minima.ressources/) |

### Shared rules and parameters

| Subject | Model |
|---|---|
| Family-benefit foundations | [`fr.pf.core`](packages/fr.pf.core/) |
| Benefit payments and debt recovery | [`fr.prestations.versement`](packages/fr.prestations.versement/) |
| Revaluation | [`fr.css.revalorisation`](packages/fr.css.revalorisation/) |
| Social-security ceiling (PASS) | [`fr.css.pass`](packages/fr.css.pass/) |
| Minimum wage (SMIC) | [`fr.travail.smic`](packages/fr.travail.smic/) |

## Find your way around the repository

| Path | What it contains |
|---|---|
| [`packages/`](packages/) | Model sources, captured texts, scenarios and pinned dependencies, one directory per canon |
| [`registry/`](registry/) | Installable publications and their dependency closure — 22 packages, including dependencies; not a duplicate of the source tree |
| [`tools/`](tools/) | Scripts to obtain the pinned build tools and restore withheld sources |
| [`packages.json`](packages.json) | Exported package versions, hashes, dependency lists and recorded scenario outcomes |
| [`toolchain.lock.json`](toolchain.lock.json) | Exact build-tool release and its SHA-256 |
| [`WITHHELD.json`](WITHHELD.json) | Addresses and hashes of source files that are not redistributed |

For a case package that consumes these canons, follow
[Install the book examples](docs/reproducibility.md#install-the-book-examples).
For compilation, scenario checks, replay and release rebuilds, follow
[Rebuild a source package](docs/reproducibility.md#rebuild-a-source-package).

## Release and verification

Published with *Law as Code in Practice: French Family Benefits*
(Law as Code by Country · Volume 1), available at [Arxo Books](https://books.arxo.io/).

The canons were exported on **12 October 2026** from Arxo commit
`7206473829`, with 1,985 scenarios passing on `law` 0.2.1
(`law.core/0.2.11`). The book's reproduction kit was checked with released
`law` 0.2.2. These are recorded execution results for this export.

The [packages workflow](.github/workflows/ci.yml) compiles each package,
runs its scenarios on both evaluators, replays saved evaluations and rebuilds
from the release using pinned `law-package-tools` 0.3.0. The
[registry workflow](.github/workflows/registry.yml) checks schemas, addresses
and hashes. See [the reproducibility guide](docs/reproducibility.md) for
requirements and commands.

## Rights and contact

Code and model: [Apache-2.0](LICENSE). Captured publisher texts retain their
own reproduction terms, listed per package in [NOTICE](NOTICE); the code
licence does not cover those texts. Some source files are
[withheld from redistribution](docs/reproducibility.md#restore-withheld-sources).

Maintainer: Rifat Dzhumagulov · [hi@arxo.io](mailto:hi@arxo.io).
