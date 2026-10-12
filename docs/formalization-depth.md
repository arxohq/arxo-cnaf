# Reading the formalization depth

The GitHub and npm READMEs describe the same canon export, source revision
[`f2efcc6788465484f145146a3ed5f76b13d41703`](https://github.com/arxohq/arxo-cnaf/tree/f2efcc6788465484f145146a3ed5f76b13d41703).
The [report](../npm/assets/formalization-depth.json) retains package hashes,
source document and declaration hashes, per-unit levels, and measurement limits
for all 21 models. It ships inside the npm archive too.

## What the numbers mean

| Level | Evidence required |
|---|---|
| `EXECUTABLE` (E) | At least one deriving node is anchored to the unit: a rule, norm template, priority, closure or constraint |
| `INTERPRETED` (I) | Deriving nodes exist, but only under an explicitly selected interpretation |
| `ANCHORED` (A) | A model node addresses the unit, without a deriving node |
| `SOURCE_ONLY` (S) | A fragment of the unit exists; no model node addresses it |
| `NONE` (N) | A recognized unit has no model node |

The denominator is **article editions in the measured pinned excerpts**.
A provision appearing in successive editions is counted in each distinct
publication; identical source-document bytes are deduplicated within a package.
The report uses **own package CLIR**, so imported rules are not counted again.
An edition may contain several articles; it is not itself one unit.

For example, APL has 1,352 executable article editions out of 1,654 measured:
166 anchored, 136 source-only, and zero interpretation-only or absent units.
The measurement is partial: one declared document does not match an own
publication in that CLIR. It is identified rather than included in the ratio.
AF's 103 / 103 likewise does not establish full coverage: two own publications
are outside its article measurement. Check every model's status and evidence.

**An executable article does not mean that all its conditions, exceptions,
paragraphs or dates are formalized.** These are static depth counts, not
legal acceptance, paragraph completeness, current-law certification or a
percentage of an entire benefit. There is no whole-benefit denominator here.
`STRUCTURED`, `SEMANTIC`, `VERIFIED` and `DISPUTED` are not assessed by this report.

Rules / norms in the README are separate structural counts of `rule` and
`norm_template` nodes. They do not include all kinds of deriving nodes and
are not substitutes for depth. Scenarios come from the pinned `packages.json`:
1,985 recorded cases across the 21 models. They were not rerun for this update.

## Boundaries are recorded per package

- `measured`: the declared texts were measurable and all own publications
  were included. It describes the available publications, not all benefit law.
- `partial` (†): a numerical measurement is available, with own publications
  or declared documents outside it. Read `unmeasuredPublications` and
  `unmeasuredDocuments` before interpreting the denominator.
- `not_measured`: no declared source-document division was available for
  this method. Payment-stage, PASS, revaluation and shared payment/recovery
  models retain their own rule and scenario counts; their depth is not zero.

AJPA, minimum-income resources and PAJE omit a unit convention in their source
maps. This report explicitly selects the existing `fr_code_lettered_article`
convention for their lettered source headings and article inventories. That
choice is recorded as `reportUnitConvention`, applies only to temporary
measurement inputs, and leaves all published model and source bytes unchanged.
Recognized numbers found only inside quoted amendment text do not count as
lettered code articles. Declared documents without a hash-matched own
publication do not contribute units either.

## Reproduce the snapshot

The generator calls Arxo's existing authoring `boundaries.depth` measure;
it does not implement another depth classifier. The report identifies the
implementation files by SHA-256. This authoring measure supports French
lettered code articles; released CLI `law audit` 0.2.2 does not support that
unit convention. The report is therefore **not** a fresh `law audit` result.
No source lowering or model execution takes place.

From this repository, export only the necessary pinned inputs into new
scratch directories:

```sh
mkdir -p /tmp/cnaf-depth-canon /tmp/cnaf-depth-sources
revision=f2efcc6788465484f145146a3ed5f76b13d41703

git archive "$revision" registry packages.json LICENSE NOTICE WITHHELD.json \
  | tar -x -C /tmp/cnaf-depth-canon

git archive "$revision" \
  packages/fr.apl.versement/sources packages/fr.apl/sources \
  packages/fr.casf.rsa/sources packages/fr.css.aah/sources \
  packages/fr.css.ajpa/sources packages/fr.css.pass/sources \
  packages/fr.css.prime_activite/sources packages/fr.css.revalorisation/sources \
  packages/fr.minima.ressources/sources packages/fr.pf.aeeh/sources \
  packages/fr.pf.af/sources packages/fr.pf.ajpp/sources \
  packages/fr.pf.ars/sources packages/fr.pf.asf/sources \
  packages/fr.pf.cf/sources packages/fr.pf.cmg/sources \
  packages/fr.pf.core/sources packages/fr.pf.paje/sources \
  packages/fr.tax.income_for_apl/sources packages/fr.travail.smic/sources \
  | tar -x -C /tmp/cnaf-depth-sources
```

With an Arxo authoring checkout whose measurement implementation matches the
hashes in the report:

```sh
python3 npm/tools/formalization-depth.py \
  --law-root /path/to/law-dsl \
  --canon /tmp/cnaf-depth-canon \
  --sources /tmp/cnaf-depth-sources \
  --output /tmp/cnaf-depth-report.json

cmp /tmp/cnaf-depth-report.json npm/assets/formalization-depth.json
```

The generator verifies the catalog and each original package CLIR against the
npm source pin; measurement texts must match an own publication by byte hash.
A different implementation is visible in `implementationHashes`; do not silently
replace the recorded snapshot or compare different denominators as progress.

This is an addressed documentation measurement over the archived inputs.
It leaves the corpus `not_checked` and `releaseVerified: false`. For rebuilding
or running a particular source package, use the
[reproducibility guide](reproducibility.md).
