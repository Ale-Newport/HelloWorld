from pathlib import Path
import bpy,sys,math,json,random,time
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'editor'),str(ROOT/'scripts'),str(Path(__file__).parent)]
import alejandro_world
from alejandro_world.core import collection,tag,move_to,material,activate
from alejandro_world.physics import configure
from alejandro_world.export import export_world
from worldgen.common import *
from worldgen.props import *
from worldgen.attractions import loop
from layout import *
from alejandro_world.roads import ribbon
start=time.time();bpy.ops.wm.open_mainfile(filepath=str(ROOT/'backups/v1-expanded/world/AlejandroWorld.blend'))
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
scene=bpy.context.scene;scene.frame_set(1)
source_names=['bowling','cookie','projects','achievements','social','career','lab','timeMachine','toilet','FerrisWheel']
roots={n:bpy.data.objects.get(n) for n in source_names};keep=set()
for o in roots.values():
 if o:keep.update([o,*o.children_recursive])
for o in list(scene.objects):
 if o.get('aw_template'):keep.add(o)
for o in keep:
 if o.parent not in keep:
  m=o.matrix_world.copy();o.parent=None;o.matrix_world=m
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
 if not c.all_objects:bpy.data.collections.remove(c)
world=collection('WORLD');cols={n:collection(n,world) for n in ['TERRAIN','ROADS','RACE_TRACK','CENTRAL_PLAZA','ABOUT','PROJECTS','ACHIEVEMENTS','BOWLING','COOKIES','CAREER','CONTACT','PARK','ICE_RINK','ATTRACTIONS','ROAD_LOOP','VEGETATION','PROPS','LIGHTING','ANIMATED_OBJECTS','COLLIDERS']}
setup();M['grass'].diffuse_color=(.29,.43,.12,1);M['grass'].node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.29,.43,.12,1)
M['paving']=material('AW Limestone',(.59,.52,.35,1),.85);M['asphalt']=material('AW Boulevard',(.10,.14,.15,1),.83);M['race']=material('AW Racing tarmac',(.035,.045,.05,1),.88);M['water']=material('AW Lagoon',(.055,.36,.42,1),.24);M['rock']=material('AW Coastal stone',(.37,.39,.31,1),.95)
scene.name='Alejandro World · Compact island';scene.render.fps=24;scene.frame_end=721;scene.unit_settings.system='METRIC';scene.aw.ground_snap=False
layout=plan();roads=layout['roads'];allroad=[p for r in roads for p in r['samples']]
# Reconstruct the coastline as concentric, editable rings, with faceted cliffs.
verts=[(0,1,0)];faces=[];segments=144;rings=34
for j in range(1,rings+1):
 f=j/rings
 for i in range(segments):
  a=i*math.tau/segments;co=coast(a);x=112*math.cos(a)*co*f;y=1+94*math.sin(a)*co*f
  z=height(x,y);lake=math.exp(-((x+31)/9)**6-((y+8)/6)**6);z-=1.25*lake
  if f>.98:z-=.20
  verts.append((x,y,z))
for i in range(segments):faces.append((0,1+i,1+(i+1)%segments))
for j in range(rings-1):
 for i in range(segments):
  a=1+j*segments+i;b=1+j*segments+(i+1)%segments;faces.append((a,a+segments,b+segments,b))
me=bpy.data.meshes.new('Sculptable island surface');me.from_pydata(verts,[],faces);me.materials.append(M['grass']);terrain=bpy.data.objects.new('Main Island · sculptable terrain',me);cols['TERRAIN'].objects.link(terrain);tag(terrain,'Nature',terrain=True,ground_surface=True,collision=True);terrain['surface_type']='terrain';terrain['sculptable']=True
# Grass variation is vertex colour, shared material and no texture dependency.
attr=me.color_attributes.new(name='TerrainTint',type='FLOAT_COLOR',domain='POINT');rng=random.Random(20)
for i,v in enumerate(me.vertices):
 edge=math.hypot(v.co.x/112,(v.co.y-1)/94);c=(.48,.52,.22,1) if edge>.91 else (.34+rng.random()*.045,.46+rng.random()*.035,.15,1);attr.data[i].color=c
