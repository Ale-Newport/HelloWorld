"""Native Bullet settings plus explicitly labelled runtime-only fields."""
import bpy
from ..core import activate

def configure(o,mode='STATIC',shape='CONVEX_HULL',mass=1,friction=.65):
    if o.type!='MESH':return
    previous=bpy.context.view_layer.objects.active
    activate(o)
    if not o.rigid_body:bpy.ops.rigidbody.object_add()
    rb=o.rigid_body;rb.type='PASSIVE' if mode=='STATIC' else 'ACTIVE';rb.kinematic=mode=='KINEMATIC';rb.collision_shape=shape;rb.mass=max(.001,mass);rb.friction=friction;rb.restitution=.08;rb.linear_damping=.08;rb.angular_damping=.12;rb.use_margin=True;rb.collision_margin=.005
    o['physics_enabled']=True;o['physics_mode']=mode;o['collision']=True;o['collision_shape']=shape;o['mass']=mass;o['friction']=friction;o['interactive']=mode!='STATIC';o['interaction_type']='physics' if mode!='STATIC' else 'none';o['static_decoration']=mode=='STATIC'
    o['rolling_friction']=o.get('rolling_friction',.015);o['gravity_scale']=o.get('gravity_scale',1.)
    return rb

def sync(o):
    rb=o.rigid_body
    if rb:
        for k in ['mass','friction','restitution','linear_damping','angular_damping','collision_shape']:o[k]=getattr(rb,k)
        o['physics_mode']='STATIC' if rb.type=='PASSIVE' else ('KINEMATIC' if rb.kinematic else 'DYNAMIC')
        o['physics_enabled']=True;o['collision']=rb.enabled if rb.type=='ACTIVE' else True
        o['lock_translation']=list(o.lock_location);o['lock_rotation']=list(o.lock_rotation)

class AW_OT_physics(bpy.types.Operator):
    bl_idname='aw.physics';bl_label='Set physics';bl_options={'REGISTER','UNDO'}
    mode:bpy.props.EnumProperty(items=[(x,x.title(),'') for x in ['STATIC','DYNAMIC','KINEMATIC','AUTO','REMOVE']])
    def execute(self,context):
        for o in list(context.selected_objects):
            if o.type!='MESH':continue
            if self.mode=='REMOVE':
                activate(o)
                if o.rigid_body:bpy.ops.rigidbody.object_remove()
                o['physics_enabled']=False;o['collision']=False;continue
            mode=self.mode if self.mode!='AUTO' else ('STATIC' if max(o.dimensions)>5 or o.get('ground_surface') else 'DYNAMIC')
            configure(o,mode,'MESH' if mode=='STATIC' else 'CONVEX_HULL',max(.1,o.dimensions.x*o.dimensions.y*o.dimensions.z*2))
        return {'FINISHED'}
class AW_OT_axis_locks(bpy.types.Operator):
    bl_idname='aw.axis_locks';bl_label='Apply native axis locks';bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        from ..core import collection
        o=context.object
        if not o or not o.rigid_body:self.report({'WARNING'},'Select a rigid body first');return {'CANCELLED'}
        key='LOCK_'+o.name;anchor=bpy.data.objects.get(key)
        if not anchor:
            anchor=bpy.data.objects.new(key,None);collection('PHYSICS_CONSTRAINTS',collection('SYSTEM')).objects.link(anchor)
        anchor.matrix_world=o.matrix_world.copy();activate(anchor)
        if not anchor.rigid_body_constraint:bpy.ops.rigidbody.constraint_add()
        rb=anchor.rigid_body_constraint;rb.type='GENERIC';rb.object1=o;rb.object2=None
        for axis,locked in zip('xyz',o.lock_location):
            setattr(rb,'use_limit_lin_'+axis,locked);setattr(rb,'limit_lin_'+axis+'_lower',0);setattr(rb,'limit_lin_'+axis+'_upper',0)
        for axis,locked in zip('xyz',o.lock_rotation):
            setattr(rb,'use_limit_ang_'+axis,locked);setattr(rb,'limit_ang_'+axis+'_lower',0);setattr(rb,'limit_ang_'+axis+'_upper',0)
        anchor.hide_render=True;activate(o);sync(o);return {'FINISHED'}
CLASSES=[AW_OT_physics,AW_OT_axis_locks]
