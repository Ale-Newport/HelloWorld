import bpy,math
from .core import CATEGORIES
from .assets import asset_items
class AW_ValidationItem(bpy.types.PropertyGroup):
    level:bpy.props.StringProperty();object_name:bpy.props.StringProperty();message:bpy.props.StringProperty()
class AW_Settings(bpy.types.PropertyGroup):
    ground_snap:bpy.props.BoolProperty(name='Ground Snap',default=False,description='Automatically settle moved selections on marked surfaces')
    align_surface:bpy.props.BoolProperty(name='Align to surface',default=False)
    grid_snap:bpy.props.BoolProperty(name='Grid Snap',default=False)
    rotation_snap:bpy.props.BoolProperty(name='Rotation Snap',default=False)
    ground_offset:bpy.props.FloatProperty(name='Ground offset',default=.01,unit='LENGTH',min=-10,max=10)
    grid_size:bpy.props.FloatProperty(name='Grid size',default=.25,min=.01,unit='LENGTH')
    rotation_increment:bpy.props.FloatProperty(name='Rotation increment',default=math.radians(15),min=.01,subtype='ANGLE')
    alignment_strength:bpy.props.FloatProperty(name='Alignment strength',default=1,min=0,max=1)
    category:bpy.props.EnumProperty(name='Category',items=[('ALL','All categories','')]+[(x,x,'') for x in CATEGORIES])
    asset:bpy.props.EnumProperty(name='Asset',items=asset_items)
    seed:bpy.props.IntProperty(name='Seed',default=42,min=0)
    scatter_count:bpy.props.IntProperty(name='Density / count',default=15,min=1,max=2000)
    scatter_radius:bpy.props.FloatProperty(name='Area radius',default=12,min=.5,unit='LENGTH')
    min_distance:bpy.props.FloatProperty(name='Minimum distance',default=2,min=.05,unit='LENGTH')
    random_rotation:bpy.props.BoolProperty(name='Random rotation',default=True)
    scale_min:bpy.props.FloatProperty(name='Min scale',default=.8,min=.01)
    scale_max:bpy.props.FloatProperty(name='Max scale',default=1.2,min=.01)
    scatter_mode:bpy.props.EnumProperty(name='Mode',items=[('RANDOM','Random area',''),('AREA','Area grid',''),('CURVE','Along selected curve',''),('LINE','Line','')])
    texture_metres:bpy.props.FloatProperty(name='Metres per tile',default=2,min=.01)
    material_name:bpy.props.StringProperty(name='Replace with')
    validation:bpy.props.CollectionProperty(type=AW_ValidationItem)
    validation_summary:bpy.props.StringProperty(default='Not yet checked')
    validation_index:bpy.props.IntProperty(default=0)
CLASSES=[AW_ValidationItem,AW_Settings]