mat=M['grass'].copy();mat.name='AW Living terrain';terrain.data.materials[0]=mat;nodes=mat.node_tree.nodes;vc=nodes.new('ShaderNodeVertexColor');vc.layer_name='TerrainTint';mat.node_tree.links.new(vc.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])
# Coastal shelf and cliff wall form a single continuous silhouette.
cliffv=[];clifff=[]
for layer in range(3):
 for i in range(segments):
  a=i*math.tau/segments;co=coast(a);f=[1,1.025,1.018][layer];x=112*math.cos(a)*co*f;y=1+94*math.sin(a)*co*f;cliffv.append((x,y,[height(x,y)-.18,-1.8,-4.2][layer]))
for j in range(2):
 for i in range(segments):clifff.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
me=bpy.data.meshes.new('Continuous cliffs');me.from_pydata(cliffv,[],clifff);me.materials.append(M['sand']);me.materials.append(M['rock']);o=bpy.data.objects.new('Coast · sandstone and rock',me);cols['TERRAIN'].objects.link(o)
for p in me.polygons:p.material_index=p.index>=segments or p.index%7==0
water=cube('Surrounding sea',(0,0,-3.2),(1600,1600,.15),'water',cols['TERRAIN']);water['collision']=False;water['surface_type']='water';water['unselectable']=True
flat_patch('Garden lagoon',(-31,-8),9,6,cols['PARK'],'water',z=-.32)
# Roads are authored before placing anything else. Curves and dimensions live in extras.
for r in roads:
 ps=[Vector(p) for p in r['samples']];mat=M['race' if r['type']=='race' else 'asphalt'];shape=json.loads((ROOT/'exports/road-surfaces.json').read_text())[r['name']];me=bpy.data.meshes.new(r['name']);me.from_pydata([(x,y,height(x,y)+.065) for x,y in shape['vertices']],[],shape['faces']);me.materials.append(mat);o=bpy.data.objects.new(r['name'],me);cols['RACE_TRACK' if r['type']=='race' else 'ROADS'].objects.link(o);tag(o,'Roads');ground(o,'road');o['road']=True;o['road_points']=json.dumps([[x,height(x,y)+.065,-y] for x,y in r['points']]);o['road_width']=r['width'];o['road_closed']=r['closed'];o['safety_margin']=1.2;o['road_network']=r['type'];o['category']='Roads';o['editable_root']=True
 for side in [-1,1]:
  if r['type']=='race':
   for k in range(0,len(ps)-1,4):ribbon('Race kerb',ps[k:k+5],.48,M['red' if k//4%2 else 'cream'],cols['RACE_TRACK'],side*(r['width']/2+.24),.008,False)
  else:
   edgeps=ps
   if r['name']=='Loop approach':edgeps=[p for p in ps if distance(p,roads[0]['samples'])>4.2]
   if r['name']=='Loop return':edgeps=[p for p in ps if distance(p,roads[0]['samples'])>4.2]
   ribbon(r['name']+' edge',edgeps,.10,M['cream'],cols['ROADS'],side*(r['width']/2-.28),.012,False)
 # Dashed line; keep it away from the designated branch junctions.
 if r['name']=='Island Boulevard':
  for k in range(0,len(ps)-2,5):
   if min((ps[k]-Vector(p)).length for p in [roads[2]['samples'][0],roads[3]['samples'][-1]])>8:ribbon('Boulevard centre dash',ps[k:k+2],.10,M['cream'],cols['ROADS'],0,.014,False)
# Source hierarchies are placed using measured visible bounds, preserving their children.
def reuse(name,target,size,col):
 o=roots.get(name)
 if not o:return
 members=[o,*o.children_recursive]
 for m in list(members):
  if m.get('w2Role')=='collider' or m.hide_render:
   bpy.data.objects.remove(m,do_unlink=True)
 members=[o,*o.children_recursive];bpy.context.view_layer.update();ps=[m.matrix_world@Vector(p) for m in members if m.type=='MESH' for p in m.bound_box]
 if not ps:return o
 lo=Vector([min(p[i] for p in ps) for i in range(3)]);hi=Vector([max(p[i] for p in ps) for i in range(3)]);s=min(size[0]/max(.01,hi.x-lo.x),size[1]/max(.01,hi.y-lo.y),1.4);pivot=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z));o.matrix_world=Matrix.Translation(Vector(target))@Matrix.Scale(s,4)@Matrix.Translation(-pivot)@o.matrix_world
 for m in members:
  move_to(m,col);m.hide_render=False;m.hide_set(False);m['aw_template']=False;m['collision']=False;m['physics_mode']='STATIC'
  if m.rigid_body:activate(m);bpy.ops.rigidbody.object_remove()
 o['editable_root']=True;o['category']='Buildings';o['source_area']=name
 return o
