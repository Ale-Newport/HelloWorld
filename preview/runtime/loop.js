import * as THREE from 'three';
/** Local stunt assistance only. Physics still resolves the chassis and raycast wheels.
 * The authored 3D ribbon supplies the path; no global gravity alteration is used.
 */
export class LoopAssist {
 constructor(vehicle,points){this.vehicle=vehicle;this.points=points.map(([x,y,z])=>new THREE.Vector3(x,z,-y));this.active=false;this.index=0;this.completed=0;this.contactSamples=[];this.enabled=true;}
 reset(){this.active=false;this.index=0;this.contactSamples=[];}
 beforeStep(){
  if(!this.enabled)return;
  const v=this.vehicle,b=v.chassis.physical.body,p=new THREE.Vector3().copy(b.translation()),vel=new THREE.Vector3().copy(b.linvel());
  if(!this.active){const a=this.points[0];if(p.distanceTo(a)<3 && vel.x>12){this.active=true;this.index=0;this.contactSamples=[];}else return;}
  let nearest=this.index,dist=Infinity;
  for(let i=Math.max(0,this.index-3);i<Math.min(this.points.length,this.index+18);i++){const d=p.distanceToSquared(this.points[i]);if(d<dist){dist=d;nearest=i;}}
  this.index=Math.max(this.index,nearest);
  if(this.index>=this.points.length-3){this.active=false;this.completed++;return;}
  const a=this.points[Math.max(0,nearest-1)],c=this.points[Math.min(this.points.length-1,nearest+1)],t=c.clone().sub(a).normalize();
  const side=new THREE.Vector3(0,0,1);const up=side.clone().cross(t).normalize();side.copy(t).cross(up).normalize();
  const q=new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(t,up,side));
  const target=this.points[nearest].clone().addScaledVector(up,1.03);const correction=target.sub(p);correction.addScaledVector(t,-correction.dot(t));
  const speed=Math.max(17,Math.min(26,vel.dot(t)));const next=t.multiplyScalar(speed).addScaledVector(correction,9);
  b.setRotation(q,true);b.setAngvel({x:0,y:0,z:0},true);b.setLinvel(next,true);
  this.contactSamples.push(v.wheels.inContactCount);
 }
}
