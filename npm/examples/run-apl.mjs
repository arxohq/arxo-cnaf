import { open } from '@arxo/law';
import { loadModel } from '@arxo/canon-fr-benefits/apl';
import { household, caseInput } from '@arxo/canon-fr-benefits/examples/apl';
const model = await loadModel();
const apl = await open(model.spec, {
  offline: true,
  local: { packages: { [model.spec]: model.package } },
});
const answer = await apl.collect('aide_formule', [household, '?amount'], caseInput);
console.log(JSON.stringify({ evaluationStatus: answer.evaluationStatus, value: answer.value,
  hashes: answer.hashes, proofNodes: answer.proof?.nodes?.length }, null, 2));
