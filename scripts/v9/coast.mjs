import * as T from 'three';
import {groundGrain} from '../../preview/meadow-grass.js';
const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t);};
export function coastalHeight(distance){return distance>=0?-.35+.5*smooth(distance/4):distance>=-12?-.35-.85*smooth(-distance/12):-1.2-2.8*smooth((-distance-12)/16);}
function inside(x,z,p){let yes=false;for(let i=0,j=p.length-1;i<p.length;j=i++){const a=p[i],b=p[j];if((a[1]>z)!==(b[1]>z)&&x<(b[0]-a[0])*(z-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
export function createCoast(operations){
 const ops=operations.map(o=>({...o,shapes:(o.polygons??[o.polygon]).map(p=>({p,minX:Math.min(...p.map(v=>v[0])),maxX:Math.max(...p.map(v=>v[0])),minZ:Math.min(...p.map(v=>v[1])),maxZ:Math.max(...p.map(v=>v[1]))}))}));
 const materialAt=(x,z)=>{let material=null;for(const o of ops)if(o.shapes.some(b=>x>=b.minX&&x<=b.maxX&&z>=b.minZ&&z<=b.maxZ&&inside(x,z,b.p)))material=o.kind==='erase'?null:o.material;return material;};
 const polygons=ops.flatMap(o=>o.shapes),minX=Math.floor(Math.min(...polygons.map(p=>p.minX)))-30,maxX=Math.ceil(Math.max(...polygons.map(p=>p.maxX)))+30,minZ=Math.floor(Math.min(...polygons.map(p=>p.minZ)))-30,maxZ=Math.ceil(Math.max(...polygons.map(p=>p.maxZ)))+30,width=maxX-minX+1,height=maxZ-minZ+1;
 const mask=new Uint8Array(width*height),dist=new Float32Array(width*height);dist.fill(1e6);
 for(let j=0;j<height;j++)for(let i=0;i<width;i++)mask[j*width+i]=materialAt(minX+i,minZ+j)?1:0;
 for(let j=1;j<height-1;j++)for(let i=1;i<width-1;i++){const k=j*width+i;if([k-1,k+1,k-width,k+width].some(n=>mask[n]!==mask[k]))dist[k]=.5;}
 for(let pass=0;pass<2;pass++){const sign=pass?-1:1;for(let j=pass?height-2:1;pass?j>=1:j<height-1;j+=sign)for(let i=pass?width-2:1;pass?i>=1:i<width-1;i+=sign){const k=j*width+i;dist[k]=Math.min(dist[k],dist[k-sign]+1,dist[k-sign*width]+1,dist[k-sign*width-sign]+Math.SQRT2,dist[k-sign*width+sign]+Math.SQRT2);}}
 const sample=(x,z)=>{const i=Math.max(0,Math.min(width-1,Math.round(x-minX))),j=Math.max(0,Math.min(height-1,Math.round(z-minZ))),k=j*width+i;return dist[k]*(mask[k]?1:-1);};
 const p=[],c=[],uv=[],indices=[],sand=new T.Color('#dac796'),grass=new T.Color('#839e47');
 for(let j=0;j<height;j++)for(let i=0;i<width;i++){const x=minX+i,z=minZ+j,d=dist[j*width+i]*(mask[j*width+i]?1:-1),y=coastalHeight(d),variation=.96+.04*Math.sin(x*.21)*Math.cos(z*.17),blend=materialAt(x,z)==='Sand'?0:smooth((d-2)/5),color=sand.clone().lerp(grass,blend).multiplyScalar(variation);p.push(x,y,z);c.push(...color.toArray());uv.push(x*.35,z*.35);}
 for(let j=0;j<height-1;j++)for(let i=0;i<width-1;i++){const a=j*width+i,b=a+1,d=a+width,e=d+1;if([a,b,d,e].every(k=>!mask[k]&&dist[k]>28))continue;indices.push(a,d,b,b,d,e);}
 const geometry=new T.BufferGeometry();geometry.setAttribute('position',new T.Float32BufferAttribute(p,3));geometry.setAttribute('color',new T.Float32BufferAttribute(c,3));geometry.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geometry.setIndex(indices);geometry.computeVertexNormals();geometry.computeBoundingBox();geometry.computeBoundingSphere();
 const mesh=new T.Mesh(geometry,new T.MeshStandardMaterial({color:0xffffff,vertexColors:true,map:groundGrain(),roughness:1,side:T.DoubleSide}));mesh.name='Archipiélago · playas y fondo costero';mesh.receiveShadow=true;mesh.userData={terrain:true,sculptable:true,ground_surface:true,collision:true,physics_mode:'STATIC',surface_type:'terrain',layer:'Terrain',category:'Terrain',editable_root:true,coastalProfile:{dryTransition:4,shallowShelf:12,deepTransition:16}};
 return {mesh,sample,materialAt,heightAt:(x,z)=>coastalHeight(sample(x,z)),bounds:{minX,maxX,minZ,maxZ},triangles:indices.length/3};
}
