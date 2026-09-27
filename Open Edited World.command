#!/bin/zsh
cd -- "${0:A:h}"
exec /Applications/Blender.app/Contents/MacOS/Blender --python scripts/v2/open_edited.py
