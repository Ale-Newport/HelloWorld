"""Purposeful landscape detail and road junction finishing."""
import bpy,math,random
from mathutils import Vector
from .common import *
from .props import *
from alejandro_world.roads import sample,regenerate

def polish(root,cols):
    park=cols['PARK'];race=cols['RACE_TRACK'];veg=cols['VEGETATION'];deco=cols['DECORATION']
    car=car_model('Paddock roadster',(-172,-61,0),cols['VEHICLES']);template(car,'AN Roadster','Vehicles')
    player=car_model('Player vehicle marker',(44,-48,0),cols['VEHICLES']);player['preview_skip']=True;player['collision']=False
    # Broad lawns break up the new ground without covering driveable routes.
    patches=[('Circuit inner meadow',(-186,-13),30,18,race),('Circuit turn garden',(-129,11),9,9,race),('Circuit north meadow',(-217,42),11,6,race),('Winter east garden',(61,126),4,13,park),('Wheel west lawn',(104,56),6,10,park),('Wheel east lawn',(148,58),8,8,park),('Loop workshop garden',(-48,-113),15,5,park),('Loop south meadow',(0,-147),16,6,park)]
    for name,center,rx,ry,col in patches:flat_patch(name,center,rx,ry,col,'grass',.009)
    # Low hill / lookout within the track, with mesh slopes and a gravel footpath.
    hill=ico('Circuit lookout hill',(-188,-5,-.65),(13,9,3),'grass',race,2);ground(hill,'terrain',.8)
    cylinder('Lookout stone platform',(-188,-5,2.0),3.5,.3,'cream',race,12)
    bench('Circuit lookout bench',(-188,-5,2.16),race)
    sign('Lookout sign','CHOOSE YOUR NEXT TURN',(-186,-7,2.0),race)
    # Source palette grass islands and a few flower beds, clustered by destination.
    rng=random.Random(51)
    for cx,cy,rx,ry,count in [(-188,-16,26,9,30),(-87,115,25,5,18),(142,60,7,4,10),(-38,-151,25,4,15)]:
        parts=[]
        for i in range(count):
            a=rng.uniform(0,math.tau);r=math.sqrt(rng.random());x=cx+rx*r*math.cos(a);y=cy+ry*r*math.sin(a)
            parts.append(ico('Shrub', (x,y,.28),(.5+rng.random()*.5,.5,.45),'grass',veg,1))
            if i%3==0:
                parts.append(ico('Warm flower',(x+.2,y,.67),(.14,.14,.12),'yellow' if i%2 else 'red',veg,1))
        o=join(parts,'Garden bed',veg);o['collision']=False
    # Repair source curve handle evaluation before generating the final surface.
    for curve in [o for o in bpy.data.objects if o.get('aw_road')]:regenerate(curve)
    # Flush junction discs cover crossing edge strokes without changing collision heights.
    for x,y,r in [(-25,-141,3.2),(-25,-132,3.2),(20,98,4.5),(-128,-44,4.7),(-77,-18,4.0),(62,41,4.0),(37,-77,4.0),(-52,-68,4.0)]:
        o=cylinder('Road junction',(x,y,.045),r,.015,'black',cols['ROADS'],32);ground(o,'asphalt',.9)
    # Support pieces read as small bridges where routes cross water between islands.
    for x,y,angle in [(-97,-19,-.1),(94,42,-.2),(-65,-90,-.65)]:
        deck=cube('Connecting bridge deck',(x,y,-.12),(14,7,.3),'cream',cols['ROADS'],.06);deck.rotation_euler.z=angle;ground(deck,'paving',.8)
        for side in [-1,1]:
            a=Vector((-7,side*3.45,.5));b=Vector((7,side*3.45,.5))
            def rotate(p):return Vector((x+p.x*math.cos(angle)-p.y*math.sin(angle),y+p.x*math.sin(angle)+p.y*math.cos(angle),p.z))
            beam('Bridge guardrail',rotate(a),rotate(b),.07,'metal',cols['ROADS'])
            for u in [-6,0,6]:
                p=rotate(Vector((u,side*3.45,0)));beam('Bridge pier',(p.x,p.y,-1),(p.x,p.y,.62),.10,'wood',cols['ROADS'])
    # Tame the supplied wheel's flat material override with a structural palette.
    support=bpy.data.objects.get('FerrisWheel_StaticSupport')
    if support:
        # Assign by face height in local coordinates, retaining the actual imported model.
        support.data.materials.clear()
        for m in [M['cream'],M['red'],M['metal']]:support.data.materials.append(m)
        for p in support.data.polygons:
            z=sum(support.data.vertices[v].co.z for v in p.vertices)/len(p.vertices);p.material_index=0 if z>1.4 else 1 if z>.45 else 2
    rotor=bpy.data.objects.get('FerrisWheel_Rotor')
    if rotor:
        rotor.data.materials.clear();rotor.data.materials.append(M['cream']);rotor.data.materials.append(M['red'])
        for p in rotor.data.polygons:
            center=p.center;r=math.hypot(center.y,center.z);p.material_index=1 if r>2.7 else 0
    # Original atlas slabs are retained as source. A calmer repeated paving material
    # avoids displaying the entire atlas at every 3 metres.
    paving=bpy.data.objects.get('Wheel tiled plaza');m=bpy.data.materials.get('AW Plaza tiles')
    if paving and m:
        n=m.node_tree.nodes;tex=next(n for n in n if n.type=='TEX_IMAGE');mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.35;mix.inputs[2].default_value=(.68,.56,.39,1);m.node_tree.links.new(tex.outputs['Color'],mix.inputs[1]);m.node_tree.links.new(mix.outputs[0],n.get('Principled BSDF').inputs['Base Color'])
        # Export stays PBR-compatible by tinting the Principled base while keeping texture.
        m.node_tree.links.new(tex.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);n.get('Principled BSDF').inputs['Base Color'].default_value=(.68,.56,.39,1)
        for uv in paving.data.uv_layers.active.data:uv.uv*=.4
