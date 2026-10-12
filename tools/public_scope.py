#!/usr/bin/env python3
"""Public package profile: retain executable inputs, replace authoring docs.

Standalone standard-library tool, also used by spinoff.py before release checks.
Use --check for a read-only guard; --apply changes only the selected package copies.
"""
from __future__ import annotations
import argparse
import json
import posixpath
from pathlib import Path
import re
import tomllib

PRIVATE_DIRS = frozenset({'analysis', 'drafts', 'tools', 'reviews', 'notes'})
PUBLIC_DIRS = frozenset({'sources', 'tests', 'bareme', 'deps', 'i18n',
                         'deduction', 'expansions', 'resources', 'queries',
                         'examples', 'tables', 'params'})
PUBLIC_ROOT_FILES = frozenset({'README.md', 'package-info.json', 'law.toml',
                               'law.lock', '.gitignore', 'LICENSE', 'NOTICE',
                               'bareme.json'})
CACHE_DIRS = frozenset({'.git', '__pycache__', '.law', '.law-cache'})
MODEL_SUFFIXES = ('.law', '.lawtest', '.lawparam.json', '.lawtable.json',
                  '.lawir.json', '.deontic-window.toml')
PUBLIC_TITLES = {
    'fr.apl': 'Housing aid (APL / AL)',
    'fr.apl.versement': 'Housing-aid payment stage',
    'fr.casf.rsa': 'Active solidarity income (RSA)',
    'fr.css.aah': 'Adult disability allowance (AAH)',
    'fr.css.ajpa': 'Caregiver allowance (AJPA)',
    'fr.css.pass': 'Social-security ceiling (PASS)',
    'fr.css.prime_activite': 'Activity bonus',
    'fr.css.revalorisation': 'Benefit revaluation',
    'fr.minima.ressources': 'Resources for minimum-income benefits',
    'fr.pf.aeeh': 'Disabled-child education allowance (AEEH)',
    'fr.pf.af': 'Family allowances (AF)',
    'fr.pf.ajpp': 'Daily parental-presence allowance (AJPP)',
    'fr.pf.ars': 'School-start allowance (ARS)',
    'fr.pf.asf': 'Family support allowance (ASF)',
    'fr.pf.cf': 'Family supplement (CF)',
    'fr.pf.cmg': 'Childcare supplement (CMG)',
    'fr.pf.core': 'Shared family-benefit rules',
    'fr.pf.paje': 'Early-childhood benefits (PAJE)',
    'fr.prestations.versement': 'Benefit payments and debt recovery',
    'fr.tax.income_for_apl': 'Income used for housing aid',
    'fr.travail.smic': 'Minimum wage (SMIC)',
}


def package_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob('*')):
        if CACHE_DIRS.intersection(path.relative_to(root).parts):
            continue
        if path.is_symlink():
            raise ValueError(f'{path}: symlinks are not public package inputs')
        if path.is_file():
            files.append(path)
    return files


def manifest(root: Path) -> dict:
    path = root / 'law.toml'
    return tomllib.loads(path.read_text()) if path.is_file() else {}


def suites(data: dict) -> list[str]:
    entries = data.get('tests', [])
    if isinstance(entries, dict):
        entries = [entries]
    return list(dict.fromkeys(rel for entry in entries
                             for part in [entry, *entry.get('part', [])]
                             for rel in part.get('suites', [])))


