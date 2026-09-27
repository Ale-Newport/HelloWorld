#!/bin/zsh
set -e
cd -- "${0:A:h}"
/Applications/Blender.app/Contents/MacOS/Blender --factory-startup -b world/AlejandroWorld.blend --python-exit-code 1 --python tests/v2-blender.py
node --loader ./tests/local-loader.mjs tests/v2-physics.mjs
node --loader ./tests/local-loader.mjs tests/v3-world2.mjs
node --loader ./tests/local-loader.mjs tests/v3-handling.mjs
node --loader ./tests/local-loader.mjs scripts/v2/audit_scene.mjs
python3 scripts/v2/road_geometry.py
python3 tests/check_assets.py
read '?Tests complete. Press Return to close.'
