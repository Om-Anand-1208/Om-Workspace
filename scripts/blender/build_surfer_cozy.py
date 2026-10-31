"""Build the web SurferFlow diorama from the editable starter scene.
Run: blender -b blender/SurferFlow-portfolio-diorama.blend -t 4 --python scripts/blender/build_surfer_cozy.py
"""
import bpy, math, random, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')); random.seed(14)
# Remove the old generic ribbon and its dot-like foam; retain the original rider.
for o in list(bpy.context.scene.objects):
    if o.name.startswith(('Wave_Main','Wave_Flow','Foam_Crest','Foam_Foot','Ocean_Ripple','Small_Sand','Rounded_Coastal','Succulent_','Coastal_Foam')):
        bpy.data.objects.remove(o,do_unlink=True)
def material(name,c,rough=.7):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; return m
sand=material('Honey sand',(.75,.57,.37)); sandlight=material('Wet sand',(.88,.72,.52)); darkwater=material('Deep lagoon',(.045,.37,.39),.36); wave=material('Wave turquoise',(.10,.61,.57),.3); wavelight=material('Foam milk',(.86,.96,.88),.47); pale=material('Translucent crest',(.33,.78,.70),.38); leaf=material('Sea oats green',(.29,.46,.25)); sage=material('Coast foliage',(.32,.50,.32)); stem=material('Sand grass',(.64,.53,.29)); bark=material('Pine bark',(.29,.21,.15)); pine=material('Pine needles',(.14,.31,.25)); white=material('Board ivory',(.95,.88,.74))
def sphere(name, loc, scale, m, seg=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=12, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
def line(name, pts, r, m):
    c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=12; c.bevel_depth=r; c.bevel_resolution=3; sp=c.splines.new('BEZIER'); sp.bezier_points.add(len(pts)-1)
    for b,p in zip(sp.bezier_points,pts): b.co=p; b.handle_left_type='AUTO'; b.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); c.materials.append(m); return o
def cyl(name, loc, radius, depth, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=radius,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(mat); return o
# Adjust palette of original water and frame for depth.
for o in bpy.context.scene.objects:
    if o.name=='Ocean_Surface': o.data.materials.clear(); o.data.materials.append(darkwater)
# A long, gently meandering bank of sand behind the surf.
verts=[]
for i in range(13):
    x=-1.88+i*3.76/12; shore=.99+.10*math.sin(i*.7)
    verts.extend([(x,shore,.375),(x,1.79,.375)])
faces=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(12)]
mesh=bpy.data.meshes.new('Sand bank mesh'); mesh.from_pydata(verts,[],faces); mesh.materials.append(sand); o=bpy.data.objects.new('Meandering sandy coastline',mesh); bpy.context.collection.objects.link(o)
solid=o.modifiers.new('Soft bank','SOLIDIFY'); solid.thickness=.07
bev=o.modifiers.new('Rounded shore','BEVEL'); bev.width=.05; bev.segments=3
# Long soft swash edge emphasizes shore without rows of dots.
shoreline=[(-1.85+i*.25,.985+.1*math.sin(i*.7),.405) for i in range(16)]
line('Shore wash',shoreline,.035,wavelight)
line('Shallow water',[(x,y-.11,z-.008) for x,y,z in shoreline],.018,pale)
# Low, soft ripples and a V-shaped wake mark the surfer's movement.
line('Wake left',[(-1.06,-.79,.405),(-1.20,-.63,.408),(-1.46,-.54,.407)],.018,wavelight)
line('Wake right',[(-1.05,-.88,.405),(-1.20,-1.04,.408),(-1.43,-1.19,.407)],.018,wavelight)
for i in range(12):
    x=random.uniform(-1.48,-.95); y=random.uniform(-1.2,-.52); sphere('Wake fleck',(x,y,.412),(.033,.018,.009),wavelight,12)
# A few low curving ripple strokes across open water.
for i in range(4):
    x=.15+i*.36; y=-.6+(i%2)*.4
    line('Ocean ripple',[(x-.16,y,.405),(x,y-.025,.407),(x+.18,y,.405)],.012,pale)
# Make the rider the hero without losing its actual outfit details.
origin=Vector((-.68,-.81,.43)); scale=1.33
for o in bpy.context.scene.objects:
    if o.name.startswith(('Surfer_','Surfboard_')):
        o.location=origin+(o.location-origin)*scale; o.scale*=scale
