"""Move the source race furniture to its redesigned western circuit.
The original road network remains a boulevard connecting the old district.
"""
import bpy,math
from mathutils import Vector,Matrix
from .common import *
from alejandro_world.physics import configure

def migrate_circuit(cols):
    race=cols['RACE_TRACK'];counters={};groups={'cones','barrels','startingLights','timer','leaderboard','podium','banners','airDancers','obstacles','zigzag'}
    # Operate at the authored hierarchy root; descendants retain full local matrices.
    candidates=[]
    for o in list(bpy.data.objects):
        memberships=set(o.get('w2Collections',[]));kind=next(iter(memberships&groups),None)
        if not kind or o.get('w2Role')=='collider':continue
        if o.parent and set(o.parent.get('w2Collections',[]))&groups:continue
        if o.type not in {'MESH','EMPTY'}:continue
        candidates.append((o,kind))
    for o,kind in candidates:
        i=counters.get(kind,0);counters[kind]=i+1
        meshes=[x for x in [o,*o.children_recursive] if x.type=='MESH' and not x.hide_render]
        if not meshes:
            o.hide_render=True;continue
        if kind=='zigzag':
            # Oversized lane blockers are retained as reusable source references.
            for member in [o,*o.children_recursive]:member.hide_render=True;member.hide_set(True);member['collision']=False;move_to(member,cols['SOURCE_REFERENCES'])
            continue
        spots={'cones':(-213+i*3,-53),'barrels':(-208+i*2.1,-69),'startingLights':(-179,-44),'timer':(-177,-49),'leaderboard':(-155+i*3,-58),'podium':(-147+i*2,-61),'banners':(-217+i*5,-58),'airDancers':(-218+i*5,-62),'obstacles':(-246+i*3,19)}
        x,y=spots[kind];world=o.matrix_world.copy();o.parent=None;o.matrix_world=world;bpy.context.view_layer.update()
        pts=[m.matrix_world@Vector(p) for m in meshes for p in m.bound_box];center=Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,(min(p.y for p in pts)+max(p.y for p in pts))/2,min(p.z for p in pts)))
        offset=Vector((x,y,.02 if kind!='startingLights' else 3.8))-center;o.location+=offset
        for member in [o,*o.children_recursive]:
            if member.get('w2Role')!='collider':move_to(member,race)
            member['original_circuit_relocated']=True
        if o.type=='MESH' and kind in {'cones','barrels'}:configure(o,'DYNAMIC','CONVEX_HULL',.65 if kind=='cones' else 4,.45)
    return counters
