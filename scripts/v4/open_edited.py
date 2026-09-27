"""Import the v4 web export without flattening its editable/animated hierarchy."""
from pathlib import Path
import bpy, json, sys
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'editor'))

def disabled(obj):
    return obj.get('editorOnly') or obj.get('deleted') or obj.get('physicsPreset') == 'No Collision' or obj.get('collisionSubtree') is False or (obj.get('assetPhysicsEdited') and obj.get('collision') is False)

def collision_parts(owner):
    found = []
    def visit(obj):
        if disabled(obj): return
        if obj != owner and obj.get('assetPhysicsEdited') and obj.get('collision'): return
        if obj.type == 'MESH' and (obj == owner or obj.get('collision') is not False): found.append(obj)
        for child in obj.children: visit(child)
    visit(owner)
    return found

def import_world(source=None, output=None):
    source = Path(source or ROOT / 'exports/EditedWorld.glb')
    output = Path(output or ROOT / 'world/EditedWorld_v4.blend')
    if not source.exists(): raise RuntimeError('Use Export GLB in World Studio first: exports/EditedWorld.glb is missing.')
    # Verify the input before clearing Blender's current document.
    raw = source.read_bytes(); size = int.from_bytes(raw[12:16], 'little'); document = json.loads(raw[20:20+size])
    if not any(n.get('extras', {}).get('worldVersion') == 4 for n in document.get('nodes', [])):
        raise RuntimeError('Export the new v4 map in World Studio first. The existing GLB is an earlier map.')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import alejandro_world
    if not hasattr(bpy.types.Scene, 'aw'): alejandro_world.register()
    bpy.ops.import_scene.gltf(filepath=str(source))
    scene = bpy.context.scene; scene.name = 'Alejandro World · v4'; scene.render.fps = 24; scene.frame_end = 721
    visual = list(scene.objects)
    parents = {o.name: o.parent.name if o.parent else None for o in visual}
    physical_collection = bpy.data.collections.new('PHYSICS · v4 hidden proxies'); scene.collection.children.link(physical_collection)
    owners = []
    for obj in visual:
        if not obj.get('collision') or disabled(obj): continue
        blocked = False; owned = False; p = obj.parent
        while p:
            if disabled(p): blocked = True; break
            if p.get('collision'): owned = True
            p = p.parent
        if not blocked and (not owned or obj.get('assetPhysicsEdited')): owners.append(obj)
    proxies = []; configurations = []
    for owner in owners:
        parts = collision_parts(owner)
        if not parts: continue
        inverse = owner.matrix_world.inverted_safe(); vertices = []; faces = []
        for part in parts:
            transform = inverse @ part.matrix_world; offset = len(vertices)
            vertices.extend(tuple(transform @ v.co) for v in part.data.vertices)
            faces.extend(tuple(offset + i for i in polygon.vertices) for polygon in part.data.polygons)
        if not faces: continue
        mesh = bpy.data.meshes.new('Collider · ' + owner.name); mesh.from_pydata(vertices, [], faces); mesh.update()
        proxy = bpy.data.objects.new('PHYSICS · ' + owner.name, mesh); physical_collection.objects.link(proxy); proxy.matrix_world = owner.matrix_world.copy()
        proxy['aw_physics_proxy'] = True; proxy['visual_owner'] = owner.name; proxy.hide_render = True; proxy.display_type = 'WIRE'
        mode = owner.get('physics_mode', 'STATIC'); shape = 'MESH' if mode == 'STATIC' else 'CONVEX_HULL'
        proxy['physics_enabled'] = True; proxy['physics_mode'] = mode; proxy['collision'] = True; proxy['collision_shape'] = shape
        proxy['mass'] = owner.get('mass', 1); proxy['friction'] = owner.get('friction', .7)
        configurations.append((proxy, owner, mode, shape)); proxies.append(proxy)
    # One operator evaluates the imported scene once. Per-object object_add
    # forces thousands of dependency-graph updates on an 8,000-node map.
    if proxies:
        bpy.ops.object.select_all(action='DESELECT')
        for proxy in proxies: proxy.select_set(True)
        bpy.context.view_layer.objects.active = proxies[0]
        bpy.ops.rigidbody.objects_add(type='PASSIVE')
        for proxy, owner, mode, shape in configurations:
            rb = proxy.rigid_body; rb.type = 'PASSIVE' if mode == 'STATIC' else 'ACTIVE'; rb.kinematic = mode == 'KINEMATIC'; rb.collision_shape = shape
            rb.mass = max(.001, owner.get('mass', 1)); rb.friction = owner.get('friction', .7); rb.restitution = owner.get('restitution', .08)
            rb.linear_damping = owner.get('linear_damping', .08); rb.angular_damping = owner.get('angular_damping', .12); rb.use_margin = True; rb.collision_margin = .005
            if mode != 'STATIC':
                constraint = owner.constraints.new('COPY_TRANSFORMS'); constraint.name = 'Follow native physical proxy'; constraint.target = proxy
                constraint.owner_space = 'WORLD'; constraint.target_space = 'WORLD'
            proxy.hide_set(True)
        print('V4_COLLIDERS', len(proxies), 'created in one batch; visual hierarchy preserved', flush=True)
    assert parents == {o.name: o.parent.name if o.parent else None for o in visual}, 'Visual hierarchy changed during collider creation'
    for image in bpy.data.images:
        if image.source == 'FILE' and image.users and not image.packed_file:
            image.pack()
    scene['world_builder_version'] = '4.0.0'; scene['web_runtime_source'] = 'HelloWorld/preview'; scene['web_gameplay_note'] = 'World2 games and vehicle transformation execute in the web runtime; native Bullet proxies preserve editable visual hierarchy.'
    scene.world = bpy.data.worlds.new('Island daylight'); scene.world.use_nodes = True; scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.32,.58,.68,1); scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .7
    light = bpy.data.lights.new('Sun', 'SUN'); light.energy = 2.6; obj = bpy.data.objects.new('Sun', light); scene.collection.objects.link(obj); obj.rotation_euler = (.4,-.45,-.6)
    data = bpy.data.cameras.new('WORLD OVERVIEW v4'); camera = bpy.data.objects.new('WORLD OVERVIEW v4', data); scene.collection.objects.link(camera)
    camera.location = (0,-220,290); camera.rotation_euler = (Vector((0,0,0))-camera.location).to_track_quat('-Z','Y').to_euler(); data.type = 'ORTHO'; data.ortho_scale = 335; scene.camera = camera
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 24; scene.render.resolution_x = 1600; scene.render.resolution_y = 1200; scene.frame_set(1)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_rotation = camera.rotation_euler.to_quaternion(); area.spaces.active.region_3d.view_distance = 300; area.spaces.active.show_region_ui = True
    bpy.ops.object.select_all(action='DESELECT')
    output.parent.mkdir(parents=True, exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=str(output), compress=True)
    report = {'source':str(source.relative_to(ROOT)), 'output':str(output.relative_to(ROOT)), 'visual_objects':len(visual), 'visual_parent_links_preserved':True, 'physics_proxies':len(proxies), 'dynamic_proxies':sum(p.rigid_body.type == 'ACTIVE' for p in proxies), 'animation_actions':len(bpy.data.actions), 'packed_images':sum(bool(i.packed_file) for i in bpy.data.images), 'compressed':True, 'native_bytes':output.stat().st_size}
    (ROOT/'reports/v4/native-roundtrip.json').write_text(json.dumps(report, indent=2)); print('V4_NATIVE_ROUNDTRIP',json.dumps(report),flush=True)
    return report

if __name__ == '__main__': import_world()
