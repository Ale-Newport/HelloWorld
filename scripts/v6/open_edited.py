"""Import the MAP/3D shared world into a separate v6 Blender document."""
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('hello_world_native_v5', ROOT / 'scripts/v5/open_edited.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


def import_world(source=None, output=None):
    return native._legacy.import_world(
        source or ROOT / 'exports/EditedWorld.glb',
        output or ROOT / 'world/EditedWorld_v6.blend',
        version=6, configure_scene=native.frame_authored_world,
        report_path=ROOT / 'reports/v6/native-roundtrip.json')


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    import_world(*args[:2])