def referenced_inputs(root: Path, files: list[Path]) -> set[str]:
    existing = {p.relative_to(root).as_posix() for p in files}
    protected = {'law.toml', 'law.lock', 'package-info.json'}
    protected.update(p.relative_to(root).as_posix() for p in files
                     if p.name.endswith(MODEL_SUFFIXES) or p.name in ('law.toml', 'law.lock'))

    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, dict):
            for child in value.values():
                yield from strings(child)
        elif isinstance(value, list):
            for child in value:
                yield from strings(child)

    for p in files:
        if p.name.endswith('.law'):
            owner = next((parent for parent in [p.parent, *p.parent.parents]
                          if parent.is_relative_to(root) and (parent / 'law.toml').is_file()), root)
            for rel in re.findall(r'\blocal_path\s+"([^"]+)"', p.read_text()):
                target = (owner / rel).resolve()
                if not target.is_relative_to(root.resolve()):
                    raise ValueError(f'{p}: source path escapes package: {rel}')
                protected.add(target.relative_to(root.resolve()).as_posix())
        elif p.name == 'law.toml':
            for rel in strings(tomllib.loads(p.read_text())):
                # Metadata descriptions are strings too, not filesystem paths.
                candidate = posixpath.normpath((p.relative_to(root).parent / rel).as_posix())
                if candidate in existing:
                    protected.add(candidate)
    return protected


def removal_plan(root: Path) -> list[str]:
    files = package_files(root)
    protected = referenced_inputs(root, files)
    result = []
    for p in files:
        rel = p.relative_to(root)
        private = bool(PRIVATE_DIRS.intersection(rel.parts[:-1]))
        # Unknown folders/files are not silently promoted into a public kit.
        # Explicit model inputs override this profile regardless of location.
        private |= (len(rel.parts) > 1 and rel.parts[0] not in PUBLIC_DIRS)
        private |= (len(rel.parts) == 1 and p.name not in PUBLIC_ROOT_FILES)
        author_doc = p.suffix.lower() == '.md' and rel.as_posix() != 'README.md'
        # A source provenance note is useful to readers; a pinned Markdown text
        # remains an input regardless of its directory or filename.
        if rel.parts[0] == 'sources' and p.name == 'PROVENANCE.md':
            author_doc = False
        if (private or author_doc) and rel.as_posix() not in protected:
            result.append(rel.as_posix())
    if 'README.md' in protected:
        raise ValueError(f'{root}: README is a pinned input and cannot be replaced')
    return result


def public_info(root: Path) -> dict | None:
    path = root / 'package-info.json'
    if not path.is_file():
        return None
    info = json.loads(path.read_text())
    purpose = info.get('purpose', '')
    # Preserve the actual purpose and all limitations, rights and examples;
    # replace only the trailing navigation to removed authoring documents.
    purpose = re.sub(r'The list of provided queries and boundaries.*$',
                     'See README.md for the exported scope and examples.', purpose)
    purpose = re.sub(r'предусмотренные запросы и границы перечислены в.*$',
                     'see README.md for the exported scope and examples.', purpose)
    info['purpose'] = purpose
    return info


