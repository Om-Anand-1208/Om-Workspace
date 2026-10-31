import bpy, math, os
from mathutils import Vector
ROOT='/home/psykr/Projects/Om-Portfolio'; OUT=ROOT+'/public/projects/Guess-Whose-Song'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def material(name, col, rough=.7, metallic=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*col,1); m.use_nodes=True; bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic; return m
wood=material('warm walnut',(.30,.16,.095)); wood2=material('honey wood',(.57,.34,.19)); woodlight=material('edge inlay',(.79,.55,.29)); floor=material('stage floor',(.70,.50,.34)); dark=material('ink',(.055,.045,.07)); cream=material('ivory',(.97,.89,.73)); yellow=material('gold',(.99,.65,.19)); orange=material('singer orange',(1,.32,.045)); lavender=material('guitar lavender',(.62,.44,.87)); lime=material('drummer lime',(.61,.82,.18)); aqua=material('keyboard teal',(.06,.72,.65)); pink=material('guitar pink',(.96,.16,.41)); violet=material('headphones violet',(.37,.18,.68)); white=material('sneakers',(.96,.94,.87)); coral=material('rug',(.63,.30,.25)); muted=material('sage',(.27,.43,.34))
def box(name, loc, size, mat, bevel=.05):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object;o.name=name;o.dimensions=size; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  m=o.modifiers.new('rounded edges','BEVEL');m.width=bevel;m.segments=3; bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=m.name)
  o.modifiers.new('weighted normals','WEIGHTED_NORMAL')
 return o
def ball(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);bpy.ops.object.shade_smooth();return o
def cyl(name,loc,r,depth,mat,axis='z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 if axis=='y':o.rotation_euler[0]=math.pi/2
 bevel=o.modifiers.new('edge','BEVEL');bevel.width=.015;bevel.segments=2;o.modifiers.new('normals','WEIGHTED_NORMAL');return o
def rod(name,a,b,r,mat):
 a,b=Vector(a),Vector(b); v=b-a;o=cyl(name,(a+b)/2,r,v.length,mat);o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o
def triangle(name,cx,cy,base,width,height,depth,mat):
 verts=[(cx-width/2,cy-depth/2,base),(cx+width/2,cy-depth/2,base),(cx,cy-depth/2,base+height),(cx-width/2,cy+depth/2,base),(cx+width/2,cy+depth/2,base),(cx,cy+depth/2,base+height)]
 faces=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);m=o.modifiers.new('soft edges','BEVEL');m.width=.07;m.segments=3;o.modifiers.new('normals','WEIGHTED_NORMAL');return o
# stage has rounded timber fascia, fine inlaid trim, planks and rug
box('floating wooden stage',(0,0,.10),(4.15,3.35,.26),wood,.10);box('gold stage edge',(0,0,.24),(4.06,3.26,.05),woodlight,.04);box('stage boards',(0,0,.32),(3.95,3.15,.13),floor,.06)
for x in [-1.45,-.88,-.31,.26,.83,1.40]: box('board seam',(x,0,.394),(.012,3.0,.006),wood2,.001)
box('soft woven rug',(0,-.35,.414),(3.45,1.55,.04),coral,.14)
for x in [-1.50,1.50]:
 box('amp cabinet',(x,.95,.8),(.55,.38,.72),wood,.06);box('speaker grille',(x,.742,.8),(.46,.02,.58),dark,.02)
 for z in [.67,.91]:cyl('speaker cone',(x,.725,z),.14,.018,wood2,'y');cyl('speaker dust cap',(x,.711,z),.055,.02,dark,'y')
 for i in [-.14,.14]:cyl('amp knob',(x+i,.715,1.12),.023,.02,yellow,'y')
# timber supports make the light string part of the stage rather than floating.
for x in [-1.65, 1.65]:
 rod('light support', (x, 1.3, .43), (x, 1.3, 1.9), .035, wood)
 ball('support finial', (x, 1.3, 1.92), (.065,.065,.065), woodlight)
