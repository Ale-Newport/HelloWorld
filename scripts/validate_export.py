import bpy,sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'editor'))
import alejandro_world
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
from alejandro_world.validation import validate
from alejandro_world.export import export_world
issues=validate(bpy.context.scene);(ROOT/'reports/world-validation.json').write_text(json.dumps(issues,indent=2));print('VALIDATION', {k:sum(i['level']==k for i in issues) for k in ['ERROR','WARNING','SUGGESTION']},flush=True)
for i in issues:
 if i['level']=='ERROR':print(i,flush=True)
if not any(i['level']=='ERROR' for i in issues):
 print('Exporting',flush=True);export_world();print('EXPORTED',flush=True)
else:raise RuntimeError('Validation errors')