# Coastal pines and scrub echo the real game's vegetation.
for x,y,h in [(-1.63,1.55,.88),(1.54,1.55,.68)]:
    cyl('Pine trunk',(x,y,.4+h*.32),.045,h*.65,bark)
    for k in range(3):
        bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.24-k*.035,radius2=.03,depth=.38,location=(x,y,.4+h*.43+k*.17)); o=bpy.context.object; o.name='Coastal pine'; o.data.materials.append(pine)
for i in range(7):
    x=-1.7+i*.54; y=1.32+random.random()*.29
    for j in range(3):
        ang=random.random()*math.tau; h=.20+random.random()*.18; tip=(x+math.cos(ang)*.10,y+math.sin(ang)*.1,.4+h)
        line('Sea oats',[(x,y,.4),(x+math.cos(ang)*.05,y+math.sin(ang)*.05,.4+h*.6),tip],.008,stem)
        sphere('Seed head',tip,(.018,.018,.055),stem,12)
for x,y in [(-1.18,1.54),(.45,1.48),(1.16,1.36)]:
    for j in range(5):
        a=j*math.tau/5; o=sphere('Dune scrub',(x+math.cos(a)*.08,y+math.sin(a)*.08,.49),(.05,.045,.13),sage,12); o.rotation_euler[1]=math.cos(a)*.6
# Weathered stones and a piece of driftwood give the quiet beach some texture.
rock=material('Warm coastal stone',(.47,.43,.37)); drift=material('Driftwood',(.48,.33,.21))
for i,(x,y,sz) in enumerate([(-1.22,1.53,.10),(-1.04,1.60,.07),(.11,1.47,.07),(1.08,1.62,.11)]):
    sphere('Beach stone',(x,y,.43),(sz*1.3,sz,.055),rock,16)
line('Driftwood branch',[(.60,1.50,.44),(.75,1.55,.46),(.88,1.54,.44)],.035,drift)
line('Driftwood twig',[(.75,1.55,.46),(.78,1.64,.49)],.014,drift)
# Small shoreline details remain visible from every side, without inventing a wave.
foam_sand=material('Shell ivory',(.91,.81,.65))
for x,y in [(-1.47,1.27),(-.64,1.59),(.30,1.67),(.96,1.23),(1.35,1.56)]:
    for j in range(5):
        a=j*math.tau/5; h=.12+(j%3)*.035
        line('Dune grass blade',[(x,y,.42),(x+math.cos(a)*.04,y+math.sin(a)*.04,.42+h*.6),(x+math.cos(a)*.10,y+math.sin(a)*.10,.42+h)],.006,leaf)
for x,y in [(-.85,1.28),(-.18,1.60),(.86,1.35)]:
    shell=sphere('Beach shell',(x,y,.413),(.075,.045,.014),foam_sand,16); shell.rotation_euler[2]=x
for i in range(6):
    x=-.35+i*.28; y=-1.24+(i%2)*.09
    line('Small surface glint',[(x-.06,y,.405),(x,y-.012,.408),(x+.08,y,.405)],.006,pale)
# Small footprints in the shoreline give the coastal scene a sense of life.
for i in range(5):
    x=-.72+i*.18; y=1.49+(i%2)*.09
    sphere('Sandy footprint',(x,y,.416),(.045,.024,.003),sandlight,12)
# Export same geometry seen in render; exclude photo backdrop.
ground=bpy.data.objects.get('Peach_Studio_Ground')
if ground: ground.hide_render=True
objs=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE'} and not o.hide_render]
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.export_scene.gltf(filepath=os.path.join(root,'public/projects/SurferFlow.glb'),export_format='GLB',use_selection=True)
bpy.ops.object.camera_add(location=(6,-8,6)); cam=bpy.context.object; cam.rotation_euler=(Vector((0,0,.7))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=6.1; bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(0,-3,7)); l=bpy.context.object; l.data.energy=650; l.data.size=7
scene=bpy.context.scene; scene.use_nodes=False; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.world.use_nodes=True; next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.045,.045,.045,1); scene.view_settings.exposure=-.5; scene.render.resolution_x=720; scene.render.resolution_y=540; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(root,'public/projects/SurferFlow.png'); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'blender/SurferFlow-cozy.blend'))
