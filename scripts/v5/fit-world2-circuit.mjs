import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import * as THREE from 'three';
import {savedWorldFixture} from '../../tests/helpers/saved-world.mjs';
import {assetBounds} from '../../preview/asset-definitions.js';
import {createRoad,rebuildRoadNetwork,roadGeometryData} from '../../preview/roads/road-system.js';
import {terrainHeight,segmentDistance} from '../../preview/world-map.js';

export const CIRCUIT_ID='user:3c9aed52-39b1-4a24-971b-2cef1903014f';
export const EXTENSION_BOUNDS={minX:-332,maxX:145,minZ:-125,maxZ:280};
export const ACCESS_ID='user:v5:world2-circuit-access';
export const TERRAIN_IDS=['user:v5:world2-circuit-land-west','user:v5:world2-circuit-land-south'];
const copy=x=>JSON.parse(JSON.stringify(x)),smooth=t=>{t=THREE.MathUtils.clamp(t,0,1);return t*t*(3-2*t);};
const visible=o=>{for(let p=o;p;p=p.parent)if(!p.visible||p.userData.deleted)return false;return true;};
export function circuitLandHeight(x,z){
 const qx=Math.abs(x+210)-79,qz=Math.abs(z-166.5)-68.5;
 const island=24-(Math.hypot(Math.max(qx,0),Math.max(qz,0))+Math.min(Math.max(qx,qz),0));
 const neck=17-Math.min(segmentDistance(x,z,[-107,76],[-110,98]),segmentDistance(x,z,[-110,98],[-153,134])),d=Math.max(island,neck);
 return d>=8?.15:d>=0?-.12+.27*smooth(d/8):Math.max(-7,-.12+d*.16);
}
function terrainBand(name,id,minX,maxX,minZ,maxZ){
 const positions=[],colors=[],indices=[],nx=(maxX-minX)/2,nz=(maxZ-minZ)/2;
 for(let j=0;j<=nz;j++)for(let i=0;i<=nx;i++){const x=minX+i*2,z=minZ+j*2,y=Math.max(terrainHeight(x,z),circuitLandHeight(x,z)),c=new THREE.Color(y<.04?0xdac796:0x86ad5f);positions.push(x,y,z);colors.push(c.r,c.g,c.b);if(i<nx&&j<nz){const a=j*(nx+1)+i;indices.push(a,a+nx+1,a+1,a+1,a+nx+1,a+nx+2);}}
 const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));g.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));g.setIndex(indices);g.computeVertexNormals();g.computeBoundingBox();g.computeBoundingSphere();
 const mesh=new THREE.Mesh(g,new THREE.MeshStandardMaterial({vertexColors:true,roughness:1,side:THREE.DoubleSide}));mesh.name=name;mesh.userData={aw_id:id,added:true,editable_root:true,terrain:true,sculptable:true,landTile:id,ground_surface:true,surface_type:'terrain',collision:true,physics_mode:'STATIC',geometryEdited:true,circuitExtension:true,worldBounds:EXTENSION_BOUNDS};return mesh;
}
function stateFor(o){return {name:o.name,p:o.position.toArray(),q:o.quaternion.toArray(),s:o.scale.toArray(),visible:o.visible,data:copy(o.userData)};}

/** Pure document migration. Geometry in the supplied fixture is changed for
 * verification, but neither exports nor source asset definitions are written.
 * All unrelated saved states and all existing added descendants are preserved. */
