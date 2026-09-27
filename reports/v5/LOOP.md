# Saved-world loop regression — 27 September 2026

Tested the user's `exports/editor-world.json` saved at `2026-09-27T09:25:29.171Z`, restored with the same editor state/definition methods as the application. This work does not modify the saved world, asset definitions, loop geometry, general car tuning or Portfolio.

## Cause

The loop retains its original v4 matrix (position `[135, 0.08500000234, -204.5]`, identity rotation, scale `[1,1,1]`). Its entrance/exit and the saved approach roads still match. No separate invisible collider obstructs its top.

The previous assistance only activated within three metres of the first endpoint with **world-X velocity >12 m/s**. Ordinary W driving reaches this entrance around **6.5–8 m/s**, so assistance never started. The car climbed to approximately **9.84 m**, lost wheel support/speed, and its chassis collided with the loop ribbon itself. Entering from the opposite connected road could never activate assistance, including with boost. Captured baseline: only **2/8** natural approaches completed; both were boosted +X entries. Full contact/trajectory evidence is in `loop-before.json`.

## Fix

`preview/runtime/loop.js` now detects both entrances from their transformed tangents. It requires supported wheels, forward alignment and a narrow entry corridor, starting at normal driving speeds. The local ribbon frame supports editor rotations/scales and preserves the driving side in either travel direction. Its speed assistance ramps in; it never sets chassis translation, creates a body, removes collision or changes the road mesh. Brake, displacement or a real obstruction releases assistance.

## Verification

`node --loader ./tests/local-loader.mjs tests/v4-saved-loop.mjs` — **12/12 PASS**.

- Actual saved map, **673 physics bodies**, all **12** source World2 gameplay activities initialized, original `Player` input and vehicle suspension/controller.
- Eight traversals: 25%, 55% and full throttle, plus full throttle with boost, from both connected roads. Measured entry speeds **3.55–9.52 m/s**; all complete the full loop and reach the opposite road on all four wheels.
- Every traversal: **100%** of assisted samples have at least two supported wheels, zero chassis contact impacts, zero respawns and zero `setTranslation` calls. Largest per-step displacement **0.728 m**.
- Brake immediately releases adhesion and reaches the original wheel brake.
- Added solid barrier produces real contact, blocks progress and releases assistance; it is not bypassed.
- Transformed frame checks preserve orthogonal axes and the inner driving side in both directions.

`node --loader ./tests/local-loader.mjs tests/v4-routes.mjs` — **7/7 PASS**, including the original 19 m/s loop entry and approach continuity. The initial natural diagnostic also tested 7 m and 18 m approaches with and without boost in both directions: **8/8 PASS** after correction (`loop-natural-diagnostic.json`).

Detailed results and sampled trajectories are in `saved-loop-tests.json`; compact metrics are in `loop-summary.json`.
