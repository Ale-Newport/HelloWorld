# Map terrain integration

The physical terrain and the 2D map share the same scene root. `root.userData.mapTerrain` stores immutable authored heightfield sources and ordered polygon operations. It is JSON data and belongs in normal editor snapshots; no second world document is created.

```js
import {
  applyTerrainOperation, previewTerrainOperation, rebuildFromState,
  captureTerrainEdits, updateTerrainShoreline,
  terrainDebugData, createTerrainDebug,
} from '../preview/map-terrain.js';
import {surfaceMaterial, surfaceUV} from '../preview/surface-materials.js';

const options = {materialFactory: surfaceMaterial, uvFor: surfaceUV};
const operation = {
  kind: 'erase', // add | erase | paint
  polygon: [[-5,-5], [5,-5], [5,5], [-5,5]], // world XZ
  material: 'Grass',
  beachWidth: 2, // metres; 0 gives an exact, abrupt edge
};
const ghost = previewTerrainOperation(root, operation); // no mutation
if (ghost.valid) applyTerrainOperation(root, operation, options);
updatePrefabTerrain(root, true);
updateTerrainShoreline(root);
```

`polygons: [polygon, ...]` can replace `polygon`. The pieces are unioned as one operation, so an entire overlapping erase-brush stroke creates one undo step and no internal coast seams. The preview returns disjoint `cells`, area, height, and affected bounds. Invalid polygons throw before modifying terrain.

- **Add** unions land with existing terrain. Its interior uses the main island height. Existing geometry under the polygon is replaced, avoiding overlapping ground; source heights outside the polygon are preserved. Joined boundaries inherit exact source triangle heights, and exposed boundaries receive an inward beach ramp.
- **Erase** performs a true difference, including the original island and user land tiles. No visual or physical triangles remain inside the erased polygon. Its optional beach slope affects retained land within `beachWidth` of the new edge.
- **Paint** clips triangles into material regions without changing their heights. `uvFor` supplies world-space texture coordinates. Material groups survive moving prefab lake/canal cuts.

On Undo/Redo/load, call `rebuildFromState(root, options)` **unconditionally**, including when the restored state has no `mapTerrain`. The latter restores the original sources when undoing the first operation in this session. Rebuild before `updatePrefabTerrain`; then refresh shoreline and physical bodies/ground queries with the editor's existing hooks.

After a deliberate 3D terrain brush, call:

```js
captureTerrainEdits(root, {register: object => editor.reindexInstance(object)});
```

This establishes the edited heights as a new source, resets its operation list, and registers any baked new-land mesh as a normal added object. The surrounding editor transaction owns Undo. Without `register`, a newly baked mesh would not enter the editor registry/save list.

`terrainDebugData(root)` returns JSON-ready world XYZ boundary segments, sea-level shoreline, closed outer/hole contours, open contours (if present), and sampled actual heights. `createTerrainDebug(root)` creates a disposable Group with boundary, sea, holes and height layers. These use a geometry/transform cache, not a global polygon union every frame. `updateTerrainShoreline` hides old sampled foam while terrain edits are active and restores it on initial Undo; new foam is derived from actual terrain, not serialized as contour metadata. Call it again after prefab cuts so moving lakes and canals update the coast too.

`terrainShape(root)` is an optional exact polygon union of all visible land above the sea plane. It can be more expensive than the segment debug and should be requested only when needed.

Validation: `node --loader ./tests/local-loader.mjs tests/v6-map-terrain.mjs`. Tests compare boolean coverage against independent Shapely/GEOS, verify original heights/hash restoration, and use real Rapier support queries after save/reload.

## Height queries during editing

`preview/terrain-query.js` provides `terrainHeightAt(root,x,z,{minHeight,maxHeight,fallback})` and `getTerrainQuery(root).heightAt(...)`. It builds a spatial index of actual transformed triangles once, then interpolates only candidates in the queried 4 m cell. The former checks a small cache signature; the latter is a fixed snapshot useful inside a synchronous batch. Empty support returns `null` by default. Map ground uses `minHeight=seaLevel+.025`; road conformance can use `fallback:0` to preserve its existing fallback.

Call `invalidateTerrainQuery(root)` at the start of editor apply/endChange when scene membership may have changed. Existing terrain buffers, transforms and deleted/visible ancestors are also detected automatically. Map booleans and prefab cuts invalidate internally. Rendering layers and selection locks never affect ground queries. Do not build a Raycaster or update all scene matrices for every road vertex.

`tests/v6-terrain-query.mjs` compares the spatial sampler with 500 independent Raycaster probes and covers deleted terrain, transforms, layers, locks, terrain holes, new land, moving lake cuts and height filters. `scripts/v6/profile-road-creation.mjs` profiles the actual saved world's 30 m road creation and editor endChange without writing the save.
