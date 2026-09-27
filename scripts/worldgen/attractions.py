import bpy,math,json
from mathutils import Vector,Matrix
from .common import *
from .props import *

def animate_rotation(o,axis,amount,name,frames=720):
    o.rotation_mode='XYZ';o.rotation_euler[axis]=0;o.keyframe_insert(data_path='rotation_euler',index=axis,frame=1);o.rotation_euler[axis]=amount;o.keyframe_insert(data_path='rotation_euler',index=axis,frame=frames+1)
    action=o.animation_data.action;action.name=name
    for fc in action.fcurves:
        for p in fc.keyframe_points:p.interpolation='LINEAR'
        fc.modifiers.new('CYCLES')
    o['animated']=True;o['loop_frames']=frames
    # NLA tracks with the same name export as one synchronized glTF clip.
    ad=o.animation_data;track=ad.nla_tracks.new();track.name='WorldLoop';strip=track.strips.new(name,1,action);ad.action=None
    o.rotation_euler[axis]=0

def ferris(root,col,animated):
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(root/'assets/imported/ferris_wheel/source/Wheel model.fbx'));objs=list(set(bpy.data.objects)-before)
    # Real cabin groups, preserving the supplied geometry. Source spokes extend past the
    # actual rim, so radial links are rebuilt using the model's own dimensions.
    cabin_groups=[o for o in objs if o.type=='EMPTY' and o.name.startswith('Group') and int(o.name[5:]) in range(2,25,2)]
    cabin_parts=[]
    for group in sorted(cabin_groups,key=lambda o:o.name):
        parts=[o for o in group.children_recursive if o.type=='MESH'];cab=join(parts,'Ferris cabin imported',col);world_matrix=cab.matrix_world.copy();cab.parent=None;cab.matrix_world=world_matrix
        # Apply world-space vertex coordinates before pivoting.
        activate(cab);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        corners=[cab.matrix_world@Vector(p) for p in cab.bound_box];cx=(min(p.x for p in corners)+max(p.x for p in corners))/2;cy=(min(p.y for p in corners)+max(p.y for p in corners))/2;cz=max(p.z for p in corners)+.12
        old=bpy.context.scene.cursor.location.copy();bpy.context.scene.cursor.location=(cx,cy,cz);bpy.ops.object.origin_set(type='ORIGIN_CURSOR');bpy.context.scene.cursor.location=old;cab.location=(0,0,0);cabin_parts.append(cab)
    # Cabins are safe to join; remove source empties and out-of-radius spoke groups.
    wheel_candidates=[];static=[]
    objs=[o for o in bpy.data.objects if o not in before and o not in cabin_parts]
    for o in objs:
        if o.name not in bpy.data.objects or o in cabin_parts:continue
        if o.type=='EMPTY':continue
        if o.type!='MESH':continue
        ancestor=o.parent
        number=int(ancestor.name[5:]) if ancestor and ancestor.name.startswith('Group') and ancestor.name[5:].isdigit() else 0
        if 25<=number<=36:bpy.data.objects.remove(o,do_unlink=True);continue
        world=o.matrix_world.copy();o.parent=None;o.matrix_world=world
        if o.name.startswith('Torus') or o.name in ['Cylinder001','Line122','Line124','Line126','Line127','Line128','Line129'] or number==37:wheel_candidates.append(o)
        elif o.name=='Line125':bpy.data.objects.remove(o,do_unlink=True)
        else:static.append(o)
    for o in list(bpy.data.objects):
        if o not in before and o.type=='EMPTY':bpy.data.objects.remove(o,do_unlink=True)
    axle=Vector((0,0,4.424))
    for i in range(12):
        a=math.tau*i/12
        for x in [-.37,.37]:wheel_candidates.append(beam('Rim spoke',(x,0,4.424),(x,2.84*math.cos(a),4.424+2.84*math.sin(a)),.033,'cream',col))
    rotor=join(wheel_candidates,'FerrisWheel_Rotor',animated,axle)
    support=join(static,'FerrisWheel_StaticSupport',col,(0,0,0))
    for part in [rotor,support]:
        activate(part);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    # Unify imported materials into a small intentional palette.
    for o in [rotor,support,*cabin_parts]:
        for slot in o.material_slots:
            if not slot.material:continue
            name=slot.material.name.lower()
            slot.material=M['metal'] if any(s in name for s in ['black','metal','iron']) else M['cream'] if any(s in name for s in ['white','gray','grey']) else M['red']
        tag(o,'Attractions',collision=False)
        o['asset_source']='//../assets/imported/ferris_wheel/source/Wheel model.fbx'
    master=bpy.data.objects.new('FerrisWheel',None);col.objects.link(master);master.location=(130,45,.08);master.scale=(3.15,)*3;master.rotation_euler.z=math.pi/2
    support.parent=master;support.matrix_parent_inverse=Matrix.Identity(4)
    rotor.parent=master;rotor.matrix_parent_inverse=Matrix.Identity(4);rotor.location=axle
    animate_rotation(rotor,0,math.tau,'FerrisWheel / wheel rotation')
    for i,cab in enumerate(cabin_parts):
        angle=math.tau*i/len(cabin_parts);pivot=bpy.data.objects.new(f'FerrisWheel_CabinPivot_{i+1:02}',None);animated.objects.link(pivot);pivot.parent=rotor;pivot.location=(0,2.85*math.cos(angle),2.85*math.sin(angle));animate_rotation(pivot,0,-math.tau,f'FerrisWheel / cabin {i+1:02} upright');cab.parent=pivot;cab.matrix_parent_inverse=Matrix.Identity(4);cab.location=(0,0,0);cab.rotation_euler=(0,0,0);cab['animated']=True;cab.name=f'FerrisWheel_Cabin_{i+1:02}'
        # Different muted cabin colors; the real model remains recognizable.
        for slot in cab.material_slots:slot.material=M[['red','mint','yellow','cream'][i%4]]
    # Fixed structural colliders are simple, independent of visual spinning parts.
    for dx in [-5,5]:
        o=cube('Ferris support collision',(130+dx,45,4),(1,9,8),None,collection('COLLIDERS'));o.hide_render=True;o.display_type='WIRE';o['collision']=True;o['runtime_collider']=True;o['collision_shape']='BOX'
    master['asset_source']='//../assets/imported/ferris_wheel/source/Wheel model.fbx';master['object_type']='ferris_wheel';master['animation_seconds']=30
    return master

