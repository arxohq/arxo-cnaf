# Public package contents

The source packages in this repository are a consumer kit: executable model
sources, pinned dependencies and resources, captured publications, parameters,
translations and scenarios. Each package has a public README with its subject,
run command and retained limitations.

Authoring reports, drafts, monorepository maintenance scripts and benchmark
notes are not part of this kit. Unknown work folders are excluded unless a file
is a model, scenario or explicitly referenced input. The source provenance note
and publication bytes retain their own reproduction terms.

The package profile preserves `.law`, `.lawtest`, parameter and table data,
`law.toml`, `law.lock`, dependency bytes, captured source paths and file inputs
named by the manifest. It does not remove required inputs because of their
folder name. It retains all model limitations in `package-info.json`; obsolete
navigation to authoring notes is replaced with navigation to the public README.

From the repository root, with Python 3.12 or later:

```sh
python3 tools/public_scope.py --packages packages --check
```

This is a read-only file/profile check. It runs no model scenarios and rebuilds
no releases. The `public package scope` workflow runs the same guard on future
updates. The exporter also applies the profile to copies before release checks;
its authoring source tree is left intact.

For execution and release rebuilding, see the
[reproducibility guide](reproducibility.md). A clean public profile is not a
claim of legal accuracy, completeness or a new verification of the whole corpus.
