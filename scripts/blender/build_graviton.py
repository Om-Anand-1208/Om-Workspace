"""Build Graviton's portfolio scene: blender -b -t 4 --python scripts/blender/build_graviton.py"""
import bpy, math, random, os
from mathutils import Vector
root=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')); random.seed(35)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c,emission=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.65
 if emission: p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m
base=mat('Deep space',(.035,.045,.075)); trim=mat('Frame',(.09,.105,.14)); gold=mat('Golden spiral',(.95,.42,.03),.55); purple=mat('Accretion ring',(.38,.10,.66),.35); hole=mat('Event horizon',(.006,.006,.014)); rock=mat('Asteroids',(.25,.27,.31)); ship=mat('Cyan spacecraft',(.06,.72,.82),.15); white=mat('Starlight',(.9,.95,1),.4)
def box(n,loc,scale,m,b=.08):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);mod=o.modifiers.new('Rounded edge','BEVEL');mod.width=b;mod.segments=3;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);return o
def line(n,pts,r,m):
 c=bpy.data.curves.new(n,'CURVE');c.dimensions='3D';c.resolution_u=2;c.bevel_depth=r;c.bevel_resolution=3;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 o=bpy.data.objects.new(n,c);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def sphere(n,loc,scale,m):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=loc);o=bpy.context.object;o.name=n;o.scale=scale;o.data.materials.append(m);return o
box('Base',(0,0,0),(4,4,.30),trim,.12);box('Night sky',(0,0,.19),(3.86,3.86,.10),base,.06)
# Archimedean spiral, a distinct visual motif of the actual game.
pts=[]
for i in range(280):
 t=i/279*math.pi*4.8;r=.20+1.52*i/279;pts.append((r*math.cos(t),r*math.sin(t),.27))
line('Orbital spiral',pts,.018,gold)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.25,depth=.09,location=(0,0,.29));bpy.context.object.name='Black hole';bpy.context.object.data.materials.append(hole)
for radius in [.31,.40]:
 line('Accretion ring',[(radius*math.cos(i*math.tau/100),radius*math.sin(i*math.tau/100),.30) for i in range(101)],.013,purple)
for i in range(6):
 a=i*math.tau/6+.45; r=1.22+(i%2)*.19; o=sphere('Asteroid',(r*math.cos(a),r*math.sin(a),.35),(.15,.10,.10),rock);o.rotation_euler=(random.random(),random.random(),random.random())
for i in range(52):
 x=random.uniform(-1.78,1.78);y=random.uniform(-1.78,1.78)
 if x*x+y*y>.35:sphere('Star',(x,y,.26),(.015,.015,.01),white)
# Arrow-shaped ship matching the game art.
mesh=bpy.data.meshes.new('Ship mesh');mesh.from_pydata([(-.25,-.21,0),(.25,-.21,0),(0,.39,0),(-.11,-.12,.12),(.11,-.12,.12),(0,.27,.12)],[],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)]);mesh.materials.append(ship);o=bpy.data.objects.new('Spacecraft',mesh);bpy.context.collection.objects.link(o);o.location=(-.95,-.70,.40);o.rotation_euler[2]=-.5
for i in range(5):sphere('Ship trail',(-1.04-i*.07,-.98-i*.055,.30),(.035-i*.004,.035-i*.004,.015),white)
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=os.path.join(root,'public/projects/Graviton.glb'),export_format='GLB')
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(6,-8,6));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.4;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='AREA',location=(0,-3,7));bpy.context.object.data.energy=600;bpy.context.object.data.size=6
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world.use_nodes=True;next(n for n in scene.world.node_tree.nodes if n.type=='BACKGROUND').inputs['Color'].default_value=(.045,.045,.045,1);scene.render.resolution_x=720;scene.render.resolution_y=540;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(root,'public/projects/Graviton.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'blender/Graviton-portfolio.blend'))
