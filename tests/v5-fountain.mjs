import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as THREE from 'three';
import {fountain} from '../preview/assets/fountain.js';
import {worldAnimationClips} from '../preview/world-animation.js';
import {collisionMeshes} from '../preview/runtime/physics.js';
import {savedWorldFixture} from './helpers/saved-world.mjs';
import {improveFountain,FOUNTAIN_ID} from '../scripts/v5/improve-fountain.mjs';
const source=JSON.parse(fs.readFileSync('backups/user_world_before_four_fixes_20260927_103401/exports/editor-world.json','utf8'));
const document=improveFountain(source),results=[];
const test=async(name,run)=>{try{const evidence=await run();results.push({name,passed:true,evidence});console.log('PASS',name);}catch(error){results.push({name,passed:false,error:error.stack});console.error('FAIL',name,error);}};
await test('Fountain upgrade preserves every unrelated saved state, custom asset and root transform',()=>{
 for(const [id,state]of Object.entries(source.states))if(id!==FOUNTAIN_ID&&!id.startsWith(FOUNTAIN_ID+'/'))assert.deepEqual(document.states[id],state,id);
 for(const key of ['p','q','s','name','visible'])assert.deepEqual(document.states[FOUNTAIN_ID][key],source.states[FOUNTAIN_ID][key]);
 assert.deepEqual(document.added,source.added);assert.deepEqual(document.instanceOverrides,source.instanceOverrides);assert.deepEqual(improveFountain(document),document);
 return {unrelatedStates:Object.keys(document.states).length-1,rootPosePreserved:true,idempotent:true};
});
await test('Saved world restores the new hollow basins without old child transforms overwriting them',async()=>{
 const {registry}=await savedWorldFixture({document});const node=registry.get(FOUNTAIN_ID),box=new THREE.Box3().setFromObject(node),size=box.getSize(new THREE.Vector3());
 assert(node.getObjectByName('Carved basin wall'));assert(node.getObjectByName('Scalloped upper bowl'));assert.equal(node.userData.fountainDesign,2);assert.equal(node.children.length,fountain().children.length);
 assert(Math.abs(size.x-10.26)<.02);assert(size.y>4.6&&size.y<5);assert.deepEqual(node.getObjectByName('Turquoise basin water').position.toArray(),[0,.57,0]);
 return {size:size.toArray(),parts:node.children.length};
});
await test('Water animation stays inside the basin and never adds invisible collision',()=>{
 const node=fountain(),colliders=new Set(collisionMeshes(node)),clips=worldAnimationClips(node),mixer=new THREE.AnimationMixer(node);clips.forEach(c=>mixer.clipAction(c).play());
 assert.equal(clips.length,25);const jets=node.children.filter(n=>n.userData.animation);for(const jet of jets)assert(!colliders.has(jet));
 assert(!colliders.has(node.getObjectByName('Turquoise basin water')));assert(colliders.has(node.getObjectByName('Carved basin wall')));
 for(let i=0;i<240;i++){mixer.update(1/60);for(const jet of jets)assert(jet.scale.toArray().every(n=>Number.isFinite(n)&&n>.85&&n<1.15));}
 const lights=node.children.filter(n=>n.isLight);assert.equal(lights.length,4);assert(lights.every(n=>n.userData.nightReady&&!n.visible));mixer.stopAllAction();
 return {waterClips:clips.length,solidMeshes:colliders.size,nightLights:lights.length};
});
await test('Hidden objects cannot create animation channels referencing nodes omitted from GLB',()=>{
 const root=new THREE.Group(),visible=fountain(),hidden=fountain();hidden.visible=false;root.add(visible,hidden);
 assert.equal(worldAnimationClips(root).length,25);visible.getObjectByName('Crown water plume').visible=false;assert.equal(worldAnimationClips(root).length,24);
 return {hiddenAssetExcluded:true,hiddenChildExcluded:true};
});
fs.mkdirSync('reports/v5',{recursive:true});fs.writeFileSync('reports/v5/fountain-tests.json',JSON.stringify(results,null,2));if(results.some(r=>!r.passed))process.exitCode=1;
