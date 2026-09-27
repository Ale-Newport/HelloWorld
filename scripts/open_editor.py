from pathlib import Path
import sys,bpy
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'editor'))
import alejandro_world
if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.show_region_ui=True
print('Alejandro World Builder is ready in Sidebar (N) > Alejandro World')
