import fs from 'node:fs';
import * as THREE from 'three';
import {worldFixture} from './world-v4.mjs';
import {WorldEditor} from '../../preview/editor.js';
import {AssetDefinitions,tagAssetParts} from '../../preview/asset-definitions.js';
import {authoringPreview} from '../../preview/world2-gameplay.js';
import {createTrackFurniture} from '../../preview/track-gameplay.js';

/** Node only: geometry/material settings use Three's real ObjectLoader. Image
 * URLs and dimensions are retained; no browser image rasterization is needed. */
export class SavedObjectLoader extends THREE.ObjectLoader {
 parseImages(images=[]){return Object.fromEntries(images.map(item=>{const decode=url=>{if(typeof url!=='string')return url?.data?{...url,data:new (globalThis[url.type]??Uint8Array)(url.data)}:null;let width=1,height=1;if(url.startsWith('data:image/png;base64,')){const b=Buffer.from(url.split(',')[1],'base64');width=b.readUInt32BE(16);height=b.readUInt32BE(20);}return {src:url,width,height};};return [item.uuid,new THREE.Source(Array.isArray(item.url)?item.url.map(decode):decode(item.url))];}));}
 async parseImagesAsync(images){return this.parseImages(images);}
}

/** Reconstruct the user's save with the same apply/replacement methods used by
 * WorldEditor. Does not write the save or asset definitions. */
export async function savedWorldFixture({documentPath='exports/editor-world.json',document:provided,assetDefinitionsPath='exports/asset-definitions.json'}={}){
 const fixture=await worldFixture(),{root,catalog}=fixture,doc=provided??JSON.parse(fs.readFileSync(documentPath,'utf8'));
 if(doc.schema!==2||doc.base!==root.userData.baseDocument)throw Error('Save does not match the generated base document');
 const furniture=createTrackFurniture(root),editor=Object.create(WorldEditor.prototype);Object.assign(editor,{root,catalog,registry:new Map(),baseline:new Map(),assetDefinitions:new AssetDefinitions(),selected:[],history:[],future:[],select(){},updateHistory(){},roadDiagnostics(){}});
 const index=(o,path='scene')=>{if(o.userData.proceduralDerived)return;o.userData.aw_id??=path;editor.registry.set(o.userData.aw_id,o);editor.baseline.set(o.userData.aw_id,{geometry:o.geometry,material:o.material});o.children.forEach((child,i)=>index(child,o.userData.aw_id+'/'+i));};index(root);
 for(const entry of catalog.entries){const node=catalog.template(entry);if(entry.feature){node.clear();node.add(authoringPreview(catalog,entry));}editor.assetDefinitions.add({id:'world2:'+entry.id,label:entry.label,category:entry.category,node});}
 for(const item of fixture.library)editor.assetDefinitions.add(item);
 if(furniture)for(const [key,id] of [['gantry','gantry'],['board','board'],['marker','marker']])editor.assetDefinitions.add({id:'v4:track-'+id,label:furniture[key].name,category:'Racing',node:furniture[key]});
 root.traverse(n=>{if(n.userData.world2Asset&&!n.userData.assetDefinitionId){const id='world2:'+n.userData.world2Asset;if(editor.assetDefinitions.get(id)){n.userData.assetDefinitionId=id;n.userData.assetDefinitionVersion=1;tagAssetParts(n);}}});
 const loader=new SavedObjectLoader();if(assetDefinitionsPath&&fs.existsSync(assetDefinitionsPath)){const saved=JSON.parse(fs.readFileSync(assetDefinitionsPath,'utf8'));for(const {object,...metadata} of saved.definitions){const node=loader.parse(object);tagAssetParts(node);editor.assetDefinitions.definitions.set(metadata.id,{...metadata,node});editor.assetDefinitions.modified.add(metadata.id);}}
 editor.refreshDefinitionInstances();
 for(const json of doc.added){const o=loader.parse(json);root.add(o);index(o);}
 for(const saved of doc.instanceOverrides??[]){const instance=editor.registry.get(saved.id);if(!instance)continue;const restored=loader.parse(saved.object),definition=editor.assetDefinitions.get(restored.userData.assetDefinitionId)??{id:restored.userData.assetDefinitionId,version:restored.userData.assetDefinitionVersion??1};editor.replaceAssetInstance(instance,{...definition,node:restored});instance.userData.assetInstanceOverride=true;}
 editor.apply(doc.states);editor.refreshDefinitionInstances();root.updateMatrixWorld(true);
 return {...fixture,root,editor,doc,definitions:editor.assetDefinitions,registry:editor.registry,missingStateIds:Object.keys(doc.states).filter(id=>!editor.registry.has(id))};
}
