"""Integration tests in a disposable Blender process. Never saves the world."""
import bpy,sys,json,math,traceback
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'editor'),str(ROOT/'scripts')]
import alejandro_world
alejandro_world.register()
from alejandro_world.core import activate,collection,material,bounds
from alejandro_world.placement import snap_object
from alejandro_world.roads import create_road,regenerate,sample
from alejandro_world.physics import configure
from alejandro_world.validation import validate
results=[]
def check(name,fn):
 try:
  result=fn();results.append({'name':name,'passed':True,'detail':result});print('PASS',name,result,flush=True)
 except Exception as e:
  results.append({'name':name,'passed':False,'error':str(e),'trace':traceback.format_exc()});print('FAIL',name,traceback.format_exc(),flush=True)

def structure():
 for name in ['WORLD','ICE_RINK','RACE_TRACK','ANIMATED_OBJECTS','VEGETATION','PERSONALIZATION']:assert bpy.data.collections.get(name),name
 assert any(o.type=='FONT' and 'ALEJANDRO' in o.data.body for o in bpy.data.objects)
 assert len([o for o in bpy.data.objects if o.name.startswith('PlasticPenguin') and not o.get('aw_template')])==8
 assert bpy.data.objects['IceLake_Surface'].rigid_body.friction<.04
 return {'objects':len(bpy.context.scene.objects),'ice_friction':bpy.data.objects['IceLake_Surface'].rigid_body.friction}
check('World structure, identity and ice metadata',structure)

def animation():
 scene=bpy.context.scene;assert scene.render.fps==24 and scene.render.fps_base==1;names=[o.name for o in bpy.data.objects if o.name.startswith('FerrisWheel_Cabin_')];assert len(names)==12,len(names)
 frames=[1,91,181,361,541,721];worlds={};worst=0
 for frame in frames:
  scene.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
  for name in names:
   o=bpy.data.objects[name].evaluated_get(deps);up=o.matrix_world.to_quaternion()@Vector((0,0,1));worst=max(worst,1-up.dot(Vector((0,0,1))))
   if frame in [1,721]:worlds[(frame,name)]=o.matrix_world.copy()
 assert worst<1e-4,f'Cabin tilt {worst}'
 error=max(max(abs(worlds[(1,n)][i][j]-worlds[(721,n)][i][j]) for i in range(4) for j in range(4)) for n in names)
 assert error<1e-3,error
 rotor=bpy.data.objects['FerrisWheel_Rotor'];scene.frame_set(1);bpy.context.view_layer.update();box=bounds(rotor);dimensions=[max(p[i] for p in box)-min(p[i] for p in box) for i in range(3)];assert dimensions[2]>15,dimensions
 return {'cabins':len(names),'max_tilt_error':worst,'loop_matrix_error':error,'rotor_world_dimensions':dimensions}
check('Ferris wheel vertical, 12 upright cabins and seamless cycle',animation)

def road_geometry():
 count=0;max_error=0
 for curve in bpy.data.objects:
  if not curve.get('aw_road'):continue
  obj=next(o for o in bpy.data.objects if o.get('road_owner')==curve['generated_id'] and o.get('ground_surface'));points=sample(curve)
  for i,p in enumerate(points):
   mid=(obj.data.vertices[2*i].co+obj.data.vertices[2*i+1].co)/2;max_error=max(max_error,(p-mid).length)
  count+=1
 assert max_error<.001,max_error
 loop=bpy.data.objects['RoadLoop_Surface'];assert loop['loop_width']>=5.5
 points=[Vector(p) for p in json.loads(loop['path_points'])];step=max((b-a).length for a,b in zip(points,points[1:]));assert step<.3,step
 return {'editable_roads':count,'centerline_error_m':max_error,'loop_segment_max_m':step,'loop_width':loop['loop_width']}
check('Road mesh follows authored Bezier curves and continuous loop',road_geometry)
def portable():
 issues=validate(bpy.context.scene);errors=[i for i in issues if i['level']=='ERROR'];assert not errors,errors
 return {'errors':len(errors)}