def loop(col):
    points=[];verts=[];faces=[];width=5.8;radius=10;segments=240
    for i in range(segments+1):
        t=i/segments;theta=math.tau*t;shift=9*(t*t*(3-2*t));p=Vector((-25+radius*math.sin(theta),-141+shift,.12+radius*(1-math.cos(theta))));points.append(p);verts.extend([p+Vector((0,-width/2,0)),p+Vector((0,width/2,0))])
        if i:faces.append((2*i-2,2*i,2*i+1,2*i-1))
    me=bpy.data.meshes.new('Loop continuous ribbon');me.from_pydata(verts,[],faces);o=bpy.data.objects.new('RoadLoop_Surface',me);col.objects.link(o);me.materials.append(bpy.data.materials.get('black') or M['black']);ground(o,'loop',.95);o['object_type']='vertical_loop';o['loop_radius']=radius;o['loop_width']=width;o['vehicle_assist']='tangent adhesion within this surface only';o['minimum_speed']=13.;o['aw_loop']=True
    uv=me.uv_layers.new(name='RoadUV')
    for li,lp in enumerate(me.loops):uv.data[li].uv=(lp.vertex_index%2,lp.vertex_index//2*.12)
    # Edge rails follow the full normal so they stay on the driving side when inverted.
    for sign_ in [-1,1]:
        c=bpy.data.curves.new('Loop rail','CURVE');c.dimensions='3D';c.bevel_depth=.075;c.bevel_resolution=1;s=c.splines.new('POLY');s.points.add(segments)
        for i,p in enumerate(points):
            theta=math.tau*i/segments;n=Vector((-math.sin(theta),0,math.cos(theta)));s.points[i].co=(*(p+Vector((0,sign_*(width/2-.12),0))+n*.3),1)
        rail=bpy.data.objects.new('Loop safety rail',c);col.objects.link(rail);c.materials.append(M['cream']);tag(rail,'Roads')
    for x,z in [(-35,10),(-15,10)]:beam('Loop truss',(x,-137,-.1),(x,-137,z),.25,'mint',col)
    o['path_points']=json.dumps([list(p) for p in points]);return o
