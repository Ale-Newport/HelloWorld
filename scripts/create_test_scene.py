import bpy,sys,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1];sys.path[:0]=[str(root/'editor'),str(root/'scripts')]
import alejandro_world
from worldgen.common import *
from worldgen.props import penguin,cone,car_model
from alejandro_world.physics import configure
bpy.ops.wm.read_factory_settings(use_empty=True);alejandro_world.register();setup();s=bpy.context.scene;s.name='Physics Playground';s.frame_start=1;s.frame_end=240;s.render.fps=24;c=collection('PHYSICS_LAB')
for y,friction,label in [(-4,.025,'ICE · 0.025'),(4,.85,'ASPHALT · 0.85')]:
 floor=cube(label,(0,y,-.15),(32,6,.3),'ice' if y<0 else 'black',c);ground(floor,'ice' if y<0 else 'asphalt',friction);configure(floor,'STATIC','BOX',1,friction)
 target=penguin('Penguin / '+label,(4,y,.01),c);target.rigid_body.friction=.1
 cone('Cone / '+label,(8,y,.01),c)
 car=car_model('Animated collision driver / '+label,(-10,y,0),c);configure(car,'KINEMATIC','CONVEX_HULL',15,.5);car.keyframe_insert(data_path='location',frame=1);car.location.x=12;car.keyframe_insert(data_path='location',frame=145)
 for fc in car.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='LINEAR'
 text('Label '+label,label,(-4,y+2.3,.04),.6,'cream',c)
s.rigidbody_world.substeps_per_frame=8;s.rigidbody_world.solver_iterations=20;s.rigidbody_world.point_cache.frame_end=240
s.world=bpy.data.worlds.new('Lab light');s.world.color=(.3,.3,.3);s.camera=save_camera('Lab camera',(18,-27,28),(0,0,0),37,c)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_location=(0,0,0);area.spaces.active.region_3d.view_distance=38;area.spaces.active.shading.type='MATERIAL'
s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(root/'world/PhysicsPlayground.blend'))
