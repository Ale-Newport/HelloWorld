import bpy,math,random
from mathutils import Vector,Matrix
from alejandro_world.core import collection,move_to,material,tag,activate
M={}
def setup():
    colors={'sand':(.59,.39,.19,1),'soil':(.25,.15,.095,1),'grass':(.20,.34,.085,1),'mint':(.20,.55,.43,1),'cream':(.86,.79,.61,1),'red':(.62,.12,.075,1),'orange':(.95,.32,.035,1),'navy':(.035,.095,.12,1),'white':(.85,.92,.90,1),'snow':(.66,.80,.80,1),'ice':(.17,.55,.65,1),'wood':(.31,.16,.07,1),'metal':(.10,.16,.17,1),'yellow':(.94,.59,.07,1),'black':(.025,.035,.04,1)}
    for name,color in colors.items():M[name]=material('AW '+name.title(),color,.24 if name=='ice' else .7,.12 if name in ['metal','ice'] else 0)

def finish(o,name,col,mat=None):
    o.name=name;move_to(o,col)
    if mat:o.data.materials.append(M.get(mat,mat) if isinstance(mat,str) else mat)
    tag(o);o['aw_new']=True
    return o

def cube(name,loc,size,mat,col,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);finish(o,name,col,mat)
    o['collision']=True;o['collision_shape']='MESH'
    if bevel:
        m=o.modifiers.new('Soft corners','BEVEL');m.width=min(bevel,min(size)*.2);m.segments=1;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o

def uv_sphere(name,loc,size,mat,col):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,col,mat)

def ico(name,loc,size,mat,col,sub=1):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=loc);o=bpy.context.object;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return finish(o,name,col,mat)

def cylinder(name,loc,radius,depth,mat,col,vertices=12,r2=None):
    if r2 is None:bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    else:bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=radius,radius2=r2,depth=depth,location=loc)
    o=finish(bpy.context.object,name,col,mat);o['collision']=True;o['collision_shape']='MESH';return o

def beam(name,a,b,r,mat,col):
    a,b=Vector(a),Vector(b);o=cylinder(name,(a+b)/2,r,(b-a).length,mat,col,8);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def text(name,body,loc,size,mat,col,rot=(0,0,0),extrude=.025):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.extrude=extrude;c.align_x='CENTER';c.align_y='CENTER';c.bevel_depth=.008
    font=bpy.data.fonts.get('Geist-Bold.ttf')
    if font:c.font=font
    o=bpy.data.objects.new(name,c);col.objects.link(o);o.location=loc;o.rotation_euler=rot;c.materials.append(M[mat]);tag(o,'Signs');o['aw_new']=True;return o

def join(parts,name,col,pivot=None):
    parts=[o for o in parts if o and o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.hide_set(False);o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name=name;move_to(o,col)
    if pivot is not None:
        old=bpy.context.scene.cursor.location.copy();bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.context.scene.cursor.location=old
    return o

def ground(o,kind='terrain',friction=.7):
    o['ground_surface']=True;o['collision']=True;o['drivable']=True;o['surface_type']=kind;o['friction']=friction;o['terrain']=kind=='terrain';return o

def island(name,center,rx,ry,col,mat='sand',seed=1,z=-.015,n=72):
    r=random.Random(seed);cx,cy=center
    ring=[]
    for i in range(n):
        a=i*math.tau/n;f=1+.028*math.sin(5*a+seed)+.018*math.cos(9*a);ring.append((cx+rx*math.cos(a)*f,cy+ry*math.sin(a)*f,z))
    verts=[(cx,cy,z)]+ring+[(x,y,-2.3) for x,y,_ in ring];faces=[]
    for i in range(n):faces.append((0,1+i,1+(i+1)%n));faces.append((1+i,1+n+i,1+n+(i+1)%n,1+(i+1)%n))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(M[mat]);me.materials.append(M['soil']);o=bpy.data.objects.new(name,me);col.objects.link(o)
    for p in me.polygons:p.material_index=p.index%2
    uv=me.uv_layers.new(name='WorldUV')
    for li,loop in enumerate(me.loops):v=me.vertices[loop.vertex_index].co;uv.data[li].uv=(v.x/8,v.y/8)
    tag(o,'Nature',ground_surface=True,terrain=True,drivable=True,collision=True,surface_type='terrain',friction=.7);return o

def flat_patch(name,center,rx,ry,col,mat,z=.005,n=48):
    cx,cy=center;verts=[(cx,cy,z)]+[(cx+rx*math.cos(i*math.tau/n)*(1+.04*math.sin(i*math.tau/n*3)),cy+ry*math.sin(i*math.tau/n)*(1+.03*math.cos(i*math.tau/n*5)),z) for i in range(n)]
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[(0,i+1,(i+1)%n+1) for i in range(n)]);o=bpy.data.objects.new(name,me);col.objects.link(o);me.materials.append(M[mat]);tag(o);o['aw_new']=True;return o

def save_camera(name,loc,target,scale,col):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);col.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=scale;return o
