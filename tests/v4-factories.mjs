import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {readGLB} from './read_glb.mjs';
import {curatedLibrary} from '../preview/assets/library.js';
import {waterFeature} from '../preview/assets/coast.js';
import {palette} from '../preview/assets/kit.js';
import {Physics,RAPIER,collisionMeshes,hasDisabledCollisionAncestor} from '../preview/runtime/physics.js';

const results=[];
async function test(name,fn){try{const evidence=await fn();results.push({name,passed:true,evidence});console.log('PASS',name,JSON.stringify(evidence));}catch(error){results.push({name,passed:false,error:error.stack});console.error('FAIL',name,error);}}
const base=readGLB('exports/AlejandroWorld.glb').scene;
// GLTFLoader sanitizes authoring spaces; the headless GLB reader deliberately does not.
base.traverse(n=>n.name=n.name.replaceAll(' ','_'));
const entries=curatedLibrary(base),byName=name=>entries.find(e=>e.label===name).node;
await test('All 118 curated definitions build with browser-sanitized source names, finite geometry and collider coverage',()=>{
 assert.equal(entries.length,118);assert.equal(new Set(entries.map(e=>e.id)).size,entries.length);let meshes=0,vertices=0;
 for(const e of entries){const root=e.node,size=new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());assert(size.toArray().every(v=>Number.isFinite(v)&&v>0),e.label);assert.equal(root.userData.assetDefinitionVersion,1,e.label);assert.equal(root.userData.groundAnchor,0,e.label);assert.equal(root.userData.assetDefinitionId,e.id);assert(root.name&&e.category);if(root.userData.collision)assert(collisionMeshes(root).length,`${e.label} has no collider geometry`);root.traverse(n=>{if(!n.isMesh)return;meshes++;const p=n.geometry.attributes.position;vertices+=p.count;assert(Array.from(p.array).every(Number.isFinite),n.name);if(n.geometry.attributes.normal)assert(Array.from(n.geometry.attributes.normal.array).every(Number.isFinite),n.name);});}
 return {definitions:entries.length,meshes,vertices,reusedAboutPavilion:!!byName('About Pavilion')};
});
await test('Every lake/channel has upward surfaces, continuous shore normals and a reversible terrain-cut contour',()=>{
 const kinds=['Pond Small','Pond Medium','Natural Lake','Decorative Lake','Frozen Lake','Canal Straight','Canal Curved','Stream'];const shapes=[];
 for(const name of kinds){const n=byName(name),water=n.getObjectByName('Water surface')??n.getObjectByName('Ice surface'),shore=n.getObjectByName('Sloping shoreline');assert.equal(n.userData.collision,false);assert(n.userData.terrainCut.contour.length>=32);for(let i=0;i<water.geometry.attributes.normal.count;i++)assert(water.geometry.attributes.normal.getY(i)>.999);for(let i=0;i<shore.geometry.attributes.normal.count;i++)assert(shore.geometry.attributes.normal.getY(i)>0,`${name} inverted shore`);shapes.push({name,points:n.userData.terrainCut.contour.length});}
 const curved=byName('Canal Curved').userData.terrainCut.contour;let concave=0;for(let i=0;i<curved.length;i++){const a=curved[i],b=curved[(i+1)%curved.length],c=curved[(i+2)%curved.length];if((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0])<-.00001)concave++;}assert(concave>20,'Curved channel must have an inner concave bank rather than an ellipse');
 const rebuilt=waterFeature('Canal Curved',{width:7,length:27,depth:2.1,bendDegrees:125,shoreMaterial:'Stone Light',vegetation:false,rocks:false});assert.equal(rebuilt.userData.parameters.depth,2.1);assert.equal(rebuilt.getObjectByName('Sloping shoreline').material.color.getHex(),palette.stoneLight);return {shapes,curvedInnerBankVertices:concave,parameterRebuild:true};
});
await test('Red suspension bridge has a road deck and animated parts are excluded from static collision',()=>{
 const bridge=byName('Red Suspension Bridge');assert.equal(bridge.getObjectByName('Deck').material.color.getHex(),palette.asphalt);assert(!bridge.children.some(n=>n.name.startsWith('Deck plank')));assert(bridge.children.some(n=>n.name.startsWith('Centre road marking')));
 const ferris=byName('Ferris Wheel');let rotor;ferris.traverse(n=>{if(/rotor/i.test(n.name))rotor=n;});assert(rotor);assert.equal(collisionMeshes(rotor).length,0);assert(hasDisabledCollisionAncestor(rotor.children[0]));assert(collisionMeshes(ferris).length>0);const wind=byName('Windmill').getObjectByName('Windmill sails');assert.equal(collisionMeshes(wind).length,0);
 let lights=0;for(const entry of entries)entry.node.traverse(n=>{if(n.isLight){lights++;assert(!n.visible||n.intensity===0,`${entry.label} has a daylight light`);}});return {redDeck:'asphalt',rotorExcluded:true,staticFerrisMeshes:collisionMeshes(ferris).length,disabledDaylightLights:lights};
});
await RAPIER.init();
await test('No Collision ancestors and explicitly edited bodies never leak into their parent collider',()=>{
 const root=new THREE.Group();root.userData.collision=true;const box=()=>new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial());const fixed=box();fixed.userData.collision=true;root.add(fixed);const child=box();child.userData={collision:true,assetPhysicsEdited:true,physics_mode:'DYNAMIC',mass:2};root.add(child);const none=new THREE.Group();none.userData={physicsPreset:'No Collision',collision:false};const nested=box();nested.userData.collision=true;none.add(nested);root.add(none);assert.deepEqual(collisionMeshes(root),[fixed]);assert.deepEqual(collisionMeshes(child),[child]);assert(hasDisabledCollisionAncestor(nested));const physics=new Physics();try{assert.equal(physics.mesh(root).colliders.length,1);assert.equal(physics.mesh(child).colliders.length,1);assert.equal(physics.world.bodies.len(),2);}finally{physics.destroy();}return {parentMeshes:1,independentBodies:2,disabledSubtree:true};
});
await test('Nested dynamic child retains transformed hierarchy during simulation and authored pose after stop',()=>{
 const scene=new THREE.Group(),parent=new THREE.Group();parent.position.set(8,3,-12);parent.rotation.y=.7;parent.scale.setScalar(1.4);scene.add(parent);const child=new THREE.Mesh(new THREE.BoxGeometry(1,1,1),new THREE.MeshBasicMaterial());child.position.set(2,4,-3);child.rotation.y=.2;child.scale.set(1,.8,1.2);child.userData={collision:true,physics_mode:'DYNAMIC',mass:2,assetPhysicsEdited:true};parent.add(child);const p=child.position.toArray(),q=child.quaternion.toArray(),s=child.scale.toArray();const physics=new Physics();physics.scene=scene;const body=physics.mesh(child);assert.equal(child.parent,parent);body.body.setLinvel({x:2,y:3,z:-1},true);for(let i=0;i<12;i++)physics.step();physics.render(1);assert.equal(child.parent,parent);const world=child.getWorldPosition(new THREE.Vector3());assert(world.distanceTo(body.current.position)<1e-6);physics.destroy();assert.equal(child.parent,parent);assert.deepEqual(child.position.toArray(),p);assert.deepEqual(child.quaternion.toArray(),q);assert.deepEqual(child.scale.toArray(),s);return {parentRetained:true,bodyWorldPosition:world.toArray(),authoringPoseRestored:true};
});
await test('Frozen lake creates an independent physical ice surface with ice grip metadata',()=>{
 const lake=byName('Frozen Lake'),physics=new Physics();const ice=lake.getObjectByName('Ice surface');let body;try{body=physics.mesh(ice);assert(body);assert.equal(body.colliders[0].userData.surface_type,'ice');assert(Math.abs(body.colliders[0].friction()-.025)<1e-6);assert.equal(body.colliders.length,1);physics.mesh(lake.getObjectByName('Lake bed'));physics.mesh(lake.getObjectByName('Sloping shoreline'));assert.equal(physics.world.bodies.len(),3);return {separateBodies:3,iceFriction:body.colliders[0].friction(),surface:body.colliders[0].userData.surface_type};}finally{physics.destroy();}
});
fs.mkdirSync('reports/v4',{recursive:true});fs.writeFileSync('reports/v4/factory-tests.json',JSON.stringify(results,null,2));if(results.some(r=>!r.passed))process.exitCode=1;
