import bpy,math,random,json
from mathutils import Vector
from .common import *
from .props import *
from .attractions import ferris,loop
from alejandro_world.roads import create_road,sample,ribbon

ROUTES=[]
def road(name,pts,width,col,closed=False):
    o=create_road(name,[(x,y,z if len(p)==3 else .035) for p in pts for x,y,*rest in [p] for z in [rest[0] if rest else .035]],width,closed,col,bpy.data.materials.get('black'))
    ROUTES.append(o);return o

def zones(root,cols,sources):
    terrain=cols['TERRAIN'];roads=cols['ROADS'];deco=cols['DECORATION'];veg=cols['VEGETATION'];props=cols['PROPS'];ice=cols['ICE_RINK'];race=cols['RACE_TRACK'];plaza=cols['ATTRACTIONS'];loopcol=cols['ROAD_LOOP']
    island('Western motorsport island',(-176,-3),83,77,terrain,seed=4)
    island('Northern garden causeway',(-81,103),76,27,terrain,seed=8)
    island('Winter lake island',(25,121),47,39,terrain,seed=2)
    island('Newport wheel gardens',(125,42),42,37,terrain,seed=6)
    island('Southern loop workshop',(-23,-132),64,29,terrain,seed=3)
    # Broad connective routes are separate curves so junctions stay editable.
    road('West / pit connection',[(-77,-18),(-103,-19),(-118,-33),(-140,-44)],6.2,roads)
    road('North / garden drive',[(-140,27),(-129,83),(-99,103),(-58,104),(-15,104),(30,98),(65,88)],6.2,roads)
    road('East / wheel promenade',[(62,41),(83,44),(103,39),(127,30),(144,28)],6.2,roads)
    road('Winter / lake entrance',[(20,98),(22,110),(25,123)],7,roads)
    road('South / loop entry',[(-52,-68),(-74,-92),(-75,-119),(-64,-141),(-25,-141)],6,roads)
    road('South / loop return',[(-25,-132),(6,-132),(30,-113),(37,-77)],6,roads)
    # Race circuit: long main straight, opening S, long T3, infield hairpins,
    # back straight and fast final pair, adapted to a 140 x 105 m diorama.
    pts=[(-230,-44),(-200,-44),(-166,-44),(-128,-44),(-112,-40),(-113,-29),(-124,-25),(-119,-16),(-109,7),(-115,23),(-134,29),(-149,19),(-147,5),(-157,-1),(-165,8),(-172,25),(-181,37),(-190,37),(-191,48),(-207,54),(-226,50),(-237,40),(-230,30),(-211,33),(-202,25),(-207,15),(-222,10),(-238,-5),(-243,-25)]
    circuit=road('Barcelona / Bezier circuit',pts,7.4,race,True);circuit['object_type']='race_circuit';circuit['layout_reference']='Barcelona-Catalunya inspired, simplified';circuit['track_length']=sum((b-a).length for a,b in zip(sample(circuit),sample(circuit)[1:]));circuit['turn_count']=14
    centerline=sample(circuit,18)
    # Alternating curb segments share only two materials; low-poly meshes remain separate by section.
    for side in [-1,1]:
        for start in range(0,len(centerline)-1,10):
            seg=centerline[start:min(len(centerline),start+11)]
            if len(seg)<2:continue
            ob=ribbon(f'Barcelona curb {side} {start//10:02}',seg,.65,M['red' if start//10%2 else 'cream'],race,side*3.95,.025,False);ob['category']='Race Track'
        for start in range(0,len(centerline)-1,40):
            seg=centerline[start:min(len(centerline),start+29)]
            if len(seg)<2:continue
            ob=ribbon(f'Grass verge {side} {start}',seg,2.2,M['grass'],race,side*5.2,-.006,False)
    road('Barcelona / pit lane',[(-221,-44),(-209,-55),(-163,-55),(-147,-44)],4,race)
    # Pits, tool scenes, tyre stacks and low stands.
    for i in range(5):
        x=-206+i*10
        cube(f'Pit {i+1} back',(x,-65,1.8),(8,.3,3.6),'cream',race,.1);cube(f'Pit {i+1} canopy',(x,-62,3.7),(8.8,6.8,.25),'mint',race,.12)
        for dx in [-4,4]:cube('Pit post',(x+dx,-59,1.8),(.22,.22,3.6),'metal',race)
        cube('Tool chest',(x+2,-64,.6),(1.4,.65,1.2),'red',race,.07)
        text('Pit bay number',f'0{i+1}',(x,-64.82,2.5),.75,'navy',race,(math.pi/2,0,0))
        for k in range(3):cylinder('Paddock tyres',(x-2,-64,.17+k*.28),.44,.26,'black',race,12)
        cone(f'Paddock cone {i}',(x,-58,0),race)
    for row in range(4):
        cube('Grandstand step',(-190,-30+row*.8,.25+row*.25),(29,.8,.5+row*.5),'cream',race)
        for j in range(13):cube('Grandstand seat',(-202+j*2,-30+row*.8,.58+row*.5),(1.1,.55,.12),'red' if j%3 else 'mint',race,.05)
    for x in [-188,-172]:beam('Start gantry support',(x,-49,0),(x,-49,5),.17,'metal',race)
    beam('Start gantry',(-188,-49,5),(-172,-49,5),.22,'metal',race)
    for j in range(5):uv_sphere('Start light',(-182+j*.65,-49.24,4.75),(.16,.12,.16),'red',race)
    for row in range(2):
        for i in range(14):cube('Start checker',(-180+row*.45,-47.4+i*.48,.05),(.45,.48,.025),'cream' if (row+i)%2 else 'black',race)
    sign('Circuit entrance','NEWPORT / MOTOR CLUB',(-116,-15,0),race)
    # Ice: an irregular shore, snow edge, open road entrance, training lanes.
    flat_patch('Snow shore',(26,132),35,24,ice,'snow',.026)
    frozen=flat_patch('IceLake_Surface',(26,132),29,19,ice,'ice',.045,80);ground(frozen,'ice',.025);frozen['water_ice']=True;frozen['category']='Ice Area';frozen['grip_multiplier']=.035;frozen['brake_multiplier']=.07
    # Ice etchings below the topmost collision layer, with subtle white lines.
    for i in range(5):
        x=6+i*9;c=bpy.data.curves.new('Ice crack','CURVE');c.dimensions='3D';c.bevel_depth=.012;s=c.splines.new('POLY');s.points.add(3)
        for p,co in zip(s.points,[(x,139,.05),(x+2,137,.05),(x+1,134,.05),(x+4,130,.05)]):p.co=(*co,1)
        o=bpy.data.objects.new('Faint ice seam',c);ice.objects.link(o);c.materials.append(M['snow'])
    penguins=[]
    for i,(x,y,angle) in enumerate([(8,128,.5),(17,140,-.4),(37,142,1.2),(44,131,-1),(33,120,2),(18,124,.3),(4,136,.8)]):penguins.append(penguin(f'PlasticPenguin_{i+1:02}',(x,y,.08),ice,.9+(i%3)*.08,angle))
    fallen=penguin('PlasticPenguin_napping',(40,137,.08),ice,.95,.5);fallen.rotation_euler.x=1.45;fallen.location.z=.46
    for i in range(8):cone(f'Ice slalom {i+1:02}',(12+i*3.3,130+(-1 if i%2 else 1)*3,.06),ice)
    cone('Ice cone fallen',(44,121,.06),ice,True);cone('Ice cone by gate',(23,113,.05),ice)
    for x,y in [(-6,125),(6,154),(37,155),(58,130)]:bench('Winter bench',(x,y,.03),ice,math.pi if y<140 else 0);lamp('Winter lantern',(x+2,y,.02),ice)
    sign('Winter welcome','LOW GRIP / HIGH SPIRITS',(16,112,0),ice)
    hut=cube('Skate rental cabin',(-6,144,1.6),(7,5,3.2),'wood',ice,.1);cube('Snow roof',(-6,144,3.3),(7.8,5.8,.32),'snow',ice,.15);cube('Skate rental window',(-6,141.45,1.8),(4,.08,1.2),'navy',ice,.03);text('Skate rental sign','SKATE CLUB',(-6,141.35,2.75),.42,'cream',ice,(math.pi/2,0,0))
    for x,y in [(-10,133),(-7,153),(8,157),(46,151),(61,136),(57,116)]:
        tree=pine('Winter pine',(x,y,0),veg,1.8);cylinder('Snow crown',(x,y,4.7),.75,1.2,'snow',veg,7,r2=0)
    template(penguins[0],'Plastic penguin','Ice Area');template(next(o for o in ice.objects if o.name.startswith('Ice slalom')),'Training cone','Props')
    # Ferris plaza with paving copied from Portfolio, and picnic gardens.
    paving=flat_patch('Wheel tiled plaza',(131,43),27,25,plaza,'cream',.025,64)
    mat=bpy.data.materials.get('AW Plaza tiles') or material('AW Plaza tiles',(.6,.48,.31,1));mat.use_nodes=True;n=mat.node_tree.nodes;tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(root/'textures/source/textures/slabs.png'),check_existing=True);tex.extension='REPEAT';mapping=n.new('ShaderNodeTexCoord');mat.node_tree.links.new(mapping.outputs['UV'],tex.inputs['Vector']);mat.node_tree.links.new(tex.outputs['Color'],n.get('Principled BSDF').inputs['Base Color']);paving.data.materials.clear();paving.data.materials.append(mat);uv=paving.data.uv_layers.new()
    for li,lp in enumerate(paving.data.loops):p=paving.data.vertices[lp.vertex_index].co;uv.data[li].uv=(p.x/3,p.y/3)
    ground(paving,'paving',.8);ferris(root,plaza,cols['ANIMATED_OBJECTS'])
    for x,y in [(111,30),(145,30),(152,47),(113,56),(139,63)]:bench('Plaza bench',(x,y,.06),plaza);lamp('Plaza lantern',(x+2,y,.04),plaza)
    sign('Wheel entrance','THE NEWPORT EYE',(120,22,0),plaza)
    cube('Ticket kiosk',(110,42,1.3),(4,3,2.6),'mint',plaza,.12);cube('Ticket kiosk roof',(110,42,2.8),(4.8,3.8,.25),'red',plaza,.08);cube('Ticket window',(110,40.45,1.5),(2.4,.1,.9),'navy',plaza);text('Ticket sign','ONE MORE TURN',(110,40.3,2.35),.24,'cream',plaza,(math.pi/2,0,0))
    for i in range(10):
        a=math.pi*.15+i*math.pi*.07;x=130+14*math.cos(a);y=45+14*math.sin(a);cylinder('Queue bollard',(x,y,.52),.06,1.04,'metal',plaza,8)
    # Southern vehicle workshop, loop and small programming easter eggs.
    loop_obj=loop(loopcol)
    sign('Loop safety sign','COMMIT TO THE LOOP',(-57,-146,0),loopcol,'red')
    cube('Workshop apron',(-51,-124,.01),(17,9,.03),'cream',loopcol)
    cube('Workshop back',(-52,-120,1.5),(14,.3,3),'mint',loopcol);cube('Workshop canopy',(-52,-123,3.2),(15,7,.25),'cream',loopcol)
    for x in [-58,-45]:beam('Workshop support',(x,-126,0),(x,-126,3.2),.09,'metal',loopcol)
    for i in range(5):cone('Workshop cone',(-62+i*2,-126,0),loopcol,i==3)
    bot=robot('Little debugging robot',(-46,-123,0),props);template(bot,'Debugging robot','Characters')
    table=cube('Coding workbench',(-52,-122,.85),(3,1.3,.15),'wood',loopcol);cube('Laptop keyboard',(-52,-122,1),(1.0,.65,.06),'navy',loopcol);screen=cube('Laptop screen',(-52,-121.68,1.38),(1.0,.055,.72),'mint',loopcol);screen.rotation_euler.x=-.12
    text('Terminal easter egg','hello, world_',(-52,-121.72,1.4),.09,'cream',loopcol,(math.pi/2,0,0),.001)
    # Purposeful garden stopping point: picnic, tiny London phone box, little lookout.
    park=cols['PARK'];flat_patch('Garden lawn',(-78,114),31,9,park,'grass',.005)
    for x,y in [(-91,116),(-74,117),(-55,112)]:
        cube('Picnic table',(x,y,.9),(2.5,1.2,.14),'wood',park,.04)
        for dy in [-.9,.9]:bench('Picnic bench',(x,y+dy,0),park,math.pi if dy<0 else 0)
    cube('London call box',(-105,117,1.2),(1.4,1.4,2.4),'red',park,.08)
    for z in [.9,1.6]:cube('Phone box glazing',(-105,116.28,z),(1.05,.03,.56),'navy',park)
    text('Phone box label','LONDON',(-105,116.24,2.14),.16,'cream',park,(math.pi/2,0,0))
    sign('Garden route sign','LONDON  /  BARCELONA',(-113,107,0),park)
    robot('Robot at the picnic',(-73,116,0),park)
    # Linked vegetation in deliberate clusters, avoiding roads and activity envelopes.
    tree=sources.get('Portfolio tree')
    if tree:
        rng=random.Random(69);accepted=[];pathpoints=[p for r in ROUTES for p in sample(r,8)]
        areas=[(-176,-3,77,67,32),(-82,101,66,23,28),(25,122,43,34,17),(127,43,37,32,15),(-23,-134,58,23,18)]
        for cx,cy,rx,ry,count in areas:
            k=0
            for attempt in range(count*70):
                if k>=count:break
                a=rng.random()*math.tau;d=math.sqrt(rng.uniform(.58,1));p=Vector((cx+rx*math.cos(a)*d,cy+ry*math.sin(a)*d,0))
                if any((p-q).length<7 for q in pathpoints) or any((p-q).length<4 for q in accepted):continue
                if 0<p.x<55 and 111<p.y<155 or 100<p.x<153 and 19<p.y<66 or -223<p.x<-152 and -70<p.y<-50:continue
                linked(tree,'Portfolio grove tree',p,veg,rng.uniform(.6,1.0),rng.random()*math.tau);accepted.append(p);k+=1
    # Asset library includes handcrafted and copied assets; all add into this project.
    for obj,label,category in [(next(o for o in plaza.objects if o.name.startswith('Plaza bench')),'Wooden bench','Street furniture'),(next(o for o in plaza.objects if o.name.startswith('Plaza lantern')),'Garden lantern','Street furniture')]:template(obj,label,category)
    rock=ico('Garden boulder',(-59,117,.4),(1.2,.8,.6),'cream',park,2);template(rock,'Soft boulder','Rocks')
    bush=ico('Garden shrub',(-88,119,.5),(1.4,1,.8),'grass',park,2);template(bush,'Shrub','Plants')
    pine_obj=next(o for o in veg.objects if o.name.startswith('Winter pine'));template(pine_obj,'Winter pine','Trees')
    (root/'exports/navigation.json').write_text(json.dumps({'spawn':[44,-48,1.2],'destinations':{'Home':[44,-48,1.2],'Ice':[24,120,1.2],'Circuit':[-197,-44,1.2],'Wheel':[121,30,1.2],'Loop':[-62,-141,1.2]},'loop':{'points':[list(p) for p in json.loads(loop_obj['path_points'])],'width':5.8,'assist':True},'track':[list(p) for p in centerline]},indent=2))
    return ROUTES
