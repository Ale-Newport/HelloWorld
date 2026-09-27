"""Polygonal road union/clipping: shared junction boundaries, no stacked asphalt."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts/vendor'))
from shapely.geometry import LineString,Point,Polygon
from shapely import constrained_delaunay_triangles
from shapely.affinity import scale,translate
from layout import plan
p=plan();surfaces={};issues=[];polys=[]
for i,r in enumerate(p['roads']):
 line=LineString([v[:2] for v in r['samples']]);poly=line.buffer(r['width']/2,cap_style='flat',join_style='round')
 if i in [2,3]:poly=poly.difference(polys[0])
 polys.append(poly);tri=constrained_delaunay_triangles(poly);verts=[];faces=[]
 for t in tri.geoms:
  coords=list(t.exterior.coords)[:3]
  if (coords[1][0]-coords[0][0])*(coords[2][1]-coords[0][1])-(coords[1][1]-coords[0][1])*(coords[2][0]-coords[0][0])<0:coords.reverse()
  idx=len(verts);verts.extend(coords);faces.append([idx,idx+1,idx+2])
 surfaces[r['name']]={'vertices':verts,'faces':faces,'area':poly.area}
for i,a in enumerate(polys):
 for j,b in enumerate(polys[i+1:],i+1):
  area=a.intersection(b).area
  if area>.01:issues.append({'type':'ROAD_ROAD','a':p['roads'][i]['name'],'b':p['roads'][j]['name'],'area':area})
for z in p['zones']:
 if z['name'] in ['Loop','Race']:continue
 footprint=translate(scale(Point(0,0).buffer(1),z['rx'],z['ry']),z['x'],z['y'])
 for i,poly in enumerate(polys):
  area=poly.buffer(1.2).intersection(footprint).area
  if area>.1:issues.append({'type':'ROAD_ZONE_CLEARANCE','zone':z['name'],'road':p['roads'][i]['name'],'area':round(area,3)})
(ROOT/'exports/road-surfaces.json').write_text(json.dumps(surfaces,separators=(',',':')))
report={'method':'Shapely polygon buffers, junction difference and constrained triangulation','safety_margin':1.2,'issues':issues,'road_areas':{r['name']:poly.area for r,poly in zip(p['roads'],polys)}}
(ROOT/'reports/v2-road-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
# Measured exported building / attraction bounds, not just planned circles.
bounds_file=ROOT/'reports/v2-scene-bounds.json'
if bounds_file.exists() and '--plan-only' not in sys.argv:
 measured=[]
 for o in json.loads(bounds_file.read_text()):
  important=o['source'] or any(s in o['name'] for s in ['clubhouse','cafe','studio','Post office','town hall','Tech pavilion','Laptop base','Camera body','Trophy pedestal','FerrisWheel_StaticSupport','Giant bowling','Giant cookie'])
  if not important:continue
  lo,hi=o['bounds'];foot=Polygon([(lo[0],-lo[2]),(hi[0],-lo[2]),(hi[0],-hi[2]),(lo[0],-hi[2])])
  for i,poly in enumerate(polys):
   area=poly.buffer(1.2).intersection(foot).area
   if area>.01:measured.append({'type':'ROAD_BUILDING','name':o['name'],'road':p['roads'][i]['name'],'overlap_m2':round(area,3)})
 report['measured_building_checks']=len([o for o in json.loads(bounds_file.read_text()) if o['source'] or o.get('category')=='Buildings']);report['issues']+=measured
 (ROOT/'reports/v2-road-validation.json').write_text(json.dumps(report,indent=2));print('Measured building conflicts:',measured)
tourfile=ROOT/'reports/v2-full-tour.json'
if tourfile.exists() and '--plan-only' not in sys.argv:
 from shapely.ops import unary_union
 driveable=unary_union(polys);outside=[]
 for point in json.loads(tourfile.read_text())['path']:
  x,up,z=point;pt=Point(x,-z)
  if not driveable.buffer(.15).covers(pt):outside.append({'x':x,'y':-z,'distance_to_asphalt':round(driveable.distance(pt),3)})
 report['full_tour_samples_off_asphalt']=outside
 (ROOT/'reports/v2-road-validation.json').write_text(json.dumps(report,indent=2));print('Tour samples off road:',outside)
if bounds_file.exists() and '--plan-only' not in sys.argv:
 from layout import height
 names=['About house','Cookie cafe building','Bowling clubhouse building','Career studio building','Contact post office','Studio camera','Studio laptop','Achievement trophy','bowling','cookie','projects','achievements','social','career','lab','timeMachine','toilet']
 placement=[]
 for o in json.loads(bounds_file.read_text()):
  if o['name'] not in names:continue
  lo,hi=o['bounds'];x=(lo[0]+hi[0])/2;y=-(lo[2]+hi[2])/2;gap=lo[1]-height(x,y)
  if gap<-.15 or gap>.18:placement.append({'type':'UNDER_TERRAIN' if gap<0 else 'FLOATING_OBJECT','name':o['name'],'gap_m':round(gap,3)})
 report['placement_checks']=len(names);report['placement_issues']=placement
 (ROOT/'reports/v2-road-validation.json').write_text(json.dumps(report,indent=2));print('Ground placement conflicts:',placement)

if report['issues'] or report.get('placement_issues') or report.get('full_tour_samples_off_asphalt'):raise SystemExit(1)
