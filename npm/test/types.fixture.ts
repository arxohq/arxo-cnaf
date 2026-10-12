import { open } from '@arxo/law';
import { loadModel, models } from '@arxo/canon-fr-benefits';
import { loadModel as loadApl } from '@arxo/canon-fr-benefits/apl';
import { caseInput, household } from '@arxo/canon-fr-benefits/examples/apl';
const model = await loadApl();
const apl = await open(model.spec, { offline: true, local: { packages: { [model.spec]: model.package } } });
await apl.collect('aide_formule', [household, '?amount'], caseInput);
// @ts-expect-error model relation names are generated from the pinned IR
await apl.collect('not_a_model_relation', [household], caseInput);
// @ts-expect-error exact published model specs only
await loadModel('fr.apl@9.9.9');
for (const row of models) await loadModel(row.spec);

await apl.collect('fr.tax.income_for_apl::deduction_forfaitaire_plafond_courant', [household, '?r'], caseInput);
// @ts-expect-error imported relation spelling is checked too
await apl.collect('fr.tax.income_for_apl::not_declared', [], caseInput);
