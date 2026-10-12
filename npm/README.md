![French Benefits on Arxo — executable rules, traceable sources.](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/cover.png)

# @arxo/canon-fr-benefits

**Load a French benefit model. Supply a case. Keep the answer and its proof.**

21 pinned models for Node.js, from housing aid and family allowances to
minimum-income and disability benefits. Execute them locally through
[`@arxo/law`](https://www.npmjs.com/package/@arxo/law), with source anchors,
exact values and a canonical evaluation document.

**Node.js 20+** · **SDK 0.4.2** · **Apache-2.0**

[Quick start](#quick-start) · [Models](#choose-a-model) ·
[Evidence](#inspect-and-save-the-evidence) · [Troubleshooting](#troubleshooting)

[Explore the browser lab](https://french-benefits.law.arxo.io/) ·
[Model sources](https://github.com/arxohq/arxo-cnaf) ·
[Book and case files](https://github.com/arxohq/law-as-code-france-examples)

> **First of all, a demonstration.** These are independent models of published
> French benefit law for teaching and demonstration. They do not claim legal
> accuracy or completeness, are not an implementation by or for the Cnaf or
> any French authority, and their answers are not legal advice.

## Quick start

Install the canon alongside its checked SDK:

```sh
npm install @arxo/law@0.4.2 @arxo/canon-fr-benefits@0.1.1
```

Save as `example.mjs`, then run `node example.mjs`. The supplied example
includes the complete input, so you can get an answer before assembling a case.

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

console.log(answer.evaluationStatus);  // COMPUTED
console.log(answer.value[0].value);    // '20.17'
console.log(answer.value[0].currency); // 'EUR'
```

This is a **technical zero-rent probe**, dated 15 June 2024: one person,
no dependants, zone II in metropolitan France and supplied resources of
€4,000. All 12 facts and the `PpPlancherFinal` reading are explicit.
**€20.17 is a formula amount, separate from a final payable benefit.**

[Read the full input](https://github.com/arxohq/arxo-cnaf/blob/a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/examples/apl-case.json).
Copy it and replace the facts for your own fictional case. The fixture's
legal date and selected reading are part of that example, not application defaults.

## From a model to an answer

![loadModel supplies a selected hash-checked world with included imports. Explicit case facts, dates and reading enter the local SDK separately. The APL probe returns COMPUTED, 20.17 EUR and its document, proof, sources and hashes.](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/model-to-answer.svg)

`loadModel` reads the selected world and checks its original bytes.
`open` loads it into the common WebAssembly engine. Your facts, dates and
human choices arrive in `caseInput`; the canon supplies the rules.
Execution is offline after installation.

The explicit `local.packages` handoff is part of this package's API.
Installing this aggregator alone does not make `open('fr.apl@0.1.0')`
automatically discover its models.

## Choose a model

Start with the benefit you want to explore:

| Subject | Import from |
|---|---|
| Housing aid — APL | `@arxo/canon-fr-benefits/apl` |
| Family allowances — AF | `@arxo/canon-fr-benefits/af` |
| Minimum income — RSA | `@arxo/canon-fr-benefits/rsa` |
| Activity bonus | `@arxo/canon-fr-benefits/prime-activite` |
| Adult disability — AAH | `@arxo/canon-fr-benefits/aah` |

Every model subpath exports its pinned `spec` and a `loadModel()` function.
The root export provides the catalog and a loader for an **exact model spec**:

```js
import { models, loadModel } from '@arxo/canon-fr-benefits';

console.log(models.map(model => model.spec));
const model = await loadModel('fr.pf.af@0.1.0');
```

<details>
<summary>All 21 model exports</summary>

Append the subpath to `@arxo/canon-fr-benefits`:

| Subject | Subpath | Model spec |
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

</details>

Root import reads only the catalog and metadata. A load parses only the
selected world and its referenced question catalog, if any. Installation
gets the whole archive. The models are separate entry points; a combined
household calculation must be defined explicitly in the models and imports.

## Keep the reading explicit

The same APL input produces different formula amounts under the model's
explicit readings. Leaving the reading out asks for a choice instead of guessing:

![For the same supplied APL case: PpPlancherFinal gives COMPUTED, 20.17 EUR; PpLitteral gives COMPUTED, 53.7338 EUR; no selection gives INTERPRETATION_REQUIRED and no amount.](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/explicit-readings.svg)

Choose a different reading in a copy of the input:

```js
const literalCase = structuredClone(caseInput);
literalCase.options.selectedInterpretations = [
  'urn:fr:corpus:clir:apl#PpLitteral',
];
const literal = await apl.collect(
  'aide_formule', [household, '?amount'], literalCase,
);
console.log(literal.value[0].value); // '53.7338'
```

Use `caseInput.options.selectedInterpretations` and the full identifier.
Missing facts are not automatically zero or false. Handle `evaluationStatus`
before using a value; a request can require more inputs, a human finding or
an explicit interpretation.

## Inspect and save the evidence

Use the existing `@arxo/law` methods: `collect`, `truth`, `positions`,
`whyNot` and `unfold`.

| You want to… | Use |
|---|---|
| See the rules available behind a question | `apl.unfold('aide_formule', { depth: 2 }).text` |
| Inspect the proof of this case's answer | `answer.proof` |
| Follow the answer's source anchors | `answer.sources` |
| Retain the canonical evaluation document | `answer.document` |
| Record execution identities | `answer.hashes` |

```js
import { writeFile } from 'node:fs/promises';

console.log(apl.unfold('aide_formule', { depth: 2 }).text);
console.log(answer.proof.nodes.length); // 46 in the supplied example
await writeFile('answer.json', answer.document);
```

`unfold` describes available rules without selecting a case. The answer's
proof records what happened for the facts, dates and reading you supplied.

<details>
<summary>See the APL rule tree and source anchors</summary>

![Native depth-2 unfold tree of aide_formule: AideFormule depends on forfait_charges, loyer_eligible and participation_personnelle. Both contribution producers and their source anchors are visible; no case or reading is selected.](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/knows-apl.svg)

[Open the full tree](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/knows-apl.svg) ·
[Native JSON](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/apl-unfold.json) ·
[Recorded example outputs](https://cdn.jsdelivr.net/gh/arxohq/arxo-cnaf@a25fa8035e85b01a699f3b5ff4372996d2a29def/npm/assets/apl-example.json)

The tree includes every producer and premise returned at depth 2.
Source labels group repeated article locators; JSON keeps the versioned
anchors. Depth-limit markers are part of the engine's response.

</details>

## Troubleshooting

| Symptom or question | Next step |
|---|---|
| `ModelNotFoundError` | Pick a full `name@version` from `models`; versionless specs do not resolve. |
| `ModelIntegrityError` | Reinstall the exact package in a clean directory; altered or unreadable model assets refuse to load. |
| `open` cannot discover the model | Pass `model.package` through `local.packages`, as in Quick start. |
| `INTERPRETATION_REQUIRED` | Supply the reading deliberately in `options.selectedInterpretations`. |
| No amount is returned | Inspect status, issues and missing inputs; supply the facts or finding the model requests. |
| A Money or Decimal input is rejected | Use strings such as `'4000 EUR'` or `'0.0283'`; fact names, arity and values are checked at runtime. |
| Can I use it in a browser? | This package's current contract is Node.js 20+. Explore the separate browser lab for the recorded browser experience. |

<details>
<summary>TypeScript setup and runtime reuse</summary>

Declarations constrain exact model specs and queried relation names,
including qualified imports. They do not replace runtime validation of the
general `CaseInput.answers` array. For strict TypeScript, include:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022", "DOM", "ESNext.Disposable"],
    "strict": true
  }
}
```

`ESNext.Disposable` supplies the optional disposal symbol in the engine's
declarations. Reuse an opened model for several cases. Long-running workers
should keep a bounded set of open models; this loader adds no program pool
and does not change the facade's lifecycle.

</details>

<details>
<summary>Loader fields, pins and verification</summary>

| Field returned by `loadModel` | Meaning |
|---|---|
| `spec` | Exact model name and version |
| `package` | `{ ir, meta }` for the SDK's `local.packages` input |
| `descriptor` | Original registry descriptor; `contentHash` identifies package CLIR |
| `pin` | Source revision, world hash, model hash and semantics |
| `questionCatalog` | Hash-checked referenced catalog, when provided |

The loader verifies raw world bytes **before** JSON parsing and returns fresh
independent parsed worlds. It has no network fallback. Facade metadata uses
`meta.contentHash` for the **world hash** and `meta.packageContentHash` for the
**package hash**; the original descriptor remains separate.

The 21 source models and linked worlds come from
[the pinned public export](https://github.com/arxohq/arxo-cnaf/tree/f2efcc6788465484f145146a3ed5f76b13d41703),
semantics `law.core/0.2.11`. npm version, model version and legal date are
separate identities. SDK `0.4.2` pins engine `0.5.2`.

This release has targeted delivery checks. Full corpus acceptance remains
**not checked** (`releaseVerified: false`, corpus `not_checked`). Delivery
and SDK compatibility do not certify legal accuracy or completeness.

</details>

## Sources and further reading

[Source models](https://github.com/arxohq/arxo-cnaf) ·
[SDK API](https://www.npmjs.com/package/@arxo/law) ·
[Maintainer's publishing guide](https://github.com/arxohq/arxo-cnaf/blob/main/npm/PUBLISHING.md)

Code and models: Apache-2.0. Captured publisher material keeps its own terms
in `NOTICE`; files listed in `WITHHELD.json` are excluded, with addresses and
hashes preserved. This package ships the public compiled model and world bytes.

Maintainer: Rifat Dzhumagulov · [hi@arxo.io](mailto:hi@arxo.io).
