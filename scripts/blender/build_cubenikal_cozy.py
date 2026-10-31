"""Cubenikal diorama: 5x5 steel arrow puzzle on a cozy wood workbench.
Reference: Om-Anand-1208/Cubenikal README and game.js (steel blocks, directional arrows,
sliding into gaps, clear-path escape; initial size 5x5x5). Run with Blender -b -t 2 --python.
"""
import bpy, math, os, random
from mathutils import Vector
random.seed(4)
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'../..')); OUT=os.path.join(ROOT,'public/projects')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,c,metal=0,rough=.55):
 m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True; p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough; return m
wood=mat('walnut stained wood',(.27,.135,.075)); wood_light=mat('warm wood edge',(.46,.27,.14)); grain=mat('wood inlay',(.62,.40,.22)); steel=mat('soft brushed steel',(.51,.56,.57),.6,.35); steel_hi=mat('steel edge',(.67,.71,.68),.45,.32); ink=mat('arrow charcoal',(.075,.11,.12)); brass=mat('aged brass',(.64,.41,.17),.55,.35); cream=mat('paper cream',(.86,.79,.63)); tea=mat('tea',(.31,.13,.055)); mug=mat('ceramic jade',(.35,.52,.44)); dark=mat('base dark',(.105,.12,.105)); light=mat('lamp warm',(.92,.67,.32)); leaf=mat('plant green',(.22,.39,.25))
def cube(name,loc,dims,m,bevel=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('rounded edge','BEVEL'); mod.width=bevel; mod.segments=3; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
  mod=o.modifiers.new('weighted normals','WEIGHTED_NORMAL'); bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(name,loc,r,depth,m,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m); b=o.modifiers.new('edge','BEVEL');b.width=.018;b.segments=3; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=b.name); return o
def torus(name,loc,r,minor,m,rotation=(0,0,0)):
 bpy.ops.mesh.primitive_torus_add(major_segments=32,minor_segments=8,location=loc,major_radius=r,minor_radius=minor,rotation=rotation);o=bpy.context.object;o.name=name;o.data.materials.append(m);return o
def rod(name,a,b,r,m):
 v=Vector(b)-Vector(a);o=cyl(name,(Vector(a)+Vector(b))/2,r,v.length,m,16);o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o
# Framed desk, inlaid corners and subtle planking.
cube('base',(0,0,.02),(4.15,3.7,.27),dark,.12);cube('walnut tabletop',(0,0,.18),(4.04,3.59,.12),wood,.07)
for y in [-1.19,0,1.19]: cube('plank seam',(0,y,.245),(3.88,.012,.008),wood_light,.003)
for x in [-1.88,1.88]: cube('end grain trim',(x,0,.25),(.055,3.42,.016),grain,.008)
# Display stand and padding: a familiar 5x5x5 steel cube, not a Rubik cube.
cube('mat',(0,.16,.30),(2.72,2.66,.12),dark,.09);cube('brass rim',(0,.16,.365),(2.61,2.55,.035),brass,.025);cube('velvet tray',(0,.16,.39),(2.51,2.45,.04),dark,.02)
step=.395; size=.377; centerz=1.42
for x in range(5):
 for y in range(5):
  for z in range(5):
   # One visible empty spot tells the sliding/removal story.
   if (x,y,z)==(0,0,4): continue
   p=((x-2)*step,(y-2)*step+.16,centerz+(z-2)*step)
   cube('steel puzzle block',p,(size,size,size),steel,.021)
# Directional arrows: triangles and stems embedded on exposed faces. Alternate directions.
verts=[];faces=[]
def arrow(center,normal,u,v,sign):
 c=Vector(center); U=Vector(u)*sign; V=Vector(v)
 # A single tapered arrow silhouette, 2D coordinates inside each block face.
 pts=[(-.105,-.023),(.025,-.023),(.025,-.060),(.108,0),(.025,.060),(.025,.023),(-.105,.023)]
 start=len(verts)
 for a,b in pts: verts.append(c+U*a+V*b+Vector(normal)*.003)
 faces.append(tuple(range(start,start+len(pts))))
for i in range(5):
 for j in range(5):
  # top face and both camera-facing vertical faces
  if (i,j)!=(0,0): arrow(((i-2)*step,(j-2)*step+.16,centerz+2*step+size/2),(0,0,1),(1,0,0),(0,1,0),1 if (i+j)%2 else -1)
  arrow(((i-2)*step,.16-2*step-size/2,centerz+(j-2)*step),(0,-1,0),(1,0,0),(0,0,1),1 if (i+j)%3 else -1)
  arrow((2*step+size/2,.16+(i-2)*step,centerz+(j-2)*step),(1,0,0),(0,1,0),(0,0,1),1 if (i+j)%2 else -1)
mesh=bpy.data.meshes.new('arrow engraving');mesh.from_pydata(verts,[],faces);mesh.update();ob=bpy.data.objects.new('directional arrows',mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(ink)
# A freed block resting next to the puzzle, and warm tabletop details.
cube('released block',(-1.51,-.87,.47),(.34,.34,.34),steel_hi,.025)
torus('cup saucer',(1.51,-1.00,.265),.25,.027,cream);cyl('cup',(1.51,-1,.38),.20,.24,mug);cyl('tea surface',(1.51,-1,.507),.16,.009,tea);torus('cup handle',(1.72,-1,.40),.115,.034,mug,(math.pi/2,0,0))
# Pinned notes, small pen, the cues of a quiet puzzle session.
paper=cube('puzzle note',(-1.45,.99,.277),(.65,.53,.026),cream,.025);paper.rotation_euler[2]=-.12
for i in range(3):
 line=cube('pencil note mark',(-1.47,.87+i*.1,.296),(.34,.014,.007),wood_light,.004);line.rotation_euler[2]=-.12
rod('pencil',(-1.77,.55,.30),(-1.13,.48,.30),.025,brass)
# Small warm desk lamp positioned behind the puzzle.
cyl('lamp foot',(1.53,1.19,.28),.24,.08,brass);rod('lamp upright',(1.53,1.19,.31),(1.53,1.19,1.15),.04,brass);rod('lamp neck',(1.53,1.19,1.15),(1.29,1.11,1.42),.036,brass)
bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.30,radius2=.12,depth=.27,location=(1.27,1.11,1.45));bpy.context.object.name='lamp shade';bpy.context.object.data.materials.append(mug)
cyl('lamp bulb',(1.27,1.11,1.30),.12,.05,light)
# Merge repeated static steel blocks to reduce web draw calls.
bpy.ops.object.select_all(action='DESELECT')
blocks=[o for o in bpy.context.scene.objects if o.name.startswith('steel puzzle block')]
for obj in blocks: obj.select_set(True)
bpy.context.view_layer.objects.active=blocks[0]; bpy.ops.object.join(); blocks[0].name='steel puzzle blocks'
# Export only geometry; keep camera and lights out of GLB.
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'Cubenikal.glb'),export_format='GLB',use_selection=True)
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.camera_add(location=(7,-9,7));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.10))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.0;bpy.context.scene.camera=cam
# Warm physically lit thumbnail.
def area(loc,power,size,color):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
area((1,-4,7),600,5,(1,.81,.61));area((-4,0,5),400,5,(.72,.84,1));area((2,4,5),480,4,(1,.85,.68))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.world.color=(.17,.17,.17);s.render.resolution_x=720;s.render.resolution_y=540;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(OUT,'Cubenikal.png');s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender/Cubenikal-portfolio-diorama.blend'));bpy.ops.render.render(write_still=True)
