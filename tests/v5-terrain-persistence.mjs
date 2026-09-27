import fs from 'node:fs';import assert from 'node:assert/strict';import {createHash} from 'node:crypto';
import {savedWorldFixture} from './helpers/saved-world.mjs';
import {updatePrefabTerrain} from '../preview/prefab-terrain.js';
const hash=a=>createHash('sha256').update(Buffer.from(a.buffer,a.byteOffset,a.byteLength)).digest('hex');
const f=await savedWorldFixture(),terrain=f.registry.get('v4:terrain'),baseline=f.editor.baseline.get('v4:terrain').geometry.clone(),serialized=f.doc.states['v4:terrain'].geometry,expected=baseline.userData.terrainCutSource?.count??baseline.attributes.position.count;
const results=[];function test(name,fn){try{const data=fn();results.push({name,passed:true,data});console.log('PASS',name,JSON.stringify(data));}catch(e){results.push({name,passed:false,error:e.stack});console.error('FAIL',name,e.message);}}
const original={position:hash(terrain.geometry.attributes.position.array),color:hash(terrain.geometry.attributes.color.array),index:hash(terrain.geometry.index.array),rendered:terrain.geometry.attributes.position.count},captures=[];
test('Existing edited main terrain restores the original grid instead of promoting shoreline vertices',()=>{assert.equal(expected,21509);assert.equal(terrain.geometry.userData.terrainCutSource.count,expected);assert.equal(original.rendered,25673);const state=f.editor.capture()['v4:terrain'].geometry;assert.equal(state.position.length,expected*3);assert.equal(state.terrainCutSource.count,expected);captures.push(state);return {previousSerializedVertices:serialized.position.length/3,originalGridVertices:expected,derivedShorelineVertices:original.rendered-expected,savedGridVertices:state.position.length/3};});
test('Two fresh-geometry save/apply cycles preserve topology, brush values and vertex count without growth',()=>{
 const cycles=[];for(let cycle=1;cycle<=2;cycle++){
  const states=JSON.parse(JSON.stringify(f.editor.capture()));terrain.geometry=baseline.clone();f.editor.baseline.set('v4:terrain',{geometry:terrain.geometry,material:terrain.material});f.editor.apply(states);updatePrefabTerrain(f.root,true);
  const g=terrain.geometry,state=f.editor.capture()['v4:terrain'].geometry;assert.equal(g.userData.terrainCutSource.count,expected);assert.equal(g.attributes.position.count,original.rendered);assert.equal(state.position.length/3,expected);assert.equal(hash(g.attributes.position.array),original.position);assert.equal(hash(g.attributes.color.array),original.color);assert.equal(hash(g.index.array),original.index);assert.deepEqual(state,captures[0]);cycles.push({cycle,sourceVertices:g.userData.terrainCutSource.count,renderedVertices:g.attributes.position.count,savedVertices:state.position.length/3,indexHash:hash(g.index.array)});
 }return {cycles};
});
fs.mkdirSync('reports/v5',{recursive:true});fs.writeFileSync('reports/v5/terrain-persistence-tests.json',JSON.stringify(results,null,2));if(results.some(r=>!r.passed))process.exitCode=1;
