# arxo-cnaf

> **First of all, a demonstration.** This repository shows what modelling legislation with Arxo can do:
> French family-benefit law written as executable canons, with the source of every answer. It is an
> independent model built from published French law for teaching and demonstration. It does not claim
> legal accuracy or completeness, it is not an implementation by or for the Cnaf or any French
> authority, and its answers are not legal advice. For a real file, rely on the official texts and the
> competent bodies.

Pinned canon, executable as it stands: source text with provenance, the
model built over it and the scenarios that check its answers. The norms
here are data — they are executed by `law`; this repository carries no
rule code of its own.

## Contents

| Package | Version | Scenarios | Dependencies |
|---|---|---|---|
| `fr.css.aah` | 0.1.0 | 70 | 0 |
| `fr.css.pass` | 0.1.0 | 26 | 0 |
| `fr.css.prime_activite` | 0.1.0 | 201 | 0 |
| `fr.css.revalorisation` | 0.1.0 | 12 | 0 |
| `fr.minima.ressources` | 0.1.0 | 31 | 0 |
| `fr.pf.paje` | 0.1.0 | 87 | 0 |
| `fr.tax.income_for_apl` | 0.1.0 | 3 | 0 |
| `fr.travail.smic` | 0.1.0 | 80 | 0 |
| `fr.apl` | 0.1.0 | 406 | 1 |
| `fr.casf.rsa` | 0.1.0 | 133 | 1 |
| `fr.pf.core` | 0.1.0 | 326 | 1 |
| `fr.apl.versement` | 0.1.0 | 11 | 2 |
| `fr.css.ajpa` | 0.1.0 | 44 | 2 |
| `fr.pf.aeeh` | 0.1.0 | 50 | 2 |
| `fr.pf.af` | 0.1.0 | 73 | 2 |
| `fr.pf.ajpp` | 0.1.0 | 91 | 2 |
| `fr.pf.ars` | 0.1.0 | 26 | 2 |
| `fr.pf.asf` | 0.1.0 | 36 | 2 |
| `fr.pf.cf` | 0.1.0 | 96 | 3 |
| `fr.pf.cmg` | 0.1.0 | 45 | 2 |
| `fr.prestations.versement` | 0.1.0 | 138 | 19 |

## How it is verified

Every package is built by `package.py` with the pinned toolchain: compilation,
§267 scenarios on both evaluators, replay of saved evaluations and a rebuild
from the release itself. A failure of any step stops the build.

```sh
python3 tools/toolchain.py download --lock toolchain.lock.json --out /tmp/law-tools
python3 /tmp/law-tools/package.py packages/<name> \
    --lawc /tmp/law-tools/law-cli --offline --out /tmp/<name>-release
```

## Dependencies

Dependency bytes are pinned under `packages/<name>/deps/` and verified against the hash recorded in `law.lock`: the build and the CI are offline.

## Sources not redistributed here

The terms of www.caf.fr do not allow republishing, so 4 pinned files
(`fr.css.prime_activite`, `fr.pf.af`) are not in this repository: their address and sha256 stay in `sources.law`,
and `WITHHELD.json` lists them. Before building those packages:

```sh
python3 tools/fetch_withheld.py
```

The script downloads each file from its address and checks the sha256; a text
extracted from a PDF is rebuilt with `pdftotext -layout` (poppler). Case packages
install from `registry/` without them.

## Installing from this repository

`registry/` publishes these packages and their closure (22) in the
layout of the Arxo registry: descriptors, canonical CLIR bytes (§208), worlds and
resources. A case package whose `law.lock` pins them installs from a clone:

```sh
law install --registry arxo=<path to the clone>/registry
```

The sources are `packages/<name>/`; the registry copy does not repeat them.
`python3 registry/check_registry.py` verifies schemas, addresses and hashes.

## Rights

Code and model: see `LICENSE`. The pinned texts of the publishers keep their
own terms of reproduction, listed per package in `NOTICE`; those terms are
not covered by the code licence.

Maintainer: Rifat Dzhumagulov (hi@arxo.io). Address: https://github.com/arxohq/arxo-cnaf.

## Status

Published with *Law as Code in Practice: French Family Benefits* (Law as Code by Country · Volume 1,
https://books.arxo.io). These canons were exported on 12 October 2026 from the Arxo repository at commit
`7206473829`, with every scenario passing (1,985) on `law` 0.2.1 (`law.core/0.2.11`); the book's
reproduction kit was checked with the released `law` 0.2.2 (`npm i -g @arxo/cli`). The book's case
packages are in [`arxohq/law-as-code-france-examples`](https://github.com/arxohq/law-as-code-france-examples)
and install from `registry/` here. The canon scenarios of the book run in place, for example:

```sh
cd packages/fr.apl
law test . --file tests/finish-lecture-pp.lawtest --json
```

The `packages` workflow builds every package on each push with `law-package-tools` 0.3.0, pinned in
`toolchain.lock.json` and mirrored in this repository's releases: compilation, scenarios, replay of saved
evaluations and a rebuild from the release, after restoring the sources listed in `WITHHELD.json`. The
`registry` workflow checks `registry/` (schema, addresses and hashes).
