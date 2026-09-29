import fs from 'node:fs';
import assert from 'node:assert/strict';
import {savedWorldFixture} from './helpers/saved-world.mjs';
import {applyTerrainOperation} from '../preview/map-terrain.js';
import {brushShape} from '../preview/map-brush.js';
import {surfaceMaterial,surfaceUV} from '../preview/surface-materials.js';
const {root,editor}=await savedWorldFixture({documentPath:'exports/worlds/archipelago/editor-world.json',assetDefinitionsPath:'exports/worlds/archipelago/asset-definitions.json'});
Object.assign(editor,{fillTransform(){},updateOutlines(){},notify(){}});
const samples=[];
for(let i=0;i<Number(process.argv[3]??4);i++){
 const op={kind:i%2?'erase':'add',polygons:brushShape([[260+(i%4)*3,110],[280+(i%4)*3,135],[305+(i%4)*3,145]],8),beachWidth:2};
 let start=performance.now();editor.startChange();const captureMs=performance.now()-start;start=performance.now();
 const result=applyTerrainOperation(root,op,{materialFactory:surfaceMaterial,uvFor:surfaceUV,deferShoreline:true});const terrainMs=performance.now()-start;start=performance.now();editor.endChange({terrainOnly:true,affectedBounds:result.affectedBounds});const endMs=performance.now()-start;assert.equal(result.replayedOperations,1);assert(result.triangles<220000,"Repeated strokes must not explode geometry");
 samples.push({kind:op.kind,captureMs,terrainMs,endMs,totalMs:captureMs+terrainMs+endMs,triangles:result.triangles,replayedOperations:result.replayedOperations});console.log(samples.at(-1));
}
fs.writeFileSync('reports/v8/'+(process.argv[2]??'timings')+'.json',JSON.stringify(samples,null,2));
