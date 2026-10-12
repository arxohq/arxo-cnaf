# Reproducibility guide

[← Back to the README](../README.md)

Choose the check you need. Running the README's first scenario, installing
a book case and rebuilding a release have different requirements.

| Task | Requirements |
|---|---|
| [Run the first scenario](../README.md#quick-start) | Git, Node.js 20+, npm, released `law` 0.2.2 |
| [Install a book case](#install-the-book-examples) | The same CLI and clones of both public repositories |
| [Rebuild a release](#rebuild-a-source-package) | Linux x86_64, Python 3.12+, GitHub CLI (`gh`), pinned toolchain and Python libraries below |
| [Restore withheld sources](#restore-withheld-sources) | Python 3; Poppler (`pdftotext`) for PDF text extraction; network access |

## Install the book examples

A case package holds a fictional file's facts and questions. Its `law.lock`
pins the canons by exact version and hash. Run this from the parent directory
of your `arxo-cnaf` clone, with `law` 0.2.2 installed as in the Quick start:

```sh
git clone https://github.com/arxohq/law-as-code-france-examples.git examples
cd examples/prime-naissance-moreau
law install --registry arxo=../../arxo-cnaf/registry
law test . --json
```

The registry contains published packages and their dependency closure (22)
in the Arxo registry layout: descriptors, canonical CLIR bytes, worlds and
resources. `law install` restores exactly what the case's lock pins and
checks the hashes; it does not select new versions. These case packages
install without the source files withheld from this repository.

See [the examples README](https://github.com/arxohq/law-as-code-france-examples#readme)
for saved questions, chapter mappings and replay instructions.

## Rebuild a source package

**The pinned build-tool release supports Linux x86_64 only.** The CLI used
in the Quick start is a separate installation route; it does not remove
this build-tool platform requirement.

Use Python 3.12+ and `gh` with access to this repository's Releases. The
following commands run from the `arxo-cnaf` repository root on Linux x86_64.
Use new output directories on a repeat run.

```sh
python3 -m venv .venv-reproduce
. .venv-reproduce/bin/activate
python3 -m pip install jsonschema fastjsonschema referencing

python3 tools/toolchain.py download \
    --lock toolchain.lock.json --out /tmp/law-tools
python3 /tmp/law-tools/package.py packages/fr.apl \
    --lawc /tmp/law-tools/law-cli --offline --out /tmp/fr-apl-release
```

The downloader obtains `law-package-tools` 0.3.0 from the release named in
[`toolchain.lock.json`](../toolchain.lock.json) and verifies its SHA-256.
Package checks cover compilation, declared scenarios on both evaluators,
replay of saved evaluations and a rebuild from the release itself. A failure
of any step stops the build. Passing establishes those execution checks,
not legal accuracy or completeness.

Dependencies are already captured under `packages/<name>/deps/`; their
bytes are checked against `law.lock`. The package build is offline after
the tools, Python libraries and required source files have been obtained.
For `fr.pf.af` or `fr.css.prime_activite`, first restore the withheld sources.

## Restore withheld sources

Four pinned files belonging to `fr.css.prime_activite` and `fr.pf.af` are not
redistributed because the publisher's reproduction terms do not permit it.
Their addresses and hashes remain in the source declarations and
[`WITHHELD.json`](../WITHHELD.json).

From the repository root, restore only the package you need:

```sh
python3 tools/fetch_withheld.py fr.pf.af
```

Use `fr.css.prime_activite` for the other affected package. A run without a
package argument restores all listed files. The script downloads from the
recorded addresses, checks each SHA-256, and refuses mismatched bytes.
PDF text is extracted using `pdftotext -layout` (Poppler) and checked too.
The recorded CI uses Poppler 24.02.

## Check the registry

From the repository root, with Python and `jsonschema` installed:

```sh
python3 registry/check_registry.py
```

This checks registry schemas, addresses and hashes. It is separate from
running source scenarios or rebuilding a source package.

## Reproduce the rule trees

The README diagrams are generated from the published APL world rather than
from a hand-written outline. From the repository root, use the released
`law` 0.2.2 CLI installed in the Quick start:

```sh
python3 tools/render_readme_trees.py --law law --check
```

The script checks the world's SHA-256 against its registry descriptor,
requests the two native `unfold` trees, and compares the JSON, native text,
manifest and SVG bytes without writing. Omit `--check` to regenerate them.
It requires no third-party Python libraries and evaluates no cases.

The underlying request for the first tree is:

```sh
law engine unfold registry/p/fr.apl/0.1.0/world.lawir.json aide_formule \
    --depth 2 --lang en --quote 0 --json
```

Use `droit_ouvert` for the second tree. The
[manifest](unfold/manifest.json) records the world hash, CLI fingerprint,
requests and response hashes. [JSON](unfold/aide-formule.json) retains all
versioned anchors; [native text](unfold/aide-formule.txt) retains the engine's
labels, including language fallbacks. The SVG displays names and grouped
article locators without inventing English labels.

These requests do not select a case, date or reading. The trees show all
returned producers at depth 2, including exception rules; they do not
establish which rule applied or whether a benefit is due.

## Troubleshooting

| Symptom | What to do |
|---|---|
| `law: command not found` | Run `npm install -g @arxo/cli@0.2.2`, ensure npm's global executable directory is on `PATH`, then check `law --version`. |
| npm reports an unsupported Node version | Install Node.js 20 or later, then repeat the CLI installation. |
| `this release supports Linux x86_64 only` | Run the pinned release rebuild on Linux x86_64. For the first scenario, use the npm CLI route in the README. |
| `gh` cannot download the release | Check that GitHub CLI is installed and can access this repository's Releases; authenticate if it requests it. |
| `the installation directory must be a new one` | Choose a fresh `--out` path for `tools/toolchain.py`; it refuses to overwrite an existing directory. |
| A required source file is missing in AF or the activity-bonus package | Run `python3 tools/fetch_withheld.py fr.pf.af` or `python3 tools/fetch_withheld.py fr.css.prime_activite` before building that package. |
| `pdftotext (poppler) is required` | Install Poppler, confirm `pdftotext` is on `PATH`, and repeat source restoration. |
| A restored file's hash differs from the pin | Confirm the Poppler version for extracted text and inspect the recorded source. Keep the pin unchanged; different bytes are not the captured publication. |
| `law install` cannot find the local registry | Run it from `examples/prime-naissance-moreau`, with `examples` and `arxo-cnaf` as sibling directories, or supply the actual absolute path to `arxo-cnaf/registry`. |

## Package inventory

These counts describe the 12 October 2026 export recorded in
[`packages.json`](../packages.json). There are 21 source packages and
1,985 declared scenarios; the registry closure contains 22 packages.

| Package | Version | Scenarios | Direct dependencies |
|---|---|---:|---:|
| [`fr.css.aah`](../packages/fr.css.aah/) | 0.1.0 | 70 | 0 |
| [`fr.css.pass`](../packages/fr.css.pass/) | 0.1.0 | 26 | 0 |
| [`fr.css.prime_activite`](../packages/fr.css.prime_activite/) | 0.1.0 | 201 | 0 |
| [`fr.css.revalorisation`](../packages/fr.css.revalorisation/) | 0.1.0 | 12 | 0 |
| [`fr.minima.ressources`](../packages/fr.minima.ressources/) | 0.1.0 | 31 | 0 |
| [`fr.pf.paje`](../packages/fr.pf.paje/) | 0.1.0 | 87 | 0 |
| [`fr.tax.income_for_apl`](../packages/fr.tax.income_for_apl/) | 0.1.0 | 3 | 0 |
| [`fr.travail.smic`](../packages/fr.travail.smic/) | 0.1.0 | 80 | 0 |
| [`fr.apl`](../packages/fr.apl/) | 0.1.0 | 406 | 1 |
| [`fr.casf.rsa`](../packages/fr.casf.rsa/) | 0.1.0 | 133 | 1 |
| [`fr.pf.core`](../packages/fr.pf.core/) | 0.1.0 | 326 | 1 |
| [`fr.apl.versement`](../packages/fr.apl.versement/) | 0.1.0 | 11 | 2 |
| [`fr.css.ajpa`](../packages/fr.css.ajpa/) | 0.1.0 | 44 | 2 |
| [`fr.pf.aeeh`](../packages/fr.pf.aeeh/) | 0.1.0 | 50 | 2 |
| [`fr.pf.af`](../packages/fr.pf.af/) | 0.1.0 | 73 | 2 |
| [`fr.pf.ajpp`](../packages/fr.pf.ajpp/) | 0.1.0 | 91 | 2 |
| [`fr.pf.ars`](../packages/fr.pf.ars/) | 0.1.0 | 26 | 2 |
| [`fr.pf.asf`](../packages/fr.pf.asf/) | 0.1.0 | 36 | 2 |
| [`fr.pf.cf`](../packages/fr.pf.cf/) | 0.1.0 | 96 | 3 |
| [`fr.pf.cmg`](../packages/fr.pf.cmg/) | 0.1.0 | 45 | 2 |
| [`fr.prestations.versement`](../packages/fr.prestations.versement/) | 0.1.0 | 138 | 19 |
