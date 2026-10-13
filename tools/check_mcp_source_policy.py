#!/usr/bin/env python3
"""Offline guard for the pinned CNAF source and public runtime surface."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def fragments(document):
    nodes = document.get('nodes', [])
    editions = {n.get('edition') for n in nodes if n.get('kind') == 'publication'
                and urlparse(n.get('uri', '')).hostname in ('caf.fr', 'www.caf.fr')}
    result = []
    for node in nodes:
        if node.get('kind') != 'fragment' or node.get('edition') not in editions:
            continue
        for text in node.get('texts', []):
            value = text['text']
            result.append({'id': node['id'], 'edition': node['edition'],
                           'nodeContentHash': node['contentHash'],
                           'textSha256': digest(value.encode()),
                           'characters': len(value), 'bytes': len(value.encode()),
                           'status': text.get('status'), 'language': text.get('language')})
    return result


def check(root, runtime=None):
    root = Path(root).resolve()
    policy = json.loads((root / 'mcp/source-policy.json').read_bytes())
    canon = json.loads((root / 'mcp/canon.json').read_bytes())
    if policy['sourceCommit'] != canon['sourceCommit']:
        raise ValueError('source policy and frozen canon commits differ')
    distribution = policy['distribution']
    if distribution['fetchWithheld'] is not False or distribution['newReproductionRightsGranted'] is not False:
        raise ValueError('source policy must not fetch full withheld texts or grant new source rights')
    withheld = json.loads((root / 'WITHHELD.json').read_bytes())['files']
    actual_paths = sorted(f"packages/{x['package']}/{x['path']}" for x in withheld)
    if sorted(distribution['withheldPaths']) != actual_paths:
        raise ValueError('withheld paths differ from the publication manifest')
    for rel in actual_paths:
        path = root / rel
        if path.is_symlink() or path.exists():
            raise ValueError(f'withheld source present in public checkout: {rel}')
    expected = distribution['allowedExistingFragments']
    keys = [(x['package'], x['version'], x['id'], x['textSha256']) for x in expected]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate accepted excerpt')
    observed = []
    for publication in canon['publications']:
        if publication['role'] != 'root':
            continue
        name, version = publication['name'], publication['version']
        document = json.loads((root / f'registry/p/{name}/{version}/package.lawir.json').read_bytes())
        for item in fragments(document):
            observed.append({'package': name, 'version': version, **item})
        if runtime is not None:
            runtime_path = Path(runtime) / f"corpus/clir/{publication['runtimeKey']}.lawir.json"
            actual = json.loads(runtime_path.read_bytes())
            if fragments(actual) != fragments(document):
                raise ValueError(f'runtime source excerpts differ: {name}')
    order = lambda x: (x['package'], x['version'], x['id'], x['textSha256'])
    if sorted(observed, key=order) != sorted(expected, key=order):
        raise ValueError('CAF excerpt IDs, hashes, text lengths or status differ from accepted public snapshot')
    if runtime is not None:
        runtime = Path(runtime)
        withheld_names = {Path(x['path']).name for x in withheld}
        for path in runtime.rglob('*'):
            rel = path.relative_to(runtime)
            if path.is_symlink():
                raise ValueError(f'runtime symlink is not allowed: {rel}')
            if {'analysis', 'drafts', 'tools', 'reviews', 'notes'}.intersection(rel.parts):
                raise ValueError(f'internal runtime path: {rel}')
            if path.is_file() and (path.name in withheld_names or path.suffix in ('.py', '.pyc', '.lawtest')
                                   or path.name in ('AUDIT.md', 'QUESTIONS.md', 'PLAN.ru.md')
                                   or path.name.startswith(('candidate-', 'phase-'))):
                raise ValueError(f'nonpublic runtime file: {rel}')
    return {'format': 'cnaf.mcp-source-check/1', 'result': 'pass',
            'acceptedExistingExcerpts': len(observed), 'withheldFilesAbsent': len(actual_paths),
            'sourceCommit': policy['sourceCommit'], 'fullCorpus': 'not_checked', 'releaseVerified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--runtime', type=Path)
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    try:
        result = check(args.root, args.runtime)
        if args.receipt:
            args.receipt.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    except (KeyError, ValueError, OSError, TypeError) as error:
        parser.exit(1, f'source surface refused: {error}\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