check('Portable world validation',portable)
# All destructive tests happen in a fresh scene, keeping the loaded world intact.
scene=bpy.data.scenes.new('TEST_ONLY');bpy.context.window.scene=scene

def box(name,pos,size):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o

def placement():
 surface=box('Test slope',(0,0,0),(12,12,.2));surface.rotation_euler.y=.18;surface['ground_surface']=True
 obj=box('Test prop',(0,0,4),(1,1,1));bpy.context.view_layer.update();assert snap_object(obj,scene,True,.02)
 bpy.context.view_layer.update();up=obj.matrix_world.to_quaternion()@Vector((0,0,1));normal=surface.matrix_world.to_quaternion()@Vector((0,0,1));assert up.dot(normal)>.999
 top=surface.matrix_world@Vector((0,0,.1));minimum=min((p-top).dot(normal) for p in bounds(obj));assert -.001<=minimum<.04,minimum
 # Drop after an arbitrary external move, including unapplied scale.
 obj.location=(2,1,9);obj.scale=(1.5,.8,1.2);bpy.context.view_layer.update();assert snap_object(obj,scene,True,.02);bpy.context.view_layer.update()
 return {'normal_alignment':up.dot(normal),'support_clearance_m':minimum,'scaled_location':list(obj.location)}
check('Snap and align on tilted ground with transformed bounds',placement)

def procedural():
 road=create_road('Test road',[(20,0,.1),(25,2,.1),(30,0,.1)],5,col=scene.collection)
 owner=road['generated_id'];first=len([o for o in scene.objects if o.get('road_owner')==owner]);regenerate(road);second=len([o for o in scene.objects if o.get('road_owner')==owner]);assert first==second==3
 road['road_width']=8;surface=regenerate(road);assert abs((surface.data.vertices[0].co-surface.data.vertices[1].co).length-8)<1e-4
 activate(road);assert bpy.ops.aw.road(action='EXTEND')=={'FINISHED'};assert len(road.data.splines[0].bezier_points)==4
 second_road=create_road('Test road',[(20,8,.1),(30,8,.1)],4,col=scene.collection)
 assert second_road['generated_id']!=road['generated_id']
 assert len([o for o in scene.objects if o.get('road_owner')==owner])==3
 return {'generated_objects':second,'new_width':8,'points':4,'unique_owner_ids':True}
check('Road regeneration idempotency, width and extend operator',procedural)

def glb_import():
 fixture=ROOT/'tests/fixtures';fixture.mkdir(exist_ok=True);o=box('Import specimen',(40,0,2),(1,2,3));activate(o)
 bpy.ops.export_scene.gltf(filepath=str(fixture/'specimen.glb'),export_format='GLB',use_selection=True,use_active_scene=True,export_animations=False)
 result=bpy.ops.aw.import_model(filepath=str(fixture/'specimen.glb'),auto_scale=True,collider=True)
 assert result=={'FINISHED'};assert list((ROOT/'assets/imported').glob('specimen_*/*.glb'))
 from alejandro_world.assets import copy_import_bundle
 local=copy_import_bundle(fixture/'specimen.glb');assert copy_import_bundle(local)==local
 return 'GLB copied, imported and collider created'
check('Portable GLB import operator',glb_import)

def material_tools():
 o=box('Material specimen',(45,0,1),(2,3,1));activate(o);bpy.ops.aw.material(action='NEW');bpy.ops.aw.material(action='TILING');bpy.ops.aw.material(action='UV');assert o.active_material.node_tree.nodes.get('AW Tiling');assert o.data.uv_layers
 return 'Principled material, tiling and metre UVs created'
check('Material and UV tools',material_tools)

