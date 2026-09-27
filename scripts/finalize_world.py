import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
root=Path(__file__).resolve().parents[1];sys.path[:0]=[str(root/'editor'),str(root/'scripts')]
import alejandro_world
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
from worldgen.common import *
from worldgen.props import template,linked
from alejandro_world.physics import configure
from alejandro_world.placement import snap_object
from alejandro_world.validation import validate
setup();scene=bpy.context.scene;scene.frame_set(1);scene.aw.ground_snap=False
from worldgen.junctions import finish_junctions
finish_junctions()
# Structure created as meshes has accurate static collision, including kiosks and roofs.
words=('Pit ','Tool chest','Grandstand','Workshop','Coding workbench','Laptop','London call box','Ticket','Skate rental','Snow roof','Lookout stone','Picnic table')
for o in scene.objects:
 if o.get('aw_new') and o.type=='MESH' and o.name.startswith(words):o['collision']=True;o['collision_shape']='MESH'
# Additional reusable source props chosen by their authored collection rather than name guesses.
for label,kind,category in [('Original traffic cone','cones','Props'),('Original barrel','barrels','Props'),('Original race banner','banners','Race Track'),('Original building','building','Buildings')]:
 if bpy.data.objects.get('LIB_'+label):continue
 candidates=[o for o in scene.objects if o.type=='MESH' and kind in o.get('w2Collections',[]) and not o.hide_render]
 if candidates:template(max(candidates,key=lambda o:o.dimensions.length),label,category)
# A reusable planted tuft: shared mesh across the new gardens.
if not bpy.data.objects.get('LIB_Grass tuft'):
 col=collection('VEGETATION');parts=[]
 for i in range(14):
  a=i*2.4;r=.22*math.sqrt(i/14);x=r*math.cos(a);y=r*math.sin(a);h=.22+(i%4)*.07
  verts=[(x-.04,y,0),(x+.04,y,0),(x+.06,y+.06,h),(x,y-.04,0),(x,y+.04,0),(x+.07,y+.04,h*.9)]
  me=bpy.data.meshes.new('Grass blade');me.from_pydata(verts,[],[(0,1,2),(3,4,5)]);o=bpy.data.objects.new('Grass blade',me);col.objects.link(o);me.materials.append(M['grass']);parts.append(o)
 turf=join(parts,'Grass tuft source',col,(0,0,0));lib=template(turf,'Grass tuft','Plants');bpy.data.objects.remove(turf,do_unlink=True)
 import random
 rng=random.Random(753)
 for cx,cy,rx,ry,n in [(-188,-18,25,8,65),(-86,115,23,4,40),(146,60,7,5,20),(-23,-149,20,3,35)]:
  for i in range(n):
   a=rng.random()*math.tau;d=math.sqrt(rng.random());o=linked(lib,'Garden grass',(cx+rx*d*math.cos(a),cy+ry*d*math.sin(a),.03),col,rng.uniform(.8,1.8),a);o['collision']=False;o['category']='Plants'
# Directly support native bodies on new procedural road meshes after regeneration.
for o in list(scene.objects):
 if o.type=='MESH' and o.get('ground_surface') and not o.rigid_body:configure(o,'STATIC','MESH',1,o.get('friction',.7))
# Place the penguin pivot over its feet for native Bullet, preserving world geometry.
meshes={o.data for o in scene.objects if o.type=='MESH' and o.get('center_of_mass') and not o.get('support_centred')}
for mesh in meshes:
 users=[o for o in scene.objects if o.type=='MESH' and o.data==mesh]
 bpy.context.view_layer.update()
 offsets={o:o.matrix_world.to_3x3()@Vector((0,-.13,0)) for o in users}
 mesh.transform(Matrix.Translation((0,.13,0)))
 for obj in users:obj.location+=offsets[obj];obj['support_centred']=True
# Drop the new dynamic props once with the exact surfaces, keeping deliberately fallen poses.
for o in list(scene.objects):
 if o.rigid_body and o.rigid_body.type=='ACTIVE' and not o.get('aw_template') and o.name.startswith(('PlasticPenguin','Ice slalom','Ice cone')):snap_object(o,scene,False,.015)
