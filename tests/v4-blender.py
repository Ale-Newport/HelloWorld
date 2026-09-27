from pathlib import Path
import bpy, json, runpy
ROOT = Path(__file__).resolve().parents[1]
report = runpy.run_path(str(ROOT/'scripts/v4/open_edited.py'))['import_world']()
scene = bpy.context.scene; visual = [o for o in scene.objects if not o.get('aw_physics_proxy')]; proxies = [o for o in scene.objects if o.get('aw_physics_proxy')]
assert scene['world_builder_version'] == '4.0.0'
assert report['visual_parent_links_preserved'] and len(visual) > 1000
assert len(proxies) > 100 and all(o.hide_render and o.rigid_body for o in proxies)
assert report['animation_actions'] >= 20
assert all(i.packed_file or i.source != 'FILE' or not i.users for i in bpy.data.images)
assert all(bpy.data.objects.get(o['visual_owner']) for o in proxies)
assert any(o.get('roadDefinition') for o in visual)
assert not any(o.get('editorOnly') for o in visual)
assert (ROOT/'world/EditedWorld_v4.blend').exists()
# Frame evaluation must preserve every animated hierarchy and keep transforms finite.
from math import isfinite
for frame in [1,91,181]:
 scene.frame_set(frame); bpy.context.view_layer.update()
 assert all(isfinite(v) for o in visual for row in o.matrix_world for v in row)
scene.frame_set(1)
(ROOT/'reports/v4/blender-tests.json').write_text(json.dumps({'passed':True,**report,'evaluated_frames':[1,91,181]},indent=2))
print('PASS v4 native hierarchy, animations, packed resources and collider proxies',flush=True)
