import bpy,os,re,json
from pathlib import Path
from ..core import project_root,bounds

def validate(scene):
    issues=[];root=project_root()
    def add(level,obj,message):issues.append(dict(level=level,object=obj,message=message))
    for image in bpy.data.images:
        if image.source!='FILE':continue
        path=Path(bpy.path.abspath(image.filepath))
        if not image.packed_file and not path.is_file():add('ERROR',image.name,'Missing texture')
        if image.filepath and not image.filepath.startswith('//'):
            if not path.is_relative_to(root):add('ERROR',image.name,'Absolute external path')
            else:add('WARNING',image.name,'Absolute path inside project; make relative')
        if max(image.size,default=0)>4096:add('WARNING',image.name,'Texture exceeds 4096 pixels')
        if image.filepath and path.suffix.lower() not in {'.png','.jpg','.jpeg','.webp','.exr','.hdr','.tif','.tiff','.bmp','.tga'}:add('WARNING',image.name,'Unsupported texture format')
    for o in scene.objects:
        if o.get('aw_template') or o.hide_render or o.type!='MESH':continue
        if (o.data.users==1 or o.rigid_body and o.rigid_body.type=='ACTIVE') and any(abs(s-1)>.001 for s in o.scale):add('SUGGESTION',o.name,'Unapplied scale; keep linked instances or apply before collider authoring')
        largest=max(o.dimensions)
        if largest>500 and o.get('surface_type')!='water':add('WARNING',o.name,'Asset exceeds 500 m')
        if 0<largest<.005:add('WARNING',o.name,'Asset smaller than 5 mm')
        if not o.data.uv_layers and any(m and m.use_nodes and any(n.type=='TEX_IMAGE' for n in m.node_tree.nodes) for m in o.data.materials):add('ERROR',o.name,'Textured mesh has no UVs')
        if o.get('drivable') and not o.get('collision'):add('ERROR',o.name,'Drivable surface without collision')
        if o.get('interactive') and o.get('interaction_type')=='physics' and not (o.rigid_body or o.get('collision')):add('ERROR',o.name,'Physics prop without collider')
        source=o.get('asset_source')
        if source and not Path(bpy.path.abspath(source)).exists():add('ERROR',o.name,'Missing asset reference')
        if o.get('animated') and not o.animation_data and not (o.parent and o.parent.get('animated')):add('WARNING',o.name,'Animated flag without action or animated parent')
        if o.get('aw_new') and o.get('surface_type')!='water' and not o.get('ground_surface') and not o.get('animated') and not o.parent:
            from ..placement import cast_ground
            box=bounds(o);c=o.matrix_world.translation;h=cast_ground(scene,__import__('mathutils').Vector((c.x,c.y,c.z+100)),[o])
            if h and max(p.z for p in box)<h[1].z-.1:add('WARNING',o.name,'Entire object below ground')
    for mat in bpy.data.materials:
        if re.search(r'\.\d{3}$',mat.name) and bpy.data.materials.get(mat.name[:-4]):add('SUGGESTION',mat.name,'Possible duplicate material; compare before merging')
    for action in bpy.data.actions:
        if action.frame_range[1]<=action.frame_range[0]:add('WARNING',action.name,'Animation has no duration')
    return issues

class AW_OT_validate(bpy.types.Operator):
    bl_idname='aw.validate';bl_label='Validate world';bl_description='Check portable dependencies, collisions, UVs, size and animation'
    def execute(self,context):
        issues=validate(context.scene);s=context.scene.aw;s.validation.clear()
        for e in issues:item=s.validation.add();item.level=e['level'];item.object_name=e['object'];item.message=e['message']
        out=project_root()/'reports/world-validation.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(issues,indent=2));s.validation_summary=', '.join(f'{sum(e["level"]==level for e in issues)} {level.lower()}s' for level in ['ERROR','WARNING','SUGGESTION'])
        self.report({'INFO'},s.validation_summary);return {'FINISHED'}
class AW_OT_select_issue(bpy.types.Operator):
    bl_idname='aw.select_issue';bl_label='Select issue object'
    name:bpy.props.StringProperty()
    def execute(self,context):
        from ..core import activate
        o=bpy.data.objects.get(self.name)
        if o and o.name in context.view_layer.objects:activate(o)
        return {'FINISHED'}
CLASSES=[AW_OT_validate,AW_OT_select_issue]
