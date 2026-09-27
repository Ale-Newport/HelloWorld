# Version 2 acceptance evidence

The current acceptance results are `reports/v2-blender-tests.json`, `reports/v2-physics-tests.json`, `reports/v2-road-validation.json`, `reports/v2-scene-validation.json` and `reports/asset-tests.json`. Browser interaction evidence is recorded in `reports/v2-browser-qa.json`; the final file hashes are in `reports/delivery-manifest.json`.

- One continuous authored island replaces the five-island expansion.
- All named districts, the independent racing installation, eight penguins, cones, the imported Ferris wheel and connected loop are present.
- Road surfaces have upward normals and share clipped junction boundaries, with no stacked asphalt.
- Planned district footprints and measured principal building bounds are checked with a 1.2 m road margin.
- The exact ported Portfolio controller, actual World2 overrides, fixed-step ratio and procedural visual vehicle are used.
- Physical tests drive a complete boulevard lap, separate race lap and a continuous district tour including the loop, returning near Central Plaza. The automated driver uses steering, throttle and brake against the real exported colliders; it does not teleport between tour stages.
- Wheel animation, native and browser penguin stability, braking on ice and rigid-body impacts are checked separately.
- Browser interaction checks covered asset placement, name and numeric transforms, duplicate, undo, redo, save, reload, road width/control-point/guardrail editing, terrain sculpt/save/undo, Edit/Drive, camera state return and map.
- Static repeated meshes are instanced in spatial cells during Drive. Remaining static geometry is batched by material and cell. Edit preserves individually selectable objects.
- The browser saves an editable JSON document and can export a self-contained GLB for the separate Blender edited-world document.
- Source and v1 backups are preserved; the Portfolio snapshot checks 477 unchanged files.

Limits of the simplified editor: GLB or embedded-resource GLTF import in the browser; FBX/OBJ import through Blender. Undo history is session-local. Returning from simulation restores authored prop positions. Rebuilding the base world is an explicit reset; preserve an edited export before rebuilding.