# tiny string lights across back
for x in [-1.5,-.9,-.3,.3,.9,1.5]:
 rod('string cord',(x,1.32,1.85),(x+.6,1.32,1.85),.008,dark);ball('fairy light',(x,1.32,1.81),(.045,.045,.05),yellow)
# human-like limbs and face anchored to each geometric character
def character_legs(cx,cy,base):
 for s in [-1,1]:
  rod('leg',(cx+s*.15,cy,base+.15),(cx+s*.20,cy-.04,base-.14),.035,dark)
  ball('sneaker',(cx+s*.20,cy-.10,base-.16),(.15,.20,.07),white)
def face(cx,cy,z,spacing=.15):
 for s in [-1,1]: ball('eye',(cx+s*spacing,cy,z),(.048,.026,.085),dark)
 ball('smile',(cx,cy-.008,z-.19),(.13,.032,.07),dark);ball('tongue',(cx,cy-.043,z-.22),(.055,.012,.025),pink)
def arm(a,b):rod('arm',a,b,.035,dark);ball('hand',b,(.07,.055,.07),dark)
# central orange singer: round shape with purple headphones
x=-.25;y=-.05; character_legs(x,y,.78);ball('orange singer',(x,y,1.23),(.48,.19,.48),orange);face(x,y-.19,1.32,.15)
for s in [-1,1]:
 ball('ear cup',(x+s*.46,y,1.29),(.12,.23,.20),violet)
rod('headphone band left',(x-.46,y,1.42),(x-.36,y,1.69),.045,violet);rod('headphone band top',(x-.36,y,1.69),(x+.36,y,1.69),.045,violet);rod('headphone band right',(x+.36,y,1.69),(x+.46,y,1.42),.045,violet)
arm((x-.43,y,1.17),(x-.65,y-.05,1.38));arm((x+.43,y,1.17),(x+.62,y-.08,1.40))
rod('microphone handle',(x+.62,y-.11,1.32),(x+.72,y-.17,1.49),.043,dark);ball('microphone grille',(x+.73,y-.18,1.52),(.075,.075,.09),woodlight)
# purple triangle guitarist
x=-1.25;y=.10;character_legs(x,y,.79);triangle('lavender guitarist',x,y,.79,.88,.94,.27,lavender);face(x,y-.15,1.30,.13)
arm((x-.39,y,1.08),(x-.26,y-.23,1.03));arm((x+.39,y,1.08),(x+.48,y-.23,1.22))
ball('guitar body',(x+.08,y-.26,1.04),(.26,.07,.24),pink);ball('guitar pickguard',(x+.08,y-.335,1.06),(.14,.015,.12),cream);rod('guitar neck',(x+.18,y-.28,1.12),(x+.51,y-.28,1.40),.065,wood);ball('guitar head',(x+.53,y-.28,1.42),(.11,.05,.08),pink)
# green square drummer behind compact drum
x=.75;y=.32;character_legs(x,y,.84);box('green drummer',(x,y,1.26),(.72,.28,.82),lime,.10);face(x,y-.15,1.37,.14)
arm((x-.35,y,1.12),(x-.24,y-.29,1.00));arm((x+.35,y,1.12),(x+.30,y-.30,1.10))
cyl('drum shell',(x,y-.40,.86),.29,.32,yellow);cyl('drum top',(x,y-.40,1.03),.30,.04,cream);cyl('drum bottom rim',(x,y-.40,.70),.30,.03,dark)
for s in [-1,1]:rod('drumstick',(x+s*.24,y-.28,1.11),(x+s*.08,y-.43,1.04),.018,wood)
# blue diamond keyboardist
x=1.5;y=-.03;character_legs(x,y,.79);o=box('teal keyboardist',(x,y,1.29),(.72,.25,.72),aqua,.1);o.rotation_euler[1]=math.pi/4;face(x,y-.15,1.32,.13)
arm((x-.36,y,1.12),(x-.20,y-.30,1.04));arm((x+.36,y,1.12),(x+.28,y-.30,1.04))
box('keytar body',(x,y-.33,.98),(.74,.12,.22),yellow,.04);box('keyboard panel',(x,y-.405,.98),(.58,.015,.15),white,.008)
for i in range(7):box('black key',(x-.23+i*.075,y-.418,1.015),(.025,.02,.08),dark,.003)
rod('keytar neck',(x+.34,y-.33,1.02),(x+.53,y-.33,1.18),.052,yellow)
# stage microphone / small cables
rod('mic stand',(-.1,-.94,.43),(-.1,-.94,1.10),.025,dark);rod('mic boom',(-.1,-.94,1.10),(.15,-.94,1.30),.025,dark);ball('mic',(.18,-.94,1.31),(.08,.05,.05),dark)
# Performance details: instrument strings, cymbal and grounded signal cables.
# The guitar strings sit on the front face and follow the full neck.
for offset in [-.033, 0, .033]:
 rod('guitar string',(-1.25+.04+offset,-.251,1.04),(-1.25+.51+offset,-.251,1.40),.004,cream)
