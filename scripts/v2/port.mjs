import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';
const root=path.resolve(import.meta.dirname,'../..'),src=path.resolve(root,'../Portfolio'),ts=createRequire(src+'/package.json')('typescript');
const files={'physics/PhysicsVehicle':'PhysicsVehicle','world/VisualVehicle':'VisualVehicle','world/materials':'materials','world/geometry':'geometry','core/palette':'palette','core/Events':'Events','core/maths':'maths'};
for(const [file,out] of Object.entries(files)){
 const source=fs.readFileSync(`${src}/src/world/${file}.ts`,'utf8');fs.mkdirSync(`${root}/assets/source-code/portfolio/${path.dirname(file)}`,{recursive:true});fs.writeFileSync(`${root}/assets/source-code/portfolio/${file}.ts`,source);
 let js=ts.transpileModule(source,{compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022}}).outputText;
 js=js.replace(/from ['"](?:\.\.\/core\/|\.\/)(Events|maths|palette|materials|geometry)['"]/g,(_,f)=>`from './${f}.js'`);
 if(out==='PhysicsVehicle')js=js.replace('this.controller.setWheelBrake(i, brake);',"this.controller.setWheelBrake(i, brake * (this.controller.wheelGroundObject(i)?.userData?.surface_type === 'ice' ? 0.07 : 1));");
 fs.writeFileSync(`${root}/preview/runtime/${out}.js`,js);
}
fs.copyFileSync(`${src}/src/world2/World2Game.ts`,`${root}/assets/source-code/portfolio/World2Game.ts`);
for(const file of ['controls/TransformControls.js','exporters/GLTFExporter.js']){const to=`${root}/preview/vendor/three/examples/jsm/${file}`;fs.mkdirSync(path.dirname(to),{recursive:true});fs.copyFileSync(`${src}/node_modules/three/examples/jsm/${file}`,to);}
console.log('Copied exact vehicle implementation, visual vehicle and its local dependencies.');
