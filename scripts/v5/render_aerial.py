"""Render the full imported v5 world without resaving its authoring document."""
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from open_edited import frame_authored_world


def render_aerial(output=None):
    scene = bpy.context.scene
    assert scene.get('world_builder_version') == '5.0.0', 'Open world/EditedWorld_v5.blend first'
    scene.frame_set(1)
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    frame_authored_world(scene, direction=(0, -310, 260))
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = -.5
    light = bpy.data.lights.get('Aerial ambient fill') or bpy.data.lights.new('Aerial ambient fill', 'SUN')
    light.energy = .55
    light.angle = .8
    obj = bpy.data.objects.get('Aerial ambient fill')
    if obj is None:
        obj = bpy.data.objects.new('Aerial ambient fill', light)
        scene.collection.objects.link(obj)
    obj.rotation_euler = (.6, .7, 2.8)
    target = Path(output or ROOT / 'reports/v5/world-aerial.png')
    target.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(target)
    bpy.ops.render.render(write_still=True)
    print('V5_AERIAL', scene.render.filepath, flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    render_aerial(args[0] if args else None)
