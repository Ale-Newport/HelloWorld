import bpy,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(root/'assets/imported/ferris_wheel/source/Wheel model.fbx'))
a=[]
for o in bpy.context.scene.objects:
 pts=[o.matrix_world@Vector(p) for p in o.bound_box]
 a.append(dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,location=list(o.matrix_world.translation),rotation=list(o.rotation_euler),scale=list(o.scale),dimensions=list(o.dimensions),bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],vertices=len(o.data.vertices) if o.type=='MESH' else 0,materials=[m.name for m in o.data.materials if m] if o.type=='MESH' else []))
(root/'reports/ferris-audit.json').write_text(json.dumps(a,indent=2))
print(json.dumps(a))
