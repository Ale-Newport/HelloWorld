"""Import the saved web world and frame all authored land, including expansions.

Blender --background --python scripts/v5/open_edited.py
Optional arguments after -- are the input GLB and output .blend paths.
"""
from pathlib import Path
import importlib.util
import json
import math
import sys
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location('hello_world_native_v4', ROOT / 'scripts/v4/open_edited.py')
_legacy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy)


def excluded(obj):
    """Never frame the ocean backdrop, hidden colliders or editor-only objects."""
    node = obj
    while node:
        if (node.hide_render or node.get('deleted') or node.get('editorOnly')
                or node.get('runtimeOnly') or node.get('aw_physics_proxy')
                or node.get('sea') or node.get('derivedWater')
                or node.get('w2Role') == 'collider'):
            return True
        node = node.parent
    return False


def authored_points(scene, objects=None):
    sea_level = next((float(o['seaLevel']) for o in scene.objects if 'seaLevel' in o), -.35)
    points = []
    selected = []
    terrain_vertices = 0
    for obj in objects if objects is not None else scene.objects:
        if obj.type != 'MESH' or excluded(obj) or not len(obj.data.vertices):
            continue
        if obj.get('terrain') or obj.get('landTile'):
            # Mesh bounds include the underwater skirt. Use visible land vertices
            # in Blender's Z-up coordinates, not the full seabed bounding box.
            local = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
            local = [p for p in local if p.z >= sea_level + .1]
            terrain_vertices += len(local)
        else:
            local = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        finite = [p for p in local if all(math.isfinite(v) for v in p)]
        if finite:
            points.extend(finite)
            selected.append(obj.name)
    if not points:
        raise RuntimeError('No visible authored geometry found for the native camera.')
    return points, {'framed_objects': len(selected), 'framed_terrain_vertices': terrain_vertices,
                    'sea_level': sea_level, 'ocean_excluded': True}


def frame_authored_world(scene, objects=None, *, direction=(0, -220, 290), padding=1.10):
    """Fit projected geometry to a horizontal-fit orthographic camera."""
    points, evidence = authored_points(scene, objects)
    camera = scene.camera
    if camera is None:
        data = bpy.data.cameras.new('WORLD OVERVIEW v5')
        camera = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(camera)
        scene.camera = camera
    outward = Vector(direction).normalized()
    rotation = (-outward).to_track_quat('-Z', 'Y')
    right = rotation @ Vector((1, 0, 0))
    up = rotation @ Vector((0, 1, 0))
    axes = (right, up, outward)
    ranges = [(min(p.dot(axis) for p in points), max(p.dot(axis) for p in points)) for axis in axes]
    centre = sum((axis * ((low + high) / 2) for axis, (low, high) in zip(axes, ranges)), Vector())
    width = ranges[0][1] - ranges[0][0]
    height = ranges[1][1] - ranges[1][0]
    depth = ranges[2][1] - ranges[2][0]
    aspect = (scene.render.resolution_x * scene.render.pixel_aspect_x) / (scene.render.resolution_y * scene.render.pixel_aspect_y)
    scale = max(width, height * aspect, 1) * padding
    distance = depth / 2 + max(250, scale * 1.25)
    camera.location = centre + outward * distance
    camera.rotation_euler = rotation.to_euler()
    camera.data.type = 'ORTHO'
    camera.data.sensor_fit = 'HORIZONTAL'
    camera.data.ortho_scale = scale
    camera.data.clip_start = .1
    camera.data.clip_end = distance + depth / 2 + 250
    camera['authoring_target'] = list(centre)
    camera['authoring_view_distance'] = distance
    minimum = [min(p[i] for p in points) for i in range(3)]
    maximum = [max(p[i] for p in points) for i in range(3)]
    evidence.update({'authored_bounds_blender': {'min': minimum, 'max': maximum},
                     'camera': {'location': list(camera.location), 'target': list(centre),
                                'ortho_scale': scale, 'sensor_fit': 'HORIZONTAL',
                                'clip_end': camera.data.clip_end, 'padding': padding,
                                'projected_width': width, 'projected_height': height,
                                'resolution': [scene.render.resolution_x, scene.render.resolution_y]}})
    scene['authoring_camera_bounds'] = json.dumps(evidence['authored_bounds_blender'])
    return evidence


def import_world(source=None, output=None):
    return _legacy.import_world(source or ROOT / 'exports/EditedWorld.glb',
                                output or ROOT / 'world/EditedWorld_v5.blend',
                                version=5, configure_scene=frame_authored_world,
                                report_path=ROOT / 'reports/v5/native-roundtrip.json')


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    import_world(*args[:2])
