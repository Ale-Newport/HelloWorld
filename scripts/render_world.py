import bpy,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];scene=bpy.context.scene
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['whole world','ice','wheel','circuit','loop','welcome']
scene.render.resolution_x=1400;scene.render.resolution_y=950;scene.cycles.samples=16
for name in args:
 scene.camera=bpy.data.objects['Camera / '+name];scene.render.filepath=str(root/'reports'/('view-'+name.replace(' ','-')+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
