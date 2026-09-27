import * as THREE from 'three';
const originalIndices=new WeakMap();
let lastSignature='';
export function sourceGroundPatch(terrain,centre,radius=9){
 const source=terrain.geometry,position=source.attributes.position,index=source.index?.array??Array.from({length:position.count},(_,i)=>i),values=[],uv=[];
 const textureUV=source.attributes.uv;
 for(let i=0;i<index.length;i+=3){const points=[0,1,2].map(k=>new THREE.Vector3().fromBufferAttribute(position,index[i+k]).applyMatrix4(terrain.matrixWorld));const mid=points[0].clone().add(points[1]).add(points[2]).divideScalar(3);if(Math.hypot(mid.x-centre.x,mid.z-centre.z)>radius)continue;for(let k=0;k<3;k++){values.push(points[k].x,points[k].y+.015,points[k].z);if(textureUV)uv.push(textureUV.getX(index[i+k]),textureUV.getY(index[i+k]));}}
 const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(values,3));if(uv.length)geo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));geo.computeVertexNormals();
 const patch=new THREE.Mesh(geo,terrain.material.clone());patch.name='World2 · suelo del hoyo';patch.userData={w2Source:'world2GroundPatch',w2Category:'terrain',w2Role:'visual'};return patch;
}
/** Derived cuts follow the prefab and restore when it moves or is deleted. */
export function updatePrefabTerrain(root,force=false){
 root.updateMatrixWorld(true);const cutters=[],terrain=[];root.traverse(o=>{
  let visible=true,insidePrefab=false;for(let p=o;p;p=p.parent){if(!p.visible||p.userData.deleted)visible=false;if(p!==o&&p.userData.world2Asset)insidePrefab=true;}
  if(o.userData.world2Pit&&visible){const p=new THREE.Vector3(...o.userData.world2Pit.centre).applyMatrix4(o.matrixWorld),s=o.getWorldScale(new THREE.Vector3());cutters.push({p,r:o.userData.world2Pit.radius*s.x});}
  if(o.isMesh&&o.userData.terrain&&!insidePrefab)terrain.push(o);
 });
 const signature=cutters.map(c=>c.p.toArray().join(',')+':'+c.r).join('|');if(!force&&signature===lastSignature)return;lastSignature=signature;
 for(const mesh of terrain){const g=mesh.geometry,a=g.attributes.position;let indices=originalIndices.get(mesh);if(!indices){indices=g.index?Array.from(g.index.array):Array.from({length:a.count},(_,i)=>i);originalIndices.set(mesh,indices);}const kept=[];
  for(let i=0;i<indices.length;i+=3){const p=new THREE.Vector3();for(let j=0;j<3;j++)p.add(new THREE.Vector3().fromBufferAttribute(a,indices[i+j]));p.divideScalar(3).applyMatrix4(mesh.matrixWorld);if(cutters.some(c=>Math.hypot(p.x-c.p.x,p.z-c.p.z)<c.r))continue;kept.push(indices[i],indices[i+1],indices[i+2]);}
  g.setIndex(kept);g.computeBoundingSphere();
 }
}
