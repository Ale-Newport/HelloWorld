// One-time read-only migration; generated runtime has no Portfolio dependency.
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const root=path.resolve(import.meta.dirname,'..');
const source=path.resolve(root,'../Portfolio');
const require=createRequire(path.join(source,'package.json'));
const ts=require('typescript');
const entries=[['src/world/physics/PhysicsVehicle.ts','preview/runtime/PhysicsVehicle.js'],['src/world/core/Events.ts','preview/runtime/Events.js'],['src/world/core/maths.ts','preview/runtime/maths.js']];
for(const [from,to] of entries){
 let src=fs.readFileSync(path.join(source,from),'utf8');
 src=src.replaceAll("'../core/Events'","'./Events.js'").replaceAll("'../core/maths'","'./maths.js'");
 let js=ts.transpileModule(src,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
 if(to.includes('PhysicsVehicle'))js=js.replace('this.controller.setWheelBrake(i, brake);',"this.controller.setWheelBrake(i, brake * (this.controller.wheelGroundObject(i)?.userData?.surface_type === 'ice' ? 0.07 : 1));");
 if(to.includes('PhysicsVehicle'))js=js.replace('parameters: [1.5, 0.5, 0.9]','parameters: [1.5, 0.6, 0.9]').replace('position: { x: 0.1, y: -0.2, z: 0 }','position: { x: 0.1, y: -0.4, z: 0 }');
 fs.mkdirSync(path.dirname(path.join(root,to)),{recursive:true});fs.writeFileSync(path.join(root,to),js);
 fs.appendFileSync(path.join(root,'ASSET_SOURCES.md'),`\n- \`${to}\`: transpiled from \`../Portfolio/${from}\`; ice-specific brake multiplier added to vehicle.\n`);
}
