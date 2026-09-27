import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {createRoad,rebuildRoadNetwork} from '../preview/roads/road-system.js';

const results=[];
function test(name,run){try{const data=run();results.push({name,passed:true,data});console.log('PASS',name,JSON.stringify(data));}catch(error){results.push({name,passed:false,error:error.stack});console.error('FAIL',name,error);}}
const root=new THREE.Group(),ring=createRoad({points:Array.from({length:16},(_,i)=>[60*Math.cos(i*Math.PI/8),.205,60*Math.sin(i*Math.PI/8)]),closed:true,width:7,type:'race'});
root.add(ring);rebuildRoadNetwork(root);
const branch=createRoad({points:[[-15,.205,0],[0,.205,0],[15,.205,0]],width:7});
test('A new road in a ring road’s empty centre preserves the outer asphalt, markings and curbs',()=>{const geometry=ring.geometry,children=ring.children.map(n=>n.geometry);root.add(branch);const started=performance.now();rebuildRoadNetwork(root);const ms=performance.now()-started;assert.strictEqual(ring.geometry,geometry);assert.deepEqual(ring.children.map(n=>n.geometry),children);branch.userData.road_points=JSON.stringify([[-15,.205,0],[0,.205,8],[15,.205,0]]);rebuildRoadNetwork(root);assert.strictEqual(ring.geometry,geometry);return {outerGeometryReused:true,createNetworkMs:ms};});
test('Moving into and out of the actual footprint rebuilds junctions exactly like forced regeneration',()=>{for(const z of [58,0]){const old=ring.geometry;branch.position.z=z;rebuildRoadNetwork(root);assert.notStrictEqual(ring.geometry,old);const state=[ring,branch].map(o=>({position:Array.from(o.geometry.attributes.position.array),indices:Array.from(o.geometry.index.array),children:o.children.filter(n=>n.geometry).map(n=>({part:n.userData.roadPart,position:Array.from(n.geometry.attributes.position.array)}))}));rebuildRoadNetwork(root,{force:true});const full=[ring,branch].map(o=>({position:Array.from(o.geometry.attributes.position.array),indices:Array.from(o.geometry.index.array),children:o.children.filter(n=>n.geometry).map(n=>({part:n.userData.roadPart,position:Array.from(n.geometry.attributes.position.array)}))}));assert.deepEqual(state,full);}return {enterAndExitRebuild:true,asphaltMarkingsCurbsMatchFullBuild:true};});
fs.mkdirSync('reports/v6',{recursive:true});fs.writeFileSync('reports/v6/road-dependencies-tests.json',JSON.stringify(results,null,2));if(results.some(r=>!r.passed))process.exitCode=1;