# District plazas, differentiated by material rather than disconnected platforms.
for z in ZONES:
 if z['name'] in ['Race','Loop','Park','Ice Rink']:continue
 c=cols.get(z['name'].upper().replace(' ','_'),cols['ATTRACTIONS']);flat_patch(z['name']+' plaza',(z['x'],z['y']),z['rx'],z['ry'],c,'paving',height(z['x'],z['y'])+.02)
reuse('bowling',(-76,18,.03),(23,20),cols['BOWLING']);reuse('cookie',(-73,-18,.03),(15,15),cols['COOKIES']);reuse('projects',(37,6,.03),(14,12),cols['PROJECTS']);reuse('lab',(46,18,.03),(9,8),cols['PROJECTS']);reuse('achievements',(81,23,.03),(14,14),cols['ACHIEVEMENTS']);reuse('career',(22,-43,.03),(12,15),cols['CAREER']);reuse('social',(66,-48,.03),(16,15),cols['CONTACT']);reuse('timeMachine',(-28,12,.03),(5,5),cols['PARK']);reuse('toilet',(-88,-3,.03),(4,4),cols['PROPS'])
# Simple pedestrian links form a different, narrow limestone network.
paths=[[(0,-18),(0,5)],[(0,5),(-3,26)],[(12,5),(25,8)], [(-14,5),(-30,5)], [(-42,30),(-63,24)], [(-54,-12),(-65,-17)],[(26,44),(28,52)], [(-26,38),(-30,48)],[(65,20),(73,23)],[(26,-24),(22,-34)],[(57,-18),(63,-39)]]
for i,path in enumerate(paths):ribbon('Walkway %02d'%i,[Vector((x,y,height(x,y)+.035)) for x,y in samples(path,False,12)],2.2,M['paving'],cols['PROPS'],0,0,False)
# Central water fountain, concentric terraces, prominent identity and town hall.
p=cols['CENTRAL_PLAZA'];cylinder('Plaza outer step',(0,5,.12),12,.24,'cream',p,64);cylinder('Plaza paving',(0,5,.26),10.8,.12,'paving',p,64);cylinder('Fountain surround',(0,5,.49),4.3,.52,'cream',p,48);cylinder('Fountain water',(0,5,.77),3.8,.04,'water',p,48);cylinder('Fountain plinth',(0,5,1.2),.95,.95,'cream',p,16);cylinder('Fountain bowl',(0,5,1.75),1.85,.3,'cream',p,32,r2=2.05);cylinder('Upper water',(0,5,1.93),1.9,.02,'water',p,32);ico('Fountain droplet',(0,5,2.75),(.28,.28,.9),'ice',p,2)
for a in [i*math.tau/8 for i in range(8)]:
 x,y=8.7*math.cos(a),5+8.7*math.sin(a);bench('Plaza bench',(x,y,.34),p,a-math.pi/2)
for x in [-6,6]:cube('Landmark pillar',(x,15,.8),(.6,.8,1.6),'cream',p,.06)
board=cube('Alejandro Newport landmark',(0,15,3.2),(15,.7,4.2),'navy',p,.25);text('ALEJANDRO NEWPORT','ALEJANDRO\nNEWPORT',(0,14.6,3.25),1.24,'cream',p,(math.pi/2,0,0))
# About house and distinctive letters.
b=cols['ABOUT'];cube('About · town hall',(-3,27,3.2),(9,6,6.4),'cream',b,.18);cube('About roof',(-3,27,6.55),(10,7,.4),'navy',b,.12)
for x in [-5.8,-3,-.2]:
 cube('About glass',(x,23.96,3.8),(1.5,.09,2.5),'ice',b,.08)
