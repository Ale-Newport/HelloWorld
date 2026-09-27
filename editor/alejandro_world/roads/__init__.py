"""Editable Bezier authoring with regenerable ribbons, UVs and guardrails."""
import bpy,math,json
from mathutils import Vector
from mathutils.geometry import interpolate_bezier
from ..core import collection,move_to,material,tag

def sample(curve,resolution=12):
    bpy.context.view_layer.update()
    out=[]
    for s in curve.data.splines:
        if s.type=='BEZIER':
            n=len(s.bezier_points);steps=n if s.use_cyclic_u else n-1
            for i in range(steps):
                a,b=s.bezier_points[i],s.bezier_points[(i+1)%n]
                out += [curve.matrix_world@p for p in interpolate_bezier(a.co,a.handle_right,b.handle_left,b.co,resolution+1)[:-1]]
            out.append(out[0].copy() if s.use_cyclic_u else curve.matrix_world@s.bezier_points[-1].co)
        else:out += [curve.matrix_world@Vector(p.co[:3]) for p in s.points]
    return out

def ribbon(name,points,width,mat,col,side_offset=0,z_offset=0,road=True):
    verts=[];faces=[];distances=[0.]
    for i,p in enumerate(points):
        tangent=((points[1]-points[-2]) if (points[0]-points[-1]).length<.001 and i in (0,len(points)-1) else (points[min(i+1,len(points)-1)]-points[max(i-1,0)])).normalized()
        if abs(tangent.z)>.9:side=Vector((0,1,0))
        else:side=Vector((-tangent.y,tangent.x,0)).normalized()
        if i:distances.append(distances[-1]+(p-points[i-1]).length)
        verts.extend([p+side*(side_offset-width/2)+Vector((0,0,z_offset)),p+side*(side_offset+width/2)+Vector((0,0,z_offset))])
        if i:faces.append((2*i-2,2*i,2*i+1,2*i-1))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();uv=me.uv_layers.new(name='RoadUV')
    for face in me.polygons:
        for li in face.loop_indices:
            vi=me.loops[li].vertex_index;uv.data[li].uv=(vi%2,distances[vi//2]/4)
    o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(mat)
    tag(o,'Roads',ground_surface=road,road=road,drivable=road,collision=road,surface_type='asphalt',friction=.9)
    return o

def create_road(name,points,width=6,closed=False,col=None,mat=None):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=16
    s=c.splines.new('BEZIER');s.bezier_points.add(len(points)-1)
    for p,co in zip(s.bezier_points,points):p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
    s.use_cyclic_u=closed;o=bpy.data.objects.new(name,c);(col or collection('ROADS')).objects.link(o)
    o['aw_road']=True;o['road_width']=width;o['barrier_left']=False;o['barrier_right']=False;o['road_material']=(mat.name if mat else 'AW Asphalt');o['generated_id']=o.name;o.hide_render=True
    regenerate(o);return o

def regenerate(curve):
    name=curve['generated_id'];col=curve.users_collection[0]
    for o in list(bpy.data.objects):
        if o.get('road_owner')==name or o.name.startswith(name+' edge') or (name=='Catalunya Club' and o.name.startswith('Race kerb')):bpy.data.objects.remove(o,do_unlink=True)
    points=sample(curve);width=curve.get('road_width',6)
    if len(points)<2:return
    mat=bpy.data.materials.get(curve.get('road_material','')) or material('AW Asphalt',(.075,.09,.10,1))
    surface=ribbon(name+' / surface',points,width,mat,col);surface['road_owner']=name
    controls=[]
    for spline in curve.data.splines:
        if spline.type=='BEZIER':
            for bp in spline.bezier_points:
                p=curve.matrix_world@bp.co;controls.append([p.x,p.z,-p.y])
    surface['road_points']=json.dumps(controls);surface['road_width']=width;surface['road_closed']=curve.data.splines[0].use_cyclic_u;surface['editable_root']=True;surface['aw_id']='road:'+name
    edge=material('AW Road edge',(.88,.81,.66,1))
    for side in (-1,1):
        o=ribbon(name+f' / edge {side}',points,.22,edge,col,side*(width/2-.22),.018,False);o['road_owner']=name
        if curve.get('barrier_left' if side<0 else 'barrier_right',False):
            c=bpy.data.curves.new(name+' barrier','CURVE');c.dimensions='3D';c.bevel_depth=.12;c.bevel_resolution=0
            s=c.splines.new('POLY');s.points.add(len(points)-1)
            for i,p in enumerate(points):
                t=(points[min(i+1,len(points)-1)]-points[max(i-1,0)]).normalized();v=p+Vector((-t.y,t.x,0))*(side*(width/2+.35))+Vector((0,0,.65));s.points[i].co=(*v,1)
            ob=bpy.data.objects.new(name+f' / barrier {side}',c);col.objects.link(ob);c.materials.append(edge);ob['road_owner']=name;tag(ob,'Roads',collision=True)
    return surface

class AW_OT_road(bpy.types.Operator):
    bl_idname='aw.road';bl_label='Road tools';bl_options={'REGISTER','UNDO'}
    action:bpy.props.EnumProperty(items=[(x,x,'') for x in ['ADD','EXTEND','REBUILD','COLLISION']])
    def execute(self,context):
        o=context.object
        if self.action=='ADD':
            p=context.scene.cursor.location;o=create_road('Road',[(p.x-8,p.y,p.z+.03),(p.x,p.y,p.z+.03),(p.x+8,p.y+3,p.z+.03)])
            from ..core import activate
            activate(o)
        elif not o or not o.get('aw_road'):self.report({'WARNING'},'Select a road guide');return {'CANCELLED'}
        elif self.action=='EXTEND':
            s=o.data.splines[0];last=s.bezier_points[-1].co.copy();s.bezier_points.add(1);p=s.bezier_points[-1];p.co=last+Vector((8,0,0));p.handle_left_type=p.handle_right_type='AUTO';regenerate(o)
        else:
            ob=regenerate(o)
            if self.action=='COLLISION':
                from ..physics import configure
                configure(ob,'STATIC','MESH')
        return {'FINISHED'}
CLASSES=[AW_OT_road]
