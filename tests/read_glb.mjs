import fs from 'node:fs';
import * as THREE from 'three';
export function readGLB(path){
 const file=fs.readFileSync(path);if(file.readUInt32LE(0)!==0x46546c67)throw Error('Invalid GLB magic');if(file.readUInt32LE(8)!==file.length)throw Error('GLB length mismatch');
 const jsonLength=file.readUInt32LE(12),doc=JSON.parse(file.subarray(20,20+jsonLength).toString()),bin=file.subarray(28+jsonLength);
 function accessor(index){const a=doc.accessors[index],view=doc.bufferViews[a.bufferView],n={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16}[a.type],bytes={5126:4,5125:4,5123:2,5121:1}[a.componentType];const array=a.componentType===5126?new Float32Array(a.count*n):new Uint32Array(a.count*n);const off=(view.byteOffset??0)+(a.byteOffset??0),stride=view.byteStride??n*bytes;
 for(let i=0;i<a.count;i++)for(let j=0;j<n;j++){const at=off+i*stride+j*bytes;array[i*n+j]=a.componentType===5126?bin.readFloatLE(at):a.componentType===5125?bin.readUInt32LE(at):a.componentType===5123?bin.readUInt16LE(at):bin.readUInt8(at);}return array;}
 const geometries=doc.meshes.map(m=>m.primitives.map(p=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(accessor(p.attributes.POSITION),3));if(p.indices!==undefined)g.setIndex(new THREE.BufferAttribute(accessor(p.indices),1));return g}));
 const mat=new THREE.MeshBasicMaterial();const nodes=doc.nodes.map(n=>{let o;if(n.mesh!==undefined&&geometries[n.mesh].length===1)o=new THREE.Mesh(geometries[n.mesh][0],mat);else{o=new THREE.Group();if(n.mesh!==undefined)for(const g of geometries[n.mesh])o.add(new THREE.Mesh(g,mat));}o.name=n.name??'';o.userData=n.extras??{};if(n.matrix){o.matrix.fromArray(n.matrix);o.matrix.decompose(o.position,o.quaternion,o.scale);}else{if(n.translation)o.position.fromArray(n.translation);if(n.rotation)o.quaternion.fromArray(n.rotation);if(n.scale)o.scale.fromArray(n.scale);}return o;});
 doc.nodes.forEach((n,i)=>{for(const child of n.children??[])nodes[i].add(nodes[child])});const scene=new THREE.Scene();for(const i of doc.scenes[doc.scene??0].nodes)scene.add(nodes[i]);scene.updateMatrixWorld(true);return {scene,nodes,doc,accessor};
}
