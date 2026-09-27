import bpy,shutil,hashlib
from pathlib import Path
from bpy_extras.io_utils import ImportHelper
from ..core import project_root,material

def mapping(mat):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    node=nodes.get('AW Tiling')
    if not node:
        node=nodes.new('ShaderNodeMapping');node.name='AW Tiling';uv=nodes.new('ShaderNodeTexCoord');links.new(uv.outputs['UV'],node.inputs['Vector'])
        for tex in nodes:
            if tex.type=='TEX_IMAGE':links.new(node.outputs['Vector'],tex.inputs['Vector'])
    return node
class AW_OT_material(bpy.types.Operator):
    bl_idname='aw.material';bl_label='Material tools';bl_options={'REGISTER','UNDO'}
    action:bpy.props.StringProperty(default='NEW')
    def execute(self,context):
        o=context.object
        if not o or o.type!='MESH':return {'CANCELLED'}
        if self.action in {'NEW','UV'} and o.data.users>1:o.data=o.data.copy()
        if self.action=='NEW':o.data.materials.clear();o.data.materials.append(material('AW '+o.name,(.35,.55,.55,1)))
        elif self.action=='UNIQUE':
            if o.active_material:o.active_material=o.active_material.copy()
        elif self.action=='TILING':
            if o.active_material:mapping(o.active_material)
        elif self.action=='UV':
            # World metre UVs respect applied and unapplied object scale.
            uv=o.data.uv_layers.active or o.data.uv_layers.new(name='WorldMetres')
            for face in o.data.polygons:
                n=o.matrix_world.to_3x3().inverted_safe().transposed()@face.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis]
                for li in face.loop_indices:
                    p=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]/context.scene.aw.texture_metres,p[axes[1]]/context.scene.aw.texture_metres)
        elif self.action=='REPLACE':
            mat=bpy.data.materials.get(context.scene.aw.material_name)
            if not mat:return {'CANCELLED'}
            for obj in context.selected_objects:
                if obj.type=='MESH':
                    if obj.data.users>1:obj.data=obj.data.copy()
                    obj.data.materials.clear();obj.data.materials.append(mat)
        return {'FINISHED'}
class AW_OT_texture(bpy.types.Operator,ImportHelper):
    bl_idname='aw.texture';bl_label='Replace texture';bl_options={'REGISTER','UNDO'}
    filename_ext='';filter_glob:bpy.props.StringProperty(default='*.png;*.jpg;*.jpeg;*.webp;*.exr',options={'HIDDEN'})
    normal:bpy.props.BoolProperty(name='Normal map',default=False)
    def execute(self,context):
        o=context.object
        if not o or not o.active_material:return {'CANCELLED'}
        src=Path(self.filepath);out=project_root()/'textures/imported'/f'{hashlib.sha256(src.read_bytes()).hexdigest()[:10]}_{src.name}';out.parent.mkdir(parents=True,exist_ok=True)
        if src.resolve()!=out.resolve():shutil.copyfile(src,out)
        img=bpy.data.images.load(str(out),check_existing=True);img.pack();img.filepath=bpy.path.relpath(str(out))
        mat=o.active_material;mat.use_nodes=True;n=mat.node_tree.nodes;links=mat.node_tree.links;p=n.get('Principled BSDF');key='AW Normal' if self.normal else 'AW Texture';tex=n.get(key) or n.new('ShaderNodeTexImage');tex.name=key;tex.image=img;links.new(mapping(mat).outputs['Vector'],tex.inputs['Vector'])
        if self.normal:
            img.colorspace_settings.name='Non-Color';normal=n.get('AW Normal decode') or n.new('ShaderNodeNormalMap');normal.name='AW Normal decode';links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],p.inputs['Normal'])
        else:links.new(tex.outputs['Color'],p.inputs['Base Color'])
        return {'FINISHED'}
CLASSES=[AW_OT_material,AW_OT_texture]
