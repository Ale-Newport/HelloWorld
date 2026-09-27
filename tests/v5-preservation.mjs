import fs from 'node:fs';
import assert from 'node:assert/strict';
import {isDeepStrictEqual} from 'node:util';
import {createHash} from 'node:crypto';
import * as THREE from 'three';
import {savedWorldFixture} from './helpers/saved-world.mjs';
import {CIRCUIT_ID,TERRAIN_IDS,ACCESS_ID,circuitLandHeight} from '../scripts/v5/fit-world2-circuit.mjs';

// This suite reads both documents and their restored scenes; it never migrates
// or writes exports. Run after the integrated browser save/reload/export.
const BACKUP='backups/user_world_before_four_fixes_20260927_103401/exports';
const beforePath=BACKUP+'/editor-world.json',afterPath='exports/editor-world.json',beforeText=fs.readFileSync(beforePath,'utf8'),afterText=fs.readFileSync(afterPath,'utf8');
const before=JSON.parse(beforeText),after=JSON.parse(afterText),beforeDefsText=fs.readFileSync(BACKUP+'/asset-definitions.json','utf8'),afterDefsText=fs.readFileSync('exports/asset-definitions.json','utf8');
const beforeFixture=await savedWorldFixture({document:before,assetDefinitionsPath:BACKUP+'/asset-definitions.json'}),afterFixture=await savedWorldFixture({document:after});
const FOUNTAIN='v4:v4:circular-fountain:1',fountainChild=id=>id.startsWith(FOUNTAIN+'/');
const oldAddedIds=new Set(),walk=(o,fn)=>{fn(o);for(const child of o.children??[])walk(child,fn);};
for(const item of before.added)walk(item.object,o=>{if(o.userData?.aw_id)oldAddedIds.add(o.userData.aw_id)});
const orphans=new Set(Object.keys(before.states).filter(id=>id.startsWith('user:')&&!beforeFixture.registry.has(id)&&!oldAddedIds.has(id)));
const preserved=Object.keys(before.states).filter(id=>!fountainChild(id)&&!orphans.has(id));
const hash=value=>createHash('sha256').update(typeof value==='string'?value:JSON.stringify(value)).digest('hex');
const same=(a,b,label)=>assert(isDeepStrictEqual(a,b),label);
const close=(a,b,label,epsilon=1e-7)=>assert(Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=epsilon,`${label}: ${a} != ${b}`);
const results=[];
function test(name,fn){try{const data=fn();results.push({name,passed:true,data});console.log('PASS',name,JSON.stringify(data));}catch(error){results.push({name,passed:false,error:error.stack});console.error('FAIL',name,error.message);}}

test('Integrated save retains every pre-existing live ID and every user-added hierarchy',()=>{
 assert.equal(before.schema,2);assert.equal(after.schema,2);assert.equal(after.base,before.base);
 assert(after.states[ACCESS_ID]&&TERRAIN_IDS.every(id=>after.states[id]),'Circuit extension must already be integrated');
 assert.equal(after.states[FOUNTAIN]?.data?.fountainDesign,2,'Fountain migration must already be integrated');
 const missing=preserved.filter(id=>!after.states[id]);same(missing,[],'Previously existing states are missing: '+missing.slice(0,20).join(', '));
 for(const id of oldAddedIds)assert(afterFixture.registry.has(id),'User-added descendant missing from restored scene: '+id);
 const removed=Object.keys(before.states).filter(id=>!after.states[id]);assert(removed.every(id=>orphans.has(id)||fountainChild(id)),'Unapproved IDs were removed');
 assert.equal(after.instanceOverrides?.length??0,before.instanceOverrides?.length??0);
 return {beforeStates:Object.keys(before.states).length,afterStates:Object.keys(after.states).length,preservedIds:preserved.length,userAddedNodes:oldAddedIds.size,alreadyAbsentOrphans:orphans.size,removedStates:removed.length,beforeSHA256:hash(beforeText),afterSHA256:hash(afterText)};
});

