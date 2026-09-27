"""Reproducible rebuild into a new working file, never overwrites sources.
Run Blender --factory-startup --background --python scripts/build_world.py.
Authoring changes belong in the blend; rebuild is an explicit reset from sources.
"""
from pathlib import Path
import bpy,sys,math,json,time,shutil,datetime
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'editor'),str(ROOT/'scripts')]
import alejandro_world
from alejandro_world.core import collection,activate
from alejandro_world.physics import configure
from worldgen.common import *
from worldgen.base import load_base,title,recover_images
from worldgen.layout import zones
from worldgen.polish import polish
from worldgen.migrate_circuit import migrate_circuit

def build():
    t=time.time()
    previous=ROOT/'world/AlejandroWorld.blend'
    if previous.exists():shutil.copyfile(previous,ROOT/'backups'/('AlejandroWorld_before_rebuild_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.blend'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not hasattr(bpy.types.Scene,'aw'):alejandro_world.register()
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1;scene.name='Alejandro World';scene.render.fps=24;scene.frame_start=1;scene.frame_end=721
    world=collection('WORLD');names=['TERRAIN','ROADS','RACE_TRACK','ICE_RINK','ROAD_LOOP','ATTRACTIONS','BUILDINGS','VEHICLES','VEGETATION','CHARACTERS','PROPS','DECORATION','PARK','ORIGINAL_DISTRICT','PERSONALIZATION','LIGHTING','ANIMATED_OBJECTS','SYSTEM','COLLIDERS','SOURCE_REFERENCES']
    cols={name:collection(name,world) for name in names};cols['SYSTEM'].hide_render=True;cols['SOURCE_REFERENCES'].hide_render=True
    setup()
    fp=ROOT/'assets/fonts/Geist-Bold.ttf'
    if fp.exists():bpy.data.fonts.load(str(fp))
    sources=load_base(ROOT,cols);title(ROOT,cols)
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'world/01_BaseRecovered.blend'))
    routes=zones(ROOT,cols,sources)
    polish(ROOT,cols)
    migrate_circuit(cols)
    for o in list(scene.objects):
        if o.get('ground_surface') and o.type=='MESH':configure(o,'STATIC','MESH',1,o.get('friction',.7))
    scene.rigidbody_world.substeps_per_frame=8;scene.rigidbody_world.solver_iterations=20;scene.rigidbody_world.point_cache.frame_end=721
    # Base terrain includes its authored basins; one water sheet only shows through them.
    water=cube('World water',(-38,6,-.43),(1200,1200,.1),material('AW Water',(.10,.32,.38,1),.35),cols['TERRAIN']);water['collision']=False;water['surface_type']='water';water['water_ice']=True
    recover_images(ROOT)
    for font in bpy.data.fonts:
        if font.filepath and font.filepath!='<builtin>':
            try:font.pack();font.filepath='//../assets/fonts/'+Path(font.filepath).name
            except Exception:pass
    # Remove unreferenced FBX-only material images after replacing their materials.
    for mat in list(bpy.data.materials):
        if mat.users==0:bpy.data.materials.remove(mat)
    for image in list(bpy.data.images):
        if image.users==0:bpy.data.images.remove(image)
    scene.world=bpy.data.worlds.new('Warm island daylight');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.30,.43,.52,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    light=bpy.data.lights.new('Afternoon sun','SUN');light.energy=2.3;light.angle=math.radians(10);sun=bpy.data.objects.new('Afternoon sun',light);cols['LIGHTING'].objects.link(sun);sun.rotation_euler=(math.radians(26),math.radians(-22),math.radians(-28))
    camera=save_camera('Camera / whole world',(-285,-350,325),(-40,6,0),465,cols['LIGHTING']);scene.camera=camera
    save_camera('Camera / ice',(-34,64,67),(25,130,0),80,cols['LIGHTING']);save_camera('Camera / wheel',(75,-23,48),(128,44,11),67,cols['LIGHTING']);save_camera('Camera / circuit',(-273,-149,151),(-175,-7,0),190,cols['LIGHTING']);save_camera('Camera / loop',(-70,-200,57),(-26,-134,6),84,cols['LIGHTING']);save_camera('Camera / welcome',(66,-94,42),(44,-40,0),52,cols['LIGHTING'])
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    scene.frame_set(1);scene.aw.ground_snap=False
    bpy.ops.object.select_all(action='DESELECT')
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                space=area.spaces.active;space.clip_end=2000;space.region_3d.view_distance=310;space.region_3d.view_location=Vector((-40,0,0));space.region_3d.view_rotation=camera.rotation_euler.to_quaternion();space.shading.type='MATERIAL';space.show_region_ui=True
    info=bpy.data.texts.new('START HERE · Alejandro World');info.write('Open with Open Alejandro World.command to enable the editor for this session.\nSidebar N > Alejandro World.\nSource and backups are untouched.\nWorldLoop is a 30-second seamless Ferris wheel cycle.\nRead README.md for driving, validation and portable export.\n')
    # Remove empty import collections, keeping the deliberate world hierarchy.
    for c in list(bpy.data.collections):
        if not c.objects and not c.children and c.name not in names and c.name not in ['WORLD','ASSET_LIBRARY']:bpy.data.collections.remove(c)
    scene['world_builder_version']='1.0.0';scene['identity']='Alejandro Newport';scene['source_blend_sha256']='df5286df6141a6bece01abbd873d87a7f3d915cb685c6c989883cb7457474080';scene['portfolio_read_only']=True
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'world/AlejandroWorld.blend'))
    report={'objects':len(scene.objects),'meshes':len(bpy.data.meshes),'materials':len(bpy.data.materials),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in scene.objects if o.type=='MESH' and not o.hide_render),'new_roads':len(routes),'dynamic_props':sum(bool(o.rigid_body and o.rigid_body.type=='ACTIVE') for o in scene.objects),'seconds':time.time()-t}
    (ROOT/'reports/build.json').write_text(json.dumps(report,indent=2));print('BUILD COMPLETE',report,flush=True)
if __name__=='__main__':
    build()
    import runpy
    runpy.run_path(str(ROOT/'scripts/finalize_world.py'),run_name='__main__')
