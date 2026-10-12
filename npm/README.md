# @arxo/canon-fr-benefits

**Load a pinned French benefit model in Node.js. Ask it through `@arxo/law`
and retain the answer, its proof, sources and hashes.**

[Explore the browser lab](https://french-benefits.law.arxo.io/) ·
[Model sources](https://github.com/arxohq/arxo-cnaf) ·
[Book and case files](https://github.com/arxohq/law-as-code-france-examples)

> **First of all, a demonstration.** These are independent models of published
> French benefit law for teaching and demonstration. They do not claim legal
> accuracy or completeness, are not an implementation by or for the Cnaf or
> any French authority, and their answers are not legal advice.

## Quick start

Node.js 20 or later. This release is checked with `@arxo/law` 0.4.2 and its
pinned `@arxo/law-engine` 0.5.2. The npm package contains data and a loader;
execution remains in the common WebAssembly engine.

```sh
npm install @arxo/law@0.4.2 @arxo/canon-fr-benefits@0.1.0
```

Save this as `example.mjs`, then run `node example.mjs`:

```js
import { open } from '@arxo/law';
import { loadModel } from '@arxo/canon-fr-benefits/apl';
import { household, caseInput } from '@arxo/canon-fr-benefits/examples/apl';

const model = await loadModel();
const apl = await open(model.spec, {
  offline: true,
  local: { packages: { [model.spec]: model.package } },
});

const answer = await apl.collect(
  'aide_formule', [household, '?amount'], caseInput,
);
console.log(answer.evaluationStatus); // COMPUTED
console.log(answer.value[0].value);   // '20.17'
console.log(answer.value[0].currency); // 'EUR'
console.log(answer.hashes.result);    // full SHA-256
```

This is the existing technical zero-rent probe dated 15 June 2024: one person,
no dependants, supplied resources of €4,000, zone II in metropolitan France.
The exported `caseInput` contains all 12 supplied facts and explicitly selects
`PpPlancherFinal`. The result is an exact **formula amount**, not a final
payable benefit or a realistic aid claim. The full input is shipped as `examples/apl-case.json` and corresponds to the
[declared scenario](https://github.com/arxohq/arxo-cnaf/blob/f2efcc6788465484f145146a3ed5f76b13d41703/packages/fr.apl/tests/finish-lecture-pp.lawtest).
Copy it and replace the facts with those of your own fictional case.

## Choose a model

The root export provides a lightweight catalog and a loader taking an exact
model spec. It does not read any model world at import time.

```js
import { models, loadModel } from '@arxo/canon-fr-benefits';

console.log(models.map(model => model.spec));
const model = await loadModel('fr.pf.af@0.1.0');
```

Each model also has an addressable export:

| Subject | Subpath | Model |
|---|---|---|
| Housing aid | `/apl` | `fr.apl@0.1.0` |
| Housing payment stage | `/apl-versement` | `fr.apl.versement@0.1.0` |
| Housing resources | `/income-for-apl` | `fr.tax.income_for_apl@0.1.0` |
| Family allowances | `/af` | `fr.pf.af@0.1.0` |
| Early childhood | `/paje` | `fr.pf.paje@0.1.0` |
| Childcare | `/cmg` | `fr.pf.cmg@0.1.0` |
| Family supplement | `/cf` | `fr.pf.cf@0.1.0` |
| School allowance | `/ars` | `fr.pf.ars@0.1.0` |
| Family support | `/asf` | `fr.pf.asf@0.1.0` |
| Adult disability | `/aah` | `fr.css.aah@0.1.0` |
| Disabled-child allowance | `/aeeh` | `fr.pf.aeeh@0.1.0` |
| Parental presence | `/ajpp` | `fr.pf.ajpp@0.1.0` |
| Caregiver allowance | `/ajpa` | `fr.css.ajpa@0.1.0` |
| Minimum income | `/rsa` | `fr.casf.rsa@0.1.0` |
| Activity bonus | `/prime-activite` | `fr.css.prime_activite@0.1.0` |
| Minimum-income resources | `/minima-ressources` | `fr.minima.ressources@0.1.0` |
| Family foundations | `/core` | `fr.pf.core@0.1.0` |
| Payments and recovery | `/versement` | `fr.prestations.versement@0.1.0` |
| Revaluation | `/revalorisation` | `fr.css.revalorisation@0.1.0` |
| Social-security ceiling | `/pass` | `fr.css.pass@0.1.0` |
| Minimum wage | `/smic` | `fr.travail.smic@0.1.0` |

Opening one model reads and parses only that world's bytes and its referenced
question catalog, if any. Installing this single npm package downloads the
whole archive. Models are not combined into a universal household calculation.

## What `loadModel` returns

| Field | Meaning |
|---|---|
| `spec` | Exact model name and version |
| `package` | `{ ir, meta }`, ready for `open(spec, { local: { packages } })` |
| `descriptor` | Original registry descriptor; its `contentHash` is the package CLIR hash |
| `pin` | Public source revision, world hash, model hash and semantics |
| `questionCatalog` | Original hash-checked catalog when the descriptor names one |

The loader checks the raw world bytes against `worldHash` **before** parsing
JSON. Its facade metadata uses the world hash as `meta.contentHash` and the
package hash as `meta.packageContentHash`. Those identities remain separate.

Unknown or versionless specs throw `ModelNotFoundError`; missing, altered or
unreadable assets throw `ModelIntegrityError`. There is no network fallback.
Each call returns a fresh parsed world; caller mutations are not shared with
later loads. Reuse an opened model for multiple cases rather than reopening it
for each request. Long-running workers should keep a bounded set of open models;
this loader does not introduce a program pool or change the facade's lifecycle.

## Ask, inspect and retain evidence

The returned model uses the existing `@arxo/law` API: `collect`, `truth`,
`positions`, `whyNot` and `unfold`. Handle `evaluationStatus` before using an
amount. Missing facts are not automatically zero or false; a request may
require additional inputs, a human finding or an explicit interpretation.

```js
console.log(apl.unfold('aide_formule', { depth: 2 }).text);

import { writeFile } from 'node:fs/promises';
await writeFile('answer.json', answer.document);
```

The APL example gives different formula amounts under explicit readings:

| Input choice | Evaluation status | Formula amount |
|---|---|---|
| `PpPlancherFinal` | `COMPUTED` | €20.17 |
| `PpLitteral` | `COMPUTED` | €53.7338 |
| No selected interpretation | `INTERPRETATION_REQUIRED` | no amount |

Set the selection in `caseInput.options.selectedInterpretations` using the
full model identifier, e.g. `urn:fr:corpus:clir:apl#PpLitteral`.
Money and Decimal inputs are strings (`'4000 EUR'`, `'0.0283'`). The facade
checks fact names, arity and values at runtime. Generated TypeScript declarations
constrain model specs and queried relation names; they do not replace runtime
checking of the general `CaseInput.answers` array. For strict TypeScript consumers,
include `ESNext.Disposable` alongside your usual `ES2022` and `DOM` libs;
the engine declarations expose an optional disposal symbol.

## Snapshot and verification

21 source models, with their already-linked dependency worlds, from the
[public 12 October 2026 canon export](https://github.com/arxohq/arxo-cnaf/tree/f2efcc6788465484f145146a3ed5f76b13d41703),
semantics `law.core/0.2.11`. The source pin identifies every shipped source asset.
The npm version, model versions and legal date are independent.

This first Node.js release has targeted delivery checks. Full corpus acceptance
is **not checked** (`releaseVerified: false`, corpus `not_checked`). Recorded
canon checks are separate from npm/WASM compatibility and do not certify legal
accuracy or completeness. Browser integration is outside this release's contract.

## Rights

Code and models: Apache-2.0 (`LICENSE`). Captured publisher material keeps its
own terms in `NOTICE`. The source files listed in `WITHHELD.json` are not included;
addresses and hashes remain available in that metadata. This package ships the
same public compiled model and world bytes as the canon registry.

Maintainer: Rifat Dzhumagulov · [hi@arxo.io](mailto:hi@arxo.io).
