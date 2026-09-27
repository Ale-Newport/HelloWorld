import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {savedWorldFixture} from './helpers/saved-world.mjs';

const backupPath='backups/world_before_map_editor_20260927/exports/editor-world.json',backup=JSON.parse(fs.readFileSync(backupPath,'utf8'));
const fixture=await savedWorldFixture(),{doc,registry}=fixture;
const missingBackupIds=Object.keys(backup.states).filter(id=>!registry.has(id));
assert.deepEqual(missingBackupIds,[],'Every pre-v6 authored state must exist in the browser-equivalent scene');
const tombstones=fixture.missingStateIds.map(id=>({id,name:doc.states[id].name,added:!!doc.states[id].data.added,deleted:!!doc.states[id].data.deleted,preV6:id in backup.states}));
assert(tombstones.every(s=>s.added&&s.deleted&&!s.preV6),'A live or pre-v6 saved object is missing from the scene');
const apron=registry.get('v4:map:199'),foam=registry.get('v4:world/550');
assert(apron?.isMesh);assert.equal(apron.name,'Aircraft parking apron');assert.deepEqual(apron.position.toArray(),[128,.18,100]);assert.deepEqual(apron.scale.toArray(),[14,.06,12]);assert(apron.userData.collision);
const bounds=new THREE.Box3().setFromObject(apron),size=bounds.getSize(new THREE.Vector3());assert(size.distanceTo(new THREE.Vector3(14,.06,12))<1e-7);
assert(foam?.isLineSegments);assert.equal(foam.name,'Shoreline foam');assert(foam.userData.derivedWater);assert(foam.geometry.attributes.position.count>0);assert.deepEqual(foam.position.toArray(),[0,0,0]);
const report={passed:true,backup:backupPath,savedAt:doc.savedAt,backupStates:Object.keys(backup.states).length,currentStates:Object.keys(doc.states).length,registry:registry.size,missingBackupIds,currentDeletedTombstones:tombstones,cause:'The Node fixture omitted finishOcean and used unsanitized base GLB names. Unlike browser GLTFLoader, its raw names created an extra pit group, shifting numeric IDs after that group.',fix:'tests/helpers/world-v4.mjs now sanitizes base names using THREE.PropertyBinding.sanitizeNodeName and runs finishOcean before indexing, matching preview/main.js.',verified:[{id:apron.userData.aw_id,name:apron.name,type:apron.type,position:apron.position.toArray(),dimensions:size.toArray(),physical:apron.userData.collision},{id:foam.userData.aw_id,name:foam.name,type:foam.type,position:foam.position.toArray(),lineVertices:foam.geometry.attributes.position.count,derivedWater:true}],conclusion:'Neither object was lost from the application or save. All 8,407 pre-v6 state IDs exist; only subsequently deleted QA objects are intentionally absent.'};
fs.mkdirSync('reports/v6',{recursive:true});fs.writeFileSync('reports/v6/missing-state-audit.json',JSON.stringify(report,null,2));console.log('PASS original state coverage',JSON.stringify({originalIds:report.backupStates,missing:0,apronDimensions:size.toArray(),foamVertices:foam.geometry.attributes.position.count,deletedTombstones:tombstones.length}));
