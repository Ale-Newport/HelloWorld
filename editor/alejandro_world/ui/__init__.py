import bpy

def quick(layout,label,action,icon='NONE'):
    op=layout.operator('aw.quick',text=label,icon=icon);op.action=action

def prop(layout,obj,name,text=None):
    if name in obj:layout.prop(obj,f'["{name}"]',text=text or name.replace('_',' ').title())

class AW_PT_main(bpy.types.Panel):
    bl_label='ALEJANDRO WORLD';bl_idname='AW_PT_main';bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Alejandro World'
    def draw(self,context):
        l=self.layout;l.label(text='Build a world worth exploring.',icon='WORLD');r=l.row(align=True);r.operator('wm.save_mainfile',text='Save',icon='FILE_TICK');r.operator('aw.validate',text='Validate',icon='CHECKMARK')
class AW_Section:
    bl_space_type='VIEW_3D';bl_region_type='UI';bl_category='Alejandro World';bl_parent_id='AW_PT_main';bl_options={'DEFAULT_CLOSED'}
class AW_PT_quick(AW_Section,bpy.types.Panel):
    bl_label='Quick Tools';bl_idname='AW_PT_quick';bl_options=set()
    def draw(self,c):
        l=self.layout;r=l.row(align=True);quick(r,'Drop to ground','DROP','IMPORT');quick(r,'Focus','FOCUS','VIEWZOOM');r=l.row(align=True);quick(r,'Duplicate','DUPLICATE','DUPLICATE');quick(r,'Delete','DELETE','TRASH');r=l.row(align=True);quick(r,'Align to surface','ALIGN','ORIENTATION_NORMAL');quick(r,'Random rotate','RANDOM','DRIVER_ROTATIONAL_DIFFERENCE')
class AW_PT_assets(AW_Section,bpy.types.Panel):
    bl_label='Assets';bl_idname='AW_PT_assets'
    def draw(self,c):
        l=self.layout;s=c.scene.aw;l.prop(s,'category');l.prop(s,'asset');r=l.row();r.operator('aw.asset',text='Add to World',icon='ADD');op=l.operator('aw.asset',text='Add selection to asset library',icon='ASSET_MANAGER');op.action='SAVE';l.label(text='Native Asset Browser also supported.',icon='INFO')
class AW_PT_transform(AW_Section,bpy.types.Panel):
    bl_label='Transform';bl_idname='AW_PT_transform'
    def draw(self,c):
        l=self.layout;o=c.object
        if not o:l.label(text='Select an object');return
        l.prop(o,'name',text='');l.prop(o,'location');l.prop(o,'rotation_euler',text='Rotation');l.prop(o,'scale');r=l.row(align=True);quick(r,'Reset rotation','ROTATION');quick(r,'Reset scale','SCALE');r=l.row(align=True);quick(r,'Center pivot','PIVOT');quick(r,'Apply scale','APPLY');r=l.row(align=True);quick(r,'Lock','LOCK','LOCKED');quick(r,'Unlock','UNLOCK','UNLOCKED');r=l.row(align=True);quick(r,'Hide','HIDE','HIDE_ON');quick(r,'Show all','SHOW','HIDE_OFF');quick(l,'Isolate / restore','ISOLATE','RESTRICT_VIEW_OFF')
class AW_PT_placement(AW_Section,bpy.types.Panel):
    bl_label='Placement';bl_idname='AW_PT_placement'
    def draw(self,c):
        l=self.layout;s=c.scene.aw
        for p in ['ground_snap','align_surface','grid_snap','rotation_snap','ground_offset','grid_size','rotation_increment','alignment_strength']:l.prop(s,p)
        l.operator('aw.place',text='Place with mouse',icon='ORIENTATION_CURSOR');l.label(text='Surfaces: mark Ground Surface in metadata.')
class AW_PT_roads(AW_Section,bpy.types.Panel):
    bl_label='Roads';bl_idname='AW_PT_roads'
    def draw(self,c):
        l=self.layout;o=c.object;op=l.operator('aw.road',text='Add Road',icon='CURVE_BEZCURVE');op.action='ADD'
        if o and o.get('aw_road'):
            prop(l,o,'road_width','Road width');l.prop_search(o,'["road_material"]',bpy.data,'materials',text='Material');prop(l,o,'barrier_left');prop(l,o,'barrier_right')
            for action,label in [('EXTEND','Extend road'),('REBUILD','Rebuild from curve'),('COLLISION','Generate collision')]:op=l.operator('aw.road',text=label);op.action=action
            l.label(text='Tab → move Bezier points → Rebuild.')
class AW_PT_scatter(AW_Section,bpy.types.Panel):
    bl_label='Vegetation & Scatter';bl_idname='AW_PT_scatter'
    def draw(self,c):
        l=self.layout;s=c.scene.aw;l.label(text='Uses asset chosen in Assets.');l.prop(s,'scatter_mode')
        for p in ['scatter_count','scatter_radius','min_distance','seed','random_rotation','scale_min','scale_max']:l.prop(s,p)
        l.operator('aw.scatter',icon='PARTICLES');l.label(text='Cursor is the centre of the area.')
