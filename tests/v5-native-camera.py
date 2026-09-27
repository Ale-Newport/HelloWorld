"""Blender-only synthetic camera checks; never imports or saves the user world."""
from pathlib import Path
import inspect
import json
import sys
import bpy
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts/v5'))
from open_edited import authored_points, frame_authored_world, _legacy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200
results = []


def mesh(name, vertices, **properties):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], [(0, 1, 2)])
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    for key, value in properties.items():
        obj[key] = value
    return obj


def test(name, fn):
    try:
        evidence = fn()
        results.append({'name': name, 'passed': True, 'evidence': evidence})
        print('PASS', name, evidence, flush=True)
    except Exception as error:
        results.append({'name': name, 'passed': False, 'error': repr(error)})
        print('FAIL', name, repr(error), flush=True)


main = mesh('Main island', [(-145, -125, .15), (145, -125, .15), (145, 125, .15), (-145, 125, .15)], terrain=True)
extension = mesh('Southwest authored land', [(-332, -280, .15), (-156, -280, .15), (-156, -58, .15), (-332, -58, .15), (-500, -500, -7)], terrain=True, landTile='v5-extension')
mesh('Infinite sea', [(-3000, -3000, -.35), (3000, -3000, -.35), (3000, 3000, -.35)], sea=True)
mesh('Native physical proxy', [(-4000, -4000, 3), (4000, -4000, 3), (4000, 4000, 3)], aw_physics_proxy=True)
mesh('Deleted user asset', [(-5000, -5000, 3), (5000, -5000, 3), (5000, 5000, 3)], deleted=True)
bpy.context.view_layer.update()


def excluded_bounds():
    points, report = authored_points(scene)
    bounds = ([min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)])
    assert report['framed_objects'] == 2 and report['framed_terrain_vertices'] == 8
    assert bounds[0][:2] == [-332.0, -280.0] and bounds[1][:2] == [145.0, 125.0]
    return {'bounds': bounds, 'excluded': ['ocean', 'proxy', 'deleted', 'underwater skirt']}


def framed(resolution, direction):
    scene.render.resolution_x, scene.render.resolution_y = resolution
    report = frame_authored_world(scene, direction=direction)
    bpy.context.view_layer.update()
    points, _ = authored_points(scene)
    projected = [world_to_camera_view(scene, scene.camera, p) for p in points]
    assert all(.035 <= p.x <= .965 and .035 <= p.y <= .965 and p.z > 0 for p in projected), [tuple(p) for p in projected]
    assert all(p.z < scene.camera.data.clip_end for p in projected)
    return {'resolution': resolution, 'ortho_scale': report['camera']['ortho_scale'], 'all_vertices_inside': True}


def moved_land():
    extension.location.x = -150
    extension.rotation_euler.z = .2
    bpy.context.view_layer.update()
    report = framed((1600, 1200), (0, -220, 290))
    assert scene.camera['authoring_target'][0] < -100
    report['camera_target'] = list(scene.camera['authoring_target'])
    return report


def legacy_defaults():
    parameters = inspect.signature(_legacy.import_world).parameters
    assert parameters['version'].default == 4
    assert parameters['configure_scene'].default is None
    assert parameters['report_path'].default is None
    return {'v4_default_version': 4, 'v4_camera_hook_disabled': True, 'v4_report_default_preserved': True}


test('Authoring bounds exclude infinite sea and underwater skirt while including southwest land', excluded_bounds)
test('Landscape native overview includes every authored vertex with margin', lambda: framed((1600, 1200), (0, -220, 290)))
test('Portrait aerial overview uses the actual aspect ratio', lambda: framed((800, 1200), (0, -310, 260)))
test('Moved and rotated terrain recomputes the camera centre and scale', moved_land)
test('Historical v4 importer keeps unchanged default configuration', legacy_defaults)
target = ROOT / 'reports/v5/native-camera-tests.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps({'passed': all(r['passed'] for r in results), 'results': results}, indent=2))
if any(not r['passed'] for r in results):
    raise RuntimeError('Native camera regression failed')
