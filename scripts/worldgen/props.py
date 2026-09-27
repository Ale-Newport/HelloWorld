import bpy,math,random
from mathutils import Vector,Matrix
from .common import *
from alejandro_world.physics import configure

def penguin(name,loc,col,scale=1,angle=0):
    x,y,z=loc;parts=[uv_sphere('body',(x,y,z+.62),(.36,.3,.53),'navy',col),uv_sphere('belly',(x,y-.235,z+.64),(.255,.10,.38),'white',col),uv_sphere('head',(x,y,z+1.15),(.285,.275,.29),'navy',col),uv_sphere('face',(x,y-.22,z+1.14),(.20,.075,.18),'white',col)]
    beak=cylinder('beak',(x,y-.32,z+1.13),.11,.20,'orange',col,8,r2=.02);beak.rotation_euler.x=math.pi/2;parts.append(beak)
    for dx in [-.13,.13]:parts.append(uv_sphere('eye',(x+dx,y-.272,z+1.22),(.035,.023,.04),'black',col))
    for dx in [-.19,.19]:parts.append(uv_sphere('foot',(x+dx,y-.13,z+.08),(.16,.23,.065),'orange',col))
    for dx in [-.36,.36]:
        wing=uv_sphere('wing',(x+dx,y+.01,z+.64),(.105,.16,.32),'navy',col);wing.rotation_euler.y=(-1 if dx<0 else 1)*.3;parts.append(wing)
    parts.append(beam('learner handle',(x-.24,y+.1,z+.98),(x+.24,y+.1,z+.98),.05,'mint',col))
    o=join(parts,name,col,(x,y-.13,z+.28));o.rotation_euler.z=angle;o.scale=(scale,)*3;tag(o,'Ice Area',interactive=True,collision=True,interaction_type='physics',surface_type='plastic');o['aw_new']=True
    configure(o,'DYNAMIC','CONVEX_HULL',2.2,.08);o.rigid_body.linear_damping=.018;o.rigid_body.angular_damping=.035;o.rigid_body.restitution=.18;o['center_of_mass']='low pivot 0.28m';o['support_centred']=True;return o

def cone(name,loc,col,fallen=False):
    x,y,z=loc;parts=[cube('base',(x,y,z+.055),(.57,.57,.11),'black',col,.025),cylinder('cone',(x,y,z+.39),.225,.64,'orange',col,12,r2=.035),cylinder('stripe',(x,y,z+.45),.14,.13,'cream',col,12,r2=.10)]
    o=join(parts,name,col,(x,y,z+.27));tag(o,'Props',interactive=True,collision=True,interaction_type='physics');o['aw_new']=True
    if fallen:o.rotation_euler.y=math.pi/2;o.location.z=z+.3
    configure(o,'DYNAMIC','CONVEX_HULL',.65,.12);o.rigid_body.linear_damping=.025;return o

def bench(name,loc,col,angle=0):
    x,y,z=loc;parts=[]
    for dy in [-.18,0,.18]:parts.append(cube('slat',(x,y+dy,z+.48),(1.75,.14,.095),'wood',col,.025))
    for zz in [.83,1.02]:parts.append(cube('back',(x,y+.25,z+zz),(1.75,.09,.13),'wood',col,.02))
    for dx in [-.63,.63]:parts.append(beam('leg',(x+dx,y-.18,z),(x+dx,y+.23,z+.85),.055,'metal',col))
    o=join(parts,name,col,(x,y,z));o.rotation_euler.z=angle;tag(o,'Street furniture',collision=True);return o

def lamp(name,loc,col):
    x,y,z=loc;parts=[cylinder('base',(x,y,z+.12),.22,.24,'metal',col),cylinder('pole',(x,y,z+1.8),.07,3.5,'metal',col),cube('lamp',(x,y,z+3.6),(.4,.4,.48),'cream',col,.05),cylinder('cap',(x,y,z+3.94),.34,.18,'metal',col,4,r2=.0)]
    o=join(parts,name,col,(x,y,z));tag(o,'Street furniture',collision=True);return o