def readme(root: Path, data: dict | None = None) -> str | None:
    data = manifest(root) if data is None else data
    package = data.get('package')
    if not isinstance(package, dict):
        return None
    name = package['name']
    title = PUBLIC_TITLES.get(name, data.get('metadata', {}).get('title', name))
    info = public_info(root) or {}
    lock_path = root / 'law.lock'
    lock = json.loads(lock_path.read_text()) if lock_path.is_file() else {}
    scenario_files = suites(data)
    first = next((p for p in scenario_files if (root / p).is_file()), None)
    lines = [f'# {name}', '', str(title), '',
             '> Independent demonstration model. It is not an implementation by or',
             '> for an authority and does not establish legal accuracy or completeness.',
             '> For a real case, rely on the official texts and competent bodies.', '',
             '## Package snapshot', '', '| Item | Value |', '|---|---|',
             f"| Version | `{package.get('version', '')}` |",
             f"| Namespace | `{package.get('namespace', '')}` |"]
    if lock.get('languageSemantics'):
        lines.append(f"| Semantics | `{lock['languageSemantics']}` |")
    deps = ', '.join(f'`{n}`' for n in data.get('dependencies', {})) or 'None declared'
    lines += [f'| Dependencies | {deps} |', '', '## Run an example', '',
              'Install the CLI as described in the [repository README](../../README.md).',
              'From the repository root:', '', '```sh', f'cd packages/{root.name}']
    if first:
        lines.append(f'law test . --file {first} --json')
    else:
        lines.append('law test . --json')
    lines += ['```', '', 'Success checks the declared expectations of the model; it does not certify',
              'that the model covers the whole benefit or every possible case.', '',
              '## Scope and inputs', '',
              'The executable scope is defined by the rules and declared scenarios in this',
              'snapshot. Each rule has its own dates, prerequisites and source anchors.',
              'Use the supplied facts and any explicitly selected readings of the scenario;',
              'do not infer wider coverage from the subject named above.', '']
    limits = info.get('limitations', [])
    if isinstance(limits, list) and limits:
        lines += ['The package author records these limitations (retained from',
                  '[package-info.json](package-info.json)):', '']
        lines += [f'- {str(item)}' for item in limits]
        lines.append('')
    lines += ['| Inspect | What it contains |', '|---|---|',
              '| [law.toml](law.toml) | Package identity, dependencies and declared scenario groups |']
    if lock_path.is_file():
        lines.append('| [law.lock](law.lock) | Exact dependency, semantics and resource pins |')
    for folder, text in [('tests', 'Declared scenarios and their fixtures'),
                         ('sources', 'Captured source material; individual reproduction terms apply'),
                         ('bareme', 'Dated model parameters'), ('deps', 'Pinned dependency bytes'),
                         ('i18n', 'Labels and translations')]:
        if (root / folder).is_dir():
            lines.append(f'| [{folder}/]({folder}/) | {text} |')
    sources = next((p for p in ['01-sources.law', 'sources.law', 'package.law']
                    if (root / p).is_file()), None)
    if sources:
        lines.append(f'| [{sources}]({sources}) | Model declarations and source references |')
    lines += ['', '## Reproduction and rights', '',
              'See the [repository instructions](../../README.md) for rebuilding',
              'a source package and restoring any withheld sources. The [repository licence](../../LICENSE)',
              'covers the model code; captured publisher texts keep their own terms in',
              '[NOTICE](../../NOTICE) and [package-info.json](package-info.json).', '']
    return '\n'.join(lines)


def clean_package(root: Path, apply: bool = False) -> dict:
    removed = removal_plan(root)
    desired = readme(root)
    current = (root / 'README.md').read_text() if (root / 'README.md').is_file() else None
    info = public_info(root)
    info_changed = info is not None and info != json.loads((root / 'package-info.json').read_text())
    report = {'package': root.name, 'removed': removed,
              'readmeChanged': desired is not None and desired != current,
              'infoChanged': info_changed}
    if apply:
        for rel in removed:
            (root / rel).unlink()
        for p in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
            if p.is_dir() and not any(p.iterdir()) and not CACHE_DIRS.intersection(p.relative_to(root).parts):
                p.rmdir()
        if desired is not None:
            (root / 'README.md').write_text(desired)
        if info_changed:
            (root / 'package-info.json').write_text(json.dumps(info, ensure_ascii=False, indent=2)+'\n')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packages', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    roots = sorted(p.parent for p in args.packages.glob('*/law.toml'))
    if not roots:
        parser.error('No packages found')
    # Validate every plan before the first deletion.
    plans = [clean_package(p) for p in roots]
    if args.apply:
        plans = [clean_package(p, apply=True) for p in roots]
    if args.report:
        args.report.write_text(json.dumps(plans, ensure_ascii=False, indent=2)+'\n')
    changed = [p for p in plans if p['removed'] or p['readmeChanged'] or p['infoChanged']]
    print(f'{len(roots)} packages; {sum(len(p["removed"]) for p in plans)} authoring files; '
          f'{len(changed)} packages {"cleaned" if args.apply else "need cleanup"}')
    return 1 if args.check and changed else 0


if __name__ == '__main__':
    raise SystemExit(main())
