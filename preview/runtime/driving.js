import * as THREE from 'three';
import {PhysicsVehicle} from './PhysicsVehicle.js';
import {Events} from './Events.js';
import {VisualVehicle} from './VisualVehicle.js';
import {Materials} from './materials.js';
import {LoopAssist} from './loop.js';
import {Player} from '../portfolio/world/player/Player.js';
import {Inputs,ACTION_DEFINITIONS} from '../portfolio/world/input/Inputs.js';
import {View} from '../portfolio/world/view/View.js';
import {Tweens} from '../portfolio/world/core/Tween.js';
import {Bin} from '../portfolio/world/core/Disposal.js';
import {Audio} from '../portfolio/world/systems/Audio.js';
const vec=p=>new THREE.Vector3(p[0],p[2],-p[1]);
/** Exact World2 Player, Inputs, View and PhysicsVehicle; only ice, loop and
 * editable-road respawn are HelloWorld-specific extensions. */
export class Driving {
 constructor(physics,scene,camera,navigation,keys,canvas=document.querySelector('#world')){
  Object.assign(this,{physics,camera,nav:navigation,keys});this.cameraMode=2;this.wet=0;this.bin=new Bin();
  this.ticker={events:new Events(),elapsed:0,elapsedScaled:0,deltaScaled:1/30,scale:2,delta:1/60,alpha:1};physics.ticker=this.ticker;
  this.inputs=new Inputs(canvas);this.inputs.add(ACTION_DEFINITIONS);this.inputs.add([{name:'boardPrevious',label:'Previous project',categories:['minigame'],keys:['Keyboard.ArrowLeft','Keyboard.KeyA','Gamepad.left']},{name:'boardNext',label:'Next project',categories:['minigame'],keys:['Keyboard.ArrowRight','Keyboard.KeyD','Gamepad.right']}]);this.inputs.setFilters(['driving','camera']);this.bin.add(()=>this.inputs.destroy());
  this.tweens=new Tweens(this.ticker,this.bin);
  this.viewport={width:canvas.clientWidth,height:canvas.clientHeight,ratio:canvas.clientWidth/canvas.clientHeight,events:new Events()};
  this.view=new View(this.ticker,this.viewport,this.inputs,physics,this.bin,false);camera.copy(this.view.camera);this.view.camera=camera;
  this.vehicle=new PhysicsVehicle(physics,this.ticker,this.bin,vec(navigation.spawn));tuneVehicle(this.vehicle);
  this.roads=navigation.roads.flatMap(r=>r.samples.slice(0,-1).map((p,i)=>({p:vec(p),next:vec(r.samples[i+1]),width:r.width,name:r.name})));
  const spawn=()=>navigation.directSpawn?{...navigation.directSpawn,position:new THREE.Vector3(...navigation.directSpawn.position)}:this.spawnAt(vec(navigation.spawn));const respawns={getDefault:spawn,getClosest:p=>this.spawnAt(p),getByName:()=>null};
  this.player=new Player(this.inputs,this.vehicle,this.view,respawns,this.ticker,this.tweens,null,this.bin);
  this.visual=new VisualVehicle(this.vehicle,this.player,this.inputs,physics,this.ticker,new Materials(this.bin),this.bin,true);this.visual.camera=camera;scene.add(this.visual.group);
  this.loop=new LoopAssist(this.vehicle,navigation.loop.points);this.ticker.events.on('fixed',()=>this.loop.beforeStep(),1.5);this.ticker.events.on('fixed',()=>physics.step(),3);
  this.save={data:{settings:{muted:true,volume:.5}},schedule(){}};this.audio=new Audio(this.ticker,this.player,this.vehicle,this.save,this.bin);this.audio.resume();
  this.player.events.on('respawn',()=>{this.inputs.releaseAll();this.player.suspensions.fill('low');this.loop.reset();this.wet=0;});
  this.vehicle.events.on('land',air=>{if(air>.35)this.view.kick(Math.min(1,air*.9));});this.vehicle.events.on('collision',force=>{if(force>24)this.view.kick(Math.min(1,force/140));});
  this.lastSafe=spawn();
 }
 nearest(position=this.vehicle.position){let best=null,d=Infinity;for(const road of this.roads){const n=road.p.distanceToSquared(position);if(n<d){d=n;best=road;}}if(!best){const p=this.nav.directSpawn?new THREE.Vector3(...this.nav.directSpawn.position):vec(this.nav.spawn);best={p,next:p.clone().add(new THREE.Vector3(1,0,0)),width:8,name:"Terreno"};d=p.distanceToSquared(position);}return {...best,distance:Math.sqrt(d)};}
 spawnAt(position){const r=this.nearest(position),p=r.p.clone();p.y+=1.18;const t=r.next.clone().sub(r.p),road={name:r.name,position:p,rotation:Math.atan2(-t.z,t.x)};const options=[road,...(this.nav.prefabSpawns??[]).map(s=>({...s,position:new THREE.Vector3(...s.position)}))];if(this.nav.directSpawn)options.push({...this.nav.directSpawn,position:new THREE.Vector3(...this.nav.directSpawn.position)});return options.sort((a,b)=>a.position.distanceToSquared(position)-b.position.distanceToSquared(position))[0];}
 respawn(){this.player.respawn();}
 fixed(){this.ticker.elapsed+=1/60;this.ticker.elapsedScaled+=1/30;this.ticker.events.trigger('fixed');const v=this.vehicle,n=this.nearest();if(n.distance<n.width/2&&v.upward.y>.9&&v.wheels.inContactCount>=3)this.lastSafe=this.spawnAt(v.position);
  this.wet=v.position.y<-1.3?this.wet+1/60:0;if(this.wet>.7){v.moveTo(this.lastSafe.position,this.lastSafe.rotation);this.player.position.copy(this.lastSafe.position);this.view.snapToTarget();this.loop.reset();this.wet=0;}
 }
 render(dt,alpha){this.ticker.delta=dt;this.ticker.alpha=alpha;const canvas=this.inputs.pointer.element??document.querySelector('#world');const w=canvas.clientWidth,h=canvas.clientHeight;if(w!==this.viewport.width||h!==this.viewport.height){Object.assign(this.viewport,{width:w,height:h,ratio:w/h});this.viewport.events.trigger('change');}this.ticker.events.trigger('tick');}
 dispose(){this.visual.group.removeFromParent();this.bin.dispose();this.ticker.events.clear();}
}
export function surfaceGrip(c){return c?.userData?.surface_type==='ice'?.025:c?.userData?.ground_surface&&c?.userData?.surface_type!=='terrain'?4:1.9;}
export function tuneVehicle(v){v.idleBrake=.14;v.boostMultiplier=.6;v.topSpeedBoost=22;v.chassis.physical.linearDamping=.18;v.chassis.physical.body.setLinearDamping(.18);const c=v.chassis.physical.body.collider(0);c.setMassProperties(c.mass(),{x:0,y:-.8,z:0},{x:1,y:1,z:1},{x:0,y:0,z:0,w:1});v.surfaceFriction=surfaceGrip;}