# A delicate guitar strap continues behind the character, so the silhouette
# remains readable as visitors rotate the scene.
rod('guitar strap front',(-1.56,-.075,1.29),(-1.32,-.19,1.03),.016,wood2)
rod('guitar strap back',(-1.56,.23,1.29),(-1.08,.21,1.02),.016,wood2)
# Cymbal stand and drum tension details, derived from the drummer's instrument.
cyl('cymbal',(.31,.55,1.27),.18,.025,woodlight)
rod('cymbal stand',(.31,.55,.43),(.31,.55,1.29),.018,dark)
for i in range(8):
 a=i*math.tau/8
 rod('drum lug',(.75+.275*math.cos(a),-.08+.275*math.sin(a),.72),(.75+.275*math.cos(a),-.08+.275*math.sin(a),.99),.008,woodlight)
# Ground the microphone and plug the stage equipment into the amplifiers.
cyl('mic stand base',(-.1,-.94,.45),.17,.025,dark)
def cable(name,points,radius=.014):
 c=bpy.data.curves.new(name,'CURVE'); c.dimensions='3D'; c.resolution_u=16; c.bevel_depth=radius; c.bevel_resolution=3
 s=c.splines.new('BEZIER'); s.bezier_points.add(len(points)-1)
 for p,pt in zip(s.bezier_points,points): p.co=pt; p.handle_left_type='AUTO'; p.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,c);bpy.context.collection.objects.link(o);o.data.materials.append(dark)
 return o
cable('guitar cable',[(-1.14,-.15,.86),(-1.12,-.25,.45),(-1.45,-.47,.45),(-1.71,-.05,.45),(-1.5,.74,.47)])
cable('keyboard cable',[(1.54,-.15,.83),(1.55,-.18,.45),(1.78,-.42,.45),(1.84,.40,.45),(1.5,.73,.47)])
cable('microphone cable',[(-.1,-.94,.46),(.05,-1.10,.45),(.5,-1.15,.45),(.95,-.9,.45),(1.74,-.52,.45)])
# Tiny floor fasteners and brass stage corners add detail without clutter.
for x in [-1.83,1.83]:
 for y in [-1.39,1.39]:
  cyl('stage fastener',(x,y,.401),.024,.008,woodlight)
# export mesh only
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=OUT+'.glb',export_format='GLB',use_selection=True)
# camera sees performers from front and right, matching site orientation
bpy.ops.object.select_all(action='DESELECT');bpy.ops.object.camera_add(location=(6,-9,6.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1.02))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.7;bpy.context.scene.camera=cam
world=bpy.context.scene.world;world.color=(.08,.10,.09)
def area(loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
area((1,-5,8),650,6);area((-5,-1,5),400,5);area((2,5,6),500,4)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True;sc.render.resolution_x=900;sc.render.resolution_y=675;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False;sc.render.filepath=OUT+'.png';sc.view_settings.view_transform='Standard';bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/blender/Guess-Whose-Song-cozy.blend');bpy.ops.render.render(write_still=True)