def sign(name,body,loc,col,color='mint'):
    x,y,z=loc;parts=[cube('post',(x,y,z+1.1),(.13,.14,2.2),'wood',col),cube('board',(x,y,z+2.05),(3,.16,.7),color,col,.07)]
    ob=join(parts,name,col,loc);tag(ob,'Signs',collision=True)
    tx=text(name+' lettering',body,(x,y-.09,z+2.05),.29,'cream',col,(math.pi/2,0,0));return ob

def pine(name,loc,col,size=1):
    x,y,z=loc;parts=[cylinder('trunk',(x,y,z+.65),.14,1.3,'wood',col,7)]
    for h,r in [(1.35,1.0),(2.05,.8),(2.65,.6)]:parts.append(cylinder('foliage',(x,y,z+h),r,1.5,'grass',col,7,r2=.02))
    o=join(parts,name,col,loc);o.scale=(size,)*3;tag(o,'Trees',collision=False);o['lod_distance']=130;return o

def robot(name,loc,col):
    x,y,z=loc;parts=[cube('body',(x,y,z+.52),(.45,.34,.48),'cream',col,.05),cube('head',(x,y,z+.94),(.57,.4,.36),'mint',col,.08)]
    for dx in [-.15,.15]:parts += [uv_sphere('eye',(x+dx,y-.205,z+.98),(.045,.025,.055),'navy',col),cube('feet',(x+dx,y-.03,z+.12),(.16,.30,.18),'metal',col,.03)]
    parts.append(beam('antenna',(x,y,z+1.1),(x+.08,y,z+1.35),.025,'orange',col));o=join(parts,name,col,loc);tag(o,'Characters',interactive=True,collision=True,interaction_type='physics');configure(o,'DYNAMIC','CONVEX_HULL',1.4,.4);return o

def linked(o,name,loc,col,scale=1,rot=0):
    new=o.copy();new.data=o.data;new.animation_data_clear();new.name=name;col.objects.link(new);new.parent=None;new.matrix_world=Matrix.Identity(4);new.location=loc;new.scale=(scale,)*3;new.rotation_euler.z=rot;new.hide_render=False;new.hide_set(False);new['aw_template']=False;return new

def template(o,label,category):
    new=o.copy();new.data=o.data;new.name='LIB_'+label;collection('ASSET_LIBRARY').objects.link(new);new.parent=None;new.location=(0,0,-100);new.hide_render=True;new.hide_set(True);new['aw_template']=True;new['asset_label']=label;new['category']=category;new.asset_mark();new.asset_data.description='Alejandro World · '+category
    return new

def car_model(name,loc,col):
    x,y,z=loc;parts=[cube('Roadster body',(x,y,z+.68),(2.56,1.6,.66),'cream',col,.10),cube('Graphite sill',(x,y,z+.36),(2.6,1.68,.18),'navy',col,.04),cube('Glazed cabin',(x-.15,y,z+1.18),(1.05,1.32,.32),'navy',col,.07),cube('Roof',(x-.15,y,z+1.38),(1.12,1.36,.08),'cream',col,.03),cube('Vermilion stripe',(x+.7,y,z+1.02),(1.1,.16,.035),'red',col)]
    for dx in [-.9,.9]:
        for dy in [-.84,.84]:
            wheel=cylinder('Roadster tyre',(x+dx,y+dy,z+.4),.4,.32,'black',col,16);wheel.rotation_euler.x=math.pi/2;parts.append(wheel)
            hub=cylinder('Roadster hub',(x+dx,y+dy,z+.4),.2,.34,'cream',col,12);hub.rotation_euler.x=math.pi/2;parts.append(hub)
    o=join(parts,name,col,(x,y,z+.55));tag(o,'Vehicles',collision=True,object_type='vehicle',drivable=False);o['collision_shape']='CONVEX_HULL';return o
