"""glTF extras + sidecar preserve physics unsupported by core glTF."""
import bpy,json
from ..core import project_root
from ..physics import sync

def export_world(path=None):
    path=path or project_root()/'exports/AlejandroWorld.glb';path.parent.mkdir(exist_ok=True)
    scene=bpy.context.scene;frame=scene.frame_current;scene.frame_set(1)
    # Physics is reconstructed from extras in the web runtime. Sampling Bullet
    # here would bake falling props and unnecessarily simulate 721 frames.
    rigid_world=scene.rigidbody_world
    physics_enabled=rigid_world.enabled if rigid_world else False
    if rigid_world:rigid_world.enabled=False
    selected=list(bpy.context.selected_objects);active=bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    metadata={}
    for o in scene.objects:
        if o.get('aw_template') or o.get('aw_road') or o.hide_render or o.type in {'LIGHT','CAMERA'}:continue
        sync(o);o.select_set(True)
        metadata[o.name]={k:(list(o[k]) if hasattr(o[k],'to_list') else o[k]) for k in o.keys() if k not in {'_RNA_UI','cycles'}}
    try:
        bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,use_active_scene=True,export_extras=True,export_animations=True,export_frame_range=True,export_force_sampling=True,export_animation_mode='NLA_TRACKS',export_anim_slide_to_zero=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False,export_materials='EXPORT',export_image_format='AUTO',export_texcoords=True,export_normals=True,export_shared_accessors=True)
        (path.parent/'world-physics.json').write_text(json.dumps({'schema':1,'units':'metres','blender_to_gltf':'x,z,-y','objects':metadata},default=str,indent=2))
    finally:
        if rigid_world:rigid_world.enabled=physics_enabled
        bpy.ops.object.select_all(action='DESELECT')
        for o in selected:
            if o.name in scene.objects:o.select_set(True)
        bpy.context.view_layer.objects.active=active;scene.frame_set(frame)
    return path
class AW_OT_export(bpy.types.Operator):
    bl_idname='aw.export';bl_label='Export world';bl_description='GLB with embedded images, animation, extras and physics sidecar'
    def execute(self,context):
        from ..validation import validate
        errors=[i for i in validate(context.scene) if i['level']=='ERROR']
        if errors:self.report({'ERROR'},f'{len(errors)} errors. Run Validate World before export.');return {'CANCELLED'}
        path=export_world();self.report({'INFO'},str(path));return {'FINISHED'}
CLASSES=[AW_OT_export]
