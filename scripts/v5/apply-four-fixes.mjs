import fs from 'node:fs';
import crypto from 'node:crypto';
import {savedWorldFixture} from '../../tests/helpers/saved-world.mjs';
import {fitWorld2Circuit} from './fit-world2-circuit.mjs';
import {improveFountain} from './improve-fountain.mjs';

const file='exports/editor-world.json',raw=fs.readFileSync(file),original=JSON.parse(raw);
const fixture=await savedWorldFixture({document:original});
const result=fitWorld2Circuit(fixture,{document:improveFountain(original)});
// Fail rather than overwrite a save made while geometry was being rebuilt.
if(!fs.readFileSync(file).equals(raw))throw Error('World was saved during migration. Run again on the latest save.');
result.document.savedAt=new Date().toISOString();
fs.mkdirSync('reports/v5',{recursive:true});
fs.writeFileSync('reports/v5/circuit-fit-report.json',JSON.stringify(result.report,null,2));
fs.writeFileSync(file+'.tmp',JSON.stringify(result.document));fs.renameSync(file+'.tmp',file);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
fs.writeFileSync('reports/v5/applied-migration.json',JSON.stringify({before:sha(raw),after:sha(fs.readFileSync(file)),appliedAt:result.document.savedAt,backup:'backups/user_world_before_four_fixes_20260927_103401',changedExisting:[...result.report.changedExistingStates,'v4:v4:circular-fountain:1'],added:result.report.createdIds},null,2));
console.log('Saved full-scale World2 circuit, sculptable island extension and new fountain. Other authored states preserved.');