cube('About entrance',(-3,23.85,1.35),(1.8,.25,2.7),'navy',b,.06);text('About monogram','A',(-3,23.7,7.5),3,'cream',b,(math.pi/2,0,0));sign('About sign','ABOUT ME',(-10,23,0),b,'mint')
# Bowling and cookie landmarks complete the reused environments.
b=cols['BOWLING'];uv_sphere('Giant bowling ball',(-81,23,5),(3.4,3.4,3.4),'red',b)
for dx,dy in [(-.7,-2.9),(.5,-3.05),(-.2,-2.8)]:uv_sphere('Ball finger hole',(-81+dx,23+dy,6),(.30,.16,.32),'black',b)
for x in [-72,-69]:
 uv_sphere('Giant pin body',(x,25,3),(1.1,1.1,2.6),'cream',b);uv_sphere('Giant pin neck',(x,25,5.6),(.55,.55,1),'cream',b);cylinder('Pin stripe',(x,25,5.2),.58,.35,'red',b)
sign('Bowling sign','BOWLING',(-68,10,0),b,'red')
b=cols['COOKIES'];disc=cylinder('Giant cookie',(-77,-17,5),3.8,.75,'sand',b,32);disc.rotation_euler.x=math.pi/2
for i in range(14):
 a=i*2.4;r=2.9*math.sqrt((i+.5)/14);ico('Chocolate chip',(-77+r*math.cos(a),-17.43,5+r*math.sin(a)),(.32,.18,.3),'wood',b)
sign('Cookie cafe sign','COOKIE CAFE',(-68,-21,0),b,'orange')
# Tech campus: camera, laptop, displays, servers, robot work area.
b=cols['PROJECTS'];cube('Tech pavilion',(40,16,2.6),(9,6,5.2),'navy',b,.3);cube('Tech roof',(40,16,5.3),(10,7,.25),'mint',b,.1)
for i in range(3):
 cube('Server rack',(44+i*1.5,0,1.6),(1.1,1.2,3.2),'navy',b,.12)
 for k in range(6):cube('Server status',(44+i*1.5,-.62,.5+k*.43),(.7,.03,.06),'mint',b)
cube('Laptop pedestal',(32,12,.26),(4.8,2.8,.52),'cream',b,.08);cube('Laptop base',(32,12,.7),(5.7,3.8,.35),'metal',b,.15);cube('Laptop display',(32,13.7,2.6),(5.7,.26,3.7),'cream',b,.12);cube('Laptop screen',(32,13.52,2.7),(5.15,.06,3.1),'navy',b);text('Laptop code','< / >',(32,13.46,2.65),1,'mint',b,(math.pi/2,0,0))
cube('Camera pedestal',(47,8,.15),(3.5,2.3,.3),'cream',b,.06);cube('Camera body',(47,8,2),(4,2.5,3.4),'navy',b,.3);lens=cylinder('Camera lens',(47,6.5,2),1.25,1.3,'metal',b,24);lens.rotation_euler.x=math.pi/2;lens=cylinder('Camera glass',(47,5.78,2),.96,.06,'ice',b,24);lens.rotation_euler.x=math.pi/2
for x,y in [(31,0),(40,-1),(49,15)]:robot('Lab assistant',(x,y,0),b)
sign('Projects sign','PROJECTS / LAB',(33,-4,0),b,'mint')
# Trophy museum recognisable at overview scale.
b=cols['ACHIEVEMENTS'];cube('Trophy pedestal',(81,17,1),(3,3,2),'cream',b,.12);cylinder('Trophy stem',(81,17,2.7),.35,1.5,'yellow',b);cylinder('Trophy cup',(81,17,4),1.65,1.4,'yellow',b,16,r2=2.05)
for x in [78.8,83.2]:
 bpy.ops.mesh.primitive_torus_add(major_radius=.9,minor_radius=.16,major_segments=16,minor_segments=6,location=(x,17,4),rotation=(math.pi/2,0,0));finish(bpy.context.object,'Trophy handle',b,'yellow')
