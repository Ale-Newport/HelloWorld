"""Metre-scale plan; the same curves feed Blender, editor and route checks."""
import math,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RING=[[12,-20],[36,-23],[58,-15],[66,3],[64,21],[54,36],[34,43],[13,42],[-10,43],[-32,37],[-49,25],[-56,6],[-53,-12],[-40,-24],[-18,-23]]
# Separate southern installation. Long start straight, sweeping opening right,
# technical infield, hairpin and final pair recall Catalunya without tracing it.
RACE=[[-68,-71],[-43,-71],[-20,-71],[-5,-61],[-5,-43],[-17,-36],[-28,-42],[-35,-53],[-44,-53],[-50,-41],[-64,-37],[-76,-44],[-76,-56]]
ZONES=[dict(name=n,x=x,y=y,rx=rx,ry=ry,color=c) for n,x,y,rx,ry,c in [
('Central Plaza',0,5,14,14,'#e7ce9c'),('About',-3,26,8,7,'#86b8d3'),('Projects',39,8,15,16,'#a38ac5'),('Achievements',81,23,10,11,'#ddb657'),('Ferris Wheel',28,62,14,13,'#de8475'),('Ice Rink',-30,61,19,12,'#b9e7ed'),('Bowling',-76,18,13,14,'#da785d'),('Cookies',-73,-18,10,11,'#cba665'),('Career',22,-43,12,11,'#82bca2'),('Contact',66,-48,11,11,'#d896ac'),('Park',-29,7,13,15,'#91b36e'),('Race',-35,-56,40,22,'#c4ba98'),('Loop',73,62,13,12,'#83a7b5')]]
def height(x,y):
 return 1.3*math.exp(-((x+30)/24)**4-((y-65)/14)**4)+.7*math.exp(-((x-72)/25)**4-((y-65)/18)**4)
def coast(a):return 1+.048*math.sin(3*a+.7)+.025*math.cos(7*a)+.015*math.sin(13*a)
def inside(x,y,margin=0):
 a=math.atan2((y-1)/94,x/112);return math.hypot(x/(112-margin),(y-1)/(94-margin))<coast(a)
def samples(points,closed=True,steps=16):
 p=points;result=[];n=len(p)
 for i in range(n if closed else n-1):
  a,b,c,d=[p[j%n] if closed else p[max(0,min(n-1,j))] for j in [i-1,i,i+1,i+2]]
  for k in range(steps):
   t=k/steps;result.append([.5*((2*b[v])+(-a[v]+c[v])*t+(2*a[v]-5*b[v]+4*c[v]-d[v])*t*t+(-a[v]+3*b[v]-3*c[v]+d[v])*t*t*t) for v in range(2)])
 result.append(result[0] if closed else p[-1]);return result
def distance(p,points):return min(math.hypot(p[0]-a,p[1]-b) for a,b,*_ in points)
def plan():
 roads=[dict(name='Island Boulevard',points=RING,width=7.6,closed=True,type='road'),dict(name='Catalunya Club',points=RACE,width=6.4,closed=True,type='race')]
 # The stunt is a connected optional northern route; its two road junctions
 # are explicit in the road graph, not accidental overlapping ribbons.
 roads.extend([dict(name='Loop approach',points=[[54,36],[56,48],[57,59],[64,62],[73,62]],width=5.8,closed=False,type='road'),dict(name='Loop return',points=[[73,71],[85,70],[98,48],[100,25],[95,5],[82,-1],[66,3]],width=5.8,closed=False,type='road')])
 for r in roads:r['samples']=[[x,y,height(x,y)+.065] for x,y in samples(r['points'],r['closed'])]
 return dict(version=2,units='metres',terrain=dict(rx=112,ry=94),roads=roads,zones=ZONES)
if __name__=='__main__':
 p=plan();(ROOT/'exports/layout.json').write_text(json.dumps(p,indent=2))
 svg=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-115 -100 230 200"><rect x="-115" y="-100" width="230" height="200" fill="#367e91"/>']
 pts=' '.join(f'{112*math.cos(a)*coast(a):.2f},{-1-94*math.sin(a)*coast(a):.2f}' for a in [i*math.tau/180 for i in range(180)])
 svg.append(f'<polygon points="{pts}" fill="#7d995d" stroke="#d9c58e" stroke-width="3"/>')
 for z in ZONES:svg.append(f'<ellipse cx="{z["x"]}" cy="{-z["y"]}" rx="{z["rx"]}" ry="{z["ry"]}" fill="{z["color"]}"/>')
 for r in p['roads']:
  pts=' '.join(f'{x:.2f},{-y:.2f}' for x,y,z in r['samples']);svg.append(f'<polyline points="{pts}" fill="none" stroke="#323c40" stroke-width="{r["width"]}" stroke-linejoin="round"/>')
 for z in ZONES:svg.append(f'<text x="{z["x"]}" y="{-z["y"]}" text-anchor="middle" font-family="sans-serif" font-size="2.5" fill="#142b33">{z["name"]}</text>')
 svg.append('</svg>');(ROOT/'reports/v2-layout-plan.svg').write_text(''.join(svg))
 print('Layout saved')
