import bpy, math, random, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..'))
random.seed(9)
def mat(name,color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); n.inputs['Base Color'].default_value=(*color,1); n.inputs['Roughness'].default_value=.78; return m
sand=mat('Warm shore sand',(.68,.52,.34)); grass=mat('Dune grass',(.35,.49,.27)); seed=mat('Sea oat seedheads',(.70,.56,.33)); foam=mat('Shoreline foam',(.92,.96,.84))
def ball(name,loc,scale,ma):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(ma); bpy.ops.object.shade_smooth(); return o
def line(name, pts, radius, ma):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=8; c.bevel_depth=radius; c.bevel_resolution=2; s=c.splines.new('BEZIER'); s.bezier_points.add(len(pts)-1)
    for p,co in zip(s.bezier_points,pts): p.co=co; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(ma); return o
# Expand the existing small corner of shore, retaining the rider and wave.
ball('Dune shore',(-1.43,1.23,.36),(.53,.37,.09),sand)
for i in range(4):
    x=-1.7+i*.13; y=1.32 + (i%2)*.14
    for j in range(4):
        a=j*math.pi/2+i*.5; h=.25+random.random()*.22
        tip=(x+math.cos(a)*.12,y+math.sin(a)*.12,.44+h)
        line('Sea oat stem',[(x,y,.43),(x+math.cos(a)*.04,y+math.sin(a)*.04,.44+h*.55),tip],.009,grass)
        ball('Oat seed',tip,(.025,.025,.07),seed)
for i in range(7): ball('Shore foam',(-1.86+i*.12, .99+math.sin(i*.7)*.035,.40),(.07,.035,.012),foam)
# Export only the scene, never the large photography background.
objs=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'} and o.name!='Peach_Studio_Ground' and not o.hide_render]
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.gltf(filepath=os.path.join(root,'public/projects/SurferFlow.glb'),export_format='GLB',use_selection=True)
# Remove the oversized studio plane from the catalogue render.
ground=bpy.data.objects.get('Peach_Studio_Ground')
if ground: ground.hide_render=True
bpy.context.scene.use_nodes=False
# A purpose-built camera frames the same object as the web model.
bpy.ops.object.camera_add(location=(6,-8,6)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=5.8; bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(0,-3,7)); l=bpy.context.object; l.data.energy=650; l.data.size=7
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=24; scene.world.color=(.04,.05,.05); scene.world.use_nodes=True; next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.045,.045,.045,1); scene.view_settings.exposure=-0.5; scene.render.resolution_x=600; scene.render.resolution_y=450; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(root,'public/projects/SurferFlow.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'blender/SurferFlow-coastal-portfolio.blend'))