test('User names, visibility, deletions and transforms are retained outside the exact circuit change',()=>{
 const mismatches=[];let fields=0;
 for(const id of preserved){const a=before.states[id],b=after.states[id];if(!b)continue;
  for(const field of ['name','p','q','s','visible']){if(id===CIRCUIT_ID&&(field==='p'||field==='s'))continue;fields++;if(!isDeepStrictEqual(a[field],b[field]))mismatches.push({id,name:a.name,field,before:a[field],after:b[field]});}
  if(!isDeepStrictEqual(a.data?.deleted,b.data?.deleted))mismatches.push({id,field:'deleted',before:a.data?.deleted,after:b.data?.deleted});
 }
 assert.equal(mismatches.length,0,'Unapproved authored changes: '+JSON.stringify(mismatches.slice(0,16)));
 const a=before.states[CIRCUIT_ID],b=after.states[CIRCUIT_ID];same(b.p,[-194,.15,173],'Circuit position');same(b.s,[1,1,1],'Circuit original 1:1 scale');same(b.q,a.q,'Circuit authored rotation');
 for(const field of ['p','q','s','name','visible'])same(after.states['v4:terrain'][field],before.states['v4:terrain'][field],'Main terrain '+field);
 return {checkedFields:fields,checkedDeletionFlags:preserved.length,circuitBefore:{p:a.p,q:a.q,s:a.s},circuitAfter:{p:b.p,q:b.q,s:b.s},terrainPoseUnchanged:true};
});

test('Authored road controls, material edits and physics choices survive save/reload',()=>{
 const protectedData=['roadDefinition','road_points','road_width','road_closed','road_network','rail_left','rail_right','road_conform','collision','physics_mode','mass','friction','restitution','linear_damping','angular_damping','gravity_scale','lock_translation','lock_rotation','physicsPreset','collisionSubtree','assetPhysicsEdited','assetInstanceOverride','assetDefinitionId','assetDefinitionVersion'];
 let roadCount=0,materialCount=0,physicsCount=0;
 for(const id of preserved){const a=before.states[id],b=after.states[id];if(!b)continue;
  if(a.materials){same(b.materials,a.materials,'Authored materials changed: '+id);materialCount++;}
  for(const field of protectedData){if(!(field in (a.data??{})))continue;same(b.data?.[field],a.data[field],`Authored ${field} changed: ${id}`);physicsCount++;}
  if(a.data?.roadDefinition)roadCount++;
 }
 return {roadDefinitions:roadCount,materialOverrides:materialCount,protectedSettings:physicsCount};
});

test('All user-edited geometry is unchanged outside the requested main-terrain extension',()=>{
 const checked=[];
 for(const id of preserved){if(id==='v4:terrain'||!before.states[id].geometry)continue;const a=before.states[id].geometry,b=after.states[id]?.geometry;for(const key of Object.keys(a))same(b?.[key],a[key],'Edited geometry field changed or lost: '+id+':'+key);same(Object.keys(b??{}).filter(key=>key!=='terrainCutSource').sort(),Object.keys(a).filter(key=>key!=='terrainCutSource').sort(),'Unexpected edited geometry fields: '+id);const source=beforeFixture.registry.get(id).geometry.userData.terrainCutSource;assert(source,'Backup terrain source topology missing: '+id);same(b?.terrainCutSource,{count:source.count,indices:source.indices},'New grid metadata must describe the original painted tile: '+id);checked.push({id,name:before.states[id].name,vertices:a.position.length/3,sha256:hash(a)});}
 assert(checked.length>=4,'Expected the four user-painted land tiles from the backup');
 return {objects:checked};
});

