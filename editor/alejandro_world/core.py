"""Shared scene conventions. Blender metres, Z up; glTF standard Y up."""
from pathlib import Path
import bpy
from mathutils import Vector
CATEGORIES=['Nature','Trees','Rocks','Plants','Roads','Buildings','Street furniture','Vehicles','Attractions','Characters','Decorations','Signs','Props','Race Track','Ice Area','Fun Objects','Miscellaneous']
def project_root():
    p=Path(bpy.data.filepath).resolve() if bpy.data.filepath else Path(__file__).resolve()
    for parent in [p.parent,*p.parents]:
        if (parent/'scripts/build_world.py').exists():return parent
    return Path(__file__).resolve().parents[2]
def collection(name,parent=None):
    available=[bpy.context.scene.collection,*bpy.context.scene.collection.children_recursive]
    c=next((c for c in available if c.name==name or c.get('aw_collection_key')==name),None)
    if not c:
        c=bpy.data.collections.new(name);c['aw_collection_key']=name
        (parent or bpy.context.scene.collection).children.link(c)
    return c
def move_to(o,c):
    for old in list(o.users_collection):old.objects.unlink(o)
    c.objects.link(o)
def activate(o):
    bpy.context.view_layer.update()
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.hide_select=False;o.select_set(True);bpy.context.view_layer.objects.active=o

def bounds(o):return [o.matrix_world@Vector(p) for p in o.bound_box]
def tag(o,category='Props',**kw):
    defaults=dict(object_type=o.type.lower(),category=category,interactive=False,drivable=False,collision=False,breakable=False,animated=False,static_decoration=True,ground_surface=False,road=False,terrain=False,water_ice=False)
    for k,v in (defaults|kw).items():o[k]=v
    return o

def material(name,color,roughness=.65,metallic=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color[:3],color[3] if len(color)>3 else 1);p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic
    m.diffuse_color=p.inputs['Base Color'].default_value
    return m
