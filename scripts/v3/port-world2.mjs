import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'../..');
const source=path.resolve(root,'../Portfolio');
const ts=createRequire(source+'/package.json')('typescript');
const out=root+'/preview/portfolio', provenance=root+'/assets/source-code/world2-port';
const seen=new Set(), manifest=[];
function port(rel){
 if(seen.has(rel))return;seen.add(rel);
 const file=source+'/src/'+rel, original=fs.readFileSync(file,'utf8');
 fs.mkdirSync(path.dirname(provenance+'/'+rel),{recursive:true});fs.writeFileSync(provenance+'/'+rel,original);
 let code=rel.endsWith('.json')?'export default '+original+';':ts.transpileModule(original,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
 // Runtime adaptations only: isolated storage, local imports and sea level.
 code=code.replace(/import \{ OCEAN_LEVEL \} from [^;]+;/,"const OCEAN_LEVEL = -1.2;");
 code=code.replaceAll("process.env.NODE_ENV === 'development'",'false');
 code=code.replaceAll('alejandro-world2-', 'helloworld-world2-');
 if(rel==='world2/World2Environment.ts')code=code.replace('this.bin.add(() => closeBitmaps(this.group));','// Image bitmaps belong to the persistent asset catalog, not one drive session.');
 code=code.replace(/from (['"])([^'"]+)\1/g,(match,quote,spec)=>{
  if(!spec.startsWith('.')&&!spec.startsWith('@/'))return match;
  const dependency=spec.startsWith('@/')?spec.slice(2):path.posix.normalize(path.posix.join(path.posix.dirname(rel),spec));
  const target=dependency.endsWith('.json')?dependency:fs.existsSync(source+'/src/'+dependency+'.ts')?dependency+'.ts':dependency+'/index.ts';port(target);
  let rewritten=path.posix.relative(path.posix.dirname(rel),target.replace(/\.(ts|json)$/,'.js'));if(!rewritten.startsWith('.'))rewritten='./'+rewritten;
  return 'from '+quote+rewritten+quote;
 });
 const dest=out+'/'+rel.replace(/\.(ts|json)$/,'.js');fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,code);
 manifest.push({source:rel,sourceSha256:crypto.createHash('sha256').update(original).digest('hex'),output:path.relative(root,dest),outputSha256:crypto.createHash('sha256').update(code).digest('hex')});
}
for(const rel of ['world/physics/PhysicsVehicle.ts','world/physics/Physics.ts','world/player/Player.ts','world/view/View.ts','world/input/Inputs.ts','world/core/Tween.ts','world/core/Disposal.ts','world/core/Ticker.ts','world/systems/Audio.ts','world2/World2Environment.ts','world2/interactions/Interactions.ts'])port(rel);
fs.mkdirSync(root+'/reports/v3',{recursive:true});fs.writeFileSync(root+'/reports/v3/source-port.json',JSON.stringify(manifest,null,2));
console.log('Ported',manifest.length,'source files without changing Portfolio.');
