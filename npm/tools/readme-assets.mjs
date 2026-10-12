/** README diagrams from the pinned APL example. No subject arithmetic here. */
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { open } from '@arxo/law';
import { loadModel } from '../src/apl.js';
import { household, caseInput } from '../examples/apl.js';
const root = new URL('../', import.meta.url);
const output = new URL('assets/', root);
await mkdir(output, { recursive: true });
const model = await loadModel();
const apl = await open(model.spec, { offline: true, local: { packages: { [model.spec]: model.package } } });
const readings = [];
for (const [reading, expected] of [['PpPlancherFinal','20.17'], ['PpLitteral','53.7338'], [null,null]]) {
  const input = structuredClone(caseInput);
  input.options = reading ? {selectedInterpretations:[`urn:fr:corpus:clir:apl#${reading}`]} : {};
  const answer = await apl.collect('aide_formule', [household, '?amount'], input);
  assert.equal(answer.evaluationStatus, reading ? 'COMPUTED' : 'INTERPRETATION_REQUIRED');
  assert.equal(answer.value?.[0]?.value ?? null, expected);
  readings.push({reading, evaluationStatus:answer.evaluationStatus, value:answer.value,
    proofNodes:answer.proof.nodes.length, hashes:answer.hashes});
}
const unfolded = apl.unfold('aide_formule', {depth:2,lang:'en',quote:0});
// The reused SVG expands this exact native tree; no case or reading is selected.
const upstream = JSON.parse(await readFile(new URL('../../docs/unfold/aide-formule.json',import.meta.url)));
assert.deepEqual(unfolded.tree, upstream);
await writeFile(new URL('apl-unfold.json',output), JSON.stringify(unfolded.tree,null,2)+'\n');
await writeFile(new URL('apl-example.json',output), JSON.stringify({
  format:'arxo.fr-benefits-readme-evidence/1', spec:model.spec, worldHash:model.pin.worldHash,
  sdk:'@arxo/law@0.4.2', engine:'@arxo/law-engine@0.5.2', household,
  caseInput, query:{predicate:'aide_formule',args:[household,'?amount']}, readings,
},null,2)+'\n');
const C={ink:'#112f50',muted:'#425d78',line:'#ccd9e5',blue:'#215983',soft:'#f4f7fa',
  green:'#0b6e4f',greenSoft:'#e6f4ee',amber:'#83500c',amberSoft:'#fff4df'};
const esc = s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
const t=(x,y,s,size=23,color=C.ink,weight=400,mono=false)=>`<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${color}"${mono?' class="mono"':''}>${esc(s)}</text>`;
const box=(x,y,w,h,fill=C.soft)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="12" fill="${fill}"/>`;
const path=d=>`<path d="${d}" fill="none" stroke="${C.blue}" stroke-width="2.5" marker-end="url(#arrow)"/>`;
const svg=(height,title,description,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="600" height="${height}" viewBox="0 0 600 ${height}" role="img" aria-labelledby="title desc">
<title id="title">${esc(title)}</title><desc id="desc">${esc(description)}</desc>
<style>text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}</style>
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="${C.blue}"/></marker></defs>
<rect width="600" height="${height}" rx="14" fill="#ffffff"/>
${body.join('\n')}
</svg>\n`;
const first=readings[0];
await writeFile(new URL('model-to-answer.svg',output),svg(680,'From a pinned model to an answer with evidence',
 'loadModel returns one hash-checked linked world. Explicit facts, dates and readings enter separately as caseInput. The common SDK opens that world offline and asks aide_formule. The supplied APL probe returns a computed EUR 20.17 formula amount, with its canonical document, proof, sources and hashes.',[
 t(24,45,'From model to answer',31,C.ink,700),
 box(24,80,264,144),box(312,80,264,144),
 t(42,117,'loadModel()',24,C.blue,650,true),t(42,151,'Selected world',23,C.ink,600),
 t(42,184,'Included imports',20,C.muted),t(42,211,'Checked raw bytes',20,C.muted),
 t(330,117,'caseInput',24,C.blue,650,true),t(330,151,'Explicit inputs',23,C.ink,600),
 t(330,184,'Facts + dates',20,C.muted),t(330,211,'Selected reading',20,C.muted),
 path('M156 230 L156 260 L270 260 L270 296'),path('M444 230 L444 260 L330 260 L330 296'),
 box(24,308,552,149,'#eaf0f7'),t(48,345,'@arxo/law',27,C.blue,650,true),
 t(48,382,'open(... local.packages)',23,C.ink,500,true),t(48,418,"collect('aide_formule', ...)",23,C.ink,500,true),
 t(48,447,'Local WebAssembly execution',20,C.muted),path('M300 464 L300 492'),
 box(24,506,552,145,C.greenSoft),t(48,546,first.evaluationStatus,23,C.green,650,true),
 t(552,548,`${first.value[0].value} ${first.value[0].currency}`,27,C.green,750).replace('font-size','text-anchor="end" font-size'),
 t(48,587,'document · proof · sources · hashes',22,C.green,500),t(48,627,`${first.proofNodes} proof nodes in the shipped example`,20,C.green),
]));
const fork=[t(24,43,'Same facts. Explicit reading.',30,C.ink,700),
 t(24,82,'The shipped APL zero-rent probe',22,C.muted),
 t(24,116,`Legal date: ${caseInput.legalTime}`,20,C.muted)];
for(let i=0;i<readings.length;i++){
 const row=readings[i], y=146+i*164, color=row.reading?C.green:C.amber;
 fork.push(box(24,y,552,145,row.reading?C.greenSoft:C.amberSoft),
  t(44,y+37,row.reading??'No selected interpretation',23,C.ink,600,Boolean(row.reading)),
  t(44,y+75,row.evaluationStatus,20,color,600,true),
  t(44,y+119,row.value[0]?`${row.value[0].value} ${row.value[0].currency}`:'No amount',31,color,750));
}
fork.push(t(24,673,'Exact formula amounts in this technical case.',21,C.muted),
 t(24,708,'A formula result is separate from a payable benefit.',21,C.muted));
await writeFile(new URL('explicit-readings.svg',output),svg(740,'APL formula amounts under two explicit readings and no selection',
 'For the same zero-rent probe on 15 June 2024, PpPlancherFinal returns COMPUTED EUR 20.17; PpLitteral returns COMPUTED EUR 53.7338; without selection the status is INTERPRETATION_REQUIRED and no amount is returned.',fork));
const files=['cover.png','model-to-answer.svg','explicit-readings.svg','knows-apl.svg','apl-unfold.json','apl-example.json'];
const hashes={};for(const name of files){const bytes=await readFile(new URL(name,output));hashes[name]={bytes:bytes.length,sha256:`sha256:${createHash('sha256').update(bytes).digest('hex')}`};}
await writeFile(new URL('manifest.json',output),JSON.stringify({format:'arxo.fr-benefits-readme-assets/1',
 worldHash:model.pin.worldHash,files:hashes,
 cover:{repository:'https://github.com/arxohq/arxo-cnaf',revision:'ca4467cabe54e2a2e0b82fa19f832ca6c90bd61d',path:'docs/images/cover.png'},
 tree:{predicate:'aide_formule',depth:2,lang:'en',quote:0,caseSelected:false,readingSelected:false,
  reusedSvg:'docs/images/unfold-aide-formule.svg',matchedNativeJson:'docs/unfold/aide-formule.json'},
},null,2)+'\n');
console.log('README assets: pinned SDK answers and native unfold match; diagrams generated.');
