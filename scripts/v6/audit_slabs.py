import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
BASE=Path('/Users/alejandro/Projects/Portfolio');OUT=Path('/Users/alejandro/Projects/HelloWorld/reports/v6')
p=BASE/'folio-2025.blend';before=hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
m=bpy.data.materials['terrain']
def val(s):
 try:
  v=s.default_value
  if hasattr(v,'__len__') and not isinstance(v,str):return list(v)
  if isinstance(v,(str,float,int,bool)) or v is None:return v
  return str(v)
 except:return None
nodes=[]
for n in m.node_tree.nodes:
 nodes.append(dict(name=n.name,type=n.bl_idname,operation=getattr(n,'operation',None),blend_type=getattr(n,'blend_type',None),data_type=getattr(n,'data_type',None),inputs=[dict(name=s.name,value=val(s),linked=s.is_linked) for s in n.inputs],outputs=[dict(name=s.name,value=val(s)) for s in n.outputs],image=n.image.name if getattr(n,'image',None) else None,interpolation=getattr(n,'interpolation',None),extension=getattr(n,'extension',None),projection=getattr(n,'projection',None)))
links=[dict(source=[l.from_node.name,l.from_socket.name],target=[l.to_node.name,l.to_socket.name]) for l in m.node_tree.links]
terrain=bpy.data.objects['terrain'];dims=list(terrain.dimensions);uv=terrain.data.uv_layers.active
uv_samples=[dict(world=list(terrain.matrix_world@terrain.data.vertices[terrain.data.loops[i].vertex_index].co),uv=list(uv.data[i].uv)) for i in [0,1,2,3,4,5,len(uv.data)//2,len(uv.data)-1]]
slabs=bpy.data.images.get('slabs.png');report=dict(source=str(p),sha256=before,sourceUnchanged=before==hashlib.sha256(p.read_bytes()).hexdigest(),material=m.name,nodes=nodes,links=links,terrain=dict(matrix=[list(row) for row in terrain.matrix_world],dimensions=dims,uvSamples=uv_samples),slabs=dict(name=slabs.name,filepath=slabs.filepath,colorspace=slabs.colorspace_settings.name,alpha_mode=slabs.alpha_mode))
(OUT/'slabs-node-audit.json').write_text(json.dumps(report,indent=2));print('SLABS_AUDIT',json.dumps({k:report[k] for k in ['sourceUnchanged','sha256','material']}))