test('Main terrain changes only by raising the specified southwest shore; original grid and colours survive elsewhere',()=>{
 const oldMesh=beforeFixture.registry.get('v4:terrain'),newMesh=afterFixture.registry.get('v4:terrain'),a=oldMesh.geometry.attributes.position,b=newMesh.geometry.attributes.position,ac=oldMesh.geometry.attributes.color,bc=newMesh.geometry.attributes.color;
 const sourceCount=oldMesh.geometry.userData.terrainCutSource?.count??a.count,newCount=newMesh.geometry.userData.terrainCutSource?.count??b.count;
 assert.equal(newCount,sourceCount,'Original terrain grid must retain its vertices');const savedGeometry=after.states['v4:terrain'].geometry;assert.equal(savedGeometry?.position.length,sourceCount*3,'Save only authored terrain vertices, not regenerated shoreline vertices');same(savedGeometry.terrainCutSource,{count:sourceCount,indices:oldMesh.geometry.userData.terrainCutSource.indices},'Persist original terrain topology alongside brush values');
 let raised=0,unchanged=0;const sand=new THREE.Color(0xdac796),grass=new THREE.Color(0x86ad5f);
 for(let i=0;i<sourceCount;i++){
  const x=a.getX(i),old=a.getY(i),z=a.getZ(i),inArea=x<=-88&&z>=58,wanted=inArea?Math.max(old,circuitLandHeight(x,z)):old;
  assert.equal(b.getX(i),x,'Terrain X grid moved at '+i);assert.equal(b.getZ(i),z,'Terrain Z grid moved at '+i);close(b.getY(i),Math.fround(wanted),'Terrain height '+i);
  const changed=wanted>old+1e-7;if(changed){raised++;assert(inArea);const color=wanted<.04?sand:grass;for(let k=0;k<3;k++)close(bc.array[i*3+k],Math.fround(color.toArray()[k]),'Raised shore colour '+i+':'+k);}else{unchanged++;for(let k=0;k<3;k++)assert.equal(bc.array[i*3+k],ac.array[i*3+k],'Preserved terrain colour '+i+':'+k);}
 }
 assert(raised>0,'The authorized circuit land must actually be added');
 // Derived shoreline-intersection vertices are regenerated from the same grid.
 // Any vertex outside the extension must retain its original XYZ and colour.
 let derivedOutside=0;const outside=new Map();for(let i=sourceCount;i<a.count;i++)if(a.getX(i)>-88||a.getZ(i)<58){const k=[a.getX(i),a.getY(i),a.getZ(i),...ac.array.slice(i*3,i*3+3)].join(',');outside.set(k,(outside.get(k)||0)+1);derivedOutside++;}
 for(let i=sourceCount;i<b.count;i++)if(b.getX(i)>-88||b.getZ(i)<58){const k=[b.getX(i),b.getY(i),b.getZ(i),...bc.array.slice(i*3,i*3+3)].join(',');assert(outside.get(k)>0,'Unapproved derived shoreline change: '+k);outside.set(k,outside.get(k)-1);}
 assert([...outside.values()].every(n=>n===0),'Existing shoreline intersection vertices were lost outside the southwest extension');
 return {originalVertices:sourceCount,raisedSouthwestVertices:raised,unchangedOriginalVertices:unchanged,unchangedDerivedVertices:derivedOutside};
});

