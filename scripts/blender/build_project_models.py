import bpy, math, os
from mathutils import Vector
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
out = os.path.join(root,'public/projects')
os.makedirs(out, exist_ok=True)

def mat(name, color):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value=(*color,1); return m
sand=mat('Sand',(0.77,0.70,0.57)); teal=mat('Teal',(0.19,0.50,0.49)); dark=mat('Ink',(0.12,0.20,0.23)); cream=mat('Cream',(0.88,0.84,0.73)); coral=mat('Coral',(0.86,0.42,0.31)); blue=mat('Blue',(0.27,0.44,0.62)); green=mat('Leaf',(0.33,0.57,0.39)); gold=mat('Gold',(0.90,0.69,0.32))
def cube(name, loc, scale, material, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if bevel:
        mod=o.modifiers.new('Soft edges','BEVEL'); mod.width=bevel; mod.segments=2; bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier=mod.name)
    return o
def sphere(name,loc,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material); return o
def cyl(name,loc,radius,depth,material):
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=radius, depth=depth, location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def build(key):
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    cube('Base',(0,0,0),(4,4,.3),dark,.12)
    cube('Surface',(0,0,.19),(3.84,3.84,.1),sand,.05)
    if key=='SurferFlow':
        cube('Ocean',(0,0,.27),(3.75,3.75,.12),teal)
        for x,y,z in [(-1.1,.3,.55),(-.7,.35,.75),(-.3,.4,.93),(.1,.45,1.05),(.5,.5,1.1),(.9,.55,1.02)]: sphere('Wave',(x,y,z),(.38,.34,.45),blue)
        board=cube('Surfboard',(0,-.6,.55),(1.6,.42,.09),cream,.16); board.rotation_euler[2]=.35
        sphere('Sun',(1.25,1.2,1.5),(.34,.34,.34),gold)
    elif key=='Cubenikal':
        for x in range(3):
            for y in range(3):
                for z in range(3): cube('Puzzle tile',((x-1)*.58,(y-1)*.58,.65+z*.58),(.52,.52,.52),[coral,teal,cream,blue,gold][(x+y+z)%5],.04)
    elif key=='eUdyaan':
        cube('Phone',(0,0,.95),(1.35,.28,1.95),dark,.12); cube('Screen',(0,-.155,.96),(1.17,.04,1.72),cream,.03)
        cyl('Planter',(0,-.35,.5),.36,.4,coral)
        for x,z in [(-.35,.95),(0,1.2),(.35,.95)]:
            leaf=sphere('Leaf',(x,-.35,z),(.22,.13,.46),green); leaf.rotation_euler[1]=x
    elif key=='Guess-Whose-Song':
        cyl('Record',(0,0,.52),1.2,.18,dark); cyl('Label',(0,0,.63),.46,.05,coral); cyl('Center',(0,0,.67),.08,.03,cream)
        cube('Player',(0,0,.33),(3.1,2.7,.22),blue)
        for x in [-1.1,-.85,-.6]: cyl('Button',(x,-.94,.49),.07,.05,gold)
    elif key=='Flood-Monitoring-System':
        cube('Water',(0,0,.3),(3.75,3.75,.16),blue)
        for x,y,h in [(-1,-.6,.8),(-.3,-.6,1.4),(.4,-.6,1.0),(1.1,-.6,1.8)]: cube('Data bar',(x,y,.38+h/2),(.42,.42,h),[teal,cream,coral,gold][int((x+1)*10)%4],.04)
        for x in [-1.1,0,1.1]: cube('Wave line',(x,.8,.43),(.75,.09,.05),cream,.02)
    else:
        cube('Wall back',(0,1.65,1.05),(3.5,.15,1.7),blue); cube('Wall side',(-1.68,0,1.05),(.15,3.4,1.7),cream)
        cube('Desk',(0,.75,.8),(2,.7,.16),sand); cube('Monitor',(0,.8,1.35),(1.1,.12,.7),dark); cube('Screen',(0,.72,1.35),(.94,.02,.54),teal)
        cube('Sofa',(.3,-.85,.55),(1.9,.75,.6),dark)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(out,key+'.glb'),export_format='GLB')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.camera_add(location=(7,-9,7)); camera=bpy.context.object; camera.rotation_euler=(Vector((0,0,.7))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=6.7; bpy.context.scene.camera=camera
    scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'; scene.display.shading.light='STUDIO'; scene.display.shading.color_type='MATERIAL'; scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True; scene.display.shading.background_type='WORLD'; scene.world.color=(.035,.055,.055); scene.render.resolution_x=600; scene.render.resolution_y=450; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(out,key+'.png'); bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root,'blender',key+'-portfolio-diorama.blend'))
for key in ['Om-Portfolio']: build(key)
