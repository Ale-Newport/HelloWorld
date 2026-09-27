"""Portable asset storage, library placements and seeded scatter."""
from pathlib import Path
import bpy,shutil,hashlib,json,random,math
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
from ..core import project_root,collection,move_to,activate,tag
from ..placement import snap_object

_items_cache=[]
_enum_strings={}
def asset_items(self,context):
    global _items_cache
    category=context.scene.aw.category if context and hasattr(context.scene,'aw') else 'ALL'
    result=[(o.name,o.get('asset_label',o.name.replace('LIB_','')),'Linked mesh asset') for o in bpy.data.objects if o.get('aw_template') and (category=='ALL' or o.get('category')==category)]
    # Blender retains enum strings beyond draw(); keep stable Python references.
    result=result or [('NONE','No assets in this category','')]
    _items_cache=[tuple(_enum_strings.setdefault(v,v) for v in item) for item in result]
    return _items_cache

def clone_hierarchy(source,destination):
    mapping={}
    for original in [source,*source.children_recursive]:
        clone=original.copy();destination.objects.link(clone);mapping[original]=clone
    for original,clone in mapping.items():
        if original.parent in mapping:clone.parent=mapping[original.parent]
        elif original is source:
            matrix=original.matrix_world.copy();clone.parent=None;clone.matrix_world=matrix
    return mapping

def duplicate_template(template,context,position):
    clones=clone_hierarchy(template,collection('USER_ASSETS',collection('WORLD')));clone=clones[template]
    clone.name=template.get('asset_label',template.name.replace('LIB_',''))
    for original,new in clones.items():
        new.hide_render=bool(original.get('library_original_hide_render',False));new.hide_viewport=False;new.hide_set(False);new['aw_template']=False;new['aw_template_part']=False
    clone.location=position
    activate(clone);snap_object(clone,context.scene,context.scene.aw.align_surface,context.scene.aw.ground_offset)
    return clone

class AW_OT_asset(bpy.types.Operator):
    bl_idname='aw.asset';bl_label='Add to world';bl_options={'REGISTER','UNDO'}
    action:bpy.props.StringProperty(default='ADD')
    def execute(self,context):
        if self.action=='SAVE':
            o=context.object
            if not o or o.type not in {'MESH','EMPTY'}:return {'CANCELLED'}
            clones=clone_hierarchy(o,collection('ASSET_LIBRARY'));clone=clones[o]
            for original,new in clones.items():
                new['library_original_hide_render']=original.hide_render;new['aw_template_part']=original is not o;new.hide_render=True;new.hide_set(True)
            clone.name='LIB_'+o.name;clone['aw_template']=True;clone['asset_label']=o.name;clone.location=(0,0,-100);clone.asset_mark()
            try:clone.asset_generate_preview()
            except RuntimeError:pass
            return {'FINISHED'}
        template=bpy.data.objects.get(context.scene.aw.asset)
        if not template:return {'CANCELLED'}
        duplicate_template(template,context,context.scene.cursor.location.copy())
        if context.area and context.area.type=='VIEW_3D':bpy.ops.aw.place('INVOKE_DEFAULT')
        return {'FINISHED'}

def copy_import_bundle(source):
    source=Path(source).resolve();digest=hashlib.sha256(source.read_bytes()).hexdigest()[:10];dest=project_root()/'assets/imported'/f'{source.stem}_{digest}';dest.mkdir(parents=True,exist_ok=True)
    if source!=(dest/source.name).resolve():shutil.copyfile(source,dest/source.name)
    # Sidecars are copied with validated relative paths. No external dependencies survive.
    def sidecar(uri):
        if uri.startswith('data:'):return
        from urllib.parse import unquote
        rel=Path(unquote(uri))
        if rel.is_absolute() or '..' in rel.parts:raise ValueError('Use sidecar paths contained in the model folder')
        target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
        if (source.parent/rel).resolve()!=target.resolve():shutil.copyfile(source.parent/rel,target)
    if source.suffix.lower()=='.gltf':
        data=json.loads(source.read_text())
        for item in data.get('buffers',[])+data.get('images',[]):
            if 'uri' in item:sidecar(item['uri'])
    elif source.suffix.lower()=='.obj':
        for line in source.read_text(errors='replace').splitlines():
            if line.startswith('mtllib '):
                name=line[7:].strip();sidecar(name)
                for mline in (source.parent/name).read_text(errors='replace').splitlines():
                    if mline.startswith(('map_','bump ')):sidecar(mline.split()[-1])
    elif source.suffix.lower()=='.fbx':
        for folder in (source.parent/'textures',source.with_suffix('.fbm')):
            if folder.is_dir() and folder.resolve()!=(dest/folder.name).resolve():shutil.copytree(folder,dest/folder.name,dirs_exist_ok=True)
    return dest/source.name

