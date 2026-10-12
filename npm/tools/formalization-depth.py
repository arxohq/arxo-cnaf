#!/usr/bin/env python3
"""Record static depth from pinned canon bytes using Arxo's existing measure.
No lowering, cases, corpus gates, network access or source rewriting.
"""
import argparse
import hashlib
import importlib.util
import json
import tempfile
from collections import Counter
from pathlib import Path


def digest(data):
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--law-root', type=Path, required=True)
    ap.add_argument('--canon', type=Path, required=True)
    ap.add_argument('--sources', type=Path, required=True,
                    help='packages/*/sources exported at the canon source revision')
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    package_dir = Path(__file__).resolve().parents[1]
    pin = json.loads((package_dir / 'source-pin.json').read_text())
    tool_path = args.law_root / '.claude/skills/formalize-act/scripts/boundaries.py'
    module_spec = importlib.util.spec_from_file_location('canon_depth', tool_path)
    measure = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(measure)
    # The original package catalog is an explicit pin, including recorded scenarios.
    catalog_bytes = (args.canon / 'packages.json').read_bytes()
    catalog_pin = pin['files']['canon-packages.json']
    if digest(catalog_bytes) != catalog_pin['sha256']:
        raise ValueError('Canon catalog differs from the pinned export')
    catalog = {row['name']: row for row in json.loads(catalog_bytes)['packages']}
    tool_files = ['.claude/skills/formalize-act/scripts/boundaries.py',
                  'corpus/tools/lib/act_split.py',
                  'engines/lawref/lawref/editions/applicability.py']
    out = {
        'format': 'arxo.canon-depth-snapshot/0.1',
        'source': {'repository': pin['repository'], 'revision': pin['revision']},
        'method': {
            'implementation': 'boundaries.depth (Arxo authoring depth measure)',
            'inputs': 'original package CLIR; hash-matched declared pinned source documents',
            'unit': 'article edition; identical source-document bytes deduplicated per package',
            'imports': 'excluded; own package nodes only',
            'implementationHashes': {p: digest((args.law_root / p).read_bytes()) for p in tool_files},
            'levels': ['EXECUTABLE', 'INTERPRETED', 'ANCHORED', 'SOURCE_ONLY', 'NONE'],
            'freshness': 'archived CLIR; no fresh lowering',
            'completeness': 'not assessed; a deriving node is not complete legal coverage',
            'scenarios': 'recorded outcomes from pinned packages.json; not rerun',
            'releaseVerified': False, 'corpus': 'not_checked',
        },
        'packages': [],
    }
    for model in sorted(pin['models'], key=lambda row: row['name']):
        name, version = model['name'], model['version']
        ir_path = args.canon / 'registry' / 'p' / name / version / 'package.lawir.json'
        ir_bytes = ir_path.read_bytes()
        if digest(ir_bytes) != model['packageHash']:
            raise ValueError(f'Package hash mismatch: {name}')
        ir = json.loads(ir_bytes)
        if any(n.get('package') != model['namespace'] for n in ir['nodes']):
            raise ValueError(f'Unexpected imported nodes: {name}')
        kinds = Counter(n['kind'] for n in ir['nodes'])
        pubs = {}
        for n in ir['nodes']:
            if n['kind'] == 'publication':
                pubs.setdefault(n.get('documentHash'), []).append(n['id'])
        counts = Counter()
        docs, unmeasured, seen = [], [], set()
        pkg_sources = args.sources / 'packages' / name
        for declaration in sorted(pkg_sources.glob('sources/**/articles.json')):
            payload = json.loads(declaration.read_text())
            entries = ([payload] if payload.get('document') else []) + payload.get('editions', [])
            for entry in entries:
                document = entry.get('document')
                if not document:
                    continue
                candidates = [declaration.parent / document, pkg_sources / document]
                source = next((p for p in candidates if p.is_file()), None)
                if source is None:
                    unmeasured.append({'declaration': str(declaration.relative_to(args.sources)),
                                       'document': document, 'reason': 'declared document missing'})
                    continue
                sha = digest(source.read_bytes())
                if sha in seen:
                    continue
                seen.add(sha)
                record = {'path': str(source.relative_to(args.sources)), 'documentHash': sha,
                          'declaration': str(declaration.relative_to(args.sources)),
                          'declarationHash': digest(declaration.read_bytes())}
                if sha not in pubs:
                    unmeasured.append({**record, 'reason': 'no own publication matches these bytes'})
                    continue
                record['publications'] = pubs[sha]
                declared = {**payload, **entry}
                if name in {'fr.css.ajpa', 'fr.minima.ressources', 'fr.pf.paje'} and not declared.get('unit'):
                    # Explicit report convention: these source headers and declared
                    # scope use lettered code articles. Leave published inputs intact.
                    declared['unit'] = 'fr_code_lettered_article'
                    record['reportUnitConvention'] = 'fr_code_lettered_article'
                    record['reportUnitReason'] = 'lettered source headings and article inventory; original declaration omits unit'
                    with tempfile.TemporaryDirectory(prefix='canon-depth-unit-') as temporary:
                        staged = Path(temporary) / 'source.txt'
                        staged.write_bytes(source.read_bytes())
                        (staged.parent / 'articles.json').write_text(json.dumps({**{k: v for k, v in declared.items() if k != 'editions'}, 'document': 'source.txt'}))
                        result = measure.depth(staged, ir_path)
                else:
                    result = measure.depth(source, ir_path)
                rows = result['rows']
                scope = declared.get('scope')
                # Auto-recognition of a numbered article in quoted amendment text
                # must not be mistaken for the lettered code article in scope.
                expected = set(map(str, scope)) if isinstance(scope, list) else {
                    str(r['num']) for r in payload.get('articles', []) if r.get('num')}
                if not rows or (expected and not any(r['article'] in expected for r in rows)):
                    unmeasured.append({**record, 'reason': 'declared article units not recognized'})
                    continue
                normalized = [{**r, 'level': 'NONE' if r['level'] == '—' else r['level']} for r in rows]
                counts.update(r['level'] for r in normalized if r['level'] != 'EXCLUDED')
                docs.append({**record, 'unit': result['unit'], 'units': normalized,
                             'unresolvedAnchors': result['unresolved']})
        measured_publications = {p for d in docs for p in d['publications']}
        without = [p for ps in pubs.values() for p in ps if p not in measured_publications]
        total = sum(counts.values())
        status = 'measured' if docs and not without and not unmeasured else 'partial' if docs else 'not_measured'
        out['packages'].append({
            'name': name, 'spec': model['spec'], 'subpath': model['subpath'],
            'packageHash': model['packageHash'], 'status': status,
            'units': total, 'levels': {k: counts[k] for k in out['method']['levels']},
            'ownRules': kinds['rule'], 'ownNormTemplates': kinds['norm_template'],
            'ownFragments': kinds['fragment'], 'ownPublications': kinds['publication'],
            'recordedScenarios': catalog[name]['tests'], 'recordedOutcome': catalog[name]['outcome'],
            'documents': docs, 'unmeasuredDocuments': unmeasured,
            'unmeasuredPublications': sorted(without),
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    for row in out['packages']:
        print(row['name'], row['status'], row['levels'], 'units', row['units'])


if __name__ == '__main__':
    main()
