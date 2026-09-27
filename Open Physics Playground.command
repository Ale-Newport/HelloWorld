#!/bin/zsh
cd -- "${0:A:h}"
exec /Applications/Blender.app/Contents/MacOS/Blender world/PhysicsPlayground.blend --python scripts/open_editor.py
