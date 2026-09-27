import bpy,json,math,hashlib
from mathutils import Vector,Matrix
from .common import *
from .props import template,linked

def load_base(root,cols):
    for filename in ['world.glb','vegetation.glb']:bpy.ops.import_scene.gltf(filepath=str(root/'assets/environment/portfolio/models'/filename))
    originals=list(bpy.context.scene.objects)
    # Importing two glTFs can add identically authored duplicate hierarchy roots.
    for o in originals:
        source=o.get('w2Source',o.name);category=o.get('w2Category','scenery');role=o.get('w2Role','visual');collections=o.get('w2Collections',[])
        if isinstance(collections,str):collections=[collections]
        dest='VEGETATION' if category=='vegetation' else 'TERRAIN' if category=='terrain' else 'ROADS' if category=='roads' else 'ORIGINAL_DISTRICT'
        move_to(o,cols[dest]);tag(o,'Trees' if category=='vegetation' else 'Roads' if category=='roads' else 'Nature' if category=='terrain' else 'Props');o['source_name']=source
        if role=='collider':o.hide_render=True;o.display_type='WIRE';o['runtime_collider']=True;o['collision_shape']=str(o.get('w2Shape','BOX')).upper();move_to(o,cols['COLLIDERS'])
        if source=='terrain':ground(o,'terrain');o['original_terrain']=True
        elif source in ['refRoad','jump'] or category=='roads' and o.type=='MESH':ground(o,'asphalt',.9)
        elif o.type=='MESH' and category!='vegetation' and role!='collider':
            o['collision']=max(o.dimensions)>.9 and not any(s in source.lower() for s in ['label','banner','screen','gradient','carpet','disc','refheat','refliquid','waterfall']);o['collision_shape']='MESH'
        if category=='vegetation':o['collision']=bool(o.get('w2Trunk',False));o['lod_distance']=160
        if 'refLettersPhysicalDynamic' in source:
            o.hide_render=True;o.hide_set(True);o['collision']=False;move_to(o,cols['SOURCE_REFERENCES'])
    # Normalize equivalent shared materials by name and image, without merging distinct shaders.
    for mat in list(bpy.data.materials):
        if mat.name.endswith('.001'):
            base=bpy.data.materials.get(mat.name[:-4])
            if base and mat.use_nodes and base.use_nodes:
                a=[n.image.name.split('.')[0] for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image];b=[n.image.name.split('.')[0] for n in base.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
                if a==b:mat.user_remap(base);bpy.data.materials.remove(mat)
    # Store reusable source props with local geometry and a bottom pivot.
    sources={}
    for label,category,needle in [('Original cone','Props','refCone'),('Original birch','Trees','treeBody'),('Original rock','Rocks','basaltRock'),('Original barrel','Props','barrel'),('Original bench','Street furniture','bench')]:
        o=next((o for o in originals if o.type=='MESH' and needle.lower() in o.get('source_name',o.name).lower() and not o.hide_render),None)
        if o:
            clone=o.copy();clone.data=o.data.copy();clone.parent=None;clone.matrix_world=o.matrix_world.copy();cols['SYSTEM'].objects.link(clone)
            activate(clone);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);pts=[clone.matrix_world@Vector(p) for p in clone.bound_box];pivot=Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,(min(p.y for p in pts)+max(p.y for p in pts))/2,min(p.z for p in pts)))
            bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');clone.location=(0,0,0)
            sources[label]=template(clone,label,category);bpy.data.objects.remove(clone,do_unlink=True)
    # A complete tree uses the actual Portfolio leaves and trunk; mesh data shared thereafter.
    tree_root=next((o for o in originals if o.get('w2Role')=='tree' and o.children),None)
    if tree_root:
        parts=[]
        for child in tree_root.children:
            if child.type=='MESH':
                c=child.copy();c.data=child.data.copy();c.parent=None;c.matrix_world=child.matrix_world.copy();cols['SYSTEM'].objects.link(c);parts.append(c)
        tree=join(parts,'Source oak complete',cols['SYSTEM']);activate(tree);bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);pts=[tree.matrix_world@Vector(p) for p in tree.bound_box];pivot=((min(p.x for p in pts)+max(p.x for p in pts))/2,(min(p.y for p in pts)+max(p.y for p in pts))/2,min(p.z for p in pts));bpy.context.scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR');tree.location=(0,0,0);sources['Portfolio tree']=template(tree,'Portfolio tree','Trees');bpy.data.objects.remove(tree,do_unlink=True)
    bpy.context.scene.cursor.location=(0,0,0)
    return sources

def title(root,cols):
    # Match the source landing heading and type scale; the identity was runtime-only.
    center=Vector((44,-41,0));heading=math.radians(25);along=Vector((math.cos(heading),math.sin(heading),0));normal=Vector((-math.sin(heading),math.cos(heading),0))
    for i,line in enumerate(['ALEJANDRO','NEWPORT']):
        p=center+normal*(1.7-i*2.5);o=text('Alejandro Newport / '+line,line,(p.x,p.y,.09),1.9,'cream',cols['PERSONALIZATION'],(math.pi/2,0,heading),.25);o['personalization']=True;o['collision']=True;o['collision_shape']='MESH'
    text('Home inscription','CODE · CREATE · EXPLORE',(44,-47,.065),.43,'navy',cols['PERSONALIZATION'],(0,0,heading),.006)


def recover_images(root):
    # GLB images are embedded. Give all file-backed images local paths and pack.
    for img in bpy.data.images:
        if img.source=='FILE':
            _=img.pixels[:4]
            if not img.packed_file:img.pack()
            extension='.jpg' if img.file_format=='JPEG' else '.png';filename=''.join(c if c.isalnum() or c in '-_' else '_' for c in img.name)
            dest=root/'textures/packed'/f'{filename}{extension}';dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():
                img.filepath_raw=str(dest)
                try:img.save()
                except RuntimeError:pass
            img.filepath='//../textures/packed/'+dest.name
