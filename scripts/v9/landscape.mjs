import fs from 'node:fs';import crypto from 'node:crypto';import assert from 'node:assert/strict';import * as T from 'three';
import {savedWorldFixture} from '../../tests/helpers/saved-world.mjs';
import {serializeWorldInstances} from '../../preview/world-instances.js';
import {isVisible} from '../../preview/map-model.js';
import {createTerrainQuery} from '../../preview/terrain-query.js';
import {createMeadow} from '../../preview/meadow-grass.js';
import {createCoast} from './coast.mjs';
const backup='backups/archipelago_before_landscape_20260928/editor-world.json',source=fs.readFileSync(backup),doc=JSON.parse(source),loadDoc=structuredClone(doc);delete loadDoc.states['v4:world'].data.mapTerrain;
const {root,editor}=await savedWorldFixture({document:loadDoc,assetDefinitionsPath:'backups/archipelago_before_landscape_20260928/asset-definitions.json'});
const additions=[],placement=[],coast=createCoast(doc.states['v4:world'].data.mapTerrain.operations);console.log('coast',coast.triangles);
let sequence=0;
function add(node,parent=root){const id='landscape:v9:'+String(++sequence).padStart(4,'0');let part=0;node.traverse(n=>{n.userData.aw_id=id+(part?'/'+part:'');part++;delete n.userData.deleted;delete n.userData.proceduralDerived;editor.registry.set(n.userData.aw_id,n);editor.baseline.set(n.userData.aw_id,{geometry:n.geometry,material:n.material});});node.userData.added=true;node.userData.landscapeV9=true;parent.add(node);additions.push(node);return node;}
add(coast.mesh);delete doc.states['v4:world'].data.mapTerrain;
doc.states['v4:world'].data.landscapeRevision={version:9,sourceSavedAt:doc.savedAt,backup,shore:'Continuous sand slopes with 12 m shallow shelf'};
// Restore the intended empty district, keeping the user's group transform.
const projects=editor.experiences.list().find(g=>g.name==='Projects District'&&isVisible(g));assert(projects&&projects.children.length===0);
const template=editor.experiences.previewTemplate('experience-template:projects');const prototype=template.children.find(n=>n.userData.world2Asset==='projects');assert(prototype);const board=editor.assetDefinitions.instantiate('world2:projects');board.scale.copy(prototype.scale);board.position.set(0,.025,0);board.quaternion.identity();board.scale.multiplyScalar(.64);board.updateMatrixWorld(true);const boardBounds=new T.Box3().setFromObject(board),center=boardBounds.getCenter(new T.Vector3());board.position.x=6-center.x;board.position.z=2-center.z;add(board,projects);projects.userData.entrancePoints=[{name:'Project boards',position:[6,0,12],direction:[0,0,1],kind:'path'}];doc.states[projects.userData.aw_id].data.entrancePoints=projects.userData.entrancePoints;
const report={backup,preservedStates:Object.keys(doc.states).length,terrainTriangles:coast.triangles,placements:placement,projectBoard:{id:board.userData.aw_id,scale:board.scale.toArray()}};
root.updateMatrixWorld(true);
// Reserve authored Experiences, walkways and props. The F1 track uses its
// triangle footprint so infields remain available without touching race lanes.
const obstacles=[],trackRoot=new T.Group();const boundsOf=n=>new T.Box3().setFromObject(n);
for(const n of root.children){if(!isVisible(n)||n===coast.mesh||n.userData.terrain||n.userData.sea||n.userData.proceduralDerived)continue;
 if(n.name==='F1 Circuit Complete'){n.traverse(m=>{if(!m.isMesh)return;const clone=new T.Mesh(m.geometry);clone.matrixAutoUpdate=false;clone.matrix.copy(m.matrixWorld);clone.userData.terrain=true;trackRoot.add(clone);});continue;}
 if(n.userData.worldExperience){for(const child of n.children)if(isVisible(child)){const b=boundsOf(child);if(!b.isEmpty())obstacles.push({id:child.userData.aw_id,b});}}
 else {const b=boundsOf(n);if(!b.isEmpty())obstacles.push({id:n.userData.aw_id,b});}
}
const raceQuery=createTerrainQuery(trackRoot),occupied=(x,z,r)=>obstacles.some(({b})=>x+r>b.min.x&&x-r<b.max.x&&z+r>b.min.z&&z-r<b.max.z)||[[0,0],[r,0],[-r,0],[0,r],[0,-r],[r*.71,r*.71],[-r*.71,r*.71],[r*.71,-r*.71],[-r*.71,-r*.71]].some(([dx,dz])=>raceQuery.heightAt(x+dx,z+dz)!==null);
const corridor=(x,z,r=0)=>Math.abs(x+69)<3+r||Math.abs(z-1)<3+r&&x<30||Math.abs(z-49)<3+r&&x<10||Math.abs(x-61)<3+r&&z>50;
let seed=907328;const random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
function place(def,x,z,scale=1,angle=0,clearance=1.4){const node=editor.assetDefinitions.instantiate(def);node.scale.multiplyScalar(scale);node.rotation.y=angle;node.position.set(x,.15,z);node.updateMatrixWorld(true);const b=boundsOf(node),r=Math.max(b.max.x-x,x-b.min.x,b.max.z-z,z-b.min.z);if(coast.sample(x,z)<r+4||occupied(x,z,r+clearance)||corridor(x,z,r))return false;add(node);obstacles.push({id:node.userData.aw_id,b});placement.push({id:node.userData.aw_id,name:node.name,x,z,r,clearance});return true;}
// Small intentional clusters: pines by the circuit/castle, blossom gardens in
// the centre and palms on the east coast. Wide continuous corridors stay free.
for(let z=-48;z<133;z+=7.5)for(let x=-127;x<111;x+=7.5){const px=x+(random()-.5)*3,pz=z+(random()-.5)*3;if(random()<.18)continue;const def=px>38||pz>107?'v4:palm-tree':pz<5||px<-72?'v4:pine':'v4:broadleaf-tree';const available=editor.assetDefinitions.get(def)?def:'v4:pine-tree';place(available,px,pz,.65+random()*.25,random()*Math.PI*2);}
for(let z=-43;z<131;z+=8)for(let x=-122;x<109;x+=8){if(random()<.48)continue;const px=x+(random()-.5)*4,pz=z+(random()-.5)*4;place('v4:flower-patch',px,pz,.85+random()*.35,random()*6.28,.65);}
for(const [x,z]of [[-78,-23],[-48,-18],[-53,70],[-73,83],[-45,109],[96,-8],[96,87],[30,111]]){place('v4:park-bench',x,z,.9,Math.PI/2,1.5);}
for(const [x,z]of [[-78,-32],[-56,-22],[-54,70],[-73,86]])place('v4:rock-cluster',x,z,.85,random()*6.28,1.2);
// Grass is a few spatial batches, never thousands of editor objects/colliders.
const batches=new Map();for(let i=0;i<125000;i++){const x=-133+random()*250,z=-59+random()*200;if(coast.materialAt(x,z)!=='Grass'||coast.sample(x,z)<6||occupied(x,z,.45))continue;const key=Math.floor(x/32)+':'+Math.floor(z/32);if(!batches.has(key))batches.set(key,[]);batches.get(key).push([x,.153,z,random()]);}
for(const [key,points]of batches){const mesh=createMeadow(points);mesh.name='Césped World2 · '+key;add(mesh);}
report.grass={batches:batches.size,blades:[...batches.values()].reduce((n,p)=>n+p.length,0)};report.raceFootprint= raceQuery.stats;report.addedObjects=additions.length;
// Persist only additions. Original JSON/textures and every existing pose remain
// byte-for-byte equivalent in state, except terrain metadata / district access.
for(const node of additions)node.traverse(n=>{doc.states[n.userData.aw_id]={parentId:n.parent?.userData.aw_id??null,name:n.name,p:n.position.toArray(),q:n.quaternion.toArray(),s:n.scale.toArray(),visible:n.visible,data:structuredClone(n.userData)};});
const encoded=serializeWorldInstances(editor,additions.filter(n=>n!==board));
const parts=[];const partOf=(n,path=[])=>{parts.push({path,id:n.userData.aw_id,uuid:n.uuid,state:{name:n.name,p:n.position.toArray(),q:n.quaternion.toArray(),s:n.scale.toArray(),visible:n.visible,data:structuredClone(n.userData),castShadow:n.castShadow,receiveShadow:n.receiveShadow,frustumCulled:n.frustumCulled,renderOrder:n.renderOrder,layers:n.layers.mask,matrixAutoUpdate:n.matrixAutoUpdate}});n.children.forEach((child,i)=>partOf(child,[...path,i]));};partOf(board);encoded.instanceRefs.push({schema:1,definitionId:'world2:projects',version:board.userData.assetDefinitionVersion,rootId:board.userData.aw_id,parentId:projects.userData.aw_id,parts});doc.added.push(...encoded.added);doc.instanceRefs??=[];doc.instanceRefs.push(...encoded.instanceRefs);
for(const node of additions.filter(n=>n.parent===projects))doc.experiences.parentLinks.push({id:node.userData.aw_id,parentId:projects.userData.aw_id,p:node.position.toArray(),q:node.quaternion.toArray(),s:node.scale.toArray()});
doc.savedAt=new Date().toISOString();const candidate='reports/v9/archipelago-candidate.json';fs.writeFileSync(candidate,JSON.stringify(doc));fs.writeFileSync('reports/v9/landscape.json',JSON.stringify(report,null,2));console.log(JSON.stringify({...report,placements:placement.length},null,2));
if(process.argv.includes('--install')){const target='exports/worlds/archipelago/editor-world.json',hash=b=>crypto.createHash('sha256').update(b).digest('hex');assert.equal(hash(fs.readFileSync(target)),hash(source),'User save changed during landscaping; refusing to overwrite.');fs.copyFileSync(candidate,target);console.log('Installed',target);}
