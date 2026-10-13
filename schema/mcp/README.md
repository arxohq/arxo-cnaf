# Standalone MCP manifests

These JSON Schema 2020-12 contracts are local artifacts, not network dependencies.
The offline tools use Python 3.12+ standard-library checks for their invariants.
`canon-artifact.schema.json` vendors the Rust host's `law.profile/0.1` format;
its source is the Arxo profile schema reviewed on 2026-10-13.

`canon.json` classifies every local registry publication. Runtime keys and package
paths are explicit. Roots and imports must produce exactly the selected closure.
Excluded publications are recorded, never copied into the runtime catalog.

Hash meanings remain separate:

* Descriptor `contentHash` and lock root/dependency `artifactHash` pin the raw
  published `package.lawir.json` bytes.
* CLIR `artifactHash`, `semanticHash` and `theoryHash` remain the existing fields;
  the materializer does not recompute or substitute their meanings.
* `sourceHash` is copied from its descriptor or lock. Absence is JSON `null`.
* Locked label overlays use canonical JSON. A3 parameter/table resources use
  their semantic projection (presentation labels and metadata removed), including
  §208 normalization of typed decimal values and ordered unordered table rows.
  Their independent `rawSha256` records the unchanged physical file.
* Frozen input inventory checks raw source bytes. Its digest enters the external
  materialization receipt; this does not imply a new subject-corpus acceptance.

The tree pin is outside the runtime. Each entry records a canonical relative POSIX
path, type and mode; files additionally record byte size and raw SHA-256. Entries
are ordered by their path strings, not filesystem or path-component traversal.
The tree digest is SHA-256 of UTF-8 JSON with sorted object keys, no whitespace,
non-ASCII characters preserved and the complete ordered entry array as its root.
Directories use `0755`; files use `0644`, except `bin/law-mcp-server` uses `0755`.
Symlinks and other file types are refused. File timestamps do not enter the pin.

The archive has a single `runtime/` root and the same POSIX path ordering. POSIX
PAX tar headers have UID/GID 0, empty owner names, epoch timestamps and the pinned
modes. Gzip has an empty filename and mtime 0. The archive's checksum and all
receipts remain external; the archive never hashes itself. Publication must reuse
the accepted archive bytes, not rebuild it from a moving checkout.
