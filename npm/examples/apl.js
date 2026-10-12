/** Technical zero-rent probe, not a realistic benefit claim. */
import { readFileSync } from 'node:fs';
export const household = 'urn:fr:apl:case:fork-pp-below';
export const caseInput = JSON.parse(readFileSync(new URL('./apl-case.json', import.meta.url), 'utf8'));