sign('Achievements sign','ACHIEVEMENTS',(76,13,0),b,'orange');sign('Career sign','CAREER',(18,-34,0),cols['CAREER']);sign('Contact sign','SAY HELLO',(63,-39,0),cols['CONTACT'],'red')
# Snow basin is part of this island, with a clear driving entrance from boulevard.
b=cols['ICE_RINK'];iz=height(-30,61);flat_patch('Snow shelf',(-30,61),21,14,b,'snow',iz+.02);ice=flat_patch('Ice rink surface',(-30,61),17.5,10.5,b,'ice',iz+.07);ground(ice,'ice',.04)
ribbon('Ice entrance',[Vector((-29,45,.09)),Vector((-30,49,iz+.02)),Vector((-30,54,iz+.07))],6,M['snow'],b,0,0,False)
for i in range(8):penguin('Learner penguin %02d'%i,(-41+(i%4)*7,57+(i//4)*7,iz+.1),b,1.15,i*.7)
for i in range(9):cone('Ice cone %02d'%i,(-43+i*3.2,60+.7*math.sin(i),iz+.1),b,False)
for i in range(22):
 a=i*math.tau/22;x=-30+20*math.cos(a);y=61+13*math.sin(a)
 if -1.9<a<-1.1:continue
 ico('Snow bank',(x,y,iz+.3),(1.8,1.2,.8),'snow',b,1)
sign('Ice sign','ICE RINK',(-43,46,height(-43,46)),b,'navy')
# Reuse the actual imported wheel and its counter-rotating cabins.
f=roots['FerrisWheel'];f.location=(28,62,height(28,62));f['editable_root']=True
for o in [f,*f.children_recursive]:move_to(o,cols['ATTRACTIONS']);o['collision']=False
for i in range(3):
 x=16+i*8;cube('Fairground kiosk',(x,51,1.5),(4,3,3),'cream',cols['ATTRACTIONS'],.12);cube('Kiosk canopy',(x,50.5,3.2),(4.8,4,.3),['red','mint','yellow'][i],cols['ATTRACTIONS'],.1)
sign('Wheel sign','NEWPORT EYE',(37,53,0),cols['ATTRACTIONS'],'red')
# The existing tested helical loop is relocated onto the northern road branch.
b=cols['ROAD_LOOP'];before=set(bpy.data.objects);lp=loop(b);dz=height(73,62)-.055
for o in set(bpy.data.objects)-before:o.location+=Vector((98,203,dz))
lpoints=[[x+98,y+203,z+dz] for x,y,z in json.loads(lp['path_points'])];lp['path_points']=json.dumps(lpoints);lp['category']='Roads';lp['editable_root']=True
# Track paddock outside the racing surface; kerbs remain visual and flush.
b=cols['RACE_TRACK']
for i in range(4):
 x=-50+i*9;cube('Pit garage',(x,-81,1.8),(7,4,3.6),'cream',b,.12);cube('Pit canopy',(x,-80,3.8),(8,6,.3),'mint',b,.1);cube('Pit opening',(x,-78.95,1.6),(5,.1,2.7),'navy',b);text('Pit bay',str(i+1),(x,-78.83,2.4),.9,'cream',b,(math.pi/2,0,0));cone('Pit cone',(x,-76,0),b)
for row in range(3):
 cube('Grandstand',(-28,-61+row*.9,.3+row*.4),(16,.9,.6+row*.8),'cream',b)
 for k in range(9):cube('Stand seat',(-35+k*1.7,-61+row*.9,.65+row*.8),(1,.6,.16),'red',b)
for i in range(8):
 cube('Grid marking',(-37+i*2.4,-71.6,.092),(.1,1.3,.018),'cream',b)['collision']=False
sign('Race entrance','NEWPORT MOTOR CLUB',(-21,-31,0),b,'red')
# Gate access is gravel and does not introduce another crossing tarmac ribbon.
ribbon('Paddock access',[Vector((-18,-23,.02)),Vector((-13,-29,.02)),Vector((-10,-35,.02))],5,M['sand'],b,0,0,False)
# Landmark buildings reinforce the original playable source scenes.
b=cols['BOWLING'];cube('Bowling clubhouse',(-78,17,1.8),(13,8,3.6),'cream',b,.18);cube('Bowling roof',(-78,17,3.8),(14,9,.35),'red',b,.1)
for x in [-82,-78,-74]:cube('Bowling shopfront',(x,12.95,1.7),(3.2,.08,2.4),'ice',b,.08)
# Source bowling lanes are retained in front of the house.
b=cols['COOKIES'];cube('Cookie cafe',(-75,-19,1.5),(10,6,3),'cream',b,.16)
for i in range(10):cube('Cafe striped canopy',(-79.5+i,-23,3.1),(1,3,.22),'red' if i%2 else 'cream',b)
for x in [-78,-74,-70]:
 cylinder('Cafe table',(x,-26,.8),.85,.12,'wood',b,12);cylinder('Table leg',(x,-26,.4),.08,.8,'metal',b)
 for dx in [-1.2,1.2]:cube('Cafe stool',(x+dx,-26,.45),(.5,.5,.9),'mint',b,.05)
b=cols['CAREER'];cube('Career studio',(24,-46,2.3),(9,6,4.6),'cream',b,.18);cube('Career roof',(24,-46,4.75),(10,7,.3),'mint',b,.1)
cube('Career display',(24,-49.1,3),(6,.12,2.2),'navy',b,.07);text('Career lettering','NEXT CHAPTER',(24,-49.2,3),.48,'cream',b,(math.pi/2,0,0))
b=cols['CONTACT'];cube('Post office',(65,-50,2.3),(9,7,4.6),'cream',b,.18);cube('Post office roof',(65,-50,4.8),(10,8,.4),'red',b,.12);cube('Giant letter',(65,-50,6.7),(5,.7,3),'cream',b,.1)
for a,c in [((62.7,-50.4,8),(65,-50.4,6.1)),((65,-50.4,6.1),(67.3,-50.4,8))]:beam('Envelope fold',a,c,.055,'red',b)
# Palm trees mark the civic centre; each frond uses a shared low-poly leaf mesh.
b=cols['CENTRAL_PLAZA']
for x,y in [(-13,-3),(13,-3),(-14,14),(14,14)]:
 cylinder('Palm trunk',(x,y,3.2),.28,6.4,'wood',b,9,r2=.18)
 for i in range(7):
  a=i*math.tau/7;leaf=ico('Palm frond',(x+1.6*math.cos(a),y+1.6*math.sin(a),6.7),(2.4,.48,.20),'grass',b,1);leaf.rotation_euler.z=a;leaf.rotation_euler.y=.18
# Vegetation and props use shared meshes; rejection sampling respects roads and zones.
veg=cols['VEGETATION'];templatepine=pine('Pine master',(0,0,-50),veg);templatepine.hide_render=True;templatepine.hide_set(True);templatepine['aw_template']=True
parts=[cylinder('trunk',(0,0,-49),.28,2,'wood',veg,7)]
for dx,dy,z,r in [(-.7,0,-47.5,1.5),(.7,.2,-47.4,1.5),(0,-.5,-46.7,1.6)]:parts.append(ico('crown',(dx,dy,z),(r,r,r),'grass',veg,2))
tree=join(parts,'Broadleaf master',veg,(0,0,-50));tree.hide_render=True;tree.hide_set(True);tree['aw_template']=True;tree['category']='Trees'
rng=random.Random(753);accepted=[]
for i in range(1600):
 x=rng.uniform(-106,106);y=rng.uniform(-87,89)
 if not inside(x,y,4) or distance((x,y),allroad)<7.1:continue
 if any(((x-z['x'])/(z['rx']+1))**2+((y-z['y'])/(z['ry']+1))**2<1 for z in ZONES if z['name']!='Park'):continue
 if math.hypot((x+31)/12,(y+8)/8)<1 or any(math.hypot(x-a,y-b)<4 for a,b in accepted):continue
 accepted.append((x,y));src=templatepine if y>43 or rng.random()<.18 else tree;o=linked(src,'Pine' if src==templatepine else 'Tree',(x,y,height(x,y)),veg,rng.uniform(.8,1.7),rng.random()*math.tau);o['category']='Trees'
 if len(accepted)>220:break
# Sculptural rocks follow the shoreline, backed by sand and low scrub.
rock=ico('Rock master',(0,0,-50),(1.7,1.1,1.2),'rock',veg,1);rock.hide_render=True;rock['aw_template']=True
for i in range(100):
 a=i*math.tau/100;f=coast(a)*.97;x=112*math.cos(a)*f;y=1+94*math.sin(a)*f
 if distance((x,y),allroad)<6:continue
 o=linked(rock,'Coastal rock',(x,y,-.25),veg,rng.uniform(.6,1.7),a);o['category']='Rocks'
# Local planting clusters, street furniture, small discovery scenes.
for z in ZONES:
 if z['name'] in ['Race','Loop','Ice Rink']:continue
 for i in range(7):
  a=i*math.tau/7;x=z['x']+(z['rx']+1)*math.cos(a);y=z['y']+(z['ry']+1)*math.sin(a)
  if distance((x,y),allroad)<6 or not inside(x,y,5):continue
  linked(tree,'District tree',(x,y,height(x,y)),veg,.9,a)
for i in range(0,len(roads[0]['samples'])-1,13):
 p0=Vector(roads[0]['samples'][i]);p1=Vector(roads[0]['samples'][i+1]);t=(p1-p0).normalized();p0+=Vector((-t.y,t.x,0))*5.5;lamp('Boulevard lamp',p0,cols['PROPS'])
for x,y,a in [(-32,3,0),(-38,13,1.3),(14,31,.2),(10,-8,.7),(58,-44,0)]:bench('Garden bench',(x,y,height(x,y)),cols['PROPS'],a)
# Footbridge across the small interior lagoon, pedestrian only.
for i in range(12):cube('Lagoon bridge plank',(-31,-13+i*.9,.55),(3,.8,.18),'wood',cols['PARK'])
for x in [-32.5,-29.5]:beam('Footbridge handrail',(x,-13,1.4),(x,-3,1.4),.06,'cream',cols['PARK'])
# Lighthouse anchors coast; sailboat gives the sea a scale cue.
b=cols['PROPS'];cylinder('Lighthouse',(-98,-33,3),1.7,7,'cream',b,12,r2=1.2);cylinder('Lighthouse red band',(-98,-33,5.6),1.32,.9,'red',b,12);cylinder('Lighthouse lantern',(-98,-33,7.3),1.05,1.5,'ice',b,10);cylinder('Lighthouse cap',(-98,-33,8.3),1.7,.7,'red',b,12,r2=0)
for x,y in [(27,-87),(70,-71)]:
 cube('Harbour jetty',(x,y,-.8),(3,12,.5),'wood',b);car_model('Parked AN roadster',(x-4,y+11,0),b)
# Group compound assets so selection, thumbnails and duplication operate on whole objects.
def assembly(name,prefixes,col):
 pieces=[o for o in list(col.objects) if any(o.name.startswith(prefix) for prefix in prefixes)]
 if not pieces:return
 root=bpy.data.objects.new(name,None);col.objects.link(root);bpy.context.view_layer.update();ps=[o.matrix_world@Vector(v) for o in pieces if o.type=='MESH' for v in o.bound_box]
 root.location=Vector(((min(p.x for p in ps)+max(p.x for p in ps))/2,(min(p.y for p in ps)+max(p.y for p in ps))/2,min(p.z for p in ps)));bpy.context.view_layer.update()
 for o in pieces:
  world=o.matrix_world.copy();o.parent=root;o.matrix_world=world;o['editable_root']=False
 root['editable_root']=True;root['category']='Buildings';tag(root,'Buildings');return root
assembly('About house',['About · town hall','About roof','About glass','About entrance','About monogram'],cols['ABOUT'])
assembly('Cookie cafe building',['Cookie cafe','Cafe striped canopy'],cols['COOKIES'])
assembly('Bowling clubhouse building',['Bowling clubhouse','Bowling roof','Bowling shopfront'],cols['BOWLING'])
assembly('Career studio building',['Career studio','Career roof','Career display','Career lettering'],cols['CAREER'])
assembly('Contact post office',['Post office','Giant letter','Envelope fold'],cols['CONTACT'])
assembly('Studio camera',['Camera pedestal','Camera body','Camera lens','Camera glass'],cols['PROJECTS'])
assembly('Studio laptop',['Laptop pedestal','Laptop base','Laptop display','Laptop screen','Laptop code'],cols['PROJECTS'])
assembly('Achievement trophy',['Trophy pedestal','Trophy stem','Trophy cup','Trophy handle'],cols['ACHIEVEMENTS'])
# Category and selectable hierarchy metadata, simple colliders for substantial props.
for o in list(scene.objects):
 if o.get('aw_template'):continue
 if o.type=='MESH' and not o.get('ground_surface') and not o.get('road'):
  if o.get('physics_mode')!='DYNAMIC' and not o.get('animated'):
   # Reused display details are visual; native solid buildings keep their mesh collider.
   if o.name.startswith(('Tree','Pine','Coastal rock','District','Race kerb','Boulevard centre','Stand seat','Server status','Grid marking')):o['collision']=False
 if o.type in {'MESH','EMPTY','FONT','CURVE'} and not o.parent:o['editable_root']=True
 if not o.get('aw_id'):o['aw_id']='v2:'+o.name
# Low foliage, flower beds and wild grasses make the street edges feel inhabited.
M['flower']=material('AW Bougainvillea',(.66,.15,.36,1),.85);M['leaf']=material('AW Deep leaves',(.14,.29,.08,1),.9)
flower=ico('Flower cluster master',(0,0,-50),(.5,.4,.42),'flower',veg,1);flower.hide_render=True;flower['aw_template']=True
bush=ico('Bush master',(0,0,-50),(.95,.7,.75),'leaf',veg,1);bush.hide_render=True;bush['aw_template']=True
for i in range(280):
 x=rng.uniform(-100,100);y=rng.uniform(-83,83)
 if not inside(x,y,7) or distance((x,y),allroad)<5.9:continue
 if any(((x-z['x'])/(z['rx']-.5))**2+((y-z['y'])/(z['ry']-.5))**2<1 for z in ZONES):continue
 src=flower if i%3==0 else bush;linked(src,'Flowering shrub' if src==flower else 'Low bush',(x,y,height(x,y)+.35),veg,rng.uniform(.65,1.6),rng.random()*math.tau)
# Lighting and genuinely useful overview saved in Blender.
scene.world=bpy.data.worlds.new('Coastal daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.32,.45,.55,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
light=bpy.data.lights.new('Sun','SUN');light.energy=2.6;light.angle=.15;sun=bpy.data.objects.new('Sun',light);cols['LIGHTING'].objects.link(sun);sun.rotation_euler=(.4,-.45,-.6)
cam=save_camera('WORLD OVERVIEW',(-158,-225,265),(0,4,0),261,cols['LIGHTING']);scene.camera=cam;save_camera('WORLD PLAN',(0,0,350),(0,0,0),245,cols['LIGHTING']);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1800;scene.render.resolution_y=1350;scene.render.resolution_percentage=80;scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
for image in bpy.data.images:
 if image.source=='FILE' and image.has_data:
  try:image.pack()
  except:pass
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_location=Vector((0,0,0));area.spaces.active.region_3d.view_distance=230;area.spaces.active.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
# Native Blender simulation uses the same authored collision surfaces.
for o in list(scene.objects):
 if o.get('collision') and o.type=='MESH' and not o.get('aw_template') and not o.rigid_body:configure(o,'STATIC','MESH',1,o.get('friction',.7))
 if o.type in {'MESH','EMPTY','CURVE','FONT'} and not o.get('aw_template'):
  if not o.parent:o['editable_root']=True
  if not o.get('aw_id'):o['aw_id']='v2:'+o.name
scene['world_builder_version']='2.0.0';scene['portfolio_read_only']=True;scene.frame_set(1)
if scene.rigidbody_world:
 scene.rigidbody_world.enabled=True;scene.rigidbody_world.substeps_per_frame=8;scene.rigidbody_world.solver_iterations=20;scene.rigidbody_world.point_cache.frame_end=721
bpy.ops.object.select_all(action='DESELECT');bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'world/AlejandroWorld.blend'))
nav=dict(spawn=[12,-20,1.25],destinations={z['name']:[z['x'],z['y'],height(z['x'],z['y'])+1.2] for z in ZONES},loop=dict(points=lpoints,width=5.8,assist=True),track=roads[1]['samples'],roads=roads,zones=ZONES)
(ROOT/'exports/navigation.json').write_text(json.dumps(nav,indent=2));(ROOT/'exports/layout.json').write_text(json.dumps(layout,indent=2));export_world()
# Asset catalogue exported independently, same portable GLB data.
report=dict(objects=len(scene.objects),trees=len(accepted),roads=len(roads),bounds=[224,188],seconds=time.time()-start)
(ROOT/'reports/v2-build.json').write_text(json.dumps(report,indent=2));print('V2 BUILT',report,flush=True)
scene.render.filepath=str(ROOT/'reports/v2-overview.png');bpy.ops.render.render(write_still=True)
