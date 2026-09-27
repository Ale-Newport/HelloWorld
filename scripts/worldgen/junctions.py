"""Finish crossing ribbons without coplanar surfaces or paint through junctions."""
import bpy
from mathutils import Vector
from alejandro_world.roads import sample,regenerate

def finish_junctions():
    north=bpy.data.objects.get('North / garden drive')
    if north:
        p=north.data.splines[0].bezier_points[0]
        p.co.x=-140;p.co.y=27
    # Small explicit layers avoid z-fighting at intersecting authored curves.
    # Store the offset on the guide, so rebuilding the road remains predictable.
    guides=sorted((o for o in bpy.context.scene.objects if o.get('aw_road')),key=lambda o:o.name)
    for i,curve in enumerate(guides):
        target=.045+i*.008
        if not curve.get('junctions_finished'):
            delta=target-curve.data.splines[0].bezier_points[0].co.z
            for spline in curve.data.splines:
                for point in spline.bezier_points:point.co.z+=delta
            curve['junctions_finished']=True
        regenerate(curve)
    paths={c.name:sample(c,24) for c in guides}
    def covered(point,owner):
        for curve in guides:
            if curve.name==owner:continue
            radius=curve['road_width']/2-.12
            for a,b in zip(paths[curve.name],paths[curve.name][1:]):
                d=b-a;d.z=0
                q=point-a;q.z=0
                t=max(0,min(1,q.dot(d)/max(d.length_squared,1e-8)))
                if (q-d*t).length<radius:return True
        return False
    import bmesh
    for obj in list(bpy.context.scene.objects):
        owner=obj.get('road_owner')
        curb=obj.name.startswith('Barcelona curb')
        if obj.type!='MESH' or not (curb or (owner and ' / edge ' in obj.name)):continue
        if curb:owner='Barcelona / Bezier circuit'
        bm=bmesh.new();bm.from_mesh(obj.data)
        remove=[f for f in bm.faces if covered(f.calc_center_median(),owner)]
        bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(obj.data);bm.free()
    for obj in bpy.data.objects:
        if obj.name.startswith('Road junction'):
            obj.location.z=.12
            asphalt=bpy.data.materials.get('black')
            if asphalt:obj.data.materials.clear();obj.data.materials.append(asphalt)
