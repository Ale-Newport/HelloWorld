bl_info={'name':'Alejandro World Builder','author':'Alejandro Newport','version':(2,0,0),'blender':(4,5,0),'location':'View3D > Sidebar > Alejandro World','description':'Portable diorama authoring, physics, ground placement and web export','category':'3D View'}
import bpy
from . import settings,operators,physics,placement,roads,assets,materials,validation,export,ui
MODULES=[settings,operators,physics,placement,roads,assets,materials,validation,export,ui]
def register():
    for module in MODULES:
        for cls in module.CLASSES:bpy.utils.register_class(cls)
    bpy.types.Scene.aw=bpy.props.PointerProperty(type=settings.AW_Settings)
    if placement.auto_snap not in bpy.app.handlers.depsgraph_update_post:bpy.app.handlers.depsgraph_update_post.append(placement.auto_snap)
def unregister():
    if placement.auto_snap in bpy.app.handlers.depsgraph_update_post:bpy.app.handlers.depsgraph_update_post.remove(placement.auto_snap)
    if hasattr(bpy.types.Scene,'aw'):del bpy.types.Scene.aw
    for module in reversed(MODULES):
        for cls in reversed(module.CLASSES):bpy.utils.unregister_class(cls)
