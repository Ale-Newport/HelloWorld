import {spawnSync} from 'node:child_process';
import fs from 'node:fs';

// Saved-world fixtures hold the complete island. Run sequentially to avoid
// competing with the browser for memory during local verification.
const suites=['map-surfaces','terrain-query','road-dependencies','map-terrain','world-instances','experiences','map-model','editor-history','state-coverage','map-controls'];
const results=[];
for(const suite of suites){
 console.log(`\nV6 ${suite}`);
 const start=Date.now(),run=spawnSync(process.execPath,['--loader','./tests/local-loader.mjs',`tests/v6-${suite}.mjs`],{stdio:'inherit'});
 results.push({suite,passed:run.status===0,seconds:(Date.now()-start)/1000,...(run.error?{error:run.error.message}:{})});
}
fs.mkdirSync('reports/v6',{recursive:true});
fs.writeFileSync('reports/v6/suite-summary.json',JSON.stringify({checkedAt:new Date().toISOString(),suites:results},null,2)+'\n');
if(results.some(r=>!r.passed))process.exitCode=1;
