from pathlib import Path
import bpy,sys,math,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'editor'))
import alejandro_world
from alejandro_world.export import export_world
from alejandro_world.physics import configure
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
scene=bpy.context.scene;scene.frame_set(1)
for i in range(9):
 o=bpy.data.objects['Ice cone %02d'%i];o.location.y=60+.7*math.sin(i)
support=bpy.data.objects.get('FerrisWheel_StaticSupport')
if support:configure(support,'STATIC','MESH',1,.7)
# Small display pedestals and sign supports meet the ground physically.
from alejandro_world.core import material,collection
from mathutils import Matrix
for name,loc,size,parent,colname in [('Laptop pedestal',(32,12,.26),(4.8,2.8,.52),'Studio laptop','PROJECTS'),('Camera pedestal',(47,8,.15),(3.5,2.3,.3),'Studio camera','PROJECTS'),('Landmark pillar L',(-6,15,.8),(.6,.8,1.6),None,'CENTRAL_PLAZA'),('Landmark pillar R',(6,15,.8),(.6,.8,1.6),None,'CENTRAL_PLAZA')]:
 if bpy.data.objects.get(name):continue
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(bpy.data.materials['AW Cream']);o['aw_id']='v2:'+name;o['editable_root']=not bool(parent)
 target=collection(colname)
 for old in list(o.users_collection):old.objects.unlink(o)
 target.objects.link(o)
 if parent:world=o.matrix_world.copy();o.parent=bpy.data.objects[parent];o.matrix_world=world
 configure(o,'STATIC','BOX',1,.7)
# Build Blender Bezier guides from exactly the same road control points.
# Browser editing remains available on each exported road mesh.
from alejandro_world.core import collection
col=collection('ROAD_GUIDES')
for o in list(scene.objects):
 if not o.get('road_points') or o.get('aw_road'):continue
 name=o.name+' · guide'
 if bpy.data.objects.get(name):continue
 curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=16;sp=curve.splines.new('BEZIER');pts=json.loads(o['road_points']);sp.bezier_points.add(len(pts)-1)
 for bp,(x,y,z) in zip(sp.bezier_points,pts):bp.co=(x,-z,y);bp.handle_left_type=bp.handle_right_type='AUTO'
 sp.use_cyclic_u=o.get('road_closed',False);guide=bpy.data.objects.new(name,curve);col.objects.link(guide);guide.hide_render=True;guide['aw_road']=True;guide['road_width']=o['road_width'];guide['road_material']=o.data.materials[0].name;guide['generated_id']=o.name;o['road_owner']=o.name;guide.display_type='WIRE'
import bmesh
# Thin glazed panels use a small bevel that cannot collapse their side faces.
for o in scene.objects:
 if o.type!='MESH':continue
 for modifier in o.modifiers:
  if modifier.type=='BEVEL':modifier.width=min(modifier.width,min(o.dimensions)*.2)
 if o.name=='FerrisWheel_StaticSupport':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bad=[f for f in bm.faces if f.calc_area()<1e-7]
  if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
  bm.to_mesh(o.data);bm.free();o.data.update()
for o in scene.objects:
 if o.type=='MESH' and o.get('road_points'):
  bm=bmesh.new();bm.from_mesh(o.data);bm.normal_update()
  for face in bm.faces:
   if face.normal.z<0:face.normal_flip()
  bm.to_mesh(o.data);bm.free();o.data.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'world/AlejandroWorld.blend'));export_world();scene.render.filepath=str(ROOT/'reports/v2-overview.png')
if '--skip-render' not in sys.argv:bpy.ops.render.render(write_still=True)
