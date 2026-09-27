"""Ground placement uses evaluated surface geometry and transformed bounds."""
import bpy,math
from bpy.app.handlers import persistent
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
from ..core import bounds
_busy=False
_cache={}

def cast_ground(scene,origin,exclude=(),direction=Vector((0,0,-1))):
    deps=bpy.context.evaluated_depsgraph_get();best=None
    excluded=set(exclude)
    for obj in scene.objects:
        if obj in excluded or obj.type!='MESH' or not obj.get('ground_surface',False) or obj.hide_get():continue
        inv=obj.matrix_world.inverted_safe();v=inv.to_3x3()@direction
        hit,loc,norm,index=obj.ray_cast(inv@origin,v.normalized(),depsgraph=deps)
        if hit:
            pos=obj.matrix_world@loc;distance=(pos-origin).length
            if best is None or distance<best[0]:best=(distance,pos,(obj.matrix_world.to_3x3().inverted_safe().transposed()@norm).normalized(),obj)
    return best

def snap_object(obj,scene,align=False,offset=0,strength=1):
    if obj.get('ground_surface') or obj.type not in {'MESH','EMPTY','CURVE','FONT'}:return False
    family=[obj,*obj.children_recursive]
    corners=[p for member in family if member.type in {'MESH','CURVE','FONT'} for p in bounds(member)]
    if not corners:return False
    center=obj.matrix_world.translation.copy();top=max(p.z for p in corners)+50
    hit=cast_ground(scene,Vector((center.x,center.y,top)),family)
    if not hit:return False
    if align:
        current_up=obj.matrix_world.to_quaternion()@Vector((0,0,1));delta=current_up.rotation_difference(hit[2]);q=Quaternion().slerp(delta,strength)@obj.matrix_world.to_quaternion()
        loc,oldq,scale=obj.matrix_world.decompose();obj.matrix_world=__import__('mathutils').Matrix.LocRotScale(loc,q,scale);bpy.context.view_layer.update()
        corners=[p for member in family if member.type in {'MESH','CURVE','FONT'} for p in bounds(member)]
    # Four footprint probes keep wide and tilted objects from penetrating relief.
    x0,x1=min(p.x for p in corners),max(p.x for p in corners);y0,y1=min(p.y for p in corners),max(p.y for p in corners)
    normal=hit[2];required=[]
    for x,y in [(center.x,center.y),(x0,y0),(x0,y1),(x1,y0),(x1,y1)]:
        h=cast_ground(scene,Vector((x,y,top)),family)
        if h:
            # Plane support value accounts for rotated bounds, rather than just origin height.
            low=min((p-h[1]).dot(h[2]) for p in corners)
            required.append((offset-low)/max(.05,h[2].z))
    if required:obj.location.z+=max(required)
    return True

@persistent
def auto_snap(scene,depsgraph):
    global _busy
    if _busy or not hasattr(scene,'aw') or not (scene.aw.ground_snap or scene.aw.grid_snap or scene.aw.rotation_snap) or bpy.context.mode!='OBJECT' or scene.frame_current!=scene.frame_start:return
    if not any(u.is_updated_transform and isinstance(u.id,bpy.types.Object) for u in depsgraph.updates):return
    _busy=True
    try:
        for obj in list(bpy.context.selected_objects):
            if obj.get('ground_surface') or obj.get('aw_road') or obj.get('aw_template') or obj.get('animated'):continue
            key=tuple(v for row in obj.matrix_world for v in row)
            if _cache.get(obj.as_pointer())==key:continue
            if scene.aw.grid_snap:
                step=scene.aw.grid_size;obj.location.x=round(obj.location.x/step)*step;obj.location.y=round(obj.location.y/step)*step
            if scene.aw.rotation_snap:
                step=scene.aw.rotation_increment;obj.rotation_euler.z=round(obj.rotation_euler.z/step)*step
            if scene.aw.ground_snap:snap_object(obj,scene,scene.aw.align_surface,scene.aw.ground_offset,scene.aw.alignment_strength)
            _cache[obj.as_pointer()]=tuple(v for row in obj.matrix_world for v in row)
    finally:_busy=False

class AW_OT_place(bpy.types.Operator):
    bl_idname='aw.place';bl_label='Place asset';bl_description='Move over a surface; click to place, Esc to cancel';bl_options={'REGISTER','UNDO'}
    _created=None
    def invoke(self,context,event):
        if context.area.type!='VIEW_3D':return {'CANCELLED'}
        if not context.selected_objects:self.report({'WARNING'},'Select an object to place');return {'CANCELLED'}
        self._created=list(context.selected_objects);self._original={o.name:o.matrix_world.copy() for o in self._created};context.window_manager.modal_handler_add(self);context.area.header_text_set('PLACE · mouse to move · click to confirm · Esc to restore');return {'RUNNING_MODAL'}
    def modal(self,context,event):
        from bpy_extras import view3d_utils
        if event.type in {'ESC','RIGHTMOUSE'}:
            for o in self._created:
                if o.name in bpy.data.objects:o.matrix_world=self._original[o.name]
            context.area.header_text_set(None);return {'CANCELLED'}
        if event.type=='LEFTMOUSE' and event.value=='PRESS':context.area.header_text_set(None);return {'FINISHED'}
        if event.type=='MOUSEMOVE':
            # Invocations from our sidebar have a UI region with no RegionView3D.
            # Convert window coordinates against the actual viewport region.
            region=next(r for r in context.area.regions if r.type=='WINDOW');rv=context.space_data.region_3d
            coord=(event.mouse_x-region.x,event.mouse_y-region.y)
            if not (0<=coord[0]<region.width and 0<=coord[1]<region.height):return {'RUNNING_MODAL'}
            excluded=[o for root in self._created for o in [root,*root.children_recursive]]
            origin=view3d_utils.region_2d_to_origin_3d(region,rv,coord);direction=view3d_utils.region_2d_to_vector_3d(region,rv,coord);hit=cast_ground(context.scene,origin,excluded,direction)
            if hit:
                anchor=self._created[0];delta=hit[1]-anchor.matrix_world.translation
                for obj in self._created:obj.location+=delta
                for obj in self._created:
                    s=context.scene.aw
                    if s.grid_snap:obj.location.x=round(obj.location.x/s.grid_size)*s.grid_size;obj.location.y=round(obj.location.y/s.grid_size)*s.grid_size
                    snap_object(obj,context.scene,s.align_surface,s.ground_offset,s.alignment_strength)
        return {'RUNNING_MODAL'}
CLASSES=[AW_OT_place]
