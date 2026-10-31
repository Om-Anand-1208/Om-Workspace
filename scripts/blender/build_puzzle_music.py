"""Editable portfolio models: Cubenikal and Guess Whose Song. Run with Blender -b -t 2 --python."""
import bpy, math, os
from mathutils import Vector
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
out = os.path.join(root, 'public/projects')

def mat(name, color, metallic=0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = .48
    return m
ink = mat('ink', (.055,.10,.12)); charcoal = mat('charcoal', (.095,.16,.17)); brass = mat('brass', (.85,.65,.34), .45); pale = mat('warm ivory', (.90,.86,.73)); mint = mat('mint', (.35,.70,.59)); blue = mat('dusk blue', (.26,.42,.55)); coral = mat('muted coral', (.80,.37,.27)); red = mat('rust', (.55,.24,.19)); orange = mat('orange', (.94,.57,.30)); white = mat('chalk', (.96,.92,.79)); violet = mat('dusty violet', (.44,.35,.49))

def cube(name, loc, dims, m, bevel=.06):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
    if bevel:
        mod=o.modifiers.new('Edge radii', 'BEVEL'); mod.width=bevel; mod.segments=3
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o

def cyl(name, loc, radius, depth, m, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(m)
    bevel=o.modifiers.new('Edge bevel', 'BEVEL'); bevel.width=.018; bevel.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=bevel.name)
    return o

def torus(name, loc, major, minor, m):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=8, location=loc, major_radius=major, minor_radius=minor); o=bpy.context.object; o.name=name; o.data.materials.append(m); return o

def rod(name,a,b,r,m):
    v=Vector(b)-Vector(a); o=cyl(name, (Vector(a)+Vector(b))/2,r,v.length,m,16); o.rotation_euler=v.to_track_quat('Z','Y').to_euler(); return o

def base():
    cube('Dark platform',(0,0,.04),(4,3.6,.28),ink,.12)
    cube('Fine rim',(0,0,.19),(3.89,3.49,.07),brass,.055)
    cube('Platform top',(0,0,.245),(3.82,3.42,.08),charcoal,.04)
    for x in (-1.7,1.7):
        for y in (-1.48,1.48): cyl('Rivet',(x,y,.3),.045,.02,brass,16)

def puzzle():
    base()
    # A nested plinth under a 3 x 3 articulated cube. Each exposed sticker is a
    # separate mesh; the deliberate seams and subtly offset top row show motion.
    cyl('Pedestal', (0,.05,.42), 1.22,.28, ink)
    torus('Pedestal rim', (0,.05,.57),1.08,.018,brass)
    spacing=.55
    core=cube('Puzzle core',(0,.05,1.49),(1.65,1.65,1.65),ink,.09)
    palette_top=[mint,mint,pale, mint,pale,coral, pale,coral,coral]
    palette_front=[blue,blue,coral, blue,pale,coral, pale,mint,mint]
    palette_right=[orange,orange,pale, orange,coral,pale, blue,blue,mint]
    for i in range(3):
        for j in range(3):
            x=(i-1)*spacing; y=.05+(j-1)*spacing
            # top, front facing camera, and right visible faces
            cube('Top tile',(x,y,2.335),(.47,.47,.055),palette_top[i*3+j],.035)
            cube('Front tile',(x,-.795,.94+j*spacing),(.47,.055,.47),palette_front[i*3+j],.035)
            cube('Right tile',(.845,.05+(i-1)*spacing,.94+j*spacing),(.055,.47,.47),palette_right[i*3+j],.035)
    # One displaced tile makes the scene feel like a puzzle in progress.
    tile=cube('Floating piece',(-1.27,-.72,1.27),(.43,.43,.43),mint,.055); tile.rotation_euler=(.13,-.20,.30)
    torus('Orbit detail',(0,.05,.595),1.39,.013,mint)
    for x, y in [(-1.55,.95),(1.5,-1.05)]: cyl('Marker',(x,y,.31),.09,.025,coral,16)

def music():
    base()
    # A compact turntable, phone and notes: record + multiplayer quiz device.
    cube('Turntable body',(-.38,.04,.48),(2.45,2.38,.39),blue,.13)
    cube('Turntable top',(-.38,.04,.7),(2.30,2.23,.08),ink,.07)
    cyl('Platter',(-.45,.10,.76),.93,.08,brass)
    cyl('Vinyl',(-.45,.10,.815),.85,.06,ink)
    for r in (.45,.58,.70,.78): torus('Vinyl groove',(-.45,.10,.849),r,.006,charcoal)
    cyl('Record label',(-.45,.10,.85),.28,.02,coral); cyl('Spindle',(-.45,.10,.88),.045,.06,pale,20)
    cyl('Tonearm pivot',(.53,.78,.80),.13,.10,brass)
    rod('Tonearm',(.53,.78,.88),(.52,-.42,.88),.036,pale)
    rod('Headshell',(.52,-.42,.88),(.35,-.58,.88),.045,coral)
    for x in (-1.18,-.92,-.66): cyl('Player button',(x,-.87,.77),.07,.05,mint,24)
    # Freestanding phone shown behind the deck with an abstract quiz UI.
    cube('Phone',(1.25,.73,1.16),(.86,.22,1.72),ink,.12)
    cube('Phone screen',(1.25,.602,1.18),(.72,.035,1.49),pale,.035)
    cube('Screen header',(1.25,.577,1.70),(.60,.012,.20),mint,.025)
    for z,width in [(1.43,.50),(1.22,.42),(1.01,.50)]: cube('Answer', (1.25,.575,z),(width,.012,.12),blue,.025)
    cube('Phone button',(1.25,.575,.65),(.16,.012,.05),coral,.02)
    # Notes float on brass stems, adding height and a musical cue.
    for x,y,z in [(-1.30,.8,1.56),(-.85,1.06,1.95)]:
        head=cyl('Music note head',(x,y,z),.12,.09,coral,20); head.rotation_euler[0]=math.pi/2
        rod('Music note stem',(x+.10,y,z),(x+.10,y,z+.54),.025,coral)
        rod('Music note flag',(x+.10,y,z+.54),(x+.37,y,z+.43),.028,coral)

def finish(key):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(out,key+'.glb'),export_format='GLB',use_selection=True)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.camera_add(location=(7,-9,7)); camera=bpy.context.object
    camera.rotation_euler=(Vector((0,0,1.05))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'; camera.data.ortho_scale=6.1; bpy.context.scene.camera=camera
    scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.background_type='WORLD'; scene.world.color=(.035,.055,.055)
    scene.render.resolution_x=600; scene.render.resolution_y=450; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(out,key+'.png'); bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'blender',key+'-portfolio-diorama.blend'))
for key, fn in [('Cubenikal',puzzle),('Guess-Whose-Song',music)]:
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False); fn(); finish(key)
