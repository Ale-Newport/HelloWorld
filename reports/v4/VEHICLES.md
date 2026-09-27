# Vehicles — v4

The current car remains based on the World2 Player, Rapier raycast vehicle, wheel placement, 2.5 kg body and −0.9 m effective centre of mass. The original moving force tuning is unchanged. New behaviour is confined to `VehicleInput`, `VehicleModes`, the optional parking extension and shallow/deep-water recovery.

## Creep diagnosis

With throttle exactly zero and the source gamepad's existing 0.2 dead zone, a perfectly horizontal floor produced zero motion. A 0.57° slope produced 0.328 m of drift over 25 seconds. The raycast suspension's 1/60 update against 1/30 gravity integration retained small tangential wheel impulses. It was a supported-body rolling residual, not an injected throttle.

Parking now requires four static contacts with coherent normals within 3° of horizontal, low measured horizontal/angular movement, upright chassis, normal suspension and no throttle/boost. After a settling interval, a bounded tyre-friction impulse cancels the planar residual. Vertical suspension remains live. Input, an external impulse, collisions, hills and ice release or prevent this state. The same slight-slope test then produces zero displacement; a 6.9° slope still rolls 3.93 m.

Rotated resting headings exposed a second source residual: the wheel side-friction solver amplified floating-point yaw errors into alternating ±1.1 rad/s impulses and a roughly 2° tremor. Parking now applies a bounded yaw moment (`I × Δω`) alongside planar static friction, leaving vertical suspension and pitch/roll live. Five headings from 0.3 to 2.75 radians remain stationary for 20 seconds; measured cumulative orientation noise is below 0.00004 rad. Steering, as well as throttle, releases parking. No moving steering or grip constants changed.

## Controls and modes

- Car: WASD or arrows, Shift boost, B brake, SPACE handbrake, R recovery, E interaction.
- SPACE is buffered for 300 ms. A single short tap applies a brief brake; holding continues it. Two taps inside the buffer change mode without first applying the brake. Repeat keydown is ignored.
- Plane: W/S speed, A/D turn, Q/E or up/down pitch. Drag within the viewport for optional mouse steering. Automatic roll/pitch levelling and a minimum speed keep flight stable.
- Double SPACE from a plane creates the car at the exact airborne position and preserves horizontal velocity. Gravity supplies the fall. Downward velocity is limited to 18 m/s; CCD is enabled during flight and the drop, then original car settings return after landing.
- One physical root, one active controller and one camera are retained across transformations. The raycast car controller performs no update in plane mode.
- Plane altitude has a gradual soft ceiling at 85 m. The world bounds exert gradual steering pressure when leaving the map.

The supplied `plane-corsair-f4u-4-low-poly-edition.zip` contains one GLB, nine mesh primitives, seven embedded materials, no external textures. Its unmodified GLB is stored under `assets/vehicles/plane/`; the display rotates original −Z forward to the vehicle's +X and scales to a 6.4 m wingspan. The propeller animates. The car has editable paint, separate roof, glazing, door trim, mirrors, grille, round lamps, bumpers, arch trim, wheels and suspension.

`vehicleLibraryEntries()` exposes the same car and plane models to the asset library. Runtime accepts edited source templates while retaining physical chassis tuning.

## Water

The source smooth damping is retained. Sea height is passed from the same world configuration used for the visible water. Shallow immersion does not trigger recovery. Only sustained deep immersion (2.2 seconds) or a fall 14 m below the waterline triggers recovery. A light water wake supplies feedback. A real sloping trimesh test drives into water, reverses back to dry sand and separately drops into deep water.

## Verification

Run `node --loader ./tests/local-loader.mjs tests/v4-vehicle.mjs`.

Eleven suites cover input buffering, creep and slopes, source chassis properties, a 260 m flight circuit, altitude ceiling, a 29.5 m drop and landing, 24 repeated transformations with unchanged body count, actual shallow-water entry/exit, deep recovery, supplied GLB portability, building collisions, ice and steering release.

The original `tests/v3-handling.mjs` reference sequence also still produces 0 m difference for the underlying source tuning when the new optional parking/controller layer is disabled. Its recorded Space=jump is deliberately a source-reference binding, not the v4 live binding.

Browser QA at `tests/vehicle-review.html`: observed real double-space CAR→PLANE→CAR, correct model visibility, flight chase camera, real drop/landing, unchanged physical body count, configurable paint, and zero console errors. It also exposed and verified a recovery-camera fix. The test page does not save or alter the user's world.

## Actual map verification

`tests/v4-world.mjs` builds the delivered v4 terrain, roads, imported assets, physical lake and eleven source World2 controllers. All ten checks pass: supported default spawn (0.144 mm vertical settling and zero yaw), shallow beach entry/reverse, mainland-to-ice entry, red and timber bridge crossings with four wheel contacts, pit-lane traversal, full-island flight and repeated transformations. The flight visits eight waypoints, covers a 298 × 225 m envelope and returns above the mainland; `island-flight-route.json` records it. Fourteen transformations keep 650 bodies and the same chassis handle. The airborne car drops from 29.7 m and lands on actual map geometry.

Profiling 1,200 actual-world fixed steps records 0.62 ms average / 0.77 ms p95 for physics, with 81 dynamic bodies and only three awake after settling. The existing source sleeping behavior remains enabled; no distant physics or interactions were removed for this timing. Browser integration separately observed both double-space transitions in the main map without console errors.

Asset Studio car-definition regression: edited roof paint/metalness, wheel suspension offset and tilt, deleted wheel, hidden lamp and authored boost-cell position survive 100 visual updates. Shell reset restores each part’s authored material; explicit Vehicle Color updates the paint mapping. Private texture clones prevent disposal of a Drive instance from disposing the source definition textures.
