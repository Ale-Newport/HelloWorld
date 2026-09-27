import fs from 'node:fs';
import * as THREE from 'three';
import {readGLB} from '../read_glb.mjs';
import {RAPIER} from '../../preview/runtime/physics.js';
import {World2Catalog} from '../../preview/world2-catalog.js';
import {curatedLibrary} from '../../preview/assets/library.js';
import {buildWorldMap,terrainHeight} from '../../preview/world-map.js';
import {finishOcean} from '../../preview/ocean.js';
import {preparePlaneModel} from '../../preview/runtime/plane-visual.js';
// Only text/canvas drawing is inert. Scene geometry, source gameplay setup and
// Rapier are the actual application modules; the browser checks visual output.
export async function worldFixture(){
 const context=new Proxy({measureText:t=>({width:String(t).length*14}),createLinearGradient:()=>({addColorStop(){}}),createRadialGradient:()=>({addColorStop(){}})}, {get:(o,k)=>o[k]??(()=>{})});
 globalThis.document??={createElement:tag=>({width:512,height:512,getContext:()=>context,style:{},addEventListener(){},removeEventListener(){}})};globalThis.window??={location:{origin:'http://127.0.0.1:8844'},open(){}};globalThis.localStorage??={getItem:()=>null,setItem(){}};
 await RAPIER.init();const base=readGLB('exports/AlejandroWorld.glb').scene,world=readGLB('assets/environment/portfolio/models/world.glb').scene,vegetation=readGLB('assets/environment/portfolio/models/vegetation.glb').scene;
 // Match GLTFLoader's names before the same map factory runs. Its legacy
 // numeric map IDs depend on which named source groups the browser finds.
 base.traverse(node=>{node.name=THREE.PropertyBinding.sanitizeNodeName(node.name);});
 const interactions=JSON.parse(fs.readFileSync('assets/environment/portfolio/interactions.json')),manifest=JSON.parse(fs.readFileSync('assets/environment/portfolio/world-manifest.json')),catalog=new World2Catalog(world,vegetation,interactions,manifest),library=curatedLibrary(base),nav=JSON.parse(fs.readFileSync('exports/navigation.json'));
 const vehicles=[{id:'vehicle-corsair',name:'Corsair Plane',label:'Corsair Plane',category:'Vehicles',node:preparePlaneModel(readGLB('assets/vehicles/plane/corsair.glb').scene)}];
 const built=buildWorldMap(base,catalog,library,nav,vehicles);finishOcean(built.root,terrainHeight);
 return {...built,base,catalog,library:[...library,...vehicles],vehicles};
}