class AW_OT_import(bpy.types.Operator,ImportHelper):
    bl_idname='aw.import_model';bl_label='Import 3D model';bl_options={'REGISTER','UNDO'}
    filename_ext='';filter_glob:bpy.props.StringProperty(default='*.glb;*.gltf;*.fbx;*.obj',options={'HIDDEN'})
    auto_scale:bpy.props.BoolProperty(name='Auto scale unusual dimensions',default=True)
    target_size:bpy.props.FloatProperty(name='Target size (m)',default=3,min=.01)
    collider:bpy.props.BoolProperty(name='Create static collider',default=True)
    def execute(self,context):
        before=set(bpy.data.objects);images_before=set(bpy.data.images)
        try:
            path=copy_import_bundle(self.filepath);ext=path.suffix.lower()
            if ext in ('.glb','.gltf'):bpy.ops.import_scene.gltf(filepath=str(path))
            elif ext=='.fbx':bpy.ops.import_scene.fbx(filepath=str(path))
            elif ext=='.obj':bpy.ops.wm.obj_import(filepath=str(path))
            else:raise ValueError('Unsupported format')
            created=set(bpy.data.objects)-before;roots=[o for o in created if o.parent not in created]
            from ..core import bounds
            pts=[p for o in created if o.type=='MESH' for p in bounds(o)]
            size=max(max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)) if pts else 1
            if self.auto_scale and (size>50 or size<.05):
                for o in roots:o.scale*=self.target_size/max(size,1e-8)
            for o in created:
                move_to(o,collection('USER_ASSETS',collection('WORLD')));tag(o);o['asset_source']='//../'+str(path.relative_to(project_root()))
                if self.collider and o.type=='MESH':
                    from ..physics import configure
                    configure(o,'STATIC')
            for img in set(bpy.data.images)-images_before:
                if img.source!='FILE':continue
                original=Path(bpy.path.abspath(img.filepath))
                if original.is_file():
                    target=project_root()/'textures/imported'/f'{hashlib.sha256(original.read_bytes()).hexdigest()[:10]}_{original.name}';target.parent.mkdir(parents=True,exist_ok=True)
                    if target.resolve()!=original.resolve():shutil.copyfile(original,target)
                    img.filepath=bpy.path.relpath(str(target))
                elif not img.packed_file:raise ValueError(f'Missing model texture: {img.name}')
                else:img.filepath='//../textures/imported/'+img.name
                if not img.packed_file:img.pack()
            for o in roots:o.location+=context.scene.cursor.location
            bpy.ops.object.select_all(action='DESELECT')
            for o in roots:o.select_set(True)
            if roots:context.view_layer.objects.active=roots[0]
            self.report({'INFO'},f'Imported {len(created)} objects; source size {size:.2f} m. Local copy saved.')
            return {'FINISHED'}
        except Exception as e:self.report({'ERROR'},str(e));return {'CANCELLED'}

class AW_OT_scatter(bpy.types.Operator):
    bl_idname='aw.scatter';bl_label='Scatter objects';bl_options={'REGISTER','UNDO'}
    def execute(self,context):
        s=context.scene.aw;template=bpy.data.objects.get(s.asset)
        if not template:self.report({'WARNING'},'Choose an asset first');return {'CANCELLED'}
        r=random.Random(s.seed);origin=context.scene.cursor.location.copy();positions=[];guide=context.object
        from ..roads import sample
        path=sample(guide,32) if s.scatter_mode=='CURVE' and guide and guide.type=='CURVE' else []
        if s.scatter_mode=='CURVE' and not path:self.report({'WARNING'},'Select a curve');return {'CANCELLED'}
        count=min(s.scatter_count,2000)
        if path:
            import bisect
            distances=[0.]
            for a,b in zip(path,path[1:]):distances.append(distances[-1]+(b-a).length)
            count=min(count,max(1,int(distances[-1]/s.min_distance)+1))
            samples=[]
            for i in range(count):
                target=distances[-1]*i/max(1,count-1);j=min(len(path)-2,max(0,bisect.bisect_right(distances,target)-1));factor=(target-distances[j])/max(1e-9,distances[j+1]-distances[j]);samples.append(path[j].lerp(path[j+1],factor))
            path=samples
        for attempt in range(count*40):
            if len(positions)>=count:break
            if path:p=path[min(len(path)-1,round(len(positions)*(len(path)-1)/max(1,count-1)))].copy()
            elif s.scatter_mode=='LINE':p=origin+Vector((len(positions)*s.min_distance,0,0))
            elif s.scatter_mode=='AREA':
                cols=max(1,int(math.sqrt(count)));p=origin+Vector(((len(positions)%cols)*s.min_distance,(len(positions)//cols)*s.min_distance,0))
            else:p=origin+Vector((r.uniform(-s.scatter_radius,s.scatter_radius),r.uniform(-s.scatter_radius,s.scatter_radius),0))
            if any((p-q).length<s.min_distance-.001 for q in positions):
                if path:break
                continue
            positions.append(p)
        for p in positions:
            o=duplicate_template(template,context,p);o.rotation_euler.z=r.uniform(0,math.tau) if s.random_rotation else 0;o.scale*=r.uniform(s.scale_min,s.scale_max);snap_object(o,context.scene,s.align_surface,s.ground_offset)
        self.report({'INFO'},f'Placed {len(positions)} linked instances (seed {s.seed})');return {'FINISHED'}
CLASSES=[AW_OT_asset,AW_OT_import,AW_OT_scatter]
