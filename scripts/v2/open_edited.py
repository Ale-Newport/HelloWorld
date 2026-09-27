"""Open the browser's explicit GLB export as a separate, editable Blender document."""
from pathlib import Path
import sys,bpy,json
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'editor'))
import alejandro_world
from alejandro_world.physics import configure
source=ROOT/'exports/EditedWorld.glb'
if not source.exists():raise RuntimeError('Use EXPORT GLB in the World Studio first.')
bpy.ops.wm.read_factory_settings(use_empty=True)
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
bpy.ops.import_scene.gltf(filepath=str(source));scene=bpy.context.scene;scene.name='Alejandro World · browser edit';scene.render.fps=24;scene.frame_end=721
# glTF represents a multi-material rigid object as an Empty with mesh children.
# Join those children around the authored pivot before creating a Bullet body.
def plain(v):
 if hasattr(v,'to_dict'):return {k:plain(x) for k,x in v.to_dict().items()}
 if hasattr(v,'to_list'):return [plain(x) for x in v.to_list()]
 if isinstance(v,(list,tuple)):return [plain(x) for x in v]
 return v
for root in [o for o in scene.objects if o.type=='EMPTY' and o.get('collision')]:
 parts=[o for o in root.children_recursive if o.type=='MESH']
 if not parts:continue
 name=root.name;metadata={k:plain(root[k]) for k in root.keys()};pivot=root.matrix_world.translation.copy();parent=root.parent
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();joined=bpy.context.object;world=joined.matrix_world.copy();joined.parent=None;joined.matrix_world=world
 scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');world=joined.matrix_world.copy();joined.parent=parent;joined.matrix_world=world
 bpy.data.objects.remove(root,do_unlink=True);joined.name=name
 for k,v in metadata.items():joined[k]=v
for o in list(scene.objects):
 if o.get('collision') and o.type=='MESH':configure(o,o.get('physics_mode','STATIC'),o.get('collision_shape','CONVEX_HULL'),o.get('mass',1),o.get('friction',.7))
for o in list(scene.objects):
 if o.get('road_points'):o['web_editable_road']=True
scene.world=bpy.data.worlds.new('Studio daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
light=bpy.data.lights.new('Sun','SUN');light.energy=2.6;o=bpy.data.objects.new('Sun',light);scene.collection.objects.link(o);o.rotation_euler=(.4,-.45,-.6)
data=bpy.data.cameras.new('WORLD OVERVIEW');camera=bpy.data.objects.new('WORLD OVERVIEW',data);scene.collection.objects.link(camera);camera.location=(-158,-225,265);camera.rotation_euler=(Vector((0,4,0))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=261;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.samples=24;scene.frame_set(1)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_rotation=camera.rotation_euler.to_quaternion();area.spaces.active.region_3d.view_distance=230;area.spaces.active.show_region_ui=True
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'world/EditedWorld.blend'))
dynamic=sum(bool(o.rigid_body and o.rigid_body.type=='ACTIVE') for o in scene.objects)
import json
(ROOT/'reports/v2-roundtrip.json').write_text(json.dumps({'source':'exports/EditedWorld.glb','output':'world/EditedWorld.blend','objects':len(scene.objects),'dynamic_bodies':dynamic,'animation_actions':len(bpy.data.actions)},indent=2))
print('Browser world opened as world/EditedWorld.blend; base world preserved.')
