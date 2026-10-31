"""Create lightweight, editable project illustrations for Om's portfolio."""
import bpy, math, os
from mathutils import Vector
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
OUT = os.path.join(ROOT, 'public/projects')

def material(name, color):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    principled = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    principled.inputs['Base Color'].default_value = (*color, 1)
    principled.inputs['Roughness'].default_value = .8
    return mat

def box(name, loc, size, mat, bevel=.05):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object; ob.name=name; ob.scale=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    if bevel:
        mod=ob.modifiers.new('Rounded edges','BEVEL'); mod.width=min(bevel, min(size)*.4); mod.segments=3
        bpy.context.view_layer.objects.active=ob; bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def cylinder(name, loc, radius, depth, mat, vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    ob=bpy.context.object; ob.name=name; ob.data.materials.append(mat)
    return ob

def ellipsoid(name, loc, scale, mat, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    ob=bpy.context.object; ob.name=name; ob.scale=scale; ob.rotation_euler=rotation; ob.data.materials.append(mat)
    for face in ob.data.polygons: face.use_smooth=True
    return ob

def line(name, start, end, radius, mat):
    delta=Vector(end)-Vector(start); mid=(Vector(start)+Vector(end))/2
    ob=cylinder(name,mid,radius,delta.length,mat,12); ob.rotation_euler=delta.to_track_quat('Z','Y').to_euler(); return ob

def base():
    box('Dark base',(0,0,0),(4.3,4.3,.30),ink,.12)
    box('Edge inset',(0,0,.18),(4.16,4.16,.10),chalk,.06)

def plant(x,y,z,s=1):
    cylinder('Plant pot',(x,y,z+.18*s),.26*s,.36*s,clay)
    cylinder('Pot rim',(x,y,z+.36*s),.29*s,.08*s,clay)
    cylinder('Pot soil',(x,y,z+.405*s),.245*s,.03*s,ink)
    for i in range(5):
        ang=2*math.pi*i/5
        start=(x,y,z+.4*s); tip=(x+math.cos(ang)*.25*s,y+math.sin(ang)*.25*s,z+.86*s)
        line('Plant stem',start,tip,.018*s,forest)
        leaf=ellipsoid('Leaf',tip,(.11*s,.06*s,.28*s),leafmat,(math.sin(ang)*.55,math.cos(ang)*.55,ang))

def screen_image(name, loc, width, height, path):
    bpy.ops.mesh.primitive_plane_add(size=2, location=loc, rotation=(math.pi/2, 0, 0)); ob=bpy.context.object; ob.name=name; ob.scale=(width/2,height/2,1)
    mat=bpy.data.materials.new(name); mat.use_nodes=True; nodes=mat.node_tree.nodes; shader=next(n for n in nodes if n.type=='BSDF_PRINCIPLED'); tex=nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(path, check_existing=True); tex.image.pack(); mat.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color']); shader.inputs['Roughness'].default_value=.8; ob.data.materials.append(mat)
    return ob

def wellness():
    base(); box('Garden ground',(0,0,.28),(4.07,4.07,.13),sage,.06)
    # A nook inspired by the Android app's ivory/sage identity and real Home UI.
    box('Back garden wall',(0,1.75,1.18),(3.82,.16,1.75),forest,.08)
    box('Wall inset',(0,1.64,1.18),(3.45,.04,1.40),leafmat,.03)
    # Rear lattice and framing keep the garden wall intentional from every view.
    box('Rear wall inset',(0,1.844,1.18),(3.50,.035,1.42),sage,.02)
    for x in (-1.68,-1.12,-.56,0,.56,1.12,1.68):
        box('Rear garden slat',(x,1.87,1.18),(.055,.04,1.38),forest,.012)
    for z in (.53,1.83):
        box('Rear garden rail',(0,1.875,z),(3.55,.04,.055),forest,.012)
    for x in (-1.72,1.72):
        box('Wall foot',(x,1.69,.40),(.18,.35,.09),wood,.025)
    phone=box('Phone case',(-.25,1.18,1.42),(1.10,.20,2.05),ink,.12)
    box('Screen border',(-.25,1.065,1.42),(.98,.035,1.88),paper,.04)
    screen_image('Actual eUdyaan home UI',(-.25,1.039,1.42),.92,1.78,os.path.join(ROOT,'blender/reference-images/eudyaan-home.png'))
    box('Earpiece',(-.25,1.015,2.32),(.22,.025,.028),ink,.012)
    # Side controls and rear mounting bracket articulate the physical device.
    box('Phone side volume',(.315,1.18,1.68),(.024,.09,.21),chalk,.01)
    box('Phone side power',(.315,1.18,1.32),(.024,.09,.11),chalk,.01)
    box('Phone wall mount',(-.25,1.39,1.40),(.38,.22,.60),forest,.04)
    box('Phone mount foot',(-.25,1.42,.42),(.44,.34,.10),wood,.02)
    # Wreath identity, leaves form a round emblem on the wall.
    for i in range(14):
        angle=2*math.pi*i/14
        leaf=ellipsoid('Wreath leaf',(-1.22+math.cos(angle)*.34,1.57,1.75+math.sin(angle)*.34),(.06,.028,.15),mint,(0,angle,0))
    # Stepping stones and flowers lead to a cozy bench.
    for i in range(5): ellipsoid('Garden stone',(-1.42+i*.34,-1.43+i*.20,.40),(.17,.13,.045),paper)
    box('Bench seat',(.83,-.75,.74),(1.35,.53,.11),wood,.05)
    box('Bench back',(.83,-.51,1.04),(1.35,.09,.57),wood,.05)
    for x in (.28,1.38):
        box('Bench leg',(x,-.75,.53),(.1,.36,.38),wood,.025)
    # A tiny person taking a quiet moment: symbolic, not a claim of app functionality.
    ellipsoid('Person body',(.70,-.82,1.13),(.21,.15,.32),coral)
    ellipsoid('Person head',(.70,-.80,1.48),(.16,.14,.19),ochre)
    ellipsoid('Person hair',(.70,-.76,1.56),(.17,.15,.12),ink)
    for x in (.64,.76): ellipsoid('Eye',(x,-.94,1.49),(.013,.012,.018),ink)
    ellipsoid('Cheek',(.60,-.935,1.45),(.023,.012,.014),clay)
    line('Arm',(.53,-.82,1.23),(.48,-1.02,.95),.05,coral)
    line('Arm',(.86,-.82,1.23),(.94,-1.02,.95),.05,coral)
    for x in (.43,.73,1.03,1.33): box('Bench detail',(x,-.465,1.04),(.015,.015,.43),clay,.004)
    box('Book on bench',(1.25,-.84,.82),(.27,.22,.04),paper,.01)
    box('Book spine',(1.25,-.95,.84),(.27,.02,.025),clay,.005)
    for x in (.58,.82):
        line('Leg',(x,-.85,.91),(x,-1.13,.55),.06,forest)
    plant(1.50,1.13,.36,.95); plant(-1.58,1.13,.36,.72)
    for x,y in [(-1.6,-.3),(-1.2,.35),(1.6,-1.35),(.15,-1.5)]:
        line('Flower stem',(x,y,.36),(x,y,.58),.012,forest)
        ellipsoid('Flower center',(x,y,.59),(.035,.035,.035),ochre)
        for i in range(5):
            a=i*2*math.pi/5
            ellipsoid('Flower petal',(x+math.cos(a)*.052,y+math.sin(a)*.052,.588),(.04,.026,.02),coral,(0,0,a))
    box('Garden path lip',(0,-1.97,.33),(3.7,.06,.05),paper,.02)
    # Tiny blossoms and leaf clusters soften the architectural wall.
    for x,y in [(-1.72,-.8),(-1.58,-.65),(-1.36,-.73),(1.62,-.38),(1.52,-.27),(1.70,-.19)]:
        ellipsoid('Ground leaf',(x,y,.40),(.12,.07,.025),forest,(0,0,x))
    for x in (-1.5, 1.48):
        box('Wall corner trim',(x,1.54,1.16),(.045,.05,1.25),mint,.01)


def flood():
    base(); box('Landscape',(0,0,.28),(4.07,4.07,.13),sand,.07)
    # App is a Streamlit risk model, not a physical sensor system.
    box('River',(0,-.70,.36),(4.0,1.48,.07),water,.06)
    for x,y in [(-1.50,-.80),(-.65,-.35),(.25,-1.05),(1.2,-.55)]:
        box('Current',(x,y,.408),(.55,.035,.015),foam,.012)
    for x in [-1.7,1.65]:
        for y in [-1.35,-.10]: ellipsoid('River stone',(x,y,.39),(.18,.11,.06),chalk)
    # Screen represents actual 7 inputs and comparative regression/tree/MLP outputs.
    box('Dashboard frame',(0,1.61,1.31),(3.35,.16,1.85),ink,.08)
    # The screen is a supported display with a serviceable rear, not a floating slab.
    for x in (-1.21,1.21):
        box('Screen upright',(x,1.75,.77),(.11,.13,.86),wood,.025)
        box('Screen foot',(x,1.66,.40),(.37,.43,.10),wood,.025)
    box('Screen rear panel',(0,1.70,1.31),(2.95,.035,1.48),forest,.045)
    box('Screen rear module',(0,1.73,1.26),(1.14,.045,.58),ink,.035)
    for i in range(5):
        box('Vent slot',(0,1.76,1.43-i*.075),(.75,.014,.018),chalk,.005)
    for x in (-1.38,1.38):
        for z in (.66,1.97): ellipsoid('Rear screw',(x,1.73,z),(.025,.012,.025),ochre)
    box('Dashboard surface',(0,1.51,1.31),(3.15,.03,1.66),paper,.03)
    box('Dashboard header',(0,1.485,1.94),(3.0,.02,.24),forest,.02)
    box('Status stripe',(-.66,1.48,1.57),(1.42,.02,.21),mint,.03)
    # seven inputs on the left; three predictions on the right.
    for i in range(7):
        z=1.34-(i//2)*.21; x=-1.13+(i%2)*.63
        box('Input field',(x,1.48,z),(.52,.02,.14),chalk,.015)
        box('Input accent',(x-.14,1.465,z),(.20,.012,.025),forest,.006)
    for i,h in enumerate((.42,.55,.66)):
        box('Model comparison bar',(.56+i*.33,1.47,.70+h/2),(.21,.02,h),[water,ochre,coral][i],.01)
    # Floodplain: cottage, hills and a bridge, with gentle rain and trees.
    box('Bridge deck',(-.35,-.73,.62),(.68,1.72,.16),wood,.04)
    for x in [-.69,-.01]:
        for y in [-1.4,-.07]: box('Bridge support',(x,y,.50),(.08,.08,.27),wood,.02)
        line('Bridge rail',(x,-1.4,.86),(x,-.06,.86),.035,wood)
        for y in [-1.4,-.73,-.06]: line('Bridge post',(x,y,.62),(x,y,.86),.025,wood)
    box('Cottage',(1.10,.35,.75),(.80,.68,.75),paper,.04)
    for side in (-1,1):
        roof=box('Cottage pitched roof',(1.10+side*.25,.35,1.19),(.58,.82,.09),coral,.02); roof.rotation_euler[1]=side*.48
    box('Cottage chimney',(1.32,.5,1.42),(.12,.14,.32),clay,.02)
    box('Cottage window',(.82,-.005,.87),(.20,.025,.22),water,.01)
    box('Window cross',(.82,-.022,.87),(.025,.015,.20),paper,.004)
    box('Window sill',(.82,-.03,.75),(.25,.035,.035),wood,.006)

    box('Door',(1.1,-.005,.65),(.22,.025,.37),wood,.01)
    ellipsoid('Door knob',(1.17,-.025,.65),(.025,.015,.025),ochre)
    # Rear and side windows make the cottage read from the reverse side too.
    box('Rear window',(1.10,.70,.87),(.23,.025,.22),water,.01)
    box('Rear sill',(1.10,.72,.75),(.29,.03,.035),wood,.006)
    box('Side window',(1.515,.32,.87),(.025,.23,.22),water,.01)
    for x,y,s in [(-1.5,.55,.8),(1.65,.8,.65),(-1.6,1.32,.55)]:
        cylinder('Tree trunk',(x,y,.60),.075*s,.50*s,wood,12)
        ellipsoid('Tree canopy',(x,y,.99),(.34*s,.30*s,.50*s),leafmat)
        ellipsoid('Tree canopy highlight',(x-.08*s,y-.05*s,1.12),(.20*s,.20*s,.30*s),mint)

    for x,z in [(-1.40,1.95),(-1.05,2.14),(-.72,1.98)]: ellipsoid('Cloud',(x,.8,z),(.25,.12,.16),chalk)
    for x,y in [(-1.70,-.2),(1.68,-.02),(-1.9,.45),(1.8,1.2)]:
        for j in range(3): ellipsoid('Small shrub',(x+j*.11,y,.40),(.10,.08,.06),forest)
    # Board mount and frame fasteners make the dashboard read as a physical display.
    for x in (-1.52,1.52):
        for z in (.53,2.08): ellipsoid('Display pin',(x,1.47,z),(.025,.015,.025),wood)

def output(key):
    # Export meshes only: no camera or Blender-only render setup in the web asset.
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,key+'.glb'), export_format='GLB', use_selection=True)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.camera_add(location=(7,-9,7)); camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,.85))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'; camera.data.ortho_scale=6.8
    scene=bpy.context.scene; scene.camera=camera; scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
    scene.world.color=(.12,.12,.12)
    bpy.ops.object.light_add(type='AREA', location=(1,-4,7)); keylight=bpy.context.object; keylight.data.energy=650; keylight.data.shape='DISK'; keylight.data.size=6
    bpy.ops.object.light_add(type='AREA', location=(-4,-1,4)); fill=bpy.context.object; fill.data.energy=300; fill.data.size=5
    scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD'; scene.world.color=(.035,.055,.055)
    scene.render.resolution_x=600; scene.render.resolution_y=450; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,key+'.png')
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'blender',key+'-portfolio-diorama.blend'))

for key, builder in [('eUdyaan',wellness),('Flood-Monitoring-System',flood)]:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    ink=material('Deep ink',(.12,.20,.20)); chalk=material('Chalk',(.86,.84,.73)); paper=material('Paper',(.94,.91,.81))
    sage=material('Garden sage',(.55,.68,.52)); leafmat=material('Leaf green',(.28,.50,.33)); forest=material('Forest',(.15,.32,.25))
    clay=material('Terracotta',(.73,.38,.27)); ochre=material('Ochre',(.87,.68,.32)); wood=material('Warm timber',(.55,.36,.24))
    sand=material('Earth',(.65,.62,.45)); earth=material('River bank',(.52,.49,.36)); water=material('River blue',(.23,.46,.55)); foam=material('Water marks',(.72,.85,.80)); mint=material('Mint',(.55,.78,.64)); coral=material('Coral',(.84,.38,.30))
    builder(); output(key)