test('Existing added meshes keep their full geometry, material resources and descendant transforms',()=>{
 const currentById=new Map(after.added.map(o=>[o.object?.userData?.aw_id,o])),summaries=[];
 for(const original of before.added){const id=original.object.userData.aw_id,current=currentById.get(id);assert(current,'Added root missing: '+id);
  same(current.materials,original.materials,'Added materials changed: '+id);
  const geometryPayloads=item=>new Map((item.geometries??[]).map(({uuid,...payload})=>[uuid,payload]));
  const oldGeometry=geometryPayloads(original),newGeometry=geometryPayloads(current),payloadOrder=values=>[...values].sort((a,b)=>hash(a).localeCompare(hash(b)));
  same(payloadOrder(newGeometry.values()),payloadOrder(oldGeometry.values()),'Added geometry payload changed: '+id);
  // ObjectLoader creates a new THREE.Source UUID for an unchanged image.
  // Verify every texture-to-image association by its exact payload bytes and
  // all texture parameters; only the Source UUID itself is non-authored.
  const resources=item=>{const images=new Map((item.images??[]).map(({uuid,...payload})=>[uuid,payload]));return {textures:(item.textures??[]).map(t=>({...t,image:images.get(t.image)})),images:[...images.values()].sort((a,b)=>hash(a).localeCompare(hash(b)))};};
  same(resources(current),resources(original),'Added texture/image payload or association changed: '+id);
  const newNodes=new Map();walk(current.object,o=>newNodes.set(o.userData?.aw_id??o.uuid,o));let nodes=0;
  walk(original.object,a=>{const key=a.userData?.aw_id??a.uuid,b=newNodes.get(key);assert(b,'Added node missing: '+key);nodes++;
   for(const field of ['uuid','type','name','material','visible'])same(b[field],a[field],`Added ${field} changed: ${key}`);
   if(a.geometry){assert(oldGeometry.has(a.geometry)&&newGeometry.has(b.geometry),'Missing mesh geometry resource: '+key);same(newGeometry.get(b.geometry),oldGeometry.get(a.geometry),'Mesh geometry association changed: '+key);}else same(b.geometry,a.geometry,'Unexpected mesh geometry: '+key);
   if(key!==CIRCUIT_ID){assert.equal(b.matrix?.length??0,a.matrix?.length??0,'Added transform matrix size: '+key);for(let i=0;i<(a.matrix?.length??0);i++)close(b.matrix[i],a.matrix[i],'Added transform '+key+':'+i,1e-9);}
  });
  if(id===CIRCUIT_ID){const state=after.states[id],m=new THREE.Matrix4().compose(new THREE.Vector3(...state.p),new THREE.Quaternion(...state.q),new THREE.Vector3(...state.s));m.elements.forEach((v,i)=>close(current.object.matrix[i],v,'Circuit saved root matrix '+i,1e-9));}
  summaries.push({id,descendants:nodes,geometryResources:original.geometries?.length??0,resourceSHA256:hash([original.geometries,original.materials,original.textures,original.images])});
 }
 return {addedRoots:summaries};
});

test('Both customized dock and pier v3 definitions remain byte-identical to backup',()=>{
 const a=JSON.parse(beforeDefsText),b=JSON.parse(afterDefsText);same(b.definitions.map(d=>d.id).sort(),a.definitions.map(d=>d.id).sort(),'Asset definition set changed');
 const summaries=[];for(const id of ['v4:marina-dock','v4:pier']){const old=a.definitions.find(d=>d.id===id),now=b.definitions.find(d=>d.id===id);assert(old&&now);assert.equal(old.version,3);assert.equal(now.version,3);const expected=Buffer.from(JSON.stringify(old)),actual=Buffer.from(JSON.stringify(now));assert(expected.equals(actual),'Serialized asset definition bytes changed: '+id);summaries.push({id,version:now.version,bytes:actual.length,sha256:hash(actual.toString())});}
 return {definitions:summaries,completeFileByteEqual:Buffer.from(beforeDefsText).equals(Buffer.from(afterDefsText))};
});

test('Fountain replacement is confined to its original root and contains the complete new design',()=>{
 const old=before.states[FOUNTAIN],now=after.states[FOUNTAIN];for(const field of ['p','q','s','name','visible'])same(now[field],old[field],'Fountain root '+field);
 const children=Object.entries(after.states).filter(([id])=>fountainChild(id));assert.equal(children.length,57,'Expected all 57 new fountain pieces');
 const names=new Set(children.map(([,s])=>s.name));for(const name of ['Carved basin wall','Sculpted central pedestal','Scalloped upper bowl','Turquoise basin water','Upper pool','Crown water plume','Cascading stream 8'])assert(names.has(name),'Fountain piece missing: '+name);
 assert(!names.has('Basin stone'),'Old solid fountain body survived');assert.equal(now.data.fountainDesign,2);
 return {rootPosePreserved:true,replacedOldPieces:Object.keys(before.states).filter(fountainChild).length,newPieces:children.length};
});

fs.mkdirSync('reports/v5',{recursive:true});fs.writeFileSync('reports/v5/preservation-tests.json',JSON.stringify({backup:beforePath,current:afterPath,results},null,2));
if(results.some(r=>!r.passed))process.exitCode=1;