export function fitWorld2Circuit(fixture,{document=fixture.doc}={}){
 const doc=copy(document),{root,registry}=fixture,circuit=registry.get(CIRCUIT_ID),originalState=doc.states[CIRCUIT_ID];
 if(!circuit||circuit.userData.world2Asset!=='circuit'||!originalState)throw Error('Expected the user-authored World2 circuit instance');
 if(doc.states[ACCESS_ID])throw Error('This document already contains the circuit extension');
 const before={position:copy(originalState.p),scale:copy(originalState.s),quaternion:copy(originalState.q)};
 circuit.scale.set(1,1,1);circuit.position.set(-194,.15,173);circuit.updateWorldMatrix(true,true);
 const circuitBounds=assetBounds(circuit),overlaps=[];
 for(const o of root.children){if(o===circuit||!visible(o)||o.userData.terrain||o.userData.sea||o.userData.unselectable)continue;const b=assetBounds(o);if(b.max.x>circuitBounds.min.x&&b.min.x<circuitBounds.max.x&&b.max.z>circuitBounds.min.z&&b.min.z<circuitBounds.max.z)overlaps.push({id:o.userData.aw_id,name:o.name});}
 if(overlaps.length)throw Error('Circuit placement overlaps saved world objects: '+JSON.stringify(overlaps));
 doc.states[CIRCUIT_ID]={...originalState,p:circuit.position.toArray(),s:[1,1,1]};
 const savedCircuit=doc.added.find(json=>json.object?.userData?.aw_id===CIRCUIT_ID);if(!savedCircuit)throw Error('Circuit is not a saved added instance');circuit.updateMatrix();savedCircuit.object.matrix=circuit.matrix.toArray();
 const ground=registry.get('v4:terrain');if(!ground?.isMesh)throw Error('Main terrain not found');
 const sourceState=doc.states['v4:terrain'],position=ground.geometry.attributes.position,color=ground.geometry.attributes.color,count=ground.geometry.userData.terrainCutSource?.count??position.count;
 const values=Array.from(position.array.slice(0,count*3)),colors=Array.from(color.array.slice(0,count*3));let raised=0;
 for(let i=0;i<count;i++){const x=values[i*3],z=values[i*3+2];if(x> -88||z<58)continue;const previous=values[i*3+1],next=Math.max(previous,circuitLandHeight(x,z));if(next<=previous+1e-7)continue;values[i*3+1]=next;position.setY(i,next);const c=new THREE.Color(next<.04?0xdac796:0x86ad5f);colors.splice(i*3,3,c.r,c.g,c.b);color.setXYZ(i,c.r,c.g,c.b);raised++;}
 position.needsUpdate=color.needsUpdate=true;ground.geometry.computeVertexNormals();ground.geometry.computeBoundingBox();ground.geometry.computeBoundingSphere();
 doc.states['v4:terrain']={...sourceState,data:{...sourceState.data,geometryEdited:true},geometry:{position:values,color:colors}};
 const west=terrainBand('Circuit island · western extension',TERRAIN_IDS[0],-332,-156,58,280),south=terrainBand('Circuit island · southern extension',TERRAIN_IDS[1],-156,-88,136,280);
 const road=createRoad({id:ACCESS_ID,type:'road',width:6.4,points:[[-107,.205,76],[-108,.205,86],[-110,.205,98],[-128,.205,114],[-153,.205,134],[-184,.205,146],[-193,.19,153],[-194,.18,158],[-194,.17,161.3]],rails:{left:false,right:false}},{name:'World2 circuit · access road'});road.userData={...road.userData,aw_id:ACCESS_ID,added:true,editable_root:true,circuitAccess:true};
 root.add(west,south,road);root.updateMatrixWorld(true);rebuildRoadNetwork(root);
 const created=[west,south,road];for(const o of created){doc.added.push(o.toJSON());doc.states[o.userData.aw_id]=stateFor(o);registry.set(o.userData.aw_id,o);}
 const height=(x,z)=>Math.max(terrainHeight(x,z),circuitLandHeight(x,z));
 const report={circuitId:CIRCUIT_ID,before,after:{position:circuit.position.toArray(),scale:circuit.scale.toArray(),quaternion:circuit.quaternion.toArray()},circuitBounds:{min:circuitBounds.min.toArray(),max:circuitBounds.max.toArray(),size:circuitBounds.getSize(new THREE.Vector3()).toArray()},obstacleOverlaps:overlaps,raisedMainTerrainVertices:raised,createdIds:created.map(o=>o.userData.aw_id),changedExistingStates:[CIRCUIT_ID,'v4:terrain'],bounds:EXTENSION_BOUNDS,accessPoints:roadGeometryData(road).samples.map(s=>s.p.toArray())};
 return {document:doc,report,circuit,road,terrain:[ground,west,south],height,fixture};
}

if(process.argv[1]&&import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href){
 const fixture=await savedWorldFixture(),result=fitWorld2Circuit(fixture),out=process.argv[2]??'reports/v5/circuit-fit-proposed.json';
 if(path.resolve(out).startsWith(path.resolve('exports')+path.sep))throw Error('Write review output outside exports; root applies the integrated migration');
 fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,JSON.stringify(result.document));fs.writeFileSync('reports/v5/circuit-fit-report.json',JSON.stringify(result.report,null,2));console.log(JSON.stringify({...result.report,accessPoints:result.report.accessPoints.length,output:out},null,2));
}