# Correct the lookout support against the actual hill instead of its nominal height.
platform=bpy.data.objects.get('Lookout stone platform')
if platform:platform.location.z=2.5;platform['ground_surface']=True
bench=bpy.data.objects.get('Circuit lookout bench')
if bench:bench.location.z=2.66
sign=bpy.data.objects.get('Lookout sign')
if sign:sign.location.z=2.5
label=bpy.data.objects.get('Lookout sign lettering')
if label:label.location.z=4.55
hill=bpy.data.objects.get('Circuit lookout hill');bed=bpy.data.objects.get('Garden bed')
if hill and bed and not bed.get('landscape_settled'):
 bpy.context.view_layer.update();inverse=hill.matrix_world.inverted();bed_inverse=bed.matrix_world.inverted()
 for vertex in bed.data.vertices:
  point=bed.matrix_world@vertex.co;origin=Vector((point.x,point.y,10));hit,position,normal,index=hill.ray_cast(inverse@origin,Vector((0,0,-1)))
  if hit:
   surface=hill.matrix_world@position
   if surface.z>0:point.z+=surface.z;vertex.co=bed_inverse@point
 bed['landscape_settled']=True
bpy.context.view_layer.update()
# Image bytes stay packed; path strings are relative even when imported from the FBX.
for img in bpy.data.images:
 if img.source=='FILE' and img.filepath and not img.filepath.startswith('//'):
  absolute=Path(bpy.path.abspath(img.filepath))
  if absolute.is_relative_to(root):img.filepath='//../'+str(absolute.relative_to(root))
scene.render.fps=24;scene.render.fps_base=1;scene.frame_end=721;scene.frame_set(1)
for d in list(bpy.data.meshes):
 if d.users==0:bpy.data.meshes.remove(d)
for d in list(bpy.data.curves):
 if d.users==0:bpy.data.curves.remove(d)
issues=validate(scene);(root/'reports/world-validation.json').write_text(json.dumps(issues,indent=2))
assert not [i for i in issues if i['level']=='ERROR'],[i for i in issues if i['level']=='ERROR']
# Hide technical collider wires in the everyday editing view.
for obj in scene.objects:
 if obj.get('runtime_collider'):obj.hide_set(True)
# Select the name and present the welcome view on first open.
bpy.ops.object.select_all(action='DESELECT');welcome=bpy.data.objects.get('Alejandro Newport / ALEJANDRO');activate(welcome)
scene.camera=bpy.data.objects['Camera / whole world']
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   space=area.spaces.active;space.region_3d.view_distance=88;space.region_3d.view_location=(36,-24,0);space.region_3d.view_rotation=bpy.data.objects['Camera / welcome'].rotation_euler.to_quaternion();space.shading.type='MATERIAL';space.overlay.show_extras=False;space.overlay.show_relationship_lines=False;space.show_region_ui=True
scene.aw.validation_summary='Run Validate World for the latest report'
bpy.ops.wm.save_as_mainfile(filepath=str(root/'world/AlejandroWorld.blend'))
terrain=[o for o in scene.objects if o.get('terrain') and o.type=='MESH'];pts=[o.matrix_world@Vector(v) for o in terrain for v in o.bound_box]
report={'objects':len(scene.objects),'unique_meshes':len(bpy.data.meshes),'visible_triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in scene.objects if o.type=='MESH' and not o.hide_render),'materials':len(bpy.data.materials),'library_assets':sum(bool(o.get('aw_template')) for o in scene.objects),'dynamic_props':sum(bool(o.rigid_body and o.rigid_body.type=='ACTIVE' and not o.get('aw_template')) for o in scene.objects),'extent_m':[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)],'original_extent_m':[192,192],'validation':{level:sum(i['level']==level for i in issues) for level in ['ERROR','WARNING','SUGGESTION']}}
(root/'reports/final-world.json').write_text(json.dumps(report,indent=2));print('FINALIZED',report,flush=True)