class AW_PT_materials(AW_Section,bpy.types.Panel):
    bl_label='Materials';bl_idname='AW_PT_materials'
    def draw(self,c):
        l=self.layout;o=c.object
        if not o or o.type!='MESH':l.label(text='Select a mesh');return
        l.template_ID(o,'active_material',new='aw.material');m=o.active_material
        if m and m.use_nodes:
            p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
            if p:
                for key in ['Base Color','Roughness','Metallic','Alpha','Emission Color','Emission Strength']:l.prop(p.inputs[key],'default_value',text=key)
            r=l.row();op=r.operator('aw.texture',text='Texture',icon='IMAGE_DATA');op.normal=False;op=r.operator('aw.texture',text='Normal map');op.normal=True
            mapping=m.node_tree.nodes.get('AW Tiling')
            if mapping:l.prop(mapping.inputs['Scale'],'default_value',text='UV scale');l.prop(mapping.inputs['Rotation'],'default_value',text='UV rotation')
            else:op=l.operator('aw.material',text='Enable texture tiling');op.action='TILING'
        r=l.row();op=r.operator('aw.material',text='New');op.action='NEW';op=r.operator('aw.material',text='Make unique');op.action='UNIQUE';l.prop(c.scene.aw,'texture_metres');op=l.operator('aw.material',text='UVs in world metres');op.action='UV';l.prop_search(c.scene.aw,'material_name',bpy.data,'materials');op=l.operator('aw.material',text='Replace on selection');op.action='REPLACE'
class AW_PT_physics(AW_Section,bpy.types.Panel):
    bl_label='Physics';bl_idname='AW_PT_physics'
    def draw(self,c):
        l=self.layout;o=c.object
        if not o:l.label(text='Select an object');return
        r=l.row(align=True)
        for mode,label in [('STATIC','Static'),('DYNAMIC','Dynamic'),('KINEMATIC','Kinematic')]:op=r.operator('aw.physics',text=label);op.mode=mode
        op=l.operator('aw.physics',text='Auto Physics / Create Collision');op.mode='AUTO';rb=o.rigid_body
        if rb:
            for p in ['type','enabled','kinematic','mass','friction','restitution','linear_damping','angular_damping','collision_shape']:l.prop(rb,p)
            l.label(text='Web runtime overrides',icon='INFO');prop(l,o,'rolling_friction');prop(l,o,'gravity_scale');l.prop(o,'lock_location',text='Lock translation');l.prop(o,'lock_rotation',text='Lock rotation');l.operator('aw.axis_locks',text='Apply axis locks in Blender');op=l.operator('aw.physics',text='Remove physics');op.mode='REMOVE'
class AW_PT_metadata(AW_Section,bpy.types.Panel):
    bl_label='Metadata & Terrain';bl_idname='AW_PT_metadata'
    def draw(self,c):
        l=self.layout;o=c.object
        if not o:return
        if 'category' not in o:quick(l,'Initialize metadata','METADATA')
        for name in ['object_type','category','interactive','interaction_type','drivable','collision','breakable','animated','static_decoration','ground_surface','road','terrain','water_ice','surface_type']:prop(l,o,name)
class AW_PT_animation(AW_Section,bpy.types.Panel):
    bl_label='Animation';bl_idname='AW_PT_animation'
    def draw(self,c):
        l=self.layout;r=l.row(align=True);r.operator('screen.animation_play',text='Play / pause',icon='PLAY');r.operator('screen.frame_jump',text='First frame',icon='REW');l.prop(c.scene,'frame_current');l.prop(c.scene,'frame_start');l.prop(c.scene,'frame_end');l.label(text='FerrisWheel: 1–721, 30 seconds.');l.label(text='Cabins counter-rotate around pivots.')
class AW_UL_validation(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index):
        row=layout.row();op=row.operator('aw.select_issue',text=item.object_name,icon='ERROR' if item.level=='ERROR' else 'INFO');op.name=item.object_name;row.label(text=item.message)
class AW_PT_validation(AW_Section,bpy.types.Panel):
    bl_label='Optimization & Validation';bl_idname='AW_PT_validation'
    def draw(self,c):
        l=self.layout;l.operator('aw.validate',icon='CHECKMARK');l.label(text=c.scene.aw.validation_summary);l.template_list('AW_UL_validation','',c.scene.aw,'validation',c.scene.aw,'validation_index',rows=5);l.label(text='Instances share meshes; textures are packed.')
class AW_PT_io(AW_Section,bpy.types.Panel):
    bl_label='Import & Export';bl_idname='AW_PT_io'
    def draw(self,c):
        l=self.layout;l.operator('aw.import_model',icon='IMPORT');l.operator('aw.export',icon='EXPORT');l.label(text='exports/AlejandroWorld.glb');l.label(text='Drive: run Start Driving.command')
CLASSES=[AW_PT_main,AW_PT_quick,AW_PT_assets,AW_PT_transform,AW_PT_placement,AW_PT_roads,AW_PT_scatter,AW_PT_materials,AW_PT_physics,AW_PT_metadata,AW_PT_animation,AW_UL_validation,AW_PT_validation,AW_PT_io]
