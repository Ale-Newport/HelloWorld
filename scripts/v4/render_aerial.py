"""Render the imported v4 world without changing its saved authoring document."""
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
scene=bpy.context.scene
assert scene.get('world_builder_version')=='4.0.0','Open world/EditedWorld_v4.blend first'
scene.frame_set(1)
camera=scene.camera; camera.location=(0,-310,260); camera.rotation_euler=(Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=335
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=-.5
# Soft opposing fill makes exported glTF colours readable without an HDRI dependency.
light=bpy.data.lights.new('Aerial ambient fill','SUN');light.energy=.55;light.angle=.8
obj=bpy.data.objects.new('Aerial ambient fill',light);scene.collection.objects.link(obj);obj.rotation_euler=(.6,.7,2.8)
scene.render.filepath=str(ROOT/'reports/v4/world-aerial.png')
bpy.ops.render.render(write_still=True)
print('V4_AERIAL',scene.render.filepath,flush=True)
