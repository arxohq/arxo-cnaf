import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import test from 'node:test';
import { open } from '@arxo/law';
import { loadModel, models, ModelIntegrityError, ModelNotFoundError } from '../src/index.js';
import { loadModel as loadApl } from '../src/apl.js';
import { household, caseInput } from '../examples/apl.js';
const root = new URL('../', import.meta.url);

test('all 21 models load their own hash-checked frozen worlds and referenced catalogs', async () => {
  assert.equal(models.length, 21);
  for (const info of models) {
    const model = await loadModel(info.spec);
    assert.equal(model.spec, info.spec);
    assert.equal(model.package.ir.package.name, info.name);
    assert.equal(model.pin.worldHash, model.descriptor.worldHash);
    assert.equal(model.package.meta.contentHash, model.descriptor.worldHash);
    assert.equal(model.package.meta.packageContentHash, model.descriptor.contentHash);
    if (info.questionCatalogHash) assert.equal(model.questionCatalog.package, info.name);
  }
});

test('versionless, unknown and path-like specs do not fall back to other models or network', async () => {
  for (const spec of ['fr.apl', 'fr.apl@9.9.9', '../../etc/passwd']) {
    await assert.rejects(loadModel(spec), ModelNotFoundError);
  }
});

test('separate calls return isolated parsed worlds', async () => {
  const a = await loadApl();
  a.package.ir.package.name = 'mutated';
  const b = await loadApl();
  assert.equal(b.package.ir.package.name, 'fr.apl');
});

test('corrupted bytes are refused before JSON parsing', async () => {
  const target = new URL('data/apl/world.lawir.json', root);
  const saved = await readFile(target);
  try {
    await writeFile(target, Buffer.from('this is not JSON'));
    await assert.rejects(loadApl(), e => e instanceof ModelIntegrityError && e.actual.startsWith('sha256:'));
  } finally {
    await writeFile(target, saved);
  }
});

test('published facade gives both readings, missing selection, proof and canonical document', async () => {
  const model = await loadApl();
  const apl = await open(model.spec, { offline: true, local: { packages: { [model.spec]: model.package } } });
  for (const [reading, expected] of [['PpPlancherFinal', '20.17'], ['PpLitteral', '53.7338'], [null, null]]) {
    const input = structuredClone(caseInput);
    input.options = reading ? { selectedInterpretations: [`urn:fr:corpus:clir:apl#${reading}`] } : {};
    const answer = await apl.collect('aide_formule', [household, '?amount'], input);
    assert.equal(answer.via, 'local');
    assert.equal(answer.evaluationStatus, expected === null ? 'INTERPRETATION_REQUIRED' : 'COMPUTED');
    if (expected === null) assert.deepEqual(answer.value, []);
    else assert.equal(answer.value[0].value, expected);
    assert.ok(answer.document.length > 0);
    assert.ok(answer.proof.nodes.length > 0);
    assert.match(answer.hashes.result, /^sha256:[0-9a-f]{64}$/);
    const document = JSON.parse(new TextDecoder().decode(answer.document));
    assert.deepEqual(document.proofGraph, answer.proof);
    assert.equal(document.resultHash, answer.hashes.result);
  }
  assert.equal(apl.unfold('aide_formule', { depth: 2 }).tree.name, 'aide_formule');
  const numericMoney = structuredClone(caseInput);
  numericMoney.answers.find(row => row.predicate === 'ressources_du_menage').args[1] = 4000;
  await assert.rejects(apl.collect('aide_formule', [household, '?amount'], numericMoney), /must be a string/);
  const unknown = structuredClone(caseInput);
  unknown.answers.push({ predicate: 'not_a_declared_fact', args: [household] });
  await assert.rejects(apl.collect('aide_formule', [household, '?amount'], unknown), /not_a_declared_fact/);
  const incomplete = structuredClone(caseInput);
  incomplete.answers = incomplete.answers.filter(row => row.predicate !== 'ressources_du_menage');
  const missing = await apl.collect('aide_formule', [household, '?amount'], incomplete);
  assert.deepEqual(missing.value, [], 'missing resources must not produce a made-up amount');
});