def group_library():
 from alejandro_world.assets import duplicate_template
 root=bpy.data.objects.new('Compound asset test',None);bpy.context.scene.collection.objects.link(root)
 for i in range(2):
  child=box('Compound child',(50+i,0,1),(1,1,1));world=child.matrix_world.copy();child.parent=root;child.matrix_world=world
 activate(root);assert bpy.ops.aw.asset(action='SAVE')=={'FINISHED'}
 source=bpy.data.objects.get('LIB_Compound asset test');assert source and len(source.children_recursive)==2
 placed=duplicate_template(source,bpy.context,Vector((55,0,2)));assert len(placed.children_recursive)==2
 assert {o.data for o in placed.children_recursive}=={o.data for o in source.children_recursive}
 return 'Two child meshes retained and shared in a compound library asset'
check('Compound asset library preserves hierarchy',group_library)

def vegetation_scatter():
 from alejandro_world.assets import asset_items
 surface=box('Scatter soil',(80,0,-.1),(24,24,.2));surface['ground_surface']=True
 shrub=box('Scatter specimen',(70,0,1),(.5,.5,.8));activate(shrub);assert bpy.ops.aw.asset(action='SAVE')=={'FINISHED'}
 asset_items(None,bpy.context);scene.aw.asset='LIB_Scatter specimen';scene.aw.scatter_count=7;scene.aw.scatter_mode='RANDOM';scene.aw.scatter_radius=6;scene.aw.min_distance=2;scene.aw.seed=71;scene.cursor.location=(80,0,0)
 before=set(scene.objects);assert bpy.ops.aw.scatter()=={'FINISHED'};placed=list(set(scene.objects)-before);assert len(placed)==7
 assert len({o.data for o in placed})==1
 min_distance=min((a.location-b.location).length for i,a in enumerate(placed) for b in placed[i+1:]);assert min_distance>=1.99
 first=sorted(tuple(round(v,5) for v in o.location) for o in placed)
 for o in placed:bpy.data.objects.remove(o,do_unlink=True)
 before=set(scene.objects);assert bpy.ops.aw.scatter()=={'FINISHED'};second=sorted(tuple(round(v,5) for v in o.location) for o in set(scene.objects)-before)
 assert first==second
 return {'instances':7,'shared_meshes':1,'min_distance':min_distance,'repeatable_seed':True}
check('Vegetation scatter spacing, shared meshes and reproducible seed',vegetation_scatter)

def native_collision():
 # Dedicated isolated scene for deterministic native Bullet drop.
 s=bpy.data.scenes.new('TEST_BULLET');bpy.context.window.scene=s;s.render.fps=24;s.frame_end=90
 floor=box('Bullet floor',(0,0,-.15),(15,15,.3));configure(floor,'STATIC','BOX')
 prop=box('Bullet falling cube',(0,0,3),(1,1,1));configure(prop,'DYNAMIC','BOX',1,.5);s.rigidbody_world.substeps_per_frame=5
 from worldgen.common import setup
 from worldgen.props import penguin
 setup();bird=penguin('Bullet standing penguin',(3,0,.02),s.collection);bird.rotation_euler.z=.6
 initial=bird.matrix_world.to_quaternion()
 for frame in range(1,91):s.frame_set(frame);bpy.context.view_layer.update()
 pos=prop.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.translation.copy();assert .45<pos.z<.65,list(pos)
 activate(prop);prop.lock_location[0]=True;assert bpy.ops.aw.axis_locks()=={'FINISHED'}
 anchor=bpy.data.objects['LOCK_'+prop.name];assert anchor.rigid_body_constraint.use_limit_lin_x
 up=bird.evaluated_get(bpy.context.evaluated_depsgraph_get()).matrix_world.to_quaternion()@Vector((0,0,1));assert up.z>.94,up.z
 return {'settled_height_m':pos.z,'frames':90,'native_axis_constraint':True}
check('Native Blender rigid-body collision',native_collision)
(ROOT/'reports/blender-tests.json').write_text(json.dumps(results,indent=2));print('TESTS',sum(r['passed'] for r in results),'/',len(results),flush=True)
if not all(r['passed'] for r in results):raise RuntimeError('Integration tests failed')
