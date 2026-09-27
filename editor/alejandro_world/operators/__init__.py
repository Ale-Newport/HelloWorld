import bpy,random
from ..core import activate
from ..placement import snap_object
class AW_OT_quick(bpy.types.Operator):
    bl_idname='aw.quick';bl_label='Quick tool';bl_options={'REGISTER','UNDO'}
    action:bpy.props.StringProperty()
    def execute(self,context):
        objects=list(context.selected_objects);o=context.object
        if not o:return {'CANCELLED'}
        if self.action in ('DROP','ALIGN'):
            for ob in objects:snap_object(ob,context.scene,self.action=='ALIGN',context.scene.aw.ground_offset,context.scene.aw.alignment_strength)
        elif self.action=='DUPLICATE':
            for root in objects:
                for child in root.children_recursive:child.select_set(True)
            bpy.ops.object.duplicate(linked=True)
        elif self.action=='DELETE':
            for root in objects:
                for child in root.children_recursive:child.select_set(True)
            bpy.ops.object.delete()
        elif self.action=='FOCUS':bpy.ops.view3d.view_selected(use_all_regions=False)
        elif self.action=='ISOLATE':bpy.ops.view3d.localview(frame_selected=True)
        elif self.action=='PIVOT':bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY',center='BOUNDS')
        elif self.action=='ROTATION':
            for ob in objects:ob.rotation_euler=(0,0,0)
        elif self.action=='SCALE':
            for ob in objects:ob.scale=(1,1,1)
        elif self.action=='APPLY':bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        elif self.action=='RANDOM':
            for ob in objects:ob.rotation_euler.z=random.uniform(0,6.283185)
        elif self.action=='LOCK':
            for ob in objects:ob.lock_location=(True,)*3;ob.lock_rotation=(True,)*3;ob.lock_scale=(True,)*3
        elif self.action=='UNLOCK':
            for ob in objects:ob.lock_location=(False,)*3;ob.lock_rotation=(False,)*3;ob.lock_scale=(False,)*3
        elif self.action=='HIDE':
            for ob in objects:ob.hide_set(True)
        elif self.action=='SHOW':
            for ob in context.scene.objects:ob.hide_set(False)
        elif self.action=='METADATA':
            from ..core import tag
            tag(o)
        return {'FINISHED'}
CLASSES=[AW_OT_quick]
