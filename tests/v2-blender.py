from pathlib import Path
import bpy,sys,json,math,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'editor'))
import alejandro_world
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
scene=bpy.context.scene;results=[]
def check(name,fn):
 try:
  result=fn();results.append({'name':name,'passed':True,'data':result});print('PASS',name,result,flush=True)
 except Exception as e:results.append({'name':name,'passed':False,'error':str(e)});print('FAIL',name,str(e),flush=True)
def world():
 assert scene['world_builder_version']=='2.0.0';assert bpy.data.objects.get('Main Island · sculptable terrain');assert bpy.data.objects.get('WORLD OVERVIEW');assert not bpy.data.objects.get('Western motorsport island');assert scene.rigidbody_world.enabled
 return {'objects':len(scene.objects),'version':scene['world_builder_version']}
def portable():
 missing=[]
 for image in bpy.data.images:
  if image.source=='FILE' and image.users and not image.packed_file and not Path(bpy.path.abspath(image.filepath)).exists():missing.append(image.name)
 assert not missing,str(missing)
 return {'packed_images':sum(bool(i.packed_file) for i in bpy.data.images),'fonts':len(bpy.data.fonts)}
def physics():
 terrain=bpy.data.objects['Main Island · sculptable terrain'];assert terrain.rigid_body and terrain.rigid_body.type=='PASSIVE';props=[o for o in scene.objects if o.get('physics_mode')=='DYNAMIC' and not o.get('aw_template')];assert len(props)==24;assert all(o.rigid_body and o.rigid_body.type=='ACTIVE' for o in props)
 return {'dynamic_props':len(props),'static_bodies':sum(bool(o.rigid_body and o.rigid_body.type=='PASSIVE') for o in scene.objects)}
def wheel():
 assert scene.render.fps==24;rotor=bpy.data.objects['FerrisWheel_Rotor'];assert rotor.animation_data.nla_tracks;cabins=[o for o in scene.objects if o.name.startswith('FerrisWheel_CabinPivot')];assert len(cabins)==12
 matrices=[]
 for frame in [1,181,361,541,721]:
  scene.frame_set(frame);bpy.context.view_layer.update();matrices.append([o.matrix_world.to_quaternion() for o in cabins])
 # World orientations remain unchanged throughout a full wheel rotation.
 for qs in matrices[1:]:
  for a,b in zip(matrices[0],qs):assert a.rotation_difference(b).angle<.002
 scene.frame_set(1);return {'cabins':12,'seconds':30}
def native_rest():
 penguins=[o for o in scene.objects if o.name.startswith('Learner penguin')];scene.frame_set(1);initial={o.name:o.matrix_world.to_quaternion() for o in penguins}
 for frame in range(2,121):scene.frame_set(frame)
 deps=bpy.context.evaluated_depsgraph_get();upright=sum(initial[o.name].rotation_difference(o.evaluated_get(deps).matrix_world.to_quaternion()).angle<.4 for o in penguins);assert upright==8,f'{upright}/8 upright';scene.frame_set(1);return {'upright':upright,'seconds':5}
check('One compact authored island',world);check('Self-contained textures and fonts',portable);check('Native static surfaces and dynamic props',physics);check('Wheel cabins remain upright throughout animation',wheel);check('Native penguins stand before impact',native_rest)
(ROOT/'reports/v2-blender-tests.json').write_text(json.dumps(results,indent=2))
if any(not r['passed'] for r in results):raise RuntimeError('Native validation failed')
